#!/usr/bin/env python3
"""
Turn the 2x infographic renders into web assets.

Each infographic becomes:
  <slug>.webp        display version, 1600px wide, for the page
  <slug>.png         download version, 2400px wide, for sharing and printing

The raw 2800px renders are 17MB in total, which is far too heavy to put on
a page. This keeps a crisp download while making the on-page version light.

Run:  python3 source/optimise-images.py
"""
import pathlib

from PIL import Image

OUT = pathlib.Path(__file__).parent.parent / "assets" / "infographics"
DISPLAY_W = 1600
DOWNLOAD_W = 2400


def main():
    total_before = total_after = 0
    for src in sorted(OUT.glob("*.png")):
        if src.stem.endswith("-download"):
            continue
        before = src.stat().st_size
        total_before += before

        img = Image.open(src).convert("RGB")

        # download version: PNG, quantised to keep the file sensible
        dl = img.resize(
            (DOWNLOAD_W, round(img.height * DOWNLOAD_W / img.width)), Image.LANCZOS
        )
        dl_path = OUT / f"{src.stem}-download.png"
        dl.quantize(colors=256, method=Image.MEDIANCUT).save(dl_path, optimize=True)

        # display version: WebP
        disp = img.resize(
            (DISPLAY_W, round(img.height * DISPLAY_W / img.width)), Image.LANCZOS
        )
        webp_path = OUT / f"{src.stem}.webp"
        disp.save(webp_path, "WEBP", quality=82, method=6)

        src.unlink()  # the raw render is not shipped

        after = webp_path.stat().st_size + dl_path.stat().st_size
        total_after += after
        print(
            f"{src.stem:<34} webp {webp_path.stat().st_size // 1024:>5} KB   "
            f"png {dl_path.stat().st_size // 1024:>5} KB   (was {before // 1024} KB)"
        )
    print(f"\nTotal {total_before // 1024} KB -> {total_after // 1024} KB")


if __name__ == "__main__":
    main()
