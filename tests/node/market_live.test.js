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
    'gpu_rent_hourly:H200', 'hy_oas', 'ig_oas', 'token_blended_price', 'ust10y_yield', 'yields']);
  // 금리 한눈에: 미국채 10년물만 받은 날은 그 선 하나다(받지 못한 회사채 금리 계열은 선을 만들지 않는다).
  assert.equal(first.series.yields.big, true);
  assert.deepEqual(first.series.yields.lines.map((l) => l.id), ['ust10y']);
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

test('금리 한눈에: 미국채 10년물과 회사채 금리 세 계열을 한 축에 싣고, 받지 못한 계열은 직전 선을 쓴다', () => {
  assert.deepEqual(live.FRED_FETCH, ['DGS10', 'BAA10Y', 'BAMLC0A0CM', 'BAMLH0A0HYM2', 'BAMLC0A0CMEY', 'DBAA', 'BAMLH0A0HYM2EY']);
  const csv = (id, v) => `observation_date,${id}\n2026-11-12,${v}\n`;
  const fred = { DGS10: csv('DGS10', 5.10), BAMLC0A0CMEY: csv('BAMLC0A0CMEY', 5.96), DBAA: csv('DBAA', 6.58), BAMLH0A0HYM2EY: csv('BAMLH0A0HYM2EY', 8.16) };
  const a = live.assemble({ fred, getdeploying: {}, daily: [], models: null, today: '2026-11-15', now: 'x' });
  assert.deepEqual(a.series.yields.lines.map((l) => [l.id, l.points]),
    [['ust10y', [['2026-11-12', 5.1]]], ['ig', [['2026-11-12', 5.96]]], ['baa', [['2026-11-12', 6.58]]], ['hy', [['2026-11-12', 8.16]]]]);
  const b = live.assemble({ fred: { DGS10: csv('DGS10', 5.2) }, getdeploying: {}, daily: [], models: null, today: '2026-11-16', now: 'y', previous: a });
  assert.deepEqual(b.series.yields.lines.map((l) => l.id), ['ust10y', 'ig', 'baa', 'hy']);
  assert.deepEqual(b.series.yields.lines[0].points, [['2026-11-12', 5.2]]);
  assert.deepEqual(b.series.yields.lines[3], a.series.yields.lines[3]);
});

test('ECOS D램 지수: 달러 기준 칸만 그달 1일로 읽고, 오류 응답이면 빈 목록이다', () => {
  const payload = { StatisticSearch: { list_total_count: 3, row: [
    { TIME: '202602', ITEM_CODE2: 'D', DATA_VALUE: '157.62' },
    { TIME: '202601', ITEM_CODE2: 'W', DATA_VALUE: '181.78' },
    { TIME: '202601', ITEM_CODE2: 'D', DATA_VALUE: '147.44' },
    { TIME: '202603', ITEM_CODE2: 'D', DATA_VALUE: '' }] } };
  assert.deepEqual(live.parseEcos(payload), [['2026-01-01', 147.44], ['2026-02-01', 157.62]]);
  assert.deepEqual(live.parseEcos({ RESULT: { CODE: 'INFO-100' } }), []);
  assert.equal(live.ecosUrl('K', '2026-11-15'),
    'https://ecos.bok.or.kr/api/StatisticSearch/K/json/kr/1/1000/402Y016/M/201501/202611/30911201AA/D');
});

test('묶음: ECOS 를 받으면 표 밖 시계열로 싣고, 키가 없으면 싣지 않으며, 빈 응답은 오류로 적고 직전 선을 쓴다', () => {
  const ecos = { StatisticSearch: { row: [{ TIME: '202601', ITEM_CODE2: 'D', DATA_VALUE: '147.44' }] } };
  const a = live.assemble({ ecos, daily: [], today: fx.ref, now: 'x' });
  assert.equal(a.series.dram_export_index.title, 'D램 수출물가지수(달러 기준, 2020=100)');
  assert.equal(a.series.dram_export_index.kind, 'index');
  assert.deepEqual(a.series.dram_export_index.lines[0].points, [['2026-01-01', 147.44]]);
  assert.equal(live.assemble({ daily: [], today: fx.ref, now: 'x' }).series.dram_export_index, undefined);
  const b = live.assemble({ ecos: { RESULT: { CODE: 'INFO-100' } }, daily: [], today: fx.ref, now: 'x', previous: a, errors: ['다른 원천'] });
  assert.deepEqual(b.series.dram_export_index.lines, a.series.dram_export_index.lines);
  assert.deepEqual(b.errors, ['다른 원천', 'ECOS: 값이 없다(INFO-100)']);
  assert.equal(live.valueText({ kind: 'index' }, 147.44), '147.4');
});

const DRAMX = `<!-- DRAM Spot Price -->
<font face="Arial">DRAM Spot Price</font> <span>Last Update: Nov.13 2026 18:10 (GMT+8)</span>
<table><tr><td class="tab_title">Item</td></tr>
<tr> <td class="tab_tr_gray2"> <a href="/Price/Dram_Spot"> <img src="/chip.gif"> DDR5 16Gb (2Gx8) 4800/5600 </a> </td>
<td class="tab_tr_gray">72.50</td> <td class="tab_tr_gray">45.50</td> <td class="tab_tr_gray">72.50</td>
<td class="tab_tr_gray">45.50</td> <td class="tab_tr_gray">60.267</td> <td class="tab_tr_font9"><img src="/up.gif"><br> 0.06 % </td>
<td class="tab_tr_gray"><img src="/flash.gif"></td> </tr>
<tr> <td> DDR5 16Gb (2Gx8) eTT </td> <td>31.50</td> <td>29.70</td> <td>31.50</td> <td>29.70</td> <td>30.1</td> </tr></table>
<!-- DRAM Spot Price -->
<!-- Module Spot Price --> Last Update: Nov.2 2026 14:40 (GMT+8)`;

test('DRAMeXchange: DRAM 표의 DDR5 16Gb 4800/5600 세션 평균과 그 표의 갱신 날짜를 읽는다', () => {
  assert.deepEqual(live.parseDramx(DRAMX), { date: '2026-11-13', value: 60.267 });
  assert.deepEqual(live.parseDramx(DRAMX.replace('Nov.13', 'Sept.3')), { date: '2026-09-03', value: 60.267 });
  // 표가 바뀌어 품목이나 값을 못 찾으면 값을 만들지 않는다
  assert.equal(live.parseDramx(DRAMX.replace('4800/5600', '6400')), null);
  assert.equal(live.parseDramx(DRAMX.replace('60.267', '-')), null);
  assert.equal(live.parseDramx('<html></html>'), null);
  const pts = live.addPoint([['2026-11-12', 59.9], ['2026-11-13', 60.0]], { date: '2026-11-13', value: 60.267 });
  assert.deepEqual(pts, [['2026-11-12', 59.9], ['2026-11-13', 60.267]]);
  assert.deepEqual(live.addPoint(pts, null), pts);
});

test('비공개 묶음: 회사채는 bp 를 %p 로 바꾸고, 받지 못한 채권은 직전 선을 쓰며, D램 현물은 쌓인 점이 있을 때만 싣는다', () => {
  const [cw, orcl] = live.BONDS;
  assert.equal(live.bondHistoryUrl(cw.isin, '2026-11-15'),
    'https://bondterminal.com/api/v1/bonds/US21873SAB43/history?start=2024-11-16&end=2026-11-15',
    'BondTerminal 은 한 요청에 730일을 넘으면 400 을 낸다');
  const hist = { isin: cw.isin, series: [{ date: '2026-11-12', price: 87.0, ytw: 14.01, spread: 997 },
    { date: '2026-11-11', price: 86.5, ytw: 14.2 }, { date: '2026-11-10', spread: 1010 }] };
  assert.deepEqual(live.parseBondHistory(hist), [['2026-11-10', 10.1], ['2026-11-12', 9.97]]);
  const a = live.assemblePrivate({ bonds: { [cw.isin]: hist }, dram: [], now: 'x' });
  assert.deepEqual(Object.keys(a.series), ['bond:coreweave', 'bond_yields']);
  assert.equal(a.series['bond:coreweave'].unit, '%p');
  // 채권 금리는 ytw, 없으면 ytm. 값이 둘 다 없는 날은 뺀다.
  assert.deepEqual(live.parseBondYield(hist), [['2026-11-11', 14.2], ['2026-11-12', 14.01]]);
  assert.deepEqual(a.series.bond_yields.lines.map((l) => [l.id, l.label, l.hidden]), [['bond:coreweave', 'CoreWeave 9.25% 2030', true]]);
  const b = live.assemblePrivate({ bonds: { [orcl.isin]: { series: [{ date: '2026-11-12', spread: 150 }] } },
    dram: [['2026-11-13', 60.267]], now: 'y', previous: a, errors: ['BondTerminal CoreWeave: HTTP 429'] });
  assert.deepEqual(Object.keys(b.series).sort(), ['bond:coreweave', 'bond:oracle', 'bond_yields', 'dram_spot']);
  // 이번에 받지 못한 CoreWeave 금리 선은 직전 선 그대로 남는다.
  assert.deepEqual(b.series.bond_yields.lines.map((l) => l.id), ['bond:coreweave']);
  assert.deepEqual(b.series.bond_yields.lines[0].points, a.series.bond_yields.lines[0].points);
  assert.deepEqual(b.series['bond:coreweave'].lines, a.series['bond:coreweave'].lines);
  assert.equal(b.series.dram_spot.kind, 'usd');
  assert.deepEqual(b.errors, ['BondTerminal CoreWeave: HTTP 429']);
  // 다음 날 받은 창은 직전 선과 날짜로 합친다. 창 밖으로 밀려난 옛 점은 남고 같은 날짜는 새 값이다.
  const c = live.assemblePrivate({ bonds: { [cw.isin]: { series: [{ date: '2026-11-12', spread: 990 }, { date: '2026-11-13', spread: 980 }] } },
    dram: [], now: 'z', previous: b });
  assert.deepEqual(c.series['bond:coreweave'].lines[0].points, [['2026-11-10', 10.1], ['2026-11-12', 9.9], ['2026-11-13', 9.8]]);
});

// 변화(bp) 보기: 기준일을 0 으로 놓고 10년물과 엇갈린 선을 고른다
const ust = { id: 'ust10y', label: '미국채 10년물', points: [['2026-10-10', 5.20], ['2026-10-13', 5.22], ['2026-11-12', 5.10]] };
const oracle = { id: 'bond:oracle', label: 'Oracle', points: [['2026-10-14', 6.00], ['2026-11-04', 6.40], ['2026-11-12', 6.35]] };
const meta = { id: 'bond:meta', label: 'Meta', points: [['2026-10-13', 5.50], ['2026-11-12', 5.39]] };
const late = { id: 'bond:late', label: 'Late', points: [['2026-10-25', 7.0], ['2026-11-12', 7.1]] };

test('변화 보기: 기준일은 마지막 날에서 기간만큼 앞이고, 휴일만 넘겨 첫 점을 0 으로 놓으며, 늦게 시작한 선은 뺀다', () => {
  const v = live.changeLines([ust, oracle, late], 30);
  assert.equal(v.base, '2026-10-13');
  assert.equal(v.end, '2026-11-12');
  assert.deepEqual(v.lines[0].points, [['2026-10-13', 0], ['2026-11-12', -12]]);
  assert.equal(v.lines[1].from, '2026-10-14');
  assert.deepEqual(v.lines[1].points, [['2026-10-14', 0], ['2026-11-04', 40], ['2026-11-12', 35]]);
  assert.equal(v.lines[2].excluded, true);
  assert.deepEqual(v.lines[2].points, []);
});

test('엇갈림: 10년물과 반대로 움직인 선과 최근 구간의 방향을 적고, 뺀 선을 밝힌다', () => {
  const d = live.divergence(live.changeLines([ust, oracle, meta, late], 30));
  assert.equal(d.recentDays, 8);
  const o = d.items.find((i) => i.id === 'bond:oracle');
  assert.deepEqual([o.change, o.gap, o.recent, o.opposite], [35, 47, 7, true]);
  assert.equal(d.items.find((i) => i.id === 'bond:meta').opposite, false);
  const text = live.divergenceText(d);
  assert.ok(text.startsWith('2026-10-13 이후 미국채 10년물은 -12bp 움직였다.'), text);
  assert.ok(text.includes('반대로 움직인 선은 Oracle +35bp(10년물 대비 +47bp, 최근 8일에도 더 벌어지는 중)이다.'), text);
  assert.ok(!text.includes('Meta'), text);
  assert.ok(text.includes('기준일에 값이 없는 Late은 뺐다.'), text);
});

test('엇갈림: 최근 구간에 차이가 줄면 좁혀지는 중이고, 반대로 움직인 선이 없으면 가장 벌어진 선 하나를 적는다', () => {
  const narrowing = { ...oracle, points: [['2026-10-14', 6.00], ['2026-11-04', 6.60], ['2026-11-12', 6.35]] };
  assert.ok(live.divergenceText(live.divergence(live.changeLines([ust, narrowing], 30))).includes('최근 8일은 좁혀지는 중'));
  const text = live.divergenceText(live.divergence(live.changeLines([ust, meta], 30)));
  assert.ok(text.includes('반대로 움직인 선은 없고, 10년물 대비 가장 많이 벌어진 선은 Meta -11bp(10년물 대비 +1bp, 최근 8일은 거의 그대로)이다.'), text);
});

test('엇갈림: 기준일에 10년물 값이 없으면 읽지 않는다', () => {
  const d = live.divergence(live.changeLines([late, oracle], 30));
  assert.equal(d, null);
  assert.ok(live.divergenceText(d).includes('미국채 10년물 값이 없어'));
});

test('만기 이름: 지수·Baa·회사채 선의 범례에 만기를 붙이고, 모르는 선은 그대로 둔다', () => {
  const out = live.withMaturity([{ id: 'ig', label: 'x', points: [] }, { id: 'baa', label: 'x', points: [] },
    { id: 'bond:oracle', label: 'Oracle 2.875% 2031', points: [], hidden: false }, { id: 'ust10y', label: '미국채 10년물', points: [] }]);
  assert.deepEqual(out.map((l) => l.label), ['투자등급 회사채(ICE 지수, 여러 만기)', '무디스 Baa 회사채(만기 20년 이상)',
    'Oracle 2.875% 2031년 만기', '미국채 10년물']);
  assert.equal(out[2].hidden, false);
});

test('가산금리 차트: 공개 방문자는 지수 선 셋, 로그인하면 회사별 G-spread 를 더하고 Baa−10년물은 꺼 둔다', () => {
  const pts = [['2026-11-12', 1]];
  const data = { series: { ig_oas: { lines: [{ points: pts }] }, hy_oas: { lines: [{ points: pts }] },
    baa_spread: { lines: [{ points: pts }] }, ust10y_yield: { lines: [{ points: [['2026-11-12', 5.1]] }] } } };
  const pub = live.spreadRow(data, null, '2026-10-27');
  assert.deepEqual(pub.lines.map((l) => [l.id, l.hidden]), [['ig_oas', false], ['hy_oas', false], ['baa_spread', true]]);
  assert.equal(pub.change, 'spread');
  assert.deepEqual(pub.ref, [['2026-11-12', 5.1]]);
  const priv = { series: { 'bond:oracle': { lines: [{ points: pts }] }, 'bond:apple': { lines: [{ points: pts }] }, dram_spot: { lines: [] } } };
  const row = live.spreadRow(data, priv, '2026-10-27');
  assert.deepEqual(row.lines.slice(3).map((l) => [l.label, l.hidden]),
    [['Oracle 2.875% 2031년 만기 G-spread', false], ['Apple 4.9% 2031년 만기 G-spread', true]]);
});

test('가산금리 요약: 같은 기간 10년물 변화, 넓어진 선과 좁아진 선을 큰 순서로 적고 최근 방향을 붙인다', () => {
  const spreads = [
    { id: 'ig_oas', label: '투자등급 OAS', points: [['2026-10-13', 0.80], ['2026-11-04', 0.85], ['2026-11-12', 0.89]] },
    { id: 'bond:oracle', label: 'Oracle', points: [['2026-10-13', 1.00], ['2026-11-04', 1.50], ['2026-11-12', 1.40]] },
    { id: 'bond:meta', label: 'Meta', points: [['2026-10-13', 0.90], ['2026-11-04', 0.85], ['2026-11-12', 0.80]] },
    { id: 'bond:late', label: 'Late', points: [['2026-10-30', 1.0], ['2026-11-12', 1.1]] }];
  const s = live.spreadSummary(live.changeLines(spreads, 30), ust.points);
  assert.equal(s.ref, -12);
  const text = live.spreadText(s);
  assert.equal(text, '2026-10-13 이후 미국채 10년물은 -12bp 움직였다. 가산금리가 넓어진 선은 Oracle +40bp(최근 8일은 다시 좁혀지는 중), ' +
    '투자등급 OAS +9bp(최근 8일에도 더 넓어지는 중)이다. 좁아진 선은 Meta -10bp(최근 8일에도 더 좁혀지는 중)이다. 기준일에 값이 없는 Late은 뺐다.');
});

test('색 장부: 켜진 회사끼리 색이 겹치지 않고, 두 차트가 같은 회사에 같은 색을 주며, 한쪽에서만 꺼도 색을 지킨다', () => {
  const book = live.colorBook();
  const a = book.take('bond:oracle');
  const b = book.take('bond:meta');
  // 켜는 순서대로 팔레트 앞쪽(가장 잘 구별되는) 색을 받는다.
  assert.deepEqual([a, b], live.PALETTE.slice(0, 2));
  assert.equal(book.take('bond:oracle'), a);
  book.drop('bond:oracle');
  assert.equal(book.color('bond:oracle'), a);
  book.drop('bond:oracle');
  assert.equal(book.color('bond:oracle'), null);
  assert.equal(book.take('bond:apple'), a);
  assert.equal(book.color('bond:meta'), b);
  // 열 곳을 켜도 색이 겹치지 않고, 쓰는 색은 팔레트 앞쪽 열 개다.
  const many = ['c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8'].map((id) => book.take(id));
  assert.deepEqual(new Set([a, b, ...many]), new Set(live.PALETTE.slice(0, 10)));
});

test('축 이름표: 기준 선은 짧은 이름, 회사채는 회사 이름만 쓴다', () => {
  assert.deepEqual(['ust10y', 'hy_oas', 'baa_spread', 'bond:oracle', 'bond:tsmc', 'x'].map(live.shortName),
    ['10년물', '하이일드', 'Baa−10년', 'Oracle', 'TSMC Arizona', '']);
});

test('CoreWeave 는 변화 폭이 커서 두 큰 차트에서 처음에 꺼 둔다', () => {
  const out = live.withMaturity([{ id: 'bond:coreweave', label: 'x', points: [], hidden: false }]);
  assert.equal(out[0].hidden, true);
  const pts = [['2026-11-12', 1]];
  const row = live.spreadRow({ series: {} }, { series: { 'bond:coreweave': { lines: [{ points: pts }] } } }, '2026-10-27');
  assert.equal(row.lines[0].hidden, true);
});
