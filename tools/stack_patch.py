"""Mark enchantments as stackable in the running game (Stack.toml). Data only: no game code is changed.

    python tools/stack_patch.py            # apply Stack.toml
    python tools/stack_patch.py --show     # list every enchantment the game marks as stackable
    python tools/stack_patch.py Swirling   # mark just these (for a test)

Each enchantment has a definition (a global, tools/enchant_registry.json). At +8 it holds a list of one-byte
tags (TArray: data, count, room). Tag 0 is on exactly the enchantments that stack in game - Sharpness, Smiting,
Looting, Prospector, Chains, Fire Aspect, Leeching, Rampaging, Radiance (melee), Cool Down, Thorns - and on none
of the others. This adds tag 0 to more of them. The tag only decides whether the game may ROLL the enchantment in
more than one slot of an item; copies of an enchantment all fire anyway (tested in play 2026-10-05).
"""
import json
import struct
import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aplus_patch import open_game  # noqa: E402
from builtins_patch import alloc, write  # noqa: E402
from memprobe import read  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "Stack.toml"
REGISTRY = json.loads((ROOT / "tools" / "enchant_registry.json").read_text())
TAGS, STACKABLE, ROOM = 0x08, 0, 16


def tags(h, base, name):
    """(definition address, [tags]) or (None, None)."""
    raw = read(h, base + int(REGISTRY[name], 16), 8) if name in REGISTRY else None
    definition = struct.unpack("<Q", raw)[0] if raw else 0
    head = read(h, definition + TAGS, 16) if definition else None
    if not head:
        return None, None
    data, count, room = struct.unpack("<QII", head)
    if count == 0:
        return definition, []
    raw = read(h, data, count) if data and count <= room <= 64 else None
    return (definition, list(raw)) if raw else (None, None)


def player_enchant(h, base, name):
    """True for enchantments that go on gear (first byte of the definition: 1 melee, 2 ranged, 8 armor)."""
    raw = read(h, base + int(REGISTRY[name], 16), 8)
    head = read(h, struct.unpack("<Q", raw)[0], 1) if raw and raw != bytes(8) else None
    return bool(head and head[0] & 0x0B and not head[0] & 0x40)


def apply(h, base, names=None):
    if names is None:
        cfg = tomllib.loads(CONFIG.read_text(encoding="utf-8")) if CONFIG.exists() else {}
        names = cfg.get("stackable", [])
        if names == "all":
            names = [n for n in sorted(REGISTRY) if n not in cfg.get("except", []) and player_enchant(h, base, n)]
    changed = 0
    for name in names:
        definition, cur = tags(h, base, name)
        if cur is None:
            print(f"  ! {name}: not found in the game - skipped")
            continue
        if STACKABLE in cur or len(cur) >= ROOM:
            continue
        at = alloc(h, ROOM)
        if not at:
            print(f"  ! {name}: no memory - skipped")
            continue
        new = cur + [STACKABLE]
        write(h, at, bytes(new))
        write(h, definition + TAGS, struct.pack("<QII", at, len(new), ROOM))
        changed += 1
    print(f"stacking: {changed} more enchantments can now be rolled in several slots")


if __name__ == "__main__":
    h, base = open_game()
    if not h:
        sys.exit("Minecraft Dungeons isn't running")
    if "--show" in sys.argv:
        for name in sorted(REGISTRY):
            _, cur = tags(h, base, name)
            if cur and STACKABLE in cur:
                print(name)
    else:
        apply(h, base, sys.argv[1:] or None)
