"""Raise the game's power cap in the running game (memory only; gone when the game closes).

    python tools/cap_patch.py [shown power]     # default: [power] cap_power in Endless.toml

Gear strength and mob scaling are both 1.25 ** (19 * min(x, 3)): three functions clamp x with one shared
float, 3.0 (gear power 315). That float is used by ~300 unrelated places, so it stays as it is; instead
the three `minss xmm6, [3.0]` instructions are pointed at a float of our own:

    exe+0xB8794F   gear attack factor      (exe+0xB87920)
    exe+0xB9336F   gear health/heal factor (exe+0xB93340)
    exe+0xB8D9E0   mob scaling             (exe+0xB8D9C0)

THIS CHANGES GAME CODE (4 bytes at each place). The first Endless Apocalypse did too and the game then
crashed when a mission started; whether any code change does that, or only what that version did, isn't
known yet. Switch: `cap` in Launcher.toml. The pak's curves (endless.py) are built for the same cap.
"""
import ctypes
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aplus_patch import alloc_near, open_game  # noqa: E402
from endless import NATURAL_CAP_X, POWER_PER_X, power_settings  # noqa: E402
from memprobe import read  # noqa: E402
from mempatch import k32, write  # noqa: E402
import settings  # noqa: E402

ENDLESS_CONFIG = settings.path("Endless.toml")
SITES = [0xB8794F, 0xB9336F, 0xB8D9E0]   # f3 0f 5d 35 <disp32>: minss xmm6, [rip + disp32]
MINSS = bytes.fromhex("f30f5d35")
SHARED_3 = 0x3101950                     # the float they all read


def apply(h, base, cap_x=None):
    if cap_x is None:
        cap_x = NATURAL_CAP_X   # retired: any code change crashes missions
    if cap_x <= NATURAL_CAP_X + 1e-6:
        print("Power cap: left at the game's own (315)")
        return
    shown = cap_x * POWER_PER_X * 10
    current = [read(h, base + s, 8) or b"" for s in SITES]
    targets = [base + site + 8 + struct.unpack_from("<i", c, 4)[0] if c[:4] == MINSS else None
               for site, c in zip(SITES, current)]
    if None in targets:
        sys.exit("Power cap: unexpected code - not changed")
    if all(t != base + SHARED_3 for t in targets):   # already pointed at our own float: just update it
        if len(set(targets)) != 1:
            sys.exit("Power cap: unexpected state - not changed")
        k32.WriteProcessMemory(h, ctypes.c_void_p(targets[0]), struct.pack("<f", cap_x), 4, None)
        print(f"Power cap: {shown:.0f} (updated)")
        return
    if any(t != base + SHARED_3 for t in targets):
        sys.exit("Power cap: unexpected code - not changed")
    page = alloc_near(h, base)
    k32.WriteProcessMemory(h, ctypes.c_void_p(page), struct.pack("<f", cap_x), 4, None)
    for s, cur in zip(SITES, current):
        write(h, base, s, cur, MINSS + struct.pack("<i", page - (base + s + 8)))
    print(f"Power cap raised from 315 to {shown:.0f} (gear and mobs)")


if __name__ == "__main__":
    h, base = open_game()
    if not h:
        sys.exit("Minecraft Dungeons isn't running")
    apply(h, base, float(sys.argv[1]) / 10 / POWER_PER_X if len(sys.argv) > 1 else None)
