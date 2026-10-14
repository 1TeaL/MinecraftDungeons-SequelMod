import sys, struct
sys.path.insert(0, 'tools')
import aplus_patch as a
from memprobe import read
h, base = a.open_game()
q = lambda addr: struct.unpack('<Q', read(h, addr, 8))[0]
for g in (0x44F1420, 0x44F1428):
    print(hex(g), hex(q(base + g)))
p = q(base + 0x44F1428)
blob = read(h, p, 0x200)
for off in range(0, 0x200, 16):
    print(f"+{off:03X} " + blob[off:off+16].hex(' '))
# look for TArray-like (ptr, count, max) whose first element starts with 05 00 00 00 01 00 00 00
for off in range(0, 0x200, 8):
    ptr, n, m = struct.unpack_from('<QII', blob, off) if off + 16 <= len(blob) else (0, 0, 0)
    if 0 < n <= 8 and n <= m <= 64 and ptr > 0x10000:
        el = read(h, ptr, 0x14 * n)
        if el:
            print(f"array at +{off:X}: n={n} first: {el[:0x14].hex(' ')}")
