# Pedagogy First. Technology Second. — `pedagogyfirst.ictevangelist.com`

Mark Anderson's six infographics and the full guide. One page. No generator, no
build step, no JavaScript.

```
index.html                     the whole site
assets/infographics/*.webp     the six infographics
assets/fonts/*.woff2           Poppins and Exo 2, served from here not Google
downloads/*.pdf                the full guide, plus each infographic as its
                               own PDF, split out of the guide's pages
source/                        Mark's originals: the six infographics as HTML,
                               the guide and mini guide as PDF
_archive/                      the previous version of the site, see below
```

## Why this is one page

The previous version expanded all 144 strategies into six long chapters. That
prose was written from model memory and never checked against the research it
described: 52 of the 144 expansions stated what a study found, and none of
those statements were verified at source. It was published under Mark's name,
so it came down.

Everything now on the site is Mark's own work: his artwork, his guide, his
words. Nothing on this page paraphrases or interprets a paper.

`_archive/` holds the old generator and content so nothing is lost. It is not
built or served. `git tag pre-reset-2026-08-17` marks the last commit before
the reset.

## The six single-guide PDFs

Pages 10, 14, 18, 22, 26 and 30 of the guide are the six infographics. They are
live text, not images, so `source/split-guide.py` lifts each page out into its
own PDF, keeping the text layer intact, and sets `/Lang` and a document title.

They are **not tagged PDFs**. The guide has no `StructTreeRoot`, so there are no
heading, list or reading-order tags and no alt text on the icons. The text is
selectable, searchable and readable aloud, and the extraction order is sensible,
but assistive technology gets no structure. Two known artefacts, both inherited
from the guide: the letter-spaced running heads read out letter by letter, and
the coloured word in each title sits in a separate text run so the H1 extracts as
"24 Ways to Embed Effective  in Your Classroom".

If tagged masters exist, drop them into `downloads/` over the top and they win.

## Rules for anything added from here

1. If it makes a claim about what research found, the source is read first and
   cited, or the claim is not made.
2. If it cannot be verified, it does not go on the site.
3. Mark's own writing needs no verification. Anything else does.

## Deployment

GitHub Pages from `main`, root folder. `CNAME` holds the custom domain. DNS is a
`CNAME` record for `pedagogyfirst` pointing at `ictevangelist.github.io`.

## Licence

Content © Mark Anderson, licensed
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
