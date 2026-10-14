"""Change artifacts' cooldown, soul cost and base duration in the running game (Artifacts.toml).
Data only: no game code is changed.

    python tools/artifacts_patch.py            # apply Artifacts.toml
    python tools/artifacts_patch.py --show     # list every artifact's current values

Each artifact's definition (a global, research/artifact_globals.json, like weapons and armor) holds three
floats: soul cost at +0x94, cooldown in seconds at +0x98, base duration in seconds at +0x9C. What the
artifact does, and most damage numbers, are in the game's code.
"""
import json
import struct
import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aplus_patch import open_game  # noqa: E402
from builtins_patch import write  # noqa: E402
from memprobe import read  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "Artifacts.toml"
GLOBALS = json.loads((ROOT / "research" / "artifact_globals.json").read_text())
FIELDS = {"souls": 0x94, "cooldown": 0x98, "duration": 0x9C}


def values(h, base, item):
    """(definition address, {field: value}) or (None, None)."""
    raw = read(h, base + int(GLOBALS[item], 16), 8)
    definition = struct.unpack("<Q", raw)[0] if raw else 0
    raw = read(h, definition + 0x94, 12) if definition else None
    if not raw:
        return None, None
    return definition, dict(zip(FIELDS, struct.unpack("<fff", raw)))


def apply(h, base):
    plan = tomllib.loads(CONFIG.read_text(encoding="utf-8")) if CONFIG.exists() else {}
    changed = 0
    for item, spec in plan.items():
        definition, cur = values(h, base, item) if item in GLOBALS else (None, None)
        bad = [k for k, v in spec.items() if k not in FIELDS or not isinstance(v, (int, float)) or not 0 <= v <= 600]
        if cur is None or bad or not 0 < cur["cooldown"] < 600:
            print(f"  ! {item}: " + (f"bad setting {bad}" if bad else "not found in the game") + " - skipped")
            continue
        for field, new in spec.items():
            if abs(cur[field] - new) > 1e-4:
                write(h, definition + FIELDS[field], struct.pack("<f", float(new)))
                print(f"  {item}: {field} {cur[field]:g} -> {new:g}")
                changed += 1
    print(f"artifacts: {changed} changed")


if __name__ == "__main__":
    h, base = open_game()
    if not h:
        sys.exit("Minecraft Dungeons isn't running")
    if "--show" in sys.argv:
        for item in sorted(GLOBALS):
            _, cur = values(h, base, item)
            if cur and 0 < cur["cooldown"] < 600:
                print(f"{item:28} cooldown {cur['cooldown']:5.1f}  souls {cur['souls']:3.0f}  duration {cur['duration']:4.1f}")
    else:
        apply(h, base)
