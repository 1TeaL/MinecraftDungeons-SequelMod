"""Test log: what our blueprint enchantments see and do, read from the running game into Mods/SequelMod/test.log.

    python tools/sequel_log.py            # watch the running game until it closes (the launcher runs it too)
    python tools/sequel_log.py --once     # one look, printed

Read-only: nothing in the game is changed. Our enchantments keep counters in their own blueprint variables (the
same ones the on-screen TEST readout shows - Debuffs.toml debug); this finds those objects by their class names
and reads the variables by name, once a second, and writes a line whenever a number changed.

How it finds things (UE 4.22, read 2026-11-07):
  - names: the game's name table (FName entries: next pointer, index at +8, the text at +0xC - read in the game;
    16384 per chunk), found by
    looking through the exe's data for the table whose first two names are "None" and "ByteProperty"
  - objects: the game's object list (live_objects.OBJECTS); an object's class at +0x10, its name at +0x18
  - variables: a blueprint class's own properties (the Children chain of the class, UField Next at +0x28), each
    with its name, its kind (IntProperty, FloatProperty...) and its place in the object (Offset_Internal)
The places inside the structures are checked when found (see probe()), so a wrong guess prints a note instead of
nonsense.
"""
import struct
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aplus_patch import open_game  # noqa: E402
from live_objects import CHUNK, ENTRY, OBJECTS  # noqa: E402
from memprobe import alive, main_module, read  # noqa: E402

LOG = Path(__file__).resolve().parent.parent / "test.log"
# where the name table's pointer sat in the exe last time (exe-relative): checked first, so a start needs no search
REMEMBER = Path(__file__).resolve().parent / "sequel_log_names.txt"
NAMES_PER_CHUNK = 0x4000
TEXT = 0xC                       # an FName entry: hash-next pointer, index (bit 0: wide), text at +0xC
CLASS, NAME, OUTER = 0x10, 0x18, 0x20
NEXT = 0x28                      # UField::Next
CDO_FLAG = 0x10                  # RF_ClassDefaultObject
# what to log: blueprint class -> (shown name, [variables])
WATCHED = {
    "BP_Knockback_C": ("Sweeping Edge", ["Looks", "Hits", "LastHit", "Bonuses", "LastBonus"]),
    "BP_EmeraldDivination_C": ("Ignite", ["Looks", "Hits", "LastHit", "Seen", "Bonuses", "LastBonus", "Extra"]),
    "BP_Altruistic_C": ("Venom Siphon", ["Looks", "Hits", "LastHit", "Seen", "Bonuses", "LastBonus", "Extra"]),
    "BP_ThriveUnderPressure_C": ("Shatter", ["Looks", "Hits", "LastHit", "Seen", "Bonuses", "LastBonus"]),
    "BP_Rushdown_C": ("Shadowcloak", ["Looks", "Hits", "Kills", "Extra"]),
    "BP_Rampaging_C": ("Rampaging", ["Looks", "Hits", "Kills", "Extra", "LastBonus"]),
    "BP_GuardingStrike_C": ("Guarding Strike", ["Looks", "Hits", "Kills", "Extra", "ArtUses"]),
    "BP_PotionThirstRanged_C": ("Refreshment (ranged)", ["Looks", "Kills", "Extra", "LastBonus", "Left"]),
    "BP_Thundering_C": ("Thundering", ["Looks", "Hits", "Weapon", "Seen", "Bonuses", "LastBonus"]),
    "BP_Leeching_C": ("Leeching", ["Looks", "Hits", "Kills", "Extra", "LastBonus", "ArtUses"]),
    "BP_PotionThirstMelee_C": ("Refreshment", ["Looks", "Hits", "Kills", "Extra", "LastBonus", "Left"]),
    "BP_Exploding_C": ("Exploding", ["Looks", "Hits", "Kills", "Extra", "LastBonus"]),
    "BP_Shockwave_C": ("Shockwave", ["Looks", "Hits", "Weapon", "Seen", "Bonuses", "LastBonus"]),
    "BP_Swirling_C": ("Swirling", ["Looks", "Hits", "Weapon", "Seen", "Bonuses", "LastBonus"]),
    "BP_Thorns_C": ("Overload", ["Looks", "Hits", "Charges", "ArrowHits", "Bonuses", "LastBonus", "Extra"]),
    "BP_Barrier_C": ("Battle Hardened", ["Hits", "Shots", "Stacks"]),
    "BP_LevitationShot_C": ("Relentless", ["Hits", "ArrowHits"]),
    "BP_levitationShot_C": ("Relentless", ["Hits", "ArrowHits"]),   # our package's spelling
    "BP_Electrified_C": ("Electrified", ["Seen", "Bonuses", "LastBonus"]),
    "BP_ShockWeb_C": ("Shock Web", ["Seen", "Bonuses", "LastBonus"]),
    "BP_FireAspect_C": ("Fire Aspect", ["Looks", "Seen", "Bonuses"]),
    "BP_FoodReserves_C": ("Bottomless Brew", ["Charges", "Recharge", "BaseLeft"]),
    "BP_SequelStatusWatcher_C": ("Fire / poison watcher", ["Ticks", "LastFire", "LastPoison", "Hurt", "LastHurt"]),
}
LABELS = {"Looks": "looks", "Hits": "hits", "LastHit": "last hit", "Seen": "status seen", "Bonuses": "extras",
          "LastBonus": "last extra", "Extra": "spreads/heals", "Cloaks": "Shadow Forms", "Ticks": "looks",
          "LastFire": "fire tier", "LastPoison": "poison tier", "Hurt": "mobs hurt", "LastHurt": "last amount"}
# Shadowcloak's Seen is the mission's kill count
LABELS_FOR = {("Bottomless Brew", "Charges"): "extras ready", ("Bottomless Brew", "Recharge"): "refill progress (s)",
              ("Bottomless Brew", "BaseLeft"): "potion wait left (s)",
              ("Guarding Strike", "Kills"): "your kills", ("Guarding Strike", "Extra"): "shields",
              ("Leeching", "ArtUses"): "artifact uses", ("Guarding Strike", "ArtUses"): "artifact uses",
("Overload", "Charges"): "charges", ("Overload", "Bonuses"): "discharges", ("Overload", "Extra"): "arcs",
              ("Overload", "LastBonus"): "last discharge", ("Overload", "ArrowHits"): "arrow hits", ("Battle Hardened", "Hits"): "your hits",
              ("Battle Hardened", "Stacks"): "stacks", ("Battle Hardened", "Heals"): "boosted heals",
              ("Battle Hardened", "LastBonus"): "last extra heal", ("Electrified", "Seen"): "mobs zapped",
              ("Electrified", "Bonuses"): "extras", ("Electrified", "LastBonus"): "last extra", ("Shock Web", "Seen"): "beam zaps", ("Shock Web", "Bonuses"): "extras",
              ("Shock Web", "LastBonus"): "last extra", ("Fire Aspect", "Seen"): "arrow hits", ("Fire Aspect", "Bonuses"): "set on fire",
("Shadowcloak", "Kills"): "your kills", ("Shadowcloak", "Extra"): "Shadow Forms",
              ("Rampaging", "Kills"): "your kills", ("Rampaging", "Extra"): "boosts", ("Rampaging", "LastBonus"): "last boost (s)",
              ("Refreshment (ranged)", "Kills"): "your kills", ("Refreshment (ranged)", "Extra"): "cuts",
              ("Refreshment (ranged)", "LastBonus"): "last cut (s)", ("Refreshment (ranged)", "Left"): "cooldown left after (s)",
              ("Thundering", "Weapon"): "your last hit", ("Thundering", "Seen"): "strikes",
              ("Thundering", "Bonuses"): "mobs hit extra", ("Thundering", "LastBonus"): "last extra", ("Leeching", "Extra"): "heals", ("Leeching", "LastBonus"): "last heal",
              ("Refreshment", "Extra"): "cuts", ("Refreshment", "LastBonus"): "last cut (s)",
              ("Refreshment", "Left"): "cooldown left after (s)", ("Leeching", "Kills"): "your kills",
              ("Refreshment", "Kills"): "your kills",
              ("Exploding", "Kills"): "your kills", ("Exploding", "Extra"): "explosions",
              ("Exploding", "LastBonus"): "last explosion damage",
              ("Shockwave", "Weapon"): "your last hit", ("Shockwave", "Seen"): "your waves",
              ("Shockwave", "Bonuses"): "mobs hit extra", ("Shockwave", "LastBonus"): "last extra",
              ("Swirling", "Weapon"): "your last hit", ("Swirling", "Seen"): "spins",
              ("Swirling", "Bonuses"): "mobs hit extra", ("Swirling", "LastBonus"): "last extra"}


def q(h, a):
    raw = read(h, a, 8)
    return struct.unpack("<Q", raw)[0] if raw and len(raw) == 8 else 0


class Game:
    def __init__(self, h, base):
        self.h, self.base = h, base
        self.names, self.table = {}, 0

    # ---- names -------------------------------------------------------------------------------------------------
    def find_names(self):
        """The name table: a pointer in the exe's data to an array of chunk pointers whose first entries are
        "None" and "ByteProperty"."""
        try:
            at = int(REMEMBER.read_text().strip(), 16)
            p = q(self.h, self.base + at)
            if p and self._is_table(p):
                self.table = p
                return p
        except (OSError, ValueError):
            pass
        _, size = main_module(self.h)
        hdr = read(self.h, self.base, 0x1000)
        pe = struct.unpack_from("<I", hdr, 0x3C)[0]
        count = struct.unpack_from("<H", hdr, pe + 6)[0]
        opt = struct.unpack_from("<H", hdr, pe + 20)[0]
        sections = []
        for i in range(count):
            s = pe + 24 + opt + 40 * i
            vsize, va, flags = struct.unpack_from("<I", hdr, s + 8)[0], struct.unpack_from("<I", hdr, s + 12)[0], \
                struct.unpack_from("<I", hdr, s + 36)[0]
            if flags & 0x80000000:                     # writable: data
                sections.append((va, vsize))
        for va, vsize in sections:
            for at in range(0, vsize, 0x10000):
                block = read(self.h, self.base + va + at, min(0x10000, vsize - at)) or b""
                for k in range(0, len(block) - 7, 8):
                    p = struct.unpack_from("<Q", block, k)[0]
                    if not (0x10000000 < p < 0x7FFFFFFFFFFF) or self.base <= p < self.base + size:
                        continue
                    if self._is_table(p):
                        self.table = p
                        try:
                            REMEMBER.write_text(f"{va + at + k:X}")
                        except OSError:
                            pass
                        return p
        return 0

    def _is_table(self, p):
        chunk0 = q(self.h, p)
        if not chunk0:
            return False
        e0, e1 = q(self.h, chunk0), q(self.h, chunk0 + 8)
        if not (e0 and e1):
            return False
        a, b = read(self.h, e0 + TEXT, 5), read(self.h, e1 + TEXT, 13)
        return a == b"None\0" and b == b"ByteProperty\0"

    def name(self, index):
        if index in self.names:
            return self.names[index]
        chunk = q(self.h, self.table + 8 * (index // NAMES_PER_CHUNK))
        entry = q(self.h, chunk + 8 * (index % NAMES_PER_CHUNK)) if chunk else 0
        text = ""
        if entry:
            head = read(self.h, entry + 8, 4)
            wide = bool(head and head[0] & 1)
            raw = read(self.h, entry + TEXT, 256) or b""
            if wide:
                text = raw.decode("utf-16-le", "replace").split("\0")[0]
            else:
                text = raw.split(b"\0")[0].decode("latin-1")
        self.names[index] = text
        return text

    def obj_name(self, o):
        raw = read(self.h, o + NAME, 8)
        if not raw:
            return ""
        index, number = struct.unpack("<ii", raw)
        n = self.name(index)
        return f"{n}_{number - 1}" if number else n

    # ---- objects -----------------------------------------------------------------------------------------------
    def all_objects(self):
        head = read(self.h, self.base + OBJECTS, 0x20)
        table, _, room, count, chunk_room, chunks = struct.unpack("<QQiiii", head)
        if not (table and 0 < count <= room and 0 < chunks <= chunk_room <= 0x400):
            return []
        out = []
        for c, at in enumerate(struct.unpack(f"<{chunks}Q", read(self.h, table, 8 * chunks))):
            data = read(self.h, at, min(CHUNK, count - c * CHUNK) * ENTRY) if at else None
            if data:
                out += [o for (o,) in struct.iter_unpack("<Q16x", data[:len(data) // ENTRY * ENTRY]) if o]
        return out

    def headers(self, objects):
        """{object: (flags, class, name index)} - objects sharing a 64 KB page read at once."""
        by_page, out = {}, {}
        for o in objects:
            by_page.setdefault(o & ~0xFFFF, []).append(o)
        for page, members in by_page.items():
            data = read(self.h, page, 0x10000) if len(members) >= 8 else None
            for o in members:
                raw = data[o - page:o - page + 0x20] if data and o - page + 0x20 <= len(data) else read(self.h, o, 0x20)
                if raw and len(raw) == 0x20:
                    out[o] = (struct.unpack_from("<I", raw, 8)[0], struct.unpack_from("<Q", raw, CLASS)[0],
                              struct.unpack_from("<i", raw, NAME)[0])
        return out

    # ---- a blueprint class's variables -------------------------------------------------------------------------
    def properties(self, cls):
        """{variable name: (kind, offset)} of a class's own properties. The Children pointer and the offset field
        are found by trying the places 4.22 uses and checking that the names come out sensible."""
        for children_at in (0x38, 0x40, 0x48, 0x30):
            first = q(self.h, cls + children_at)
            props, p, n = {}, first, 0
            while p and n < 200:
                kind = self.obj_name(q(self.h, p + CLASS))
                if not kind.endswith("Property") and kind != "Function":
                    props = None
                    break
                if kind.endswith("Property"):
                    props[self.obj_name(p)] = (kind, p)
                p, n = q(self.h, p + NEXT), n + 1
            if props:
                for off_at in (0x44, 0x4C, 0x40, 0x48):
                    offs = {k: struct.unpack("<i", read(self.h, v[1] + off_at, 4))[0] for k, v in props.items()}
                    if all(0x28 <= o < 0x4000 for o in offs.values()) and len(set(offs.values())) == len(offs):
                        return {k: (props[k][0], offs[k]) for k in props}
        return {}


class SequelLog:
    """The launcher's watcher: tick() about once a second."""

    def __init__(self, h, base, scanner=None, path=LOG):
        self.g = Game(h, base)
        self.path, self.ready = path, False
        self.classes = {}          # class address -> (shown name, {var: (kind, offset)})
        self.instances = {}        # object -> class address
        self.last = {}             # object -> line
        self.next_look = 0.0
        self.busy = None
        self.out = open(path, "a", encoding="utf-8")
        self.write(f"--- test log started {datetime.now():%Y-%m-%d %H:%M:%S}")

    def write(self, line):
        self.out.write(f"{datetime.now():%H:%M:%S} {line}\n")
        self.out.flush()

    def look(self):
        """Find our classes and their objects (beside the passes: a look through the whole object list)."""
        try:
            if not self.g.table and not self.g.find_names():
                self.write("! the game's name table was not found - nothing to log")
                return
            objects = self.g.all_objects()
            heads = self.g.headers(objects)
            wanted = set(WATCHED)
            # classes first: objects whose own name is one of ours (UClass objects)
            for o, (flags, cls, name) in heads.items():
                n = self.g.name(name)
                if n in wanted and o not in self.classes:
                    props = self.g.properties(o)
                    if not props:
                        continue                    # a class without our variables (the game's own copy): not ours
                    shown, wanted_vars = WATCHED[n]
                    missing = [v for v in wanted_vars if v not in props]
                    if missing:
                        self.write(f"! {shown}: variables not found: {', '.join(missing)} (found: {', '.join(props) or 'none'})")
                    self.classes[o] = (shown, props, wanted_vars)
            for o, (flags, cls, name) in heads.items():
                if cls in self.classes and not flags & CDO_FLAG:
                    self.instances[o] = cls
            self.ready = True
        except Exception as e:  # noqa: BLE001 - a bad read (level loading); the next look tries again
            self.write(f"! look failed: {e!r}")

    def tick(self):
        now = time.time()
        if now >= self.next_look and not (self.busy and self.busy.is_alive()):
            self.next_look = now + (10 if self.ready else 3)    # new objects (equipped gear, a new level) in 10 s
            self.busy = threading.Thread(target=self.look, daemon=True)
            self.busy.start()
        for o, cls in list(self.instances.items()):
            shown, props, wanted_vars = self.classes[cls]
            raw = read(self.g.h, o, 0x20)
            if not raw or struct.unpack_from("<Q", raw, CLASS)[0] != cls:
                del self.instances[o]                            # gone (unequipped, level left)
                self.last.pop(o, None)
                continue
            parts = []
            for var in wanted_vars:
                if var not in props:
                    continue
                kind, off = props[var]
                data = read(self.g.h, o + off, 4)
                if not data:
                    continue
                value = struct.unpack("<f", data)[0] if kind == "FloatProperty" else struct.unpack("<i", data)[0]
                label = LABELS_FOR.get((shown, var), LABELS.get(var, var))
                parts.append(f"{label} {round(value) if isinstance(value, float) else value}")
            line = f"{shown}: " + ", ".join(parts)
            # a line only when something happened: the look counters tick all the time
            key = ", ".join(x for x in parts if not x.startswith("looks "))
            if self.last.get(o) != key:
                self.last[o] = key
                self.write(line)


if __name__ == "__main__":
    h, base = open_game()
    if not h:
        sys.exit("start the game first")
    log = SequelLog(h, base)
    log.look()
    print(f"name table at 0x{log.g.table:X}; classes found: {', '.join(v[0] for v in log.classes.values()) or 'none'}; "
          f"objects: {len(log.instances)}")
    for cls, (shown, props, _) in log.classes.items():
        print(f"  {shown}: " + ", ".join(f"{k} {v[0][:-8]} +0x{v[1]:X}" for k, v in props.items()))
    log.tick()
    if "--once" not in sys.argv:
        while alive(h):
            log.tick()
            time.sleep(1)
    print(f"log: {LOG}")
