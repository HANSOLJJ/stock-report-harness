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
      <div class="ev-card${confirmed ? ' ev-confirmed' : ''}" data-group="${escapeHtml(cid)}" id="ev-${escapeHtml(eid)}">
        ${confirmed
    ? `<button type="submit" class="btn-link ev-revert" name="revert" value="${escapeHtml(eid)}" title="확정을 번복해 후보로 되돌립니다">번복</button>`
    : `<input type="checkbox" name="evidence" value="${escapeHtml(eid)}" id="chk_${escapeHtml(eid)}" checked aria-label="${escapeHtml(eid)} 확정" />`}
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

// 2026-10-01 사용자 요청: 8절을 다시 만든다. factor 를 고를 때 페이지를 다시 불러오지 않고(맨 위로 튀지 않게) 탭으로 바꾸며,
// 표 대신 기업 카드에 지금 값을 말로 풀어 보이고, 카드 안에서 바로 수정 칸을 연다. 입력 키는 한국어 이름과 뜻으로 보인다.
const INPUT_LABELS = {
  A: { label: '동맹 등급', help: '+2 지분 걸린 동맹이 복수이거나 경쟁사까지 내 매대에 편입 · +1 의미 있는 상업 동맹이 소수 · 0 독립 상업 동맹 없음' },
  H: { label: '적대 등급', help: '0 눈에 띄는 적대 없음 · -1 비용형(벌금·소송·조사·시장 일부 차단) · -2 구조형(주요 고객이 경쟁자, 사업 정당성 표적) · -3 다발형' },
  imitation: { label: '모방 불가능성', help: '선두가 내 방식을 베끼면 선두 자신의 수익모델이 무너지는가' },
  revenue_model: { label: '별도 수익모델', help: '선두와 다른 수익모델로 들어왔는가' },
  acceleration: { label: '후발 가속도', help: 'AI 에 귀속되는 성장률이 빨라지고 있는가' },
  door_closed: { label: '문 닫기(후발 차단)', help: '선두 가격 결정력 붕괴·점유율 역전 같은 실측 증거가 있는가' },
  funding_dependent_share: { label: '조달 의존 고객 비중', help: '내 매출 가운데 투자·부채로 지출하는 고객의 비중' },
  own_money_returns: { label: '내 돈이 돌아오는가', help: '내가 고객에게 넣은 돈이 고객을 거쳐 내 매출로 돌아오는가' },
  operating_result_reviewed: { label: '영업손익 (게이트 1)', help: '본업이 이익인가 손실인가' },
  bep_retreat: { label: 'BEP 목표 후퇴 (게이트 1)', help: '손익분기 목표 시점이 뒤로 밀렸는가' },
  buffer_erosion: { label: '완충 잠식 (게이트 1)', help: '현금과 확정 미인출 여신이 줄고 있는가' },
  direction_A: { label: '방향 A (게이트 1 완화)', help: '영업손실률이 4분기 연속 전년 대비 개선되는가' },
  direction_B: { label: '방향 B (게이트 1 완화)', help: '매출 성장률이 비용 성장률보다 큰가' },
  fcf_trend: { label: 'FCF 추세 (게이트 2)', help: '최근 1년 잉여현금흐름이 흑자일 때 그 추세가 안정적인가' },
  coverage_comparable: { label: '커버리지 비교 가능 (게이트 4)', help: '약정 지출과 계약 수입을 같은 범위로 비교할 수 있는가' },
};
const VALUE_LABELS = {
  pass: '충족', partial: '절반', fail: '미충족', unknown: '모름', yes: '예', no: '아니오',
  large: '큼', small: '작음', stable: '안정', deteriorating: '악화', profit: '이익', loss: '손실',
};
const STATUS_LABELS = { carried: '이전 판단 승계', new: '이번 실행 판단' };

function inputLabel(key) {
  return INPUT_LABELS[key] ? INPUT_LABELS[key].label : key;
}

function valueText(v) {
  const s = String(v);
  if (VALUE_LABELS[s]) return VALUE_LABELS[s];
  return /^[0-9]+$/.test(s) && s !== '0' ? `+${s}` : s;
}

// 지금 값을 한 줄로 말한다. ⑤ 는 규칙이 3 + 동맹 + 적대 로 계산하므로 결과 점수까지 보인다.
function judgmentValueHtml(j) {
  if (j.kind === 'score') {
    const range = Array.isArray(j.score_range) ? ` (범위 ${escapeHtml(j.score_range[0])} ~ ${escapeHtml(j.score_range[1])})` : '';
    const note = j.edit_kind && j.edit_kind !== 'score'
      ? `<div class="muted">이전 실행에서 점수로 승계했다. 판정 재료로 고치면 ${escapeHtml(EDIT_KIND_LABELS[j.edit_kind] || j.edit_kind)} 방식으로 바뀌고 점수는 규칙이 계산한다.</div>` : '';
    return `<div class="judge-value"><strong>점수 ${escapeHtml(j.score)}</strong>${range}</div>${note}`;
  }
  const inputs = Array.isArray(j.inputs) ? j.inputs : [];
  const parts = inputs.map((pr) => `<span class="judge-input"><span class="muted">${escapeHtml(inputLabel(pr.key))}</span> <strong>${escapeHtml(valueText(pr.value))}</strong></span>`).join('');
  let total = '';
  if (j.kind === 'grade') {
    const map = Object.fromEntries(inputs.map((pr) => [pr.key, Number(pr.value)]));
    if (Number.isInteger(map.A) && Number.isInteger(map.H)) {
      total = `<div class="judge-total">3 + 동맹 ${escapeHtml(valueText(map.A))} + 적대 ${escapeHtml(map.H)} = <strong>${escapeHtml(3 + map.A + map.H)}점</strong></div>`;
    }
  } else {
    total = '<div class="muted">점수는 규칙이 이 판정 재료로 계산한다.</div>';
  }
  return `<div class="judge-value">${parts || '-'}</div>${total}`;
}

function renderJudgeForm(runId, j, choices, formId) {
  const editKind = j.edit_kind;
  let fields = '';
  if (editKind === 'score') {
    const range = Array.isArray(j.score_range) ? j.score_range : [];
    fields = `
        <div class="form-group">
          <label for="${formId}_score">점수 (${escapeHtml(range[0])} ~ ${escapeHtml(range[1])}):</label>
          <input type="number" id="${formId}_score" name="score" value="${escapeHtml(j.score)}" min="${escapeHtml(range[0])}" max="${escapeHtml(range[1])}" step="1" required />
        </div>`;
  } else {
    const current = {};
    for (const pr of (Array.isArray(j.inputs) ? j.inputs : [])) current[pr.key] = String(pr.value);
    const keys = choices[editKind] || {};
    fields = Object.keys(keys).map((key) => {
      const has = Object.prototype.hasOwnProperty.call(current, key);
      const opts = (has ? '' : '<option value="">(값 없음 — 고르지 않으면 바꾸지 않음)</option>')
        + keys[key].map((v) => `<option value="${escapeHtml(v)}"${has && current[key] === String(v) ? ' selected' : ''}>${escapeHtml(valueText(v))}${VALUE_LABELS[String(v)] ? ` (${escapeHtml(v)})` : ''}</option>`).join('');
      const help = INPUT_LABELS[key] && INPUT_LABELS[key].help ? `<div class="field-help">${escapeHtml(INPUT_LABELS[key].help)}</div>` : '';
      return `
        <div class="form-group">
          <label for="${formId}_in_${escapeHtml(key)}">${escapeHtml(inputLabel(key))}</label>
          ${help}
          <select id="${formId}_in_${escapeHtml(key)}" name="in_${escapeHtml(key)}">${opts}</select>
        </div>`;
    }).join('');
  }
  const evidenceText = (Array.isArray(j.evidence) ? j.evidence : []).join('\n');
  return `
      <form method="POST" action="/approve/${escapeHtml(runId)}/judge" class="judge-form" id="${formId}">
        <p class="form-desc">점수가 아니라 판단 입력을 고칩니다. 제출하면 판단 해시가 바뀌어 지금의 점수·초안·리뷰·승인이 무효가 되고, 이전 값은 수정 이력에 남습니다.</p>
        <input type="hidden" name="company" value="${escapeHtml(j.company_id)}" />
        <input type="hidden" name="factor" value="${escapeHtml(j.factor)}" />
        ${fields}
        <div class="form-group">
          <label for="${formId}_evidence">근거 문장 (한 줄에 하나)</label>
          <div class="field-help">바꿀 줄만 고치면 됩니다. 손대지 않으면 근거는 그대로 둡니다.</div>
          <textarea id="${formId}_evidence" name="evidence" rows="8">${escapeHtml(evidenceText)}</textarea>
          <input type="hidden" name="evidence_original" value="${escapeHtml(evidenceText)}" />
        </div>
        <div class="form-row">
          <div class="form-group">
            <label for="${formId}_reason">수정 사유</label>
            <input type="text" id="${formId}_reason" name="reason" required placeholder="왜 고치는지" />
          </div>
          <div class="form-group">
            <label for="${formId}_by">수정자 이름</label>
            <input type="text" id="${formId}_by" name="by" required placeholder="수정자 이름" />
          </div>
        </div>
        <button type="submit" class="btn btn-primary">판단 수정 제출</button>
      </form>`;
}

// 2026-10-01 사용자 요청: research 뒤 에이전트가 낸 판단 변경 제안. 사람은 반영·거부만 누른다. 거부는 사유가 필수다.
const PROPOSAL_ID_REGEX = /^PRP-\d{3}$/;
const PROPOSAL_STATUS_LABELS = { pending: '결정 전', accepted: '반영됨', rejected: '거부됨' };

function pairsToMap(pairs) {
  const m = {};
  for (const pr of (Array.isArray(pairs) ? pairs : [])) m[pr.key] = pr.value;
  return m;
}

function proposalChangeHtml(pr) {
  const before = pr.before || {};
  const beforeInputs = pairsToMap(before.inputs);
  const changes = Array.isArray(pr.changes) ? pr.changes : [];
  const rows = changes.map((c) => {
    const from = c.key === 'score' ? before.score : beforeInputs[c.key];
    const label = c.key === 'score' ? '점수' : inputLabel(c.key);
    return `<li><span class="muted">${escapeHtml(label)}</span> <strong>${escapeHtml(from === undefined || from === null ? '없음' : valueText(from))}</strong> → <strong class="to">${escapeHtml(valueText(c.value))}</strong></li>`;
  }).join('');
  let total = '';
  if (before.kind === 'grade' || pr.edit_kind === 'grade') {
    const after = Object.assign({}, beforeInputs, pairsToMap(changes));
    const a0 = Number(beforeInputs.A); const h0 = Number(beforeInputs.H);
    const a1 = Number(after.A); const h1 = Number(after.H);
    if ([a0, h0, a1, h1].every(Number.isInteger)) {
      total = `<li><span class="muted">⑤ 점수</span> <strong>${3 + a0 + h0}점</strong> → <strong class="to">${3 + a1 + h1}점</strong></li>`;
    }
  }
  return rows || total ? `<ul class="prop-changes">${rows}${total}</ul>` : '<p class="muted">판정 값은 그대로 두고 근거 문장만 고칩니다.</p>';
}

function proposalEvidenceDiffHtml(pr, ctx) {
  if (!Array.isArray(pr.evidence_after)) return '';
  const before = Array.isArray(pr.before && pr.before.evidence) ? pr.before.evidence : [];
  const after = pr.evidence_after;
  const removed = before.filter((s) => !after.includes(s));
  const added = after.filter((s) => !before.includes(s));
  const same = after.length - added.length;
  const line = (cls, mark, s) => `<li class="${cls}"><span class="mark">${mark}</span> ${linkTerms(escapeHtml(s), ctx)}</li>`;
  return `
        <div class="prop-label">근거 문장 바뀌는 줄 <span class="muted">(그대로 두는 줄 ${same}개)</span></div>
        <ul class="prop-diff">${removed.map((s) => line('del', '−', s)).join('')}${added.map((s) => line('add', '+', s)).join('')}</ul>`;
}

function renderProposalSection(data, ctx) {
  const runId = data.run_id || '';
  const proposals = Array.isArray(data.proposals) ? data.proposals : [];
  if (proposals.length === 0) {
    return '<p class="form-desc">에이전트가 낸 판단 변경 제안이 없습니다. 판단을 직접 고치려면 아래 "전체 판단 표" 를 씁니다.</p>';
  }
  const pending = proposals.filter((pr) => pr.status === 'pending').length;
  const cards = proposals.map((pr) => {
    const cited = (Array.isArray(pr.evidence_ids) ? pr.evidence_ids : [])
      .map((eid) => `<a class="term" href="#ev-${escapeHtml(eid)}">${escapeHtml(eid)}</a>`).join(', ');
    let actions = '';
    if (pr.status === 'pending' && pr.stale) {
      actions = '<div class="warning-banner">이 제안을 쓴 뒤 판단이 바뀌어 반영할 수 없습니다. 사유를 적어 거부하고 에이전트에게 다시 제안받으세요.</div>';
    }
    if (pr.status === 'pending') {
      const fid = `prop-${escapeHtml(pr.proposal_id)}`;
      actions += `
        <div class="prop-actions">
          ${pr.stale ? '' : `<form method="POST" action="/approve/${escapeHtml(runId)}/proposal" class="prop-form">
            <input type="hidden" name="id" value="${escapeHtml(pr.proposal_id)}" />
            <input type="hidden" name="decision" value="accept" />
            <input type="text" name="note" placeholder="메모 (선택)" aria-label="${escapeHtml(pr.proposal_id)} 반영 메모" />
            <button type="submit" class="btn btn-primary">반영</button>
          </form>`}
          <button type="button" class="btn btn-danger" data-open-reject="${fid}">거부</button>
          <form method="POST" action="/approve/${escapeHtml(runId)}/proposal" class="prop-form prop-reject" id="${fid}" hidden>
            <input type="hidden" name="id" value="${escapeHtml(pr.proposal_id)}" />
            <input type="hidden" name="decision" value="reject" />
            <label for="${fid}-note">거부 사유 (필수)</label>
            <textarea id="${fid}-note" name="note" rows="2" required placeholder="왜 거부하는지. 다음 실행에서 같은 제안이 올라올 때 참고합니다"></textarea>
            <button type="submit" class="btn btn-danger">거부 확정</button>
          </form>
        </div>`;
    } else {
      actions = `
        <div class="prop-decided">
          <span><strong>${escapeHtml(PROPOSAL_STATUS_LABELS[pr.status] || pr.status)}</strong> · ${escapeHtml(pr.decided_by || '-')} · ${escapeHtml(pr.decided_at || '-')}${pr.decision_note ? ` · ${pr.status === 'rejected' ? '거부 사유' : '메모'}: ${escapeHtml(pr.decision_note)}` : ''}</span>
          <form method="POST" action="/approve/${escapeHtml(runId)}/proposal" class="prop-form">
            <input type="hidden" name="id" value="${escapeHtml(pr.proposal_id)}" />
            <input type="hidden" name="decision" value="undo" />
            <button type="submit" class="btn btn-secondary" title="${pr.status === 'accepted' ? '판단을 반영 전 값으로 되돌리고 결정 전으로 돌립니다' : '결정 전으로 돌립니다'}">번복</button>
          </form>
        </div>`;
    }
    return `
      <div class="prop-card prop-${escapeHtml(pr.status)}" id="proposal-${escapeHtml(pr.proposal_id)}">
        <div class="judge-head">
          <h3>${escapeHtml(pr.display_name || pr.company_id)}</h3>${factorChips([pr.factor])}
          <span class="badge${pr.status === 'accepted' ? ' badge-ok' : pr.status === 'rejected' ? ' badge-warn' : ''}">${escapeHtml(PROPOSAL_STATUS_LABELS[pr.status] || pr.status)}</span>
          <span class="muted">${escapeHtml(pr.proposal_id)} · 제안 ${escapeHtml(pr.proposed_by)} · ${escapeHtml(pr.proposed_at)}</span>
        </div>
        <div class="prop-label">바뀌는 값</div>
        ${proposalChangeHtml(pr)}
        ${proposalEvidenceDiffHtml(pr, ctx)}
        <div class="prop-label">사유</div>
        <p class="prop-reason">${linkTerms(escapeHtml(pr.reason), ctx)}</p>
        ${cited ? `<div class="muted">인용 근거: ${cited}</div>` : ''}
        ${actions}
      </div>`;
  }).join('');
  return `
    <p class="form-desc">에이전트가 research 뒤 바꾸자고 낸 판단입니다. "반영" 을 누르면 그대로 판단을 고치고 인용 근거를 판단에 붙입니다. "거부" 는 사유를 적어야 합니다. 결정 전 ${pending}건.</p>
    ${cards}`;
}

// 판단 수정 절. factor 탭을 고르면 그 factor 의 모든 기업 판단을 카드로 나란히 보이고(Q03), 카드에서 수정 칸을 연다.
// 쿼리(?factor=&company=)로 들어오면 그 탭과 그 기업의 수정 칸을 연 채로 그리고, 그 칸의 id 는 judge-form 이다.
function renderJudgeSection(data, judgeFactor, judgeCompany, termCtx) {
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
  const active = editable.some((e) => e.factor === judgeFactor) ? judgeFactor : editable[0].factor;
  const ctx = termCtx || { runId, companyNames: {} };
  const tabs = editable.map((e) => `<button type="button" class="judge-tab" data-judge-tab="${escapeHtml(e.factor)}" aria-selected="${e.factor === active}">${escapeHtml(factorLabel(e.factor))}</button>`).join('');
  const panels = editable.map((e) => {
    const guide = FACTOR_GUIDE[e.factor];
    const cards = judgments.filter((j) => j.factor === e.factor).map((j) => {
      const selected = j.factor === judgeFactor && j.company_id === judgeCompany;
      const formId = selected ? 'judge-form' : `judge-form-${j.factor}-${j.company_id}`;
      const evidence = Array.isArray(j.evidence) ? j.evidence : [];
      const agent = j.last_revision_session === 'agent' ? ' <span class="badge badge-warn">에이전트 세션에서 수정</span>' : '';
      return `
      <div class="judge-card${selected ? ' judge-card-open' : ''}" id="judge-${escapeHtml(j.factor)}-${escapeHtml(j.company_id)}">
        <div class="judge-head">
          <h3>${escapeHtml(j.display_name || j.company_id)}</h3>
          <span class="badge">${escapeHtml(STATUS_LABELS[j.status] || j.status)}</span>${agent}
          <span class="muted">검토 ${escapeHtml(j.reviewer)} · ${escapeHtml(j.reviewed_at)}${j.revisions ? ` · 수정 ${escapeHtml(j.revisions)}회` : ''}</span>
        </div>
        ${judgmentValueHtml(j)}
        <details class="judge-evidence">
          <summary>근거 문장 ${evidence.length}줄 보기</summary>
          <ol>${evidence.map((s) => `<li>${linkTerms(escapeHtml(s), ctx)}</li>`).join('')}</ol>
        </details>
        <button type="button" class="btn btn-secondary judge-open" data-open-form="${formId}" aria-expanded="${selected}">${selected ? '수정 칸 닫기' : '이 판단 고치기'}</button>
        <div class="judge-form-wrap"${selected ? '' : ' hidden'}>${renderJudgeForm(runId, j, choices, formId)}</div>
      </div>`;
    }).join('');
    return `
    <div class="judge-panel" data-judge-panel="${escapeHtml(e.factor)}"${e.factor === active ? '' : ' hidden'}>
      <p class="judge-guide">${factorChips([e.factor])} <span>${escapeHtml(guide ? guide.question : '')}</span><br /><span class="muted">고치는 것: ${escapeHtml(EDIT_KIND_LABELS[e.edit_kind] || e.edit_kind)}. 같은 잣대가 모든 기업에 닿는지 나란히 보고 고칩니다.</span></p>
      ${cards}
    </div>`;
  }).join('');
  return `
    <p class="form-desc">위의 factor 탭을 고르면 그 factor 의 모든 기업 판단이 나옵니다. 고칠 기업 카드의 "이 판단 고치기" 를 누르면 그 카드 안에 수정 칸이 열립니다.</p>
    <div class="judge-tabs" role="tablist">${tabs}</div>
    ${panels}`;
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
  // 2026-10-01: summary 가 승인과 같은 계약 검증을 미리 돌린 결과. 없으면(예전 summary) 막지 않는다.
  const readiness = data.approval_ready || { ready: true, blockers: [] };
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

  // 2026-10-01 사용자 요청: 버튼을 누른 뒤 맨 위로 가지 않게, 결과는 화면 오른쪽 아래 알림 상자로 띄운다.
  let lastResultBlock = '';
  if (lastResult) {
    const ok = Number(lastResult.exitCode) === 0;
    lastResultBlock = `
    <aside class="toast ${ok ? 'toast-ok' : 'toast-fail'}" role="status" id="result-toast">
      <div class="toast-head"><strong>${ok ? '완료' : '실패'}</strong> <code>${escapeHtml(lastResult.command)}</code>
        <button type="button" class="toast-close" aria-label="닫기" onclick="this.closest('.toast').remove()">×</button></div>
      ${notice ? `<div class="toast-notice">${escapeHtml(notice)}</div>` : ''}
      ${!ok && lastResult.stderr ? `<pre class="stderr">${escapeHtml(lastResult.stderr)}</pre>` : ''}
      <details><summary>자세히</summary>
        ${lastResult.stdout ? `<pre>${escapeHtml(lastResult.stdout)}</pre>` : ''}
        ${ok && lastResult.stderr ? `<pre class="stderr">${escapeHtml(lastResult.stderr)}</pre>` : ''}
        <div class="muted">종료 코드 ${escapeHtml(lastResult.exitCode)}</div>
      </details>
    </aside>`;
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
  // 2026-10-01: 일괄 확정·제외는 아직 후보인 근거만 다룬다. 확정 근거의 체크를 풀어 삭제되던 위험을 없앤다.
  const pendingEvidence = evidenceItems.filter((item) => item.status !== 'confirmed');
  const candidateIds = pendingEvidence.map((item) => item.evidence_id).join(',');
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
  } else if (!readiness.ready) {
    const blockers = Array.isArray(readiness.blockers) ? readiness.blockers : [];
    approvalForm = `
      <div class="warning-banner">
        <strong>아직 승인할 수 없습니다.</strong> 근거 확정이나 판단 수정으로 입력이 바뀌었거나, 계산·초안·리뷰가 끝나지 않았습니다.
        에이전트에게 <code>research → calculate → draft → review</code> 를 돌리게 한 뒤 이 페이지를 새로고침하세요.
      </div>
      <details><summary>막힌 이유 ${blockers.length}건</summary>
        <ul>${blockers.map((b) => `<li><code>${escapeHtml(b)}</code></li>`).join('')}</ul>
      </details>`;
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
    [hidden] { display: none !important; }   /* 2026-10-01: .prop-form 의 display:flex 가 hidden 을 덮어써 거부 칸이 처음부터 펼쳐졌다 */
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
    .notice-banner { background: #fffbeb; border: 1px solid #fde68a; color: #92400e; padding: 12px 16px; border-radius: 6px; margin-bottom: 12px; font-weight: 500; }
    .form-desc { color: #64748b; margin-top: 0; margin-bottom: 12px; font-size: 13px; }
    .meta-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-bottom: 10px; }
    .meta-card { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px 14px; }
    .meta-card .label { font-size: 12px; color: #64748b; font-weight: 600; }
    .meta-card .value { font-size: 15px; font-weight: 700; color: #0f172a; margin-top: 4px; word-break: break-all; }
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
    .judge-tabs { display: flex; flex-wrap: wrap; gap: 6px; margin: 8px 0 12px; }
    .judge-tab { border: 1px solid #cbd5e1; background: #f8fafc; color: #334155; border-radius: 999px; padding: 6px 12px; font-size: 13px; font-weight: 600; cursor: pointer; }
    .judge-tab[aria-selected="true"] { background: #1d4ed8; border-color: #1d4ed8; color: #ffffff; }
    .judge-guide { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 10px 12px; font-size: 13px; }
    .judge-card { border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 14px; margin-top: 10px; scroll-margin-top: 230px; }
    .judge-card-open { border-color: #93c5fd; box-shadow: 0 0 0 2px #dbeafe; }
    .judge-head { display: flex; flex-wrap: wrap; align-items: baseline; gap: 8px; }
    .judge-head h3 { margin: 0; }
    .judge-value { display: flex; flex-wrap: wrap; gap: 6px 16px; margin-top: 8px; font-size: 14px; }
    .judge-input { white-space: nowrap; }
    .judge-total { margin-top: 4px; font-size: 14px; }
    .judge-evidence { margin: 8px 0; font-size: 13px; }
    .judge-evidence summary { cursor: pointer; color: #2563eb; }
    .judge-evidence ol { margin: 6px 0 0; padding-left: 22px; }
    .judge-evidence li { margin-bottom: 4px; overflow-wrap: anywhere; }
    .judge-form { border-top: 1px dashed #cbd5e1; margin-top: 10px; padding-top: 10px; scroll-margin-top: 230px; }
    .field-help { font-size: 12px; color: #64748b; margin-bottom: 4px; }
    .form-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 0 12px; }
    .badge-warn { border-color: #f59e0b; color: #b45309; background: #fffbeb; }
    .toast { position: fixed; right: 16px; bottom: 16px; z-index: 50; width: min(520px, calc(100vw - 32px)); max-height: 60vh; overflow: auto; background: #ffffff; border: 1px solid #cbd5e1; border-left-width: 5px; border-radius: 8px; padding: 10px 12px; box-shadow: 0 8px 24px rgba(15,23,42,0.18); font-size: 13px; }
    .toast-ok { border-left-color: #16a34a; }
    .toast-fail { border-left-color: #dc2626; }
    .toast-head { display: flex; gap: 6px; align-items: baseline; }
    .toast-head code { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .toast-close { border: none; background: none; font-size: 18px; cursor: pointer; color: #64748b; }
    .toast-notice { margin-top: 6px; color: #92400e; }
    .toast pre { max-height: 200px; }
    .confirm-bar { position: sticky; bottom: 0; background: #ffffff; padding: 10px 0; margin-top: 12px; border-top: 1px solid #e2e8f0; }
    .ev-revert { font-weight: 700; flex: none; }
    .prop-decided { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; margin-top: 10px; }
    .prop-card { border: 1px solid #c7d2fe; border-left: 4px solid #6366f1; border-radius: 8px; padding: 12px 14px; margin-top: 10px; }
    .prop-card.prop-accepted { border-left-color: #16a34a; border-color: #bbf7d0; }
    .prop-card.prop-rejected { border-left-color: #f59e0b; border-color: #fde68a; }
    .prop-label { margin-top: 10px; font-size: 12px; font-weight: 700; color: #475569; }
    .prop-changes { margin: 4px 0 0; padding-left: 18px; font-size: 14px; }
    .prop-changes .to { color: #1d4ed8; }
    .prop-diff { list-style: none; margin: 4px 0 0; padding: 0; font-size: 13px; }
    .prop-diff li { padding: 4px 8px; border-radius: 4px; margin-bottom: 3px; overflow-wrap: anywhere; }
    .prop-diff li.del { background: #fef2f2; color: #991b1b; text-decoration: line-through; }
    .prop-diff li.add { background: #f0fdf4; color: #166534; }
    .prop-diff .mark { font-weight: 700; margin-right: 4px; }
    .prop-reason { margin: 4px 0; }
    .prop-actions { display: flex; flex-wrap: wrap; gap: 8px; align-items: flex-start; margin-top: 10px; }
    .prop-form { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
    .prop-form input[type=text] { padding: 7px 8px; border: 1px solid #cbd5e1; border-radius: 4px; min-width: 200px; }
    .prop-reject { flex-basis: 100%; flex-direction: column; align-items: stretch; }
    .prop-reject textarea { width: 100%; padding: 8px; border: 1px solid #fca5a5; border-radius: 4px; font: inherit; }
    .prop-decided { margin-top: 8px; }
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
    <form method="POST" action="/approve/${escapeHtml(runId)}/confirm" id="evidence-form">
      <input type="hidden" name="candidate_ids" value="${escapeHtml(candidateIds)}" />
      ${evidenceGroups || '<p>근거 항목이 없습니다.</p>'}
      <div class="confirm-bar">
        ${pendingEvidence.length
    ? `<button type="submit" name="confirm_action" value="apply" class="btn btn-primary">후보 ${pendingEvidence.length}건: 체크한 것 확정 / 체크 푼 것 제외</button>`
    : '<span class="badge badge-ok">모든 근거가 확정됐습니다</span> <span class="muted">잘못 확정한 근거는 카드의 "번복" 으로 후보로 되돌립니다.</span>'}
      </div>
    </form>
  </section>

  <!-- (5) 판단 변경 제안 -->
  <section id="proposals">
    <h2>5. 판단 변경 제안</h2>
    ${renderProposalSection(data, termCtx)}
  </section>

  <!-- (5) 활성 트리거 표 -->
  <section>
    <h2>6. 모니터링 활성 트리거</h2>
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
    <h2>7. 미결 규칙 결정 (Pending Decisions)</h2>
    ${pendingDecisionsContent}
  </section>

  <!-- (7) 지문(해시) 목록 -->
  <section>
    <h2>8. 무결성 검증 지문 (Hashes)</h2>
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
    <h2>9. 전체 판단 표 (정성 판단 수정)</h2>
    ${renderJudgeSection(data, judgeFactor, judgeCompany, termCtx)}
  </section>

  <!-- (참조) 규칙 용어 -->
  <section>
    <h2>참조. 근거 문장에 나오는 규칙 용어</h2>
    ${renderGlossary()}
  </section>

  <!-- (9) 승인 / 취소 폼 -->
  <section>
    <h2>10. 실행 승인 / 승인 취소</h2>
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
    // 8절: factor 탭은 페이지를 다시 불러오지 않고 패널만 바꾼다. 카드의 버튼은 그 카드의 수정 칸을 열고 닫는다.
    document.querySelectorAll('[data-judge-tab]').forEach(function (b) {
      b.addEventListener('click', function () {
        var f = b.getAttribute('data-judge-tab');
        document.querySelectorAll('[data-judge-tab]').forEach(function (x) { x.setAttribute('aria-selected', String(x === b)); });
        document.querySelectorAll('[data-judge-panel]').forEach(function (p) { p.hidden = p.getAttribute('data-judge-panel') !== f; });
      });
    });
    document.querySelectorAll('[data-open-form]').forEach(function (b) {
      b.addEventListener('click', function () {
        var card = b.closest('.judge-card');
        var wrap = card.querySelector('.judge-form-wrap');
        var open = wrap.hidden;
        wrap.hidden = !open;
        card.classList.toggle('judge-card-open', open);
        b.setAttribute('aria-expanded', String(open));
        b.textContent = open ? '수정 칸 닫기' : '이 판단 고치기';
        if (open) { card.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
      });
    });
    document.querySelectorAll('[data-open-reject]').forEach(function (b) {
      b.addEventListener('click', function () {
        var f = document.getElementById(b.getAttribute('data-open-reject'));
        f.hidden = !f.hidden;
        if (!f.hidden) { f.querySelector('textarea').focus(); }
      });
    });
    // 2026-10-01 사용자 요청: 버튼을 누르면 결과 페이지가 맨 위에서 열리던 것을, 누르기 직전 보던 카드 위치로 되돌린다.
    var KEY = 'approvals-scroll';
    document.addEventListener('submit', function (ev) {
      var src = ev.submitter || ev.target;
      var anchor = src.closest('[id^="ev-"], [id^="proposal-"], [id^="judge-F"], section[id], .judge-card') || ev.target.closest('section');
      if (!anchor || !anchor.id) { anchor = ev.target.closest('[id]'); }
      try {
        if (anchor && anchor.id) {
          sessionStorage.setItem(KEY, JSON.stringify({ id: anchor.id, top: anchor.getBoundingClientRect().top, path: location.pathname.split('/').slice(0, 3).join('/') }));
        }
      } catch (e) { /* 저장소를 못 쓰면 위치 복원만 빠진다 */ }
    }, true);
    var restored = false;
    try {
      var saved = JSON.parse(sessionStorage.getItem(KEY) || 'null');
      sessionStorage.removeItem(KEY);
      if (saved && location.pathname.indexOf(saved.path) === 0) {
        var el = document.getElementById(saved.id);
        if (el) {
          var panel = el.closest('[data-judge-panel]');
          if (panel && panel.hidden) {
            var tab = document.querySelector('[data-judge-tab="' + panel.getAttribute('data-judge-panel') + '"]');
            if (tab) { tab.click(); }
          }
          window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - saved.top);
          restored = true;
        }
      }
    } catch (e) { /* 무시 */ }
    var openForm = document.getElementById('judge-form');
    if (!restored && openForm && !location.hash) { openForm.closest('.judge-card').scrollIntoView({ block: 'start' }); }
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
      if (!['confirm', 'approve', 'revoke', 'judge', 'proposal'].includes(action)) {
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

        // 2026-10-01 사용자 요청: 일회용 코드는 승인·취소에만 받는다. 근거 확정·판단 수정·제안 결정은 코드 없이 처리한다.
        // 승인·취소에 남기는 이유는 에이전트가 이 서버로 승인을 누르는 것을 막는 유일한 장치이기 때문이다.
        if (['approve', 'revoke'].includes(action) && submittedCode !== code.trim()) {
          codeFailures += 1;
          if (codeFailures === MAX_CODE_FAILURES) {
            log(`코드 실패 ${MAX_CODE_FAILURES}회 — 서버를 다시 띄우세요`);
          }
          sendText(res, 403, 'Forbidden: Invalid approval code');
          return;
        }

        let cliArgs = [];
        const revertId = (params.get('revert') || '').trim();
        if (action === 'confirm' && revertId) {
          // 2026-10-01: 확정 근거 번복은 그 근거 하나만 후보로 되돌린다(같은 폼의 다른 체크 상자는 무시한다).
          if (!/^EV-[a-z0-9-]+-\d{3}$/.test(revertId)) {
            sendText(res, 400, 'Bad Request: Invalid evidence id');
            return;
          }
          cliArgs.push('confirm', runId, '--revert', revertId);
        } else if (action === 'confirm') {
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
        } else if (action === 'proposal') {
          const id = (params.get('id') || '').trim();
          const decision = (params.get('decision') || '').trim();
          const note = (params.get('note') || '').trim();
          if (!PROPOSAL_ID_REGEX.test(id) || !['accept', 'reject', 'undo'].includes(decision)) {
            sendText(res, 400, 'Bad Request: Invalid proposal id or decision');
            return;
          }
          cliArgs = ['proposal', runId, '--id', id, { accept: '--accept', reject: '--reject', undo: '--undo' }[decision]];
          if (note) cliArgs.push(`--note=${note}`);
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
            if (action === 'proposal' && cliResult && cliResult.exitCode === 0 && ['--accept', '--undo'].includes(cliArgs[4])) {
              pageOptions.notice = '제안을 반영해 판단이 바뀌었다 — 에이전트에게 research → calculate → draft → review 를 다시 돌리게 한 뒤 새로고침해 승인한다. 지금 페이지의 점수는 아직 반영 전 값이다.';
            }
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
