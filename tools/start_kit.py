"""Start in Apocalypse with a starter kit (Settings.toml [start]) - a save edit, made by the launcher while the game is closed.

    python tools/start_kit.py            # apply to every character now (the game must be closed)

Only new characters are changed (user, 2026-10-28): ones still below the starting level (below level 10 if the
starting level is 1), so a character already played for a while is left as it is. A new character that hasn't
unlocked Apocalypse yet gets it unlocked (and selected), so the Default and Adventure campaigns can be skipped; a character whose gear is below the kit's power also gets the kit: plain gear at about
Apocalypse I's power (~70; Apocalypse VII is ~105). Each kit item offers three random enchantment options per slot,
like a fresh drop. A character is changed once: afterwards it has Apocalypse unlocked. The launcher does this
before it starts the game and again after the game closes, so a character made in this session is ready next time.
Saves are backed up by the launcher first (play.backup_saves).
"""
import json
import random
import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import savefile  # noqa: E402
import settings  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CONFIG = settings.path("QoL.toml")
POOLS = json.loads((ROOT / "tools" / "enchant_pools.json").read_text())
ARMOR_PERKS = json.loads((ROOT / "research" / "armor_props_raw.json").read_text())
SAVES = Path.home() / "Saved Games" / "Mojang Studios" / "Dungeons"
DIFFICULTY = {"adventure": "Difficulty_2", "apocalypse": "Difficulty_3"}
GEAR = {"Sword": "melee", "Bow": "ranged", "ScaleMail": "armor"}   # anything else in the kit is an artifact


def perk_names():
    import perks_patch
    return perks_patch.NAMES


def xp_for(level):
    """Total XP at the start of a character level: 100 x (level - 1) x (3 x level - 1) - the game's formula (Minecraft
    Wiki, Dungeons:Experience; matches the saves: 12.5 million XP ~ level 205). One enchantment point per level."""
    return 100 * (level - 1) * (3 * level - 1)


def options(kind, rng):
    """Three slots of three different enchantment options, from what can roll on that kind of gear."""
    pool = [e for e in POOLS[kind] if e not in POOLS.get("soul", [])]
    out = []
    for _ in range(3):
        out += [{"id": e, "investedPoints": 0, "level": 0} for e in rng.sample(pool, 3)]
    return out


def apply(quiet=False):
    cfg = settings.load(CONFIG).get("start", {})
    start = cfg.get("start", "apocalypse" if cfg.get("apocalypse") else "off")
    if start not in DIFFICULTY:
        return
    target = DIFFICULTY[start]
    kp = cfg.get("kit_power", 70)
    power = float(kp.get(start, 70) if isinstance(kp, dict) else kp)
    kit = cfg.get("kit", [])
    lv = cfg.get("start_level", 1)
    level = int(lv.get(start, 1) if isinstance(lv, dict) else lv)
    names = perk_names()
    for f in SAVES.glob("*/Characters/*.dat"):
        try:
            data = json.loads(savefile.decrypt(f.read_bytes()))
        except Exception:  # noqa: BLE001 - no key yet, or not a character save
            continue
        diff = data.get("difficulties")
        if not isinstance(diff, dict):   # an empty slot, never played (no difficulties yet): left for when it is
            continue
        if diff.get("unlocked", "Difficulty_1") >= target or data.get("xp", 0) >= xp_for(level if level > 1 else 10):
            continue                     # there already, or not a new character
        diff.update({"unlocked": target, "selected": target, "announced": target})
        added = 0
        if data.get("totalGearPower", 0) < power:
            rng = random.Random(f.stem)
            index = max((it.get("inventoryIndex", -1) for it in data.get("items", [])), default=-1) + 1
            for n, item in enumerate(kit):
                new = {"inventoryIndex": index + n, "markedNew": True, "power": 1 + power / 10, "rarity": "Common",
                       "type": item, "upgraded": False}
                if item in GEAR:
                    new["enchantments"] = options(GEAR[item], rng)
                    if GEAR[item] == "armor":
                        new["armorproperties"] = [{"id": names[i], "rarity": "Common"} for i, _ in ARMOR_PERKS.get("Armor/" + item, [])]
                data.setdefault("items", []).append(new)
                added += 1
        raised = level > 1 and data.get("xp", 0) < xp_for(level)
        if raised:
            data["xp"] = xp_for(level)
        f.write_bytes(savefile.encrypt(json.dumps(data, indent=1)))
        json.loads(savefile.decrypt(f.read_bytes()))   # read back
        if not quiet:
            print(f"Start in {start.title()}: {data.get('name') or 'character ' + f.stem[:8]} - {start.title()} unlocked"
                  + (f", starter kit ({added} items at power {power:g})" if added else "")
                  + (f", level {level}" if raised else ""))


if __name__ == "__main__":
    from memprobe import pid_of
    if pid_of():
        sys.exit("Close the game first.")
    apply()
