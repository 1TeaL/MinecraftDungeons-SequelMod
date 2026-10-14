"""Read-only: compare item definitions byte by byte (running game), to find what marks a seasonal item.

    python research/def_diff.py MeleeWeapons/Sword_Spooky1 MeleeWeapons/Sword_Unique1 [more pairs...]
"""
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from aplus_patch import open_game  # noqa: E402
from memprobe import read  # noqa: E402

REG = json.loads((Path(__file__).resolve().parent.parent / "tools" / "item_registry.json").read_text())
SIZE = 0x260
h, base = open_game()
if not h:
    sys.exit("game not running")


def definition(name):
    p = struct.unpack("<Q", read(h, base + int(REG[name], 16), 8))[0]
    return p, read(h, p, SIZE)


names = sys.argv[1:]
for a, b in zip(names[::2], names[1::2]):
    (pa, da), (pb, db) = definition(a), definition(b)
    print(f"== {a} ({pa:#x})  vs  {b} ({pb:#x})")
    for off in range(0, SIZE, 4):
        x, y = da[off:off + 4], db[off:off + 4]
        if x != y:
            fx, fy = struct.unpack("<f", x)[0], struct.unpack("<f", y)[0]
            print(f"   +{off:#05x}  {x.hex()}  {y.hex()}   ints {struct.unpack('<i', x)[0]} / {struct.unpack('<i', y)[0]}"
                  + (f"   floats {fx:g} / {fy:g}" if 1e-3 < abs(fx) < 1e6 and 1e-3 < abs(fy) < 1e6 else ""))
