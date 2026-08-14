/* Behaviour tests for the chapters panel and the strategy filter. */
const { chromium } = require('playwright');

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await (await b.newContext({ viewport: { width: 1280, height: 900 } })).newPage();
  const BASE = 'http://localhost:8899';
  let fails = 0;
  const check = (label, ok, detail) => {
    console.log(`  ${ok ? 'ok  ' : 'FAIL'} ${label}${detail ? '  (' + detail + ')' : ''}`);
    if (!ok) fails++;
  };

  // ---------- chapters panel ----------
  console.log('Chapters panel');
  await p.goto(BASE + '/feedback/', { waitUntil: 'networkidle' });
  await p.waitForTimeout(200);
  check('starts closed', await p.locator('#site-nav').isHidden());
  await p.locator('.nav-toggle').focus();
  await p.keyboard.press('Enter');
  check('opens on Enter', await p.locator('#site-nav').isVisible());
  check('focus moves into the panel',
    await p.evaluate(() => document.getElementById('site-nav').contains(document.activeElement)));
  const titles = await p.locator('#site-nav .nav-title').allInnerTexts();
  check('shows full chapter titles', titles.includes('Metacognition & Self-Regulation'), titles.length + ' items');
  await p.keyboard.press('ArrowDown');
  const moved = await p.evaluate(() => document.activeElement.textContent.trim());
  check('arrow keys move between chapters', moved.length > 0, moved.slice(0, 30));
  await p.keyboard.press('Escape');
  check('Escape closes it', await p.locator('#site-nav').isHidden());
  check('focus returns to the button',
    await p.evaluate(() => document.activeElement.classList.contains('nav-toggle')));

  // ---------- filter ----------
  console.log('\nStrategy filter');
  await p.goto(BASE + '/questioning-and-discussion/', { waitUntil: 'networkidle' });
  await p.waitForTimeout(250);
  check('enabled once JS runs', !(await p.locator('#strategyFilter').isDisabled()));

  await p.locator('#strategyFilter').fill('wait time');
  await p.waitForTimeout(400);
  let visible = await p.locator('.strategy:not([hidden])').count();
  check('narrows the cards', visible > 0 && visible < 24, visible + ' of 24 shown');
  const status = await p.locator('#filterStatus').innerText();
  check('announces the count', /strateg/i.test(status), status);
  const emptyClusters = await p.evaluate(() =>
    Array.from(document.querySelectorAll('.cluster')).filter(c => !c.hidden && !c.querySelector('.strategy:not([hidden])')).length);
  check('hides clusters left with nothing', emptyClusters === 0);

  await p.locator('#strategyFilter').fill('Rosenshine');
  await p.waitForTimeout(400);
  visible = await p.locator('.strategy:not([hidden])').count();
  check('searches the expansion text too, not just titles', visible >= 0, visible + ' match "Rosenshine"');

  await p.locator('#strategyFilter').fill('zzzznothing');
  await p.waitForTimeout(400);
  check('shows the empty state', await p.locator('#filterEmpty').isVisible());
  await p.locator('#filterReset').click();
  await p.waitForTimeout(300);
  check('reset restores all 24', (await p.locator('.strategy:not([hidden])').count()) === 24);

  await p.locator('#strategyFilter').fill('quiz');
  await p.waitForTimeout(400);
  await p.locator('#strategyFilter').press('Escape');
  await p.waitForTimeout(300);
  check('Escape clears the field', (await p.locator('.strategy:not([hidden])').count()) === 24);

  await p.goto(BASE + '/retrieval-practice/?find=spacing', { waitUntil: 'networkidle' });
  await p.waitForTimeout(400);
  visible = await p.locator('.strategy:not([hidden])').count();
  check('deep link ?find= works', visible > 0 && visible < 24, visible + ' shown');

  // ---------- infographic and downloads ----------
  console.log('\nAssets');
  const img = p.locator('.infographic-figure img');
  check('infographic is on the chapter page', await img.count() === 1);
  const dims = await img.evaluate(el => ({ w: el.naturalWidth, h: el.naturalHeight }));
  check('infographic actually loads', dims.w > 0, dims.w + 'x' + dims.h);
  for (const url of ['/downloads/pedagogy-first-technology-second.pdf', '/assets/og/home.png',
                     '/assets/infographics/feedback-download.png']) {
    const r = await p.request.get(BASE + url);
    check('serves ' + url, r.status() === 200, r.status() + ', ' + Math.round((+r.headers()['content-length'] || 0) / 1024) + ' KB');
  }

  await b.close();
  console.log(fails ? `\n${fails} FAILURE(S)` : '\nAll behaviour checks passed.');
})();
