// 국면 탭 시장 지표의 계산 정의와 추이 시계열을 한 곳에 둔다. 리포트는 차트를 그리고, finance 서버(맥미니)는 이 파일을 불러 매일 시계열을 쌓는다
// 계산 정의는 scripts/scorecard/market_now.py 와 같아야 한다(tests/test_market_now.py · tests/node/market_live.test.js 가 같은 고정 자료로 잠근다).
(function (root) {
  'use strict';

  var GPU_TYPES = ['H100 SXM', 'H200', 'B200'];
  var TOKEN_LABS = ['openai', 'anthropic', 'google', 'x-ai', 'deepseek', 'qwen', 'moonshotai'];
  var TOKEN_WINDOW_DAYS = 180;
  // FRED 의 ICE BofA OAS 두 계열은 최근 3년만 내준다. 무디스 Baa−10년물은 10년 추이용이다.
  var FRED_SERIES = [['ust10y_yield', 'DGS10'], ['baa_spread', 'BAA10Y'], ['ig_oas', 'BAMLC0A0CM'], ['hy_oas', 'BAMLH0A0HYM2']];
  var FRED_START = '2015-01-01';
  // 2026-11-15 사용자 요청: 미국채 10년물과 회사채 금리를 한 차트에서 본다. 스프레드가 아니라 금리 수준이라 같은 % 축에 놓인다.
  // ICE BofA 실효수익률 두 계열은 OAS 와 같이 최근 3년, 무디스 Baa(DBAA)는 2015년부터다.
  // 이름에 만기를 붙인다. 금리 수준은 만기가 다르면 신용 차이와 만기 차이가 섞이므로 어느 만기인지 이름에서 보이게 한다.
  var FRED_YIELDS = [['ig', 'BAMLC0A0CMEY', '투자등급 회사채(ICE 지수, 여러 만기)'], ['baa', 'DBAA', '무디스 Baa 회사채(만기 20년 이상)'],
    ['hy', 'BAMLH0A0HYM2EY', '하이일드 회사채(ICE 지수, 여러 만기)']];
  var FRED_FETCH = FRED_SERIES.map(function (p) { return p[1]; }).concat(FRED_YIELDS.map(function (p) { return p[1]; }));
  // 큰 차트의 선 색(dataviz 기본 범주 팔레트의 어두운 화면 값, 리포트 배경 #161a22 에서 검증 통과). 아홉째 선부터는 같은 색의 점선이다.
  var PALETTE = ['#3987e5', '#d95926', '#199e70', '#c98500', '#d55181', '#0ca30c', '#9085e9', '#e66767'];
  // 금리 한눈에·가산금리 한눈에 차트에 붙는 회사별 채권 가운데 처음에 끈 것. 지수 선과 합쳐 선이 열셋·열넷이라, 신용도가 갈리는
  // CoreWeave·Oracle·Meta 만 켜 두고 나머지는 범례로 켠다.
  var BOND_YIELD_HIDDEN = ['bond:microsoft', 'bond:alphabet', 'bond:amazon', 'bond:apple', 'bond:nvidia', 'bond:alibaba', 'bond:tsmc'];
  // GetDeploying 무료 데이터(CC BY 4.0)의 GPU 이름. 공급자 여러 곳의 호가 중간값이라 우리 vast.ai 정의와 다른 숫자다.
  var GETDEPLOYING_SLUGS = { 'H100 SXM': 'nvidia-h100', 'H200': 'nvidia-h200', 'B200': 'nvidia-b200' };
  var TOKEN_RECON_START = '2025-07-07';
  var OPENROUTER_URL = 'https://openrouter.ai/api/v1/models';
  // 한국은행 ECOS 수출물가지수(품목별) D램, 달러 기준(2020=100) 월별. 환율 효과를 뺀 수출 계약 가격이다.
  var ECOS_DRAM = { table: '402Y016', item: '30911201AA', basis: 'D', start: '201501' };
  // 아래 두 원천은 약관이 게시를 막아 로그인한 사람에게만 보인다(BondTerminal 무료 키는 게시·표시 금지, DRAMeXchange 는 사전 동의 없는 표시 금지).
  // 회사채는 회사마다 대표 채권 하나의 국채 대비 가산금리(G-spread)다. BondTerminal 에 실린 대상은 CoreWeave·Oracle·Meta 뿐이다.
  var BONDS = [
    { key: 'bond:coreweave', isin: 'US21873SAB43', title: 'CoreWeave 9.25% 2030 가산금리' },
    { key: 'bond:oracle', isin: 'US68389XCE31', title: 'Oracle 2.875% 2031 가산금리' },
    { key: 'bond:meta', isin: 'US30303M8N52', title: 'Meta 4.95% 2033 가산금리' },
    // 2026-11-15 사용자 요청: BondTerminal 에 있는 나머지 채점 대상 회사. 비교가 되게 2031년 만기 고정금리 채권을 고르고,
    // 2031년물이 목록에 없는 Microsoft 만 가장 가까운 2035년물이다. Tesla·Palantir·SpaceX-xAI·Anthropic·OpenAI 는 목록에 없다.
    // 한 채권에 하루 10단위라 열 채권이 하루 100단위다(무료 한도 200).
    { key: 'bond:microsoft', isin: 'US594918BC73', title: 'Microsoft 3.5% 2035 가산금리' },
    { key: 'bond:alphabet', isin: 'US02079KBK25', title: 'Alphabet 4.1% 2031 가산금리' },
    { key: 'bond:amazon', isin: 'US023135DD51', title: 'Amazon 4.25% 2031 가산금리' },
    { key: 'bond:apple', isin: 'US037833FG02', title: 'Apple 4.9% 2031 가산금리' },
    { key: 'bond:nvidia', isin: 'US67066GAR56', title: 'NVIDIA 4.5% 2031 가산금리' },
    { key: 'bond:alibaba', isin: 'US01609WAX02', title: 'Alibaba 2.125% 2031 가산금리' },
    { key: 'bond:tsmc', isin: 'US872898AC52', title: 'TSMC Arizona 2.5% 2031 가산금리' }
  ];

  // 큰 차트 범례의 이름. 채권은 "Oracle 2.875% 2031년 만기" 처럼 만기를 드러낸다. 서버 파일에 옛 이름이 남아 있어도 화면은 이 이름을 쓴다.
  function bondName(key) {
    var b = BONDS.filter(function (x) { return x.key === key; })[0];
    return b ? b.title.replace(/ 가산금리$/, '').replace(/ (\d{4})$/, ' $1년 만기') : null;
  }

  function withMaturity(lines) {
    return lines.map(function (l) {
      var y = FRED_YIELDS.filter(function (p) { return p[0] === l.id; })[0];
      var name = y ? y[2] : bondName(l.id);
      if (!name) return l;
      var out = {};
      Object.keys(l).forEach(function (k) { out[k] = l[k]; });
      out.label = name;
      return out;
    });
  }
  // 2026-11-15: BondTerminal 은 한 요청의 기간이 730일을 넘으면 400 을 낸다(2015-01-01 부터 한 번에 받던 요청이 전부 실패했다).
  // 매일 최근 729일을 받아 직전 시계열과 날짜로 합치므로 날이 갈수록 2년보다 긴 기록이 쌓인다.
  // var BOND_START = '2015-01-01';
  var BOND_WINDOW_DAYS = 729;
  var BONDTERMINAL_API = 'https://bondterminal.com/api/v1';
  // 과거 차트는 유료 회원 전용이라 첫 화면 표의 세션 평균을 날마다 쌓는다.
  var DRAMX_URL = 'https://www.dramexchange.com/';
  var DRAMX_ITEM = 'DDR5 16Gb (2Gx8) 4800/5600';
  var MONTHS = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'];
  var SERIES_URL = '/reports/market-series.json';
  var PRIVATE_URL = '/api/market-private';
  var LWC_URL = 'https://cdn.jsdelivr.net/npm/lightweight-charts@5.2.1/dist/lightweight-charts.standalone.production.js';
  var LWC_SRI = 'sha384-KkYqTZlM13Zya6fVUF3IGCBOQ1ehFeJVVgxaVvD/0MebineF9EI8Jkd3NnWNChqN';
  var DAY_MS = 86400000;

  function median(values) {
    if (!values.length) return null;
    var xs = values.slice().sort(function (a, b) { return a - b; });
    var mid = Math.floor(xs.length / 2);
    return xs.length % 2 ? xs[mid] : (xs[mid - 1] + xs[mid]) / 2;
  }

  // GPU 한 장 시간당 단가(dph_total ÷ num_gpus)의 GPU 수 가중 중간값.
  function gpuRent(offers) {
    var prices = [];
    var count = 0;
    (offers || []).forEach(function (o) {
      var n = o.num_gpus;
      var dph = o.dph_total;
      if (typeof n !== 'number' || !Number.isInteger(n) || n <= 0 || typeof dph !== 'number') return;
      for (var i = 0; i < n; i += 1) prices.push(dph / n);
      count += 1;
    });
    var value = median(prices);
    return value === null ? null : { value: value, gpus: prices.length, offers: count };
  }

  function usdPerM(raw) {
    if (raw === null || raw === undefined || raw === '') return null;
    var v = Number(raw);
    return Number.isFinite(v) && v > 0 ? v * 1e6 : null;
  }

  function utcDay(ms) { return new Date(ms).toISOString().slice(0, 10); }

  // 연구소마다 최근 180일 안에 나온 비배치 유료 텍스트 모델 가운데 혼합 단가(입력 3 : 출력 1)가 가장 높은 것.
  // 같으면 더 최근 모델, 그것도 같으면 이름이 앞선 모델이다.
  function tokenPicks(models, ref) {
    var refMs = Date.parse(ref + 'T00:00:00Z');
    var floor = utcDay(refMs - TOKEN_WINDOW_DAYS * DAY_MS);
    var best = {};
    (models || []).forEach(function (m) {
      var id = m.id || '';
      var lab = id.split('/')[0];
      if (TOKEN_LABS.indexOf(lab) < 0 || id.indexOf(':') >= 0) return;
      var out = (m.architecture || {}).output_modalities;
      if (!Array.isArray(out) || out.length !== 1 || out[0] !== 'text') return;
      var created = m.created;
      if (typeof created !== 'number') return;
      var made = utcDay(created * 1000);
      if (made < floor || made > ref) return;
      var pricing = m.pricing || {};
      var pi = usdPerM(pricing.prompt);
      var po = usdPerM(pricing.completion);
      if (pi === null || po === null) return;
      var blended = (3 * pi + po) / 4;
      var cur = best[lab];
      if (!cur || blended > cur.blended ||
          (blended === cur.blended && (created > cur.created || (created === cur.created && id < cur.model)))) {
        best[lab] = { lab: lab, model: id, blended: blended, created: created };
      }
    });
    return TOKEN_LABS.filter(function (lab) { return best[lab]; })
      .map(function (lab) { return { lab: lab, model: best[lab].model, blended: best[lab].blended }; });
  }

  // FRED API(series/observations, 최신순)의 첫 유효 값. "." 는 값이 없는 날이다.
  function fredLatest(payload) {
    var rows = (payload && payload.observations) || [];
    for (var i = 0; i < rows.length; i += 1) {
      var raw = rows[i].value;
      if (raw && raw !== '.') return { date: rows[i].date, value: Number(raw) };
    }
    return null;
  }

  function byDate(a, b) { return a[0] < b[0] ? -1 : (a[0] > b[0] ? 1 : 0); }

  // 같은 날짜는 뒤의 것 하나만 남기고 날짜 오름차순으로 둔다(차트는 시각이 겹치거나 거꾸로 가면 그리지 않는다).
  function sortPoints(points) {
    var by = {};
    points.forEach(function (p) { by[p[0]] = p; });
    return Object.keys(by).sort().map(function (k) { return by[k]; });
  }

  // FRED fredgraph.csv(observation_date,<계열>) → [[날짜, 값]]. 빈 칸과 "." 는 값이 없는 날이다.
  function parseFredCsv(text) {
    var out = [];
    String(text || '').split(/\r?\n/).forEach(function (line, i) {
      if (!i || !line) return;
      var parts = line.split(',');
      var raw = (parts[1] || '').trim();
      var v = Number(raw);
      if (raw && raw !== '.' && Number.isFinite(v)) out.push([parts[0].trim(), v]);
    });
    return sortPoints(out.sort(byDate));
  }

  // GetDeploying 주간 CSV → 약정 없는 on-demand 행의 [[주 시작일, 중간값]]. 열은 머리글 이름으로 찾는다.
  function parseGetDeployingCsv(text) {
    var lines = String(text || '').split(/\r?\n/).filter(Boolean);
    if (!lines.length) return [];
    var head = lines[0].split(',').map(function (h) { return h.trim(); });
    var d = head.indexOf('date');
    var bt = head.indexOf('billing_type');
    var rm = head.indexOf('reservation_months');
    var mp = head.indexOf('median_price');
    if (d < 0 || bt < 0 || mp < 0) return [];
    var out = [];
    lines.slice(1).forEach(function (line) {
      var c = line.split(',');
      if (c[bt] !== 'ON_DEMAND' || (rm >= 0 && c[rm])) return;
      var v = Number(c[mp]);
      if (c[mp] !== '' && Number.isFinite(v) && v > 0) out.push([c[d], v]);
    });
    return sortPoints(out);
  }

  function addDays(iso, n) { return utcDay(Date.parse(iso + 'T00:00:00Z') + n * DAY_MS); }

  // OpenRouter 지금 목록을 과거 날짜에 대입한 토큰 단가(주별). 사라진 모델과 가격 인하가 빠지므로 우리 정의 선과 잇지 않는다.
  function reconstructTokens(models, start, end) {
    var out = [];
    for (var d = start; d <= end; d = addDays(d, 7)) {
      var v = median(tokenPicks(models, d).map(function (p) { return p.blended; }));
      if (v !== null) out.push([d, v]);
    }
    return out;
  }

  // 하루 한 번 찍는 우리 정의 값. 받지 못한 원천은 null 이다(0 이 아니다).
  function dailyPoint(offersByGpu, models, today) {
    var gpu = {};
    GPU_TYPES.forEach(function (g) {
      var offers = offersByGpu ? offersByGpu[g] : null;
      var rent = offers ? gpuRent(offers) : null;
      gpu[g] = rent ? { value: rent.value, gpus: rent.gpus, offers: rent.offers } : null;
    });
    var picks = models ? tokenPicks(models, today) : [];
    return { date: today, gpu: gpu, token: median(picks.map(function (p) { return p.blended; })), labs: picks.length };
  }

  // 같은 날 다시 찍으면 이번에 받은 값으로 바꾸되, 이번에 받지 못한 칸은 먼저 받은 값을 지킨다.
  function mergeDaily(history, point) {
    var prev = null;
    var rest = (history || []).filter(function (p) {
      if (p.date === point.date) { prev = p; return false; }
      return true;
    });
    var merged = point;
    if (prev) {
      var gpu = {};
      GPU_TYPES.forEach(function (g) { gpu[g] = point.gpu[g] || (prev.gpu || {})[g] || null; });
      var keep = point.token === null || point.token === undefined;
      merged = { date: point.date, gpu: gpu, token: keep ? prev.token : point.token, labs: keep ? prev.labs : point.labs };
    }
    return rest.concat([merged]).sort(function (a, b) { return a.date < b.date ? -1 : (a.date > b.date ? 1 : 0); });
  }

  // ECOS StatisticSearch 응답 → [[그달 1일, 지수]]. 오류 응답(RESULT)이면 빈 목록이다.
  function parseEcos(payload) {
    var rows = (payload && payload.StatisticSearch && payload.StatisticSearch.row) || [];
    var out = [];
    rows.forEach(function (r) {
      var t = String(r.TIME || '');
      var v = Number(r.DATA_VALUE);
      if (r.ITEM_CODE2 === ECOS_DRAM.basis && /^\d{6}$/.test(t) && r.DATA_VALUE !== '' && Number.isFinite(v)) {
        out.push([t.slice(0, 4) + '-' + t.slice(4, 6) + '-01', v]);
      }
    });
    return sortPoints(out);
  }

  // BondTerminal /bonds/{isin}/history → [[날짜, 가산금리 %p]]. 가산금리는 bp 정수로 온다.
  function parseBondHistory(payload) {
    var out = [];
    ((payload && payload.series) || []).forEach(function (p) {
      if (p && typeof p.date === 'string' && typeof p.spread === 'number') out.push([p.date, p.spread / 100]);
    });
    return sortPoints(out);
  }

  // 채권 금리(%). 조기상환 조건이 있는 채권은 만기·조기상환 가운데 낮은 쪽 수익률(ytw)이고, 없으면 만기수익률(ytm)이다.
  function parseBondYield(payload) {
    var out = [];
    ((payload && payload.series) || []).forEach(function (p) {
      var y = p && (typeof p.ytw === 'number' ? p.ytw : p.ytm);
      if (p && typeof p.date === 'string' && typeof y === 'number') out.push([p.date, y]);
    });
    return sortPoints(out);
  }

  // DRAMeXchange 첫 화면의 DRAM 현물 표에서 DDR5 16Gb 4800/5600 세션 평균과 표의 갱신 날짜(대만 시각)를 읽는다.
  function parseDramx(html) {
    var t = String(html || '');
    var mark = '<!-- DRAM Spot Price -->';
    var start = t.indexOf(mark);
    var end = start < 0 ? -1 : t.indexOf(mark, start + mark.length);
    if (end < 0) return null;
    var block = t.slice(start, end);
    var m = /Last Update:\s*([A-Za-z]{3})[a-z]*\.?\s*(\d{1,2})\s+(\d{4})/.exec(block);
    var mon = m ? MONTHS.indexOf(m[1].toLowerCase()) : -1;
    var i = block.indexOf(DRAMX_ITEM);
    if (mon < 0 || i < 0) return null;
    var row = block.slice(i, block.indexOf('</tr>', i));
    var cells = [];
    var re = /<td[^>]*>([\s\S]*?)<\/td>/g;
    var c;
    while ((c = re.exec(row))) cells.push(c[1].replace(/<[^>]+>/g, '').trim());
    // 품목 이름 칸 뒤의 순서: Daily High, Daily Low, Session High, Session Low, Session Average, Session Change, History
    var avg = Number(cells[4]);
    if (cells[4] === undefined || cells[4] === '' || !Number.isFinite(avg) || avg <= 0) return null;
    function pad(n) { return (n < 10 ? '0' : '') + n; }
    return { date: m[3] + '-' + pad(mon + 1) + '-' + pad(Number(m[2])), value: avg };
  }

  // 날마다 쌓는 점에 새 점 하나를 더한다. 같은 날짜면 새 값으로 바꾼다.
  function addPoint(points, point) {
    var pts = (points || []).slice();
    if (point) pts.push([point.date, point.value]);
    return sortPoints(pts);
  }

  // 로그인한 사람에게만 내보내는 시계열. 받지 못한 채권은 직전 선을 그대로 쓴다.
  function mergePoints(old, fresh) {
    var byDate = {};
    old.concat(fresh).forEach(function (p) { byDate[p[0]] = p; });
    return Object.keys(byDate).sort().map(function (d) { return byDate[d]; });
  }

  function assemblePrivate(input) {
    var previous = (input.previous && input.previous.series) || {};
    var series = {};
    BONDS.forEach(function (b) {
      var payload = (input.bonds || {})[b.isin];
      var pts = payload ? parseBondHistory(payload) : [];
      var prev = (((previous[b.key] || {}).lines) || [])[0] || null;
      // 새로 받은 창(최근 729일)을 직전 선과 날짜로 합친다. 같은 날짜는 새 값을 쓴다.
      var line = pts.length ? { id: 'bondterminal', label: 'BondTerminal 국채 대비 가산금리', points: mergePoints(prev ? prev.points : [], pts) }
        : prev;
      if (line) series[b.key] = { title: b.title, kind: 'pct', unit: '%p', lines: [line] };
    });
    // 회사채 금리 큰 차트. 미국채 10년물 선은 공개 시계열에 있어 브라우저가 맨 앞에 붙인다.
    var prevYields = ((previous.bond_yields || {}).lines) || [];
    var yieldLines = [];
    BONDS.forEach(function (b) {
      var payload = (input.bonds || {})[b.isin];
      var pts = payload ? parseBondYield(payload) : [];
      var prev = prevYields.filter(function (l) { return l.id === b.key; })[0] || null;
      var merged = mergePoints(prev ? prev.points : [], pts);
      if (merged.length) yieldLines.push({ id: b.key, label: b.title.replace(/ 가산금리$/, ''), points: merged, hidden: BOND_YIELD_HIDDEN.indexOf(b.key) >= 0 });
    });
    if (yieldLines.length) {
      series.bond_yields = { title: '회사채 금리(YTW)와 미국채 10년물', kind: 'pct', unit: '%', big: true, lines: yieldLines };
    }
    var dram = input.dram || [];
    if (dram.length) {
      series.dram_spot = { title: 'D램 현물가 DDR5 16Gb 4800/5600', kind: 'usd', unit: '$',
        lines: [{ id: 'dramexchange', label: 'DRAMeXchange 세션 평균', points: dram }] };
    }
    return { schema: 'market-private/1', updated_at: input.now, series: series, errors: (input.errors || []).slice() };
  }

  // 서버가 내보내는 시계열. 지표 열쇠는 리포트 표 행의 data-key 와 같다.
  // 표에 없는 시계열(title 이 있는 것)은 차트만 그린다.
  // 이번에 받지 못한 외부 원천(fred·getdeploying 의 본문이 null)은 직전 시계열(previous)의 선을 그대로 쓴다.
  function assemble(input) {
    var previous = (input.previous && input.previous.series) || {};
    function prevLine(key, id) {
      var lines = (previous[key] && previous[key].lines) || [];
      return lines.filter(function (l) { return l.id === id; })[0] || null;
    }
    var errors = (input.errors || []).slice();
    var series = {};
    FRED_SERIES.forEach(function (pair) {
      var text = (input.fred || {})[pair[1]];
      var line = text ? { id: 'fred', label: 'FRED ' + pair[1], points: parseFredCsv(text) } : prevLine(pair[0], 'fred');
      series[pair[0]] = { lines: line ? [line] : [] };
    });
    // 금리 한눈에: 미국채 10년물과 회사채 금리 세 계열을 같은 % 축에. 받지 못한 계열은 직전 선을 쓴다.
    var ust = (series.ust10y_yield.lines[0] || null);
    var yieldLines = ust ? [{ id: 'ust10y', label: '미국채 10년물', points: ust.points }] : [];
    FRED_YIELDS.forEach(function (y) {
      var text = (input.fred || {})[y[1]];
      var line = text ? { id: y[0], label: y[2], points: parseFredCsv(text) } : prevLine('yields', y[0]);
      if (line && line.points.length) yieldLines.push(line);
    });
    if (yieldLines.length) series.yields = { title: '금리 한눈에: 미국채 10년물과 회사채', kind: 'pct', unit: '%', big: true, lines: yieldLines };
    var daily = input.daily || [];
    GPU_TYPES.forEach(function (g) {
      var key = 'gpu_rent_hourly:' + g;
      var ours = daily.filter(function (p) { return p.gpu && p.gpu[g]; }).map(function (p) { return [p.date, p.gpu[g].value]; });
      var lines = [{ id: 'ours', label: 'vast.ai 호가(이 리포트 정의)', points: ours }];
      var gd = (input.getdeploying || {})[g];
      var ext = gd ? { id: 'getdeploying', label: 'GetDeploying 주간 중간값(형태 구분 없음)', dashed: true, points: parseGetDeployingCsv(gd) }
        : prevLine(key, 'getdeploying');
      if (ext) lines.push(ext);
      series[key] = { lines: lines };
    });
    var tok = daily.filter(function (p) { return p.token !== null && p.token !== undefined; }).map(function (p) { return [p.date, p.token]; });
    var tokLines = [{ id: 'ours', label: 'OpenRouter(이 리포트 정의)', points: tok }];
    var recon = input.models
      ? { id: 'reconstructed', label: '재구성(지금 목록을 과거에 대입)', dashed: true, points: reconstructTokens(input.models, TOKEN_RECON_START, input.today) }
      : prevLine('token_blended_price', 'reconstructed');
    if (recon) tokLines.push(recon);
    series.token_blended_price = { lines: tokLines };
    // ECOS 키가 없으면 서버가 ecos 를 넘기지 않는다(실패가 아니다). 받았는데 값이 없으면 오류로 적고 직전 선을 쓴다.
    var ecosPts = input.ecos ? parseEcos(input.ecos) : null;
    if (ecosPts && !ecosPts.length) errors.push('ECOS: 값이 없다(' + ((input.ecos.RESULT || {}).CODE || '응답 형식') + ')');
    var ecosLine = ecosPts && ecosPts.length ? { id: 'ecos', label: '한국은행 ECOS 402Y016', points: ecosPts } : prevLine('dram_export_index', 'ecos');
    if (ecosLine) {
      series.dram_export_index = { title: 'D램 수출물가지수(달러 기준, 2020=100)', kind: 'index', unit: '', lines: [ecosLine] };
    }
    return { schema: 'market-series/1', updated_at: input.now, series: series, errors: errors };
  }

  function ecosUrl(key, today) {
    var end = today.slice(0, 4) + today.slice(5, 7);
    return 'https://ecos.bok.or.kr/api/StatisticSearch/' + encodeURIComponent(key) + '/json/kr/1/1000/' +
      ECOS_DRAM.table + '/M/' + ECOS_DRAM.start + '/' + end + '/' + ECOS_DRAM.item + '/' + ECOS_DRAM.basis;
  }

  function bondHistoryUrl(isin, today) {
    return BONDTERMINAL_API + '/bonds/' + isin + '/history?start=' + addDays(today, -BOND_WINDOW_DAYS) + '&end=' + today;
  }

  function vastUrl(gpu) {
    var q = { gpu_name: { eq: gpu }, rentable: { eq: true }, type: 'on-demand', limit: 500 };
    return 'https://console.vast.ai/api/v0/bundles/?q=' + encodeURIComponent(JSON.stringify(q));
  }

  function fredCsvUrl(series, start, end) {
    return 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=' + series + '&cosd=' + start + '&coed=' + end;
  }

  function getDeployingUrl(gpu) {
    return 'https://getdeploying.com/dataset/gpu-prices/' + GETDEPLOYING_SLUGS[gpu] + '.csv';
  }

  function failText(err) {
    var code = err && err.status;
    if (code === 404) return '시계열을 찾지 못했다. 공개 사이트의 리포트 주소에서 열어야 받는다.';
    if (err && err.lwc) return '차트 라이브러리를 불러오지 못했다. 연결을 확인하고 다시 눌러 보라.';
    return code ? '시계열을 받지 못했다(응답 ' + code + '). 다시 눌러 보라.' : '시계열을 받지 못했다. 연결을 확인하고 다시 눌러 보라.';
  }

  function getJson(url) {
    return fetch(url, { cache: 'no-store' }).then(function (r) {
      if (!r.ok) { var e = new Error('HTTP ' + r.status); e.status = r.status; throw e; }
      return r.json();
    });
  }

  function valueText(row, value) {
    if (row.kind === 'pct') return value.toFixed(2) + row.unit;
    if (row.kind === 'index') return value.toFixed(1);
    return '$' + value.toFixed(2);
  }

  function changeText(row, base, now) {
    if (base === null || base === undefined) return '—';
    if (row.kind === 'pct') {
      var bp = Math.round((now - base) * 100);
      return (bp > 0 ? '+' : '') + bp + 'bp';
    }
    var pct = (now / base - 1) * 100;
    return (pct > 0 ? '+' : '') + pct.toFixed(1) + '%';
  }

  // ---------------------------------------------------------------- 변화(bp) 보기: 기준일을 0 으로 놓고 엇갈림을 읽는다
  // 2026-11-15 사용자 요청: 10년물은 내려가는데 회사채는 올라가는 흐름이 이어지는지를 한눈에 보려고 한다.

  var CHANGE_RANGES = [['1개월', 30], ['3개월', 91], ['6개월', 182], ['1년', 365]];
  // 기준일에 값이 없으면 그 뒤 첫 점을 쓰는데, 주말·연휴만 넘긴다. 자료가 그보다 늦게 시작한 선은 기준이 달라 뺀다.
  var BASE_SLACK_DAYS = 7;
  // 이보다 작은 움직임은 방향으로 치지 않는다(bp).
  var FLAT_BP = 2;

  function round2(v) { return Math.round(v * 100) / 100; }

  // 모든 선의 마지막 날 가운데 가장 늦은 날에서 days 만큼 거슬러 간 날이 기준일이다.
  // 선마다 기준일 이후 첫 점을 0 으로 놓고 그 뒤를 bp 로 바꾼다. 기준일에서 BASE_SLACK_DAYS 안에 점이 없으면 excluded 다.
  function changeLines(lines, days) {
    var end = null;
    lines.forEach(function (l) {
      var p = l.points[l.points.length - 1];
      if (p && (end === null || p[0] > end)) end = p[0];
    });
    if (end === null) return { base: null, end: null, lines: [] };
    var base = addDays(end, -days);
    var limit = addDays(base, BASE_SLACK_DAYS);
    return { base: base, end: end, lines: lines.map(function (l) {
      var i = 0;
      while (i < l.points.length && l.points[i][0] < base) i += 1;
      var start = l.points[i];
      if (!start || start[0] > limit) return { id: l.id, label: l.label, excluded: true, points: [] };
      var pts = l.points.slice(i).map(function (p) { return [p[0], round2((p[1] - start[1]) * 100)]; });
      return { id: l.id, label: l.label, excluded: false, from: start[0], points: pts, change: pts[pts.length - 1][1] };
    }) };
  }

  function valueAt(points, date) {
    var v = null;
    for (var i = 0; i < points.length && points[i][0] <= date; i += 1) v = points[i][1];
    return v;
  }

  function dirOf(bp) { return bp >= FLAT_BP ? 1 : (bp <= -FLAT_BP ? -1 : 0); }

  // 첫 선(미국채 10년물)을 기준으로 다른 선의 변화·10년물 대비 차이(gap)를 잰다.
  // recent 는 마지막 4분의 1 구간(최소 7일)에서 차이가 더 움직인 폭이고, 엇갈림이 이어지는지를 본다.
  function divergence(view) {
    var ref = view.lines[0];
    if (!ref || ref.excluded) return null;
    var span = Math.round((Date.parse(view.end) - Date.parse(view.base)) / DAY_MS);
    var recentDays = Math.max(7, Math.round(span / 4));
    var cut = addDays(view.end, -recentDays);
    var refCut = valueAt(ref.points, cut);
    var items = view.lines.slice(1).filter(function (l) { return !l.excluded; }).map(function (l) {
      var lineCut = valueAt(l.points, cut);
      var recent = lineCut === null || refCut === null ? null : round2((l.change - lineCut) - (ref.change - refCut));
      return { id: l.id, label: l.label, change: l.change, gap: round2(l.change - ref.change), recent: recent,
        opposite: dirOf(l.change) !== 0 && dirOf(ref.change) !== 0 && dirOf(l.change) !== dirOf(ref.change) };
    });
    return { base: view.base, ref: { label: ref.label, change: ref.change }, recentDays: recentDays, items: items,
      excluded: view.lines.filter(function (l) { return l.excluded; }).map(function (l) { return l.label; }) };
  }

  function bpText(v) {
    var r = Math.round(v);
    return (r > 0 ? '+' : '') + r + 'bp';
  }

  function trendText(item, days) {
    if (item.recent === null) return '';
    var g = dirOf(item.gap);
    var r = dirOf(item.recent);
    if (g === 0 || r === 0) return ', 최근 ' + days + '일은 거의 그대로';
    return g === r ? ', 최근 ' + days + '일에도 더 벌어지는 중' : ', 최근 ' + days + '일은 좁혀지는 중';
  }

  // 10년물과 반대로 움직인 선을 모두 적는다. 없으면 10년물 대비 가장 많이 벌어진 선 하나를 적는다.
  function divergenceText(d) {
    if (!d) return '기준일에 미국채 10년물 값이 없어 엇갈림을 읽지 못했다.';
    var opp = d.items.filter(function (i) { return i.opposite; });
    var pick = opp.length ? opp : d.items.slice().sort(function (a, b) { return Math.abs(b.gap) - Math.abs(a.gap); }).slice(0, 1);
    var body = pick.map(function (i) {
      return i.label + ' ' + bpText(i.change) + '(10년물 대비 ' + bpText(i.gap) + trendText(i, d.recentDays) + ')';
    }).join(', ');
    var text = d.base + ' 이후 ' + d.ref.label + '은 ' + bpText(d.ref.change) + ' 움직였다. ';
    if (opp.length) text += '10년물과 반대로 움직인 선은 ' + body + '이다.';
    else if (pick.length) text += '10년물과 반대로 움직인 선은 없고, 10년물 대비 가장 많이 벌어진 선은 ' + body + '이다.';
    else text += '비교할 다른 선이 없다.';
    if (d.excluded.length) text += ' 기준일에 값이 없는 ' + d.excluded.join('·') + '은 뺐다.';
    return text;
  }

  // 가산금리 차트의 요약 재료. 가산금리는 같은 만기 국채와 비교한 값이라 선끼리 기준이 같다.
  // 선마다 기준일 이후 변화와 마지막 4분의 1 구간(최소 7일)의 변화를 재고, 같은 기간 미국채 10년물의 변화(ref)를 덧붙인다.
  function spreadSummary(view, refPoints) {
    var span = Math.round((Date.parse(view.end) - Date.parse(view.base)) / DAY_MS);
    var recentDays = Math.max(7, Math.round(span / 4));
    var cut = addDays(view.end, -recentDays);
    var ref = null;
    var pts = refPoints || [];
    var i = 0;
    while (i < pts.length && pts[i][0] < view.base) i += 1;
    if (pts[i] && pts[i][0] <= addDays(view.base, BASE_SLACK_DAYS)) ref = round2((pts[pts.length - 1][1] - pts[i][1]) * 100);
    var items = view.lines.filter(function (l) { return !l.excluded; }).map(function (l) {
      var lineCut = valueAt(l.points, cut);
      return { id: l.id, label: l.label, change: l.change, recent: lineCut === null ? null : round2(l.change - lineCut) };
    });
    return { base: view.base, recentDays: recentDays, ref: ref, items: items,
      excluded: view.lines.filter(function (l) { return l.excluded; }).map(function (l) { return l.label; }) };
  }

  function spreadTrend(item, days) {
    if (item.recent === null) return '';
    var r = dirOf(item.recent);
    if (r === 0) return '(최근 ' + days + '일은 거의 그대로)';
    if (r > 0) return item.change > 0 ? '(최근 ' + days + '일에도 더 넓어지는 중)' : '(최근 ' + days + '일은 다시 넓어지는 중)';
    return item.change < 0 ? '(최근 ' + days + '일에도 더 좁혀지는 중)' : '(최근 ' + days + '일은 다시 좁혀지는 중)';
  }

  // 넓어진 선과 좁아진 선을 큰 순서로 모두 적는다. 2bp 미만은 그대로로 친다.
  function spreadText(s) {
    var one = function (i) { return i.label + ' ' + bpText(i.change) + spreadTrend(i, s.recentDays); };
    var wide = s.items.filter(function (i) { return dirOf(i.change) > 0; }).sort(function (a, b) { return b.change - a.change; });
    var narrow = s.items.filter(function (i) { return dirOf(i.change) < 0; }).sort(function (a, b) { return a.change - b.change; });
    var text = s.base + ' 이후 ' + (s.ref === null ? '미국채 10년물 값은 기준일에 없다. ' : '미국채 10년물은 ' + bpText(s.ref) + ' 움직였다. ');
    text += wide.length ? '가산금리가 넓어진 선은 ' + wide.map(one).join(', ') + '이다.' : '가산금리가 넓어진 선은 없다.';
    if (narrow.length) text += ' 좁아진 선은 ' + narrow.map(one).join(', ') + '이다.';
    if (s.excluded.length) text += ' 기준일에 값이 없는 ' + s.excluded.join('·') + '은 뺐다.';
    return text;
  }

  // 같은 만기 국채와 비교한 가산금리를 한 차트에 모은다. 공개 계열(ICE OAS 둘, Baa−10년물)에 로그인하면 회사별 G-spread 를 더한다.
  // Baa−10년물은 20년 이상 채권에서 10년 국채를 뺀 값이라 만기가 맞지 않아 처음에는 끈다.
  function spreadRow(data, priv, asOf) {
    var series = data.series || {};
    var first = function (key) { return (((series[key] || {}).lines) || [])[0] || null; };
    var lines = [];
    [['ig_oas', '투자등급 OAS(ICE 지수, 여러 만기)', false], ['hy_oas', '하이일드 OAS(ICE 지수, 여러 만기)', false],
      ['baa_spread', '무디스 Baa−10년물(만기 안 맞음)', true]].forEach(function (p) {
      var l = first(p[0]);
      if (l) lines.push({ id: p[0], label: p[1], points: l.points, hidden: p[2] });
    });
    var ps = (priv && priv.series) || {};
    BONDS.forEach(function (b) {
      var l = (((ps[b.key] || {}).lines) || [])[0];
      if (l) lines.push({ id: b.key, label: bondName(b.key) + ' G-spread', points: l.points, hidden: BOND_YIELD_HIDDEN.indexOf(b.key) >= 0 });
    });
    var ust = first('ust10y_yield');
    return { key: 'spreads', kind: 'pct', unit: '%p', asOf: asOf, big: true, change: 'spread', lines: lines,
      ref: ust ? ust.points : [], label: '가산금리 한눈에: 같은 만기 국채 대비(회사별 채권 선은 로그인한 사람에게만 보인다)' };
  }

  // ---------------------------------------------------------------- 브라우저: 지금 값 칸과 추이 차트

  var RANGES = [['1년', 365], ['3년', 1095], ['10년', 3650]];

  function loadLwc(doc) {
    if (root.LightweightCharts) return Promise.resolve(root.LightweightCharts);
    return new Promise(function (resolve, reject) {
      var s = doc.createElement('script');
      s.src = LWC_URL;
      s.integrity = LWC_SRI;
      s.crossOrigin = 'anonymous';
      s.onload = function () { resolve(root.LightweightCharts); };
      s.onerror = function () { var e = new Error('lwc'); e.lwc = true; reject(e); };
      doc.head.appendChild(s);
    });
  }

  function token(doc, name, fallback) {
    var v = root.getComputedStyle(doc.documentElement).getPropertyValue(name).trim();
    return v || fallback;
  }

  // 지금 값은 첫 선(이 리포트 정의 또는 FRED)의 마지막 점이다. 정의가 다른 외부 선으로 채우지 않는다.
  function fillNow(rows, data) {
    var filled = 0;
    rows.forEach(function (row) {
      var lines = (data.series[row.key] || {}).lines || [];
      var pts = lines.length ? lines[0].points : [];
      var nowCell = row.tr.querySelector('.mkt-now');
      // 시장 관측이 없는 실행의 표에는 변화 칸이 없다.
      var chgCell = row.tr.querySelector('.mkt-chg');
      if (!pts.length) {
        nowCell.textContent = '아직 쌓인 값이 없다';
        if (chgCell) chgCell.textContent = '—';
        return;
      }
      var last = pts[pts.length - 1];
      filled += 1;
      nowCell.textContent = valueText(row, last[1]) + ' (' + last[0] + ')';
      if (chgCell) chgCell.textContent = changeText(row, row.base, last[1]);
    });
    return filled;
  }

  function lineKey(doc, color, dashed) {
    var k = doc.createElement('span');
    k.className = 'lk' + (dashed ? ' dash' : '');
    k.style.borderTopColor = color;
    return k;
  }

  function drawCharts(doc, box, data, LWC, rows) {
    box.textContent = '';
    var colors = [token(doc, '--mkt-a', '#4f97e6'), token(doc, '--mkt-b', '#c97a38')];
    var font = root.getComputedStyle(doc.body).fontFamily;
    var charts = [];
    rows.forEach(function (row) {
      var lines = (row.lines || (data.series[row.key] || {}).lines || []).filter(function (l) { return l.points.length; });
      // 큰 차트(여러 계열을 한 축에)는 범주 팔레트로 칠하고, 아홉째 선부터 같은 색의 점선이다. 작은 차트는 우리 정의·참고 선 두 색이다.
      var colorOf = function (i) { return row.big ? PALETTE[i % PALETTE.length] : colors[i % 2]; };
      var dashOf = function (i, l) { return row.big ? i >= PALETTE.length : Boolean(l.dashed); };
      var sers = [];
      // 변화 보기에서 기준일 값이 없어 뺀 선. 범례로 켜도 그 보기에서는 그리지 않는다.
      var state = { excluded: [], items: [], names: [] };
      var fig = doc.createElement('figure');
      fig.className = 'mkt-fig' + (row.big ? ' big' : '');
      var cap = doc.createElement('figcaption');
      var title = doc.createElement('b');
      title.textContent = row.label;
      cap.appendChild(title);
      if (lines.length > 1) {
        var legend = doc.createElement('span');
        legend.className = 'mkt-legend';
        lines.forEach(function (l, i) {
          // 큰 차트의 범례는 선을 켜고 끄는 버튼이다.
          var item = doc.createElement(row.big ? 'button' : 'span');
          if (row.big) {
            item.type = 'button';
            item.setAttribute('aria-pressed', l.hidden ? 'false' : 'true');
            item.addEventListener('click', function () {
              var on = item.getAttribute('aria-pressed') !== 'true';
              item.setAttribute('aria-pressed', on ? 'true' : 'false');
              if (sers[i]) sers[i].applyOptions({ visible: on && !state.excluded[i] });
            });
          }
          item.appendChild(lineKey(doc, colorOf(i), dashOf(i, l)));
          state.names[i] = doc.createTextNode(l.label);
          item.appendChild(state.names[i]);
          state.items[i] = item;
          legend.appendChild(item);
        });
        cap.appendChild(legend);
      } else if (lines.length === 1) {
        var src = doc.createElement('span');
        src.className = 'mkt-legend';
        src.textContent = lines[0].label;
        cap.appendChild(src);
      }
      fig.appendChild(cap);
      box.appendChild(fig);
      if (!lines.length) {
        var empty = doc.createElement('p');
        empty.className = 'sub';
        empty.textContent = '아직 쌓인 값이 없다. 서버가 하루 한 번 값을 더한다.';
        fig.appendChild(empty);
        return;
      }
      var holder = doc.createElement('div');
      holder.className = 'mkt-chart';
      fig.appendChild(holder);
      var chart = LWC.createChart(holder, {
        autoSize: true,
        layout: { background: { color: token(doc, '--bg2', '#161a22') }, textColor: token(doc, '--tx2', '#a3abba'), fontFamily: font },
        grid: { vertLines: { visible: false }, horzLines: { color: token(doc, '--line', '#2b313d') } },
        rightPriceScale: { borderVisible: false },
        // 10년 일별(약 2,900점)을 폭 300px 안에 넣으려면 점 간격이 0.1px 아래로 내려가야 한다. 기본 하한 0.5px 은 3년에서 멈춘다.
        // 화면 폭이 바뀌어도(폰 회전·창 크기) 고른 기간을 지킨다.
        timeScale: { borderVisible: false, minBarSpacing: 0.02, lockVisibleTimeRangeOnResize: true },
        localization: { locale: 'ko-KR', priceFormatter: function (v) { return valueText(row, v); } }
      });
      var first = null;
      var last = null;
      lines.forEach(function (l, i) {
        var ser = chart.addSeries(LWC.LineSeries, {
          color: colorOf(i), lineWidth: 2, lineStyle: dashOf(i, l) ? LWC.LineStyle.Dashed : LWC.LineStyle.Solid,
          priceLineVisible: false, pointMarkersVisible: l.points.length < 40, visible: !l.hidden
        });
        sers[i] = ser;
        ser.setData(l.points.map(function (p) { return { time: p[0], value: p[1] }; }));
        if (first === null || l.points[0][0] < first) first = l.points[0][0];
        var end = l.points[l.points.length - 1][0];
        if (last === null || end > last) last = end;
        // 기준일 점: 첫 선에서 기준일 이하 가장 가까운 점.
        if (i === 0 && row.asOf) {
          var hit = l.points.filter(function (p) { return p[0] <= row.asOf; }).pop();
          if (hit) {
            LWC.createSeriesMarkers(ser, [{ time: hit[0], position: 'inBar', shape: 'circle', color: token(doc, '--tx', '#e6e9ee') }]);
          }
        }
      });
      var entry = { chart: chart, first: first, last: last, locked: false, days: RANGES[1][1] };
      if (row.change) wireChange(doc, row, fig, holder, LWC, sers, lines, state, entry);
      charts.push(entry);
    });
    return charts;
  }

  function buttonGroup(doc, label, options, current, onPick) {
    var g = doc.createElement('div');
    g.className = 'mkt-group';
    g.setAttribute('role', 'group');
    g.setAttribute('aria-label', label);
    options.forEach(function (o) {
      var b = doc.createElement('button');
      b.type = 'button';
      b.textContent = o[0];
      b.setAttribute('aria-pressed', o[1] === current ? 'true' : 'false');
      b.addEventListener('click', function () {
        Array.prototype.forEach.call(g.querySelectorAll('button'), function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        onPick(o[1]);
      });
      g.appendChild(b);
    });
    return g;
  }

  // 수준 / 변화(bp) 전환. 변화 보기는 기간 버튼이 기준일을 정하고, 그 기간만 보인다(끌어도 기준일은 그대로다).
  // 위쪽 기간 막대(1년·3년·10년)는 수준 보기에만 닿는다.
  function wireChange(doc, row, fig, holder, LWC, sers, lines, state, entry) {
    var chart = entry.chart;
    var mode = 'level';
    var days = CHANGE_RANGES[1][1];
    var zero = null;
    var tools = doc.createElement('div');
    tools.className = 'mkt-range mkt-mode';
    var periods = buttonGroup(doc, '변화의 기준 기간', CHANGE_RANGES, days, function (d) { days = d; render(); });
    tools.appendChild(buttonGroup(doc, '보기 방식', [['수준(%)', 'level'], ['변화(bp)', 'change']], mode, function (m) { mode = m; render(); }));
    tools.appendChild(periods);
    fig.insertBefore(tools, holder);
    var sum = doc.createElement('p');
    sum.className = 'sub mkt-sum';
    fig.appendChild(sum);
    var toData = function (pts) { return pts.map(function (p) { return { time: p[0], value: p[1] }; }); };
    function render() {
      var change = mode === 'change';
      periods.hidden = !change;
      sum.hidden = !change;
      if (zero) { sers[0].removePriceLine(zero); zero = null; }
      var view = change ? changeLines(lines, days) : null;
      lines.forEach(function (l, i) {
        var v = view ? view.lines[i] : null;
        state.excluded[i] = Boolean(v && v.excluded);
        sers[i].setData(toData(v ? v.points : l.points));
        if (state.names[i]) state.names[i].nodeValue = l.label + (state.excluded[i] ? ' (기준일 값 없음)' : '');
        var on = !state.items[i] || state.items[i].getAttribute('aria-pressed') === 'true';
        sers[i].applyOptions({ visible: on && !state.excluded[i] });
      });
      chart.applyOptions({ localization: { locale: 'ko-KR', priceFormatter: change ? bpText : function (v) { return valueText(row, v); } } });
      entry.locked = change;
      if (change) {
        zero = sers[0].createPriceLine({ price: 0, color: token(doc, '--tx2', '#a3abba'), lineWidth: 1, lineStyle: LWC.LineStyle.Dotted, axisLabelVisible: false });
        chart.timeScale().setVisibleRange({ from: view.base, to: view.end });
        sum.textContent = row.change === 'spread' ? spreadText(spreadSummary(view, row.ref)) : divergenceText(divergence(view));
      } else {
        applyRange([entry], entry.days);
      }
    }
    sum.hidden = true;
    periods.hidden = true;
  }

  // 차트가 자기 폭을 잡은 뒤에 범위를 정한다. 폭이 0 일 때 맞추면 선이 오른쪽 구석에 몰린다.
  function setRange(charts, days) {
    root.requestAnimationFrame(function () { root.requestAnimationFrame(function () { applyRange(charts, days); }); });
  }

  function applyRange(charts, days) {
    charts.forEach(function (c) {
      c.days = days;
      // 변화 보기 중인 차트는 자기 기간 버튼을 따른다.
      if (c.locked) return;
      var from = addDays(c.last, -days);
      if (from <= c.first) c.chart.timeScale().fitContent();
      else c.chart.timeScale().setVisibleRange({ from: from, to: c.last });
    });
  }

  function rangeBar(doc, bar, getCharts) {
    bar.textContent = '';
    RANGES.forEach(function (r, i) {
      var b = doc.createElement('button');
      b.type = 'button';
      b.textContent = r[0];
      b.setAttribute('aria-pressed', i === 1 ? 'true' : 'false');
      b.addEventListener('click', function () {
        Array.prototype.forEach.call(bar.querySelectorAll('button'), function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        setRange(getCharts(), r[1]);
      });
      bar.appendChild(b);
    });
    bar.hidden = false;
  }

  // 표에 없는 시계열(title 이 있는 것)을 표 행과 같은 모양으로 만든다. 기준일은 표 첫 행(미국채 10년물, 가격 기준일)의 것이다.
  function extraRows(data, skip, asOf) {
    return Object.keys(data.series || {}).filter(function (k) {
      return skip.indexOf(k) < 0 && data.series[k].title;
    }).map(function (k) {
      var s = data.series[k];
      return { key: k, kind: s.kind, unit: s.unit, asOf: asOf, label: s.title, big: Boolean(s.big) };
    });
  }

  // 큰 차트를 맨 앞에 둔다(화면 폭 전체를 쓴다). 나머지 순서는 그대로다.
  function bigFirst(rows) {
    return rows.filter(function (r) { return r.big; }).concat(rows.filter(function (r) { return !r.big; }));
  }

  // 로그인한 사람에게만 보이는 절. 차트 상자 바로 뒤에 한 번만 만든다.
  function privateBox(doc, box) {
    var wrap = box.parentNode.querySelector('.mkt-private');
    if (!wrap) {
      wrap = doc.createElement('div');
      wrap.className = 'mkt-private';
      var h = doc.createElement('h4');
      h.textContent = '로그인한 사람에게만 보이는 지표';
      var p = doc.createElement('p');
      p.className = 'sub';
      p.textContent = '회사채(BondTerminal)와 D램 현물가(DRAMeXchange)는 원천 약관이 게시를 막아 공개 방문자에게는 보이지 않는다. ' +
        '회사채는 회사마다 대표 채권 하나의 금리(YTW)와 같은 만기 국채 대비 가산금리(G-spread)이고, 맨 위 두 큰 차트에 함께 그린다. ' +
        'D램 현물가는 과거 값이 유료라 서버가 날마다 쌓는다. ' +
        'Tesla·Palantir·SpaceX-xAI·Anthropic·OpenAI 는 BondTerminal 목록에 채권이 없어 차트가 없다. 공개 시장에서 거래되는 회사채를 ' +
        '찾지 못했다는 뜻이고, 빌린 돈이 없다는 뜻은 아니다(은행 대출·사모 채권·전환사채는 이 목록에 없을 수 있다).';
      var c = doc.createElement('div');
      c.className = 'mkt-charts';
      wrap.appendChild(h);
      wrap.appendChild(p);
      wrap.appendChild(c);
      box.parentNode.insertBefore(wrap, box.nextSibling);
    }
    return wrap;
  }

  // 로그인하지 않은 방문자는 Access 가 로그인 화면으로 돌려보내 요청이 실패한다. 그때는 null 이고 비공개 지표를 그리지 않는다.
  function getPrivate() {
    return getJson(PRIVATE_URL).catch(function () { return null; });
  }

  // 비공개 절. 회사채 금리(bond_yields)와 회사별 가산금리(bond:*)는 맨 위 두 큰 차트에 합쳐 그리므로 여기서는 뺀다.
  function drawPrivate(doc, box, LWC, asOf, priv) {
    var old = box.parentNode.querySelector('.mkt-private');
    var skip = ['bond_yields'].concat(BONDS.map(function (b) { return b.key; }));
    var rows = priv ? extraRows(priv, skip, asOf) : [];
    if (!rows.length) {
      if (old) old.parentNode.removeChild(old);
      return [];
    }
    var wrap = privateBox(doc, box);
    return drawCharts(doc, wrap.querySelector('.mkt-charts'), priv, LWC, rows);
  }

  // 기준일 값은 표 행의 data 속성(data-key·data-kind·data-unit·data-base·data-asof)에 있다.
  function wire(doc) {
    var panel = doc.getElementById('market-live');
    if (!panel) return;
    var button = panel.querySelector('.mkt-btn');
    var status = panel.querySelector('.mkt-status');
    var bar = panel.querySelector('.mkt-range');
    var box = panel.querySelector('.mkt-charts');
    var rows = Array.prototype.slice.call(panel.querySelectorAll('tr[data-key]')).map(function (tr) {
      return { tr: tr, key: tr.dataset.key, kind: tr.dataset.kind, unit: tr.dataset.unit, asOf: tr.dataset.asof,
        base: tr.dataset.base === '' ? null : Number(tr.dataset.base), label: tr.querySelector('.name').textContent };
    });
    if (!button || !status || !bar || !box || !rows.length) return;
    var charts = [];
    function load() {
      button.disabled = true;
      box.style.opacity = charts.length ? '0.5' : '';
      status.textContent = '받는 중이다.';
      Promise.all([getJson(SERIES_URL), loadLwc(doc), getPrivate()]).then(function (res) {
        var data = res[0];
        var LWC = res[1];
        var priv = res[2];
        var filled = fillNow(rows, data);
        charts.forEach(function (c) { c.chart.remove(); });
        var asOf = rows[0].asOf;
        var keys = rows.map(function (r) { return r.key; });
        var all = bigFirst(rows.concat(extraRows(data, keys, asOf)));
        // 2026-11-15 사용자 요청: 로그인했으면 회사별 채권 금리를 맨 위 금리 차트(미국채 10년물·회사채 지수)에 함께 그린다.
        var bonds = priv && priv.series && priv.series.bond_yields;
        all.forEach(function (r) {
          if (r.key !== 'yields') return;
          r.change = true;
          r.lines = withMaturity((((data.series.yields || {}).lines) || []).concat(bonds ? bonds.lines : []));
          r.label = '금리 한눈에: 미국채 10년물과 회사채(회사별 채권 선은 로그인한 사람에게만 보인다)';
        });
        // 2026-11-15 사용자 요청: 금리 수준은 만기가 달라 같은 기준이 아니므로, 같은 만기 국채 대비 가산금리를 금리 차트 바로 뒤에 둔다.
        var at = all.map(function (r) { return r.key; }).indexOf('yields');
        all.splice(at + 1, 0, spreadRow(data, priv, asOf));
        charts = drawCharts(doc, box, data, LWC, all);
        var privCharts = drawPrivate(doc, box, LWC, asOf, priv);
        charts = charts.concat(privCharts);
        rangeBar(doc, bar, function () { return charts; });
        setRange(charts, RANGES[1][1]);
        var bondCount = BONDS.filter(function (b) { return priv && priv.series && priv.series[b.key]; }).length;
        status.textContent = '시계열은 ' + String(data.updated_at || '').slice(0, 16).replace('T', ' ') + '(UTC)에 갱신됐다. ' +
          rows.length + '개 가운데 ' + filled + '개에 지금 값이 있다.' +
          (bondCount ? ' 로그인한 사람에게만 보이는 회사채 ' + bondCount + '곳을 위 두 차트에 더했다.' : '') +
          (privCharts.length ? ' 로그인한 사람에게만 보이는 지표 ' + privCharts.length + '개를 아래에 더 그렸다.' : '');
      }).catch(function (e) {
        status.textContent = failText(e);
      }).then(function () {
        box.style.opacity = '';
        button.disabled = false;
      });
    }
    button.addEventListener('click', load);
    // 2026-11-15 사용자 요청: 탭을 열 때마다 버튼을 누르지 않게, 절이 화면에 처음 보일 때 한 번 저절로 받는다. 버튼은 다시 받을 때 쓴다.
    // 숨은 탭 안에서는 보이지 않으므로 국면 탭을 열기 전에는 받지 않는다(숨은 상자에 차트를 그리면 폭이 0 이다).
    if (root.IntersectionObserver) {
      var seen = new root.IntersectionObserver(function (entries) {
        if (entries.some(function (e) { return e.isIntersecting; })) {
          seen.disconnect();
          load();
        }
      });
      seen.observe(panel);
    }
  }

  var api = { median: median, gpuRent: gpuRent, tokenPicks: tokenPicks, fredLatest: fredLatest, changeText: changeText,
    valueText: valueText, parseFredCsv: parseFredCsv, parseGetDeployingCsv: parseGetDeployingCsv, reconstructTokens: reconstructTokens,
    dailyPoint: dailyPoint, mergeDaily: mergeDaily, assemble: assemble, vastUrl: vastUrl, fredCsvUrl: fredCsvUrl,
    getDeployingUrl: getDeployingUrl, GPU_TYPES: GPU_TYPES, FRED_SERIES: FRED_SERIES, FRED_START: FRED_START,
    OPENROUTER_URL: OPENROUTER_URL, parseEcos: parseEcos, parseBondHistory: parseBondHistory, parseDramx: parseDramx,
    addPoint: addPoint, assemblePrivate: assemblePrivate, ecosUrl: ecosUrl, bondHistoryUrl: bondHistoryUrl,
    parseBondYield: parseBondYield, FRED_YIELDS: FRED_YIELDS, FRED_FETCH: FRED_FETCH,
    changeLines: changeLines, divergence: divergence, divergenceText: divergenceText, CHANGE_RANGES: CHANGE_RANGES,
    spreadSummary: spreadSummary, spreadText: spreadText, spreadRow: spreadRow, withMaturity: withMaturity,
    BONDS: BONDS, DRAMX_URL: DRAMX_URL };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (root && root.document) {
    if (root.document.readyState === 'loading') root.document.addEventListener('DOMContentLoaded', function () { wire(root.document); });
    else wire(root.document);
  }
})(typeof window !== 'undefined' ? window : null);
