"""Static scan of the exe dump: item path -> global holding its registered definition.

Each item is registered by its own function: it references the item path ("MeleeWeapons/Axe_Unique1"),
builds the definition (call exe+0xB1A520), inserts it into a category registry (a further call) and stores
the returned pointer in a per-item global (mov qword ptr [rip+disp32], rax). Built-in enchantments are
created with exe+0xAD8970(out, TypeID=dl, Level=r8d, ...)."""
import re, struct, json
from pathlib import Path
d = Path(__file__).with_name("dungeons_image.bin").read_bytes()
text = d[:0x3000000]
BUILD, MAKE_ENCH = 0xB1A520, 0xAD8970
PATH = re.compile(rb"((?:MeleeWeapons|RangedWeapons|Armor|Items)/[A-Za-z0-9_]+)\x00")


def fn_start(i):
    while not (text[i - 1] == 0xCC and text[i] != 0xCC):
        i -= 1
    return i


def call_target(i):
    return i + 5 + struct.unpack_from("<i", text, i + 1)[0]


funcs = {}
for m in re.finditer(rb"[\x48\x4c]\x8d[\x05\x0d\x15\x1d\x25\x2d\x35\x3d]", text):   # lea reg, [rip+disp]
    k = m.start()
    tgt = k + 7 + struct.unpack_from("<i", text, k + 3)[0]
    if 0 < tgt < len(d) - 80:
        pm = PATH.match(d[tgt:tgt + 80])
        if pm:
            funcs.setdefault(fn_start(k), pm.group(1).decode())
out = {}
starts = sorted(funcs)
for n, f in enumerate(starts):
    path = funcs[f]
    limit = starts[n + 1] if n + 1 < len(starts) else f + 0x800
    body = text[f:min(f + 0x800, limit)]
    end = body.find(b"\xc3\xcc")                      # ret + int3 padding = end of this function
    body = body[:end + 1 if end > 0 else len(body)]
    builds = [i for i in range(len(body) - 5) if body[i] == 0xE8 and call_target(f + i) == BUILD]
    if not builds:
        continue
    glob = None
    for i in range(builds[-1], len(body) - 7):
        if body[i:i + 3] == b"\x48\x89\x05":
            glob = f + i + 7 + struct.unpack_from("<i", body, i + 3)[0]
            break
    # built-in enchantments: mov dl, imm8 ... call MAKE_ENCH ; level from r8d (lea r8d,[rsi+1] or mov r8d, imm)
    enchants = []
    for i in range(len(body) - 5):
        if body[i] == 0xE8 and call_target(f + i) == MAKE_ENCH:
            win = body[max(0, i - 40):i]
            t = [win[j + 2] for j in range(len(win) - 2) if win[j:j + 2] == b"\xb2"[:1] + b"" and False]
            tid = next((win[j + 1] for j in range(len(win) - 2, -1, -1) if win[j] == 0xB2), None)   # mov dl, imm8
            enchants.append(tid)
    out[path] = {"fn": hex(f), "global": hex(glob) if glob else None, "builtin_ids": enchants}
Path(__file__).with_name("item_globals.json").write_text(json.dumps(out, indent=1))
cats = {}
for p, v in out.items():
    cats.setdefault(p.split("/")[0], [0, 0])[0 if v["global"] else 1] += 1
print(cats)
from collections import Counter
dup = [g for g, c in Counter(v["global"] for v in out.values() if v["global"]).items() if c > 1]
print("duplicate globals:", dup)
for k in ["MeleeWeapons/Sword_Unique1", "MeleeWeapons/Sword_Unique2", "MeleeWeapons/Daggers_Unique3", "Armor/EmeraldArmor_Unique1"]:
    print(k, out.get(k))
