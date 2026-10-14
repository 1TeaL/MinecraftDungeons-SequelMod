"""Read-only: every merchant's pricing component in the running game, with the merchant it belongs to."""
import struct, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from aplus_patch import open_game
from endless_patch import find_pointers
from memprobe import read
PVT, DVT = 0x34C39C8, 0x334BC28

def merchants(h, base):
    """[(pricing object, merchant name, currency bytes, base price, second int)]"""
    found = find_pointers(h, [base + PVT, base + DVT])
    by_class = {}
    for dobj in found[base + DVT]:
        raw = read(h, dobj, 0x70)
        sp, sn = struct.unpack_from("<QI", raw, 0x30)
        name = (read(h, sp, sn * 2) or b"").decode("utf-16le", "ignore").split("\0")[0] if sp and 0 < sn < 64 else ""
        actor_class = struct.unpack_from("<Q", raw, 0x28)[0]
        if actor_class and name:
            by_class[actor_class] = (name, raw[0x68:0x6a].hex())
    out = []
    for o in found[base + PVT]:
        raw = read(h, o, 0x48); owner = struct.unpack_from("<Q", raw, 0x28)[0]
        cls = struct.unpack("<Q", read(h, owner + 0x10, 8))[0] if owner else 0
        name, cur = by_class.get(cls, ("?", "?"))
        out.append((o, name, cur, struct.unpack_from("<i", raw, 0x30)[0], struct.unpack_from("<i", raw, 0x38)[0]))
    return out

if __name__ == "__main__":
    h, base = open_game()
    for o, name, cur, price, second in sorted(merchants(h, base), key=lambda x: x[1]):
        print(f"{o:#x}  {name:32} bytes {cur}  base {price:4}  second {second}")
