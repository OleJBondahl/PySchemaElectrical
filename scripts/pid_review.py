#!/usr/bin/env python3
"""P&ID review tool — converts SVG to PNG for visual inspection."""

import sys
from pathlib import Path


def svg_to_png(svg_path: str, dpi: int = 300) -> str:
    """Convert SVG to PNG, return PNG path."""
    import cairosvg

    svg = Path(svg_path)
    png = svg.with_suffix(".png")
    cairosvg.svg2png(
        url=str(svg.resolve()),
        write_to=str(png),
        dpi=dpi,
    )
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
