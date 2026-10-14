"""Dev tool (read-only): dump a function in the running game and find constants that look like the A+ cap.

    python tools/memscan.py <exe_offset_hex> [depth]
Dumps the function, follows direct calls (depth levels), and reports 25 / 24 / 25.0 / 24.0 constants.
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from memprobe import k32, main_module, pid_of, read  # noqa: E402

PATTERNS = {
    "imm32 25": bytes.fromhex("19000000"), "imm32 24": bytes.fromhex("18000000"),
    "float 25.0": struct.pack("<f", 25.0), "float 24.0": struct.pack("<f", 24.0),
    "cmp reg,25 (83 xx 19)": None,
}
SKIP = set()
SPAN = 400
CALL_TARGETS = {0xA210D0: "GetTotalNumEndlessStruggles", 0xA210E0: "GetTotalNumThreat+A+", 0xA1E720: "GetNumEndlessStrugglesInDifficulty"}


def scan(h, base, size, off, depth, seen, indent=""):
    if off in seen or depth < 0:
        return
    seen.add(off)
    code = read(h, base + off, SPAN) or b""
    end = code.find(b"\xcc\xcc\xcc")
    code = code[:end if end > 0 else len(code)]
    print(f"{indent}exe+0x{off:X} ({len(code)} bytes): {code[:160].hex(' ')}{' ...' if len(code) > 160 else ''}")
    for name, pat in PATTERNS.items():
        if pat is None:
            hits = [i for i in range(len(code) - 2) if code[i] == 0x83 and code[i + 2] == 0x19]
        else:
            hits = [i for i in range(len(code)) if code.startswith(pat, i)]
        for i in hits:
            print(f"{indent}  ** {name} at +0x{i:X}: {code[max(0, i - 6):i + 6].hex(' ')}")
    # rip-relative SSE operands (movss/mulss/divss/subss/addss/minss/maxss/comiss/ucomiss/cvtsi2ss xmm, [rip+d32])
    for i in range(2, len(code) - 5):
        if code[i - 2] == 0x0F and code[i - 1] in (0x10, 0x59, 0x5E, 0x5C, 0x58, 0x5D, 0x5F, 0x2F, 0x2E)                 and (code[i] & 0xC7) == 0x05:
            disp = struct.unpack_from("<i", code, i + 1)[0]
            addr = base + off + i + 5 + disp
            raw = read(h, addr, 4)
            if raw:
                val = struct.unpack("<f", raw)[0]
                if 0.0 < abs(val) < 100000 and val == val:
                    op = {0x10: "movss", 0x59: "mulss", 0x5E: "divss", 0x5C: "subss", 0x58: "addss", 0x5D: "minss",
                          0x5F: "maxss", 0x2F: "comiss", 0x2E: "ucomiss"}[code[i - 1]]
                    print(f"{indent}  ** {op} [exe+0x{addr - base:X}] = {val:g} at +0x{i:X}")
    # rip-relative SSE2 double loads/maths (f2 0f 10/59/5e/5c/58 [rip+d32])
    for i in range(3, len(code) - 5):
        if code[i - 3] == 0xF2 and code[i - 2] == 0x0F and code[i - 1] in (0x10, 0x59, 0x5E, 0x5C, 0x58)                 and (code[i] & 0xC7) == 0x05:
            addr = base + off + i + 5 + struct.unpack_from("<i", code, i + 1)[0]
            raw = read(h, addr, 8)
            if raw:
                print(f"{indent}  ** double [exe+0x{addr - base:X}] = {struct.unpack('<d', raw)[0]:g} at +0x{i:X}")
    # integer immediates in cmp/imul/mov that look like power levels
    for i in range(len(code) - 4):
        v = struct.unpack_from("<i", code, i)[0]
        if v in (320, 300, 263, 252, 251, 250, 33, 32) and code[i - 1] in (0x3D, 0xB8, 0xB9, 0xBA, 0xBB, 0x69, 0xF8, 0xF9, 0xFA, 0xFB):
            print(f"{indent}  ** int {v} at +0x{i:X}: {code[max(0, i - 4):i + 4].hex(' ')}")
    for i in range(len(code) - 5):
        if code[i] == 0xE8:
            tgt = base + off + i + 5 + struct.unpack_from("<i", code, i + 1)[0]
            if tgt - base in CALL_TARGETS:
                print(f"{indent}  ** calls {CALL_TARGETS[tgt - base]} at +0x{i:X}")
            if base <= tgt < base + size and (tgt - base) not in SKIP:
                scan(h, base, size, tgt - base, depth - 1, seen, indent + "    ")


if __name__ == "__main__":
    h = k32.OpenProcess(0x0410, False, pid_of())
    base, size = main_module(h)
    SKIP.add(0x124DFB0)  # UE param-reading helper used by every thunk
    if len(sys.argv) > 3:
        SPAN = int(sys.argv[3])
    for a in sys.argv[1].split(","):
        print(f"=== exe+{a}")
        scan(h, base, size, int(a, 16), int(sys.argv[2]) if len(sys.argv) > 2 else 2, set())
