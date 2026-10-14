"""List code that clamps with the shared 3.0 float (minss/minps with [rip -> exe+0x3101950]) and code that
uses the 1.25 base (exe+0x3241210)."""
import re, struct
from pathlib import Path
d = Path(__file__).with_name("dungeons_image.bin").read_bytes()
text = d[:0x3000000]
def fn_start(i):
    j = i
    while not (text[j-1] == 0xCC and text[j] != 0xCC and j % 16 == 0): j -= 1
    return j
for target, name in ((0x3101950, "3.0"), (0x3241210, "1.25")):
    print("==", name)
    for m in re.finditer(rb"\x0f[\x5d\x10\x59\x5f\x2f\x2e\x5e\x58\x5c][\x05\x0d\x15\x1d\x25\x2d\x35\x3d]", text):
        i = m.start() + 2
        t = i + 5 + struct.unpack_from("<i", text, i + 1)[0]
        if t == target:
            op = {0x5d: "min", 0x10: "mov", 0x59: "mul", 0x5f: "max", 0x2f: "comiss", 0x2e: "ucomiss", 0x5e: "div", 0x58: "add", 0x5c: "sub"}[text[m.start()+1]]
            if name == "3.0" and op != "min": continue
            print(f"  {op:6} at 0x{m.start():X} (fn 0x{fn_start(m.start()):X})")
