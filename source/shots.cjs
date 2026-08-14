/* Render check shots of the built site. */
const { chromium } = require('playwright');

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await (await b.newContext({ viewport: { width: 1280, height: 1000 } })).newPage();
  const BASE = 'http://localhost:8899';
  const shots = [
    ['home', '/'],
    ['ch-feedback', '/feedback/'],
    ['ch-metacog', '/metacognition-and-self-regulation/'],
    ['ch-explanations', '/explanations-and-modelling/'],
  ];
  for (const [name, url] of shots) {
    await p.goto(BASE + url, { waitUntil: 'networkidle' });
    await p.screenshot({ path: `/tmp/${name}.png` });
  }
  // a strategy card in context
  await p.goto(BASE + '/questioning-and-discussion/#06-wait-time-1-after-you-ask', { waitUntil: 'networkidle' });
  await p.waitForTimeout(500);
  await p.screenshot({ path: '/tmp/card-detail.png' });
  // mobile
  await p.setViewportSize({ width: 390, height: 900 });
  await p.goto(BASE + '/retrieval-practice/', { waitUntil: 'networkidle' });
  await p.screenshot({ path: '/tmp/mobile.png' });
  await b.close();
  console.log('shots done');
})();
