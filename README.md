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
| `index.html` | Home: the five principles, the six chapters, running it with a team |
| `find-a-strategy/` | All 144 searchable at once: by problem, by chapter, or by phrase |
| `get-the-guide/` | The PDF, as a real page so the download can actually be counted |
| `privacy/` | Privacy and cookies, written to match what the site actually does |
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
- `content/front_matter.py` - the endorsements, the About Mark copy, the work-with-Mark pitch.
- `content/reviewer_additions.py` - the five principles, the per-chapter "How would you know?"
  measures, and the three CPD session plans.
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

## Where the shape came from

Eight people endorsed the original guide. The site was read back against what each of
them actually said they valued, and the gaps became the work:

| Who | What they asked of the guide | What the site now does |
| --- | --- | --- |
| Gemma Gwilliam | "the right approach is chosen for the right activity at the right moment in time" | `/find-a-strategy/`: all 144 at once, eight problem-first starters, chapter chips, `?q=` deep links. Search could only work inside a chapter before, which is no help when you don't know which chapter you need |
| Dr Zoë Elder | "an elegant set of evidence-informed design principles" | Five principles on the home page, each cross-linked to the clusters it runs through. They were implied by 144 strategies and never stated |
| Al Kingsley MBE | technology "has to genuinely add value that can be measured" | A "How would you know?" section on every chapter, naming the signal and how to read it. The site said what to do and never how you'd know it worked |
| Tom Sale | "I will use this guide to support staff development" | Three session plans: 20 minutes in a department meeting, an hour twilight, an INSET day |
| Jacqui Hughes | "practical and usable straight away… embedding digital across the curriculum" | The same plans, plus the licence stated in plain words so nobody has to ask before using it |
| Jo Fletcher-Saxon | "Mark is generous with his sharing; no gatekeeping" | `SIGNUP_EMBED_URL` stays empty. Nothing is behind a form, and the licence says so out loud |
| Olly Lewis | "applied across classrooms, curricula and systems" | Nothing assumes England: no key stages, no phase-locked examples, no single inspectorate |
| Emma Darcy | "it avoids gimmicks and trends" | Every strategy names the failure mode, the point at which the tool starts doing the thinking |

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
- **Reflow.** No horizontal scrolling at 200% text on a 640px viewport, or at 320px with
  normal text. Sticky offsets are measured at runtime rather than hard coded, so they
  survive a wrapped header and any text size.
- **Target size.** All standalone targets meet the 24px minimum. Inline links in prose take
  the WCAG 2.2 inline exception.
- **Preferences.** `prefers-reduced-motion`, `prefers-contrast` and `forced-colors` are all
  handled, plus a print stylesheet.
- **Without JavaScript.** All content, navigation and in-page links work, on all nine pages.
  The chapters panel is opened by a button, so a `<noscript>` rule drops it open and removes
  the button rather than leaving a dead control. The two search boxes ship `disabled` and are
  enabled by their scripts. Only the reading-controls widget needs JavaScript, and everything
  it offers is already the page's default.

Tests live in `source/` and run against a local server:

```sh
python3 -m http.server 8899 &
node source/a11y-test.cjs      # structure, keyboard, reflow, target size, 6 pages
node source/nojs-test.cjs      # progressive enhancement across all 9 pages
node source/overflow-test.cjs  # reflow at 640px/200% and 320px/100%, all 9 pages
node source/feature-test.cjs   # chapters panel, per-chapter filter, assets
node source/finder-test.cjs    # /find-a-strategy/ search, chips, starters, deep links
```

## Writing

`source/tone-audit.py` holds the writing to the standard Mark set, and does it twice.

First against `content/ch0*.py`, the 144 written expansions: banned phrases and the
wider family of AI tells, contraction rate, stiff connectives, sentence length. Then
against the built HTML, so nothing written anywhere on the site escapes it: headings,
standfirsts, calls to action, the principles, the CPD plans.

Three kinds of text are reported separately rather than quietly skipped, because they
are not the site's to rewrite:

| `data-source` | What it is |
| --- | --- |
| *(blockquote)* | Other people's words. Never edited. |
| `guide` | Mark's published guide prose, extracted from the PDF. His call, not a script's. |
| `infographic` | Strategy titles and summaries as printed on the original six. Changing them breaks the link back to the artwork. |

```sh
python3 source/contractions.py   # proposes contractions, shows every change first
python3 source/tone-audit.py     # the audit, expansions then whole site
```

No em dashes. The audit fails the build's own copy on one, wherever it appears.

## Analytics

Off by default. Nothing loads, no banner appears, no cookie is set.

To switch it on, put the GA4 measurement ID into `GA_MEASUREMENT_ID` at the top of
`build.py` and rebuild. The script then loads behind a consent banner: nothing is
requested from Google until the visitor agrees, and declining sticks. Advertising
storage and personalisation are denied in Consent Mode regardless of the answer.

Five events, chosen to answer questions worth asking of this site rather than to
fill a dashboard:

| Event | Question it answers |
| --- | --- |
| `guide_download` | Did the PDF actually get taken, and from which page |
| `infographic_download` | Which of the six pulls its weight |
| `cta_click` | Did anyone go on to make contact, and from where on the page |
| `strategy_filter` | What people search for, which shows what they expected to find |
| `chapter_depth` | Whether a chapter got read or bounced off the top |
| `strategy_search` | What people search for across all 144, and how many results came back |
| `problem_starter` | Which problem teachers actually arrive with |
| `chapter_chip` | Which of the six people narrow to first |

`strategy_search` is the one to watch: a search that runs across all 144 and returns
nothing is a gap in the guide, and it's the closest thing here to a request for the
next infographic.

`source/analytics-test.cjs` checks that nothing reaches Google before consent,
that declining persists across pages, and that each event fires.

`/privacy/` describes exactly this behaviour and carries a control to change the
answer. That control only renders when `GA_MEASUREMENT_ID` is set, so the page
never offers to change a choice that cannot exist.

## Deployment

GitHub Pages from `main`, root folder.

- `CNAME` contains `pedagogyfirst.ictevangelist.com`
- `.nojekyll` stops Jekyll processing
- DNS: a `CNAME` record for `pedagogyfirst` pointing at `ictevangelist.github.io`

## Licence

Content © Mark Anderson, licensed
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
