"""Stacking test: give one item type extra built-in copies of an enchantment in the running game.

    python research/stack_test.py MeleeWeapons/Axe_Unique1 Shockwave 3 2    # one copy at tier 3, one at tier 2
    python research/stack_test.py MeleeWeapons/Axe_Unique1 Shockwave        # back to its own built-ins

The item's own built-ins are kept (remembered per game session in research/stack_test_original.json).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import builtins_patch as bp  # noqa: E402
from aplus_patch import open_game, pid_of  # noqa: E402
from bonus_watch import Watch  # noqa: E402

KEEP = Path(__file__).with_name("stack_test_original.json")
item, enchant, tiers = sys.argv[1], sys.argv[2], [int(t) for t in sys.argv[3:]]
h, base = open_game()
if not h:
    sys.exit("game not running")
kept = json.loads(KEEP.read_text()) if KEEP.exists() else {}
if kept.get("pid") != pid_of():
    kept = {"pid": pid_of()}
if item not in kept:
    kept[item] = bp.builtins(h, base, item)[1]
    KEEP.write_text(json.dumps(kept))
entries = [tuple(e) for e in kept[item]] + [(bp.IDS[enchant], t) for t in tiers]
print("written" if Watch(h, base).write(item, entries) else "FAILED",
      ", ".join(f"{bp.NAMES[t]} {lv}" for t, lv in entries))
