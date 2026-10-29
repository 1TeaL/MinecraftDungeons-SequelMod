"""Transmog prototype (2026-10-30): an item type wears another item's look - its stats, perks and swings stay.

    python tools/looks.py ScaleMail=WolfArmor      # every Scale Mail looks like Wolf Armor (the game must be closed)
    python tools/looks.py ScaleMail=WolfArmor Axe=Axe_Unique1
    python tools/looks.py --off                    # remove the looks: every item looks like itself again

Each item has a gameplay file (BP_<Item>Instance: stats, perks, swings) and a look file (BP_<Item>: model and
material); the gameplay file names its look in GearActor. This writes copies of the gameplay files with GearActor
pointing at the other item's look file into a small second pak, SequelLooks_P.pak, next to the mod's in ~mods.
Data only, no game code; saves aren't touched. Same kind only (armor to armor, melee to melee, bow to bow). Not in
the release yet: a prototype, to see in game whether the look swaps cleanly.
"""
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from memprobe import pid_of  # noqa: E402
from uasset import Package, set_export_properties  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
GAME = ROOT.parents[1]
EXTRACT = GAME / "Mods" / "Dungeons BMS" / "BMS output"
U4PAK = GAME / "Mods" / "Dungeons-Mod-Kit-master" / "Tools" / "py" / "u4pak.py"
STAGE = ROOT / "looks_build"
# The number puts it before the mod's pak where both have a file: Unreal ranks <name>_<n>_P.pak above <name>_P.pak.
OUT_PAK = GAME / "Dungeons" / "Content" / "Paks" / "~mods" / "SequelLooks_2_P.pak"
OLD_PAKS = [OUT_PAK.with_name("SequelLooks_P.pak")]
MOD_BUILD = ROOT / "build"


def gameplay_file(item):
    found = [f for f in EXTRACT.rglob(f"BP_{item}Instance.uasset") if "/Equipment/" in f.as_posix()]
    if len(found) != 1:
        sys.exit(f"{item}: no single gameplay file found ({len(found)}) - check the name in NAMES.md")
    return found[0]


def kind(file):
    """Armor, MeleeWeapons or RangedWeapons: the folder under Actors/Equipment."""
    parts = file.relative_to(EXTRACT).parts
    return parts[parts.index("Equipment") + 1]


def game_path(file):
    """/Game/... package path of an extracted file."""
    rel = file.relative_to(EXTRACT / "Dungeons" / "Content").with_suffix("")
    return "/Game/" + rel.as_posix()


def swap(item, look):
    src, donor = gameplay_file(item), gameplay_file(look)
    if kind(src) != kind(donor):
        sys.exit(f"{item} ({kind(src)}) can't wear {look} ({kind(donor)}): same kind only")
    rel = src.relative_to(EXTRACT)
    modded = MOD_BUILD / rel
    if modded.exists():   # the mod's pak changes this file too (stats): start from its version, so they stay
        src = modded
    look_file = donor.with_name(f"BP_{look}.uasset")
    if not look_file.exists():
        sys.exit(f"{look}: no look file {look_file.name}")
    pkg = Package(src)
    cdo = f"Default__BP_{item}Instance_C"
    before = {p["name"]: p.get("value") for p in pkg.export_props(next(e for e in pkg.exports if e["name"] == cdo))}
    ref = ("/Script/Engine", "BlueprintGeneratedClass", game_path(look_file), f"BP_{look}_C")
    head, body = set_export_properties(pkg, cdo, [("GearActor", "object", ref)])
    out = STAGE / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(head)
    out.with_suffix(".uexp").write_bytes(body)
    after = Package(out)   # read back
    now = {p["name"]: p.get("value") for p in after.export_props(next(e for e in after.exports if e["name"] == cdo))}
    print(f"{item}: look {before.get('GearActor')} -> {now.get('GearActor')}")


def main(args):
    if pid_of():
        sys.exit("Close the game first: it keeps its mod files open while it runs.")
    if STAGE.exists():
        shutil.rmtree(STAGE)
    for old in OLD_PAKS:
        if old.exists():
            old.unlink()
    if args == ["--off"] or not args:
        if OUT_PAK.exists():
            OUT_PAK.unlink()
            print(f"Removed {OUT_PAK.name}: every item looks like itself again.")
        return
    for a in args:
        item, _, look = a.partition("=")
        swap(item.strip(), look.strip())
    subprocess.run([sys.executable, str(U4PAK), "pack", str(OUT_PAK), "Dungeons"], cwd=STAGE, check=True)
    print(f"Wrote {OUT_PAK}")


if __name__ == "__main__":
    main(sys.argv[1:])
