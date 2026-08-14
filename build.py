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

# Full chapter names are long enough that seven of them wrap the header onto a
# second row. The nav carries a short form; the full name is on the page itself,
# in the breadcrumb and in the link's title.
SHORT = {
    "retrieval-practice": "Retrieval",
    "formative-assessment": "Formative",
    "feedback": "Feedback",
    "questioning-and-discussion": "Questioning",
    "explanations-and-modelling": "Explanations",
    "metacognition-and-self-regulation": "Metacognition",
}


# ---------------------------------------------------------------- helpers
def e(s):
    """Escape for HTML text nodes."""
    return html.escape(s or "", quote=True)


def load_json(name):
    return json.loads((SRC / name).read_text(encoding="utf-8"))


def load_expansions(slug):
    """Import content/<module>.py and return its EXPANSIONS dict."""
    module_name = CHAPTER_MODULES[slug]
    path = ROOT / "content" / f"{module_name}.py"
    if not path.exists():
        return {}
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, "EXPANSIONS", {})


def asset_version():
    """Fingerprint css/js so GitHub Pages cannot serve a stale bundle."""
    blob = b"".join(
        (ROOT / p).read_bytes() for p in ("css/styles.css", "js/a11y.js", "js/nav.js")
    )
    return hashlib.md5(blob).hexdigest()[:8]


VER = asset_version()


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
def head(title, description, canonical, chapter=None, extra_ld=None):
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
        },
        "license": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
        "dateModified": REVIEWED,
    }
    if extra_ld:
        ld.update(extra_ld)

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
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/css/styles.css?v={VER}">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
<div class="skip-links">
  <a href="#main">Skip to main content</a>
  <a href="#clusters">Skip to the strategies</a>
  <a href="#site-nav">Skip to navigation</a>
</div>
<span id="top"></span>
"""


def header(chapters, current=None):
    items = []
    home_current = ' aria-current="page"' if current is None else ""
    items.append(f'<li><a href="/"{home_current}>Home</a></li>')
    for c in chapters:
        cur = ' aria-current="page"' if c["slug"] == current else ""
        short = SHORT.get(c["slug"], c["name"])
        items.append(
            f'<li><a href="/{c["slug"]}/"{cur} title="{e(c["name"])}">'
            f'<span class="nav-no">{c["number"]}</span> {e(short)}</a></li>'
        )
    return f"""<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="/">Pedagogy First. <span>Technology Second.</span></a>
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-nav">
      <svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true" focusable="false" fill="currentColor"><rect y="2" width="18" height="2" rx="1"/><rect y="8" width="18" height="2" rx="1"/><rect y="14" width="18" height="2" rx="1"/></svg>
      Chapters
    </button>
    <nav class="main-nav" id="site-nav" aria-label="Chapters">
      <ul>{"".join(items)}</ul>
    </nav>
  </div>
</header>
"""


def footer(research=None):
    extra = f'<p>{e(research)}</p>' if research else ""
    return f"""<footer class="site-footer">
  <div class="wrap">
    <img src="/assets/ict-evangelist-logo-white.png" alt="ICT Evangelist" width="200" height="34">
    <p class="motto"><span>Pedagogy first, technology second.</span> Always.</p>
    <p>An evidence informed resource by <a href="https://ictevangelist.com">Mark Anderson</a>,
       expanding the six <em>Pedagogy First, Technology Second</em> infographics and the guide that
       accompanies them. Want to bring this thinking to your school or trust?
       <a href="https://ictevangelist.com/contact">Get in touch</a>.</p>
    {extra}
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
<script src="/js/a11y.js?v={VER}" defer></script>
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


def strategy_card(s, exp, chapter_slug, colour, badge):
    """One strategy, expanded. Falls back gracefully if not yet written."""
    anchor = s["slug"]
    body = ""
    if exp:
        steps = "".join(f"<li>{e(step)}</li>" for step in exp.get("how", []))
        body = f"""
      <div class="strategy__body">
        <h4>What it is</h4>
        <p>{e(exp.get("what", ""))}</p>
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
    chips.append(
        f'<a class="permalink" href="#{anchor}" aria-label="Link to strategy {s["number"]}, {e(s["title"])}">#{s["number"]}</a>'
    )

    return f"""    <article class="strategy" id="{anchor}" style="--cluster:{colour};--cluster-badge:{badge}" aria-labelledby="{anchor}-h">
      <div class="strategy__top">
        <span class="strategy__icon" aria-hidden="true">{s["icon"]}</span>
        <span class="strategy__no">{s["number"]}</span>
        <h3 id="{anchor}-h"><a href="#{anchor}">{e(s["title"])}</a></h3>
      </div>
      <p class="strategy__summary">{e(s["summary"])}</p>{body}
      <div class="chips">{"".join(chips)}</div>
    </article>"""


def cluster_section(cluster, strategies, chapter_slug, expansions):
    cards = "\n".join(
        strategy_card(
            s, expansions.get(s["number"]), chapter_slug,
            cluster["colour"], cluster["badge"],
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


# ---------------------------------------------------------------- pages
def build_chapter(chapter, prose, chapters, index):
    slug = chapter["slug"]
    name = chapter["name"]
    number = chapter["number"]
    expansions = load_expansions(slug)
    cprose = prose["chapters"].get(slug, {})

    # group strategies by cluster, preserving the infographic's order
    clusters = []
    for c in chapter["clusters"]:
        cid = re.sub(r"[^a-z0-9]+", "-", c["label"].lower()).strip("-")
        badge = readable_on_white_text(c["colour"])
        items = [s for s in chapter["strategies"] if s["cluster"] == c["key"]]
        if items:
            clusters.append(({**c, "id": cid, "badge": badge}, items))

    nav_items = "".join(
        f'<li><a href="#{c["id"]}"><span class="dot" style="--cluster:{c["colour"]}" aria-hidden="true"></span>{e(c["label"])}</a></li>'
        for c, _ in clusters
    )
    sections = "\n".join(
        cluster_section(c, items, slug, expansions) for c, items in clusters
    )

    opener = cprose.get("opener", {})
    lead_html = ""
    quote_html = ""

    if opener.get("is_quote"):
        # This chapter opens on a quotation rather than a standfirst.
        quote_html = (
            f'<blockquote><p>{e(opener["standfirst"])}</p>'
            f'<cite>{e(opener.get("attribution", ""))}</cite></blockquote>'
        )
    else:
        if opener.get("standfirst"):
            lead_html = f'<p class="lead">{e(opener["standfirst"])}</p>'
        quote = chapter.get("quote", "")
        if quote:
            m = re.match(r"^[\u201c\"](.+?)[\u201d\"]\s*[\u2014-]\s*(.+)$", quote)
            if m:
                quote_html = (
                    f"<blockquote><p>{e(m.group(1))}</p>"
                    f"<cite>{e(m.group(2))}</cite></blockquote>"
                )
            else:
                quote_html = f'<blockquote><p>{e(quote.strip(chr(8220) + chr(8221)))}</p></blockquote>'

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

    counts = ", ".join(f"{len(items)} on {c['label'].lower()}" for c, items in clusters)
    description = (
        f"All 24 {name.lower()} strategies from the Pedagogy First, Technology Second "
        f"infographic, each expanded: what it is, why it works, how to run it and where "
        f"technology serves. {counts}."
    )

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
    </div>
  </div>
""",
        prose_section("the-thinking", "The thinking", "Why these strategies", cprose.get("thinking")),
        prose_section("in-practice", "In practice", "Where technology serves", cprose.get("practice")),
        f"""  <nav class="cluster-nav" id="clusters" aria-label="Strategy groups">
    <div class="wrap">
      <h2>The 24 strategies, grouped</h2>
      <ul>{nav_items}</ul>
    </div>
  </nav>
""",
        sections,
        f"""  <div class="wrap">
    <nav class="pager" aria-label="Chapter navigation">{"".join(pager)}</nav>
  </div>
</main>
""",
        footer(chapter.get("research")),
    ]

    target = ROOT / slug
    target.mkdir(exist_ok=True)
    (target / "index.html").write_text("".join(out), encoding="utf-8")
    return len(chapter["strategies"])


def build_index(chapters, prose):
    cards = []
    for c in chapters:
        opener = prose["chapters"].get(c["slug"], {}).get("opener", {})
        blurb = opener.get("standfirst", "")
        if opener.get("is_quote") and opener.get("attribution"):
            blurb = f'\u201c{blurb}\u201d {opener["attribution"]}'
        clusters = "".join(
            f'<li><span class="dot" style="--cluster:{cl["colour"]}" aria-hidden="true"></span>{e(cl["label"])}</li>'
            for cl in c["clusters"]
        )
        cards.append(f"""    <li class="chapter-card" data-chapter="{c['slug']}">
      <div class="chapter-card__band">
        <span class="no" aria-hidden="true">{c['number']}</span>
        <h3>{e(c['name'])}</h3>
      </div>
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
        items = block.get("paragraphs", [])[:limit]
        return "".join(f"<p>{e(p)}</p>" for p in items)

    total = sum(len(c["strategies"]) for c in chapters)
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
      <p class="lead">{e(TAGLINE)} {total} strategies to try, with or without technology.</p>
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

  <section class="prose-block" aria-labelledby="chapters-h">
    <div class="wrap">
      <p class="kicker">The six guides</p>
      <h2 id="chapters-h">Six areas the evidence keeps returning to</h2>
      <ul class="chapter-grid">
{"".join(cards)}
      </ul>
    </div>
  </section>

  <section class="prose-block" aria-labelledby="how-h">
    <div class="wrap wrap--narrow">
      <p class="kicker">How to use this</p>
      <h2 id="how-h">{e(how.get("standfirst", "How to use this guide."))}</h2>
      {paras(how)}
      <ul class="stats">
        <li><span class="n">6</span><span class="l">guides, one per area of practice</span></li>
        <li><span class="n">{total}</span><span class="l">strategies, each expanded in full</span></li>
        <li><span class="n">0</span><span class="l">tools you have to buy to start</span></li>
      </ul>
      <p><a class="btn btn--ghost" href="/{chapters[0]['slug']}/">Start with {e(chapters[0]['name'].lower())}</a></p>
    </div>
  </section>
</main>
""",
        footer(),
    ]
    (ROOT / "index.html").write_text("".join(out), encoding="utf-8")


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
        '<path d="M8 23V9h6.2c3 0 4.8 1.7 4.8 4.3 0 2.7-1.9 4.4-4.9 4.4H11V23z" fill="#FEAE00"/>'
        '<circle cx="23" cy="21" r="2.4" fill="#17abce"/></svg>\n',
        encoding="utf-8",
    )


def main():
    chapters = load_json("strategies.json")
    prose = load_json("prose.json")

    build_index(chapters, prose)
    written = 0
    missing = []
    for i, c in enumerate(chapters):
        n = build_chapter(c, prose, chapters, i)
        exps = load_expansions(c["slug"])
        gaps = [s["number"] for s in c["strategies"] if s["number"] not in exps]
        if gaps:
            missing.append((c["slug"], len(gaps)))
        written += n
        print(f"  /{c['slug']}/  {n} strategies, {n - len(gaps)} expanded")
    build_extras(chapters)

    print(f"\nBuilt {len(chapters)} chapter pages + index ({written} strategies).")
    if missing:
        print("Still to expand:")
        for slug, n in missing:
            print(f"  {slug}: {n}")
    else:
        print("All strategies expanded.")


if __name__ == "__main__":
    sys.exit(main())
