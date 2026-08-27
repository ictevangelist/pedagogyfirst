"""
card_generator.py
=================

Reusable image-card generator for LinkedIn posts, quick-reference cards,
and similar branded resources.

Approach: define your palette and your card content at the top of the file,
run it, and it batches out PNGs you can post directly or drop into Canva
as a background to overlay/edit.

Design defaults follow the house style:
  - Headings:  Exo 2
  - Body:      Poppins
  - Compact:   Inter
  - Palette:   Flat UI Colors (flatuicolors.com)
  - Contrast:  WCAG AA checked at runtime; warns if a pairing fails

Dependencies:  pip install pillow requests
(requests is only used to auto-fetch fonts on first run; if you'd rather
supply your own .ttf files, drop them in ./fonts and the fetch is skipped.)

Author scaffold for: Mark Anderson, ICT Evangelist
"""

from __future__ import annotations

import os
import textwrap
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# 1. PALETTE  -  pivot this block per project / per platform
# ---------------------------------------------------------------------------
# Flat UI Colors. Swap the values to re-theme an entire batch in one place.

PALETTE = {
    "turquoise":    "#1ABC9C",
    "green_sea":    "#16A085",
    "emerald":      "#2ECC71",
    "nephritis":    "#27AE60",
    "peter_river":  "#3498DB",
    "belize_hole":  "#2980B9",
    "amethyst":     "#9B59B6",
    "wisteria":     "#8E44AD",
    "wet_asphalt":  "#34495E",
    "midnight":     "#2C3E50",
    "sunflower":    "#F1C40F",
    "orange":       "#F39C12",
    "carrot":       "#E67E22",
    "pumpkin":      "#D35400",
    "alizarin":     "#E74C3C",
    "pomegranate":  "#C0392B",
    "clouds":       "#ECF0F1",
    "silver":       "#BDC3C7",
    "concrete":     "#95A5A6",
    "asbestos":     "#7F8C8D",
    "white":        "#FFFFFF",
}

# The theme each card draws from. Change these four keys to re-skin a batch.
THEME = {
    "background":  PALETTE["midnight"],     # card background
    "heading":     PALETTE["white"],        # main heading colour
    "accent":      PALETTE["turquoise"],    # eyebrow / accent / rule
    "body":        PALETTE["clouds"],       # body text colour
    "footer":      PALETTE["concrete"],     # footer / attribution
}

# ---------------------------------------------------------------------------
# 2. CARD SIZE  -  pick your platform ratio
# ---------------------------------------------------------------------------
# 16:9 landscape:         1280 x 720
# LinkedIn square:        1200 x 1200
# LinkedIn link/landscape:1200 x 627
# Portrait (mobile feed): 1080 x 1350
CARD_W, CARD_H = 1280, 720

MARGIN = 90          # inner padding
RULE_GAP = 28        # space around the accent rule

# ---------------------------------------------------------------------------
# 3. FONTS  -  auto-fetched on first run if not present in ./fonts
# ---------------------------------------------------------------------------
FONT_DIR = Path("fonts")
FONT_FILES = {
    # name: (local filename, Google Fonts raw URL)
    "exo2_bold":      ("Exo2-Bold.ttf",
        "https://github.com/google/fonts/raw/main/ofl/exo2/Exo2%5Bwght%5D.ttf"),
    "poppins":        ("Poppins-Regular.ttf",
        "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Regular.ttf"),
    "poppins_semi":   ("Poppins-SemiBold.ttf",
        "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-SemiBold.ttf"),
    "inter":          ("Inter-Regular.ttf",
        "https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bopsz%2Cwght%5D.ttf"),
}


def ensure_fonts() -> None:
    """Fetch fonts into ./fonts if they aren't already there."""
    FONT_DIR.mkdir(exist_ok=True)
    missing = [(n, u) for n, (f, u) in FONT_FILES.items()
               if not (FONT_DIR / FONT_FILES[n][0]).exists()]
    if not missing:
        return
    try:
        import requests
    except ImportError:
        raise SystemExit(
            "Fonts not found locally and 'requests' isn't installed.\n"
            "Either: pip install requests   (to auto-fetch)\n"
            "Or:     drop the .ttf files into ./fonts yourself."
        )
    for name, url in missing:
        target = FONT_DIR / FONT_FILES[name][0]
        print(f"Fetching {target.name} ...")
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        target.write_bytes(r.content)


def load(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_DIR / FONT_FILES[name][0]), size)


# ---------------------------------------------------------------------------
# 4. WCAG AA CONTRAST CHECK
# ---------------------------------------------------------------------------
def _rel_lum(hex_colour: str) -> float:
    h = hex_colour.lstrip("#")
    rgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
           for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast_ratio(fg: str, bg: str) -> float:
    l1, l2 = _rel_lum(fg), _rel_lum(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return round((hi + 0.05) / (lo + 0.05), 2)


def check_contrast(theme: dict) -> None:
    """Warn (don't fail) if any text pairing misses WCAG AA."""
    bg = theme["background"]
    for role in ("heading", "accent", "body", "footer"):
        ratio = contrast_ratio(theme[role], bg)
        # 4.5 for body text, 3.0 acceptable for large headings/accents
        threshold = 4.5 if role in ("body", "footer") else 3.0
        flag = "OK " if ratio >= threshold else "LOW"
        print(f"  [{flag}] {role:8s} vs background: {ratio}:1 "
              f"(needs {threshold}:1)")


# ---------------------------------------------------------------------------
# 5. CARD CONTENT  -  the bit you rewrite per post
# ---------------------------------------------------------------------------
@dataclass
class Card:
    eyebrow: str            # small label above the heading
    heading: str            # the big line
    body: str               # the main message
    footer: str = "Mark Anderson | ICT Evangelist © 2026 · CC BY-NC-SA 4.0"
    theme: dict = field(default_factory=lambda: THEME)


# Day numbering shows in the footer; keep it consistent across the run.
DOWNLOAD = "Download the guide: tinyurl.com/pedagogyfirst"
FOOTER_BASE = "Mark Anderson | ICT Evangelist · Pedagogy First, Technology Second"


def day_footer(n: int) -> str:
    return f"Day {n} of 7   ·   {FOOTER_BASE}"


# 7-day scheduled CTA sequence for the Pedagogy First, Technology Second guide.
# Each card is a quotable pull-out: a sharp idea from the guide, with a
# standing download line. Accent rotates through the Flat UI palette so the
# set reads as a series.
CARDS = [
    Card(
        eyebrow="DAY 1 · PEDAGOGY FIRST",
        heading="The best technology decision starts with a teaching question.",
        body=DOWNLOAD,
        footer=day_footer(1),
        theme={**THEME, "accent": PALETTE["turquoise"]},
    ),
    Card(
        eyebrow="DAY 2 · START WITH THE PROBLEM",
        heading="Name the problem before you name the tool.",
        body=DOWNLOAD,
        footer=day_footer(2),
        theme={**THEME, "accent": PALETTE["emerald"]},
    ),
    Card(
        eyebrow="DAY 3 · ECOSYSTEM THINKING",
        heading="AI is an ecosystem decision, not a tool decision.",
        body=DOWNLOAD,
        footer=day_footer(3),
        theme={**THEME, "accent": PALETTE["peter_river"]},
    ),
    Card(
        eyebrow="DAY 4 · GOVERNANCE",
        heading="A DPIA matters more than the platform you choose.",
        body=DOWNLOAD,
        footer=day_footer(4),
        theme={**THEME, "accent": PALETTE["amethyst"]},
    ),
    Card(
        eyebrow="DAY 5 · WORKLOAD AND WELLBEING",
        heading="More time for what matters is the point, not the novelty.",
        body=DOWNLOAD,
        footer=day_footer(5),
        theme={**THEME, "accent": PALETTE["sunflower"], "body": PALETTE["clouds"]},
    ),
    Card(
        eyebrow="DAY 6 · SHARED LANGUAGE",
        heading="Consistent practice beats scattered experiments.",
        body=DOWNLOAD,
        footer=day_footer(6),
        theme={**THEME, "accent": PALETTE["carrot"]},
    ),
    Card(
        eyebrow="DAY 7 · ONE HUNDRED AND FORTY-FOUR IDEAS",
        heading="One hundred and forty-four ideas. Pick one and start today.",
        body=DOWNLOAD,
        footer=day_footer(7),
        theme={**THEME, "accent": PALETTE["alizarin"]},
    ),
]


# ---------------------------------------------------------------------------
# 6. RENDERING
# ---------------------------------------------------------------------------
def _wrap(draw, text, font, max_w):
    """Greedy word-wrap to a pixel width."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _draw_block(draw, lines, font, x, y, fill, line_gap=10):
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        bbox = draw.textbbox((x, y), line, font=font)
        y = bbox[3] + line_gap
    return y


def render_card(card: Card, out_path: Path) -> None:
    theme = card.theme
    img = Image.new("RGB", (CARD_W, CARD_H), theme["background"])
    draw = ImageDraw.Draw(img)
    content_w = CARD_W - 2 * MARGIN

    f_eyebrow = load("inter", 28)
    f_heading = load("exo2_bold", 62)
    f_body = load("poppins_semi", 30)
    f_footer = load("inter", 22)

    y = MARGIN

    # eyebrow / accent label
    draw.text((MARGIN, y), card.eyebrow.upper(), font=f_eyebrow,
              fill=theme["accent"])
    y = draw.textbbox((MARGIN, y), card.eyebrow.upper(),
                      font=f_eyebrow)[3] + RULE_GAP

    # accent rule
    draw.rectangle([MARGIN, y, MARGIN + 120, y + 6], fill=theme["accent"])
    y += 6 + RULE_GAP * 2

    # heading
    heading_lines = _wrap(draw, card.heading, f_heading, content_w)
    y = _draw_block(draw, heading_lines, f_heading, MARGIN, y,
                    theme["heading"], line_gap=14)
    y += RULE_GAP

    # body
    body_lines = _wrap(draw, card.body, f_body, content_w)
    _draw_block(draw, body_lines, f_body, MARGIN, y,
                theme["body"], line_gap=12)

    # footer pinned to bottom
    fb = draw.textbbox((0, 0), card.footer, font=f_footer)
    draw.text((MARGIN, CARD_H - MARGIN - (fb[3] - fb[1])),
              card.footer, font=f_footer, fill=theme["footer"])

    img.save(out_path, "PNG")
    print(f"Saved {out_path}")


# ---------------------------------------------------------------------------
# 7. RUN
# ---------------------------------------------------------------------------
def main(out_dir: str = "output") -> None:
    ensure_fonts()
    out = Path(out_dir)
    out.mkdir(exist_ok=True)

    print("Contrast check (current THEME):")
    check_contrast(THEME)
    print()

    for i, card in enumerate(CARDS, start=1):
        render_card(card, out / f"card_{i:02d}.png")


if __name__ == "__main__":
    main()
