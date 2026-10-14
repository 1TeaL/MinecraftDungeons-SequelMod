"""Find each enchantment's definition global: registration functions call exe+0xA79EE0 with the type id in cl
and store the finished definition pointer in a global."""
import re, struct, json
from pathlib import Path
d = Path(__file__).with_name("dungeons_image.bin").read_bytes()
text = d[:0x3000000]
ids = json.loads((Path(__file__).parent.parent / "tools" / "enchant_ids.json").read_text())
names = {v: k for k, v in ids.items()}
out = {}
for m in re.finditer(rb"\xe8", text):
    i = m.start()
    if i + 5 + struct.unpack_from("<i", text, i + 1)[0] != 0xA79EE0:
        continue
    tid = None
    for back in range(2, 12):                      # mov cl, imm8 = b1 xx   /  xor ecx, ecx = 33 c9
        if text[i - back] == 0xB1: tid = text[i - back + 1]; break
        if text[i - back:i - back + 2] == b"\x33\xc9": tid = 0; break
    glob = None
    for j in range(i, i + 0x120):                  # mov [rip+X], rax = 48 89 05 disp32
        if text[j:j + 3] == b"\x48\x89\x05":
            glob = j + 7 + struct.unpack_from("<i", text, j + 3)[0]; break
    if tid is not None and glob:
        out[names.get(tid, str(tid))] = hex(glob)
print(len(out))
json.dump(out, open(Path(__file__).parent.parent / "tools" / "enchant_registry.json", "w"), indent=1)
print({k: out[k] for k in ("Echo", "FireAspect", "Leeching", "Swirling", "Weakening", "MultiShot", "Protection") if k in out})
