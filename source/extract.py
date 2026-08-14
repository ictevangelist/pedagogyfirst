#!/usr/bin/env python3
"""
Extract the 144 strategies (6 infographics x 24) plus each infographic's
palette and metadata from the original HTML infographics into strategies.json.

Run:  python3 source/extract.py
"""
import html
import json
import pathlib
import re

SRC = pathlib.Path(__file__).parent / "infographics"
OUT = pathlib.Path(__file__).parent / "strategies.json"

CHAPTERS = [
    ("01-retrieval-practice", "retrieval-practice", "Retrieval Practice", "01"),
    ("02-formative-assessment", "formative-assessment", "Formative Assessment", "02"),
    ("03-feedback", "feedback", "Feedback", "03"),
    ("04-questioning-discussion", "questioning-and-discussion", "Questioning &amp; Discussion", "04"),
    ("05-explanations-modelling", "explanations-and-modelling", "Explanations &amp; Modelling", "05"),
    ("06-metacognition", "metacognition-and-self-regulation", "Metacognition &amp; Self-Regulation", "06"),
]


def txt(raw):
    """HTML fragment -> clean text."""
    s = re.sub(r"<[^>]+>", "", raw)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def slugify(s):
    s = html.unescape(s).lower()
    s = s.replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def grab(pattern, source, flags=re.S):
    m = re.search(pattern, source, flags)
    return m.group(1) if m else ""


def parse(path):
    doc = path.read_text(encoding="utf-8")

    # --- legend: cluster key -> label, in document order ---
    clusters = []
    for cls, label in re.findall(
        r'<div class="legend-dot ([a-z]+)"></div>\s*(.*?)</div>', doc, re.S
    ):
        clusters.append({"key": cls, "label": txt(label)})

    # --- cluster accent colours from .legend-dot.<key> { background: #xxx } ---
    colours = {}
    for key, hexval in re.findall(
        r"\.legend-dot\.([a-z]+)\s*\{\s*background:\s*(#[0-9a-fA-F]{3,8})", doc
    ):
        colours[key] = hexval
    for c in clusters:
        c["colour"] = colours.get(c["key"], "#666666")

    # --- header meta ---
    h1 = grab(r"<h1>(.*?)</h1>", doc)
    scholars = grab(r'<p class="scholars">(.*?)</p>', doc)
    if not scholars:
        # some files fold the scholar list into the subtitle or a bare <p>
        scholars = grab(
            r'<p style="font-size:10px;[^"]*">(.*?)</p>', doc
        ) or grab(r'<div class="footer-research">(.*?)</div>', doc)
    quote = grab(r'<p class="quote">(.*?)</p>', doc)
    subtitle = grab(r'<p class="subtitle">(.*?)</p>', doc)
    research = grab(r'<div class="footer-research">(.*?)</div>', doc)

    # --- page palette ---
    body_bg = grab(r"body\s*\{[^}]*background:\s*([^;]+);", doc)
    panel_bg = grab(r"\.infographic\s*\{[^}]*background:\s*([^;]+);", doc)
    accent = grab(r"\.footer-author\s*\{[^}]*color:\s*(#[0-9a-fA-F]{3,8})", doc)

    # --- the 24 cards ---
    cards = []
    for block in re.findall(r'<div class="card cat-([a-z]+)"[^>]*>(.*?)\n\s*</div>\s*\n\s*</div>', doc, re.S):
        cluster_key, body = block
        number = txt(grab(r'<span class="card-number">(.*?)</span>', body))
        icon = txt(grab(r'<div class="card-icon">(.*?)</div>', body))
        category = txt(grab(r'<div class="card-category">(.*?)</div>', body))
        title = txt(grab(r'<div class="card-title">(.*?)</div>', body))
        desc = txt(grab(r'<div class="card-desc">(.*?)</div>', body))
        chips = re.findall(
            r'<span class="meta-chip"><span class="meta-label">(.*?)</span>(.*?)</span>', body, re.S
        )
        tech = informed = ""
        for label, value in chips:
            label = txt(label).lower()
            if label.startswith("tech"):
                tech = txt(value)
            elif label.startswith("informed"):
                informed = txt(value)
        if not (number and title):
            continue
        cards.append(
            {
                "number": number,
                "slug": f"{number}-{slugify(title)}",
                "icon": icon,
                "cluster": cluster_key,
                "category": category,
                "title": title,
                "summary": desc,
                "tech": tech,
                "informed_by": informed,
            }
        )

    cards.sort(key=lambda c: int(c["number"]))
    return {
        "title": txt(h1),
        "subtitle": txt(subtitle),
        "scholars": txt(scholars),
        "quote": txt(quote),
        "research": txt(research),
        "palette": {
            "body_bg": body_bg.strip(),
            "panel_bg": panel_bg.strip(),
            "accent": accent or "#FEAE00",
        },
        "clusters": clusters,
        "strategies": cards,
    }


def main():
    out = []
    for filestem, slug, name, number in CHAPTERS:
        data = parse(SRC / f"{filestem}.html")
        data.update({"slug": slug, "name": html.unescape(name), "number": number})
        out.append(data)
        counts = {}
        for s in data["strategies"]:
            counts[s["cluster"]] = counts.get(s["cluster"], 0) + 1
        print(
            f"{number} {data['name']:<34} {len(data['strategies']):>3} strategies  "
            f"clusters: {', '.join(f'{k}={v}' for k, v in counts.items())}"
        )
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    total = sum(len(c["strategies"]) for c in out)
    print(f"\nWrote {OUT} ({total} strategies)")


if __name__ == "__main__":
    main()
