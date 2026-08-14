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
    "at the end of the day", "when it comes to", "more than just", "not just a",
    "isn't just", "is not just", "the reality is", "the truth is",
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


if __name__ == "__main__":
    main()
