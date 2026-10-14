"""Read-only: the player's attribute sets in the running game (plain floats; offsets from the exe's reflection data)."""
import struct, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from artifact_fields import class_info
from aplus_patch import open_game
from endless_patch import find_pointers
from memprobe import read
SETS = {"HealthAttributeSet": 0x70, "MeleeAttributeSet": 0x60, "RangedAttributeSet": 0x60, "ItemAttributeSet": 0x60}
h, base = open_game()
vts = {}
for name in SETS:
    ctor, size, vt = class_info(name)
    print(name, "ctor", hex(ctor or 0), "size", hex(size or 0), "vtable", hex(vt or 0))
    if vt:
        vts[name] = base + vt
found = find_pointers(h, list(vts.values()))
for name, vt in vts.items():
    for o in found[vt][:12]:
        raw = read(h, o + 0x28, SETS[name] + 0x20)
        print(f"  {name} {o:#x} +0x28: " + " ".join(f"{x:.4g}" for x in struct.unpack(f"<{len(raw)//4}f", raw)))
