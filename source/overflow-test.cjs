/* Find which elements overflow the viewport at 200% text on a narrow screen.

   WCAG 2.2 reflow (1.4.10) is the target: 320 CSS pixels of content at 400%,
   which is the same thing as 1280 at 100%. Two widths are checked because the
   failures differ: 640 at 200% catches wrapping problems, 320 at 100% catches
   anything with a hard minimum width.
*/
const { chromium } = require('playwright');

const PAGES = [
  '/', '/find-a-strategy/', '/get-the-guide/',
  '/retrieval-practice/', '/formative-assessment/', '/feedback/',
  '/questioning-and-discussion/', '/explanations-and-modelling/',
  '/metacognition-and-self-regulation/',
];

const CASES = [
  { label: '640px at 200% text', width: 640, zoom: '200%' },
  { label: '320px at 100% text', width: 320, zoom: '100%' },
];

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  let total = 0;

  for (const c of CASES) {
    console.log(c.label);
    const ctx = await b.newContext({ viewport: { width: c.width, height: 900 } });
    const p = await ctx.newPage();
    for (const path of PAGES) {
      await p.goto('http://localhost:8899' + path, { waitUntil: 'networkidle' });
      await p.evaluate(z => { document.documentElement.style.fontSize = z; }, c.zoom);
      await p.waitForTimeout(250);
      const bad = await p.evaluate(() => {
        const w = document.documentElement.clientWidth;
        const out = [];
        document.querySelectorAll('*').forEach(el => {
          const r = el.getBoundingClientRect();
          if (r.width === 0 && r.height === 0) return;      // hidden, so irrelevant
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
        return {
          count: out.length,
          scrolls: document.documentElement.scrollWidth > w + 1,
          sample: out.slice(0, 12),
        };
      });
      total += bad.count;
      const flag = bad.count || bad.scrolls ? 'FAIL' : 'ok  ';
      console.log(`  ${flag} ${path}  ${bad.count} overflowing${bad.scrolls ? ', page scrolls sideways' : ''}`);
      bad.sample.forEach(x =>
        console.log(`       ${x.tag}.${x.cls} L${x.left} R${x.right} W${x.width} "${x.text}"`));
    }
    await ctx.close();
  }

  await b.close();
  console.log(total ? `\n${total} OVERFLOWING ELEMENT(S)` : '\nNothing overflows at either width.');
})();
