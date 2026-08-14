#!/usr/bin/env python3
"""
Bring the written expansions closer to how Mark actually writes.

His own prose in the guide mixes: contractions through the body copy, full
forms kept for the short aphoristic lines where the rhythm carries the point.
"Feedback is not what the teacher gives. It is what the learner does with it."
would be spoiled by contracting either half.

So this contracts body prose and leaves short punchy sentences alone.

Run:  python3 source/contractions.py --apply
"""
import argparse
import pathlib
import re

ROOT = pathlib.Path(__file__).parent.parent
FILES = sorted((ROOT / "content").glob("ch0*.py"))

# Ordered: longer patterns first so "there is not" resolves before "is not".
RULES = [
    (r"\bcannot\b", "can't"),
    (r"\bcan not\b", "can't"),
    (r"\bdo not\b", "don't"),
    (r"\bdoes not\b", "doesn't"),
    (r"\bdid not\b", "didn't"),
    (r"\bis not\b", "isn't"),
    (r"\bare not\b", "aren't"),
    (r"\bwas not\b", "wasn't"),
    (r"\bwere not\b", "weren't"),
    (r"\bwill not\b", "won't"),
    (r"\bwould not\b", "wouldn't"),
    (r"\bshould not\b", "shouldn't"),
    (r"\bcould not\b", "couldn't"),
    (r"\bhas not\b", "hasn't"),
    (r"\bhave not\b", "haven't"),
    (r"\bhad not\b", "hadn't"),
    (r"\bIt is\b", "It's"),
    (r"\bit is\b", "it's"),
    (r"\bThat is\b", "That's"),
    (r"\bthat is\b", "that's"),
    (r"\bThere is\b", "There's"),
    (r"\bthere is\b", "there's"),
    (r"\bHere is\b", "Here's"),
    (r"\bhere is\b", "here's"),
    (r"\byou are\b", "you're"),
    (r"\bYou are\b", "You're"),
    (r"\bthey are\b", "they're"),
    (r"\bThey are\b", "They're"),
    (r"\bwe are\b", "we're"),
    (r"\byou will\b", "you'll"),
    (r"\bYou will\b", "You'll"),
    (r"\bthey will\b", "they'll"),
    (r"\bwe will\b", "we'll"),
    (r"\byou have\b", "you've"),
    (r"\bYou have\b", "You've"),
    (r"\bthey have\b", "they've"),
    (r"\bwe have\b", "we've"),
    (r"\byou would\b", "you'd"),
    (r"\bthey would\b", "they'd"),
    (r"\blet us\b", "let's"),
]

# Never contract "it is" when "it" is the object of a preposition: "the heart
# of it is X" must not become "the heart of it's X".
BAD_SHAPES = [
    (r"\b(of|for|to|in|on|at|with|from|about|heart of|version of) it's\b", r"\1 it is"),
]

# Leave these alone: contracting them breaks the sense or the grammar.
PROTECT = [
    r"what is being", r"what is really", r"what is actually",
    r"knowing what is", r"see what is", r"tells you what is",
    # "is not" inside a definition being drawn, where the stress is the point
    r"assessment is not", r"listening is not", r"telling is not",
    r"feedback is not what", r"forgetting is not", r"retrieval is not",
    r"marking but not", r"is not learning",
]

# A short sentence is doing rhythmic work. Mark keeps the full forms there.
SHORT_SENTENCE_WORDS = 9


def split_sentences(text):
    return re.split(r"(?<=[.!?])(\s+)", text)


def contract_sentence(sentence):
    if len(sentence.split()) <= SHORT_SENTENCE_WORDS:
        return sentence
    low = sentence.lower()
    if any(re.search(p, low) for p in PROTECT):
        return sentence
    out = sentence
    for pattern, replacement in RULES:
        out = re.sub(pattern, replacement, out)
    # Undo any contraction that landed after a preposition
    for pattern, replacement in BAD_SHAPES:
        out = re.sub(pattern, replacement, out)
    return out


def contract(text):
    parts = split_sentences(text)
    return "".join(
        part if i % 2 else contract_sentence(part) for i, part in enumerate(parts)
    )


STRING_RE = re.compile(r'("(?:[^"\\]|\\.)*")')


def process(source):
    """Rewrite only the contents of double quoted strings."""
    def repl(m):
        inner = m.group(1)[1:-1]
        if len(inner) < 25:          # keys and short flags, not prose
            return m.group(1)
        return '"' + contract(inner) + '"'
    return STRING_RE.sub(repl, source)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write the changes")
    args = ap.parse_args()

    changed_total = 0
    for path in FILES:
        original = path.read_text(encoding="utf-8")
        updated = process(original)
        changed = sum(
            1 for a, b in zip(original.split("\n"), updated.split("\n")) if a != b
        )
        changed_total += changed
        print(f"  {path.name:<36} {changed:>3} lines changed")
        if args.apply and updated != original:
            path.write_text(updated, encoding="utf-8")

    print(f"\n{changed_total} lines {'updated' if args.apply else 'would change'}")
    if not args.apply:
        print("Run with --apply to write.")


if __name__ == "__main__":
    main()
