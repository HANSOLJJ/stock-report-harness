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
