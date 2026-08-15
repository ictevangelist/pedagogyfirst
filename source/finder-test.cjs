/* Behaviour tests for /find-a-strategy/.

   Gemma Gwilliam's line about the guide was "the right approach for the right
   activity at the right moment". This page is the answer to that, so it needs
   to actually work: search across all 144, filter by chapter, start from a
   problem, deep link, and still be useful with JavaScript switched off.
*/
const { chromium } = require('playwright');

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const BASE = 'http://localhost:8899';
  let fails = 0;
  const check = (label, ok, detail) => {
    console.log(`  ${ok ? 'ok  ' : 'FAIL'} ${label}${detail ? '  (' + detail + ')' : ''}`);
    if (!ok) fails++;
  };

  const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } });
  const p = await ctx.newPage();
  const shown = () => p.locator('.finding:not([hidden])').count();

  // ---------- everything is there to begin with ----------
  console.log('Starting state');
  await p.goto(BASE + '/find-a-strategy/', { waitUntil: 'networkidle' });
  await p.waitForTimeout(250);
  check('all 144 strategies are on the page', await p.locator('.finding').count() === 144,
    (await p.locator('.finding').count()) + ' items');
  check('all 144 are visible', await shown() === 144, (await shown()) + ' visible');
  check('the search box is enabled by JavaScript',
    await p.locator('#finderInput').isEnabled());
  check('the status line reports the total',
    /144/.test(await p.locator('#finderStatus').innerText()),
    await p.locator('#finderStatus').innerText());
  check('the status line is a live region',
    await p.locator('#finderStatus').getAttribute('aria-live') !== null);

  // ---------- searching ----------
  console.log('\nSearching');
  await p.locator('#finderInput').fill('wait time');
  await p.waitForTimeout(400);
  const waitHits = await shown();
  check('narrows on a phrase', waitHits > 0 && waitHits < 144, waitHits + ' hits');
  check('when something carries every word, only those are shown',
    await p.evaluate(() => Array.prototype.slice
      .call(document.querySelectorAll('.finding:not([hidden])'))
      .every(li => {
        const h = li.getAttribute('data-search');
        return h.indexOf('wait') !== -1 && h.indexOf('time') !== -1;
      })));
  check('the status line names the search',
    /wait time/.test(await p.locator('#finderStatus').innerText()),
    await p.locator('#finderStatus').innerText());
  check('a clear button appears', await p.locator('#finderClear').isVisible());

  // ---------- forgiving, because teachers type sentences ----------
  console.log('\nTyping a sentence, not keywords');
  for (const sentence of [
    "my kids have forgotten it all by next week",
    "they don't act on the comments I write",
    "I want to know if they actually understood it",
    "marking is taking over my weekends",
  ]) {
    await p.locator('#finderInput').fill(sentence);
    await p.waitForTimeout(400);
    const n = await shown();
    check('"' + sentence + '"', n >= 3 && n < 60, n + ' hits');
  }
  await p.locator('#finderInput').fill('feedback timing');
  await p.waitForTimeout(400);
  const groupsShown = await p.locator('.findings-group:not([hidden])').count();
  check('empty chapter headings are hidden', groupsShown >= 1 && groupsShown <= 6, groupsShown + ' groups');
  check('every visible group actually has results',
    await p.evaluate(() => Array.prototype.slice
      .call(document.querySelectorAll('.findings-group:not([hidden])'))
      .every(g => g.querySelectorAll('.finding:not([hidden])').length > 0)));

  console.log('\nNo results');
  await p.locator('#finderInput').fill('xylophone');
  await p.waitForTimeout(400);
  check('nothing matches', await shown() === 0);
  check('an empty state is shown, not a blank page',
    await p.locator('#finderEmpty').isVisible());
  check('the empty state offers a way back',
    await p.locator('#finderEmpty #finderReset').count() === 1);
  await p.locator('#finderReset').click();
  await p.waitForTimeout(300);
  check('resetting puts all 144 back', await shown() === 144, (await shown()) + '');
  check('focus returns to the search box',
    await p.evaluate(() => document.activeElement.id) === 'finderInput');

  // ---------- Escape ----------
  console.log('\nKeyboard');
  await p.locator('#finderInput').fill('feedback');
  await p.waitForTimeout(350);
  await p.locator('#finderInput').press('Escape');
  await p.waitForTimeout(200);
  check('Escape clears the search', await shown() === 144, (await shown()) + '');
  await p.keyboard.press('Tab');
  check('tabbing out of the box lands on something focusable',
    await p.evaluate(() => document.activeElement.tagName) !== 'BODY',
    await p.evaluate(() => document.activeElement.tagName + '.' + document.activeElement.className));

  // ---------- chapter chips ----------
  console.log('\nChapter chips');
  const chip = p.locator('.finder__chip[data-chapter="feedback"]');
  check('chips start unpressed', await chip.getAttribute('aria-pressed') === 'false');
  await chip.click();
  await p.waitForTimeout(300);
  check('chip filters to one chapter', await shown() === 24, (await shown()) + ' shown');
  check('chip reports itself pressed', await chip.getAttribute('aria-pressed') === 'true');
  check('only feedback strategies remain',
    await p.evaluate(() => Array.prototype.slice
      .call(document.querySelectorAll('.finding:not([hidden])'))
      .every(li => li.getAttribute('data-chapter') === 'feedback')));
  await p.locator('#finderInput').fill('marking');
  await p.waitForTimeout(400);
  const both = await shown();
  check('search and chapter combine', both > 0 && both < 24, both + ' hits');
  check('the status line names both',
    /marking/.test(await p.locator('#finderStatus').innerText()) &&
    /in /.test(await p.locator('#finderStatus').innerText()),
    await p.locator('#finderStatus').innerText());
  await chip.click();
  await p.waitForTimeout(300);
  check('clicking the chip again releases it', await chip.getAttribute('aria-pressed') === 'false');
  check('search survives the chip being released', await shown() > both, (await shown()) + '');

  // ---------- problem-first starters ----------
  console.log('\nProblem-first starters');
  await p.locator('#finderClear').click();
  await p.waitForTimeout(250);
  const starters = p.locator('.starter');
  const nStarters = await starters.count();
  check('there are starters to click', nStarters >= 6, nStarters + ' starters');
  for (let i = 0; i < nStarters; i++) {
    const s = starters.nth(i);
    const label = (await s.innerText()).trim().replace(/\s+/g, ' ');
    await s.click();
    await p.waitForTimeout(400);
    const n = await shown();
    check('"' + label.slice(0, 44) + '" returns results', n > 0 && n < 144, n + ' hits');
    await p.locator('#finderClear').click();
    await p.waitForTimeout(200);
  }

  // ---------- deep link ----------
  console.log('\nDeep link');
  await p.goto(BASE + '/find-a-strategy/?q=cold+call', { waitUntil: 'networkidle' });
  await p.waitForTimeout(400);
  check('?q= prefills the box', await p.locator('#finderInput').inputValue() === 'cold call');
  const deep = await shown();
  check('?q= filters on load', deep > 0 && deep < 144, deep + ' hits');

  // ---------- results link somewhere real ----------
  console.log('\nResults');
  const href = await p.locator('.finding:not([hidden]) a').first().getAttribute('href');
  check('results link to the strategy anchor', /^\/[a-z-]+\/#\d\d-/.test(href), href);
  const r = await p.request.get(BASE + href.split('#')[0]);
  check('that chapter page exists', r.status() === 200, r.status() + '');
  check('the anchor exists on it',
    (await r.text()).indexOf('id="' + href.split('#')[1] + '"') !== -1, href.split('#')[1]);
  await ctx.close();

  // ---------- without JavaScript ----------
  console.log('\nWithout JavaScript');
  const noJs = await b.newContext({ javaScriptEnabled: false, viewport: { width: 1280, height: 900 } });
  const np = await noJs.newPage();
  await np.goto(BASE + '/find-a-strategy/', { waitUntil: 'load' });
  check('all 144 are still listed', await np.locator('.finding').count() === 144,
    (await np.locator('.finding').count()) + '');
  check('all 144 are still visible', await np.locator('.finding:not([hidden])').count() === 144);
  check('the search box is disabled rather than broken',
    await np.locator('#finderInput').isDisabled());
  check('results are grouped by chapter',
    await np.locator('.findings-group, .finder__group').count() >= 6,
    (await np.locator('.findings-group, .finder__group').count()) + ' groups');
  check('links still work', (await np.locator('.finding a').first().getAttribute('href')).indexOf('#') !== -1);
  await noJs.close();

  await b.close();
  console.log(fails ? `\n${fails} FAILURE(S)` : '\nThe finder behaves correctly.');
})();
