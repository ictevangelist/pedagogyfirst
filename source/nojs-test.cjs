/* Confirm the site is usable with JavaScript disabled. */
const { chromium } = require('playwright');

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const ctx = await b.newContext({ javaScriptEnabled: false, viewport: { width: 1280, height: 900 } });
  const p = await ctx.newPage();
  await p.goto('http://localhost:8899/retrieval-practice/', { waitUntil: 'load' });
  const r = await p.evaluate(() => ({
    navLinks: document.querySelectorAll('.main-nav a').length,
    clusterLinks: document.querySelectorAll('.cluster-nav a').length,
    strategies: document.querySelectorAll('.strategy').length,
    bodyText: document.querySelectorAll('.strategy__body').length,
    a11yWidget: !!document.querySelector('.a11y-widget'),
    toTop: !!document.querySelector('.to-top'),
    overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
  }));
  console.log('No-JS render:', JSON.stringify(r, null, 2));
  console.log(
    r.navLinks === 7 && r.clusterLinks === 5 && r.strategies === 24 && r.bodyText === 24 && r.overflow === 0
      ? 'Content and navigation fully available without JavaScript.'
      : 'PROBLEM: something depends on JavaScript.'
  );
  await b.close();
})();
