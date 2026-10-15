"""Per-tier values for enchantments whose numbers are fixed in the game's code (Formulas.toml).
No game code is changed: the launcher adds a small routine of its own and points live enchantment objects at it.

    python tools/formula_patch.py            # watch the running game until it closes
    python tools/formula_patch.py --once     # one pass

Every enchantment object holds a std::function "value for this tier" at +0x110 (its target pointer at +0x148,
normally the object's own +0x110). The target starts with a vtable; the game calls entry 2 with a pointer to the
tier and takes the float it returns. The game's own targets work the value out from constants in code, e.g.
Critical Hit's chance (tier + 1) * 0.05. For each enchantment in Formulas.toml this makes, in new memory:
    a table of three floats, a routine returning table[tier - 1], and a copy of the original vtable with entry 2
    pointing at that routine
and then, on every live object of that enchantment (found by its class vtable, live_objects.py), replaces the
target's vtable pointer with the copy. Objects are made when gear is equipped or a level starts; a new one gets
its values at the next pass.
What each number means (research/ctor_members.py, 2026-10-05):
    CriticalHit      chance to trigger          0.10 / 0.15 / 0.20
    EnigmaResonator  chance at full souls       0.15 / 0.20 / 0.25
    BonusShot        extra arrow's damage       0.10 / 0.17 / 0.24
    Recycler         hits taken per refill      30 / 20 / 10
    Punch            pushback strength          3 / 4 / 5
    RapidFire        attack speed multiplier    1.10 / 1.15 / 1.20
    HealthSynergy    heal per artifact use      0.03 / 0.04 / 0.05 of max health
    Cowardice        damage multiplier          1.2 / 1.3 / 1.4 (at full health)
    Frenzied         attack speed multiplier    1.1 / 1.2 / 1.3 (below its health threshold)
The description's {0} is this same number, so a value set here also shows on the item card (2026-10-15: Cowardice
and Frenzied moved here from a hidden extra in the pak, whose description could only say "{0} +20%").
"""
import struct
import sys
import time
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aplus_patch import alloc_near, open_game, pid_of  # noqa: E402
from builtins_patch import write  # noqa: E402
from live_objects import Scanner  # noqa: E402
from memprobe import read  # noqa: E402

CONFIG = Path(__file__).resolve().parent.parent / "Formulas.toml"
FUNCTION, TARGET = 0x110, 0x148
# name -> ([class vtables of the objects], vtable of the game's own target, the game's own values)
KNOWN = {
    "CriticalHit": ([0x32B5888], 0x32C8200, (0.10, 0.15, 0.20)),
    "EnigmaResonator": ([0x32BB0B0, 0x32BB5B0], 0x32C8410, (0.15, 0.20, 0.25)),   # melee, ranged
    "BonusShot": ([0x31D27E0], 0x31D4290, (0.10, 0.17, 0.24)),
    "Recycler": ([0x32D98C8], 0x32F1BC0, (30.0, 20.0, 10.0)),
    "Punch": ([0x32D5018], 0x32F1A40, (3.0, 4.0, 5.0)),
    "RapidFire": ([0x32D8EC0], 0x32F1B60, (1.10, 1.15, 1.20)),
    "HealthSynergy": ([0x32C0EE0], 0x32C86E0, (0.03, 0.04, 0.05)),
    "Cowardice": ([0x32B5358], 0x32C81D0, (1.2, 1.3, 1.4)),       # damage multiplier at full health: tier*0.1+1.1
    "Frenzied": ([0x32BE9A8], 0x32C85C0, (1.1, 1.2, 1.3)),        # attack speed multiplier when low: tier*0.1+1.0
}
# float f(void *self, const int *tier): table[clamp(*tier, 1, 3) - 1]; the table follows the code
ROUTINE = bytes.fromhex(
    "8b02"              # mov eax, [rdx]
    "ffc8"              # dec eax
    "7902"              # jns +2
    "31c0"              # xor eax, eax
    "83f802"            # cmp eax, 2
    "7605"              # jbe +5
    "b802000000"        # mov eax, 2
    "488d0d06000000"    # lea rcx, [rip + 6]     -> the table
    "f30f100481"        # movss xmm0, [rcx + rax*4]
    "c3")               # ret
SLOT = 0x80                    # per enchantment: routine + table at +0, vtable copy at +0x40


class Formulas:
    def __init__(self, h, base, scanner=None):
        self.h, self.base = h, base
        self.own_scanner = scanner is None
        self.scanner = scanner or Scanner(h, base)
        cfg = tomllib.loads(CONFIG.read_text(encoding="utf-8")) if CONFIG.exists() else {}
        self.plan, self.ready, self.changed, self.page = {}, {}, {}, 0
        for name, values in cfg.items():
            ok = name in KNOWN and isinstance(values, list) and len(values) == 3 and \
                all(isinstance(v, (int, float)) and 0 <= v <= 1000 for v in values)
            if not ok:
                print(f"  ! Formulas.toml {name}: unknown name or not three numbers - skipped")
            elif tuple(float(v) for v in values) != KNOWN[name][2]:
                self.plan[name] = [float(v) for v in values]
                for vt in KNOWN[name][0]:
                    self.scanner.register(vt)

    def prepare(self, name):
        """Our vtable copy for this enchantment (built once), or 0 if the game isn't as expected."""
        if name in self.ready:
            return self.ready[name]
        self.ready[name] = 0
        original = read(self.h, self.base + KNOWN[name][1], 0x30)
        if not original or not all(self.base < q < self.base + 0x3100000 for q in struct.unpack("<6Q", original)):
            print(f"  ! {name}: unexpected data in the game - left alone")
            return 0
        if not self.page:
            self.page = alloc_near(self.h, self.base)
        at = self.page + SLOT * (len(self.ready) - 1)
        write(self.h, at, ROUTINE + struct.pack("<3f", *self.plan[name]))
        table = bytearray(original)
        struct.pack_into("<Q", table, 0x10, at)
        write(self.h, at + 0x40, bytes(table))
        self.ready[name] = at + 0x40
        return at + 0x40

    def tick(self, quiet=False):
        if self.own_scanner and self.plan:
            self.scanner.refresh()
        for name, values in self.plan.items():
            own = self.base + KNOWN[name][1]
            for vt in KNOWN[name][0]:
                for o in self.scanner.found.get(self.base + vt, []):
                    raw = read(self.h, o + FUNCTION, 0x40)
                    if not raw or struct.unpack_from("<Q", raw, TARGET - FUNCTION)[0] != o + FUNCTION \
                            or struct.unpack_from("<Q", raw)[0] != own:
                        continue       # not built as expected, or already ours
                    ours = self.prepare(name)
                    if not ours:
                        break
                    write(self.h, o + FUNCTION, struct.pack("<Q", ours))
                    self.changed[name] = self.changed.get(name, 0) + 1
                    if not quiet and self.changed[name] == 1:
                        print(f"{name}: per-tier values now " + " / ".join(f"{v:g}" for v in values))


if __name__ == "__main__":
    h, base = open_game()
    if not h:
        sys.exit("Minecraft Dungeons isn't running")
    w = Formulas(h, base)
    w.tick()
    while "--once" not in sys.argv and pid_of():
        time.sleep(3)
        w.tick()
    print("objects changed:", w.changed or "none")
