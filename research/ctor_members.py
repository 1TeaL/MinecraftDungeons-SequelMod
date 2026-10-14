"""List the plain numbers a native class's constructor writes into each object (exe dump).

    python research/ctor_members.py CriticalHit BonusShot ...

For class UName: find its GetPrivateStaticClass (it passes the wide name "Name" and the object size), follow the
constructor wrapper it registers, and print every `mov [this + off], imm` in the constructor. Numbers that are
not reflected properties but sit in the object can be rewritten on live objects (see tools/echo_patch.py).
"""
import re
import struct
import sys
from pathlib import Path

from capstone import Cs, CS_ARCH_X86, CS_MODE_64

d = Path(__file__).with_name("dungeons_image.bin").read_bytes()
text = d[:0x3000000]
md = Cs(CS_ARCH_X86, CS_MODE_64)
LEA = re.compile(rb"[\x48\x4c]\x8d[\x05\x0d\x15\x1d\x25\x2d\x35\x3d]")
leas = {}
for m in LEA.finditer(text):
    j = m.start()
    leas.setdefault(j + 7 + struct.unpack_from("<i", text, j + 3)[0], []).append(j)


def func_start(a):
    s = a
    while d[s - 1] != 0xCC and s > a - 0x400:
        s -= 1
    return s


def ctor_of(name):
    wides = [b"\0\0" + (p + name).encode("utf-16le") + b"\0\0" for p in "UA"]   # objects and actors
    for m in (m for w in wides for m in re.finditer(re.escape(w), d)):
        for site in leas.get(m.start() + 4, []):
            f = func_start(site)
            size, cands = None, []
            for ins in md.disasm(d[f:f + 0x120], f):
                if ins.mnemonic == "mov" and ins.op_str.startswith("dword ptr [rsp + 0x20],"):
                    size = int(ins.op_str.split(",")[1], 16)
                if ins.mnemonic == "lea" and "rip" in ins.op_str:
                    t = ins.address + ins.size + int(ins.op_str.split("rip")[1].replace("]", "").replace(" ", ""), 16)
                    if 0 < t < len(text) and d[t:t + 3] == b"\x48\x8b\x09":      # mov rcx, [rcx]
                        cands.append(t)
                if ins.mnemonic == "ret":
                    break
            for t in cands:
                for ins in md.disasm(d[t:t + 0x20], t):
                    if ins.mnemonic in ("jne", "jmp") and ins.op_str.startswith("0x"):
                        return int(ins.op_str, 16), size
    return None, None


for name in sys.argv[1:]:
    ctor, size = ctor_of(name)
    if not ctor:
        print(f"{name}: constructor not found")
        continue
    print(f"{name}: constructor exe+0x{ctor:X}, object size 0x{size or 0:X}")
    this = "rcx"
    for ins in md.disasm(d[ctor:ctor + 0x400], ctor):
        if ins.mnemonic == "mov" and ins.op_str in ("rbx, rcx", "rdi, rcx", "rsi, rcx"):
            this = ins.op_str[:3]
        if ins.mnemonic == "lea" and ins.op_str.startswith("rax, [rip") and "vt" not in locals():
            pass
        m = re.match(r"(byte|word|dword|qword) ptr \[%s \+ (0x[0-9a-f]+)\], (0x[0-9a-f]+|\d+)$" % this, ins.op_str)
        if ins.mnemonic == "mov" and m:
            off, imm = int(m.group(2), 16), int(m.group(3), 0)
            as_float = struct.unpack("<f", struct.pack("<I", imm))[0] if m.group(1) == "dword" else None
            shown = f"{as_float:g}" if as_float is not None and 1e-4 < abs(as_float) < 1e6 else str(imm)
            print(f"    +0x{off:X} {m.group(1):5} = {shown}")
        if ins.mnemonic in ("ret", "int3"):
            break
