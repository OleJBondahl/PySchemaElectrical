#!/usr/bin/env python3
"""P&ID review tool — converts SVG to PNG for visual inspection.

Tries cairosvg first, falls back to Playwright (Chromium) on Windows
where the native Cairo library is often unavailable.
"""

import sys
from pathlib import Path


def svg_to_png(svg_path: str, dpi: int = 300) -> str:
    """Convert SVG to PNG, return PNG path."""
    svg = Path(svg_path)
    png = svg.with_suffix(".png")

    try:
        import cairosvg

        cairosvg.svg2png(
            url=str(svg.resolve()),
            write_to=str(png),
            dpi=dpi,
        )
    except (ImportError, OSError):
        # Fallback: Playwright with bundled Chromium
        from playwright.sync_api import sync_playwright

        # A3 landscape at approximate DPI
        width = int(297 * dpi / 96)
        height = int(210 * dpi / 96)

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": width, "height": height})
            page.goto(f"file:///{svg.resolve().as_posix()}")
            page.wait_for_timeout(2000)
            page.screenshot(path=str(png), timeout=60000)
            browser.close()

    return str(png)


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/pid_review.py <svg_file>")
        sys.exit(1)

    svg_path = sys.argv[1]
    if not Path(svg_path).exists():
        print(f"Error: {svg_path} not found")
        sys.exit(1)

    png_path = svg_to_png(svg_path)
    print(f"PNG rendered: {png_path}")


if __name__ == "__main__":
    main()
