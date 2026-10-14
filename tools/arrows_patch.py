"""Arrows that come back by themselves while you aren't shooting (Arrows.toml). Data only.

    python tools/arrows_patch.py            # watch the running game until it closes
    python tools/arrows_patch.py --show     # the arrow slots found and their counts

The player's arrows are a number: ItemSlot.Count, an int at +0x1FC of the UArrowItemSlot object (class vtable
exe+0x32F7D60; offsets from the game's reflection data in the exe dump). Every pass (3 s) the launcher looks at it:
    fewer arrows than last time   the player is shooting - nothing happens
    otherwise                     a share of a bundle is added, up to one bundle
A bundle is the equipped bow's own bundle size (ProjectileStackCount in SequelGear.toml; the equipped bow is read
from the character save, re-read when the save changes), or `default_bundle` if that can't be worked out.
The count was read live once (2026-10-12: one slot at 117 in a mission); the refill itself is NOT YET SEEN WORKING.
"""
import json
import math
import struct
import sys
import time
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aplus_patch import open_game, pid_of  # noqa: E402
from builtins_patch import write  # noqa: E402
from live_objects import Scanner  # noqa: E402
from memprobe import read  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "Arrows.toml"
SLOT_VTABLE, FLAGS, COUNT = 0x32F7D60, 0x08, 0x1FC
CLASS_DEFAULT = 0x10          # object flag: the class's default object, not a real slot
PASS_SECONDS = 3


def bundles():
    """{bow id in lower case: bundle size} from SequelGear.toml (a unique without its own number uses its family's)."""
    gear = tomllib.loads((ROOT / "SequelGear.toml").read_text(encoding="utf-8")).get("Ranged", {})
    out = {}
    for name, fields in gear.items():
        for key, value in fields.items():
            if key.endswith(".ProjectileStackCount"):
                out[name.lower()] = int(value)
    return out


def equipped_bundle(sizes, default):
    """Bundle size of the bow the last-played character has equipped."""
    try:
        import savefile
        from bonus_watch import save_folder
        files = sorted(save_folder().glob("*/Characters/*.dat"), key=lambda f: f.stat().st_mtime)
        data = json.loads(savefile.decrypt(files[-1].read_bytes()))
        bow = next(it["type"] for it in data["items"] if it.get("equipmentSlot") == "RangedGear").lower()
        return sizes.get(bow) or sizes.get(bow.split("_")[0]) or default, files[-1].stat().st_mtime
    except Exception:  # noqa: BLE001 - no save, no bow equipped...
        return default, 0.0


class Arrows:
    def __init__(self, h, base, scanner=None):
        self.h, self.base = h, base
        self.own_scanner = scanner is None
        self.scanner = scanner or Scanner(h, base)
        cfg = tomllib.loads(CONFIG.read_text(encoding="utf-8")) if CONFIG.exists() else {}
        self.on = bool(cfg.get("refill", False)) and bool(base)
        self.refill_seconds = max(PASS_SECONDS, float(cfg.get("refill_seconds", 30)))
        self.default = int(cfg.get("default_bundle", 40))
        self.vt = self.scanner.register(SLOT_VTABLE) if self.on else 0
        self.sizes = bundles() if self.on else {}
        self.bundle, self.save_time, self.checked = self.default, 0.0, 0.0
        self.last = {}            # slot object -> arrows at the previous pass
        self.start = {}           # slot object -> arrows when first seen (a mission's starting stock)
        self.used = set()         # slots seen holding arrows: only those are refilled (the game keeps ~30 other
                                  # slots of this kind at 0 - seen live 2026-10-12, one slot at 117 = the player's)
        self.said = False

    def slots(self):
        out = []
        for o in self.scanner.found.get(self.vt, []):
            raw = read(self.h, o, COUNT + 4)
            if raw and not struct.unpack_from("<I", raw, FLAGS)[0] & CLASS_DEFAULT:
                count = struct.unpack_from("<i", raw, COUNT)[0]
                if 0 <= count <= 5000:
                    out.append((o, count))
        return out

    def tick(self, quiet=False):
        if not self.on:
            return
        if self.own_scanner:
            self.scanner.refresh()
        now = time.time()
        if now - self.checked >= 15:                      # which bow is equipped: a look at the save now and then
            self.checked = now
            self.bundle, self.save_time = equipped_bundle(self.sizes, self.default)
        step = max(1, math.ceil(self.bundle * PASS_SECONDS / self.refill_seconds))
        seen = {}
        for o, count in self.slots():
            before = self.last.get(o)
            seen[o] = count
            if count > 0:
                self.used.add(o)
            # The cap: a bundle, or the mission's starting stock where that is a bit more (user, 2026-10-12: a bow
            # whose bundle is 60 in the files started a mission with 80).
            first = self.start.setdefault(o, count)
            cap = first if self.bundle < first <= 2 * self.bundle else self.bundle
            if o not in self.used or before is None or count < before or count >= cap:
                continue                                  # first sight, shooting, or full already
            seen[o] = min(cap, count + step)
            write(self.h, o + COUNT, struct.pack("<i", seen[o]))
            if not quiet and not self.said:
                self.said = True
                print(f"Arrows: refilling {step} every {PASS_SECONDS} s while not shooting, up to a bundle of {self.bundle}")
        self.last = seen
        self.start = {o: c for o, c in self.start.items() if o in seen}


if __name__ == "__main__":
    h, base = open_game()
    if not h:
        sys.exit("Minecraft Dungeons isn't running")
    w = Arrows(h, base)
    if "--show" in sys.argv:
        w.vt = w.vt or w.scanner.register(SLOT_VTABLE)
        w.scanner.refresh()
        print("arrow slots (object, arrows):", [(hex(o), c) for o, c in w.slots()], "bundle", equipped_bundle(bundles(), 40)[0])
        sys.exit()
    while pid_of():
        w.tick()
        time.sleep(PASS_SECONDS)
