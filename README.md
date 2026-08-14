# Pedagogy First. Technology Second. — `pedagogyfirst.ictevangelist.com`

A companion site to **Pedagogy First. Technology Second.** by Mark Anderson (ICT Evangelist).

The guide collects six infographics, each carrying 24 evidence informed teaching strategies.
This site takes all **144** of them and expands every one: what it is, why it works, how to
run it, where technology serves, and the failure mode to watch for.

Built on the same kit as `aigovernance.ictevangelist.com` and the Woodland review site:
vendored fonts, no external requests, and a reading-controls widget that behaves identically
across all three.

## Structure

| Path | Content |
| --- | --- |
| `index.html` | Home: why the guides exist, the six chapters, how to use them |
| `retrieval-practice/` | 01 - the testing effect, spacing, desirable difficulties, formats, calibration |
| `formative-assessment/` | 02 - intentions, eliciting evidence, feedback, peers, ownership |
| `feedback/` | 03 - what feedback is, timing, source, the learner, closing the gap |
| `questioning-and-discussion/` | 04 - question quality, wait time, equity, dialogic talk, student questions |
| `explanations-and-modelling/` | 05 - structure, cognitive load, dual coding, worked examples |
| `metacognition-and-self-regulation/` | 06 - forethought, monitoring, reflection, strategy use, digital cognition |

Each strategy has a stable anchor, so an individual idea can be linked directly:

```
https://pedagogyfirst.ictevangelist.com/retrieval-practice/#04-test-before-you-teach
```

## Editing

Content lives in two places and the HTML is generated from both.

- `source/strategies.json` - the 144 strategies, their clusters, colours and metadata,
  extracted from the original infographics.
- `content/ch0*.py` - the written expansion for each strategy, keyed by its number.
- `source/prose.json` - Mark's own chapter prose, extracted from the definitive guide PDF.

To change wording, edit the relevant `content/ch0*.py` and rebuild:

```sh
python3 build.py
```

To re-extract from the original sources after updating an infographic or the guide:

```sh
python3 source/extract.py        # infographics -> source/strategies.json
python3 source/extract_prose.py  # guide PDF    -> source/prose.json
python3 build.py
```

`build.py` needs only the standard library. `extract_prose.py` needs `pypdf`.

## Accessibility

WCAG 2.2 AA is the floor, with AAA where it was achievable.

- **Contrast.** Body text is 16.5:1, secondary text 7.0:1, both AAA. Every chapter's link
  colour clears AA on white and on the panel background. The 17 infographic cluster colours
  that failed white-on-colour in the number badge are darkened programmatically by
  `readable_on_white_text()` in `build.py`, which preserves the hue while clearing AA.
- **Keyboard.** Everything is operable without a mouse. Three skip links, visible 3px focus
  rings that switch colour on dark panels, arrow-key movement in the chapter menu, a focus
  trap and Escape handling in the reading-controls panel, and in-page links that move focus
  to the destination rather than only scrolling to it.
- **Reflow.** No horizontal scrolling at 200% text on a 640px viewport. Sticky offsets are
  measured at runtime rather than hard coded, so they survive a wrapped header and any text size.
- **Target size.** All standalone targets meet the 24px minimum. Inline links in prose take
  the WCAG 2.2 inline exception.
- **Preferences.** `prefers-reduced-motion`, `prefers-contrast` and `forced-colors` are all
  handled, plus a print stylesheet.
- **Without JavaScript.** All content, navigation and in-page links work. Only the reading
  controls widget requires it.

Tests live in `source/` and run against a local server:

```sh
python3 -m http.server 8899 &
node source/a11y-test.cjs      # structure, keyboard, reflow, target size
node source/nojs-test.cjs      # progressive enhancement
node source/overflow-test.cjs  # locates any element breaking reflow
```

## Deployment

GitHub Pages from `main`, root folder.

- `CNAME` contains `pedagogyfirst.ictevangelist.com`
- `.nojekyll` stops Jekyll processing
- DNS: a `CNAME` record for `pedagogyfirst` pointing at `ictevangelist.github.io`

## Licence

Content © Mark Anderson, licensed
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
