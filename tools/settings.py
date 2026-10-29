"""Where the settings files live, and the two central files laid over them.

    Settings.toml           the launcher's settings in one file (no rebuild: change, save, restart)
    Build.toml              the pak's big dials in one file (change, then python tools/sequel.py build)
    settings/launcher/      the detailed files the launcher reads
    settings/build/         the detailed files built into the pak

Every line of the two central files stands for one setting of a detailed file, and lives only there: the detailed
file has a note in its place. The tools read their file through load(), which fills those lines in. A setting
missing from both places falls back to the tool's default (mostly the game's own value).

    python tools/settings.py        # check both central files and show what they set where
"""
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LAUNCHER_DIR = ROOT / "settings" / "launcher"
BUILD_DIR = ROOT / "settings" / "build"
BUILD_FILES = {"SequelMod.toml", "SequelGear.toml", "SequelText.toml", "Endless.toml", "Player.toml", "StackNotes.toml"}
FRONT = {"Settings.toml": ROOT / "Settings.toml", "Build.toml": ROOT / "Build.toml"}

# "<section>.<key>" of a central file -> (detailed file, path inside it). [on] of Settings.toml maps key for key onto
# Launcher.toml. QoL.toml and Player.toml have no file of their own any more: all their settings are central.
MAP = {
    "Settings.toml": {
        "start.start": ("QoL.toml", ("start", "start")),
        "start.level": ("QoL.toml", ("start", "start_level")),
        "start.kit_power": ("QoL.toml", ("start", "kit_power")),
        "start.kit": ("QoL.toml", ("start", "kit")),
        "gear.blacksmith_missions": ("QoL.toml", ("blacksmith", "missions")),
        "gear.blacksmith_match_power": ("Bonus.toml", ("blacksmith", "match_power")),
        "gear.gilded_chance": ("Bonus.toml", ("gilded", "chance")),
        "gear.gilded_from": ("Bonus.toml", ("gilded", "from_power")),
        "gear.gilded_early_chance": ("Bonus.toml", ("gilded", "early_chance")),
        "gear.gilded_early_from": ("Bonus.toml", ("gilded", "early_from")),
        "prices.enchantsmith": ("Prices.toml", ("enchantmentmerchant",)),
        "prices.piglin": ("Prices.toml", ("piglinmerchant",)),
        "mobs.deflect": ("MobPool.toml", ("pool", "Deflecting")),
        "mobs.levitation_shot": ("MobPool.toml", ("pool", "LevitationShot")),
        "endless.staged": ("Unlock.toml", ("unlock", "staged")),
    },
    "Build.toml": {
        "mobs.health": ("Endless.toml", ("natural", "MobMaxHealthMultiplier")),
        "mobs.damage": ("Endless.toml", ("natural", "MobDamageMultiplier")),
        "mobs.speed": ("Endless.toml", ("natural", "MobSpeedMultiplier")),
        "mobs.knockback": ("Endless.toml", ("natural", "MobPushbackMultiplier")),
        "mobs.count": ("Endless.toml", ("natural", "MobCountMultiplier")),
        "mobs.revive_chance": ("Endless.toml", ("natural", "MobResurrectionChance")),
        "mobs.enchanted_chance": ("Endless.toml", ("natural", "EnchantedMobChanceMultiplier")),
        "mobs.enchanted_power": ("Endless.toml", ("natural", "EnchantedMobPowerMultiplier")),
        "player.healing_received": ("Endless.toml", ("natural", "PlayerReceiveHealingMultiplier")),
        "player.speed_after_roll": ("Player.toml", ("speed_after_roll",)),
        "player.walk_speed": ("Player.toml", ("walk_speed",)),
        "rewards.xp": ("Endless.toml", ("natural", "XPMultiplier")),
        "rewards.loot_quality": ("Endless.toml", ("natural", "LootQualityBoost")),
        "rewards.finale_xp": ("Endless.toml", ("finale", "XPMultiplier")),
        "rewards.finale_loot_quality": ("Endless.toml", ("finale", "LootQualityBoost")),
    },
}
ON_KEYS = {"builtins", "stacking", "echo", "formulas", "artifact_scaling", "seasonal_drops", "prices", "mob_pool",
           "arrows", "mob_enchants", "qol", "bonus", "endless"}   # not "cap": that one changes game code

_cache = {}


def path(name):
    """Where a detailed settings file lives: settings/build/ for the pak's, settings/launcher/ for the rest."""
    return (BUILD_DIR if name in BUILD_FILES else LAUNCHER_DIR) / name


def _read(front):
    found, problems = {}, []
    file = FRONT[front]
    try:
        data = tomllib.loads(file.read_text(encoding="utf-8")) if file.exists() else {}
    except tomllib.TOMLDecodeError as e:
        return {}, [f"{front} can't be read ({e}) - its settings are not used."]
    for section, values in data.items():
        if not isinstance(values, dict):
            problems.append(f"{front}: '{section}' isn't under a [section] - ignored.")
            continue
        for key, value in values.items():
            if front == "Settings.toml" and section == "on" and key in ON_KEYS:
                target = ("Launcher.toml", (key,))
            elif f"{section}.{key}" in MAP[front]:
                target = MAP[front][f"{section}.{key}"]
            else:
                problems.append(f"{front}: unknown setting [{section}] {key} - ignored.")
                continue
            found.setdefault(target[0], []).append((target[1], value))
    return found, problems


def overrides():
    """{detailed file name: [(path, value)]} from both central files - read again whenever one of them changes, so
    a change made while the launcher runs counts at its next step (for example the start kit after the game closes)."""
    stamp = tuple(f.stat().st_mtime_ns if f.exists() else 0 for f in FRONT.values())
    if _cache.get("stamp") != stamp:
        _cache["stamp"] = stamp
        _cache["data"], _cache["problems"] = {}, {}
        for front in FRONT:
            found, problems = _read(front)
            for name, items in found.items():
                _cache["data"].setdefault(name, []).extend(items)
            _cache["problems"][front] = problems
    return _cache["data"]


def problems(front="Settings.toml"):
    overrides()
    return _cache["problems"][front]


def load(file):
    """A detailed settings file as a dict (empty if it's missing), with the central files' values filled in."""
    file = Path(file)
    cfg = tomllib.loads(file.read_text(encoding="utf-8")) if file.exists() else {}
    for keys, value in overrides().get(file.name, []):
        at = cfg
        for k in keys[:-1]:
            at = at.setdefault(k, {})
        at[keys[-1]] = value
    return cfg


if __name__ == "__main__":
    for front in FRONT:
        for p in problems(front):
            print(p)
    for name, items in overrides().items():
        for keys, value in items:
            print(f"{name} {'.'.join(keys)} = {value!r}")
