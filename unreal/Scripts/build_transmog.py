"""Transmog: one chosen look per slot - melee, ranged, armor - picked from an in-game menu. While a look is chosen,
every item in that slot wears it (stats, swings and shots stay the item's own); with none chosen, items wear their
own look. The menu offers only items the character has found (the save's itemsFound).

    BP_SequelLooksSave     the save: Melee, Ranged, Armor (the chosen look file, or empty) and MenuKey (Y), in the
                           engine's own save file SequelLooks.sav - not the game's save
    BP_SequelTransmog      the actor, in camp and in missions:
                             BeginPlay   load the save (or make one), LoadLooks, listen to keys, Reapply every 0.2 s
                             LoadLooks   load the chosen look files into MeleeLook, RangedLook, ArmorLook
                             Reapply     ApplySlot for melee, ranged, armor
                             ApplySlot   the equipped item of a slot: remember its own look the first time it is
                                         seen; if it wears anything but the wanted look (chosen, or its own), swap
                                         and rebuild the slot
                             any key     the menu key opens/closes the menu; after WaitForKey, the next key (not a
                                         mouse button; Esc cancels) becomes the menu key
                             Choose      (Kind, Look) from the menu: store, LoadLooks, save
                             ToggleMenu, WaitForKey   for the menu
    WBP_SequelMenu         the menu: tabs Melee / Ranged / Armor, a grid of the found items' icons, "Own looks",
                           the menu key and Change, Close. Holds the item list (tools/transmog_items.py)
    WBP_SequelLookEntry    one icon in the grid; a click calls the menu's Pick(Index)
    BP_AvatarInfo          the mod's loader: a copy of the game's own empty helper /Game/Actors/BP_AvatarInfo
                           (placed in the menu, camp and mission maps) that, outside the menu, spawns
                           BP_SequelTransmog once. Needs no other mod.

Run headless: python tools/blueprints.py build_transmog
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from seqbp import *  # noqa: E402,F401,F403
import seqbp  # noqa: E402

seqbp.start(__file__)

ITEMS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "transmog_items.json")))
KINDS = {"MeleeWeapons": 0, "RangedWeapons": 1, "Armor": 2}
SAVE_SLOT = "SequelLooks"
SAVE = "/Game/SequelMod/BP_SequelLooksSave"
ACTOR = "/Game/SequelMod/BP_SequelTransmog"
MENU = "/Game/SequelMod/WBP_SequelMenu"
ENTRY = "/Game/SequelMod/WBP_SequelLookEntry"
STARTER = "/Game/Actors/BP_AvatarInfo"
SAVE_CLASS = SAVE + ".BP_SequelLooksSave_C"
ACTOR_CLASS = ACTOR + ".BP_SequelTransmog_C"
MENU_CLASS = MENU + ".WBP_SequelMenu_C"
ENTRY_CLASS = ENTRY + ".WBP_SequelLookEntry_C"
GEAR_ITEM = "/Script/Dungeons.GearItemInstance"
GEAR_LOOK = "/Script/Dungeons.GearActor"
ITEM_ID = "/Script/Dungeons.SerializableItemId"
LOOK_FILE = "softobject:/Script/CoreUObject.Object"
SLOTS = [("Melee", "MeleeWeapon"), ("Ranged", "RangedWeapon"), ("Armor", "Armor")]
DARK = unreal.LinearColor(0.08, 0.08, 0.1, 1.0)

for old in ["/Game/SequelMod/WBP_SequelStatus", "/Game/BPLoader/Lobby/SequelTransmog", "/Game/BPLoader/Ingame/SequelTransmog"]:
    remove(old)

# 1. The save.
save = blueprint(SAVE, unreal.SaveGame)
for name, _ in SLOTS:
    check(LIB.add_variable(save, name, LOOK_FILE), "save " + name)
check(LIB.add_variable(save, "MenuKey", "struct:/Script/InputCore.Key"), "save MenuKey")
check(LIB.set_variable_default(save, "MenuKey", "Y"), "MenuKey = Y")
compile_save(save, "save")

# 2. The actor's routines the menu calls (bodies come in step 5).
bp = blueprint(ACTOR, unreal.Actor)
for name, kind in [("Save", "object:" + SAVE_CLASS), ("Waiting", "bool"), ("Listening", "bool"),
                   ("Applied", "array:object:" + GEAR_ITEM), ("Originals", "array:class:" + GEAR_LOOK)] +                   [(name + "Look", "class:" + GEAR_LOOK) for name, _ in SLOTS]:
    check(LIB.add_variable(bp, name, kind), "variable " + name)
a = Graph(bp)
a.row(3000)
choose = a.custom_event("Choose", "Kind=int;Look=" + LOOK_FILE)
toggle = a.custom_event("ToggleMenu")
wait_key = a.custom_event("WaitForKey")
compile_save(bp, "actor routines")

# 3. The menu: layout and routines (bodies in step 4b).
menu = fresh(MENU, unreal.WidgetBlueprint, unreal.WidgetBlueprintFactory())
widget(menu, "", unreal.CanvasPanel, "Root")
panel = widget(menu, "Root", unreal.Border, "Panel")
panel.set_editor_property("brush_color", unreal.LinearColor(0.02, 0.02, 0.03, 0.93))
panel.set_editor_property("padding", unreal.Margin(20, 16, 20, 16))
spot = panel.get_editor_property("slot")
spot.set_anchors(unreal.Anchors(minimum=unreal.Vector2D(0.5, 0.5), maximum=unreal.Vector2D(0.5, 0.5)))
spot.set_alignment(unreal.Vector2D(0.5, 0.5))
spot.set_position(unreal.Vector2D(0, 0))
spot.set_size(unreal.Vector2D(1000, 660))
widget(menu, "Panel", unreal.VerticalBox, "Rows")
label(menu, "Rows", "Heading", "Transmog", 28)


def button(wbp, parent, name, words, text_name=None):
    b = widget(wbp, parent, unreal.Button, name, True)
    b.set_editor_property("background_color", DARK)
    label(wbp, name, text_name or name + "Text", words, 16, is_variable=bool(text_name))
    pad = b.get_editor_property("slot")
    pad.set_padding(unreal.Margin(0, 6, 10, 6))
    return b


widget(menu, "Rows", unreal.HorizontalBox, "Tabs")
for name, words in [("MeleeTab", "Melee"), ("RangedTab", "Ranged"), ("ArmorTab", "Armor"), ("OwnLook", "Own looks")]:
    button(menu, "Tabs", name, words)
label(menu, "Rows", "Status", "", 16, is_variable=True)
scroll = widget(menu, "Rows", unreal.ScrollBox, "Scroll")
scroll.get_editor_property("slot").set_size(unreal.SlateChildSize(1.0, unreal.SlateSizeRule.FILL))
widget(menu, "Scroll", unreal.WrapBox, "Grid", True)
widget(menu, "Rows", unreal.HorizontalBox, "Footer")
button(menu, "Footer", "ChangeKey", "Menu key: Y - change", text_name="KeyLabel")
button(menu, "Footer", "Close", "Close")
for name, kind in [("Owner", "object:" + ACTOR_CLASS), ("Tab", "int"), ("Ids", "array:struct:" + ITEM_ID),
                   ("CurId", "struct:" + ITEM_ID),
                   ("Kinds", "array:int"), ("Looks", "array:" + LOOK_FILE)]:
    check(LIB.add_variable(menu, name, kind), "menu variable " + name)
# Ready-made item ids: a Make struct node inside the loop kept giving the first one (every icon was Anchor).
check(LIB.set_variable_default(menu, "Ids", "(" + ",".join('(SerializedId="%s")' % i["id"] for i in ITEMS) + ")"),
      "menu Ids")
check(LIB.set_variable_default(menu, "Kinds", "(" + ",".join(str(KINDS[i["kind"]]) for i in ITEMS) + ")"), "menu Kinds")
check(LIB.set_variable_default(menu, "Looks", "(" + ",".join('"%s"' % i["look"] for i in ITEMS) + ")"), "menu Looks")
m = Graph(menu)
pick = m.custom_event("Pick", "Index=int")
show = m.custom_event("Show", "Tab=int")
show_key = m.custom_event("ShowKey")
compile_save(menu, "menu routines")

# 4a. One grid entry: an icon and a name; a click picks it.
entry = fresh(ENTRY, unreal.WidgetBlueprint, unreal.WidgetBlueprintFactory())
box = widget(entry, "", unreal.SizeBox, "Box")
box.set_width_override(124)
box.set_height_override(150)
widget(entry, "Box", unreal.Button, "Pick", True).set_editor_property("background_color", DARK)
widget(entry, "Pick", unreal.VerticalBox, "Stack")
icon = widget(entry, "Stack", unreal.Image, "Icon", True)
brush = icon.get_editor_property("brush")
brush.set_editor_property("image_size", unreal.Vector2D(88, 88))
icon.set_editor_property("brush", brush)
icon.get_editor_property("slot").set_horizontal_alignment(unreal.HorizontalAlignment.H_ALIGN_CENTER)
name_text = label(entry, "Stack", "Label", "", 12, is_variable=True)
name_text.set_auto_wrap_text(True)
name_text.set_editor_property("justification", unreal.TextJustify.CENTER)
for name, kind in [("Index", "int"), ("Menu", "object:" + MENU_CLASS)]:
    check(LIB.add_variable(entry, name, kind), "entry variable " + name)
e = Graph(entry)
clicked = e.bound_event("Pick", "OnClicked")
call_pick = e.call(MENU_CLASS, "Pick")
e.link(e.var("Menu"), "Menu", call_pick, "self")
e.link(e.var("Index"), "Index", call_pick, "Index")
e.flow(clicked, call_pick)
compile_save(entry, "entry")


# 4b. The menu's routines.
def text_of(*parts):
    """Text joined from parts: plain strings or (node, pin) of text."""
    joined = None
    for part in parts:
        if isinstance(part, tuple):
            to_string = m.call("/Script/Engine.KismetTextLibrary", "Conv_TextToString")
            m.link(part[0], part[1], to_string, "InText")
            piece = (to_string, "ReturnValue")
        else:
            piece = part
        if joined is None:
            if isinstance(piece, tuple):
                joined = piece
                continue
            start = m.call("/Script/Engine.KismetStringLibrary", "Concat_StrStr", A=piece, B="")
            joined = (start, "ReturnValue")
            continue
        concat = m.call("/Script/Engine.KismetStringLibrary", "Concat_StrStr")
        m.link(joined[0], joined[1], concat, "A")
        if isinstance(piece, tuple):
            m.link(piece[0], piece[1], concat, "B")
        else:
            m.set(concat, B=piece)
        joined = (concat, "ReturnValue")
    to_text = m.call("/Script/Engine.KismetTextLibrary", "Conv_StringToText")
    m.link(joined[0], joined[1], to_text, "InString")
    return to_text, "ReturnValue"


def set_text(graph_text_widget, text):
    node = m.call("/Script/UMG.TextBlock", "SetText")
    m.link(graph_text_widget, graph_text_widget_pin[graph_text_widget], node, "self")
    if isinstance(text, tuple):
        m.link(text[0], text[1], node, "InText")
    else:
        m.set(node, InText=text)
    return node


graph_text_widget_pin = {}


def menu_widget(name):
    node = m.var(name)
    graph_text_widget_pin[node] = name
    return node




# Show(Tab): list the found items of that kind.
m.row(0)
set_tab = m.var("Tab", set_=True)
m.link(show, "Tab", set_tab, "Tab")
clear = m.call("/Script/UMG.PanelWidget", "ClearChildren")
m.link(m.var("Grid"), "Grid", clear, "self")
player = m.call("/Script/Engine.GameplayStatics", "GetPlayerCharacter", PlayerIndex=0)
stash = m.call("/Script/Engine.Actor", "GetComponentByClass", ComponentClass="/Script/Dungeons.ItemStashComponent")
m.link(player, "ReturnValue", stash, "self")
as_stash, stash_pin = m.cast("/Script/Dungeons.ItemStashComponent", (stash, "ReturnValue"))
last = m.array_call("Array_LastIndex", (m.var("Ids"), "Ids"), "TargetArray")
loop = m.macro("ForLoop", FirstIndex=0)
log.append("ForLoop pins: " + ", ".join(m.pins(loop)))
m.link(last, "ReturnValue", loop, "LastIndex")
kind = m.item_at((m.var("Kinds"), "Kinds"), (loop, "Index"))
same_kind = m.call("/Script/Engine.KismetMathLibrary", "EqualEqual_IntInt")
m.link(kind[0], kind[1], same_kind, "A")
m.link(m.var("Tab"), "Tab", same_kind, "B")
# Each pass copies its item's id into CurId first, so everything after reads this pass's item.
take_id = m.var("CurId", set_=True)
loop_id = m.item_at((m.var("Ids"), "Ids"), (loop, "Index"))
m.link(loop_id[0], loop_id[1], take_id, "CurId")
this_id = (m.var("CurId"), "CurId")
found = m.call("/Script/Dungeons.ItemStashComponent", "HasPreviouslyFoundItem")
m.link(as_stash, stash_pin, found, "self")
m.link(this_id[0], this_id[1], found, "ItemType")
both = m.call("/Script/Engine.KismetMathLibrary", "BooleanAND")
m.link(same_kind, "ReturnValue", both, "A")
m.link(found, "ReturnValue", both, "B")
listed = m.branch((both, "ReturnValue"))
make_entry = m.node("/Script/UMGEditor.K2Node_CreateWidget")
m.set(make_entry, Class=ENTRY_CLASS)
new_entry = (make_entry, "ReturnValue")
set_index = m.var("Index", set_=True, owner=ENTRY_CLASS, target=new_entry)
m.link(loop, "Index", set_index, "Index")
set_menu = m.var("Menu", set_=True, owner=ENTRY_CLASS, target=new_entry)
me = m.self_node()
m.link(me[0], me[1], set_menu, "Menu")
icon_texture = m.call("/Script/Dungeons.ItemFunctionLibrary", "StreamIconTextureForItemIdHigh", blockingLoad="true")
m.link(this_id[0], this_id[1], icon_texture, "Type")
set_icon = m.call("/Script/UMG.Image", "SetBrushFromTexture")
m.link(m.var("Icon", owner=ENTRY_CLASS, target=new_entry), "Icon", set_icon, "self")
m.link(icon_texture, "ReturnValue", set_icon, "Texture")
item_name = m.call("/Script/Dungeons.ItemFunctionLibrary", "GetNameForItemType")
m.link(this_id[0], this_id[1], item_name, "Type")
set_name = m.call("/Script/UMG.TextBlock", "SetText")
m.link(m.var("Label", owner=ENTRY_CLASS, target=new_entry), "Label", set_name, "self")
m.link(item_name, "ReturnValue", set_name, "InText")
add_entry = m.call("/Script/UMG.PanelWidget", "AddChild")
m.link(m.var("Grid"), "Grid", add_entry, "self")
m.link(make_entry, "ReturnValue", add_entry, "Content")
said = set_text(menu_widget("Status"), "Pick a look - every item in this slot will wear it. Own looks: each item wears its own.")
m.flow(show, set_tab, clear, as_stash)
m.link(as_stash, "then", loop, "execute")
m.link(loop, "LoopBody", take_id, "execute")
m.flow(take_id, listed)
m.flow((listed, "then"), make_entry, set_index, set_menu, set_icon, set_name, add_entry)
m.link(loop, "Completed", said, "execute")

# Pick(Index): that item's look for its slot.
m.row(800)
chosen_kind = m.item_at((m.var("Kinds"), "Kinds"), (pick, "Index"))
chosen_look = m.item_at((m.var("Looks"), "Looks"), (pick, "Index"))
call_choose = m.call(ACTOR_CLASS, "Choose")
m.link(m.var("Owner"), "Owner", call_choose, "self")
m.link(chosen_kind[0], chosen_kind[1], call_choose, "Kind")
m.link(chosen_look[0], chosen_look[1], call_choose, "Look")
picked_name = m.call("/Script/Dungeons.ItemFunctionLibrary", "GetNameForItemType")
picked_id = m.item_at((m.var("Ids"), "Ids"), (pick, "Index"))
m.link(picked_id[0], picked_id[1], picked_name, "Type")
said_pick = set_text(menu_widget("Status"), text_of("Every item in this slot now looks like ", (picked_name, "ReturnValue"), " (saved)"))
m.flow(pick, call_choose, said_pick)

# Buttons.
m.row(1200)
for tab, name in enumerate(["MeleeTab", "RangedTab", "ArmorTab"]):
    on_tab = m.bound_event(name, "OnClicked")
    call_show = m.self_call("Show", Tab=tab)
    m.flow(on_tab, call_show)
m.row(1500)
on_own = m.bound_event("OwnLook", "OnClicked")
own_choose = m.call(ACTOR_CLASS, "Choose")
m.link(m.var("Owner"), "Owner", own_choose, "self")
m.link(m.var("Tab"), "Tab", own_choose, "Kind")
said_own = set_text(menu_widget("Status"), "Each item in this slot wears its own look again (saved)")
m.flow(on_own, own_choose, said_own)
m.row(1800)
on_close = m.bound_event("Close", "OnClicked")
close_menu = m.call(ACTOR_CLASS, "ToggleMenu")
m.link(m.var("Owner"), "Owner", close_menu, "self")
m.flow(on_close, close_menu)
m.row(2100)
on_change = m.bound_event("ChangeKey", "OnClicked")
start_wait = m.call(ACTOR_CLASS, "WaitForKey")
m.link(m.var("Owner"), "Owner", start_wait, "self")
said_wait = set_text(menu_widget("KeyLabel"), "Press the new menu key... (Esc: keep the old one)")
m.flow(on_change, start_wait, said_wait)

# ShowKey: "Menu key: <key> - change".
m.row(2400)
owner_save = m.var("Save", owner=ACTOR_CLASS, target=(m.var("Owner"), "Owner"))
menu_key = m.var("MenuKey", owner=SAVE_CLASS, target=(owner_save, "Save"))
key_name = m.call("/Script/Engine.KismetInputLibrary", "Key_GetDisplayName")
m.link(menu_key, "MenuKey", key_name, "Key")
said_key = set_text(menu_widget("KeyLabel"), text_of("Menu key: ", (key_name, "ReturnValue"), " - change"))
m.flow(show_key, said_key)
compile_save(menu, "menu")

# 5. The actor.
check(LIB.add_variable(bp, "Menu", "object:" + MENU_CLASS), "variable Menu")


def save_var(name, set_=False):
    return a.var(name, set_=set_, owner=SAVE_CLASS, target=(a.var("Save"), "Save"))


def store_save():
    store = a.call("/Script/Engine.GameplayStatics", "SaveGameToSlot", SlotName=SAVE_SLOT, UserIndex=0)
    a.link(a.var("Save"), "Save", store, "SaveGameObject")
    return store


def menu_call(fn):
    node = a.call(MENU_CLASS, fn)
    a.link(a.var("Menu"), "Menu", node, "self")
    return node


def equipped(slot_type):
    """The equipped item of a slot type ((node, pin)): (equipment cast, gear cast, (gear node, pin),
    (slot node, pin)). Wire exec into the equipment cast; it flows on to the gear cast."""
    player = a.call("/Script/Engine.GameplayStatics", "GetPlayerCharacter", PlayerIndex=0)
    component = a.call("/Script/Engine.Actor", "GetComponentByClass",
                       ComponentClass="/Script/Dungeons.EquipmentComponent")
    a.link(player, "ReturnValue", component, "self")
    as_equipment, eq_pin = a.cast("/Script/Dungeons.EquipmentComponent", (component, "ReturnValue"))
    slots = a.call("/Script/Dungeons.EquipmentComponent", "GetSlotsOfType")
    a.link(as_equipment, eq_pin, slots, "self")
    a.link(slot_type[0], slot_type[1], slots, "Type")
    first = a.item_at((slots, "ReturnValue"))
    item = a.call("/Script/Dungeons.ItemSlot", "GetItem")
    a.link(first[0], first[1], item, "self")
    as_gear, gear_pin = a.cast(GEAR_ITEM, (item, "ReturnValue"))
    a.flow(as_equipment, as_gear)
    return as_equipment, as_gear, (as_gear, gear_pin), first


# BeginPlay: load or make the save, LoadLooks, listen to keys, start Reapply.
a.row(0)
begin = a.event("/Script/Engine.Actor", "ReceiveBeginPlay")
exists = a.call("/Script/Engine.GameplayStatics", "DoesSaveGameExist", SlotName=SAVE_SLOT, UserIndex=0)
has_save = a.branch((exists, "ReturnValue"))
load = a.call("/Script/Engine.GameplayStatics", "LoadGameFromSlot", SlotName=SAVE_SLOT, UserIndex=0)
as_loaded, loaded_pin = a.cast(SAVE_CLASS, (load, "ReturnValue"))
set_loaded = a.var("Save", set_=True)
a.link(as_loaded, loaded_pin, set_loaded, "Save")
make = a.call("/Script/Engine.GameplayStatics", "CreateSaveGameObject", SaveGameClass=SAVE_CLASS)
as_made, made_pin = a.cast(SAVE_CLASS, (make, "ReturnValue"))
set_made = a.var("Save", set_=True)
a.link(as_made, made_pin, set_made, "Save")
a.flow(begin, exists, has_save)
a.flow((has_save, "then"), load, as_loaded, set_loaded)
a.flow((has_save, "else"), make, as_made, set_made)
a.flow((as_loaded, "CastFailed"), make)

# LoadLooks: each slot's chosen look file -> <Slot>Look (None when nothing is chosen).
a.row(600)
looks_event = a.custom_event("LoadLooks")
prev = [(looks_event, "then")]
for name, _ in SLOTS:
    load_look = a.call("/Script/Engine.KismetSystemLibrary", "LoadAsset_Blocking")
    a.link(save_var(name), name, load_look, "Asset")
    look_class = a.call("/Script/Engine.GameplayStatics", "GetObjectClass")
    a.link(load_look, "ReturnValue", look_class, "Object")
    as_look, look_pin = a.cast(GEAR_LOOK, (look_class, "ReturnValue"), cls_cast=True)
    set_found = a.var(name + "Look", set_=True)
    a.link(as_look, look_pin, set_found, name + "Look")
    set_none = a.var(name + "Look", set_=True)
    for node, pin in prev:
        a.link(node, pin, load_look, "execute")
    a.flow(load_look, as_look, set_found)
    a.flow((as_look, "CastFailed"), set_none)
    prev = [(set_found, "then"), (set_none, "then")]

# BeginPlay, continued (LoadLooks exists now).
a.row(300)
call_looks = a.self_call("LoadLooks")
timer = a.call("/Script/Engine.KismetSystemLibrary", "K2_SetTimer", FunctionName="Reapply", Time=0.2, bLooping="true")
a.flow(set_loaded, call_looks)
a.flow(set_made, call_looks, timer)

# ApplySlot(Type, Look): the slot's equipped item should wear Look (or, with no Look, its own).
a.row(1200)
apply_slot = a.custom_event("ApplySlot", "Type=enum:/Script/Dungeons.ESlotType;Look=class:" + GEAR_LOOK)
as_equipment, as_gear, gear, first = equipped((apply_slot, "Type"))
seen = a.array_call("Array_Contains", (a.var("Applied"), "Applied"), "TargetArray", ItemToFind=gear)
is_seen = a.branch((seen, "ReturnValue"))
add_item = a.array_call("Array_Add", (a.var("Applied"), "Applied"), "TargetArray", NewItem=gear)
add_own = a.array_call("Array_Add", (a.var("Originals"), "Originals"), "TargetArray",
                       NewItem=(a.var("GearActor", owner=GEAR_ITEM, target=gear), "GearActor"))
valid = a.call("/Script/Engine.KismetSystemLibrary", "IsValidClass")
a.link(apply_slot, "Look", valid, "Class")
wants_chosen = a.branch((valid, "ReturnValue"))
own_index = a.array_call("Array_Find", (a.var("Applied"), "Applied"), "TargetArray", ItemToFind=gear)
own = a.item_at((a.var("Originals"), "Originals"), (own_index, "ReturnValue"))
sets = []
for wanted in [(apply_slot, "Look"), own]:
    wearing = a.var("GearActor", owner=GEAR_ITEM, target=gear)
    differs = a.call("/Script/Engine.KismetMathLibrary", "NotEqual_ClassClass")
    a.link(wearing, "GearActor", differs, "A")
    a.link(wanted[0], wanted[1], differs, "B")
    swap = a.branch((differs, "ReturnValue"))
    set_look = a.var("GearActor", set_=True, owner=GEAR_ITEM, target=gear)
    a.link(wanted[0], wanted[1], set_look, "GearActor")
    a.flow(swap, set_look)
    sets.append((swap, set_look))
player = a.call("/Script/Engine.GameplayStatics", "GetPlayerCharacter", PlayerIndex=0)
display = a.call("/Script/Engine.Actor", "GetComponentByClass",
                 ComponentClass="/Script/Dungeons.EquipmentDisplayComponent")
a.link(player, "ReturnValue", display, "self")
as_display, display_pin = a.cast("/Script/Dungeons.EquipmentDisplayComponent", (display, "ReturnValue"))
rebuild = a.call("/Script/Dungeons.EquipmentDisplayComponent", "OnGearItemSlotUpdated")
a.link(as_display, display_pin, rebuild, "self")
a.link(first[0], first[1], rebuild, "ItemSlot")
# Rebuild only a slot the display already shows: the game's rebuild looks the slot up in SlotActors and crashes
# when it isn't there (e.g. while the character is still being set up). A slot added later is built from the
# item's GearActor, which is already the wanted look.
manager = a.var("SlotActorManager", owner="/Script/Dungeons.EquipmentDisplayComponent", target=(as_display, display_pin))
shown_slots = a.var("SlotActors", owner="/Script/Dungeons.SlotActorManager", target=(manager, "SlotActorManager"))
is_shown = a.call("/Script/Engine.BlueprintMapLibrary", "Map_Contains")
a.link(shown_slots, "SlotActors", is_shown, "TargetMap")
a.link(first[0], first[1], is_shown, "Key")
shown = a.branch((is_shown, "ReturnValue"))
a.flow(apply_slot, as_equipment)
a.flow(as_gear, is_seen)
a.flow((is_seen, "else"), add_item, add_own, wants_chosen)
a.flow((is_seen, "then"), wants_chosen)
a.flow((wants_chosen, "then"), sets[0][0])
a.flow((wants_chosen, "else"), sets[1][0])
for _, set_look in sets:
    a.flow(set_look, as_display, shown)
a.flow((shown, "then"), rebuild)

# Reapply: every 0.2 s (timer by name).
a.row(1800)
# Listen to keys once the player controller exists (the actor can be spawned before it).
reapply = a.custom_event("Reapply")
controller = a.call("/Script/Engine.GameplayStatics", "GetPlayerController", PlayerIndex=0)
has_controller = a.call("/Script/Engine.KismetSystemLibrary", "IsValid")
a.link(controller, "ReturnValue", has_controller, "Object")
not_listening = a.call("/Script/Engine.KismetMathLibrary", "Not_PreBool")
a.link(a.var("Listening"), "Listening", not_listening, "A")
start_listening = a.call("/Script/Engine.KismetMathLibrary", "BooleanAND")
a.link(has_controller, "ReturnValue", start_listening, "A")
a.link(not_listening, "ReturnValue", start_listening, "B")
should_listen = a.branch((start_listening, "ReturnValue"))
listen = a.call("/Script/Engine.Actor", "EnableInput")
a.link(controller, "ReturnValue", listen, "PlayerController")
now_listening = a.var("Listening", set_=True)
a.set(now_listening, Listening="true")
first_apply = a.self_call("ApplySlot", Type=SLOTS[0][1])
a.flow(reapply, should_listen)
a.flow((should_listen, "then"), listen, now_listening, first_apply)
a.flow((should_listen, "else"), first_apply)
steps = [first_apply]
a.link(a.var(SLOTS[0][0] + "Look"), SLOTS[0][0] + "Look", first_apply, "Look")
for name, slot_type in SLOTS[1:]:
    step = a.self_call("ApplySlot", Type=slot_type)
    a.link(a.var(name + "Look"), name + "Look", step, "Look")
    steps.append(step)
a.flow(*steps)

# Choose(Kind, Look): 0 melee, 1 ranged, 2 armor.
a.row(2200)
prev = (choose, "then")
done = a.self_call("LoadLooks")
for kind_number, (name, _) in enumerate(SLOTS):
    is_kind = a.call("/Script/Engine.KismetMathLibrary", "EqualEqual_IntInt", B=kind_number)
    a.link(choose, "Kind", is_kind, "A")
    which = a.branch((is_kind, "ReturnValue"))
    store_look = save_var(name, set_=True)
    a.link(choose, "Look", store_look, name)
    a.link(prev[0], prev[1], which, "execute")
    a.flow((which, "then"), store_look, done)
    prev = (which, "else")
a.flow(done, store_save())

# ToggleMenu: close it if open, else open it on the Melee tab.
a.row(2600)
menu_valid = a.call("/Script/Engine.KismetSystemLibrary", "IsValid")
a.link(a.var("Menu"), "Menu", menu_valid, "Object")
is_open = a.branch((menu_valid, "ReturnValue"))
take_down = menu_call("RemoveFromParent")
forget = a.var("Menu", set_=True)
stop_wait = a.var("Waiting", set_=True)
make_menu = a.node("/Script/UMGEditor.K2Node_CreateWidget")
a.set(make_menu, Class=MENU_CLASS)
set_menu = a.var("Menu", set_=True)
a.link(make_menu, "ReturnValue", set_menu, "Menu")
set_owner = a.var("Owner", set_=True, owner=MENU_CLASS, target=(make_menu, "ReturnValue"))
me = a.self_node()
a.link(me[0], me[1], set_owner, "Owner")
put_up = menu_call("AddToViewport")
first_tab = menu_call("Show")
a.set(first_tab, Tab=0)
key_label = menu_call("ShowKey")
a.flow(toggle, is_open)
a.flow((is_open, "then"), take_down, forget, stop_wait)
a.flow((is_open, "else"), make_menu, set_menu, set_owner, put_up, first_tab, key_label)

# WaitForKey: the next key press becomes the menu key.
a.row(3200)
start_waiting = a.var("Waiting", set_=True)
a.set(start_waiting, Waiting="true")
a.flow(wait_key, start_waiting)

# Any key: rebind while waiting, else the menu key toggles the menu. Doesn't consume keys: the game still gets them.
a.row(3600)
any_key = a.node("/Script/BlueprintGraph.K2Node_InputKey", InputKey="AnyKey", bConsumeInput="False")
pressed_key = (any_key, "Key")
waiting = a.branch((a.var("Waiting"), "Waiting"))
is_mouse = a.call("/Script/Engine.KismetInputLibrary", "Key_IsMouseButton")
a.link(pressed_key[0], pressed_key[1], is_mouse, "Key")
mouse = a.branch((is_mouse, "ReturnValue"))
is_escape = a.call("/Script/Engine.KismetInputLibrary", "EqualEqual_KeyKey", B="Escape")
a.link(pressed_key[0], pressed_key[1], is_escape, "A")
escape = a.branch((is_escape, "ReturnValue"))
new_key = save_var("MenuKey", set_=True)
a.link(pressed_key[0], pressed_key[1], new_key, "MenuKey")
saved_key = store_save()
done_waiting = a.var("Waiting", set_=True)
relabel = menu_call("ShowKey")
is_menu_key = a.call("/Script/Engine.KismetInputLibrary", "EqualEqual_KeyKey")
a.link(pressed_key[0], pressed_key[1], is_menu_key, "A")
a.link(save_var("MenuKey"), "MenuKey", is_menu_key, "B")
menu_key = a.branch((is_menu_key, "ReturnValue"))
call_toggle = a.self_call("ToggleMenu")
a.flow((any_key, "Pressed"), waiting)
a.flow((waiting, "then"), mouse)
a.flow((mouse, "else"), escape)
a.flow((escape, "else"), new_key, saved_key, done_waiting)
a.flow((escape, "then"), done_waiting, relabel)
a.flow((waiting, "else"), menu_key)
a.flow((menu_key, "then"), call_toggle)

compile_save(bp, "actor")

# 6. The loader: the game's BP_AvatarInfo (an empty AvatarInfo with a scene root, in the Menu, Lobby and Ingame
# maps and some sublevels) plus: outside the menu, spawn BP_SequelTransmog unless one is already there.
starter = blueprint(STARTER, unreal.load_class(None, "/Script/Dungeons.AvatarInfo"))
s = Graph(starter)
began = s.event("/Script/Engine.Actor", "ReceiveBeginPlay")
map_name = s.call("/Script/Engine.GameplayStatics", "GetCurrentLevelName", bRemovePrefixString="true")
in_menu = s.call("/Script/Engine.KismetStringLibrary", "EqualEqual_StrStr", B="Menu")
s.link(map_name, "ReturnValue", in_menu, "A")
is_menu = s.branch((in_menu, "ReturnValue"))
existing = s.call("/Script/Engine.GameplayStatics", "GetAllActorsOfClass", ActorClass=ACTOR_CLASS)
count = s.array_call("Array_Length", (existing, "OutActors"), "TargetArray")
none_yet = s.call("/Script/Engine.KismetMathLibrary", "EqualEqual_IntInt", B=0)
s.link(count, "ReturnValue", none_yet, "A")
is_first = s.branch((none_yet, "ReturnValue"))
spawn = s.node("/Script/BlueprintGraph.K2Node_SpawnActorFromClass")
s.set(spawn, Class=ACTOR_CLASS)
here = s.call("/Script/Engine.Actor", "GetTransform")
s.link(here, "ReturnValue", spawn, "SpawnTransform")
s.flow(began, map_name, is_menu)
s.flow((is_menu, "else"), existing, is_first)
s.flow((is_first, "then"), spawn)
compile_save(starter, "loader")
check(True, "done")
