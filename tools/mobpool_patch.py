"""Which enchantments enchanted mobs can roll (MobPool.toml). Data only.

    python tools/mobpool_patch.py            # apply MobPool.toml
    python tools/mobpool_patch.py --show     # the pool as it is in the running game

How the game picks (from the exe, 2026-10-13): when a mob is enchanted, exe+0xA7ACB0 walks every enchantment
definition and keeps those for which exe+0xA7B780 says yes:
    definition +0xD5 is 0                      (a switch nothing in the game sets)
    definition +0xD3 is not 0                  "mobs may roll this" - on by default, and switched off by the
                                               registration code of every enchantment mobs never get (Looting,
                                               Leeching, Sharpness, Infinity ...); see research/enchant_flags.py
    its tag list (+0x08) does not hold tag 2
    its gear byte (+0x00: 1 melee, 2 ranged, 8 armor) fits the mob, and its game version is not newer
Nothing is cached: the list is built again for every mob. So setting +0xD3 of a definition (found by type id
through the table at exe+0x44EF680, as the game does) to 0 takes the enchantment out of the pool from the next
mob on, and 1 puts one in.
The player's side never looks at this byte. Mobs that carry an enchantment by design (a boss's own list) are not
rolled and keep theirs.

(An earlier version of this tool changed the byte at +4, on a wrong reading; that byte is something else.)
NOT YET SEEN WORKING.
"""
import json
import struct
import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aplus_patch import open_game  # noqa: E402
from builtins_patch import write  # noqa: E402
from memprobe import read  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "MobPool.toml"
IDS = json.loads((ROOT / "tools" / "enchant_ids.json").read_text())
GEAR, TYPE_ID, MOBS, OFF = 0x00, 0x03, 0xD3, 0xD5
TABLE = 0x44EF680     # global: pointer to the definitions by type id (8 bytes each)
GEARS = {1: "melee", 2: "ranged", 8: "armor"}


def definition(h, base, name):
    """(address, its first 0xD8 bytes) of an enchantment's definition, or (0, None). Looked up the way the game's
    own roll does it - by type id in the table at exe+0x44EF680 - and only trusted if the definition carries
    that id."""
    table = read(h, base + TABLE, 8) if name in IDS else None
    table = struct.unpack("<Q", table)[0] if table else 0
    raw = read(h, table + 8 * IDS[name], 8) if table else None
    at = struct.unpack("<Q", raw)[0] if raw else 0
    body = read(h, at, 0xD8) if at else None
    if not body or body[TYPE_ID] != IDS[name]:
        return 0, None
    return at, body


def apply(h, base):
    plan = tomllib.loads(CONFIG.read_text(encoding="utf-8")) if CONFIG.exists() else {}
    changed = []
    # [pool] name = true / false (every mob enchantment listed; 2026-10-18), or the older remove / add lists
    pool = plan.get("pool", {})
    lists = [("remove", [n for n, on in pool.items() if on is False] + plan.get("remove", [])),
             ("add", [n for n, on in pool.items() if on is True] + plan.get("add", []))]
    for (key, names), (value, word) in zip(lists, ((0, "no longer rolled by mobs"), (1, "can now be rolled by mobs"))):
        for name in names:
            at, body = definition(h, base, name)
            if not at:
                print(f"  ! {name}: not found in the game - skipped")
            elif body[MOBS] > 1 or body[OFF] > 1:
                print(f"  ! {name}: unexpected data in its definition - left alone")
            elif bool(body[MOBS]) != bool(value):
                write(h, at + MOBS, bytes([value]))
                changed.append(name)
                print(f"  {name}: {word}")
    print(f"mob enchantment pool: {len(changed)} changed")


def show(h, base):
    pool = {}
    for name in sorted(n for n in IDS if IDS[n] < 162):
        at, body = definition(h, base, name)
        if body and body[MOBS] and not body[OFF]:
            gear = "+".join(g for bit, g in GEARS.items() if body[GEAR] & bit) or "other"
            pool.setdefault(gear, []).append(name)
    for gear, names in sorted(pool.items()):
        print(f"{gear}: " + ", ".join(names))


if __name__ == "__main__":
    h, base = open_game()
    if not h:
        sys.exit("Minecraft Dungeons isn't running")
    if "--show" in sys.argv:
        show(h, base)
    else:
        apply(h, base)
