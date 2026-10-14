"""Find live inventory items in the running game (read-only): look for the test items' power value."""
import struct, sys, json
sys.path.insert(0, "tools")
import endless_patch as ep
from memprobe import read, main_module
h, base = ep.open_game()
size = main_module(h)[1]
target = struct.pack("<f", 1 + 324 / 10)
import ctypes
info = ep.MBI(); addr = 0x10000; hits = []
while ep.k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(info), ctypes.sizeof(info)):
    start, sz = info.BaseAddress or 0, info.RegionSize
    if info.State == 0x1000 and info.Type == 0x20000 and info.Protect == 0x04:
        for off in range(0, sz, 1 << 24):
            data = read(h, start + off, min(1 << 24, sz - off)) or b""
            i = data.find(target)
            while i >= 0:
                if i % 4 == 0: hits.append(start + off + i)
                i = data.find(target, i + 1)
    addr = start + sz
print(len(hits), "hits")
json.dump(hits, open("research/inv_hits.json", "w"))
for a in hits[:40]:
    ctx = read(h, a - 0x40, 0xC0) or b""
    q = [struct.unpack_from("<Q", ctx, o)[0] for o in range(0, 0xC0, 8)]
    tags = ["V" if base <= v < base + size else ("P" if 0x10000000000 < v < 0x7ff000000000 else ".") for v in q]
    print(hex(a), "".join(tags), ctx[0x38:0x50].hex(" "))
