import sys, struct, json
sys.path.insert(0, 'tools')
import aplus_patch as a
from memprobe import read
h, base = a.open_game()
G = json.load(open('tools/item_registry.json'))
q = lambda addr: struct.unpack('<Q', read(h, addr, 8))[0]
for path in sys.argv[1:]:
    g = int(G[path], 16)
    p = q(base + g)
    blob = read(h, p, 0x400)
    hits = []
    for off in range(0, 0x400 - 16, 8):
        ptr, n, m = struct.unpack_from('<QII', blob, off)
        if 0 < n <= 4 and n <= m <= 16 and ptr > 0x10000:
            el = read(h, ptr, 0x14 * n) or b''
            ids = [el[i * 0x14] for i in range(n)] if len(el) == 0x14 * n else []
            lv = [struct.unpack_from('<i', el, i * 0x14 + 4)[0] for i in range(n)] if ids else []
            if ids and all(0 < x < 200 for x in ids) and all(1 <= l <= 3 for l in lv):
                hits.append((hex(off), n, ids, lv))
    print(path, '', hits)
