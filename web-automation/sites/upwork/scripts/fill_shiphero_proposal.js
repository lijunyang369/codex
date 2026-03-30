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

const coverLetter = `Hello,

I can help lead this kind of integration work from an operations-first perspective, not just a pure coding perspective. My background combines hands-on systems development with end-to-end supply chain ownership in a cross-border apparel business, covering planning, production, warehousing, inventory, fulfillment, and logistics coordination.

I have direct experience integrating ecommerce and operations systems, including Shopify and multiple WMS/ERP-style workflows, and I am comfortable owning API, webhook, order sync, inventory sync, routing logic, exception handling, and tracking data flows across warehouse and delivery partners. I have also worked with self-built systems as well as platforms such as WangdianTong and Mabang, so I am used to messy real-world fulfillment environments where reliability matters more than slide-deck architecture.

While my background is not positioned as a dedicated ShipHero-only specialist, the core problem in this role is exactly where I am strong: connecting ecommerce, warehouse, and logistics systems into a stable operational workflow. I can communicate clearly in written English and Mandarin and work closely with technical and operations teams in China.

If helpful, I can start by reviewing your current integration landscape, identifying the main data flow risks, and then prioritizing the first implementation steps for store onboarding, inventory sync, courier connections, and exception handling.

Best regards,
Li`;

const q1 = `I have strong experience integrating WMS and other operational systems, including ERP-style workflows, inventory sync, order sync, and warehouse process automation. I have worked with self-built systems as well as tools such as WangdianTong and Mabang in cross-border ecommerce operations.

I do not position myself as a Cin7 specialist specifically, so I want to be accurate about that. However, the underlying integration work is very familiar to me: product and SKU mapping, inventory synchronization, order lifecycle updates, exception handling, and connecting warehouse data with upstream and downstream systems.`;

const q2 = `Yes. I have practical experience integrating Shopify with WMS and operational systems, including order import, inventory sync, status updates, tracking feedback, and exception workflows. I am familiar with Shopify data structures, operational edge cases, and the importance of keeping store, warehouse, and fulfillment data aligned in real time or near real time.`;

const q3 = `Yes. I have experience with API integrations between ecommerce / WMS environments and logistics providers, including shipment creation, status synchronization, tracking updates, and handling operational exceptions when data becomes inconsistent across systems. I understand the fulfillment side, not only the API side, which helps a lot when troubleshooting final-mile and warehouse issues.`;

const q4 = `Recently, my work has been centered on cross-border ecommerce operations where technology and supply chain execution are tightly connected. I was responsible at CTO and supply chain lead level, covering forecasting, replenishment, production coordination, warehouse operations, and logistics execution.

On the systems side, I have built and integrated backend tools and workflows around ecommerce operations, including Shopify-related workflows, custom systems, WMS/ERP-style integrations, and process automation. I have worked on real operational problems such as order routing, inventory accuracy, production-to-warehouse handoff, tracking synchronization, and reducing manual coordination across teams.

That combination of technical execution and operational understanding is why I believe I am a strong fit for this role.`;

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
  if (rate) {
    setField(rate, '45.00');
  }

  const texts = ${JSON.stringify([coverLetter, q1, q2, q3, q4])};
  const textareas = [...document.querySelectorAll('textarea')];
  texts.forEach((text, index) => {
    if (textareas[index]) {
      setField(textareas[index], text);
    }
  });

  return {
    rate: document.getElementById('step-rate')?.value,
    fee: document.getElementById('fee-rate')?.value,
    receive: document.getElementById('receive-step-rate')?.value,
    textareas: [...document.querySelectorAll('textarea')].map((t, i) => ({
      i,
      len: t.value.length,
      preview: t.value.slice(0, 60),
    })),
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
