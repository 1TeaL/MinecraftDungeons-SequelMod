"""Read-only: while the drop test runs, log how many live objects of each drop-related kind the game holds.

    python research/drop_watch_live.py      # waits for the game, runs until it closes; log in research/drop_watch.log

Every half second it counts the live objects of each kind below (found by their class vtable, tools/live_objects.py)
and writes a line whenever a count changes, so a press of O / P that makes an item shows as new objects - or not.
Vtables from research/artifact_fields.py class_info (exe dump); the inventory item one from research/inv_live.py.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from aplus_patch import open_game  # noqa: E402
from live_objects import Scanner  # noqa: E402
from memprobe import pid_of  # noqa: E402

KINDS = {
    "item dropper (ItemDropActor)": 0x3226808,
    "item emitter (ItemEmitterActor)": 0x3221870,
    "walk-over pickup (WalkPickupComponent)": 0x3293FC0,
    "item actor (ItemActor)": 0x321B780,
    "loot actor (LootActor)": 0x31F9DC0,
    "item instance (ItemInstance)": 0x32F6F60,
    "gear item instance (GearItemInstance)": 0x32F7660,
    "drop component (ItemDropComponent)": 0x3271568,
    "inventory item (item data object)": 0x346FCF8,
}
LOG = Path(__file__).with_name("drop_watch.log")


def say(line, out):
    stamp = time.strftime("%H:%M:%S")
    print(stamp, line, flush=True)
    out.write(f"{stamp} {line}\n")
    out.flush()


def main():
    while not pid_of():
        time.sleep(2)
    time.sleep(5)
    h, base = open_game()
    if not h:
        sys.exit("could not open the game")
    scanner = Scanner(h, base, wait=False)
    for vt in KINDS.values():
        scanner.register(vt)
    last = {}
    with open(LOG, "w") as out:
        say("watching (read only)", out)
        while pid_of():
            found = scanner.refresh()
            for name, vt in KINDS.items():
                n = len(found.get(base + vt, []))
                if n != last.get(name):
                    say(f"{name}: {last.get(name, '-')} -> {n}", out)
                    last[name] = n
            time.sleep(0.5)
        say("game closed", out)


if __name__ == "__main__":
    main()
