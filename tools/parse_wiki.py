import re, json, sys
t = open(sys.argv[1], encoding="utf-8").read()
lines = t.split("\n")
sections = {"Melee": (111, 650), "Ranged": (650, 1262), "Armor": (1262, 1887), "Unique-only": (1887, 2041)}

def clean(s):
    s = re.sub(r"<ref[^>]*?/>|<ref.*?</ref>", "", s, flags=re.S)
    s = re.sub(r"\{\{(?:MCD|DuItemLink|MCD2)\|([^}|]*)\|([^}]*)\}\}", r"\2", s)
    s = re.sub(r"\{\{(?:MCD|DuItemLink|MCD2)\|([^}]*)\}\}", r"\1", s)
    s = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"\{\{[^}]*\}\}", "", s)
    s = re.sub(r"<br ?/?>", " ", s)
    s = re.sub(r"'''?", "", s)
    s = re.sub(r"^\s*(style=\"[^\"]*\"\s*\|)", "", s)
    return s.strip()

out = []
for cat, (a, b) in sections.items():
    body = "\n".join(lines[a:b])
    for row in body.split("\n|-")[1:]:
        cells, cur = [], None
        for ln in row.split("\n"):
            if ln.startswith("|}"):
                break
            if ln.startswith("|") and not ln.startswith("|-"):
                if cur is not None:
                    cells.append(cur)
                cur = ln[1:]
            elif ln.startswith("!"):
                if cur is None:
                    cells = []; break
                cells.append(cur); cur = ln[1:]
            elif cur is not None:
                cur += "\n" + ln
        if cur is not None:
            cells.append(cur)
        fi = next((i for i, c in enumerate(cells) if "File:" in c), None)
        ni = fi + 1 if fi is not None else next((i for i, c in enumerate(cells) if "{{MCD|" in c), None)
        if ni is None or len(cells) < ni + 6:
            continue
        name = clean(cells[ni])
        desc = " ".join(clean(x.lstrip("* ")) for x in cells[ni + 1].strip().split("\n") if x.strip())
        out.append({"cat": cat, "name": name, "desc": desc, "tiertext": clean(cells[ni + 2]),
                    "t": [clean(cells[ni + 3]), clean(cells[ni + 4]), clean(cells[ni + 5])]})
json.dump(out, open(sys.argv[2], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
for o in out:
    print(o["cat"][0], "|", o["name"], "|", o["desc"][:90], "|", o["tiertext"], "|", " / ".join(o["t"]))
