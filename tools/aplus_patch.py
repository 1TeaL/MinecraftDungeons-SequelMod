"""RETIRED - replaced by endless_patch.py (data only). With these code patches active the game crashed
when a mission started (exe+0xB9CFFB). Kept for reference; the launcher still uses open_game /
unpacked / alloc_near from here.

Raise the Apocalypse+ level cap in the running game (memory only; gone when the game closes).

    python tools/aplus_patch.py [levels] [--cap-only]     # default 99; --cap-only: no curve/gold hooks

Patches the three places the game hard-codes 25 A+ levels, then bends the power curve past A+25.
Each patch checks the original bytes first and refuses to touch anything that doesn't match (e.g. after
a game update).

The A+ table builder (exe+0xA1A660) also uses 25.0, as (L - IntroducedAt) / (25 - IntroducedAt). That
one is deliberately left alone: A+1-25 stay exactly vanilla, and what each stat does past A+25 comes
from its curve in the pak (Endless.toml) - frozen at the A+25 value unless a curve says otherwise.

Power scaling (from the exe): the game turns a difficulty into x = threat/18 + A+level/19 (+ small
extras such as player count). Gear power is linear in x (display ~= 104.8 * x * loot multiplier) and
mob scaling is 1.25 ** (19 * min(x, 3)), so mobs stop growing at x = 3 (A+38 solo at threat 7): the
"natural limit" of ~320 power. Past A+25 the level is compressed before it enters that math:
    L' = 25 + (L - 25) * (38 - 25) / (levels - 25)
so A+1-25 stay vanilla and A+<levels> lands exactly on the x = 3 limit. Gear and mobs stay in step.

Gold: the pak adds a Gold entry with 0% chance to the regular mob drops. The drop roll (exe+0x856930)
gets each entry's chance from exe+0x837ED0; that call is hooked to give Gold a chance past A+25 only
([gold] in Endless.toml). The drop code has no difficulty at hand, so the mob-difficulty hook records
the last A+ level the game scaled anything for - inside a mission, that's the mission's level.
"""
import ctypes
import ctypes.wintypes as wt
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from endless import gold_settings  # noqa: E402
from memprobe import main_module, pid_of, read  # noqa: E402
from mempatch import k32, write  # noqa: E402
import settings  # noqa: E402

ENDLESS_CONFIG = settings.path("Endless.toml")
THREAT_LEVELS = 7
SOFT_CAP = 25                 # A+ levels up to here keep vanilla power scaling
LIMIT_LEVEL = 38              # 1 + 38/19 = 3.0: the game's own mob scaling clamp
# Where the A+ level is read for power math: (exe offset, original bytes, xmm register it's loaded
# into, record it as the current level).
LEVEL_READS = [
    (0xA3AE10 + 0x96, "66 0f 6e 41 04 0f 5b c0", 0, False),  # power for a difficulty (gear, drops, recommended)
    (0xA3AC20 + 0x1B, "f3 0f 2a 71 04", 6, True),            # mob difficulty factor
]
DROP_ROLL = 0x856930 + 0xBC   # call DropChance (exe+0x837ED0) inside the mob drop roll
DROP_CHANCE = 0x837ED0
GOLD = 6                      # EDropCategory::Gold
# Stub page layout
STUB_GOLD, K25, SLOPE, LAST_LEVEL, GOLD_SLOPE, GOLD_BASE = 0x100, 0x200, 0x204, 0x208, 0x20C, 0x210


def alloc_near(h, base):
    """Executable page within +-2 GB of the exe (rel32 calls can reach it)."""
    k32.VirtualAllocEx.restype = ctypes.c_void_p
    k32.VirtualAllocEx.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.c_size_t, wt.DWORD, wt.DWORD]
    for i in range(1, 4000):
        addr = k32.VirtualAllocEx(h, ctypes.c_void_p(base - i * 0x10000), 0x1000, 0x3000, 0x40)
        if addr:
            return addr
    sys.exit("no free memory near the exe - not patching")


class Asm:
    """Tiny x64 emitter for the stubs: raw bytes plus RIP-relative operands."""

    def __init__(self, at):
        self.at, self.code = at, bytearray()

    def raw(self, *b):
        self.code.extend(b)

    def rip(self, op, reg, target, imm=b""):
        """`op` with a [rip+disp32] operand (modrm reg field = `reg`), optional trailing immediate."""
        ins = bytes(op) + bytes([0x05 | reg << 3])
        end = self.at + len(self.code) + len(ins) + 4 + len(imm)
        self.code.extend(ins + struct.pack("<i", target - end) + imm)

    def call(self, target):
        self.code.extend(b"\xe8" + struct.pack("<i", target - (self.at + len(self.code) + 5)))


def compress_stub(at, reg, page, record):
    """[record: mov [LAST_LEVEL], [rcx+4]]; cvtsi2ss xmmR,[rcx+4];
    if > 25: xmmR = 25 + (xmmR - 25) * slope; ret"""
    a = Asm(at)
    if record:
        a.raw(0x50, 0x8B, 0x41, 0x04)              # push rax; mov eax, [rcx+4]
        a.rip([0x89], 0, page + LAST_LEVEL)        # mov [LAST_LEVEL], eax
        a.raw(0x58)                                # pop rax
    a.raw(0xF3, 0x0F, 0x2A, 0x41 | reg << 3, 4)    # cvtsi2ss xmmR, [rcx+4]
    a.rip([0x0F, 0x2F], reg, page + K25)           # comiss xmmR, 25
    a.raw(0x76, 0x18)                              # jbe -> ret
    a.rip([0xF3, 0x0F, 0x5C], reg, page + K25)     # subss xmmR, 25
    a.rip([0xF3, 0x0F, 0x59], reg, page + SLOPE)   # mulss xmmR, slope
    a.rip([0xF3, 0x0F, 0x58], reg, page + K25)     # addss xmmR, 25
    a.raw(0xC3)
    return bytes(a.code)


def gold_stub(at, page, drop_chance):
    """Call the real DropChance; for the Gold entry (rbx) return a chance by A+ level instead."""
    a = Asm(at)
    a.raw(0x48, 0x83, 0xEC, 0x08)                  # sub rsp, 8 (keep the callee's stack aligned)
    a.call(drop_chance)
    a.raw(0x48, 0x83, 0xC4, 0x08)                  # add rsp, 8
    a.raw(0x80, 0x3B, GOLD)                        # cmp byte [rbx], Gold
    a.raw(0x75, 0x0C)                              # jne -> ret
    a.rip([0x83], 7, page + LAST_LEVEL, bytes([SOFT_CAP]))  # cmp dword [LAST_LEVEL], 25
    a.raw(0x7F, 0x04)                              # jg -> chance
    a.raw(0x0F, 0x57, 0xC0)                        # xorps xmm0, xmm0
    a.raw(0xC3)                                    # ret
    a.rip([0xF3, 0x0F, 0x2A], 0, page + LAST_LEVEL)  # chance: cvtsi2ss xmm0, [LAST_LEVEL]
    a.rip([0xF3, 0x0F, 0x5C], 0, page + K25)       # subss xmm0, 25
    a.rip([0xF3, 0x0F, 0x59], 0, page + GOLD_SLOPE)  # mulss xmm0, gold slope
    a.rip([0xF3, 0x0F, 0x58], 0, page + GOLD_BASE)   # addss xmm0, gold base
    a.raw(0xC3)
    return bytes(a.code)


def install_hooks(h, base, levels, gold):
    """Route the A+ level reads through stubs that compress levels past SOFT_CAP, and hook the drop
    roll for gold. All sites are checked before anything is written."""
    reads = [(off, bytes.fromhex(orig), reg, rec) for off, orig, reg, rec in LEVEL_READS]
    roll = read(h, base + DROP_ROLL, 5)
    roll_target = base + DROP_ROLL + 5 + struct.unpack_from("<i", roll, 1)[0] if roll[0] == 0xE8 else None
    use_gold = bool(gold.get("enabled"))
    if all(read(h, base + off, 1) == b"\xe8" for off, *_ in reads) and (not use_gold or roll_target != base + DROP_CHANCE):
        print("power curve already patched")
        return
    for off, orig, *_ in reads:
        if read(h, base + off, len(orig)) != orig:
            sys.exit(f"exe+0x{off:X}: unexpected code - not patching the power curve")
    if use_gold and roll_target != base + DROP_CHANCE:
        sys.exit(f"exe+0x{DROP_ROLL:X}: unexpected code - not patching gold drops")

    page = alloc_near(h, base)
    g_slope = (gold["chance_at_99"] - gold["chance_at_26"]) / (99 - 26)
    consts = struct.pack("<ffiff", float(SOFT_CAP), (LIMIT_LEVEL - SOFT_CAP) / (levels - SOFT_CAP), 0,
                         g_slope, gold["chance_at_26"] - g_slope)
    k32.WriteProcessMemory(h, ctypes.c_void_p(page + K25), consts, len(consts), None)
    stubs = [(page + 0x40 * i, compress_stub(page + 0x40 * i, reg, page, rec), off, orig)
             for i, (off, orig, reg, rec) in enumerate(reads)]
    if use_gold:
        stubs.append((page + STUB_GOLD, gold_stub(page + STUB_GOLD, page, base + DROP_CHANCE), DROP_ROLL, roll))
    for at, code, _, _ in stubs:
        k32.WriteProcessMemory(h, ctypes.c_void_p(at), code, len(code), None)
    for at, _, off, orig in stubs:
        write(h, base, off, orig, b"\xe8" + struct.pack("<i", at - (base + off + 5)) + b"\x90" * (len(orig) - 5))
    print(f"power curve bent: A+{SOFT_CAP + 1}..{levels} now scale like A+{SOFT_CAP + 1}..{LIMIT_LEVEL} did")
    if use_gold:
        print(f"gold from mobs past A+25: {gold['chance_at_26']:.0%} at A+26 -> {gold['chance_at_99']:.0%} at A+99")


COUNT_FN = 0xA210D0  # GetTotalNumEndlessStruggles: mov eax, 25; ret


def open_game():
    """(process handle, exe base) of the running game, or (None, None)."""
    pid = pid_of()
    if not pid:
        return None, None
    h = k32.OpenProcess(0x0438, False, pid)  # VM_OPERATION | VM_READ | VM_WRITE | QUERY_INFORMATION
    try:
        return h, main_module(h)[0]
    except (TypeError, struct.error):  # process still starting (or already gone): nothing readable yet
        return None, None


def unpacked(h, base):
    """True once the exe has decrypted its code (the packed exe has garbage there before that)."""
    cur = read(h, base + COUNT_FN, 5)
    return cur is not None and cur[0] == 0xB8 and cur[2:] == b"\0\0\0"


def apply(h, base, levels=99, hooks=True):
    assert 25 < levels < 128, "keep it to a sensible range"
    write(h, base, COUNT_FN, bytes.fromhex("b819000000"), bytes([0xB8, levels, 0, 0, 0]))
    write(h, base, 0xA210E0, bytes.fromhex("b820000000"), bytes([0xB8, levels + THREAT_LEVELS, 0, 0, 0]))
    write(h, base, 0xA1E722, bytes.fromhex("ba19000000"), bytes([0xBA, levels, 0, 0, 0]))
    print(f"A+ levels raised to {levels}")
    if hooks:
        install_hooks(h, base, levels, gold_settings(ENDLESS_CONFIG))


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    h, base = open_game()
    if not h:
        sys.exit("Minecraft Dungeons isn't running")
    apply(h, base, int(args[0]) if args else 99, hooks="--cap-only" not in sys.argv)
