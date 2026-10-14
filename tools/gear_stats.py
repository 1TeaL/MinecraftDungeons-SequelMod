"""Extract melee/ranged weapon stats from the game files into tools/gear_stats.json (read-only).

    python tools/gear_stats.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sequel import EXTRACT, _bp_super, _find_package  # noqa: E402
from uasset import Package  # noqa: E402

CONTENT = EXTRACT / "Dungeons" / "Content"


def val(props, name, default=None):
    return next((p["value"] for p in props if p["name"] == name), default)


def melee(props):
    variants = val(props, "ConfiguredAttackVariants", [])
    hits = []
    for v in variants:
        d = {p["name"]: p["value"] for p in v}
        hits.append({"name": d.get("Name"), "damage": d.get("Damage"), "time": d.get("AttackAnimationTimeDurationSeconds"),
                     "range": d.get("AttackRange"), "cone": d.get("ConeAngleDegrees"), "splash": d.get("DamageSplashMultiplier"),
                     "cooldown": d.get("CooldownSeconds"), "type": str(d.get("AttackVariantType", "")).split("::")[-1],
                     "loop": d.get("VariantLoopAmount"), "interval": d.get("ContinuousDamageInterval")})
    return {"hits": hits}


def ranged(props):
    a = val(props, "AttackDefintion", [])
    d = {p["name"]: p["value"] for p in a} if isinstance(a, list) else {}
    projs = d.get("ProjectileDefinition") or []
    n = sum(next((p["value"] for p in pr if p["name"] == "NumberOfProjectiles"), 1) for pr in projs) if projs else None
    return {"attack_rate": d.get("AttackRateSeconds"), "charge_time": d.get("ChargeTimeSecond"),
            "charge_mult": d.get("ChargeDamageMultiplier"), "damage_factor": d.get("ProjectileDamageFactor"),
            "projectiles": n, "ammo": val(props, "ProjectileStackCount")}


def merged_props(f):
    """CDO properties of a blueprint with values inherited from its parent blueprints filled in."""
    chain, pkg = [], Package(f)
    for _ in range(10):
        cdo = pkg.cdo()
        if cdo:
            chain.append(pkg.export_props(cdo))
        sup = _bp_super(pkg)
        if not sup or not sup[2].startswith("/Game/"):
            break
        pf = _find_package(sup[2])
        if pf is None:
            break
        pkg = Package(pf)
    def merge(child, parent):
        """Child values win; structs are stored as differences, so merge them field by field."""
        by_name = {p["name"]: p for p in child}
        out = list(child)
        for prop in parent:
            mine = by_name.get(prop["name"])
            if mine is None:
                out.append(prop)
            elif prop["type"] == "StructProperty" and isinstance(mine["value"], list) and isinstance(prop["value"], list):
                mine["value"] = merge(mine["value"], prop["value"])
        return out

    merged = []
    for props in chain:  # child first
        merged = merge(merged, props)
    return merged


out = {}
for f in sorted(CONTENT.rglob("BP_*Instance.uasset")):
    if "Equipment" not in f.parts:
        continue
    try:
        props = merged_props(f)
    except Exception as e:  # noqa: BLE001
        print("skip", f.name, e)
        continue
    item = val(props, "ItemIdName") or f.parent.name
    kind = "Melee" if "MeleeWeapons" in f.parts else "Ranged" if "RangedWeapons" in f.parts else "Armor" if "Armor" in f.parts else "?"
    rec = {"kind": kind, "file": str(f.relative_to(CONTENT)).replace("\\", "/")}
    if kind == "Melee":
        rec.update(melee(props))
    elif kind == "Ranged":
        rec.update(ranged(props))
    out[item] = rec
    out.setdefault(f.parent.name, rec)  # wiki ids sometimes use the folder name (e.g. Sword_Steel)
(Path(__file__).with_name("gear_stats.json")).write_text(json.dumps(out, indent=1), encoding="utf-8")
from collections import Counter
print(Counter(r["kind"] for r in out.values()))
