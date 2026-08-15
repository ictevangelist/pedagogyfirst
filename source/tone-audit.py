#!/usr/bin/env python3
"""
Tone audit for the written expansions.

Checks three things Mark cares about:
  1. AI slop: the stock phrases and hedges that give machine writing away
  2. Contractions: he writes with them, so the site should too
  3. Formality markers: passive constructions and stiff connectives

Run:  python3 source/tone-audit.py
"""
import collections
import importlib.util
import pathlib
import re

ROOT = pathlib.Path(__file__).parent.parent
CHAPTERS = [
    "ch01_retrieval_practice", "ch02_formative_assessment", "ch03_feedback",
    "ch04_questioning_discussion", "ch05_explanations_modelling", "ch06_metacognition",
]

# Phrases Mark has explicitly banned, plus the wider family of AI tells.
SLOP = [
    "earns its place", "this one matters", "quietly", "delve", "tapestry",
    "testament to", "it's worth noting", "it is worth noting", "in today's",
    "landscape of", "navigate the", "unlock", "harness", "leverage",
    "game changer", "game-changer", "seamless", "robust solution", "deep dive",
    "at the end of the day", "when it comes to", "more than just a",
    "not just another", "isn't just a", "is not just a", "it's not just",
    "the reality is", "the truth is",
    "let's be honest", "make no mistake", "crucially", "importantly",
    "significantly", "notably", "ultimately", "fundamentally", "essentially",
    "arguably", "vital", "crucial", "pivotal", "paramount", "myriad",
    "plethora", "realm", "sphere", "underscore", "underscores", "moreover",
    "furthermore", "however it", "that said", "in conclusion", "in summary",
    "dive into", "supercharge", "elevate your", "transform your",
    "power of", "journey", "empower", "cutting edge", "cutting-edge",
    "best practice", "best-in-class", "holistic", "synergy", "streamline",
    "actionable insights", "key takeaway", "takeaways", "resonate",
    "compelling", "meaningful ways", "truly", "simply put", "in essence",
    # Mark's own list, added after he spotted these in the first pass
    "what matters", "what really matters", "matters most", "the key is",
    "the point is not", "here's the thing", "the bottom line", "at its core",
    "more than ever", "in a world where", "the beauty of", "the magic",
    "it's not about", "it's about", "think of it as", "put simply",
]

# Contraction opportunities: the expanded form, and what it should become.
CONTRACTIONS = {
    r"\bdo not\b": "don't", r"\bdoes not\b": "doesn't", r"\bdid not\b": "didn't",
    r"\bis not\b": "isn't", r"\bare not\b": "aren't", r"\bwas not\b": "wasn't",
    r"\bwere not\b": "weren't", r"\bcannot\b": "can't", r"\bcan not\b": "can't",
    r"\bwill not\b": "won't", r"\bwould not\b": "wouldn't",
    r"\bshould not\b": "shouldn't", r"\bcould not\b": "couldn't",
    r"\bhas not\b": "hasn't", r"\bhave not\b": "haven't", r"\bhad not\b": "hadn't",
    r"\bit is\b": "it's", r"\bthat is\b": "that's", r"\bthere is\b": "there's",
    r"\bhere is\b": "here's", r"\bwhat is\b": "what's", r"\bwho is\b": "who's",
    r"\byou are\b": "you're", r"\bthey are\b": "they're", r"\bwe are\b": "we're",
    r"\byou will\b": "you'll", r"\bthey will\b": "they'll", r"\bwe will\b": "we'll",
    r"\byou have\b": "you've", r"\bthey have\b": "they've", r"\bwe have\b": "we've",
    r"\byou would\b": "you'd", r"\blet us\b": "let's",
}

FORMAL = {
    r"\butilise\b": "use", r"\butilize\b": "use", r"\bcommence\b": "start",
    r"\bprior to\b": "before", r"\bsubsequent to\b": "after",
    r"\bin order to\b": "to", r"\bwith regard to\b": "about",
    r"\bin the event that\b": "if", r"\bat this juncture\b": "now",
    r"\bnumerous\b": "many", r"\bendeavour\b": "try", r"\bascertain\b": "find out",
}


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "content" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.EXPANSIONS


def all_strings():
    """Every piece of written prose, with a label saying where it came from."""
    for name in CHAPTERS:
        for number, entry in load(name).items():
            for field, value in entry.items():
                if isinstance(value, str):
                    yield name, number, field, value
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        yield name, number, f"{field}[{i}]", item


def main():
    items = list(all_strings())
    words = sum(len(v.split()) for *_, v in items)

    print(f"{len(items)} passages, {words:,} words\n")

    print("AI slop")
    hits = collections.Counter()
    where = collections.defaultdict(list)
    for name, no, field, text in items:
        low = text.lower()
        for phrase in SLOP:
            if re.search(r"\b" + re.escape(phrase) + r"\b", low):
                hits[phrase] += 1
                where[phrase].append(f"{name[:4]} {no} {field}")
    if hits:
        for phrase, n in hits.most_common():
            print(f"  {n:>3}  {phrase}")
            for w in where[phrase][:3]:
                print(f"         {w}")
    else:
        print("  none found")

    print("\nContractions")
    expanded = collections.Counter()
    for name, no, field, text in items:
        for pattern in CONTRACTIONS:
            found = re.findall(pattern, text, re.I)
            if found:
                expanded[pattern.strip(r"\b")] += len(found)
    used = sum(len(re.findall(r"\w+'(?:s|t|re|ll|ve|d|m)\b", v)) for *_, v in items)
    total_expanded = sum(expanded.values())
    print(f"  contractions used:            {used}")
    print(f"  expanded forms that could be: {total_expanded}")
    if total_expanded:
        rate = used / (used + total_expanded) * 100
        print(f"  contraction rate:             {rate:.0f}%")
        for form, n in expanded.most_common(12):
            print(f"    {n:>3}  {form}")

    print("\nStiff or formal wording")
    formal_hits = collections.Counter()
    for name, no, field, text in items:
        for pattern, better in FORMAL.items():
            if re.search(pattern, text, re.I):
                formal_hits[f"{pattern.strip(chr(92) + 'b')} -> {better}"] += 1
    if formal_hits:
        for k, n in formal_hits.most_common():
            print(f"  {n:>3}  {k}")
    else:
        print("  none found")

    print("\nSentence length")
    sentences = []
    for *_, text in items:
        sentences += [s for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    lengths = [len(s.split()) for s in sentences]
    long_ones = [s for s in sentences if len(s.split()) > 40]
    print(f"  {len(sentences)} sentences, mean {sum(lengths)/len(lengths):.1f} words")
    print(f"  over 40 words: {len(long_ones)}")
    for s in long_ones[:5]:
        print(f"    {len(s.split())}w: {s[:110]}...")


def audit_built_pages():
    """
    The same checks again, but against what a reader actually sees.

    The chapter modules are only part of the site. Headings, standfirsts, the
    home page, the principles, the CPD sessions and the calls to action all
    live elsewhere, and slop in any of them is still slop.

    Three kinds of text are separated out rather than silently ignored:

      quoted      other people's words, in blockquotes. Not ours to edit, ever.
      guide       Mark's published guide prose, extracted from the PDF. His
                  call whether to change it, not a build script's.
      infographic the strategy titles and summaries as printed on the original
                  six. Changing them would break the link back to the artwork.

    Everything else is site copy that was written here, and that is held to the
    full standard.
    """
    import html as _html

    def strip(pattern, text):
        return re.sub(pattern, " ", text, flags=re.S | re.I)

    def visible(raw):
        raw = strip(r"<script.*?</script>", raw)
        raw = strip(r"<style.*?</style>", raw)
        raw = strip(r"<!--.*?-->", raw)
        return re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", raw)))

    QUOTED = r"<(blockquote|figure class=\"(?:praise|mini-quote)[^\"]*\").*?</\1>"
    SOURCED = r"<([a-z][a-z0-9]*)[^>]*data-source=\"[^\"]*\".*?</\1>"

    pages = sorted(ROOT.glob("*/index.html")) + [ROOT / "index.html"]
    pages = [p for p in pages if p.exists() and "source" not in p.parts]
    print("\n" + "=" * 62)
    print(f"The built site: {len(pages)} pages")

    problems = 0
    words = 0
    inherited = collections.Counter()

    for page in pages:
        raw = page.read_text(encoding="utf-8")
        label = "/" + (page.parent.name + "/" if page.parent != ROOT else "")

        # Everything on the page, and then everything we actually wrote.
        all_text = visible(raw)
        words += len(all_text.split())
        ours = visible(strip(SOURCED, strip(QUOTED, raw)))
        theirs = all_text.lower()

        hits = [ph for ph in SLOP if ph in ours.lower()]
        # Mark's hard rule: no em dashes, anywhere, ever, whoever wrote it.
        dashes = all_text.count("\u2014") + all_text.count("\u2013")
        for ph in SLOP:
            if ph in theirs and ph not in ours.lower():
                inherited[ph] += 1

        if hits or dashes:
            problems += len(hits) + dashes
            print(f"  FAIL {label}")
            for ph in hits:
                print(f'         slop in our own copy: "{ph}"')
            if dashes:
                print(f"         {dashes} em or en dash(es)")
        else:
            print(f"  ok   {label}")

    print(f"\n  {words:,} words of visible copy across the site")
    print("  " + ("our own copy is clean" if not problems else f"{problems} PROBLEM(S)"))

    if inherited:
        print("\n  Present only in quoted, published or infographic text, so left alone:")
        for ph, n in inherited.most_common():
            print(f'    {n:>2} page(s)  "{ph}"')


if __name__ == "__main__":
    main()
    audit_built_pages()
