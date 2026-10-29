"""Shorten Echo's gap between repeats in the running game (Echo.toml). Data only: no game code is changed.

    python tools/echo_patch.py            # watch the running game until it closes
    python tools/echo_patch.py --once     # one pass

Echo has no settings in the game's files. Its gap is worked out in code as  base - (tier - 1)  seconds, and the
base (5.0, giving 5 / 4 / 3 s) is a plain number inside every Echo object (+0x1F8, set when the object is made).
So the launcher looks for Echo objects (vtable exe+0x32B9548) while the game runs and rewrites that number.
An object is made when a weapon with Echo is equipped or a level starts; it gets the new gap at the next pass,
which can take up to half a minute (live_objects.py).
Beside the base sit 0.2 (+0x1FC) and 2.0 (+0x200, the gap for mobs that have Echo); both are left alone and
used to make sure the object is what we think it is.
"""
import struct
import sys
import time
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aplus_patch import open_game, pid_of  # noqa: E402
from builtins_patch import write  # noqa: E402
from live_objects import Scanner  # noqa: E402
from memprobe import read  # noqa: E402
import settings  # noqa: E402

CONFIG = settings.path("Echo.toml")
VTABLE, BASE_GAP = 0x32B9548, 0x1F8
VANILLA = (5.0, 0.2, 2.0)        # +0x1F8, +0x1FC, +0x200 as the game sets them
MIN_TIER3_GAP = 0.05             # a timer of 0 s never fires: Echo would stop working


class EchoWatch:
    def __init__(self, h, base, scanner=None):
        self.h, self.base = h, base
        self.own_scanner = scanner is None
        self.scanner = scanner or Scanner(h, base)
        self.vt = self.scanner.register(VTABLE)
        cfg = settings.load(CONFIG)
        gap3 = max(MIN_TIER3_GAP, float(cfg.get("tier3_gap", VANILLA[0] - 2)))
        self.value = gap3 + 2      # tier 1 = value, tier 2 = value - 1, tier 3 = value - 2
        self.changed = 0

    def tick(self, quiet=False):
        if abs(self.value - VANILLA[0]) < 1e-4:
            return
        if self.own_scanner:
            self.scanner.refresh()
        for o in self.scanner.found.get(self.vt, []):
            raw = read(self.h, o + BASE_GAP, 12)
            if not raw:
                continue
            gap, delay, mob_gap = struct.unpack("<fff", raw)
            if abs(delay - VANILLA[1]) > 1e-4 or abs(mob_gap - VANILLA[2]) > 1e-4 or abs(gap - VANILLA[0]) > 1e-4:
                continue           # not an Echo object as we know it, or already changed
            write(self.h, o + BASE_GAP, struct.pack("<f", self.value))
            self.changed += 1
            if not quiet and self.changed == 1:
                v = self.value
                print(f"Echo: gap between repeats now {v:g} / {v - 1:g} / {v - 2:g} s (tier 1 / 2 / 3)")


if __name__ == "__main__":
    h, base = open_game()
    if not h:
        sys.exit("Minecraft Dungeons isn't running")
    w = EchoWatch(h, base)
    w.tick()
    while "--once" not in sys.argv and pid_of():
        time.sleep(3)
        w.tick()
    print(f"Echo objects changed: {w.changed}")
