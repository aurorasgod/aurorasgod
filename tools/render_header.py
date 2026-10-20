"""Compose a Persona 5 fan banner from the credited official Joker artwork.

Usage: python tools/render_header.py --font-dir C:/Windows/Fonts
Requires Pillow and the Windows fonts Impact, Arial Bold, and Arial Bold Italic.
Artwork provenance is documented in assets/README.md.
"""

import argparse
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]


def render(font_dir: Path, output: Path) -> None:
    scale = 2
    width, height = 1600, 560
    ink, paper, red = "#111114", "#F2F2EF", "#D32232"
    image = Image.new("RGBA", (width * scale, height * scale), paper)
    draw = ImageDraw.Draw(image)

    def polygon(points, fill):
        draw.polygon([(round(x * scale), round(y * scale)) for x, y in points], fill=fill)

    def star(x, y, radius, fill, angle=0):
        points = []
        for i in range(10):
            a = math.radians(-90 + angle + i * 36)
            r = radius if i % 2 == 0 else radius * 0.39
            points.append((x + math.cos(a) * r, y + math.sin(a) * r))
        polygon(points, fill)

    def label(value, size, x, y, color, angle=0, family="arialbd.ttf", backing=None, pad=14):
        font = ImageFont.truetype(str(font_dir / family), size * scale)
        bounds = font.getbbox(value)
        w, h = bounds[2] - bounds[0], bounds[3] - bounds[1]
        inset = pad * scale
        layer = Image.new("RGBA", (w + inset * 2, h + inset * 2))
        pen = ImageDraw.Draw(layer)
        if backing:
            pen.polygon([(0, 3 * scale), (layer.width - 4 * scale, 0),
                         (layer.width, layer.height - 5 * scale), (6 * scale, layer.height)], fill=backing)
        pen.text((inset - bounds[0], inset - bounds[1]), value, font=font, fill=color)
        rotated = layer.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
        image.alpha_composite(rotated, (round(x * scale), round(y * scale)))

    # Large paper cuts establish the composition before the character and type.
    polygon([(0, 0), (1064, 0), (864, 139), (975, 172), (723, 560), (0, 560)], ink)
    polygon([(0, 0), (697, 0), (575, 38), (0, 106)], red)
    polygon([(1590, 0), (1600, 0), (1600, 560), (1245, 560)], red)
    polygon([(940, 0), (1112, 0), (803, 560), (714, 560), (918, 183), (872, 153)], "#D9DADB")
    polygon([(760, 125), (976, 177), (915, 292), (924, 310), (831, 363), (757, 337)], ink)
    polygon([(0, 488), (468, 401), (422, 440), (911, 383), (772, 560), (0, 560)], red)
    polygon([(0, 527), (347, 470), (315, 493), (571, 466), (480, 560), (0, 560)], paper)

    for y in range(16, height, 14):
        for x in range(944 + (7 if (y // 14) % 2 else 0), width, 14):
            if x < 1055 - y * 0.38 or x > 1536 - y * 0.37:
                continue
            r = 1.6 + 0.9 * (x - 944) / (width - 944)
            draw.ellipse([(round((x - r) * scale), round((y - r) * scale)),
                          (round((x + r) * scale), round((y + r) * scale))], fill="#B7B9BC")

    # Screenprint treatment retains the red gloves and a crisp paper silhouette.
    source = Image.open(ROOT / "assets/joker.png").convert("RGBA").crop((375, 5, 996, 652))
    source = source.resize((790 * scale, round(source.height / source.width * 790 * scale)), Image.Resampling.LANCZOS)
    alpha = source.getchannel("A")
    gray = ImageEnhance.Contrast(ImageOps.grayscale(source)).enhance(1.55)
    gray = ImageOps.posterize(gray, 4)
    portrait = ImageOps.colorize(gray, "#09090C", "#FAFAF7").convert("RGBA")
    pixels = source.convert("RGB")
    red_mask = Image.new("L", source.size)
    red_mask.putdata([255 if r > 65 and r > g * 1.65 and r > b * 1.45 else 0 for r, g, b in pixels.getdata()])
    portrait = Image.composite(ImageEnhance.Color(source).enhance(1.3), portrait, red_mask)
    portrait.putalpha(alpha)
    outline = alpha.filter(ImageFilter.MaxFilter(31))
    shadow = Image.new("RGBA", source.size, ink)
    shadow.putalpha(outline)
    sticker = Image.new("RGBA", source.size, paper)
    sticker.putalpha(outline)
    position = (916 * scale, 9 * scale)
    image.alpha_composite(shadow, (position[0] + 17 * scale, position[1] + 13 * scale))
    image.alpha_composite(sticker, position)
    image.alpha_composite(portrait, position)

    # Individually cut letters use intentional baseline changes, not font spacing.
    letters = [
        ("L", 56, 159, -8, paper, None, "impact.ttf", 161),
        ("A", 151, 132, 7, ink, paper, "arialbd.ttf", 151),
        ("P", 293, 165, -6, paper, None, "impact.ttf", 166),
        ("L", 390, 151, 5, paper, None, "arialbi.ttf", 158),
        ("A", 494, 155, -8, paper, red, "impact.ttf", 157),
        ("C", 625, 138, 6, ink, paper, "arialbd.ttf", 154),
        ("E", 779, 169, -8, paper, None, "impact.ttf", 157),
    ]
    for value, x, y, angle, color, backing, family, size in letters:
        label(value, size, x, y, color, angle, family, backing, pad=9)

    label("@aurorasgod", 36, 85, 364, ink, 5, "arialbd.ttf", paper, pad=13)
    star(844, 83, 38, paper, 15)
    star(844, 83, 22, ink, 15)
    star(70, 383, 19, red, -14)
    star(1468, 466, 49, paper, 12)
    star(1468, 466, 30, ink, 12)
    polygon([(1450, 54), (1551, 26), (1509, 70), (1582, 61), (1482, 110), (1516, 74)], ink)
    polygon([(104, 113), (274, 86), (240, 102), (389, 88), (181, 124)], paper)

    # Sparse print grain stays subtle at GitHub's display size.
    noise = Image.new("RGBA", image.size)
    speckles = ImageDraw.Draw(noise)
    rng = random.Random(5)
    for _ in range(4600):
        x, y = rng.randrange(image.width), rng.randrange(image.height)
        speckles.point((x, y), fill=(255, 255, 255, rng.randrange(10, 38)))
    image = Image.alpha_composite(image, noise)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").resize((width, height), Image.Resampling.LANCZOS).save(output, optimize=True)
    print(f"Rendered {output.name} ({width}x{height})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "assets/header-persona.png")
    args = parser.parse_args()
    render(args.font_dir, args.output)
