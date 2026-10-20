# Profile artwork

The current profile uses `p5/header.png` and the matching section labels,
project markers, tool icons, navigation controls, and footer in `p5/`.
The layout uses diagonal typography, spot red, ink separations, and localized
screen tones inspired by Persona 5. Body copy remains native Markdown / HTML.

Rebuild with Pillow, fonttools, and Windows fonts:

```sh
python tools/render_profile.py --font-dir C:/Windows/Fonts
```

All lettering in the SVG assets is converted to paths for consistent rendering.
Lucide icon data is stored in `p5/icons.json`; its license is included in
`p5/LUCIDE-LICENSE.txt`. To update it from a local `@lucide/astro` installation,
pass `--import-lucide /path/to/node_modules/@lucide/astro` when rebuilding.

## Earlier header

`header-persona.png` is a personal, unofficial Persona 5-inspired collage.
Typography, composition, halftone pattern, and print treatment are produced by
`../tools/render_header.py`. The header has no affiliation with ATLUS or SEGA.

The Joker illustration in `joker.png` comes from the official Persona 5 Royal
[protagonist page](https://p5r.jp/character/hero/):
[original artwork](https://p5r.jp/resources/img/character/hero/costume2_fbfcd04fd7ce91f54b1ec840887c9923.png).

Character artwork: Copyright ATLUS / SEGA. All rights reserved. The collage does
not change the ownership or licensing of the source artwork.

To rebuild with Pillow and the required Windows fonts:

```sh
python tools/render_header.py --font-dir C:/Windows/Fonts
```
