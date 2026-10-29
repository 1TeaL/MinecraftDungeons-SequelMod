"""Bonus built-in enchantments for gear above the power cap, kept up to date while the game runs (Bonus.toml).
Data only: reads the player's items, writes item definitions' built-in lists. No game code is changed.

    python tools/bonus_watch.py            # watch the running game until it closes
    python tools/bonus_watch.py --once     # one pass: print what each held item type gets, apply it

How it works
- Every item the game holds (inventory, equipped, storage) is an object with one vtable (exe+0x346FCF8):
  its type is an FName at +0x34, its stored power a float at +0x3C. Shown power = (stored - 1) * 10 + 1.
- An item definition (builtins_patch.py) starts with that same FName, so type -> definition is a lookup.
- For each item type the best copy's power decides the number of upgrade steps (Bonus.toml [thresholds]):
  first the type's own built-ins rise to tier 3 one tier per step, then its bonus enchantments one tier at a
  time. Copies of one enchantment all fire, so a bonus adds to the same enchantment picked by the player. The definition's built-in list is rebuilt to match, and put back when no copy qualifies any more.
- Armor above the cap also earns extra perks at set power levels ([armor_perks]). A perk is stored on the single
  armor (a list at +0x50 of the item object, 2 bytes per perk, room for 8), so this is exact per item and the game
  saves it with the item. Perks are only ever added.
- The objects are found by live_objects.py (whole heap every half minute, known pages in between).
"""
import hashlib
import json
import os
import re
import struct
import sys
import time
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import builtins_patch as bp  # noqa: E402
import perks_patch as pp  # noqa: E402
from aplus_patch import open_game, pid_of  # noqa: E402
from live_objects import Scanner  # noqa: E402
from memprobe import read  # noqa: E402
import settings  # noqa: E402

CONFIG = settings.path("Bonus.toml")
ITEM_VTABLE = 0x346FCF8
ITEM_TYPE, ITEM_POWER, ITEM_PERKS = 0x34, 0x3C, 0x50
BASE_ITEM = 0x228             # an item definition's plain item (tools/drops_patch.py)
ITEM_GILDED = 0x88            # int flag; then the enchantment: id byte +0x8C, tier int +0x90, bytes 00 03 at +0x94
MAX_TIER, MAX_ENTRIES = 3, 16    # entries: our own buffer's room (the game reads the count) - 16 since the A+100 ladder
POOLS = json.loads((Path(__file__).resolve().parent / "enchant_pools.json").read_text())   # rollable, by gear type
SECTIONS = {"MeleeWeapons": "melee", "RangedWeapons": "ranged", "Armor": "armor"}


def saved_items():
    """{(item id in lower case, power as 4 float bytes)} of every item in the character saves, or None if they
    can't be read. These are the items the player had before this session: only others count as new drops."""
    try:
        import savefile
        root = save_folder()
        seen = set()

        def walk(node):
            if isinstance(node, dict):
                if isinstance(node.get("type"), str) and isinstance(node.get("power"), (int, float)):
                    seen.add((node["type"].lower(), struct.pack("<f", node["power"])))
                for v in node.values():
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)
        files = list(root.glob("*/Characters/*.dat"))
        for f in files:
            walk(json.loads(savefile.decrypt(f.read_bytes())))
        return seen if files else None
    except Exception:  # noqa: BLE001 - no key, unknown format...: then nothing is gilded
        return None


def saved_best():
    """{registry name: best shown power} of the gear the character played last owns (inventory, equipped and
    storage chest), from its save; {} if it can't be read. Lets the launcher give an item type its bonuses before
    the character is loaded: a built-in only reaches a weapon when it is equipped, so bonuses written after the
    camp has loaded would be missing from the equipped gear until the next level."""
    try:
        import savefile
        files = sorted(save_folder().glob("*/Characters/*.dat"), key=lambda f: f.stat().st_mtime)
        data = json.loads(savefile.decrypt(files[-1].read_bytes()))
        by_id = {name.split("/")[1].lower(): name for name in bp.REGISTRY}
        best = {}
        for item in (data.get("items") or []) + (data.get("storageChestItems") or []):
            name = by_id.get(str(item.get("type", "")).lower())
            power = item.get("power")
            if name and isinstance(power, (int, float)) and 1.0 <= power < 60.0:
                best[name] = max(best.get(name, 0), int((power - 1) * 10 + 1 + 1e-3))
        return best
    except Exception:  # noqa: BLE001 - no save yet, no key, unknown format
        return {}


def upgraded_items():
    """(power level of the character played last, {(item id in lower case, power as 4 float bytes)} of its items the
    Blacksmith has upgraded, the save's change time), or None if the save can't be read."""
    try:
        import savefile
        files = sorted(save_folder().glob("*/Characters/*.dat"), key=lambda f: f.stat().st_mtime)
        if not files:
            return None
        data = json.loads(savefile.decrypt(files[-1].read_bytes()))
        done = {(item["type"].lower(), struct.pack("<f", item["power"]))
                for item in (data.get("items") or []) + (data.get("storageChestItems") or [])
                if item.get("upgraded") and isinstance(item.get("type"), str) and isinstance(item.get("power"), (int, float))}
        return int(data.get("totalGearPower", 0)), done, files[-1].stat().st_mtime
    except Exception:  # noqa: BLE001
        return None


SHOPS = ("VillageMerchantDef", "LuxuryMerchantDef", "PiglinMerchantDef")   # merchants that sell gear


def save_folder():
    return Path(os.environ["USERPROFILE"]) / "Saved Games" / "Mojang Studios" / "Dungeons"


def merchant_stock():
    """(power level of the character played last, {(item id in lower case, power as 4 float bytes)} of the stock
    of all its merchants, the save's change time), or None if the save can't be read."""
    try:
        import savefile
        files = sorted(save_folder().glob("*/Characters/*.dat"), key=lambda f: f.stat().st_mtime)
        if not files:
            return None
        data = json.loads(savefile.decrypt(files[-1].read_bytes()))
        stock = set()
        for key, merchant in data.get("merchantData", {}).items():
            if not any(shop in key for shop in SHOPS):   # not the Blacksmith's or Gift Wrapper's slot: that is
                continue                                 # the player's own item, nor Tower rewards
            for slot in (merchant.get("slots") or {}).values():
                item = (slot or {}).get("item") or {}
                if isinstance(item.get("type"), str) and isinstance(item.get("power"), (int, float)):
                    stock.add((item["type"].lower(), struct.pack("<f", item["power"])))
        return int(data.get("totalGearPower", 0)), stock, files[-1].stat().st_mtime
    except Exception:  # noqa: BLE001
        return None


HOLD_SECONDS = 90     # how long an item type's best copy must stay lower before bonuses are taken away


class Watch:
    def __init__(self, h, base, scanner=None):
        self.h, self.base = h, base
        self.own_scanner = scanner is None      # the launcher shares one scanner between its watchers
        self.scanner = scanner or Scanner(h, base)
        self.item_vt = self.scanner.register(ITEM_VTABLE) if base else 0
        self.cfg = settings.load(CONFIG)
        self.cap, self.step = self.cfg["thresholds"]["cap"], self.cfg["thresholds"]["step"]
        self.final = self.cfg["thresholds"].get("final", 0)
        self.early = self.cfg["thresholds"].get("early", [])   # power levels below the cap that give a step too
        self.total = self.cfg["thresholds"].get("total", 4)    # enchantments beyond the plain item's, bonuses included
        self.final_extra = self.cfg.get("final_extra", {})     # section -> the A+100 extra every item of it gets
        self.ladder = self.cfg.get("ladder", {})               # past `final`: one more tier every `step` power
        self.climbed = set()                                   # (id, power bytes) of drops the ladder raised...
        self.shelf = set()                                     # ...and of merchant wares, which it leaves alone
        self._slots = {}
        self.types = {}        # FName id -> registry name (ids differ every session)
        self.original = {}     # registry name -> [(type_id, level)] as the launcher left them
        self.buffers = {}      # registry name -> address of our rebuilt list
        self.applied = {}      # registry name -> list currently written
        self.applied_power = {}   # registry name -> the best copy's power that list was written for
        self.lower_since = {}  # registry name -> when its best copy was first seen lower than that
        self.held = []         # [(object, registry name, shown power)] from the last pass
        self._base_perks = {}
        self.old_items = saved_items() if base else set()     # read once, when the launcher starts
        self.seed = saved_best() if base else {}              # what the save says, until the game shows its items
        self.seen_live = False
        self.stock_info, self.stock_checked = None, 0.0      # the save's merchant stock, re-read when the save changes
        self.wares = set()                                   # item objects that are merchant stock
        self.shifted = set()                                 # ...whose power was raised in this session
        got = upgraded_items() if base else None             # Blacksmith: upgrades already collected don't count
        self.upgrades_seen = got[1] if got else None         # None: the save couldn't be read yet (no key yet)
        self.upgrades_time = got[2] if got else 0.0
        self.saves_retry = 0.0
        self.upgrades_due = {}                               # (id, power bytes) -> (power level, when first seen)
        self.upgrades_checked = 0.0

    def learn_types(self):
        for name, glob in bp.REGISTRY.items():
            raw = read(self.h, self.base + int(glob, 16), 8)
            definition = struct.unpack("<Q", raw)[0] if raw else 0
            raw = read(self.h, definition, 4) if definition else None
            if raw:
                self.types[struct.unpack("<I", raw)[0]] = name
        return bool(self.types)

    def items(self):
        """{registry name: best shown power} over every item object in the game."""
        if self.own_scanner:
            self.scanner.refresh()
        objs = self.scanner.found.get(self.item_vt, [])
        best, self.held, self.raw_power = {}, [], {}
        for o in objs:
            raw = read(self.h, o + ITEM_TYPE, 12)
            if not raw:
                continue
            name = self.types.get(struct.unpack_from("<I", raw)[0])
            power = struct.unpack_from("<f", raw, 8)[0]
            if name and 1.0 <= power < 60.0:
                shown = int((power - 1) * 10 + 1 + 1e-3)
                if o not in self.wares:                  # what a merchant has on the shelf isn't the player's yet
                    best[name] = max(best.get(name, 0), shown)
                self.held.append((o, name, shown))
                self.raw_power[o] = raw[8:12]
        return best

    def bonus_list(self, name):
        cat, item = name.split("/")
        section = self.cfg.get(SECTIONS[cat], {})
        family = re.sub(r"_(Unique\d|Spooky\d|Winter\d|Year\d|spooky\d).*$", "", item)
        return section.get(item) or section.get(family) or section.get("all") or []

    def plain_item(self, name):
        """Registry name of the plain item this one is a unique of (None for a plain item): the definition's own
        link (+0x228), else by its name (Sword_Unique1 -> Sword or Sword_Steel)."""
        raw = read(self.h, self.base + int(bp.REGISTRY[name], 16), 8)
        definition = struct.unpack("<Q", raw)[0] if raw else 0
        raw = read(self.h, definition + BASE_ITEM, 8) if definition else None
        link = struct.unpack("<Q", raw)[0] if raw else 0
        raw = read(self.h, link, 4) if link else None
        found = self.types.get(struct.unpack("<I", raw)[0]) if raw else None
        if found:
            return found
        cat, item = name.split("/")
        family = re.sub(r"_(Unique\d|Spooky\d|Winter\d|Year\d|spooky\d).*$", "", item)
        if family == item:
            return None
        return next((f"{cat}/{c}" for c in (family, family + "_Steel") if f"{cat}/{c}" in bp.REGISTRY), None)

    def bonus_slots(self, name):
        """How many bonus enchantments this item type gets: every item ends with the same number of enchantments
        beyond what its family's plain item has (`total`, 4 - user, 2026-10-14), so a unique with two of its own
        gets one bonus fewer than one with a single one. Never fewer than one, never more than three."""
        if name not in self._slots:
            plain = self.plain_item(name)
            family = set()
            if plain:
                if plain not in self.original:
                    _, cur = bp.builtins(self.h, self.base, plain)
                    self.original[plain] = cur or []
                family = {t for t, _ in self.original[plain]}
            own = sum(1 for t, _ in self.original[name] if t not in family) if plain else 0
            self._slots[name] = min(3, max(1, self.total - own))
        return self._slots[name]

    def wanted(self, name, power):
        """The built-in list this item type should have with its best copy at `power`."""
        past_cap = max(0, (power - self.cap) // self.step)
        steps = sum(power >= lv for lv in self.early) + past_cap   # the early steps only ever raise own built-ins
        if self.final and power >= self.final:
            steps = 99       # A+100 gear is complete: every built-in and all three bonuses at tier 3 (user, 2026-10-13;
                             # 14 uniques with two to four tier-1 built-ins would otherwise stop a few tiers short)
        out = list(self.original[name])
        for i, (type_id, level) in enumerate(out):       # own built-ins first
            up = min(steps, max(0, MAX_TIER - level))
            out[i] = (type_id, level + up)
            steps -= up
        have = {t for t, _ in out}
        if steps < 99:
            steps = min(steps, past_cap)       # bonuses only from the cap on, whatever the early steps did
        given, used, slots = 0, set(), self.bonus_slots(name)
        names = self.bonus_list(name)
        # A name ending in "!" asks for a second copy of an enchantment the item has built in (copies all fire).
        wants = [(bp.IDS.get(n.rstrip("!")), n.endswith("!")) for n in names]
        for i, (type_id, copy) in enumerate(wants):      # the bonuses, one tier at a time
            if steps <= 0 or given >= slots or type_id is None or len(out) >= MAX_ENTRIES:
                continue
            if type_id in have and not copy:             # (a list may hold spares for items that own one already)
                continue
            tier = min(steps, MAX_TIER)
            out.append((type_id, tier))
            have.add(type_id)
            used.add(i)
            steps -= tier
            given += 1
        if self.final and power >= self.final and not name.startswith("Armor/"):   # A+100 gear: one more, at tier 3
            more = [t for i, (t, copy) in enumerate(wants) if i not in used and t is not None and (copy or t not in have)]
            extra = bp.IDS.get(self.final_extra.get(SECTIONS[name.split("/")[0]], ""))
            if extra is not None and extra not in have:      # [final_extra]: the same one for the whole section
                more.insert(0, extra)
            if more and given >= slots and len(out) < MAX_ENTRIES:
                out.append((more[0], MAX_TIER))
        name_id = bp.IDS.get(self.ladder.get(SECTIONS[name.split("/")[0]], ""))
        if self.final and name_id is not None and self.ladder.get("step"):   # the ladder: new lines below the rest
            tiers = max(0, (power - self.final) // self.ladder["step"])
            while tiers > 0 and len(out) < MAX_ENTRIES:
                out.append((name_id, min(tiers, MAX_TIER)))
                tiers -= MAX_TIER
        return out

    def perk_list(self, name):
        section = self.cfg.get("armor_perks", {})
        item = name.split("/")[1]
        family = re.sub(r"_(Unique\d|Spooky\d|Winter\d|Year\d|spooky\d).*$", "", item)
        return section.get(item) or section.get(family) or section.get("all") or []

    def give_perks(self, quiet=False):
        """Armor at or above each [armor_perks] level gets that many extra perks from its list (once, for good)."""
        levels = self.cfg.get("armor_perks", {}).get("levels", [])
        for o, name, shown in self.held:
            due = sum(shown >= lv for lv in levels)
            if not due or not name.startswith("Armor/"):
                continue
            head = read(self.h, o + ITEM_PERKS, 16)
            if not head:
                continue
            data, count, cap = struct.unpack("<QII", head)
            raw = read(self.h, data, 2 * count) if data and 0 < count <= cap <= 16 else None
            if not raw:
                continue
            have = [raw[i] for i in range(0, len(raw), 2)]
            wanted = [pp.PERKS[p] for p in self.perk_list(name) if p in pp.PERKS]
            # perks already on the armor from its list count as given (also after a restart)
            given = sum(1 for p in wanted if p in have and raw[2 * have.index(p) + 1] == 2 and p not in self.base_perks(name))
            for perk in wanted:
                if given >= due or count >= cap:
                    break
                if perk in have:
                    continue
                bp.write(self.h, data + 2 * count, bytes([perk, 2]))
                count += 1
                bp.write(self.h, o + ITEM_PERKS + 8, struct.pack("<I", count))
                have.append(perk)
                given += 1
                if not quiet:
                    print(f"  {name} ({shown}): perk {pp.NAMES[perk]} added")

    def stock(self, quiet=False):
        """Merchant stock follows the character's power level ([merchants] in Bonus.toml).

        The game stocks merchants near A+25 power however strong the character is. Stock items are ordinary item
        objects; which ones are stock comes from the save (each shop's slots: type + exact power). The game's own
        choice is kept - each ware's power relative to the others - and only moved up: every weapon and armor on
        the shelves gains (character's power level - game_ceiling) points, the character's level being the save's
        totalGearPower. Nothing happens while the character is at or below the ceiling. Artifacts are not handled."""
        cfg = self.cfg.get("merchants", {})
        if not cfg.get("follow_power", False):
            return
        now = time.time()
        if now - self.stock_checked >= 10:                # a look at the save every 10 s is plenty
            self.stock_checked = now
            files = list(save_folder().glob("*/Characters/*.dat"))
            newest = max((f.stat().st_mtime for f in files), default=0)
            if self.stock_info is None or newest > self.stock_info[2]:
                self.stock_info = merchant_stock() or self.stock_info
        if not self.stock_info:
            return
        level, stock, _ = self.stock_info
        self.wares = {o for o in self.wares if any(o == held[0] for held in self.held)}
        for o, name, shown in self.held:
            if (name.split("/")[1].lower(), self.raw_power[o]) in stock:
                self.wares.add(o)
        ceiling = int(cfg.get("game_ceiling", 254))
        shift = level - ceiling
        for o, name, shown in self.held:
            # Stock the game made itself sits around its ceiling; anything clearly above was shifted before
            # (in this session or an earlier one - the game saves the stock with its new power).
            if shift <= 0 or o not in self.wares or o in self.shifted or shown > ceiling + 3:
                continue
            bp.write(self.h, o + ITEM_POWER, struct.pack("<f", struct.unpack("<f", self.raw_power[o])[0] + shift / 10))
            self.shifted.add(o)
            if not quiet:
                print(f"  merchant stock: {name} {shown} -> {shown + shift}")

    def blacksmith(self, quiet=False):
        """A Blacksmith upgrade comes back at least at the character's power level ([blacksmith] in Bonus.toml).

        The game works the upgraded power out from the difficulty of the missions won, and its difficulties stop at
        A+25 - so above that an upgrade would fall short. A collected upgrade is an item the save marks `upgraded`;
        one that wasn't there before (type + exact power) and is below the character's power level - the save's
        totalGearPower, as for the merchants - is raised to it, once. Never lowered. Artifacts are not handled
        (not item objects). It happens once the game has saved after the item was collected."""
        if not self.cfg.get("blacksmith", {}).get("match_power", False):
            return
        now = time.time()
        if now - self.upgrades_checked >= 10:
            self.upgrades_checked = now
            files = list(save_folder().glob("*/Characters/*.dat"))
            newest = max((f.stat().st_mtime for f in files), default=0)
            if newest > self.upgrades_time:
                got = upgraded_items()
                if got:
                    level, done, self.upgrades_time = got
                    if self.upgrades_seen is None:            # first read: what is there now isn't new
                        self.upgrades_seen = set(done)
                    for key in done - self.upgrades_seen:
                        self.upgrades_due[key] = (level, now)
                    self.upgrades_seen |= done
        for key, (level, since) in list(self.upgrades_due.items()):
            if now - since > 600:                         # not among the items any more (sold, salvaged...)
                del self.upgrades_due[key]
                continue
            for o, name, shown in self.held:
                if o in self.wares or (name.split("/")[1].lower(), self.raw_power[o]) != key:
                    continue
                del self.upgrades_due[key]
                if shown < level:
                    bp.write(self.h, o + ITEM_POWER, struct.pack("<f", struct.unpack("<f", self.raw_power[o])[0] + (level - shown) / 10))
                    print(f"  Blacksmith upgrade: {name} {shown} -> {level} (your power level)")
                break

    def climb(self, quiet=False):
        """A+100 drops keep climbing ([ladder] climb in Bonus.toml): a new drop at `final` power or more comes in a
        few points above the character's power level (the save's totalGearPower), so every run nudges the gear up
        and the ladder grows. Once per item; never lowered. Items from before this session, merchant wares and
        anything already raised are left alone."""
        low, high = (self.ladder.get("climb") or [0, 0])[:2]
        if not self.final or high <= 0 or self.old_items is None:
            return
        if self.stock_info is None or time.time() - self.stock_checked >= 10:
            self.stock_checked = time.time()
            self.stock_info = merchant_stock() or self.stock_info
        if not self.stock_info:
            return
        level = self.stock_info[0]
        self.shelf |= {(name.split("/")[1].lower(), self.raw_power[o]) for o, name, _ in self.held if o in self.wares}
        for o, name, shown in self.held:
            key = (name.split("/")[1].lower(), self.raw_power[o])
            if shown < self.final or o in self.wares or key in self.old_items or key in self.shelf or key in self.climbed:
                continue
            roll = hashlib.sha256(b"climb" + name.encode() + self.raw_power[o]).digest()
            target = level + low + roll[0] % (high - low + 1)
            self.climbed.add(key)
            if target <= shown:
                continue
            new = struct.pack("<f", struct.unpack("<f", self.raw_power[o])[0] + (target - shown) / 10)
            bp.write(self.h, o + ITEM_POWER, new)
            self.climbed.add((key[0], new))
            self.raw_power[o] = new
            if not quiet:
                print(f"  A+100 drop: {name} {shown} -> {target}")

    def gild(self, quiet=False):
        """Gear from [gilded] from_power up has a chance to be gilded: one extra enchantment ([gilded] pool).

        Stored on the single item (the game saves it as the item's gilded enchantment). Whether an item is gilded,
        with what and at which tier is worked out from its name and exact power, so it is decided once per item
        and comes out the same in every session; an item that is gilded already is left alone.
        Only new items: anything found in the character saves when the launcher started is skipped."""
        cfg = self.cfg.get("gilded", {})
        chance, start = float(cfg.get("chance", 0)), cfg.get("from_power", 10**6)
        early_from, early_chance = cfg.get("early_from", start), float(cfg.get("early_chance", chance))
        tiers = cfg.get("tier_chances", [0.5, 0.35, 0.15])
        for o, name, shown in self.held:
            this_chance = chance if shown >= start else early_chance if shown >= early_from else 0.0
            if this_chance <= 0 or self.old_items is None:
                continue
            if (name.split("/")[1].lower(), self.raw_power[o]) in self.old_items:
                continue                                 # the player had it before this session: not a new drop
            names = [e.rstrip("!") for e in self.bonus_list(name) if e.rstrip("!") in bp.IDS]
            if cfg.get("pool", "any") == "any":          # any enchantment that can roll on this kind of gear;
                soul = any(e in POOLS["soul"] for e in names)   # soul ones only on gear that is built around souls
                names = [e for e in POOLS[SECTIONS[name.split("/")[0]]] if e in bp.IDS and (soul or e not in POOLS["soul"])]
            raw = read(self.h, o + ITEM_GILDED, 4)
            if not names or raw != bytes(4):
                continue
            roll = hashlib.sha256(name.encode() + self.raw_power[o]).digest()
            if roll[0] / 256 >= this_chance:
                continue
            enchant = names[roll[1] % len(names)]
            pick, tier = roll[2] / 256, 1
            for i, weight in enumerate(tiers[:MAX_TIER]):
                if pick < weight:
                    tier = i + 1
                    break
                pick -= weight
            bp.write(self.h, o + ITEM_GILDED + 4, bytes([bp.IDS[enchant], 0, 0, 0]) + struct.pack("<i", tier) + bytes([0, 3, 0, 0]))
            bp.write(self.h, o + ITEM_GILDED, struct.pack("<i", 1))
            if not quiet:
                print(f"  {name} ({shown}): gilded with {enchant} {tier}")

    def base_perks(self, name):
        """Perk ids the item type comes with (its definition's list, including Perks.toml additions)."""
        if name not in self._base_perks:
            got = pp.perks(self.h, self.base, name)
            self._base_perks[name] = [i for i, _ in got[1]] if got else []
        return self._base_perks[name]

    def write(self, name, entries):
        definition = struct.unpack("<Q", read(self.h, self.base + int(bp.REGISTRY[name], 16), 8))[0]
        if name not in self.buffers:
            self.buffers[name] = bp.alloc(self.h, bp.STRIDE * MAX_ENTRIES)
        at = self.buffers[name]
        tdata, tcur = bp.builtins(self.h, self.base, bp.TEMPLATE_ITEM)
        template = read(self.h, tdata, bp.STRIDE) if tcur else None
        if not at or not template:
            return False
        raw = bytearray()
        for type_id, level in entries:
            e = bytearray(template)
            e[0] = type_id
            struct.pack_into("<i", e, 4, level)
            raw += e
        if raw:
            bp.write(self.h, at, bytes(raw))
        bp.write(self.h, definition + bp.ARRAY, struct.pack("<QII", at, len(entries), MAX_ENTRIES))
        return True

    def tick(self, quiet=False):
        if not self.types and not self.learn_types():
            return
        if self.old_items is None and time.time() - self.saves_retry >= 10:
            # On a first start without research/save_key.bin the saves can't be read until the game has loaded a
            # character (the key is read from the game then). The game only saves new drops after a mission, so
            # a read in the menu still shows what was there before this session.
            self.saves_retry = time.time()
            self.old_items = saved_items()
            if not self.seed:
                self.seed = saved_best()
        best = self.items()
        if best:
            self.seen_live = True
        elif not self.seen_live:
            best = dict(self.seed)           # no character loaded yet: go by the save
        self.stock(quiet)
        self.blacksmith(quiet)
        self.climb(quiet)                    # before gild: an item is gilded (or not) at its final power
        self.give_perks(quiet)
        self.gild(quiet)
        for name in set(best) | set(self.applied):
            if name not in self.original:
                _, cur = bp.builtins(self.h, self.base, name)
                if cur is None:
                    continue
                self.original[name] = cur
            power = best.get(name, 0)
            # Taking bonuses away waits: while a level loads, items are gone for a moment, and a character built
            # in that moment from a stripped list would be without its bonuses for the whole mission (a built-in
            # change only reaches a weapon when it is equipped again). Seen 2026-10-13: "best copy 0" in the log
            # between two "best copy 364".
            if power < self.applied_power.get(name, 0):
                if time.time() - self.lower_since.setdefault(name, time.time()) < HOLD_SECONDS:
                    continue
            self.lower_since.pop(name, None)
            want = self.wanted(name, power)
            if want != self.applied.get(name, self.original[name]) and self.write(name, want):
                self.applied[name] = want
                self.applied_power[name] = power
                if not quiet:
                    shown = ", ".join(f"{bp.NAMES.get(t, t)} {lv}" for t, lv in want) or "none"
                    print(f"  {name} (best copy {power}): {shown}")


if __name__ == "__main__":
    h, base = open_game()
    if not h:
        sys.exit("Minecraft Dungeons isn't running")
    w = Watch(h, base)
    w.tick()
    while "--once" not in sys.argv and pid_of():
        time.sleep(3)
        w.tick()
