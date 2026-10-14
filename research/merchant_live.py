"""Read-only: merchant definitions in the running game and what they point at."""
import struct, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from artifact_fields import class_info
from aplus_patch import open_game
from endless_patch import find_pointers
from memprobe import read, main_module
h, base = open_game(); size = main_module(h)[1]
def dump(a, n, label):
    raw = read(h, a, n)
    if not raw: print(label, "unreadable"); return b""
    print(label, hex(a))
    for off in range(0, n, 16):
        row = raw[off:off+16]
        fl = " ".join(f"{x:9.4g}" if 1e-3 < abs(x) < 1e7 else "        ." for x in struct.unpack(f"<{len(row)//4}f", row))
        print(f"   +{off:03x} {row.hex(' ', 4)}   {fl}")
    return raw
names = sys.argv[1:] or ["EnchantmentMerchantDef", "PiglinMerchantDef"]
for name in names:
    ctor, sz, vt = class_info(name)
    objs = find_pointers(h, [base + vt])[base + vt]
    print("==", name, "vtable", hex(vt), "objects", [hex(o) for o in objs])
    for o in objs[:2]:
        raw = dump(o, 0x70, name)
        for off in (0x28, 0x50, 0x58):
            p = struct.unpack_from("<Q", raw, off)[0]
            if p > 0x10000 and not base <= p < base + size:
                dump(p, 0x80, f"  -> [{off:#x}]")
