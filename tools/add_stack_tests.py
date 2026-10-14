"""Dev tool: add a few items for trying out copies of one enchantment on the same item.

    python tools/add_stack_tests.py [--wait]     # --wait: wait for the game to close first

Every item offers the SAME three enchantments in each of its three slots, nothing chosen yet - so one, two or
three copies of an enchantment can be picked in game, at any tiers, with the player's own enchantment points.
Power 251: below the gear cap, so no bonus built-ins get in the way.
Run it with the game open first (it reads the armors' perk lists from the game - a save stores perks per item),
then it writes the save once the game is closed. The save is backed up to save_backups/ first.
"""
import json
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import perks_patch  # noqa: E402
import savefile  # noqa: E402
from aplus_patch import open_game, pid_of  # noqa: E402
from bonus_watch import save_folder  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PERKS_CACHE = ROOT / "research" / "stack_test_perks.json"
POWER = 1 + 251 / 10          # stored power: shown power = (stored - 1) * 10
ROOM = 300                    # inventory slots
# (item, rarity, the three enchantments every slot offers). The batch before this one (2026-10-13, tested by the
# user): Critical Hit, Thundering, Fire Aspect, Shockwave, Swirling, Bonus Shot, Burning, Electrified stack;
# Poison Cloud, Exploding and Echo show several procs but no extra damage.
ITEMS = [
    # batch 3 (2026-10-14): the ones a build would double up on, plus three expected not to add (Cowardice, Rush,
    # Final Shout) to check the rule "own hits and flat amounts add, a named buff or debuff doesn't"
    ("Mace", "Common", ["Looting", "Prospector", "PotionThirstMelee"]),
    ("Bow", "Common", ["RadianceRanged", "CooldownShot", "ShockWeb"]),
    ("ScaleMail", "Common", ["FireFocus", "LightningFocus", "PoisonFocus"]),
    ("EvocationRobe", "Common", ["SoulFocus", "BagOfSouls", "SpiritSpeed"]),
    ("ScaleMail", "Common", ["Reckless", "Frenzied", "FireTrail"]),
    ("EvocationRobe", "Common", ["Cowardice", "Flee", "FinalShout"]),
]
EXTRA = [   # --add: put these in without taking the current batch out (2026-10-14: Unchanting, user)
    ("Sword", "Common", ["Unchanting", "BaneOfIllagers", "Smiting"]),
]
STACK_TYPES = {"Sword", "Daggers", "Axe", "Glaive", "SoulScythe", "Katana", "Cutlass", "Mace", "Bow", "Crossbow",
               "Shortbow", "Longbow", "SoulBow", "HeavyCrossbow", "ScaleMail", "EvocationRobe"}   # every batch so far
ARMORS = ("ScaleMail", "EvocationRobe")


def read_perks():
    h, base = open_game()
    if not h:
        return False
    out = {}
    for item in ARMORS:
        got = perks_patch.perks(h, base, "Armor/" + item)
        out[item] = [{"id": perks_patch.NAMES[i], "rarity": "Unique" if flag == 2 else "Common"} for i, flag in got[1]]
    PERKS_CACHE.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("armor perks read from the game:", {k: [p["id"] for p in v] for k, v in out.items()})
    return True


def main():
    if pid_of():
        read_perks()
        if "--wait" not in sys.argv:
            sys.exit("Close the game, then run this again to write the save.")
        print("waiting for the game to close...", flush=True)
        while pid_of():
            time.sleep(2)
        time.sleep(10)   # let the game finish writing its own save
    perks = json.loads(PERKS_CACHE.read_text(encoding="utf-8"))
    save = sorted(save_folder().glob("*/Characters/*.dat"), key=lambda f: f.stat().st_mtime)[-1]
    data = json.loads(savefile.decrypt(save.read_bytes()))
    # Earlier stack-test items go (their enchantment points come back with them): a plain item of a type these
    # batches use, at exactly power 251. (Not recognised by its offered enchantments: the user rerolls them at the
    # Enchantsmith.) One that is equipped stays.
    def test_item(it):
        return abs(it.get("power", 0) - POWER) < 1e-4 and it.get("rarity") == "Common"             and it.get("type") in STACK_TYPES and not it.get("equipmentSlot")
    before = len(data["items"])
    if "--add" in sys.argv:
        ITEMS[:] = EXTRA
    else:
        data["items"] = [it for it in data["items"] if not test_item(it)]
    print(f"removed {before - len(data['items'])} earlier stack-test items")
    if len(data["items"]) + len(ITEMS) > ROOM:
        sys.exit(f"no room: {len(data['items'])} items in the inventory, {len(ITEMS)} to add, {ROOM} slots")
    backup = ROOT / "save_backups" / f"character_before_stack_tests_{datetime.now():%Y-%m-%d_%H%M%S}.dat"
    backup.parent.mkdir(exist_ok=True)
    shutil.copyfile(save, backup)
    index = max((it.get("inventoryIndex", -1) for it in data["items"]), default=-1) + 1
    for n, (item, rarity, offered) in enumerate(ITEMS):
        new = {"enchantments": [{"id": e, "investedPoints": 0, "level": 0} for _ in range(3) for e in offered],
               "inventoryIndex": index + n, "markedNew": True, "power": POWER, "rarity": rarity, "type": item,
               "upgraded": False}
        if item in ARMORS:
            new["armorproperties"] = perks[item]
        data["items"].append(new)
    save.write_bytes(savefile.encrypt(json.dumps(data, indent=1)))
    check = json.loads(savefile.decrypt(save.read_bytes()))
    assert len(check["items"]) == len(data["items"])
    print(f"added {len(ITEMS)} items at power 251 to {save.name} (inventory now {len(check['items'])} of {ROOM}); backup: {backup.name}")


if __name__ == "__main__":
    main()
