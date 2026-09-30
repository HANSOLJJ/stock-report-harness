#!/usr/bin/env node

const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = Number(process.env.PORT) || 3000;
const ROOT = path.resolve(__dirname, 'output');
const REQUESTED_REPORT = process.argv[2] || process.env.REPORT_SLUG || process.env.REPORT;

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.htm': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.webp': 'image/webp',
  '.ico': 'image/x-icon',
  '.txt': 'text/plain; charset=utf-8',
  // 실행 묶음의 audit.md·draft.md 를 브라우저에서 바로 읽게 한다. text/markdown 은 내려받기로 처리되는 브라우저가 있다.
  '.md': 'text/plain; charset=utf-8',
  '.pdf': 'application/pdf',
};

function send(res, statusCode, body, headers = {}) {
  res.writeHead(statusCode, {
    'Content-Type': 'text/plain; charset=utf-8',
    ...headers,
  });
  res.end(body);
}

function safeResolve(urlPath) {
  const decodedPath = decodeURIComponent(urlPath.split('?')[0]);
  const filePath = path.resolve(ROOT, `.${decodedPath}`);

  if (filePath !== ROOT && !filePath.startsWith(`${ROOT}${path.sep}`)) {
    return null;
  }

  return filePath;
}

function renderDirectoryListing(reqPath, entries) {
  const rows = entries
    .filter((entry) => !entry.name.startsWith('.'))
    .map((entry) => {
      const href = path.posix.join(reqPath, entry.name) + (entry.isDirectory() ? '/' : '');
      return `<li><a href="${href}">${entry.name}${entry.isDirectory() ? '/' : ''}</a></li>`;
    })
    .join('\n');

  return `<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>output static server</title>
  <style>
    body { font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; line-height: 1.5; }
    a { color: #2563eb; }
  </style>
</head>
<body>
  <h1>output/</h1>
  <ul>${rows || '<li>No files</li>'}</ul>
</body>
</html>`;
}

function toUrlPath(filePath) {
  const relativePath = path.relative(ROOT, filePath).split(path.sep).join('/');
  return `/${relativePath}`;
}

function reportUrl(filePath) {
  return `http://localhost:${PORT}${encodeURI(toUrlPath(filePath))}`;
}

// 실행 묶음 output/<run_id>/report.html 을 한 단계만 내려가 찾는다. name 은 run_id 다.
function findHtmlReports() {
  if (!fs.existsSync(ROOT)) {
    return [];
  }

  return fs
    .readdirSync(ROOT, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && !entry.name.startsWith('.'))
    .map((entry) => ({ name: entry.name, filePath: path.join(ROOT, entry.name, 'report.html') }))
    .filter((report) => fs.existsSync(report.filePath))
    .map((report) => ({ ...report, mtimeMs: fs.statSync(report.filePath).mtimeMs }))
    .sort((a, b) => b.mtimeMs - a.mtimeMs);
}

// run_id, output/<run_id>/, output/<run_id>/report.html 어느 형태로 받아도 run_id 로 맞춘다.
function normalizeRequestedReport(value) {
  if (!value) {
    return '';
  }

  const trimmed = String(value).trim().replace(/[\\/]+$/, '');
  const withoutFile = path.basename(trimmed) === 'report.html' ? path.dirname(trimmed) : trimmed;
  return path.basename(withoutFile).replace(/\.html$/, '');
}

function printReportLinks() {
  const reports = findHtmlReports();
  const requestedName = normalizeRequestedReport(REQUESTED_REPORT);
  const requestedReport = requestedName
    ? reports.find((report) => report.name === requestedName)
    : null;
  const latestReport = requestedReport || reports[0];

  console.log(`Serving ${ROOT} at http://localhost:${PORT}/`);

  if (requestedName && !requestedReport) {
    console.warn(`Requested report not found: output/${requestedName}`);
  }

  if (!latestReport) {
    console.log('No HTML reports found yet. Build a report into output/*.html, then reload this server.');
    return;
  }

  console.log(`Report URL: ${reportUrl(latestReport.filePath)}`);

  if (reports.length > 1) {
    console.log('Available reports:');
    reports.forEach((report) => console.log(`- ${reportUrl(report.filePath)}`));
  }
}

const server = http.createServer((req, res) => {
  if (!['GET', 'HEAD'].includes(req.method)) {
    return send(res, 405, 'Method Not Allowed', { Allow: 'GET, HEAD' });
  }

  let filePath;
  try {
    filePath = safeResolve(req.url || '/');
  } catch (_) {
    return send(res, 400, 'Bad Request');
  }

  if (!filePath) {
    return send(res, 403, 'Forbidden');
  }

  fs.stat(filePath, (statError, stats) => {
    if (statError) {
      return send(res, 404, 'Not Found');
    }

    if (stats.isDirectory()) {
      const reqPath = new URL(req.url || '/', `http://${req.headers.host || 'localhost'}`).pathname;
      // 묶음의 report.html 은 audit.md 를 상대 경로로 링크한다. 끝 슬래시가 없으면 링크가 한 단계 위로 풀린다.
      if (!reqPath.endsWith('/')) {
        res.writeHead(301, { Location: `${reqPath}/` });
        return res.end();
      }
      const indexPath = ['index.html', 'report.html']
        .map((name) => path.join(filePath, name))
        .find((candidate) => fs.existsSync(candidate));
      if (indexPath) {
        filePath = indexPath;
      } else {
        const entries = fs.readdirSync(filePath, { withFileTypes: true });
        const html = renderDirectoryListing(reqPath, entries);
        res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
        return res.end(req.method === 'HEAD' ? undefined : html);
      }
    }

    const ext = path.extname(filePath).toLowerCase();
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';
    res.writeHead(200, { 'Content-Type': contentType });

    if (req.method === 'HEAD') {
      return res.end();
    }

    fs.createReadStream(filePath).pipe(res);
  });
});

server.on('error', (error) => {
  if (error.code === 'EADDRINUSE') {
    console.error(`Port ${PORT} is already in use. Stop the existing server or run with PORT=<other-port> node server.js.`);
    process.exit(1);
  }

  throw error;
});

server.listen(PORT, printReportLinks);
