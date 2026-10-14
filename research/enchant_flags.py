"""Static: what each enchantment's registration code writes straight into its definition.

Every enchantment is registered by its own piece of code: `mov cl, <type id>; call exe+0xA79EE0` makes the
definition, a chain of setter calls fills in names and texts, plain `mov byte ptr [rax + X], imm` lines set flags,
and the result is stored in a global. This lists those plain writes (and the setter calls used) per enchantment,
to find what marks an enchantment as one that mobs can roll.

    python research/enchant_flags.py            # table: flags per enchantment
    python research/enchant_flags.py --calls    # also which setter functions each one calls
"""
import json
import re
import struct
import sys
from pathlib import Path

from capstone import CS_ARCH_X86, CS_MODE_64, Cs

d = Path(__file__).with_name("dungeons_image.bin").read_bytes()
text = d[:0x3000000]
md = Cs(CS_ARCH_X86, CS_MODE_64)
ids = json.loads((Path(__file__).parent.parent / "tools" / "enchant_ids.json").read_text())
names = {v: k for k, v in ids.items()}
MAKE = 0xA79EE0


def registrations():
    """{type id: (address of the make call, flags {offset: value}, setter calls [target])}"""
    out = {}
    for m in re.finditer(rb"\xe8", text[:-8]):
        i = m.start()
        if i + 5 + struct.unpack_from("<i", text, i + 1)[0] != MAKE:
            continue
        tid = None
        for back in range(2, 12):
            if text[i - back] == 0xB1:
                tid = text[i - back + 1]
                break
            if text[i - back:i - back + 2] == b"\x33\xc9":
                tid = 0
                break
        flags, calls = {}, []
        for ins in md.disasm(text[i + 5:i + 5 + 0x400], i + 5):
            if ins.mnemonic == "call" and ins.op_str.startswith("0x"):
                calls.append(int(ins.op_str, 16))
            w = re.match(r"(byte|word|dword) ptr \[rax(?: \+ (0x[0-9a-f]+|\d+))?\], (0x[0-9a-f]+|\d+)$", ins.op_str)
            if ins.mnemonic == "mov" and w:
                flags[int(w.group(2) or "0", 0)] = int(w.group(3), 0)
            if ins.mnemonic == "mov" and ins.op_str.startswith("qword ptr [rip") and ins.op_str.endswith(", rax"):
                break                                    # stored in its global: done
            if ins.mnemonic == "ret":
                break
        if tid is not None:
            out[tid] = (i, flags, calls)
    return out


if __name__ == "__main__":
    regs = registrations()
    offsets = sorted({o for _, f, _ in regs.values() for o in f})
    print(len(regs), "registrations; offsets written:", [hex(o) for o in offsets])
    print(f"{'id':>3} {'name':28} " + " ".join(f"{o:>5x}" for o in offsets))
    for tid in sorted(regs):
        at, flags, calls = regs[tid]
        row = " ".join(f"{flags[o]:>5}" if o in flags else "    ." for o in offsets)
        print(f"{tid:>3} {names.get(tid, '?'):28} {row}" + ("  " + " ".join(f"{c:x}" for c in calls) if "--calls" in sys.argv else ""))
