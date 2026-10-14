"""Accelerate's speed limit (Accelerate.toml). Data only: no game code is changed.

    python tools/accelerate_patch.py            # apply Accelerate.toml to the running game

Accelerate adds attack speed with every shot (8 / 10 / 12% per tier, up to 25 / 20 / 16 shots = about +200%), but
its blueprint asks the game for a speed limit and gets 2.0 - double speed, +100% - at every tier, so the last half
of those stacks never did anything (and raising the stack counts in the pak did nothing either; user, 2026-10-13:
"it maxes out at 100%").
The limit is a native function, GetSpeedLimit (exe+0xA20C80: return 2.0), reached only through its script-callable
entry (exe+0xE9EDD0), which the function's UFunction object points at (+0xC0). The launcher puts a copy of that
entry into new memory - the same instructions, with the call replaced by "load our number" - and points the
UFunction at the copy, as tools/endless_patch.py does for the A+ level counts.
Only the real object is changed: the object list must have it at its own index (a table of native functions holds the
same address - that second match stopped the change until 2026-10-14). NOT YET SEEN WORKING.
"""
import struct
import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aplus_patch import alloc_near, open_game  # noqa: E402
from builtins_patch import write  # noqa: E402
from endless_patch import find_pointers  # noqa: E402
from live_objects import OBJECTS  # noqa: E402
from memprobe import main_module, read  # noqa: E402

CONFIG = Path(__file__).resolve().parent.parent / "Accelerate.toml"
ENTRY, FUNC, VANILLA = 0xE9EDD0, 0xC0, 2.0
# The entry as the game has it, up to its call; ours continues with: mov eax, <float>; movd xmm0, eax; then the
# game's own ending (movss [rbx], xmm0; add rsp, 0x20; pop rbx; ret).
HEAD = bytes.fromhex("4053" "4883ec20" "488b4220" "33c9" "4885c0" "498bd8" "0f95c1" "4803c8" "48894a20")
TAIL = bytes.fromhex("660f6ec0" "f30f1103" "4883c420" "5b" "c3")


def listed(h, base, o):
    """True if `o` is a real object: the game's object list (tools/live_objects.py) has it at its own index. (The
    entry's address also sits in a table of native functions next to their names - not an object; 2026-10-14 that
    second match stopped the change.)"""
    raw = read(h, o + 0xC, 4)
    index = struct.unpack("<i", raw)[0] if raw else -1
    raw = read(h, base + OBJECTS, 8)
    table = struct.unpack("<Q", raw)[0] if raw else 0
    raw = read(h, table + (index // 0x10000) * 8, 8) if table and index > 0 else None
    chunk = struct.unpack("<Q", raw)[0] if raw else 0
    raw = read(h, chunk + (index % 0x10000) * 0x18, 8) if chunk else None
    return bool(raw) and struct.unpack("<Q", raw)[0] == o


def apply(h, base):
    cfg = tomllib.loads(CONFIG.read_text(encoding="utf-8")) if CONFIG.exists() else {}
    limit = cfg.get("speed_limit")
    if limit is None:
        return
    if isinstance(limit, bool) or not isinstance(limit, (int, float)) or not 1.0 <= limit <= 5.0:
        sys.exit("Accelerate.toml: speed_limit must be a number from 1 to 5 (2 = the game's own)")
    if abs(limit - VANILLA) < 1e-6:
        return
    game = read(h, base + ENTRY, len(HEAD) + 5)
    if not game or game[:len(HEAD)] != HEAD or game[len(HEAD)] != 0xE8:
        sys.exit("Accelerate: the game's code isn't what this was built for - limit not changed")
    size = main_module(h)[1]
    owners = [a - FUNC for a in find_pointers(h, [base + ENTRY])[base + ENTRY]
              if base <= struct.unpack("<Q", read(h, a - FUNC, 8) or bytes(8))[0] < base + size and listed(h, base, a - FUNC)]
    if len(owners) != 1:
        sys.exit(f"Accelerate: expected one function object for the speed limit, found {len(owners)} - not changed")
    at = alloc_near(h, base)
    write(h, at, HEAD + b"\xb8" + struct.pack("<f", float(limit)) + TAIL)
    write(h, owners[0] + FUNC, struct.pack("<Q", at))
    print(f"Accelerate: speed limit {VANILLA:g}x -> {limit:g}x (+{(limit - 1) * 100:g}% attack speed at most)")


if __name__ == "__main__":
    h, base = open_game()
    if not h:
        sys.exit("Minecraft Dungeons isn't running")
    apply(h, base)
