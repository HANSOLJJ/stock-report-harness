// 국면 탭 시장 지표의 지금 값을 브라우저에서 받아 기준일 값과 견준다. 계산 정의는 scripts/scorecard/market_now.py 와 같아야 한다
(function (root) {
  'use strict';

  var GPU_TYPES = ['H100 SXM', 'H200', 'B200'];
  var TOKEN_LABS = ['openai', 'anthropic', 'google', 'x-ai', 'deepseek', 'qwen', 'moonshotai'];
  var TOKEN_WINDOW_DAYS = 180;
  var FRED_SERIES = [['ust10y_yield', 'DGS10'], ['ig_oas', 'BAMLC0A0CM'], ['hy_oas', 'BAMLH0A0HYM2']];
  var OPENROUTER_URL = 'https://openrouter.ai/api/v1/models';
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

  function vastUrl(gpu) {
    var q = { gpu_name: { eq: gpu }, rentable: { eq: true }, type: 'on-demand', limit: 500 };
    return 'https://console.vast.ai/api/v0/bundles/?q=' + encodeURIComponent(JSON.stringify(q));
  }

  function fredUrl(series) {
    return 'https://api.stlouisfed.org/fred/series/observations?series_id=' + series +
      '&file_type=json&sort_order=desc&limit=10';
  }

  function proxied(url) { return '/api/proxy?url=' + encodeURIComponent(url); }

  function failText(err) {
    var code = err && err.status;
    if (code === 404) return '공개 주소에서 열어야 받을 수 있다';
    if (code === 403) return '사이트 프록시가 이 원천을 허용하지 않는다';
    return code ? '받지 못했다(응답 ' + code + ')' : '받지 못했다(연결 실패)';
  }

  function getJson(url) {
    return fetch(url, { cache: 'no-store' }).then(function (r) {
      if (!r.ok) { var e = new Error('HTTP ' + r.status); e.status = r.status; throw e; }
      return r.json();
    });
  }

  // 원천마다 따로 받는다. 하나가 실패해도 나머지 칸은 채운다.
  function fetchLive(today) {
    var out = {};
    var jobs = FRED_SERIES.map(function (pair) {
      return getJson(proxied(fredUrl(pair[1]))).then(function (p) {
        var hit = fredLatest(p);
        out[pair[0]] = hit ? { value: hit.value, date: hit.date } : { error: '값이 없다' };
      }, function (e) { out[pair[0]] = { error: failText(e) }; });
    });
    GPU_TYPES.forEach(function (gpu) {
      var key = 'gpu_rent_hourly:' + gpu;
      jobs.push(getJson(proxied(vastUrl(gpu))).then(function (p) {
        var rent = gpuRent(p.offers);
        out[key] = rent ? { value: rent.value, date: today, gpus: rent.gpus } : { error: '호가가 없다' };
      }, function (e) { out[key] = { error: failText(e) }; }));
    });
    jobs.push(getJson(OPENROUTER_URL).then(function (p) {
      var picks = tokenPicks(p.data, today);
      var value = median(picks.map(function (x) { return x.blended; }));
      out.token_blended_price = value === null ? { error: '고를 모델이 없다' } : { value: value, date: today };
    }, function (e) { out.token_blended_price = { error: failText(e) }; }));
    return Promise.all(jobs).then(function () { return out; });
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

  // 기준일 값은 표 행의 data 속성(data-key·data-kind·data-unit·data-base)에 있다.
  function wire(doc) {
    var panel = doc.getElementById('market-live');
    if (!panel) return;
    var button = panel.querySelector('.mkt-btn');
    var status = panel.querySelector('.mkt-status');
    var trs = Array.prototype.slice.call(panel.querySelectorAll('tr[data-key]'));
    if (!button || !status || !trs.length) return;
    button.addEventListener('click', function () {
      var today = new Date().toISOString().slice(0, 10);
      button.disabled = true;
      status.textContent = '받는 중이다.';
      fetchLive(today).then(function (live) {
        var filled = 0;
        trs.forEach(function (tr) {
          var row = { kind: tr.dataset.kind, unit: tr.dataset.unit };
          var base = tr.dataset.base === '' ? null : Number(tr.dataset.base);
          var got = live[tr.dataset.key] || { error: '받지 못했다' };
          var nowCell = tr.querySelector('.mkt-now');
          var chgCell = tr.querySelector('.mkt-chg');
          if (got.error) {
            nowCell.textContent = got.error;
            chgCell.textContent = '—';
            return;
          }
          filled += 1;
          nowCell.textContent = valueText(row, got.value) + (got.date ? ' (' + got.date + ')' : '');
          chgCell.textContent = changeText(row, base, got.value);
        });
        var stamp = new Date().toLocaleString('ko-KR');
        status.textContent = stamp + '에 받았다. ' + trs.length + '개 가운데 ' + filled + '개를 채웠다.';
      }, function () {
        status.textContent = '받지 못했다. 다시 눌러 보라.';
      }).then(function () { button.disabled = false; });
    });
  }

  var api = { median: median, gpuRent: gpuRent, tokenPicks: tokenPicks, fredLatest: fredLatest, changeText: changeText,
    valueText: valueText, vastUrl: vastUrl, fredUrl: fredUrl };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (root && root.document) {
    if (root.document.readyState === 'loading') root.document.addEventListener('DOMContentLoaded', function () { wire(root.document); });
    else wire(root.document);
  }
})(typeof window !== 'undefined' ? window : null);
