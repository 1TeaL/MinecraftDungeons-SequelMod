"""Find the exec thunk registered for a UFunction name (FNameNativePtrPair tables in the exe dump)."""
import re, struct, sys
from pathlib import Path
d = Path(__file__).with_name("dungeons_image.bin").read_bytes()
BASE = 0x7ff6b16e0000   # exe base when the image was dumped
for name in sys.argv[1:]:
    for m in re.finditer(re.escape(name.encode()) + b"\x00", d):
        s = m.start()
        if d[s - 1] != 0:
            continue
        ref = struct.pack("<Q", BASE + s)
        for r in re.finditer(re.escape(ref), d):
            thunk = struct.unpack_from("<Q", d, r.start() + 8)[0] - BASE
            if 0 < thunk < 0x3100000:
                print(name, "thunk exe+0x%X" % thunk)
