"""One-off (2026-11-09): Last Stand and Buddy Brew swapped hosts (Last Stand: Regeneration -> Shielding, Buddy Brew:
Shielding -> Regeneration; user: the icons fit better). Items in the saves swap the two ids so every item keeps the
enchantment it had, level and points included (Last Stand stays Powerful on its new host).

    python tools/swap_stand_buddy.py      # waits for the game to close, backs up each save, then swaps
"""
import json, shutil, sys, time
from datetime import datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import savefile  # noqa: E402
from aplus_patch import pid_of  # noqa: E402
from bonus_watch import save_folder  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SWAP = {"Regeneration": "Shielding", "Shielding": "Regeneration"}


def walk(node, changed):
    """Every item anywhere in the save (inventory, storage...): anything with an enchantments list."""
    if isinstance(node, dict):
        for e in node.get("enchantments") or []:
            if isinstance(e, dict) and e.get("id") in SWAP:
                changed.append(f"{node.get('type')}: {e['id']} -> {SWAP[e['id']]} (level {e.get('level', 0)})")
                e["id"] = SWAP[e["id"]]
        for v in node.values():
            walk(v, changed)
    elif isinstance(node, list):
        for v in node:
            walk(v, changed)


DONE = ROOT / "save_backups" / "stand_buddy_swap.done"   # a second run would swap them back
if DONE.exists():
    sys.exit("already swapped (" + DONE.read_text().strip() + ") - delete " + DONE.name + " to run it again")
if pid_of():
    print("waiting for the game to close...", flush=True)
    while pid_of():
        time.sleep(2)
    time.sleep(10)
for save in save_folder().glob("*/Characters/*.dat"):
    data = json.loads(savefile.decrypt(save.read_bytes()))
    changed = []
    walk(data, changed)
    if not changed:
        print(save.name, "- nothing to swap")
        continue
    backup = ROOT / "save_backups" / f"character_before_stand_buddy_swap_{datetime.now():%Y-%m-%d_%H%M%S}_{save.stem}.dat"
    backup.parent.mkdir(exist_ok=True)
    shutil.copyfile(save, backup)
    save.write_bytes(savefile.encrypt(json.dumps(data, indent=1)))
    assert json.loads(savefile.decrypt(save.read_bytes())) == data
    print(save.name, "backup:", backup.name)
    print("  " + "\n  ".join(changed))
DONE.parent.mkdir(exist_ok=True)
DONE.write_text(f"{datetime.now():%Y-%m-%d %H:%M:%S}\n")
