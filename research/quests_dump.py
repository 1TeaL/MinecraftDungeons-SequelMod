"""List the merchants' quest objects in the running game (read-only)."""
import os, struct, sys, time
sys.path.insert(0, "tools")
import aplus_patch, play, endless_patch as ep
from memprobe import read, main_module
if not aplus_patch.pid_of():
    os.startfile("steam://rungameid/1672970")
t = time.time()
while time.time() - t < 220:
    h, base = aplus_patch.open_game()
    if h and aplus_patch.unpacked(h, base) and play.game_age(h) >= 60:
        break
    time.sleep(2)
else:
    sys.exit("game did not start")
size = main_module(h)[1]
cls = struct.unpack("<Q", read(h, base + 0x4548B40, 8))[0]
print("quest class", hex(cls))
hits = ep.find_pointers(h, [cls])[cls]
objs = []
for a in hits:
    o = a - 0x10
    raw = read(h, o, 0x90)
    if not raw: continue
    vt = struct.unpack_from("<Q", raw, 0)[0]
    if base <= vt < base + size:
        objs.append((o, raw))
print(len(objs), "objects")
for o, raw in objs:
    vt, flags, idx, cl, name, num, outer = struct.unpack_from("<QIIQIIQ", raw, 0)
    print(f"0x{o:X} vt exe+0x{vt-base:X} name#{name}_{num} outer 0x{outer:X} +0x28 {raw[0x28:0x40].hex(' ')} | +0x38 {raw[0x38]:d}")
