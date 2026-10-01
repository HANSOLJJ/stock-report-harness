// 스코어카드 실행 승인을 위한 HTTP 라우트 및 페이지 렌더러
const child_process = require('child_process');

const RUN_ID_REGEX = /^[a-z0-9][a-z0-9-]{2,80}$/;
const MAX_CODE_FAILURES = 5;
// 판단 수정(2026-10-01 레인 J). 기업 id 는 schema.ID_RE, factor 는 F1~F9, 판정 재료 키는 영문 식별자만 받는다.
const COMPANY_ID_REGEX = /^[a-z0-9][a-z0-9._-]{0,63}$/;
const FACTOR_REGEX = /^F[1-9]$/;
const INPUT_KEY_REGEX = /^[A-Za-z_]{1,40}$/;
const EDIT_KIND_LABELS = {
  score: '점수와 근거',
  criteria: '판정 기준(criteria)',
  grade: '등급(A·H)',
  matrix: '매트릭스',
  gate_inputs: '게이트 입력',
};
// 2026-10-01 사용자 요청(가독성): factor 코드만으로는 뜻을 알 수 없다. 이름과 핵심 판별 질문을 함께 보인다.
// 출처는 docs/scorecard/rules/AI기업_채점규칙_v1.7.md 의 과점·함정 factor 표(핵심 판별 질문 열)다.
const FACTOR_GUIDE = {
  F1: { label: '① 네트워크 효과', group: 'moat', question: '가격을 올려도 남는가? 락인 강도·데이터 루프. 가장 강한 채널로 매긴다' },
  F2: { label: '② 신기술 게임체인저', group: 'moat', question: '판을 바꿀 기술을 먼저 냈나, 남이 바꾼 판에 빨리 올라탔나? 성능 도약·패러다임 적응·표준 선점' },
  F3: { label: '③ Last Mover', group: 'moat', question: '선두가 내 방식을 베끼면 선두 수익모델이 무너지나, 내 뒤 진입로는 닫히나?' },
  F4: { label: '④ 호황 이후 비전', group: 'moat', question: '곡괭이만 팔다 끝나나, 광부가 되나? 출하·사업 부문만 센다(계획은 0)' },
  F5: { label: '⑤ 아군 확보', group: 'moat', question: '동맹이 적보다 많은가? 조달은 동맹이 아니고, 규제·소송은 적대로 센다' },
  F6: { label: '⑥ 가격', group: 'trap', question: '미래 성장이 얼마나 선반영됐나? PER·EV/매출·매출 성장' },
  F7: { label: '⑦ 순환금융', group: 'trap', question: '내 매출을 내는 고객이 그 돈을 어디서 구했나? 자기 이익인가, 조달인가' },
  F8: { label: '⑧ 비대칭 의존', group: 'trap', question: '끊기면 매출이 주나, 회사가 멈추나? 공급자가 곧 경쟁자인가' },
  F9: { label: '⑨ 적자 깊이', group: 'trap', question: '본업이 버나 → 현금이 새나 → 얼마나 버티나 → 약정이 덮이나' },
};
const CHANNEL_LABELS = {
  disclosure: '공시',
  press: '언론 보도',
  company_statement: '기업 발표',
  secondary: '의견·재전달',
};

// 2026-10-01 사용자 요청: 근거 문장의 규칙 용어(별표·잣대·게이트·체크리스트)를 설명 없이 두지 않는다.
// 출처는 docs/scorecard/rules/AI기업_채점규칙_v1.7.md 의 해당 절이다. 문장에 나오면 아래 참조표로 연결한다.
const RULES_DOC = 'docs/scorecard/rules/AI기업_채점규칙_v1.7.md';
const GLOSSARY = {
  'star-A': { term: '별표 A', text: '① 은 회사의 모든 실질 채널(소비자·업무·거래·부품)을 보고 가장 강한 락인으로 매긴다. 얕은 채널이 깊은 채널을 깎지 않는다.' },
  'star-B': { term: '별표 B', text: '③ 은 "안 만든 자" 에게 주는 점수가 아니다. 선두가 못 따라 하는 방식으로 들어가기와, 내 뒤 진입로를 닫기 두 동작을 본다.' },
  'star-C': { term: '별표 C', text: '⑤ 의 적대세력은 수가 아니라 성격을 본다. 고객이 적이 되면 존립 위협이고, 규제기관·경쟁사 소송은 비용이다.' },
  'star-D': { term: '별표 D', text: '미래 계획은 현재 점수에 넣지 않는다. 출하·매출·채택처럼 지금 측정되는 것만 세고, 계획·발표·예정은 0 이다.' },
  'star-E': { term: '별표 E', text: '비AI 사업(로켓·Starlink·리테일·iPhone 등)은 ①(채널 락인)·③ 의 별도 수익모델·④(다각화)에서만 센다. ② 와 ③ 의 모방불가·가속도는 AI 에 귀속되는 부분만 센다.' },
  'star-F': { term: '별표 F', text: '② 는 세 경로 가운데 하나면 된다. 성능 도약 · 패러다임 적응(남이 바꾼 판에 빨리 올라탐) · 표준 선점.' },
  'star-G': { term: '별표 G', text: '⑤ = 3 + 동맹 등급(0~+2) + 적대 등급(0~-3). 적대 등급은 -1 비용형(벌금·소송·조사), -2 구조형(주요 고객이 경쟁자이거나 사업 정당성 자체를 겨냥), -3 다발형(구조형이 여러 전선에서 동시에).' },
  'star-H': { term: '별표 H', text: '조달과 동맹을 가르는 네 질문. 지분·독점·공동개발·재판매·수수료 분배가 있고 상대가 잘되면 내가 잘되는 관계만 동맹이다. 돈 주고 사는 관계는 조달이다. 내가 상대를 못 떠나면 ⑧ 에서 깎는다.' },
  'star-I': { term: '별표 I', text: '⑦ 판정표. 조달(투자·부채)로 지출하는 고객의 매출 비중(작음·큼)과, 내 돈이 고객을 거쳐 내 매출로 돌아오는지로 0·-1·-2 를 정한다.' },
  'star-J': { term: '별표 J', text: '신용등급·CDS 는 점수 입력이 아니라 함정 점수가 맞는지 교차검증하는 데만 쓴다.' },
  P1: { term: 'P1 PER', text: '⑥ 첫째 잣대. 시가총액 ÷ 최근 1년 순이익. 25배 미만 0, 45배 미만 -1, 그 밖 -2.' },
  P2: { term: 'P2 EV/매출', text: '⑥ 둘째 잣대. (시가총액 − 순현금) ÷ 최근 1년 매출. 8배 미만 0, 20배 미만 -1, 그 밖 -2.' },
  P3: { term: 'P3 매출 성장', text: '⑥ 셋째 잣대. 최근 1년 매출 ÷ 그 전 1년 − 1. 30% 이상 0, 15% 이상 -1, 5% 이상 -2, 그 아래 -3.' },
  P4: { term: 'P4 입력 신뢰도', text: '⑥ 넷째 잣대. 입력 자료에 결함이 있으면 P1~P3 소계에서 한 칸 더 깎는다(조건이 여럿이어도 한 칸).' },
  G1: { term: '⑨ 게이트 1', text: '본업이 버는가(영업이익). 적자면 영업손실률로 -2(-10% 이내)·-3(-10~-30%)·-4(-30% 초과).' },
  G2: { term: '⑨ 게이트 2', text: '현금이 새는가(최근 1년 잉여현금흐름 FCF). 흑자면 추세만 보고 끝난다.' },
  G3: { term: '⑨ 게이트 3', text: '얼마나 버티는가(런웨이). 완충은 현금과 확정 미인출 여신뿐이다.' },
  G4: { term: '⑨ 게이트 4', text: '미래 지출이 덮이는가(약정 커버리지). 회사가 공시하지 않았다고 확인된 경우만 한 칸 깎는다.' },
  checklist: { term: '체크리스트', text: '규칙 문서 끝의 "채점 전 체크리스트 — 실제로 걸렸던 오류 23가지". 3번(Q03)은 "한 회사에 새 잣대를 댔으면 같은 잣대가 닿는 모든 회사에 대야 한다" 이다.' },
  tension: { term: '긴장', text: '규칙과 실제 판정이 어긋나 아직 풀지 않은 항목의 번호. 규칙 문서의 운영 이력에 재검토 시점과 함께 적혀 있다.' },
};
// 별표 X · P1~P4 · G1~G4 · 게이트 N · 체크리스트 N · QNN · 긴장 #N · <company>.F<n>
const TERM_RE = /별표\s*([A-J])|\bP([1-4])\b|\bG([1-4])\b|게이트\s*([1-4])|체크리스트\s*(\d{1,2})|\bQ(\d{2})\b|긴장\s*#?(\d{1,2})|\b([a-z][a-z-]*)\.F([1-9])\b/g;

// 이미 escapeHtml 한 문장에 적용한다. 용어 문자열에는 HTML 특수문자가 없다.
function linkTerms(escaped, ctx) {
  return String(escaped).replace(TERM_RE, (m, star, p, g, gate, cl, q, ten, cid, fac) => {
    let key = null;
    if (star) key = `star-${star}`;
    else if (p) key = `P${p}`;
    else if (g || gate) key = `G${g || gate}`;
    else if (cl || q) key = 'checklist';
    else if (ten) key = 'tension';
    if (key) {
      const ref = GLOSSARY[key];
      return `<a class="term" href="#ref-${key}" title="${escapeHtml(ref.term)}: ${escapeHtml(ref.text)}">${m}</a>`;
    }
    const name = ctx && ctx.companyNames ? ctx.companyNames[cid] : null;
    if (!name) return m;   // 등록된 기업이 아니면 판단 ID 로 보지 않는다
    const href = `/approve/${encodeURIComponent(ctx.runId)}?factor=F${fac}&company=${encodeURIComponent(cid)}#judge-form`;
    return `<a class="term" href="${escapeHtml(href)}" title="판단 ${escapeHtml(m)} 보기">${escapeHtml(name)} ${escapeHtml(factorLabel(`F${fac}`))} 판단</a>`;
  });
}

function renderGlossary() {
  const rows = Object.keys(GLOSSARY).map((key) => `<dt id="ref-${key}">${escapeHtml(GLOSSARY[key].term)}</dt><dd>${escapeHtml(GLOSSARY[key].text)}</dd>`).join('');
  return `<p class="form-desc">근거 문장의 밑줄 용어를 누르면 여기로 옵니다. 전체 정의는 <code>${escapeHtml(RULES_DOC)}</code> 에 있습니다.</p><dl class="ref-list">${rows}</dl>`;
}

function factorLabel(f) {
  return FACTOR_GUIDE[f] ? FACTOR_GUIDE[f].label : String(f);
}

function factorChips(list) {
  const factors = Array.isArray(list) ? list : [];
  return factors.map((f) => {
    const g = FACTOR_GUIDE[f] ? FACTOR_GUIDE[f].group : 'other';
    return `<span class="fchip fchip-${g}" title="${escapeHtml(FACTOR_GUIDE[f] ? FACTOR_GUIDE[f].question : '')}">${escapeHtml(factorLabel(f))}</span>`;
  }).join(' ');
}

function formatKst(iso) {
  if (!iso) return '시각 없음';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return String(iso);
  return `${new Intl.DateTimeFormat('ko-KR', {
    timeZone: 'Asia/Seoul', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hour12: false,
  }).format(d)} KST`;
}

function renderFactorBar() {
  const items = Object.keys(FACTOR_GUIDE).map((f) => `<div class="factor-item">${factorChips([f])}<span class="fq">${escapeHtml(FACTOR_GUIDE[f].question)}</span></div>`).join('');
  return `
  <nav class="factor-bar" aria-label="factor 안내">
    <details open>
      <summary><strong>Factor 안내</strong> <span class="fq">파란색 ①~⑤ 과점(가점) · 주황색 ⑥~⑨ 함정(감점). 눌러서 접기</span></summary>
      <div class="factor-grid">${items}</div>
    </details>
  </nav>`;
}

function renderEvidenceCard(item, ctx) {
  const L = (s) => linkTerms(escapeHtml(s), ctx);
  const eid = item.evidence_id || '';
  const cid = item.company_id || '';
  const titleLink = item.url
    ? `<a href="${escapeHtml(item.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(item.title || eid)}</a>`
    : escapeHtml(item.title || eid);
  const confirmed = item.status === 'confirmed';
  const counter = Array.isArray(item.counter_evidence) ? item.counter_evidence : [];
  const unverified = Array.isArray(item.unverified) ? item.unverified : [];
  const details = [
    item.relevance ? `<dt>고른 이유</dt><dd>${L(item.relevance)}</dd>` : '',
    item.conditional_impact ? `<dt>예상 영향</dt><dd>${L(item.conditional_impact)}</dd>` : '',
    item.horizon ? `<dt>시간 범위</dt><dd>${L(item.horizon)}</dd>` : '',
    counter.length ? `<dt>반대 근거·한계</dt><dd>${counter.map((c) => L(c)).join('<br />')}</dd>` : '',
    unverified.length ? `<dt>확인 못 한 것</dt><dd class="muted">${unverified.map((u) => L(u)).join('<br />')}</dd>` : '',
    item.excerpt && item.excerpt !== item.title ? `<dt>발췌</dt><dd class="muted">${escapeHtml(item.excerpt)}</dd>` : '',
  ].join('');
  return `
      <div class="ev-card${confirmed ? ' ev-confirmed' : ''}" data-group="${escapeHtml(cid)}">
        <input type="checkbox" name="evidence" value="${escapeHtml(eid)}" id="chk_${escapeHtml(eid)}" checked aria-label="${escapeHtml(eid)} 확정" />
        <div class="ev-body">
          <div class="ev-meta">${factorChips(item.factors)}
            <span class="badge">${escapeHtml(CHANNEL_LABELS[item.channel] || item.channel || (item.kind === 'filing' ? '공시' : '뉴스'))}</span>
            <span class="muted">${escapeHtml(formatKst(item.published_at_utc))}</span>
            ${confirmed ? '<span class="badge badge-ok">확정됨</span>' : ''}
          </div>
          <div class="ev-title">${titleLink}</div>
          <dl class="ev-detail">${details}</dl>
          <div class="ev-id"><label for="chk_${escapeHtml(eid)}">${escapeHtml(eid)}</label></div>
        </div>
      </div>`;
}

function isLoopback(remoteAddress) {
  if (!remoteAddress) return false;
  const normalized = String(remoteAddress).trim();
  return (
    normalized === '127.0.0.1' ||
    normalized === '::1' ||
    normalized === '::ffff:127.0.0.1'
  );
}

function isValidRunId(runId) {
  return typeof runId === 'string' && RUN_ID_REGEX.test(runId);
}

function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function defaultRunCli(args, callback) {
  let cmd;
  let cmdArgs;
  if (process.env.SCORECARD_CLI) {
    const parts = process.env.SCORECARD_CLI.trim().split(/\s+/);
    cmd = parts[0];
    cmdArgs = parts.slice(1).concat(args);
  } else {
    cmd = 'uv';
    cmdArgs = ['run', '--frozen', 'python', '-X', 'utf8', 'scripts/scorecard_cli.py', ...args];
  }

  child_process.execFile(cmd, cmdArgs, { encoding: 'utf8' }, (err, stdout, stderr) => {
    const exitCode = err ? (typeof err.code === 'number' ? err.code : 1) : 0;
    callback(null, {
      exitCode,
      stdout: stdout || '',
      stderr: stderr || (err && err.message) || '',
    });
  });
}

function sendText(res, statusCode, body, headers = {}) {
  res.writeHead(statusCode, {
    'Content-Type': 'text/plain; charset=utf-8',
    ...headers,
  });
  res.end(body);
}

function sendHtml(res, statusCode, html) {
  res.writeHead(statusCode, {
    'Content-Type': 'text/html; charset=utf-8',
  });
  res.end(html);
}

function readBody(req, callback) {
  let body = '';
  req.on('data', (chunk) => {
    body += chunk;
    if (body.length > 1e6) {
      req.socket.destroy();
      callback(new Error('Body too large'));
    }
  });
  req.on('end', () => {
    callback(null, body);
  });
  req.on('error', (err) => {
    callback(err);
  });
}

function renderErrorPage(statusCode, title, detail) {
  return `<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>${escapeHtml(title)} - 승인 시스템</title>
  <style>
    body { font-family: system-ui, -apple-system, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 16px; color: #1e293b; line-height: 1.5; }
    h1 { color: #dc2626; font-size: 24px; }
    pre { background: #0f172a; color: #f8fafc; padding: 16px; border-radius: 6px; overflow-x: auto; font-size: 13px; }
    a { color: #2563eb; text-decoration: none; }
  </style>
</head>
<body>
  <h1>${statusCode} - ${escapeHtml(title)}</h1>
  <pre>${escapeHtml(detail || '알 수 없는 오류가 발생했습니다.')}</pre>
</body>
</html>`;
}

function judgmentInputText(j) {
  if (j.kind === 'score') return `score ${j.score}`;
  const inputs = Array.isArray(j.inputs) ? j.inputs : [];
  return inputs.map((p) => `${p.key}=${p.value}`).join(', ') || '-';
}

// 판단 수정 절. factor 를 고르면 그 factor 의 모든 기업 판단을 나란히 보이고(Q03), 기업을 고르면 판정 종류에 맞는 입력란을 낸다.
function renderJudgeSection(data, judgeFactor, judgeCompany) {
  const runId = data.run_id || '';
  const judgments = Array.isArray(data.judgments) ? data.judgments : [];
  const choices = data.judgment_choices || {};
  const editable = [];
  for (const j of judgments) {
    if (j.edit_kind && !editable.some((e) => e.factor === j.factor)) {
      editable.push({ factor: j.factor, edit_kind: j.edit_kind });
    }
  }
  editable.sort((a, b) => a.factor.localeCompare(b.factor));
  if (editable.length === 0) {
    return '<p>고칠 수 있는 판단이 없습니다.</p>';
  }
  const options = editable.map((e) => `<option value="${escapeHtml(e.factor)}"${e.factor === judgeFactor ? ' selected' : ''}>${escapeHtml(factorLabel(e.factor))} · ${escapeHtml(EDIT_KIND_LABELS[e.edit_kind] || e.edit_kind)}</option>`).join('');
  const picker = `
    <form method="GET" action="/approve/${escapeHtml(runId)}" class="inline-form">
      <label for="judge_factor">factor:</label>
      <select id="judge_factor" name="factor">${options}</select>
      <button type="submit" class="btn btn-secondary">이 factor 의 판단 보기</button>
    </form>`;
  const selected = editable.find((e) => e.factor === judgeFactor);
  if (!selected) {
    return `<p class="form-desc">factor 를 고르면 그 factor 의 모든 기업 판단을 나란히 보여 줍니다. 점수가 아니라 판단 입력을 고칩니다.</p>${picker}`;
  }

  const rows = judgments.filter((j) => j.factor === selected.factor).map((j) => {
    const evidence = Array.isArray(j.evidence) ? j.evidence : [];
    const href = `/approve/${encodeURIComponent(runId)}?factor=${encodeURIComponent(j.factor)}&company=${encodeURIComponent(j.company_id)}#judge-form`;
    return `<tr${j.company_id === judgeCompany ? ' class="row-selected"' : ''}>
      <td><strong>${escapeHtml(j.display_name || j.company_id)}</strong></td>
      <td>${escapeHtml(j.kind)}</td>
      <td>${escapeHtml(judgmentInputText(j))}</td>
      <td>${escapeHtml(j.status)}</td>
      <td>${escapeHtml(j.reviewer)} · ${escapeHtml(j.reviewed_at)}${j.last_revision_session === 'agent' ? '<br /><strong>에이전트 세션에서 수정</strong>' : ''}</td>
      <td>${escapeHtml(j.revisions || 0)}</td>
      <td><div class="excerpt">${evidence.map((e) => escapeHtml(e)).join('<br />') || '-'}</div></td>
      <td><a href="${escapeHtml(href)}">고치기</a></td>
    </tr>`;
  }).join('\n');
  const table = `
    <div class="table-wrapper">
      <table>
        <thead>
          <tr><th>기업</th><th>판정 종류</th><th>현재 입력</th><th>상태</th><th>검토자 · 검토일</th><th>수정 횟수</th><th>근거</th><th></th></tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>`;

  const target = judgments.find((j) => j.factor === selected.factor && j.company_id === judgeCompany);
  let form = '';
  if (target) {
    const editKind = target.edit_kind;
    let fields = '';
    if (editKind === 'score') {
      const range = Array.isArray(target.score_range) ? target.score_range : [];
      fields = `
        <div class="form-group">
          <label for="judge_score">점수 (${escapeHtml(range[0])} ~ ${escapeHtml(range[1])}):</label>
          <input type="number" id="judge_score" name="score" value="${escapeHtml(target.score)}" min="${escapeHtml(range[0])}" max="${escapeHtml(range[1])}" step="1" required />
        </div>`;
    } else {
      const current = {};
      for (const p of (Array.isArray(target.inputs) ? target.inputs : [])) current[p.key] = String(p.value);
      const keys = choices[editKind] || {};
      fields = Object.keys(keys).map((key) => {
        const has = Object.prototype.hasOwnProperty.call(current, key);
        const opts = (has ? '' : '<option value="">(값 없음 — 고르지 않으면 바꾸지 않음)</option>')
          + keys[key].map((v) => `<option value="${escapeHtml(v)}"${has && current[key] === String(v) ? ' selected' : ''}>${escapeHtml(v)}</option>`).join('');
        return `
        <div class="form-group">
          <label for="judge_in_${escapeHtml(key)}">${escapeHtml(key)}:</label>
          <select id="judge_in_${escapeHtml(key)}" name="in_${escapeHtml(key)}">${opts}</select>
        </div>`;
      }).join('');
    }
    const evidenceText = (Array.isArray(target.evidence) ? target.evidence : []).join('\n');
    form = `
      <form method="POST" action="/approve/${escapeHtml(runId)}/judge" class="action-form" id="judge-form">
        <h3>${escapeHtml(target.display_name || target.company_id)} · ${escapeHtml(target.factor)} 판단 수정</h3>
        <p class="form-desc">점수가 아니라 판단 입력을 고칩니다. 제출하면 판단 해시가 바뀌어 지금의 점수·초안·리뷰·승인이 무효가 됩니다. 이전 값은 판단 안의 수정 이력에 남습니다.</p>
        <input type="hidden" name="company" value="${escapeHtml(target.company_id)}" />
        <input type="hidden" name="factor" value="${escapeHtml(target.factor)}" />
        ${fields}
        <div class="form-group">
          <label for="judge_evidence">근거 문장 (한 줄에 하나):</label>
          <textarea id="judge_evidence" name="evidence" rows="6">${escapeHtml(evidenceText)}</textarea>
          <input type="hidden" name="evidence_original" value="${escapeHtml(evidenceText)}" />
        </div>
        <div class="form-group">
          <label for="judge_reason">수정 사유:</label>
          <input type="text" id="judge_reason" name="reason" required placeholder="왜 고치는지" />
        </div>
        <div class="form-group">
          <label for="judge_by">수정자 이름:</label>
          <input type="text" id="judge_by" name="by" required placeholder="수정자 성함" />
        </div>
        <div class="form-group">
          <label for="judge_code">일회용 코드 (6자리):</label>
          <input type="text" id="judge_code" name="code" required pattern="[0-9]{6}" maxlength="6" placeholder="터미널 확인" />
        </div>
        <button type="submit" class="btn btn-primary">판단 수정 제출</button>
      </form>`;
  }
  return `${picker}${table}${form}`;
}

function normalizeLines(text) {
  return String(text || '').replace(/\r\n?/g, '\n').split('\n').map((s) => s.trim()).filter(Boolean);
}

// 판단 수정 POST 의 CLI 인자. 자유 입력(근거·사유·이름)은 `--opt=value` 꼴로 넘겨 '-' 로 시작해도 옵션으로 읽히지 않게 한다.
function buildJudgeArgs(runId, params) {
  const company = (params.get('company') || '').trim();
  const factor = (params.get('factor') || '').trim();
  if (!COMPANY_ID_REGEX.test(company) || !FACTOR_REGEX.test(factor)) {
    return null;
  }
  const args = ['judge', runId, '--company', company, '--factor', factor];
  const score = (params.get('score') || '').trim();
  if (score) {
    args.push('--set', `score=${score}`);
  }
  for (const [name, value] of params.entries()) {
    if (!name.startsWith('in_')) continue;
    const key = name.slice(3);
    const v = String(value).trim();
    if (!INPUT_KEY_REGEX.test(key) || !v) continue;
    args.push('--set', `${key}=${v}`);
  }
  const evidence = normalizeLines(params.get('evidence'));
  if (params.has('evidence') && evidence.join('\n') !== normalizeLines(params.get('evidence_original')).join('\n')) {
    for (const line of evidence) args.push(`--evidence=${line}`);
  }
  args.push(`--reason=${(params.get('reason') || '').trim()}`);
  args.push(`--by=${(params.get('by') || '').trim()}`);
  return args;
}

function renderSummaryPage(data, options = {}) {
  const { lastResult, notice, judgeFactor, judgeCompany } = options;
  const runId = data.run_id || '';
  const asOf = data.as_of || '-';
  const ruleVersion = data.rule_version || '-';
  const approval = data.approval || { exists: false, valid: false };
  const review = data.review;
  const companies = Array.isArray(data.companies) ? data.companies : [];
  const evidence = data.evidence || { items: [] };
  const evidenceItems = Array.isArray(evidence.items) ? evidence.items : [];
  const triggers = Array.isArray(data.triggers) ? data.triggers : [];
  const pendingDecisions = Array.isArray(data.pending_rule_decisions) ? data.pending_rule_decisions : [];
  const hashes = data.hashes || {};
  const companyNames = Object.assign({}, ...(Array.isArray(data.judgments) ? data.judgments : [])
    .map((j) => ({ [j.company_id]: j.display_name })),
    ...(Array.isArray(data.company_names) ? data.company_names : []).map((c) => ({ [c.company_id]: c.display_name })));
  const companyName = (cid) => companyNames[cid] || cid;
  const termCtx = { runId, companyNames };

  const checklistFailCount = review ? Number(review.checklist_fail || 0) : 0;
  const reviewStatus = review ? review.status : 'none';
  const showReviewWarning = checklistFailCount > 0 || reviewStatus !== 'pass';

  let lastResultBlock = '';
  if (lastResult) {
    lastResultBlock = `
    <section class="cli-result-section">
      <h2>최근 명령 실행 결과 (${escapeHtml(lastResult.command)})</h2>
      <p>종료 코드: <strong>${escapeHtml(lastResult.exitCode)}</strong></p>
      ${notice ? `<div class="notice-banner">${escapeHtml(notice)}</div>` : ''}
      ${lastResult.stdout ? `<div><strong>표준 출력 (stdout)</strong><pre>${escapeHtml(lastResult.stdout)}</pre></div>` : ''}
      ${lastResult.stderr ? `<div><strong>표준 오류 (stderr)</strong><pre class="stderr">${escapeHtml(lastResult.stderr)}</pre></div>` : ''}
    </section>`;
  }

  // (1) 실행 머리
  const approvalStatusText = approval.exists
    ? `승인 완료 (${approval.approved_by || '익명'}, ${approval.approved_at || '-'})`
    : '미승인';

  // (2) 기업별 표
  const companyRows = companies.map((c) => {
    const baseTotal = c.baseline ? c.baseline.total : '-';
    const baseRank = c.baseline ? c.baseline.rank : '-';
    const currTotal = c.current ? c.current.total : '-';
    const currRank = c.current ? c.current.rank : '-';
    const changed = Array.isArray(c.changed_factors)
      ? c.changed_factors.map((f) => `${factorLabel(f.factor)}: ${f.from}→${f.to}`).join(', ')
      : '-';
    const carried = Array.isArray(c.carried_factors) ? c.carried_factors.map((f) => factorLabel(f)).join(', ') : '-';
    const pending = Array.isArray(c.pending) ? c.pending.join(', ') : '-';

    return `<tr>
      <td><strong>${escapeHtml(c.display_name || c.company_id)}</strong></td>
      <td>${escapeHtml(baseTotal)}점 (${escapeHtml(baseRank)}위) → ${escapeHtml(currTotal)}점 (${escapeHtml(currRank)}위)</td>
      <td>${escapeHtml(changed || '-')}</td>
      <td>${escapeHtml(carried || '-')}</td>
      <td>${escapeHtml(pending || '-')}</td>
    </tr>`;
  }).join('\n');

  // (3) 리뷰
  let reviewContent = '';
  if (!review) {
    reviewContent = '<p>리뷰 없음</p>';
  } else {
    const areaRows = Array.isArray(review.areas)
      ? review.areas.map((a) => `<tr>
          <td>${escapeHtml(a.area)}</td>
          <td>${escapeHtml(a.reviewer || '-')}</td>
          <td>${escapeHtml(a.result || '-')}</td>
        </tr>`).join('\n')
      : '';

    reviewContent = `
      <p>전체 상태: <strong>${escapeHtml(review.status || '-')}</strong> | 체크리스트 실패 건수: <strong>${checklistFailCount}</strong></p>
      <div class="table-wrapper">
        <table>
          <thead>
            <tr><th>영역</th><th>검토자</th><th>결과</th></tr>
          </thead>
          <tbody>${areaRows || '<tr><td colspan="3">영역 정보 없음</td></tr>'}</tbody>
        </table>
      </div>`;
  }

  // (4) 근거 후보 목록
  const candidateIds = evidenceItems.map((item) => item.evidence_id).join(',');
  const evidenceByCompany = new Map();
  for (const item of evidenceItems) {
    if (!evidenceByCompany.has(item.company_id)) evidenceByCompany.set(item.company_id, []);
    evidenceByCompany.get(item.company_id).push(item);
  }
  const evidenceGroups = [...evidenceByCompany].map(([cid, items]) => `
    <div class="ev-group">
      <div class="ev-group-head">
        <h3>${escapeHtml(companyName(cid))} <span class="muted">${items.length}건</span></h3>
        <button type="button" class="btn-link" data-toggle-group="${escapeHtml(cid)}">이 기업 모두 선택·해제</button>
      </div>
      ${items.map((item) => renderEvidenceCard(item, termCtx)).join('')}
    </div>`).join('\n');

  // (5) 활성 트리거 표
  const triggerRows = triggers.map((t) => {
    return `<tr>
      <td><strong>${escapeHtml(t.trigger_id || '-')}</strong></td>
      <td>${escapeHtml(companyName(t.company_id || '-'))}</td>
      <td>${factorChips(t.factors)}</td>
      <td>${t.observation ? `<div class="muted">관측: ${linkTerms(escapeHtml(t.observation), termCtx)}</div>` : ''}${linkTerms(escapeHtml(t.condition || '-'), termCtx)}${t.recheck_what ? `<div class="muted">다시 볼 것: ${linkTerms(escapeHtml(t.recheck_what), termCtx)}</div>` : ''}</td>
      <td>${escapeHtml(t.deadline || '-')}</td>
      <td>${escapeHtml(t.status || '-')}</td>
    </tr>`;
  }).join('\n');

  // (6) 미결 규칙 결정
  const pendingDecisionsContent = pendingDecisions.length > 0
    ? `<ul>${pendingDecisions.map((d) => `<li>${escapeHtml(d)}</li>`).join('')}</ul>`
    : '<p>미결 규칙 결정 사항이 없습니다.</p>';

  // (7) 지문(해시) 목록
  const hashKeys = ['rules', 'observations', 'judgments', 'run', 'results', 'draft', 'sources', 'evidence', 'triggers'];
  const hashRows = hashKeys
    .filter((k) => hashes[k])
    .map((k) => `<tr><th>${escapeHtml(k)}</th><td><code>${escapeHtml(hashes[k])}</code></td></tr>`)
    .join('\n');

  // (8) 승인 / 취소 폼
  let approvalForm = '';
  if (approval.exists) {
    approvalForm = `
      <form method="POST" action="/approve/${escapeHtml(runId)}/revoke" class="action-form">
        <h3>승인 취소</h3>
        <p class="form-desc">이미 승인된 실행입니다. 승인을 취소하려면 이름과 이유, 일회용 코드를 입력하십시오.</p>
        <div class="form-group">
          <label for="revoke_by">이름:</label>
          <input type="text" id="revoke_by" name="by" required placeholder="취소자 성함" />
        </div>
        <div class="form-group">
          <label for="revoke_note">취소 이유:</label>
          <input type="text" id="revoke_note" name="note" required placeholder="취소 사유" />
        </div>
        <div class="form-group">
          <label for="revoke_code">일회용 코드 (6자리):</label>
          <input type="text" id="revoke_code" name="code" required pattern="[0-9]{6}" maxlength="6" placeholder="터미널 확인" />
        </div>
        <button type="submit" class="btn btn-danger">승인 취소</button>
      </form>`;
  } else {
    approvalForm = `
      ${showReviewWarning ? `
      <div class="warning-banner">
        <strong>승인 유의 안내:</strong> 리뷰 상태가 'pass'가 아니거나 체크리스트 실패 건수가 존재합니다 (실패: ${checklistFailCount}건). Python 승인 검증기가 해당 실행을 거부할 수 있습니다.
      </div>` : ''}
      <form method="POST" action="/approve/${escapeHtml(runId)}/approve" class="action-form">
        <h3>실행 승인</h3>
        <div class="form-group">
          <label for="approve_by">승인자 이름:</label>
          <input type="text" id="approve_by" name="by" required placeholder="승인자 성함" />
        </div>
        <div class="form-group">
          <label for="approve_note">메모 (선택):</label>
          <input type="text" id="approve_note" name="note" placeholder="승인 메모" />
        </div>
        <div class="form-group">
          <label for="approve_code">일회용 코드 (6자리):</label>
          <input type="text" id="approve_code" name="code" required pattern="[0-9]{6}" maxlength="6" placeholder="터미널 확인" />
        </div>
        <button type="submit" class="btn btn-primary">승인 확정</button>
      </form>`;
  }

  return `<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>스코어카드 실행 승인: ${escapeHtml(runId)}</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: system-ui, -apple-system, sans-serif; max-width: 1040px; margin: 0 auto; padding: 16px; color: #1e293b; background: #f8fafc; line-height: 1.5; font-size: 14px; }
    h1 { font-size: 22px; margin-top: 0; color: #0f172a; border-bottom: 2px solid #cbd5e1; padding-bottom: 8px; }
    h2 { font-size: 18px; margin-top: 0; color: #334155; }
    h3 { font-size: 16px; margin-top: 0; }
    section { background: #ffffff; border-radius: 8px; padding: 20px; margin-bottom: 20px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .table-wrapper { width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; margin-top: 10px; margin-bottom: 12px; }
    table { width: 100%; border-collapse: collapse; text-align: left; min-width: 600px; font-size: 13px; }
    th, td { border: 1px solid #e2e8f0; padding: 8px 10px; }
    th { background: #f1f5f9; font-weight: 600; color: #475569; }
    .col-check { width: 36px; text-align: center; }
    .excerpt { max-height: 80px; overflow-y: auto; font-size: 12px; color: #64748b; }
    code { font-family: monospace; font-size: 12px; background: #f1f5f9; padding: 2px 4px; border-radius: 4px; word-break: break-all; }
    pre { background: #0f172a; color: #f8fafc; padding: 12px; border-radius: 6px; overflow-x: auto; font-size: 12px; font-family: monospace; }
    pre.stderr { background: #450a0a; color: #fecaca; }
    .warning-banner { background: #fff1f2; border: 1px solid #fecdd3; color: #be123c; padding: 12px 16px; border-radius: 6px; margin-bottom: 16px; font-weight: 500; }
    .btn { display: inline-block; padding: 8px 16px; font-size: 14px; font-weight: 600; border-radius: 6px; border: none; cursor: pointer; }
    .btn-primary { background: #2563eb; color: #ffffff; }
    .btn-primary:hover { background: #1d4ed8; }
    .btn-secondary { background: #64748b; color: #ffffff; margin-left: 8px; }
    .btn-secondary:hover { background: #475569; }
    .btn-danger { background: #dc2626; color: #ffffff; }
    .btn-danger:hover { background: #b91c1c; }
    .form-group { margin-bottom: 12px; }
    .form-group label { display: block; font-weight: 600; margin-bottom: 4px; }
    .form-group input { width: 100%; max-width: 400px; padding: 8px; border: 1px solid #cbd5e1; border-radius: 4px; font-size: 14px; }
    .form-group select { width: 100%; max-width: 400px; padding: 8px; border: 1px solid #cbd5e1; border-radius: 4px; font-size: 14px; background: #ffffff; }
    .form-group textarea { width: 100%; padding: 8px; border: 1px solid #cbd5e1; border-radius: 4px; font-size: 13px; font-family: inherit; }
    .inline-form { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin-bottom: 8px; }
    .inline-form select { padding: 6px 8px; border: 1px solid #cbd5e1; border-radius: 4px; font-size: 14px; }
    .inline-form .btn-secondary { margin-left: 0; }
    tr.row-selected td { background: #eff6ff; }
    .notice-banner { background: #fffbeb; border: 1px solid #fde68a; color: #92400e; padding: 12px 16px; border-radius: 6px; margin-bottom: 12px; font-weight: 500; }
    .form-desc { color: #64748b; margin-top: 0; margin-bottom: 12px; font-size: 13px; }
    .meta-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-bottom: 10px; }
    .meta-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px 14px; }
    .meta-card .label { font-size: 12px; color: #64748b; font-weight: 600; }
    .meta-card .value { font-size: 15px; font-weight: 700; color: #0f172a; margin-top: 4px; word-break: break-all; }
    .cli-result-section { border-left: 4px solid #2563eb; }
    .factor-bar { position: sticky; top: 0; z-index: 20; background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 8px 14px; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(15,23,42,0.08); }
    .factor-bar summary { cursor: pointer; }
    .factor-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 6px 18px; margin-top: 8px; max-height: 40vh; overflow-y: auto; }
    .factor-item { display: flex; gap: 8px; align-items: baseline; }
    .factor-item .fchip { flex: none; }
    .fq { font-size: 12px; color: #64748b; }
    .fchip { display: inline-block; font-size: 12px; font-weight: 700; padding: 2px 8px; border-radius: 999px; white-space: nowrap; }
    .fchip-moat { background: #dbeafe; color: #1e40af; }
    .fchip-trap { background: #ffedd5; color: #9a3412; }
    .fchip-other { background: #e2e8f0; color: #334155; }
    .badge { display: inline-block; font-size: 11px; padding: 1px 7px; border-radius: 999px; border: 1px solid #cbd5e1; color: #475569; background: #f8fafc; }
    .badge-ok { border-color: #16a34a; color: #15803d; background: #f0fdf4; }
    .muted { color: #64748b; }
    .ev-group { margin-top: 18px; }
    .ev-group-head { display: flex; align-items: baseline; justify-content: space-between; gap: 8px; border-bottom: 2px solid #e2e8f0; padding-bottom: 4px; }
    .ev-group-head h3 { margin: 0; }
    .btn-link { background: none; border: none; color: #2563eb; cursor: pointer; font-size: 13px; padding: 0; }
    .ev-card { display: flex; gap: 12px; align-items: flex-start; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 14px; margin-top: 10px; background: #ffffff; }
    .ev-card input[type=checkbox] { width: 20px; height: 20px; margin-top: 2px; flex: none; }
    .ev-card.ev-confirmed { border-color: #86efac; background: #f0fdf4; }
    .ev-body { flex: 1; min-width: 0; }
    .ev-meta { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; font-size: 12px; }
    .ev-title { font-size: 15px; font-weight: 600; margin: 6px 0; line-height: 1.4; overflow-wrap: anywhere; }
    .ev-title a { color: #0f172a; text-decoration: none; }
    .ev-title a:hover { color: #2563eb; text-decoration: underline; }
    .ev-detail { display: grid; grid-template-columns: 110px 1fr; gap: 4px 12px; margin: 0; font-size: 13px; }
    .ev-detail dt { color: #475569; font-weight: 600; }
    .ev-detail dd { margin: 0; overflow-wrap: anywhere; }
    .ev-id { margin-top: 6px; font-size: 11px; color: #94a3b8; }
    a.term { color: #1d4ed8; text-decoration: underline dotted; text-underline-offset: 2px; }
    .ref-list { display: grid; grid-template-columns: 140px 1fr; gap: 6px 14px; margin: 0; font-size: 13px; }
    .ref-list dt { font-weight: 700; color: #1e3a8a; scroll-margin-top: 240px; }
    .ref-list dd { margin: 0; }
    .ref-list dt:target, .ref-list dt:target + dd { background: #fef9c3; }
    @media (max-width: 480px) {
      body { padding: 8px; }
      section { padding: 12px; }
      .meta-grid { grid-template-columns: 1fr; }
      .ev-detail { grid-template-columns: 1fr; }
      .ev-detail dt { margin-top: 4px; }
      .factor-grid { grid-template-columns: 1fr; max-height: 30vh; }
      .ref-list { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <header>
    <h1>AI 기업 스코어카드 승인 검토</h1>
  </header>
  ${renderFactorBar()}

  ${lastResultBlock}

  <!-- (1) 실행 머리 -->
  <section>
    <h2>1. 실행 기본 정보</h2>
    <div class="meta-grid">
      <div class="meta-card"><div class="label">실행 ID (run_id)</div><div class="value">${escapeHtml(runId)}</div></div>
      <div class="meta-card"><div class="label">기준일 (as_of)</div><div class="value">${escapeHtml(asOf)}</div></div>
      <div class="meta-card"><div class="label">규칙 버전 (rule_version)</div><div class="value">${escapeHtml(ruleVersion)}</div></div>
      <div class="meta-card"><div class="label">승인 상태</div><div class="value">${escapeHtml(approvalStatusText)}</div></div>
    </div>
  </section>

  <!-- (2) 기업별 표 -->
  <section>
    <h2>2. 기업별 점수 및 순위 변동</h2>
    <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>기업명</th>
            <th>점수 및 순위 (기준선 → 현재)</th>
            <th>변경된 팩터</th>
            <th>승계된 팩터</th>
            <th>미결 팩터</th>
          </tr>
        </thead>
        <tbody>
          ${companyRows || '<tr><td colspan="5">기업 정보가 없습니다.</td></tr>'}
        </tbody>
      </table>
    </div>
  </section>

  <!-- (3) 리뷰 -->
  <section>
    <h2>3. 독립 검토(Review) 결과</h2>
    ${reviewContent}
  </section>

  <!-- (4) 근거 후보 목록 및 확정/제외 폼 -->
  <section>
    <h2>4. 수집 근거(Evidence) 후보 검토</h2>
    <p class="form-desc">
      후보 근거 총 ${escapeHtml(evidence.candidates || evidenceItems.length)}건 중 ${escapeHtml(evidence.selected || 0)}건 선택됨 (${escapeHtml(evidence.confirmed || 0)}건 확정 완료). 체크된 근거는 확정되고, 체크를 푼 근거는 제외(삭제)됩니다. 제목을 누르면 원문이 새 탭에서 열립니다.
    </p>
    <form method="POST" action="/approve/${escapeHtml(runId)}/confirm">
      <input type="hidden" name="candidate_ids" value="${escapeHtml(candidateIds)}" />
      ${evidenceGroups || '<p>근거 항목이 없습니다.</p>'}
      <div style="margin-top: 14px;">
        <div class="form-group">
          <label for="confirm_code">일회용 코드 (6자리):</label>
          <input type="text" id="confirm_code" name="code" required pattern="[0-9]{6}" maxlength="6" placeholder="터미널 확인" />
        </div>
        <button type="submit" name="confirm_action" value="apply" class="btn btn-primary">선택 근거 확정 / 미선택 제외</button>
      </div>
    </form>
  </section>

  <!-- (5) 활성 트리거 표 -->
  <section>
    <h2>5. 모니터링 활성 트리거</h2>
    <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>트리거 ID</th>
            <th>기업</th>
            <th>팩터</th>
            <th>관측 · 조건 · 다시 볼 것</th>
            <th>기한</th>
            <th>상태</th>
          </tr>
        </thead>
        <tbody>
          ${triggerRows || '<tr><td colspan="6">활성 트리거가 없습니다.</td></tr>'}
        </tbody>
      </table>
    </div>
  </section>

  <!-- (6) 미결 규칙 결정 -->
  <section>
    <h2>6. 미결 규칙 결정 (Pending Decisions)</h2>
    ${pendingDecisionsContent}
  </section>

  <!-- (7) 지문(해시) 목록 -->
  <section>
    <h2>7. 무결성 검증 지문 (Hashes)</h2>
    <div class="table-wrapper">
      <table>
        <thead>
          <tr><th style="width: 160px;">구성 요소</th><th>해시 값 (SHA-256)</th></tr>
        </thead>
        <tbody>
          ${hashRows || '<tr><td colspan="2">해시 정보가 없습니다.</td></tr>'}
        </tbody>
      </table>
    </div>
  </section>

  <!-- (8) 정성 판단 수정 -->
  <section>
    <h2>8. 정성 판단 수정</h2>
    ${renderJudgeSection(data, judgeFactor, judgeCompany)}
  </section>

  <!-- (참조) 규칙 용어 -->
  <section>
    <h2>참조. 근거 문장에 나오는 규칙 용어</h2>
    ${renderGlossary()}
  </section>

  <!-- (9) 승인 / 취소 폼 -->
  <section>
    <h2>9. 실행 승인 / 승인 취소</h2>
    ${approvalForm}
  </section>
  <script>
    document.querySelectorAll('[data-toggle-group]').forEach(function (b) {
      b.addEventListener('click', function () {
        var g = b.getAttribute('data-toggle-group');
        var boxes = Array.prototype.filter.call(document.querySelectorAll('.ev-card input[type=checkbox]'), function (x) {
          return x.closest('.ev-card').getAttribute('data-group') === g;
        });
        var all = boxes.every(function (x) { return x.checked; });
        boxes.forEach(function (x) { x.checked = !all; });
      });
    });
  </script>
</body>
</html>`;
}

function parseEvidenceList(params, key) {
  const vals = params.getAll ? params.getAll(key) : [params.get(key)];
  const result = [];
  for (const v of vals) {
    if (!v) continue;
    for (const part of String(v).split(',')) {
      const trimmed = part.trim();
      if (trimmed && !result.includes(trimmed)) {
        result.push(trimmed);
      }
    }
  }
  return result;
}

function createApprovals(options = {}) {
  const enabled = Boolean(options.enabled);
  const code = options.code !== undefined ? String(options.code) : '';
  // 2026-10-01 V2-13: 승인 모드에서 코드가 비면 코드 검사가 빈 문자열끼리 비교되어 통과한다. 생성 시점에 막는다.
  if (enabled && !/^\d{6}$/.test(code)) {
    throw new Error('승인 모드에는 6자리 숫자 일회용 코드(code)가 필요합니다');
  }
  const runCli = typeof options.runCli === 'function' ? options.runCli : defaultRunCli;
  const onApproved = typeof options.onApproved === 'function' ? options.onApproved : null;
  const log = typeof options.log === 'function' ? options.log : (msg) => console.error(msg);
  // 잘못된 코드가 MAX_CODE_FAILURES 번 오면 이 서버의 모든 POST 를 막는다. 풀려면 서버를 다시 띄워 새 코드를 받는다.
  let codeFailures = 0;

  function handle(req, res) {
    const rawUrl = req.url || '/';
    const rawPath = rawUrl.split('?')[0];

    // /approve 로 시작하는 요청인지 원본 경로(rawPath)로 판별
    if (rawPath !== '/approve' && !rawPath.startsWith('/approve/')) {
      return false;
    }

    if (!enabled) {
      sendText(res, 404, 'Not Found: Approvals mode is not enabled');
      return true;
    }

    const remoteAddress = req.socket && req.socket.remoteAddress;
    if (!isLoopback(remoteAddress)) {
      sendText(res, 403, 'Forbidden: Loopback requests only');
      return true;
    }

    if (req.method === 'POST' && codeFailures >= MAX_CODE_FAILURES) {
      sendText(res, 403, `Forbidden: ${MAX_CODE_FAILURES} invalid codes - restart the server`);
      return true;
    }

    // 경로 조작(..) 시도 검출
    if (rawPath.includes('..')) {
      sendText(res, 400, 'Bad Request: Invalid run_id path traversal');
      return true;
    }

    let pathname;
    let query;
    try {
      const urlObj = new URL(rawUrl, 'http://127.0.0.1');
      pathname = urlObj.pathname;
      query = urlObj.searchParams;
    } catch (_) {
      sendText(res, 400, 'Bad Request: Malformed URL');
      return true;
    }

    const subPath = pathname.slice('/approve'.length);
    const trimmedPath = subPath.startsWith('/') ? subPath.slice(1) : subPath;
    const segments = trimmedPath.split('/').filter(Boolean);

    if (segments.length === 0) {
      sendText(res, 400, 'Bad Request: Missing run_id');
      return true;
    }

    const runId = segments[0];
    if (!isValidRunId(runId)) {
      sendText(res, 400, 'Bad Request: Invalid run_id format');
      return true;
    }

    if (req.method === 'GET' && segments.length === 1) {
      runCli(['summary', runId, '--json'], (err, result) => {
        if (err || result.exitCode !== 0) {
          const detail = result ? (result.stderr || result.stdout) : (err && err.message);
          sendHtml(res, 500, renderErrorPage(500, '요약 데이터 조회 실패 (CLI)', detail));
          return;
        }

        let summaryData;
        try {
          summaryData = JSON.parse(result.stdout);
        } catch (jsonErr) {
          sendHtml(res, 500, renderErrorPage(500, '요약 데이터 JSON 파싱 실패', jsonErr.message));
          return;
        }

        // 판단 수정 절의 선택. 형식이 아니면 무시한다(페이지는 그대로 그린다).
        const judgeFactor = FACTOR_REGEX.test(query.get('factor') || '') ? query.get('factor') : null;
        const judgeCompany = COMPANY_ID_REGEX.test(query.get('company') || '') ? query.get('company') : null;
        sendHtml(res, 200, renderSummaryPage(summaryData, { judgeFactor, judgeCompany }));
      });
      return true;
    }

    if (req.method === 'POST' && segments.length === 2) {
      const action = segments[1];
      if (!['confirm', 'approve', 'revoke', 'judge'].includes(action)) {
        sendText(res, 404, 'Not Found: Invalid action');
        return true;
      }

      readBody(req, (err, rawBody) => {
        if (err) {
          sendText(res, 400, 'Bad Request: Failed to read request body');
          return;
        }

        const params = new URLSearchParams(rawBody);
        const submittedCode = (params.get('code') || '').trim();

        if (submittedCode !== code.trim()) {
          codeFailures += 1;
          if (codeFailures === MAX_CODE_FAILURES) {
            log(`코드 실패 ${MAX_CODE_FAILURES}회 — 서버를 다시 띄우세요`);
          }
          sendText(res, 403, 'Forbidden: Invalid approval code');
          return;
        }

        let cliArgs = [];
        if (action === 'confirm') {
          cliArgs.push('confirm', runId);
          const evidenceList = parseEvidenceList(params, 'evidence');
          let rejectList = parseEvidenceList(params, 'reject');

          const candidateIdsParam = params.get('candidate_ids');
          if (candidateIdsParam && rejectList.length === 0) {
            const allCandidates = candidateIdsParam.split(',').map((s) => s.trim()).filter(Boolean);
            rejectList = allCandidates.filter((cid) => !evidenceList.includes(cid));
          }

          if (evidenceList.length > 0) {
            cliArgs.push('--evidence', evidenceList.join(','));
          }
          if (rejectList.length > 0) {
            cliArgs.push('--reject', rejectList.join(','));
          }
        } else if (action === 'approve') {
          const by = (params.get('by') || params.get('name') || '').trim();
          const note = (params.get('note') || '').trim();
          cliArgs.push('approve', runId, '--by', by);
          if (note) {
            cliArgs.push('--note', note);
          }
          cliArgs.push('--via', 'browser');
        } else if (action === 'revoke') {
          const by = (params.get('by') || params.get('name') || '').trim();
          const note = (params.get('note') || params.get('reason') || '').trim();
          cliArgs.push('revoke', runId, '--by', by, '--note', note);
        } else if (action === 'judge') {
          const judgeArgs = buildJudgeArgs(runId, params);
          if (!judgeArgs) {
            sendText(res, 400, 'Bad Request: Invalid company or factor');
            return;
          }
          cliArgs = judgeArgs;
        }

        runCli(cliArgs, (cliErr, cliResult) => {
          runCli(['summary', runId, '--json'], (sumErr, sumResult) => {
            let summaryData = null;
            if (sumResult && sumResult.exitCode === 0) {
              try {
                summaryData = JSON.parse(sumResult.stdout);
              } catch (_) {
                summaryData = null;
              }
            }

            const pageOptions = {
              lastResult: {
                command: cliArgs.join(' '),
                exitCode: cliResult ? cliResult.exitCode : 1,
                stdout: cliResult ? cliResult.stdout : '',
                stderr: cliResult ? cliResult.stderr : (cliErr ? cliErr.message : ''),
              },
            };
            if (action === 'judge') {
              pageOptions.judgeFactor = cliArgs[5];
              pageOptions.judgeCompany = cliArgs[3];
              if (cliResult && cliResult.exitCode === 0) {
                pageOptions.notice = '판단 해시가 바뀌었다 — 에이전트에게 research → calculate → draft → review 를 다시 돌리게 한 뒤 새로고침해 승인한다. 지금 페이지의 점수는 아직 수정 전 값이다.';
              }
            }

            if (summaryData) {
              sendHtml(res, 200, renderSummaryPage(summaryData, pageOptions));
            } else {
              sendHtml(res, 200, renderErrorPage(200, '작업 결과', `명령 실행 완료: ${cliArgs.join(' ')}\n\n표준 출력:\n${cliResult ? cliResult.stdout : ''}\n\n표준 오류:\n${cliResult ? cliResult.stderr : ''}`));
            }

            if (action === 'approve' && cliResult && cliResult.exitCode === 0) {
              if (typeof onApproved === 'function') {
                setTimeout(onApproved, 100);
              }
            }
          });
        });
      });
      return true;
    }

    sendText(res, 404, 'Not Found');
    return true;
  }

  return {
    handle,
    isLoopback,
    isValidRunId,
    code,
    enabled,
  };
}

module.exports = {
  createApprovals,
  isLoopback,
  isValidRunId,
  escapeHtml,
  defaultRunCli,
};
