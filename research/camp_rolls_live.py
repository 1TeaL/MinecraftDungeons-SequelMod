"""Test: more rarity rolls for drops in camp (the item reroll) - the live loot quality number, set by the launcher.

    python research/camp_rolls_live.py [rolls]     # rolls = loot quality to set (default 4); log in camp_rolls.log

A drop's rarity is rolled LootQualityBoost + 1 times, keeping the first result that isn't common ("Reroll for rares
N times", exe+0xB53AA0). The value is the 3rd float of the live FEndlessStruggleConfiguration that the drop code
finds like this (exe+0xB09F60 -> exe+0xC28910): a per-world list at exe+0x421D770 (a TMap of weak world pointer ->
TArray of objects, 32-byte elements) -> its first object -> [+0x488] -> config at +0x248.

Every second this walks every element of that map the same way, logs the config whenever it changes and writes the
test value over LootQualityBoost. Camp already has one: about 6 (seen 2026-11-03 - XP 2.0, loot power 1.05, loot
quality 6.0; likely the difficulty picked at the mission table). The tool can't tell camp from a mission, so stay in
camp while it runs. Waits for the game and stops when it closes. Writes nothing else.
"""
import ctypes
import ctypes.wintypes as wt
import struct
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from aplus_patch import k32, open_game, unpacked  # noqa: E402
from memprobe import alive, main_module, pid_of, read  # noqa: E402

REGISTRY = 0x421D770        # TMap<TWeakObjectPtr<UWorld>, TArray<object*>> the drop code looks the world up in
HOLDER = 0x488              # first object -> the object holding the config
CONFIG = 0x248              # FEndlessStruggleConfiguration in that object
FIELDS = ["XPMultiplier", "LootPowerMultiplier", "LootQualityBoost", "ShopPriceMultiplier", "MobCountMultiplier"]
LOOT_QUALITY = 8            # offset of LootQualityBoost in the config
LOG = Path(__file__).with_name("camp_rolls.log")

k32.WriteProcessMemory.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t,
                                   ctypes.POINTER(ctypes.c_size_t)]


def q(h, addr):
    raw = read(h, addr, 8)
    return struct.unpack("<Q", raw)[0] if raw and len(raw) == 8 else 0


def in_exe(value, base, size):
    return base <= value < base + size


def configs(h, base, size):
    """[(config address, (5 floats))] for every map element whose chain checks out: the first object's vtable inside
    the exe, and config values that look like the game's (the holder at +0x488 has no vtable of its own)."""
    head = read(h, base + REGISTRY, 16)
    if not head:
        return []
    data, num = struct.unpack_from("<Qi", head)
    if not data or not 0 < num < 64:
        return []
    found = []
    for i in range(num):
        elem = read(h, data + 32 * i, 32)
        if not elem:
            continue
        arr, count = struct.unpack_from("<Qi", elem, 8)
        if not arr or not 0 < count < 64:
            continue
        first = q(h, arr)
        if not first or not in_exe(q(h, first), base, size):
            continue
        holder = q(h, first + HOLDER)
        if not holder:
            continue
        raw = read(h, holder + CONFIG, 4 * len(FIELDS))
        if not raw:
            continue
        values = struct.unpack("<" + "f" * len(FIELDS), raw)
        if 0.5 <= values[0] < 1000.0 and 0.5 <= values[1] < 10.0 and all(0.0 <= v < 1000.0 for v in values):
            found.append((holder + CONFIG, values))
    return found


def say(line, out):
    stamp = time.strftime("%H:%M:%S")
    print(stamp, line, flush=True)
    out.write(f"{stamp} {line}\n")
    out.flush()


def main():
    rolls = float(sys.argv[1]) if len(sys.argv) > 1 else 4.0
    assert 0 <= rolls <= 100, "loot quality 0..100 (A+100 uses 100)"
    while not pid_of():
        time.sleep(2)
    h = base = None
    while not h:
        time.sleep(2)
        h, base = open_game()
    while not unpacked(h, base):
        time.sleep(1)
    size = main_module(h)[1]
    seen = {}
    with open(LOG, "w") as out:
        say(f"watching; loot quality set to {rolls:g} ({rolls + 1:g} rarity rolls)", out)
        while alive(h):
            for addr, values in configs(h, base, size):
                shown = ", ".join(f"{n} {v:g}" for n, v in zip(FIELDS, values))
                if seen.get(addr) != values:
                    say(f"config at 0x{addr:X}: {shown}", out)
                    seen[addr] = values
                if values[2] != rolls:
                    k32.WriteProcessMemory(h, ctypes.c_void_p(addr + LOOT_QUALITY), struct.pack("<f", rolls), 4,
                                           None)
                    say(f"  set LootQualityBoost {values[2]:g} -> {rolls:g} at 0x{addr + LOOT_QUALITY:X}", out)
            time.sleep(1)
        say("game closed", out)


if __name__ == "__main__":
    main()
