"""Dump the A+ unlock step objects from the running game (read-only)."""
import struct, sys
sys.path.insert(0, "tools")
import aplus_patch
from memprobe import read, main_module
h, base = aplus_patch.open_game()
if not h:
    sys.exit("game not running")
size = main_module(h)[1]
src = struct.unpack("<QII", read(h, base + 0x44EE690, 16))
cache = struct.unpack("<QII", read(h, base + 0x44EF430, 16))
print("source array", hex(src[0]), src[1:], "| cache", hex(cache[0]), cache[1:], "guard", struct.unpack("<i", read(h, base + 0x44EF440, 4))[0])
ptrs = struct.unpack("<%dQ" % src[1], read(h, src[0], 8 * src[1]))
if cache[0]:
    print("cache order:", [hex(p) for p in struct.unpack("<%dQ" % cache[1], read(h, cache[0], 8 * cache[1]))])
for n, p in enumerate(ptrs):
    o = read(h, p, 0x150)
    print(f"\nstep {n} at 0x{p:X}")
    for off in range(0, 0x150, 8):
        v = struct.unpack_from("<Q", o, off)[0]
        note = ""
        if base <= v < base + size:
            note = f"exe+0x{v - base:X}"
        elif p <= v < p + 0x150:
            note = f"self+0x{v - p:X}"
        elif v > 0x10000000000:
            note = "heap ptr"
        lo, hi = struct.unpack_from("<ii", o, off)
        print(f"  +0x{off:03X}  {v:016X}  {note or (lo, hi)}")
