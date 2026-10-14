"""Find RIP-relative references to given exe offsets (modrm mod=00 rm=101, disp32, optional imm8)."""
import re, struct, sys
from pathlib import Path
data = Path(__file__).with_name("dungeons_image.bin").read_bytes()
text = data[:0x3000000]
targets = {int(t, 16): t for t in sys.argv[1].split(",")}
for m in re.finditer(rb"[\x05\x0d\x15\x1d\x25\x2d\x35\x3d]", text):
    i = m.start()
    disp = struct.unpack_from("<i", text, i + 1)[0]
    for extra in (0, 1, 4):
        t = i + 5 + extra + disp
        if t in targets:
            print(f"{targets[t]} imm{extra}: modrm at 0x{i:X} ctx {text[i-6:i+5].hex(' ')}")
