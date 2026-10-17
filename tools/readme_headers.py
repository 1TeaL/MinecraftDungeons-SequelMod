"""Draw the README's headers as pixel-art SVGs (docs/headers/), in the change page's look: its green, a hard dark
shadow one pixel down and right, and the dark-mode green when GitHub shows the page dark.

    python tools/readme_headers.py

GitHub READMEs can't load web fonts, so the letters are drawn here from a 5x7 pixel font, one rect per run of
lit pixels. Each heading in README.md shows its SVG with the heading text as the alt text.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "docs" / "headers"
HEADERS = {   # file name -> [(text, pixel size), ...]: one line, or several stacked in one image
    "sequel-mod": [("MINECRAFT DUNGEONS:", 4), ("SEQUEL MOD", 9)],
    "what-it-does": [("WHAT IT DOES", 4)],
    "playing-it": [("PLAYING IT", 4)],
    "how-it-works": [("HOW IT WORKS", 4)],
    "how-it-was-made": [("HOW IT WAS MADE", 4)],
    "building-it-yourself": [("BUILDING IT YOURSELF", 4)],
    "settings": [("SETTINGS", 3)],
    "research-tools": [("RESEARCH TOOLS", 3)],
    "not-in-this-repository": [("NOT IN THIS REPOSITORY", 4)],
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
    " ": "00000 00000 00000 00000 00000 00000 00000", ":": "00000 00100 00100 00000 00100 00100 00000",
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


def svg(lines):
    """One image of the lines, stacked with a gap of two of the largest pixels."""
    gap = 2 * max(px for _, px in lines)
    shadow, text, width, top = [], [], 0, 0
    for line, px in lines:
        for x, y, n in runs(line):
            for out, d in ((shadow, 1), (text, 0)):
                out.append(f'<rect class="{"s" if d else "t"}" x="{(x + d) * px}" y="{top + (y + d) * px}" '
                           f'width="{n * px}" height="{px}"/>')
        width, top = max(width, len(line) * 6 * px), top + 8 * px + gap
    height = top - gap
    label = " ".join(line for line, _ in lines).title()
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
            f'shape-rendering="crispEdges" role="img" aria-label="{label}"><style>{STYLE}</style>'
            + "".join(shadow) + "".join(text) + "</svg>\n")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, lines in HEADERS.items():
        (OUT / f"{name}.svg").write_text(svg(lines), encoding="utf-8")
    print(f"wrote {len(HEADERS)} headers to {OUT}")


if __name__ == "__main__":
    main()
