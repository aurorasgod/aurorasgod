"""Render the profile's original signal graphic with Pillow.

Usage: python tools/render_header.py --font-dir C:/Windows/Fonts
Pass a directory containing arial.ttf, arialbd.ttf and consola.ttf.
"""

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def render(font_dir: Path, output: Path) -> None:
    scale = 2
    width, height = 1600, 480
    image = Image.new("RGB", (width * scale, height * scale), "#131416")
    draw = ImageDraw.Draw(image)

    def line(points, color, stroke=1):
        draw.line([(int(x * scale), int(y * scale)) for x, y in points],
                  fill=color, width=stroke * scale)

    def text(position, value, size, color, family="arial.ttf"):
        font = ImageFont.truetype(str(font_dir / family), size * scale)
        draw.text(tuple(int(v * scale) for v in position), value,
                  font=font, fill=color, anchor="lt")

    red, white, muted = "#F05257", "#F6F5F2", "#B6B9BE"
    line([(64, 61), (112, 61)], red, 5)
    text((132, 50), "@aurorasgod", 24, muted, "consola.ttf")
    text((59, 113), "Laplace.", 150, white, "arialbd.ttf")
    text((67, 291), "From signals to systems.", 40, white)
    text((68, 402), "ROBOTICS  /  CONTROL  /  CODE", 23, muted, "consola.ttf")

    # A damped signal and its envelope echo the Laplace transform.
    left, top, right, bottom = 1016, 82, 1520, 365
    baseline = (top + bottom) / 2
    for x in range(left, right + 1, 42):
        line([(x, top), (x, bottom)], "#25272B")
    for y in range(top, bottom + 1, 47):
        line([(left, y), (right, y)], "#25272B")
    line([(left, baseline), (right, baseline)], "#676B72")
    line([(left, top), (left, bottom)], "#676B72")
    curve = []
    envelope = []
    for i in range(right - left + 1):
        t = i / (right - left)
        amplitude = 116 * math.exp(-2.65 * t)
        curve.append((left + i, baseline - amplitude * math.cos(5.8 * math.pi * t)))
        envelope.append((left + i, baseline - amplitude))
    for start in range(0, len(envelope), 14):
        line(envelope[start:start + 6], "#8A8D93")
    line(curve, red, 4)
    text((1016, 402), "f(t)  ->  F(s)", 23, muted, "consola.ttf")
    text((1494, 375), "t", 19, muted, "consola.ttf")
    line([(0, height - 3), (width, height - 3)], red, 6)

    output.parent.mkdir(parents=True, exist_ok=True)
    image.resize((width, height), Image.Resampling.LANCZOS).save(output, optimize=True)
    print(f"Rendered {output} ({width}x{height})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).resolve().parents[1] / "assets/header.png")
    args = parser.parse_args()
    render(args.font_dir, args.output)
