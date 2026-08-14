/* Full-page renders for review. */
const { chromium } = require('playwright');

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await (await b.newContext({ viewport: { width: 1440, height: 1000 } })).newPage();
  const BASE = 'http://localhost:8899';
  for (const [name, url] of [['rev-home', '/'], ['rev-chapter', '/retrieval-practice/']]) {
    await p.goto(BASE + url, { waitUntil: 'networkidle' });
    await p.evaluate(() => window.scrollTo(0, 0));
    await p.screenshot({ path: `/tmp/${name}-full.png`, fullPage: true });
  }
  // measure the reading line length in the main text blocks
  const m = await p.evaluate(() => {
    const out = {};
    const sample = (sel, label) => {
      const el = document.querySelector(sel);
      if (!el) return;
      const cs = getComputedStyle(el);
      const px = el.getBoundingClientRect().width;
      const fs = parseFloat(cs.fontSize);
      // rough chars-per-line: average glyph ~0.5em for this stack
      out[label] = { widthPx: Math.round(px), fontPx: Math.round(fs), approxChars: Math.round(px / (fs * 0.5)) };
    };
    sample('.prose-block p', 'prose paragraph');
    sample('.strategy__body p', 'card paragraph');
    sample('.hero .lead', 'hero lead');
    sample('.hero .meta', 'hero meta');
    sample('.site-footer p', 'footer paragraph');
    return out;
  });
  console.log(JSON.stringify(m, null, 2));
  await b.close();
})();
