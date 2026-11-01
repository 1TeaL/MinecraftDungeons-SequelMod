"""Loadouts: the transmog menu's Loadouts tab. build_transmog.py execs this file and calls its steps where they belong.

A loadout is a name, the 6 items worn (melee, ranged, armor, 3 artifacts - recognised by type, power and rarity,
since items have no id) and, if saved with "Save gear + looks", the 3 chosen looks. Up to 100, kept in the
transmog's own save (SequelLooks.sav) as four lists: LoadoutNames, LoadoutItems (6 per loadout, in KEYS order; an
empty slot is an empty entry), LoadoutLooks (3 per loadout) and LoadoutWithLooks.

    tab        Save gear / Save gear + looks (with the name box; empty = "Loadout N"), then one row per loadout
    row        its name (type to rename, Enter keeps it), gear only / gear + looks, the 6 icons, Load, Save over
               (keeps the row's kind), Delete (asks once more)
    Load       each item is swapped in from the inventory - or from another equipment slot, e.g. artifacts in a
               different order - with the inventory screen's own Swap (tested 2026-11-01), so enchantment points
               stay on their items; items already on stay; missing ones leave their slot alone. Then the looks.
"""
ROW = "/Game/SequelMod/WBP_SequelLoadoutRow"
ROW_CLASS = ROW + ".WBP_SequelLoadoutRow_C"
DATA = "/Script/Dungeons.InventoryItemData"
STASH = "/Script/Dungeons.ItemStashComponent"
INV_SLOT = "/Script/Dungeons.InventoryItemSlot"
INV_ITEM = "/Script/Dungeons.InventoryItem"
MAPS = "/Script/Engine.BlueprintMapLibrary"
MATH = "/Script/Engine.KismetMathLibrary"
STRINGS = "/Script/Engine.KismetStringLibrary"
KEYS = ["MeleeGear", "RangedGear", "ArmorGear", "HotbarSlot1", "HotbarSlot2", "HotbarSlot3"]
MOST = 100
LOADOUT_TAB = 3
# save list -> the menu's working copy
LISTS = [("LoadoutNames", "Names", "array:string"), ("LoadoutItems", "Items", "array:struct:" + DATA),
         ("LoadoutLooks", "Outfits", "array:" + LOOK_FILE), ("LoadoutWithLooks", "WithLooks", "array:bool")]
COUNTERS = ["Swapped", "Already", "Missing", "Refused"]
LO = {}


def loadout_save_vars(save):
    for name, _, kind in LISTS:
        check(LIB.add_variable(save, name, kind), "save " + name)


def loadout_layout(menu):
    """Under the status line: the name box and the two save buttons (shown on the Loadouts tab only)."""
    row = widget(menu, "Rows", unreal.HorizontalBox, "NewRow", True)
    row.set_editor_property("visibility", unreal.SlateVisibility.COLLAPSED)
    size = widget(menu, "NewRow", unreal.SizeBox, "NewNameSize")
    size.set_width_override(320)
    size.get_editor_property("slot").set_padding(unreal.Margin(0, 6, 10, 6))
    name_box = widget(menu, "NewNameSize", unreal.EditableTextBox, "NewName", True)
    name_box.set_editor_property("hint_text", unreal.Text("Name (optional)"))
    button(menu, "NewRow", "SaveGear", "Save gear")
    button(menu, "NewRow", "SaveAll", "Save gear + looks")
    for _, local, kind in LISTS:
        check(LIB.add_variable(menu, local, kind), "menu variable " + local)
    for name, kind in [("Picked", "array:struct:" + DATA), ("Empty", "struct:" + DATA), ("NewTitle", "string"),
                       ("Cells", "array:object:" + INV_SLOT), ("Found", "bool"), ("FoundSlot", "object:" + INV_SLOT)] + \
            [(c, "int") for c in COUNTERS]:
        check(LIB.add_variable(menu, name, kind), "menu variable " + name)


def loadout_events(g):
    for name, params in [("ShowLoadouts", ""), ("NewLoadout", "KeepLooks=bool"), ("LoadLoadout", "Index=int"),
                         ("OverwriteLoadout", "Index=int"), ("DeleteLoadout", "Index=int"),
                         ("RenameLoadout", "Index=int;Name=string"), ("Remember", ""),
                         ("EquipOne", "Key=enum:/Script/Dungeons.EEquipmentSlot;Want=struct:" + DATA),
                         ("StoreLoadouts", "")]:
        LO[name] = g.custom_event(name, params)


def loadout_row():
    """WBP_SequelLoadoutRow: one loadout in the list. Its buttons call the menu with the row's Index."""
    row = fresh(ROW, unreal.WidgetBlueprint, unreal.WidgetBlueprintFactory())
    box = widget(row, "", unreal.SizeBox, "Box")
    box.set_width_override(940)
    box.set_height_override(64)
    widget(row, "Box", unreal.HorizontalBox, "Line")
    size = widget(row, "Line", unreal.SizeBox, "NameSize")
    size.set_width_override(220)
    size.get_editor_property("slot").set_vertical_alignment(unreal.VerticalAlignment.V_ALIGN_CENTER)
    widget(row, "NameSize", unreal.EditableTextBox, "NameBox", True)
    kind_size = widget(row, "Line", unreal.SizeBox, "KindSize")
    kind_size.set_width_override(110)
    kind_size.get_editor_property("slot").set_vertical_alignment(unreal.VerticalAlignment.V_ALIGN_CENTER)
    kind_size.get_editor_property("slot").set_padding(unreal.Margin(8, 0, 0, 0))
    label(row, "KindSize", "Kind", "", 12, is_variable=True).set_auto_wrap_text(True)
    for k in range(len(KEYS)):
        icon = widget(row, "Line", unreal.Image, "Icon%d" % k, True)
        brush = icon.get_editor_property("brush")
        brush.set_editor_property("image_size", unreal.Vector2D(52, 52))
        icon.set_editor_property("brush", brush)
        spot = icon.get_editor_property("slot")
        spot.set_vertical_alignment(unreal.VerticalAlignment.V_ALIGN_CENTER)
        spot.set_padding(unreal.Margin(2, 0, 2, 0))
    for name, words, text_name in [("Load", "Load", None), ("SaveOver", "Save over", None),
                                   ("Delete", "Delete", "DeleteText")]:
        b = button(row, "Line", name, words, text_name=text_name)
        b.get_editor_property("slot").set_vertical_alignment(unreal.VerticalAlignment.V_ALIGN_CENTER)
        b.get_editor_property("slot").set_padding(unreal.Margin(8, 6, 0, 6))
    for name, kind in [("Index", "int"), ("Menu", "object:" + MENU_CLASS), ("Armed", "bool")]:
        check(LIB.add_variable(row, name, kind), "row variable " + name)
    r = Graph(row)

    def to_menu(event, button_name):
        clicked = r.bound_event(button_name, "OnClicked")
        call = r.call(MENU_CLASS, event)
        r.link(r.var("Menu"), "Menu", call, "self")
        r.link(r.var("Index"), "Index", call, "Index")
        return clicked, call

    clicked, call = to_menu("LoadLoadout", "Load")
    r.flow(clicked, call)
    r.row(300)
    clicked, call = to_menu("OverwriteLoadout", "SaveOver")
    r.flow(clicked, call)
    # Delete: the first click asks, the second deletes.
    r.row(600)
    clicked, call = to_menu("DeleteLoadout", "Delete")
    armed = r.branch((r.var("Armed"), "Armed"))
    arm = r.var("Armed", set_=True)
    r.set(arm, Armed="true")
    ask = r.call("/Script/UMG.TextBlock", "SetText", InText="Sure? Click again")
    r.link(r.var("DeleteText"), "DeleteText", ask, "self")
    r.flow(clicked, armed)
    r.flow((armed, "then"), call)
    r.flow((armed, "else"), arm, ask)
    # Typing a new name: kept when the box is left or Enter is pressed.
    r.row(900)
    typed = r.bound_event("NameBox", "OnTextCommitted")
    as_string = r.call("/Script/Engine.KismetTextLibrary", "Conv_TextToString")
    r.link(typed, "Text", as_string, "InText")
    rename = r.call(MENU_CLASS, "RenameLoadout")
    r.link(r.var("Menu"), "Menu", rename, "self")
    r.link(r.var("Index"), "Index", rename, "Index")
    r.link(as_string, "ReturnValue", rename, "Name")
    r.flow(typed, rename)
    r.row(1200)
    highlight(r, ["Load", "SaveOver", "Delete"], in_list=True)
    compile_save(row, "loadout row")


def loadout_tab_switch(g, after):
    """After `after` (node leaving by "then"): on the Loadouts tab show the save row and the list; on the others
    hide the save row. Returns (node, pin) that goes on to the item tabs."""
    is_tab = g.call(MATH, "EqualEqual_IntInt", B=LOADOUT_TAB)
    g.link(g.var("Tab"), "Tab", is_tab, "A")
    which = g.branch((is_tab, "ReturnValue"))
    steps = {}
    for case, new_row, own in [("then", "Visible", "Collapsed"), ("else", "Collapsed", "Visible")]:
        show_row = g.call("/Script/UMG.Widget", "SetVisibility", InVisibility=new_row)
        g.link(g.var("NewRow"), "NewRow", show_row, "self")
        show_own = g.call("/Script/UMG.Widget", "SetVisibility", InVisibility=own)
        g.link(g.var("OwnLook"), "OwnLook", show_own, "self")
        g.flow((which, case), show_row, show_own)
        steps[case] = show_own
    g.flow(after, which)
    g.flow(steps["then"], g.self_call("ShowLoadouts"))
    return steps["else"], "then"


def loadout_routines(g):
    """The menu's loadout routines (the events declared by loadout_events)."""

    def owner_save():
        return g.var("Save", owner=ACTOR_CLASS, target=(g.var("Owner"), "Owner")), "Save"

    def saved(name):
        return g.var(name, owner=SAVE_CLASS, target=owner_save()), name

    def local(name):
        return g.var(name), name

    def words(*parts):
        """Text from parts: plain strings or (node, pin) of strings."""
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
        text = g.call("/Script/Engine.KismetTextLibrary", "Conv_StringToText")
        g.link(out[0], out[1], text, "InString")
        return text, "ReturnValue"

    def status(*parts):
        return set_text(menu_widget("Status"), words(*parts) if len(parts) > 1 or isinstance(parts[0], tuple)
                        else parts[0])

    def int_text(value):
        node = g.call(STRINGS, "Conv_IntToString")
        g.link(value[0], value[1], node, "InInt")
        return node, "ReturnValue"

    def at(index, per, plus=0):
        """index * per + plus, for the flat lists."""
        times = g.call(MATH, "Multiply_IntInt", B=per)
        g.link(index[0], index[1], times, "A")
        add = g.call(MATH, "Add_IntInt", B=plus)
        g.link(times, "ReturnValue", add, "A")
        return add, "ReturnValue"

    def length(array):
        node = g.array_call("Array_Length", array, "TargetArray")
        return node, "ReturnValue"

    def stash_cast():
        player = g.call("/Script/Engine.GameplayStatics", "GetPlayerCharacter", PlayerIndex=0)
        stash = g.call("/Script/Engine.Actor", "GetComponentByClass", ComponentClass=STASH)
        g.link(player, "ReturnValue", stash, "self")
        return g.cast(STASH, (stash, "ReturnValue"))

    def equipment(stash):
        slots = g.call(STASH, "GetEquipmentSlots")
        g.link(stash[0], stash[1], slots, "self")
        return slots, "ReturnValue"

    def slot_for(stash, key=None, key_pin=None):
        find = g.call(MAPS, "Map_Find")
        slots = equipment(stash)
        g.link(slots[0], slots[1], find, "TargetMap")
        if key_pin:
            g.link(key_pin[0], key_pin[1], find, "Key")
        else:
            g.set(find, Key=key)
        return find, "Value"

    def item_of(slot):
        return g.var("Item", owner=INV_SLOT, target=slot), "Item"

    def data_of(item):
        return g.var("Item", owner=INV_ITEM, target=item), "Item"

    def valid(obj):
        node = g.call("/Script/Engine.KismetSystemLibrary", "IsValid")
        g.link(obj[0], obj[1], node, "Object")
        return node, "ReturnValue"

    def both(a, b):
        node = g.call(MATH, "BooleanAND")
        g.link(a[0], a[1], node, "A")
        g.link(b[0], b[1], node, "B")
        return node, "ReturnValue"

    def item_id(data):
        broken = g.node("/Script/BlueprintGraph.K2Node_BreakStruct", StructType=DATA)
        g.link(data[0], data[1], broken, g.pins(broken)[0])
        return broken

    def same_item(a, b):
        """Same type, power and rarity."""
        parts = []
        for data in (a, b):
            broken = item_id(data)
            name = g.node("/Script/BlueprintGraph.K2Node_BreakStruct", StructType="/Script/Dungeons.SerializableItemId")
            g.link(broken, "ItemId", name, g.pins(name)[0])
            parts.append((broken, name))
        tests = []
        for fn, pin, which in [("EqualEqual_NameName", "SerializedId", 1), ("EqualEqual_FloatFloat", "ItemPower", 0),
                               ("EqualEqual_ByteByte", "Rarity", 0)]:
            test = g.call(MATH, fn)
            g.link(parts[0][which], pin, test, "A")
            g.link(parts[1][which], pin, test, "B")
            tests.append((test, "ReturnValue"))
        return both(both(tests[0], tests[1]), tests[2])

    def has_item(data):
        broken = item_id(data)
        name = g.node("/Script/BlueprintGraph.K2Node_BreakStruct", StructType="/Script/Dungeons.SerializableItemId")
        g.link(broken, "ItemId", name, g.pins(name)[0])
        test = g.call(MATH, "NotEqual_NameName", B="None")
        g.link(name, "SerializedId", test, "A")
        return test, "ReturnValue"

    def bump(counter):
        plus = g.call(MATH, "Add_IntInt", B=1)
        g.link(g.var(counter), counter, plus, "A")
        setter = g.var(counter, set_=True)
        g.link(plus, "ReturnValue", setter, counter)
        return setter

    def loop(array, with_break=False):
        last = g.array_call("Array_LastIndex", array, "TargetArray")
        node = g.macro("ForLoopWithBreak" if with_break else "ForLoop", FirstIndex=0)
        g.link(last, "ReturnValue", node, "LastIndex")
        return node, g.item_at(array, (node, "Index"))

    # StoreLoadouts: the working copies -> the save, written to disk.
    g.row(6000)
    steps = [LO["StoreLoadouts"]]
    for name, mine, _ in LISTS:
        put = g.var(name, set_=True, owner=SAVE_CLASS, target=owner_save())
        g.link(g.var(mine), mine, put, name)
        steps.append(put)
    write = g.call("/Script/Engine.GameplayStatics", "SaveGameToSlot", SlotName=SAVE_SLOT, UserIndex=0)
    holder = owner_save()
    g.link(holder[0], holder[1], write, "SaveGameObject")
    g.flow(*(steps + [write]))

    # ShowLoadouts: the save -> working copies, then one row per loadout.
    g.row(6300)
    wipe = g.call("/Script/UMG.PanelWidget", "ClearChildren")
    g.link(g.var("Grid"), "Grid", wipe, "self")
    steps = [LO["ShowLoadouts"], wipe]
    for name, mine, _ in LISTS:
        take = g.var(mine, set_=True)
        g.link(*(saved(name) + (take, mine)))
        steps.append(take)
    rows, name = loop(local("Names"))
    g.flow(*(steps + [rows]))
    g.row(6600)
    make_row = g.node("/Script/UMGEditor.K2Node_CreateWidget")
    g.set(make_row, Class=ROW_CLASS)
    new_row = (make_row, "ReturnValue")
    set_index = g.var("Index", set_=True, owner=ROW_CLASS, target=new_row)
    g.link(rows, "Index", set_index, "Index")
    set_menu = g.var("Menu", set_=True, owner=ROW_CLASS, target=new_row)
    me = g.self_node()
    g.link(me[0], me[1], set_menu, "Menu")
    name_text = g.call("/Script/Engine.KismetTextLibrary", "Conv_StringToText")
    g.link(name[0], name[1], name_text, "InString")
    set_name = g.call("/Script/UMG.EditableTextBox", "SetText")
    g.link(g.var("NameBox", owner=ROW_CLASS, target=new_row), "NameBox", set_name, "self")
    g.link(name_text, "ReturnValue", set_name, "InText")
    with_looks = g.item_at(local("WithLooks"), (rows, "Index"))
    kind = g.branch(with_looks)
    g.flow((rows, "LoopBody"), make_row, set_index, set_menu, set_name, kind)
    prev = []
    for case, said in [("then", "gear + looks"), ("else", "gear only")]:
        set_kind = g.call("/Script/UMG.TextBlock", "SetText", InText=said)
        g.link(g.var("Kind", owner=ROW_CLASS, target=new_row), "Kind", set_kind, "self")
        g.flow((kind, case), set_kind)
        prev.append((set_kind, "then"))
    for k in range(len(KEYS)):
        g.row(6900 + 300 * k)
        data = g.item_at(local("Items"), at((rows, "Index"), len(KEYS), k))
        filled = g.branch(has_item(data))
        icon = g.var("Icon%d" % k, owner=ROW_CLASS, target=new_row)
        texture = g.call("/Script/Dungeons.ItemFunctionLibrary", "StreamIconTextureForItemIdHigh", blockingLoad="true")
        g.link(item_id(data), "ItemId", texture, "Type")
        set_icon = g.call("/Script/UMG.Image", "SetBrushFromTexture")
        g.link(icon, "Icon%d" % k, set_icon, "self")
        g.link(texture, "ReturnValue", set_icon, "Texture")
        hide = g.call("/Script/UMG.Widget", "SetVisibility", InVisibility="Hidden")
        g.link(icon, "Icon%d" % k, hide, "self")
        for node, pin in prev:
            g.link(node, pin, filled, "execute")
        g.flow((filled, "then"), set_icon)
        g.flow((filled, "else"), hide)
        prev = [(set_icon, "then"), (hide, "then")]
    g.row(8800)
    add_row = g.call("/Script/UMG.PanelWidget", "AddChild")
    g.link(g.var("Grid"), "Grid", add_row, "self")
    g.link(make_row, "ReturnValue", add_row, "Content")
    for node, pin in prev:
        g.link(node, pin, add_row, "execute")
    count = length(local("Names"))
    listed = status(int_text(count), " of %d loadouts. Load swaps each item in from your inventory (enchantment "
                                      "points stay on their items); a loadout with looks puts them on too." % MOST)
    g.flow((rows, "Completed"), listed)

    # Remember: the 6 equipment slots' items -> Picked (an empty entry for an empty slot).
    g.row(9200)
    as_stash, stash_pin = stash_cast()
    clear = g.array_call("Array_Clear", local("Picked"), "TargetArray")
    g.flow(LO["Remember"], as_stash, clear)
    prev = [(clear, "then")]
    for key in KEYS:
        worn = item_of(slot_for((as_stash, stash_pin), key=key))
        filled = g.branch(valid(worn))
        add_worn = g.array_call("Array_Add", local("Picked"), "TargetArray", NewItem=data_of(worn))
        add_empty = g.array_call("Array_Add", local("Picked"), "TargetArray", NewItem=local("Empty"))
        for node, pin in prev:
            g.link(node, pin, filled, "execute")
        g.flow((filled, "then"), add_worn)
        g.flow((filled, "else"), add_empty)
        prev = [(add_worn, "then"), (add_empty, "then")]

    # NewLoadout(KeepLooks): Remember, then add it under the typed name (or "Loadout N").
    g.row(9800)
    new = LO["NewLoadout"]
    full_test = g.call(MATH, "GreaterEqual_IntInt", B=MOST)
    g.link(*(length(local("Names")) + (full_test, "A")))
    full = g.branch((full_test, "ReturnValue"))
    g.flow(new, full)
    g.flow((full, "then"), status("%d loadouts already - delete one or save over one." % MOST))
    text_box = g.var("NewName")
    get_text = g.call("/Script/UMG.EditableTextBox", "GetText")
    g.link(text_box, "NewName", get_text, "self")
    typed = g.call("/Script/Engine.KismetTextLibrary", "Conv_TextToString")
    g.link(get_text, "ReturnValue", typed, "InText")
    blank_test = g.call(STRINGS, "Len")
    g.link(typed, "ReturnValue", blank_test, "S")
    is_blank = g.call(MATH, "EqualEqual_IntInt", B=0)
    g.link(blank_test, "ReturnValue", is_blank, "A")
    blank = g.branch((is_blank, "ReturnValue"))
    title_typed = g.var("NewTitle", set_=True)
    g.link(typed, "ReturnValue", title_typed, "NewTitle")
    title_made = g.var("NewTitle", set_=True)
    next_number = g.call(MATH, "Add_IntInt", B=1)
    g.link(*(length(local("Names")) + (next_number, "A")))
    made = words("Loadout ", int_text((next_number, "ReturnValue")))
    made_string = g.call("/Script/Engine.KismetTextLibrary", "Conv_TextToString")
    g.link(made[0], made[1], made_string, "InText")
    g.link(made_string, "ReturnValue", title_made, "NewTitle")
    g.flow((full, "else"), g.self_call("Remember"), blank)
    g.flow((blank, "then"), title_made)
    g.flow((blank, "else"), title_typed)
    g.row(10100)
    add_name = g.array_call("Array_Add", local("Names"), "TargetArray", NewItem=local("NewTitle"))
    add_items = g.array_call("Array_Append", local("Items"), "TargetArray", SourceArray=local("Picked"))
    adds = [add_name, add_items]
    for slot_name, _ in SLOTS:
        adds.append(g.array_call("Array_Add", local("Outfits"), "TargetArray", NewItem=saved(slot_name)))
    adds.append(g.array_call("Array_Add", local("WithLooks"), "TargetArray", NewItem=(new, "KeepLooks")))
    title_made_next = (title_made, "then")
    g.link(title_typed, "then", add_name, "execute")
    g.link(title_made_next[0], title_made_next[1], add_name, "execute")
    clear_box = g.call("/Script/UMG.EditableTextBox", "SetText", InText="")
    g.link(g.var("NewName"), "NewName", clear_box, "self")
    g.flow(*(adds + [g.self_call("StoreLoadouts"), clear_box, g.self_call("ShowLoadouts"),
                     status("Saved ", local("NewTitle"), ".")]))

    # OverwriteLoadout(Index): Remember, then put it in place of that loadout's items and looks.
    g.row(10600)
    over = LO["OverwriteLoadout"]
    each, picked = loop(local("Picked"))
    g.flow(over, g.self_call("Remember"), each)
    put = g.array_call("Array_Set", local("Items"), "TargetArray", Item=picked)
    plus = g.call(MATH, "Add_IntInt")
    first = at((over, "Index"), len(KEYS))
    g.link(first[0], first[1], plus, "A")
    g.link(each, "Index", plus, "B")
    g.link(plus, "ReturnValue", put, "Index")
    g.flow((each, "LoopBody"), put)
    steps = []
    for j, (slot_name, _) in enumerate(SLOTS):
        put_look = g.array_call("Array_Set", local("Outfits"), "TargetArray", Item=saved(slot_name))
        index = at((over, "Index"), len(SLOTS), j)
        g.link(index[0], index[1], put_look, "Index")
        steps.append(put_look)
    over_name = g.item_at(local("Names"), (over, "Index"))
    g.flow(*([(each, "Completed")] + steps + [g.self_call("StoreLoadouts"), g.self_call("ShowLoadouts"),
                                              status("Saved over ", over_name, ".")]))

    # DeleteLoadout(Index).
    g.row(11000)
    gone = LO["DeleteLoadout"]
    steps = [gone]
    for mine, per in [("Names", 1), ("WithLooks", 1)] + [("Items", len(KEYS))] * len(KEYS) + \
            [("Outfits", len(SLOTS))] * len(SLOTS):
        remove_one = g.array_call("Array_Remove", local(mine), "TargetArray")
        index = at((gone, "Index"), per)
        g.link(index[0], index[1], remove_one, "IndexToRemove")
        steps.append(remove_one)
    g.flow(*(steps + [g.self_call("StoreLoadouts"), g.self_call("ShowLoadouts"), status("Deleted.")]))

    # RenameLoadout(Index, Name).
    g.row(11400)
    rename = LO["RenameLoadout"]
    put_name = g.array_call("Array_Set", local("Names"), "TargetArray", Item=(rename, "Name"))
    g.link(rename, "Index", put_name, "Index")
    g.flow(rename, put_name, g.self_call("StoreLoadouts"), status("Renamed to ", (rename, "Name"), "."))

    # EquipOne(Key, Want): put Want into that equipment slot, unless it's empty or already there.
    g.row(11800)
    one = LO["EquipOne"]
    wanted = (one, "Want")
    wants_one = g.branch(has_item(wanted))
    as_stash, stash_pin = stash_cast()
    target = slot_for((as_stash, stash_pin), key_pin=(one, "Key"))
    current = item_of(target)
    there = g.branch(both(valid(current), same_item(data_of(current), wanted)))
    g.flow(one, wants_one)
    g.flow((wants_one, "then"), as_stash, there)
    g.flow((there, "then"), bump("Already"))
    g.row(12100)
    cells = g.var("Cells", set_=True)
    inventory = g.call(STASH, "GetInventorySlots")
    g.link(as_stash, stash_pin, inventory, "self")
    g.link(inventory, "ReturnValue", cells, "Cells")
    worn_slots = g.call(MAPS, "Map_Values")
    slots = equipment((as_stash, stash_pin))
    g.link(slots[0], slots[1], worn_slots, "TargetMap")
    add_worn = g.array_call("Array_Append", local("Cells"), "TargetArray", SourceArray=(worn_slots, "Values"))
    not_found = g.var("Found", set_=True)
    g.set(not_found, Found="false")
    search, cell = loop(local("Cells"), with_break=True)
    g.flow((there, "else"), cells, worn_slots, add_worn, not_found, search)
    g.row(12400)
    cell_item = item_of(cell)
    hit = g.branch(both(valid(cell_item), same_item(data_of(cell_item), wanted)))
    found = g.var("Found", set_=True)
    g.set(found, Found="true")
    keep = g.var("FoundSlot", set_=True)
    g.link(cell[0], cell[1], keep, "FoundSlot")
    g.flow((search, "LoopBody"), hit)
    g.flow((hit, "then"), found, keep)
    g.link(keep, "then", search, "Break")
    g.row(12700)
    was_found = g.branch(local("Found"))
    allowed = g.call(INV_SLOT, "CanSwapWith")
    g.link(target[0], target[1], allowed, "self")
    g.link(g.var("FoundSlot"), "FoundSlot", allowed, "Other")
    may = g.branch((allowed, "ReturnValue"))
    swap = g.call(INV_SLOT, "Swap")
    g.link(target[0], target[1], swap, "self")
    g.link(g.var("FoundSlot"), "FoundSlot", swap, "Other")
    g.flow((search, "Completed"), was_found, may, swap, bump("Swapped"))
    g.flow((was_found, "else"), bump("Missing"))
    g.flow((may, "else"), bump("Refused"))

    # LoadLoadout(Index): each item, then (with looks) the looks, then what happened.
    g.row(13100)
    load = LO["LoadLoadout"]
    steps = [load]
    for counter in COUNTERS:
        zero = g.var(counter, set_=True)
        g.set(zero, **{counter: 0})
        steps.append(zero)
    for k, key in enumerate(KEYS):
        put_on = g.self_call("EquipOne", Key=key)
        data = g.item_at(local("Items"), at((load, "Index"), len(KEYS), k))
        g.link(data[0], data[1], put_on, "Want")
        steps.append(put_on)
    looks_too = g.branch(g.item_at(local("WithLooks"), (load, "Index")))
    g.flow(*(steps + [looks_too]))
    g.row(13400)
    load_name = g.item_at(local("Names"), (load, "Index"))
    counts = [load_name, ": ", int_text(local("Swapped")), " put on, ", int_text(local("Already")), " already on, ",
              int_text(local("Missing")), " not in your inventory, ", int_text(local("Refused")), " couldn't move"]
    steps = []
    for j in range(len(SLOTS)):
        choose = g.call(ACTOR_CLASS, "Choose", Kind=j)
        g.link(g.var("Owner"), "Owner", choose, "self")
        look = g.item_at(local("Outfits"), at((load, "Index"), len(SLOTS), j))
        g.link(look[0], look[1], choose, "Look")
        steps.append(choose)
    g.flow(*([(looks_too, "then")] + steps + [status(*(counts + [" - looks on."]))]))
    g.flow((looks_too, "else"), status(*(counts + ["."])))

    # The tab's two save buttons.
    g.row(13800)
    for button_name, keep_looks in [("SaveGear", "false"), ("SaveAll", "true")]:
        clicked = g.bound_event(button_name, "OnClicked")
        g.flow(clicked, g.self_call("NewLoadout", KeepLooks=keep_looks))
