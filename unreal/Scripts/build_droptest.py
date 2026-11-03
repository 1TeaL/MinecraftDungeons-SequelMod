"""Test build: can our blueprint make the game drop a new copy of an item kind (for an emerald "reroll")?

The normal build (transmog + super bosses), plus BP_SequelDropTest, which the loader also starts:
    Test 6: both keys drop through our own LootDrop component (the game's ULootTableItemDropComponent, the kind
    mobs and chests drop with), which takes the rarity odds to use (ODDS) and, for plain kinds, IncludeUniques.
    O   asks the game's item dropper (AItemDropActor - the map's own if it has one, else one of ours, made once) for
        one item of the exact kind of melee weapon you wear, at your feet: DropItems(there, that kind, 1, you, locked
        to you) - every INTERVAL seconds until the map has one more item, at most TRIES times; the text says how many
        tries it took (a unique is mostly refused for a while after one dropped - test 4).
    P   one item of the plain kind: a unique's id cut back to its weapon (Gauntlets_Unique3 -> Gauntlets), so the
        game picks the rarity itself.
The game rolls the new item itself (enchantments, power, gilding) - the test is whether it drops, and what it gets.
A text at the top left, every second: the last result, how often it was asked, the melee weapon worn, how many
droppers, storable items and item actors the map has (to see whether a press made an item), and the
emeralds and gold the game's wallet reports (read only - nothing is taken). Nothing is written to any save by us; a
picked-up item is saved by the game itself.

Run headless: python tools/blueprints.py build_droptest   (the normal build_transmog drops the test again)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from seqbp import *  # noqa: E402,F401,F403
import seqbp  # noqa: E402

seqbp.start(__file__)

TEST = "/Game/SequelMod/BP_SequelDropTest"
VIEW = "/Game/SequelMod/WBP_SequelDropTest"
TEST_CLASS = TEST + ".BP_SequelDropTest_C"
VIEW_CLASS = VIEW + ".WBP_SequelDropTest_C"
STASH = "/Script/Dungeons.ItemStashComponent"
SLOT = "/Script/Dungeons.InventoryItemSlot"
ITEM = "/Script/Dungeons.InventoryItem"
DATA = "/Script/Dungeons.InventoryItemData"
ITEM_ID = "/Script/Dungeons.SerializableItemId"
LOOT = "/Script/Dungeons.LootTableItemDropComponent"
ODDS = "Boss"   # the rarity odds both keys use (EItemRarityChanceCategory): Boss = common 0, rare 50, unique 50
DROPPER = "/Script/Dungeons.ItemDropActor"
WALLET = "/Script/Dungeons.WalletComponent"
STR = "/Script/Engine.KismetStringLibrary"
MATH = "/Script/Engine.KismetMathLibrary"
STATICS = "/Script/Engine.GameplayStatics"
TRIES = 240     # O: drop calls per press at most (2 minutes): a unique is mostly refused for a while after one dropped
INTERVAL = 0.5  # seconds between them - the item appears a moment after the call, so the check waits

# The text at the top left.
view = fresh(VIEW, unreal.WidgetBlueprint, unreal.WidgetBlueprintFactory())
widget(view, "", unreal.CanvasPanel, "Root")
line = label(view, "Root", "Info", "Drop test", 18, is_variable=True)
spot = line.get_editor_property("slot")
spot.set_position(unreal.Vector2D(40, 40))
spot.set_size(unreal.Vector2D(1600, 400))
line.set_auto_wrap_text(True)
compile_save(view, "test view")

bp = blueprint(TEST, unreal.Actor)
for name, kind in [("View", "object:" + VIEW_CLASS), ("Status", "string"), ("Dropper", "object:" + DROPPER),
                   ("Asked", "int"), ("Before", "int"), ("Tries", "int")]:
    check(LIB.add_variable(bp, name, kind), "variable " + name)
check(LIB.add_component(bp, unreal.LootTableItemDropComponent, "LootDrop") is not None, "loot drop component")
LIB.compile(bp)   # so the graph can use the component
g = Graph(bp)


def joined(*parts):
    """A string from parts: plain strings or (node, pin) of strings."""
    out = None
    for part in parts:
        concat = g.call(STR, "Concat_StrStr")
        if out:
            g.link(out[0], out[1], concat, "A")
        for pin, value in [("B", part)] if out else [("A", part), ("B", "")]:
            if isinstance(value, tuple):
                g.link(value[0], value[1], concat, pin)
            else:
                g.set(concat, **{pin: value})
        out = (concat, "ReturnValue")
    return out


def set_status(*parts):
    setter = g.var("Status", set_=True)
    text = joined(*parts)
    g.link(text[0], text[1], setter, "Status")
    return setter


def int_text(value):
    node = g.call(STR, "Conv_IntToString")
    g.link(value[0], value[1], node, "InInt")
    return node, "ReturnValue"


def name_text(item_id):
    name = g.call("/Script/Dungeons.ItemFunctionLibrary", "GetNameForItemType")
    g.link(item_id[0], item_id[1], name, "Type")
    text = g.call("/Script/Engine.KismetTextLibrary", "Conv_TextToString")
    g.link(name, "ReturnValue", text, "InText")
    return text, "ReturnValue"


def player():
    return g.call(STATICS, "GetPlayerCharacter", PlayerIndex=0), "ReturnValue"


def worn_melee():
    """(cast node, (break node of the worn melee weapon's InventoryItemData)). The cast has exec pins."""
    stash = g.call("/Script/Engine.Actor", "GetComponentByClass", ComponentClass=STASH)
    who = player()
    g.link(who[0], who[1], stash, "self")
    as_stash, stash_pin = g.cast(STASH, (stash, "ReturnValue"))
    slots = g.call(STASH, "GetEquipmentSlots")
    g.link(as_stash, stash_pin, slots, "self")
    find = g.call("/Script/Engine.BlueprintMapLibrary", "Map_Find")
    g.link(slots, "ReturnValue", find, "TargetMap")
    g.set(find, Key="MeleeGear")   # after the map is linked: before, the key pin has no type and reads slot 0
    item = g.var("Item", owner=SLOT, target=(find, "Value"))
    data = g.var("Item", owner=ITEM, target=(item, "Item"))
    broken = g.node("/Script/BlueprintGraph.K2Node_BreakStruct", StructType=DATA)
    g.link(data, "Item", broken, g.pins(broken)[0])
    return as_stash, broken


def spot(ahead):
    """(node, pin): where to drop - the player's feet, or 200 units in front of them."""
    who = player()
    at = g.call("/Script/Engine.Actor", "K2_GetActorLocation")
    g.link(who[0], who[1], at, "self")
    if not ahead:
        return at, "ReturnValue"
    forward = g.call("/Script/Engine.Actor", "GetActorForwardVector")
    g.link(who[0], who[1], forward, "self")
    far = g.call(MATH, "Multiply_VectorFloat", B=200.0)
    g.link(forward, "ReturnValue", far, "A")
    there = g.call(MATH, "Add_VectorVector")
    g.link(at, "ReturnValue", there, "A")
    g.link(far, "ReturnValue", there, "B")
    return there, "ReturnValue"


def count_of(cls):
    """(the GetAllActorsOfClass node - it has exec pins, (node, pin) of how many there are)."""
    found = g.call(STATICS, "GetAllActorsOfClass", ActorClass=cls)
    n = g.array_call("Array_Length", (found, "OutActors"), "TargetArray")
    return found, (n, "ReturnValue")


# BeginPlay: show the text, listen for keys after 3 s (the player controller may not exist yet), Refresh every 1 s.
g.row(0)
begin = g.event("/Script/Engine.Actor", "ReceiveBeginPlay")
make_view = g.node("/Script/UMGEditor.K2Node_CreateWidget")
g.set(make_view, Class=VIEW_CLASS)
set_view = g.var("View", set_=True)
g.link(make_view, "ReturnValue", set_view, "View")
show = g.call("/Script/UMG.UserWidget", "AddToViewport")
g.link(make_view, "ReturnValue", show, "self")
listen_timer = g.call("/Script/Engine.KismetSystemLibrary", "K2_SetTimer", FunctionName="Listen", Time=3.0)
refresh_timer = g.call("/Script/Engine.KismetSystemLibrary", "K2_SetTimer", FunctionName="Refresh", Time=1.0,
                       bLooping="true")
ready = set_status("ready")
g.flow(begin, make_view, set_view, show, listen_timer, refresh_timer, ready)

g.row(300)
listen = g.custom_event("Listen")
controller = g.call(STATICS, "GetPlayerController", PlayerIndex=0)
enable = g.call("/Script/Engine.Actor", "EnableInput")
g.link(controller, "ReturnValue", enable, "PlayerController")
g.flow(listen, enable)

g.row(500)
end = g.event("/Script/Engine.Actor", "ReceiveEndPlay")
hide = g.call("/Script/UMG.Widget", "RemoveFromParent")
g.link(g.var("View"), "View", hide, "self")
g.flow(end, hide)

# FindDropper: the one dropper we use - the map's own if it has one, else one of our own (made once).
g.row(800)
make = g.custom_event("FindDropper")
have = g.call("/Script/Engine.KismetSystemLibrary", "IsValid")
g.link(g.var("Dropper"), "Dropper", have, "Object")
has_it = g.branch((have, "ReturnValue"))
found, n = count_of(DROPPER)
some = g.call(MATH, "Greater_IntInt", B=0)
g.link(n[0], n[1], some, "A")
map_has = g.branch((some, "ReturnValue"))
g.flow(make, has_it)
g.flow((has_it, "else"), found, map_has)
g.row(1100)
first = g.item_at((found, "OutActors"))
as_dropper, dropper_pin = g.cast(DROPPER, first)
keep = g.var("Dropper", set_=True)
g.link(as_dropper, dropper_pin, keep, "Dropper")
g.flow((map_has, "then"), as_dropper, keep)
spawn = g.node("/Script/BlueprintGraph.K2Node_SpawnActorFromClass")
g.set(spawn, Class=DROPPER)
who = player()
here = g.call("/Script/Engine.Actor", "GetTransform")
g.link(who[0], who[1], here, "self")
g.link(here, "ReturnValue", spawn, "SpawnTransform")
keep_own = g.var("Dropper", set_=True)
g.link(spawn, "ReturnValue", keep_own, "Dropper")
g.flow((map_has, "else"), spawn, keep_own)

def item_count():
    """([the two GetAllActorsOfClass nodes - exec pins], (node, pin) of storable items + item actors in the map)."""
    storables, n_storable = count_of("/Script/Dungeons.StorableItem")
    items, n_item = count_of("/Script/Dungeons.ItemActor")
    total = g.call(MATH, "Add_IntInt")
    g.link(n_storable[0], n_storable[1], total, "A")
    g.link(n_item[0], n_item[1], total, "B")
    return [storables, items], (total, "ReturnValue")


def base_kind(item_id):
    """(node, pin): the item id with any _UniqueN cut off - Gauntlets_Unique3 (Fighter's Bindings) -> Gauntlets."""
    broken = g.node("/Script/BlueprintGraph.K2Node_BreakStruct", StructType=ITEM_ID)
    g.link(item_id[0], item_id[1], broken, g.pins(broken)[0])
    as_text = g.call(STR, "Conv_NameToString")
    g.link(broken, "SerializedId", as_text, "InName")
    at = g.call(STR, "FindSubstring", Substring="_Unique")
    g.link(as_text, "ReturnValue", at, "SearchIn")
    cut = g.call(STR, "Left")
    g.link(as_text, "ReturnValue", cut, "SourceString")
    g.link(at, "ReturnValue", cut, "Count")
    pick = g.call(MATH, "SelectString")
    g.link(cut, "ReturnValue", pick, "A")
    g.link(as_text, "ReturnValue", pick, "B")
    unique = g.at_least_zero((at, "ReturnValue"))
    g.link(unique[0], unique[1], pick, "bPickA")
    name = g.call(STR, "Conv_StringToName")
    g.link(pick, "ReturnValue", name, "InString")
    made = g.node("/Script/BlueprintGraph.K2Node_MakeStruct", StructType=ITEM_ID)
    g.link(name, "ReturnValue", made, "SerializedId")
    return made, "SerializableItemId"


def loot_drop(kind, uniques):
    """(first, last) exec nodes: our LootDrop component set to drop one item of kind (node, pin) with ODDS - plain
    kinds may come out as one of their uniques when uniques is True - then ServerDropItems at the player's feet."""
    comp = (g.var("LootDrop"), "LootDrop")
    table = g.node("/Script/BlueprintGraph.K2Node_MakeArray")
    g.link(kind[0], kind[1], table, "[0]")
    steps = []
    for field, value in [("LootTable", None), ("IncludeUniques", "true" if uniques else "false"),
                         ("rarityChanceCategory", ODDS), ("Proability", "1.0"), ("MinCount", "1"),
                         ("MaxCount", "1"), ("bEnableDrops", "true")]:
        put = g.var(field, set_=True, owner=LOOT, target=comp)
        if value is None:
            g.link(table, "Array", put, field)
        else:
            g.set(put, **{field: value})
        steps.append(put)
    call = g.call(LOOT, "ServerDropItems")
    g.link(comp[0], comp[1], call, "self")
    where = spot(False)
    g.link(where[0], where[1], call, "spawnLocation")
    who = player()
    g.link(who[0], who[1], call, "TriggeringPlayer")
    g.link(*(g.self_node() + (call, "Source")))
    g.flow(*(steps + [call]))
    return steps[0], call


def pressed_key(key):
    """(key node, cast node, worn melee break, branch "dropper usable") - the start every key shares; Asked + 1."""
    pressed = g.node("/Script/BlueprintGraph.K2Node_InputKey", InputKey=key, bConsumeInput="False")
    as_stash, melee = worn_melee()
    get = g.self_call("FindDropper")
    ok = g.call("/Script/Engine.KismetSystemLibrary", "IsValid")
    g.link(g.var("Dropper"), "Dropper", ok, "Object")
    usable = g.branch((ok, "ReturnValue"))
    plus = g.call(MATH, "Add_IntInt", B=1)
    g.link(g.var("Asked"), "Asked", plus, "A")
    bump = g.var("Asked", set_=True)
    g.link(plus, "ReturnValue", bump, "Asked")
    g.flow((pressed, "Pressed"), as_stash, get, bump, usable)
    g.flow((usable, "else"), set_status(key + ": no dropper"))
    g.flow((as_stash, "CastFailed"), set_status(key + ": no inventory found"))
    return as_stash, melee, usable


# O: the worn melee weapon's exact kind, one call every INTERVAL s until the map has one more item (the spawn
# comes a moment after the call), at most TRIES calls. TryExact drops and sets the CheckExact timer; CheckExact
# stops on a new item, else tries again.
g.row(1900)
try_exact = g.custom_event("TryExact")
as_stash, melee = worn_melee()
first, call = loot_drop((melee, "ItemId"), False)
plus = g.call(MATH, "Add_IntInt", B=1)
g.link(g.var("Tries"), "Tries", plus, "A")
keep_tries = g.var("Tries", set_=True)
g.link(plus, "ReturnValue", keep_tries, "Tries")
wait = g.call("/Script/Engine.KismetSystemLibrary", "K2_SetTimer", FunctionName="CheckExact", Time=INTERVAL)
g.flow(try_exact, as_stash, first)
g.flow(call, keep_tries, wait)

g.row(2200)
check_exact = g.custom_event("CheckExact")
after_counts, after = item_count()
more = g.call(MATH, "Greater_IntInt")
g.link(after[0], after[1], more, "A")
g.link(g.var("Before"), "Before", more, "B")
got = g.branch((more, "ReturnValue"))
room = g.call(MATH, "Less_IntInt", B=TRIES)
g.link(g.var("Tries"), "Tries", room, "A")
again = g.branch((room, "ReturnValue"))
g.row(2400)
done = set_status("O: dropped after ", int_text((g.var("Tries"), "Tries")), " tries (half a second each)")
gave_up = set_status("O: nothing after ", int_text((g.var("Tries"), "Tries")), " tries")
g.flow(*([check_exact] + after_counts + [got]))
g.flow((got, "then"), done)
g.flow((got, "else"), again)
g.flow((again, "then"), g.self_call("TryExact"))
g.flow((again, "else"), gave_up)

# The O key (after TryExact exists, which it calls).
g.row(1500)
as_stash, melee, usable = pressed_key("O")
before_counts, before = item_count()
keep_before = g.var("Before", set_=True)
g.link(before[0], before[1], keep_before, "Before")
zero = g.var("Tries", set_=True)
g.set(zero, Tries=0)
g.row(1700)
asking = set_status("O: asking for exactly ", name_text((melee, "ItemId")), " (" + ODDS + " odds) every half second...")
g.flow(*([(usable, "then")] + before_counts + [keep_before, zero, asking, g.self_call("TryExact")]))

# P: one item of the plain kind (uniques cut back to the plain weapon) - the game picks the rarity.
g.row(2600)
as_stash, melee, usable = pressed_key("P")
kind = base_kind((melee, "ItemId"))
first, call = loot_drop(kind, True)
g.flow((usable, "then"), first)
g.flow(call, set_status("P: asked for one ", name_text(kind), " (uniques included, " + ODDS + " odds)"))

# Refresh: "Drop test (...) | <status> || melee: <name> (power) || droppers in this map: N || emeralds: N"
g.row(3000)
refresh = g.custom_event("Refresh")
as_stash, melee = worn_melee()
power = g.call(STR, "Conv_FloatToString")
g.link(melee, "ItemPower", power, "InFloat")
droppers, n = count_of(DROPPER)
storables, n_storable = count_of("/Script/Dungeons.StorableItem")
items, n_item = count_of("/Script/Dungeons.ItemActor")
g.row(3300)
wallet = g.call("/Script/Engine.Actor", "GetComponentByClass", ComponentClass=WALLET)
who = player()
g.link(who[0], who[1], wallet, "self")
as_wallet, wallet_pin = g.cast(WALLET, (wallet, "ReturnValue"))
balances = []
for currency in ("Emerald", "Gold"):
    kind = g.node("/Script/BlueprintGraph.K2Node_MakeStruct", StructType=ITEM_ID)
    g.set(kind, SerializedId=currency)
    balance = g.call(WALLET, "Balance")
    g.link(as_wallet, wallet_pin, balance, "self")
    g.link(kind, "SerializableItemId", balance, "Type")
    balances.append((balance, "ReturnValue"))
said = joined("Drop test (O: this exact item, P: the plain kind) | ", (g.var("Status"), "Status"),
              " || asked ", int_text((g.var("Asked"), "Asked")), " times",
              " || melee worn: ", name_text((melee, "ItemId")), " (", (power, "ReturnValue"), ")",
              " || in this map: droppers ", int_text(n), ", storable items ", int_text(n_storable),
              ", item actors ", int_text(n_item),
              " || emeralds: ", int_text(balances[0]), ", gold: ", int_text(balances[1]))
as_text = g.call("/Script/Engine.KismetTextLibrary", "Conv_StringToText")
g.link(said[0], said[1], as_text, "InString")
set_text = g.call("/Script/UMG.TextBlock", "SetText")
g.link(g.var("Info", owner=VIEW_CLASS, target=(g.var("View"), "View")), "Info", set_text, "self")
g.link(as_text, "ReturnValue", set_text, "InText")
g.flow(refresh, as_stash, droppers, storables, items, as_wallet, set_text)
compile_save(bp, "test actor")

# The normal build, with the loader also starting the test.
EXTRA_ACTORS = [TEST_CLASS]
transmog = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_transmog.py")
exec(compile(open(transmog).read(), transmog, "exec"), dict(globals(), __file__=__file__))
