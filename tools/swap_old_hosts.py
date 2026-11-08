"""One-off (2026-11-08): items in the save still carrying Shatter's and Shadowcloak's old hosts get the new ones.

    python tools/swap_old_hosts.py      # waits for the game to close, backs up the save, then swaps

Charging Acceleration (old Shatter) -> Thrive Under Pressure; Sponge Strike (old Shadowcloak) -> Rushdown. A swapped
enchantment is reset to not chosen with its points refunded, so it is picked again at its new cost (Shatter is
Powerful now).
"""
import json, shutil, sys, time
from datetime import datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import savefile  # noqa: E402
from aplus_patch import pid_of  # noqa: E402
from bonus_watch import save_folder  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SWAP = {"ChargingAcceleration": "ThriveUnderPressure", "SpongeStrike": "Rushdown"}

if pid_of():
    print("waiting for the game to close...", flush=True)
    while pid_of():
        time.sleep(2)
    time.sleep(10)
for save in save_folder().glob("*/Characters/*.dat"):
    data = json.loads(savefile.decrypt(save.read_bytes()))
    changed = []
    for it in data.get("items", []):
        for e in it.get("enchantments") or []:
            if e.get("id") in SWAP:
                changed.append(f"{it.get('type')}: {e['id']} -> {SWAP[e['id']]} (was level {e.get('level', 0)})")
                e["id"] = SWAP[e["id"]]
                e["level"] = 0
                e["investedPoints"] = 0
    if not changed:
        continue
    backup = ROOT / "save_backups" / f"character_before_host_swap_{datetime.now():%Y-%m-%d_%H%M%S}.dat"
    backup.parent.mkdir(exist_ok=True)
    shutil.copyfile(save, backup)
    save.write_bytes(savefile.encrypt(json.dumps(data, indent=1)))
    assert json.loads(savefile.decrypt(save.read_bytes()))["items"] == data["items"]
    print(save.name, "backup:", backup.name)
    print("  " + "\n  ".join(changed))
