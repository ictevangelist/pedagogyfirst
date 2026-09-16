#!/usr/bin/env python3
# =====================================================================
# pedagogyfirst.ictevangelist.com — the guide, web based.
#
# Eight pages: home, find-a-strategy, six chapters, built from:
#
#   source/strategies.json  the 144 cards
#   source/prose.json       the chapter prose and front matter
#   source/front.json       front and back matter
#
# Run:  python3 build.py
# =====================================================================
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "source"
SITE = "https://pedagogyfirst.ictevangelist.com"
TITLE = "Pedagogy First. Technology Second."

CHAPTERS = json.loads((SRC / "strategies.json").read_text())
PROSE = json.loads((SRC / "prose.json").read_text())
FRONT = json.loads((SRC / "front.json").read_text())
# Real pixel sizes of the six renders, so the browser reserves the right
# space and the page does not jump as they load. They are not all the same.
SIZES = json.loads((SRC / "image-sizes.json").read_text())
# Non-canonical discovery metadata: classroom needs, inclusive practice
# lenses, the try-tomorrow shortlist and related areas. Maps existing
# strategies to routes; never carries strategy wording of its own.
LENSES = json.loads((SRC / "lenses.json").read_text())
CH_BY_SLUG = {c["slug"]: c for c in CHAPTERS}
STRAT = {}
for _c in CHAPTERS:
    _cl = {x["key"]: x for x in _c["clusters"]}
    for _s in _c["strategies"]:
        STRAT[f"{_c['slug']}/{_s['slug']}"] = (_c, _s, _cl[_s["cluster"]])
TRY_TOMORROW = set(LENSES["try_tomorrow"])
# Reverse index: strategy ref -> the companion routes that surface it.
ALSO_UNDER = {}
for _n in LENSES["needs"]:
    for _r in _n["strategies"]:
        ALSO_UNDER.setdefault(_r, []).append((_n["label"], f"/classroom-needs/#{_n['key']}"))
for _n in LENSES["inclusive"]:
    for _r in _n["strategies"]:
        ALSO_UNDER.setdefault(_r, []).append((f"Inclusive practice: {_n['label'].lower()}", f"/inclusive-practice/#{_n['key']}"))
for _r in LENSES["try_tomorrow"]:
    ALSO_UNDER.setdefault(_r, []).append(("Try this tomorrow", "/try-this-tomorrow/"))
REVIEW_LABEL = "September 2026"
STRATEGY_PAGES = json.loads((SRC / "strategy-pages.json").read_text())["pages"]
PILOT = {p["ref"]: p for p in STRATEGY_PAGES}
def canonical_strategy_url(ref):
    """The one permanent home for a strategy: its own page if it has one,
    otherwise its anchor on the strand page."""
    if ref in PILOT:
        return f"/strategies/{PILOT[ref]['slug']}/"
    c, st, _ = STRAT[ref]
    return f"/{c['slug']}/#{st['slug']}"


def e(s):
    return html.escape(s or "", quote=True)


# ---------------------------------------------------------------- colour
def _lum(hex_colour):
    h = hex_colour.lstrip("#")
    parts = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in parts]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(fg, bg):
    a, b = _lum(fg), _lum(bg)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


def darken_for_white(hex_colour, target=4.6):
    """The infographic hues carry dark text on pale cards; darken until
    white text on the hue clears WCAG AA so the badges stay legible."""
    h = hex_colour.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    for _ in range(60):
        cand = f"#{r:02x}{g:02x}{b:02x}"
        if contrast("#ffffff", cand) >= target:
            return cand
        r, g, b = (int(v * 0.94) for v in (r, g, b))
    return "#333333"


# ---------------------------------------------------------------- chrome
# The stylesheet is linked with a content hash so browsers pick up CSS
# changes with the page instead of serving a stale cached copy.
import hashlib
CSS_V = hashlib.sha256((ROOT / "css" / "styles.css").read_bytes()).hexdigest()[:8]
A11Y_V = hashlib.sha256((ROOT / "js" / "a11y.js").read_bytes()).hexdigest()[:8]
FINDER_V = hashlib.sha256((ROOT / "js" / "finder.js").read_bytes()).hexdigest()[:8]
COPY_V = hashlib.sha256((ROOT / "js" / "copylink.js").read_bytes()).hexdigest()[:8]


def head(title, description, canonical, jsonld=None, body_class=None):
    return f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<meta name="author" content="Mark Anderson">
<link rel="canonical" href="{e(canonical)}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{e(canonical)}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/css/styles.css?v={CSS_V}">{_ld(jsonld)}
</head>
<body{' class="' + body_class + '"' if body_class else ''}>
<a class="skip" href="#main">Skip to main content</a>
"""


SEARCH_ICON = ('<svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" focusable="false" '
               'fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round">'
               '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m20 20-4.8-4.8"/></svg>')


def _ld(jsonld):
    if not jsonld:
        return ""
    return '\n<script type="application/ld+json">' + json.dumps(jsonld, ensure_ascii=False) + "</script>"


PERSON_LD = {
    "@type": "Person",
    "@id": "https://ictevangelist.com/#mark-anderson",
    "name": "Mark Anderson",
    "url": "https://ictevangelist.com",
}


def strand_jsonld(c):
    """Accurate structured data for a strand page: the page, its author, and
    an ItemList naming each strategy at its anchor. Describes the existing
    structure; it does not pretend each strategy is a separate page."""
    canonical = f"{SITE}/{c['slug']}/"
    items = [{
        "@type": "ListItem", "position": i + 1,
        "name": st["title"], "url": f"{canonical}#{st['slug']}",
    } for i, st in enumerate(c["strategies"])]
    return {
        "@context": "https://schema.org",
        "@graph": [
            PERSON_LD,
            {"@type": "WebPage", "@id": canonical, "url": canonical,
             "name": c["title"], "inLanguage": "en-GB",
             "author": {"@id": PERSON_LD["@id"]}},
            {"@type": "ItemList", "name": c["title"],
             "numberOfItems": len(c["strategies"]), "itemListElement": items},
        ],
    }


def header(current=None):
    # The brand is the home link; the strip is the six guides.
    items = []
    for c in CHAPTERS:
        cur = ' aria-current="page"' if current == c["slug"] else ""
        items.append(f'<li><a href="/{c["slug"]}/"{cur}>'
                     f'<span class="n" aria-hidden="true">{c["number"]}</span>{e(c["name"])}</a></li>')
    find_cur = ' aria-current="page"' if current == "find" else ""
    needs_cur = ' aria-current="page"' if current == "needs" else ""
    tom_cur = ' aria-current="page"' if current == "tomorrow" else ""
    return f"""<header class="site-header">
  <div class="wrap bar">
    <a class="brand" href="/">Pedagogy First. <span>Technology Second.</span></a>
    <nav class="tools" aria-label="Tools">
      <a class="dl-link" href="/classroom-needs/"{needs_cur}>What are you trying to improve?</a>
      <a class="dl-link" href="/try-this-tomorrow/"{tom_cur}>Try tomorrow</a>
      <a class="find-pill" href="/find-a-strategy/"{find_cur}>{SEARCH_ICON}Find a strategy</a>
    </nav>
  </div>
  <nav class="chapters" aria-label="Guides">
    <ul class="wrap">{"".join(items)}</ul>
  </nav>
</header>
"""


def footer():
    return f"""<footer class="site-footer">
  <div class="wrap">
    <p class="motto">{e(FRONT["about"]["motto"])}</p>
    <nav class="footer-nav" aria-label="More from this site">
      <div>
        <h2>Explore</h2>
        <ul>
          <li><a href="/find-a-strategy/">Find a strategy</a></li>
          <li><a href="/classroom-needs/">Classroom needs</a></li>
          <li><a href="/inclusive-practice/">Inclusive practice</a></li>
          <li><a href="/try-this-tomorrow/">Try this tomorrow</a></li>
        </ul>
      </div>
      <div>
        <h2>Professional learning</h2>
        <ul>
          <li><a href="/professional-learning/">Using Pedagogy First with colleagues</a></li>
        </ul>
      </div>
      <div>
        <h2>Understand</h2>
        <ul>
          <li><a href="/about-pedagogy-first/">About Pedagogy First</a></li>
          <li><a href="/about-the-evidence/">About the evidence</a></li>
          <li><a href="/updates/">Updates</a></li>
        </ul>
      </div>
      <div>
        <h2>Resources</h2>
        <ul>
          <li><a href="/download-resources/">Downloads</a></li>
        </ul>
      </div>
    </nav>
    <p>{e(FRONT["contact"]["line"])}
       <a href="{e(FRONT["contact"]["url"])}">ictevangelist.com/contact</a></p>
    <p class="fine">Content &copy; Mark Anderson.
       The guide is licensed CC BY-NC-ND 4.0. The infographics are licensed CC BY-NC-SA 4.0.
       The six infographics and 144 strategies are the fixed published resource; this site is the
       living companion around them. Companion guidance reviewed: {REVIEW_LABEL} &middot;
       <a href="/updates/">updates</a>.</p>
  </div>
</footer>
<script src="/js/a11y.js?v={A11Y_V}" defer></script>
<script src="/js/copylink.js?v={COPY_V}" defer></script>
</body>
</html>
"""


def prose_paras(paras, cols=True):
    body = "".join(f"<p>{e(p)}</p>" for p in paras)
    return f'<div class="{"cols" if cols else "plain"}">{body}</div>'


def split_section(sec_id, kicker, heading, inner, img, alt, img_left=False):
    side = "split-imgleft" if img_left else "split-imgright"
    return f"""<section id="{sec_id}" aria-labelledby="{sec_id}-h">
  <div class="wrap split {side}">
    <div class="split-text">
      <p class="kicker">{e(kicker)}</p>
      <h2 id="{sec_id}-h">{e(heading)}</h2>
      {inner}
    </div>
    <figure class="split-fig">
      <img src="/assets/{img}" width="1200" height="900" alt="{e(alt)}" decoding="async">
    </figure>
  </div>
</section>
"""


def section(sec_id, kicker, heading, inner):
    return f"""<section id="{sec_id}" aria-labelledby="{sec_id}-h">
  <div class="wrap">
    <p class="kicker">{e(kicker)}</p>
    <h2 id="{sec_id}-h">{e(heading)}</h2>
    {inner}
  </div>
</section>
"""


def quote_fig(q, cls="praise"):
    return (f'<figure class="{cls}"><blockquote><p>{e(q["quote"])}</p></blockquote>'
            f'<figcaption>{e(q["name"])}<span>{e(q["role"])}</span></figcaption></figure>')


def pdf_size_mb(slug):
    p = ROOT / "downloads" / f"{slug}.pdf"
    return p.stat().st_size / 1024 / 1024 if p.exists() else None


def infographic_figure(c, on_chapter_page=True):
    slug = c["slug"]
    mb = pdf_size_mb(slug)
    alt = (f"The {c['name']} infographic. The same 24 strategies as a one page poster. "
           f"Every strategy on it is written out as text below.")
    dl = ""
    if mb:
        dl = (f'<a href="/downloads/{slug}.pdf">Download this guide as a PDF</a> '
              f'<span class="meta">({mb:.1f}&nbsp;MB, text is selectable and searchable)</span> · '
              f'<a href="/assets/infographics/{slug}-download.png">Download the infographic as an image</a>')
    w, h = SIZES.get(slug, [1600, 1194])
    return f"""<figure class="infographic">
      <img src="/assets/infographics/{slug}.webp" width="{w}" height="{h}"
           alt="{e(alt)}" decoding="async"{"" if on_chapter_page else ' loading="lazy"'}>
      <figcaption>{dl}</figcaption>
    </figure>"""


# ---------------------------------------------------------------- companion
def tie(text):
    """Join the final two words of a companion string with a non-breaking
    space so its last line can never be a single orphaned word."""
    i = text.rstrip().rfind(" ")
    return text if i < 0 else text[:i] + "\u00a0" + text[i + 1:]


def companion_section(sec_id, kicker, heading, inner):
    """Like section(), marked data-companion so verification tooling can
    separate companion additions from canonical guide content."""
    return f"""<section id="{sec_id}" data-companion aria-labelledby="{sec_id}-h">
  <div class="wrap">
    <p class="kicker">{e(kicker)}</p>
    <h2 id="{sec_id}-h">{e(heading)}</h2>
    {inner}
  </div>
</section>
"""


def finding_row(ref, tag_tomorrow=False):
    """One strategy as a linked card row, identical to the finder's rows.
    Renders from canonical data only."""
    c, st, cl = STRAT[ref]
    tom = ' data-tomorrow="1"' if tag_tomorrow and ref in TRY_TOMORROW else ""
    return f"""        <li class="finding"{tom}>
          <a href="{canonical_strategy_url(ref)}">
            <span class="sicon" aria-hidden="true">{st['icon']}</span>
            <span class="ftext"><strong>{e(st['title'])}</strong>
              <span class="fsum">{e(st['summary'])}</span>
              <span class="fwhere">{c['number']} {e(c['name'])} &middot; {e(cl['label'])}</span>
            </span>
          </a>
        </li>"""


def findings_list(refs):
    rows = "\n".join(finding_row(r) for r in refs)
    return f'<ul class="findings">\n{rows}\n      </ul>'


def support_block(lede, strong=False):
    cls = "support support-strong" if strong else "support"
    return f"""<section class="{cls}" aria-labelledby="support-h">
  <div class="wrap">
    <p class="kicker">Want to take this further?</p>
    <h2 id="support-h">Support is available</h2>
    <p>{lede}</p>
    <p class="actions"><a class="btn" href="https://ictevangelist.com/contact/">Work with Mark</a></p>
  </div>
</section>
"""


def simple_page(slug, title, desc, hero_eyebrow, hero_h1, hero_lead, body, current=None, narrow=False):
    out = [
        head(f"{title} | {TITLE}", desc, f"{SITE}/{slug}/",
             body_class="text-page" if narrow else None),
        header(current),
        f"""<div class="hero">
  <div class="wrap">
    <p class="eyebrow">{e(hero_eyebrow)}</p>
    <h1>{hero_h1}</h1>
    <p class="lead">{hero_lead}</p>
  </div>
</div>
<main id="main">
""",
        body,
        "</main>\n",
        footer(),
    ]
    target = ROOT / slug
    target.mkdir(exist_ok=True)
    (target / "index.html").write_text("".join(out), encoding="utf-8")


def build_needs():
    chips = "".join(f'<li><a href="#{n["key"]}">{e(n["label"])}</a></li>' for n in LENSES["needs"])
    sections = []
    for n in LENSES["needs"]:
        sections.append(f"""<section id="{n['key']}" aria-labelledby="{n['key']}-h">
  <div class="wrap">
    <h2 id="{n['key']}-h">{e(n['label'])}</h2>
    <p class="wide">{e(tie(n['blurb']))}</p>
    {findings_list(n['strategies'])}
  </div>
</section>
""")
    body = f"""<section id="how-this-works" aria-labelledby="how-h">
  <div class="wrap">
    <p class="kicker">How this works</p>
    <h2 id="how-h">Start with the learning need</h2>
    <p class="wide">Explore the approaches that speak to it. Think about your subject, your phase and your pupils. Decide what might help. Then, and only then, ask whether technology adds anything useful.</p>
    <p class="note wide">Every strategy below is one of the original 144, written exactly as it appears on its card. Nothing has been renamed or rewritten; a strategy can appear under more than one need. Each link takes you to the strategy's own page, with why you might use it, what it could look like in your classroom and a way to begin. Prefer the original structure? <a href="/#guides">Browse the six guides</a> or <a href="/find-a-strategy/">search all 144</a>.</p>
    <nav aria-label="Classroom needs">
      <ul class="chips">{chips}</ul>
    </nav>
  </div>
</section>
""" + "".join(sections)
    simple_page("classroom-needs", "What are you trying to improve?",
        "Start with a classroom need and go straight to the relevant Pedagogy First strategies: "
        "remembering more, checking understanding, better questioning, useful feedback and more.",
        "Start with the need", "What are you trying to improve?",
        "You don't need to know a strategy's name or which guide it lives in. "
        "Start with what's happening in your classroom.",
        body, current="needs")


def build_inclusive():
    sections = []
    for n in LENSES["inclusive"]:
        sections.append(f"""<section id="{n['key']}" aria-labelledby="{n['key']}-h">
  <div class="wrap">
    <p class="kicker">A lens on the 144</p>
    <h2 id="{n['key']}-h">{e(n['label'])}</h2>
    <p class="wide">{e(tie(n['blurb']))}</p>
    {findings_list(n['strategies'])}
  </div>
</section>
""")
    body = f"""<section id="intro" aria-labelledby="intro-h">
  <div class="wrap">
    <p class="kicker">What this page is</p>
    <h2 id="intro-h">A curated lens across the existing 144 strategies</h2>
    <div class="plain">
      <p>Inclusive practice begins with responsive teaching: identifying the barriers pupils may experience and making thoughtful decisions about how best to support access, participation and independence.</p>
      <p>This page brings together existing Pedagogy First strategies that may help. It doesn't introduce a new set of strategies, and it isn't a SEND intervention framework. Everything here comes from the original 144, seen through six practical lenses, and should be used thoughtfully, responsively and in context. If your school thinks about inclusion through ideas like universal design for learning, these lenses will feel familiar: reduce the barriers, and more pupils can show what they know.</p>
    </div>
  </div>
</section>
""" + "".join(sections) + f"""<section id="judgement" aria-labelledby="judgement-h">
  <div class="wrap">
    <p class="kicker">Professional judgement matters</p>
    <h2 id="judgement-h">No strategy works for every pupil</h2>
    <p class="wide">No strategy works for every pupil, subject or context. Inclusive practice depends on understanding your pupils, identifying the barriers they experience, evaluating what helps and adapting your teaching accordingly. The lenses above are places to look, not prescriptions.</p>
  </div>
</section>
<section id="team" aria-labelledby="team-h">
  <div class="wrap">
    <p class="kicker">Use this with your team</p>
    <h2 id="team-h">A 30 minute team activity</h2>
    <ol class="steps">
      <li>Identify a barrier to participation or learning that pupils are actually experiencing.</li>
      <li>Explore the lens above that speaks to it.</li>
      <li>Select two or three strategies that look relevant.</li>
      <li>Discuss why each might help, not just whether it looks appealing.</li>
      <li>Consider what adaptation your subject, phase and pupils would need.</li>
      <li>Agree one approach to trial.</li>
      <li>Look at what happens to learning and participation.</li>
      <li>Decide together whether to continue, adapt or stop.</li>
    </ol>
  </div>
</section>
""" + support_block(
        "If your school or trust wants help thinking through inclusive teaching in context, "
        "that's work I do with leaders and teams.")
    simple_page("inclusive-practice", "Inclusive Practice",
        "Inclusive classroom practice through six practical lenses on the 144 Pedagogy First "
        "strategies: access, participation, working memory and cognitive load, language, "
        "independence, self regulation and feedback. Not a SEND framework; a thoughtful way in.",
        "A lens, not a seventh guide", "Inclusive Practice",
        "Approaches from across the 144 strategies that may support access, participation, "
        "clarity, independence and manageable cognitive demand.",
        body)


def build_tomorrow():
    body = f"""<section id="list" aria-labelledby="list-h">
  <div class="wrap">
    <p class="kicker">Deliberately curated</p>
    <h2 id="list-h">Fourteen you could trial within ordinary teaching</h2>
    <p class="wide">Chosen from the 144 because they're easy to understand, need little or no preparation, respond to common classroom needs, and don't require buying or adopting anything. Each links to its own page.</p>
    {findings_list(LENSES['try_tomorrow'])}
    <p class="note">This list is curated, not rotated for novelty. Want to start from a specific need instead? <a href="/classroom-needs/">What are you trying to improve?</a></p>
  </div>
</section>
"""
    simple_page("try-this-tomorrow", "Something to try tomorrow",
        "Low preparation Pedagogy First strategies you could sensibly trial in tomorrow's "
        "lessons: retrieval, questioning, feedback and metacognition approaches that need "
        "nothing new bought or installed.",
        "Ten minutes to choose", "Something to try tomorrow",
        "The promise of this whole resource in one page: something here may help you tomorrow morning.",
        body, current="tomorrow")


def build_strategy_page(page):
    ref = page["ref"]
    c, st, cl = STRAT[ref]
    url = f"/strategies/{page['slug']}/"
    accent = darken_for_white(cl["colour"])

    def paras(key):
        v = page.get(key)
        if not v:
            return ""
        items = v if isinstance(v, list) else [v]
        return "".join(f"<p>{e(tie(t))}</p>" for t in items)

    def bullets(key):
        v = page.get(key) or []
        return "".join(f"<li>{e(tie(t))}</li>" for t in v)

    card = strategy_article(st, cl, c["slug"], on_own_page=True)
    sections = [f"""<section id="the-strategy" aria-labelledby="ts-h">
  <div class="wrap">
    <p class="kicker">The strategy, as published</p>
    <h2 id="ts-h">Exactly as it appears on the card</h2>
    <div class="strategy-grid strategy-single" style="--accent:{accent}">
{card}
    </div>
    <p class="note" data-companion>Part of {e(cl["label"])} in <a href="/{c["slug"]}/#{st["slug"]}">{c["number"]} {e(c["name"])}</a>, where it sits alongside its neighbouring strategies, the infographic and the thinking for the whole area.</p>
  </div>
</section>
"""]
    if page.get("why"):
        sections.append(companion_section("why-use-it", "Why you might use it",
            "The problem it may help with", paras("why")))
    if page.get("example"):
        sections.append(companion_section("example", "What it could look like",
            "One way in your classroom", paras("example")))
    if page.get("try"):
        sections.append(companion_section("try-it", "Try it",
            "A way to begin", paras("try")))
    if page.get("notice"):
        sections.append(companion_section("notice", "What to notice",
            "Reading what happens", '<ul class="prompts">' + bullets("notice") + "</ul>"))
    if page.get("consider"):
        sections.append(companion_section("consider", "Things to think about",
            "Before and while you use it", '<ul class="prompts">' + bullets("consider") + "</ul>"))
    if page.get("related"):
        sections.append(companion_section("related", "Related strategies",
            "Where this connects", findings_list(page["related"])))
    if page.get("lenses"):
        lens_by_key = {n["key"]: n for n in LENSES["inclusive"]}
        lis = "".join(
            f'<li><a href="/inclusive-practice/#{k}">{e(lens_by_key[k]["label"])}</a></li>'
            for k in page["lenses"])
        sections.append(companion_section("inclusive", "Inclusive practice",
            "The lens this connects with",
            "<p>Through the inclusive practice lens, this is one of the approaches that may reduce barriers around:</p>"
            + '<ul class="prompts">' + lis + "</ul>"))
    if page.get("tech"):
        tech_inner = paras("tech")
        st_block = ""
        stair = page.get("stair")
        if stair:
            st_block = (
                "<p>" + e(tie(stair["lede"])) + "</p>"
                + '<figure class="prompt-block">'
                + '<figcaption>A prompt to start from, shaped by the STAIR approach '
                + '(Specific, Tell, Actionable, Iterate, Role)</figcaption>'
                + "<pre>" + e(stair["prompt"]) + "</pre>"
                + '<button class="copylink copyprompt" type="button" hidden '
                + 'aria-label="Copy this prompt">Copy prompt</button>'
                + "</figure>"
                + "<p>" + e(tie(stair["after"])) + "</p>")
        sections.append(companion_section("tech", "Technology second",
            "Where technology fits", tech_inner + st_block))
    wider = ""
    if page.get("wider"):
        informed = ""
        if st.get("informed_by"):
            informed = " The card\u2019s attribution stands as published: " + e(st["informed_by"]) + "."
        wider = companion_section("wider", "The wider thinking", "Where the evidence sits",
            "<p>" + e(tie(page["wider"])) + informed + "</p>"
            + f'<p class="note">The fuller picture, sources included, is in <a href="/{c["slug"]}/#further-reading">further reading and evidence for {e(c["name"])}</a>.</p>')
    keep = f"""<section class="keep-exploring" data-companion aria-labelledby="keep-h">
  <div class="wrap">
    <p class="kicker">Keep exploring</p>
    <h2 id="keep-h">Where next?</h2>
    <p>Back to <a href="/{c["slug"]}/#{st["slug"]}">this strategy in {c["number"]} {e(c["name"])}</a>, across to <a href="/classroom-needs/">what you're trying to improve</a>, or into <a href="/find-a-strategy/">all 144 at once</a>.</p>
  </div>
</section>
"""
    support = """<section class="support" data-companion aria-labelledby="support-h">
  <div class="wrap">
    <p class="kicker">Want to take this further?</p>
    <h2 id="support-h">Support is available</h2>
    <p>Pedagogy First gives you a starting point. If you want support exploring how approaches like this can work across your school, trust or professional learning programme, that work is available.</p>
    <p class="actions"><a class="btn" href="https://ictevangelist.com/contact/">Work with Mark</a></p>
  </div>
</section>
"""
    ld = {"@context": "https://schema.org", "@graph": [PERSON_LD, {
        "@type": "WebPage", "@id": SITE + url, "url": SITE + url,
        "name": st["title"], "inLanguage": "en-GB",
        "isPartOf": SITE + "/" + c["slug"] + "/",
        "author": {"@id": PERSON_LD["@id"]}}]}
    out = [
        head(st["title"] + " | " + TITLE,
             st["title"] + ": one of the 144 Pedagogy First strategies, from " + c["name"]
             + ", with why you might use it, what it could look like in your classroom, and a way to begin.",
             SITE + url, ld, body_class="text-page"),
        header(c["slug"]),
        f"""<div class="hero">
  <div class="wrap">
    <nav class="crumbs" aria-label="You are here"><a href="/">Pedagogy First</a> <span class="sep" aria-hidden="true">›</span> <a href="/{c["slug"]}/">{c["number"]} {e(c["name"])}</a> <span class="sep" aria-hidden="true">›</span> <span aria-current="page">{e(st["title"])}</span></nav>
    <h1>{e(st["title"])}</h1>
  </div>
</div>
<main id="main">
""",
        "".join(sections),
        wider,
        keep,
        support,
        "</main>\n",
        footer(),
    ]
    target = ROOT / "strategies" / page["slug"]
    target.mkdir(parents=True, exist_ok=True)
    (target / "index.html").write_text("".join(out), encoding="utf-8")


def build_evidence():
    body = """<section id="means" aria-labelledby="means-h">
  <div class="wrap">
    <p class="kicker">What evidence informed means here</p>
    <h2 id="means-h">Research, theory and professional knowledge, translated</h2>
    <div class="plain">
      <p>Pedagogy First draws on a wide body of educational research, theory and professional practice. Its purpose isn't to attach a citation to every classroom technique. It's to translate established thinking about teaching and learning into practical approaches teachers can consider in their own contexts.</p>
      <p>Several kinds of knowledge sit behind the guides, and they do different jobs. Original research studies establish mechanisms, like the testing effect or the limits of working memory. Theories of learning and instruction organise those mechanisms into something a teacher can plan with. Reviews and syntheses weigh the evidence across many studies. And professional knowledge, mine and that of the hundreds of schools I've worked with, shapes how any of it survives contact with a real classroom. A strategy earns a place on a card when those lines of evidence and experience point the same way.</p>
    </div>
  </div>
</section>
<section id="informed-by" aria-labelledby="informed-h">
  <div class="wrap">
    <p class="kicker">What informed by means</p>
    <h2 id="informed-h">An influence, not a warranty</h2>
    <div class="plain">
      <p>Each card names the thinking it draws on: Rooted in the work of, or the researcher named in the strategy itself. That attribution identifies an important intellectual influence on the strategy. It doesn't mean the named researcher personally proposed that exact classroom routine, and it doesn't mean every precise strategy has been independently tested as a standalone intervention in the form written here.</p>
      <p>Individual strategies may draw on several overlapping evidence bases. Where the research is nuanced or contested, the further reading on each guide page says so plainly.</p>
    </div>
  </div>
</section>
<section id="fixed" aria-labelledby="fixed-h">
  <div class="wrap">
    <p class="kicker">Why the original 144 stay fixed</p>
    <h2 id="fixed-h">A fixed resource, and a living companion</h2>
    <div class="plain">
      <p>The six infographics and 144 strategies form the core published resource. They've been downloaded, shared, printed and used in real schools, and they don't shift underneath the people using them.</p>
      <p>This microsite is the living companion around them: it helps you explore, connect and apply the ideas, and it gives the wider evidence and supporting thinking space to keep developing. The strategies stay put. The support around them grows.</p>
    </div>
  </div>
</section>
<section id="selection" aria-labelledby="selection-h">
  <div class="wrap">
    <p class="kicker">How evidence is selected</p>
    <h2 id="selection-h">A small number of strong sources</h2>
    <p class="wide">The further reading on each guide page is deliberately short. Priority goes to original research where it matters, significant reviews and syntheses, established researchers, reputable evidence organisations and high quality professional guidance. A handful of strong sources beats a long list of weak ones.</p>
  </div>
</section>
<section id="recipe" aria-labelledby="recipe-h">
  <div class="wrap">
    <p class="kicker">Research is not a recipe</p>
    <h2 id="recipe-h">The decision stays professional</h2>
    <p class="wide">Research can tell us a great deal about mechanisms, patterns and approaches that may support learning. It can't remove the need for teachers to understand their pupils, subject, curriculum and context. That's why every guide asks you to decide what fits, trial it, and look at what actually happens.</p>
    <p class="note">Companion guidance reviewed: """ + REVIEW_LABEL + """ &middot; <a href="/updates/">see what's changed</a>.</p>
  </div>
</section>
""" + support_block(
        "If you're a leader wanting help translating this evidence into professional learning "
        "or teaching and learning strategy, that's exactly the work I do.")
    simple_page("about-the-evidence", "About the evidence",
        "How Pedagogy First uses evidence: what evidence informed means, what the attributions "
        "on the 144 strategy cards do and don't claim, how sources are selected, and why "
        "research informs rather than replaces professional judgement.",
        "Evidence informed, not evidence decorated", "About the evidence",
        "What the research behind these guides can tell you, what it can't, "
        "and how to read the attributions on the cards.",
        body, narrow=True)


def build_pl():
    model = [
        ("Explore", "Identify the learning problem or the area of practice you care about."),
        ("Choose", "Select a small number of relevant Pedagogy First strategies."),
        ("Discuss", "Consider why they might help, rather than simply whether they look attractive."),
        ("Trial", "Agree one approach to try."),
        ("Notice", "Look at what happens to pupil learning, participation or understanding."),
        ("Review", "Decide whether to continue, adapt or stop."),
    ]
    steps = "".join(f"<li><strong>{t}.</strong> {d}</li>" for t, d in model)
    guides = "".join(
        f'<li><a href="/{c["slug"]}/#pl-activity"><span class="n" aria-hidden="true">{c["number"]}</span>'
        f'{e(c["name"])}</a></li>' for c in CHAPTERS)
    body = f"""<section id="who" aria-labelledby="who-h">
  <div class="wrap">
    <p class="kicker">Who it works for</p>
    <h2 id="who-h">Built for discussion, not delivery</h2>
    <div class="plain">
      <p>Pedagogy First works as professional learning material for individual teachers, departments, subject and phase teams, professional learning groups and senior leaders. The guides give you the thinking and the strategies; what turns them into professional learning is discussion, trial, reflection and honest evaluation.</p>
      <p>You don't need a licence, a login or a course. You need the guide, a genuine teaching and learning need, and half an hour with colleagues.</p>
    </div>
  </div>
</section>
<section id="model" aria-labelledby="model-h">
  <div class="wrap">
    <p class="kicker">A reusable model</p>
    <h2 id="model-h">Explore, choose, discuss, trial, notice, review</h2>
    <ol class="steps">{steps}</ol>
    <p class="note">Implementation isn't linear and trying something is never a guarantee of improvement. The point of notice and review is to find out what actually happened, and to be willing to stop.</p>
  </div>
</section>
<section id="activities" aria-labelledby="activities-h">
  <div class="wrap">
    <p class="kicker">Ready-made starting points</p>
    <h2 id="activities-h">A 30 minute activity on every guide</h2>
    <p>Each of the six guide pages carries a professional learning activity tailored to its area, ready to use with a team:</p>
    <ul class="guide-links">{guides}</ul>
    <p class="note">Exploring inclusion? <a href="/inclusive-practice/#team">Inclusive Practice has its own team activity</a>.</p>
  </div>
</section>
<section id="further-support" aria-labelledby="fs-h">
  <div class="wrap">
    <p class="kicker">Taking this further across your school or trust</p>
    <h2 id="fs-h">When you want more than the free activities</h2>
    <p class="wide">Everything on this page can be used independently, and schools do. Facilitated support is for organisations that want to develop a coherent professional learning programme around these ideas, connect them to existing teaching and learning priorities, help leaders and teams choose the right areas of focus, move from isolated strategies towards sustained implementation, and evaluate what's actually changing in classrooms.</p>
  </div>
</section>
""" + support_block(
        "Pedagogy First is designed to give teachers and leaders practical ideas they can "
        "explore and use. If you want support applying the thinking across a school or trust, "
        "developing professional learning around it, or embedding it into wider teaching and "
        "learning strategy, I can help.", strong=True)
    simple_page("professional-learning", "Using Pedagogy First for professional learning",
        "How to use the Pedagogy First guides for professional learning: a simple "
        "explore-choose-discuss-trial-notice-review model, 30 minute activities on every "
        "guide, and support for whole school or trust implementation.",
        "Professional learning", "Using Pedagogy First for professional learning",
        "The guides were made for discussion as much as for reading. "
        "Here's how to use them with colleagues.",
        body, narrow=True)


def build_updates():
    body = """<section id="log" aria-labelledby="log-h">
  <div class="wrap">
    <p class="kicker">The companion changes; the resource doesn't</p>
    <h2 id="log-h">September 2026</h2>
    <ul class="updates">
      <li>Added classroom need based discovery: <a href="/classroom-needs/">What are you trying to improve?</a></li>
      <li>Added the <a href="/inclusive-practice/">Inclusive Practice</a> lens across the 144 strategies.</li>
      <li>Added <a href="/about-the-evidence/">About the evidence</a>.</li>
      <li>Added <a href="/professional-learning/">professional learning support</a>, with a 30 minute activity on every guide.</li>
      <li>Added <a href="/try-this-tomorrow/">Something to try tomorrow</a>.</li>
      <li>Added further reading and evidence to all six guides.</li>
      <li>Added an individual page for every one of the 144 strategies, each with why you might use it, an example, a way to begin and what to notice. Where a tool type genuinely helps, the page says how; a handful carry an AI prompt shaped by the STAIR approach.</li>
      <li>Reorganised the homepage and navigation around three ways in: <a href="/classroom-needs/">what you're trying to improve</a>, <a href="/try-this-tomorrow/">something to try tomorrow</a> and exploring the 144. The story behind the guides moved to <a href="/about-pedagogy-first/">About Pedagogy First</a>, every strategy page gained a breadcrumb trail, and the search now also matches classroom needs and inclusive practice terms. No content was removed and no addresses changed.</li>
    </ul>
    <p class="note">The six infographics and 144 strategies are the fixed published resource and are unchanged. This page records significant changes to the companion material around them.</p>
  </div>
</section>
"""
    simple_page("updates", "Updates",
        "Significant changes to the Pedagogy First companion site. The published guide, "
        "infographics and 144 strategies remain fixed.",
        "The companion, evolving", "Updates",
        "Significant changes to the companion material on this site, most recent first.",
        body, narrow=True)


# Further reading per guide: a small number of strong sources, with honest
# notes. Links use DOIs or stable organisation pages.
FURTHER = {
 "retrieval-practice": [
  ('<a href="https://doi.org/10.1111/j.1467-9280.2006.01693.x">Roediger &amp; Karpicke (2006), Test-Enhanced Learning</a>, <em>Psychological Science</em>',
   "The modern starting point for the testing effect: retrieving beats restudying."),
  ('<a href="https://doi.org/10.1177/1529100612453266">Dunlosky, Rawson, Marsh, Nathan &amp; Willingham (2013), Improving Students\u2019 Learning With Effective Learning Techniques</a>, <em>PSPI</em>',
   "The review that ranked practice testing and distributed practice highest, and re-reading among the least effective."),
  ('<a href="https://doi.org/10.1126/science.1199327">Karpicke &amp; Blunt (2011), Retrieval Practice Produces More Learning than Elaborative Studying</a>, <em>Science</em>',
   "Retrieval outperformed concept mapping from the text, and even improved later concept mapping."),
  ('<a href="https://www.retrievalpractice.org/">Agarwal &amp; Bain, retrievalpractice.org</a>',
   "Free, practical guides translating the research for classrooms."),
  ('<a href="https://educationendowmentfoundation.org.uk/education-evidence/evidence-reviews/cognitive-science-approaches-in-the-classroom">EEF (2021), Cognitive Science Approaches in the Classroom</a>',
   "Supportive on retrieval and spacing, and honest that classroom evidence is thinner than laboratory evidence."),
 ],
 "formative-assessment": [
  ('<a href="https://doi.org/10.1080/0969595980050102">Black &amp; Wiliam (1998), Assessment and Classroom Learning</a>, <em>Assessment in Education</em>',
   "The review that put formative assessment on the map. The original effect sizes have been debated since; the direction of travel has held."),
  ('<a href="https://doi.org/10.1177/003172171009200119">Black &amp; Wiliam, Inside the Black Box</a>, <em>Phi Delta Kappan</em>',
   "The short version written for teachers, still the clearest statement of the argument."),
  ('<a href="https://www.ascd.org/el/articles/classroom-assessment-minute-by-minute-day-by-day">Leahy, Lyon, Thompson &amp; Wiliam (2005), Classroom Assessment: Minute by Minute, Day by Day</a>, <em>Educational Leadership</em>',
   "The five formative assessment strategies most schools now use, in their original form."),
  ('<a href="https://www.dylanwiliam.org/">Wiliam (2011), Embedded Formative Assessment</a>',
   "The book-length treatment, with the practical techniques behind many of these cards."),
 ],
 "feedback": [
  ('<a href="https://doi.org/10.3102/003465430298487">Hattie &amp; Timperley (2007), The Power of Feedback</a>, <em>Review of Educational Research</em>',
   "The feed up, feed back, feed forward model and the four levels of feedback."),
  ('<a href="https://doi.org/10.1037/0033-2909.119.2.254">Kluger &amp; DeNisi (1996), The Effects of Feedback Interventions on Performance</a>, <em>Psychological Bulletin</em>',
   "The meta-analysis behind the sobering finding that over a third of feedback interventions made performance worse."),
  ('<a href="https://doi.org/10.1111/j.2044-8279.1988.tb00874.x">Butler (1988), Task-involving and ego-involving properties of evaluation</a>, <em>BJEP</em>',
   "Comments alone beat grades, and grades cancel comments. A small study with a long shadow; its pattern has replicated in spirit if not always in size."),
  ('<a href="https://educationendowmentfoundation.org.uk/education-evidence/guidance-reports/feedback">EEF (2021), Teacher Feedback to Improve Pupil Learning</a>',
   "The guidance report: six recommendations, including laying foundations before feedback and planning for how pupils use it."),
 ],
 "questioning-and-discussion": [
  ('<a href="https://doi.org/10.1177/002248718603700110">Rowe (1986), Wait Time: Slowing Down May Be a Way of Speeding Up</a>, <em>Journal of Teacher Education</em>',
   "The wait time research: what changes when teachers pause for three seconds."),
  ('<a href="https://doi.org/10.1080/02671522.2018.1481140">Alexander (2018), Developing dialogic teaching: genesis, process, trial</a>, <em>Research Papers in Education</em>',
   "Reports the EEF randomised trial of dialogic teaching, with gains in English, maths and science."),
  ('<a href="https://robinalexander.org.uk/dialogic-teaching/">Robin Alexander, dialogic teaching</a>',
   "The five principles and the wider framework, from the source."),
  ('<a href="https://thinkingtogether.educ.cam.ac.uk/">Mercer and colleagues, Thinking Together, University of Cambridge</a>',
   "Exploratory talk and ground rules for talk, with free classroom materials."),
  ('<a href="https://doi.org/10.1007/s11217-007-9071-1">Michaels, O\u2019Connor &amp; Resnick (2008), Deliberative Discourse Idealized and Realized</a>, <em>Studies in Philosophy and Education</em>',
   "The thinking behind accountable talk."),
 ],
 "explanations-and-modelling": [
  ('<a href="https://www.aft.org/sites/default/files/Rosenshine.pdf">Rosenshine (2012), Principles of Instruction</a>, <em>American Educator</em>',
   "Ten principles, small steps and guided practice among them, drawn from cognitive science and studies of effective teachers."),
  ('<a href="https://doi.org/10.1007/s10648-019-09465-5">Sweller, van Merri\u00ebnboer &amp; Paas (2019), Cognitive Architecture and Instructional Design: 20 Years Later</a>, <em>Educational Psychology Review</em>',
   "Cognitive load theory reviewed by its authors, including where the theory has been revised."),
  ('<a href="https://doi.org/10.1017/9781316941355">Mayer, Multimedia Learning</a> (Cambridge University Press)',
   "The principles behind dual coding done properly: coherence, signalling, segmenting, modality and the rest."),
  ('<a href="https://www.danielwillingham.com/">Willingham, Why Don\u2019t Students Like School?</a>',
   "Memory is the residue of thought, and why concrete examples and stories work."),
 ],
 "metacognition-and-self-regulation": [
  ('<a href="https://educationendowmentfoundation.org.uk/education-evidence/guidance-reports/metacognition">EEF, Metacognition and Self-Regulated Learning</a>',
   "The guidance report most schools start with: seven recommendations, explicit strategy teaching among them."),
  ('<a href="https://doi.org/10.1207/s15430421tip4102_2">Zimmerman (2002), Becoming a Self-Regulated Learner: An Overview</a>, <em>Theory Into Practice</em>',
   "The forethought, performance and self-reflection cycle behind many of these cards."),
  ('<a href="https://doi.org/10.1037/0003-066X.34.10.906">Flavell (1979), Metacognition and Cognitive Monitoring</a>, <em>American Psychologist</em>',
   "Where the term begins: knowledge and regulation of one\u2019s own thinking."),
  ('<a href="https://educationendowmentfoundation.org.uk/education-evidence/evidence-reviews/metacognition-and-self-regulated-learning">Muijs &amp; Bokhove (2020), Metacognition and Self-Regulation: Evidence Review</a> (EEF)',
   "The fuller review behind the guidance, honest about where evidence is strong and where it thins."),
 ],
}

# A 30 minute professional learning activity per guide, tailored to its area.
PL_ACT = {
 "retrieval-practice": (
  "How does revision actually happen in your classrooms?",
  ["Read the thinking section above together, ten minutes at most.",
   "Individually, note how your students currently revise and how your lessons currently revisit prior content.",
   "Explore the strategies above and pick two or three that respond to what you noticed.",
   "Discuss the mechanism: why would retrieval, spacing or the struggle itself help your subject?",
   "Talk honestly about context: exam classes, practical subjects, younger pupils.",
   "Ask whether technology adds anything useful here, a quiz tool perhaps, or whether paper does the job.",
   "Choose one strategy each to trial for two weeks.",
   "Agree what you'll look at to judge it: what students retain, not just what they enjoyed."]),
 "formative-assessment": (
  "How do you know what they know, lesson by lesson?",
  ["Read the thinking section above together.",
   "Each colleague brings one moment from this week where they discovered too late that students hadn't understood.",
   "Explore the strategies and pick two or three that would have caught it earlier.",
   "Discuss the mechanism: what makes evidence of understanding visible while there's still time to act?",
   "Consider your context: class sizes, subjects, the students who never volunteer.",
   "Ask whether technology helps here, a response tool perhaps, or whether whiteboards do the job.",
   "Choose one strategy to trial in the same class next week.",
   "Agree the evidence you'll compare: what you knew about their understanding before and after."]),
 "feedback": (
  "Is the effort you spend marking coming back as learning?",
  ["Read the thinking section above together.",
   "Estimate, honestly, the hours your team spent on written feedback last fortnight, and what students did with it.",
   "Explore the strategies and pick two or three that shift effort from writing feedback to acting on it.",
   "Discuss the mechanism: why does feedback only work when it causes thinking?",
   "Consider context: subjects with extended writing, practical work, your marking policy as it stands.",
   "Ask whether technology genuinely helps here, audio comments perhaps, or whether it just moves the work.",
   "Choose one change to trial across one class set.",
   "Agree how you'll judge it: the quality of student responses to feedback, not the volume of feedback given."]),
 "questioning-and-discussion": (
  "Who does the thinking when you ask a question?",
  ["Read the thinking section above together.",
   "In pairs, recall this week's lessons: who answered, who never did, and how long the silence lasted before someone spoke.",
   "Explore the strategies and pick two or three that would spread the thinking wider.",
   "Discuss the mechanism: what changes when every student must compose an answer before any student gives one?",
   "Consider context: seminar-sized sixth form groups, classes of 32, students anxious about speaking.",
   "Ask whether technology helps, anonymous response perhaps, or whether hands-down and wait time cost nothing.",
   "Choose one strategy to trial for a week in one class.",
   "Agree what you'll count: who participates, and the length and quality of answers."]),
 "explanations-and-modelling": (
  "Bring a real explanation, and make it clearer",
  ["Read the thinking section above together.",
   "Each colleague brings one explanation or slide deck they'll teach next week.",
   "Explore the strategies, especially the cognitive load group, and audit the materials against them.",
   "Discuss the mechanism: what is competing for your students' working memory in each example?",
   "Strip one slide deck as a group: fewer words, integrated labels, one idea per reveal.",
   "Ask where technology genuinely helps, a visualiser or a short screencast, and where it adds noise.",
   "Each colleague commits to one revised explanation next week.",
   "Agree how you'll judge it: what students could do unaided afterwards, compared with the last topic."]),
 "metacognition-and-self-regulation": (
  "Teach one strategy explicitly, then watch what happens",
  ["Read the thinking section above together, noting that metacognition works on knowledge, never instead of it.",
   "Discuss where your students currently regulate their own learning, and where they wait to be told.",
   "Explore the strategies and pick two or three that teach a named method explicitly.",
   "Discuss the mechanism: why does naming and modelling a strategy beat telling students to reflect more?",
   "Consider context: which topic next fortnight gives a natural home for one strategy?",
   "Ask whether technology helps, a self-marking quiz for calibration perhaps, or whether prediction on paper does it.",
   "Choose one strategy to teach explicitly, inside subject content, within two weeks.",
   "Agree the evidence: do students use the method unprompted the following week?"]),
}


def further_block(slug):
    refs = FURTHER[slug]
    lis = "".join(f'<li><span class="ref-t">{t}.</span> <span class="ref-n">{e(n)}</span></li>'
                  for t, n in refs)
    inner = (f'<p>The wider evidence around this area, kept deliberately short. '
             f'No single study validates all 24 strategies; these are the traditions the '
             f'thinking comes from, and good places to read further. '
             f'<a href="/about-the-evidence/">How this site uses evidence</a>.</p>'
             f'<ul class="reading">{lis}</ul>')
    return companion_section("further-reading", "Further reading and evidence",
                   "Where this thinking comes from", inner)


def pl_block(slug, name):
    intro, steps = PL_ACT[slug]
    lis = "".join(f"<li>{e(st)}</li>" for st in steps)
    inner = (f'<p class="wide">{e(intro)}. A 30 minute activity for a department, phase or '
             f'professional learning group, using this guide as it stands.</p>'
             f'<ol class="steps">{lis}</ol>'
             f'<p class="note">The model behind this, and how to run it across a school or trust, '
             f'is on the <a href="/professional-learning/">professional learning\u00a0page</a>.</p>')
    return f"""<section id="pl-activity" data-companion aria-labelledby="pl-h">
  <div class="wrap">
    <p class="kicker">Use this for professional learning</p>
    <h2 id="pl-h">A 30 minute activity for your team</h2>
    {inner}
  </div>
</section>
"""


def related_block(slug):
    lis = []
    for target, why in LENSES["related_areas"][slug]:
        t = CH_BY_SLUG[target]
        lis.append(f'<li><a href="/{target}/"><strong><span class="n" aria-hidden="true">'
                   f'{t["number"]}</span> {e(t["name"])}</strong><span>{e(why)}</span></a></li>')
    return companion_section("related", "Related thinking", "You may also find useful",
                   f'<ul class="related">{"".join(lis)}</ul>')


# ---------------------------------------------------------------- home
def build_home():
    f = FRONT

    cards = []
    for c in CHAPTERS:
        op = PROSE["chapters"][c["slug"]]["opener"]
        fr = f["openers"][c["slug"]]
        if op.get("is_quote"):
            blurb = (f'<blockquote class="mini"><p>{e(op["standfirst"])}</p>'
                     f'<cite>{e(op["attribution"])}</cite></blockquote>')
        else:
            blurb = f"<p>{e(op['standfirst'])}</p>"
        accent = darken_for_white(c["clusters"][0]["colour"])
        cards.append(f"""      <li style="--accent:{accent}">
        <a href="/{c['slug']}/">
          <span class="card-no" aria-hidden="true">{c['number']}</span>
          <h3>{e(fr['display_title'])}</h3>
          {blurb}
          <p class="rooted">{e(fr['rooted'])}</p>
        </a>
      </li>""")

    out = [
        head(TITLE + " | Mark Anderson",
             "Six evidence informed guides to teaching and learning by Mark Anderson, "
             "ICT Evangelist. All 144 strategies, the six infographics and the full guide.",
             SITE + "/"),
        header("home"),
        f"""<div class="hero">
  <div class="wrap hero-grid">
    <div>
      <p class="eyebrow">{e(f["cover"]["eyebrow"])}</p>
      <h1>Pedagogy First.<br>Technology Second.</h1>
      <p class="lead">{e(f["cover"]["strapline"])}</p>
      <p class="hero-note">You don't need all 144. Pedagogy First is designed to be explored according to what you need, not read from beginning to end.</p>
    </div>
    <figure class="hero-cover">
      <a href="/download-resources/">
        <img src="/assets/guide-cover.webp" width="840" height="630"
             alt="The front cover of the guide. Download resources." decoding="async">
      </a>
    </figure>
  </div>
</div>
<main id="main">
<section id="routes" data-companion aria-labelledby="routes-h">
  <div class="wrap">
    <p class="kicker">Where do you want to start?</p>
    <h2 id="routes-h">One clear way in, whatever you need</h2>
    <ul class="route-grid route-primary">
      <li><a href="/classroom-needs/"><h3>What are you trying to improve?</h3><p>Start with the classroom problem or the aspect of practice you're working on.</p><span class="go">Start here</span></a></li>
      <li><a href="/try-this-tomorrow/"><h3>Try something tomorrow</h3><p>A deliberately small, practical selection of ideas you can explore quickly.</p><span class="go">See the shortlist</span></a></li>
      <li><a href="#guides"><h3>Explore the 144</h3><p>Browse the six areas and the wider collection at your own pace.</p><span class="go">Browse the areas</span></a></li>
    </ul>
    <p class="colleagues"><strong>Using Pedagogy First with colleagues?</strong> Explore ways to use the resource for professional learning, discussion and development across teams, schools and trusts. <a href="/professional-learning/">Start here</a>.</p>
  </div>
</section>
""",
        f"""<section id="guides" aria-labelledby="guides-h">
  <div class="wrap">
    <p class="kicker">Explore the 144</p>
    <h2 id="guides-h">Six Guides</h2>
    <ul class="guide-grid">
{"".join(cards)}
    </ul>
    <p class="note" data-companion>The story behind the guides, the thinking, and how to use them well: <a href="/about-pedagogy-first/">About Pedagogy First</a>.</p>
  </div>
</section>
""",
        f"""<section id="download" aria-labelledby="download-h">
  <div class="wrap">
    <p class="kicker">The guide</p>
    <h2 id="download-h">Download the full guide</h2>
    <p>The full 35 page guide, including all six infographics.</p>
    <p class="actions">
      <a class="btn" href="/downloads/pedagogy-first-technology-second.pdf">
        Download the full guide <span>PDF, 35 pages</span></a>
      <a class="btn btn-quiet" href="/download-resources/">Download resources</a>
    </p>
    <p class="fine">{e(f["cover"]["copyright"])}</p>
  </div>
</section>
</main>
""",
        footer(),
    ]
    (ROOT / "index.html").write_text("".join(out), encoding="utf-8")



def build_about():
    f = FRONT
    why = PROSE["front"]["why"]
    idea = PROSE["front"]["idea"]
    how = PROSE["front"]["how"]
    steps = "".join(f"<li>{e(s)}</li>" for s in how["steps"])
    lead_praise = "".join(quote_fig(q, "praise praise-lead") for q in f["praise"] if q.get("lead"))
    rest_praise = "".join(quote_fig(q) for q in f["praise"] if not q.get("lead"))
    ww = f["work_with"]
    ww_lead = "".join(quote_fig(q, "praise praise-lead") for q in ww["quotes"] if q.get("lead"))
    ww_rest = "".join(quote_fig(q) for q in ww["quotes"][1:4])

    out = [
        head("About Pedagogy First | " + TITLE,
             "The story behind Pedagogy First, Technology Second: why Mark Anderson made "
             "the guides, the idea that shapes them, how to use them, and the work behind them.",
             SITE + "/about-pedagogy-first/"),
        header(None),
        f"""<div class="hero">
  <div class="wrap">
    <p class="eyebrow">The story behind the site</p>
    <h1>About Pedagogy First</h1>
    <p class="lead">Why the guides exist, the idea that shapes them, and how to use them well.</p>
  </div>
</div>
<main id="main">
""",
        split_section("why", "Why I made these", why["standfirst"],
                      "".join(f"<p>{e(p)}</p>" for p in why["paragraphs"]),
                      "guide-page-strategies.webp",
                      "A strategies page from the guide: 24 retrieval practice "
                      "strategies on a single page."),
        split_section("idea", "The idea", idea["standfirst"],
                      "".join(f"<p>{e(p)}</p>" for p in idea["paragraphs"]),
                      "guide-page-contents.webp",
                      "The contents page of the guide: the six guides, numbered "
                      "one to six.", img_left=True),
        split_section("how", "How to use this guide", how["standfirst"],
                      prose_paras(how["paragraphs"], cols=False)
                      + f'<ol class="steps">{steps}</ol>'
                      + f'<p class="callout">{e(how["motto"])}</p>',
                      "guide-page-how.webp",
                      "The how to use this guide page from the guide, with the "
                      "six guides linked online."),
        f"""<section id="praise" class="band" aria-labelledby="praise-h">
  <div class="wrap">
    <p class="kicker">Praise</p>
    <h2 id="praise-h">{e(f["praise_heading"])}</h2>
    <div class="praise-leads">{lead_praise}</div>
    <div class="praise-grid">{rest_praise}</div>
  </div>
</section>
""",
        section("about", "About Mark", f["about"]["standfirst"],
                prose_paras(f["about"]["paragraphs"])),
        f"""<section id="work" class="band" aria-labelledby="work-h">
  <div class="wrap">
    <p class="kicker">Work with Mark</p>
    <h2 id="work-h">{e(ww["standfirst"])}</h2>
    <p class="wide">{e(ww["lede"])}</p>
    <div class="praise-leads">{ww_lead}</div>
    <div class="praise-grid">{ww_rest}</div>
    <p class="actions">
      <a class="btn btn-light" href="{e(f["contact"]["url"])}">Work with Mark</a>
    </p>
  </div>
</section>
""",
        "</main>\n",
        footer(),
    ]
    target = ROOT / "about-pedagogy-first"
    target.mkdir(exist_ok=True)
    (target / "index.html").write_text("".join(out), encoding="utf-8")



# ---------------------------------------------------------------- chapters
def strategy_article(st, cluster, chapter_slug=None, on_own_page=False):
    accent = darken_for_white(cluster["colour"])
    meta = []
    if st.get("tech"):
        meta.append(f'<span class="mlabel">Suggested technology</span> {e(st["tech"])}')
    if st.get("informed_by"):
        meta.append(f'<span class="mlabel">Informed by</span> {e(st["informed_by"])}')
    meta_html = f'<p class="smeta">{" · ".join(meta)}</p>' if meta else ""
    also_html = ""
    if chapter_slug:
        routes = ALSO_UNDER.get(f"{chapter_slug}/{st['slug']}", [])
        if routes:
            links = " · ".join(f'<a href="{u}">{e(l)}</a>' for l, u in routes)
            also_html = f'\n        <p class="also-under" data-companion><span class="mlabel">Find this under</span> {links}</p>'
    copy_btn = ""
    more_link = ""
    title_href = f"#{st['slug']}"
    if chapter_slug:
        _target = canonical_strategy_url(f"{chapter_slug}/{st['slug']}")
        if on_own_page:
            copy_btn = (f'<button class="copylink" type="button" hidden '
                        f'data-path="{_target}" '
                        f'aria-label="Copy a link to {e(st["title"])}">Copy link</button>')
        else:
            title_href = _target
    return f"""      <article class="strategy" id="{st['slug']}" style="--accent:{accent}">
        <h3><a href="{title_href}"><span class="sno" aria-hidden="true">{st['number']}</span>
          <span class="sicon" aria-hidden="true">{st['icon']}</span>{e(st['title'])}</a></h3>
        <p>{e(st['summary'])}</p>
        {meta_html}{also_html}
        {copy_btn}{more_link}
      </article>"""


def build_chapter(c, index):
    slug = c["slug"]
    ch_prose = PROSE["chapters"][slug]
    fr = FRONT["openers"][slug]
    op = ch_prose["opener"]

    if op.get("is_quote"):
        opener = (f'<blockquote class="lead"><p>{e(op["standfirst"])}</p>'
                  f'<cite>{e(op["attribution"])}</cite></blockquote>')
    else:
        opener = f'<p class="lead">{e(op["standfirst"])}</p>'

    clusters = {cl["key"]: cl for cl in c["clusters"]}
    groups = []
    for cl in c["clusters"]:
        sts = [s for s in c["strategies"] if s["cluster"] == cl["key"]]
        arts = "\n".join(strategy_article(s, cl, slug) for s in sts)
        accent = darken_for_white(cl["colour"])
        groups.append(f"""    <section class="cluster" style="--accent:{accent}" aria-labelledby="g-{cl['key']}">
      <h3 id="g-{cl['key']}"><span class="dot" aria-hidden="true"></span>{e(cl['label'])}</h3>
      <div class="strategy-grid">
{arts}
      </div>
    </section>""")

    prev_c = CHAPTERS[index - 1] if index > 0 else None
    next_c = CHAPTERS[index + 1] if index < len(CHAPTERS) - 1 else None
    pager = ['<nav class="pager wrap" aria-label="Chapters">']
    if prev_c:
        pager.append(f'<a href="/{prev_c["slug"]}/" rel="prev"><span>Previous chapter</span>'
                     f'{prev_c["number"]} {e(prev_c["name"])}</a>')
    else:
        pager.append('<a href="/"><span>Home</span>All six guides</a>')
    if next_c:
        pager.append(f'<a class="next" href="/{next_c["slug"]}/" rel="next"><span>Next chapter</span>'
                     f'{next_c["number"]} {e(next_c["name"])}</a>')
    else:
        pager.append('<a class="next" href="/find-a-strategy/"><span>All 144</span>Find a strategy</a>')
    pager.append("</nav>")

    thinking = ch_prose.get("thinking", {})
    practice = ch_prose.get("practice", {})
    thinking_html = practice_html = ""
    if thinking.get("standfirst"):
        thinking_html = split_section(
            "thinking", "The thinking", thinking["standfirst"],
            "".join(f"<p>{e(p)}</p>" for p in thinking["paragraphs"]),
            f"guide-page-{slug}-thinking.webp",
            f"The thinking page for {c['name']} from the guide.")
    if practice.get("standfirst"):
        practice_html = split_section(
            "practice", "In practice", practice["standfirst"],
            "".join(f"<p>{e(p)}</p>" for p in practice["paragraphs"]),
            f"guide-page-{slug}-practice.webp",
            f"The in practice page for {c['name']} from the guide.",
            img_left=True)

    out = [
        head(f'{fr["display_title"]} | {TITLE}',
             f'{c["title"]}. Every strategy from the infographic as accessible text, '
             f'with the thinking behind the guide, by Mark Anderson.',
             f"{SITE}/{slug}/", strand_jsonld(c)),
        header(slug),
        f"""<div class="hero">
  <div class="wrap">
    <p class="eyebrow">{e(fr['label'])}</p>
    <h1><span class="ch-no" aria-hidden="true">{c['number']}</span>{e(fr['display_title'])}</h1>
    {opener}
    <p class="rooted">{e(fr['rooted'])}</p>
  </div>
</div>
<main id="main">
<section id="infographic" aria-labelledby="info-h">
  <div class="wrap">
    <p class="kicker">The infographic</p>
    <h2 id="info-h">{e(c['title'])}</h2>
{infographic_figure(c)}
  </div>
</section>
<section id="strategies" aria-labelledby="strat-h">
  <div class="wrap">
    <p class="kicker">The strategies</p>
    <h2 id="strat-h">24 strategies in 5 groups</h2>
    <p class="note">Each strategy below is written exactly as it appears on the card.</p>
{"".join(groups)}
  </div>
</section>
""",
        thinking_html,
        practice_html,
        further_block(slug),
        pl_block(slug, c["name"]),
        related_block(slug),
        "".join(pager),
        "</main>\n",
        footer(),
    ]
    target = ROOT / slug
    target.mkdir(exist_ok=True)
    (target / "index.html").write_text("".join(out), encoding="utf-8")


# ---------------------------------------------------------------- finder
def build_finder():
    extra_terms = {}
    for _n in LENSES["needs"] + LENSES["inclusive"]:
        for _r in _n["strategies"]:
            extra_terms.setdefault(_r, []).append(_n["label"])
    groups = []
    total = 0
    for c in CHAPTERS:
        clusters = {cl["key"]: cl for cl in c["clusters"]}
        rows = []
        for st in c["strategies"]:
            total += 1
            cl = clusters[st["cluster"]]
            blob = " ".join(filter(None, [
                st["title"], st["summary"], st.get("tech", ""),
                st.get("informed_by", ""), cl["label"], c["name"],
            ] + extra_terms.get(f"{c['slug']}/{st['slug']}", []))).lower()
            tom = ' data-tomorrow="1"' if f"{c['slug']}/{st['slug']}" in TRY_TOMORROW else ""
            rows.append(f"""        <li class="finding" data-search="{e(blob)}"{tom}>
          <a href="{canonical_strategy_url(f"{c['slug']}/{st['slug']}")}">
            <span class="sicon" aria-hidden="true">{st['icon']}</span>
            <span class="ftext"><strong>{e(st['title'])}</strong>
              <span class="fsum">{e(st['summary'])}</span>
              <span class="fwhere">{c['number']} {e(c['name'])} · {e(cl['label'])}</span>
            </span>
          </a>
        </li>""")
        groups.append(f"""    <section class="fgroup" aria-labelledby="fg-{c['slug']}">
      <h2 id="fg-{c['slug']}"><span class="n" aria-hidden="true">{c['number']}</span>{e(c['name'])}
        <a class="open" href="/{c['slug']}/">Start reading</a></h2>
      <ul class="findings">
{"".join(rows)}
      </ul>
    </section>""")

    out = [
        head(f"Find a strategy | {TITLE}",
             "Search all 144 Pedagogy First, Technology Second strategies at once. "
             "Every result is the exact text of Mark Anderson's cards.",
             SITE + "/find-a-strategy/"),
        header("find"),
        f"""<div class="hero">
  <div class="wrap">
    <p class="eyebrow">All 144, in one place</p>
    <h1>Find a strategy</h1>
    <p class="lead">Searches the exact text of the cards, plus the classroom needs and inclusive practice lenses each strategy sits under. Results link to each strategy's own page.</p>
  </div>
</div>
<main id="main">
  <div class="wrap">
    <div class="finder">
      <label for="q">Search all 144 strategies</label>
      <div class="finder-row">
        <input type="search" id="q" autocomplete="off" spellcheck="false" disabled
               placeholder="Type a word from a strategy, a topic, or a researcher's name">
        <button type="button" id="clear" hidden>Clear</button>
      </div>
      <p id="status" role="status" aria-live="polite"></p>
      <p class="finder-more" data-companion>
        <button type="button" id="tomorrow" aria-pressed="false" disabled>Only things to try tomorrow</button>
        <span>Or start from a <a href="/classroom-needs/">classroom need</a> or the <a href="/inclusive-practice/">inclusive practice lenses</a>.</span>
      </p>
    </div>
{"".join(groups)}
    <p class="empty" id="empty" hidden>Nothing matches that.
      <button type="button" class="linkish" id="reset">Show all 144</button></p>
  </div>
</main>
<script src="/js/finder.js?v={FINDER_V}" defer></script>
""",
        footer(),
    ]
    target = ROOT / "find-a-strategy"
    target.mkdir(exist_ok=True)
    (target / "index.html").write_text("".join(out), encoding="utf-8")


# ---------------------------------------------------------------- downloads
def build_downloads():
    full_mb = (ROOT / "downloads" / "pedagogy-first-technology-second.pdf").stat().st_size / 1024 / 1024
    rows = []
    for c in CHAPTERS:
        slug = c["slug"]
        mb = pdf_size_mb(slug)
        fr = FRONT["openers"][slug]
        links = []
        if mb:
            links.append(f'<a class="btn" href="/downloads/{slug}.pdf">Download this guide as a PDF '
                         f'<span>{mb:.1f}&nbsp;MB</span></a>')
        links.append(f'<a class="btn btn-quiet" href="/assets/infographics/{slug}-download.png">'
                     f'Download the infographic as an image</a>')
        rows.append(f"""      <li style="--accent:{darken_for_white(c["clusters"][0]["colour"])}">
        <span class="card-no" aria-hidden="true">{c['number']}</span>
        <h3>{e(fr['display_title'])}</h3>
        <p class="note">{e(c['title'])}</p>
        <p class="dl-actions">{" ".join(links)}</p>
      </li>""")

    out = [
        head(f"Download resources | {TITLE}",
             "Download the full Pedagogy First, Technology Second guide and each of the "
             "six guides as its own PDF, free, with no sign-up.",
             SITE + "/download-resources/"),
        header("downloads"),
        f"""<div class="hero">
  <div class="wrap hero-grid">
    <div>
      <p class="eyebrow">The guide and the six infographics</p>
      <h1>Download resources</h1>
      <p class="lead">Free to download and share. No sign-up, no form.</p>
    </div>
    <figure class="hero-cover">
      <a href="/downloads/pedagogy-first-technology-second.pdf">
        <img src="/assets/guide-cover.webp" width="840" height="630"
             alt="The front cover of the guide. Download the full guide." decoding="async">
      </a>
    </figure>
  </div>
</div>
<main id="main">
  <section id="full" aria-labelledby="full-h">
    <div class="wrap">
      <p class="kicker">The guide</p>
      <h2 id="full-h">Download the full guide</h2>
      <p>The full 35 page guide, including all six infographics.</p>
      <p class="actions">
        <a class="btn" href="/downloads/pedagogy-first-technology-second.pdf">
          Download the full guide <span>PDF, 35 pages, {full_mb:.1f}&nbsp;MB</span></a>
      </p>
      <p class="fine">{e(FRONT["cover"]["copyright"])}</p>
    </div>
  </section>
  <section id="each" aria-labelledby="each-h">
    <div class="wrap">
      <p class="kicker">The six guides</p>
      <h2 id="each-h">Six Guides</h2>
      <p class="note">Text is selectable and searchable in every PDF.</p>
      <ul class="guide-grid dl-grid">
{"".join(rows)}
      </ul>
    </div>
  </section>
</main>
""",
        footer(),
    ]
    target = ROOT / "download-resources"
    target.mkdir(exist_ok=True)
    (target / "index.html").write_text("".join(out), encoding="utf-8")


# ---------------------------------------------------------------- extras
def build_extras():
    urls = ([f"{SITE}/", f"{SITE}/about-pedagogy-first/",
             f"{SITE}/find-a-strategy/", f"{SITE}/download-resources/",
             f"{SITE}/classroom-needs/", f"{SITE}/inclusive-practice/", f"{SITE}/try-this-tomorrow/",
             f"{SITE}/about-the-evidence/", f"{SITE}/professional-learning/", f"{SITE}/updates/"]
            + [f"{SITE}/{c['slug']}/" for c in CHAPTERS]
            + [f"{SITE}/strategies/{p['slug']}/" for p in STRATEGY_PAGES])
    body = "".join(f"<url><loc>{u}</loc></url>" for u in urls)
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>\n',
        encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    (ROOT / "CNAME").write_text("pedagogyfirst.ictevangelist.com\n", encoding="utf-8")


def main():
    build_home()
    build_about()
    for i, c in enumerate(CHAPTERS):
        build_chapter(c, i)
    build_finder()
    build_downloads()
    build_needs()
    build_inclusive()
    build_tomorrow()
    build_evidence()
    build_pl()
    build_updates()
    for _p in STRATEGY_PAGES:
        build_strategy_page(_p)
    build_extras()
    n = sum(len(c["strategies"]) for c in CHAPTERS)
    print(f"Built home, find-a-strategy, {len(CHAPTERS)} chapter pages ({n} strategies) "
          f"and 6 companion pages.")


if __name__ == "__main__":
    main()
