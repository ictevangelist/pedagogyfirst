#!/usr/bin/env python3
# =====================================================================
# Static site generator for pedagogyfirst.ictevangelist.com
#
# Companion site to "Pedagogy First. Technology Second." (Mark Anderson,
# ICT Evangelist). Takes the six original infographics and the definitive
# guide, and expands all 144 strategies into six deep reference pages.
#
# Emits self-contained static HTML: no build step, no external requests.
# Run:  python3 build.py
# =====================================================================
import hashlib
import html
import importlib.util
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "source"
SITE = "https://pedagogyfirst.ictevangelist.com"
AUTHOR = "Mark Anderson"
TITLE = "Pedagogy First. Technology Second."
TAGLINE = "Six evidence informed guides to teaching and learning, and the thinking behind them."
REVIEWED = "2026-08-15"

# Put the GA4 measurement ID here, e.g. "G-XXXXXXXXXX", and analytics switch
# on behind a consent banner. Left empty, nothing loads and no banner appears.
GA_MEASUREMENT_ID = ""

CHAPTER_MODULES = {
    "retrieval-practice": "ch01_retrieval_practice",
    "formative-assessment": "ch02_formative_assessment",
    "feedback": "ch03_feedback",
    "questioning-and-discussion": "ch04_questioning_discussion",
    "explanations-and-modelling": "ch05_explanations_modelling",
    "metacognition-and-self-regulation": "ch06_metacognition",
}

WORDS = {
    "01": "One", "02": "Two", "03": "Three",
    "04": "Four", "05": "Five", "06": "Six",
}

# Where the expansion's opening paragraph mostly restates the line already on
# the infographic, it is dropped rather than printed twice. Above this overlap
# the two were saying the same thing in different words.
RESTATEMENT_THRESHOLD = 0.35

STOPWORDS = set(
    "the a an and or but of to in is it that this for with as on at be are was "
    "were not you your they their we our i so if then than which what when".split()
)


# ---------------------------------------------------------------- helpers
def e(s):
    """Escape for HTML text nodes."""
    return html.escape(s or "", quote=True)


def load_json(name):
    return json.loads((SRC / name).read_text(encoding="utf-8"))


def load_module(name):
    path = ROOT / "content" / f"{name}.py"
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_expansions(slug):
    mod = load_module(CHAPTER_MODULES[slug])
    return getattr(mod, "EXPANSIONS", {}) if mod else {}


FRONT = load_module("front_matter")

# Real pixel dimensions of the rendered infographics, so the browser reserves
# the right space and the page does not jump as they load.
IMAGE_SIZES = json.loads((SRC / "image-sizes.json").read_text(encoding="utf-8"))


def img_size(slug):
    w, h = IMAGE_SIZES.get(slug, [1600, 1194])
    return f'width="{w}" height="{h}"' 


def asset_version():
    """Fingerprint css/js so GitHub Pages cannot serve a stale bundle."""
    blob = b"".join(
        (ROOT / p).read_bytes()
        for p in ("css/styles.css", "js/a11y.js", "js/nav.js", "js/filter.js", "js/analytics.js")
        if (ROOT / p).exists()
    )
    return hashlib.md5(blob).hexdigest()[:8]


VER = asset_version()


def words_of(text):
    return {
        w for w in re.findall(r"[a-z']+", (text or "").lower())
        if w not in STOPWORDS and len(w) > 3
    }


def overlap(a, b):
    wa, wb = words_of(a), words_of(b)
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / len(wa | wb)


def reading_minutes(text):
    return max(1, round(len(text.split()) / 200))


# ---------------------------------------------------------------- colour
def _lum(hex_colour):
    h = hex_colour.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    parts = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in parts]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(fg, bg):
    a, b = _lum(fg), _lum(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def readable_on_white_text(hex_colour, target=4.6):
    """
    Darken a colour until white text on it clears WCAG AA.

    The infographic palettes were designed for dark text on pale cards. On the
    site the same hues carry white text in the number badge, and 17 of the 29
    fail at full saturation. Darkening preserves the hue, and therefore the
    link back to the infographic, while making the badge legible. The original
    colour is kept for the rules and dots, which are decorative.
    """
    h = hex_colour.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    for _ in range(60):
        candidate = f"#{r:02x}{g:02x}{b:02x}"
        if contrast("#ffffff", candidate) >= target:
            return candidate
        r, g, b = (int(v * 0.94) for v in (r, g, b))
    return "#333333"


# ---------------------------------------------------------------- chrome
def head(title, description, canonical, chapter=None, extra_ld=None, og_image=None):
    ld = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": title,
        "description": description,
        "url": canonical,
        "inLanguage": "en-GB",
        "isPartOf": {"@type": "WebSite", "name": TITLE, "url": SITE + "/"},
        "author": {
            "@type": "Person",
            "name": AUTHOR,
            "url": "https://ictevangelist.com",
            "jobTitle": "Education technology consultant, author and keynote speaker",
        },
        "license": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        "dateModified": REVIEWED,
    }
    if extra_ld:
        ld.update(extra_ld)

    image = og_image or f"{SITE}/assets/og/home.png"
    attr = f' data-chapter="{chapter}"' if chapter else ""
    return f"""<!DOCTYPE html>
<html lang="en-GB"{attr}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<meta name="author" content="{e(AUTHOR)}">
<link rel="canonical" href="{e(canonical)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(TITLE)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{e(canonical)}">
<meta property="og:image" content="{e(image)}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{e(image)}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/css/styles.css?v={VER}">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
<div class="skip-links">
  <a href="#main">Skip to main content</a>
  <a href="#clusters">Skip to the strategies</a>
</div>
<span id="top"></span>
"""


def header(chapters, current=None):
    """
    Brand plus a Chapters panel at every width.

    Six full chapter titles will not sit on one row alongside the brand, and
    shortening them loses the point of the chapter. The panel keeps the full
    titles at every screen size and gives one predictable behaviour to test.
    """
    home_current = ' aria-current="page"' if current is None else ""
    items = [
        f'<li><a href="/"{home_current}>'
        f'<span class="nav-no" aria-hidden="true">&#9632;</span>'
        f'<span class="nav-title">All six guides</span></a></li>'
    ]
    for c in chapters:
        cur = ' aria-current="page"' if c["slug"] == current else ""
        items.append(
            f'<li><a href="/{c["slug"]}/"{cur}>'
            f'<span class="nav-no" aria-hidden="true">{c["number"]}</span>'
            f'<span class="nav-title">{e(c["name"])}</span></a></li>'
        )
    return f"""<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="/">Pedagogy First. <span>Technology Second.</span></a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">
      <svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true" focusable="false" fill="currentColor"><rect y="2" width="18" height="2" rx="1"/><rect y="8" width="18" height="2" rx="1"/><rect y="14" width="18" height="2" rx="1"/></svg>
      <span>Chapters</span>
    </button>
    <nav class="main-nav" id="site-nav" aria-label="Chapters" hidden>
      <ul>{"".join(items)}</ul>
    </nav>
  </div>
</header>
"""


def cta_band(context="site"):
    """
    One clear next step, in the same place on every page.

    The site is free to read and the point of it is the conversation that
    follows, so the ask is explicit rather than buried in the footer.
    """
    return f"""<section class="cta-band" aria-labelledby="cta-h">
  <div class="wrap">
    <div class="cta-band__inner">
      <div>
        <h2 id="cta-h">Want this thinking in your school?</h2>
        <p>I run keynotes, INSET and workshops on pedagogy, AI and digital strategy,
           and I work with schools and trusts over time rather than one day and gone.
           Tell me where your team is and I'll tell you honestly whether I can help.</p>
      </div>
      <div class="cta-band__actions">
        <a class="btn btn--light" href="https://ictevangelist.com/contact"
           data-cta="{context}">Talk to me about it</a>
        <a class="btn btn--outline" href="/#downloads">Download the guide first</a>
      </div>
    </div>
  </div>
</section>"""


def work_with_mark():
    w = FRONT.WORK_WITH_MARK
    quotes = "".join(
        f'<figure class="mini-quote"><blockquote><p>{e(q["quote"])}</p></blockquote>'
        f'<figcaption>{e(q["name"])}<span>{e(q["role"])}</span></figcaption></figure>'
        for q in w["quotes"]
    )
    return f"""<section class="prose-block band" id="work-with-mark" aria-labelledby="wwm-h">
  <div class="wrap">
    <p class="kicker">Work with Mark</p>
    <h2 id="wwm-h">{e(w["standfirst"])}</h2>
    <p class="standfirst">{e(w["body"])}</p>
    <p><a class="btn" href="https://ictevangelist.com/contact">Get in touch</a></p>
    <div class="mini-quotes">{quotes}</div>
  </div>
</section>"""


def analytics_tag():
    if not GA_MEASUREMENT_ID:
        return "<!-- analytics off: set GA_MEASUREMENT_ID in build.py -->"
    return (
        f'<script src="/js/analytics.js?v={VER}" '
        f'data-ga="{GA_MEASUREMENT_ID}" defer></script>'
    )


def footer(research=None):
    extra = f'<p class="footer-research">{e(research)}</p>' if research else ""
    return f"""<footer class="site-footer">
  <div class="wrap">
    <img src="/assets/ict-evangelist-logo-white.png" alt="ICT Evangelist" width="200" height="34">
    <p class="motto"><span>Pedagogy first, technology second.</span> Always.</p>
    <p>An evidence informed resource by <a href="https://ictevangelist.com">Mark Anderson</a>,
       expanding the six <em>Pedagogy First, Technology Second</em> infographics and the guide that
       accompanies them.</p>
    {extra}
    <p><a href="/#downloads">Download the guide and the infographics</a> &middot;
       <a href="https://ictevangelist.com/contact">Work with Mark</a> &middot;
       <a href="https://ictevangelist.com">ictevangelist.com</a></p>
    <p>Licensed <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/" rel="license">CC BY-NC-SA 4.0</a>.
       Last reviewed {REVIEWED}.</p>
    <p class="licence" aria-label="Creative Commons Attribution NonCommercial ShareAlike 4.0">
      <span aria-hidden="true">CC</span><span aria-hidden="true">BY</span><span aria-hidden="true">NC</span><span aria-hidden="true">SA</span>
    </p>
  </div>
</footer>
<a class="to-top" href="#top" aria-label="Back to top of page">
  <svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true" focusable="false" fill="currentColor"><path d="M7 2l5 6H9v4H5V8H2z"/></svg>
  Back to top
</a>
<script src="/js/nav.js?v={VER}" defer></script>
<script src="/js/filter.js?v={VER}" defer></script>
<script src="/js/a11y.js?v={VER}" defer></script>
{analytics_tag()}
</body>
</html>
"""


# ---------------------------------------------------------------- pieces
def prose_section(section_id, kicker, heading, block, callout_last=True):
    """Render one of Mark's prose spreads."""
    if not block or not block.get("standfirst"):
        return ""
    paras = list(block.get("paragraphs", []))
    tail = ""
    if callout_last and paras:
        tail = f'<div class="callout"><p>{e(paras.pop())}</p></div>'
    body = "".join(f"<p>{e(p)}</p>" for p in paras)
    return f"""<section class="prose-block" id="{section_id}" aria-labelledby="{section_id}-h">
  <div class="wrap wrap--narrow">
    <p class="kicker">{e(kicker)}</p>
    <h2 id="{section_id}-h">{e(heading)}</h2>
    <p class="standfirst">{e(block["standfirst"])}</p>
    {body}
    {tail}
  </div>
</section>"""


def strategy_card(s, exp, colour, badge, alsoin):
    """
    One strategy, expanded.

    The line from the infographic is Mark's own and opens the card. The
    expansion's own opening paragraph is only printed where it adds a picture
    of the strategy in the classroom rather than restating that line.
    """
    anchor = s["slug"]
    body = ""
    if exp:
        lead_extra = ""
        if overlap(s["summary"], exp.get("what", "")) < RESTATEMENT_THRESHOLD:
            lead_extra = f'<p class="strategy__picture">{e(exp["what"])}</p>'
        steps = "".join(f"<li>{e(step)}</li>" for step in exp.get("how", []))
        body = f"""{lead_extra}
      <div class="strategy__body">
        <h4>Why it works</h4>
        <p>{e(exp.get("why", ""))}</p>
        <h4>How to run it</h4>
        <ol>{steps}</ol>
        <h4>Where technology serves</h4>
        <p>{e(exp.get("tech", ""))}</p>
      </div>
      <div class="strategy__watch"><p><strong>Watch for:</strong> {e(exp.get("watch", ""))}</p></div>"""

    chips = []
    if s.get("tech"):
        chips.append(f'<span class="chip"><b>Tech</b>{e(s["tech"])}</span>')
    if s.get("informed_by"):
        chips.append(f'<span class="chip"><b>Informed by</b>{e(s["informed_by"])}</span>')
    if alsoin:
        links = ", ".join(
            f'<a href="/{a["slug"]}/#{a["anchor"]}">{e(a["chapter"])}</a>' for a in alsoin
        )
        chips.append(f'<span class="chip chip--also"><b>Also in</b>{links}</span>')
    chips.append(
        f'<a class="permalink" href="#{anchor}" '
        f'aria-label="Link to strategy {s["number"]}, {e(s["title"])}">#{s["number"]}</a>'
    )

    search_blob = " ".join(
        filter(None, [
            s["title"], s["summary"], s.get("tech", ""), s.get("informed_by", ""),
            s.get("category", ""),
            (exp or {}).get("why", ""), (exp or {}).get("what", ""),
            " ".join((exp or {}).get("how", [])), (exp or {}).get("tech", ""),
        ])
    ).lower()

    return f"""    <article class="strategy" id="{anchor}" style="--cluster:{colour};--cluster-badge:{badge}"
             aria-labelledby="{anchor}-h" data-search="{e(search_blob)}">
      <div class="strategy__top">
        <span class="strategy__icon" aria-hidden="true">{s["icon"]}</span>
        <span class="strategy__no">{s["number"]}</span>
        <h3 id="{anchor}-h"><a href="#{anchor}">{e(s["title"])}</a></h3>
      </div>
      <p class="strategy__summary">{e(s["summary"])}</p>{body}
      <div class="chips">{"".join(chips)}</div>
    </article>"""


def cluster_section(cluster, strategies, expansions, crossrefs):
    cards = "\n".join(
        strategy_card(
            s, expansions.get(s["number"]), cluster["colour"], cluster["badge"],
            crossrefs.get(s["title"].lower(), []),
        )
        for s in strategies
    )
    n = len(strategies)
    return f"""<section class="cluster" id="{cluster['id']}" style="--cluster:{cluster['colour']}" aria-labelledby="{cluster['id']}-h">
  <div class="wrap">
    <div class="cluster-head">
      <h2 id="{cluster['id']}-h">{e(cluster['label'])}</h2>
      <span class="count">{n} {"strategy" if n == 1 else "strategies"}</span>
    </div>
    <div class="strategies">
{cards}
    </div>
  </div>
</section>"""


def infographic_figure(chapter):
    slug = chapter["slug"]
    return f"""<section class="prose-block" id="the-infographic" aria-labelledby="info-h">
  <div class="wrap">
    <p class="kicker">The original</p>
    <h2 id="info-h">The infographic this chapter expands</h2>
    <figure class="infographic-figure">
      <a href="/assets/infographics/{slug}-download.png">
        <img src="/assets/infographics/{slug}.webp" {img_size(slug)}
             alt="The {e(chapter['name'])} infographic: 24 strategies laid out in colour coded groups, each with a title, a short description, a suggested technology and the researchers behind it. Every strategy is written out in full further down this page."
             loading="lazy" decoding="async">
      </a>
      <figcaption>
        All 24 on one page.
        <a href="/assets/infographics/{slug}-download.png" download>Download the full size image</a>
        for printing or sharing, or read every strategy expanded below.
      </figcaption>
    </figure>
  </div>
</section>"""


# ---------------------------------------------------------------- pages
def build_chapter(chapter, prose, chapters, index, crossrefs):
    slug = chapter["slug"]
    name = chapter["name"]
    number = chapter["number"]
    expansions = load_expansions(slug)
    cprose = prose["chapters"].get(slug, {})

    clusters = []
    for c in chapter["clusters"]:
        cid = re.sub(r"[^a-z0-9]+", "-", c["label"].lower()).strip("-")
        items = [s for s in chapter["strategies"] if s["cluster"] == c["key"]]
        if items:
            clusters.append((
                {**c, "id": cid, "badge": readable_on_white_text(c["colour"])},
                items,
            ))

    nav_items = "".join(
        f'<li><a href="#{c["id"]}"><span class="dot" style="--cluster:{c["colour"]}" aria-hidden="true"></span>'
        f'{e(c["label"])} <span class="n">{len(items)}</span></a></li>'
        for c, items in clusters
    )
    sections = "\n".join(
        cluster_section(c, items, expansions, crossrefs) for c, items in clusters
    )

    opener = cprose.get("opener", {})
    lead_html = ""
    quote_html = ""
    if opener.get("is_quote"):
        quote_html = (
            f'<blockquote><p>{e(opener["standfirst"])}</p>'
            f'<cite>{e(opener.get("attribution", ""))}</cite></blockquote>'
        )
    else:
        if opener.get("standfirst"):
            lead_html = f'<p class="lead">{e(opener["standfirst"])}</p>'
        quote = chapter.get("quote", "")
        if quote:
            m = re.match(r"^[“\"](.+?)[”\"]\s*[—-]\s*(.+)$", quote)
            if m:
                quote_html = (
                    f"<blockquote><p>{e(m.group(1))}</p>"
                    f"<cite>{e(m.group(2))}</cite></blockquote>"
                )
            else:
                quote_html = (
                    f'<blockquote><p>{e(quote.strip(chr(8220) + chr(8221)))}</p></blockquote>'
                )

    prev_c = chapters[index - 1] if index > 0 else None
    next_c = chapters[index + 1] if index < len(chapters) - 1 else None
    pager = []
    if prev_c:
        pager.append(
            f'<a href="/{prev_c["slug"]}/" rel="prev"><span>Previous chapter</span>'
            f'<strong>{prev_c["number"]}. {e(prev_c["name"])}</strong></a>'
        )
    else:
        pager.append('<a href="/"><span>Back to</span><strong>All six guides</strong></a>')
    if next_c:
        pager.append(
            f'<a href="/{next_c["slug"]}/" rel="next"><span>Next chapter</span>'
            f'<strong>{next_c["number"]}. {e(next_c["name"])}</strong></a>'
        )
    else:
        pager.append(
            '<a href="/#downloads"><span>Read all six?</span>'
            '<strong>Download the guide</strong></a>'
        )

    counts = ", ".join(f"{len(items)} on {c['label'].lower()}" for c, items in clusters)
    description = (
        f"All 24 {name.lower()} strategies from the Pedagogy First, Technology Second "
        f"infographic, each expanded: why it works, how to run it and where technology "
        f"serves. {counts}."
    )

    all_text = " ".join(
        [opener.get("standfirst", "")]
        + [
            p for b in (cprose.get("thinking"), cprose.get("practice")) if b
            for p in [b.get("standfirst", "")] + b.get("paragraphs", [])
        ]
        + [s["summary"] + " " + s["title"] for s in chapter["strategies"]]
        + [
            " ".join(filter(None, [
                x.get("what", ""), x.get("why", ""), x.get("tech", ""), x.get("watch", ""),
                " ".join(x.get("how", [])),
            ]))
            for x in expansions.values()
        ]
    )
    minutes = reading_minutes(all_text)

    itemlist = {
        "hasPart": {
            "@type": "ItemList",
            "numberOfItems": len(chapter["strategies"]),
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": int(s["number"]),
                    "name": s["title"],
                    "url": f"{SITE}/{slug}/#{s['slug']}",
                }
                for s in chapter["strategies"]
            ],
        }
    }

    out = [
        head(
            f"{name}: 24 ways to embed it | {TITLE}",
            description,
            f"{SITE}/{slug}/",
            chapter=slug,
            extra_ld=itemlist,
            og_image=f"{SITE}/assets/og/{slug}.png",
        ),
        header(chapters, current=slug),
        f"""<main id="main">
  <nav class="crumbs wrap" aria-label="Breadcrumb">
    <ol>
      <li><a href="/">All six guides</a></li>
      <li aria-current="page">{number}. {e(name)}</li>
    </ol>
  </nav>

  <div class="hero">
    <div class="wrap">
      <p class="eyebrow">Chapter {WORDS[number]} of six</p>
      <span class="chapter-no" aria-hidden="true">{number}</span>
      <h1>{e(name)}</h1>
      {lead_html}
      <p class="meta">{e(chapter.get("scholars") or chapter.get("research", ""))}</p>
      {quote_html}
      <p class="hero-facts">
        <span>24 strategies</span><span>{len(clusters)} groups</span><span>about {minutes} minutes to read</span>
      </p>
    </div>
  </div>
""",
        infographic_figure(chapter),
        prose_section("the-thinking", "The thinking", "Why these strategies", cprose.get("thinking")),
        prose_section("in-practice", "In practice", "Where technology serves", cprose.get("practice")),
        f"""  <nav class="cluster-nav" id="clusters" aria-label="Strategy groups and search">
    <div class="wrap">
      <div class="cluster-nav__inner">
        <div class="cluster-nav__groups">
          <h2>The 24 strategies, grouped</h2>
          <ul>{nav_items}</ul>
        </div>
        <div class="filter">
          <label for="strategyFilter">Find a strategy</label>
          <input type="search" id="strategyFilter" autocomplete="off" spellcheck="false"
                 placeholder="quizzing, wait time, Rosenshine&hellip;" disabled>
          <button type="button" class="filter__clear" id="filterClear" hidden>Clear</button>
          <p class="filter__status" id="filterStatus" role="status" aria-live="polite"></p>
        </div>
      </div>
    </div>
  </nav>
""",
        sections,
        f"""  <div class="wrap">
    <p class="filter__empty" id="filterEmpty" hidden>Nothing here matches that.
       <button type="button" class="linkbtn" id="filterReset">Show all 24 strategies</button></p>
    <nav class="pager" aria-label="Chapter navigation">{"".join(pager)}</nav>
  </div>
</main>
""",
        cta_band(context=slug),
        footer(chapter.get("research")),
    ]

    target = ROOT / slug
    target.mkdir(exist_ok=True)
    (target / "index.html").write_text("".join(out), encoding="utf-8")

    restated = [
        s["number"] for s in chapter["strategies"]
        if s["number"] in expansions
        and overlap(s["summary"], expansions[s["number"]].get("what", "")) >= RESTATEMENT_THRESHOLD
    ]
    gaps = [s["number"] for s in chapter["strategies"] if s["number"] not in expansions]
    return len(chapter["strategies"]), len(gaps), len(restated)


def build_index(chapters, prose):
    cards = []
    for c in chapters:
        opener = prose["chapters"].get(c["slug"], {}).get("opener", {})
        blurb = opener.get("standfirst", "")
        if opener.get("is_quote") and opener.get("attribution"):
            blurb = f'“{blurb}” {opener["attribution"]}'
        clusters = "".join(
            f'<li><span class="dot" style="--cluster:{cl["colour"]}" aria-hidden="true"></span>{e(cl["label"])}</li>'
            for cl in c["clusters"]
        )
        cards.append(f"""    <li class="chapter-card" data-chapter="{c['slug']}">
      <a class="chapter-card__band" href="/{c['slug']}/">
        <span class="no" aria-hidden="true">{c['number']}</span>
        <h3>{e(c['name'])}</h3>
      </a>
      <div class="chapter-card__body">
        <p>{e(blurb)}</p>
        <ul class="chapter-card__clusters">{clusters}</ul>
        <a class="btn" href="/{c['slug']}/">All 24 strategies<span class="sr-only"> for {e(c['name'])}</span></a>
      </div>
    </li>""")

    front = prose["front"]
    why = front.get("why", {})
    idea = front.get("idea", {})
    how = front.get("how", {})

    def paras(block, limit=None):
        return "".join(f"<p>{e(p)}</p>" for p in block.get("paragraphs", [])[:limit])

    total = sum(len(c["strategies"]) for c in chapters)

    lead_praise = "".join(
        f'<figure class="praise praise--lead"><blockquote><p>{e(q["quote"])}</p></blockquote>'
        f'<figcaption>{e(q["name"])}<span>{e(q["role"])}</span></figcaption></figure>'
        for q in FRONT.PRAISE if q.get("lead")
    )
    rest_praise = "".join(
        f'<figure class="praise"><blockquote><p>{e(q["quote"])}</p></blockquote>'
        f'<figcaption>{e(q["name"])}<span>{e(q["role"])}</span></figcaption></figure>'
        for q in FRONT.PRAISE if not q.get("lead")
    )

    downloads = "".join(
        f"""        <li>
          <a href="/assets/infographics/{c['slug']}-download.png" download>
            <img src="/assets/infographics/{c['slug']}.webp" alt="" {img_size(c['slug'])} loading="lazy" decoding="async">
            <span><strong>{c['number']}. {e(c['name'])}</strong>Infographic, PNG</span>
          </a>
        </li>"""
        for c in chapters
    )

    about = FRONT.ABOUT
    description = (
        "One hundred and forty four evidence informed teaching strategies, with or without "
        "technology, across retrieval practice, formative assessment, feedback, questioning "
        "and discussion, explanations and modelling, and metacognition. Each one expanded in full."
    )

    out = [
        head(f"{TITLE} | {AUTHOR}", description, f"{SITE}/"),
        header(chapters, current=None),
        f"""<main id="main">
  <div class="hero">
    <div class="wrap">
      <p class="eyebrow">An evidence informed resource by {e(AUTHOR)}</p>
      <h1>Pedagogy First.<br>Technology Second.</h1>
      <p class="lead">{e(TAGLINE)} {total} strategies to try, with or without technology, every one expanded in full.</p>
      <p class="hero-actions">
        <a class="btn btn--light" href="#chapters">Start reading</a>
        <a class="btn btn--outline" href="#downloads">Download the guide</a>
      </p>
      <blockquote>
        <p>{e(idea.get("standfirst", "Technology should enhance teaching and learning, not dictate teaching and learning."))}</p>
        <cite>{e(AUTHOR)}</cite>
      </blockquote>
    </div>
  </div>

  <section class="prose-block" aria-labelledby="why-h">
    <div class="wrap wrap--narrow">
      <p class="kicker">Why I made these</p>
      <h2 id="why-h">{e(why.get("standfirst", "Why I made these."))}</h2>
      {paras(why)}
    </div>
  </section>

  <section class="prose-block" id="chapters" aria-labelledby="chapters-h">
    <div class="wrap">
      <p class="kicker">The six guides</p>
      <h2 id="chapters-h">Six areas the evidence keeps returning to</h2>
      <ul class="chapter-grid">
{"".join(cards)}
      </ul>
    </div>
  </section>

  <section class="prose-block band" id="praise" aria-labelledby="praise-h">
    <div class="wrap">
      <p class="kicker">Praise</p>
      <h2 id="praise-h">What others say about this guide</h2>
      <div class="praise-lead">{lead_praise}</div>
      <div class="praise-grid">{rest_praise}</div>
    </div>
  </section>

  <section class="prose-block" id="how" aria-labelledby="how-h">
    <div class="wrap wrap--narrow">
      <p class="kicker">How to use this</p>
      <h2 id="how-h">{e(how.get("standfirst", "How to use this guide."))}</h2>
      {paras(how)}
      <ul class="stats">
        <li><span class="n">6</span><span class="l">guides, one per area of practice</span></li>
        <li><span class="n">{total}</span><span class="l">strategies, each expanded in full</span></li>
        <li><span class="n">1</span><span class="l">to pick and try tomorrow morning</span></li>
      </ul>
    </div>
  </section>

  <section class="prose-block" id="downloads" aria-labelledby="dl-h">
    <div class="wrap">
      <p class="kicker">Take it with you</p>
      <h2 id="dl-h">Download the guide and the infographics</h2>
      <p class="standfirst">Free to use and share under Creative Commons, for anything
         other than commercial use.</p>
      <p><a class="btn btn--big" href="/downloads/pedagogy-first-technology-second.pdf" download>
        Download the full guide <span class="btn__meta">PDF, 35 pages</span></a></p>
      <ul class="download-grid">
{downloads}
      </ul>
    </div>
  </section>

  <section class="prose-block" id="about" aria-labelledby="about-h">
    <div class="wrap wrap--narrow">
      <p class="kicker">About Mark</p>
      <h2 id="about-h">{e(about["standfirst"])}</h2>
      {"".join(f"<p>{e(p)}</p>" for p in about["paragraphs"])}
      <div class="callout"><p>Pedagogy first. Technology second. Always.</p></div>
    </div>
  </section>
</main>
""",
        work_with_mark(),
        footer(),
    ]
    (ROOT / "index.html").write_text("".join(out), encoding="utf-8")


def build_crossrefs(chapters):
    """Strategies whose title appears in more than one chapter."""
    seen = {}
    for c in chapters:
        for s in c["strategies"]:
            seen.setdefault(s["title"].lower(), []).append(
                {"slug": c["slug"], "chapter": c["name"], "anchor": s["slug"]}
            )
    return {t: places for t, places in seen.items() if len(places) > 1}


def build_extras(chapters):
    (ROOT / "CNAME").write_text("pedagogyfirst.ictevangelist.com\n", encoding="utf-8")
    (ROOT / ".nojekyll").write_text("", encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8"
    )
    urls = [f"{SITE}/"] + [f"{SITE}/{c['slug']}/" for c in chapters]
    body = "".join(
        f"<url><loc>{u}</loc><lastmod>{REVIEWED}</lastmod></url>" for u in urls
    )
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{body}</urlset>\n',
        encoding="utf-8",
    )
    (ROOT / "favicon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
        '<rect width="32" height="32" rx="6" fill="#16202b"/>'
        '<path d="M9 24V8h6.4c3.2 0 5.2 1.9 5.2 4.8s-2 4.9-5.3 4.9H12V24z" fill="#FEAE00"/>'
        '<circle cx="23.5" cy="22.5" r="2.6" fill="#17abce"/></svg>\n',
        encoding="utf-8",
    )


def main():
    chapters = load_json("strategies.json")
    prose = load_json("prose.json")
    crossrefs_all = build_crossrefs(chapters)

    build_index(chapters, prose)
    written = total_gaps = total_restated = 0
    for i, c in enumerate(chapters):
        refs = {
            t: [p for p in places if p["slug"] != c["slug"]]
            for t, places in crossrefs_all.items()
        }
        n, gaps, restated = build_chapter(c, prose, chapters, i, refs)
        written += n
        total_gaps += gaps
        total_restated += restated
        print(
            f"  /{c['slug']}/  {n} strategies, {n - gaps} expanded, "
            f"{restated} restating openers folded away"
        )
    build_extras(chapters)

    print(f"\nBuilt {len(chapters)} chapter pages + index ({written} strategies).")
    print(f"{len(crossrefs_all)} strategy titles appear in more than one chapter, now cross-linked.")
    print(f"{total_restated} openers that restated the infographic line were folded into it.")
    if total_gaps:
        print(f"WARNING: {total_gaps} strategies still have no expansion.")


if __name__ == "__main__":
    sys.exit(main())
