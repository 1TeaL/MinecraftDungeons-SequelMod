"""List every gear item's look file for the in-game transmog menu: unreal/Scripts/transmog_items.json.

    python tools/transmog_items.py

Reads each gameplay file (BP_<Item>Instance) in the extracted game: its ItemIdName (the id the save's itemsFound
uses) and GearActor (its look file). Only items in tools/item_registry.json (the game's registered melee, ranged
and armor items) are listed; the menu shows just the ones the player has found, so nothing unreleased appears.
"""
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from uasset import Package  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
EXTRACT = ROOT.parents[1] / "Mods" / "Dungeons BMS" / "BMS output" / "Dungeons" / "Content"
REGISTRY = ROOT / "tools" / "item_registry.json"
OUT = ROOT / "unreal" / "Scripts" / "transmog_items.json"


def look_of(pkg):
    """(item id, path of the look file's default object) from a gameplay file, or None."""
    props = {p["name"]: p for p in pkg.export_props(pkg.cdo())}
    if "GearActor" not in props or "ItemIdName" not in props:
        return None
    index = struct.unpack_from("<i", pkg.data, props["GearActor"]["pos"])[0]
    if index >= 0:
        return None
    _, _, outer, name = pkg.imports[-index - 1]
    package = pkg.imports[-outer - 1][3]
    return props["ItemIdName"]["value"], "%s.Default__%s" % (package, name)


def main():
    registry = json.loads(REGISTRY.read_text())
    wanted = {key.split("/", 1)[1].lower(): key.split("/", 1)[0] for key in registry}
    items, missing = {}, set(wanted)
    for file in sorted(EXTRACT.rglob("BP_*Instance.uasset")):
        try:
            found = look_of(Package(str(file)))
        except Exception:
            continue
        if found and found[0].lower() in wanted and found[0] not in items:
            items[found[0]] = {"id": found[0], "kind": wanted[found[0].lower()], "look": found[1]}
            missing.discard(found[0].lower())
    order = {"MeleeWeapons": 0, "RangedWeapons": 1, "Armor": 2}
    rows = sorted(items.values(), key=lambda r: (order[r["kind"]], r["id"].lower()))
    OUT.write_text(json.dumps(rows, indent=1))
    print("%d items -> %s" % (len(rows), OUT))
    if missing:
        print("no gameplay file found for: " + ", ".join(sorted(missing)))


if __name__ == "__main__":
    main()
