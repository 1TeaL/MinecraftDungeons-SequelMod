"""Dev tool: add the mod's changed items to a character save so they can be tried in game.

    python tools/add_test_items.py [--wait]     # --wait: wait for the game to close first

Run it once with the game open (it reads each armor's perk list from the game into
research/test_item_perks.json - saves store perks per item), then with the game closed to write the save.
The save is backed up to save_backups/ first.
"""
import json
import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import perks_patch  # noqa: E402
import savefile  # noqa: E402
from aplus_patch import open_game, pid_of  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SAVE = Path(os.environ["USERPROFILE"]) / "Saved Games/Mojang Studios/Dungeons/2535416308206199/Characters/4CF2A97A494A5A2B972671BC27F5A1DC.dat"
PERKS_CACHE = ROOT / "research" / "test_item_perks.json"
POWER = 1 + 251 / 10          # stored power: shown power = (stored - 1) * 10

ARMORS = ["NatureArmor_Unique1", "WolfArmor_Unique2", "SpelunkersArmor_Unique1", "EmeraldArmor_Unique2",
          "PhantomArmor_Unique1", "PiglinArmor_Unique1", "TurtleArmor_Unique1", "ClimbingGear_Unique2",
          "EvocationRobe_Unique1", "SnowArmor_Unique1"]
MELEE = ["Axe_Unique1", "Axe_Unique2", "Gauntlets_Unique2", "Gauntlets_Unique1", "CoralBlade_Unique1",
         "Daggers_Unique1", "Daggers_Unique3", "Sickles_Unique1", "Sickles_Unique2", "Sword_Unique1",
         "Hammer_Unique1", "TempestKnife_Unique2", "SoulKnife_Unique2", "Cutlass_Unique2", "Whip_Unique1"]
# Enchantments the mod changed, by the gear they go on. Each item gets nine of them as its options.
MELEE_ENCHANTS = ["FireAspect", "Thundering", "Shockwave", "RadianceMelee", "PainCycle", "Stunning", "Freezing",
                  "PoisonedMelee", "Rampaging", "CriticalHit", "Smiting", "Chains", "BusyBee", "Backstabber",
                  "BaneOfIllagers", "DamageSynergy"]
ARMOR_ENCHANTS = ["BagOfSouls", "BeastBoss", "BeastSurge", "Burning", "Cowardice", "Electrified", "Explorer",
                  "FinalShout", "FireFocus", "FireTrail", "Frenzied", "LightningFocus", "LuckOfTheSea",
                  "PoisonFocus", "Reckless", "ShadowFlash", "Snowing", "SpeedSynergy", "SpiritSpeed", "Thorns"]


def read_perks():
    h, base = open_game()
    if not h:
        return False
    out = {}
    for item in ARMORS:
        got = perks_patch.perks(h, base, "Armor/" + item)
        out[item] = [{"id": perks_patch.NAMES[i], "rarity": "Unique" if flag == 2 else "Common"} for i, flag in got[1]]
    PERKS_CACHE.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"armor perks read from the game for {len(out)} armors")
    return True


def options(pool, n):
    """Nine enchantment options starting at a different point of the pool for each item."""
    start = (n * 5) % len(pool)
    return [{"id": pool[(start + k) % len(pool)], "investedPoints": 0, "level": 0} for k in range(9)]


def main():
    if pid_of():
        read_perks()
        if "--wait" not in sys.argv:
            sys.exit("Close the game, then run this again to write the save.")
        print("waiting for the game to close...")
        while pid_of():
            time.sleep(2)
        time.sleep(8)   # let the game finish writing its own save
    perks = json.loads(PERKS_CACHE.read_text(encoding="utf-8"))
    backup = ROOT / "save_backups" / f"character_before_test_items_{datetime.now():%Y-%m-%d_%H%M%S}.dat"
    backup.parent.mkdir(exist_ok=True)
    shutil.copyfile(SAVE, backup)
    data = json.loads(savefile.decrypt(SAVE.read_bytes()))
    index = max((it.get("inventoryIndex", -1) for it in data["items"]), default=-1) + 1
    added = []
    for n, item in enumerate(MELEE + ARMORS):
        armor = item in ARMORS
        new = {"enchantments": options(ARMOR_ENCHANTS if armor else MELEE_ENCHANTS, n), "inventoryIndex": index + n,
               "markedNew": True, "power": POWER, "rarity": "Unique", "type": item, "upgraded": False}
        if armor:
            new["armorproperties"] = perks[item]
        data["items"].append(new)
        added.append(item)
    text = json.dumps(data, indent=1)
    SAVE.write_bytes(savefile.encrypt(text))
    check = json.loads(savefile.decrypt(SAVE.read_bytes()))
    assert len(check["items"]) == len(data["items"])
    print(f"added {len(added)} items at power 251 (inventory now {len(check['items'])}); backup: {backup.name}")


if __name__ == "__main__":
    main()
