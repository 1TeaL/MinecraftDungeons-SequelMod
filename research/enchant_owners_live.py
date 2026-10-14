"""Read-only: live enchantment objects of some classes and who owns them (run in a mission with enchanted mobs).

    python research/enchant_owners_live.py [Deflecting Thorns LevitationRanged ...]

For each object: its tier (+0x1D8), its owner (+0xE8), the owner's class vtable and the owner's byte at +0x118
(the game's own code tests that byte for 3 before a deflect), and the object's own floats past the base class.
Purpose: learn how to tell a mob's copy of an enchantment from the player's, so the launcher can weaken or switch
off only the mobs' copies (per object, like tools/formula_patch.py and tools/echo_patch.py).
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from artifact_fields import class_info  # noqa: E402
from aplus_patch import open_game  # noqa: E402
from endless_patch import find_pointers  # noqa: E402
from memprobe import main_module, read  # noqa: E402

LEVEL, OWNER, BASE_SIZE = 0x1D8, 0xE8, 0x1F8

h, base = open_game()
if not h:
    sys.exit("game not running")
size = main_module(h)[1]
names = sys.argv[1:] or ["Deflecting", "Thorns", "LevitationRanged", "LevitationMelee", "Levitation"]
vts = {}
for name in names:
    ctor, obj_size, vt = class_info(name)
    if vt:
        vts[name] = (base + vt, obj_size)
    else:
        print(name, ": class not found in the exe dump")
found = find_pointers(h, [v for v, _ in vts.values()])
for name, (vt, obj_size) in vts.items():
    objs = found[vt]
    print(f"== {name}: {len(objs)} objects, size {obj_size:#x}")
    for o in objs[:40]:
        raw = read(h, o, obj_size)
        if not raw:
            continue
        owner = struct.unpack_from("<Q", raw, OWNER)[0]
        head = read(h, owner, 0x120) if owner else None
        owner_vt = struct.unpack_from("<Q", head)[0] - base if head else None
        tag = head[0x118] if head else None
        flags = struct.unpack_from("<I", raw, 8)[0]
        tail = raw[BASE_SIZE:obj_size]
        floats = " ".join(f"{x:g}" if 1e-4 < abs(x) < 1e6 else "." for x in struct.unpack(f"<{len(tail) // 4}f", tail[:len(tail) // 4 * 4]))
        print(f"  {o:#x} flags {flags:#x} tier {struct.unpack_from('<i', raw, LEVEL)[0]} owner {owner:#x} "
              f"owner class {'exe+%#x' % owner_vt if owner_vt and 0 < owner_vt < size else owner_vt} byte118 {tag} | {floats}")
