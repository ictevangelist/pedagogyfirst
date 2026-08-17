# Pedagogy First. Technology Second. — `pedagogyfirst.ictevangelist.com`

Mark Anderson's six infographics and the full guide. One page. No generator, no
build step, no JavaScript.

```
index.html                     the whole site
assets/infographics/*.webp     the six infographics
assets/fonts/*.woff2           Poppins and Exo 2, served from here not Google
downloads/*.pdf                the full guide
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
