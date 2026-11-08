"""Which native class owns a reflected property / function name, and its offset (exe dump).

    python research/prop_owner.py OnAnyPlayerKilledMob OnMobKilled ...

A property's params struct starts with a pointer to its UTF-8 name (offset 36 bytes in). The class's property list
is an array of pointers to those structs, referenced by the class's FClassParams, whose first field is the class's
StaticClass function; that function loads the class's wide name. Also prints a delegate signature's parameters
(the params struct's last pointer is the signature's construct function, which loads its FFunctionParams).
"""
import re
import struct
import sys
from pathlib import Path

d = (Path(__file__).with_name("dungeons_image.bin")).read_bytes()
BASE = 0x7ff6b16e0000
TEXT = 0x3000000


def q(off):
    return struct.unpack_from("<Q", d, off)[0]


def cstr(addr):
    a = addr - BASE
    return d[a:d.index(b"\0", a)].decode(errors="replace")


def refs(addr):
    return [m.start() for m in re.finditer(re.escape(struct.pack("<Q", addr)), d) if m.start() % 8 == 0]


def wide_at(off):
    end = off
    while d[end:end + 2] != b"\0\0":
        end += 2
    return d[off:end].decode("utf-16le", errors="replace")


def class_of_static(fn):
    """The wide class name a StaticClass function loads (lea rdx/rcx/r8, [rip+X] to a wide string)."""
    for i in range(fn, fn + 0x80):
        if d[i] in (0x48, 0x4C) and d[i + 1] == 0x8D and (d[i + 2] & 0xC7) == 0x05:
            t = i + 7 + struct.unpack_from("<i", d, i + 3)[0]
            if 0 < t < len(d) - 4 and d[t + 1] == 0 and 0x41 <= d[t] <= 0x5A:
                s = wide_at(t)
                if len(s) > 3 and s.isidentifier():
                    return s
    return None


def owners(name):
    out = []
    for m in re.finditer(b"\0" + name.encode() + b"\0", d):
        for p in refs(BASE + m.start() + 1):
            offset = struct.unpack_from("<I", d, p + 36)[0]
            # the property list: an array holding BASE + p
            for a in refs(BASE + p):
                start = a
                while q(start - 8) - BASE > TEXT and q(start - 8) - BASE < len(d):   # walk to the array's start
                    start -= 8
                for c in refs(BASE + start):
                    fn = q(c - 0x30) - BASE if False else None
                    # FClassParams: ClassNoRegisterFunc first; the array pointer a few fields in
                    for back in range(8, 0x60, 8):
                        f = q(c - back) - BASE
                        if 0 < f < TEXT:
                            cls = class_of_static(f)
                            if cls:
                                out.append((cls, offset, p))
                                break
    return out


for name in sys.argv[1:]:
    found = owners(name)
    print(name, sorted(set((c, hex(o)) for c, o, _ in found)) or "no owner found")
