"""Code in the exe dump that touches a struct field at a given offset (disp32 or disp8 addressing).

    python research/field_refs.py <offset hex> [byte|word|dword|qword|any] [--near <other offset hex>]

Lists each instruction with the start of its function. --near keeps only functions that also touch the other
offset (e.g. two fields of the same struct).
"""
import re
import struct
import sys
from pathlib import Path

from capstone import CS_ARCH_X86, CS_MODE_64, Cs

d = Path(__file__).with_name("dungeons_image.bin").read_bytes()
text = d[:0x3000000]
md = Cs(CS_ARCH_X86, CS_MODE_64)


def fn_start(i):
    while i > 0 and not (text[i - 1] == 0xCC and text[i] != 0xCC):
        i -= 1
    return i


def refs(offset, kind="any"):
    """[(address, instruction text)] of instructions whose memory operand has this displacement."""
    pat = struct.pack("<i", offset) if offset > 0x7F else None
    out = []
    if pat is None:
        return out
    for m in re.finditer(re.escape(pat), text):
        at = m.start()
        for back in range(2, 8):                      # opcode + modrm (+ rex, prefixes, sib) before the disp32
            start = at - back
            ins = next(md.disasm(text[start:start + 16], start), None)
            if ins and ins.address + ins.size >= at + 4 and f"+ {offset:#x}]" in ins.op_str:
                if kind == "any" or f"{kind} ptr" in ins.op_str or (kind == "byte" and ins.mnemonic in ("movzx", "movsx") and "byte ptr" in ins.op_str):
                    out.append((start, f"{ins.mnemonic} {ins.op_str}"))
                break
    return out


if __name__ == "__main__":
    offset = int(sys.argv[1], 16)
    kind = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else "any"
    hits = refs(offset, kind)
    if "--near" in sys.argv:
        other = int(sys.argv[sys.argv.index("--near") + 1], 16)
        fns = {fn_start(a) for a, _ in refs(other)}
        hits = [h for h in hits if fn_start(h[0]) in fns]
    for a, t in hits:
        print(f"{a:#x} (fn {fn_start(a):#x}) {t}")
    print(len(hits), "references")
