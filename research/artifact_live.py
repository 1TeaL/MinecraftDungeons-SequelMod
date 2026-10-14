"""Live artifact instances (the actors of equipped artifacts): their ItemPower (+0x480) and neighbours.

    python research/artifact_live.py                 # list
    python research/artifact_live.py <address> <f>   # write float f to that instance's ItemPower
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from aplus_patch import open_game  # noqa: E402
from builtins_patch import write  # noqa: E402
from endless_patch import find_pointers  # noqa: E402
from memprobe import read  # noqa: E402

VTABLES = {"TargetingStrikeItem (Lightning Rod)": 0xB188C8 + 0x281F458, "SoulHealer": 0xB182F8 + 0x28217E8}
ITEM_POWER = 0x480

h, base = open_game()
if not h:
    sys.exit("game not running")
if len(sys.argv) == 3:
    at = int(sys.argv[1], 16)
    old = struct.unpack("<f", read(h, at + ITEM_POWER, 4))[0]
    write(h, at + ITEM_POWER, struct.pack("<f", float(sys.argv[2])))
    print(f"{at:#x}: ItemPower {old:g} -> {float(sys.argv[2]):g}")
    sys.exit()
found = find_pointers(h, [base + v for v in VTABLES.values()])
for name, v in VTABLES.items():
    for o in found[base + v]:
        raw = read(h, o + 0x470, 0x30)
        if raw:
            print(f"{name:38} {o:#x}  " + " ".join(f"{x:g}" for x in struct.unpack("<12f", raw)))
