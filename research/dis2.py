"""Disassemble with float/pointer annotations: python research/dis2.py <exe offset hex> [max instructions]"""
import struct, sys
from pathlib import Path
from capstone import Cs, CS_ARCH_X86, CS_MODE_64
d = Path(__file__).with_name("dungeons_image.bin").read_bytes()
md = Cs(CS_ARCH_X86, CS_MODE_64)
s = int(sys.argv[1], 16); n = int(sys.argv[2]) if len(sys.argv) > 2 else 80
for k, ins in enumerate(md.disasm(d[s:s + n * 16], s)):
    extra = ""
    if "rip" in ins.op_str:
        t = ins.address + ins.size + int(ins.op_str.split("rip")[1].split("]")[0].replace(" ", ""), 16)
        extra = f"   ; ->{t:#x}"
        if "ss" in ins.mnemonic or "ps" in ins.mnemonic:
            extra += f" = {struct.unpack_from('<f', d, t)[0]:g}"
    if ins.mnemonic == "mov" and "dword ptr" in ins.op_str and ins.op_str.split(",")[-1].strip().startswith("0x"):
        v = int(ins.op_str.split(",")[-1], 16)
        f = struct.unpack("<f", struct.pack("<I", v & 0xffffffff))[0]
        if 1e-3 < abs(f) < 1e6: extra += f"   ; float {f:g}"
    print(hex(ins.address), ins.mnemonic, ins.op_str, extra)
    if k >= n or ins.mnemonic == "int3":
        break
