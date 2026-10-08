// 승인 페이지 테스트를 위한 scorecard_cli 가짜(mock) 스크립트
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);

if (process.env.FAKE_CLI_FAIL === '1') {
  console.error('FAKE_CLI_ERROR: simulated failure');
  process.exit(1);
}

const subCommand = args[0];
if (subCommand === 'summary') {
  // 2026-10-08: 규칙 v2.0 summary 처럼 다른 요약이 필요한 시험은 FAKE_SUMMARY 로 fixtures 아래 파일 이름을 고른다.
  const fixturePath = path.resolve(__dirname, 'fixtures', path.basename(process.env.FAKE_SUMMARY || 'summary.sample.json'));
  const content = fs.readFileSync(fixturePath, 'utf8');
  process.stdout.write(content);
  process.exit(0);
}

const output = {
  command: subCommand,
  args: args,
  received_at: new Date().toISOString(),
};
process.stdout.write(JSON.stringify(output, null, 2) + '\n');
process.exit(0);
