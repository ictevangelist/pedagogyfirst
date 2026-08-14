/* Accessibility and keyboard smoke tests for the built site.
   Serve the folder, then:  node source/a11y-test.cjs  */
const { chromium } = require('playwright');

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } });
  const p = await ctx.newPage();
  const BASE = 'http://localhost:8899';
  const pages = ['/', '/retrieval-practice/', '/feedback/', '/metacognition-and-self-regulation/'];
  let total = 0;

  for (const url of pages) {
    await p.goto(BASE + url, { waitUntil: 'networkidle' });
    const r = await p.evaluate(() => {
      const out = [];
      const h1 = document.querySelectorAll('h1');
      if (h1.length !== 1) out.push(`h1 count = ${h1.length}`);

      let last = 0;
      document.querySelectorAll('h1,h2,h3,h4,h5,h6').forEach(h => {
        const lvl = +h.tagName[1];
        if (last && lvl > last + 1) out.push(`heading jump h${last}->h${lvl}: ${h.textContent.trim().slice(0, 40)}`);
        last = lvl;
      });

      document.querySelectorAll('img').forEach(i => {
        if (!i.hasAttribute('alt')) out.push('img without alt: ' + i.getAttribute('src'));
      });

      // A link's accessible name can come from its text, an aria-label, or
      // the alt text of an image it wraps.
      document.querySelectorAll('a').forEach(a => {
        const img = a.querySelector('img[alt]');
        const name = (a.innerText || '').trim()
          || a.getAttribute('aria-label')
          || (img ? img.getAttribute('alt').trim() : '');
        if (!name) out.push('link with no accessible name: ' + a.getAttribute('href'));
      });

      const ids = {};
      document.querySelectorAll('[id]').forEach(el => { ids[el.id] = (ids[el.id] || 0) + 1; });
      Object.entries(ids).filter(([, n]) => n > 1).forEach(([id]) => out.push('duplicate id: ' + id));

      if (!document.querySelector('main')) out.push('no <main>');
      if (!document.querySelector('header')) out.push('no <header>');
      if (!document.querySelector('footer')) out.push('no <footer>');
      if (!document.documentElement.lang) out.push('no lang attribute');

      document.querySelectorAll('button').forEach(btn => {
        const n = (btn.innerText || '').trim() || btn.getAttribute('aria-label') || '';
        if (!n) out.push('button with no accessible name');
      });

      // WCAG 2.2 target size (minimum), 24x24 CSS px. The success criterion
      // exempts targets that sit inline within a sentence or block of text,
      // so those are filtered out rather than reported as failures.
      const inlineParent = el => {
        const p = el.parentElement;
        if (!p) return false;
        if (!/^(P|LI|CITE|H1|H2|H3|H4|SPAN|BLOCKQUOTE|OL|UL|DD|TD)$/.test(p.tagName)) return false;
        // inline means there is other text alongside the link in its container
        return p.textContent.trim().length > el.textContent.trim().length;
      };
      document.querySelectorAll('a, button').forEach(el => {
        const r = el.getBoundingClientRect();
        if (!r.width || !r.height) return;
        if (r.height >= 24 && r.width >= 24) return;
        if (inlineParent(el)) return; // exempt: inline in text
        out.push(`target under 24px: ${el.tagName} ${Math.round(r.width)}x${Math.round(r.height)} "${(el.innerText || '').trim().slice(0, 25)}"`);
      });
      return out;
    });
    total += r.length;
    console.log(`${url}: ${r.length} issue(s)`);
    r.slice(0, 15).forEach(i => console.log('    - ' + i));
  }

  // ---- keyboard walk ----
  await p.goto(BASE + '/retrieval-practice/', { waitUntil: 'networkidle' });
  const stops = [];
  for (let i = 0; i < 8; i++) {
    await p.keyboard.press('Tab');
    stops.push(await p.evaluate(() => {
      const a = document.activeElement;
      const s = getComputedStyle(a);
      return {
        tag: a.tagName,
        text: (a.innerText || a.getAttribute('aria-label') || '').trim().slice(0, 38),
        outline: s.outlineWidth,
      };
    }));
  }
  console.log('\nFirst 8 tab stops:');
  stops.forEach((f, i) => console.log(`  ${i + 1}. ${f.tag} "${f.text}" outline=${f.outline}`));

  // ---- reading-controls panel by keyboard ----
  await p.goto(BASE + '/', { waitUntil: 'networkidle' });
  await p.waitForTimeout(300);
  await p.locator('#a11yFab').focus();
  await p.keyboard.press('Enter');
  const opened = await p.locator('#a11yPanel').isVisible();
  const focusIn = await p.evaluate(() => document.getElementById('a11yPanel').contains(document.activeElement));
  await p.keyboard.press('Escape');
  const closed = !(await p.locator('#a11yPanel').isVisible());
  const focusBack = await p.evaluate(() => document.activeElement.id === 'a11yFab');
  console.log(`\nReading controls: opens=${opened} focusMovesIn=${focusIn} escCloses=${closed} focusReturns=${focusBack}`);

  // ---- skip link ----
  await p.goto(BASE + '/feedback/', { waitUntil: 'networkidle' });
  await p.keyboard.press('Tab');
  const skip = await p.evaluate(() => {
    const a = document.activeElement;
    const r = a.getBoundingClientRect();
    return { text: a.innerText.trim(), visible: r.left >= 0 && r.width > 0 };
  });
  console.log(`Skip link: "${skip.text}" visible on focus = ${skip.visible}`);

  // ---- reflow: 200% text at 640px, no horizontal scroll ----
  await p.setViewportSize({ width: 640, height: 900 });
  await p.goto(BASE + '/feedback/', { waitUntil: 'networkidle' });
  await p.evaluate(() => { document.documentElement.style.fontSize = '200%'; });
  await p.waitForTimeout(250);
  const overflow = await p.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  console.log(`Horizontal overflow at 200% text / 640px: ${overflow}px`);

  await b.close();
  console.log(total ? '\nISSUES FOUND' : '\nNo structural issues found.');
})();
