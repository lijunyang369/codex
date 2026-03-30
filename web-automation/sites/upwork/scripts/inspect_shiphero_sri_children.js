const http = require('http');

async function getJson(url) {
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

async function evaluate(expression) {
  const targets = await getJson('http://172.31.208.1:9223/json/list');
  const target = targets.find(
    (t) =>
      t.type === 'page' &&
      typeof t.url === 'string' &&
      t.url.includes('/nx/proposals/job/~022035994848742629554/apply/')
  );
  if (!target || !target.webSocketDebuggerUrl) {
    throw new Error('ShipHero proposal page not found');
  }

  const ws = new WebSocket(target.webSocketDebuggerUrl);
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

  ws.close();
  return result.result.value;
}

const expression = `(() => {
  const summarize = (vm) => ({
    name: vm.$options?.name || vm.$options?._componentTag || null,
    props: Object.keys(vm._props || {}),
    data: Object.keys(vm._data || {}),
    methods: Object.keys(vm).filter((k) => typeof vm[k] === 'function' && !k.startsWith('_')).slice(0, 20),
    children: (vm.$children || []).map((child) => child.$options?.name || child.$options?._componentTag || null),
  });

  const h3 = [...document.querySelectorAll('h3')].find((el) =>
    (el.innerText || '').includes('Schedule a rate increase')
  );
  const sri = h3.parentElement.__vue__;
  return {
    sri: summarize(sri),
    childSummaries: (sri.$children || []).map((child) => summarize(child)),
  };
})()`;

evaluate(expression)
  .then((value) => {
    console.log(JSON.stringify(value, null, 2));
  })
  .catch((err) => {
    console.error(err && err.stack ? err.stack : String(err));
    process.exit(1);
  });
