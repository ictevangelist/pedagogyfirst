/* Consent and analytics behaviour.

   Run against a build with a test measurement ID in place. Confirms nothing
   is requested from Google before consent, that declining sticks, and that
   the events fire once consent is given.
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

  // ---------- before any choice ----------
  let ctx = await b.newContext();
  let p = await ctx.newPage();
  const googleHits = [];
  p.on('request', r => {
    if (/googletagmanager|google-analytics/.test(r.url())) googleHits.push(r.url());
  });
  await p.goto(BASE + '/feedback/', { waitUntil: 'networkidle' });
  await p.waitForTimeout(600);

  console.log('Before consent');
  check('banner is shown', await p.locator('.consent').isVisible());
  check('nothing requested from Google', googleHits.length === 0, googleHits.length + ' requests');
  const cookies = await ctx.cookies();
  check('no cookies set', cookies.length === 0, cookies.length + ' cookies');
  check('banner has a dialog role', await p.locator('.consent[role="dialog"]').count() === 1);
  check('focus starts inside the banner',
    await p.evaluate(() => document.querySelector('.consent').contains(document.activeElement)));

  // ---------- declining ----------
  console.log('\nDeclining');
  await p.locator('[data-consent="no"]').click();
  await p.waitForTimeout(400);
  check('banner closes', await p.locator('.consent').count() === 0);
  check('still nothing requested from Google', googleHits.length === 0);
  await p.goto(BASE + '/retrieval-practice/', { waitUntil: 'networkidle' });
  await p.waitForTimeout(500);
  check('the choice sticks across pages', await p.locator('.consent').count() === 0);
  check('still no Google requests after navigating', googleHits.length === 0, googleHits.length + '');
  await ctx.close();

  // ---------- accepting ----------
  console.log('\nAccepting');
  ctx = await b.newContext();
  p = await ctx.newPage();
  const accepted = [];
  p.on('request', r => {
    if (/googletagmanager|google-analytics/.test(r.url())) accepted.push(r.url());
  });
  // Google is not reachable from here, so stub the endpoint and watch for the call.
  await p.route('**/googletagmanager.com/**', route => route.fulfill({
    status: 200, contentType: 'application/javascript', body: 'window.__gtagLoaded = true;',
  }));
  await p.goto(BASE + '/feedback/', { waitUntil: 'networkidle' });
  await p.waitForTimeout(400);
  await p.locator('[data-consent="yes"]').click();
  await p.waitForTimeout(700);
  check('gtag.js is requested', accepted.length > 0, accepted.length + ' requests');
  check('the measurement ID is passed', accepted.some(u => /id=G-/.test(u)),
    (accepted[0] || '').slice(0, 78));

  const layer = await p.evaluate(() => (window.dataLayer || []).map(a => Array.from(a)[0]));
  check('consent mode is set before config', layer.indexOf('consent') !== -1, layer.join(','));

  // events
  await p.evaluate(() => { window.__events = []; const g = window.gtag; window.gtag = function () {
    if (arguments[0] === 'event') window.__events.push([arguments[1], arguments[2]]); return g.apply(null, arguments); }; });
  await p.evaluate(() => window.scrollTo(0, document.body.scrollHeight / 3));
  await p.waitForTimeout(400);
  await p.locator('#strategyFilter').fill('marking');
  await p.waitForTimeout(1900);
  const events = await p.evaluate(() => window.__events.map(e => e[0]));
  check('scroll depth is recorded', events.includes('chapter_depth'), events.join(','));
  check('filter terms are recorded', events.includes('strategy_filter'));

  await p.evaluate(() => {
    const a = document.querySelector('a[href*="ictevangelist.com/contact"]');
    a.addEventListener('click', ev => ev.preventDefault(), { once: true });
    a.click();
  });
  await p.waitForTimeout(300);
  const after = await p.evaluate(() => window.__events.map(e => e[0]));
  check('CTA clicks are recorded', after.includes('cta_click'));

  await p.evaluate(() => {
    const a = document.querySelector('a[href$=".pdf"], a[href*="-download.png"]');
    if (a) { a.addEventListener('click', ev => ev.preventDefault(), { once: true }); a.click(); }
  });
  await p.waitForTimeout(300);
  const dl = await p.evaluate(() => window.__events.map(e => e[0]));
  check('downloads are recorded',
    dl.includes('infographic_download') || dl.includes('guide_download'), dl.join(','));

  await b.close();
  console.log(fails ? `\n${fails} FAILURE(S)` : '\nConsent and analytics behave correctly.');
})();
