/* Find which elements overflow the viewport at 200% text on a narrow screen. */
const { chromium } = require('playwright');

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await (await b.newContext({ viewport: { width: 640, height: 900 } })).newPage();
  await p.goto('http://localhost:8899/feedback/', { waitUntil: 'networkidle' });
  await p.evaluate(() => { document.documentElement.style.fontSize = '200%'; });
  await p.waitForTimeout(300);
  const bad = await p.evaluate(() => {
    const w = document.documentElement.clientWidth;
    const out = [];
    document.querySelectorAll('*').forEach(el => {
      const r = el.getBoundingClientRect();
      if (r.right > w + 1 || r.left < -1) {
        out.push({
          tag: el.tagName,
          cls: (el.className || '').toString().slice(0, 40),
          left: Math.round(r.left),
          right: Math.round(r.right),
          width: Math.round(r.width),
          text: (el.innerText || '').trim().slice(0, 30),
        });
      }
    });
    return { viewport: w, count: out.length, sample: out.slice(0, 25) };
  });
  console.log('viewport', bad.viewport, 'overflowing elements', bad.count);
  bad.sample.forEach(x => console.log(`  ${x.tag}.${x.cls} L${x.left} R${x.right} W${x.width} "${x.text}"`));
  await b.close();
})();
