"""Quality-of-life changes to the running game (QoL.toml). Data only: no game code is changed.

    python tools/qol_patch.py

Blacksmith: its definition (BlacksmithMerchantDef, built by code at startup, exe+0xBB96B0) owns three
upgrade quests, UpgradeQuest1-3, one per upgrade slot. A quest object holds its owner at +0x28 and the
number of missions to complete at +0x30 (3). [blacksmith] missions sets that number.
The Blacksmith's own description keeps saying 3: that text is fixed in code.
"""
import struct
import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aplus_patch import open_game  # noqa: E402
from endless_patch import find_pointers, poke  # noqa: E402
from memprobe import main_module, read  # noqa: E402

CONFIG = Path(__file__).resolve().parent.parent / "QoL.toml"
QUEST_CLASS = 0x4548B40       # global: the quest class (set once the class is registered)
CLASS, OWNER, MISSIONS = 0x10, 0x28, 0x30
VANILLA_MISSIONS = 3


def blacksmith(h, base, missions):
    if not (isinstance(missions, int) and 0 <= missions <= VANILLA_MISSIONS):
        sys.exit("QoL.toml [blacksmith]: missions must be 0-3")
    size = main_module(h)[1]
    cls = struct.unpack("<Q", read(h, base + QUEST_CLASS, 8) or bytes(8))[0]
    if not cls:
        sys.exit("Blacksmith: the game hasn't set up its quests yet - not changed")
    quests = {}   # owner -> [(object, missions)]
    for at in find_pointers(h, [cls])[cls]:
        raw = read(h, at - CLASS, MISSIONS + 4)
        if raw and base <= struct.unpack_from("<Q", raw)[0] < base + size:   # an object: starts with a vtable
            owner, count = struct.unpack_from("<Q", raw, OWNER)[0], struct.unpack_from("<i", raw, MISSIONS)[0]
            quests.setdefault(owner, []).append((at - CLASS, count))
    # The Blacksmith is the owner with three quests that all ask for the same number of missions.
    mine = [q for owner, q in quests.items() if owner and len(q) == 3 and len({c for _, c in q}) == 1
            and 0 <= q[0][1] <= VANILLA_MISSIONS]
    if len(mine) != 1:
        sys.exit("Blacksmith: couldn't identify its three upgrade quests - not changed")
    was = mine[0][0][1]
    for obj, _ in mine[0]:
        poke(h, obj + MISSIONS, struct.pack("<i", missions))
    print(f"Blacksmith: upgrades take {missions} mission{'s' if missions != 1 else ''}"
          + ("" if was == missions else f" (was {was})"))


class Blacksmith:
    """Launcher watcher. The three quests found at startup are not the ones a hand-in uses: an item handed in
    after the startup change still asked for 3 missions (user, 2026-10-13; the save showed target = start + 3).
    The game makes further quest objects later, so every upgrade quest (class DynamicProgressStatQuest, vtable
    exe+0x3445DE0) is set as it turns up. Starting a quest reads this number: exe+0xB937F0, target = count so
    far + [quest + 0x30]."""
    VTABLE = 0x3445DE0

    def __init__(self, h, base, scanner):
        cfg = tomllib.loads(CONFIG.read_text(encoding="utf-8")) if CONFIG.exists() else {}
        self.missions = cfg.get("blacksmith", {}).get("missions")
        self.h, self.scanner, self.changed = h, scanner, 0
        self.on = isinstance(self.missions, int) and 0 <= self.missions < VANILLA_MISSIONS and bool(base)
        self.vt = scanner.register(self.VTABLE) if self.on else 0

    def tick(self):
        if not self.on:
            return
        for o in self.scanner.found.get(self.vt, []):
            raw = read(self.h, o + MISSIONS, 4)
            if raw and struct.unpack("<i", raw)[0] == VANILLA_MISSIONS:
                poke(self.h, o + MISSIONS, struct.pack("<i", self.missions))
                self.changed += 1
                if self.changed in (1, 4):
                    print(f"Blacksmith: upgrade quest set to {self.missions} mission{'s' if self.missions != 1 else ''}"
                          + (" (a quest made after startup)" if self.changed == 4 else ""))


def apply(h, base):
    cfg = tomllib.loads(CONFIG.read_text(encoding="utf-8")) if CONFIG.exists() else {}
    missions = cfg.get("blacksmith", {}).get("missions")
    if missions is not None:
        blacksmith(h, base, missions)


if __name__ == "__main__":
    h, base = open_game()
    if not h:
        sys.exit("Minecraft Dungeons isn't running")
    apply(h, base)
