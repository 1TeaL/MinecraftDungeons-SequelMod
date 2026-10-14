"""Parse minecraft.wiki gear tables (raw wikitext in research/wiki/) into tools/wiki_gear.json.

    python tools/parse_gear_wiki.py

Pages: Dungeons:Weapon (melee + ranged), Dungeons:Armor, Dungeons:Artifact, saved with ?action=raw.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "research" / "wiki"


def clean(s):
    s = re.sub(r"<ref[^>]*?/>|<ref.*?</ref>", "", s, flags=re.S)
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"\{\{DuMiscSprite\|[^}]*\}\}", "", s)
    s = re.sub(r"\{\{tc\|[^|}]*\|([^|}]*)[^}]*\}\}", r"\1", s)
    s = re.sub(r"\{\{(?:MCD|DuItemLink|DuEnchantmentLink|DuLevelLink|DuEntityLink|MCD2)\|([^}|]*)\|([^}]*)\}\}", r"\2", s)
    s = re.sub(r"\{\{(?:MCD|DuItemLink|DuEnchantmentLink|DuLevelLink|DuEntityLink|MCD2)\|([^}]*)\}\}", r"\1", s)
    s = re.sub(r"\[\[File:[^\]]*\]\]", "", s)
    s = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"\{\{[^}]*\}\}", "", s)
    s = re.sub(r"<br ?/?>", " ", s)
    s = re.sub(r"</?code>|'''?", "", s)
    s = re.sub(r'^\s*style="[^"]*"\s*\|', "", s)
    return s.strip()


def bullets(cell):
    items = [clean(x) for x in re.split(r"\n\s*\*", "\n" + cell)]
    return [x for x in items if x and x.lower() != "none"]


def tables(text):
    """Yield (section heading, header names, rows of raw cells) for every wikitable."""
    heading = ""
    for m in re.finditer(r"(^=+[^=\n]+=+\s*$)|(^\{\|.*?^\|\})", text, flags=re.M | re.S):
        if m.group(1):
            heading = clean(m.group(1).strip("= \n"))
            continue
        body = m.group(2)
        parts = body.split("\n|-")
        header = [clean(h) for h in re.findall(r"^!(.*)$", parts[0], flags=re.M)]
        header = [re.sub(r"^\*\s*", "", h).split("*")[0].strip() or "Name" for h in header]
        rows = []
        for row in parts[1:]:
            cells, cur = [], None
            for ln in row.split("\n"):
                if ln.startswith("|}"):
                    break
                if (ln.startswith("|") and not ln.startswith("|-")) or ln.startswith("!"):  # some rows use "!"
                    if cur is not None:
                        cells.append(cur)
                    cur = ln[1:]
                elif cur is not None:
                    cur += "\n" + ln
            if cur is not None:
                cells.append(cur)
            if len(cells) >= 3:
                rows.append(cells)
        yield heading, header, rows


def gear(page, category):
    out = []
    for heading, header, rows in tables((WIKI / page).read_text(encoding="utf-8")):
        if category in ("Melee", "Ranged"):
            in_melee = heading.lower().startswith(("default", "adventure", "apocalypse", "the tower", "unused")) \
                and not heading.endswith("=")
            if category == "Ranged" and "Combo" in " ".join(header):
                continue
            if category == "Melee" and "Combo" not in " ".join(header):
                continue
        cols = {h.lower(): i for i, h in enumerate(header)}

        def col(*names):
            for n in names:
                for h, i in cols.items():
                    if h.startswith(n) and i < len(row):
                        return row[i]
            return ""
        for row in rows:
            names = bullets(row[1]) if len(row) > 1 else []
            if not names:
                continue
            props = bullets(col("properties"))
            entry = {
                "category": category, "section": heading, "name": names[0],
                "id": names[1] if len(names) > 1 else "",
                "group": clean(col("group")), "unique": clean(col("unique")).lower().startswith("yes"),
                "dlc": clean(col("dlc")).replace("✖", "").strip(),
                "properties": props,
                "builtin": bullets(col("built-in")),
                "combo": clean(col("combo")),
                "cooldown": " ".join(bullets(col("cooldown"))),
                "soul": clean(col("soul requiring")).startswith("✔"),
            }
            if re.fullmatch(r"\d+", " ".join(entry["builtin"])) and not entry["combo"].isdigit():
                entry["builtin"], entry["combo"] = ([entry["combo"]] if entry["combo"] else []), entry["builtin"][0]
            if category == "Artifact" and not entry["properties"]:
                entry["properties"] = [clean(col("properties"))]
            out.append(entry)
    return out


if __name__ == "__main__":
    items = gear("Weapon.txt", "Melee") + gear("Weapon.txt", "Ranged") + gear("Armor.txt", "Armor") \
        + gear("Artifact.txt", "Artifact")
    seen, uniq = set(), []
    for it in items:
        key = (it["category"], it["name"])
        if key not in seen:
            seen.add(key)
            uniq.append(it)
    (ROOT / "tools" / "wiki_gear.json").write_text(json.dumps(uniq, indent=1, ensure_ascii=False), encoding="utf-8")
    from collections import Counter
    print(Counter(i["category"] for i in uniq))
