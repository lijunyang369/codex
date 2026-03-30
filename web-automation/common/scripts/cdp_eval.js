const http = require('http');
const WebSocketImpl = globalThis.WebSocket;

if (!WebSocketImpl) {
  throw new Error('This Node runtime does not provide WebSocket');
}

function httpGetJson(url) {
  return new Promise((resolve, reject) => {
    http
      .get(url, (res) => {
        let data = '';
        res.on('data', (chunk) => {
          data += chunk;
        });
        res.on('end', () => {
          try {
            resolve(JSON.parse(data));
          } catch (err) {
            reject(err);
          }
        });
      })
      .on('error', reject);
  });
}

async function getWsUrl() {
  if (process.env.CDP_WS_URL) {
    return process.env.CDP_WS_URL;
  }

  const targets = await httpGetJson('http://172.31.208.1:9223/json/list');
  const upworkTarget =
    targets.find(
      (target) =>
        target.type === 'page' &&
        typeof target.url === 'string' &&
        target.url.includes('upwork.com/nx/proposals/job/')
    ) ||
    targets.find(
      (target) =>
        target.type === 'page' &&
        typeof target.url === 'string' &&
        target.url.includes('upwork.com')
    );

  if (!upworkTarget || !upworkTarget.webSocketDebuggerUrl) {
    throw new Error('Missing Upwork page target');
  }
  return upworkTarget.webSocketDebuggerUrl;
}

async function main() {
  const expression = process.argv.slice(2).join(' ');
  if (!expression) {
    throw new Error('Usage: node cdp_eval.js "<expression>"');
  }

  const wsUrl = await getWsUrl();
  const ws = new WebSocketImpl(wsUrl);
  let nextId = 1;

  const send = (method, params = {}) =>
    new Promise((resolve, reject) => {
      const id = nextId++;
      const onMessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.id !== id) {
          return;
        }
        ws.removeEventListener('message', onMessage);
        if (msg.error) {
          reject(new Error(JSON.stringify(msg.error)));
          return;
        }
        resolve(msg.result);
      };
      ws.addEventListener('message', onMessage);
      ws.send(JSON.stringify({ id, method, params }));
    });

  await new Promise((resolve, reject) => {
    ws.addEventListener('open', resolve, { once: true });
    ws.addEventListener('error', reject, { once: true });
  });

  const result = await send('Runtime.evaluate', {
    expression,
    awaitPromise: true,
    returnByValue: true,
  });

  console.log(JSON.stringify(result.result.value, null, 2));
  ws.close();
}

main().catch((err) => {
  console.error(err && err.stack ? err.stack : String(err));
  process.exit(1);
});
