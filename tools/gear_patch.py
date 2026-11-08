"""Which gear an enchantment can roll on (EnchantGear.toml). Data only.

    python tools/gear_patch.py            # apply EnchantGear.toml
    python tools/gear_patch.py --show     # every enchantment's gear in the running game

Every enchantment definition has a gear byte at +0x00, a set of bits: 1 melee, 2 ranged, 8 armor (see
research/enchant_flags.py and mobpool_patch.py, which reads the same byte for mobs). Most carry one bit; some
carry two - Critical Hit, Committed, Smiting, Looting and others are 1 + 2, and in the user's save a bow rolled
Critical Hit - so an enchantment with an extra bit should be offered on that gear too. This tool only ADDS bits
(EnchantGear.toml `also_on`), never takes one away. An enchantment works from any gear: it is a component on its
wearer, not on the item (armor built-ins past the cap already carry Burst Bowstring and Roll Charge).
Unlock (EnchantGear.toml `unlock`): every enchantment the game keeps for one unique item sets byte +0xD0 = 1
(Shadow Shot, Rushdown, Shared Pain, Thrive Under Pressure, ...), and no enchantment that rolls does
(research/enchant_flags.py, 2026-11-05). Clearing it should let that enchantment roll like any other - a guess
until seen in game. Only enchantments whose tiers really differ are unlocked (user rule, 2026-11-05).
Mobs: the same byte decides which mobs may roll an enchantment, but only those whose "mobs may roll" byte (+0xD3)
is on - Burst Bowstring's is off, so mobs still never get it.
Confirmed in the game's code (2026-11-05): the player roll (exe+0xA7ADA0) walks every definition and offers it only if
+0xD5 == 0, +0xD0 == 0 (not unique-only), +0x00 has the item's bit (item kind 10 -> 1, 11 -> 2, 12 -> 8), its DLC is
owned and the item doesn't already have it; +0x02 sorts it into the powerful or the normal list. It reads the rolls'
own COPIES of the definitions (made at the game's first roll, mobpool_patch.COPIES), so every change goes to the
definition and to its copy (2026-11-05: changing only the definitions reached no drop).
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aplus_patch import open_game  # noqa: E402
from builtins_patch import write  # noqa: E402
from memprobe import read  # noqa: E402
from mobpool_patch import GEARS, IDS, copies, definition, write_both  # noqa: E402
import settings  # noqa: E402

CONFIG = settings.path("EnchantGear.toml")
GEAR = 0x00
UNIQUE_ONLY = 0xD0
POWERFUL = 0x02   # 1 = a "Powerful" enchantment: its own roll list and the higher enchantment-point cost (2 / 3 / 4)
# +0x08: a list of tag bytes (data, count at +0x10). The roll checks two against the item: 2 (an item check, see
# exe+0xB656F0 / exe+0xB65690) and 3 - only on a ranged weapon that shoots arrows. Burst Bowstring and Roll Charge
# carry [3], so opening them to armor also needs that tag gone (found 2026-11-05: Burst Bowstring never rolled on
# armor with only its gear byte changed).
TAGS, BOW_TAG = 0x08, 3
BITS = {name: bit for bit, name in GEARS.items()}   # melee 1, ranged 2, armor 8


def bow_only(h, at):
    """Whether the definition (or copy) at `at` has exactly the tag list [3]: offered only on a ranged weapon that
    shoots arrows (the roll's item check exe+0xB654C0: item kind +0x89 == 11 and +0x88 == 1)."""
    raw = read(h, at + TAGS, 12)
    if not raw:
        return False
    data, count = struct.unpack("<Qi", raw)
    return count == 1 and (read(h, data, 1) or b"\x00")[0] == BOW_TAG


def stale(h, base, name, offset, value):
    """Whether any of the rolls' copies of name's definition still has another value at offset."""
    return any((read(h, c + offset, 1) or bytes([value]))[0] != value for c in copies(h, base, name))


def gear_names(value):
    return "+".join(g for bit, g in GEARS.items() if value & bit) or "other"


def apply(h, base):
    plan = settings.load(CONFIG).get("also_on", {})
    changed = 0
    for name, gears in plan.items():
        at, body = definition(h, base, name)
        if not at:
            print(f"  ! {name}: not found in the game - skipped")
            continue
        unknown = [g for g in gears if g not in BITS]
        if unknown or body[GEAR] not in (1, 2, 3, 8, 9, 10, 11):
            print(f"  ! {name}: unknown gear {unknown or body[GEAR]} - left alone")
            continue
        new = body[GEAR]
        for g in gears:
            new |= BITS[g]
        if new != body[GEAR] or stale(h, base, name, GEAR, new):
            write_both(h, base, name, at, GEAR, bytes([new]))
            changed += 1
            print(f"  {name}: rolls on {gear_names(new)} (was {gear_names(body[GEAR])})")
        if bow_only(h, at) or any(bow_only(h, c) for c in copies(h, base, name)):
            for where in [at] + copies(h, base, name):
                write(h, where + TAGS + 8, b"\x00\x00\x00\x00")   # the list's count: no tags
            changed += 1
            print(f"  {name}: no longer bow-only")
    for name in settings.load(CONFIG).get("unlock", []):
        at, body = definition(h, base, name)
        if not at:
            print(f"  ! {name}: not found in the game - skipped")
        elif body[UNIQUE_ONLY] == 1 or stale(h, base, name, UNIQUE_ONLY, 0):
            write_both(h, base, name, at, UNIQUE_ONLY, b"\x00")
            changed += 1
            print(f"  {name}: unlocked - can roll on {gear_names(body[GEAR])}")
        elif body[UNIQUE_ONLY] != 0:
            print(f"  ! {name}: unexpected unique-only byte {body[UNIQUE_ONLY]} - left alone")
    # Rarity (EnchantGear.toml [rarity] powerful / common; user, 2026-11-08): the "Powerful" byte, on the definition
    # and on the rolls' copies - the card's badge, the point cost and which roll list it comes from
    rarity = settings.load(CONFIG).get("rarity", {})
    for value, names in ((1, rarity.get("powerful", [])), (0, rarity.get("common", []))):
        for name in names:
            at, body = definition(h, base, name)
            if not at:
                print(f"  ! {name}: not found in the game - skipped")
            elif body[POWERFUL] != value or stale(h, base, name, POWERFUL, value):
                write_both(h, base, name, at, POWERFUL, bytes([value]))
                changed += 1
                print(f"  {name}: {'powerful' if value else 'common'}")
    print(f"enchantment gear: {changed} changed")


def show(h, base):
    for name in sorted(n for n in IDS if IDS[n] < 162):
        at, body = definition(h, base, name)
        if body:
            print(f"{name:28} {gear_names(body[GEAR]):18} {'unique only' if body[UNIQUE_ONLY] == 1 else ''}")


if __name__ == "__main__":
    h, base = open_game()
    if not h:
        sys.exit("Minecraft Dungeons isn't running")
    if "--show" in sys.argv:
        show(h, base)
    else:
        apply(h, base)
