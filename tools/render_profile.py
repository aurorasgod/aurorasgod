"""Build the P5-inspired profile artwork, outlined type, and Lucide controls.

python tools/render_profile.py --font-dir C:/Windows/Fonts
Requires Pillow and fonttools. Pass --import-lucide to import icon data once.
"""

import argparse
import json
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/p5"
INK, PAPER, RED = "#101010", "#FFFFFF", "#E51B2B"
ICONS = ("book-open", "code-xml", "mail", "cpu", "circuit-board", "notebook-pen")
ET.register_namespace("", "http://www.w3.org/2000/svg")


def node(parent, tag, **attrs):
    return ET.SubElement(parent, tag, {k.replace("_", "-"): str(v) for k, v in attrs.items()})


def svg(width, height, title):
    root = ET.Element("svg", {"xmlns": "http://www.w3.org/2000/svg", "width": str(width),
                              "height": str(height), "viewBox": f"0 0 {width} {height}",
                              "role": "img", "aria-labelledby": "title"})
    ET.SubElement(root, "title", id="title").text = title
    return root


def save_svg(root, name):
    ET.ElementTree(root).write(OUT / name, encoding="utf-8", xml_declaration=False)


class Lettering:
    def __init__(self, path):
        self.font = TTFont(path)
        self.glyphs = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()
        self.units = self.font["head"].unitsPerEm

    def text(self, parent, value, x, baseline, size, color, transform=None):
        scale = size / self.units
        outer = node(parent, "g", fill=color, **({"transform": transform} if transform else {}))
        for char in value:
            glyph = self.glyphs[self.cmap[ord(char)]]
            pen = SVGPathPen(self.glyphs)
            glyph.draw(pen)
            if pen.getCommands():
                node(outer, "path", d=pen.getCommands(),
                     transform=f"translate({x:.3f} {baseline}) scale({scale:.6f} {-scale:.6f})")
            x += glyph.width * scale
        return x


def icon(parent, data, x, y, size, color=PAPER):
    group = node(parent, "g", transform=f"translate({x} {y}) scale({size / 24})",
                 fill="none", stroke=color, stroke_width="2", stroke_linecap="round", stroke_linejoin="round")
    for tag, attributes in data["node"]:
        ET.SubElement(group, tag, attributes)


def import_icons(folder):
    data = {}
    for name in ICONS:
        source = (folder / "src/icons" / f"{name}.ts").read_text(encoding="utf-8")
        match = re.search(r"const iconData: LucideIconData = (.*);", source)
        if not match:
            raise ValueError(f"Missing structured Lucide data: {name}")
        data[name] = json.loads(match.group(1))
    (OUT / "icons.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    (OUT / "LUCIDE-LICENSE.txt").write_bytes((folder / "LICENSE").read_bytes())


def render_header(font_dir):
    scale, width, height = 2, 1600, 520
    image = Image.new("RGBA", (width * scale, height * scale), RED)
    draw = ImageDraw.Draw(image)

    def poly(points, color):
        draw.polygon([(round(x * scale), round(y * scale)) for x, y in points], fill=color)

    def type_layer(value, size, x, y, color, angle=0, stroke=0, stroke_color=INK, family="impact.ttf"):
        font = ImageFont.truetype(str(font_dir / family), size * scale)
        bounds = font.getbbox(value, stroke_width=stroke * scale)
        pad = 18 * scale
        layer = Image.new("RGBA", (bounds[2] - bounds[0] + pad * 2, bounds[3] - bounds[1] + pad * 2))
        ImageDraw.Draw(layer).text((pad - bounds[0], pad - bounds[1]), value, font=font,
                                  fill=color, stroke_width=stroke * scale, stroke_fill=stroke_color)
        if angle:
            layer = layer.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)
        image.alpha_composite(layer, (round(x * scale), round(y * scale)))

    def star(x, y, radius, color, angle=0):
        points = []
        for i in range(10):
            a = math.radians(angle - 90 + i * 36)
            r = radius if i % 2 == 0 else radius * 0.38
            points.append((x + r * math.cos(a), y + r * math.sin(a)))
        poly(points, color)

    # A single diagonal carries the title, portrait, and lower paper edge.
    poly([(1029, 0), (1600, 0), (1600, 520), (746, 520), (913, 257), (861, 236)], PAPER)
    poly([(0, 157), (954, 45), (920, 322), (0, 473)], INK)
    poly([(0, 143), (938, 31), (907, 68), (0, 180)], PAPER)
    poly([(0, 480), (763, 396), (715, 448), (1134, 415), (1042, 520), (0, 520)], INK)
    poly([(0, 511), (696, 448), (666, 478), (948, 461), (903, 520), (0, 520)], PAPER)
    poly([(1517, 0), (1600, 0), (1600, 520), (1385, 520)], RED)

    # Two localized screen-tone patches leave the type and face clear.
    for row, y in enumerate(range(18, 506, 15)):
        for x in range(984 + (7 if row % 2 else 0), 1570, 15):
            if x < 1110 - y * 0.4 or x > 1490 - y * 0.08:
                continue
            radius = 2.0 * scale
            cx, cy = x * scale, y * scale
            draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill="#B9B9B9")
    for x in range(70, 720, 21):
        for y in range(16, 107, 21):
            if y < 96 - x * 0.1:
                draw.ellipse((x * scale, y * scale, (x + 3) * scale, (y + 3) * scale), fill="#A80D1A")

    source = Image.open(ROOT / "assets/joker.png").convert("RGBA").crop((370, 5, 996, 570))
    source = source.resize((790 * scale, round(source.height / source.width * 790 * scale)), Image.Resampling.LANCZOS)
    alpha = source.getchannel("A")
    gray = ImageEnhance.Contrast(ImageOps.grayscale(source)).enhance(1.7)
    separated = gray.point([8 if n < 50 else 65 if n < 105 else 158 if n < 172 else 255 for n in range(256)])
    portrait = Image.merge("RGB", (separated, separated, separated)).convert("RGBA")
    red_mask = Image.new("L", source.size)
    red_mask.putdata([255 if r > 65 and r > g * 1.7 and r > b * 1.45 else 0
                      for r, g, b in source.convert("RGB").getdata()])
    red_ink = Image.new("RGBA", source.size, RED)
    portrait = Image.composite(red_ink, portrait, red_mask)
    portrait.putalpha(alpha)
    outline = alpha.filter(ImageFilter.MaxFilter(19))
    backing = Image.new("RGBA", source.size, PAPER)
    backing.putalpha(outline)
    shadow = Image.new("RGBA", source.size, INK)
    shadow.putalpha(outline)
    pos = (903 * scale, 6 * scale)
    image.alpha_composite(shadow, (pos[0] + 11 * scale, pos[1] + 11 * scale))
    image.alpha_composite(backing, pos)
    image.alpha_composite(portrait, pos)

    type_layer("LAPLACE", 210, 51, 129, PAPER, angle=6, stroke=3, stroke_color=INK)
    poly([(83, 425), (430, 382), (446, 447), (95, 490)], INK)
    poly([(79, 416), (420, 375), (433, 436), (90, 478)], PAPER)
    type_layer("@aurorasgod", 36, 96, 397, INK, angle=6, family="arialbd.ttf")
    type_layer("PERSONAL FILE", 24, 51, 15, PAPER, angle=6, family="arialbd.ttf")
    star(848, 361, 49, PAPER, -12)
    star(848, 361, 27, INK, -12)
    star(1479, 81, 53, INK, 17)
    poly([(1469, 393), (1576, 354), (1533, 391), (1586, 387), (1492, 441), (1512, 409)], INK)
    image.convert("RGB").resize((width, height), Image.Resampling.LANCZOS).save(OUT / "header.png", optimize=True)


def render_sections(lettering):
    for index, title in enumerate(("PROFILE", "PROJECTS", "TOOLBOX", "NOTES"), 1):
        root = svg(880, 144, f"{index:02d} / {title}")
        node(root, "path", d="M20 26 864 6 825 92 847 111 117 136 34 112Z", fill=PAPER)
        node(root, "path", d="M109 25 848 13 804 95 824 111 103 126Z", fill=INK)
        node(root, "path", d="M8 14 133 7 109 129 23 139 36 92Z", fill=INK)
        node(root, "path", d="M3 7 124 0 101 121 15 131 28 84Z", fill=RED)
        lettering.text(root, f"{index:02d}", 23, 98, 90, PAPER, "matrix(1 0 -0.10 1 8 0)")
        lettering.text(root, title, 153, 100, 91, PAPER, "matrix(1 -0.025 -0.08 1 4 5)")
        node(root, "path", d="M135 132 804 117 790 130 142 142Z", fill=RED)
        save_svg(root, f"section-{title.lower()}.svg")


def render_controls(lettering, icons):
    for name, key, label in (("blog", "book-open", "BLOG"), ("code", "code-xml", "CODE"), ("mail", "mail", "MAIL")):
        root = svg(144, 88, label)
        node(root, "path", d="M5 12 140 1 127 78 1 86Z", fill=PAPER)
        node(root, "path", d="M0 8 134 0 122 74 0 82Z", fill=INK)
        node(root, "path", d="M0 8 12 7 0 72Z", fill=RED)
        icon(root, icons[key], 14, 27, 27)
        lettering.text(root, label, 47, 56, 35, PAPER, "matrix(1 -0.05 -0.08 1 5 1)")
        save_svg(root, f"nav-{name}.svg")

    for i in range(1, 5):
        root = svg(96, 96, f"Project {i:02d}")
        node(root, "path", d="M9 9 93 1 80 88 3 95Z", fill=PAPER)
        node(root, "path", d="M7 10 92 4 76 84 1 90Z", fill=INK)
        node(root, "path", d="M3 4 85 0 70 78 0 85Z", fill=RED)
        lettering.text(root, f"{i:02d}", 14, 65, 61, PAPER, "matrix(1 0 -0.08 1 3 0)")
        save_svg(root, f"project-{i:02d}.svg")

    for name, key in (("code", "code-xml"), ("robot", "cpu"), ("circuit", "circuit-board"), ("notes", "notebook-pen")):
        root = svg(64, 64, key)
        node(root, "path", d="M4 4 61 0 55 57 0 64Z", fill=PAPER)
        node(root, "path", d="M1 4 57 0 51 53 0 59Z", fill=INK)
        node(root, "path", d="M0 56 51 50 49 59 0 64Z", fill=RED)
        icon(root, icons[key], 12, 11, 33)
        save_svg(root, f"tool-{name}.svg")

    root = svg(700, 112, "To be continued")
    node(root, "path", d="M10 22 691 0 655 87 673 103 0 112Z", fill=PAPER)
    node(root, "path", d="M1 16 681 0 644 80 661 96 0 105Z", fill=INK)
    node(root, "path", d="M1 16 48 14 18 99 0 104Z", fill=RED)
    lettering.text(root, "TO BE CONTINUED", 61, 74, 58, PAPER, "matrix(1 -0.02 -0.10 1 6 0)")
    node(root, "path", d="m619 31 30 20-37 20 9-20Z", fill=RED)
    save_svg(root, "footer.svg")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font-dir", type=Path, required=True)
    parser.add_argument("--import-lucide", type=Path)
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.import_lucide:
        import_icons(args.import_lucide)
    icons = json.loads((OUT / "icons.json").read_text(encoding="utf-8"))
    lettering = Lettering(args.font_dir / "impact.ttf")
    render_header(args.font_dir)
    render_sections(lettering)
    render_controls(lettering, icons)
    print(f"Rendered profile artwork in {OUT}")


if __name__ == "__main__":
    main()
