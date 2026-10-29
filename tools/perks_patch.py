"""Add perks to armors in the running game (Perks.toml). Data only: no game code is changed.

    python tools/perks_patch.py            # apply Perks.toml
    python tools/perks_patch.py --show     # list every armor's perks

An armor's perks ("35% damage reduction", "-40% artifact cooldown" ...) are a list in its item definition
(the same object the built-in enchantments live in, see builtins_patch.py): a TArray at +0x1A8 of 2-byte
entries {perk id, flag}; flag 2 marks a perk the unique adds over its base armor. The game gives each
list room for 8. What a perk does and its numbers are in the game's code; only the list can be changed.
"""
import struct
import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aplus_patch import open_game  # noqa: E402
from builtins_patch import alloc, REGISTRY, write  # noqa: E402
from memprobe import read  # noqa: E402
import settings  # noqa: E402

CONFIG = settings.path("Perks.toml")
ARRAY = 0x1A8
# The game's own perk names, in id order (EArmorPropertyID in the exe). Saves store perks by these names.
PERK_NAMES = [
    "Unset", "SoulGatheringBoost", "SuperbDamageAbsorption", "MissChance", "TeleportChance", "ItemDamageBoost",
    "ItemCooldownDecrease", "AllyDamageBoost", "IncreasedArrowBundleSize", "MeleeDamageBoost",
    "MeleeAttackSpeedBoost", "RangedDamageBoost", "LifeStealAura", "MoveSpeedAura", "PetBat", "AreaHeal",
    "MoveSpeedReduction", "IncreasedMobTargeting", "PotionCooldownDecrease", "DodgeCooldownIncrease",
    "DodgeSpeedIncrease", "DodgeInvulnerability", "DamageAbsorption", "SlowResistance", "DodgeGhostForm",
    "Beekeeper", "DodgeRoot", "Heavyweight", "EnvironmentalProtection", "EmeraldShield", "ItemCooldownReset",
    "SquidRollQuick", "SquidRollLimited", "HealingAura", "FallResistance", "SquidRoll", "Resonant",
    "ImmunityBoost", "InstantTransmission",
]
PERKS = {name: i for i, name in enumerate(PERK_NAMES) if i}
NAMES = {v: k for k, v in PERKS.items()}


def perks(h, base, item):
    """(list address, [(perk id, flag)], capacity, address of the list header) or None."""
    raw = read(h, base + int(REGISTRY[item], 16), 8)
    definition = struct.unpack("<Q", raw)[0] if raw else 0
    head = read(h, definition + ARRAY, 16) if definition else None
    if not head:
        return None
    data, count, cap = struct.unpack("<QII", head)
    if not (data and 0 < count <= cap <= 16):
        return None
    raw = read(h, data, 2 * count)
    return data, [(raw[i], raw[i + 1]) for i in range(0, len(raw), 2)], cap, definition + ARRAY


def apply(h, base):
    plan = settings.load(CONFIG)
    for item, spec in plan.items():
        add = spec.get("add", [])
        replace = spec.get("set")
        bad = [p for p in add + (replace or []) if p not in PERKS]
        got = perks(h, base, item) if item in REGISTRY else None
        if bad or got is None:
            print(f"  ! {item}: " + (f"unknown perk {bad}" if bad else "no perk list found") + " - skipped")
            continue
        data, current, cap, head = got
        if replace is not None:
            # `set`: the armor's whole list, in this order (a perk it already had keeps its own flag byte)
            if [i for i, _ in current] == [PERKS[p] for p in replace]:
                print(f"  {item}: perks already {', '.join(replace)}")
                continue
            flags = dict(current)
            entries = b"".join(bytes([PERKS[p], flags.get(PERKS[p], 2)]) for p in replace)
            if len(replace) > cap:                    # more than the game's list has room for: a new list
                data = alloc(h, 16)
                if not data:
                    print(f"  ! {item}: no memory - skipped")
                    continue
                cap = 8
            write(h, data, entries)
            write(h, head, struct.pack("<QII", data, len(replace), cap))
            print(f"  {item}: perks now {', '.join(replace)}")
            continue
        new = [PERKS[p] for p in add if PERKS[p] not in [i for i, _ in current]]
        if not new:
            print(f"  {item}: already has {', '.join(add)}")
            continue
        if len(current) + len(new) > cap:
            print(f"  ! {item}: no room for {len(new)} more perks - skipped")
            continue
        write(h, data + 2 * len(current), b"".join(bytes([i, 2]) for i in new))
        write(h, head + 8, struct.pack("<I", len(current) + len(new)))
        print(f"  {item}: added {', '.join(NAMES[i] for i in new)}")


if __name__ == "__main__":
    h, base = open_game()
    if not h:
        sys.exit("Minecraft Dungeons isn't running")
    if "--show" in sys.argv:
        for item in sorted(k for k in REGISTRY if k.startswith("Armor/")):
            got = perks(h, base, item)
            print(item, [NAMES.get(i, i) for i, _ in got[1]] if got else "-")
    else:
        apply(h, base)
