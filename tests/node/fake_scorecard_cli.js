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
  const fixturePath = path.resolve(__dirname, 'fixtures', 'summary.sample.json');
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
