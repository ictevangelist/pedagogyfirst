/* Generate 1200x630 Open Graph cards, one per page.

   The site had no og:image, so every share on LinkedIn fell back to a bare
   link. Each card uses that chapter's own hero colours so a shared link is
   recognisable as part of the set.

   node source/og-images.cjs
*/
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const OUT = path.join(__dirname, '..', 'assets', 'og');
const FONTS = path.join(__dirname, '..', 'assets', 'fonts');
const LOGO = path.join(__dirname, '..', 'assets', 'ict-evangelist-logo-white.png');

const THEMES = {
  home: { bg: 'linear-gradient(135deg,#1d2632,#121821)', accent: '#FEAE00', ink: '#fff', soft: '#ced8de' },
  'retrieval-practice': { bg: 'linear-gradient(135deg,#2d3436,#1a1f24 50%,#0f1317)', accent: '#ff9d76', ink: '#fff', soft: '#ced8de' },
  'formative-assessment': { bg: 'linear-gradient(135deg,#2c3e50,#1a2530 50%,#0f1922)', accent: '#74b9ff', ink: '#fff', soft: '#ced8de' },
  feedback: { bg: 'linear-gradient(135deg,#f5c518,#f0b400 50%,#e8a800)', accent: '#9c1049', ink: '#1a1a1a', soft: '#4a3a00' },
  'questioning-and-discussion': { bg: 'linear-gradient(135deg,#00574a,#00433a 50%,#00382e)', accent: '#f1c40f', ink: '#fff', soft: '#ced8de' },
  'explanations-and-modelling': { bg: 'linear-gradient(135deg,#40407a,#2c2c54 50%,#1e1e3f)', accent: '#ffb142', ink: '#fff', soft: '#ced8de' },
  'metacognition-and-self-regulation': { bg: 'linear-gradient(135deg,#f2bc36,#e8ae1f)', accent: '#9c1049', ink: '#1a1a1a', soft: '#4a3a00' },
};

const PAGES = [
  { slug: 'home', eyebrow: 'An evidence informed resource by Mark Anderson', title: 'Pedagogy First.<br>Technology Second.', sub: '144 classroom strategies, with or without technology. Every one expanded in full.', no: '' },
  { slug: 'retrieval-practice', eyebrow: 'Chapter one of six', title: 'Retrieval Practice', sub: '24 ways to embed it, from the testing effect to calibration.', no: '01' },
  { slug: 'formative-assessment', eyebrow: 'Chapter two of six', title: 'Formative Assessment', sub: '24 ways to embed it, from learning intentions to student ownership.', no: '02' },
  { slug: 'feedback', eyebrow: 'Chapter three of six', title: 'Feedback', sub: '24 ways to embed it, from what feedback is to closing the gap.', no: '03' },
  { slug: 'questioning-and-discussion', eyebrow: 'Chapter four of six', title: 'Questioning &amp; Discussion', sub: '24 ways to embed it, from question quality to student generated questions.', no: '04' },
  { slug: 'explanations-and-modelling', eyebrow: 'Chapter five of six', title: 'Explanations &amp; Modelling', sub: '24 ways to embed it, from small steps to worked examples.', no: '05' },
  { slug: 'metacognition-and-self-regulation', eyebrow: 'Chapter six of six', title: 'Metacognition &amp; Self-Regulation', sub: '24 ways to embed it, from forethought to digital cognition.', no: '06' },
];

function html(page) {
  const t = THEMES[page.slug];
  const logo = 'data:image/png;base64,' + fs.readFileSync(LOGO).toString('base64');
  const font = f => 'data:font/woff2;base64,' + fs.readFileSync(path.join(FONTS, f)).toString('base64');
  return `<!DOCTYPE html><html><head><meta charset="utf-8"><style>
@font-face{font-family:'Poppins';src:url('${font('poppins-400.woff2')}') format('woff2');font-weight:400}
@font-face{font-family:'Poppins';src:url('${font('poppins-600.woff2')}') format('woff2');font-weight:600}
@font-face{font-family:'Exo 2';src:url('${font('exo2-700.woff2')}') format('woff2');font-weight:700}
*{margin:0;padding:0;box-sizing:border-box}
body{margin:0}
.card{width:1200px;height:630px;background:${t.bg};color:${t.ink};font-family:'Poppins',sans-serif;
  padding:66px 72px 54px;display:flex;flex-direction:column;position:relative;overflow:hidden}
.card::before{content:"";position:absolute;top:0;left:0;right:0;height:9px;
  background:linear-gradient(90deg,#17abce 0%,#0ea3ab 45%,#45b84a 100%)}
.eyebrow{color:${t.accent};font-weight:600;letter-spacing:3px;text-transform:uppercase;font-size:20px}
.no{font-family:'Exo 2';font-weight:700;font-size:104px;line-height:.9;color:${t.accent};margin:14px 0 2px}
h1{font-family:'Exo 2';font-weight:700;font-size:${page.slug === 'home' ? 78 : 64}px;line-height:1.08;letter-spacing:-.5px;margin-top:${page.no ? 4 : 22}px}
.sub{font-size:26px;line-height:1.45;color:${t.soft};margin-top:18px;max-width:900px}
.foot{margin-top:auto;display:flex;align-items:center;justify-content:space-between;
  border-top:1px solid ${t.ink === '#fff' ? 'rgba(255,255,255,.22)' : 'rgba(0,0,0,.18)'};padding-top:26px}
.foot img{height:40px;${t.ink === '#fff' ? '' : 'filter:invert(1) brightness(.2)'}}
.foot .site{font-size:23px;font-weight:600;color:${t.soft}}
</style></head><body><div class="card" id="c">
  <div class="eyebrow">${page.eyebrow}</div>
  ${page.no ? `<div class="no">${page.no}</div>` : ''}
  <h1>${page.title}</h1>
  <div class="sub">${page.sub}</div>
  <div class="foot"><img src="${logo}" alt=""><div class="site">pedagogyfirst.ictevangelist.com</div></div>
</div></body></html>`;
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await (await b.newContext({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 })).newPage();
  for (const page of PAGES) {
    await p.setContent(html(page), { waitUntil: 'networkidle' });
    await p.waitForTimeout(300);
    const out = path.join(OUT, page.slug + '.png');
    await p.locator('#c').screenshot({ path: out });
    console.log(`${page.slug}.png  ${Math.round(fs.statSync(out).size / 1024)} KB`);
  }
  await b.close();
})();
