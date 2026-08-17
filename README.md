# Pedagogy First. Technology Second. — `pedagogyfirst.ictevangelist.com`

Mark Anderson's guide, web based. Nothing more, nothing less.

Eight pages: home, find-a-strategy, and one page per chapter. Every content
string on the site is Mark's own text, verbatim, from three sources:

```
source/strategies.json   the 144 strategy cards, extracted from his six infographics
source/prose.json        his prose, extracted from the definitive guide PDF
source/front.json        his front and back matter, transcribed from the same PDF
```

## The rule, enforced

`source/verify.py` proves it in both directions (the pre-reset site was
removed from the tree; the tag `pre-reset-2026-08-17` keeps it in history):

1. **Transcription.** Every string in those three files must appear verbatim in
   the guide PDF or the infographic HTML (whitespace and typography normalised).
2. **Site.** Every visible string on the built pages must come from those
   verified files, or appear on the `NAVIGATION` whitelist printed inside
   `verify.py`. That list is the complete inventory of words on the site that
   Mark did not write: labels, buttons, image descriptions. It is short.

Nothing on the site reports what research found beyond what Mark's own cards
and prose say. If a claim cannot be verified, it is not on the site.

```sh
python3 build.py                    # rebuild the eight pages
python3 source/verify.py --site     # prove the content rule holds
node source/site-test.cjs           # behaviour, reflow, keyboard, no-JS
```

## Downloads

`downloads/` holds the full guide plus each infographic as its own PDF, split
out of the guide's pages by `source/split-guide.py`. The pages are live text,
so the PDFs are selectable, searchable and readable aloud. They are not tagged
(the guide itself has no structure tree); the site labels them accordingly.

Licences as printed on the artefacts themselves: the guide's back cover says
CC BY-NC-ND, the infographics carry CC BY-NC-SA.

## Structure

```
index.html                 home: cover, why, the idea, the six guides, how to
                           use, praise, about, work with Mark, download
download-resources/        the full guide and each of the six as its own PDF
find-a-strategy/           all 144 cards searchable at once; results are the
                           exact card text and link to the strategy's anchor
<chapter>/                 opener, infographic at full size with downloads,
                           the 24 strategies as accessible text, the thinking,
                           in practice
css/styles.css             one stylesheet, vendored fonts, no external requests
js/finder.js               the finder; works without JavaScript as a plain list
js/a11y.js                 the reading-controls widget shared with Mark's other
                           microsites: text size, high contrast, extra spacing,
                           listen aloud; preferences stay on the visitor's device
```

## Accessibility

WCAG 2.2 AA floor: AAA body contrast, visible focus, skip link, one h1 per
page, alt text throughout, 44px targets, no sideways scroll at 640px/200% or
320px/100%, `prefers-reduced-motion`, `prefers-contrast`, `forced-colors`,
print styles. The finder is progressive enhancement; without JavaScript the
full list is simply readable. The reading-controls widget (text size, high
contrast, extra spacing, listen aloud) is a focus-trapped dialog, identical in
behaviour to the aigovernance and Woodland microsites.

## Deployment

GitHub Pages from `main`, root. `CNAME` holds the custom domain.

## Licence

Content © Mark Anderson. Guide: CC BY-NC-ND 4.0. Infographics: CC BY-NC-SA 4.0.
