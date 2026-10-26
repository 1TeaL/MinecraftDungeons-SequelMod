"""Write CHANGES.md: every change the mod makes, base game -> mod, as plain Markdown that can be copied anywhere.

    python tools/change_sheet.py

Everything is read from the mod's own files, so the sheet is rebuilt after any change:
  SequelMod.toml / SequelGear.toml / SequelText.toml   through `sequel.py diff` and the `# default` comments
  Builtins.toml, Perks.toml, Artifacts.toml            with the game's own values taken from the launcher's last
                                                       log (launcher.log prints "old -> new" for each)
  Bonus.toml, Endless.toml, Formulas.toml, Echo.toml, ArtifactScaling.toml, Prices.toml, QoL.toml, Drops.toml,
  MobPool.toml, MobEnchants.toml
Facts only - no opinions or reasons (those are in decisions.md). Settings that are in place only for a test are
listed in their own section at the end and left out of the tables.
"""
import json
import re
import subprocess
import sys
import tomllib
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import endless_patch  # noqa: E402
import formula_patch  # noqa: E402
import sequel  # noqa: E402

LOC = json.loads((ROOT / "tools" / "game_en.json").read_text(encoding="utf-8"))
ALIASES = {"FireAspect": "Fire Aspect", "CriticalHit": "Critical Hit", "EnigmaResonatorMelee": "Enigma Resonator",
           "EnigmaResonatorRanged": "Enigma Resonator", "EnigmaResonator": "Enigma Resonator",
           "AnimaConduitMelee": "Anima Conduit", "AnimaConduitRanged": "Anima Conduit", "SoulSiphon": "Soul Siphon",
           "VoidTouchedMelee": "Void Strike", "VoidTouchedRanged": "Void Strike", "TempoTheft": "Tempo Theft",
           "Gravity": "Gravity", "Accelerating": "Accelerate", "Deflecting": "Deflect", "Celerity": "Cool Down",
           "LevitationShot": "Levitation Shot", "Levitation": "Levitation Shot", "Poisoned": "Poison Cloud"}
# In place for a test only: setting -> the value the mod is meant to have (None = the game's own, i.e. no change).
TESTS = {}
TEST_BUILTINS = set()
GEAR_FIELDS = {"Damage": "Damage", "AttackAnimationTimeDurationSeconds": "Swing time (s)", "AttackRange": "Reach",
               "ConeAngleDegrees": "Swing angle", "DamageSplashMultiplier": "Splash damage", "pushbackStrength": "Knockback",
               "StunMultiplier": "Stun", "CooldownSeconds": "Cooldown (s)", "AttackRateSeconds": "Time between shots (s)",
               "ChargeDamageMultiplier": "Charged shot damage", "ChargeTimeSecond": "Charge time (s)",
               "ProjectileDamageFactor": "Damage factor", "NumberOfProjectiles": "Projectiles per shot",
               "ProjectileStackCount": "Arrows per bundle"}


def words(name):
    """CamelCase or snake_case -> plain words."""
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|_", " ", name).strip()
    return s[:1].upper() + s[1:]


def num(v):
    try:
        return f"{float(v):g}"
    except (TypeError, ValueError):
        return str(v)


def ench(name):
    copy = name.endswith("!")
    name = name.rstrip("!")
    out = ALIASES.get(name)
    for c in (name, name.removesuffix("Melee"), name.removesuffix("Ranged"), name.removesuffix("Shot")):
        out = out or LOC.get(f"Enchantment/{c}")
    return (out or words(name)) + (" (second copy)" if copy else "")


def noted_names():
    """Item names written as comments in the mod's own lists: ["Armor/EmeraldArmor_Unique2"]  # Gilded Glory"""
    out = {}
    for name in ("Builtins.toml", "Perks.toml", "Drops.toml"):
        p = ROOT / name
        for line in (p.read_text(encoding="utf-8") if p.exists() else "").splitlines():
            m = re.match(r'\[?"(?:\w+/)?(\w+)"\]?[^#]*#\s*([A-Z][^:(=]*)', line)
            if m:
                out.setdefault(m.group(1), m.group(2).strip())
    return out


NOTED = noted_names()
ARTIFACTS = {"GuardianEye", "IceWand", "TastyBone", "GolemKit", "WonderfulWheat", "RainbowGrass", "SoulLantern"}


ITEM_NAMES = {k.split("/", 1)[1].lower(): v.strip() for k, v in LOC.items() if k.startswith("ItemType/") and "/" not in k[9:]}


def item(ident):
    ident = ident.split("/")[-1]
    for c in (ident, ident.removesuffix("_Steel"), ident.replace("_Steel", "")):
        if c.lower() in ITEM_NAMES:
            return ITEM_NAMES[c.lower()]
    return NOTED.get(ident) or words(ident)


def perk(name):
    return LOC.get(f"ArmorProperties/{name}") or words(name)


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(str(c).replace("|", "/") for c in r) + " |" for r in rows]
    return out + [""]


def toml(name):
    p = ROOT / name
    return tomllib.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


# ---- sources ---------------------------------------------------------------------------------------------------
def stat_changes():
    """[(section, key, old, new)] from `sequel.py diff`."""
    out = subprocess.run([sys.executable, str(ROOT / "tools" / "sequel.py"), "diff"], capture_output=True, text=True,
                         encoding="utf-8", errors="replace").stdout
    rows = []
    for line in out.splitlines():
        m = re.match(r"\[(.+?)\] (.+?): (.+) -> (.+)$", line)
        if m:
            rows.append(m.groups())
    return rows


def gear_rows():
    """{(kind, display name): {field label: (old values, new values)}} for weapons SequelGear.toml changes."""
    out, section = {}, None
    data = defaultdict(lambda: defaultdict(dict))
    for line in (ROOT / "SequelGear.toml").read_text(encoding="utf-8").splitlines():
        m = re.match(r"\[(Melee|Ranged)\.(\w+)\]\s*#\s*(.+?)(?: \((.+?)\))?\s*$", line)
        if m:
            section = (m.group(1), item(m.group(2)) if m.group(2).lower().replace("_steel", "") in ITEM_NAMES else m.group(3).strip())
            continue
        m = re.match(r'"B[Pp]_\w+?Instance\.(.+?)" = ([\d.]+)\s+# default ([\d.]+)', line)
        if m and section:
            field = m.group(1).split(".")[-1]
            variant = re.search(r"\[(\d+)\]", m.group(1))
            data[section][field][int(variant.group(1)) if variant else 0] = (m.group(3), m.group(2))
    for section, fields in data.items():
        changed = {}
        for field, variants in fields.items():
            if any(float(o) != float(n) for o, n in variants.values()):
                order = sorted(variants)
                changed[GEAR_FIELDS.get(field, words(field))] = ("/".join(num(variants[v][0]) for v in order),
                                                                 "/".join(num(variants[v][1]) for v in order))
        if changed:
            out[section] = changed
    return out


def launcher_lines():
    """What the launcher's last log says it changed: built-ins, perks, artifacts."""
    log = ROOT / "launcher.log"
    builtins, perks, artifacts = defaultdict(list), defaultdict(list), defaultdict(list)
    if not log.exists():
        return builtins, perks, artifacts
    for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"\s+((?:MeleeWeapons|RangedWeapons|Armor)/\w+): (\w+) (\d) -> (\w+) (\d)$", line)
        if m:
            builtins[m.group(1)].append((m.group(2), m.group(3), m.group(4), m.group(5)))
            continue
        m = re.match(r"\s+((?:MeleeWeapons|RangedWeapons|Armor)/\w+): added ((?:\w+ \d(?:, )?)+)$", line)
        if m:
            builtins[m.group(1)] += [(None, None, n, lv) for n, lv in re.findall(r"(\w+) (\d)", m.group(2))]
            continue
        m = re.match(r"\s+(Armor/\w+): added (\w+)$", line)
        if m:
            perks[m.group(1)].append(m.group(2))
            continue
        m = re.match(r"\s+(\w+): (cooldown|souls|duration) ([\d.]+) -> ([\d.]+)$", line)
        if m:
            artifacts[m.group(1)].append((m.group(2), m.group(3), m.group(4)))
    return builtins, perks, artifacts


# ---- the sheet -------------------------------------------------------------------------------------------------
def build():
    names = sequel.display_names()
    stats = stat_changes()
    builtins, perks, artifacts = launcher_lines()
    bonus, endless, tests = toml("Bonus.toml"), toml("Endless.toml"), []
    L = [f"# Sequel Mod - every change", "",
         f"Minecraft Dungeons, base game -> mod. Generated {date.today().isoformat()} from the mod's own settings.", "",
         "Install (Steam version on Windows): unpack the mod's zip into the game folder (Steam: right-click Minecraft Dungeons > "
         "Manage > Browse local files) and start the game with \"Play Sequel Mod.bat\" there, keeping its window open. "
         "Nothing else to install. In multiplayer everyone needs the mod.", "",
         "Contents: 1 Enchantments - 2 Weapons - 3 Unique items' built-in enchantments - 4 Armor perks - 5 Artifacts - "
         "6 Endless Apocalypse - 7 Mobs - 8 Seasonal items - 9 Player, merchants and camp - 10 Changed texts", ""]

    # 1 enchantments
    groups = defaultdict(list)
    for section, key, old, new in stats:
        if not section.startswith("Enchantments."):
            continue
        folder = section.split(".", 1)[1]
        if key in TESTS:
            tests.append(f"{words(key.split('.')[-1])} ({folder}): {num(new)} for the test"
                         + (f", meant to be {TESTS[key]}" if TESTS[key] else ", the game's own value otherwise"))
            if TESTS[key] is None:
                continue
            new = TESTS[key]
        bp, prop = key.split(".", 1) if "." in key else ("", key)
        hint = bp.removeprefix("BP_").removesuffix("Instance")
        setting = words(prop) + (f" ({words(hint)})" if hint.lower() not in (folder.lower(), "") and not folder.startswith("Perk") else "")
        if folder.startswith("Perk"):
            groups["Armor perks"].append((perk(folder.removeprefix("Perk").removesuffix("GameplayEffect")), setting, num(old), num(new)))
        elif folder in ARTIFACTS:
            groups["Artifacts"].append((item(folder), setting, num(old), num(new)))
        else:
            name, cat = names.get(folder.lower(), (ench(folder), "Other"))
            groups[cat].append((name, setting, num(old), num(new)))
    L += ["## 1. Enchantments", ""]
    for cat in ("Melee", "Ranged", "Armor", "Other"):
        if groups[cat]:
            L += [f"### {cat}", ""] + table(["Enchantment", "Setting", "Base game", "Mod"], sorted(groups[cat]))
    formulas = toml("Formulas.toml")
    rows = [(ench(n), " / ".join(num(v) for v in formula_patch.KNOWN[n][2]), " / ".join(num(v) for v in vals))
            for n, vals in formulas.items() if n in formula_patch.KNOWN]
    gap = toml("Echo.toml").get("tier3_gap")
    if gap is not None:
        rows.append(("Echo (seconds between repeats)", "5 / 4 / 3", " / ".join(num(gap + k) for k in (2, 1, 0))))
    L += ["### Values per tier (I / II / III)", ""] + table(["Enchantment", "Base game", "Mod"], rows)
    limit = toml("Accelerate.toml").get("speed_limit")
    if limit and abs(limit - 2.0) > 1e-6:
        L += [f"Accelerate: its attack speed tops out at +{num((limit - 1) * 100)}% (base game +100%).", ""]
    notes = toml("StackNotes.toml")
    if notes:
        L += ["### Several copies of one enchantment on an item", "",
              "A built-in copy plus a chosen one, or the same pick in more than one slot. Tried in game; anything not listed is untried.", ""]
        rows = [("Adds up", ", ".join(sorted({ench(n) for n in notes.get("full", [])})))]
        rows += [("Adds up in part", "; ".join(f"{ench(n)} ({t})" if t else ench(n) for n, t in notes.get("partly", {}).items()))]
        seen, none = set(), []
        for n, t in notes.get("none", {}).items():
            if ench(n) not in seen:
                seen.add(ench(n))
                none.append(f"{ench(n)} ({t})" if t else ench(n))
        rows += [("No gain", "; ".join(none))]
        L += table(["Result", "Enchantments"], rows)
    rolls = toml("Stack.toml").get("stackable", [])
    if isinstance(rolls, list) and rolls:
        L += ["These can also roll in more than one slot of the same item (base game: only Sharpness, Smiting, Fire Aspect, "
              "Leeching, Rampaging, Radiance, Chains, Looting, Prospector, Cool Down, Thorns and Knockback): "
              + ", ".join(sorted({ench(n) for n in rolls})) + ".", ""]

    # 2 weapons
    gear = gear_rows()
    L += ["## 2. Weapons", ""]
    for kind in ("Melee", "Ranged"):
        rows = [(name, label, old, new) for (k, name), fields in sorted(gear.items()) if k == kind
                for label, (old, new) in fields.items()]
        L += [f"### {kind}", "", "Several numbers = the hits of the combo in order.", ""] if kind == "Melee" else [f"### {kind}", ""]
        L += table(["Weapon", "Setting", "Base game", "Mod"], rows)
    L += ["The power / speed / area / ammo bars on the item cards follow these numbers.", ""]

    # 3 built-ins
    rows = []
    for ident, changes in builtins.items():
        before = ", ".join(f"{ench(o)} {lv}" for o, lv, _, _ in changes if o) or "-"
        after = ", ".join(f"{ench(n)} {lv}" for o, _, n, lv in changes if (ident, n) not in TEST_BUILTINS)
        if any((ident, n) in TEST_BUILTINS for _, _, n, _ in changes):
            tests.append(f"{item(ident)}: extra built-in " + ", ".join(f"{ench(n)} {lv}" for _, _, n, lv in changes if (ident, n) in TEST_BUILTINS))
        if after:
            rows.append((item(ident), ident.split("/")[0].replace("Weapons", ""), before, after))
    L += ["## 3. Unique items: built-in enchantments", "",
          "Base game = the built-ins that were changed; Mod = what the item has instead (new ones included).", ""]
    L += table(["Item", "Type", "Base game", "Mod"], sorted(rows, key=lambda r: (r[1], r[0])))

    # 4 armor perks
    L += ["## 4. Armor: extra perks", ""]
    L += table(["Armor", "Added perk"], sorted((item(a), ", ".join(perk(p) for p in ps)) for a, ps in perks.items()))

    # 5 artifacts
    L += ["## 5. Artifacts", ""]
    rows = [(item(a), words(f), o, n) for a, cs in artifacts.items() for f, o, n in cs]
    L += table(["Artifact", "Setting", "Base game", "Mod"], sorted(rows + groups["Artifacts"]))
    scale = toml("ArtifactScaling.toml")
    if scale:
        L += [f"Above power {scale['cap'] - 1} artifacts keep gaining: damage up to x{num(scale['damage_at_top'])} and healing up to "
              f"x{num(scale['heal_at_top'])} at power {scale['top_power']}.", ""]
    if groups["Armor perks"]:
        L += ["### Armor perk values", ""] + table(["Perk", "Setting", "Base game", "Mod"], sorted(groups["Armor perks"]))

    # 6 endless
    L += ["## 6. Endless Apocalypse (Apocalypse +26 to +100)", ""]
    power, natural = endless.get("power", {}), endless.get(endless.get("profile", "natural"), {})
    L += [f"- Apocalypse Plus goes to +100 (base game: +25). A+1-25 are unchanged.",
          f"- Gear power: about 254 at A+25, the gear strength cap (315) at A+{power.get('cap_level')}, then 1 more per level up to "
          f"{power.get('top_power')} at A+100. Above 315 gear gets no stronger by itself; the levels unlock the rewards below.", ""]
    rows = []
    for row, spec in natural.items():
        if isinstance(spec, list):
            text = "; ".join(f"{num(v)} at A+{lv}" for lv, v in spec)
        elif isinstance(spec, dict):
            text = f"from A+{spec.get('from')}, rising to {num(spec.get('to'))} at A+99"
        elif spec == "grow":
            text = "keeps rising at its A+1-25 pace"
        elif spec == "freeze":
            text = "stays at its A+25 value"
        else:
            text = f"rising to {num(spec)} at A+99"
        if f"EndlessStruggle.{row}.MaxValue" in TESTS:
            text += " (raised for a test at the moment)"
        rows.append((words(row), text))
    L += ["### Level modifiers past A+25", ""] + table(["Modifier", "Value"], rows)
    L += [f"A+100 itself: " + ", ".join(f"{words(k)} {num(v)}" for k, v in endless.get("finale", {}).items()) + ".", ""]
    rows = []
    for t in endless.get("trial", []):
        first = t["level"] - t.get("levels", 1) + 1
        what = ", ".join(f"{words(k)} x{num(v)} of its A+100 value" for k, v in t.items()
                         if k not in ("level", "levels", "name", "LootQualityBoost", "XPMultiplier"))
        rows.append((f"A+{first}" + (f"-{t['level']}" if first != t["level"] else ""), t.get("name", ""), what))
    L += ["### Trials", ""] + table(["Levels", "Trial", "Raised"], rows)
    settings = endless_patch.unlock_settings()
    tops = settings.get("tops") or []
    if settings.get("staged") and tops:
        needs = [25] + tops[:-1]
        counts = endless_patch.boss_counts(needs, settings)
        L += ["### Unlocking", "", "Different boss missions to clear on the level in the first column.", ""]
        L += table(["Clear on", "Boss missions", "Opens"],
                   [(f"A+{n}", c, f"A+{n + 1}" + (f"-{t}" if t != n + 1 else "")) for n, t, c in zip(needs, tops, counts)])
    th = bonus.get("thresholds", {})
    L += ["### Rewards above the gear cap", "",
          f"- Bonus built-in enchantments: from power {th.get('cap')}, every {th.get('step')} power adds one tier - first the item's own "
          f"built-ins rise to tier 3, then bonus enchantments from its list below, each up to tier 3. An item gets as many "
          f"bonuses as bring it to {th.get('total', 4)} enchantments beyond its family's plain item: three for a unique with one "
          f"enchantment of its own, two for one with two (a plain item gets three)."
          + (f" At power {th.get('final')} everything is tier 3 and weapons get one more" if th.get("final") else "")
          + ("".join(f"{', ' if i else ': '}{ench(n)} for every {k} weapon" for i, (k, n) in enumerate(bonus.get("final_extra", {}).items()))
             + ", the next name of its list for the others." if th.get("final") and bonus.get("final_extra") else "." if th.get("final") else ""),
          "- An item type's bonuses follow its best copy; weaker copies of the same item get them too.",
          "- Enchantments the item already has are skipped, unless the list says second copy; the last entry of a list is a spare for that."]
    ld = bonus.get("ladder", {})
    if ld.get("step") and th.get("final"):
        L += [f"- Past power {th.get('final')}: every {ld['step']} power adds one tier of "
              + ", ".join(f"{ench(ld[k])} ({k})" for k in ("melee", "ranged", "armor") if ld.get(k))
              + " as new lines under the other enchantments (I, II, III, then another line)."
              + (f" Drops at power {th.get('final')} or more come in {ld['climb'][0]}-{ld['climb'][1]} above your power level, so the number keeps climbing." if ld.get("climb") else "")]
    ap = bonus.get("armor_perks", {})
    if ap:
        L += [f"- Armor: one more perk at power {', '.join(str(x) for x in ap.get('levels', []))} - the first perks of its list below that it doesn't have yet."]
    early = th.get("early", [])
    if early:
        L += [f"- A taste earlier: a unique's own built-in enchantments rise one tier at power {' and '.join(str(x) for x in early)} "
              "(about A+1 and A+20); bonus enchantments still start past the cap."]
    g = bonus.get("gilded", {})
    if g:
        if g.get("early_from"):
            L += [f"- New drops of power {g['early_from']} to {g.get('from_power')} have a {num(g.get('early_chance', 0) * 100)}% chance to be gilded."]
        L += [f"- New drops of power {g.get('from_power')} or more have a {num(g.get('chance', 0) * 100)}% chance to be gilded "
              f"(tier I / II / III: {' / '.join(num(c * 100) + '%' for c in g.get('tier_chances', []))})."]
    if bonus.get("merchants", {}).get("follow_power"):
        L += ["- Merchant stock follows your gear power above the base game's ceiling."]
    L += [""]
    for kind, title in (("melee", "Bonus enchantments: melee"), ("ranged", "Bonus enchantments: ranged"), ("armor", "Bonus enchantments: armor")):
        rows = [("Any other" if k == "all" else item(k), ", ".join(ench(n) for n in v)) for k, v in bonus.get(kind, {}).items() if isinstance(v, list)]
        L += [f"### {title}", ""] + table(["Item or family", "In this order"], sorted(set(rows)))
    rows = [("Any other" if k == "all" else item(k), ", ".join(perk(n) for n in v)) for k, v in ap.items() if isinstance(v, list) and k != "levels"]
    L += ["### Extra armor perks above the gear cap", ""] + table(["Armor", "In this order"], sorted(set(rows)))

    # 7 mobs
    pool, mobs = toml("MobPool.toml"), toml("MobEnchants.toml")
    L += ["## 7. Mobs", ""]
    ancient = {"Committed", "Cowardice", "Echo", "FuseShot", "Huge", "Leeching", "Rampaging", "Sharpness", "Shockwave",
               "Swirling", "Thundering"}   # ancient mobs only in the base game (MobPool.toml)
    rolls = pool.get("pool", {})
    removed = [n for n, on in rolls.items() if on is False and n not in ancient] + pool.get("remove", [])
    added = [n for n, on in rolls.items() if on is True and n in ancient] + pool.get("add", [])
    if removed:
        L += ["- Enchanted mobs no longer roll: " + ", ".join(ench(n) for n in removed) + "."]
    if added:
        L += ["- Enchanted mobs can now also roll: " + ", ".join(ench(n) for n in added) + "."]
    if "Deflecting" in mobs:
        L += ["- Deflect is switched off on every mob that carries it (ancient mobs and the Tower Guard included). The player's Deflect is unchanged."]
    if "Levitation" in mobs:
        L += ["- Levitation Shot from mobs does nothing."]
    for section, key, old, new in stats:
        if key.endswith("Mob") and "Thorns" in key:
            L += [f"- Thorns on mobs: damage returned {num(old)} -> {num(new)}."]
    L += [""]

    # 8 seasonal
    drops = toml("Drops.toml")
    L += ["## 8. Seasonal items", "",
          "These event items drop in missions like the other uniques of their family (base game: Tower or past events only). "
          "Their built-in enchantments are in section 3.", ""]
    L += table(["Item", "Family"], sorted((item(k), item(v[-1])) for k, v in drops.items()))

    # 9 merchants and other
    prices, qol = toml("Prices.toml"), toml("QoL.toml")
    shops = {"enchantmentmerchant": "Enchantsmith (gold)", "piglinmerchant": "Piglin merchant (gold)", "shopkeeper": "Village merchant",
             "luxurymerchant": "Luxury merchant", "mysterymerchant": "Mystery merchant", "blacksmith": "Blacksmith", "giftwrapper": "Gift wrapper"}
    L += ["## 9. Player, merchants and camp", ""]
    import player
    labels = {"speed_after_roll": "Speed kept right after a roll", "walk_speed": "Walking speed"}
    L += [f"- {labels.get(k, k)}: {num(old)} -> {num(new)}." for k, old, new in player.changes(sequel.EXTRACT, ROOT / "Player.toml")]
    L += [f"- {shops.get(k, k)}: prices x{num(v)}." for k, v in prices.items()]
    st = qol.get("start", {})
    start = st.get("start", "apocalypse" if st.get("apocalypse") else "off")
    if start in ("apocalypse", "adventure"):
        kp = st.get("kit_power", 70)
        kp = kp.get(start, 70) if isinstance(kp, dict) else kp
        L += [f"- Start in {start.title()}: a character that hasn't reached it gets {start.title()} unlocked, and a starter kit at power "
              f"{num(kp)} ({', '.join(item(k) for k in st.get('kit', []))}) if its gear is weaker"
              + (lambda lv: f", and starts at level {lv} ({lv - 1} enchantment points) if lower" if lv > 1 else "")(
                  int((st.get('start_level', {}) or {}).get(start, 1) if isinstance(st.get('start_level'), dict) else st.get('start_level', 1)))
              + " (base game: "
              + ("Default and Adventure first)." if start == "apocalypse" else "Default first).")]
    if qol.get("blacksmith", {}).get("missions") is not None:
        n = qol["blacksmith"]["missions"]
        L += [f"- Blacksmith: an upgrade takes {n} mission{'s' if n != 1 else ''} (base game: 3)."]
    if bonus.get("blacksmith", {}).get("match_power"):
        L += ["- Blacksmith: an upgraded weapon or armor comes back at least at your power level (the game's own result stops near A+25 power)."]
    L += [""]

    # 10 text
    import stack_text
    closing = tuple(stack_text.SENTENCE.values())
    rows, marked = [], 0
    for section, key, old, new in stats:
        if not section.startswith("text"):
            continue
        old, new = old.strip("'\""), new.strip("'\"")
        for sentence in closing:
            if new.endswith(sentence):
                new, marked = new[:-len(sentence)].rstrip(), marked + 1
        if new != old:
            rows.append((key, old, new))
    if rows or marked:
        L += ["## 10. Changed texts", ""]
        if marked:
            L += [f"The descriptions of {marked} enchantments whose copies don't add up end with "
                  + " or ".join(f'"{c}"' for c in closing) + " (see section 1).", ""]
        L += table(["Text", "Base game", "Mod"], rows)

    # tests
    for section, key, old, new in stats:
        if section.startswith("Difficulty") and key in TESTS:
            tests.append(f"{words(key.split('.')[1])}: {num(new)} for the test (the game's own {num(old)} otherwise)")
    if tests:
        L += ["## Temporary test settings (not part of the mod)", ""] + [f"- {t}" for t in sorted(set(tests))] + [""]
    out = ROOT / "CHANGES.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {out} ({len(L)} lines)")
    return L


if __name__ == "__main__":
    build()
