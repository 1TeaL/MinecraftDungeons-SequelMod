"""Tiny PNG reader / writer for 8-bit RGBA / RGB images (no Pillow needed): for the mod's own icon art.

    python tools/png_rgba.py in.png out.png [--clear-white]

--clear-white makes the near-white background around the picture transparent (flood fill from the corners, so
white inside the picture stays). Used for the user's enchantment icons (unreal/Art).
"""
import struct
import sys
import zlib


def read(path):
    data = open(path, "rb").read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    pos, idat, width = 8, b"", None
    while pos < len(data):
        size = struct.unpack(">I", data[pos:pos + 4])[0]
        kind, body = data[pos + 4:pos + 8], data[pos + 8:pos + 8 + size]
        if kind == b"IHDR":
            width, height, depth, color, _, _, interlace = struct.unpack(">IIBBBBB", body)
            assert depth == 8 and color in (2, 6) and interlace == 0, "only 8-bit RGB / RGBA, not interlaced"
        elif kind == b"IDAT":
            idat += body
        pos += 12 + size
    channels = 4 if color == 6 else 3
    raw, stride = zlib.decompress(idat), width * channels
    rows, prev, i = [], bytearray(stride), 0
    for _ in range(height):
        kind, line = raw[i], bytearray(raw[i + 1:i + 1 + stride])
        i += 1 + stride
        for x in range(stride):
            a = line[x - channels] if x >= channels else 0
            b, c = prev[x], prev[x - channels] if x >= channels else 0
            if kind == 1:
                line[x] = (line[x] + a) & 255
            elif kind == 2:
                line[x] = (line[x] + b) & 255
            elif kind == 3:
                line[x] = (line[x] + (a + b) // 2) & 255
            elif kind == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append(line)
        prev = line
    pixels = [[tuple(r[x * channels:x * channels + channels]) + ((255,) if channels == 3 else ()) for x in range(width)]
              for r in rows]
    return width, height, pixels


def write(path, width, height, pixels):
    raw = b"".join(b"\x00" + bytes(v for px in row for v in px) for row in pixels)
    def chunk(kind, body):
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)
    open(path, "wb").write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
                           + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def clear_white(width, height, pixels, limit=235):
    seen, todo = set(), [(0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)]
    while todo:
        x, y = todo.pop()
        if (x, y) in seen or not (0 <= x < width and 0 <= y < height):
            continue
        seen.add((x, y))
        r, g, b, a = pixels[y][x]
        if a == 0 or min(r, g, b) >= limit:
            pixels[y][x] = (0, 0, 0, 0)
            todo += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    return pixels


if __name__ == "__main__":
    w, h, px = read(sys.argv[1])
    if "--clear-white" in sys.argv:
        px = clear_white(w, h, px)
    write(sys.argv[2], w, h, px)
    print("wrote", sys.argv[2], w, "x", h, "- corner", px[0][0], "centre", px[h // 2][w // 2])
