"""Test: give one item the mission drop list of another, in the running game (data only).

    python research/drops_test.py MeleeWeapons/Sword_Spooky1 MeleeWeapons/Sword_Unique1

An item definition holds, at +0xB0, a map from level id (one byte) to that level's drop settings: a TSet with
0x50-byte elements (key at +0, hash links at +0x48 / +0x4C), allocation bits inline at +0xC0, hash at +0xE8/+0xF0
with its size at +0xF8, and a flag byte at +0x100 (1 on every item that has a list). Seasonal and Tower-only
items have an empty map. This copies the donor's elements and hash into new memory and points the target at the
copies, so the two items do not share buffers.
"""
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from aplus_patch import open_game  # noqa: E402
from builtins_patch import alloc, write  # noqa: E402
from memprobe import read  # noqa: E402

REG = json.loads((Path(__file__).resolve().parent.parent / "tools" / "item_registry.json").read_text())
MAP, FLAG, ELEMENT = 0xB0, 0x100, 0x50

h, base = open_game()
if not h:
    sys.exit("game not running")
target, donor = sys.argv[1], sys.argv[2]
tp = struct.unpack("<Q", read(h, base + int(REG[target], 16), 8))[0]
dp = struct.unpack("<Q", read(h, base + int(REG[donor], 16), 8))[0]
box = bytearray(read(h, dp + MAP, FLAG - MAP))
data, num, room = struct.unpack_from("<QII", box, 0)
hash_ptr, hash_size = struct.unpack_from("<Q", box, 0x40)[0], struct.unpack_from("<I", box, 0x48)[0]
tnum = struct.unpack("<I", read(h, tp + MAP + 8, 4))[0]
if tnum or not 0 < num <= 128 or room < num or hash_size not in (1, 2, 4, 8, 16, 32, 64, 128, 256):
    sys.exit(f"unexpected: target has {tnum} entries, donor {num}/{room}, hash {hash_size}")
new_data = alloc(h, room * ELEMENT)
write(h, new_data, read(h, data, room * ELEMENT))
struct.pack_into("<Q", box, 0, new_data)
if hash_size > 1:
    new_hash = alloc(h, hash_size * 4)
    write(h, new_hash, read(h, hash_ptr, hash_size * 4))
    struct.pack_into("<Q", box, 0x40, new_hash)
write(h, tp + MAP, bytes(box))
write(h, tp + FLAG, read(h, dp + FLAG, 1))
print(f"{target}: now has the {num} mission entries of {donor}")
