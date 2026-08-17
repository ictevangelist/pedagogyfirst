#!/usr/bin/env python3
"""
Split the six infographic pages out of the guide into standalone PDFs.

The infographics are pages 10, 14, 18, 22, 26 and 30 of the definitive guide,
and they are live text rather than placed images, so lifting the page out keeps
the text layer: selectable, searchable and readable by a screen reader. A
rendered PNG throws all of that away, which is why this exists.

The guide is not a tagged PDF (no StructTreeRoot), so neither are these. What
this script can add, it adds: a document language and a real title.

Run:  python3 source/split-guide.py
"""
import pathlib

from pypdf import PdfReader, PdfWriter
from pypdf.generic import BooleanObject, DictionaryObject, NameObject, TextStringObject

ROOT = pathlib.Path(__file__).parent.parent
GUIDE = ROOT / "source" / "pdf" / "definitive-guide.pdf"
OUT = ROOT / "downloads"

PAGES = [
    (10, "retrieval-practice", "24 Ways to Embed Retrieval Practice in Your Classroom"),
    (14, "formative-assessment", "24 Ways to Embed Formative Assessment in Your Classroom"),
    (18, "feedback", "24 Ways to Embed Effective Feedback in Your Classroom"),
    (22, "questioning-and-discussion", "24 Ways to Embed Effective Questioning & Discussion in Your Classroom"),
    (26, "explanations-and-modelling", "24 Ways to Embed Effective Explanations & Modelling in Your Classroom"),
    (30, "metacognition-and-self-regulation", "24 Ways to Embed Metacognition & Self-Regulation in Your Classroom"),
]


def main():
    src = PdfReader(str(GUIDE))
    for pageno, slug, title in PAGES:
        writer = PdfWriter()
        writer.add_page(src.pages[pageno - 1])
        writer.add_metadata({
            "/Title": title,
            "/Author": "Mark Anderson",
            "/Subject": "Pedagogy First. Technology Second.",
            "/Creator": "Mark Anderson, ICT Evangelist",
        })
        root = writer._root_object
        root[NameObject("/Lang")] = TextStringObject("en-GB")
        root[NameObject("/ViewerPreferences")] = DictionaryObject(
            {NameObject("/DisplayDocTitle"): BooleanObject(True)}
        )
        target = OUT / f"{slug}.pdf"
        with open(target, "wb") as fh:
            writer.write(fh)

        words = len((PdfReader(str(target)).pages[0].extract_text() or "").split())
        size = target.stat().st_size / 1024
        print(f"{target.name:40} {size:6.0f} KB  {words} words of live text")


if __name__ == "__main__":
    main()
