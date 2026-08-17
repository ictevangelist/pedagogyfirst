#!/usr/bin/env python3
"""
Prove that every content string on the site is Mark's, verbatim.

Two passes:

1. TRANSCRIPTION. Every string in source/front.json and source/prose.json must
   appear in the definitive guide PDF, and every strategy field in
   source/strategies.json must appear in the original infographic HTML. Both
   sides are normalised (whitespace squashed to nothing, quotes and dashes and
   ligatures unified) because the PDF letter-spaces its display text.

2. SITE. Every piece of visible text in the built pages must come from one of
   those verified sources, or be on the NAVIGATION whitelist printed at the end
   of this file. The whitelist is the complete inventory of words on the site
   that Mark did not write, and it should stay short and boring.

Run:  python3 source/verify.py          (pass 1)
      python3 source/verify.py --site   (both passes)
"""
import html as html_mod
import json
import pathlib
import re
import sys
import unicodedata

ROOT = pathlib.Path(__file__).parent.parent
SRC = ROOT / "source"


def squash(text):
    """Normalise for comparison: no whitespace, unified punctuation."""
    t = unicodedata.normalize("NFKC", text)
    t = (t.replace("‘", "'").replace("’", "'")
          .replace("“", '"').replace("”", '"')
          .replace("–", "-").replace("—", "-")
          .replace("ﬁ", "fi").replace("ﬂ", "fl")
          .replace("­", "").replace("‑", "-")
          .replace(" ", " "))
    return re.sub(r"\s+", "", t).lower()


def pdf_corpus():
    from pypdf import PdfReader
    r = PdfReader(str(SRC / "pdf" / "definitive-guide.pdf"))
    return squash(" ".join((p.extract_text() or "") for p in r.pages))


def infographic_corpus():
    out = []
    for f in sorted((SRC / "infographics").glob("*.html")):
        s = f.read_text(encoding="utf-8", errors="replace")
        s = re.sub(r"<style.*?</style>|<script.*?</script>", " ", s, flags=re.S)
        out.append(html_mod.unescape(re.sub(r"<[^>]+>", " ", s)))
    return squash(" ".join(out))


def walk_strings(node, path="", skip_keys=("_note", "url", "slug", "icon",
                                          "colour", "key", "is_quote", "lead",
                                          "palette")):
    if isinstance(node, dict):
        for k, v in node.items():
            if k in skip_keys or k.startswith("_"):
                continue
            yield from walk_strings(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk_strings(v, f"{path}[{i}]")
    elif isinstance(node, str) and len(node.strip()) > 2:
        yield path, node


def check_transcription():
    pdf = pdf_corpus()
    info = infographic_corpus()
    fails = 0

    print("Pass 1: transcription against Mark's artefacts")
    for name, corpus in (("front.json", pdf), ("prose.json", pdf)):
        data = json.loads((SRC / name).read_text())
        n = bad = 0
        for path, s in walk_strings(data):
            n += 1
            sq = squash(s)
            # A short role line may carry commas the PDF renders as line
            # breaks; every comma-separated part must still be found verbatim.
            ok = sq in corpus or (
                len(s) < 130 and "," in s
                and all(squash(part) in corpus for part in s.split(",") if part.strip())
            )
            if not ok:
                bad += 1
                print(f"  FAIL {name}{path}: {s[:80]!r}")
        print(f"  {'ok  ' if not bad else 'FAIL'} {name}: {n - bad}/{n} strings found in the guide PDF")
        fails += bad

    data = json.loads((SRC / "strategies.json").read_text())
    n = bad = 0
    for c in data:
        for st in c["strategies"]:
            for field in ("title", "summary", "tech", "informed_by"):
                s = st.get(field, "")
                if not s:
                    continue
                n += 1
                if squash(s) not in info:
                    bad += 1
                    print(f"  FAIL strategies {c['slug']} #{st['number']} {field}: {s[:70]!r}")
        for cl in c["clusters"]:
            n += 1
            if squash(cl["label"]) not in info:
                bad += 1
                print(f"  FAIL cluster label {cl['label']!r}")
    print(f"  {'ok  ' if not bad else 'FAIL'} strategies.json: {n - bad}/{n} card strings found in the infographic HTML")
    return fails + bad


# ----------------------------------------------------------------------
# Every string on the site that Mark did NOT write. This list is the whole
# of it: navigation, labels, link text, image descriptions. If a string is
# not his and not here, pass 2 fails the build.
NAVIGATION = [
    "Pedagogy First. Technology Second.",
    "Skip to main content",
    "Menu", "Close",
    "Home", "Find a strategy", "All six guides",
    "Guide", "Guides", "The six guides",
    "Start reading", "On this page",
    "Why I made these", "The idea", "How to use this guide",
    "Praise", "About Mark", "Work with Mark", "Contents",
    "The infographic", "The thinking", "In practice", "The strategies",
    "Download the full guide", "PDF, 35 pages", "PDF",
    "pages",
    "Download this guide as a PDF", "Download the infographic as an image",
    "Text is selectable and searchable",
    "Previous chapter", "Next chapter", "Back to top",
    "Search all 144 strategies",
    "All 144, in one place",
    "Download resources", "The guide and the six infographics",
    "Free to download and share. No sign-up, no form.",
    "The guide", "The six guides", "Six Guides",
    "Text is selectable and searchable in every PDF.",
    "The front cover of the guide. Download resources.",
    "The front cover of the guide. Download the full guide.",
    "Type a word from a strategy, a topic, or a researcher's name",
    "Clear", "Show all 144", "Showing all 144 strategies",
    "Nothing matches that.",
    "strategies", "strategy", "for",
    "Suggested technology", "Informed by",
    "Chapter", "of", "in",
    "24 strategies in 5 groups",
    "By", "Licensed", "Content",
    "Mark Anderson", "ICT Evangelist", "ictevangelist.com",
    "CC BY-NC-ND 4.0", "CC BY-NC-SA 4.0",
    "The full 35 page guide, including all six infographics.",
    "Each strategy below is written exactly as it appears on the card.",
    "Searches the exact text of the cards. Results link to the strategy on its chapter page.",
    # image descriptions
    "infographic. The same 24 strategies as a one page poster. Every strategy on it is written out as text below.",
    "The", "and",
    # footer
    "Content © Mark Anderson.",
    "The guide is licensed CC BY-NC-ND 4.0. The infographics are licensed CC BY-NC-SA 4.0.",
]

# The six image descriptions, one per chapter, generated so the list stays
# in step with the chapter names.
for _c in json.loads((SRC / "strategies.json").read_text()):
    NAVIGATION.append(
        f"The {_c['name']} infographic. The same 24 strategies as a one page poster. "
        f"Every strategy on it is written out as text below."
    )


def visible_text(html):
    html = re.sub(r"<style.*?</style>|<script.*?</script>|<!--.*?-->", " ", html, flags=re.S)
    # capture alt text as visible-to-AT text
    alts = re.findall(r'alt="([^"]*)"', html)
    text = html_mod.unescape(re.sub(r"<[^>]+>", "\n", html))
    return text + "\n" + "\n".join(html_mod.unescape(a) for a in alts)


def check_site():
    pdf = pdf_corpus()
    info = infographic_corpus()
    nav = {squash(s) for s in NAVIGATION}
    pages = sorted(ROOT.glob("*/index.html")) + [ROOT / "index.html"]
    pages = [p for p in pages if "source" not in p.parts and "_archive" not in p.parts]

    print("\nPass 2: every visible string on the built site")
    total_fails = 0
    for page in pages:
        raw = page.read_text(encoding="utf-8")
        fails = []
        for line in visible_text(raw).split("\n"):
            line = line.strip()
            if len(line) < 3:
                continue
            sq = squash(line)
            if not sq:
                continue
            if sq in nav or sq in pdf or sq in info:
                continue
            # composites: a line may be several whitelisted fragments
            parts = [squash(p) for p in re.split(r"[·|•,]|\s[-–]\s|[()]|\d+(?:\.\d+)?\s?(?:MB|KB)|\bGuide 0\d\b|\b\d+\b", line)]
            if all((not p) or p in nav or p in pdf or p in info for p in parts):
                continue
            fails.append(line)
        label = "/" + (page.parent.name + "/" if page.parent != ROOT else "")
        if fails:
            total_fails += len(fails)
            print(f"  FAIL {label}  {len(fails)} unverified string(s):")
            for f in fails[:10]:
                print(f"       {f[:100]!r}")
        else:
            print(f"  ok   {label}")
    return total_fails


if __name__ == "__main__":
    bad = check_transcription()
    if "--site" in sys.argv:
        bad += check_site()
    print()
    if bad:
        print(f"{bad} PROBLEM(S). Fix the transcription or the whitelist before shipping.")
        sys.exit(1)
    print("Everything checks out: every content string is Mark's, verbatim.")
