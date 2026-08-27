/* Render each original infographic to a PNG for the chapter pages.
   The source HTML is 1400px wide and pulls its fonts from Google, so we
   render with a network-idle wait at 2x for a crisp 2800px asset.

   node source/render-infographics.cjs
*/
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const SRC = path.join(__dirname, 'infographics');
const OUT = path.join(__dirname, '..', 'assets', 'infographics');

const MAP = {
  '01-retrieval-practice.html': 'retrieval-practice',
  '02-formative-assessment.html': 'formative-assessment',
  '03-feedback.html': 'feedback',
  '04-questioning-discussion.html': 'questioning-and-discussion',
  '05-explanations-modelling.html': 'explanations-and-modelling',
  '06-metacognition.html': 'metacognition-and-self-regulation',
};

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const ctx = await b.newContext({ viewport: { width: 1400, height: 900 }, deviceScaleFactor: 2 });
  const p = await ctx.newPage();

  for (const [file, slug] of Object.entries(MAP)) {
    await p.goto('file://' + path.join(SRC, file), { waitUntil: 'networkidle' });
    await p.waitForTimeout(1200); // let webfonts settle
    const el = await p.$('.infographic');
    const out = path.join(OUT, slug + '.png');
    await el.screenshot({ path: out });
    const { width, height } = await el.boundingBox();
    console.log(`${slug}.png  ${Math.round(width)}x${Math.round(height)} css  (${Math.round(fs.statSync(out).size / 1024)} KB)`);
  }
  await b.close();
})();
