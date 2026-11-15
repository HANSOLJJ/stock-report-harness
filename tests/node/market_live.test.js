// 리포트 국면 탭의 지금 값 계산(assets/market_live.js)이 market_now.py 와 같은 고정 자료로 같은 값을 내는지 잠그는 테스트
const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const fs = require('node:fs');

const live = require('../../scripts/scorecard/assets/market_live.js');
const fx = JSON.parse(fs.readFileSync(path.join(__dirname, 'fixtures', 'market_live.json'), 'utf8'));

const close = (a, b) => assert.ok(Math.abs(a - b) < 1e-9, `${a} != ${b}`);

test('GPU 임대료는 GPU 수로 가중한 중간값이고 잘못된 호가는 건너뛴다', () => {
  const got = live.gpuRent(fx.offers);
  close(got.value, fx.expect_gpu.value);
  assert.equal(got.gpus, fx.expect_gpu.gpus);
  assert.equal(got.offers, fx.expect_gpu.offers);
  close(live.gpuRent(fx.offers_even).value, fx.expect_gpu_even);
  assert.equal(live.gpuRent([]), null);
});

test('토큰 모델 고르기: 창·UTC 날짜·동점 규칙이 파이썬과 같다', () => {
  const picks = live.tokenPicks(fx.models, fx.ref);
  assert.deepEqual(picks.map((p) => [p.lab, p.model]), fx.expect_picks.map((p) => [p.lab, p.model]));
  picks.forEach((p, i) => close(p.blended, fx.expect_picks[i].blended));
  close(live.median(picks.map((p) => p.blended)), fx.expect_token);
});

test('FRED 최신 값은 "." 인 날을 건너뛴다', () => {
  const payload = { observations: [{ date: '2026-11-14', value: '.' }, { date: '2026-11-13', value: '4.12' }] };
  assert.deepEqual(live.fredLatest(payload), { date: '2026-11-13', value: 4.12 });
  assert.equal(live.fredLatest({ observations: [{ date: '2026-11-14', value: '.' }] }), null);
  assert.equal(live.fredLatest(null), null);
});

test('변화 칸: 금리는 bp, 단가는 %', () => {
  assert.equal(live.changeText({ kind: 'pct' }, 4.1, 4.235), '+14bp');
  assert.equal(live.changeText({ kind: 'pct' }, 4.1, 4.0), '-10bp');
  assert.equal(live.changeText({ kind: 'usd' }, 2.0, 2.5), '+25.0%');
  assert.equal(live.changeText({ kind: 'usd' }, null, 2.5), '—');
  assert.equal(live.valueText({ kind: 'pct', unit: '%p' }, 0.894), '0.89%p');
  assert.equal(live.valueText({ kind: 'usd', unit: '$/GPU·시간' }, 2.667), '$2.67');
});

test('vast.ai 주소는 파이썬과 같은 질의를 만든다', () => {
  const url = live.vastUrl('H100 SXM');
  const q = JSON.parse(decodeURIComponent(url.split('?q=')[1]));
  assert.deepEqual(q, { gpu_name: { eq: 'H100 SXM' }, rentable: { eq: true }, type: 'on-demand', limit: 500 });
});

test('FRED CSV 는 빈 칸과 "." 를 건너뛰고 날짜순으로 둔다', () => {
  const csv = 'observation_date,BAA10Y\n2026-11-12,1.48\n2026-11-10,1.50\n2026-11-11,.\n2026-11-13,\n';
  assert.deepEqual(live.parseFredCsv(csv), [['2026-11-10', 1.5], ['2026-11-12', 1.48]]);
  assert.deepEqual(live.parseFredCsv(''), []);
});

test('GetDeploying CSV 는 약정 없는 on-demand 의 중간값만 머리글 이름으로 읽는다', () => {
  const csv = [
    'gpu_slug,date,billing_type,reservation_months,min_price,max_price,median_price,provider_median_price,provider_count,offering_count',
    'nvidia-h100,2026-11-09,ON_DEMAND,,1.8,12.29,4.0775,3.96,44,120',
    'nvidia-h100,2026-11-09,RESERVED,12,1.5,3,2.2,2.1,9,12',
    'nvidia-h100,2026-11-02,ON_DEMAND,,1.8,12,4.1,4,40,110',
    'nvidia-h100,2026-10-26,ON_DEMAND,,,,,,0,0'
  ].join('\n');
  assert.deepEqual(live.parseGetDeployingCsv(csv), [['2026-11-02', 4.1], ['2026-11-09', 4.0775]]);
  assert.deepEqual(live.parseGetDeployingCsv('date,price\n2026-11-02,1'), []);
});

test('재구성 토큰 단가는 날짜마다 같은 고르기 규칙의 중간값이다', () => {
  const pts = live.reconstructTokens(fx.models, '2026-11-01', fx.ref);
  assert.deepEqual(pts.map((p) => p[0]), ['2026-11-01', '2026-11-08', '2026-11-15']);
  close(pts[2][1], fx.expect_token);
});

test('하루 값: 받지 못한 원천은 null 이고, 같은 날 다시 찍어도 먼저 받은 값을 지킨다', () => {
  const a = live.dailyPoint({ 'H100 SXM': fx.offers }, fx.models, fx.ref);
  close(a.gpu['H100 SXM'].value, 2.5);
  assert.equal(a.gpu.H200, null);
  close(a.token, fx.expect_token);
  const b = live.dailyPoint({ H200: fx.offers_even }, null, fx.ref);
  assert.equal(b.token, null);
  const merged = live.mergeDaily([{ date: '2026-11-14', gpu: {}, token: 1, labs: 1 }, a], b);
  assert.deepEqual(merged.map((p) => p.date), ['2026-11-14', '2026-11-15']);
  const day = merged[1];
  close(day.gpu['H100 SXM'].value, 2.5);
  close(day.gpu.H200.value, 2.0);
  close(day.token, fx.expect_token);
});

test('시계열 묶음: 열쇠는 리포트 행과 같고, 받지 못한 외부 원천은 직전 선을 쓴다', () => {
  const daily = [live.dailyPoint({ 'H100 SXM': fx.offers }, fx.models, fx.ref)];
  const fred = { DGS10: 'observation_date,DGS10\n2026-11-12,4.10\n', BAA10Y: 'observation_date,BAA10Y\n2026-11-12,1.48\n' };
  const gd = { 'H100 SXM': 'date,billing_type,reservation_months,median_price\n2026-11-09,ON_DEMAND,,4.0\n' };
  const first = live.assemble({ fred, getdeploying: gd, daily, models: fx.models, today: fx.ref, now: '2026-11-15T00:00:00Z' });
  assert.deepEqual(Object.keys(first.series).sort(), ['baa_spread', 'gpu_rent_hourly:B200', 'gpu_rent_hourly:H100 SXM',
    'gpu_rent_hourly:H200', 'hy_oas', 'ig_oas', 'token_blended_price', 'ust10y_yield']);
  assert.deepEqual(first.series.ig_oas.lines, []);
  const h100 = first.series['gpu_rent_hourly:H100 SXM'].lines;
  assert.deepEqual(h100.map((l) => [l.id, l.points.length, !!l.dashed]), [['ours', 1, false], ['getdeploying', 1, true]]);
  assert.equal(first.series.token_blended_price.lines[1].id, 'reconstructed');
  // 다음 날 FRED·GetDeploying·OpenRouter 를 모두 받지 못하면 직전 선을 그대로 쓴다
  const second = live.assemble({ fred: { DGS10: null }, getdeploying: {}, daily, models: null, today: fx.ref, now: 'x', previous: first });
  assert.deepEqual(second.series.ust10y_yield.lines, first.series.ust10y_yield.lines);
  assert.deepEqual(second.series['gpu_rent_hourly:H100 SXM'].lines[1], h100[1]);
  assert.deepEqual(second.series.token_blended_price.lines[1], first.series.token_blended_price.lines[1]);
});
