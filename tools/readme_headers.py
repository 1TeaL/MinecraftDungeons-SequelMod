"""Draw the README's headers as pixel-art SVGs (docs/headers/), in the change page's look: its green, a hard dark
shadow one pixel down and right, and the dark-mode green when GitHub shows the page dark.

    python tools/readme_headers.py

GitHub READMEs can't load web fonts, so the letters are drawn here from a 5x7 pixel font, one rect per run of
lit pixels. Each heading in README.md shows its SVG with the heading text as the alt text.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "docs" / "headers"
HEADERS = {   # file name -> (text, pixel size)
    "sequel-mod": ("SEQUEL MOD", 9),
    "what-it-does": ("WHAT IT DOES", 4),
    "playing-it": ("PLAYING IT", 4),
    "how-it-works": ("HOW IT WORKS", 4),
    "building-it-yourself": ("BUILDING IT YOURSELF", 4),
    "settings": ("SETTINGS", 3),
    "research-tools": ("RESEARCH TOOLS", 3),
    "not-in-this-repository": ("NOT IN THIS REPOSITORY", 4),
}
FONT = {
    "A": "01110 10001 10001 11111 10001 10001 10001", "B": "11110 10001 10001 11110 10001 10001 11110",
    "C": "01110 10001 10000 10000 10000 10001 01110", "D": "11110 10001 10001 10001 10001 10001 11110",
    "E": "11111 10000 10000 11110 10000 10000 11111", "F": "11111 10000 10000 11110 10000 10000 10000",
    "G": "01110 10001 10000 10111 10001 10001 01111", "H": "10001 10001 10001 11111 10001 10001 10001",
    "I": "01110 00100 00100 00100 00100 00100 01110", "J": "00111 00010 00010 00010 00010 10010 01100",
    "K": "10001 10010 10100 11000 10100 10010 10001", "L": "10000 10000 10000 10000 10000 10000 11111",
    "M": "10001 11011 10101 10101 10001 10001 10001", "N": "10001 10001 11001 10101 10011 10001 10001",
    "O": "01110 10001 10001 10001 10001 10001 01110", "P": "11110 10001 10001 11110 10000 10000 10000",
    "Q": "01110 10001 10001 10001 10101 10010 01101", "R": "11110 10001 10001 11110 10100 10010 10001",
    "S": "01111 10000 10000 01110 00001 00001 11110", "T": "11111 00100 00100 00100 00100 00100 00100",
    "U": "10001 10001 10001 10001 10001 10001 01110", "V": "10001 10001 10001 10001 10001 01010 00100",
    "W": "10001 10001 10001 10101 10101 10101 01010", "X": "10001 10001 01010 00100 01010 10001 10001",
    "Y": "10001 10001 10001 01010 00100 00100 00100", "Z": "11111 00001 00010 00100 01000 10000 11111",
    " ": "00000 00000 00000 00000 00000 00000 00000",
}
STYLE = (".t{fill:#1c7c45}.s{fill:#0d3f23}"
         "@media (prefers-color-scheme:dark){.t{fill:#4cc17f}.s{fill:#06140b}}")


def runs(text):
    """[(x, y, length)] of lit pixels, in font pixels."""
    out = []
    for i, ch in enumerate(text):
        for y, row in enumerate(FONT[ch].split()):
            x = 0
            while x < 5:
                if row[x] == "1":
                    start = x
                    while x < 5 and row[x] == "1":
                        x += 1
                    out.append((i * 6 + start, y, x - start))
                else:
                    x += 1
    return out


def svg(text, px):
    w, h = (len(text) * 6 - 1 + 1) * px, 8 * px
    lit = runs(text)
    rects = lambda cls, dx: "".join(  # noqa: E731
        f'<rect class="{cls}" x="{(x + dx) * px}" y="{(y + dx) * px}" width="{n * px}" height="{px}"/>' for x, y, n in lit)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'shape-rendering="crispEdges" role="img" aria-label="{text.title()}"><style>{STYLE}</style>'
            f'{rects("s", 1)}{rects("t", 0)}</svg>\n')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (text, px) in HEADERS.items():
        (OUT / f"{name}.svg").write_text(svg(text, px), encoding="utf-8")
    print(f"wrote {len(HEADERS)} headers to {OUT}")


if __name__ == "__main__":
    main()
