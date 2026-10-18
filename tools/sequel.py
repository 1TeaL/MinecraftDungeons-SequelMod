"""Sequel Mod builder.

    python tools/sequel.py scan     # read the game files, (re)write SequelMod.toml with every editable stat
    python tools/sequel.py build    # apply SequelMod.toml and pack Dungeons/Content/Paks/~mods/SequelMod_P.pak
    python tools/sequel.py diff     # list the stats you've changed from the game defaults

Only values that differ from the game's defaults are written, and only the assets that contain
them go into the .pak, so the mod stays small and everything else stays vanilla.
"""
import json
import re
import shutil
import struct
import subprocess
import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bars  # noqa: E402
import player  # noqa: E402
import stack_text  # noqa: E402
import endless  # noqa: E402
from locres import Locres  # noqa: E402
from effects import EFFECTS, EXTRA_PROPS, modifiers_node  # noqa: E402
from uasset import Package, add_properties, set_export_properties  # noqa: E402
from memprobe import pid_of  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent          # Mods/SequelMod
GAME = ROOT.parent.parent                              # MinecraftDungeons
EXTRACT = GAME / "Mods" / "Dungeons BMS" / "BMS output"
U4PAK = GAME / "Mods" / "Dungeons-Mod-Kit-master" / "Tools" / "py" / "u4pak.py"
OUT_PAK = GAME / "Dungeons" / "Content" / "Paks" / "~mods" / "SequelMod_P.pak"
STAGED_PAK = ROOT / "staged" / OUT_PAK.name   # built here while the game is running
CONFIG = ROOT / "SequelMod.toml"
TEXT_CONFIG = ROOT / "SequelText.toml"
GEAR_CONFIG = ROOT / "SequelGear.toml"
ENDLESS_CONFIG = ROOT / "Endless.toml"
LOCRES = "Dungeons/Content/Localization/Game/{lang}/Game.locres"
INDEX = ROOT / "tools" / "fields.json"
BUILD = ROOT / "build"
UE4SS_MOD = GAME / "Dungeons" / "Binaries" / "Win64" / "ue4ss" / "Mods" / "SequelMod"  # old, removed on build

# Exports that never hold gameplay numbers.
SKIP_CLASSES = {"Function", "BlueprintGeneratedClass", "SCS_Node", "SimpleConstructionScript",
                "AudioComponent", "ParticleSystemComponent", "StaticMeshComponent",
                "SkeletalMeshComponent", "SceneComponent", "BillboardComponent", "ArrowComponent",
                "PointLightComponent", "DecalComponent", "Package", "MetaData"}
# Property paths that are engine plumbing rather than stats.
NOISE = re.compile(
    r"Tick|BodyInstance|Collision|Relative|UberGraph|Guid|bAutoActivate|bVisible|bHidden|Shadow"
    r"|bReplicates|NetCull|bNetLoad|DrawDistance|Navigation|AttributeBasedMagnitude|SetByCaller"
    r"|GameplayCues|Lightmap|LightMap|Bounds|TreatAsInherrent|bIsEditorOnly|ComponentTags|AreaClass"
    r"|SpriteScale|ArrowSize|bUseAttachParentBound|bAbsolute|VisibilityId|EntryPoint|ShapeColor"
    r"|bGenerateOverlapEvents|bCanEverAffect|bSuppressStackingCues|bDenyOverflowApplication"
    r"|bClearStackOnOverflow|bRequireModifierSuccessToTriggerCues|Priority$|bValidatedAsWired"
    r"|bIsExternalCurve|bRenderInMainPass|bReceivesDecals|bGridMovement|(^|[.:])Level$"
    r"|InheritableComponentHandler|CookedComponentInstancing")


# --------------------------------------------------------------------------------------------
# scan
# --------------------------------------------------------------------------------------------

def leaves(props, prefix=""):
    """Yield (path, type, default, pos) for every editable number/bool in a property list."""
    for p in props:
        label = p["name"] + (f"[{p['index']}]" if p["index"] else "")
        path = prefix + label
        if NOISE.search(path):
            continue
        t, v = p["type"], p["value"]
        if t == "FloatProperty":
            yield path, "float", v, p["pos"]
        elif t == "IntProperty":
            yield path, "int", v, p["pos"]
        elif t == "BoolProperty":
            yield path, "bool", v, p["pos"]
        elif t == "ArrayProperty" and p["extra"] in ("FloatProperty", "IntProperty") and isinstance(v, list):
            yield path, "float[]" if p["extra"] == "FloatProperty" else "int[]", v, p["pos"]
        elif t == "StructProperty" and isinstance(v, list):
            yield from leaves(v, path + ".")
        elif t == "ArrayProperty" and isinstance(v, list) and v and isinstance(v[0], list):
            for i, item in enumerate(v):
                yield from leaves(item, f"{path}[{i}].")


def scan_asset(f):
    pkg = Package(f)
    out = []
    for e in pkg.exports:
        cls = pkg.objname(e["class"])
        if cls in SKIP_CLASSES or cls.endswith("Property") or cls.startswith("Anim"):
            continue
        try:
            props = pkg.export_props(e)
        except Exception:
            continue
        owner = "" if e["name"].startswith("Default__") else e["name"] + ":"
        for path, t, v, pos in leaves(props):
            out.append((owner + path, t, v, pos))
    return pkg, out


def scan_table(f):
    pkg = Package(f)
    out = []
    for row, props in pkg.datatable_rows(pkg.exports[0]).items():
        for path, t, v, pos in leaves(props, row + "."):
            out.append((path, t, v, pos))
    return pkg, out


# Generic UEnchantment fields - per-item state, not balance stats.
RUNTIME_SKIP = {"Level", "TypeID", "EnchantmentSource", "OwnerItemRarity", "bAlwaysTrigger",
                "TreatAsInherrent", "ApplyOnlyToFirstHit", "bOverrideSecondaryEnchantmentEffects",
                "DestroySummonsOnDestruction"}
RUNTIME_TYPES = {"FloatProperty": "float", "IntProperty": "int", "BoolProperty": "bool"}


def _bp_super(pkg):
    """(class name, parent class name, parent package path) for a blueprint package, or None."""
    for e in pkg.exports:
        if e["name"].endswith("_C") and not e["name"].startswith("Default__") and e["super"] < 0:
            cpkg, cls, outer, name = pkg.imports[-e["super"] - 1]
            if outer < 0:
                return e["name"], name, pkg.imports[-outer - 1][3]
    return None


def _find_package(game_path):
    rel = game_path[len("/Game/"):] + ".uasset"
    for cand in (EXTRACT / "Dungeons" / "Content" / rel, EXTRACT / rel):
        if cand.exists():
            return cand
    return None


def native_parent(pkg):
    """(blueprint class name, /Script/Dungeons class name, values set by parent blueprints) or None.

    Walks up through parent blueprints (e.g. BP_PlayerPoisonArrow -> BP_BowArrow -> BP_Arrow -> native)
    so inherited settings get their real defaults.
    """
    first = _bp_super(pkg)
    if not first:
        return None
    inherited, cur = {}, first
    for _ in range(10):
        _, parent, parent_pkg = cur
        if parent_pkg == "/Script/Dungeons":
            return first[0], parent, inherited
        if not parent_pkg.startswith("/Game/"):
            return None
        f = _find_package(parent_pkg)
        if f is None:
            return None
        ppkg = Package(f)
        cdo = ppkg.cdo()
        if cdo:
            try:
                for path, t, v, _pos in leaves(ppkg.export_props(cdo)):
                    inherited.setdefault(path.lower(), (t, v))  # nearer parents win
            except Exception:
                pass
        cur = _bp_super(ppkg)
        if not cur:
            return None
    return None


def native_defaults():
    """class -> {property: (type, default)} from the UE4SS dump (data/native_defaults.tsv)."""
    path = ROOT / "data" / "native_defaults.tsv"
    out = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines()[1:]:
        cls, prop, ptype, value, _owner = line.split(chr(9))
        t = RUNTIME_TYPES.get(ptype)
        if not t or prop in RUNTIME_SKIP or value == "?":
            continue
        v = (value == "true") if t == "bool" else int(value) if t == "int" else float(value)
        out.setdefault(cls, {})[prop] = (t, v)
    return out


NAME_FALLBACK = {"AnimaRanged": "Anima Conduit", "Celerity": "Cool Down", "Soul": "Soul Siphon"}


def display_names():
    """Folder/blueprint name -> in-game enchantment name, from the game's text + our sheet mapping."""
    loc = json.load(open(ROOT / "tools" / "game_en.json", encoding="utf-8"))
    names = {}
    sheet = (ROOT / "tools" / "build_sheet.py").read_text(encoding="utf-8")
    for cat, key, bp in re.findall(r'\((M|R|A), "(\w+)", "(\w+)"', sheet):
        n = loc.get(f"Enchantment/{key}") or NAME_FALLBACK.get(key, key)
        names[bp.lower()] = (n, {"M": "Melee", "R": "Ranged", "A": "Armor"}[cat])
    return names


# Assets outside the enchantment folders that belong to an enchantment: path -> config folder name.
EXTRA_ASSETS = {
    "Dungeons/Content/Actors/Items/Arrow/Player/BP_PlayerPoisonArrow.uasset": "DippingPoison",
    "Dungeons/Content/Content_DLC5/Actors/Items/GuardianEye/BP_GuardianEyeInstance.uasset": "GuardianEye",
    "Dungeons/Content/Actors/Items/IceWand/BP_IceWandInstance.uasset": "IceWand",
    "Dungeons/Content/Actors/Items/TastyBone/BP_TastyBoneInstance.uasset": "TastyBone",
    "Dungeons/Content/Actors/Items/GolemKit/BP_GolemKitInstance.uasset": "GolemKit",
    "Dungeons/Content/Actors/Items/WonderfulWheat/BP_WonderfulWheatInstance.uasset": "WonderfulWheat",
    "Dungeons/Content/Patch2/Actors/Items/RainbowGrass/BP_RainbowGrassInstance.uasset": "RainbowGrass",
    "Dungeons/Content/Patch2/Actors/Items/SoulLantern/BP_SoulLanternInstance.uasset": "SoulLantern",
    "Components/ArmorProperties/TeleportChance/BP_TeleportChance.uasset": "PerkTeleportChance",
    "Components/ArmorProperties/RangedDamageBoost/BP_RangedDamageBoost.uasset": "PerkRangedDamageBoost",
    "Components/ArmorProperties/MoveSpeedAura/BP_MoveSpeedAura.uasset": "PerkMoveSpeedAura",
    "Dungeons/Content/Components/ArmorProperties/HealingAura/BP_HealingAura.uasset": "PerkHealingAura",
    "Dungeons/Content/Components/ArmorProperties/HealingAura/BP_HealingAuraGameplayEffect.uasset": "PerkHealingAuraGameplayEffect",
}
# Projectile plumbing that isn't worth exposing.
RUNTIME_SKIP_EXTRA = {"enableDebugVisuals", "bShouldHitTerrain", "ignoreFriendlyFire", "TimeThreshold",
                      "HomingThreshold", "RespectWeaponProjectileVelocityFactor", "MaxProjectileLifeTime",
                      "IsCharged", "bCanTriggerEnchantments", "bAffectedByCustomPhysics", "MaxDist5Degrees",
                      "MaxDist40Degrees", "ForcedExpireDistance", "bCanAttachPropOnDeadMobs",
                      "SerializedExplosionDamage", "SerializedExplosionRadius", "UseDefaultDissolveOnKill",
                      "ReplaceOldInstances", "Damage"}


# Weapon blueprints: only balance fields go in SequelGear.toml.
GEAR_DIRS = {"meleeweapons": "Melee", "rangedweapons": "Ranged"}
GEAR_FIELDS = re.compile(
    r"^ConfiguredAttackVariants\[\d+\]\.(Damage|AttackAnimationTimeDurationSeconds|AttackRange|ConeAngleDegrees"
    r"|DamageSplashMultiplier|CooldownSeconds|StunMultiplier|pushback\.pushbackStrength)$"
    r"|^AttackDefintion\.(AttackRateSeconds|ChargeTimeSecond|ChargeDamageMultiplier|ProjectileDamageFactor"
    r"|ProjectileDefinition\[\d+\]\.NumberOfProjectiles)$|^ProjectileStackCount$")


def gear_files():
    """{weapon instance blueprint: (section, title)}"""
    loc = json.load(open(ROOT / "tools" / "game_en.json", encoding="utf-8"))
    out = {}
    for f in sorted(EXTRACT.rglob("BP_*Instance.uasset")):
        if f.parent.parent.name.lower() not in GEAR_DIRS:
            continue
        kind = GEAR_DIRS[f.parent.parent.name.lower()]
        item = f.parent.name
        name = loc.get(f"ItemType/{item}") or item
        base = item.split("_")[0]
        base_name = loc.get(f"ItemType/{base}") or base
        title = name if "_" not in item or name == base_name else f"{name} ({base_name} variant)"
        out[f] = (f"{kind}.{item}", title)
    return out


# Ranged stats a bow may not store in its own file: a unique often keeps only its arrow count and inherits the rest
# from its base bow (and with it the mod's changes to that bow). Listed as settings anyway, with the inherited game
# value as the default; a changed one is added to the bow's file at build time (into its AttackDefintion struct, or
# at the top for the bundle size), after which that bow no longer inherits it (user, 2026-10-18: seasonal bows with
# stats of their own).
INHERITED = {"AttackDefintion.AttackRateSeconds": ("float", "attack_rate"),
             "AttackDefintion.ChargeTimeSecond": ("float", "charge_time"),
             "AttackDefintion.ChargeDamageMultiplier": ("float", "charge_mult"),
             "AttackDefintion.ProjectileDamageFactor": ("float", "damage_factor"),
             "ProjectileStackCount": ("int", "ammo")}


def inherited_stats(item, have):
    """[(path, type, inherited game value)] of INHERITED stats a ranged weapon's file doesn't store."""
    stats = {k.lower(): v for k, v in json.loads((ROOT / "tools" / "gear_stats.json").read_text()).items() if v}
    resolved = stats.get(item.lower()) or {}
    out = []
    for path, (t, field) in INHERITED.items():
        v = resolved.get(field)
        if path not in have and v is not None:
            out.append((path, t, int(v) if t == "int" else round(float(v), 6)))
    return out


def scan():
    files = sorted(p for p in EXTRACT.rglob("*.uasset")
                   if "/components/enchantments/" in p.as_posix().lower()
                   and not re.match(r"(T|M|MI|P|PS|S|SK|SM)_", p.name))
    extra = {EXTRACT / rel: folder for rel, folder in EXTRA_ASSETS.items()}
    files += sorted(extra)
    tables = [EXTRACT / "Dungeons/Content/DataTables/Assets/EndlessStruggle.uasset"]
    names = display_names()
    gear = gear_files()
    files += list(gear)

    natives = native_defaults()
    index, sections, seen = {}, {}, {}
    for f in files + tables:
        pkg, fields = scan_table(f) if f in tables else scan_asset(f)
        if f in gear:
            fields = [x for x in fields if GEAR_FIELDS.search(x[0])]
        game_path = pkg.package_path()
        parent = None if f in tables or f in gear else native_parent(pkg)
        runtime = []
        if parent and parent[1] in natives:
            overridden = {path.split(".")[0].split("[")[0].lower() for path, *_ in fields if ":" not in path}
            runtime = [(prop, t, parent[2].get(prop.lower(), (t, v))[1]) for prop, (t, v) in natives[parent[1]].items()
                       if prop.lower() not in overridden and not (f in extra and prop in RUNTIME_SKIP_EXTRA)]
        if not (fields or runtime) or not game_path:
            continue
        if game_path in seen:
            print(f"  ! duplicate asset {game_path}: using {seen[game_path]}")
            continue
        seen[game_path] = f.relative_to(EXTRACT).as_posix()
        if f in gear:
            section, title = gear[f]
        elif f in tables:
            section = "Difficulty.EndlessStruggle"
            title = "Apocalypse+ (Endless Struggle) scaling. Each stat goes from MinValue at level " \
                    "IntroducedAt to MaxValue at the top level. IntroducedAt 999 = off."
        else:
            folder = extra.get(f, f.parent.name)
            section = "Enchantments." + folder
            n = names.get(folder.lower()) or names.get(f.stem[3:].lower())
            title = f"{n[0]} ({n[1]})" if n else f"{folder} (unique item, mob or shared effect)"
        head = len(pkg.head)
        sec = sections.setdefault(section, {"title": title, "keys": []})
        for path, t, v, pos in fields:
            key = f"{f.stem}.{path}"
            assert pos >= head, f"{key} not in .uexp"
            index[f"{section}/{key}"] = {"file": seen[game_path], "game_path": game_path,
                                         "type": t, "default": v, "pos": pos - head}
            sec["keys"].append((key, t, v, False))
        if f in gear and section.startswith("Ranged."):
            for path, t, v in inherited_stats(section.split(".", 1)[1], {x[0] for x in fields}):
                key = f"{f.stem}.{path}"
                index[f"{section}/{key}"] = {"add": True, "file": seen[game_path], "game_path": game_path,
                                             "export": None, "struct": path.split(".")[0] if "." in path else None,
                                             "prop": path.split(".")[-1], "type": t, "default": v}
                sec["keys"].append((key, t, v, True))
        for prop, t, v in runtime:
            key = f"{f.stem}.{prop}"
            # Not stored in the file yet: build adds it to the blueprint's defaults.
            index[f"{section}/{key}"] = {"add": True, "file": seen[game_path], "game_path": game_path,
                                         "export": f"Default__{parent[0]}", "prop": prop,
                                         "type": t, "default": v}
            sec["keys"].append((key, t, v, True))

    # Gameplay effects whose modifier list we rebuild (see tools/effects.py).
    for folder, rel, keys, _ in EFFECTS:
        f = EXTRACT / rel
        game_path = Package(f).package_path()
        section = "Enchantments." + folder
        n = names.get(folder.lower())
        sec = sections.setdefault(section, {"title": f"{n[0]} ({n[1]})" if n else folder, "keys": []})
        for k, d in keys.items():
            key = f"{f.stem}.{k}"
            t = "int" if isinstance(d, int) else "float"
            index[f"{section}/{key}"] = {"effect": rel, "file": seen.get(game_path, rel), "game_path": game_path,
                                         "prop": k, "type": t, "default": d}
            sec["keys"].append((key, t, d, True))

    INDEX.write_text(json.dumps(index, indent=1), encoding="utf-8")
    old = load_config()
    is_gear = lambda s: s.split(".")[0] in GEAR_DIRS.values()  # noqa: E731
    write_config({k: v for k, v in sections.items() if not is_gear(k)}, old, CONFIG, HEADER)
    write_config({k: v for k, v in sections.items() if is_gear(k)}, old, GEAR_CONFIG, GEAR_HEADER)
    n_add = sum(1 for m in index.values() if m.get("add"))
    print(f"{len(index)} stats ({len(index) - n_add} stored in the files, {n_add} added on change) "
          f"in {len(sections)} sections -> {CONFIG.name} + {GEAR_CONFIG.name}")


def fmt(t, v):
    if t == "bool":
        return "true" if v else "false"
    if t == "float":
        return repr(round(v, 6))
    if t == "float[]":
        return "[" + ", ".join(repr(round(x, 6)) for x in v) + "]"
    if t == "int[]":
        return "[" + ", ".join(str(x) for x in v) + "]"
    return str(v)


HEADER = [
    "# Sequel Mod - stat config",
    "#",
    "# Change any value, then run:  python tools/sequel.py build",
    "# The comment after each value is the original game default. Delete a line or set it back",
    "# to the default to leave that stat vanilla. Don't add new lines - only stats listed here",
    "# exist in the game files.",
    "#",
    "# Everything here ends up in one file: Dungeons/Content/Paks/~mods/SequelMod_P.pak.",
    "# Defaults come from the game files and from the game's own class defaults.",
    "",
]
GEAR_HEADER = [
    "# Sequel Mod - weapon stats (melee and ranged)",
    "#",
    "# Change any value, then run:  python tools/sequel.py build   (same .pak as SequelMod.toml)",
    "# The comment after each value is the original game default.",
    "#",
    "# Melee, per hit of the combo (ConfiguredAttackVariants[0] = first hit):",
    "#   Damage, AttackAnimationTimeDurationSeconds (swing time), AttackRange, ConeAngleDegrees (width),",
    "#   DamageSplashMultiplier (damage to mobs around the target), CooldownSeconds, StunMultiplier,",
    "#   pushback.pushbackStrength (knockback).",
    "# Ranged: AttackRateSeconds (time between shots), ChargeTimeSecond, ChargeDamageMultiplier,",
    "#   ProjectileDamageFactor, NumberOfProjectiles (arrows per shot), ProjectileStackCount (arrow stack).",
    "# Ranged uniques also list the stats they inherit from their base weapon: left at the default, the unique follows its base",
    "# (including the mod's changes to it); a changed value is written into the unique itself.",
    "",
]


def write_config(sections, old, path=CONFIG, header=HEADER):
    lines = list(header)
    for section in sorted(sections, key=lambda s: (not s.startswith("Difficulty"), s.lower())):
        sec = sections[section]
        lines.append(f"[{section}]  # {sec['title']}")
        for key, t, default, runtime in sec["keys"]:
            cur = old.get(section, {}).get(key, default)
            lines.append(f'"{key}" = {fmt(t, cur)}  # default {fmt(t, default)}')
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


# --------------------------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------------------------

def load_config():
    data = {}
    for path in (CONFIG, GEAR_CONFIG):
        if path.exists():
            data.update(tomllib.loads(path.read_text(encoding="utf-8")))
    flat = {}

    def walk(d, prefix):
        for k, v in d.items():
            if isinstance(v, dict):
                walk(v, f"{prefix}{k}.")
            else:
                flat.setdefault(prefix[:-1], {})[k] = v
    walk(data, "")
    return flat


def changes():
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    out, errors = [], []
    for section, keys in load_config().items():
        for key, value in keys.items():
            meta = index.get(f"{section}/{key}")
            if meta is None:
                errors.append(f"[{section}] {key}: not a known stat (run scan?)")
                continue
            t, default = meta["type"], meta["default"]
            if t == "float" and isinstance(value, (int, float)) and not isinstance(value, bool):
                value = float(value)
            elif t == "int" and isinstance(value, int) and not isinstance(value, bool):
                pass
            elif t == "bool" and isinstance(value, bool):
                pass
            elif t.endswith("[]") and isinstance(value, list) and len(value) == len(default):
                value = [float(x) if t == "float[]" else int(x) for x in value]
            else:
                errors.append(f"[{section}] {key}: expected {t}"
                              + (f" with {len(default)} entries" if t.endswith("[]") else "")
                              + f", got {value!r}")
                continue
            same = (value == default if t != "float"
                    else struct.pack("<f", value) == struct.pack("<f", default))
            if t == "float[]":
                same = all(struct.pack("<f", a) == struct.pack("<f", b) for a, b in zip(value, default))
            if not same:
                out.append((section, key, meta, value))
    return out, errors


def patch(buf, meta, value):
    t, pos = meta["type"], meta["pos"]
    if t == "float":
        struct.pack_into("<f", buf, pos, value)
    elif t == "int":
        struct.pack_into("<i", buf, pos, value)
    elif t == "bool":
        buf[pos] = 1 if value else 0
    elif t in ("float[]", "int[]"):
        n = struct.unpack_from("<i", buf, pos)[0]
        assert n == len(value)
        for i, x in enumerate(value):
            struct.pack_into("<f" if t == "float[]" else "<i", buf, pos + 4 + 4 * i, x)


def text_changes():
    """[(lang, key, original, new)] for text overrides that differ from the game, plus errors."""
    if not TEXT_CONFIG.exists():
        return [], []
    out, errors = [], []
    for lang, entries in tomllib.loads(TEXT_CONFIG.read_text(encoding="utf-8")).items():
        src = EXTRACT / LOCRES.format(lang=lang)
        if not src.exists():
            errors.append(f"[{lang}] no extracted text file at {src}")
            continue
        loc = Locres(src.read_bytes())
        entries = dict(entries)
        if lang == "en":
            # "Copies of this enchantment stack." and the like, after the description (tools/stack_text.py)
            for key, sentence in stack_text.sentences(loc.keys).items():
                entries[key] = (entries.get(key) or loc.get(key)).rstrip() + " " + sentence
        for key, new in entries.items():
            if key not in loc.keys:
                errors.append(f"[{lang}] {key}: not a known text key")
            elif loc.get(key) != new:
                out.append((lang, key, loc.get(key), new))
    return out, errors


def build_text(changes_):
    for lang in sorted({c[0] for c in changes_}):
        loc = Locres((EXTRACT / LOCRES.format(lang=lang)).read_bytes())
        for _, key, old, new in (c for c in changes_ if c[0] == lang):
            loc.set(key, new)
            print(f"  text {key}: {new!r}")
        dest = BUILD / LOCRES.format(lang=lang)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(loc.to_bytes())
        check = Locres(dest.read_bytes())
        for _, key, old, new in (c for c in changes_ if c[0] == lang):
            if check.get(key) != new:
                sys.exit(f"Verification failed for text {key}")


def build(out_pak=None):
    staged = out_pak is None and pid_of() is not None   # the game keeps its .pak open while it runs
    out_pak = Path(out_pak) if out_pak else STAGED_PAK if staged else OUT_PAK
    todo, errors = changes()
    texts, text_errors = text_changes()
    errors += text_errors
    if errors:
        print("Config errors - nothing built:")
        for e in errors:
            print("  " + e)
        sys.exit(1)
    if UE4SS_MOD.exists():  # older builds applied some stats through UE4SS; the .pak does it all now
        shutil.rmtree(UE4SS_MOD)

    if not todo and not texts:
        print("No stats or text changed from default - no .pak needed.")
        if out_pak.exists():
            out_pak.unlink()
            print(f"Removed old {out_pak.name}.")
        return

    if BUILD.exists():
        shutil.rmtree(BUILD)
    by_file = {}
    for section, key, meta, value in todo:
        by_file.setdefault(meta["file"], (meta["game_path"], []))[1].append((key, meta, value))

    for rel, (game_path, edits) in by_file.items():
        src = EXTRACT / rel
        if not game_path.startswith("/Game/"):
            print(f"  ! skipping {game_path} (not under /Game)")
            continue
        dest = BUILD / "Dungeons" / "Content" / game_path[len("/Game/"):]
        dest.parent.mkdir(parents=True, exist_ok=True)
        uexp = bytearray(src.with_suffix(".uexp").read_bytes())
        added, effect_values = [], {}
        for key, meta, value in edits:
            if meta.get("effect"):
                effect_values.setdefault(meta["effect"], {})[meta["prop"]] = value
            elif meta.get("add"):
                added.append((meta.get("export"), meta.get("struct"), meta["prop"], meta["type"], value))
            else:
                patch(uexp, meta, value)
            print(f"  {key}: {fmt(meta['type'], meta['default'])} -> {fmt(meta['type'], value)}")
        head = src.read_bytes()
        for export, into in sorted({(a[0], a[1]) for a in added}, key=str):
            props = [(n, t, v) for e, st, n, t, v in added if (e, st) == (export, into)]
            pkg = Package(src, head=head, body=bytes(uexp))
            head, uexp = add_properties(pkg, export or pkg.cdo()["name"], props, into_struct=into)
        expected_mods = None
        for rel_effect, values in effect_values.items():
            _, _, keys, build_mods = next(e for e in EFFECTS if e[1] == rel_effect)
            allv = {**keys, **values}
            mods = build_mods(allv)
            nodes = [modifiers_node(mods)]
            nodes += [(prop, t, allv[k]) for k, (prop, t) in EXTRA_PROPS.items() if k in keys]
            pkg = Package(src, head=head, body=bytes(uexp))
            head, uexp = set_export_properties(pkg, pkg.cdo()["name"], nodes)
            expected_mods = len(mods)
        dest.with_suffix(".uasset").write_bytes(head)
        dest.with_suffix(".uexp").write_bytes(uexp)
        if src.with_suffix(".ubulk").exists():
            shutil.copyfile(src.with_suffix(".ubulk"), dest.with_suffix(".ubulk"))

        # Re-read the patched copy to make sure every value landed where we expect.
        check = Package(dest.with_suffix(".uasset"))
        _, fields = (scan_table if "DataTables" in game_path else scan_asset)(dest.with_suffix(".uasset"))
        got = {f"{dest.stem}.{p}": v for p, t, v, pos in fields}
        if expected_mods is not None:
            cdo_props = check.export_props(check.cdo())
            mods_read = next((x["value"] for x in cdo_props if x["name"] == "Modifiers"), [])
            if len(mods_read) != expected_mods:
                sys.exit(f"Verification failed for {dest.name}: expected {expected_mods} modifiers, "
                         f"read back {len(mods_read)}")
        for key, meta, value in edits:
            if meta.get("effect"):
                continue
            g = got.get(key)
            ok = (abs(g - value) < 1e-4 if meta["type"] == "float"
                  else [round(x, 4) for x in g] == [round(x, 4) for x in value] if meta["type"] == "float[]"
                  else g == value)
            if not ok:
                sys.exit(f"Verification failed for {key}: wrote {value!r}, read back {g!r}")
        del check

    endless_files = endless.build(BUILD, EXTRACT, ENDLESS_CONFIG) if ENDLESS_CONFIG.exists() else []
    bars.build(BUILD, EXTRACT, GEAR_CONFIG)
    player.build(BUILD, EXTRACT, ROOT / "Player.toml")
    build_text(texts)
    out_pak.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(U4PAK), "pack", str(out_pak), "Dungeons"], cwd=BUILD, check=True)
    print(f"Built {out_pak} ({len(todo)} stats in {len(by_file)} files, {len(texts)} text changes"
          + (f", {len(endless_files)} Endless Apocalypse files" if endless_files else "")
          + ")")
    if staged:
        print("The game is running, so the .pak was built aside. The launcher installs it at the next start.")
    elif out_pak == OUT_PAK and STAGED_PAK.exists():
        STAGED_PAK.unlink()   # older than what was just built


def diff():
    todo, errors = changes()
    for e in errors:
        print("  ! " + e)
    for section, key, meta, value in todo:
        print(f"[{section}] {key}: {fmt(meta['type'], meta['default'])} -> {fmt(meta['type'], value)}")
    texts, text_errors = text_changes()
    for e in text_errors:
        print("  ! " + e)
    for lang, key, old, new in texts:
        print(f"[text.{lang}] {key}: {old!r} -> {new!r}")
    if not todo and not texts:
        print("Everything is at game defaults.")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    args = sys.argv[2:]
    {"scan": scan, "build": lambda: build(*args), "diff": diff}.get(cmd, lambda: print(__doc__))()
