"""Read and patch UE4 .locres files (version 2, as used by Minecraft Dungeons).

Only the localized-string array is rewritten. Each changed key gets its own new string appended to
the array, so strings shared with other keys stay untouched, and the namespace/key tables (with
their hashes) keep their exact bytes.
"""
import struct


def _fstring(d, p):
    n = struct.unpack_from("<i", d, p)[0]
    p += 4
    if n >= 0:
        return d[p:p + n - 1].decode("latin-1") if n else "", p + n
    return d[p:p - 2 * n - 2].decode("utf-16-le"), p - 2 * n


def _write_fstring(s):
    try:
        raw = s.encode("ascii") + b"\0"
        return struct.pack("<i", len(raw)) + raw
    except UnicodeEncodeError:
        raw = s.encode("utf-16-le") + b"\0\0"
        return struct.pack("<i", -(len(raw) // 2)) + raw


class Locres:
    def __init__(self, data):
        self.data = bytearray(data)
        d = self.data
        p = 16
        self.version = d[p]
        p += 1
        assert self.version == 2, f"unsupported locres version {self.version}"
        self.array_off_pos = p
        self.array_off = struct.unpack_from("<q", d, p)[0]
        p += 8 + 4  # entries count
        q = self.array_off
        n = struct.unpack_from("<i", d, q)[0]
        q += 4
        self.strings = []
        for _ in range(n):
            s, q = _fstring(d, q)
            ref = struct.unpack_from("<i", d, q)[0]
            q += 4
            self.strings.append([s, ref])
        self.keys = {}  # "Namespace/Key" -> position of its string index
        ns_count = struct.unpack_from("<I", d, p)[0]
        p += 4
        for _ in range(ns_count):
            p += 4
            ns, p = _fstring(d, p)
            kc = struct.unpack_from("<I", d, p)[0]
            p += 4
            for _ in range(kc):
                p += 4
                k, p = _fstring(d, p)
                p += 4  # source string hash
                self.keys[f"{ns}/{k}"] = p
                p += 4
        assert p <= self.array_off

    def get(self, key):
        return self.strings[struct.unpack_from("<i", self.data, self.keys[key])[0]][0]

    def set(self, key, text):
        pos = self.keys[key]
        old = struct.unpack_from("<i", self.data, pos)[0]
        self.strings[old][1] -= 1
        self.strings.append([text, 1])
        struct.pack_into("<i", self.data, pos, len(self.strings) - 1)

    def to_bytes(self):
        out = bytearray(self.data[:self.array_off])
        out += struct.pack("<i", len(self.strings))
        for s, ref in self.strings:
            out += _write_fstring(s) + struct.pack("<i", ref)
        return bytes(out)
