"""Merchant prices in the running game (Prices.toml). Data only: no game code is changed.

    python tools/prices_patch.py            # watch the running game until it closes
    python tools/prices_patch.py --once     # one pass
    python tools/prices_patch.py --show     # every merchant's current numbers

A price is worked out in code (exe+0xB8FA70) as
    base price x power factor x rarity (1 / 1.4 / 2) x the slot's own multiplier x 3 if gilded x (1 - rebate)
and the base price is a plain int inside each merchant's pricing object (UProgressPowerRarityPricing, vtable
exe+0x34C39C8: base price at +0x30, a second int at +0x38 that only merchants with a restock have - taken to be
the restock price). The pricing object belongs to the merchant's actor (+0x28), whose class is named by a merchant
definition (vtable exe+0x334BC28: actor class at +0x28, unlock key as text at +0x30), which is how the merchant
is recognised. Read 2026-10-07:
    enchantmentmerchant (Enchantsmith, gold) 20      piglinmerchant (gold) 12, restock 5
    shopkeeper (Village Merchant) 100, 50            luxurymerchant 200, 200       mysterymerchant 150, 50
    blacksmith 150                                    giftwrapper 100
The actors are made each time the camp loads, so the launcher sets the numbers whenever it sees them
(tools/live_objects.py). A number is only changed while it still has the game's own value.
"""
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

CONFIG = Path(__file__).resolve().parent.parent / "Prices.toml"
PRICING, DEFINITION = 0x34C39C8, 0x334BC28
OWNER, BASE_PRICE, RESTOCK = 0x28, 0x30, 0x38
VANILLA = {"enchantmentmerchant": (20, 0), "piglinmerchant": (12, 5), "shopkeeper": (100, 50),
           "luxurymerchant": (200, 200), "mysterymerchant": (150, 50), "blacksmith": (150, 0), "giftwrapper": (100, 0)}


class Prices:
    def __init__(self, h, base, scanner=None):
        self.h, self.base = h, base
        self.own_scanner = scanner is None
        self.scanner = scanner or Scanner(h, base)
        cfg = tomllib.loads(CONFIG.read_text(encoding="utf-8")) if CONFIG.exists() else {}
        self.plan = {}
        for name, factor in cfg.items():
            if name in VANILLA and isinstance(factor, (int, float)) and not isinstance(factor, bool) and 0 < factor <= 10:
                if factor != 1:
                    self.plan[name] = float(factor)
            else:
                print(f"  ! Prices.toml {name}: unknown merchant or not a factor between 0 and 10 - skipped")
        self.pricing = self.scanner.register(PRICING) if base else 0
        self.definition = self.scanner.register(DEFINITION) if base else 0
        self.said = set()

    def names(self):
        """{actor class: merchant name} from the merchant definitions."""
        out = {}
        for o in self.scanner.found.get(self.definition, []):
            raw = read(self.h, o, 0x40)
            if not raw:
                continue
            actor_class, text, count = struct.unpack_from("<QQI", raw, 0x28)
            key = read(self.h, text, count * 2) if actor_class and text and 0 < count < 64 else None
            if key:
                out[actor_class] = key.decode("utf-16le", "ignore").split("\0")[0].removesuffix("_unlocked")
        return out

    def merchants(self):
        """[(pricing object, merchant name, base price, restock price)] in the game right now."""
        names, out = self.names(), []
        for o in self.scanner.found.get(self.pricing, []):
            raw = read(self.h, o, 0x40)
            owner = struct.unpack_from("<Q", raw, OWNER)[0] if raw else 0
            cls = read(self.h, owner + 0x10, 8) if owner else None
            if cls:
                out.append((o, names.get(struct.unpack("<Q", cls)[0], "?"),
                            struct.unpack_from("<i", raw, BASE_PRICE)[0], struct.unpack_from("<i", raw, RESTOCK)[0]))
        return out

    def tick(self, quiet=False):
        if not self.plan:
            return
        if self.own_scanner:
            self.scanner.refresh()
        for o, name, price, restock in self.merchants():
            if name not in self.plan or (price, restock) != VANILLA[name]:
                continue                                  # not ours to change, or changed already
            new_price = max(1, round(price * self.plan[name]))
            write(self.h, o + BASE_PRICE, struct.pack("<i", new_price))
            if restock:
                write(self.h, o + RESTOCK, struct.pack("<i", max(1, round(restock * self.plan[name]))))
            if not quiet and name not in self.said:
                self.said.add(name)
                print(f"  {name}: base price {price} -> {new_price}")


if __name__ == "__main__":
    h, base = open_game()
    if not h:
        sys.exit("Minecraft Dungeons isn't running")
    w = Prices(h, base)
    if "--show" in sys.argv:
        w.scanner.refresh()
        for o, name, price, restock in sorted(w.merchants(), key=lambda m: m[1]):
            print(f"{name:22} base price {price:4}   restock {restock}")
        sys.exit()
    w.tick()
    while "--once" not in sys.argv and pid_of():
        time.sleep(3)
        w.tick()
