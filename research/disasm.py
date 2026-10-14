"""Disassemble the exe dump: python research/dis.py <exe offset hex> [max instructions]"""
import sys
from pathlib import Path
from capstone import Cs, CS_ARCH_X86, CS_MODE_64
d = Path(__file__).with_name("dungeons_image.bin").read_bytes()
md = Cs(CS_ARCH_X86, CS_MODE_64)
s = int(sys.argv[1], 16); n = int(sys.argv[2]) if len(sys.argv) > 2 else 80
for k, ins in enumerate(md.disasm(d[s:s + n * 16], s)):
    print(hex(ins.address), ins.mnemonic, ins.op_str)
    if k >= n or ins.mnemonic == "int3":
        break
