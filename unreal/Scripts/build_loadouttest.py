"""Test build: can our blueprint equip items the way the inventory screen does (for loadouts)?

The normal build (transmog + super bosses), plus BP_SequelLoadoutTest, which the loader also starts:
    O   remembers what you wear (the inventory screen's 6 equipment slots: 3 artifacts, melee, ranged, armor) -
        in memory only, gone when the mission or camp ends.
    P   puts it back: for each remembered item, finds it in the inventory (same type, power, rarity) and swaps it
        into its equipment slot with the inventory screen's own Swap, if CanSwapWith allows.
    L   the same, between the inventory screen's EnterInventoryUI / ExitInventoryUI (in case the game only takes
        the changes when the screen closes).
A text at the top left, every second: the last result, what the inventory screen's slots hold, and what the
character really holds (its EquipmentComponent slots) - the test is whether the second follows the first.
Nothing is written to any save by us; the game saves the swapped gear itself, as after the inventory screen.

Run headless: python tools/blueprints.py build_loadouttest   (the normal build_transmog drops the test again)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from seqbp import *  # noqa: E402,F401,F403
import seqbp  # noqa: E402

seqbp.start(__file__)

TEST = "/Game/SequelMod/BP_SequelLoadoutTest"
VIEW = "/Game/SequelMod/WBP_SequelLoadoutTest"
TEST_CLASS = TEST + ".BP_SequelLoadoutTest_C"
VIEW_CLASS = VIEW + ".WBP_SequelLoadoutTest_C"
STASH = "/Script/Dungeons.ItemStashComponent"
SLOT = "/Script/Dungeons.InventoryItemSlot"
ITEM = "/Script/Dungeons.InventoryItem"
DATA = "/Script/Dungeons.InventoryItemData"
MAPS = "/Script/Engine.BlueprintMapLibrary"
STR = "/Script/Engine.KismetStringLibrary"
MATH = "/Script/Engine.KismetMathLibrary"
COUNTERS = ["Swapped", "Already", "Missing", "Refused"]

# The text at the top left.
view = fresh(VIEW, unreal.WidgetBlueprint, unreal.WidgetBlueprintFactory())
widget(view, "", unreal.CanvasPanel, "Root")
line = label(view, "Root", "Info", "Loadout test", 18, is_variable=True)
spot = line.get_editor_property("slot")
spot.set_position(unreal.Vector2D(40, 40))
spot.set_size(unreal.Vector2D(1600, 400))
line.set_auto_wrap_text(True)
compile_save(view, "test view")

bp = blueprint(TEST, unreal.Actor)
for name, kind in [("View", "object:" + VIEW_CLASS), ("Status", "string"), ("Saved", "array:struct:" + DATA),
                   ("SavedKeys", "array:enum:/Script/Dungeons.EEquipmentSlot"), ("Found", "bool"),
                   ("FoundSlot", "object:" + SLOT)] + [(c, "int") for c in COUNTERS]:
    check(LIB.add_variable(bp, name, kind), "variable " + name)
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


def loop_over(array, with_break=False):
    """A ForLoop(WithBreak) over array (node, pin). Returns (loop, item (node, pin))."""
    last = g.array_call("Array_LastIndex", array, "TargetArray")
    loop = g.macro("ForLoopWithBreak" if with_break else "ForLoop", FirstIndex=0)
    g.link(last, "ReturnValue", loop, "LastIndex")
    return loop, g.item_at(array, (loop, "Index"))


def stash_of_player():
    """(cast node, its As pin): the player's ItemStashComponent. The cast has exec pins."""
    player = g.call("/Script/Engine.GameplayStatics", "GetPlayerCharacter", PlayerIndex=0)
    stash = g.call("/Script/Engine.Actor", "GetComponentByClass", ComponentClass=STASH)
    g.link(player, "ReturnValue", stash, "self")
    return g.cast(STASH, (stash, "ReturnValue"))


def equipment_slot(stash, key=None, key_pin=None):
    """The inventory screen's equipment slot for key (a literal EEquipmentSlot name or a (node, pin)).
    Returns (Map_Find node, its Value pin) - a pure node."""
    slots = g.call(STASH, "GetEquipmentSlots")
    g.link(stash[0], stash[1], slots, "self")
    find = g.call(MAPS, "Map_Find")
    g.link(slots, "ReturnValue", find, "TargetMap")
    if key_pin:
        g.link(key_pin[0], key_pin[1], find, "Key")
    else:
        g.set(find, Key=key)
    return find, "Value"


def item_of(slot):
    """(node, pin) of the InventoryItem in an InventoryItemSlot (node, pin)."""
    return g.var("Item", owner=SLOT, target=slot), "Item"


def data_of(item):
    return g.var("Item", owner=ITEM, target=item), "Item"


def same_item(a, b):
    """(node, pin) of a bool: InventoryItemData a and b are the same type, power and rarity."""
    parts = []
    for data in (a, b):
        broken = g.node("/Script/BlueprintGraph.K2Node_BreakStruct", StructType=DATA)
        g.link(data[0], data[1], broken, g.pins(broken)[0])
        item_id = g.node("/Script/BlueprintGraph.K2Node_BreakStruct", StructType="/Script/Dungeons.SerializableItemId")
        g.link(broken, "ItemId", item_id, g.pins(item_id)[0])
        parts.append((broken, item_id))
    tests = []
    for fn, pin, which in [("EqualEqual_NameName", "SerializedId", 1), ("EqualEqual_FloatFloat", "ItemPower", 0),
                           ("EqualEqual_ByteByte", "Rarity", 0)]:
        test = g.call(MATH, fn)
        g.link(parts[0][which], pin, test, "A")
        g.link(parts[1][which], pin, test, "B")
        tests.append(test)
    both = g.call(MATH, "BooleanAND")
    g.link(tests[0], "ReturnValue", both, "A")
    g.link(tests[1], "ReturnValue", both, "B")
    all_three = g.call(MATH, "BooleanAND")
    g.link(both, "ReturnValue", all_three, "A")
    g.link(tests[2], "ReturnValue", all_three, "B")
    return all_three, "ReturnValue"


def valid(obj):
    node = g.call("/Script/Engine.KismetSystemLibrary", "IsValid")
    g.link(obj[0], obj[1], node, "Object")
    return node, "ReturnValue"


def bump(counter):
    """A Set node: counter = counter + 1."""
    plus = g.call(MATH, "Add_IntInt", B=1)
    g.link(g.var(counter), counter, plus, "A")
    setter = g.var(counter, set_=True)
    g.link(plus, "ReturnValue", setter, counter)
    return setter


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
ready = set_status("O = remember what you wear")
g.flow(begin, make_view, set_view, show, listen_timer, refresh_timer, ready)

g.row(300)
listen = g.custom_event("Listen")
controller = g.call("/Script/Engine.GameplayStatics", "GetPlayerController", PlayerIndex=0)
enable = g.call("/Script/Engine.Actor", "EnableInput")
g.link(controller, "ReturnValue", enable, "PlayerController")
g.flow(listen, enable)

g.row(500)
end = g.event("/Script/Engine.Actor", "ReceiveEndPlay")
hide = g.call("/Script/UMG.Widget", "RemoveFromParent")
g.link(g.var("View"), "View", hide, "self")
g.flow(end, hide)

# O Remember: each equipment slot with an item -> Saved (its data) + SavedKeys (which slot).
g.row(800)
f7 = g.node("/Script/BlueprintGraph.K2Node_InputKey", InputKey="O", bConsumeInput="False")
as_stash, stash_pin = stash_of_player()
clear_saved = g.array_call("Array_Clear", (g.var("Saved"), "Saved"), "TargetArray")
clear_keys = g.array_call("Array_Clear", (g.var("SavedKeys"), "SavedKeys"), "TargetArray")
slots = g.call(STASH, "GetEquipmentSlots")
g.link(as_stash, stash_pin, slots, "self")
keys = g.call(MAPS, "Map_Keys")
g.link(slots, "ReturnValue", keys, "TargetMap")
values = g.call(MAPS, "Map_Values")
g.link(slots, "ReturnValue", values, "TargetMap")
loop, slot = loop_over((values, "Values"))
g.flow((f7, "Pressed"), as_stash, clear_saved, clear_keys, keys, values, loop)
g.row(1100)
item = item_of(slot)
has_item = g.branch(valid(item))
add_data = g.array_call("Array_Add", (g.var("Saved"), "Saved"), "TargetArray", NewItem=data_of(item))
add_key = g.array_call("Array_Add", (g.var("SavedKeys"), "SavedKeys"), "TargetArray",
                       NewItem=g.item_at((keys, "Keys"), (loop, "Index")))
g.flow((loop, "LoopBody"), has_item)
g.flow((has_item, "then"), add_data, add_key)
count = g.array_call("Array_Length", (g.var("Saved"), "Saved"), "TargetArray")
remembered = set_status("O: remembered ", int_text((count, "ReturnValue")), " items. Change gear, then P (or L)")
g.flow((loop, "Completed"), remembered)

# Equip: for each remembered item, already there / swap it in from the inventory / missing / refused.
g.row(1500)
equip = g.custom_event("Equip")
as_stash, stash_pin = stash_of_player()
steps = [equip, as_stash]
for counter in COUNTERS:
    zero = g.var(counter, set_=True)
    g.set(zero, **{counter: 0})
    steps.append(zero)
outer, wanted = loop_over((g.var("Saved"), "Saved"))
g.flow(*(steps + [outer]))
g.row(1800)
target, target_pin = equipment_slot((as_stash, stash_pin), key_pin=g.item_at((g.var("SavedKeys"), "SavedKeys"),
                                                                              (outer, "Index")))
current = item_of((target, target_pin))
there_already = g.call(MATH, "BooleanAND")
current_ok = valid(current)
g.link(current_ok[0], current_ok[1], there_already, "A")
match_now = same_item(data_of(current), wanted)
g.link(match_now[0], match_now[1], there_already, "B")
is_there = g.branch((there_already, "ReturnValue"))
g.flow((outer, "LoopBody"), is_there)
g.flow((is_there, "then"), bump("Already"))
g.row(2100)
not_found = g.var("Found", set_=True)
g.set(not_found, Found="false")
inventory = g.call(STASH, "GetInventorySlots")
g.link(as_stash, stash_pin, inventory, "self")
inner, cell = loop_over((inventory, "ReturnValue"), with_break=True)
g.flow((is_there, "else"), not_found, inner)
g.row(2400)
cell_item = item_of(cell)
is_it = g.call(MATH, "BooleanAND")
cell_ok = valid(cell_item)
g.link(cell_ok[0], cell_ok[1], is_it, "A")
match_cell = same_item(data_of(cell_item), wanted)
g.link(match_cell[0], match_cell[1], is_it, "B")
hit = g.branch((is_it, "ReturnValue"))
found = g.var("Found", set_=True)
g.set(found, Found="true")
keep = g.var("FoundSlot", set_=True)
g.link(cell[0], cell[1], keep, "FoundSlot")
g.flow((inner, "LoopBody"), hit)
g.flow((hit, "then"), found, keep)
g.link(keep, "then", inner, "Break")
g.row(2700)
was_found = g.branch((g.var("Found"), "Found"))
allowed = g.call(SLOT, "CanSwapWith")
g.link(target, target_pin, allowed, "self")
g.link(g.var("FoundSlot"), "FoundSlot", allowed, "Other")
may_swap = g.branch((allowed, "ReturnValue"))
swap = g.call(SLOT, "Swap")
g.link(target, target_pin, swap, "self")
g.link(g.var("FoundSlot"), "FoundSlot", swap, "Other")
g.flow((inner, "Completed"), was_found, may_swap, swap, bump("Swapped"))
g.flow((was_found, "else"), bump("Missing"))
g.flow((may_swap, "else"), bump("Refused"))
g.row(3000)
report = set_status("swapped ", int_text((g.var("Swapped"), "Swapped")), ", already worn ",
                    int_text((g.var("Already"), "Already")), ", not in inventory ",
                    int_text((g.var("Missing"), "Missing")), ", refused ", int_text((g.var("Refused"), "Refused")))
g.flow((outer, "Completed"), report)

# P: Equip. L: Equip inside EnterInventoryUI / ExitInventoryUI.
g.row(3300)
f8 = g.node("/Script/BlueprintGraph.K2Node_InputKey", InputKey="P", bConsumeInput="False")
plain = set_status("P (plain)")
g.flow((f8, "Pressed"), plain, g.self_call("Equip"))
f9 = g.node("/Script/BlueprintGraph.K2Node_InputKey", InputKey="L", bConsumeInput="False")
as_stash, stash_pin = stash_of_player()
enter = g.call(STASH, "EnterInventoryUI")
g.link(as_stash, stash_pin, enter, "self")
leave = g.call(STASH, "ExitInventoryUI")
g.link(as_stash, stash_pin, leave, "self")
g.flow((f9, "Pressed"), as_stash, enter, g.self_call("Equip"), leave)

# Refresh: "Loadout test | <status> || screen: melee A (power), ranged B, armor C || character: melee A, ..."
g.row(3700)
refresh = g.custom_event("Refresh")
as_stash, stash_pin = stash_of_player()
steps, screen = [refresh, as_stash], []
for key, words in [("MeleeGear", "melee "), ("RangedGear", ", ranged "), ("ArmorGear", ", armor ")]:
    find, value = equipment_slot((as_stash, stash_pin), key=key)
    worn = data_of(item_of((find, value)))
    broken = g.node("/Script/BlueprintGraph.K2Node_BreakStruct", StructType=DATA)
    g.link(worn[0], worn[1], broken, g.pins(broken)[0])
    power = g.call(STR, "Conv_FloatToString")
    g.link(broken, "ItemPower", power, "InFloat")
    screen += [words, name_text((broken, "ItemId")), " (", (power, "ReturnValue"), ")"]
g.row(4000)
player = g.call("/Script/Engine.GameplayStatics", "GetPlayerCharacter", PlayerIndex=0)
gear = g.call("/Script/Engine.Actor", "GetComponentByClass", ComponentClass="/Script/Dungeons.EquipmentComponent")
g.link(player, "ReturnValue", gear, "self")
as_gear, gear_pin = g.cast("/Script/Dungeons.EquipmentComponent", (gear, "ReturnValue"))
steps.append(as_gear)
held = []
for slot_type, words in [("MeleeWeapon", "melee "), ("RangedWeapon", ", ranged "), ("Armor", ", armor ")]:
    of_type = g.call("/Script/Dungeons.EquipmentComponent", "GetSlotsOfType", Type=slot_type)
    g.link(as_gear, gear_pin, of_type, "self")
    first = g.item_at((of_type, "ReturnValue"))
    instance = g.call("/Script/Dungeons.ItemSlot", "GetItem")
    g.link(first[0], first[1], instance, "self")
    item_id = g.call("/Script/Dungeons.ItemInstance", "GetItemId")
    g.link(instance, "ReturnValue", item_id, "self")
    held += [words, name_text((item_id, "ReturnValue"))]
said = joined(*(["Loadout test (O remember, P put back, L put back via the inventory screen) | ",
                 (g.var("Status"), "Status"), " || inventory screen: "] + screen + [" || character holds: "] + held))
as_text = g.call("/Script/Engine.KismetTextLibrary", "Conv_StringToText")
g.link(said[0], said[1], as_text, "InString")
set_text = g.call("/Script/UMG.TextBlock", "SetText")
g.link(g.var("Info", owner=VIEW_CLASS, target=(g.var("View"), "View")), "Info", set_text, "self")
g.link(as_text, "ReturnValue", set_text, "InText")
g.flow(*(steps + [set_text]))
compile_save(bp, "test actor")

# The normal build, with the loader also starting the test.
EXTRA_ACTORS = [TEST_CLASS]
transmog = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_transmog.py")
exec(compile(open(transmog).read(), transmog, "exec"), dict(globals(), __file__=__file__))
