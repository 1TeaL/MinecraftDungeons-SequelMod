"""Write ENCHANTMENTS.md: every enchantment in the mod, laid out like the Minecraft Wiki's enchantment tables - icon,
name, description, tier values, rarity (cost), mobs, more than one per item, built into, the item card's short line,
and what the mod changed.

    python tools/enchant_sheet.py

Base game values come from the wiki (tools/wiki_enchantments.py -> tools/wiki_enchantments.json; the game works
most tier numbers out in its code). The mod's side is read from its own files where it can be (names and texts from
SequelText.toml, rarity from EnchantGear.toml, mob rolls from MobPool.toml, stacking from Stack.toml, built-ins from
the launcher's last log) and from MOD below for the tier numbers the mod changed - keep MOD in step with the
settings (CHANGES.md lists every raw number).
"""
import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import change_sheet as cs  # noqa: E402  (names, items, the launcher's log)
import settings  # noqa: E402

WIKI = json.loads((ROOT / "tools" / "wiki_enchantments.json").read_text(encoding="utf-8"))
TEXT = tomllib.loads((ROOT / "settings" / "build" / "SequelText.toml").read_text(encoding="utf-8"))["en"]
ICONS = "docs/enchantments"
ART = ROOT / "unreal" / "Art"
YES, NO = "✔", "✖"

# Our enchantments: the game's enchantment whose slot they use (wiki name, internal id) -> what the page shows.
NEW = {
    "Knockback": dict(id="Knockback", name="Sweeping Edge", gear="Melee", tier_text="splash damage", tiers=["20%", "30%", "40%"]),
    "Rushdown": dict(id="Rushdown", name="Shadowcloak", gear="Any", tier_text="chance of Shadow Form on a kill", tiers=["15%", "20%", "25%"]),
    "Lucky Explorer": dict(id="EmeraldDivination", name="Ignite", gear="Any", tier_text="of max health as extra damage", tiers=["3%", "4%", "5%"]),
    "Heals Allies": dict(id="Altruistic", name="Venom Siphon", gear="Any", tier_text="of max health as extra damage", tiers=["3%", "4%", "5%"]),
    "Thrive Under Pressure": dict(id="ThriveUnderPressure", name="Shatter", gear="Any", tier_text="more damage to chilled mobs", tiers=["+100%", "+150%", "+200%"]),
    "Thorns": dict(id="Thorns", name="Overload", gear="Any", tier_text="of max health; mobs it arcs to", tiers=["3%; 3", "4%; 4", "5%; 5"]),
    "Levitation Shot": dict(id="LevitationShot", name="Relentless", gear="Any", tier_text="damage and attack speed per stack (10 stacks)", tiers=["+2%", "+3%", "+4%"]),
    "Barrier": dict(id="Barrier", name="Battle Hardened", gear="Armor", tier_text="damage resistance per stack (10 stacks)", tiers=["1%", "2%", "3%"]),
    "Shielding": dict(id="Shielding", name="Last Stand", gear="Armor", tier_text="less damage below half health", tiers=["20%", "40%", "60%"]),
    "Regeneration": dict(id="Regeneration", name="Buddy Brew", gear="Armor", tier_text="of max health healed (5% a second)", tiers=["10% over 2 s", "20% over 4 s", "30% over 6 s"]),
    "Gravity Pulse": dict(id="GravityPulse", name="Artifact Amplifier", gear="Armor", tier_text="more artifact damage and souls", tiers=["20%", "35%", "50%"]),
    "Recycler": dict(id="Recycler", name="Ancient Alchemy", gear="Armor", tier_text="souls per potion", tiers=["60", "90", "120"]),
    "Food Reserves": dict(id="FoodReserves", name="Bottomless Brew", gear="Armor", tier_text="extra potion drinks", tiers=["1", "2", "3"]),
    "Explorer": dict(id="Explorer", name="Barrier Brew", gear="Armor", tier_text="less damage for 6 s, you and allies", tiers=["30%", "50%", "70%"]),
}
NEW_LINES = {   # the short line an item card shows for a built-in copy (SequelText.toml ItemType/..., or lent keys)
    "Knockback": "Hits splash nearby mobs", "Rushdown": "Chance of Shadow Form on kill",
    "Lucky Explorer": "Extra damage to burning mobs", "Heals Allies": "Drains health from poisoned mobs",
    "Thrive Under Pressure": "Extra damage to chilled mobs", "Thorns": "Lightning charges mobs to discharge",
    "Levitation Shot": "Hits build damage and attack speed", "Barrier": "Hits build damage resistance",
    "Shielding": "Less damage taken at low health", "Regeneration": "Potions heal you and allies over time",
    "Gravity Pulse": "More artifact damage and souls", "Recycler": "Potions grant souls",
    "Food Reserves": "Extra potion drinks", "Explorer": "Potions shield you and allies",
}
NEW_CHANGED = {
    "Knockback": "New, in Knockback's slot (unused in the game).",
    "Rushdown": "New, in Rushdown's slot (it was only on the Tempest Knives, which now have Shadowcloak). Uses kill credit.",
    "Lucky Explorer": "Replaces Lucky Explorer. Arrows count; bosses take 40% of the max-health damage.",
    "Heals Allies": "New, in Heals Allies' slot (unused in the game). Arrows count; you heal 10% of the damage.",
    "Thrive Under Pressure": "New, in Thrive Under Pressure's slot (a unique-only one). Arrows count.",
    "Thorns": "Replaces Thorns. Lightning Focus boosts it; bosses take 40%.",
    "Levitation Shot": "Replaces Levitation Shot. Copies add.",
    "Barrier": "New, in Barrier's slot (unused in the game). Copies add.",
    "Shielding": "New, in Shielding's slot (unused in the game).",
    "Regeneration": "New, in Regeneration's slot (unused in the game). Allies and pets nearby too.",
    "Gravity Pulse": "Replaces Gravity Pulse.",
    "Recycler": "Replaces Recycler.",
    "Food Reserves": "Replaces Food Reserves. Each extra refills after one potion cooldown; Refreshment kills speed it up.",
    "Explorer": "Replaces Explorer.",
}
# The game's enchantments whose tier numbers the mod changed: name -> (tiers, what changed). None = the wiki's tiers.
MOD = {
    "Ambush": (["50%", "100%", "150%"], "+50% damage per tier (game: +20%)."),
    "Artifact Synergy": (["150%", "200%", "250%"], "Bigger bonus."),
    "Busy Bee": (["33%", "67%", "100%"], "Higher chance."),
    "Chains": (None, "45% chance (game: 30%), chains 4 mobs (game: 2)."),
    "Critical Hit": (None, "x5 damage (game: x3)."),
    "Echo": (["2.1", "1.1", "0.1"], "Repeats far sooner."),
    "Exploding": (["15%", "25%", "35%"], "Goes off at once and chains (mobs the blast kills explode too). Uses kill credit. Also rolls on bows."),
    "Fire Aspect": (None, "Arrows set mobs on fire too, and it also rolls on bows. Burning mobs lose 3 / 4 / 5% of their max health every second (bosses 40% of it)."),
    "Freezing": (["-40%", "-55%", "-70%"], "Stronger slow."),
    "Illager's Bane": (["+50%", "+75%", "+100%"], "More damage to illagers."),
    "Leeching": (["4%", "5%", "6%"], "Uses kill credit (fewer % since far more kills count). Kills by your melee attack heal twice. Also rolls on bows."),
    "Pain Cycle": (["Quadruple (4x)", "Sextuple (6x)", "Octuple (8x)"], "Bigger final hit; drains 2% health (game: 3%)."),
    "Poison Cloud": (None, "Always triggers (game: 30%), wider cloud. Poisoned mobs lose 5 / 7.5 / 10% of their max health every second."),
    "Radiance": (None, "Always triggers (game: 20%), heals less per proc."),
    "Rampaging": (["1", "2", "3"], "Every kill of yours (game: 10% chance on a weapon kill): +50% attack speed. Uses kill credit."),
    "Shockwave": (None, "Plus 50 / 75 / 100% of your weapon hit to the mobs it reaches."),
    "Smiting": (["+50%", "+75%", "+100%"], "More damage to the undead."),
    "Stunning": (["15%", "30%", "45%"], "Higher chance."),
    "Swirling": (None, "Plus 50 / 75 / 100% of your weapon hit to the mobs it reaches."),
    "Thundering": (None, "Strikes on every hit (game: 30%), less flat damage, plus 1 / 2 / 3% of max health per strike. Lightning Focus boosts it."),
    "Guarding Strike": (["3", "4", "5"], "Any kill of yours counts (kill credit), not only weapon kills."),
    "Refreshment": (None, "Uses kill credit; melee kills also trigger the game's own Refreshment. Speeds up Bottomless Brew's extras too."),
    "Bonus Shot": (["30%", "50%", "75%"], "Much stronger second arrow."),
    "Dipping Poison": (["10", "15", "20"], "More arrows. Poisoned mobs lose 5 / 7.5 / 10% of their max health every second."),
    "Enigma Resonator": (["0-30%", "0-40%", "0-50%"], "Higher chance."),
    "Fuse Shot": (None, "Explodes almost at once (game: after 1 s), 2x damage, 1.5x radius."),
    "Growing": (None, "Reaches full damage sooner (10 blocks instead of 16)."),
    "Punch": (["700%", "1100%", "1500%"], "Much stronger knockback."),
    "Radiance Shot": (None, "Always triggers (game: 50%), heals less per proc."),
    "Rapid Fire": (["+20%", "+35%", "+50%"], "Faster shooting."),
    "Shock Web": (None, "Mobs a beam touches lose 1 / 2 / 3% of their max health (at most twice a second; bosses 40%) and are charged for Overload. Lightning Focus boosts it. Flat damage back to the game's."),
    "Bag of Souls": (["100%", "200%", "300%"], "More souls."),
    "Beast Boss": (["50% increase", "100% increase", "150% increase"], "More pet damage."),
    "Beast Surge": (None, "Lasts 20 s (game: 10 s)."),
    "Burning": (None, "Wider (4 blocks, game: 3). Burning mobs lose 3 / 4 / 5% of their max health every second."),
    "Cowardice": (["+40%", "+50%", "+60%"], "More damage at full health."),
    "Electrified": (None, "Its zap also takes 4 / 6 / 8% of max health. Lightning Focus boosts it."),
    "Final Shout": (["8th", "6th", "4th"], "Triggers below 50% health (game: 25%), more often."),
    "Fire Focus": (["+50%", "+100%", "+150%"], "Bigger boost."),
    "Fire Trail": (None, "Lasts 6 s (game: 4 s). Burning mobs lose 3 / 4 / 5% of their max health every second."),
    "Frenzied": (["+40%", "+50%", "+60%"], "Faster attacks at low health."),
    "Life Boost": (["20%", "40%", "60%"], "More health."),
    "Lightning Focus": (None, "Also boosts Thundering's, Electrified's and Overload's max-health damage."),
    "Luck of the Sea": (["25%", "50%", "75%"], "More luck."),
    "Poison Focus": (["+50%", "+100%", "+150%"], "Bigger boost."),
    "Protection": (["-15%", "-25%", "-35%"], "Less damage taken."),
    "Reckless": (["+100%", "+125%", "+150%"], "More damage."),
    "Rush": (["50%", "100%", "150%"], "Faster."),
    "Snowball": (["3", "2", "1"], "Throws more often."),
    "Soul Speed": (None, "Double speed bonus."),
    "Speed Synergy": (None, "+50% speed (game: +20%)."),
    "Swiftfooted": (None, "Lasts 5 s (game: 3 s)."),
    "Shadow Blast": (None, "Triple damage."),
    "Soul Siphon": (None, "40% chance (game: 20%)."),
    "Health Synergy": (["5%", "7.5%", "10%"], "Bigger heal."),
    "Beast Burst": (["2X", "4X", "6X"], "Double damage."),
    "Deflect": (["30%", "40%", "50%"], "Higher chance."),
    "Supercharge": (["+40%", "+60%", "+80%"], "Bigger charged shots."),
    "Wild Rage": (["30%", "45%", "60%"], "Higher chance."),
    "Soul Focus": (["+25%", "+50%", "+75%"], "Like the other Focuses (game: +10 / 20 / 30%)."),
    "Burst Bowstring": (None, "Also rolls on armor."),
}
COST = {"Common": "1 / 2 / 3", "Powerful": "2 / 3 / 4"}


def icon_file(row):
    return re.sub(r"[^A-Za-z0-9]+", "_", Path(row["icon"]).stem).strip("_") + ".png"


def img(file, alt):
    return f'<img src="{ICONS}/{file}" width="40" alt="{alt}">'


def cell(text):
    return str(text).replace("|", "/").replace("\n", " ")


def desc_overrides():
    """base name -> the mod's description: whole new texts as they are; for texts that keep the game's {0}, only the
    sentences the mod added (to put after the wiki's own description)."""
    out = {}
    for key, value in TEXT.items():
        m = re.match(r"Enchantment/(\w+?)(?:_effect)?_desc$", key)
        if not m:
            continue
        base = cs.LOC.get(f"Enchantment/{m.group(1)}")
        if not base:
            continue
        if "{" in value:
            original = cs.LOC.get(key, "")
            extra = value[len(original):].strip() if value.startswith(original) else ""
            out[base] = ("add", extra)
        else:
            out[base] = ("whole", value)
    return out


def built_ins():
    """base enchantment name -> {item name: level or None}: the wiki's (base game) list with the launcher's changes."""
    out = {row["name"]: {i: None for i in row["built_into"]} for row in WIKI}
    changes, _, _ = cs.launcher_lines()
    for ident, rows in changes.items():
        name = cs.item(ident)
        for old, _, new, level in rows:
            for gone in [cs.ench(old)] if old and old != new else []:
                for i in [i for i in out.setdefault(gone, {}) if i.lower() == name.lower()]:
                    out[gone].pop(i)
            items = out.setdefault(cs.ench(new), {})
            for i in [i for i in items if i.lower() == name.lower()]:   # the wiki's spelling may differ in case
                items.pop(i)
            items[name] = level
    return out


def main():
    gear = settings.load(settings.path("EnchantGear.toml"))
    powerful = {cs.ench(n) for n in gear.get("rarity", {}).get("powerful", [])}
    common = {cs.ench(n) for n in gear.get("rarity", {}).get("common", [])}
    mobs = settings.load(settings.path("MobPool.toml"))
    mob_off = {cs.ench(k) for k, v in mobs.items() if v is False}
    mob_on = {cs.ench(k) for k, v in mobs.items() if v is True}
    stack_cfg = settings.load(settings.path("Stack.toml"))
    # what may roll in more than one slot: the game's own repeats (stack_patch.py's list) + Stack.toml, minus `once`
    game_repeats = {"Sharpness", "Smiting", "Looting", "Prospector", "Chains", "FireAspect", "Leeching", "Rampaging",
                    "RadianceMelee", "Celerity", "Thorns", "Knockback"}
    multi = {cs.ench(n) for n in (game_repeats | set(stack_cfg.get("stackable", []))) - set(stack_cfg.get("once", []))}
    descs = desc_overrides()
    builts = built_ins()
    notes = tomllib.loads((ROOT / "settings" / "build" / "StackNotes.toml").read_text(encoding="utf-8"))
    stacks = {cs.ench(n): YES for n in notes.get("full", [])}
    stacks.update({cs.ench(n): f"partly: {why}" if why else "partly" for n, why in notes.get("partly", {}).items()})
    stacks.update({cs.ench(n): f"{NO} ({why})" if why else NO for n, why in notes.get("none", {}).items()})

    def rarity(name, wiki_rarity):
        r = "Powerful" if name in powerful else "Common" if name in common else wiki_rarity
        return f"{r} ({COST.get(r, '?')})" if r in COST else r

    def built_cell(name):
        items = builts.get(name, {})
        return "<br>".join(f"{i} {lv}" if lv else i for i, lv in sorted(items.items())) or "None"

    L = ["# Sequel Mod - enchantments", "",
         "Every enchantment, laid out like the [Minecraft Wiki's enchantment page](https://minecraft.wiki/w/Dungeons:Enchantment). "
         "Base game numbers come from the wiki; where the mod changes a number the mod's is shown, and **What changed** "
         "says how. Every raw number is in [CHANGES.md](CHANGES.md). Icons: the game's, from the wiki; the new "
         "enchantments' icons are the mod's own.", "",
         "**Enchantment points per tier (I / II / III):** Common 1 / 2 / 3, Powerful 2 / 3 / 4; gilded (a free built-in "
         "on gilded gear) one more each. **Repeats** = can roll in more than one slot of the same item (the game's own "
         "repeats, plus the mod's stacking builds; utility picks roll once per item so items don't fill up with "
         "repeats). Copies of most enchantments add up however they come - built in, gilded, bonus or picked; "
         "see **Stacks**. **Mobs** = "
         "enchanted mobs can roll it. **Stacks** = whether two copies on one item add up (tested in game by the user, "
         "2026-10; the new enchantments by how they are built; ? = not tried). **Short line** = what an item card "
         "shows under the item for a built-in copy.", ""]
    head = ["Icon", "Name", "Description", "Tier text", "I", "II", "III", "Rarity (points)", "Mobs", "Stacks", "Repeats",
            "Built into", "Short line", "What changed"]

    # our new enchantments first
    L += ["## New enchantments", "",
          "Each one takes over the slot of a weak or unused game enchantment (the mod changes no game code). "
          "**Gear** = what it rolls on.", ""]
    rows = []
    for base, n in sorted(NEW.items(), key=lambda kv: kv[1]["name"]):   # alphabetical (user, 2026-11-09)
        w = next(r for r in WIKI if r["name"] == base)
        art = ART / f"T_{n['id']}_Icon.png"
        icon = img(f"New_{n['name'].replace(' ', '_')}.png" if art.exists() else icon_file(w), n["name"])
        rows.append([icon, f"**{n['name']}**<br>({n['gear']})", cell(descs.get(base, ("whole", ""))[1]), n["tier_text"],
                     *n["tiers"], rarity(base, w["rarity"]), NO, stacks.get(base, "?"), YES if base in multi else NO,
                     built_cell(base), NEW_LINES[base], NEW_CHANGED[base]])
    L += cs.table(head, rows)

    shown = set(NEW)
    for section in ("Melee", "Ranged", "Armor", "Exclusive"):
        rows = []
        for w in WIKI:
            if w["section"] != section or w["name"] in shown:
                continue
            tiers, changed = MOD.get(w["name"], (None, ""))
            how, extra = descs.get(w["name"], ("add", ""))
            desc = extra if how == "whole" else " ".join(filter(None, [w["description"][0] if w["description"] else "", extra]))
            mob = NO if w["name"] in mob_off else YES if (w["name"] in mob_on or w["mobs"] == YES) else NO
            many = YES if w["name"] in multi else NO
            tiers = [t or "-" for t in (tiers or w["tiers"])]
            rows.append([img(icon_file(w), w["name"]), w["name"], cell(desc), cell(w["tier_text"]) or "-", *tiers,
                         rarity(w["name"], w["rarity"]).replace("Unknown", "-"), mob, stacks.get(w["name"], "?"), many,
                         built_cell(w["name"]),
                         cell(w["gilded"]) or "-", changed])
        title = {"Exclusive": "Unique-only (built into one item, never rolled)"}.get(section, section)
        L += [f"## {title}", ""] + cs.table(head, rows)

    L += ["Frost Shot (Freezing Ranged) and Wither are left out: the game gave them no card text, so the mod doesn't "
          "roll them (see the README).", ""]
    out = ROOT / "ENCHANTMENTS.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {out} ({len(L)} lines)")


if __name__ == "__main__":
    main()
