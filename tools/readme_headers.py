"""Draw the README's headers as pixel-art SVGs (docs/headers/): chunky blocky letters like the game's own, in the
change page's green (a lighter green when GitHub shows the page dark), no shadow.

    python tools/readme_headers.py

GitHub READMEs can't load web fonts, so the letters are drawn here from a bold 8-pixel-high font (strokes two
pixels thick), one rect per run of lit pixels. Each heading in README.md shows its SVG with the heading text as
the alt text.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "docs" / "headers"
HEADERS = {   # file name -> [(text, pixel size), ...]: one line, or several stacked in one image
    "sequel-mod": [("MINECRAFT DUNGEONS:", 4), ("SEQUEL MOD", 8)],
    "why-it-was-made": [("WHY IT WAS MADE", 4)],
    "what-it-does": [("WHAT IT DOES", 4)],
    "playing-it": [("PLAYING IT", 4)],
    "mcd-transmog": [("MCD TRANSMOG", 4)],
    "how-it-works": [("HOW IT WORKS", 4)],
    "how-it-was-made": [("HOW IT WAS MADE", 4)],
    "building-it-yourself": [("BUILDING IT YOURSELF", 4)],
    "settings": [("SETTINGS", 3)],
    "research-tools": [("RESEARCH TOOLS", 3)],
    "not-in-this-repository": [("NOT IN THIS REPOSITORY", 4)],
}
HEIGHT = 8
FONT = {   # rows top to bottom; a letter is as wide as its rows
    "A": ".#####. ####### ##...## ##...## ####### ####### ##...## ##...##",
    "B": "######. ####### ##...## ######. ######. ##...## ####### ######.",
    "C": ".###### ####### ##..... ##..... ##..... ##..... ####### .######",
    "D": "######. ####### ##...## ##...## ##...## ##...## ####### ######.",
    "E": "####### ####### ##..... ######. ######. ##..... ####### #######",
    "F": "####### ####### ##..... ######. ######. ##..... ##..... ##.....",
    "G": ".###### ####### ##..... ##.#### ##.#### ##...## ####### .#####.",
    "H": "##...## ##...## ##...## ####### ####### ##...## ##...## ##...##",
    "I": "###### ###### ..##.. ..##.. ..##.. ..##.. ###### ######",
    "J": ".....## .....## .....## .....## .....## ##...## ####### .#####.",
    "K": "##...## ##..##. ##.##.. ####... ####... ##.##.. ##..##. ##...##",
    "L": "##..... ##..... ##..... ##..... ##..... ##..... ####### #######",
    "M": "##...## ###.### ####### ##.#.## ##...## ##...## ##...## ##...##",
    "N": "##...## ###..## ####.## ##.#### ##..### ##...## ##...## ##...##",
    "O": ".#####. ####### ##...## ##...## ##...## ##...## ####### .#####.",
    "P": "######. ####### ##...## ##...## ####### ######. ##..... ##.....",
    "Q": ".#####. ####### ##...## ##...## ##.#.## ##..##. ####### .###.##",
    "R": "######. ####### ##...## ##...## ######. #####.. ##..##. ##...##",
    "S": ".###### ####### ##..... ######. .###### .....## ####### ######.",
    "T": "###### ###### ..##.. ..##.. ..##.. ..##.. ..##.. ..##..",
    "U": "##...## ##...## ##...## ##...## ##...## ##...## ####### .#####.",
    "V": "##...## ##...## ##...## ##...## ##...## .##.##. ..###.. ...#...",
    "W": "##...## ##...## ##...## ##...## ##.#.## ####### ###.### ##...##",
    "X": "##...## ##...## .##.##. ..###.. ..###.. .##.##. ##...## ##...##",
    "Y": "##..## ##..## ##..## .####. ..##.. ..##.. ..##.. ..##..",
    "Z": "####### ####### ....##. ...##.. ..##... .##.... ####### #######",
    " ": "... ... ... ... ... ... ... ...",
    ":": ".. ## ## .. .. ## ## ..",
}
STYLE = ".t{fill:#1c7c45}@media (prefers-color-scheme:dark){.t{fill:#4cc17f}}"


def runs(text):
    """([(x, y, length)] of lit pixels, width), in font pixels; one blank column between letters."""
    out, left = [], 0
    for ch in text:
        rows = FONT[ch].split()
        for y, row in enumerate(rows):
            x = 0
            while x < len(row):
                if row[x] == "#":
                    start = x
                    while x < len(row) and row[x] == "#":
                        x += 1
                    out.append((left + start, y, x - start))
                else:
                    x += 1
        left += len(rows[0]) + 1
    return out, left - 1


def svg(lines):
    """One image of the lines, stacked with a gap of two of the largest pixels."""
    gap = 2 * max(px for _, px in lines)
    text, width, top = [], 0, 0
    for line, px in lines:
        pixels, line_width = runs(line)
        for x, y, n in pixels:
            text.append(f'<rect class="t" x="{x * px}" y="{top + y * px}" width="{n * px}" height="{px}"/>')
        width, top = max(width, line_width * px), top + HEIGHT * px + gap
    height = top - gap
    label = " ".join(line for line, _ in lines).title()
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
            f'shape-rendering="crispEdges" role="img" aria-label="{label}"><style>{STYLE}</style>'
            + "".join(text) + "</svg>\n")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, lines in HEADERS.items():
        (OUT / f"{name}.svg").write_text(svg(lines), encoding="utf-8")
    print(f"wrote {len(HEADERS)} headers to {OUT}")


if __name__ == "__main__":
    main()
