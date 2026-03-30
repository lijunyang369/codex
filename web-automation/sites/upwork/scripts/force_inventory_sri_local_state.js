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
      t.url.includes('/nx/proposals/job/~022036280203046168876/apply/')
  );
  if (!target || !target.webSocketDebuggerUrl) {
    throw new Error('Inventory proposal page not found');
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
  if (!h3 || !h3.parentElement || !h3.parentElement.__vue__) {
    return { error: 'sri component not found' };
  }

  const sri = h3.parentElement.__vue__;
  const form = sri.$children[0];
  const cadence = form.getCadenceMonthsList().find((item) => item.value === 12);
  const rate = form.getRateList().find((item) => item.value === 5);
  form.localCadenceMonths = cadence;
  form.localRate = rate;
  sri.rateIncrease = { cadenceMonths: 12, rate: 5 };

  const dropdowns = form.$children.filter((child) => child.$options?.name === 'UpCDropdown');
  if (dropdowns[0]) {
    dropdowns[0].internalSelected = [cadence];
    dropdowns[0].lastSelected = [cadence];
  }
  if (dropdowns[1]) {
    dropdowns[1].internalSelected = [rate];
    dropdowns[1].lastSelected = [rate];
  }

  const termsVm = sri.$parent.$parent.$parent;
  termsVm.percent = 5;
  termsVm.frequency = 12;

  if (typeof form.$forceUpdate === 'function') form.$forceUpdate();
  if (typeof sri.$forceUpdate === 'function') sri.$forceUpdate();
  if (typeof termsVm.$forceUpdate === 'function') termsVm.$forceUpdate();
  dropdowns.forEach((dd) => {
    if (typeof dd.$forceUpdate === 'function') dd.$forceUpdate();
  });

  return {
    cadence,
    rate,
    terms: { percent: termsVm.percent, frequency: termsVm.frequency },
    sriProps: { cadenceMonths: sri.$props.cadenceMonths, rate: sri.$props.rate },
    labels: [...document.querySelectorAll('.air3-dropdown-toggle-label')].map((el) => (el.innerText || '').trim()).slice(0, 8),
  };
})()`;

evaluate(expression)
  .then((value) => console.log(JSON.stringify(value, null, 2)))
  .catch((err) => {
    console.error(err && err.stack ? err.stack : String(err));
    process.exit(1);
  });
