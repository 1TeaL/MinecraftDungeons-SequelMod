"""Read-only: list live inventory items (vtable exe+0x346FCF8) and try to link each to its item definition."""
import struct, sys, json, ctypes
sys.path.insert(0, "tools")
import endless_patch as ep
from memprobe import read, main_module
h, base = ep.open_game()
if not h: sys.exit("game not running")
size = main_module(h)[1]
VT = base + 0x346FCF8
reg = json.load(open("tools/item_registry.json"))
defs = {struct.unpack("<Q", read(h, base + int(g, 16), 8))[0]: k for k, g in reg.items()}
items = ep.find_pointers(h, [VT])[VT]
print(len(items), "item objects")
rows = []
for o in items:
    r = read(h, o, 0x140)
    if not r: continue
    fn, num = struct.unpack_from("<II", r, 0x34); power = struct.unpack_from("<f", r, 0x3C)[0]
    link = [(off, defs[v]) for off in range(0, 0x140, 8) for v in [struct.unpack_from("<Q", r, off)[0]] if v in defs]
    rows.append((o, fn, num, power, link))
import collections
print("with a definition pointer:", sum(1 for r in rows if r[4]), "offsets used:", collections.Counter(off for r in rows for off, _ in r[4]))
for o, fn, num, power, link in rows[:12]:
    print(hex(o), fn, num, round((power - 1) * 10 + 1), link)
by = collections.defaultdict(set)
for o, fn, num, power, link in rows:
    for off, name in link: by[fn].add(name)
print("FName ids mapping to exactly one type:", sum(1 for v in by.values() if len(v) == 1), "of", len(by))
json.dump({str(k): sorted(v) for k, v in by.items()}, open("research/fname_types.json", "w"), indent=0)
