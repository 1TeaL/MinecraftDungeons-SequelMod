"""Dev tool (read-only): save the running game's unpacked exe image so code can be studied offline.

    python tools/dumpimage.py [out_file]      # default research/dungeons_image.bin

The exe on disk is encrypted; once running it is unpacked in memory. The dump is laid out by RVA
(file offset == exe offset), unreadable pages are zero-filled.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from memprobe import k32, main_module, pid_of, read  # noqa: E402

PAGE = 0x1000

if __name__ == "__main__":
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "research" / "dungeons_image.bin"
    out.parent.mkdir(parents=True, exist_ok=True)
    h = k32.OpenProcess(0x0410, False, pid_of())
    base, size = main_module(h)
    missing = 0
    with open(out, "wb") as f:
        for off in range(0, size, 1 << 20):
            n = min(1 << 20, size - off)
            chunk = read(h, base + off, n)
            if chunk is None or len(chunk) != n:
                chunk = bytearray()
                for p in range(off, off + n, PAGE):
                    page = read(h, base + p, PAGE)
                    if page is None:
                        missing += 1
                        page = b"\0" * PAGE
                    chunk += page
            f.write(chunk)
    print(f"saved 0x{size:X} bytes to {out} ({missing} unreadable pages)")
