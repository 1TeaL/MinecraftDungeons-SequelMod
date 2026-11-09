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
    Protection       damage taken divisor       1.06 / 1.12 / 1.18 (tier*0.06+1: -6/11/15%)
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
import settings  # noqa: E402

CONFIG = settings.path("Formulas.toml")
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
    # Deflect: tier * 0.1 + 0.15 (exe+0x32C8290's routine, the same mob_enchants.py points mobs' copies away from);
    # the player's Deflecting only (the Tower Guard's DeflectingWithShield vtable is left out), PLAYER_ONLY below
    "Deflecting": ([0x32B70C8], 0x32C8290, (0.25, 0.35, 0.45)),
    # Supercharge: charged-shot damage multiplier 1.1 + 0.1 x tier; Wild Rage: chance 0.1 + 0.1 x tier (research/
    # value_lambda.py, 2026-11-09; the same kind of routine as Rapid Fire's)
    "Supercharge": ([0x32E4920], 0x32F1F50, (1.2, 1.3, 1.4)),
    "WildRage": ([0x32E9A00], 0x32F2160, (0.2, 0.3, 0.4)),
    "Cowardice": ([0x32B5358], 0x32C81D0, (1.2, 1.3, 1.4)),       # damage multiplier at full health: tier*0.1+1.1
    "Frenzied": ([0x32BE9A8], 0x32C85C0, (1.1, 1.2, 1.3)),        # attack speed multiplier when low: tier*0.1+1.0
    "Protection": ([0x32D4B18], 0x32F1A10, (1.06, 1.12, 1.18)),   # damage taken divisor: tier*0.06+1.0 (exe+0xACEDB0)
    # Thrive Under Pressure: the same routine as Protection (exe+0xACEDB0); what it does there is untested (2026-11-05)
    "ThriveUnderPressure": ([0x32E6EE0], 0x32F2070, (1.06, 1.12, 1.18)),
    # Explorer = Bottomless Brew: its heal share (tier * 0.0033, exe+0xA794D0) is unused now - only the card shows it
    "Explorer": ([0x32BBFF8], 0x32C8470, (0.0033, 0.0066, 0.0099)),
    # Food Reserves = Barrier Brew: its value is the food count (tier, exe+0xA4E3B0's target; read as a whole number,
    # rounded down, by exe+0xAAE850 - 0 or less crafts nothing, exe+0xAAC5E2), 2026-11-06
    "FoodReserves": ([0x32BE440], 0x32C8560, (1.0, 2.0, 3.0)),
    # Knockback = Sweeping Edge: its value is the knockback chance (tier / 10, exe+0xA51F00's target); the card's
    # tier line is the shared "{0} chance to trigger" - 1.0 makes it read 100% (the push itself is 0), 2026-11-06
    "Knockback": ([0x32C3870], 0x32C8740, (0.1, 0.2, 0.3)),
    # Heals Allies = Radiant Guard: tier x PercentageOfDamageToHeal (+0x1F8, 0 in ours) - the card's "{0} of max
    # health healed"; Barrier = Battle Hardened: 1 / (1 - 0.03 x tier), shown as (value - 1) - "+10% damage
    # resistance at full stacks". Display only: both enchantments' own effects are off (2026-11-06)
    "Altruistic": ([0x3296D40], 0x329AC28, (0.25, 0.5, 0.75)),
    "Barrier": ([0x3299358], 0x329AD78, (1 / 0.97, 1 / 0.94, 1 / 0.91)),
    # Charging Acceleration = Shatter: a constant 1 (exe+0x32C80E0's routine) - its card's "{0}" only; its own speed-up
    # is off (AccelerationAmount 0), 2026-11-07
    "ChargingAcceleration": ([0x32B31D0], 0x32C80E0, (1.0, 1.0, 1.0)),
    # Regeneration = Last Stand: heal per second x (1 + tier / 3) from +0x214 (exe+0x32F1BF0's routine) - card only;
    # its heal never starts (TimeUntilRegeneration 1e9). Mobs' copies are left alone (PLAYER_ONLY, 2026-11-09): their
    # heal has its own number (MobRegenerationAmountPerSecond, +0x210) - this keeps ours off them either way
    "Regeneration": ([0x32DA018], 0x32F1BF0, (4.0, 5.0, 6.0)),
    # Leeching and Refreshment (melee): their own triggers are off (numbers 0: Base + PerLevel x (tier - 1), exe+0x32C8770
    # / exe+0x32F1980's routines), ours count every kill credited to the wearer (build_enchants.py) - so the card shows
    # 0 unless patched; the third item is what it shows in our build, 2026-11-07
    "Leeching": ([0x32C3D70], 0x32C8770, (0.0, 0.0, 0.0)),
    "PotionThirstMelee": ([0x32D36C8], 0x32F1980, (0.0, 0.0, 0.0)),
    # Exploding: Base (+0x20C) + PerLevel (+0x210) x (tier - 1) (exe+0x32C8440's routine); ours explodes every
    # credited kill at once and its own numbers are 0, 2026-11-08
    "Exploding": ([0x32BBAB0], 0x32C8440, (0.0, 0.0, 0.0)),
    # Refreshment (ranged): as the melee one (exe+0x32F19B0), ours on kill credit with arrow marks, 2026-11-08
    "PotionThirstRanged": ([0x32D3BC8], 0x32F19B0, (0.0, 0.0, 0.0)),
    # (Thorns, exe+0x32F2040, class vtable 0x32E69E0: not patched - the game's Thorns uses that number for its damage
    # back, so a card number there made Overload reflect damage, 2026-11-08)
    # Gravity Pulse = Artifact Amplifier: a fixed 1 + 0.5 x (tier - 1) (exe+0x32C8650's routine, research/value_lambda.py
    # 2026-11-08); the card shows Artifact Amplifier's artifact damage instead
    "GravityPulse": ([0x32BFF18], 0x32C8650, (1.0, 1.5, 2.0)),
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
# enchantments whose number is never changed on a mob's copy (the game's own stays; copies with no owner, like the
# item card's, get ours)
PLAYER_ONLY = {"Regeneration", "Deflecting"}
SLOT = 0x80                    # per enchantment: routine + table at +0, vtable copy at +0x40


class Formulas:
    def __init__(self, h, base, scanner=None):
        self.h, self.base = h, base
        self.own_scanner = scanner is None
        self.scanner = scanner or Scanner(h, base)
        cfg = settings.load(CONFIG)
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

    def owner_kind(self, obj):
        """"mob" / "player" for an enchantment object's owner (mob_enchants' ancestor test), None if not known yet."""
        import mob_enchants as me   # here, not at the top: mob_enchants imports this module
        raw = read(self.h, self.base + me.MOB_CLASS, 8)
        mob = struct.unpack("<Q", raw)[0] if raw else 0
        raw = read(self.h, obj + me.OWNER, 8)
        owner = struct.unpack("<Q", raw)[0] if raw else 0
        if not owner:
            return None
        if not mob:
            return "player"        # MobCharacter isn't loaded yet, so no mob exists
        depth = read(self.h, mob + me.DEPTH, 4)
        raw = read(self.h, owner + me.CLASS, 8)
        cls = struct.unpack("<Q", raw)[0] if raw else 0
        head = read(self.h, cls + me.CHAIN, 12) if cls and depth else None
        if not head:
            return None
        depth = struct.unpack("<i", depth)[0]
        chain, own_depth = struct.unpack("<Qi", head)
        if not chain:
            return None
        if depth > own_depth:
            return "player"
        entry = read(self.h, chain + 8 * depth, 8)
        return "mob" if entry and struct.unpack("<Q", entry)[0] == mob + me.CHAIN else "player"

    def tick(self, quiet=False):
        if self.own_scanner and self.plan:
            self.scanner.refresh()
        for name, values in self.plan.items():
            own = self.base + KNOWN[name][1]
            for vt in KNOWN[name][0]:
                for o in self.scanner.found.get(self.base + vt, []):
                    raw = read(self.h, o + FUNCTION, 0x40)
                    if not raw or struct.unpack_from("<Q", raw, TARGET - FUNCTION)[0] != o + FUNCTION:
                        continue       # not built as expected
                    now = struct.unpack_from("<Q", raw)[0]
                    if name in PLAYER_ONLY and self.owner_kind(o) == "mob":
                        # a mob's copy keeps the game's own number - put back if we changed it before its owner
                        # was set (the item card's copy has no owner at all, so unknown owners get ours)
                        if now == self.ready.get(name):
                            write(self.h, o + FUNCTION, struct.pack("<Q", own))
                        continue
                    if now != own:
                        continue       # already ours
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
