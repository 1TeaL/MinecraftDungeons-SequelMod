"""Fetch the Minecraft Wiki's Dungeons enchantment tables into tools/wiki_enchantments.json, and the icons it shows
into docs/enchantments/ (for ENCHANTMENTS.md, tools/enchant_sheet.py).

    python tools/wiki_enchantments.py            # fetch the page and any icon not downloaded yet
    python tools/wiki_enchantments.py --parse    # only re-read the saved page (tools/wiki_enchantments.txt)

The base game's per-tier numbers are worked out in the game's code, so the wiki is where the page takes them from.
The icons are the game's own art, kept for the documentation page only (user, 2026-11-09) - never put in a pak.
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = "Dungeons:Enchantment"
API = "https://minecraft.wiki/api.php?action=parse&page=%s&prop=wikitext&format=json" % urllib.parse.quote(PAGE)
SAVED = ROOT / "tools" / "wiki_enchantments.txt"
OUT = ROOT / "tools" / "wiki_enchantments.json"
ICONS = ROOT / "docs" / "enchantments"
AGENT = "SequelModDocs/1.0 (Minecraft Dungeons mod documentation; github.com/1TeaL/MinecraftDungeons-SequelMod)"
SECTIONS = ["Melee", "Ranged", "Armor", "Exclusive", "Unused"]
PNG = b"\x89PNG\r\n\x1a\n"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": AGENT})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def plain(text):
    """Wiki markup -> plain text."""
    text = re.sub(r"\{\{(?:MCD|DuItemLink|MCDLink)\|([^}|]*)\|([^}]*)\}\}", r"\2", text)
    text = re.sub(r"\{\{(?:MCD|DuItemLink|MCDLink)\|([^}]*)\}\}", r"\1", text)
    text = re.sub(r"\{\{tc\|[^|}]*\|([^|}]*)(?:\|[^}]*)?\}\}", r"\1", text)
    text = re.sub(r"\[\[(?:[^]|]*\|)?([^]]*)\]\]", r"\1", text)
    text = re.sub(r"\{\{[^}]*\}\}", "", text)
    text = re.sub(r"<br\s*/?>", " ", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"'''?", "", text)
    return " ".join(text.split())


def cells(row):
    """A table row's cells: lines starting with | (a cell may go on over several lines)."""
    out = []
    for line in row.split("\n"):
        if line.startswith("|"):
            out.append(line[1:])
        elif out:
            out[-1] += "\n" + line
    return out


def parse(text):
    found = []
    heads = [(m.start(), m.group(1).strip()) for m in re.finditer(r"^===\s*([^=]+?)\s*===\s*$", text, re.M)]
    for n, (at, name) in enumerate(heads):
        if name not in SECTIONS:
            continue
        end = heads[n + 1][0] if n + 1 < len(heads) else len(text)
        body = text[at:end]
        start = body.find("{|")
        if start < 0:
            continue
        rows = body[start:body.find("\n|}", start)].split("\n|-")
        for row in rows[1:]:
            c = cells(row)
            icon = re.search(r"\[\[File:([^|\]]+)", c[0]) if c else None
            if not icon or len(c) < 11:
                continue
            c = [x.strip() for x in c]
            rarity = c[-1].split("|")[-1].strip()
            desc = [plain(x) for x in re.split(r"^\*", c[2], flags=re.M) if plain(x)]
            built = [plain(x) for x in re.split(r"^\*", c[9], flags=re.M) if plain(x)]
            found.append({
                "section": name,
                "icon": icon.group(1).strip(),
                "name": plain(c[1]),
                "description": desc,
                "tier_text": plain(c[3]),
                "tiers": [plain(c[4]), plain(c[5]), plain(c[6])],
                "mobs": plain(c[7]),
                "multiple": plain(c[8]),
                "built_into": [] if built == ["None"] else built,
                "gilded": plain(c[10]) if len(c) > 11 else "",
                "rarity": plain(rarity),
            })
    return found


def main():
    if "--parse" in sys.argv:
        text = SAVED.read_text(encoding="utf-8")
    else:
        text = json.loads(get(API))["parse"]["wikitext"]["*"]
        SAVED.write_text(text, encoding="utf-8")
    rows = parse(text)
    OUT.write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{len(rows)} enchantments -> {OUT.name}")
    if "--parse" in sys.argv:
        return
    ICONS.mkdir(parents=True, exist_ok=True)
    for row in rows:
        target = ICONS / (re.sub(r"[^A-Za-z0-9]+", "_", Path(row["icon"]).stem).strip("_") + ".png")
        if target.exists():
            continue
        data = get("https://minecraft.wiki/w/Special:FilePath/" + urllib.parse.quote(row["icon"].replace(" ", "_")))
        if not data.startswith(PNG):
            print("  not a PNG, skipped:", row["icon"])
            continue
        target.write_bytes(data)
        print("  icon", target.name, len(data))
        time.sleep(0.3)   # gently


if __name__ == "__main__":
    main()
