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
  const h3 = [...document.querySelectorAll('h3')].find((el) =>
    (el.innerText || '').includes('Schedule a rate increase')
  );
  if (!h3 || !h3.parentElement || !h3.parentElement.__vue__) {
    return { error: 'SRI component not found' };
  }

  const sriVm = h3.parentElement.__vue__;
  const termsVm = sriVm.$parent.$parent.$parent;

  sriVm.rateIncrease = { rate: 5, cadenceMonths: 12 };
  termsVm.percent = 5;
  termsVm.frequency = 12;

  if (typeof sriVm.validateSriValues === 'function') {
    sriVm.validateSriValues();
  }
  if (typeof termsVm.validateForm === 'function') {
    termsVm.validateForm();
  }
  if (typeof sriVm.$forceUpdate === 'function') {
    sriVm.$forceUpdate();
  }
  if (typeof termsVm.$forceUpdate === 'function') {
    termsVm.$forceUpdate();
  }

  return {
    sriData: {
      rateIncrease: sriVm.rateIncrease,
      isEditForm: sriVm.isEditForm,
    },
    termsData: {
      percent: termsVm.percent,
      frequency: termsVm.frequency,
      chargedAmount: termsVm.chargedAmount,
      earnedAmount: termsVm.earnedAmount,
    },
    bodyHasFreqError: document.body.innerText.includes('Enter a rate-increase frequency.'),
    bodyHasPercentError: document.body.innerText.includes('Enter a rate-increase percent.'),
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
