"""The player's movement settings (Build.toml [player]), built into the pak by `sequel.py build`.

The player character blueprint (Dungeons/Content/Actors/Characters/Player/BP_PlayerCharacter) keeps a few movement
numbers in its movement component (CharMoveComp): how much speed is left right after a roll
(DodgeEndSlowSpeedFactor, 0.8 in the game = a fifth slower) and the walking speed (MaxWalkSpeed, 700).
Only numbers the blueprint stores can be set; each is overwritten in place, so the file keeps its size.
The other two post-roll settings (braking and turning: DodgeEndSlowBrakingFactor, DodgeEndSlowRotationRateFactor)
and the length of the post-roll moment (PostDodgeDuration) are not stored in the blueprint and stay as they are.
"""
import struct
import settings
from pathlib import Path

from uasset import Package

ASSET = "Dungeons/Content/Actors/Characters/Player/BP_PlayerCharacter.uasset"
COMPONENT = "CharMoveComp"
SETTINGS = {"speed_after_roll": ("DodgeEndSlowSpeedFactor", 0.1, 2.0), "walk_speed": ("MaxWalkSpeed", 300.0, 1400.0)}


def build(build_root, extract_root, config):
    """Write the blueprint with Build.toml's movement numbers under build_root. Returns the files written."""
    src = Path(extract_root) / ASSET
    cfg = settings.load(config)
    if not src.exists() or not cfg:
        return []
    pkg = Package(src)
    export = next((e for e in pkg.exports if e["name"] == COMPONENT), None)
    props = {p["name"]: p for p in pkg.export_props(export)} if export else {}
    data, notes = bytearray(pkg.data), []
    for key, value in cfg.items():
        if key not in SETTINGS:
            raise SystemExit(f"Build.toml [player]: unknown setting {key!r} (known: {', '.join(SETTINGS)})")
        name, low, high = SETTINGS[key]
        p = props.get(name)
        if not p or p["type"] != "FloatProperty":
            raise SystemExit(f"Build.toml [player] {key}: the game's blueprint doesn't hold {name} - nothing built")
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not low <= value <= high:
            raise SystemExit(f"Build.toml [player] {key}: expected a number from {low:g} to {high:g}, got {value!r}")
        if abs(p["value"] - value) > 1e-6:
            struct.pack_into("<f", data, p["pos"], float(value))
            notes.append(f"{name}: {p['value']:g} -> {value:g}")
    if not notes:
        return []
    dest = Path(build_root) / ASSET
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(bytes(data[:len(pkg.head)]))
    dest.with_suffix(".uexp").write_bytes(bytes(data[len(pkg.head):]))
    check = Package(dest)                                   # read back what was written
    again = {p["name"]: p["value"] for p in check.export_props(next(e for e in check.exports if e["name"] == COMPONENT))}
    for key, value in cfg.items():
        if abs(again[SETTINGS[key][0]] - value) > 1e-4:
            raise SystemExit(f"Build.toml [player] {key}: wrote {value!r}, read back {again[SETTINGS[key][0]]!r}")
    for note in notes:
        print(f"  player {note}")
    return [dest]


def changes(extract_root, config):
    """[(setting, game value, mod value)] for the change sheet."""
    src = Path(extract_root) / ASSET
    cfg = settings.load(config)
    if not src.exists() or not cfg:
        return []
    pkg = Package(src)
    props = {p["name"]: p["value"] for p in pkg.export_props(next(e for e in pkg.exports if e["name"] == COMPONENT))}
    return [(key, props.get(SETTINGS[key][0]), value) for key, value in cfg.items()
            if key in SETTINGS and abs(props.get(SETTINGS[key][0], value) - value) > 1e-6]
