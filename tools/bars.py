"""The power / speed / area (ammo) bars on a weapon's card, kept in step with SequelGear.toml.

The bars are not worked out from a weapon's numbers: they are stored scores (1-14) per item in one lookup asset,
Dungeons/Content/Packaging/ItemInstanceDataLookup - a map item id -> list of entries {ItemStatsID, ScoreInt,
ScoreFloat, ScoreMax, names}. So they stay as the game shipped them when a weapon is re-tuned.
This rewrites the scores of every weapon whose numbers differ from the game's in SequelGear.toml (each line there
carries its `# default`), scaling the game's own score by how much the weapon changed:
    melee   power x total damage of the combo, speed x 1 / total swing time, area x range^2 * cone angle
    ranged  power x damage factor (or the charge multiplier where only that changed) x projectiles per shot,
            speed x 1 / time between shots, ammo x bundle size
kept within 1-14. Only the two numbers are overwritten in place, so the file keeps its size and layout.
Checked against the game's own scores (2026-10-13): power is close to 0.083 x the combo's average damage.
"""
import re
from collections import defaultdict
from pathlib import Path

import uasset
from uasset import Package

ASSET = "Dungeons/Content/Packaging/ItemInstanceDataLookup.uasset"
LOW, HIGH = 1.0, 14.0
LINE = re.compile(r'"B[Pp]_\w+?Instance\.(.+?)" = ([\d.]+)\s+# default ([\d.]+)')
ALIASES = {"sword_steel": "sword", "pickaxe_steel": "pickaxe", "pickaxe_unique1_steel": "pickaxe_unique1",
           "pickaxe_unique2_steel": "pickaxe_unique2"}


def gear_changes(gear_config):
    """{item id in lower case: {"AverageDamage": factor, "AttackSpeed": factor, "AreaDamage" | "QuiverAmmo": factor}}
    for the weapons SequelGear.toml changes; factors of 1 are left out."""
    items, kind, name = defaultdict(lambda: defaultdict(dict)), None, None
    for line in Path(gear_config).read_text(encoding="utf-8").splitlines():
        m = re.match(r"\[(Melee|Ranged)\.(\w+)\]", line)
        if m:
            kind, name = m.group(1), m.group(2).lower()
            continue
        m = LINE.match(line)
        if m and kind:
            field = m.group(1)
            variant = re.search(r"\[(\d+)\]", field)
            items[(kind, name)][field.split(".")[-1]][int(variant.group(1)) if variant else 0] = (float(m.group(2)), float(m.group(3)))
    out = {}
    for (kind, name), fields in items.items():
        def ratio(field, inverse=False):
            vals = fields.get(field, {}).values()
            new, old = sum(v[0] for v in vals), sum(v[1] for v in vals)
            if not new or not old:
                return 1.0
            return old / new if inverse else new / old
        if kind == "Melee":
            area = [[fields["AttackRange"][v][k] ** 2 * min(360.0, fields["ConeAngleDegrees"][v][k]) for v in fields.get("AttackRange", {})
                     if v in fields.get("ConeAngleDegrees", {})] for k in (0, 1)]   # lists: a generator here saw only k = 1
            new_area, old_area = (sum(a) for a in area)
            factors = {"AverageDamage": ratio("Damage"), "AttackSpeed": ratio("AttackAnimationTimeDurationSeconds", True),
                       "AreaDamage": new_area / old_area if new_area and old_area else 1.0}
        else:
            damage = ratio("ProjectileDamageFactor")
            if damage == 1.0:
                damage = ratio("ChargeDamageMultiplier")
            factors = {"AverageDamage": damage * ratio("NumberOfProjectiles"), "AttackSpeed": ratio("AttackRateSeconds", True),
                       "QuiverAmmo": ratio("ProjectileStackCount")}
        factors = {k: f for k, f in factors.items() if abs(f - 1.0) > 0.005}
        if factors:
            out[ALIASES.get(name, name)] = factors
    return out


def entries(pkg):
    """{item id in lower case: {stat: (ScoreInt property, ScoreFloat property)}} of the lookup."""
    stats = next(p for p in pkg.export_props(pkg.exports[0]) if p["name"] == "Stats")
    r = uasset.Reader(pkg.data, stats["pos"])
    end = stats["pos"] + stats["size"]
    r.i32()
    out = {}
    for _ in range(r.i32()):
        key = pkg.read_props(r, end, 1)
        value = pkg.read_props(r, end, 1)
        if not key or not value or not isinstance(value[0]["value"], list):
            continue
        item = {}
        for entry in value[0]["value"]:
            by = {q["name"]: q for q in entry}
            if {"ItemStatsID", "ScoreInt", "ScoreFloat"} <= set(by):
                item[str(by["ItemStatsID"]["value"]).split("::")[-1]] = (by["ScoreInt"], by["ScoreFloat"])
        out[str(key[0]["value"]).lower()] = item
    return out


def build(build_root, extract_root, gear_config, quiet=False):
    """Write the lookup with the changed weapons' scores under build_root. Returns the files written."""
    import struct
    src = Path(extract_root) / ASSET
    if not src.exists() or not Path(gear_config).exists():
        return []
    pkg = Package(src)
    data, table, changed = bytearray(pkg.data), entries(pkg), 0
    for name, factors in sorted(gear_changes(gear_config).items()):
        notes = []
        for stat, factor in factors.items():
            if stat not in table.get(name, {}):
                continue
            as_int, as_float = table[name][stat]
            old = as_float["value"]
            new = min(HIGH, max(LOW, old * factor))
            if abs(new - old) < 0.05:
                continue
            struct.pack_into("<f", data, as_float["pos"], new)
            struct.pack_into("<i", data, as_int["pos"], max(1, int(new + 0.5)))
            notes.append(f"{stat} {old:.1f} -> {new:.1f}")
        if notes:
            changed += 1
            if not quiet:
                print(f"  bars {name}: " + ", ".join(notes))
    if not changed:
        return []
    dest = Path(build_root) / ASSET
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(bytes(data[:len(pkg.head)]))
    dest.with_suffix(".uexp").write_bytes(bytes(data[len(pkg.head):]))
    print(f"  weapon card bars: {changed} weapons updated")
    return [dest]
