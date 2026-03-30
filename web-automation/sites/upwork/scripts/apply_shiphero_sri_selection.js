const http = require('http');

async function getJson(url) {
  return new Promise((resolve, reject) => {
    http.get(url, (res) => {
      let data = '';
      res.on('data', (chunk) => (data += chunk));
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (err) {
          reject(err);
        }
      });
    }).on('error', reject);
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
        if (msg.id !== id) return;
        ws.removeEventListener('message', onMessage);
        if (msg.error) return reject(new Error(JSON.stringify(msg.error)));
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
  const h3 = [...document.querySelectorAll('h3')].find((el) =>
    (el.innerText || '').includes('Schedule a rate increase')
  );
  const sri = h3.parentElement.__vue__;
  const form = sri.$children[0];
  const cadence = form.getCadenceMonthsList().find((item) => item.value === 12);
  const rate = form.getRateList().find((item) => item.value === 5);

  form.onCadenceMonthsChange(cadence);
  form.onRateChange(rate);
  sri.onRateChange({ cadenceMonths: 12, rate: 5 });
  sri.validateSriValues();

  return {
    cadence,
    rate,
    localCadenceMonths: form.localCadenceMonths,
    localRate: form.localRate,
    sriProps: {
      cadenceMonths: sri.$props.cadenceMonths,
      rate: sri.$props.rate,
    },
    text: document.body.innerText.slice(
      document.body.innerText.indexOf('Schedule a rate increase'),
      document.body.innerText.indexOf('Additional details')
    ),
  };
})()`;

evaluate(expression)
  .then((value) => console.log(JSON.stringify(value, null, 2)))
  .catch((err) => {
    console.error(err && err.stack ? err.stack : String(err));
    process.exit(1);
  });
