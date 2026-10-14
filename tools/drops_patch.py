"""Let seasonal (Tower-only) gear drop in missions, in the running game (Drops.toml). Data only.

    python tools/drops_patch.py            # apply Drops.toml
    python tools/drops_patch.py --show     # how many missions each item of Drops.toml drops in right now

Where an item drops is part of its definition (a global, tools/item_registry.json): at +0xB0 a map from level id
(one byte) to that level's drop settings - a TSet with 0x50-byte elements (key at +0, hash links at +0x48/+0x4C),
allocation bits inline at +0xC0, the hash at +0xE8/+0xF0 with its size at +0xF8 - and a flag byte at +0x100 that
is 1 on every item with a list. Read 2026-10-06: 207 items have 4-39 levels; the 19 seasonal items, Bone Cudgel
(SkeletonHammer) and BatCrossbow have none, which is all that keeps them out of missions.
For each `item = [donors]` in Drops.toml this builds the item a map of its own holding the levels of all the
donors together (new memory, nothing shared), so it drops wherever any of them does; links it to the plain item
its family's uniques belong to; and takes off its seasonal-event mark, without which the game's loot filters
skip it whatever its level list says.
NOT YET SEEN WORKING: the level list and the link alone did nothing (user, 2026-10-13); the seasonal mark is the
part found last. Unknown still: whether the game builds a mission's loot pool when the mission loads or earlier.
"""
import json
import struct
import sys
import time
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aplus_patch import open_game  # noqa: E402
from builtins_patch import alloc, write  # noqa: E402
from memprobe import read  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "Drops.toml"
REGISTRY = json.loads((ROOT / "tools" / "item_registry.json").read_text())
MAP, FLAG, ELEMENT = 0xB0, 0x100, 0x50
GRACE = 60            # seconds the game gets to make an item's level list itself once its family's are made
BASE_ITEM = 0x228     # a unique's plain item (pointer to its definition); 0 on a plain item - and on 13 of the 19
                      # seasonal items (read 2026-10-12)
SEASON, SEASONS = 0x1E1, 5    # the seasonal event an item belongs to (1-5; 0 = none). The game's loot filters
                      # (exe+0xB09440 and its neighbours) only take items for which this is 0 (exe+0xB654F0) -
                      # THE reason seasonal gear never drops in missions (found 2026-10-13 from the items'
                      # registration code: a seasonal item's builder gets its event number at +0x1C9, which the
                      # definition's constructor exe+0xB19D90 stores at +0x1E1)


def definition(h, base, item):
    raw = read(h, base + int(REGISTRY[item], 16), 8) if item in REGISTRY else None
    return struct.unpack("<Q", raw)[0] if raw else 0


def levels(h, definition_):
    """Number of levels in the item's drop map, or None if it can't be read."""
    raw = read(h, definition_ + MAP + 8, 8) if definition_ else None
    return struct.unpack("<II", raw)[0] if raw else None


def entries(h, definition_):
    """{level id: the level's 0x50-byte drop entry} of an item, in the order the game keeps them."""
    raw = read(h, definition_ + MAP, 16) if definition_ else None
    data, num, room = struct.unpack("<QII", raw) if raw else (0, 0, 0)
    body = read(h, data, num * ELEMENT) if data and 0 < num <= room <= 128 else None
    return {body[i * ELEMENT]: body[i * ELEMENT:(i + 1) * ELEMENT] for i in range(num)} if body else {}


def give_map(h, target, donors):
    """Give `target` the levels of all `donors` together (an earlier donor's entry wins where two list a level).
    Builds a fresh map in new memory: elements, allocation bits, and the hash chains the game looks levels up by
    (bucket = level id & (buckets - 1); each element holds the next element of its bucket and its bucket)."""
    merged = {}
    for donor in donors:
        for level, entry in entries(h, donor).items():
            merged.setdefault(level, entry)
    n = len(merged)
    if not 0 < n <= 128:
        return 0
    buckets = 64 if n <= 64 else 128
    heads, body = [-1] * buckets, bytearray()
    for i, (level, entry) in enumerate(merged.items()):
        e = bytearray(entry)
        bucket = level & (buckets - 1)
        struct.pack_into("<ii", e, 0x48, heads[bucket], bucket)
        heads[bucket] = i
        body += e
    new_data, new_hash = alloc(h, len(body)), alloc(h, buckets * 4)
    box = bytearray(read(h, donors[0] + MAP, FLAG - MAP))
    if not new_data or not new_hash or len(box) != FLAG - MAP:
        return 0
    write(h, new_data, bytes(body))
    write(h, new_hash, struct.pack(f"<{buckets}i", *heads))
    bits = (1 << n) - 1
    struct.pack_into("<QII", box, 0x00, new_data, n, n)           # elements: data, count, room
    box[0x10:0x20] = bits.to_bytes(16, "little")                  # which element slots are in use (inline, 128 bits)
    struct.pack_into("<QII", box, 0x20, 0, n, 128)                # no overflow bit storage; bits used, bits available
    struct.pack_into("<ii", box, 0x30, -1, 0)                     # no free slots
    struct.pack_into("<QI", box, 0x40, new_hash, buckets)         # hash buckets
    write(h, target + MAP, bytes(box))
    write(h, target + FLAG, bytes([1]))                           # the "has a level list" flag
    return n


def give_base(h, target, donors):
    """Point a seasonal item at the plain item its family's uniques belong to, if it has none. True if written."""
    raw = read(h, target + BASE_ITEM, 8)
    if not raw or struct.unpack("<Q", raw)[0]:
        return False
    for donor in donors:
        own = read(h, donor + BASE_ITEM, 8)
        own = struct.unpack("<Q", own)[0] if own else 0
        if own:
            write(h, target + BASE_ITEM, struct.pack("<Q", own))
            return True
    return False


def clear_season(h, target):
    """Take the seasonal-event mark off an item. True if written."""
    raw = read(h, target + SEASON, 1)
    if not raw or not 0 < raw[0] <= SEASONS:
        return False
    write(h, target + SEASON, bytes([0]))
    return True


def apply(h, base, quiet=False, state=None):
    """Make every item of Drops.toml an ordinary mission drop. Returns how many still have no level list.

    The seasonal mark and the family link are written at once. The level list is left to the game where it can
    be: a list is made the first time it is asked for (exe+0xB65390: a "made" byte at +0x100, a maker at +0x140
    that a seasonal item gets from its plain item like any unique), and once the mark is off the game asks.
    Only if that leaves the item empty-handed - asked and still empty, or its family's lists made for GRACE
    seconds and its own still not - is it given the levels of its donors (new memory).
    state: the launcher's {item: when its family's lists were first seen made} and the set of items already
    reported; a one-off run (None) doesn't wait."""
    plan = tomllib.loads(CONFIG.read_text(encoding="utf-8")) if CONFIG.exists() else {}
    since, told = state if state is not None else ({}, set())
    changed = waiting = 0
    for item, donors in plan.items():
        donors = [donors] if isinstance(donors, str) else donors
        tp, dps = definition(h, base, item), [definition(h, base, d) for d in donors]
        have = levels(h, tp)
        if not tp or not all(dps) or have is None:
            waiting += 1
            if not quiet:
                print(f"  ! {item} = {donors!r}: not found in the game - skipped")
            continue
        done = []
        if give_base(h, tp, dps):
            done.append("linked to its family's plain item")
        if clear_season(h, tp):
            done.append("seasonal mark off")
        if have:
            if item not in told:
                told.add(item)
                done.append(f"drops in {have} levels (the game's own list)")
        else:
            family_made = any(levels(h, d) for d in dps)
            asked = read(h, tp + FLAG, 1) == b"\x01"
            overdue = family_made and (state is None or time.time() - since.setdefault(item, time.time()) >= GRACE)
            n = give_map(h, tp, dps) if family_made and (asked or overdue) else 0
            if n:
                told.add(item)
                done.append(f"given the {n} levels of {', '.join(d.split('/')[1] for d in donors)}")
            else:
                waiting += 1
                if not quiet:
                    print(f"  {item}: no level list yet (the game makes them on first use)")
        if done:
            changed += 1
            print(f"  {item}: " + ", ".join(done))
    if changed or not quiet:
        print(f"mission drops: {changed} items changed" + (f", {waiting} still without a level list" if waiting else ""))
    return waiting


class Drops:
    """Launcher watcher: repeats apply() until every item has its level list."""
    def __init__(self, h, base):
        self.h, self.base, self.waiting = h, base, 1
        self.state = ({}, set())

    def tick(self):
        if self.waiting:
            self.waiting = apply(self.h, self.base, quiet=True, state=self.state)


if __name__ == "__main__":
    h, base = open_game()
    if not h:
        sys.exit("Minecraft Dungeons isn't running")
    if "--show" in sys.argv:
        for item in tomllib.loads(CONFIG.read_text(encoding="utf-8")):
            print(f"{item:36} {levels(h, definition(h, base, item))}")
    else:
        apply(h, base)
