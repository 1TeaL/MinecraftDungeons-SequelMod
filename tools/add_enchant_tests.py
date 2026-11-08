"""Dev tool: add test gear with the new and reworked enchantments already at tier III, so they can be tried at once.

    python tools/add_enchant_tests.py [--wait]     # --wait: wait for the game to close first

Each item's first slots hold one test enchantment each, already at tier III (no enchantment points spent, so none
come back when it is salvaged); a slot marked None is left open with ordinary choices. Power 251: below the gear
cap, so no bonus built-ins get in the way. Plain released items only (no unreleased items in saves - user rule).
Armor perks come from research/stack_test_perks.json (read from the game by add_stack_tests.py).
The save of the character played last is backed up to save_backups/ first. The game must be closed.
"""
import json
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import savefile  # noqa: E402
from aplus_patch import pid_of  # noqa: E402
from bonus_watch import save_folder  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PERKS = json.loads((ROOT / "research" / "stack_test_perks.json").read_text(encoding="utf-8"))
POWER = 1 + 251 / 10          # stored power: shown power = (stored - 1) * 10
ROOM = 300
# (item, [three slots: the enchantment chosen at tier III, or None = open], the open slot's choices)
ITEMS = [
    # the debuffer enchantments, each next to its status source (2026-11-07)
    ("Sword", ["FireAspect", "EmeraldDivination", "Knockback"], []),
    #          Fire Aspect, Ignite, Sweeping Edge
    ("Axe", ["PoisonedMelee", "Altruistic", None], ["Leeching", "Sharpness", "Committed"]),
    #        Poison Cloud, Venom Siphon
    ("Claymore", ["Freezing", "ChargingAcceleration", None], ["Sharpness", "Committed", "CriticalHit"]),
    #             Freezing, Shatter
    ("ScaleMail", ["Burning", "Chilling", "EmeraldDivination"], []),
    #              Burning aura, Chilling aura, Ignite
]


def slots(chosen, open_choices):
    out = []
    for pick in chosen:
        if pick:
            out += [{"id": pick, "investedPoints": 0, "level": 3},
                    {"id": "Unset", "investedPoints": 0, "level": 0}, {"id": "Unset", "investedPoints": 0, "level": 0}]
        else:
            out += [{"id": e, "investedPoints": 0, "level": 0} for e in open_choices]
    return out


def main():
    if pid_of():
        if "--wait" not in sys.argv:
            sys.exit("Close the game first (or run with --wait).")
        print("waiting for the game to close...", flush=True)
        while pid_of():
            time.sleep(2)
        time.sleep(10)   # let the game finish writing its own save
    save = sorted(save_folder().glob("*/Characters/*.dat"), key=lambda f: f.stat().st_mtime)[-1]
    data = json.loads(savefile.decrypt(save.read_bytes()))
    if len(data["items"]) + len(ITEMS) > ROOM:
        sys.exit(f"no room: {len(data['items'])} items in the inventory, {len(ITEMS)} to add, {ROOM} slots")
    backup = ROOT / "save_backups" / f"character_before_enchant_tests_{datetime.now():%Y-%m-%d_%H%M%S}.dat"
    backup.parent.mkdir(exist_ok=True)
    shutil.copyfile(save, backup)
    index = max((it.get("inventoryIndex", -1) for it in data["items"]), default=-1) + 1
    for n, (item, chosen, open_choices) in enumerate(ITEMS):
        new = {"enchantments": slots(chosen, open_choices), "inventoryIndex": index + n, "markedNew": True,
               "power": POWER, "rarity": "Common", "type": item, "upgraded": False}
        if item in PERKS:
            new["armorproperties"] = PERKS[item]
        data["items"].append(new)
    save.write_bytes(savefile.encrypt(json.dumps(data, indent=1)))
    check = json.loads(savefile.decrypt(save.read_bytes()))
    assert len(check["items"]) == len(data["items"])
    print(f"added {len(ITEMS)} test items at power 251 to {save.name} (inventory now {len(check['items'])} of {ROOM}); "
          f"backup: {backup.name}")


if __name__ == "__main__":
    main()
