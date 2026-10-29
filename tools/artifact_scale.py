"""Artifact damage and healing that keep growing above the power cap (ArtifactScaling.toml). Data only.

    python tools/artifact_scale.py            # watch the running game until it closes
    python tools/artifact_scale.py --once     # one pass, printing what it set

The game stops gear at power 316: an artifact's power (a float at +0x480 of the artifact's actor, the stored
value: shown power = (stored - 1) * 10 + 1) is capped in code when it is used. But every equipped artifact is an
actor of its own that holds its base numbers - Lightning Rod's damage per soul, Soul Healer's heal per soul, a
pet artifact's damage and health multipliers... - as plain floats/ints (tools/artifact_fields.json, built by
research/artifact_fields.py from the exe). This multiplies those numbers on each live artifact above the cap by
a factor that grows with its power. Tested in play 2026-10-06 (Lightning Rod at 3x dealt 3x).

The unscaled numbers are taken from the class's default object (same class pointer at +0x10, power exactly 1),
so a pass is repeatable and a new actor - made when an artifact is equipped or a level starts - is simply set at
the next pass (tools/live_objects.py). Only equipped artifacts exist as actors.
"""
import json
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
import settings  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CONFIG = settings.path("ArtifactScaling.toml")
FIELDS = json.loads((ROOT / "tools" / "artifact_fields.json").read_text())
CLASS, ITEM_POWER = 0x10, 0x480


class ArtifactScale:
    def __init__(self, h, base, scanner=None):
        self.h, self.base = h, base
        self.own_scanner = scanner is None
        self.scanner = scanner or Scanner(h, base)
        cfg = settings.load(CONFIG)
        self.cap, self.top = cfg.get("cap", 316), cfg.get("top_power", 365)
        self.at_top = {"damage": float(cfg.get("damage_at_top", 1.0)), "heal": float(cfg.get("heal_at_top", 1.0))}
        self.by_vtable = {}        # absolute vtable -> {property: field} (classes sharing a vtable share a layout)
        if base and any(v != 1.0 for v in self.at_top.values()):
            for entry in FIELDS.values():
                if entry["fields"]:
                    self.by_vtable.setdefault(self.scanner.register(int(entry["vtable"], 16)), {}).update(entry["fields"])
        self.said = set()

    def factor(self, kind, shown):
        """1.0 up to the cap, then a steady percentage per power point up to `at_top` at top_power (and beyond)."""
        if shown <= self.cap:
            return 1.0
        return self.at_top[kind] ** ((shown - self.cap) / (self.top - self.cap))

    def value(self, o, field):
        raw = read(self.h, o + int(field["offset"], 16), 4)
        return struct.unpack("<f" if field["type"] == "float" else "<i", raw)[0] if raw else None

    def tick(self, quiet=False):
        if not self.by_vtable:
            return
        if self.own_scanner:
            self.scanner.refresh()
        for vt, fields in self.by_vtable.items():
            groups = {}            # class pointer -> [(object, stored power)]
            for o in self.scanner.found.get(vt, []):
                raw = read(self.h, o, ITEM_POWER + 4)
                if raw:
                    power = struct.unpack_from("<f", raw, ITEM_POWER)[0]
                    if 1.0 <= power < 60.0:
                        groups.setdefault(struct.unpack_from("<Q", raw, CLASS)[0], []).append((o, power))
            for members in groups.values():
                defaults = [o for o, power in members if power == 1.0]
                if not defaults:
                    continue
                for name, field in fields.items():
                    start = self.value(defaults[0], field)
                    if not start or not 0 < start < 1e6:
                        continue
                    for o, power in members:
                        shown = int((power - 1) * 10 + 1 + 1e-3)
                        want = start * self.factor(field["kind"], shown)
                        want = float(want) if field["type"] == "float" else int(round(want))
                        now = self.value(o, field)
                        if power == 1.0 or now is None or abs(now - want) <= 0.005 * abs(want):
                            continue
                        write(self.h, o + int(field["offset"], 16),
                              struct.pack("<f" if field["type"] == "float" else "<i", want))
                        if not quiet and (o, name) not in self.said:
                            self.said.add((o, name))
                            print(f"  artifact at power {shown}: {name} {start:g} -> {want:g}")


if __name__ == "__main__":
    h, base = open_game()
    if not h:
        sys.exit("Minecraft Dungeons isn't running")
    w = ArtifactScale(h, base)
    w.tick()
    while "--once" not in sys.argv and pid_of():
        time.sleep(3)
        w.tick()
