// 승인 페이지 라우트, 일회용 코드 인증, CLI 연동 테스트
const test = require('node:test');
const assert = require('node:assert/strict');
const http = require('node:http');
const path = require('node:path');

const {
  createApprovals,
  isLoopback,
  isValidRunId,
} = require('../../server/approvals');

const FAKE_CLI_PATH = path.resolve(__dirname, 'fake_scorecard_cli.js');

// 2026-10-01 V2-13: 승인 모드에서 코드가 없거나 6자리 숫자가 아니면 라우트를 만들지 않는다
test('createApprovals: 승인 모드는 6자리 숫자 코드 없이 만들 수 없다', () => {
  for (const options of [{ enabled: true }, { enabled: true, code: '' }, { enabled: true, code: '12345' },
    { enabled: true, code: 'abcdef' }, { enabled: true, code: null }]) {
    assert.throws(() => createApprovals(options), /6자리/, JSON.stringify(options));
  }
  assert.doesNotThrow(() => createApprovals({ enabled: false }));
  assert.doesNotThrow(() => createApprovals({ enabled: true, code: '012345' }));
});

function makeRequest(server, options, body = null) {
  return new Promise((resolve, reject) => {
    const port = server.address().port;
    const req = http.request(
      {
        host: '127.0.0.1',
        port,
        path: options.path,
        method: options.method || 'GET',
        headers: options.headers || {},
      },
      (res) => {
        let responseBody = '';
        res.setEncoding('utf8');
        res.on('data', (chunk) => {
          responseBody += chunk;
        });
        res.on('end', () => {
          resolve({
            statusCode: res.statusCode,
            headers: res.headers,
            body: responseBody,
          });
        });
      }
    );
    req.on('error', reject);
    if (body) {
      req.write(body);
    }
    req.end();
  });
}

test('isLoopback() 단위 테스트', () => {
  assert.equal(isLoopback('127.0.0.1'), true);
  assert.equal(isLoopback('::1'), true);
  assert.equal(isLoopback('::ffff:127.0.0.1'), true);
  assert.equal(isLoopback('192.168.0.1'), false);
  assert.equal(isLoopback('10.0.0.1'), false);
  assert.equal(isLoopback('example.com'), false);
  assert.equal(isLoopback(''), false);
  assert.equal(isLoopback(null), false);
  assert.equal(isLoopback(undefined), false);
});

test('isValidRunId() 단위 테스트', () => {
  assert.equal(isValidRunId('ai-scorecard-2026-09-obsreg'), true);
  assert.equal(isValidRunId('ai-scorecard-2026-11-x'), true);
  assert.equal(isValidRunId('run-123'), true);
  assert.equal(isValidRunId('../x'), false);
  assert.equal(isValidRunId('UPPERCASE'), false);
  assert.equal(isValidRunId('has space'), false);
  assert.equal(isValidRunId('a'), false);
  assert.equal(isValidRunId(''), false);
  assert.equal(isValidRunId(null), false);
});

test('승인 모드 비활성화: GET /approve/<run_id> → 404', async () => {
  const approvals = createApprovals({ enabled: false });
  const server = http.createServer((req, res) => {
    if (approvals.handle(req, res)) return;
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('fallback');
  });

  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));

  try {
    const res = await makeRequest(server, { path: '/approve/ai-scorecard-2026-11-x' });
    assert.equal(res.statusCode, 404);
    assert.match(res.body, /Not Found/);
  } finally {
    server.close();
  }
});

test('잘못된 run_id: 400 Bad Request', async () => {
  const approvals = createApprovals({ enabled: true, code: '123456' });
  const server = http.createServer((req, res) => {
    if (approvals.handle(req, res)) return;
    res.writeHead(404);
    res.end('not handled');
  });

  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));

  try {
    const badIds = ['../x', 'UPPERCASE', 'a', ''];
    for (const badId of badIds) {
      const res = await makeRequest(server, { path: `/approve/${badId}` });
      assert.equal(res.statusCode, 400, `run_id '${badId}' should return 400`);
      assert.match(res.body, /Bad Request/);
    }
  } finally {
    server.close();
  }
});

test('승인 모드 활성화: GET /approve/<run_id> → 200 및 요약 필드 렌더링 확인', async () => {
  process.env.SCORECARD_CLI = `node ${FAKE_CLI_PATH}`;
  const approvals = createApprovals({ enabled: true, code: '123456' });
  const server = http.createServer((req, res) => {
    if (approvals.handle(req, res)) return;
    res.writeHead(404);
    res.end();
  });

  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));

  try {
    const res = await makeRequest(server, { path: '/approve/ai-scorecard-2026-11-x' });
    assert.equal(res.statusCode, 200);
    assert.match(res.headers['content-type'], /text\/html/);
    // 지시서 요구사항: 기업 표시명, evidence_id, 해시 일부가 본문에 있어야 함
    assert.match(res.body, /NVIDIA/, '기업 표시명(NVIDIA)이 포함되어야 함');
    assert.match(res.body, /EV-nvidia-001/, 'evidence_id가 포함되어야 함');
    assert.match(res.body, /345c3353372d0f95/, '해시 일부가 포함되어야 함');
    // 2026-10-01 사용자 요청(가독성): factor 이름·핵심 질문 고정 막대, 근거 카드의 판단 재료, 기업 표시명 묶음
    assert.match(res.body, /class="factor-bar"/, 'factor 안내 막대가 있어야 함');
    for (const label of ['① 네트워크 효과', '② 신기술 게임체인저', '⑤ 아군 확보', '⑨ 적자 깊이']) {
      assert.ok(res.body.includes(label), `factor 이름 ${label}`);
    }
    assert.match(res.body, /class="ev-card[^"]*" data-group="nvidia"/, '근거는 기업별 카드');
    assert.match(res.body, /고른 이유<\/dt><dd>추론: Blackwell/, '근거의 고른 이유가 보여야 함');
    // 2026-10-01 사용자 요청: 규칙 용어는 참조표로, 판단 ID 는 기업·factor 이름과 판단 수정 화면으로 연결
    assert.match(res.body, /<a class="term" href="#ref-star-F"[^>]*>별표 F<\/a>/);
    assert.match(res.body, /<a class="term" href="#ref-P3"[^>]*>P3<\/a>/);
    assert.match(res.body, /<a class="term" href="#ref-G2"[^>]*>게이트 2<\/a>/);
    assert.match(res.body, /href="\/approve\/ai-scorecard-2026-11-x\?factor=F2&amp;company=nvidia#judge-form"[^>]*>NVIDIA ② 신기술 게임체인저 판단<\/a>/);
    assert.match(res.body, /<dt id="ref-star-G">별표 G<\/dt>/, '참조표가 있어야 함');
    assert.match(res.body, /예상 영향<\/dt>/);
    assert.match(res.body, /확인 못 한 것<\/dt>/);
    assert.match(res.body, /기업 발표/, '매체 성격은 한국어 이름');
    assert.match(res.body, /2026\. 10\. 30\. 21:00 KST|2026\. 10\. 30\.? 21:00 KST/, '발행 시각은 KST');
    assert.match(res.body, /관측: Blackwell 생산 확대 발표/, '트리거의 관측');
  } finally {
    server.close();
  }
});

test('POST /approve: 코드 불일치 시 403 Forbidden 및 가짜 CLI 미호출', async () => {
  let cliCalled = false;
  const dummyRunCli = (args, cb) => {
    cliCalled = true;
    cb(null, { exitCode: 0, stdout: 'ok', stderr: '' });
  };

  const approvals = createApprovals({
    enabled: true,
    code: '654321',
    runCli: dummyRunCli,
  });

  const server = http.createServer((req, res) => {
    if (approvals.handle(req, res)) return;
    res.writeHead(404);
    res.end();
  });

  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));

  try {
    const body = 'code=000000&by=tester';
    const res = await makeRequest(
      server,
      {
        path: '/approve/ai-scorecard-2026-11-x/approve',
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      },
      body
    );

    assert.equal(res.statusCode, 403);
    assert.equal(cliCalled, false, '코드 불일치 시 CLI가 호출되면 안 됨');
  } finally {
    server.close();
  }
});

test('POST /approve: 코드 일치 시 200, 올바른 인자 전달, onApproved 1회 호출', async () => {
  process.env.SCORECARD_CLI = `node ${FAKE_CLI_PATH}`;
  delete process.env.FAKE_CLI_FAIL;

  let approvedCount = 0;
  const approvals = createApprovals({
    enabled: true,
    code: '123456',
    onApproved: () => {
      approvedCount += 1;
    },
  });

  const server = http.createServer((req, res) => {
    if (approvals.handle(req, res)) return;
    res.writeHead(404);
    res.end();
  });

  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));

  try {
    const body = 'code=123456&by=홍길동&note=정상승인메모';
    const res = await makeRequest(
      server,
      {
        path: '/approve/ai-scorecard-2026-11-x/approve',
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      },
      body
    );

    assert.equal(res.statusCode, 200);
    // 가짜 CLI stdout에 인자가 반영되어 결과 페이지에 출력되었는지 확인
    assert.match(res.body, /approve/);
    assert.match(res.body, /ai-scorecard-2026-11-x/);
    assert.match(res.body, /홍길동/);
    assert.match(res.body, /--via/);
    assert.match(res.body, /browser/);

    // onApproved 콜백 호출 대기
    await new Promise((resolve) => setTimeout(resolve, 200));
    assert.equal(approvedCount, 1, 'onApproved 콜백이 정확히 1회 호출되어야 함');
  } finally {
    server.close();
  }
});

test('POST /confirm: --evidence 와 --reject 를 올바르게 생성', async () => {
  let capturedArgs = null;
  const approvals = createApprovals({
    enabled: true,
    code: '123456',
    runCli: (args, cb) => {
      if (args[0] === 'confirm') {
        capturedArgs = args;
      }
      cb(null, { exitCode: 0, stdout: JSON.stringify({ ok: true }), stderr: '' });
    },
  });

  const server = http.createServer((req, res) => {
    if (approvals.handle(req, res)) return;
    res.writeHead(404);
    res.end();
  });

  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));

  try {
    const body = 'code=123456&evidence=EV-001,EV-002&reject=EV-003,EV-004';
    const res = await makeRequest(
      server,
      {
        path: '/approve/ai-scorecard-2026-11-x/confirm',
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      },
      body
    );

    assert.equal(res.statusCode, 200);
    assert.ok(capturedArgs, 'confirm 인자가 수집되어야 함');
    assert.deepEqual(capturedArgs, [
      'confirm',
      'ai-scorecard-2026-11-x',
      '--evidence',
      'EV-001,EV-002',
      '--reject',
      'EV-003,EV-004',
    ]);
  } finally {
    server.close();
  }
});

test('코드 실패 5회 뒤 모든 POST 403, CLI 미호출, 터미널 안내 1회', async () => {
  let cliCalls = 0;
  const logs = [];
  const approvals = createApprovals({
    enabled: true,
    code: '123456',
    runCli: (args, cb) => {
      cliCalls += 1;
      cb(null, { exitCode: 0, stdout: '{}', stderr: '' });
    },
    log: (msg) => logs.push(msg),
  });

  const server = http.createServer((req, res) => {
    if (approvals.handle(req, res)) return;
    res.writeHead(404);
    res.end();
  });

  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));

  const post = (action, body) => makeRequest(
    server,
    {
      path: `/approve/ai-scorecard-2026-11-x/${action}`,
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    },
    body
  );

  try {
    // 4번 틀린 뒤에는 아직 맞는 코드가 통한다.
    for (let i = 0; i < 4; i += 1) {
      assert.equal((await post('approve', 'code=000000&by=x')).statusCode, 403);
    }
    assert.equal(logs.length, 0);
    assert.equal((await post('confirm', 'code=123456&evidence=EV-nvidia-001')).statusCode, 200);
    assert.ok(cliCalls > 0);

    // 5번째 실패에서 막힌다. 그 뒤에는 맞는 코드도, 다른 동작도 403 이다.
    assert.equal((await post('approve', 'code=000000&by=x')).statusCode, 403);
    assert.deepEqual(logs, ['코드 실패 5회 — 서버를 다시 띄우세요']);
    const before = cliCalls;
    for (const action of ['approve', 'revoke', 'confirm']) {
      const res = await post(action, 'code=123456&by=x&note=n');
      assert.equal(res.statusCode, 403, `${action} 는 403 이어야 함`);
      assert.match(res.body, /restart the server/);
    }
    assert.equal(cliCalls, before, '잠긴 뒤에는 CLI 가 호출되면 안 됨');
    assert.equal(logs.length, 1, '안내는 한 번만 출력');
  } finally {
    server.close();
  }
});

test('CLI 실패 시 500 및 stderr 표시', async () => {
  process.env.SCORECARD_CLI = `node ${FAKE_CLI_PATH}`;
  process.env.FAKE_CLI_FAIL = '1';

  const approvals = createApprovals({ enabled: true, code: '123456' });
  const server = http.createServer((req, res) => {
    if (approvals.handle(req, res)) return;
    res.writeHead(404);
    res.end();
  });

  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));

  try {
    const res = await makeRequest(server, { path: '/approve/ai-scorecard-2026-11-x' });
    assert.equal(res.statusCode, 500);
    assert.match(res.body, /FAKE_CLI_ERROR: simulated failure/);
  } finally {
    delete process.env.FAKE_CLI_FAIL;
    server.close();
  }
});

// 2026-10-01 레인 J: 판단 수정 절과 POST /approve/<run_id>/judge
function startServer(options) {
  const approvals = createApprovals(options);
  const server = http.createServer((req, res) => {
    if (approvals.handle(req, res)) return;
    res.writeHead(404);
    res.end();
  });
  return new Promise((resolve) => server.listen(0, '127.0.0.1', () => resolve(server)));
}

function postForm(server, action, body) {
  return makeRequest(
    server,
    {
      path: `/approve/ai-scorecard-2026-11-x/${action}`,
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    },
    body
  );
}

test('GET ?factor=F3: 같은 factor 의 모든 기업 판단을 나란히, company 를 고르면 입력란', async () => {
  process.env.SCORECARD_CLI = `node ${FAKE_CLI_PATH}`;
  delete process.env.FAKE_CLI_FAIL;
  const server = await startServer({ enabled: true, code: '123456' });
  try {
    const list = await makeRequest(server, { path: '/approve/ai-scorecard-2026-11-x?factor=F3' });
    assert.equal(list.statusCode, 200);
    assert.match(list.body, /정성 판단 수정/);
    // 2026-10-01 사용자 요청: factor 탭(페이지를 다시 불러오지 않음) + 기업 카드 + 한국어 입력 이름
    assert.match(list.body, /data-judge-tab="F3" aria-selected="true">③ Last Mover<\/button>/, 'F3 탭이 열려 있어야 함');
    assert.match(list.body, /data-judge-panel="F3">/);
    assert.match(list.body, /모방 불가능성<\/span> <strong>미충족<\/strong>/, '지금 값은 한국어 이름과 값');
    assert.match(list.body, /별도 수익모델<\/span> <strong>충족<\/strong>/);
    assert.match(list.body, /모방 불가능성<\/span> <strong>절반<\/strong>/, '다른 기업(OpenAI)의 같은 factor 판단도 보여야 함');
    assert.match(list.body, /&lt;b&gt;태그&lt;\/b&gt;/, '근거 문장은 이스케이프');
    assert.doesNotMatch(list.body, /id="judge-form"/, '기업을 고르기 전에는 열린 입력란이 없다');
    assert.match(list.body, /<div class="judge-form-wrap" hidden>/, '수정 칸은 닫힌 채 카드 안에 있다');

    const form = await makeRequest(server, { path: '/approve/ai-scorecard-2026-11-x?factor=F3&company=nvidia' });
    assert.match(form.body, /<div class="judge-form-wrap"><\s*form method="POST" action="\/approve\/ai-scorecard-2026-11-x\/judge" class="judge-form" id="judge-form">|<div class="judge-form-wrap">\s*<form method="POST" action="\/approve\/ai-scorecard-2026-11-x\/judge" class="judge-form" id="judge-form">/, '고른 기업의 수정 칸이 열려 있어야 함');
    assert.match(form.body, /name="in_imitation"/);
    assert.match(form.body, /name="in_door_closed"/);
    assert.match(form.body, /<option value="fail" selected>미충족 \(fail\)<\/option>/);
    assert.match(form.body, /문 닫기\(후발 차단\)/, '입력란 이름은 한국어');
    assert.doesNotMatch(form.body.split('id="judge-form"')[1].split('</form>')[0], /name="score"/, 'criteria 판단에는 점수 입력란이 없다');
    assert.match(form.body, /name="reason"/);

    const score = await makeRequest(server, { path: '/approve/ai-scorecard-2026-11-x?factor=F1&company=nvidia' });
    assert.match(score.body, /name="score" value="2" min="0" max="5"/);

    const bad = await makeRequest(server, { path: '/approve/ai-scorecard-2026-11-x?factor=F3%22%3E&company=..%2Fx' });
    assert.equal(bad.statusCode, 200);
    assert.doesNotMatch(bad.body, /id="judge-form"/);
  } finally {
    server.close();
  }
});

test('POST /judge: 코드 불일치면 403, CLI 미호출', async () => {
  let cliCalled = false;
  const server = await startServer({
    enabled: true,
    code: '654321',
    runCli: (args, cb) => { cliCalled = true; cb(null, { exitCode: 0, stdout: '{}', stderr: '' }); },
  });
  try {
    const res = await postForm(server, 'judge', 'code=000000&company=nvidia&factor=F3&in_imitation=pass&reason=r&by=u');
    assert.equal(res.statusCode, 403);
    assert.equal(cliCalled, false);
  } finally {
    server.close();
  }
});

test('POST /judge: 인자 생성 — 판정 재료는 --set, 바뀐 근거만 --evidence=, 자유 입력은 --opt=value', async () => {
  const calls = [];
  const server = await startServer({
    enabled: true,
    code: '123456',
    runCli: (args, cb) => { calls.push(args); cb(null, { exitCode: 0, stdout: '{}', stderr: '' }); },
  });
  try {
    const body = new URLSearchParams({
      code: '123456', company: 'nvidia', factor: 'F3', in_imitation: 'pass', in_door_closed: '', 'in_bad-key': 'x',
      evidence: '- 하이픈으로 시작\r\n\r\n둘째 문장  ', evidence_original: '옛 문장', reason: '잣대 맞춤', by: '홍길동',
    }).toString();
    const res = await postForm(server, 'judge', body);
    assert.equal(res.statusCode, 200);
    assert.deepEqual(calls[0], [
      'judge', 'ai-scorecard-2026-11-x', '--company', 'nvidia', '--factor', 'F3',
      '--set', 'imitation=pass',
      '--evidence=- 하이픈으로 시작', '--evidence=둘째 문장',
      '--reason=잣대 맞춤', '--by=홍길동',
    ]);
    assert.deepEqual(calls[1], ['summary', 'ai-scorecard-2026-11-x', '--json']);
    assert.match(res.body, /판단 해시가 바뀌었다/);

    // 근거를 그대로 두면 --evidence 를 넘기지 않는다. 점수 판단은 score=N 이다.
    await postForm(server, 'judge', new URLSearchParams({
      code: '123456', company: 'nvidia', factor: 'F1', score: '3', evidence: 'a\nb', evidence_original: 'a\r\nb', reason: 'r', by: 'u',
    }).toString());
    assert.deepEqual(calls[2], ['judge', 'ai-scorecard-2026-11-x', '--company', 'nvidia', '--factor', 'F1',
      '--set', 'score=3', '--reason=r', '--by=u']);
  } finally {
    server.close();
  }
});

test('POST /judge: 기업·factor 형식이 아니면 400, CLI 미호출', async () => {
  let cliCalls = 0;
  const server = await startServer({
    enabled: true,
    code: '123456',
    runCli: (args, cb) => { cliCalls += 1; cb(null, { exitCode: 0, stdout: '{}', stderr: '' }); },
  });
  try {
    for (const [company, factor] of [['nvidia', 'F10'], ['nvidia', 'f3'], ['--x', 'F3'], ['../x', 'F3'], ['', 'F3']]) {
      const res = await postForm(server, 'judge', new URLSearchParams({ code: '123456', company, factor, reason: 'r', by: 'u' }).toString());
      assert.equal(res.statusCode, 400, `${company} ${factor}`);
    }
    assert.equal(cliCalls, 0);
  } finally {
    server.close();
  }
});

test('POST /judge: CLI 가 거부하면 안내 없이 stderr 를 보인다', async () => {
  const server = await startServer({
    enabled: true,
    code: '123456',
    runCli: (args, cb) => {
      if (args[0] === 'judge') return cb(null, { exitCode: 1, stdout: '', stderr: '[FAIL] F3 의 점수는 규칙이 판정 재료에서 계산한다' });
      return cb(null, { exitCode: 1, stdout: '', stderr: 'no summary' });
    },
  });
  try {
    const res = await postForm(server, 'judge', 'code=123456&company=nvidia&factor=F3&score=3&reason=r&by=u');
    assert.equal(res.statusCode, 200);
    assert.match(res.body, /규칙이 판정 재료에서 계산한다/);
    assert.doesNotMatch(res.body, /판단 해시가 바뀌었다/);
  } finally {
    server.close();
  }
});
