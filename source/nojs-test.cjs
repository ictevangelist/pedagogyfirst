/* Confirm the site is usable with JavaScript disabled.

   Nothing here is a single page app and nothing should need to be. Only the
   reading-controls widget is allowed to be JS-only, because it has nothing to
   fall back to: everything it offers is already the page's default.
*/
const { chromium } = require('playwright');

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const ctx = await b.newContext({ javaScriptEnabled: false, viewport: { width: 1280, height: 900 } });
  const p = await ctx.newPage();
  let fails = 0;
  const check = (label, ok, detail) => {
    console.log(`  ${ok ? 'ok  ' : 'FAIL'} ${label}${detail ? '  (' + detail + ')' : ''}`);
    if (!ok) fails++;
  };
  const BASE = 'http://localhost:8899';

  console.log('A chapter page');
  await p.goto(BASE + '/retrieval-practice/', { waitUntil: 'load' });
  const r = await p.evaluate(() => ({
    navLinks: document.querySelectorAll('#site-nav a').length,
    navVisible: getComputedStyle(document.getElementById('site-nav')).display !== 'none',
    clusterLinks: document.querySelectorAll('.cluster-nav a').length,
    strategies: document.querySelectorAll('.strategy').length,
    bodyText: document.querySelectorAll('.strategy__body').length,
    hidden: document.querySelectorAll('.strategy[hidden]').length,
    filterDisabled: !!document.querySelector('#strategyFilter[disabled]'),
    knowing: !!document.querySelector('#how-would-you-know'),
    toTop: !!document.querySelector('.to-top'),
    overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
  }));
  check('every chapter is reachable from the menu', r.navLinks >= 8, r.navLinks + ' links');
  check('the menu is open rather than collapsed behind a button', r.navVisible);
  check('the cluster jump links are there', r.clusterLinks === 5, r.clusterLinks + '');
  check('all 24 strategies render', r.strategies === 24, r.strategies + '');
  check('all 24 expansions render', r.bodyText === 24, r.bodyText + '');
  check('nothing is left hidden', r.hidden === 0, r.hidden + ' hidden');
  check('the filter is disabled rather than dead', r.filterDisabled);
  check('the "how would you know" section is server rendered', r.knowing);
  check('no sideways scroll', r.overflow === 0, r.overflow + 'px');

  console.log('\nThe other pages');
  for (const [path, sel, n] of [
    ['/', '.chapter-card', 6],
    ['/find-a-strategy/', '.finding', 144],
    ['/get-the-guide/', 'a[href$=".pdf"]', 1],
  ]) {
    await p.goto(BASE + path, { waitUntil: 'load' });
    const count = await p.locator(sel).count();
    check(path + ' renders its content', count >= n, count + ' × ' + sel);
    const over = await p.evaluate(() =>
      document.documentElement.scrollWidth - document.documentElement.clientWidth);
    check(path + ' has no sideways scroll', over === 0, over + 'px');
  }

  await b.close();
  console.log(fails ? `\n${fails} FAILURE(S)` : '\nContent and navigation work without JavaScript.');
})();
