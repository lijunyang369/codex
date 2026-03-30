const http = require('http');
const net = require('net');

const LISTEN_PORT = 9223;
const TARGET_HOST = '127.0.0.1';
const TARGET_PORT = 9222;

const server = http.createServer((req, res) => {
  const upstream = http.request(
    {
      host: TARGET_HOST,
      port: TARGET_PORT,
      path: req.url,
      method: req.method,
      headers: req.headers,
    },
    (upstreamRes) => {
      res.writeHead(upstreamRes.statusCode || 500, upstreamRes.headers);
      upstreamRes.pipe(res);
    }
  );

  req.pipe(upstream);
  upstream.on('error', (err) => {
    res.writeHead(502, { 'content-type': 'text/plain' });
    res.end(String(err));
  });
});

server.on('upgrade', (req, socket, head) => {
  const upstreamSocket = net.connect(TARGET_PORT, TARGET_HOST, () => {
    const headers = [
      `GET ${req.url} HTTP/1.1`,
      ...Object.entries(req.headers).map(([key, value]) => `${key}: ${value}`),
      '\r\n',
    ].join('\r\n');
    upstreamSocket.write(headers);
    if (head && head.length) {
      upstreamSocket.write(head);
    }
    socket.pipe(upstreamSocket).pipe(socket);
  });

  upstreamSocket.on('error', () => {
    socket.destroy();
  });
});

server.listen(LISTEN_PORT, '0.0.0.0', () => {
  console.log(`[chrome-cdp-proxy] listening on 0.0.0.0:${LISTEN_PORT} -> ${TARGET_HOST}:${TARGET_PORT}`);
});
