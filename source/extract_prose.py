#!/usr/bin/env python3
"""
Pull Mark's own prose out of the definitive guide PDF: the front matter and,
for each chapter, "Why these strategies" (The Thinking) and "Where technology
serves" (In Practice). Writes prose.json.

Headings in the PDF are letter-spaced (C H A P T E R  O N E), body copy is not,
so the un-spacing pass only touches lines that are clearly spaced out.

Run:  python3 source/extract_prose.py
"""
import json
import pathlib
import re

import pypdf

PDF = pathlib.Path(__file__).parent / "pdf" / "definitive-guide.pdf"
OUT = pathlib.Path(__file__).parent / "prose.json"

# 0-indexed pages in the definitive guide
FRONT = {
    "why": 4,        # Why I made these
    "idea": 5,       # The idea
    "how": 7,        # How to use this guide
}
CHAPTERS = [
    ("retrieval-practice", 8, 10, 11),
    ("formative-assessment", 12, 14, 15),
    ("feedback", 16, 18, 19),
    ("questioning-and-discussion", 20, 22, 23),
    ("explanations-and-modelling", 24, 26, 27),
    ("metacognition-and-self-regulation", 28, 30, 31),
]
CLOSING = 32  # The idea behind it

# Running heads/feet, matched against a spaces-stripped form of the line so
# that letter-spaced settings ("P E D A G O G Y  F I R S T .") are caught too.
FOOTER_KEYS = ("PEDAGOGYFIRST", "ICTEVANGELIST", "CHAPTER", "DRAFT", "ROOTEDINTHEWORK")


def is_furniture(line):
    key = re.sub(r"[^A-Za-z]", "", line).upper()
    return any(key.startswith(k) for k in FOOTER_KEYS)


def unspace(line):
    """Letter-spaced heading -> normal heading; leave prose alone."""
    tokens = [t for t in line.split(" ") if t]
    if len(tokens) > 3 and all(len(t) == 1 for t in tokens):
        # word breaks are runs of 2+ spaces; letter breaks are single spaces
        words = re.split(r"\s{2,}", line.strip())
        return " ".join(w.replace(" ", "") for w in words)
    return line


def opener_of(lines, name, number):
    """Chapter opener: number, one or two title lines, then the standfirst."""
    keep = [l for l in lines if not is_furniture(l)]
    # drop the big chapter numeral
    keep = [l for l in keep if l.strip() != number]
    # drop title lines: short lines built only from words in the chapter name
    name_words = set(re.findall(r"[A-Za-z]+", name.lower()))
    while keep:
        words = set(re.findall(r"[A-Za-z]+", keep[0].lower()))
        if words and words <= name_words and len(keep[0]) < 40:
            keep.pop(0)
            continue
        break
    if not keep:
        return {"standfirst": "", "attribution": "", "is_quote": False}
    # rejoin wrapped lines into sentences
    paras, cur = [], ""
    for line in keep:
        cur = f"{cur} {line}".strip()
        if line.endswith((".", "?", "!", "\u201d", '"')):
            paras.append(cur)
            cur = ""
    if cur:
        paras.append(cur)
    text = " ".join(paras).strip()
    is_quote = text.startswith("\u201c")
    attribution = ""
    if is_quote:
        m = re.match(r"^\u201c(.+?)\u201d\s*(.*)$", text, re.S)
        if m:
            text, attribution = m.group(1).strip(), m.group(2).strip()
    return {
        "standfirst": normalise(text),
        "attribution": normalise(attribution),
        "is_quote": is_quote,
    }


LIGATURES = {
    "\ufb00": "ff", "\ufb01": "fi", "\ufb02": "fl",
    "\ufb03": "ffi", "\ufb04": "ffl", "\ufb05": "st", "\ufb06": "st",
}


def normalise(text):
    """Undo PDF typesetting artefacts: ligatures and broken hyphenation."""
    for lig, plain in LIGATURES.items():
        text = text.replace(lig, plain)
    # "two- minute" is a line-break hyphen that survived the rejoin
    text = re.sub(r"(\w)-\s+(\w)", r"\1-\2", text)
    return re.sub(r"\s{2,}", " ", text).strip()


def page_lines(reader, index):
    raw = reader.pages[index].extract_text() or ""
    out = []
    for line in raw.split("\n"):
        line = unspace(line.strip())
        if line:
            out.append(line)
    return out


def body_of(lines):
    """Drop running heads/footers, split into a standfirst and paragraphs."""
    keep = [l for l in lines if not is_furniture(l)]
    # the all-caps kicker (WHY THESE STRATEGIES) is the first shouty line
    while keep and keep[0].isupper():
        keep.pop(0)
    # rejoin: a line ending without terminal punctuation continues the sentence
    paras, cur = [], ""
    for line in keep:
        cur = f"{cur} {line}".strip()
        if line.endswith((".", "?", "!", "”", '"')):
            paras.append(cur)
            cur = ""
    if cur:
        paras.append(cur)
    if not paras:
        return {"standfirst": "", "paragraphs": []}
    paras = [normalise(x) for x in paras]
    return {"standfirst": paras[0], "paragraphs": paras[1:]}


def main():
    reader = pypdf.PdfReader(str(PDF))
    out = {"front": {}, "chapters": {}, "closing": {}}

    for key, idx in FRONT.items():
        out["front"][key] = body_of(page_lines(reader, idx))

    names = {
        "retrieval-practice": ("Retrieval Practice Memory", "01"),
        "formative-assessment": ("Formative Assessment", "02"),
        "feedback": ("Feedback", "03"),
        "questioning-and-discussion": ("Questioning Discussion", "04"),
        "explanations-and-modelling": ("Explanations Modelling", "05"),
        "metacognition-and-self-regulation": ("Metacognition Self Regulation", "06"),
    }
    for slug, opener, thinking, practice in CHAPTERS:
        nm, no = names[slug]
        out["chapters"][slug] = {
            "opener": opener_of(page_lines(reader, opener), nm, no),
            "thinking": body_of(page_lines(reader, thinking)),
            "practice": body_of(page_lines(reader, practice)),
        }

    out["closing"] = body_of(page_lines(reader, CLOSING))

    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    for slug, data in out["chapters"].items():
        t = data["thinking"]
        p = data["practice"]
        print(
            f"{slug:<34} thinking {len(t['paragraphs'])+1:>2} paras   "
            f"practice {len(p['paragraphs'])+1:>2} paras"
        )
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()
