"""Read and write Minecraft Dungeons character saves (dev tool).

A save is "D001" + 4 zero bytes, then the character's JSON encrypted with AES-256 in ECB mode and padded
with zero bytes to a multiple of 16. The key is built by the game the first time it loads a save;
research/save_key.bin holds a copy read from the running game (std::string at exe+0x44F86B8).

    python tools/savefile.py decrypt <save.dat> <out.json>
    python tools/savefile.py encrypt <in.json> <save.dat>
"""
import sys
from pathlib import Path

KEY = Path(__file__).resolve().parent.parent / "research" / "save_key.bin"
MAGIC = b"D001\0\0\0\0"

SBOX = [0] * 256


def _init():
    p = q = 1
    while True:
        p = p ^ ((p << 1) & 0xFF) ^ (0x1B if p & 0x80 else 0)
        q ^= q << 1
        q ^= q << 2
        q ^= q << 4
        q &= 0xFF
        if q & 0x80:
            q ^= 0x09
        x = q ^ (q << 1 | q >> 7) & 0xFF ^ (q << 2 | q >> 6) & 0xFF ^ (q << 3 | q >> 5) & 0xFF ^ (q << 4 | q >> 4) & 0xFF
        SBOX[p] = (x ^ 0x63) & 0xFF
        if p == 1:
            break
    SBOX[0] = 0x63


_init()
INV = [0] * 256
for _i, _v in enumerate(SBOX):
    INV[_v] = _i


def _xt(a):
    return ((a << 1) ^ 0x1B) & 0xFF if a & 0x80 else a << 1


def _mul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a, b = _xt(a), b >> 1
    return r


M2, M3 = [_mul(i, 2) for i in range(256)], [_mul(i, 3) for i in range(256)]
M9, M11, M13, M14 = ([_mul(i, k) for i in range(256)] for k in (9, 11, 13, 14))


def expand(key):
    n = len(key) // 4
    w = [list(key[4 * i:4 * i + 4]) for i in range(n)]
    rcon = 1
    for i in range(n, 4 * (n + 7)):
        t = list(w[i - 1])
        if i % n == 0:
            t = [SBOX[t[1]] ^ rcon, SBOX[t[2]], SBOX[t[3]], SBOX[t[0]]]
            rcon = _xt(rcon)
        elif n > 6 and i % n == 4:
            t = [SBOX[b] for b in t]
        w.append([a ^ b for a, b in zip(w[i - n], t)])
    return [sum(w[4 * r:4 * r + 4], []) for r in range(n + 7)]


def _decrypt_block(b, rk):
    s = [x ^ k for x, k in zip(b, rk[-1])]
    for r in range(len(rk) - 2, -1, -1):
        s = [INV[s[(i - 4 * (i % 4)) % 16]] for i in range(16)]          # inverse ShiftRows + SubBytes
        s = [x ^ k for x, k in zip(s, rk[r])]
        if r:
            o = []
            for c in range(0, 16, 4):
                a, b_, c_, d = s[c:c + 4]
                o += [M14[a] ^ M11[b_] ^ M13[c_] ^ M9[d], M9[a] ^ M14[b_] ^ M11[c_] ^ M13[d],
                      M13[a] ^ M9[b_] ^ M14[c_] ^ M11[d], M11[a] ^ M13[b_] ^ M9[c_] ^ M14[d]]
            s = o
    return bytes(s)


def _encrypt_block(b, rk):
    s = [x ^ k for x, k in zip(b, rk[0])]
    for r in range(1, len(rk)):
        s = [SBOX[s[(i + 4 * (i % 4)) % 16]] for i in range(16)]         # SubBytes + ShiftRows
        if r < len(rk) - 1:
            o = []
            for c in range(0, 16, 4):
                a, b_, c_, d = s[c:c + 4]
                o += [M2[a] ^ M3[b_] ^ c_ ^ d, a ^ M2[b_] ^ M3[c_] ^ d, a ^ b_ ^ M2[c_] ^ M3[d], M3[a] ^ b_ ^ c_ ^ M2[d]]
            s = o
        s = [x ^ k for x, k in zip(s, rk[r])]
    return bytes(s)


def decrypt(data, key=None):
    """Save file bytes -> JSON text."""
    if data[:8] != MAGIC or (len(data) - 8) % 16:
        raise ValueError("not a Dungeons save")
    rk = expand(key or KEY.read_bytes())
    body = b"".join(_decrypt_block(data[i:i + 16], rk) for i in range(8, len(data), 16))
    return body.rstrip(b"\0").decode("utf-8")


def encrypt(text, key=None):
    """JSON text -> save file bytes."""
    rk = expand(key or KEY.read_bytes())
    body = text.encode("utf-8")
    body += b"\0" * (-len(body) % 16)
    return MAGIC + b"".join(_encrypt_block(body[i:i + 16], rk) for i in range(0, len(body), 16))


if __name__ == "__main__":
    mode, src, dst = sys.argv[1:4]
    if mode == "decrypt":
        Path(dst).write_text(decrypt(Path(src).read_bytes()), encoding="utf-8")
    else:
        Path(dst).write_bytes(encrypt(Path(src).read_text(encoding="utf-8")))
