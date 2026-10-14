"""Dev tool (read-only): disassemble functions in the running game, annotating constants and calls.

    python tools/disasm.py <exe_offset_hex>[,<exe_offset_hex>...] [max_bytes]

Uses research/dungeons_image.bin (from dumpimage.py) when it exists, so the game needn't be running.
"""
import struct
import sys
from pathlib import Path

from capstone import CS_ARCH_X86, CS_MODE_64, Cs
from capstone.x86 import X86_OP_MEM, X86_REG_RIP

sys.path.insert(0, str(Path(__file__).resolve().parent))
from memprobe import k32, main_module, pid_of, read  # noqa: E402

NAMES = {
    0xA210D0: "GetTotalNumEndlessStruggles", 0xA210E0: "GetTotalNumThreat+A+",
    0xA1E720: "GetNumEndlessStrugglesInDifficulty", 0xB8DF00: "StoredToDisplayPower",
    0xA1A660: "BuildEndlessStruggleConfig", 0x1EF2030: "RichCurveEval",
}


def disasm(h, base, off, limit):
    code = read_any(h, base + off, limit) or b""
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.detail = True
    print(f"\n=== exe+0x{off:X} {NAMES.get(off, '')}")
    for ins in md.disasm(code, base + off):
        note = ""
        for op in ins.operands:
            if op.type == X86_OP_MEM and op.mem.base == X86_REG_RIP:
                addr = ins.address + ins.size + op.mem.disp
                raw = read_any(h, addr, 8) or b"\0" * 8
                f, d = struct.unpack_from("<f", raw)[0], struct.unpack_from("<d", raw)[0]
                i32 = struct.unpack_from("<i", raw)[0]
                note = f"[exe+0x{addr - base:X}] f={f:g} d={d:g} i={i32}"
        if ins.mnemonic in ("call", "jmp") and ins.op_str.startswith("0x"):
            tgt = int(ins.op_str, 16) - base
            note = f"-> exe+0x{tgt:X} {NAMES.get(tgt, '')}"
        print(f"  +0x{ins.address - base - off:03X}  {ins.mnemonic:8} {ins.op_str:44} {note}")
        if ins.mnemonic in ("ret", "int3") and ins.address - base - off > 4:
            if ins.mnemonic == "int3":
                break


IMAGE = Path(__file__).resolve().parent.parent / "research" / "dungeons_image.bin"


class Image:
    """Stands in for a process handle: reads from the saved image at a fake base."""
    base = 0x140000000

    def __init__(self, path):
        self.data = path.read_bytes()


def read_any(h, addr, n):
    if isinstance(h, Image):
        off = addr - h.base
        return h.data[off:off + n] if 0 <= off < len(h.data) else None
    return read(h, addr, n)


if __name__ == "__main__":
    if IMAGE.exists():
        h = Image(IMAGE)
        base = h.base
    else:
        h = k32.OpenProcess(0x0410, False, pid_of())
        base, _ = main_module(h)
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 600
    for a in sys.argv[1].split(","):
        disasm(h, base, int(a, 16), limit)
