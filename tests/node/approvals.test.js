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
