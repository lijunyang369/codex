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
    throw new Error('Inventory Shopify proposal page not found');
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

const coverLetter = `Hello,

This project matches my background very closely because my experience is not only in automation tooling, but in the real operational workflow behind bespoke orders, replenishment, production, warehouse execution, and logistics.

I previously worked at CTO and supply chain lead level in a cross-border apparel business, where I was responsible for forecasting, stock preparation, production coordination, warehouse operations, and fulfillment workflows. Because of that, I understand the operational logic behind factory batching, lead-time based restock planning, SKU structure, order exceptions, and the handoff between customer service, operations, and production.

On the systems side, I have hands-on experience building and integrating workflows around Shopify, internal tools, inventory processes, and back-office automation. I have also worked with WMS / ERP-style systems and real fulfillment operations, so I am comfortable designing solutions that are operationally usable, not just technically possible.

For a project like this, I would usually break the work into a few practical layers:
1. bespoke order batching and factory sheet generation
2. inventory / restock recommendation logic based on sales velocity and lead times
3. Shopify + Airtable + automation flow integration
4. centralized support workflow with clear rules, triggers, and reporting

I can also help document the workflow clearly for your internal team so the system is maintainable after launch.

Best regards,
Li`;

const expression = `(() => {
  const setField = (el, value) => {
    el.focus();
    if (typeof el.setSelectionRange === 'function') {
      el.setSelectionRange(0, el.value.length);
    }
    if (typeof el.setRangeText === 'function') {
      el.setRangeText(value, 0, el.value.length, 'end');
    } else {
      el.value = value;
    }
    el.dispatchEvent(new InputEvent('input', { bubbles: true, data: value, inputType: 'insertText' }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
  };

  const rate = document.getElementById('step-rate');
  if (rate) setField(rate, '25.00');

  const textarea = document.querySelector('textarea');
  if (textarea) setField(textarea, ${JSON.stringify(coverLetter)});

  return {
    rate: document.getElementById('step-rate')?.value,
    fee: document.getElementById('fee-rate')?.value,
    receive: document.getElementById('receive-step-rate')?.value,
    textareaLen: textarea?.value.length || 0,
    preview: textarea?.value.slice(0, 100) || '',
  };
})()`;

evaluate(expression)
  .then((value) => console.log(JSON.stringify(value, null, 2)))
  .catch((err) => {
    console.error(err && err.stack ? err.stack : String(err));
    process.exit(1);
  });
