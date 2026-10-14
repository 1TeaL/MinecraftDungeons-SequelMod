"""How is a function reached: direct calls/jmps (with the caller's start) and stored pointers."""
import re, struct, sys
from pathlib import Path
d = Path(__file__).with_name("dungeons_image.bin").read_bytes()
BASE = 0x7ff6b16e0000
text = d[:0x3000000]
CALLS = {}
for m in re.finditer(rb"[\xe8\xe9]", text):
    i = m.start()
    if i + 5 > len(text): break
    CALLS.setdefault(i + 5 + struct.unpack_from("<i", text, i + 1)[0], []).append(i)
def fn_start(i):
    j = i
    while not (text[j-1] == 0xCC and text[j] != 0xCC and j % 16 == 0): j -= 1
    return j
def reach(fn, depth=0, seen=None):
    seen = seen if seen is not None else set()
    if fn in seen or depth > 4: return
    seen.add(fn)
    ptrs = [m.start() for m in re.finditer(re.escape(struct.pack("<Q", BASE + fn)), d)]
    print("  " * depth + f"exe+0x{fn:X}: pointers at {[hex(p) for p in ptrs[:6]]}{' ...' if len(ptrs) > 6 else ''}")
    for site in CALLS.get(fn, [])[:12]:
        s = fn_start(site)
        print("  " * depth + f"  {'call' if text[site] == 0xE8 else 'jmp'} from 0x{site:X} in fn 0x{s:X}")
        reach(s, depth + 1, seen)
for a in sys.argv[1:]:
    reach(int(a, 16))
