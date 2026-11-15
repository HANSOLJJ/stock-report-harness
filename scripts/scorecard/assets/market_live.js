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
    { key: 'bond:meta', isin: 'US30303M8N52', title: 'Meta 4.95% 2033 가산금리' }
  ];
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
      var lines = ((data.series[row.key] || {}).lines || []).filter(function (l) { return l.points.length; });
      var fig = doc.createElement('figure');
      fig.className = 'mkt-fig';
      var cap = doc.createElement('figcaption');
      var title = doc.createElement('b');
      title.textContent = row.label;
      cap.appendChild(title);
      if (lines.length > 1) {
        var legend = doc.createElement('span');
        legend.className = 'mkt-legend';
        lines.forEach(function (l, i) {
          var item = doc.createElement('span');
          item.appendChild(lineKey(doc, colors[i % 2], l.dashed));
          item.appendChild(doc.createTextNode(l.label));
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
          color: colors[i % 2], lineWidth: 2, lineStyle: l.dashed ? LWC.LineStyle.Dashed : LWC.LineStyle.Solid,
          priceLineVisible: false, pointMarkersVisible: l.points.length < 40
        });
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
      charts.push({ chart: chart, first: first, last: last });
    });
    return charts;
  }

  // 차트가 자기 폭을 잡은 뒤에 범위를 정한다. 폭이 0 일 때 맞추면 선이 오른쪽 구석에 몰린다.
  function setRange(charts, days) {
    root.requestAnimationFrame(function () { root.requestAnimationFrame(function () { applyRange(charts, days); }); });
  }

  function applyRange(charts, days) {
    charts.forEach(function (c) {
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
      return { key: k, kind: s.kind, unit: s.unit, asOf: asOf, label: s.title };
    });
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
        '회사채는 회사마다 대표 채권 하나의 국채 대비 가산금리(G-spread)다. D램 현물가는 과거 값이 유료라 서버가 날마다 쌓는다.';
      var c = doc.createElement('div');
      c.className = 'mkt-charts';
      wrap.appendChild(h);
      wrap.appendChild(p);
      wrap.appendChild(c);
      box.parentNode.insertBefore(wrap, box.nextSibling);
    }
    return wrap;
  }

  // 로그인하지 않은 방문자는 Access 가 로그인 화면으로 돌려보내 요청이 실패한다. 그때는 비공개 절을 그리지 않는다.
  function loadPrivate(doc, box, LWC, asOf) {
    var old = box.parentNode.querySelector('.mkt-private');
    return getJson(PRIVATE_URL).then(function (priv) {
      var rows = extraRows(priv, [], asOf);
      if (!rows.length) throw new Error('empty');
      var wrap = privateBox(doc, box);
      return drawCharts(doc, wrap.querySelector('.mkt-charts'), priv, LWC, rows);
    }).catch(function () {
      if (old) old.parentNode.removeChild(old);
      return [];
    });
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
    button.addEventListener('click', function () {
      button.disabled = true;
      box.style.opacity = charts.length ? '0.5' : '';
      status.textContent = '받는 중이다.';
      Promise.all([getJson(SERIES_URL), loadLwc(doc)]).then(function (res) {
        var data = res[0];
        var LWC = res[1];
        var filled = fillNow(rows, data);
        charts.forEach(function (c) { c.chart.remove(); });
        var asOf = rows[0].asOf;
        var keys = rows.map(function (r) { return r.key; });
        charts = drawCharts(doc, box, data, LWC, rows.concat(extraRows(data, keys, asOf)));
        return loadPrivate(doc, box, LWC, asOf).then(function (priv) {
          charts = charts.concat(priv);
          rangeBar(doc, bar, function () { return charts; });
          setRange(charts, RANGES[1][1]);
          status.textContent = '시계열은 ' + String(data.updated_at || '').slice(0, 16).replace('T', ' ') + '(UTC)에 갱신됐다. ' +
            rows.length + '개 가운데 ' + filled + '개에 지금 값이 있다.' +
            (priv.length ? ' 로그인한 사람에게만 보이는 지표 ' + priv.length + '개를 더 그렸다.' : '');
        });
      }).catch(function (e) {
        status.textContent = failText(e);
      }).then(function () {
        box.style.opacity = '';
        button.disabled = false;
      });
    });
  }

  var api = { median: median, gpuRent: gpuRent, tokenPicks: tokenPicks, fredLatest: fredLatest, changeText: changeText,
    valueText: valueText, parseFredCsv: parseFredCsv, parseGetDeployingCsv: parseGetDeployingCsv, reconstructTokens: reconstructTokens,
    dailyPoint: dailyPoint, mergeDaily: mergeDaily, assemble: assemble, vastUrl: vastUrl, fredCsvUrl: fredCsvUrl,
    getDeployingUrl: getDeployingUrl, GPU_TYPES: GPU_TYPES, FRED_SERIES: FRED_SERIES, FRED_START: FRED_START,
    OPENROUTER_URL: OPENROUTER_URL, parseEcos: parseEcos, parseBondHistory: parseBondHistory, parseDramx: parseDramx,
    addPoint: addPoint, assemblePrivate: assemblePrivate, ecosUrl: ecosUrl, bondHistoryUrl: bondHistoryUrl,
    BONDS: BONDS, DRAMX_URL: DRAMX_URL };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (root && root.document) {
    if (root.document.readyState === 'loading') root.document.addEventListener('DOMContentLoaded', function () { wire(root.document); });
    else wire(root.document);
  }
})(typeof window !== 'undefined' ? window : null);
