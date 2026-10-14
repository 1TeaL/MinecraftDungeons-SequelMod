"""Dump every enchantment definition from the running game: header bytes and the optional list at +8."""
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from aplus_patch import open_game  # noqa: E402
from memprobe import read  # noqa: E402

REG = json.loads((Path(__file__).resolve().parent.parent / "tools" / "enchant_registry.json").read_text())
h, base = open_game()
if not h:
    sys.exit("game not running")
for name, glob in sorted(REG.items()):
    raw = read(h, base + int(glob, 16), 8)
    d = struct.unpack("<Q", raw)[0] if raw else 0
    body = read(h, d, 0x40) if d else None
    if not body:
        print(f"{name:26} -")
        continue
    data, count, cap = struct.unpack_from("<QII", body, 8)
    arr = read(h, data, min(count, 16)) if data and 0 < count <= 64 else b""
    print(f"{name:26} {body[:8].hex()} n={count:<2} cap={cap:<2} [{(arr or b'').hex()}]  {body[0x18:0x40].hex()}")
