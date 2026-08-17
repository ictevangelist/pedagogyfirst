/* Behaviour and accessibility checks for the whole site.
   Run:  python3 -m http.server 8899 &  then  node source/site-test.cjs  */
const { chromium } = require('playwright');

const PAGES = ['/', '/find-a-strategy/', '/retrieval-practice/', '/formative-assessment/',
  '/feedback/', '/questioning-and-discussion/', '/explanations-and-modelling/',
  '/metacognition-and-self-regulation/'];
const BASE = 'http://localhost:8899';

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  let fails = 0;
  const check = (label, ok, detail) => {
    console.log(`  ${ok ? 'ok  ' : 'FAIL'} ${label}${detail ? '  (' + detail + ')' : ''}`);
    if (!ok) fails++;
  };

  // ---------- structure, images, external requests ----------
  console.log('Structure');
  let ctx = await b.newContext({ viewport: { width: 1280, height: 900 } });
  let p = await ctx.newPage();
  for (const path of PAGES) {
    await p.goto(BASE + path, { waitUntil: 'networkidle' });
    const r = await p.evaluate(() => ({
      h1: document.querySelectorAll('h1').length,
      lang: document.documentElement.lang,
      noAlt: Array.from(document.images).filter(i => !i.hasAttribute('alt')).length,
      broken: Array.from(document.images).filter(i => !i.naturalWidth).length,
      external: performance.getEntriesByType('resource')
        .filter(x => !x.name.includes('localhost')).length,
      skip: !!document.querySelector('.skip'),
    }));
    const ok = r.h1 === 1 && r.lang === 'en-GB' && !r.noAlt && !r.broken && !r.external && r.skip;
    check(path, ok, `h1=${r.h1} noAlt=${r.noAlt} broken=${r.broken} ext=${r.external}`);
  }

  // ---------- reflow ----------
  console.log('\nReflow');
  for (const [w, zoom] of [[640, '200%'], [320, '100%']]) {
    const c2 = await b.newContext({ viewport: { width: w, height: 900 } });
    const p2 = await c2.newPage();
    let worst = 0, worstPage = '';
    for (const path of PAGES) {
      await p2.goto(BASE + path, { waitUntil: 'networkidle' });
      await p2.evaluate(z => { document.documentElement.style.fontSize = z; }, zoom);
      await p2.waitForTimeout(150);
      const over = await p2.evaluate(() =>
        document.documentElement.scrollWidth - document.documentElement.clientWidth);
      if (over > worst) { worst = over; worstPage = path; }
    }
    check(`${w}px at ${zoom}: no sideways scroll anywhere`, worst === 0, `${worstPage} ${worst}px`);
    await c2.close();
  }

  // ---------- finder ----------
  console.log('\nFinder');
  await p.goto(BASE + '/find-a-strategy/', { waitUntil: 'networkidle' });
  await p.waitForTimeout(250);
  const shown = () => p.locator('.finding:not([hidden])').count();
  check('all 144 on the page', await p.locator('.finding').count() === 144);
  check('input enabled by JS', await p.locator('#q').isEnabled());
  await p.locator('#q').fill('wait time');
  await p.waitForTimeout(350);
  const hits = await shown();
  check('search narrows', hits > 0 && hits < 144, hits + ' hits');
  check('AND matching', await p.evaluate(() =>
    Array.from(document.querySelectorAll('.finding:not([hidden])')).every(li => {
      const h = li.getAttribute('data-search');
      return h.includes('wait') && h.includes('time');
    })));
  check('status announces', /wait time/.test(await p.locator('#status').innerText()));
  check('empty groups hidden', await p.evaluate(() =>
    Array.from(document.querySelectorAll('.fgroup:not([hidden])'))
      .every(g => g.querySelectorAll('.finding:not([hidden])').length > 0)));
  await p.locator('#q').fill('zzzzz');
  await p.waitForTimeout(300);
  check('empty state appears', await p.locator('#empty').isVisible());
  await p.locator('#reset').click();
  await p.waitForTimeout(250);
  check('reset restores all', await shown() === 144);
  await p.goto(BASE + '/find-a-strategy/?q=cold+call', { waitUntil: 'networkidle' });
  await p.waitForTimeout(300);
  check('?q= deep link works', (await shown()) > 0 && (await shown()) < 144, await shown() + '');

  // every finder link resolves to a real anchor
  const links = await p.locator('.finding a').evaluateAll(a => a.map(x => x.getAttribute('href')));
  let missing = 0;
  const seen = {};
  for (const href of links) {
    const [page, anchor] = href.split('#');
    if (!seen[page]) seen[page] = await (await p.request.get(BASE + page)).text();
    if (!seen[page].includes(`id="${anchor}"`)) missing++;
  }
  check('all 144 finder links resolve to anchors', missing === 0, missing + ' missing');
  await ctx.close();

  // ---------- without JavaScript ----------
  console.log('\nWithout JavaScript');
  const nj = await b.newContext({ javaScriptEnabled: false, viewport: { width: 1280, height: 900 } });
  const np = await nj.newPage();
  await np.goto(BASE + '/find-a-strategy/', { waitUntil: 'load' });
  check('all 144 still listed and visible',
    await np.locator('.finding:not([hidden])').count() === 144);
  check('input disabled rather than broken', await np.locator('#q').isDisabled());
  await np.goto(BASE + '/feedback/', { waitUntil: 'load' });
  check('chapter strategies all present', await np.locator('.strategy').count() === 24);
  check('nav reaches every chapter', await np.locator('.site-header nav a').count() === 8);
  await nj.close();

  // ---------- keyboard ----------
  console.log('\nKeyboard');
  const kc = await b.newContext({ viewport: { width: 1280, height: 900 } });
  const kp = await kc.newPage();
  await kp.goto(BASE + '/', { waitUntil: 'networkidle' });
  await kp.keyboard.press('Tab');
  check('first Tab reaches the skip link',
    await kp.evaluate(() => document.activeElement.classList.contains('skip')));
  await kp.keyboard.press('Enter');
  await kp.waitForTimeout(150);
  check('skip link jumps to main',
    await kp.evaluate(() => location.hash === '#main'));
  await kc.close();

  await b.close();
  console.log(fails ? `\n${fails} FAILURE(S)` : '\nAll site checks pass.');
  process.exit(fails ? 1 : 0);
})();
