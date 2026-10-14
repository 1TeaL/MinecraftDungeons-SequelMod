"""Find direct calls/jmps (E8/E9 rel32) to given exe offsets."""
import re, struct, sys
from pathlib import Path
data = Path(__file__).with_name("dungeons_image.bin").read_bytes()
text = data[:0x3000000]
targets = {int(t, 16): t for t in sys.argv[1].split(",")}
for m in re.finditer(rb"[\xe8\xe9]", text):
    i = m.start()
    if i + 5 > len(text): break
    t = i + 5 + struct.unpack_from("<i", text, i + 1)[0]
    if t in targets:
        j = i
        while not (text[j-1] == 0xCC and text[j] != 0xCC): j -= 1
        print(f"{targets[t]} <- {'call' if text[i]==0xE8 else 'jmp '} at 0x{i:X} (fn 0x{j:X} +0x{i-j:X})")
