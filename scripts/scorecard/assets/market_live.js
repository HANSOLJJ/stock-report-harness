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
  var SERIES_URL = '/reports/market-series.json';
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

  // 서버가 내보내는 시계열. 지표 열쇠는 리포트 표 행의 data-key 와 같다.
  // 이번에 받지 못한 외부 원천(fred·getdeploying 의 본문이 null)은 직전 시계열(previous)의 선을 그대로 쓴다.
  function assemble(input) {
    var previous = (input.previous && input.previous.series) || {};
    function prevLine(key, id) {
      var lines = (previous[key] && previous[key].lines) || [];
      return lines.filter(function (l) { return l.id === id; })[0] || null;
    }
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
    return { schema: 'market-series/1', updated_at: input.now, series: series, errors: input.errors || [] };
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
    return row.kind === 'pct' ? value.toFixed(2) + row.unit : '$' + value.toFixed(2);
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
      var chgCell = row.tr.querySelector('.mkt-chg');
      if (!pts.length) {
        nowCell.textContent = '아직 쌓인 값이 없다';
        chgCell.textContent = '—';
        return;
      }
      var last = pts[pts.length - 1];
      filled += 1;
      nowCell.textContent = valueText(row, last[1]) + ' (' + last[0] + ')';
      chgCell.textContent = changeText(row, row.base, last[1]);
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
        var filled = fillNow(rows, data);
        charts.forEach(function (c) { c.chart.remove(); });
        charts = drawCharts(doc, box, data, res[1], rows);
        rangeBar(doc, bar, function () { return charts; });
        setRange(charts, RANGES[1][1]);
        status.textContent = '시계열은 ' + String(data.updated_at || '').slice(0, 16).replace('T', ' ') + '(UTC)에 갱신됐다. ' +
          rows.length + '개 가운데 ' + filled + '개에 지금 값이 있다.';
      }, function (e) {
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
    OPENROUTER_URL: OPENROUTER_URL };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (root && root.document) {
    if (root.document.readyState === 'loading') root.document.addEventListener('DOMContentLoaded', function () { wire(root.document); });
    else wire(root.document);
  }
})(typeof window !== 'undefined' ? window : null);
