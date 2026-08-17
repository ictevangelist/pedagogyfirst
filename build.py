#!/usr/bin/env python3
# =====================================================================
# pedagogyfirst.ictevangelist.com — the guide, web based.
#
# Eight pages: home, find-a-strategy, six chapters. Everything readable
# on them is Mark's own text, verbatim, from three verified sources:
#
#   source/strategies.json  the 144 cards, extracted from his infographics
#   source/prose.json       his chapter prose, extracted from the guide PDF
#   source/front.json       his front and back matter, transcribed from it
#
# source/verify.py proves both directions: that those files match his
# artefacts, and that the built pages contain nothing outside them except
# a short printed whitelist of navigation labels.
#
# Run:  python3 build.py && python3 source/verify.py --site
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
def head(title, description, canonical):
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
<link rel="stylesheet" href="/css/styles.css">
</head>
<body>
<a class="skip" href="#main">Skip to main content</a>
"""


def header(current=None):
    items = ['<li><a href="/"%s>Home</a></li>' % (' aria-current="page"' if current == "home" else "")]
    for c in CHAPTERS:
        cur = ' aria-current="page"' if current == c["slug"] else ""
        items.append(f'<li><a href="/{c["slug"]}/"{cur}>'
                     f'<span class="n" aria-hidden="true">{c["number"]}</span>{e(c["name"])}</a></li>')
    cur = ' aria-current="page"' if current == "find" else ""
    items.append(f'<li><a href="/find-a-strategy/"{cur}>Find a strategy</a></li>')
    return f"""<header class="site-header">
  <div class="wrap">
    <a class="brand" href="/">Pedagogy First. <span>Technology Second.</span></a>
    <nav aria-label="Site">
      <ul>{"".join(items)}</ul>
    </nav>
  </div>
</header>
"""


def footer():
    return f"""<footer class="site-footer">
  <div class="wrap">
    <p class="motto">{e(FRONT["about"]["motto"])}</p>
    <p>{e(FRONT["contact"]["line"])}
       <a href="{e(FRONT["contact"]["url"])}">ictevangelist.com/contact</a></p>
    <p class="fine">Content &copy; Mark Anderson.
       The guide is licensed CC BY-NC-ND 4.0. The infographics are licensed CC BY-NC-SA 4.0.</p>
  </div>
</footer>
</body>
</html>
"""


def prose_paras(paras, cols=True):
    body = "".join(f"<p>{e(p)}</p>" for p in paras)
    return f'<div class="{"cols" if cols else "plain"}">{body}</div>'


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
    return f"""<figure class="infographic">
      <img src="/assets/infographics/{slug}.webp" width="1600" height="1194"
           alt="{e(alt)}" decoding="async"{"" if on_chapter_page else ' loading="lazy"'}>
      <figcaption>{dl}</figcaption>
    </figure>"""


# ---------------------------------------------------------------- home
def build_home():
    f = FRONT
    why = PROSE["front"]["why"]
    idea = PROSE["front"]["idea"]
    how = PROSE["front"]["how"]
    closing = PROSE["closing"]

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

    steps = "".join(f"<li>{e(s)}</li>" for s in how["steps"])
    lead_praise = "".join(quote_fig(q, "praise praise-lead") for q in f["praise"] if q.get("lead"))
    rest_praise = "".join(quote_fig(q) for q in f["praise"] if not q.get("lead"))
    ww = f["work_with"]
    ww_lead = "".join(quote_fig(q, "praise praise-lead") for q in ww["quotes"] if q.get("lead"))
    ww_rest = "".join(quote_fig(q) for q in ww["quotes"][1:4])

    out = [
        head(TITLE + " | Mark Anderson",
             "Six evidence informed guides to teaching and learning by Mark Anderson, "
             "ICT Evangelist. All 144 strategies, the six infographics and the full guide.",
             SITE + "/"),
        header("home"),
        f"""<div class="hero">
  <div class="wrap">
    <p class="eyebrow">{e(f["cover"]["eyebrow"])}</p>
    <h1>Pedagogy First.<br>Technology Second.</h1>
    <p class="lead">{e(f["cover"]["strapline"])}</p>
    <p class="actions">
      <a class="btn btn-light" href="#guides">Start reading</a>
      <a class="btn btn-outline" href="/find-a-strategy/">Find a strategy</a>
    </p>
  </div>
</div>
<main id="main">
""",
        section("why", "Why I made these", why["standfirst"], prose_paras(why["paragraphs"])),
        section("idea", "The idea", idea["standfirst"], prose_paras(idea["paragraphs"])),
        f"""<section id="guides" aria-labelledby="guides-h">
  <div class="wrap">
    <p class="kicker">The six guides</p>
    <h2 id="guides-h">Six Guides</h2>
    <ul class="guide-grid">
{"".join(cards)}
    </ul>
  </div>
</section>
""",
        section("how", "How to use this guide", how["standfirst"],
                prose_paras(how["paragraphs"], cols=False)
                + f'<ol class="steps">{steps}</ol>'
                + f'<p class="callout">{e(how["motto"])}</p>'),
        f"""<section id="praise" class="band" aria-labelledby="praise-h">
  <div class="wrap">
    <p class="kicker">Praise</p>
    <h2 id="praise-h">{e(f["praise_heading"])}</h2>
    <div class="praise-leads">{lead_praise}</div>
    <div class="praise-grid">{rest_praise}</div>
  </div>
</section>
""",
        section("closing", "The idea behind it", closing["standfirst"],
                prose_paras(closing["paragraphs"])),
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
        f"""<section id="download" aria-labelledby="download-h">
  <div class="wrap">
    <p class="kicker">The guide</p>
    <h2 id="download-h">Download the full guide</h2>
    <p>The full 35 page guide, including all six infographics.</p>
    <p class="actions">
      <a class="btn" href="/downloads/pedagogy-first-technology-second.pdf">
        Download the full guide <span>PDF, 35 pages</span></a>
    </p>
    <p class="fine">{e(f["cover"]["copyright"])}</p>
  </div>
</section>
</main>
""",
        footer(),
    ]
    (ROOT / "index.html").write_text("".join(out), encoding="utf-8")


# ---------------------------------------------------------------- chapters
def strategy_article(st, cluster):
    accent = darken_for_white(cluster["colour"])
    meta = []
    if st.get("tech"):
        meta.append(f'<span class="mlabel">Suggested technology</span> {e(st["tech"])}')
    if st.get("informed_by"):
        meta.append(f'<span class="mlabel">Informed by</span> {e(st["informed_by"])}')
    meta_html = f'<p class="smeta">{" · ".join(meta)}</p>' if meta else ""
    return f"""      <article class="strategy" id="{st['slug']}" style="--accent:{accent}">
        <h3><a href="#{st['slug']}"><span class="sno" aria-hidden="true">{st['number']}</span>
          <span class="sicon" aria-hidden="true">{st['icon']}</span>{e(st['title'])}</a></h3>
        <p>{e(st['summary'])}</p>
        {meta_html}
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
        arts = "\n".join(strategy_article(s, cl) for s in sts)
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
        thinking_html = section(f"thinking", "The thinking", thinking["standfirst"],
                                prose_paras(thinking["paragraphs"]))
    if practice.get("standfirst"):
        practice_html = section(f"practice", "In practice", practice["standfirst"],
                                prose_paras(practice["paragraphs"]))

    out = [
        head(f'{fr["display_title"]} | {TITLE}',
             f'{c["title"]}. Every strategy from the infographic as accessible text, '
             f'with the thinking behind the guide, by Mark Anderson.',
             f"{SITE}/{slug}/"),
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
        "".join(pager),
        "</main>\n",
        footer(),
    ]
    target = ROOT / slug
    target.mkdir(exist_ok=True)
    (target / "index.html").write_text("".join(out), encoding="utf-8")


# ---------------------------------------------------------------- finder
def build_finder():
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
            ])).lower()
            rows.append(f"""        <li class="finding" data-search="{e(blob)}">
          <a href="/{c['slug']}/#{st['slug']}">
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
    <p class="lead">Searches the exact text of the cards. Results link to the strategy on its chapter page.</p>
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
    </div>
{"".join(groups)}
    <p class="empty" id="empty" hidden>Nothing matches that.
      <button type="button" class="linkish" id="reset">Show all 144</button></p>
  </div>
</main>
<script src="/js/finder.js" defer></script>
""",
        footer(),
    ]
    target = ROOT / "find-a-strategy"
    target.mkdir(exist_ok=True)
    (target / "index.html").write_text("".join(out), encoding="utf-8")


# ---------------------------------------------------------------- extras
def build_extras():
    urls = [f"{SITE}/", f"{SITE}/find-a-strategy/"] + [f"{SITE}/{c['slug']}/" for c in CHAPTERS]
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
    for i, c in enumerate(CHAPTERS):
        build_chapter(c, i)
    build_finder()
    build_extras()
    n = sum(len(c["strategies"]) for c in CHAPTERS)
    print(f"Built home, find-a-strategy and {len(CHAPTERS)} chapter pages ({n} strategies).")


if __name__ == "__main__":
    main()
