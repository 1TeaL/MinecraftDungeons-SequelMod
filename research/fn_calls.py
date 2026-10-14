"""A function's skeleton from the exe dump: its calls, the strings and globals it points at, immediates it stores.

    python research/fn_calls.py <exe offset hex> [max bytes] [--all]

--all prints every instruction (with the same notes). Used to compare how two items are registered.
"""
import re
import struct
import sys
from pathlib import Path

from capstone import CS_ARCH_X86, CS_MODE_64, Cs

d = Path(__file__).with_name("dungeons_image.bin").read_bytes()
md = Cs(CS_ARCH_X86, CS_MODE_64)


def text_at(t):
    """A short description of what is at an exe offset: an ASCII or wide string, or nothing."""
    if not 0 < t < len(d) - 16:
        return ""
    m = re.match(rb"[\x20-\x7e]{3,60}\x00", d[t:t + 64])
    if m:
        return '"' + m.group()[:-1].decode() + '"'
    m = re.match(rb"(?:[\x20-\x7e]\x00){3,60}\x00\x00", d[t:t + 130])
    if m:
        return 'L"' + m.group()[:-2].decode("utf-16le") + '"'
    return ""


def skeleton(start, limit=0x1000, everything=False):
    out = []
    for ins in md.disasm(d[start:start + limit], start):
        note = ""
        if "rip" in ins.op_str:
            t = ins.address + ins.size + int(ins.op_str.split("rip")[1].split("]")[0].replace(" ", ""), 16)
            note = f"-> {t:#x} {text_at(t)}"
            if "ss" in ins.mnemonic and 0 < t < len(d) - 4:
                note += f" = {struct.unpack_from('<f', d, t)[0]:g}"
        elif ins.mnemonic in ("call", "jmp") and ins.op_str.startswith("0x"):
            note = "CALL" if ins.mnemonic == "call" else ""
        elif ins.mnemonic == "mov" and re.search(r", (0x[0-9a-f]+|\d+)$", ins.op_str):
            v = int(ins.op_str.split(",")[-1], 0)
            f = struct.unpack("<f", struct.pack("<I", v & 0xFFFFFFFF))[0]
            note = f"imm {v}" + (f" (float {f:g})" if 1e-3 < abs(f) < 1e7 and v > 0xFFFF else "")
        if everything or note:
            out.append(f"{ins.address:#x} {ins.mnemonic} {ins.op_str}   {note}")
        if ins.mnemonic == "ret" and d[ins.address + 1] == 0xCC:
            break
    return out


if __name__ == "__main__":
    start = int(sys.argv[1], 16)
    limit = int(sys.argv[2], 16) if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else 0x1000
    print("\n".join(skeleton(start, limit, "--all" in sys.argv)))
