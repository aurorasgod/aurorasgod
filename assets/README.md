# Header artwork

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
