"""Change unique items' built-in enchantments in the running game (memory only; gone when the game closes).

    python tools/builtins_patch.py            # apply Builtins.toml
    python tools/builtins_patch.py --show     # list every item's current built-ins

How it works: each item is registered at startup by its own function, which stores the finished item
definition in a global (tools/item_registry.json, found by research/item_globals.py). The definition keeps its
built-in enchantments at +0x1B8 as a TArray of 20-byte entries: FEnchantmentData {TypeID u8, Level i32 @+4, ...}
plus 4 extra bytes. Built-ins aren't saved with items, so the game reads them from here.
Data only - no code is changed. Every entry is checked before it's written.

Extra built-ins: `add = { Enchantment = level, ... }` gives an item more built-in enchantments than the game
does (the game itself has items with two or three). The list has no spare room, so the item's list is
rebuilt in memory this tool allocates in the game and the definition is pointed at it.
"""
import ctypes
import json
import struct
import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from memprobe import read  # noqa: E402
from mempatch import k32  # noqa: E402

TOOLS = Path(__file__).resolve().parent
CONFIG = TOOLS.parent / "Builtins.toml"
REGISTRY = json.loads((TOOLS / "item_registry.json").read_text())
IDS = json.loads((TOOLS / "enchant_ids.json").read_text())
NAMES = {v: k for k, v in IDS.items()}
ARRAY, STRIDE = 0x1B8, 0x14
TEMPLATE_ITEM = "MeleeWeapons/Axe_Unique1"   # a built-in entry to copy the bookkeeping bytes from
k32.VirtualAllocEx.restype = ctypes.c_void_p
k32.VirtualAllocEx.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint32, ctypes.c_uint32]
_pool = {"at": 0, "left": 0}


def alloc(h, size):
    """Memory inside the game for a rebuilt list (read/write data, never freed while the game runs)."""
    size = (size + 15) & ~15
    if _pool["left"] < size:
        _pool["at"] = k32.VirtualAllocEx(h, None, 0x10000, 0x3000, 0x04)
        _pool["left"] = 0x10000 if _pool["at"] else 0
    if not _pool["at"]:
        return 0
    at = _pool["at"]
    _pool["at"] += size
    _pool["left"] -= size
    return at


def add_builtins(h, base, item, wanted):
    """Append built-ins the item doesn't have yet. Returns how many were added."""
    data, current = builtins(h, base, item)
    new = [(IDS[n], lv) for n, lv in wanted.items() if IDS[n] not in [t for t, _ in current]]
    if not new:
        print(f"  {item}: already has {', '.join(wanted)}")
        return 0
    tdata, tcur = builtins(h, base, TEMPLATE_ITEM)
    template = read(h, tdata, STRIDE) if tcur else None
    old = read(h, data, STRIDE * len(current)) if current else b""
    if template is None or old is None or len(current) + len(new) > 8:
        print(f"  ! {item}: can't extend its built-ins - skipped")
        return 0
    entries = bytearray(old)
    for type_id, level in new:
        e = bytearray(template)
        e[0] = type_id
        struct.pack_into("<i", e, 4, level)
        entries += e
    count = len(current) + len(new)
    at = alloc(h, len(entries))
    if not at:
        print(f"  ! {item}: no memory - skipped")
        return 0
    definition = struct.unpack("<Q", read(h, base + int(REGISTRY[item], 16), 8))[0]
    write(h, at, bytes(entries))
    write(h, definition + ARRAY, struct.pack("<QII", at, count, count))
    _, check = builtins(h, base, item)
    ok = check is not None and len(check) == count
    print(f"  {item}: added " + ", ".join(f"{NAMES[t]} {lv}" for t, lv in new) + ("" if ok else "  ! VERIFY FAILED"))
    return len(new) if ok else 0


def builtins(h, base, item):
    """(entries address, [(type_id, level)]) of an item's built-in enchantments, or (None, None)."""
    raw = read(h, base + int(REGISTRY[item], 16), 8)
    if not raw:
        return None, None
    definition = struct.unpack("<Q", raw)[0]
    head = read(h, definition + ARRAY, 16) if definition else None
    if not head:
        return None, None
    data, count, cap = struct.unpack("<QII", head)
    if not (0 <= count <= 16 and count <= cap <= 64):   # 16: the A+100 ladder (bonus_watch.MAX_ENTRIES)
        return None, None
    entries = read(h, data, STRIDE * count) if count else b""
    if entries is None:
        return None, None
    return data, [(entries[i * STRIDE], struct.unpack_from("<i", entries, i * STRIDE + 4)[0]) for i in range(count)]


def write(h, addr, data):
    k32.WriteProcessMemory(h, ctypes.c_void_p(addr), data, len(data), None)


def apply(h, base, config=CONFIG):
    plan = tomllib.loads(config.read_text(encoding="utf-8")) if config.exists() else {}
    changed = 0
    for item, changes in plan.items():
        if item not in REGISTRY:
            print(f"  ! {item}: unknown item - skipped")
            continue
        data, current = builtins(h, base, item)
        if current is None:
            print(f"  ! {item}: definition not readable - skipped")
            continue
        extra = changes.get("add", {})
        for name, spec in changes.items():
            if name == "add":
                continue
            to, level = (spec.get("to", name), spec.get("level")) if isinstance(spec, dict) else (name, spec)
            if name not in IDS or to not in IDS or not isinstance(level, int) or not 1 <= level <= 3:
                print(f"  ! {item}: bad entry {name} = {spec!r} - skipped")
                continue
            src, dst = IDS[name], IDS[to]
            slot = next((i for i, (t, _) in enumerate(current) if t == src), None)
            if slot is None:
                done = next((i for i, (t, lv) in enumerate(current) if t == dst and lv == level), None)
                print(f"  {item}: {to} {level} " + ("already set" if done is not None
                                                     else f"- ! no {name} built in ({[NAMES.get(t, t) for t, _ in current]})"))
                continue
            if src == dst and current[slot][1] == level:
                print(f"  {item}: {to} {level} already set")
                continue
            entry = data + slot * STRIDE
            write(h, entry, bytes([dst]))
            write(h, entry + 4, struct.pack("<i", level))
            check = read(h, entry, 8)
            ok = check[0] == dst and struct.unpack_from("<i", check, 4)[0] == level
            print(f"  {item}: {name} {current[slot][1]} -> {to} {level}" + ("" if ok else "  ! VERIFY FAILED"))
            changed += ok
        if extra:
            if all(n in IDS and isinstance(lv, int) and 1 <= lv <= 3 for n, lv in extra.items()):
                changed += add_builtins(h, base, item, extra)
            else:
                print(f"  ! {item}: bad add = {extra!r} - skipped")
    print(f"built-in enchantments: {changed} changed")


if __name__ == "__main__":
    import aplus_patch
    h, base = aplus_patch.open_game()
    if not h:
        sys.exit("Minecraft Dungeons isn't running")
    if "--show" in sys.argv:
        for item in sorted(REGISTRY):
            _, cur = builtins(h, base, item)
            if cur:
                print(item, ", ".join(f"{NAMES.get(t, t)} {lv}" for t, lv in cur))
    else:
        apply(h, base)
