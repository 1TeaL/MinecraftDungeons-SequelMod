"""Switch off or weaken enchantments on MOBS only (MobEnchants.toml). Data only: no game code is changed.

    python tools/mob_enchants.py            # watch the running game until it closes
    python tools/mob_enchants.py --show     # the copies found right now and who owns them

Every enchantment in play is an object of its own that records its owner (a character) at +0xE8. The launcher
finds the copies of an enchantment by their class vtable (tools/live_objects.py), keeps those whose owner is a
MobCharacter, and changes only them - the player's copy of the same enchantment is never touched.

Is the owner a mob: the game's own test (as in its code at exe+0xA637A0). A class object lists its ancestors at
+0x30 with their number minus one at +0x38; the owner is a MobCharacter if the entry at MobCharacter's depth is
MobCharacter itself. MobCharacter's class object is the global at exe+0x454F5A0 (set once the class is first used).

What can be changed (worked out from the exe, 2026-10-11):
  Deflecting   its chance per tier. The game computes tier * 0.1 + 0.15 (25 / 35 / 45%) in a small function the
               object points at (+0x110); the mob copies are pointed at a table of our own instead, as
               tools/formula_patch.py does. All zeros = mobs never deflect.
  Levitation   (Levitation Shot; the game's classes are Levitation, LevitationMelee, LevitationRanged) plain
               floats in the object: Duration +0x1FC, EffectStrength +0x200, LaunchStrength +0x204,
               FallDamagePercentagePerLevel +0x208. All zeros = the shot does nothing.
NOT YET SEEN WORKING. The LevitationMelee / LevitationRanged vtables were picked by position next to Levitation's.
"""
import struct
import sys
import time
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aplus_patch import alloc_near, open_game, pid_of  # noqa: E402
from builtins_patch import write  # noqa: E402
from formula_patch import FUNCTION, ROUTINE, TARGET  # noqa: E402
from live_objects import Scanner  # noqa: E402
from memprobe import read  # noqa: E402
import settings  # noqa: E402

CONFIG = settings.path("MobEnchants.toml")
OWNER, CLASS, CHAIN, DEPTH = 0xE8, 0x10, 0x30, 0x38
ALWAYS = 0x1DF                   # bAlwaysTrigger of an enchantment object
MOB_CLASS = 0x454F5A0            # global: MobCharacter's class object
# Deflecting, and DeflectingWithShield (the Tower Guard's; same code throughout, only the vtable address differs)
DEFLECT = {"vtables": [0x32B70C8, 0x3426C78], "function": 0x32C8290}
LEVITATION = {"vtables": [0x32C42A0, 0x32C47A0, 0x32C4CA0],
              "fields": {"Duration": 0x1FC, "EffectStrength": 0x200, "LaunchStrength": 0x204,
                         "FallDamagePercentagePerLevel": 0x208}}


class MobEnchants:
    def __init__(self, h, base, scanner=None):
        self.h, self.base = h, base
        self.own_scanner = scanner is None
        self.scanner = scanner or Scanner(h, base)
        cfg = settings.load(CONFIG)
        chance = cfg.get("Deflecting", {}).get("chance")
        self.chance = [float(c) for c in chance] if isinstance(chance, list) and len(chance) == 3 else None
        self.levitation = {k: float(v) for k, v in cfg.get("Levitation", {}).items() if k in LEVITATION["fields"]}
        self.on = bool(base) and (self.chance is not None or bool(self.levitation))
        if self.on and self.chance is not None:
            for vt in DEFLECT["vtables"]:
                self.scanner.register(vt)
        if self.on and self.levitation:
            for vt in LEVITATION["vtables"]:
                self.scanner.register(vt)
        self.table, self.said = 0, set()

    def is_mob(self, obj):
        """True if the enchantment object's owner is a MobCharacter (the game's own ancestor test)."""
        raw = read(self.h, self.base + MOB_CLASS, 8)
        mob = struct.unpack("<Q", raw)[0] if raw else 0
        owner = read(self.h, obj + OWNER, 8)
        owner = struct.unpack("<Q", owner)[0] if owner else 0
        if not mob or not owner:
            return False
        depth = read(self.h, mob + DEPTH, 4)
        cls = read(self.h, owner + CLASS, 8)
        cls = struct.unpack("<Q", cls)[0] if cls else 0
        head = read(self.h, cls + CHAIN, 12) if cls and depth else None
        if not head:
            return False
        depth = struct.unpack("<i", depth)[0]
        chain, own_depth = struct.unpack("<Qi", head)
        if not 0 <= depth <= own_depth or not chain:
            return False
        entry = read(self.h, chain + 8 * depth, 8)
        return bool(entry) and struct.unpack("<Q", entry)[0] == mob + CHAIN

    def deflect_table(self):
        """Our copy of the value function's vtable, returning the configured chances (built once)."""
        if self.table:
            return self.table
        original = read(self.h, self.base + DEFLECT["function"], 0x30)
        if not original or not all(self.base < q < self.base + 0x3100000 for q in struct.unpack("<6Q", original)):
            return 0
        at = alloc_near(self.h, self.base)
        write(self.h, at, ROUTINE + struct.pack("<3f", *self.chance))
        table = bytearray(original)
        struct.pack_into("<Q", table, 0x10, at)
        write(self.h, at + 0x40, bytes(table))
        self.table = at + 0x40
        return self.table

    def tick(self, quiet=False):
        if not self.on:
            return
        if self.own_scanner:
            self.scanner.refresh()
        if self.chance is not None:
            own = self.base + DEFLECT["function"]
            for vt in DEFLECT["vtables"]:
                for o in self.scanner.found.get(self.base + vt, []):
                    raw = read(self.h, o + FUNCTION, 0x40)
                    always = read(self.h, o + ALWAYS, 1)
                    if not raw or not always or struct.unpack_from("<Q", raw, TARGET - FUNCTION)[0] != o + FUNCTION:
                        continue
                    if not self.is_mob(o):
                        continue                         # the player's copy
                    if always[0] and not any(self.chance):
                        # Mobs' copies are marked "always triggers": the handler (exe+0xA6F6B0) deflects when the
                        # roll is under the chance OR this byte is set - which is why a chance of 0 alone did
                        # nothing (user, 2026-10-12: mobs still deflect, every time).
                        write(self.h, o + ALWAYS, bytes([0]))
                        self.note("Deflect on mobs: 'always triggers' switched off", quiet)
                    if struct.unpack_from("<Q", raw)[0] != own:
                        continue                         # chance already ours
                    ours = self.deflect_table()
                    if not ours:
                        break
                    write(self.h, o + FUNCTION, struct.pack("<Q", ours))
                    self.note("Deflect on mobs: chance now " + " / ".join(f"{c:.0%}" for c in self.chance), quiet)
        if self.levitation:
            for vt in LEVITATION["vtables"]:
                for o in self.scanner.found.get(self.base + vt, []):
                    raw = read(self.h, o + 0x1F8, 0x20)
                    if not raw or not self.is_mob(o):
                        continue
                    for name, value in self.levitation.items():
                        off = LEVITATION["fields"][name]
                        now = struct.unpack_from("<f", raw, off - 0x1F8)[0]
                        if abs(now - value) > 1e-6 and abs(now) < 1000:      # a sane float that isn't ours yet
                            write(self.h, o + off, struct.pack("<f", value))
                            self.note("Levitation Shot on mobs: " + ", ".join(f"{k} {v:g}" for k, v in self.levitation.items()), quiet)

    def note(self, text, quiet):
        if not quiet and text not in self.said:
            self.said.add(text)
            print(text)


if __name__ == "__main__":
    h, base = open_game()
    if not h:
        sys.exit("Minecraft Dungeons isn't running")
    w = MobEnchants(h, base)
    if "--show" in sys.argv:
        for vt in DEFLECT["vtables"] + LEVITATION["vtables"]:
            w.scanner.register(vt)
        w.scanner.refresh()
        for vt in DEFLECT["vtables"] + LEVITATION["vtables"]:
            objs = w.scanner.found.get(base + vt, [])
            print(f"class vtable exe+{vt:#x}: {len(objs)} copies, owned by mobs: {sum(w.is_mob(o) for o in objs)}")
        sys.exit()
    while pid_of():
        w.tick()
        time.sleep(1)
