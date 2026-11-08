"""Reroll: the transmog menu's Reroll tab - one row per worn melee weapon, ranged weapon and armor (icon, name,
power, gilded) with its buttons. build_transmog.py execs this file and calls its steps where they belong.

For the item worn in a row's slot, paid with emeralds or gold (the game's own wallet, Deduct). The prices go
with the average power of the worn gear: PRICES at PRICE_POWER, x (average power / PRICE_POWER), emeralds to the
nearest 10 (at least 10), gold whole (at least 1) - the new item's power follows the gear too. A button shows its
price and is greyed out when the wallet holds less; the price is checked again right before paying.
    Reroll       a new item of its plain kind (a unique cut back to its base: Gauntlets_Unique3 -> Gauntlets) or one
                 of that kind's uniques. The odds go with the average power of the worn gear, after the game's own
                 drop odds (common / rare / unique): under 200 a fancy chest's 75/20/5, 200 an event mob's 65/25/10,
                 250 a deluxe chest's 0/75/25, 300 a boss's 0/50/50. The unique share is rolled here (UNIQUE_SHARES):
                 a hit picks one of the kind's _UniqueN items (transmog_items.json) and drops it like an exact copy
                 (no gilding); else the plain kind drops through a fresh dropper with that category (its unique roll
                 falls back to rare), paid at once. Not the game's IncludeUniques: with it, every later drop that
                 session was the first kind asked for (Gauntlets) - tests 3 and 4, 2026-11-03.
    Exact copy   uniques only: the same unique, with a boss's odds, asked again every half second until a new item of
                 that kind lies in the map (a unique only drops when the rarity roll lands on unique; test 6: about
                 2 tries). When the worn one is gilded, the copy gets its gilding (the same gilded enchantment)
                 while it lies on the ground - the game's drops are never gilded themselves: the mod's gilding is
                 the launcher's, written to new items later (bonus_watch). Paid when it drops; nothing after TRIES
                 tries; if the wallet no longer holds the price then, the copy is cleared away (the game's own
                 StorableItem.TimeToPoolFinished) unpaid.
The game rolls the new item itself (enchantments, power, gilding) and drops it at the player's feet; the old item
stays. The drop goes through the transmog actor's own LootDrop component (the game's ULootTableItemDropComponent,
the kind mobs and chests drop with) - found with drop tests 1-6 (build_droptest.py, decisions.md 2026-11-02/03).
"""
LOOT = "/Script/Dungeons.LootTableItemDropComponent"
WALLET = "/Script/Dungeons.WalletComponent"
STORABLE = "/Script/Dungeons.StorableItem"
DROPPER = "/Game/SequelMod/BP_SequelRerollDrop"   # one per reroll: a fresh drop component (see reroll_actor_vars)
DROPPER_CLASS = DROPPER + ".BP_SequelRerollDrop_C"
DROPPER_LIFE = 30.0   # seconds it stays after its drop
SLOT_KEY = "enum:/Script/Dungeons.EEquipmentSlot"
PRICES = {(False, False): 500, (False, True): 10, (True, False): 5000, (True, True): 100}   # (exact, gold) -> price
import json as _json, os as _os
with open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "_settings.json")) as _f:
    FREE = _json.load(_f).get("free_reroll", False)   # a TEST build: every price 0 (tools/blueprints.py)
if FREE:
    PRICES = {key: 0 for key in PRICES}
PRICE_POWER = 255.0   # ... at this average gear power (user, 2026-11-03)
# the buttons in the order of the actor's Prices list (index = exact * 2 + gold)
REROLL_BUTTONS = [("RerollEmerald", False, False, "", " emeralds"), ("RerollGold", False, True, "", " gold"),
                  ("ExactEmerald", True, False, "", " emeralds"), ("ExactGold", True, True, "", " gold")]
ODDS = ["FancyChest", "EventMob", "DeluxeChest", "Boss"]          # by OddsTier: average power under 200 / 200 / 250 / 300
ODDS_WORDS = ["common 75%, rare 20%, unique 5%", "common 65%, rare 25%, unique 10%", "rare 75%, unique 25%",
              "rare 50%, unique 50%"]
ODDS_STEPS = [200.0, 250.0, 300.0]
UNIQUE_SHARES = [0.05, 0.10, 0.25, 0.50]   # the unique weight of each ODDS category (of 100)
TRIES = 240        # exact copy: drop calls at most (2 minutes)
INTERVAL = 0.5     # seconds between them - the item appears a moment after the call, so the check waits
REROLL_TAB = 4   # Melee, Ranged, Armor, Loadouts, Reroll
REROLL_SLOTS = [("Melee", "MeleeGear"), ("Ranged", "RangedGear"), ("Armor", "ArmorGear")]
# the buttons the pad can select (build_transmog.py's highlight)
REROLL_FOCUS = [slot + name for slot, _ in REROLL_SLOTS for name, _, _, _, _ in REROLL_BUTTONS]
RR = {}


# --- shared pieces (g is the graph being built) ---

def rr_stash(g):
    """The player's item stash: (cast node - has exec pins, (node, pin))."""
    player = g.call("/Script/Engine.GameplayStatics", "GetPlayerCharacter", PlayerIndex=0)
    stash = g.call("/Script/Engine.Actor", "GetComponentByClass", ComponentClass=STASH)
    g.link(player, "ReturnValue", stash, "self")
    node, pin = g.cast(STASH, (stash, "ReturnValue"))
    return node, (node, pin)


def rr_worn(g, stash, key=None, key_pin=None):
    """((node, pin) of the InventoryItem worn in that equipment slot - None when empty, (node, pin) of its data)."""
    slots = g.call(STASH, "GetEquipmentSlots")
    g.link(stash[0], stash[1], slots, "self")
    find = g.call(MAPS, "Map_Find")
    g.link(slots, "ReturnValue", find, "TargetMap")
    if key_pin:   # after the map is linked: before, the key pin has no type
        g.link(key_pin[0], key_pin[1], find, "Key")
    else:
        g.set(find, Key=key)
    item = g.var("Item", owner=INV_SLOT, target=(find, "Value"))
    data = g.var("Item", owner=INV_ITEM, target=(item, "Item"))
    return (item, "Item"), (data, "Item")


def rr_break(g, data):
    broken = g.node("/Script/BlueprintGraph.K2Node_BreakStruct", StructType=DATA)
    g.link(data[0], data[1], broken, g.pins(broken)[0])
    return broken


def rr_valid(g, obj):
    node = g.call("/Script/Engine.KismetSystemLibrary", "IsValid")
    g.link(obj[0], obj[1], node, "Object")
    return node, "ReturnValue"


def rr_id_text(g, item_id):
    broken = g.node("/Script/BlueprintGraph.K2Node_BreakStruct", StructType=ITEM_ID)
    g.link(item_id[0], item_id[1], broken, g.pins(broken)[0])
    text = g.call(STRINGS, "Conv_NameToString")
    g.link(broken, "SerializedId", text, "InName")
    return text, "ReturnValue"


def rr_is_unique(g, item_id):
    """(node, pin): the id has a variant after its base (Gauntlets_Unique3, Glaive_Spooky2) - every base id is one
    word (transmog_items.json)."""
    at = g.call(STRINGS, "FindSubstring", Substring="_")
    text = rr_id_text(g, item_id)
    g.link(text[0], text[1], at, "SearchIn")
    return g.at_least_zero((at, "ReturnValue"))


def rr_base(g, item_id, owner=None):
    """(node, pin): the id cut back to its base kind - Gauntlets_Unique3 -> Gauntlets; a base id stays. Taken from
    the transmog actor's ready-made AllIds by name (owner: (node, pin) of the actor, else self): a Make struct node
    keeps the first value it ever made (build_transmog.py's icons; here the reroll kept Gauntlets and the gold
    button paid emeralds - tests 5 and 6, 2026-11-03)."""
    text = rr_id_text(g, item_id)
    at = g.call(STRINGS, "FindSubstring", Substring="_")
    g.link(text[0], text[1], at, "SearchIn")
    cut = g.call(STRINGS, "Left")
    g.link(text[0], text[1], cut, "SourceString")
    g.link(at, "ReturnValue", cut, "Count")
    pick = g.call(MATH, "SelectString")
    g.link(cut, "ReturnValue", pick, "A")
    g.link(text[0], text[1], pick, "B")
    variant = g.at_least_zero((at, "ReturnValue"))
    g.link(variant[0], variant[1], pick, "bPickA")
    return rr_id_named(g, (pick, "ReturnValue"), owner)


def rr_id_named(g, name, owner=None):
    """(node, pin): the item id called name ((node, pin) of a string) from the actor's AllIds / AllNames."""
    names = g.var("AllNames", owner=ACTOR_CLASS if owner else "", target=owner)
    index = g.array_call("Array_Find", (names, "AllNames"), "TargetArray", ItemToFind=name)
    ids = g.var("AllIds", owner=ACTOR_CLASS if owner else "", target=owner)
    return g.item_at((ids, "AllIds"), (index, "ReturnValue"))


def rr_name(g, item_id):
    """(node, pin) of the item kind's name as a string."""
    name = g.call("/Script/Dungeons.ItemFunctionLibrary", "GetNameForItemType")
    g.link(item_id[0], item_id[1], name, "Type")
    text = g.call("/Script/Engine.KismetTextLibrary", "Conv_TextToString")
    g.link(name, "ReturnValue", text, "InText")
    return text, "ReturnValue"


def rr_int_text(g, value):
    node = g.call(STRINGS, "Conv_IntToString")
    g.link(value[0], value[1], node, "InInt")
    return node, "ReturnValue"


def rr_joined(g, *parts):
    """A string from parts: plain strings or (node, pin) of strings."""
    out = None
    for part in parts:
        concat = g.call(STRINGS, "Concat_StrStr")
        if out:
            g.link(out[0], out[1], concat, "A")
        for pin, value in [("B", part)] if out else [("A", part), ("B", "")]:
            if isinstance(value, tuple):
                g.link(value[0], value[1], concat, pin)
            else:
                g.set(concat, **{pin: value})
        out = (concat, "ReturnValue")
    return out


def rr_wallet(g):
    """The player's wallet: (cast node - has exec pins, (node, pin))."""
    player = g.call("/Script/Engine.GameplayStatics", "GetPlayerCharacter", PlayerIndex=0)
    wallet = g.call("/Script/Engine.Actor", "GetComponentByClass", ComponentClass=WALLET)
    g.link(player, "ReturnValue", wallet, "self")
    node, pin = g.cast(WALLET, (wallet, "ReturnValue"))
    return node, (node, pin)


def rr_currency(g, name=None, gold=None):
    """(node, pin) of the currency's item id: a fixed one by name (a Make struct of a constant), or - in the actor -
    Gold / Emerald by the bool gold (node, pin), from its ready-made CurrencyIds."""
    if name:
        made = g.node("/Script/BlueprintGraph.K2Node_MakeStruct", StructType=ITEM_ID)
        g.set(made, SerializedId=name)
        return made, "SerializableItemId"
    which = g.call(MATH, "Conv_BoolToInt")
    g.link(gold[0], gold[1], which, "InBool")
    return g.item_at((g.var("CurrencyIds"), "CurrencyIds"), (which, "ReturnValue"))


def rr_balance(g, wallet, currency):
    node = g.call(WALLET, "Balance")
    g.link(wallet[0], wallet[1], node, "self")
    g.link(currency[0], currency[1], node, "Type")
    return node, "ReturnValue"


def rr_visible(g, name, shown, owner=None, target=None):
    node = g.call("/Script/UMG.Widget", "SetVisibility", InVisibility="Visible" if shown else "Collapsed")
    g.link(g.var(name, owner=owner or "", target=target), name, node, "self")
    return node


# --- the menu ---

GREY = unreal.LinearColor(0.62, 0.64, 0.7, 1.0)    # small print
BAND = unreal.LinearColor(0.07, 0.07, 0.09, 0.95)  # a row's background
NAME_WIDTH, BUTTON_WIDTH, GROUP_GAP = 270, 165, 16   # 165: "5000 emeralds" fits
REROLL_HELP = ("Reroll: drops a completely new item of the same kind, with a chance of any of its uniques.\n"
               "Exact copy: drops a completely new item but keeps the same unique, with the same gilded enchantment.\n"
               "Prices go with your power. New items drop at your feet; yours stays.")   # wording: the user


def small_print(text):
    text.set_editor_property("color_and_opacity", unreal.SlateColor(GREY))
    return text


def reroll_layout(menu):
    """Under the status line (Reroll tab only): one line of power, odds and wallet; the column heads; a band per
    slot - icon, name over power / gilded, the reroll buttons and (uniques only) the exact copy buttons, all the
    same width so the columns line up; then the small print."""
    box = widget(menu, "Rows", unreal.VerticalBox, "RerollBox", True)
    box.set_editor_property("visibility", unreal.SlateVisibility.COLLAPSED)
    info = label(menu, "RerollBox", "RerollInfo", "", 16, is_variable=True)
    info.get_editor_property("slot").set_padding(unreal.Margin(0, 2, 0, 8))
    widget(menu, "RerollBox", unreal.HorizontalBox, "RerollHead")
    widget(menu, "RerollHead", unreal.SizeBox, "RerollHeadPad").set_width_override(6 + 56 + 8 + NAME_WIDTH)
    for title, name, gap in [("REROLL", "RerollHeadReroll", 0), ("EXACT COPY", "RerollHeadExact", GROUP_GAP)]:
        size = widget(menu, "RerollHead", unreal.SizeBox, name + "Size")
        size.set_width_override(2 * BUTTON_WIDTH)
        size.get_editor_property("slot").set_padding(unreal.Margin(gap, 0, 0, 2))
        small_print(label(menu, name + "Size", name, title, 13))
    for slot, _ in REROLL_SLOTS:
        band = widget(menu, "RerollBox", unreal.Border, slot + "RerollBand")
        band.set_editor_property("brush_color", BAND)
        band.set_editor_property("padding", unreal.Margin(6, 4, 6, 4))
        band.get_editor_property("slot").set_padding(unreal.Margin(0, 0, 0, 4))
        widget(menu, slot + "RerollBand", unreal.HorizontalBox, slot + "RerollRow")
        icon = widget(menu, slot + "RerollRow", unreal.Image, slot + "RerollIcon", True)
        brush = icon.get_editor_property("brush")
        brush.set_editor_property("image_size", unreal.Vector2D(56, 56))
        icon.set_editor_property("brush", brush)
        size = widget(menu, slot + "RerollRow", unreal.SizeBox, slot + "RerollNameSize")
        size.set_width_override(NAME_WIDTH)
        spot = size.get_editor_property("slot")
        spot.set_vertical_alignment(unreal.VerticalAlignment.V_ALIGN_CENTER)
        spot.set_padding(unreal.Margin(8, 0, 0, 0))
        widget(menu, slot + "RerollNameSize", unreal.VerticalBox, slot + "RerollNameCol")
        label(menu, slot + "RerollNameCol", slot + "RerollName", "", 16, is_variable=True)
        small_print(label(menu, slot + "RerollNameCol", slot + "RerollDetail", "", 13, is_variable=True))
        buttons = widget(menu, slot + "RerollRow", unreal.HorizontalBox, slot + "RerollButtons", True)
        buttons.get_editor_property("slot").set_vertical_alignment(unreal.VerticalAlignment.V_ALIGN_CENTER)
        widget(menu, slot + "RerollButtons", unreal.HorizontalBox, slot + "RerollPart")
        exact_part = widget(menu, slot + "RerollButtons", unreal.HorizontalBox, slot + "ExactPart", True)
        exact_part.get_editor_property("slot").set_padding(unreal.Margin(GROUP_GAP, 0, 0, 0))
        for button_name, exact, gold, before, unit in REROLL_BUTTONS:
            size = widget(menu, slot + ("ExactPart" if exact else "RerollPart"), unreal.SizeBox,
                          slot + button_name + "Size")
            size.set_width_override(BUTTON_WIDTH)
            button(menu, slot + button_name + "Size", slot + button_name, str(PRICES[(exact, gold)]) + unit,
                   text_name=slot + button_name + "Text")
    help_text = small_print(label(menu, "RerollBox", "RerollHelp", REROLL_HELP, 13))
    help_text.set_auto_wrap_text(True)
    help_text.get_editor_property("slot").set_padding(unreal.Margin(0, 6, 0, 0))
    check(LIB.add_variable(menu, "OddsWords", "array:string"), "menu variable OddsWords")
    check(LIB.set_variable_default(menu, "OddsWords", "(" + ",".join('"%s"' % w for w in ODDS_WORDS) + ")"),
          "menu OddsWords")


def reroll_menu_events(g):
    RR["ShowReroll"] = g.custom_event("ShowReroll")


def reroll_menu_routines(g):
    """ShowReroll (from Show on the Reroll tab, and from the actor after a reroll) and the buttons."""
    g.row(12000)
    is_tab = g.call(MATH, "EqualEqual_IntInt", B=REROLL_TAB)
    g.link(g.var("Tab"), "Tab", is_tab, "A")
    on_tab = g.branch((is_tab, "ReturnValue"))
    g.flow(RR["ShowReroll"], on_tab)
    owner = (g.var("Owner"), "Owner")
    odds = g.call(ACTOR_CLASS, "WorkOutOdds")
    g.link(owner[0], owner[1], odds, "self")
    as_wallet, wallet = rr_wallet(g)
    as_stash, stash = rr_stash(g)
    g.flow((on_tab, "then"), rr_visible(g, "RerollBox", True), rr_visible(g, "OwnLook", False), odds, as_wallet,
           as_stash)
    balances = {gold: rr_balance(g, wallet, rr_currency(g, name="Gold" if gold else "Emerald")) for gold in (False, True)}
    prev = [(as_stash, "then")]
    for slot, key in REROLL_SLOTS:
        # A row: nothing worn -> "nothing worn", no buttons. Else icon, name over "power - gilded", the exact buttons
        # only for a unique, each button's price and greyed out when the wallet holds less.
        g.row(12400 + 900 * REROLL_SLOTS.index((slot, key)))
        item, data = rr_worn(g, stash, key=key)
        worn = g.branch(rr_valid(g, item))
        for node, pin in prev:
            g.link(node, pin, worn, "execute")
        nothing = set_words(g, slot + "RerollName", "nothing worn")
        no_detail = set_words(g, slot + "RerollDetail", " ")
        g.flow((worn, "else"), rr_visible(g, slot + "RerollButtons", False), rr_visible(g, slot + "RerollIcon", False),
               nothing, no_detail)
        broken = rr_break(g, data)
        texture = g.call("/Script/Dungeons.ItemFunctionLibrary", "StreamIconTextureForItemIdHigh", blockingLoad="true")
        g.link(broken, "ItemId", texture, "Type")
        paint = g.call("/Script/UMG.Image", "SetBrushFromTexture")
        g.link(g.var(slot + "RerollIcon"), slot + "RerollIcon", paint, "self")
        g.link(texture, "ReturnValue", paint, "Texture")
        shown = shown_power(g, (broken, "ItemPower"))
        gilded = g.call(MATH, "SelectString", A="  -  gilded", B="")
        g.link(broken, "bHasNetherite", gilded, "bPickA")
        titled = set_words(g, slot + "RerollName", rr_name(g, (broken, "ItemId")))
        detail = set_words(g, slot + "RerollDetail", rr_joined(g, "power ", rr_int_text(g, shown),
                                                              (gilded, "ReturnValue")))
        unique = g.branch(rr_is_unique(g, (broken, "ItemId")))
        g.flow((worn, "then"), rr_visible(g, slot + "RerollButtons", True), rr_visible(g, slot + "RerollIcon", True),
               paint, titled, detail, unique)
        steps = []
        for index, (name, exact, gold, before, unit) in enumerate(REROLL_BUTTONS):
            price = g.item_at((g.var("Prices", owner=ACTOR_CLASS, target=owner), "Prices"))
            g.set(price[0], **{"Dimension 1": index})
            enough = g.call(MATH, "GreaterEqual_IntInt")
            g.link(balances[gold][0], balances[gold][1], enough, "A")
            g.link(price[0], price[1], enough, "B")
            enable = g.call("/Script/UMG.Widget", "SetIsEnabled")
            g.link(g.var(slot + name), slot + name, enable, "self")
            g.link(enough, "ReturnValue", enable, "bInIsEnabled")
            relabel = set_words(g, slot + name + "Text", rr_joined(g, before, rr_int_text(g, price), unit))
            steps += [enable, relabel]
        for case, shown_exact in [("then", True), ("else", False)]:
            g.flow(*([(unique, case)] + [rr_visible(g, slot + "ExactPart", shown_exact)]
                     + [steps[0]]))
        g.flow(*steps)
        prev = [(no_detail, "then"), (steps[-1], "then")]
    g.row(15200)
    avg = g.call(MATH, "Round")
    g.link(g.var("AvgPower", owner=ACTOR_CLASS, target=owner), "AvgPower", avg, "A")
    words = g.item_at((g.var("OddsWords"), "OddsWords"),
                      (g.var("OddsTier", owner=ACTOR_CLASS, target=owner), "OddsTier"))
    said = set_words(g, "RerollInfo", rr_joined(
        g, "Power ", rr_int_text(g, (avg, "ReturnValue")), "   |   ", words, "   |   ",
        rr_int_text(g, balances[False]), " emeralds   |   ", rr_int_text(g, balances[True]), " gold"))
    for node, pin in prev:
        g.link(node, pin, said, "execute")

    # The buttons: the actor's Reroll for that row's slot.
    g.row(15600)
    for slot, key in REROLL_SLOTS:
        for name, exact, gold, _, _ in REROLL_BUTTONS:
            clicked = g.bound_event(slot + name, "OnClicked")
            call = g.call(ACTOR_CLASS, "Reroll", Key=key, Exact="true" if exact else "false",
                          Gold="true" if gold else "false")
            g.link(owner[0], owner[1], call, "self")
            g.flow(clicked, call)


def set_words(g, text_widget, words):
    """A SetText node for the menu's text widget: words is a plain string or (node, pin) of a string."""
    node = g.call("/Script/UMG.TextBlock", "SetText")
    g.link(g.var(text_widget), text_widget, node, "self")
    if isinstance(words, tuple):
        as_text = g.call("/Script/Engine.KismetTextLibrary", "Conv_StringToText")
        g.link(words[0], words[1], as_text, "InString")
        g.link(as_text, "ReturnValue", node, "InText")
    else:
        g.set(node, InText=words)
    return node


def shown_power(g, stored):
    """(node, pin): an item's power as the game shows it - stored power (stored - 1) x 10 + 1, rounded."""
    less_one = g.call(MATH, "Subtract_FloatFloat", B=1.0)
    g.link(stored[0], stored[1], less_one, "A")
    tens = g.call(MATH, "Multiply_FloatFloat", B=10.0)
    g.link(less_one, "ReturnValue", tens, "A")
    plus_one = g.call(MATH, "Add_FloatFloat", B=1.0)
    g.link(tens, "ReturnValue", plus_one, "A")
    whole = g.call(MATH, "Round")
    g.link(plus_one, "ReturnValue", whole, "A")
    return whole, "ReturnValue"


# --- the actor ---

def reroll_actor_vars(bp):
    # The reroll's own dropper: an actor with just a LootDrop component, spawned for each reroll. A component that
    # has dropped a plain kind with uniques included keeps that kind's list (test 3, 2026-11-03: after a weapon
    # change the reroll still dropped Gauntlets; the exact copy, without uniques, followed) - so a new one each time.
    dropper = blueprint(DROPPER, unreal.Actor)
    check(LIB.add_component(dropper, unreal.LootTableItemDropComponent, "LootDrop") is not None, "dropper component")
    compile_save(dropper, "reroll dropper")
    for name, kind in [("RerollDropper", "object:" + DROPPER_CLASS), ("RerollFamily", "array:int"), ("RerollData", "struct:" + DATA),
                       ("AllIds", "array:struct:" + ITEM_ID), ("AllNames", "array:string"),
                       ("CurrencyIds", "array:struct:" + ITEM_ID),
                       ("RerollWorn", "struct:" + DATA), ("RerollBase", "struct:" + ITEM_ID),
                       ("UniqueShares", "array:float"), ("RerollKind", "struct:" + ITEM_ID), ("RerollGold", "bool"), ("RerollGilded", "bool"),
                       ("RerollGilding", "struct:/Script/Dungeons.EnchantmentData"),
                       ("RerollSeen", "array:object:/Script/Engine.Actor"), ("RerollFound", "object:" + STORABLE),
                       ("RerollTries", "int"), ("Rerolling", "bool"), ("AvgPower", "float"), ("OddsTier", "int"),
                       ("Prices", "array:int"), ("RerollPrice", "int")]:
        check(LIB.add_variable(bp, name, kind), "variable " + name)
    check(LIB.set_variable_default(bp, "Prices", "(" + ",".join(str(PRICES[(e, gd)]) for _, e, gd, _, _ in REROLL_BUTTONS)
                                   + ")"), "Prices")
    # every item id the menu knows, plus each variant's base (Sword is only there as Sword_Unique1 ...)
    names = [i["id"] for i in ITEMS]
    names += sorted({n.split("_")[0] for n in names} - set(names))
    check(LIB.set_variable_default(bp, "AllNames", "(" + ",".join('"' + n + '"' for n in names) + ")"),
          "AllNames (%d)" % len(names))
    check(LIB.set_variable_default(bp, "AllIds", "(" + ",".join('(SerializedId="' + n + '")' for n in names) + ")"),
          "AllIds")
    check(LIB.set_variable_default(bp, "CurrencyIds", '((SerializedId="Emerald"),(SerializedId="Gold"))'),
          "CurrencyIds")
    check(LIB.set_variable_default(bp, "UniqueShares", "(" + ",".join(str(u) for u in UNIQUE_SHARES) + ")"),
          "UniqueShares")
    check(LIB.add_component(bp, unreal.LootTableItemDropComponent, "LootDrop") is not None, "loot drop component")
    LIB.compile(bp)   # so the graphs can use the component


def reroll_actor_events(g):
    for name, params in [("Reroll", "Key=" + SLOT_KEY + ";Exact=bool;Gold=bool"), ("WorkOutOdds", ""),
                         ("TryExact", ""), ("CheckExact", "")]:
        RR[name] = g.custom_event(name, params)


def reroll_actor_routines(g):
    def after(exits, node):
        """Wire every exit (node, pin) into node; returns node."""
        for src, pin in exits:
            g.link(src, pin, node, "execute")
        return node

    def tell(*parts):
        """(first node, exits): the text in the menu's status line, if the menu is open."""
        open_ = g.branch(rr_valid(g, (g.var("Menu"), "Menu")))
        said = rr_joined(g, *parts)
        as_text = g.call("/Script/Engine.KismetTextLibrary", "Conv_StringToText")
        g.link(said[0], said[1], as_text, "InString")
        put = g.call("/Script/UMG.TextBlock", "SetText")
        g.link(g.var("Status", owner=MENU_CLASS, target=(g.var("Menu"), "Menu")), "Status", put, "self")
        g.link(as_text, "ReturnValue", put, "InText")
        g.flow((open_, "then"), put)
        return open_, [(put, "then"), (open_, "else")]

    def refresh_menu():
        """The menu's ShowReroll (new balances), if it is open."""
        open_ = g.branch(rr_valid(g, (g.var("Menu"), "Menu")))
        node = g.call(MENU_CLASS, "ShowReroll")
        g.link(g.var("Menu"), "Menu", node, "self")
        g.flow((open_, "then"), node)
        return open_

    def storables():
        """(the GetAllActorsOfClass node - exec pins, (node, pin) of the items lying in the map)."""
        found = g.call("/Script/Engine.GameplayStatics", "GetAllActorsOfClass", ActorClass=STORABLE)
        return found, (found, "OutActors")

    def price_of(exact, gold):
        """(node, pin): the price (Prices, from WorkOutOdds) for the bools exact and gold ((node, pin) each)."""
        pair = g.call(MATH, "SelectInt", A=2, B=0)
        g.link(exact[0], exact[1], pair, "bPickA")
        one = g.call(MATH, "Conv_BoolToInt")
        g.link(gold[0], gold[1], one, "InBool")
        index = g.call(MATH, "Add_IntInt")
        g.link(pair, "ReturnValue", index, "A")
        g.link(one, "ReturnValue", index, "B")
        return g.item_at((g.var("Prices"), "Prices"), (index, "ReturnValue"))

    def currency_word(gold):
        pick = g.call(MATH, "SelectString", A=" gold", B=" emeralds")
        g.link(gold[0], gold[1], pick, "bPickA")
        return pick, "ReturnValue"

    def pay(gold, price):
        """The Deduct node (exec pins): price (node, pin) of Gold or Emerald by gold (node, pin)."""
        as_wallet, wallet = rr_wallet(g)
        node = g.call(WALLET, "Deduct")
        g.link(wallet[0], wallet[1], node, "self")
        currency = rr_currency(g, gold=gold)
        g.link(currency[0], currency[1], node, "Type")
        g.link(price[0], price[1], node, "Amount")
        g.flow(as_wallet, node)
        return as_wallet, node

    def loot_drop(kind, uniques, category=None, source=None):
        """(first, last) exec nodes: a LootDrop set to drop one item of kind (node, pin) - a plain kind may come out
        as one of its uniques when uniques - with the odds category (else as set before), then ServerDropItems
        at the player's feet. Our own LootDrop, or that of source (node, pin): a reroll dropper."""
        comp = (g.var("LootDrop"), "LootDrop") if not source else             (g.var("LootDrop", owner=DROPPER_CLASS, target=source), "LootDrop")
        table = g.node("/Script/BlueprintGraph.K2Node_MakeArray")
        g.link(kind[0], kind[1], table, "[0]")
        steps = []
        fields = [("LootTable", None), ("IncludeUniques", "true" if uniques else "false"), ("Proability", "1.0"),
                  ("MinCount", "1"), ("MaxCount", "1"), ("bEnableDrops", "true")]
        if category:
            fields.append(("rarityChanceCategory", category))
        for field, value in fields:
            put = g.var(field, set_=True, owner=LOOT, target=comp)
            if value is None:
                g.link(table, "Array", put, field)
            else:
                g.set(put, **{field: value})
            steps.append(put)
        call = g.call(LOOT, "ServerDropItems")
        g.link(comp[0], comp[1], call, "self")
        player = g.call("/Script/Engine.GameplayStatics", "GetPlayerCharacter", PlayerIndex=0)
        at = g.call("/Script/Engine.Actor", "K2_GetActorLocation")
        g.link(player, "ReturnValue", at, "self")
        g.link(at, "ReturnValue", call, "spawnLocation")
        g.link(player, "ReturnValue", call, "TriggeringPlayer")
        g.link(*((source or g.self_node()) + (call, "Source")))
        g.flow(*(steps + [call]))
        return steps[0], call

    # WorkOutOdds: AvgPower = the average power of the worn items (empty slots left out), OddsTier = how many of
    # ODDS_STEPS it reaches.
    g.row(5000)
    as_stash, stash = rr_stash(g)
    total, count = None, None
    for key in KEYS:
        item, data = rr_worn(g, stash, key=key)
        has = rr_valid(g, item)
        power = g.call(MATH, "SelectFloat", B=0.0)
        g.link(rr_break(g, data), "ItemPower", power, "A")
        g.link(has[0], has[1], power, "bPickA")
        one = g.call(MATH, "Conv_BoolToInt")
        g.link(has[0], has[1], one, "InBool")
        if total:
            add = g.call(MATH, "Add_FloatFloat")
            g.link(total[0], total[1], add, "A")
            g.link(power, "ReturnValue", add, "B")
            more = g.call(MATH, "Add_IntInt")
            g.link(count[0], count[1], more, "A")
            g.link(one, "ReturnValue", more, "B")
            total, count = (add, "ReturnValue"), (more, "ReturnValue")
        else:
            total, count = (power, "ReturnValue"), (one, "ReturnValue")
    at_least_one = g.call(MATH, "Max", B=1)
    g.link(count[0], count[1], at_least_one, "A")
    as_float = g.call(MATH, "Conv_IntToFloat")
    g.link(at_least_one, "ReturnValue", as_float, "InInt")
    avg = g.call(MATH, "Divide_FloatFloat")
    g.link(total[0], total[1], avg, "A")
    g.link(as_float, "ReturnValue", avg, "B")
    # ItemPower is the stored power: shown power = (stored - 1) * 10 + 1 (tools/bonus_watch.py) - 26.4 is 255.
    less_one = g.call(MATH, "Subtract_FloatFloat", B=1.0)
    g.link(avg, "ReturnValue", less_one, "A")
    tens = g.call(MATH, "Multiply_FloatFloat", B=10.0)
    g.link(less_one, "ReturnValue", tens, "A")
    shown = g.call(MATH, "Add_FloatFloat", B=1.0)
    g.link(tens, "ReturnValue", shown, "A")
    keep_avg = g.var("AvgPower", set_=True)
    g.link(shown, "ReturnValue", keep_avg, "AvgPower")
    tier = None
    for step in ODDS_STEPS:
        reached = g.call(MATH, "GreaterEqual_FloatFloat", B=step)
        g.link(g.var("AvgPower"), "AvgPower", reached, "A")
        one = g.call(MATH, "Conv_BoolToInt")
        g.link(reached, "ReturnValue", one, "InBool")
        if tier:
            add = g.call(MATH, "Add_IntInt")
            g.link(tier[0], tier[1], add, "A")
            g.link(one, "ReturnValue", add, "B")
            tier = (add, "ReturnValue")
        else:
            tier = (one, "ReturnValue")
    keep_tier = g.var("OddsTier", set_=True)
    g.link(tier[0], tier[1], keep_tier, "OddsTier")
    steps = []
    for index, (_, exact, gold, _, _) in enumerate(REROLL_BUTTONS):
        step = 1 if gold else 10   # emeralds to the nearest 10, gold whole
        scaled = g.call(MATH, "Multiply_FloatFloat", B=PRICES[(exact, gold)] / PRICE_POWER / step)
        g.link(g.var("AvgPower"), "AvgPower", scaled, "A")
        rounded = g.call(MATH, "Round")
        g.link(scaled, "ReturnValue", rounded, "A")
        whole = g.call(MATH, "Multiply_IntInt", B=step)
        g.link(rounded, "ReturnValue", whole, "A")
        least = g.call(MATH, "Max", B=0 if FREE else step)
        g.link(whole, "ReturnValue", least, "A")
        put = g.array_call("Array_Set", (g.var("Prices"), "Prices"), "TargetArray", Item=(least, "ReturnValue"))
        g.set(put, Index=index)
        steps.append(put)
    g.flow(*([RR["WorkOutOdds"], as_stash, keep_avg, keep_tier] + steps))

    # Reroll(Key, Exact, Gold): the worn item, the price, the wallet; then the drop.
    g.row(5600)
    ev = RR["Reroll"]
    busy = g.branch((g.var("Rerolling"), "Rerolling"))
    g.flow(ev, busy)
    g.flow((busy, "then"), tell("Still dropping the last exact copy - a moment...")[0])
    odds = g.self_call("WorkOutOdds")   # the odds and prices at the gear worn now
    as_stash, stash = rr_stash(g)
    item, data = rr_worn(g, stash, key_pin=(ev, "Key"))
    worn = g.branch(rr_valid(g, item))
    g.flow((busy, "else"), odds, as_stash, worn)
    g.flow((worn, "else"), tell("Nothing is worn in this slot.")[0])
    g.row(5900)
    # The worn item and its plain kind into variables first: read straight from the slot, the plain kind kept the
    # first weapon of the session (test 5, 2026-11-03: Spear worn, "a new Gauntlets dropped").
    keep_worn = g.var("RerollWorn", set_=True)
    g.link(data[0], data[1], keep_worn, "RerollWorn")
    broken = rr_break(g, (g.var("RerollWorn"), "RerollWorn"))
    keep_base = g.var("RerollBase", set_=True)
    plain = rr_base(g, (broken, "ItemId"))
    g.link(plain[0], plain[1], keep_base, "RerollBase")
    as_wallet, wallet = rr_wallet(g)
    currency = rr_currency(g, gold=(ev, "Gold"))
    price = price_of((ev, "Exact"), (ev, "Gold"))
    have = rr_balance(g, wallet, currency)
    enough = g.call(MATH, "GreaterEqual_IntInt")
    g.link(have[0], have[1], enough, "A")
    g.link(price[0], price[1], enough, "B")
    can_pay = g.branch((enough, "ReturnValue"))
    g.flow((worn, "then"), keep_worn, keep_base, as_wallet, can_pay)
    g.flow((can_pay, "else"), tell("Not enough: it costs ", rr_int_text(g, price), currency_word((ev, "Gold")),
                                   ", you have ", rr_int_text(g, have), ".")[0])
    exact = g.branch((ev, "Exact"))
    g.flow((can_pay, "then"), exact)

    def start_copy(entry, kind, worn=None):
        """From entry (node, pin): drop kind (node, pin of an item id) like an exact copy - remember what, the
        currency and price, the gilding of worn (the break node of the worn item; None: no gilding), note the items
        already lying here, TryExact."""
        keep_kind = g.var("RerollKind", set_=True)
        g.link(kind[0], kind[1], keep_kind, "RerollKind")
        keep_gold = g.var("RerollGold", set_=True)
        g.link(ev, "Gold", keep_gold, "RerollGold")
        keep_price = g.var("RerollPrice", set_=True)
        g.link(price[0], price[1], keep_price, "RerollPrice")
        keep_gilded = g.var("RerollGilded", set_=True)
        steps = [keep_kind, keep_gold, keep_price, keep_gilded]
        if worn:
            g.link(worn, "bHasNetherite", keep_gilded, "RerollGilded")
            keep_gilding = g.var("RerollGilding", set_=True)
            g.link(worn, "NetheriteEnchantData", keep_gilding, "RerollGilding")
            steps.append(keep_gilding)
        lying, lying_pin = storables()
        keep_seen = g.var("RerollSeen", set_=True)
        g.link(lying_pin[0], lying_pin[1], keep_seen, "RerollSeen")
        zero = g.var("RerollTries", set_=True)
        g.set(zero, RerollTries=0)
        start = g.var("Rerolling", set_=True)
        g.set(start, Rerolling="true")
        gilded_word = g.call(MATH, "SelectString", A=" (gilded, like yours)", B="")
        g.link(g.var("RerollGilded"), "RerollGilded", gilded_word, "bPickA")
        asking, exits = tell("Dropping ", rr_name(g, (g.var("RerollKind"), "RerollKind")),
                             (gilded_word, "ReturnValue"), " - trying until it comes out...")
        g.flow(*([entry] + steps + [lying, keep_seen, zero, start, asking]))
        after(exits, g.self_call("TryExact"))

    # Reroll, plain kind: the kind's uniques from the item list; with the tier's unique share one of them like an
    # exact copy, else the plain kind through a new dropper at the tier's odds, paid at once.
    g.row(6200)
    base = (g.var("RerollBase"), "RerollBase")
    family = (g.var("RerollFamily"), "RerollFamily")
    clear_family = g.array_call("Array_Clear", family, "TargetArray")
    last = g.array_call("Array_LastIndex", (g.var("AllNames"), "AllNames"), "TargetArray")
    loop = g.macro("ForLoop", FirstIndex=0)
    g.link(last, "ReturnValue", loop, "LastIndex")
    g.flow((exact, "else"), clear_family, loop)
    candidate = g.item_at((g.var("AllNames"), "AllNames"), (loop, "Index"))
    prefix = rr_joined(g, rr_id_text(g, base), "_Unique")   # a base's uniques: <base>_UniqueN
    starts = g.call(STRINGS, "StartsWith")
    g.link(candidate[0], candidate[1], starts, "SourceString")
    g.link(prefix[0], prefix[1], starts, "InPrefix")
    is_family = g.branch((starts, "ReturnValue"))
    add = g.array_call("Array_Add", (g.var("RerollFamily"), "RerollFamily"), "TargetArray", NewItem=(loop, "Index"))
    g.flow((loop, "LoopBody"), is_family)
    g.flow((is_family, "then"), add)
    g.row(6400)
    share = g.item_at((g.var("UniqueShares"), "UniqueShares"), (g.var("OddsTier"), "OddsTier"))
    roll = g.call(MATH, "RandomFloat")
    lucky = g.call(MATH, "Less_FloatFloat")
    g.link(roll, "ReturnValue", lucky, "A")
    g.link(share[0], share[1], lucky, "B")
    members = g.array_call("Array_Length", (g.var("RerollFamily"), "RerollFamily"), "TargetArray")
    some = g.call(MATH, "Greater_IntInt", B=0)
    g.link(members, "ReturnValue", some, "A")
    unique = g.call(MATH, "BooleanAND")
    g.link(lucky, "ReturnValue", unique, "A")
    g.link(some, "ReturnValue", unique, "B")
    gets_unique = g.branch((unique, "ReturnValue"))
    g.flow((loop, "Completed"), gets_unique)
    top = g.array_call("Array_LastIndex", (g.var("RerollFamily"), "RerollFamily"), "TargetArray")
    which = g.call(MATH, "RandomIntegerInRange", Min=0)
    g.link(top, "ReturnValue", which, "Max")
    chosen = g.item_at((g.var("RerollFamily"), "RerollFamily"), (which, "ReturnValue"))
    chosen_id = g.item_at((g.var("AllIds"), "AllIds"), chosen)
    start_copy((gets_unique, "then"), chosen_id)

    g.row(6600)
    spawn = g.node("/Script/BlueprintGraph.K2Node_SpawnActorFromClass")
    g.set(spawn, Class=DROPPER_CLASS)
    spot = g.call("/Script/Engine.Actor", "GetTransform")
    g.link(g.call("/Script/Engine.GameplayStatics", "GetPlayerCharacter", PlayerIndex=0), "ReturnValue", spot, "self")
    g.link(spot, "ReturnValue", spawn, "SpawnTransform")
    keep_dropper = g.var("RerollDropper", set_=True)
    g.link(spawn, "ReturnValue", keep_dropper, "RerollDropper")
    g.flow((gets_unique, "else"), spawn, keep_dropper)
    dropper = (g.var("RerollDropper"), "RerollDropper")
    first, call = loot_drop(base, False, source=dropper)
    prev = (keep_dropper, "then")
    for tier, category in enumerate(ODDS):
        is_t = g.call(MATH, "EqualEqual_IntInt", B=tier)
        g.link(g.var("OddsTier"), "OddsTier", is_t, "A")
        which_tier = g.branch((is_t, "ReturnValue"))
        g.link(prev[0], prev[1], which_tier, "execute")
        put = g.var("rarityChanceCategory", set_=True, owner=LOOT,
                    target=(g.var("LootDrop", owner=DROPPER_CLASS, target=dropper), "LootDrop"))
        g.set(put, rarityChanceCategory=category)
        g.flow((which_tier, "then"), put, first)
        prev = (which_tier, "else")
    g.link(prev[0], prev[1], first, "execute")
    paying, paid = pay((ev, "Gold"), price)
    told, exits = tell("Paid ", rr_int_text(g, price), currency_word((ev, "Gold")), ": a new ", rr_name(g, base),
                       " dropped at your feet.")
    expire = g.call("/Script/Engine.Actor", "SetLifeSpan", InLifespan=DROPPER_LIFE)
    g.link(dropper[0], dropper[1], expire, "self")
    g.flow(call, expire, paying)
    g.flow(paid, told)
    after(exits, refresh_menu())

    # Exact copy: the worn item's own id, gilded when it is.
    g.row(6800)
    start_copy((exact, "then"), (broken, "ItemId"), worn=broken)

    # TryExact: one drop of the exact kind with a boss's odds, then CheckExact after INTERVAL.
    g.row(7000)
    first, call = loot_drop((g.var("RerollKind"), "RerollKind"), False, category="Boss")
    plus = g.call(MATH, "Add_IntInt", B=1)
    g.link(g.var("RerollTries"), "RerollTries", plus, "A")
    keep_tries = g.var("RerollTries", set_=True)
    g.link(plus, "ReturnValue", keep_tries, "RerollTries")
    wait = g.call("/Script/Engine.KismetSystemLibrary", "K2_SetTimer", FunctionName="CheckExact", Time=INTERVAL)
    g.flow(RR["TryExact"], first)
    g.flow(call, keep_tries, wait)

    # CheckExact: of the items lying here that weren't before, one of the wanted kind is ours (others - a mob's
    # drop - are just noted): gild it like the worn one if that is gilded, pay and stop. Nothing new -> again, up
    # to TRIES.
    g.row(7400)
    clear_found = g.var("RerollFound", set_=True)
    now, now_pin = storables()
    last = g.array_call("Array_LastIndex", now_pin, "TargetArray")
    loop = g.macro("ForLoop", FirstIndex=0)
    g.link(last, "ReturnValue", loop, "LastIndex")
    g.flow(RR["CheckExact"], clear_found, now, loop)
    g.row(7700)
    each = g.item_at(now_pin, (loop, "Index"))
    known = g.array_call("Array_Contains", (g.var("RerollSeen"), "RerollSeen"), "TargetArray", ItemToFind=each)
    is_known = g.branch((known, "ReturnValue"))
    note = g.array_call("Array_Add", (g.var("RerollSeen"), "RerollSeen"), "TargetArray", NewItem=each)
    as_item, item_pin = g.cast(STORABLE, each)
    dropped = rr_break(g, (g.var("ItemData", owner=STORABLE, target=(as_item, item_pin)), "ItemData"))
    same = g.call(MATH, "EqualEqual_NameName")
    for side, item_id in [("A", (dropped, "ItemId")), ("B", (g.var("RerollKind"), "RerollKind"))]:
        id_parts = g.node("/Script/BlueprintGraph.K2Node_BreakStruct", StructType=ITEM_ID)
        g.link(item_id[0], item_id[1], id_parts, g.pins(id_parts)[0])
        g.link(id_parts, "SerializedId", same, side)
    is_ours = g.branch((same, "ReturnValue"))
    keep_found = g.var("RerollFound", set_=True)
    g.link(as_item, item_pin, keep_found, "RerollFound")
    g.flow((loop, "LoopBody"), is_known)
    g.flow((is_known, "else"), note, as_item, is_ours)
    g.flow((is_ours, "then"), keep_found)
    g.row(8000)
    found = g.branch(rr_valid(g, (g.var("RerollFound"), "RerollFound")))
    g.flow((loop, "Completed"), found)
    gild = g.branch((g.var("RerollGilded"), "RerollGilded"))
    g.flow((found, "then"), gild)
    # The dropped item's data copied into RerollData, its gilding set there (Set members - not a Make struct, which
    # keeps its first value), and written back.
    found_item = (g.var("RerollFound"), "RerollFound")
    copy = g.var("RerollData", set_=True)
    g.link(g.var("ItemData", owner=STORABLE, target=found_item), "ItemData", copy, "RerollData")
    members = g.node("/Script/BlueprintGraph.K2Node_SetFieldsInStruct", StructType=DATA,
                     ShowPinForProperties='((PropertyName="bHasNetherite",bShowPin=True),'
                                          '(PropertyName="NetheriteEnchantData",bShowPin=True))')
    shown = set(g.pins(members)) - {"execute", "then", "StructRef", "StructOut"}
    check(shown == {"bHasNetherite", "NetheriteEnchantData"}, "gilding members: " + ", ".join(sorted(shown)))
    g.link(g.var("RerollData"), "RerollData", members, "StructRef")
    g.set(members, bHasNetherite="true")
    g.link(g.var("RerollGilding"), "RerollGilding", members, "NetheriteEnchantData")
    gilded = g.var("ItemData", set_=True, owner=STORABLE, target=found_item)
    g.link(g.var("RerollData"), "RerollData", gilded, "ItemData")
    g.flow((gild, "then"), copy, members, gilded)
    room = g.call(MATH, "Less_IntInt", B=TRIES)
    g.link(g.var("RerollTries"), "RerollTries", room, "A")
    again = g.branch((room, "ReturnValue"))
    g.flow((found, "else"), again)
    g.flow((again, "then"), g.self_call("TryExact"))
    stop = g.var("Rerolling", set_=True)
    g.flow((again, "else"), stop, tell("No copy came out after ", rr_int_text(g, (g.var("RerollTries"), "RerollTries")),
                                       " tries - nothing was paid.")[0])
    g.row(8300)
    gold = (g.var("RerollGold"), "RerollGold")
    price = (g.var("RerollPrice"), "RerollPrice")
    as_wallet, wallet = rr_wallet(g)
    have = rr_balance(g, wallet, rr_currency(g, gold=gold))
    enough = g.call(MATH, "GreaterEqual_IntInt")
    g.link(have[0], have[1], enough, "A")
    g.link(price[0], price[1], enough, "B")
    still = g.branch((enough, "ReturnValue"))
    g.flow(as_wallet, still)
    clear_away = g.call(STORABLE, "TimeToPoolFinished")
    g.link(g.var("RerollFound"), "RerollFound", clear_away, "self")
    broke = g.var("Rerolling", set_=True)
    g.flow((still, "else"), clear_away, broke, tell("Not enough any more: it costs ", rr_int_text(g, price),
                                                    currency_word(gold), " - the copy was taken back.")[0])
    paying, paid = pay(gold, price)
    g.flow((still, "then"), paying)
    done = g.var("Rerolling", set_=True)
    told, exits = tell("Paid ", rr_int_text(g, price), currency_word(gold), ": a new ",
                       rr_name(g, (g.var("RerollKind"), "RerollKind")), " dropped at your feet (after ",
                       rr_int_text(g, (g.var("RerollTries"), "RerollTries")), " tries).")
    g.flow((gild, "else"), as_wallet)
    g.flow(gilded, as_wallet)
    g.flow(paid, done, told)
    after(exits, refresh_menu())

