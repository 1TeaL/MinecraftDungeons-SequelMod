"""The Sequel Mod's reworked enchantments (exec'd by build_transmog.py; packed into SequelMod_P.pak by tools/sequel.py).

Each is our own copy of the game's enchantment blueprint - in the game an empty blueprint over its native class, so
ours has the same name, and the game creates ours wherever an item gives that enchantment (proven with Gravity Pulse,
2026-11-04). An enchantment is a component on its wearer while the item is worn; ours carries its own logic. The old
native behaviour is switched off through its own settings, or - where it has none - by building ours on the game's
plain Enchantment class instead of the native one, so the old code isn't there at all. Names and descriptions are in
settings/build/SequelText.toml.

    Recycler -> Ancient Alchemy        using a healing potion grants SOULS_BASE + SOULS_PER_TIER x tier souls
                                       (60 / 90 / 120). Built on Recycler's code so the card's tier line reads
                                       "60 souls" etc.: its {0} is Recycler's per-tier value, set to 60 / 90 / 120
                                       in settings/launcher/Formulas.toml. Recycler's own arrows can't be switched
                                       off (no settings) - they now come every 60 / 90 / 120 projectile hits taken.
                                       (First built on Gravity Pulse, 2026-11-04; its card could only say
                                       100 / 150 / 200%. Gravity Pulse is the game's own again.)
    Explorer -> Bottomless Brew        EXTRA_DRINKS_PER_TIER x tier extra drinks (1 / 2 / 3): after a drink, the
                                       potion's cooldown effect (the one granting tag Cooldown.SlotHealthPotion) is
                                       removed, until the extra drinks are used up; a cooldown that runs out on its
                                       own refills them. Built on Explorer's code so its card shows our texts
                                       (the plain Enchantment class showed only the name, 2026-11-05); Explorer's
                                       heal is off (BlockThreshold EXPLORER_OFF). First built over Food Reserves,
                                       which has no setting to switch its food off - Food Reserves is the game's
                                       own again.

    Sponge Strike -> Shadowcloak       a kill by the wearer has a 15 / 20 / 25% chance of Shadow Form (the game's
                                       Backstabber's Brew effect, applied as Shadow Shot applies it). Rolls on
                                       melee and ranged (EnchantGear.toml).
    Knockback -> Sweeping Edge         every melee hit splashes: other mobs within 3 blocks of the mob hit take
                                       10 / 20 / 30% of the hit's damage (our copy of the game's melee hit spark,
                                       /Game/Cues/HitCues/BP_HitMeleeNotifyStatic). The wider swing is off.
    (Frost Shot is the game's own unused FreezingRanged, unlocked - data only, no blueprint here.)
    Gravity Pulse -> Artifact Amplifier  while worn: artifact damage and souls gathered +20 / 35 / 50%
                                       (our own effect).
    Food Reserves -> Barrier Brew      drinking a potion gives you and players near you 70% less damage taken for
                                       2 / 4 / 6 s (our own effect). Its food is off (Formulas.toml FoodReserves 0).

Ancient Alchemy and Bottomless Brew watch the wearer's potion slot every WATCH_SECONDS and act when its cooldown starts. They run where the wearer
has authority (the host), so a co-op player is paid / refilled once. Bottomless Brew removes the cooldown one look
AFTER it saw it start, so Ancient Alchemy (its own look, at most WATCH_SECONDS later) always sees every drink.
"""
from seqbp import *  # noqa: F401,F403

GRAVITY_PULSE = "/Game/Components/Enchantments/GravityPulse/BP_GravityPulse"   # was Ancient Alchemy; Artifact Amplifier now
RECYCLER = "/Game/Components/Enchantments/Recycler/BP_Recycler"
FOOD_RESERVES = "/Game/Components/Enchantments/FoodReserves/BP_FoodReserves"   # Bottomless Brew (2026-11-08; Barrier Brew before)
EXPLORER = "/Game/Components/Enchantments/Explorer/BP_Explorer"   # Barrier Brew (2026-11-08; Bottomless Brew before)
EXPLORER_OFF = 1000000000   # blocks to explore before Explorer heals: never
SOULS_BASE, SOULS_PER_TIER = 30, 30   # 60 / 90 / 120 at tier I / II / III (user, 2026-11-04)
EXTRA_DRINKS_PER_TIER = 1             # 1 / 2 / 3, as in Dungeons II (user, 2026-11-04)
POTION_COOLDOWN_TAG = "Cooldown.SlotHealthPotion"   # in unreal/Config/DefaultGameplayTags.ini, so the editor keeps it
WATCH_SECONDS = 0.25
_MATH = "/Script/Engine.KismetMathLibrary"
_COMPONENT = "/Script/Engine.ActorComponent"

for _old in ["/Game/Components/Enchantments/GravityPulse/WBP_SequelPulseTest"]:   # old tries
    remove(_old)


def potion_watch(bp, variables, find):
    """The shared start of both: variables (name -> type) added, BeginPlay starting Watch every WATCH_SECONDS, and
    Watch on the host looking at the wearer's potion slot. find: owner components to cast to, in order.
    Returns the graph, a dict of the casts (class -> (node, pin)), the IsOnCooldown node, the tier node and the exec
    point (node, pin) reached when the potion slot is there."""
    for name, kind in dict(Started="bool", WasCooling="bool", **variables).items():
        check(LIB.add_variable(bp, name, kind), "variable " + name)
    LIB.compile(bp)
    g = Graph(bp)
    g.row(0)
    begin = g.event(_COMPONENT, "ReceiveBeginPlay")
    timer = g.call("/Script/Engine.KismetSystemLibrary", "K2_SetTimer", FunctionName="Watch", Time=WATCH_SECONDS,
                   bLooping="true")
    g.flow(begin, timer)

    g.row(300)
    watch = g.custom_event("Watch")
    owner = g.call(_COMPONENT, "GetOwner")
    authority = g.call("/Script/Engine.Actor", "HasAuthority")
    g.link(owner, "ReturnValue", authority, "self")
    on_host = g.branch((authority, "ReturnValue"))
    g.flow(watch, on_host)
    casts, steps = {}, [(on_host, "then")]
    for cls in ["/Script/Dungeons.EquipmentComponent"] + find:
        found = g.call("/Script/Engine.Actor", "GetComponentByClass", ComponentClass=cls)
        g.link(owner, "ReturnValue", found, "self")
        casts[cls] = g.cast(cls, (found, "ReturnValue"))
        steps.append(casts[cls][0])
    g.flow(*steps)

    g.row(600)
    equipment = casts["/Script/Dungeons.EquipmentComponent"]
    slots = g.call("/Script/Dungeons.EquipmentComponent", "GetSlotsOfType", Type="HealthPotion")
    g.link(equipment[0], equipment[1], slots, "self")
    slot = g.item_at((slots, "ReturnValue"))
    valid = g.call("/Script/Engine.KismetSystemLibrary", "IsValid")
    g.link(slot[0], slot[1], valid, "Object")
    has_slot = g.branch((valid, "ReturnValue"))
    cooling = g.call("/Script/Dungeons.ItemSlot", "IsOnCooldown")
    g.link(slot[0], slot[1], cooling, "self")
    tier = g.call(_MATH, "Clamp", Min=1, Max=3)
    g.link(g.var("Level"), "Level", tier, "Value")
    g.flow(steps[-1], has_slot)
    return g, casts, cooling, tier, (has_slot, "then")


def note_cooling(g, cooling):
    """A Set WasCooling = the slot's cooldown now."""
    node = g.var("WasCooling", set_=True)
    g.link(cooling, "ReturnValue", node, "WasCooling")
    return node


def set_value(g, name, value):
    """A Set name = value (node, pin) or a constant."""
    node = g.var(name, set_=True)
    if isinstance(value, tuple):
        g.link(value[0], value[1], node, name)
    else:
        g.set(node, **{name: value})
    return node


def just_started(g, cooling):
    """cooling now and not at the last look."""
    was_not = g.call(_MATH, "Not_PreBool")
    g.link(g.var("WasCooling"), "WasCooling", was_not, "A")
    both = g.call(_MATH, "BooleanAND")
    g.link(cooling, "ReturnValue", both, "A")
    g.link(was_not, "ReturnValue", both, "B")
    return both, "ReturnValue"


# --- Recycler -> Ancient Alchemy --------------------------------------------------------------------------------
# The first look only notes whether the potion is cooling down (an item put on while it cools down pays nothing);
# after that, a cooldown that has just started is a potion used.
_bp = blueprint(RECYCLER, unreal.load_class(None, "/Script/Dungeons.Recycler"))
_g, _casts, _cooling, _tier, _ready = potion_watch(_bp, {}, ["/Script/Dungeons.SoulComponent"])
_g.row(900)
_started = _g.branch((_g.var("Started"), "Started"))
_g.flow(_ready, _started)
_g.flow((_started, "else"), note_cooling(_g, _cooling), set_value(_g, "Started", "true"))
_g.row(1200)
_used = _g.branch(just_started(_g, _cooling))
_times = _g.call(_MATH, "Multiply_IntInt", B=SOULS_PER_TIER)
_g.link(_tier, "ReturnValue", _times, "A")
_amount = _g.call(_MATH, "Add_IntInt", B=SOULS_BASE)
_g.link(_times, "ReturnValue", _amount, "A")
_pay = _g.call("/Script/Dungeons.SoulComponent", "ServerAddSouls")
_souls = _casts["/Script/Dungeons.SoulComponent"]
_g.link(_souls[0], _souls[1], _pay, "self")
_g.link(_amount, "ReturnValue", _pay, "Amount")
_remember = note_cooling(_g, _cooling)
_g.flow((_started, "then"), _used)
_g.flow((_used, "then"), _pay, _remember)
_g.flow((_used, "else"), _remember)
compile_save(_bp, "Ancient Alchemy (Recycler)")

# --- Explorer -> Bottomless Brew -----------------------------------------------------------------------------------
# The potion itself plus Charges extra drinks (full = tier x EXTRA_DRINKS_PER_TIER). Our blueprint keeps the potion's
# own cooldown itself (BaseLeft): a drink while BaseLeft is 0 is the potion itself (BaseLeft = Cooldown), any other
# drink is an extra (one charge). The game's cooldown is removed whenever a drink is ready - the potion itself
# (BaseLeft 0) or an extra - so an extra can be drunk while the potion cools down, and a ready potion is drunk
# before the extras (user, 2026-11-05). Each look, in order:
#   first look   Charges = all; BaseLeft = Cooldown if the potion is cooling already; the counter on the wearer's
#                own screen
#   clocks       BaseLeft counts down; while charges are missing, Recharge counts up and one comes back every
#                Cooldown seconds
#   Pending      (set at the last look) remove the game's cooldown
#   a drink      (a cooldown that has just started) the potion itself or an extra, as above
#   ready?       cooling, and BaseLeft is 0 or a charge is left -> Pending (removed at the next look, so Ancient
#                Alchemy, looking every WATCH_SECONDS too, always sees the drink)
#   counter      "2/3" (the extras left; user, 2026-11-06: just the number, next to the potion)
# Cooldown = POTION_COOLDOWN x the wearer's PotionCooldownMultiplier (ItemAttributeSet; potion cooldown perks).
# The counter shows only on the wearer's own screen when the wearer is the host (solo, or the host in co-op): the
# charges are counted on the host. It sits under the game's own screens (ZOrder -1), so menus cover it.
# 2026-11-08 (user): swapped with Barrier Brew - Bottomless Brew sits on Food Reserves now (its card rows are fixed text
# either way; Food Reserves' food stays off by Formulas.toml FoodReserves = 0), Barrier Brew on Explorer (whose card
# shows its per-tier number as a percent: Barrier Brew's 30 / 50 / 70%).
remove("/Game/Components/Enchantments/Explorer/WBP_SequelBrewCount")
remove("/Game/Components/Enchantments/FoodReserves/GE_SequelBarrierBrew")
BREW_VIEW = "/Game/Components/Enchantments/FoodReserves/WBP_SequelBrewCount"
BREW_VIEW_CLASS = BREW_VIEW + ".WBP_SequelBrewCount_C"
POTION_COOLDOWN = 45.0   # the healing potion's cooldown in its definition (+0x98, read in the game 2026-11-05)
# the game's potion cooldown effect, for GetActiveEffects: effects whose tags (own + granted) include the cooldown tag.
# A gameplay tag query's token stream: version 0, has a root, AnyTagsMatch (1), 1 tag, tag 0.
COOLDOWN_QUERY = ('(OwningTagQuery=(TokenStreamVersion=0,TagDictionary=((TagName="%s")),QueryTokenStream=(0,1,1,1,0)))'
                  % POTION_COOLDOWN_TAG)
# Refreshment (PotionThirstMelee/Ranged) cuts the real potion only (user, 2026-11-06: like the extra rolls - the
# extras just refill with time): while the game's cooldown runs the game cuts it, and the follow step below moves that
# cut to BaseLeft. While the game's cooldown is off (a drink is ready), nothing is cut. (A kill listener that also cut
# the extras' refill is gone: the soul component's OnAnyMobKilled only fires for players with soul gathering.)
_view = fresh(BREW_VIEW, unreal.WidgetBlueprint, unreal.WidgetBlueprintFactory())
widget(_view, "", unreal.CanvasPanel, "Root")
_line = label(_view, "Root", "Info", "", 20, is_variable=True)
_line.set_editor_property("justification", unreal.TextJustify.CENTER)
_line.set_editor_property("shadow_offset", unreal.Vector2D(2, 2))
_line.set_editor_property("shadow_color_and_opacity", unreal.LinearColor(0, 0, 0, 0.85))
_spot = _line.get_editor_property("slot")
_spot.set_anchors(unreal.Anchors(minimum=unreal.Vector2D(0.5, 1.0), maximum=unreal.Vector2D(0.5, 1.0)))
_spot.set_alignment(unreal.Vector2D(0.5, 1.0))
_spot.set_position(unreal.Vector2D(117, -128))   # just above the potion slot (user, 2026-11-07; was above artifact 1)
_spot.set_size(unreal.Vector2D(420, 34))
# Hidden during cutscenes: every frame, the game's own "a cutscene is playing" check (the game's sound blueprints use it).
_vg = Graph(_view)
_in_cutscene = _vg.branch((_vg.call("/Script/Dungeons.DungeonsAudioUtils", "CinematicPlaying"), "ReturnValue"))
_vg.flow(_vg.event("/Script/UMG.UserWidget", "Tick"), _in_cutscene)
for _pin, _seen in [("then", "Collapsed"), ("else", "HitTestInvisible")]:
    _show = _vg.call("/Script/UMG.Widget", "SetVisibility", InVisibility=_seen)
    _vg.link(_vg.var("Info"), "Info", _show, "self")
    _vg.flow((_in_cutscene, _pin), _show)
compile_save(_view, "Bottomless Brew counter")

_bp = blueprint(FOOD_RESERVES, unreal.load_class(None, "/Script/Dungeons.FoodReserves"))
_g, _casts, _cooling, _tier, _ready = potion_watch(
    _bp, dict(Pending="bool", Charges="int", Recharge="float", BaseLeft="float", Expected="float", Followed="bool",
              CooldownQuery="struct:/Script/GameplayAbilities.GameplayEffectQuery",
              View="object:" + BREW_VIEW_CLASS),
    [])
check(LIB.set_variable_default(_bp, "Expected", "-1.0"), "Expected default")
check(LIB.set_variable_default(_bp, "CooldownQuery", COOLDOWN_QUERY), "CooldownQuery default")
_full = _g.call(_MATH, "Multiply_IntInt", B=EXTRA_DRINKS_PER_TIER)
_g.link(_tier, "ReturnValue", _full, "A")
_asc = _g.call("/Script/GameplayAbilities.AbilitySystemBlueprintLibrary", "GetAbilitySystemComponent")
_g.link(_g.call(_COMPONENT, "GetOwner"), "ReturnValue", _asc, "Actor")
_multiplier = _g.call("/Script/GameplayAbilities.AbilitySystemBlueprintLibrary", "GetFloatAttribute")
_g.link(_g.call(_COMPONENT, "GetOwner"), "ReturnValue", _multiplier, "Actor")
check(LIB.set_attribute_pin(_bp, _g.name, _multiplier, "Attribute",
                            unreal.load_class(None, "/Script/Dungeons.ItemAttributeSet"), "PotionCooldownMultiplier"),
      "PotionCooldownMultiplier attribute")
_cooldown = _g.call(_MATH, "Multiply_FloatFloat", B=POTION_COOLDOWN)
_g.link(_multiplier, "ReturnValue", _cooldown, "A")
_COOLDOWN = (_cooldown, "ReturnValue")


def _link_value(value, node, pin):
    if isinstance(value, tuple):
        _g.link(value[0], value[1], node, pin)
    else:
        _g.set(node, **{pin: value})


def _math(fn, a, b):
    node = _g.call(_MATH, fn)
    _link_value(a, node, "A")
    _link_value(b, node, "B")
    return node, "ReturnValue"


def _v(name):
    return _g.var(name), name


# first look (+ the counter on the wearer's own screen)
_g.row(900)
_started = _g.branch(_v("Started"))
_g.flow(_ready, _started)
_base_at_start = _g.call(_MATH, "SelectFloat", B=0.0)
_g.link(_COOLDOWN[0], _COOLDOWN[1], _base_at_start, "A")
_g.link(_cooling, "ReturnValue", _base_at_start, "bPickA")
_pawn = _g.cast("/Script/Engine.Pawn", (_g.call(_COMPONENT, "GetOwner"), "ReturnValue"))
_local = _g.call("/Script/Engine.Pawn", "IsLocallyControlled")
_g.link(_pawn[0], _pawn[1], _local, "self")
_is_local = _g.branch((_local, "ReturnValue"))
_make = _g.node("/Script/UMGEditor.K2Node_CreateWidget")
_g.set(_make, Class=BREW_VIEW_CLASS)
_keep = set_value(_g, "View", (_make, "ReturnValue"))
_up = _g.call("/Script/UMG.UserWidget", "AddToViewport", ZOrder=-1)   # under the game's menus
_g.link(_make, "ReturnValue", _up, "self")
_g.flow((_started, "else"), note_cooling(_g, _cooling), set_value(_g, "Charges", (_full, "ReturnValue")),
        set_value(_g, "BaseLeft", (_base_at_start, "ReturnValue")), set_value(_g, "Started", "true"),
        _pawn[0], _is_local)
_g.flow((_is_local, "then"), _make, _keep, _up)

# clocks
_g.row(1200)
_less = _math("Subtract_FloatFloat", _v("BaseLeft"), WATCH_SECONDS)
_floor = _math("FMax", _less, 0.0)
_tick_base = set_value(_g, "BaseLeft", _floor)
_g.flow((_started, "then"), _tick_base)
_is_missing = _g.branch(_math("Less_IntInt", _v("Charges"), (_full, "ReturnValue")))
_counted = set_value(_g, "Recharge", _math("Add_FloatFloat", _v("Recharge"), WATCH_SECONDS))
_is_due = _g.branch(_math("GreaterEqual_FloatFloat", _v("Recharge"), _COOLDOWN))
_back = set_value(_g, "Recharge", 0.0)
_full_now = set_value(_g, "Recharge", 0.0)
_g.flow(_tick_base, _is_missing)
_g.flow((_is_missing, "then"), _counted, _is_due)
_g.flow((_is_due, "then"), set_value(_g, "Charges", _math("Add_IntInt", _v("Charges"), 1)), _back)
_g.flow((_is_missing, "else"), _full_now)

# follow the game's cooldown: while it runs, its time left should drop WATCH_SECONDS per look; a bigger drop is
# something cutting the potion's cooldown (Refreshment's kills) - that cut goes to BaseLeft only
_g.row(1350)
_is_running = _g.branch((_cooling, "ReturnValue"))
for _end in [(_is_due, "else"), (_back, "then"), (_full_now, "then")]:
    _g.flow(_end, _is_running)
_effects = _g.call("/Script/GameplayAbilities.AbilitySystemComponent", "GetActiveEffects")
_g.link(_asc, "ReturnValue", _effects, "self")
_g.link(_g.var("CooldownQuery"), "CooldownQuery", _effects, "Query")
_found = _g.array_call("Array_Length", (_effects, "ReturnValue"), "TargetArray")
_has_effect = _g.branch(_math("Greater_IntInt", (_found, "ReturnValue"), 0))
_time_left = _g.call("/Script/GameplayAbilities.AbilitySystemBlueprintLibrary", "GetActiveGameplayEffectRemainingDuration")
_first = _g.item_at((_effects, "ReturnValue"))
_g.link(_first[0], _first[1], _time_left, "ActiveHandle")
_LEFT = (_time_left, "ReturnValue")
_cut = _math("Subtract_FloatFloat", _v("Expected"), _LEFT)
_known = _math("GreaterEqual_FloatFloat", _v("Expected"), 0.0)
_is_cut = _g.branch(_math("BooleanAND", _known, _math("Greater_FloatFloat", _cut, 0.2)))
_cut_base = set_value(_g, "BaseLeft", _math("FMax", _math("Subtract_FloatFloat", _v("BaseLeft"), _cut), 0.0))
_expect = set_value(_g, "Expected", _math("Subtract_FloatFloat", _LEFT, WATCH_SECONDS))
_unknown = set_value(_g, "Expected", -1.0)
_g.flow((_is_running, "then"), _effects, _has_effect)
_g.flow((_has_effect, "then"), _time_left, _is_cut)
_g.flow((_is_cut, "then"), _cut_base, _expect)
_g.flow((_is_cut, "else"), _expect)
_g.flow((_has_effect, "else"), _unknown)
_g.flow((_is_running, "else"), _unknown)
# Followed: the game's cooldown is on, so a Refreshment cut reaches BaseLeft through it (above)
_followed = set_value(_g, "Followed", "true")
_unfollowed = set_value(_g, "Followed", "false")
_g.flow((_expect, "then"), _followed)
_g.flow((_unknown, "then"), _unfollowed)

# Pending: remove the game's cooldown (a drink is ready)
_g.row(1500)
_pending = _g.branch(_v("Pending"))
for _end in [(_followed, "then"), (_unfollowed, "then")]:
    _g.flow(_end, _pending)
_remove = _g.call("/Script/GameplayAbilities.AbilitySystemComponent", "RemoveActiveEffectsWithGrantedTags",   # a cooldown GRANTS its tag (WithTags only matches label tags)
                  Tags='(GameplayTags=((TagName="%s")))' % POTION_COOLDOWN_TAG)
_g.link(_asc, "ReturnValue", _remove, "self")
_wiped = set_value(_g, "WasCooling", "false")
_g.flow((_pending, "then"), _remove, set_value(_g, "Pending", "false"), _wiped)

# a drink: the potion itself when it is ready (or no extra is left), else an extra
_g.row(1800)
_is_drink = _g.branch(just_started(_g, _cooling))
_g.flow((_pending, "else"), _is_drink)
_base_ready = _math("LessEqual_FloatFloat", _v("BaseLeft"), 0.0)
_none_left = _math("LessEqual_IntInt", _v("Charges"), 0)
_is_base = _g.branch(_math("BooleanOR", _base_ready, _none_left))
_used_base = set_value(_g, "BaseLeft", _COOLDOWN)
_used_extra = set_value(_g, "Charges", _math("Subtract_IntInt", _v("Charges"), 1))
_g.flow((_is_drink, "then"), _is_base)
_g.flow((_is_base, "then"), _used_base)
_g.flow((_is_base, "else"), _used_extra)

# ready? cooling, and the potion itself or an extra can be drunk -> remove the cooldown at the next look
_g.row(2100)
_can = _math("BooleanOR", _math("LessEqual_FloatFloat", _v("BaseLeft"), 0.0),
             _math("Greater_IntInt", _v("Charges"), 0))
_is_ready = _g.branch(_math("BooleanAND", (_cooling, "ReturnValue"), _can))
for _end in [(_is_drink, "else"), (_used_base, "then"), (_used_extra, "then")]:
    _g.flow(_end, _is_ready)
_mark = set_value(_g, "Pending", "true")
_g.flow((_is_ready, "then"), _mark)

# remember the cooldown, then the counter
_g.row(2400)
_noted = note_cooling(_g, _cooling)
for _end in [(_is_ready, "else"), (_mark, "then")]:
    _g.flow(_end, _noted)
_shown = _g.call("/Script/Engine.KismetSystemLibrary", "IsValid")
_g.link(_g.var("View"), "View", _shown, "Object")
_has_view = _g.branch((_shown, "ReturnValue"))
_g.flow(_noted, _has_view)
_g.flow((_wiped, "then"), _has_view)


def _str(node_pin):
    node = _g.call("/Script/Engine.KismetStringLibrary", "Conv_IntToString")
    _g.link(node_pin[0], node_pin[1], node, "InInt")
    return node, "ReturnValue"


def _concat(*parts):
    out = None
    for part in parts:
        node = _g.call("/Script/Engine.KismetStringLibrary", "Concat_StrStr")
        if out:
            _g.link(out[0], out[1], node, "A")
        else:
            _g.set(node, A="")
        if isinstance(part, tuple):
            _g.link(part[0], part[1], node, "B")
        else:
            _g.set(node, B=part)
        out = (node, "ReturnValue")
    return out


_g.row(2700)
_words = _concat(_str(_v("Charges")), "/", _str((_full, "ReturnValue")))
_as_text = _g.call("/Script/Engine.KismetTextLibrary", "Conv_StringToText")
_g.link(_words[0], _words[1], _as_text, "InString")
_put = _g.call("/Script/UMG.TextBlock", "SetText")
_g.link(_g.var("Info", owner=BREW_VIEW_CLASS, target=(_g.var("View"), "View")), "Info", _put, "self")
_g.link(_as_text, "ReturnValue", _put, "InText")
_g.flow((_has_view, "then"), _put)

# Refreshed(Seconds): told by the wearer's Refreshment on a kill (user, 2026-11-08: its kills shorten the extras'
# refill too). The refill clock moves on by Seconds while drinks are missing; the potion's own clock (BaseLeft) too,
# but only while the game's cooldown is off (a drink ready) - while it runs, Refreshment cuts it and the follow step
# above already moves that cut to BaseLeft.
_g.row(3300)
_refreshed = _g.custom_event("Refreshed", "Seconds=float")
_SECONDS = (_refreshed, "Seconds")
_is_followed = _g.branch(_v("Followed"))
_cut_own = set_value(_g, "BaseLeft", _math("FMax", _math("Subtract_FloatFloat", _v("BaseLeft"), _SECONDS), 0.0))
_misses = _g.branch(_math("Less_IntInt", _v("Charges"), (_full, "ReturnValue")))
_sooner = set_value(_g, "Recharge", _math("Add_FloatFloat", _v("Recharge"), _SECONDS))
_g.flow(_refreshed, _is_followed)
_g.flow((_is_followed, "else"), _cut_own, _misses)
_g.flow((_is_followed, "then"), _misses)
_g.flow((_misses, "then"), _sooner)

# the counter goes when the enchantment does (armor taken off, level left)
_g.row(3000)
_end_play = _g.event(_COMPONENT, "ReceiveEndPlay")
_gone = _g.call("/Script/Engine.KismetSystemLibrary", "IsValid")
_g.link(_g.var("View"), "View", _gone, "Object")
_has = _g.branch((_gone, "ReturnValue"))
_hide = _g.call("/Script/UMG.Widget", "RemoveFromParent")
_g.link(_g.var("View"), "View", _hide, "self")
_g.flow(_end_play, _has)
_g.flow((_has, "then"), _hide)
compile_save(_bp, "Bottomless Brew (Food Reserves)")

# Buff icons on the left of the screen: the game's own icon widgets, named by placeholders at the game's paths. The
# placeholders are cooked but never packed (blueprints.py leaves out everything placeholder() lists), so in the game
# the effect's link reaches the real icon. Our effects' buffs borrow these until we draw our own (user, 2026-11-06).
GAME_ICONS = "/Game/UI/StatusEffects/GameplayEffect/Icons/"
_placeholders = {}
PLACEHOLDER_LIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_placeholders.json")


def placeholder(path):
    """Note path (a /Game package) as a placeholder for a game asset: cooked, so our blueprints link to it, but
    tools/blueprints.py deletes it from the cooked files before packing, so in the game the link reaches the real
    asset (nothing of the game's is copied)."""
    import json
    try:
        listed = json.load(open(PLACEHOLDER_LIST))
    except Exception:   # the editor's Python 2.7: IOError when there is no list yet
        listed = []
    if path not in listed:
        json.dump(sorted(listed + [path]), open(PLACEHOLDER_LIST, "w"), indent=1)


def game_icon(name):
    """The class of a placeholder for the game's buff icon widget GAME_ICONS + name."""
    if name not in _placeholders:
        icon = fresh(GAME_ICONS + name, unreal.WidgetBlueprint, unreal.WidgetBlueprintFactory())
        compile_save(icon, "placeholder for the game's " + name)
        placeholder(GAME_ICONS + name)
        _placeholders[name] = assets.load_blueprint_class(GAME_ICONS + name)
    return _placeholders[name]


BUFF_CROP = (0.32, 0.68)


def buff_icon(spec):
    """A buff's icon widget class. spec "UMG_<Name>" = the game's own buff icon (game_icon); otherwise spec is the
    path of an enchantment's card icon texture (e.g. /Game/Components/Enchantments/Explorer/T_Explorer_Icon)
    and the buff shows that picture (user, 2026-11-08: a buff's icon should match its enchantment). Our widget is a
    scale box with a clipping frame and one image, next to the texture: UMG_SequelBuff_<Id>. A texture of the game's own (not one of the
    user's, which ship at the game's path) gets a placeholder there - a blank image, never packed - so in the game
    the widget shows the real one."""
    if spec.startswith("UMG_"):
        return game_icon(spec)
    if spec in _placeholders:
        return _placeholders[spec]
    folder, name = spec.rsplit("/", 1)
    if assets.load_asset(spec) is None:
        import_icon("T_SequelBlankShine.png", folder, name)
        placeholder(spec)
    path = folder + "/UMG_SequelBuff_" + name[2:-5]   # T_<Id>_Icon -> UMG_SequelBuff_<Id>
    icon = fresh(path, unreal.WidgetBlueprint, unreal.WidgetBlueprintFactory())
    # Only the square inside the card icon's diamond shows (user, 2026-11-08: buff icons are square). The diamonds
    # span about 32..223 of 256 px (the user's art and the game's alike), so the square inside is about 0.32..0.68:
    # the picture is drawn 1 / 0.36 times bigger, centred, in a 40 x 40 frame that clips the rest (no texture is
    # cut or copied, so the game's own icons work too).
    widget(icon, "", unreal.ScaleBox, "Fit")
    frame = widget(icon, "Fit", unreal.SizeBox, "Frame")
    frame.set_width_override(40.0)    # also turns the override on
    frame.set_height_override(40.0)
    frame.set_editor_property("clipping", unreal.WidgetClipping.CLIP_TO_BOUNDS)
    picture = widget(icon, "Frame", unreal.Image, "Picture")
    picture.set_brush_from_texture(assets.load_asset(spec), False)
    brush = picture.get_editor_property("brush")
    brush.set_editor_property("image_size", unreal.Vector2D(40, 40))   # the game's buff pictures are 40 x 40
    picture.set_editor_property("brush", brush)
    zoom = 1.0 / (BUFF_CROP[1] - BUFF_CROP[0])
    turn = picture.get_editor_property("render_transform")
    turn.set_editor_property("scale", unreal.Vector2D(zoom, zoom))
    picture.set_editor_property("render_transform", turn)
    picture.set_editor_property("render_transform_pivot", unreal.Vector2D(0.5, 0.5))
    compile_save(icon, "buff icon " + name)
    check(picture.get_editor_property("brush").get_editor_property("resource_object") is not None,
          "buff icon %s shows its picture" % name)
    check(abs(picture.get_editor_property("render_transform").get_editor_property("scale").x - zoom) < 1e-3,
          "buff icon %s: the square inside the diamond" % name)
    _placeholders[spec] = assets.load_blueprint_class(path)
    return _placeholders[spec]


def game_particle(path):
    """The object path of a placeholder for the game's particle effect at path (a /Game package): our blueprints
    spawn it directly (loading it by name at run time did nothing in game, 2026-11-07)."""
    if path not in _placeholders:
        effect = fresh(path, unreal.ParticleSystem, unreal.ParticleSystemFactoryNew())
        assets.save_loaded_asset(effect)
        placeholder(path)
        _placeholders[path] = path + "." + path.rsplit("/", 1)[1]
    return _placeholders[path]


# --- Sponge Strike -> Shadowcloak ----------------------------------------------------------------------------------
# A kill by the wearer has a CLOAK_BASE + CLOAK_PER_TIER x tier chance (15 / 20 / 25%, user 2026-11-05) to put the
# wearer in Shadow Form: the game's Backstabber's Brew effect, applied the way the game's Shadow Shot does it (its
# code at exe+0xAB6460, read 2026-11-05): a spec of the effect at the enchantment's level with set-by-caller values
# "Duration" (seconds; the effect's duration goes through StatusDurationModCalculation) and "Magnitude" (the next
# melee hit's boost, MeleePowerBoostAmount), applied to the wearer itself. Kills: every WATCH_SECONDS on the host it
# reads the mission's count of hostile mobs killed (DungeonsGameState.HostileMobsKilled); the kills since the last look
# roll once together (1 - (1 - chance)^kills). It counts every player's and pet's kills, so in co-op a teammate's kill
# can cloak you too. (First built on the soul component's OnAnyMobKilled, which only fires for a player whose soul
# gathering is above 0 - soul gear - so it never fired in test, 2026-11-06.) Sponge Strike's own effect is dead (no power scaling), and its only item,
# the Sponge Striker, gets Pain Cycle III instead (Builtins.toml), so nothing is lost. Shadow Shot (the Veiled /
# Shrieking Crossbow's, 50% on that bow's arrow kills) stays the game's own; both can be worn and both trigger.
# Rolls on melee and ranged: settings/launcher/EnchantGear.toml (unlock + also_on). The effect is linked through a
# placeholder at the game's path (the game's asset isn't in our project, and a copy must not ship).
# 2026-11-08 (user): moved from Sponge Strike - which has no icon the game lists, so ours never showed - to Rushdown (a
# melee kill enchantment no item in the mod carries; its icon is listed). The name SPONGE_STRIKE stays for the code.
SPONGE_STRIKE = "/Game/Content_DLC3/Components/Enchantments/Rushdown/BP_Rushdown"
for _old in ("/Game/Content_DLC5/Components/Enchantments/SpongeStrike/BP_SpongeStrike",
             "/Game/Content_DLC5/Components/Enchantments/SpongeStrike/T_SpongeStrike_Icon",
             "/Game/Content_DLC4/Components/Enchantments/ChargingAcceleration/BP_ChargingAcceleration",
             "/Game/Content_DLC4/Components/Enchantments/ChargingAcceleration/GE_SequelNoCharge",
             "/Game/Content_DLC4/Components/Enchantments/ChargingAcceleration/T_ChargingAcceleration_Icon"):
    remove(_old)   # the old hosts go back to the game's own
SHADOW_FORM = ("/Game/Actors/Items/Potions/BackstabbersBrew/BP_BackstabbersBrewGameplayEffect"
               ".BP_BackstabbersBrewGameplayEffect_C")
CLOAK_BASE, CLOAK_PER_TIER = 0.10, 0.05   # 15 / 20 / 25%
CLOAK_SECONDS = 3.0                       # Shadow Shot's DurationMagnitude
CLOAK_BOOST = 8.0                         # Shadow Shot's MeleePowerBoostAmount
_GAS = "/Script/GameplayAbilities.AbilitySystemBlueprintLibrary"
_ASC = "/Script/GameplayAbilities.AbilitySystemComponent"

# Shadow Form's effect, linked through a placeholder at the game's path (loading it by name at run time did nothing
# in game - as with the particles, 2026-11-07): cooked so our blueprint links to it, never packed
_SHADOW_PATH = SHADOW_FORM.split(".")[0]
compile_save(blueprint(_SHADOW_PATH, unreal.GameplayEffect), "placeholder for the game's Shadow Form effect")
placeholder(_SHADOW_PATH)
# (the graph: with the kill-credit enchantments further down - it counts the kills credited to the wearer)


def import_icon(png, folder, name):
    """The user's icon art (unreal/Art/<png>) as the enchantment's card icon texture folder/name - the game finds an
    enchantment's icon by name next to its blueprint (T_<Id>_Icon; MI_<Id>_Icon is the animated one, optional)."""
    task = unreal.AssetImportTask()
    task.set_editor_property("filename", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Art", png))
    task.set_editor_property("destination_path", folder)
    task.set_editor_property("destination_name", name)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("automated", True)
    task.set_editor_property("save", True)
    tools.import_asset_tasks([task])
    texture = assets.load_asset(folder + "/" + name)
    check(texture is not None, "icon " + name)
    texture.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_EDITOR_ICON)  # as the
    texture.set_editor_property("lod_group", unreal.TextureGroup.TEXTUREGROUP_PROJECT01)                    # game's
    assets.save_loaded_asset(texture)


# The user's icons (unreal/Art, 2026-11-07 / 08). The game finds an icon by name through its own asset list, so only an
# icon the game already lists can be replaced: ours goes in at that same path, and the old icon's animated shine
# (T_<Id>Shine_Icon, used by MI_<Id>_Icon) is made blank so it doesn't play over ours. (Shadowcloak and Shatter moved to
# Rushdown and Thrive Under Pressure for this: Sponge Strike and Charging Acceleration have no listed icon.)
_ICONS = [  # (id, folder, has the game a shine for it)
    ("FoodReserves", "/Game/Components/Enchantments/FoodReserves", True),          # Bottomless Brew (2026-11-08)
    ("Explorer", "/Game/Components/Enchantments/Explorer", True),                  # Barrier Brew (2026-11-08)
    ("LevitationShot", "/Game/Components/Enchantments/LevitationShot", True),      # Relentless
    ("Recycler", "/Game/Components/Enchantments/Recycler", True),                  # Ancient Alchemy
    ("Altruistic", "/Game/Components/Enchantments/Altruistic", False),             # Venom Siphon (no MI / shine)
    ("GravityPulse", "/Game/Components/Enchantments/GravityPulse", True),          # Artifact Amplifier
    ("EmeraldDivination", "/Game/Content_DLC3/Components/Enchantments/EmeraldDivination", True),   # Ignite
    ("Rushdown", "/Game/Content_DLC3/Components/Enchantments/Rushdown", True),                     # Shadowcloak
    ("ThriveUnderPressure", "/Game/Components/Enchantments/ThriveUnderPressure", True),             # Shatter
]
for _id, _folder, _shine in _ICONS:
    import_icon("T_%s_Icon.png" % _id, _folder, "T_%s_Icon" % _id)
    if _shine:
        import_icon("T_SequelBlankShine.png", _folder, "T_%sShine_Icon" % _id)

def _nearest_gate(mob, after):
    """From the exec (node, pin) after: go on only if no other player is closer to mob (node, pin) than the wearer -
    the hit spark can't tell who hit, so a hit counts for the nearest player only (user, 2026-11-07: only your own
    direct hits; a teammate's hit must not trigger your enchantment). Needs a bool variable Closer. Returns the exec
    (node, pin) that goes on."""
    me = (_g.call(_COMPONENT, "GetOwner"), "ReturnValue")
    reset = set_value(_g, "Closer", "false")
    players = _g.call("/Script/Engine.GameplayStatics", "GetAllActorsOfClass", ActorClass="/Script/Dungeons.PlayerCharacter")
    last = _g.array_call("Array_LastIndex", (players, "OutActors"), "TargetArray")
    loop = _g.macro("ForLoop", FirstIndex=0)
    _g.link(last, "ReturnValue", loop, "LastIndex")
    other = _g.item_at((players, "OutActors"), (loop, "Index"))
    theirs = _g.call("/Script/Engine.Actor", "GetDistanceTo")
    _g.link(other[0], other[1], theirs, "self")
    _g.link(mob[0], mob[1], theirs, "OtherActor")
    mine = _g.call("/Script/Engine.Actor", "GetDistanceTo")
    _g.link(me[0], me[1], mine, "self")
    _g.link(mob[0], mob[1], mine, "OtherActor")
    someone = _g.call(_MATH, "NotEqual_ObjectObject")
    _g.link(other[0], other[1], someone, "A")
    _g.link(me[0], me[1], someone, "B")
    closer = _g.branch(_math("BooleanAND", (someone, "ReturnValue"),
                             _math("Less_FloatFloat", (theirs, "ReturnValue"), (mine, "ReturnValue"))))
    _g.flow(after, reset, players, loop)
    _g.flow((loop, "LoopBody"), closer)
    _g.flow((closer, "then"), set_value(_g, "Closer", "true"))
    not_closer = _g.call(_MATH, "Not_PreBool")
    _g.link(_g.var("Closer"), "Closer", not_closer, "A")
    mine_go = _g.branch((not_closer, "ReturnValue"))
    _g.flow((loop, "Completed"), mine_go)
    return mine_go, "then"


# --- Knockback -> Sweeping Edge -------------------------------------------------------------------------------------
# Every melee hit splashes (user, 2026-11-07: an Anchor-style splash around the mob hit, scaling with our own hit):
# other hostile mobs within SPLASH_RADIUS of the mob hit take SPLASH_BASE + SPLASH_PER_TIER x tier (10 / 20 / 30%) of
# the hit's damage. The game plays GameplayCue.Hit.Melee on every mob a melee swing hits, but passes neither the hitter
# nor the damage (seen in game: Instigator / EffectCauser None, RawMagnitude 0), so:
#   - our copy of the hit spark (the cue, further down) tells every Sweeping Edge wearer within SPLASH_HITTER_RANGE of
#     the mob hit: Struck(mob)
#   - this enchantment notes the health of the mobs around its wearer every SPLASH_LOOK seconds; at the look after a
#     Struck, the mob's health drop since the last look is the hit's damage (two hits on one mob between looks merge);
#     all drops are worked out first, then the splashes go out (so one splash doesn't inflate another)
#   - the splash: from the wearer's own ability system, GE_SequelSplash (instant, Health + set-by-caller Damage,
#     negative). Our damage plays no hit cue, so it can't chain.
# Knockback's own code still runs on every hit (its chance is 100% in Formulas.toml, so the card reads "100% chance to
# trigger") and shows its "triggered" icon on the left; its push is off (knockbackPower 0). The first Sweeping Edge
# (2026-11-06, wider and longer swings: MeleeAttackAngle / RangeMultiplier) is gone - its effect copies piled up
# ("x23") once their numbers were 1.
KNOCKBACK = "/Game/Components/Enchantments/Knockback/BP_Knockback"
KNOCKBACK_CLASS = KNOCKBACK + ".BP_Knockback_C"
SPLASH_RADIUS, SPLASH_BASE, SPLASH_PER_TIER = 500.0, 0.1, 0.1   # 5 blocks (user, 2026-11-07: was 3, wider); 20 / 30 / 40% (user, 2026-11-08: was 10 / 20 / 30)
SPLASH_LOOK, SPLASH_WATCHED, SPLASH_HITTER_RANGE = 0.1, 2000.0, 1200.0
SPLASH_EFFECT = "/Game/Components/Enchantments/Knockback/GE_SequelSplash"
_BASE = "/Script/Dungeons.BaseCharacter"
_ACTOR = "object:/Script/Engine.Actor"
remove("/Game/Components/Enchantments/Knockback/GE_SequelSweepingEdge")   # the first Sweeping Edge

_hit_fx = blueprint(SPLASH_EFFECT, unreal.GameplayEffect)
compile_save(_hit_fx, "Sweeping Edge splash effect")
check(LIB.make_instant_set_by_caller_effect(_hit_fx, unreal.load_class(None, "/Script/Dungeons.HealthAttributeSet"),
                                            "Health", 0, "Damage"),
      "Sweeping Edge splash: Health + set-by-caller Damage, instant")
# the game's damage number and hit flash for our damage (seen in game: our damage landed but showed nothing, user
# 2026-11-07); BP_DamageNumberNotifyStatic shows |RawMagnitude| = the change of Health
check(LIB.add_effect_cue(_hit_fx, unreal.load_class(None, "/Script/Dungeons.HealthAttributeSet"), "Health",
                         "GameplayCue.DamageNumber, GameplayCue.Damage"), "our damage: number and hit flash")
# KILL CREDIT (2026-11-07): splash-only kills do not count for Refreshment / Leeching - neither from the wearer's own
# ability system nor with the weapon hits' Damage.Melee tag (tried, no change, removed). The game's on-kill
# enchantments only see the weapon's own swing.
assets.save_loaded_asset(_hit_fx)

_bp = blueprint(KNOCKBACK, unreal.load_class(None, "/Script/Dungeons.Knockback"))
for _name, _kind in dict(Mobs="array:" + _ACTOR, Healths="array:float", Pending="array:" + _ACTOR,
                         PendingAt="array:struct:/Script/CoreUObject.Vector", Drops="array:float",
                         Hits="int", Seen="int", Bonuses="int", LastHit="float", LastBonus="float", Looks="int",
                         Extra="int", Closer="bool").items():   # the second row: the debug readout's counters
    check(LIB.add_variable(_bp, _name, _kind), "variable " + _name)
LIB.compile(_bp)
_g = Graph(_bp)


def _health_of(actor):
    node = _g.call(_GAS, "GetFloatAttribute")
    _g.link(actor[0], actor[1], node, "Actor")
    check(LIB.set_attribute_pin(_bp, _g.name, node, "Attribute",
                                unreal.load_class(None, "/Script/Dungeons.HealthAttributeSet"), "Health"), "Health attribute")
    return node, "ReturnValue"


def _loop_over(array, after):
    """A ForLoop over array (node, pin) from the exec (node, pin) after. Returns (loop, item (node, pin), index)."""
    last = _g.array_call("Array_LastIndex", array, "TargetArray")
    loop = _g.macro("ForLoop", FirstIndex=0)
    _g.link(last, "ReturnValue", loop, "LastIndex")
    _g.flow(after, loop)
    return loop, _g.item_at(array, (loop, "Index")), (loop, "Index")


# Struck(mob): from our hit cue - remember the mob and where it was
_g.row(0)
_struck = _g.custom_event("Struck", "Mob=" + _ACTOR)
_known = _g.array_call("Array_Find", _v("Pending"), "TargetArray", ItemToFind=(_struck, "Mob"))
_is_new = _g.branch(_math("Less_IntInt", (_known, "ReturnValue"), 0))
_where = _g.call("/Script/Engine.Actor", "K2_GetActorLocation")
_g.link(_struck, "Mob", _where, "self")
_add_mob = _g.array_call("Array_Add", _v("Pending"), "TargetArray", NewItem=(_struck, "Mob"))
_add_at = _g.array_call("Array_Add", _v("PendingAt"), "TargetArray", NewItem=(_where, "ReturnValue"))
_g.flow(_nearest_gate((_struck, "Mob"), (_struck, "then")), _is_new)
_g.flow((_is_new, "then"), _add_mob, _add_at)

# every SPLASH_LOOK seconds on the host
_g.row(300)
_g.flow(_g.event(_COMPONENT, "ReceiveBeginPlay"),
        _g.call("/Script/Engine.KismetSystemLibrary", "K2_SetTimer", FunctionName="Look", Time=SPLASH_LOOK,
                bLooping="true"))
_look_event = _g.custom_event("Look")
_WEARER = (_g.call(_COMPONENT, "GetOwner"), "ReturnValue")
_authority = _g.call("/Script/Engine.Actor", "HasAuthority")
_g.link(_WEARER[0], _WEARER[1], _authority, "self")
_host = _g.branch((_authority, "ReturnValue"))
_g.flow(_look_event, _host)

# 1. the drops of the mobs struck since the last look
_g.row(600)
_looked = set_value(_g, "Looks", _math("Add_IntInt", _v("Looks"), 1))
_g.flow((_host, "then"), _looked)
_loop1, _mob1, _ = _loop_over(_v("Pending"), (_looked, "then"))
_at = _g.array_call("Array_Find", _v("Mobs"), "TargetArray", ItemToFind=_mob1)
_seen = _g.branch(_math("GreaterEqual_IntInt", (_at, "ReturnValue"), 0))
_before = _g.item_at(_v("Healths"), (_at, "ReturnValue"))
_drop = _math("FMax", _math("Subtract_FloatFloat", _before, _health_of(_mob1)), 0.0)
_add_drop = _g.array_call("Array_Add", _v("Drops"), "TargetArray", NewItem=_drop)
_add_none = _g.array_call("Array_Add", _v("Drops"), "TargetArray")
_g.set(_add_none, NewItem=0.0)
_g.flow((_loop1, "LoopBody"), _seen)
_g.flow((_seen, "then"), _add_drop, set_value(_g, "Hits", _math("Add_IntInt", _v("Hits"), 1)), set_value(_g, "LastHit", _drop))
_g.flow((_seen, "else"), _add_none)

# 2. the splashes
_g.row(900)
_loop2, _drop2, _i2 = _loop_over(_v("Drops"), (_loop1, "Completed"))
_center = _g.item_at(_v("PendingAt"), _i2)
_hit_mob = _g.item_at(_v("Pending"), _i2)
_tier = _g.call(_MATH, "Clamp", Min=1, Max=3)
_g.link(_g.var("Level"), "Level", _tier, "Value")
_tier_f = _g.call(_MATH, "Conv_IntToFloat")
_g.link(_tier, "ReturnValue", _tier_f, "InInt")
_share = _math("Add_FloatFloat", SPLASH_BASE, _math("Multiply_FloatFloat", (_tier_f, "ReturnValue"), SPLASH_PER_TIER))
_amount = _math("Multiply_FloatFloat", _drop2, _share)
_worth = _g.branch(_math("Greater_FloatFloat", _amount, 0.0))
_g.flow((_loop2, "LoopBody"), _worth)
_mobs = _g.call("/Script/Engine.GameplayStatics", "GetAllActorsOfClass", ActorClass="/Script/Dungeons.MobCharacter")
_g.flow((_worth, "then"), _mobs)
_loop3, _other, _ = _loop_over((_mobs, "OutActors"), (_mobs, "then"))
_as_char = _g.cast(_BASE, _other)
_me = _g.cast(_BASE, _WEARER)
_friendly = _g.call(_BASE, "IsFriendlyTowards")
_g.link(_me[0], _me[1], _friendly, "self")
_g.link(_as_char[0], _as_char[1], _friendly, "Target")
_hostile = _g.call(_MATH, "Not_PreBool")
_g.link(_friendly, "ReturnValue", _hostile, "A")
# not a mob the swing hit itself (user, 2026-11-07: the struck mobs splashed each other - a mob in a group of five
# took its hit + 4 splashes; Anchor-style: the splash only reaches the mobs around that the weapon missed). The struck
# mobs of this look are the ones a swing hits together (looks every 0.1 s)
_struck_too = _g.array_call("Array_Find", _v("Pending"), "TargetArray", ItemToFind=_other)
_not_hit = _g.call(_MATH, "Less_IntInt", B=0)
_g.link(_struck_too, "ReturnValue", _not_hit, "A")
_other_at = _g.call("/Script/Engine.Actor", "K2_GetActorLocation")
_g.link(_other[0], _other[1], _other_at, "self")
_gap = _g.call(_MATH, "Vector_Distance")
_g.link(_other_at, "ReturnValue", _gap, "V1")
_g.link(_center[0], _center[1], _gap, "V2")
# and alive (user, 2026-11-07: dying mobs still took the splash and flinched)
_living = _math("Greater_FloatFloat", _health_of(_other), 0.0)
_in_reach = _g.branch(_math("BooleanAND", _math("BooleanAND", _math("BooleanAND", (_hostile, "ReturnValue"),
                                                                   (_not_hit, "ReturnValue")), _living),
                            _math("LessEqual_FloatFloat", (_gap, "ReturnValue"), SPLASH_RADIUS)))
_asc = _g.call(_GAS, "GetAbilitySystemComponent")
_g.link(_WEARER[0], _WEARER[1], _asc, "Actor")
_ctx = _g.call(_ASC, "MakeEffectContext")
_g.link(_asc, "ReturnValue", _ctx, "self")
_spec = _g.call(_ASC, "MakeOutgoingSpec", GameplayEffectClass=SPLASH_EFFECT + ".GE_SequelSplash_C", Level=1.0)
_g.link(_asc, "ReturnValue", _spec, "self")
_g.link(_ctx, "ReturnValue", _spec, "Context")
_sized = _g.call(_GAS, "AssignSetByCallerMagnitude", DataName="Damage")
_g.link(_spec, "ReturnValue", _sized, "SpecHandle")
_g.link(*(_math("Multiply_FloatFloat", _amount, -1.0) + (_sized, "Magnitude")))
_victim = _g.call(_GAS, "GetAbilitySystemComponent")
_g.link(_other[0], _other[1], _victim, "Actor")
_strike = _g.call(_ASC, "BP_ApplyGameplayEffectSpecToTarget")
_g.link(_asc, "ReturnValue", _strike, "self")
_g.link(_sized, "ReturnValue", _strike, "SpecHandle")
_g.link(_victim, "ReturnValue", _strike, "Target")
_g.flow((_loop3, "LoopBody"), _as_char[0], _me[0], _in_reach)
_g.flow((_in_reach, "then"), *([n for n in (_spec, _sized) if "execute" in _g.pins(n)] + [_strike]
                                + [set_value(_g, "Bonuses", _math("Add_IntInt", _v("Bonuses"), 1)),
                                   set_value(_g, "LastBonus", _amount)]))

# 3. forget the struck mobs, note everyone's health again
_g.row(1300)
_clear = [_g.array_call("Array_Clear", _v(n), "TargetArray") for n in ("Pending", "PendingAt", "Drops", "Mobs", "Healths")]
_g.flow((_loop2, "Completed"), *_clear)
_all = _g.call("/Script/Engine.GameplayStatics", "GetAllActorsOfClass", ActorClass="/Script/Dungeons.MobCharacter")
_g.flow((_clear[-1], "then"), _all)
_loop4, _mob4, _ = _loop_over((_all, "OutActors"), (_all, "then"))
_near = _g.call("/Script/Engine.Actor", "GetDistanceTo")
_g.link(_WEARER[0], _WEARER[1], _near, "self")
_g.link(_mob4[0], _mob4[1], _near, "OtherActor")
_watched = _g.branch(_math("LessEqual_FloatFloat", (_near, "ReturnValue"), SPLASH_WATCHED))
_note_mob = _g.array_call("Array_Add", _v("Mobs"), "TargetArray", NewItem=_mob4)
_note_health = _g.array_call("Array_Add", _v("Healths"), "TargetArray", NewItem=_health_of(_mob4))
_g.flow((_loop4, "LoopBody"), _watched)
_g.flow((_watched, "then"), _note_mob, _note_health)
compile_save(_bp, "Sweeping Edge (Knockback)")

_cdo = unreal.get_default_object(assets.load_blueprint_class(KNOCKBACK))   # after the last compile, so it stays
_cdo.set_editor_property("knockbackPower", 0.0)                             # Knockback's own push off
check(_cdo.get_editor_property("knockbackPower") == 0.0, "Knockback's push off")
assets.save_loaded_asset(_bp)


def _tier():
    """clamp(Level, 1, 3) (node, pin)."""
    node = _g.call(_MATH, "Clamp", Min=1, Max=3)
    _g.link(_g.var("Level"), "Level", node, "Value")
    return node, "ReturnValue"


def _by_tier(classes):
    """classes[tier - 1] (three effect class paths) as a gameplay effect class: (cast node - put it in the exec
    flow before the use -, its class pin)."""
    tier = _tier()
    two = _g.call(_MATH, "SelectClass", A=classes[1], B=classes[0])
    _g.link(*(_math("EqualEqual_IntInt", tier, 2) + (two, "bSelectA")))
    three = _g.call(_MATH, "SelectClass", A=classes[2])
    _g.link(two, "ReturnValue", three, "B")
    _g.link(*(_math("EqualEqual_IntInt", tier, 3) + (three, "bSelectA")))
    return _g.cast("/Script/GameplayAbilities.GameplayEffect", (three, "ReturnValue"), cls_cast=True)


def timed_spec(effect_class, seconds):
    """The wearer's ability system (node, pin) and a spec (node, pin) of effect_class lasting seconds (node, pin) -
    the set-by-caller "Duration" our timed effects read (LIB.set_effect_duration). Returns (asc, spec, exec nodes)."""
    asc = _g.call(_GAS, "GetAbilitySystemComponent")
    _g.link(_g.call(_COMPONENT, "GetOwner"), "ReturnValue", asc, "Actor")
    context = _g.call(_ASC, "MakeEffectContext")
    _g.link(asc, "ReturnValue", context, "self")
    if isinstance(effect_class, tuple):   # a class picked in the graph, e.g. by tier (_by_tier)
        spec = _g.call(_ASC, "MakeOutgoingSpec", Level=1.0)
        _g.link(effect_class[0], effect_class[1], spec, "GameplayEffectClass")
    else:
        spec = _g.call(_ASC, "MakeOutgoingSpec", GameplayEffectClass=effect_class, Level=1.0)
    _g.link(asc, "ReturnValue", spec, "self")
    _g.link(context, "ReturnValue", spec, "Context")
    duration = _g.call(_GAS, "AssignSetByCallerMagnitude", DataName="Duration")
    _g.link(spec, "ReturnValue", duration, "SpecHandle")
    _g.link(seconds[0], seconds[1], duration, "Magnitude")
    steps = [n for n in (spec, duration) if "execute" in _g.pins(n)]
    return (asc, "ReturnValue"), (duration, "ReturnValue"), steps


def timed_effect(path, what, modifiers, buff=None):
    """Our own effect at path: modifiers [(attribute set, attribute, op, magnitude)], lasting a set-by-caller time,
    one copy per character (a new one refreshes the time); buff = (shown name, game icon widget) for the left of the
    screen. Returns its class path."""
    effect = blueprint(path, unreal.GameplayEffect)
    compile_save(effect, what + " effect")
    for attribute_set, attribute, op, magnitude in modifiers:
        check(LIB.add_effect_modifier(effect, unreal.load_class(None, attribute_set), attribute, op, magnitude),
              "%s: %s op %d %s" % (what, attribute, op, magnitude))
    check(LIB.set_effect_duration(effect, "Duration"), what + ": lasts a set time, one copy")
    if buff:
        check(LIB.set_effect_ui_data(effect, unreal.load_class(None, "/Script/Dungeons.DungeonsGameplayEffectUIData"),
                                     unreal.Text(buff[0]), buff_icon(buff[1])), what + ": buff " + " / ".join(buff))
    assets.save_loaded_asset(effect)
    return path + "." + path.rsplit("/", 1)[1] + "_C"


def tier_seconds(base, per_tier):
    """base + per_tier x clamp(Level, 1, 3), as a float (node, pin)."""
    tier = _g.call(_MATH, "Clamp", Min=1, Max=3)
    _g.link(_g.var("Level"), "Level", tier, "Value")
    tier_f = _g.call(_MATH, "Conv_IntToFloat")
    _g.link(tier, "ReturnValue", tier_f, "InInt")
    return _math("Add_FloatFloat", base, _math("Multiply_FloatFloat", (tier_f, "ReturnValue"), per_tier))


_ITEM_SET, _HEALTH_SET = "/Script/Dungeons.ItemAttributeSet", "/Script/Dungeons.HealthAttributeSet"
_MULTIPLY, _DIVIDE = 1, 2   # divisions multiply together, so stacked damage / cooldown cuts never pass zero


# --- Food Reserves -> Barrier Brew ----------------------------------------------------------------------------------
# Drinking a healing potion gives you and every player within BREW_RADIUS 70% less damage taken for 2 / 4 / 6 s
# (Dungeons II's Barrier Brew: Fortifying, 70%, 2 / 4 / 6 s; user, 2026-11-06 - weaker than Potion Barrier is fine
# as it reaches the team). Our own effect GE_SequelBarrierBrew divides TakeDamageMultiplier by 1 / 0.3 (divisions
# multiply, so with Potion Barrier or Protection it only gets better, never past zero); one copy per player, a new
# drink refreshes it. Drinks are seen as Ancient Alchemy sees them (the potion watch, so every Bottomless Brew drink
# counts too). Food Reserves' food is off: its food count is its per-tier value, 0 in Formulas.toml. No item has it
# built in. Its card's tier line would read that 0, so it is fixed text and the numbers are in the description.
# 2026-11-08 (user): 30 / 50 / 70% less damage taken for 6 s at every tier (was 70% for 2 / 4 / 6 s), on Explorer now
# (its card shows Formulas.toml Explorer = 0.3 / 0.5 / 0.7 as "30.0%" etc.; its heal is off, BlockThreshold).
BREW_SECONDS = 6.0
BREW_CUT = (0.3, 0.5, 0.7)
BREW_RADIUS = 1000.0   # 10 m
_barriers = [timed_effect("/Game/Components/Enchantments/Explorer/GE_SequelBarrierBrew%d" % _n, "Barrier Brew %d" % _n, [
    (_HEALTH_SET, "TakeDamageMultiplier", _DIVIDE, 1 / (1 - _c))],
    ("Barrier Brew", "/Game/Components/Enchantments/Explorer/T_Explorer_Icon")) for _n, _c in enumerate(BREW_CUT, 1)]

_bp = blueprint(EXPLORER, unreal.load_class(None, "/Script/Dungeons.Explorer"))
_g, _casts, _cooling, _unused_tier, _ready = potion_watch(_bp, {}, [])
_g.row(900)
_started = _g.branch((_g.var("Started"), "Started"))
_g.flow(_ready, _started)
_g.flow((_started, "else"), note_cooling(_g, _cooling), set_value(_g, "Started", "true"))
_g.row(1200)
_drunk = _g.branch(just_started(_g, _cooling))
_which = _by_tier(_barriers)
_asc, _spec, _steps = timed_spec(_which, _math("Add_FloatFloat", BREW_SECONDS, 0.0))
_steps = [_which[0]] + _steps
_players = _g.call("/Script/Engine.GameplayStatics", "GetAllActorsOfClass",
                   ActorClass="/Script/Dungeons.PlayerCharacter")
_last = _g.array_call("Array_LastIndex", (_players, "OutActors"), "TargetArray")
_loop = _g.macro("ForLoop", FirstIndex=0)
_g.link(_last, "ReturnValue", _loop, "LastIndex")
_player = _g.item_at((_players, "OutActors"), (_loop, "Index"))
_distance = _g.call("/Script/Engine.Actor", "GetDistanceTo")
_g.link(_g.call(_COMPONENT, "GetOwner"), "ReturnValue", _distance, "self")
_g.link(_player[0], _player[1], _distance, "OtherActor")
_near = _g.branch(_math("LessEqual_FloatFloat", (_distance, "ReturnValue"), BREW_RADIUS))
_their_asc = _g.call(_GAS, "GetAbilitySystemComponent")
_g.link(_player[0], _player[1], _their_asc, "Actor")
_give = _g.call(_ASC, "BP_ApplyGameplayEffectSpecToTarget")
_g.link(_asc[0], _asc[1], _give, "self")
_g.link(_spec[0], _spec[1], _give, "SpecHandle")
_g.link(_their_asc, "ReturnValue", _give, "Target")
_remember = note_cooling(_g, _cooling)
_g.flow((_started, "then"), _drunk)
_g.flow(*([(_drunk, "then")] + _steps + [_players, _loop]))
_g.flow((_loop, "LoopBody"), _near)
_g.flow((_near, "then"), _give)
_g.flow((_loop, "Completed"), _remember)
_g.flow((_drunk, "else"), _remember)
compile_save(_bp, "Barrier Brew (Explorer)")
_cdo = unreal.get_default_object(assets.load_blueprint_class(EXPLORER))   # after the last compile, so it stays
_cdo.set_editor_property("BlockThreshold", EXPLORER_OFF)                   # Explorer's heal off
check(_cdo.get_editor_property("BlockThreshold") == EXPLORER_OFF, "Explorer's heal off")
assets.save_loaded_asset(_bp)


# --- four unique-only armor enchantments taken over (user, 2026-11-06) ---------------------------------------------
# Heals Allies -> Radiant Guard, Barrier -> Battle Hardened, Shielding -> Last Stand, Regeneration -> Buddy Brew (swapped
# 2026-11-09, user: the icons fit better that way round).
# Each is our own BP_<Name> at the game's path (the game's AssetRegistry lists /Game/Components/Enchantments/<Name>/
# BP_<Name>), on the native class so the card keeps its texts; the native effect is switched off by its settings
# (CDO, after the last compile). Cards: settings/build/SequelText.toml; Heals Allies' and Barrier's tier lines show our
# numbers through Formulas.toml (formula_patch KNOWN).
ALTRUISTIC = "/Game/Components/Enchantments/Altruistic/BP_Altruistic"
BARRIER = "/Game/Components/Enchantments/Barrier/BP_Barrier"
REGENERATION = "/Game/Components/Enchantments/Regeneration/BP_Regeneration"
SHIELDING = "/Game/Components/Enchantments/Shielding/BP_Shielding"
_DAMAGE_SET = "/Script/Dungeons.DamageAttributeSet"
_ADD = 0
_BASE = "/Script/Dungeons.BaseCharacter"


def _by_tier_and_copy(grid, own_class):
    """grid[this component's place among the owner's own_class components (0..COPY_SLOTS-1)][tier - 1] as a gameplay
    effect class: (cast node - in the exec flow before the use -, its class pin)."""
    copies = _g.call(_AC, "GetComponentsByClass", ComponentClass=own_class)
    _g.link(_g.call(_COMPONENT, "GetOwner"), "ReturnValue", copies, "self")
    place = _g.array_call("Array_Find", (copies, "ReturnValue"), "TargetArray", ItemToFind=_g.self_node())
    slot = _g.call(_MATH, "Clamp", Min=0, Max=len(grid) - 1)
    _g.link(place, "ReturnValue", slot, "Value")
    tier = _tier()
    flat = _math("Add_IntInt", _math("Multiply_IntInt", (slot, "ReturnValue"), 3), _math("Subtract_IntInt", tier, 1))
    classes = [c for row in grid for c in row]
    current = None
    for k, c in enumerate(classes):
        pick = _g.call(_MATH, "SelectClass", A=c)
        if current is None:
            _g.set(pick, B=c)
        else:
            _g.link(current[0], current[1], pick, "B")
        _g.link(*(_math("EqualEqual_IntInt", flat, k) + (pick, "bSelectA")))
        current = (pick, "ReturnValue")
    return _g.cast("/Script/GameplayAbilities.GameplayEffect", current, cls_cast=True)


def _same_team(me, other):
    """me's and other's (cast BaseCharacter (node, pin)s) TeamName equal (node, pin). Players and pets are Heroes;
    IsFriendlyTowards also counts camp animals (they got Buddy Brew's buff and heal, user 2026-11-07)."""
    mine = _g.var("TeamName", owner=_BASE, target=me)
    theirs = _g.var("TeamName", owner=_BASE, target=other)
    same = _g.node("/Script/BlueprintGraph.K2Node_EnumEquality")
    _g.link(mine, "TeamName", same, "A")
    _g.link(theirs, "TeamName", same, "B")
    return same, "ReturnValue"


def _is_player(actor):
    """actor (node, pin) is a hero (node, pin). Heals Allies and Regeneration are rolled by enchanted mobs too: our
    versions are for players only (user, 2026-11-07 - a mob had Radiant Guard)."""
    cls = _g.call("/Script/Engine.GameplayStatics", "GetObjectClass")
    _g.link(actor[0], actor[1], cls, "Object")
    test = _g.call(_MATH, "ClassIsChildOf", ParentClass="/Script/Dungeons.PlayerCharacter")
    _g.link(cls, "ReturnValue", test, "TestClass")
    return test, "ReturnValue"

def _attribute(actor, attribute_set, name):
    """actor's (node, pin) gameplay attribute as a float (node, pin)."""
    node = _g.call(_GAS, "GetFloatAttribute")
    _g.link(actor[0], actor[1], node, "Actor")
    check(LIB.set_attribute_pin(_bp, _g.name, node, "Attribute", unreal.load_class(None, attribute_set), name),
          name + " attribute")
    return node, "ReturnValue"


def _on_host_every(seconds, event_name):
    """BeginPlay starts event_name every seconds; returns the custom event's host branch exec (node, pin)."""
    _g.row(0)
    _g.flow(_g.event(_COMPONENT, "ReceiveBeginPlay"),
            _g.call("/Script/Engine.KismetSystemLibrary", "K2_SetTimer", FunctionName=event_name, Time=seconds,
                    bLooping="true"))
    _g.row(300)
    event = _g.custom_event(event_name)
    authority = _g.call("/Script/Engine.Actor", "HasAuthority")
    _g.link(_g.call(_COMPONENT, "GetOwner"), "ReturnValue", authority, "self")
    host = _g.branch((authority, "ReturnValue"))
    _g.flow(event, host)
    return host, "then"


def _effect_class(path):
    return path + "." + path.rsplit("/", 1)[1] + "_C"


def _switch_off(path, values, what):
    cdo = unreal.get_default_object(assets.load_blueprint_class(path))   # after the last compile, so it stays
    for prop, value in values.items():
        current = cdo.get_editor_property(prop)
        if isinstance(current, int) and not isinstance(current, bool):
            value = int(value)   # a count (the toml numbers are read as floats)
        cdo.set_editor_property(prop, value)
        check(abs(cdo.get_editor_property(prop) - value) < 1e-6, what + ": " + prop + " = " + str(value))
    assets.save_loaded_asset(assets.load_asset(path))


def permanent_effect(path, what, modifiers, buff=None):
    """Our own lasting effect (until removed) - like timed_effect without the duration."""
    effect = blueprint(path, unreal.GameplayEffect)
    compile_save(effect, what + " effect")
    for attribute_set, attribute, op, magnitude in modifiers:
        check(LIB.add_effect_modifier(effect, unreal.load_class(None, attribute_set), attribute, op, magnitude),
              "%s: %s op %d %s" % (what, attribute, op, magnitude))
    if buff:
        check(LIB.set_effect_ui_data(effect, unreal.load_class(None, "/Script/Dungeons.DungeonsGameplayEffectUIData"),
                                     unreal.Text(buff[0]), buff_icon(buff[1])), what + ": buff " + " / ".join(buff))
    assets.save_loaded_asset(effect)
    return _effect_class(path)


# Heals Allies was Radiant Guard (2026-11-06 / 07; user: it's bad, replace it) - Venom Siphon now (further down).
# Its instant heal stays: Buddy Brew and Venom Siphon heal with it.
_heal = blueprint("/Game/Components/Enchantments/Altruistic/GE_SequelRadiantHeal", unreal.GameplayEffect)
compile_save(_heal, "Radiant Guard heal effect")
check(LIB.make_instant_set_by_caller_effect(_heal, unreal.load_class(None, _HEALTH_SET), "Health", _ADD, "Heal"),
      "Radiant Guard heal: Health + set-by-caller Heal, instant")
assets.save_loaded_asset(_heal)
_HEAL = _effect_class("/Game/Components/Enchantments/Altruistic/GE_SequelRadiantHeal")


# Barrier -> Battle Hardened (user, 2026-11-08: on hits, so it works on bosses, and with Radiance): each melee hit of
# the wearer on a hostile mob adds a stack of 2% damage resistance (TakeDamageMultiplier - 0.02 per stack, added
# before the other multipliers) lasting HARDENED_SECONDS (a new stack refreshes them all); 5 / 8 / 10 stacks at most
# (one effect per tier, its stack limit). With Radiance's heals it makes a tank against high-health mobs (the user's
# synergy - no heal bonus, user 2026-11-08). Barrier's own resistance is off (AffectionRadius 0: it sees no enemies).
# 2026-11-08 (user): always HARDENED_STACKS stacks; the tier sets each stack's share (3 / 4 / 5%), and every copy worn
# adds its own share per stack - each copy (its place among the wearer's copies, up to COPY_SLOTS) has its own effect,
# so copies of one tier don't share a stack count.
HARDENED_PER_STACK, HARDENED_SECONDS, HARDENED_STACKS = (0.01, 0.02, 0.03), 3.0, 10   # 10 / 20 / 30% per full copy (whole numbers on the card)
COPY_SLOTS = 3


def stacking_effects(folder, name, modifiers_of_tier, buff, limit):
    """grid[copy][tier - 1]: our timed effects (one per copy place and tier), stack limit limit each; modifiers_of_tier
    (tier) -> modifiers. Returns the class paths."""
    grid = []
    for copy in range(COPY_SLOTS):
        row = []
        for tier in (1, 2, 3):
            path = "%s/GE_Sequel%s%d%s" % (folder, name.replace(" ", ""), tier, "" if copy == 0 else "_" + str(copy + 1))
            cls = timed_effect(path, "%s %d (copy %d)" % (name, tier, copy + 1), modifiers_of_tier(tier), buff)
            effect = assets.load_asset(path)
            check(LIB.set_default_property(effect, "StackLimitCount", str(limit)), "%s %d: %d stacks" % (name, tier, limit))
            assets.save_loaded_asset(effect)
            row.append(cls)
        grid.append(row)
    return grid


# Each stack subtracts its share from the damage taken, so copies add in a straight line (user, 2026-11-08: 5% per
# stack made two tier III copies immune; now 30% per full tier III copy - three copies, the most one can carry, 90%).
_hardened = stacking_effects("/Game/Components/Enchantments/Barrier", "Battle Hardened",
                             lambda t: [(_HEALTH_SET, "TakeDamageMultiplier", _ADD, -HARDENED_PER_STACK[t - 1])],
                             ("Battle Hardened", "/Game/Components/Enchantments/Barrier/T_Barrier_Icon"), HARDENED_STACKS)

# Battle Hardened's graph: further down, before the hit spark (it is told of hits; user, 2026-11-08).

# Shielding -> Last Stand (Regeneration until 2026-11-09): every WATCH_SECONDS on the host, while the wearer is below LAST_STAND_BELOW of max health
# (and alive) our effect of the tier is on - 20 / 40 / 60% less damage taken (TakeDamageMultiplier divided, so with
# Protection / Barrier Brew it only gets better, never past zero) - and off again above it. Shielding's own aura is
# off (ShieldMultiplier 1 = no cut, ShieldRadius 0).
LAST_STAND_BELOW, LAST_STAND_CUT = 0.5, (0.2, 0.4, 0.6)
_stands = [permanent_effect("/Game/Components/Enchantments/Regeneration/GE_SequelLastStand%d" % _n, "Last Stand %d" % _n,
                            [(_HEALTH_SET, "TakeDamageMultiplier", _DIVIDE, 1 / (1 - _cut))], ("Last Stand", "/Game/Components/Enchantments/Shielding/T_Shielding_Icon"))
           for _n, _cut in enumerate(LAST_STAND_CUT, 1)]
_bp = blueprint(SHIELDING, unreal.load_class(None, "/Script/Dungeons.Shielding"))
for _name, _kind in dict(Active="bool", Handle="struct:/Script/GameplayAbilities.ActiveGameplayEffectHandle").items():
    check(LIB.add_variable(_bp, _name, _kind), "variable " + _name)
LIB.compile(_bp)
_g = Graph(_bp)
_host = _on_host_every(WATCH_SECONDS, "Watch")
_WEARER = (_g.call(_COMPONENT, "GetOwner"), "ReturnValue")
_health = _attribute(_WEARER, _HEALTH_SET, "Health")
_low = _math("BooleanAND", _math("Less_FloatFloat", _health,
                                  _math("Multiply_FloatFloat", _attribute(_WEARER, _HEALTH_SET, "MaxHealth"), LAST_STAND_BELOW)),
             _math("Greater_FloatFloat", _health, 0.0))
_is_low = _g.branch(_math("BooleanAND", _low, _is_player(_WEARER)))
_g.flow(_host, _is_low)
_g.row(600)
_not_on = _g.call(_MATH, "Not_PreBool")
_g.link(_g.var("Active"), "Active", _not_on, "A")
_needs_on = _g.branch((_not_on, "ReturnValue"))
_asc = _g.call(_GAS, "GetAbilitySystemComponent")
_g.link(_WEARER[0], _WEARER[1], _asc, "Actor")
_context = _g.call(_ASC, "MakeEffectContext")
_g.link(_asc, "ReturnValue", _context, "self")
_on = _g.call(_ASC, "BP_ApplyGameplayEffectToSelf", Level=1.0)
_g.link(_asc, "ReturnValue", _on, "self")
_pick = _by_tier(_stands)
_g.link(_pick[0], _pick[1], _on, "GameplayEffectClass")
_g.link(_context, "ReturnValue", _on, "EffectContext")
_g.flow((_is_low, "then"), _needs_on)
_g.flow((_needs_on, "then"), _pick[0], _on, set_value(_g, "Handle", (_on, "ReturnValue")), set_value(_g, "Active", "true"))
_g.row(900)
_needs_off = _g.branch(_v("Active"))
_off = _g.call(_ASC, "RemoveActiveGameplayEffect", StacksToRemove=-1)
_g.link(_asc, "ReturnValue", _off, "self")
_g.link(_g.var("Handle"), "Handle", _off, "Handle")
_g.flow((_is_low, "else"), _needs_off)
_g.flow((_needs_off, "then"), _off, set_value(_g, "Active", "false"))
_g.row(1200)
_end = _g.event(_COMPONENT, "ReceiveEndPlay")
_was_on = _g.branch(_v("Active"))
_off_end = _g.call(_ASC, "RemoveActiveGameplayEffect", StacksToRemove=-1)
_g.link(_asc, "ReturnValue", _off_end, "self")
_g.link(_g.var("Handle"), "Handle", _off_end, "Handle")
_g.flow(_end, _was_on)
_g.flow((_was_on, "then"), _off_end, set_value(_g, "Active", "false"))
compile_save(_bp, "Last Stand (Shielding)")
_switch_off(SHIELDING, {"ShieldMultiplier": 1.0, "ShieldRadius": 0.0}, "Shielding's own aura off")

# --- Gravity Pulse -> Artifact Amplifier ----------------------------------------------------------------------------
# Permanent while worn (user, 2026-11-08: a buff after an artifact use was pointless - the first use already gets
# it; no cooldown part): artifact damage and souls gathered x1.2 / 1.35 / 1.5. One effect per
# tier (no buff icon - it never ends); every WATCH_SECONDS on the host it is put on if it isn't yet, and taken off
# when the enchantment goes (unequipped). Players only. Gravity Pulse's pull is off by data (radius 0, every
# 9999 s - proven 2026-11-04). Its card's tier line is a fixed 100 / 150 / 200% in the game's code, so the numbers
# are in the description. No item has it built in (Hungry Horror's became Chilling, 2026-11-04).
AMPLIFY_DAMAGE, AMPLIFY_SOULS = (1.2, 1.35, 1.5), (1.2, 1.35, 1.5)   # the same for both, one card line (user, 2026-11-08)
_amplified = [permanent_effect("/Game/Components/Enchantments/GravityPulse/GE_SequelAmplifier%d" % _n,
                               "Artifact Amplifier %d" % _n,
                               [(_ITEM_SET, "ItemDamageMultiplier", _MULTIPLY, _dmg),
                                (_ITEM_SET, "SoulGatheringMultiplier", _MULTIPLY, _souls)])
              for _n, (_dmg, _souls) in enumerate(zip(AMPLIFY_DAMAGE, AMPLIFY_SOULS), 1)]
_bp = blueprint(GRAVITY_PULSE, unreal.load_class(None, "/Script/Dungeons.GravityPulse"))
for _name, _kind in dict(Active="bool", Handle="struct:/Script/GameplayAbilities.ActiveGameplayEffectHandle").items():
    check(LIB.add_variable(_bp, _name, _kind), "Artifact Amplifier: variable " + _name)
LIB.compile(_bp)
_g = Graph(_bp)
_host = _on_host_every(WATCH_SECONDS, "Watch")
_WEARER = (_g.call(_COMPONENT, "GetOwner"), "ReturnValue")
_not_on = _g.call(_MATH, "Not_PreBool")
_g.link(_g.var("Active"), "Active", _not_on, "A")
_needs_on = _g.branch(_math("BooleanAND", (_not_on, "ReturnValue"), _is_player(_WEARER)))
_g.flow(_host, _needs_on)
_g.row(600)
_asc = _g.call(_GAS, "GetAbilitySystemComponent")
_g.link(_WEARER[0], _WEARER[1], _asc, "Actor")
_context = _g.call(_ASC, "MakeEffectContext")
_g.link(_asc, "ReturnValue", _context, "self")
_on = _g.call(_ASC, "BP_ApplyGameplayEffectToSelf", Level=1.0)
_g.link(_asc, "ReturnValue", _on, "self")
_pick = _by_tier(_amplified)
_g.link(_pick[0], _pick[1], _on, "GameplayEffectClass")
_g.link(_context, "ReturnValue", _on, "EffectContext")
_g.flow((_needs_on, "then"), _pick[0], _on, set_value(_g, "Handle", (_on, "ReturnValue")), set_value(_g, "Active", "true"))
_g.row(1200)
_end = _g.event(_COMPONENT, "ReceiveEndPlay")
_was_on = _g.branch(_v("Active"))
_off_end = _g.call(_ASC, "RemoveActiveGameplayEffect", StacksToRemove=-1)
_g.link(_asc, "ReturnValue", _off_end, "self")
_g.link(_g.var("Handle"), "Handle", _off_end, "Handle")
_g.flow(_end, _was_on)
_g.flow((_was_on, "then"), _off_end, set_value(_g, "Active", "false"))
compile_save(_bp, "Artifact Amplifier (Gravity Pulse)")
_switch_off(GRAVITY_PULSE, {"BaseRadius": 0.0, "PulseInterval": 9999.0}, "Gravity Pulse's pull off")


# Regeneration -> Buddy Brew (Shielding until 2026-11-09; Dungeons II's name: Barrier Brew's twin with Regenerating; its numbers aren't published,
# ours - user, 2026-11-07): drinking a healing potion (seen as Barrier Brew sees it, so every Bottomless Brew drink
# counts) starts Regenerating for 2 / 4 / 6 s: every BUDDY_EVERY seconds on the host, the wearer and every character
# on the wearer's team (other players, pets) within BUDDY_RADIUS heal BUDDY_SHARE of their max health, never past
# full (GE_SequelRadiantHeal, Radiant Guard's instant heal). It follows the wearer; a new drink restarts the time.
# Those near at the drink get the buff icon (GE_SequelBuddyBrew: no modifiers, Buddy Brew's card icon).
# Regeneration's own heal is off for players (below). (Pack Leader, built here first the
# same day, was dropped: Beast Boss / Burst / Surge already cover pets, user 2026-11-06.)
BUDDY_RADIUS, BUDDY_SHARE, BUDDY_EVERY = 1000.0, 0.05, 1.0   # 5%/s (user, 2026-11-09; was 3%)
BUDDY_SECONDS_BASE, BUDDY_SECONDS_PER_TIER = 0.0, 2.0   # 2 / 4 / 6 s (user, 2026-11-09; was 3 / 5 / 7)
for _old in ["/Game/Components/Enchantments/Shielding/GE_SequelPackLeader%d" % _n for _n in (1, 2, 3)]:
    remove(_old)
_buddy = timed_effect("/Game/Components/Enchantments/Shielding/GE_SequelBuddyBrew", "Buddy Brew", [],
                      ("Buddy Brew", "/Game/Components/Enchantments/Regeneration/T_Regeneration_Icon"))


def _for_buddies(after, radius):
    """From the exec (node, pin) after: a loop over every character within radius of the wearer that is the wearer or
    friendly to it. Returns (the loop body's exec for one of them (node, pin), that character (node, pin), the loop
    node - its "Completed" goes on)."""
    wearer = (_g.call(_COMPONENT, "GetOwner"), "ReturnValue")
    found = _g.call("/Script/Engine.GameplayStatics", "GetAllActorsOfClass", ActorClass=_BASE)
    last = _g.array_call("Array_LastIndex", (found, "OutActors"), "TargetArray")
    loop = _g.macro("ForLoop", FirstIndex=0)
    _g.link(last, "ReturnValue", loop, "LastIndex")
    one = _g.item_at((found, "OutActors"), (loop, "Index"))
    as_char = _g.cast(_BASE, one)
    me = _g.cast(_BASE, wearer)
    friend = _same_team(me, as_char)
    is_me = _g.call(_MATH, "EqualEqual_ObjectObject")
    _g.link(one[0], one[1], is_me, "A")
    _g.link(wearer[0], wearer[1], is_me, "B")
    distance = _g.call("/Script/Engine.Actor", "GetDistanceTo")
    _g.link(wearer[0], wearer[1], distance, "self")
    _g.link(one[0], one[1], distance, "OtherActor")
    ok = _g.branch(_math("BooleanAND", _math("BooleanOR", friend, (is_me, "ReturnValue")),
                         _math("LessEqual_FloatFloat", (distance, "ReturnValue"), radius)))
    _g.flow(after, found, loop)
    _g.flow((loop, "LoopBody"), as_char[0], me[0], ok)
    return (ok, "then"), one, loop


_bp = blueprint(REGENERATION, unreal.load_class(None, "/Script/Dungeons.Regeneration"))
_g, _casts, _cooling, _unused_tier, _ready = potion_watch(_bp, dict(RegenUntil="float"), [])
check(LIB.set_variable_default(_bp, "RegenUntil", "-1.0"), "RegenUntil default")
_g.row(900)
_started = _g.branch(_v("Started"))
_g.flow(_ready, _started)
_ticks = _g.call("/Script/Engine.KismetSystemLibrary", "K2_SetTimer", FunctionName="Regen", Time=BUDDY_EVERY,
                 bLooping="true")
_g.flow((_started, "else"), note_cooling(_g, _cooling), set_value(_g, "Started", "true"), _ticks)

# a drink: Regenerating until now + 3 / 5 / 7 s, and the buff for those near
_g.row(1200)
_drunk = _g.branch(just_started(_g, _cooling))
_g.flow((_started, "then"), _drunk)
_seconds = tier_seconds(BUDDY_SECONDS_BASE, BUDDY_SECONDS_PER_TIER)
_now = _g.call("/Script/Engine.GameplayStatics", "GetTimeSeconds")
_until = set_value(_g, "RegenUntil", _math("Add_FloatFloat", (_now, "ReturnValue"), _seconds))
_asc, _spec, _steps = timed_spec(_buddy, _seconds)
_g.flow(*([(_drunk, "then")] + _steps + [_until]))
_body, _one, _loop = _for_buddies((_until, "then"), BUDDY_RADIUS)
_their = _g.call(_GAS, "GetAbilitySystemComponent")
_g.link(_one[0], _one[1], _their, "Actor")
_give = _g.call(_ASC, "BP_ApplyGameplayEffectSpecToTarget")
_g.link(_asc[0], _asc[1], _give, "self")
_g.link(_spec[0], _spec[1], _give, "SpecHandle")
_g.link(_their, "ReturnValue", _give, "Target")
_g.flow(_body, _give)
_remember = note_cooling(_g, _cooling)
_g.flow((_loop, "Completed"), _remember)
_g.flow((_drunk, "else"), _remember)

# Regenerating: every BUDDY_EVERY seconds while it lasts
_g.row(1600)
_regen = _g.custom_event("Regen")
_authority = _g.call("/Script/Engine.Actor", "HasAuthority")
_g.link(_g.call(_COMPONENT, "GetOwner"), "ReturnValue", _authority, "self")
_now = _g.call("/Script/Engine.GameplayStatics", "GetTimeSeconds")
_on = _g.branch(_math("BooleanAND", (_authority, "ReturnValue"),
                      _math("Less_FloatFloat", (_now, "ReturnValue"), _v("RegenUntil"))))
_g.flow(_regen, _on)
_body, _one, _loop = _for_buddies((_on, "then"), BUDDY_RADIUS)
_max = _attribute(_one, _HEALTH_SET, "MaxHealth")
_health = _attribute(_one, _HEALTH_SET, "Health")
_amount = _math("FMin", _math("Multiply_FloatFloat", _max, BUDDY_SHARE), _math("Subtract_FloatFloat", _max, _health))
_hurt_one = _g.branch(_math("Greater_FloatFloat", _amount, 0.0))
_wearer_asc = _g.call(_GAS, "GetAbilitySystemComponent")
_g.link(_g.call(_COMPONENT, "GetOwner"), "ReturnValue", _wearer_asc, "Actor")
_context = _g.call(_ASC, "MakeEffectContext")
_g.link(_wearer_asc, "ReturnValue", _context, "self")
_heal_spec = _g.call(_ASC, "MakeOutgoingSpec", GameplayEffectClass=_HEAL, Level=1.0)
_g.link(_wearer_asc, "ReturnValue", _heal_spec, "self")
_g.link(_context, "ReturnValue", _heal_spec, "Context")
_sized = _g.call(_GAS, "AssignSetByCallerMagnitude", DataName="Heal")
_g.link(_heal_spec, "ReturnValue", _sized, "SpecHandle")
_g.link(_amount[0], _amount[1], _sized, "Magnitude")
_their = _g.call(_GAS, "GetAbilitySystemComponent")
_g.link(_one[0], _one[1], _their, "Actor")
_heal_them = _g.call(_ASC, "BP_ApplyGameplayEffectSpecToTarget")
_g.link(_wearer_asc, "ReturnValue", _heal_them, "self")
_g.link(_sized, "ReturnValue", _heal_them, "SpecHandle")
_g.link(_their, "ReturnValue", _heal_them, "Target")
_g.flow(_body, _hurt_one)
_g.flow((_hurt_one, "then"), *([n for n in (_heal_spec, _sized) if "execute" in _g.pins(n)] + [_heal_them]))
compile_save(_bp, "Buddy Brew (Regeneration)")
# Regeneration's own heal off for players (0 per second, after 10^9 s unhurt); a mob's copy keeps its own
# Mob... numbers (MobPool.toml: mobs still roll Regeneration)
_switch_off(REGENERATION, {"RegenerationAmountPerSecond": 0.0, "TimeUntilRegeneration": 1.0e9}, "Regeneration's own heal off")

# --- the debuffer enchantments: statuses that pay off (user, 2026-11-07) -----------------------------------------
#   Lucky Explorer -> Ignite        hits on a burning mob: + IGNITE share of its max health (bosses BOSS_SHARE of it),
#                                   at most once every BONUS_GAP s per mob; mobs within SPREAD_RADIUS of it catch fire
#                                   for SPREAD_SECONDS (our GE_SequelIgniteBurn: the game's burning marker and flames)
#   Heals Allies -> Venom Siphon    hits on a poisoned mob: + DRAIN share of its max health (same limits); the wearer
#                                   heals DRAIN_HEAL of that extra damage
#   Charging Acceleration -> Shatter  every hit on a chilled / frozen mob deals SHATTER more (x2 / x2.5 / x3)
# The hits come as for Sweeping Edge: our melee hit spark (further down) calls Struck(mob) on the wearer's enchantment,
# which measures the mob's health drop at its next look (measuring_host). A status is the game's own marker on the mob
# (an active gameplay cue tag, ASC IsGameplayCueActive - the game adds active cue tags to the mob's tags).
# The status watcher (BP_SequelStatusWatcher, one per mission, spawned by these enchantments and by the hit spark):
# every STATUS_EVERY s, for every player wearing a fire enchantment (Fire Aspect, Burning, Fire Trail, Ignite) each
# burning hostile mob within STATUS_RANGE loses STATUS share of its max health (best tier worn; bosses BOSS_SHARE of
# it), from the player (kill credit) - whatever set it on fire; the same for poison (Poison Cloud, Poison, Dipping
# Poison, Venom Siphon). A mob is hurt once per look, by the first player that qualifies.
# Numbers: settings/build/Debuffs.toml (via _settings.json).
import json as _json
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "_settings.json")) as _f:
    _DEBUFFS = _json.load(_f).get("debuffs", {})


def _num(key, default):
    return float(_DEBUFFS.get(key, default))

def _toml_numbers(prefix):
    """{field: value} of settings/build/SequelMod.toml's "prefix.field" = number lines."""
    import re
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "settings", "build", "SequelMod.toml")
    found = {}
    for line in open(path):
        m = re.match(r'\s*"%s\.(\w+)"\s*=\s*([-0-9.]+)' % re.escape(prefix), line)
        if m:
            found[m.group(1)] = float(m.group(2))
    return found


IGNITE = (_num("ignite_base", 0.02), _num("ignite_per_tier", 0.01))          # 3 / 4 / 5% of max health
DRAIN = (_num("drain_base", 0.02), _num("drain_per_tier", 0.01))             # 3 / 4 / 5%
DRAIN_HEAL = _num("drain_heal", 0.1)
SHATTER = (_num("shatter_base", 0.5), _num("shatter_per_tier", 0.5))         # +100 / 150 / 200% = x2 / 2.5 / 3
STATUS = (_num("status_base", 0.025), _num("status_per_tier", 0.025))        # poison: 5 / 7.5 / 10% per second
FIRE_STATUS = (_num("fire_base", 0.02), _num("fire_per_tier", 0.01))       # fire: 3 / 4 / 5% per second (user, 2026-11-09:
                                                                           # the game's own fire stacks, poison doesn't)
BOSS_SHARE = _num("boss_share", 0.4)
BONUS_GAP = _num("bonus_gap", 0.5)
SPREAD_RADIUS, SPREAD_SECONDS = _num("spread_radius", 300.0), _num("spread_seconds", 3.0)
STATUS_EVERY, STATUS_RANGE = _num("status_every", 1.0), _num("status_range", 2000.0)

BURN_TAGS = ["GameplayCue.StatusEffect.Burning", "GameplayCue.StatusEffect.BurningOilVial",
             "GameplayCue.StatusEffect.BubbleColumnBurning", "GameplayCue.StatusEffect.Enchantment.FireAspect",
             "GameplayCue.StatusEffect.Enchantment.FireTrail", "StatusEffect.Fire.Burning", "StatusEffect.Fire.Lava"]
POISON_TAGS = ["GameplayCue.StatusEffect.Poison", "GameplayCue.StatusEffect.TwistingVinePoison",
               "GameplayCue.StatusEffect.Enchantment.JunglePoison", "GameplayCue.StatusEffect.Enchantment.Poisoned"]
CHILL_TAGS = ["GameplayCue.StatusEffect.Enchantment.Freezing", "GameplayCue.StatusEffect.Enchantment.Chilling",
              "StatusEffect.Immobile.FrozenSolid"]
_D = "/Script/Dungeons."
FIRE_CLASSES = [_D + n for n in ("FireAspect", "Burning", "FireTrail", "EmeraldDivination")]
POISON_CLASSES = [_D + n for n in ("PoisonedMelee", "PoisonedRanged", "JunglePoisonMelee", "JunglePoisonRanged",
                                   "DippingPoison", "Altruistic")]
EMERALD_DIVINATION = "/Game/Content_DLC3/Components/Enchantments/EmeraldDivination/BP_EmeraldDivination"
# 2026-11-08 (user): Shatter moved from Charging Acceleration (no icon the game lists) to Thrive Under Pressure (an
# armor enchantment no item in the mod carries; listed icon; its value routine gives the card's tier numbers). The
# name CHARGING_ACCELERATION stays for the code.
CHARGING_ACCELERATION = "/Game/Components/Enchantments/ThriveUnderPressure/BP_ThriveUnderPressure"
WATCHER = "/Game/Components/Enchantments/Sequel/BP_SequelStatusWatcher"
WATCHER_CLASS = WATCHER + ".BP_SequelStatusWatcher_C"
IGNITE_BURN = "/Game/Components/Enchantments/Sequel/GE_SequelIgniteBurn"
_SPLASH = SPLASH_EFFECT + ".GE_SequelSplash_C"
_GS = "/Script/Engine.GameplayStatics"
_KSL = "/Script/Engine.KismetSystemLibrary"
_AC = "/Script/Engine.Actor"

# TEST readout (Debuffs.toml debug = true; user, 2026-11-07: see what's happening): a few lines at the top left of
# the host's screen - per hit enchantment its looks, hits measured (last drop), status seen, extras dealt (last
# amount), spreads / heals; the watcher's looks, tiers and mobs hurt. Off for a release.
DEBUG = bool(_DEBUFFS.get("debug", False))
DEBUG_VIEW = "/Game/Components/Enchantments/Sequel/WBP_SequelDebug"
DEBUG_VIEW_CLASS = DEBUG_VIEW + ".WBP_SequelDebug_C"
_debug_view = fresh(DEBUG_VIEW, unreal.WidgetBlueprint, unreal.WidgetBlueprintFactory())
widget(_debug_view, "", unreal.CanvasPanel, "Root")
_info = label(_debug_view, "Root", "Info", "", 16, is_variable=True)
_info.set_editor_property("shadow_offset", unreal.Vector2D(1, 1))
_info.set_editor_property("shadow_color_and_opacity", unreal.LinearColor(0, 0, 0, 0.9))
_spot = _info.get_editor_property("slot")
_spot.set_position(unreal.Vector2D(420, 140))
_spot.set_size(unreal.Vector2D(1100, 200))
check(LIB.add_variable(_debug_view, "Lines", "string"), "debug view: variable Lines")
compile_save(_debug_view, "debug readout (empty)")

# the spread fire: the game's burning marker (its flames show) for a set time, no damage of its own (the watcher's)
_burn_class = timed_effect(IGNITE_BURN, "Ignite burn", [])
_burn = assets.load_asset(IGNITE_BURN)
check(LIB.set_default_property(_burn, "GameplayCues",
                               '((GameplayCueTags=(GameplayTags=((TagName="GameplayCue.StatusEffect.Burning")))))'),
      "Ignite burn: the game's burning cue")
assets.save_loaded_asset(_burn)


def _typed_damage(path, what, damage_tag, on_effect=True):
    """Our instant damage (Health + set-by-caller Damage, negative) carrying damage_tag (the game colours the damage
    number by it: fire orange, poison green...) and the game's damage number only - no hit flash or hurt sound (user,
    2026-11-07: the max-health burn played a hurt sound and a white number beside the game's orange burn number).
    Returns its class path."""
    fx = blueprint(path, unreal.GameplayEffect)
    compile_save(fx, what + " effect")
    health = unreal.load_class(None, "/Script/Dungeons.HealthAttributeSet")
    check(LIB.make_instant_set_by_caller_effect(fx, health, "Health", 0, "Damage"), what + ": instant damage")
    check(LIB.add_effect_cue(fx, health, "Health", "GameplayCue.DamageNumber"), what + ": damage number")
    if on_effect:   # off for lightning: the game's Lightning Focus might boost a tagged effect too - ours does it itself
        check(LIB.add_effect_tags(fx, damage_tag), what + ": tagged " + damage_tag)
    assets.save_loaded_asset(fx)
    # The number's colour comes from the cue's TARGET tags (BP_DamageNumberNotifyStatic passes AggregatedTargetTags to
    # AddDamagePop - read in its bytecode, 2026-11-07), so the mob is given damage_tag for a moment just before the
    # damage: a tiny effect of ours that only grants it (_deal applies it first)
    mark = path + "Mark"
    timed_effect(mark, what + " mark", [])
    check(LIB.add_effect_granted_tags(assets.load_asset(mark), damage_tag), what + ": mark grants " + damage_tag)
    assets.save_loaded_asset(assets.load_asset(mark))
    _MARKS[path + "." + path.rsplit("/", 1)[1] + "_C"] = mark + "." + mark.rsplit("/", 1)[1] + "_C"
    return path + "." + path.rsplit("/", 1)[1] + "_C"


_MARKS = {}


FIRE_DAMAGE = _typed_damage("/Game/Components/Enchantments/Sequel/GE_SequelFireDamage", "fire damage", "Damage.Elemental.Fire")
POISON_DAMAGE = _typed_damage("/Game/Components/Enchantments/Sequel/GE_SequelPoisonDamage", "poison damage",
                              "Damage.Elemental.Poison")
CRIT_DAMAGE = _typed_damage("/Game/Components/Enchantments/Sequel/GE_SequelCritDamage", "crit-coloured damage",
                            "Damage.Melee.Critical")   # Shatter's extra: red, like a critical hit


def _pure(node, what):
    check("execute" not in _g.pins(node), what + " is pure")
    return node


def _has_status(actor, tags):
    """actor (node, pin) shows any of tags (node, pin)."""
    asc = _g.call(_GAS, "GetAbilitySystemComponent")
    _g.link(actor[0], actor[1], asc, "Actor")
    result = None
    for tag in tags:
        q = _pure(_g.call(_ASC, "IsGameplayCueActive", GameplayCueTag='(TagName="%s")' % tag), "IsGameplayCueActive")
        _g.link(asc, "ReturnValue", q, "self")
        result = (q, "ReturnValue") if result is None else _math("BooleanOR", result, (q, "ReturnValue"))
    return result


def _boss_factor(actor):
    """BOSS_SHARE for a mob with the big health bar at the top of the screen (bosses), else 1 (node, pin)."""
    bar = _pure(_g.call(_AC, "GetComponentByClass", ComponentClass=_D + "GlobalHealthBarComponent"), "GetComponentByClass")
    _g.link(actor[0], actor[1], bar, "self")
    valid = _g.call(_KSL, "IsValid")
    _g.link(bar, "ReturnValue", valid, "Object")
    pick = _g.call(_MATH, "SelectFloat", A=BOSS_SHARE, B=1.0)
    _g.link(valid, "ReturnValue", pick, "bPickA")
    return pick, "ReturnValue"


def _own_share(base_per):
    """base + per x clamp(Level, 1, 3) (node, pin)."""
    tier = _g.call(_MATH, "Clamp", Min=1, Max=3)
    _g.link(_g.var("Level"), "Level", tier, "Value")
    tier_f = _g.call(_MATH, "Conv_IntToFloat")
    _g.link(tier, "ReturnValue", tier_f, "InInt")
    return _math("Add_FloatFloat", base_per[0], _math("Multiply_FloatFloat", (tier_f, "ReturnValue"), base_per[1]))


def _count(var):
    """var += 1 (a set node)."""
    return set_value(_g, var, _math("Add_IntInt", _v(var), 1))


def _steps(*nodes):
    return [n for n in nodes if "execute" in _g.pins(n)]


def _deal(source, target, amount, effect=None):
    """source (node, pin) hurts target (node, pin) by amount (node, pin) - our instant damage, from source's ability
    system (kill credit). Returns the exec steps."""
    asc = _g.call(_GAS, "GetAbilitySystemComponent")
    _g.link(source[0], source[1], asc, "Actor")
    ctx = _g.call(_ASC, "MakeEffectContext")
    _g.link(asc, "ReturnValue", ctx, "self")
    spec = _g.call(_ASC, "MakeOutgoingSpec", GameplayEffectClass=effect or _SPLASH, Level=1.0)
    _g.link(asc, "ReturnValue", spec, "self")
    _g.link(ctx, "ReturnValue", spec, "Context")
    sized = _g.call(_GAS, "AssignSetByCallerMagnitude", DataName="Damage")
    _g.link(spec, "ReturnValue", sized, "SpecHandle")
    _link_value(_math("Multiply_FloatFloat", amount, -1.0), sized, "Magnitude")
    victim = _g.call(_GAS, "GetAbilitySystemComponent")
    _g.link(target[0], target[1], victim, "Actor")
    strike = _g.call(_ASC, "BP_ApplyGameplayEffectSpecToTarget")
    _g.link(asc, "ReturnValue", strike, "self")
    _g.link(sized, "ReturnValue", strike, "SpecHandle")
    _g.link(victim, "ReturnValue", strike, "Target")
    marks = []
    if effect in _MARKS:   # the damage type on the mob for a moment, for the number's colour
        mspec = _g.call(_ASC, "MakeOutgoingSpec", GameplayEffectClass=_MARKS[effect], Level=1.0)
        _g.link(asc, "ReturnValue", mspec, "self")
        _g.link(ctx, "ReturnValue", mspec, "Context")
        mtime = _g.call(_GAS, "AssignSetByCallerMagnitude", DataName="Duration", Magnitude=0.05)   # short: other hits in that moment would take the colour too
        _g.link(mspec, "ReturnValue", mtime, "SpecHandle")
        mark = _g.call(_ASC, "BP_ApplyGameplayEffectSpecToTarget")
        _g.link(asc, "ReturnValue", mark, "self")
        _g.link(mtime, "ReturnValue", mark, "SpecHandle")
        _g.link(victim, "ReturnValue", mark, "Target")
        marks = _steps(mspec, mtime) + [mark]
    return marks + _steps(spec, sized) + [strike]


def _heal_self(actor, amount):
    """actor (node, pin) heals amount (node, pin), never past full. Returns the exec steps."""
    room = _math("Subtract_FloatFloat", _attribute(actor, _HEALTH_SET, "MaxHealth"), _attribute(actor, _HEALTH_SET, "Health"))
    asc = _g.call(_GAS, "GetAbilitySystemComponent")
    _g.link(actor[0], actor[1], asc, "Actor")
    ctx = _g.call(_ASC, "MakeEffectContext")
    _g.link(asc, "ReturnValue", ctx, "self")
    spec = _g.call(_ASC, "MakeOutgoingSpec", GameplayEffectClass=_HEAL, Level=1.0)
    _g.link(asc, "ReturnValue", spec, "self")
    _g.link(ctx, "ReturnValue", spec, "Context")
    sized = _g.call(_GAS, "AssignSetByCallerMagnitude", DataName="Heal")
    _g.link(spec, "ReturnValue", sized, "SpecHandle")
    _link_value(_math("FMax", _math("FMin", amount, room), 0.0), sized, "Magnitude")
    give = _g.call(_ASC, "BP_ApplyGameplayEffectSpecToSelf")
    _g.link(asc, "ReturnValue", give, "self")
    _g.link(sized, "ReturnValue", give, "SpecHandle")
    return _steps(spec, sized) + [give]


def _link_exec(froms, node):
    for f in froms:
        _g.link(f[0], f[1], node, "execute")


def _gap_check(mob, entry, gap=None):
    """At most once every BONUS_GAP s per mob (GapMobs / GapTimes): from entry (node, pin). Returns (the execs that
    pass - (node, pin)s, the exec that is held back (node, pin))."""
    known = _g.array_call("Array_Find", _v("GapMobs"), "TargetArray", ItemToFind=mob)
    is_known = _g.branch(_math("GreaterEqual_IntInt", (known, "ReturnValue"), 0))
    now = _g.call(_GS, "GetTimeSeconds")
    last = _g.item_at(_v("GapTimes"), (known, "ReturnValue"))
    rested = _g.branch(_math("GreaterEqual_FloatFloat", _math("Subtract_FloatFloat", (now, "ReturnValue"), last), BONUS_GAP if gap is None else gap))
    renew = _g.array_call("Array_Set", _v("GapTimes"), "TargetArray", Index=(known, "ReturnValue"), Item=(now, "ReturnValue"))
    add_mob = _g.array_call("Array_Add", _v("GapMobs"), "TargetArray", NewItem=mob)
    add_time = _g.array_call("Array_Add", _v("GapTimes"), "TargetArray", NewItem=(now, "ReturnValue"))
    _g.flow(entry, is_known)
    _g.flow((is_known, "then"), rested)
    _g.flow((rested, "then"), renew)
    _g.flow((is_known, "else"), add_mob, add_time)
    return [(renew, "then"), (add_time, "then")], (rested, "else")


def _hostile_mobs_near(center, radius, after, skip=None):
    """From the exec (node, pin) after: a loop over every MobCharacter within radius of center (a location (node,
    pin)) that is not on the wearer's team (and not skip (node, pin)). Returns (body exec (node, pin), the mob
    (node, pin), the loop)."""
    wearer = (_g.call(_COMPONENT, "GetOwner"), "ReturnValue")
    found = _g.call(_GS, "GetAllActorsOfClass", ActorClass=_D + "MobCharacter")
    last = _g.array_call("Array_LastIndex", (found, "OutActors"), "TargetArray")
    loop = _g.macro("ForLoop", FirstIndex=0)
    _g.link(last, "ReturnValue", loop, "LastIndex")
    one = _g.item_at((found, "OutActors"), (loop, "Index"))
    as_char = _g.cast(_BASE, one)
    me = _g.cast(_BASE, wearer)
    foe = _g.call(_MATH, "Not_PreBool")
    _g.link(*(_same_team(me, as_char) + (foe, "A")))
    at = _g.call(_AC, "K2_GetActorLocation")
    _g.link(one[0], one[1], at, "self")
    gap = _g.call(_MATH, "Vector_Distance")
    _g.link(at, "ReturnValue", gap, "V1")
    _g.link(center[0], center[1], gap, "V2")
    ok = _math("BooleanAND", (foe, "ReturnValue"), _math("LessEqual_FloatFloat", (gap, "ReturnValue"), radius))
    # alive only (dying mobs took Sweeping Edge's splash and flinched, user 2026-11-07 - the same for Ignite's spread)
    ok = _math("BooleanAND", ok, _math("Greater_FloatFloat", _attribute(one, _HEALTH_SET, "Health"), 0.0))
    if skip:
        other = _g.call(_MATH, "NotEqual_ObjectObject")
        _g.link(one[0], one[1], other, "A")
        _g.link(skip[0], skip[1], other, "B")
        ok = _math("BooleanAND", ok, (other, "ReturnValue"))
    go = _g.branch(ok)
    _g.flow(after, found, loop)
    _g.flow((loop, "LoopBody"), as_char[0], me[0], go)
    return (go, "then"), one, loop


def _ensure_watcher(context, after):
    """From the exec (node, pin) after, on the host: spawn the status watcher if the mission has none. context: an
    actor (node, pin) in the world. Returns (the spawn's last node, the branch - its "else" when there is one)."""
    authority = _g.call(_AC, "HasAuthority")
    _g.link(context[0], context[1], authority, "self")
    there = _g.call(_GS, "GetAllActorsOfClass", ActorClass=WATCHER_CLASS)
    if "WorldContextObject" in _g.pins(there):
        _g.link(context[0], context[1], there, "WorldContextObject")
    count = _g.array_call("Array_Length", (there, "OutActors"), "TargetArray")
    none = _g.branch(_math("BooleanAND", (authority, "ReturnValue"), _math("EqualEqual_IntInt", (count, "ReturnValue"), 0)))
    at = _g.call(_AC, "K2_GetActorLocation")
    _g.link(context[0], context[1], at, "self")
    place = _g.call(_MATH, "MakeTransform")
    _g.link(at, "ReturnValue", place, "Location")
    spawn = _g.call(_GS, "BeginDeferredActorSpawnFromClass", ActorClass=WATCHER_CLASS)
    _g.link(context[0], context[1], spawn, "WorldContextObject")
    _g.link(place, "ReturnValue", spawn, "SpawnTransform")
    finish = _g.call(_GS, "FinishSpawningActor")
    _g.link(spawn, "ReturnValue", finish, "Actor")
    _g.link(place, "ReturnValue", finish, "SpawnTransform")
    _g.flow(after, there, none)
    _g.flow((none, "then"), spawn, finish)
    return finish, none


# the status watcher: an actor of its own, one per mission ------------------------------------------------------
_bp = blueprint(WATCHER, unreal.load_class(None, "/Script/Engine.Actor"))
for _name, _kind in dict(Done="array:" + _ACTOR, FireTier="int", PoisonTier="int", Ticks="int", Hurt="int",
                         LastHurt="float", LastFire="int", LastPoison="int").items():
    check(LIB.add_variable(_bp, _name, _kind), "variable " + _name)
LIB.compile(_bp)
_g = Graph(_bp)
_g.row(0)
_burn_timer = _g.call(_KSL, "K2_SetTimer", FunctionName="Burn", Time=STATUS_EVERY, bLooping="true")
_g.flow(_g.event(_AC, "ReceiveBeginPlay"), _burn_timer)
if DEBUG:
    _make = _g.node("/Script/UMGEditor.K2Node_CreateWidget")
    _g.set(_make, Class=DEBUG_VIEW_CLASS)
    _g.link(_g.call(_GS, "GetPlayerController", PlayerIndex=0), "ReturnValue", _make, "OwningPlayer")
    _up = _g.call("/Script/UMG.UserWidget", "AddToViewport", ZOrder=-1)
    _g.link(_make, "ReturnValue", _up, "self")
    _g.flow((_burn_timer, "then"), _make, _up)
_g.row(300)
_tick = _g.custom_event("Burn")
_authority = _g.call(_AC, "HasAuthority")
_g.link(*(_g.self_node() + (_authority, "self")))
_on_host = _g.branch((_authority, "ReturnValue"))
_clear = _g.array_call("Array_Clear", _v("Done"), "TargetArray")
_players = _g.call(_GS, "GetAllActorsOfClass", ActorClass=_D + "PlayerCharacter")
_g.flow(_tick, _on_host)
_g.flow((_on_host, "then"), _count("Ticks"), _clear, _players)
_loop_p, _player, _ = _loop_over((_players, "OutActors"), (_players, "then"))
# the best fire / poison tier the player wears
_g.row(600)
_zero_f = set_value(_g, "FireTier", 0)
_zero_p = set_value(_g, "PoisonTier", 0)
_worn = _pure(_g.call(_AC, "GetComponentsByClass", ComponentClass=_D + "Enchantment"), "GetComponentsByClass")
_g.link(_player[0], _player[1], _worn, "self")
_g.flow((_loop_p, "LoopBody"), _zero_f, _zero_p)
_loop_e, _ench, _ = _loop_over((_worn, "ReturnValue"), (_zero_p, "then"))
_as_ench = _g.cast(_D + "Enchantment", _ench)
_level = _g.var("Level", owner=_D + "Enchantment", target=_as_ench)
_cls = _g.call(_GS, "GetObjectClass")
_g.link(_ench[0], _ench[1], _cls, "Object")


def _is_one_of(classes):
    result = None
    for c in classes:
        t = _g.call(_MATH, "ClassIsChildOf", ParentClass=c)
        _g.link(_cls, "ReturnValue", t, "TestClass")
        result = (t, "ReturnValue") if result is None else _math("BooleanOR", result, (t, "ReturnValue"))
    return result


def _best(var, classes):
    pick = _g.call(_MATH, "SelectInt", B=0)
    _g.link(_level, "Level", pick, "A")
    _link_value(_is_one_of(classes), pick, "bPickA")
    return set_value(_g, var, _math("Max", _v(var), (pick, "ReturnValue")))


_set_f = _best("FireTier", FIRE_CLASSES)
_set_p = _best("PoisonTier", POISON_CLASSES)
_g.flow((_loop_e, "LoopBody"), _as_ench[0], _set_f, _set_p)
# then the mobs near that player
_g.row(1000)
_wears_any = _g.branch(_math("BooleanOR", _math("Greater_IntInt", _v("FireTier"), 0), _math("Greater_IntInt", _v("PoisonTier"), 0)))
_g.flow((_loop_e, "Completed"), set_value(_g, "LastFire", _v("FireTier")), set_value(_g, "LastPoison", _v("PoisonTier")),
        _wears_any)
_mobs = _g.call(_GS, "GetAllActorsOfClass", ActorClass=_D + "MobCharacter")
_g.flow((_wears_any, "then"), _mobs)
_loop_m, _mob, _ = _loop_over((_mobs, "OutActors"), (_mobs, "then"))
_hero = _g.cast(_BASE, _player)
_foe_char = _g.cast(_BASE, _mob)
_foe = _g.call(_MATH, "Not_PreBool")
_g.link(*(_same_team(_hero, _foe_char) + (_foe, "A")))
_dist = _g.call(_AC, "GetDistanceTo")
_g.link(_player[0], _player[1], _dist, "self")
_g.link(_mob[0], _mob[1], _dist, "OtherActor")
_done_at = _g.array_call("Array_Find", _v("Done"), "TargetArray", ItemToFind=_mob)
_alive = _math("Greater_FloatFloat", _attribute(_mob, _HEALTH_SET, "Health"), 0.0)


def _status_share(tier_var, tags, numbers):
    """numbers' share at tier_var's tier if that tier > 0 and the mob shows one of tags, else 0 (node, pin)."""
    tier = _g.call(_MATH, "Clamp", Min=1, Max=3)
    _link_value(_v(tier_var), tier, "Value")
    tier_f = _g.call(_MATH, "Conv_IntToFloat")
    _g.link(tier, "ReturnValue", tier_f, "InInt")
    share = _math("Add_FloatFloat", numbers[0], _math("Multiply_FloatFloat", (tier_f, "ReturnValue"), numbers[1]))
    pick = _g.call(_MATH, "SelectFloat", B=0.0)
    _link_value(share, pick, "A")
    _link_value(_math("BooleanAND", _math("Greater_IntInt", _v(tier_var), 0), _has_status(_mob, tags)), pick, "bPickA")
    return pick, "ReturnValue"


_fire_share, _poison_share = _status_share("FireTier", BURN_TAGS, FIRE_STATUS), _status_share("PoisonTier", POISON_TAGS, STATUS)
_share = _math("Add_FloatFloat", _fire_share, _poison_share)
_amount = _math("Multiply_FloatFloat", _math("Multiply_FloatFloat", _attribute(_mob, _HEALTH_SET, "MaxHealth"), _share),
                _boss_factor(_mob))
_fire_amount = _math("Multiply_FloatFloat", _math("Multiply_FloatFloat", _attribute(_mob, _HEALTH_SET, "MaxHealth"),
                                                  _fire_share), _boss_factor(_mob))
_poison_amount = _math("Multiply_FloatFloat", _math("Multiply_FloatFloat", _attribute(_mob, _HEALTH_SET, "MaxHealth"),
                                                    _poison_share), _boss_factor(_mob))
_go = _g.branch(_math("BooleanAND", _math("BooleanAND", (_foe, "ReturnValue"),
                                          _math("LessEqual_FloatFloat", (_dist, "ReturnValue"), STATUS_RANGE)),
                      _math("BooleanAND", _math("BooleanAND", _math("Less_IntInt", (_done_at, "ReturnValue"), 0), _alive),
                            _math("Greater_FloatFloat", _amount, 0.0))))
_g.flow((_loop_m, "LoopBody"), _hero[0], _foe_char[0], _go)
_mark = _g.array_call("Array_Add", _v("Done"), "TargetArray", NewItem=_mob)
# the amount noted BEFORE the damage: a mob it kills reads 0 afterwards (the log showed "last amount 0", 2026-11-07)
_noted = set_value(_g, "LastHurt", _amount)
_burns = _g.branch(_math("Greater_FloatFloat", _fire_amount, 0.0))
_g.flow((_go, "then"), _noted, _burns)
_burn_hit = _deal(_player, _mob, _fire_amount, FIRE_DAMAGE)
_g.flow(*([(_burns, "then")] + _burn_hit))
_poisons = _g.branch(_math("Greater_FloatFloat", _poison_amount, 0.0))
_link_exec([(_burns, "else"), (_burn_hit[-1], "then")], _poisons)
_poison_hit = _deal(_player, _mob, _poison_amount, POISON_DAMAGE)
_g.flow(*([(_poisons, "then")] + _poison_hit))
_link_exec([(_poisons, "else"), (_poison_hit[-1], "then")], _mark)
_g.flow(_mark, _count("Hurt"))
compile_save(_bp, "status watcher (fire / poison max-health damage)")


# Arrows (user, 2026-11-08: ranged Refreshment; every damage of the player's should count): every look, the mobs
# within ARROW_MARK of each of the wearer's flying projectiles (owner / instigator the wearer) are marked - an arrow
# moves a few blocks per look, so the reach is wide. The game's projectile base class through a placeholder.
PROJECTILE = "/Game/Actors/Items/Arrow/BP_Projectile"
ARROW_MARK = _num("arrow_mark", 400.0)
compile_save(blueprint(PROJECTILE, unreal.Actor.static_class()), "placeholder for the game's projectile")
placeholder(PROJECTILE)


def _shot_is_mine(shot, wearer):
    """shot's (node, pin) owner, its owner's owner (the bow held by the wearer) or its instigator is wearer (node, pin)
    - (node, pin) bool."""
    owner = _g.call(_AC, "GetOwner")
    _g.link(shot[0], shot[1], owner, "self")
    owners_owner = _g.call(_AC, "GetOwner")
    _g.link(owner, "ReturnValue", owners_owner, "self")
    inst = _g.call(_AC, "GetInstigator")
    _g.link(shot[0], shot[1], inst, "self")
    result = None
    for who in (owner, owners_owner, inst):
        same = _g.call(_MATH, "EqualEqual_ObjectObject")
        _g.link(who, "ReturnValue", same, "A")
        _g.link(wearer[0], wearer[1], same, "B")
        result = (same, "ReturnValue") if result is None else _math("BooleanOR", result, (same, "ReturnValue"))
    return result


ARROW_TOUCH = _num("arrow_touch", 150.0)


# An arrow hit, seen without the game telling (user, 2026-11-08: a look for arrows near mobs caught 1 arrow in 150 -
# arrows fly ~3 blocks per look and are gone the moment they land). Every look the wearer's flying projectiles are
# noted (where, how fast); one that is gone or has stopped since the last look landed: the first hostile mob around
# where it was heading (half a look ahead, within ARROW_TOUCH + half a look's flight) counts as hit by it. Each arrow
# once (Used). Needs variables Tracked / TrackedAt / TrackedVel / Used / Got (ARROW_VARIABLES).
ARROW_VARIABLES = dict(Tracked="array:" + _ACTOR, TrackedAt="array:struct:/Script/CoreUObject.Vector",
                       TrackedVel="array:struct:/Script/CoreUObject.Vector", Used="array:" + _ACTOR, Got="bool")


def _arrow_pass(wearer, after, on_hit):
    """From the exec (node, pin) after: the arrow-hit pass; on_hit(mob (node, pin), exec (node, pin)) adds what a hit
    does."""
    many = _g.array_call("Array_Length", _v("Used"), "TargetArray")
    tidy = _g.branch(_math("Greater_IntInt", (many, "ReturnValue"), 64))
    clear = _g.array_call("Array_Clear", _v("Used"), "TargetArray")
    _g.flow(after, tidy)
    _g.flow((tidy, "then"), clear)
    start = set_value(_g, "Got", "false")
    _link_exec([(tidy, "else"), (clear, "then")], start)
    tloop, arrow, index = _loop_over(_v("Tracked"), (start, "then"))
    valid = _g.call(_KSL, "IsValid")
    _g.link(arrow[0], arrow[1], valid, "Object")
    gone = _g.call(_MATH, "Not_PreBool")
    _g.link(valid, "ReturnValue", gone, "A")
    vel_now = _g.call(_AC, "GetVelocity")
    _g.link(arrow[0], arrow[1], vel_now, "self")
    speed_now = _g.call(_MATH, "VSize")
    _g.link(vel_now, "ReturnValue", speed_now, "A")
    used = _g.array_call("Array_Find", _v("Used"), "TargetArray", ItemToFind=arrow)
    landed = _g.branch(_math("BooleanAND", _math("BooleanOR", (gone, "ReturnValue"),
                                                 _math("Less_FloatFloat", (speed_now, "ReturnValue"), 50.0)),
                             _math("Less_IntInt", (used, "ReturnValue"), 0)))
    _g.flow((tloop, "LoopBody"), landed)
    was_at = _g.item_at(_v("TrackedAt"), index)
    was_vel = _g.item_at(_v("TrackedVel"), index)
    ahead = _g.call(_MATH, "Multiply_VectorFloat", B=SPLASH_LOOK * 0.5)
    _g.link(was_vel[0], was_vel[1], ahead, "A")
    point = _g.call(_MATH, "Add_VectorVector")
    _g.link(was_at[0], was_at[1], point, "A")
    _g.link(ahead, "ReturnValue", point, "B")
    speed_was = _g.call(_MATH, "VSize")
    _g.link(was_vel[0], was_vel[1], speed_was, "A")
    reach = _math("Add_FloatFloat", _math("Multiply_FloatFloat", (speed_was, "ReturnValue"), SPLASH_LOOK * 0.5), ARROW_TOUCH)
    note = _g.array_call("Array_Add", _v("Used"), "TargetArray", NewItem=arrow)
    reset = set_value(_g, "Got", "false")
    _g.flow((landed, "then"), note, reset)
    body, mob, _ = _hostile_mobs_near((point, "ReturnValue"), reach, (reset, "then"))
    not_yet = _g.call(_MATH, "Not_PreBool")
    _g.link(_g.var("Got"), "Got", not_yet, "A")
    first = _g.branch((not_yet, "ReturnValue"))
    got = set_value(_g, "Got", "true")
    _g.flow(body, first)
    _g.flow((first, "then"), got)
    on_hit(mob, (got, "then"))
    # then: note the wearer's arrows in flight now
    clears = [_g.array_call("Array_Clear", _v(n), "TargetArray") for n in ("Tracked", "TrackedAt", "TrackedVel")]
    shots = _g.call(_GS, "GetAllActorsOfClass", ActorClass=_effect_class(PROJECTILE))
    _g.flow(*([(tloop, "Completed")] + clears + [shots]))
    sloop, shot, _ = _loop_over((shots, "OutActors"), (shots, "then"))
    mine = _g.branch(_shot_is_mine(shot, wearer))
    _g.flow((sloop, "LoopBody"), mine)
    shot_at = _g.call(_AC, "K2_GetActorLocation")
    _g.link(shot[0], shot[1], shot_at, "self")
    shot_vel = _g.call(_AC, "GetVelocity")
    _g.link(shot[0], shot[1], shot_vel, "self")
    _g.flow((mine, "then"), _g.array_call("Array_Add", _v("Tracked"), "TargetArray", NewItem=shot),
            _g.array_call("Array_Add", _v("TrackedAt"), "TargetArray", NewItem=(shot_at, "ReturnValue")),
            _g.array_call("Array_Add", _v("TrackedVel"), "TargetArray", NewItem=(shot_vel, "ReturnValue")))
    return sloop, "Completed"



def measuring_host(path, parent, what, extra=None, arrows=False, players_only=False):
    """Our enchantment at path over the native class parent, told Struck(mob) by our melee hit spark; at each look
    (SPLASH_LOOK s, on the host) the drop of every struck mob's health since the last look is that hit's damage.
    Also starts the status watcher. Returns (the look's per-hit body exec (node, pin), the mob, the drop, where the
    mob was, the loop) - the caller adds what a hit does, then compile_save(_bp, what)."""
    global _bp, _g
    _bp = blueprint(path, unreal.load_class(None, parent))
    variables = dict(Mobs="array:" + _ACTOR, Healths="array:float", Pending="array:" + _ACTOR,
                     PendingAt="array:struct:/Script/CoreUObject.Vector", Drops="array:float",
                     GapMobs="array:" + _ACTOR, GapTimes="array:float", Bonus="float",
                     Hits="int", Seen="int", Bonuses="int", LastHit="float", LastBonus="float", Looks="int",
                     Extra="int", Closer="bool")   # the second row: the debug readout's counters
    variables.update(extra or {})
    if arrows:   # the wearer's arrows count as hits too (user, 2026-11-08: Ignite / Venom Siphon / Shatter / Overload)
        variables.update(ARROW_VARIABLES)
    for name, kind in variables.items():
        check(LIB.add_variable(_bp, name, kind), what + ": variable " + name)
    LIB.compile(_bp)
    _g = Graph(_bp)
    _g.row(0)
    struck = _g.custom_event("Struck", "Mob=" + _ACTOR)
    known = _g.array_call("Array_Find", _v("Pending"), "TargetArray", ItemToFind=(struck, "Mob"))
    is_new = _g.branch(_math("Less_IntInt", (known, "ReturnValue"), 0))
    where = _g.call(_AC, "K2_GetActorLocation")
    _g.link(struck, "Mob", where, "self")
    add_mob = _g.array_call("Array_Add", _v("Pending"), "TargetArray", NewItem=(struck, "Mob"))
    add_at = _g.array_call("Array_Add", _v("PendingAt"), "TargetArray", NewItem=(where, "ReturnValue"))
    _g.flow(_nearest_gate((struck, "Mob"), (struck, "then")), is_new)
    _g.flow((is_new, "then"), add_mob, add_at)

    _g.row(300)
    begin = _g.event(_COMPONENT, "ReceiveBeginPlay")
    timer = _g.call(_KSL, "K2_SetTimer", FunctionName="Look", Time=SPLASH_LOOK, bLooping="true")
    wearer = (_g.call(_COMPONENT, "GetOwner"), "ReturnValue")
    _g.flow(begin, timer)
    _ensure_watcher(wearer, (timer, "then"))
    _g.row(600)
    look = _g.custom_event("Look")
    authority = _g.call(_AC, "HasAuthority")
    _g.link(wearer[0], wearer[1], authority, "self")
    if players_only:   # a copy on an enchanted mob does nothing of ours (no look for arrows every 0.1 s)
        host = _g.branch(_math("BooleanAND", (authority, "ReturnValue"), _is_player(wearer)))
    else:
        host = _g.branch((authority, "ReturnValue"))
    looked = set_value(_g, "Looks", _math("Add_IntInt", _v("Looks"), 1))
    _g.flow(look, host)
    _g.flow((host, "then"), looked)
    # forget old per-mob limits now and then (dead mobs)
    many = _g.branch(_math("Greater_IntInt", (_g.array_call("Array_Length", _v("GapMobs"), "TargetArray"), "ReturnValue"), 200))
    forget = [_g.array_call("Array_Clear", _v(n), "TargetArray") for n in ("GapMobs", "GapTimes")]
    _g.flow((looked, "then"), many)
    _g.flow((many, "then"), *forget)

    _g.row(900)
    start = [(forget[-1], "then"), (many, "else")]
    if arrows:
        def _arrow_struck(mob, after):
            """An arrow hit mob: measured with the melee hits of this look."""
            known = _g.array_call("Array_Find", _v("Pending"), "TargetArray", ItemToFind=mob)
            new = _g.branch(_math("Less_IntInt", (known, "ReturnValue"), 0))
            where_now = _g.call(_AC, "K2_GetActorLocation")
            _g.link(mob[0], mob[1], where_now, "self")
            _g.flow(after, new, _g.array_call("Array_Add", _v("Pending"), "TargetArray", NewItem=mob),
                    _g.array_call("Array_Add", _v("PendingAt"), "TargetArray", NewItem=(where_now, "ReturnValue")))
        joined = set_value(_g, "Looks", _v("Looks"))   # a join
        _link_exec(start, joined)
        start = [_arrow_pass(wearer, (joined, "then"), _arrow_struck)]
    loop1, mob1, _ = _loop_over(_v("Pending"), start[0])
    for extra_start in start[1:]:
        _g.link(extra_start[0], extra_start[1], loop1, "execute")
    at = _g.array_call("Array_Find", _v("Mobs"), "TargetArray", ItemToFind=mob1)
    seen = _g.branch(_math("GreaterEqual_IntInt", (at, "ReturnValue"), 0))
    before = _g.item_at(_v("Healths"), (at, "ReturnValue"))
    drop = _math("FMax", _math("Subtract_FloatFloat", before, _attribute(mob1, _HEALTH_SET, "Health")), 0.0)
    add_drop = _g.array_call("Array_Add", _v("Drops"), "TargetArray", NewItem=drop)
    add_none = _g.array_call("Array_Add", _v("Drops"), "TargetArray")
    _g.set(add_none, NewItem=0.0)
    _g.flow((loop1, "LoopBody"), seen)
    _g.flow((seen, "then"), add_drop, _count("Hits"), set_value(_g, "LastHit", drop))
    _g.flow((seen, "else"), add_none)

    _g.row(1200)
    loop2, drop2, i2 = _loop_over(_v("Drops"), (loop1, "Completed"))
    hit_mob = _g.item_at(_v("Pending"), i2)
    hit_at = _g.item_at(_v("PendingAt"), i2)

    _g.row(2400)
    clear = [_g.array_call("Array_Clear", _v(n), "TargetArray") for n in ("Pending", "PendingAt", "Drops", "Mobs", "Healths")]
    _g.flow((loop2, "Completed"), *clear)
    every = _g.call(_GS, "GetAllActorsOfClass", ActorClass=_D + "MobCharacter")
    _g.flow((clear[-1], "then"), every)
    loop4, mob4, _ = _loop_over((every, "OutActors"), (every, "then"))
    near = _g.call(_AC, "GetDistanceTo")
    _g.link(wearer[0], wearer[1], near, "self")
    _g.link(mob4[0], mob4[1], near, "OtherActor")
    watched = _g.branch(_math("LessEqual_FloatFloat", (near, "ReturnValue"), SPLASH_WATCHED))
    note_mob = _g.array_call("Array_Add", _v("Mobs"), "TargetArray", NewItem=mob4)
    note_health = _g.array_call("Array_Add", _v("Healths"), "TargetArray", NewItem=_attribute(mob4, _HEALTH_SET, "Health"))
    _g.flow((loop4, "LoopBody"), watched)
    _g.flow((watched, "then"), note_mob, note_health)
    _g.row(1500)
    measuring_host.after_look = (loop4, "Completed")   # the look's end, for more work every look (Shatter)
    return (loop2, "LoopBody"), hit_mob, drop2, hit_at, wearer


def _triggered():
    return _g.call("/Script/Dungeons.Enchantment", "BroadcastEnchantmentTriggeredEvent", canCombo="false")


# Lucky Explorer -> Ignite ------------------------------------------------------------------------------------------
_body, _mob, _drop, _at, _wearer = measuring_host(EMERALD_DIVINATION, _D + "EmeraldDivination", "Ignite", arrows=True)
_burning = _g.branch(_has_status(_mob, BURN_TAGS))
_g.flow(_body, _burning)
_seen_one = _count("Seen")
_g.flow((_burning, "then"), _seen_one)
_pass, _held = _gap_check(_mob, (_seen_one, "then"))
_g.row(1800)
_bonus = _math("Multiply_FloatFloat", _math("Multiply_FloatFloat", _attribute(_mob, _HEALTH_SET, "MaxHealth"),
                                            _own_share(IGNITE)), _boss_factor(_mob))
_hurt = _deal(_wearer, _mob, _bonus, FIRE_DAMAGE)
_link_exec(_pass, _hurt[0])
_told = _triggered()
_g.flow(*(_hurt + [_count("Bonuses"), set_value(_g, "LastBonus", _bonus), _told]))
_g.row(2100)
_one_body, _one, _spread_loop = _hostile_mobs_near(_at, SPREAD_RADIUS, (_told, "then"), skip=_mob)
_asc, _spec, _spec_steps = timed_spec(_burn_class, _math("Add_FloatFloat", SPREAD_SECONDS, 0.0))
_their = _g.call(_GAS, "GetAbilitySystemComponent")
_g.link(_one[0], _one[1], _their, "Actor")
_catch = _g.call(_ASC, "BP_ApplyGameplayEffectSpecToTarget")
_g.link(_asc[0], _asc[1], _catch, "self")
_g.link(_spec[0], _spec[1], _catch, "SpecHandle")
_g.link(_their, "ReturnValue", _catch, "Target")
_g.flow(*([_one_body] + _spec_steps + [_catch, _count("Extra")]))
compile_save(_bp, "Ignite (Lucky Explorer)")
# its card's tier number = EmeraldToSpawnBase + EmeraldToSpawnPerLevel x (tier - 1) (exe+0x32C83E0, read 2026-11-07):
# Ignite's extra in percent, for the tier line "{0}% of max health as extra damage"
_switch_off(EMERALD_DIVINATION, {"PercentageToSpawn": 0.0,
                                 "EmeraldToSpawnBase": 100 * (IGNITE[0] + IGNITE[1]), "EmeraldToSpawnPerLevel": 100 * IGNITE[1]},
            "Lucky Explorer's emeralds off, its card number = Ignite's extra")

# Heals Allies -> Venom Siphon --------------------------------------------------------------------------------------
_body, _mob, _drop, _at, _wearer = measuring_host(ALTRUISTIC, _D + "Altruistic", "Venom Siphon", arrows=True)
_poisoned = _g.branch(_has_status(_mob, POISON_TAGS))
_no_bonus = set_value(_g, "Bonus", 0.0)
_g.flow(_body, _poisoned, _count("Seen"), _no_bonus)
_pass, _held = _gap_check(_mob, (_no_bonus, "then"))
_g.row(1800)
_amount = _math("Multiply_FloatFloat", _math("Multiply_FloatFloat", _attribute(_mob, _HEALTH_SET, "MaxHealth"),
                                             _own_share(DRAIN)), _boss_factor(_mob))
_keep = set_value(_g, "Bonus", _amount)
_link_exec(_pass, _keep)
_hurt = _deal(_wearer, _mob, _v("Bonus"), POISON_DAMAGE)
_told = _triggered()
_g.flow(*([_keep] + _hurt + [_count("Bonuses"), set_value(_g, "LastBonus", _v("Bonus")), _told]))
_g.row(2100)
_heal = _heal_self(_wearer, _math("Multiply_FloatFloat", _v("Bonus"), DRAIN_HEAL))   # 10% of the extra (user, 2026-11-07)
_link_exec([(_told, "then")], _heal[0])
_g.flow(*(_heal + [_count("Extra")]))
compile_save(_bp, "Venom Siphon (Heals Allies)")
_switch_off(ALTRUISTIC, {"PercentageOfDamageToHeal": 0.0, "AffectionRadius": 0.0}, "Heals Allies' own heal off")

# Charging Acceleration -> Shatter ----------------------------------------------------------------------------------
# Shatter: every one of the wearer's hits on a chilled / frozen mob deals SHATTER more of the hit as an extra hit
# (x2 / x2.5 / x3 in all), shown red like a crit (user, 2026-11-07: only your own direct hits, and only for the
# wearer - so not a "fragile" effect on the mob, which every player's damage would use; tried and dropped the same
# day. One number isn't possible: the game draws a number per damage event).
for _n in (1, 2, 3):
    remove("/Game/Components/Enchantments/Sequel/GE_SequelShatter%d" % _n)
remove("/Game/Components/Enchantments/Sequel/GE_SequelIceDamage")
_body, _mob, _drop, _at, _wearer = measuring_host(CHARGING_ACCELERATION, _D + "ThriveUnderPressure", "Shatter", arrows=True)
_chilled = _g.branch(_math("BooleanAND", _has_status(_mob, CHILL_TAGS), _math("Greater_FloatFloat", _drop, 0.0)))
_g.flow(_body, _chilled)
_g.row(1800)
_extra = _math("Multiply_FloatFloat", _drop, _own_share(SHATTER))
_hurt = _deal(_wearer, _mob, _extra, CRIT_DAMAGE)
_g.flow(*([(_chilled, "then"), _count("Seen")] + _hurt + [_count("Bonuses"), set_value(_g, "LastBonus", _extra), _triggered()]))
compile_save(_bp, "Shatter (Thrive Under Pressure)")
# Thrive Under Pressure's own damage cut never triggers: no range, an unreachable crowd
_switch_off(CHARGING_ACCELERATION, {"TriggerRange": 0.0, "MobThreshold": 9999}, "Thrive Under Pressure's own cut off")

# --- Fire Aspect: arrows set mobs on fire too (user, 2026-11-12) ------------------------------------------------------
# The game's Fire Aspect burns on melee hits only (it rolls on melee weapons only). Ours keeps that - its own burn, the
# game's effect through a placeholder (Effect, the only object default of the game's BP_FireAspect) - and every mob the
# wearer's arrows hit catches fire for its burn time: the game's burning look (Ignite's burn), no damage of its own -
# burning mobs lose the fire share of their max health (the status watcher). So it can roll on bows (EnchantGear
# also_on) and a fire build works from range, Ignite included. Players only; enchanted mobs keep the game's melee burn.
FIRE_ASPECT = "/Game/Components/Enchantments/FireAspect/BP_FireAspect"
FIRE_ASPECT_EFFECT = "/Game/Components/Enchantments/FireAspect/BP_FireAspectGameplayEffect"
compile_save(blueprint(FIRE_ASPECT_EFFECT, unreal.GameplayEffect),
             "placeholder for the game's Fire Aspect burn")
placeholder(FIRE_ASPECT_EFFECT)
_fire_numbers = _toml_numbers("BP_FireAspect")
ARROW_BURN_SECONDS = _fire_numbers.get("fireDuration", 3.0)
_body, _mob, _drop, _at, _wearer = measuring_host(FIRE_ASPECT, _D + "FireAspect", "Fire Aspect", arrows=True,
                                                  players_only=True)
_g.row(1800)
_asc, _spec, _spec_steps = timed_spec(_burn_class, _math("Add_FloatFloat", ARROW_BURN_SECONDS, 0.0))
_their = _g.call(_GAS, "GetAbilitySystemComponent")
_g.link(_mob[0], _mob[1], _their, "Actor")
_catch = _g.call(_ASC, "BP_ApplyGameplayEffectSpecToTarget")
_g.link(_asc[0], _asc[1], _catch, "self")
_g.link(_spec[0], _spec[1], _catch, "SpecHandle")
_g.link(_their, "ReturnValue", _catch, "Target")
_g.flow(*([_body, _count("Seen")] + _spec_steps + [_catch, _count("Bonuses")]))
compile_save(_bp, "Fire Aspect (arrows burn too)")
_cdo = unreal.get_default_object(assets.load_blueprint_class(FIRE_ASPECT))
_cdo.set_editor_property("Effect", assets.load_blueprint_class(FIRE_ASPECT_EFFECT))
check(_cdo.get_editor_property("Effect") is not None, "Fire Aspect: the game's burn effect")
_switch_off(FIRE_ASPECT, _fire_numbers, "Fire Aspect's numbers (SequelMod.toml)")

# --- Kill credit: our Leeching and Refreshment (melee) ---------------------------------------------------------------
# The game's on-kill enchantments only count the weapon swing's own kill (tested 2026-11-07: kills by Sweeping Edge's
# splash - from the wearer, even tagged Damage.Melee - and by Poison Cloud never triggered Refreshment / Leeching).
# User, 2026-11-07: make them work with proc builds. Ours mark mobs as the wearer's: a mob the wearer hits (our hit
# spark's Struck, nearest player only), every mob within KILL_AREA of it then (Shockwave, Swirling, Sweeping Edge,
# lightning land there), and every burning / poisoned mob within KILL_NEAR of the wearer (every KILL_NEAR_EVERY s).
# A marked mob that dies within KILL_WINDOW s of its last mark is the wearer's kill (looked at every SPLASH_LOOK s,
# health 0). The game's own trigger is switched off (its numbers 0); the card numbers come from Formulas.toml.
KILL_WINDOW, KILL_AREA, KILL_NEAR = _num("kill_window", 5.0), _num("kill_area", 500.0), _num("kill_near", 800.0)
KILL_NEAR_EVERY = 0.25
# and every hostile mob within KILL_CLOSE of the wearer (user, 2026-11-08: Thorns kills only counted when the mob had
# been hit - a mob that walks up, hits you and dies to Thorns now counts; so does other damage right around you)
KILL_CLOSE = _num("kill_close", 300.0)
# Artifacts (user, 2026-11-08): using an artifact notes the health of every hostile mob within ARTIFACT_REACH; for
# ARTIFACT_WINDOW s a noted mob that has lost health since is marked as the wearer's (a teammate's hit still takes it -
# Taken, as for every mark other than the wearer's own hit).
ARTIFACT_REACH, ARTIFACT_WINDOW = _num("artifact_reach", 1200.0), _num("artifact_window", 5.0)
LEECH = (_num("leech_base", 0.03), _num("leech_per_tier", 0.01))   # 4 / 5 / 6%
REFRESH = (_num("refresh_base", 1.0), _num("refresh_per_tier", 1.0))
LEECHING = "/Game/Components/Enchantments/Leeching/BP_Leeching"
REFRESHMENT = "/Game/Content_DLC5/Components/Enchantments/PotionThirstMelee/BP_PotionThirstMelee"
_POTION_CD = "/Game/Components/Enchantments/Sequel/GE_SequelPotionCooldown"






def _forget(mob, names, after):
    """From the exec (node, pin) after: take mob (node, pin) out of the paired arrays names (mobs, times). Returns
    the execs that end it."""
    at = _g.array_call("Array_Find", _v(names[0]), "TargetArray", ItemToFind=mob)
    there = _g.branch(_math("GreaterEqual_IntInt", (at, "ReturnValue"), 0))
    # the times first: the index (pure) is found again for each removal, in names[0] - which must still hold the mob
    out = [_g.array_call("Array_Remove", _v(n), "TargetArray", IndexToRemove=(at, "ReturnValue")) for n in reversed(names)]
    _g.flow(after, there)
    _g.flow(*([(there, "then")] + out))
    return [(there, "else"), (out[-1], "then")]


def _note_in(mob, names, after):
    """From the exec (node, pin) after: mob (node, pin) in the paired arrays names (mobs, times) at the time now
    (renewed when there). Returns the execs that end it."""
    known = _g.array_call("Array_Find", _v(names[0]), "TargetArray", ItemToFind=mob)
    is_known = _g.branch(_math("GreaterEqual_IntInt", (known, "ReturnValue"), 0))
    now = _g.call(_GS, "GetTimeSeconds")
    renew = _g.array_call("Array_Set", _v(names[1]), "TargetArray", Index=(known, "ReturnValue"), Item=(now, "ReturnValue"))
    add_mob = _g.array_call("Array_Add", _v(names[0]), "TargetArray", NewItem=mob)
    add_at = _g.array_call("Array_Add", _v(names[1]), "TargetArray", NewItem=(now, "ReturnValue"))
    _g.flow(after, is_known)
    _g.flow((is_known, "then"), renew)
    _g.flow((is_known, "else"), add_mob, add_at)
    return [(renew, "then"), (add_at, "then")]


def _mark(mob, after, own_hit=False):
    """From the exec (node, pin) after: note mob (node, pin) as the wearer's now, unless already counted (Done) or -
    for marks other than the wearer's own hit - a teammate hit it (or a mob next to it) within KILL_WINDOW s (Taken;
    user, 2026-11-07: a teammate's kill must not count for you). The wearer's own hit takes it back. Returns the execs
    that end it."""
    done = _g.array_call("Array_Find", _v("Done"), "TargetArray", ItemToFind=mob)
    fresh = _g.branch(_math("Less_IntInt", (done, "ReturnValue"), 0))
    _g.flow(after, fresh)
    ends = [(fresh, "else")]
    if own_hit:
        go = _forget(mob, ("Taken", "TakenAt"), (fresh, "then"))
    else:
        taken = _g.array_call("Array_Find", _v("Taken"), "TargetArray", ItemToFind=mob)
        is_taken = _g.branch(_math("GreaterEqual_IntInt", (taken, "ReturnValue"), 0))
        now = _g.call(_GS, "GetTimeSeconds")
        since = _math("Subtract_FloatFloat", (now, "ReturnValue"), _g.item_at(_v("TakenAt"), (taken, "ReturnValue")))
        theirs = _g.branch(_math("LessEqual_FloatFloat", since, KILL_WINDOW))
        _g.flow((fresh, "then"), is_taken)
        _g.flow((is_taken, "then"), theirs)
        ends.append((theirs, "then"))
        go = [(is_taken, "else"), (theirs, "else")]
    join = _g.branch((_g.call(_MATH, "Not_PreBool"), "ReturnValue"))   # a join point (NOT false: always "then")
    _link_exec(go, join)
    return ends + _note_in(mob, ("Marked", "MarkedAt"), (join, "then"))


def _take(mob, after):
    """A teammate hit mob (node, pin) (or a mob next to it): not the wearer's any more, and kept from the wearer's
    status / area marks for KILL_WINDOW s. From the exec (node, pin) after."""
    gone = _forget(mob, ("Marked", "MarkedAt"), after)
    join = _g.branch((_g.call(_MATH, "Not_PreBool"), "ReturnValue"))   # a join point (NOT false: always "then")
    _link_exec(gone, join)
    _note_in(mob, ("Taken", "TakenAt"), (join, "then"))


def kill_credit_host(path, parent, what, extra=None, defaults=None):
    """Our enchantment at path over the native class parent, counting the wearer's kills as above. Returns (the exec
    (node, pin) reached once per kill, the killed mob (node, pin), the wearer (node, pin)) - the caller adds what a
    kill does, then compile_save(_bp, what)."""
    global _bp, _g
    _bp = blueprint(path, unreal.load_class(None, parent))
    for name, kind in dict(Marked="array:" + _ACTOR, MarkedAt="array:float", Keep="array:" + _ACTOR,
                           KeepAt="array:float", Done="array:" + _ACTOR, Taken="array:" + _ACTOR,
                           TakenAt="array:float", Closer="bool", Looks="int", Hits="int",
                           Kills="int", LastBonus="float", Extra="int", ArtMobs="array:" + _ACTOR,
                           ArtHealths="array:float", ArtUntil="float", ArtUses="int", **(extra or {})).items():
        check(LIB.add_variable(_bp, name, kind), what + ": variable " + name)
    for name, value in (defaults or {}).items():
        check(LIB.set_variable_default(_bp, name, value), what + ": " + name + " default")
    LIB.compile(_bp)
    _g = Graph(_bp)
    wearer = (_g.call(_COMPONENT, "GetOwner"), "ReturnValue")
    # Struck(mob): the hit mob, and the mobs around it
    _g.row(0)
    struck = _g.custom_event("Struck", "Mob=" + _ACTOR)
    counted = _count("Hits")
    mine = _nearest_gate((struck, "Mob"), (struck, "then"))
    _g.flow(mine, counted)
    # the mobs around it first, then the mob itself (each mark has several ends; a loop has one)
    where = _g.call(_AC, "K2_GetActorLocation")
    _g.link(struck, "Mob", where, "self")
    body, one, area = _hostile_mobs_near((where, "ReturnValue"), KILL_AREA, (counted, "then"), skip=(struck, "Mob"))
    _mark(one, body)
    _mark((struck, "Mob"), (area, "Completed"), own_hit=True)
    # a teammate was closer: their hit - the mob and the mobs around it are theirs for now
    _g.row(150)
    tbody, tone, tarea = _hostile_mobs_near((where, "ReturnValue"), KILL_AREA, (mine[0], "else"), skip=(struck, "Mob"))
    _take(tone, tbody)
    _take((struck, "Mob"), (tarea, "Completed"))
    # BeginPlay: the looks
    _g.row(300)
    _g.flow(_g.event(_COMPONENT, "ReceiveBeginPlay"),
            _g.call(_KSL, "K2_SetTimer", FunctionName="Look", Time=SPLASH_LOOK, bLooping="true"),
            _g.call(_KSL, "K2_SetTimer", FunctionName="Near", Time=KILL_NEAR_EVERY, bLooping="true"),
            _g.call(_KSL, "K2_SetTimer", FunctionName="Listen", Time=1.0, bLooping="true"))
    # Listen (every second; binding twice keeps one): each artifact slot's "used" event -> Used
    _g.row(1500)
    listen = _g.custom_event("Listen")
    lauth = _g.call(_AC, "HasAuthority")
    _g.link(wearer[0], wearer[1], lauth, "self")
    lhost = _g.branch((lauth, "ReturnValue"))
    found = _g.call(_AC, "GetComponentByClass", ComponentClass="/Script/Dungeons.EquipmentComponent")
    _g.link(wearer[0], wearer[1], found, "self")
    equipment = _g.cast("/Script/Dungeons.EquipmentComponent", (found, "ReturnValue"))
    slots = _g.call("/Script/Dungeons.EquipmentComponent", "GetSlotsOfType", Type="ActivePermanent")
    _g.link(equipment[0], equipment[1], slots, "self")
    _g.flow(listen, lhost)
    _g.flow((lhost, "then"), equipment[0])
    sloop, slot, _ = _loop_over((slots, "ReturnValue"), (equipment[0], "then"))
    bind = _g.node("/Script/BlueprintGraph.K2Node_AddDelegate")
    check(LIB.set_node_property(_bp, _g.name, bind, "DelegateReference",
                                "(MemberParent=Class'/Script/Dungeons.ItemSlot',MemberName=\"OnItemSlotActivationCompleted\")"),
          what + ": artifact used delegate")
    _g.link(slot[0], slot[1], bind, "self")
    _g.flow((sloop, "LoopBody"), bind)
    _g.row(1800)
    used = _g.custom_event("Used", "slot=object:/Script/Dungeons.ItemSlot;success=bool")
    _g.link(used, "OutputDelegate", bind, "Delegate")
    uauth = _g.call(_AC, "HasAuthority")
    _g.link(wearer[0], wearer[1], uauth, "self")
    did = _g.branch(_math("BooleanAND", (used, "success"), (uauth, "ReturnValue")))
    unow = _g.call(_GS, "GetTimeSeconds")
    until = set_value(_g, "ArtUntil", _math("Add_FloatFloat", (unow, "ReturnValue"), ARTIFACT_WINDOW))
    uclear = [_g.array_call("Array_Clear", _v(n), "TargetArray") for n in ("ArtMobs", "ArtHealths")]
    _g.flow(used, did)
    _g.flow(*([(did, "then"), until, _count("ArtUses")] + uclear))
    uat = _g.call(_AC, "K2_GetActorLocation")
    _g.link(wearer[0], wearer[1], uat, "self")
    ubody, umob, _ = _hostile_mobs_near((uat, "ReturnValue"), ARTIFACT_REACH, (uclear[-1], "then"))
    _g.flow(ubody, _g.array_call("Array_Add", _v("ArtMobs"), "TargetArray", NewItem=umob),
            _g.array_call("Array_Add", _v("ArtHealths"), "TargetArray", NewItem=_attribute(umob, _HEALTH_SET, "Health")))
    # Near: burning / poisoned mobs around the wearer
    _g.row(600)
    near = _g.custom_event("Near")
    authority = _g.call(_AC, "HasAuthority")
    _g.link(wearer[0], wearer[1], authority, "self")
    host = _g.branch((authority, "ReturnValue"))
    _g.flow(near, host)
    mine_at = _g.call(_AC, "K2_GetActorLocation")
    _g.link(wearer[0], wearer[1], mine_at, "self")
    nbody, nmob, nloop = _hostile_mobs_near((mine_at, "ReturnValue"), KILL_NEAR, (host, "then"))
    close = _g.call(_AC, "GetDistanceTo")
    _g.link(wearer[0], wearer[1], close, "self")
    _g.link(nmob[0], nmob[1], close, "OtherActor")
    sick = _g.branch(_math("BooleanOR", _has_status(nmob, BURN_TAGS + POISON_TAGS),
                           _math("LessEqual_FloatFloat", (close, "ReturnValue"), KILL_CLOSE)))
    _g.flow(nbody, sick)
    _mark(nmob, (sick, "then"))
    # after an artifact: the noted mobs that lost health since
    _g.row(750)
    anow = _g.call(_GS, "GetTimeSeconds")
    in_time = _g.branch(_math("LessEqual_FloatFloat", (anow, "ReturnValue"), _v("ArtUntil")))
    _g.flow((nloop, "Completed"), in_time)
    aloop2, amob2, aidx = _loop_over(_v("ArtMobs"), (in_time, "then"))
    avalid = _g.call(_KSL, "IsValid")
    _g.link(amob2[0], amob2[1], avalid, "Object")
    hurt = _g.branch(_math("BooleanAND", (avalid, "ReturnValue"),
                           _math("Less_FloatFloat", _attribute(amob2, _HEALTH_SET, "Health"),
                                 _math("Subtract_FloatFloat", _g.item_at(_v("ArtHealths"), aidx), 0.5))))
    _g.flow((aloop2, "LoopBody"), hurt)
    _mark(amob2, (hurt, "then"))
    # Look: kills and old marks
    _g.row(900)
    look = _g.custom_event("Look")
    authority2 = _g.call(_AC, "HasAuthority")
    _g.link(wearer[0], wearer[1], authority2, "self")
    host2 = _g.branch((authority2, "ReturnValue"))
    clear = [_g.array_call("Array_Clear", _v(n), "TargetArray") for n in ("Keep", "KeepAt")]
    _g.flow(look, host2)
    _g.flow((host2, "then"), _count("Looks"), *clear)
    # the wearer's arrows in flight: the mobs around each
    shots = _g.call(_GS, "GetAllActorsOfClass", ActorClass=_effect_class(PROJECTILE))
    _g.flow((clear[-1], "then"), shots)
    aloop, arrow, _ = _loop_over((shots, "OutActors"), (shots, "then"))
    shot_mine = _g.branch(_shot_is_mine(arrow, wearer))
    arrow_at = _g.call(_AC, "K2_GetActorLocation")
    _g.link(arrow[0], arrow[1], arrow_at, "self")
    _g.flow((aloop, "LoopBody"), shot_mine)
    abody, amob, _ = _hostile_mobs_near((arrow_at, "ReturnValue"), ARROW_MARK, (shot_mine, "then"))
    _mark(amob, abody)
    loop, mob, index = _loop_over(_v("Marked"), (aloop, "Completed"))
    marked_at = _g.item_at(_v("MarkedAt"), index)
    valid = _g.call(_KSL, "IsValid")
    _g.link(mob[0], mob[1], valid, "Object")
    there = _g.branch((valid, "ReturnValue"))
    dead = _g.branch(_math("LessEqual_FloatFloat", _attribute(mob, _HEALTH_SET, "Health"), 0.0))
    now = _g.call(_GS, "GetTimeSeconds")
    recent = _g.branch(_math("LessEqual_FloatFloat", _math("Subtract_FloatFloat", (now, "ReturnValue"), marked_at),
                             KILL_WINDOW))
    keep = _g.array_call("Array_Add", _v("Keep"), "TargetArray", NewItem=mob)
    keep_at = _g.array_call("Array_Add", _v("KeepAt"), "TargetArray", NewItem=marked_at)
    add_done = _g.array_call("Array_Add", _v("Done"), "TargetArray", NewItem=mob)
    _g.flow((loop, "LoopBody"), there)
    _g.flow((there, "then"), dead)
    _g.flow((dead, "else"), recent)
    _g.flow((recent, "then"), keep, keep_at)
    killed = _count("Kills")
    _g.flow((dead, "then"), add_done, killed)
    # after the loop: the kept marks replace the old; forget the counted ones now and then
    _g.row(1500)
    swap = [set_value(_g, "Marked", _v("Keep")), set_value(_g, "MarkedAt", _v("KeepAt"))]
    many = _g.branch(_math("Greater_IntInt", (_g.array_call("Array_Length", _v("Done"), "TargetArray"), "ReturnValue"), 200))
    _g.flow((loop, "Completed"), *(swap + [many]))
    _g.flow((many, "then"), *[_g.array_call("Array_Clear", _v(n), "TargetArray") for n in ("Done", "Taken", "TakenAt")])
    _g.row(1800)
    return (killed, "then"), mob, wearer


# Leeching: a kill heals the wearer LEECH of the killed mob's max health (4 / 5 / 6%; user, 2026-11-08)
_kill, _dead, _wearer = kill_credit_host(LEECHING, _D + "Leeching", "Leeching")
_keep = set_value(_g, "LastBonus", _math("Multiply_FloatFloat", _attribute(_dead, _HEALTH_SET, "MaxHealth"),
                                          _own_share((LEECH[0] - LEECH[1], LEECH[1]))))
_g.flow(*([_kill, _keep] + _heal_self(_wearer, _v("LastBonus")) + [_count("Extra"), _triggered()]))
compile_save(_bp, "Leeching (kill credit)")
_switch_off(LEECHING, {"HealPerLevelFactor": 0.0, "BaseHealFactor": 0.0}, "Leeching's own heal off")

# Refreshment (melee): a kill cuts REFRESH s off the health potion's cooldown (1 / 2 / 3 s, the game's numbers).
# Blueprints can't shorten a running effect, so the game's cooldown effect is removed and ours (granting the same
# cooldown tag, which the potion slot and Bottomless Brew go by) put on for the time that is left. Refreshment on
# ranged weapons stays the game's own (arrow kills: our hit spark is melee only).
timed_effect(_POTION_CD, "Refreshment's potion cooldown", [])
check(LIB.add_effect_granted_tags(assets.load_asset(_POTION_CD), POTION_COOLDOWN_TAG),
      "Refreshment's potion cooldown grants " + POTION_COOLDOWN_TAG)
assets.save_loaded_asset(assets.load_asset(_POTION_CD))
# ranged Refreshment the same way, its own numbers (3 / 6 / 9 s, SequelMod.toml's): arrow kills count through the
# arrow marks above (user, 2026-11-08)
REFRESHMENT_RANGED = "/Game/Content_DLC5/Components/Enchantments/PotionThirstRanged/BP_PotionThirstRanged"
REFRESH_RANGED = (_num("refresh_ranged_base", 2.0), _num("refresh_ranged_per_tier", 2.0))   # 2 / 4 / 6 s (user, 2026-11-08)
for _path, _native, _what, _cuts in [(REFRESHMENT, "PotionThirstMelee", "Refreshment", REFRESH),
                                     (REFRESHMENT_RANGED, "PotionThirstRanged", "Refreshment (ranged)", REFRESH_RANGED)]:
    _kill, _dead, _wearer = kill_credit_host(_path, _D + _native, _what,
                                             dict(Left="float", CooldownQuery="struct:/Script/GameplayAbilities.GameplayEffectQuery"),
                                             dict(CooldownQuery=COOLDOWN_QUERY))
    _asc = _g.call(_GAS, "GetAbilitySystemComponent")
    _g.link(_wearer[0], _wearer[1], _asc, "Actor")
    _effects = _g.call(_ASC, "GetActiveEffects")
    _g.link(_asc, "ReturnValue", _effects, "self")
    _g.link(*(_v("CooldownQuery") + (_effects, "Query")))
    _cooling = _g.branch(_math("Greater_IntInt", (_g.array_call("Array_Length", (_effects, "ReturnValue"), "TargetArray"), "ReturnValue"), 0))
    _first = _g.item_at((_effects, "ReturnValue"))
    _left = _g.call(_GAS, "GetActiveGameplayEffectRemainingDuration")
    _g.link(_first[0], _first[1], _left, "ActiveHandle")
    _cut = _own_share((_cuts[0] - _cuts[1], _cuts[1]))
    # noted BEFORE the removal: the pure nodes above would read nothing afterwards
    _note = [set_value(_g, "LastBonus", _cut), set_value(_g, "Left", _math("Subtract_FloatFloat", (_left, "ReturnValue"), _cut))]
    _remove = _g.call(_ASC, "RemoveActiveGameplayEffect", StacksToRemove=-1)
    _g.link(_asc, "ReturnValue", _remove, "self")
    _g.link(_first[0], _first[1], _remove, "Handle")
    _again = _g.branch(_math("Greater_FloatFloat", _v("Left"), 0.05))
    _ctx = _g.call(_ASC, "MakeEffectContext")
    _g.link(_asc, "ReturnValue", _ctx, "self")
    _spec = _g.call(_ASC, "MakeOutgoingSpec", GameplayEffectClass=_effect_class(_POTION_CD), Level=1.0)
    _g.link(_asc, "ReturnValue", _spec, "self")
    _g.link(_ctx, "ReturnValue", _spec, "Context")
    _dur = _g.call(_GAS, "AssignSetByCallerMagnitude", DataName="Duration")
    _g.link(_spec, "ReturnValue", _dur, "SpecHandle")
    _link_value(_v("Left"), _dur, "Magnitude")
    _put_on = _g.call(_ASC, "BP_ApplyGameplayEffectSpecToSelf")
    _g.link(_asc, "ReturnValue", _put_on, "self")
    _g.link(_dur, "ReturnValue", _put_on, "SpecHandle")
    _done = _count("Extra")
    _told = _triggered()
    # every Bottomless Brew the wearer has is told first (user, 2026-11-08: the extras refill sooner too)
    _brews = _pure(_g.call(_AC, "GetComponentsByClass", ComponentClass=FOOD_RESERVES + "." + FOOD_RESERVES.rsplit("/", 1)[1] + "_C"),
                   "GetComponentsByClass")
    _g.link(_wearer[0], _wearer[1], _brews, "self")
    _bloop, _brew, _ = _loop_over((_brews, "ReturnValue"), _kill)
    _brew_c = _g.cast(FOOD_RESERVES + "." + FOOD_RESERVES.rsplit("/", 1)[1] + "_C", _brew)
    _tell_brew = _g.call(FOOD_RESERVES + "." + FOOD_RESERVES.rsplit("/", 1)[1] + "_C", "Refreshed")
    _g.link(_brew_c[0], _brew_c[1], _tell_brew, "self")
    _link_value(_own_share((_cuts[0] - _cuts[1], _cuts[1])), _tell_brew, "Seconds")
    _g.flow((_bloop, "LoopBody"), _brew_c[0], _tell_brew)
    _g.flow(*([(_bloop, "Completed")] + _steps(_effects) + [_cooling]))
    _g.flow(*([(_cooling, "then")] + _steps(_left) + _note + [_remove, _again]))
    _g.flow(*([(_again, "then")] + _steps(_spec, _dur) + [_put_on, _done, _told]))
    _g.link(_again, "else", _done, "execute")
    compile_save(_bp, _what + " (kill credit)")
    _switch_off(_path, {"cooldownReductionBase": 0.0, "cooldownReductionPerLevel": 0.0}, _what + "'s own cut off")

# --- Shockwave and Swirling: scaling with the weapon (user, 2026-11-07) ---------------------------------------------
# Both keep the game's own damage; on top, every mob the wave passes / the spin reaches takes COMBO of the wearer's
# last weapon hit (50 / 75 / 100%), from the wearer (kill credit). The hit is measured as for Sweeping Edge (our hit
# spark tells the enchantment Struck(mob); measuring_host). Ours sit at the game's paths over the native classes:
#   Shockwave: the game's BP_Shockwave only sets the wave's class (BP_ShockwaveProjectile, linked through a
#     placeholder) - the numbers come from SequelMod.toml (our file replaces the patched one). Every look the wearer's
#     waves (owner / instigator the wearer; none at all and within WAVE_MINE when first seen) are found and every
#     hostile mob within WAVE_REACH of one takes the extra, at most once every BONUS_GAP s per mob.
#   Swirling: the game plays GameplayCue.Trigger.Enchantment.Swirling on the wearer at the spin (its
#     BP_SwirlingNotifyStatic: the swirl particle attached to the wearer, scale RawMagnitude / 300, and the swirl
#     sound, read 2026-11-07). Ours at that path does the same (placeholders) and tells the wearer's Swirling
#     Swirled(RawMagnitude = the spin's range); hostile mobs within it take the extra.
COMBO = (_num("combo_base", 0.25), _num("combo_per_tier", 0.25))
WAVE_REACH, WAVE_MINE = _num("wave_reach", 250.0), 400.0
SHOCKWAVE = "/Game/Components/Enchantments/Shockwave/BP_Shockwave"
SWIRLING = "/Game/Components/Enchantments/Swirling/BP_Swirling"
WAVE_PROJECTILE = "/Game/Components/Enchantments/Shockwave/BP_ShockwaveProjectile"
SWIRL_CUE = "/Game/Cues/Enchantments/BP_SwirlingNotifyStatic"
SWIRL_FX = "/Game/Components/Enchantments/Swirling/PS_Swirling.PS_Swirling"
SWIRL_SOUND = "/Game/AudioForce/04_playback_soundCue/05_sfx_player_attack1Normal/sfx_ui_swirlingNotifyStaticOnexecute"




def _keep_weapon(body, drop):
    """From a measured hit's body exec: Weapon = drop when the hit landed."""
    landed = _g.branch(_math("Greater_FloatFloat", drop, 0.0))
    _g.flow(body, landed, set_value(_g, "Weapon", drop))


def _combo_extra(center, radius, after):
    """From after: every hostile mob within radius of center (once every BONUS_GAP s each) takes COMBO x Weapon
    from the wearer. Returns the mob loop."""
    body, mob, loop = _hostile_mobs_near(center, radius, after)
    passed, _ = _gap_check(mob, body)
    amount = _math("Multiply_FloatFloat", _v("Weapon"), _own_share(COMBO))
    some = _g.branch(_math("Greater_FloatFloat", amount, 0.0))
    _link_exec(passed, some)
    hurt = _deal(_wearer, mob, amount)
    _g.flow(*([(some, "then")] + hurt + [_count("Bonuses"), set_value(_g, "LastBonus", amount)]))
    return loop


# the wave's class: a placeholder at the game's path (never packed)
compile_save(blueprint(WAVE_PROJECTILE, unreal.Actor.static_class()), "placeholder for the game's Shockwave wave")
placeholder(WAVE_PROJECTILE)
_WAVE_CLASS = _effect_class(WAVE_PROJECTILE)

_body, _mob, _drop, _at, _wearer = measuring_host(SHOCKWAVE, _D + "Shockwave", "Shockwave",
                                                  dict(Weapon="float", Waves="array:" + _ACTOR,
                                                       KeepWaves="array:" + _ACTOR, Checked="array:" + _ACTOR))
_keep_weapon(_body, _drop)
_g.row(2700)
_found = _g.call(_GS, "GetAllActorsOfClass", ActorClass=_WAVE_CLASS)
_g.flow(measuring_host.after_look, _found)
_loop, _wave, _ = _loop_over((_found, "OutActors"), (_found, "then"))
_old = _g.array_call("Array_Find", _v("Checked"), "TargetArray", ItemToFind=_wave)
_is_new = _g.branch(_math("Less_IntInt", (_old, "ReturnValue"), 0))
_owner = _g.call(_AC, "GetOwner")
_g.link(_wave[0], _wave[1], _owner, "self")
_instigator = _g.call(_AC, "GetInstigator")
_g.link(_wave[0], _wave[1], _instigator, "self")
_by_owner = _g.call(_MATH, "EqualEqual_ObjectObject")
_g.link(_owner, "ReturnValue", _by_owner, "A")
_g.link(_wearer[0], _wearer[1], _by_owner, "B")
_by_instigator = _g.call(_MATH, "EqualEqual_ObjectObject")
_g.link(_instigator, "ReturnValue", _by_instigator, "A")
_g.link(_wearer[0], _wearer[1], _by_instigator, "B")
_owned = [_g.call(_KSL, "IsValid") for _ in range(2)]
_g.link(_owner, "ReturnValue", _owned[0], "Object")
_g.link(_instigator, "ReturnValue", _owned[1], "Object")
_unowned = []
for _o in _owned:
    _no = _g.call(_MATH, "Not_PreBool")
    _g.link(_o, "ReturnValue", _no, "A")
    _unowned.append((_no, "ReturnValue"))
_wave_gap = _g.call(_AC, "GetDistanceTo")
_g.link(_wave[0], _wave[1], _wave_gap, "self")
_g.link(_wearer[0], _wearer[1], _wave_gap, "OtherActor")
_nobodys_near = _math("BooleanAND", _math("BooleanAND", _unowned[0], _unowned[1]),
                      _math("LessEqual_FloatFloat", (_wave_gap, "ReturnValue"), WAVE_MINE))
_mine = _g.branch(_math("BooleanOR", _math("BooleanOR", (_by_owner, "ReturnValue"), (_by_instigator, "ReturnValue")),
                        _nobodys_near))
_add_wave = _g.array_call("Array_Add", _v("Waves"), "TargetArray", NewItem=_wave)
_g.flow((_loop, "LoopBody"), _is_new, _mine, _add_wave, _count("Seen"))
# then every wave of the wearer's still there: the mobs near it
_g.row(3000)
_loop2, _my_wave, _ = _loop_over(_v("Waves"), (_loop, "Completed"))
_there = _g.call(_KSL, "IsValid")
_g.link(_my_wave[0], _my_wave[1], _there, "Object")
_alive = _g.branch((_there, "ReturnValue"))
_keep_it = _g.array_call("Array_Add", _v("KeepWaves"), "TargetArray", NewItem=_my_wave)
_wave_at = _g.call(_AC, "K2_GetActorLocation")
_g.link(_my_wave[0], _my_wave[1], _wave_at, "self")
_g.flow((_loop2, "LoopBody"), _alive, _keep_it)
_g.row(3300)
_combo_extra((_wave_at, "ReturnValue"), WAVE_REACH, (_keep_it, "then"))
_g.row(3600)
_g.flow((_loop2, "Completed"), set_value(_g, "Waves", _v("KeepWaves")),
        _g.array_call("Array_Clear", _v("KeepWaves"), "TargetArray"),
        set_value(_g, "Checked", (_found, "OutActors")))
compile_save(_bp, "Shockwave (weapon scaling)")
_wave_numbers = _toml_numbers("BP_Shockwave")
check(len(_wave_numbers) >= 5, "Shockwave's numbers in SequelMod.toml")
_switch_off(SHOCKWAVE, _wave_numbers, "Shockwave's numbers (SequelMod.toml)")
check(LIB.set_default_property(assets.load_asset(SHOCKWAVE), "ShockWaveProjectileClass",
                               "BlueprintGeneratedClass'%s'" % _WAVE_CLASS), "Shockwave's wave class")
assets.save_loaded_asset(assets.load_asset(SHOCKWAVE))
check(unreal.get_default_object(assets.load_blueprint_class(SHOCKWAVE)).get_editor_property("ShockWaveProjectileClass")
      is not None, "Shockwave's wave class is set")

# Swirling
_body, _mob, _drop, _at, _wearer = measuring_host(SWIRLING, _D + "Swirling", "Swirling", dict(Weapon="float"))
_keep_weapon(_body, _drop)
_g.row(2700)
_swirled = _g.custom_event("Swirled", "Radius=float")
_authority = _g.call(_AC, "HasAuthority")
_g.link(_wearer[0], _wearer[1], _authority, "self")
_on_host = _g.branch((_authority, "ReturnValue"))
_reach = _g.call(_MATH, "SelectFloat", B=_toml_numbers("BP_Swirling").get("Range", 400.0))
_g.link(_swirled, "Radius", _reach, "A")
_g.link(*(_math("Greater_FloatFloat", (_swirled, "Radius"), 50.0) + (_reach, "bPickA")))
_spun = _count("Seen")
_wearer_at = _g.call(_AC, "K2_GetActorLocation")
_g.link(_wearer[0], _wearer[1], _wearer_at, "self")
_g.flow(_swirled, _on_host, _spun)
_g.row(3000)
_combo_extra((_wearer_at, "ReturnValue"), (_reach, "ReturnValue"), (_spun, "then"))
compile_save(_bp, "Swirling (weapon scaling)")
_switch_off(SWIRLING, {k: v for k, v in _toml_numbers("BP_Swirling").items() if k != "MinimalHitCountToTrigger"},
            "Swirling's numbers (SequelMod.toml)")

# Thundering: as Shockwave / Swirling, but it strikes on (nearly) every hit (TriggerChance 1 in SequelMod.toml), so
# THUNDER of the hit like Sweeping Edge's splash: every hostile mob within StrikeRadius of the strike, the hit mob too
# (user, 2026-11-08: proc enchantments scaling with the weapon). Hooked through our copy of its strike cue (below).
def _particle_at(effect, target):
    """Spawn the particle effect (object path) at target (node, pin). Returns the exec steps."""
    where = _g.call("/Script/Engine.Actor", "K2_GetActorLocation")
    _g.link(target[0], target[1], where, "self")
    spawn = _g.call("/Script/Engine.GameplayStatics", "SpawnEmitterAtLocation", EmitterTemplate=effect)
    if "WorldContextObject" in _g.pins(spawn):
        _g.link(target[0], target[1], spawn, "WorldContextObject")
    _g.link(where, "ReturnValue", spawn, "Location")
    return [spawn]


# Lightning (user, 2026-11-08: all lightning deals a share of max health, like fire and poison, and Lightning
# Focus boosts all of it): Thundering, Electrified, Overload.
LIGHTNING_FOCUS = "/Game/Content_DLC4/Components/Enchantments/LightningFocus/BP_LightningFocus"
LIGHTNING_FOCUS_PER_TIER = _toml_numbers("BP_LightningFocus").get("DamageIncreasePerLevel", 0.25)
compile_save(blueprint(LIGHTNING_FOCUS, unreal.load_class(None, _D + "Enchantment")),
             "placeholder for the game's Lightning Focus")
placeholder(LIGHTNING_FOCUS)
LIGHTNING_DAMAGE = _typed_damage("/Game/Components/Enchantments/Sequel/GE_SequelLightningDamage", "lightning damage",
                                 "Damage.Elemental.Lightning", on_effect=False)
_ARC_FX = game_particle("/Game/Components/Enchantments/Thundering/PS_ThunderingImpact")


def _lightning_focus(wearer, after):
    """From the exec (node, pin) after: Focus = 1 + LIGHTNING_FOCUS_PER_TIER x the tier of the Lightning Focus the
    wearer wears (its first copy), else 1. Returns the exec (node, pin)s that go on."""
    plain = set_value(_g, "Focus", 1.0)
    found = _pure(_g.call(_AC, "GetComponentByClass", ComponentClass=_effect_class(LIGHTNING_FOCUS)), "GetComponentByClass")
    _g.link(wearer[0], wearer[1], found, "self")
    valid = _g.call(_KSL, "IsValid")
    _g.link(found, "ReturnValue", valid, "Object")
    has = _g.branch((valid, "ReturnValue"))
    focus = _g.cast(_D + "Enchantment", (found, "ReturnValue"))
    level = _g.var("Level", owner=_D + "Enchantment", target=focus)
    level_f = _g.call(_MATH, "Conv_IntToFloat")
    _g.link(level, "Level", level_f, "InInt")
    boosted = set_value(_g, "Focus", _math("Add_FloatFloat", 1.0,
                                            _math("Multiply_FloatFloat", (level_f, "ReturnValue"), LIGHTNING_FOCUS_PER_TIER)))
    _g.flow(after, plain, has)
    _g.flow((has, "then"), focus[0], boosted)
    return [(has, "else"), (focus[0], "CastFailed"), (boosted, "then")]


def _lightning_share(mob, share):
    """mob's (node, pin) max health x share (node, pin) x the boss factor x Focus (node, pin)."""
    return _math("Multiply_FloatFloat", _math("Multiply_FloatFloat", _math("Multiply_FloatFloat",
                 _attribute(mob, _HEALTH_SET, "MaxHealth"), share), _boss_factor(mob)), _v("Focus"))


def _listen_shots(wearer, after, event_name):
    """From the exec (node, pin) after (run it again and again: binding twice keeps one): the wearer's
    RangedAttackComponent.OnBeginRangedAttack - every shot fired, Accelerating's trigger (user, 2026-11-08) - calls the
    custom event event_name (no inputs). Returns that event node."""
    found = _g.call(_AC, "GetComponentByClass", ComponentClass=_D + "RangedAttackComponent")
    _g.link(wearer[0], wearer[1], found, "self")
    ranged = _g.cast(_D + "RangedAttackComponent", (found, "ReturnValue"))
    bind = _g.node("/Script/BlueprintGraph.K2Node_AddDelegate")
    check(LIB.set_node_property(_bp, _g.name, bind, "DelegateReference",
                                "(MemberParent=Class'/Script/Dungeons.RangedAttackComponent',MemberName=\"OnBeginRangedAttack\")"),
          "OnBeginRangedAttack delegate")
    _g.link(ranged[0], ranged[1], bind, "self")
    _g.flow(after, ranged[0], bind)
    shot = _g.custom_event(event_name)
    _g.link(shot, "OutputDelegate", bind, "Delegate")
    return shot





THUNDERING = "/Game/Components/Enchantments/Thundering/BP_Thundering"
THUNDER = (_num("thunder_base", 0.0), _num("thunder_per_tier", 0.01))   # 1 / 2 / 3% of max health per strike
THUNDER_GAP = _num("thunder_gap", 0.1)   # no half-second cap (user, 2026-11-09): only one swing's overlapping strikes count once
THUNDER_CUE = "/Game/Cues/Enchantments/BP_ThunderingStrikeNotifyStatic"
THUNDER_FX = "/Game/Components/Enchantments/Thundering/PS_ThunderingImpact.PS_ThunderingImpact"
THUNDER_SOUND = "/Game/AudioForce/04_playback_soundCue/05_sfx_player_attack2Rare/sfx_player_thunderingStrikeNotifyStaticOnExecute"
_thunder_numbers = _toml_numbers("BP_Thundering")
STRIKE_REACH = _thunder_numbers.get("StrikeRadius", 150.0) + 100.0
_body, _mob, _drop, _at, _wearer = measuring_host(THUNDERING, _D + "Thundering", "Thundering",
                                                  dict(Weapon="float", Focus="float"))
_keep_weapon(_body, _drop)
_g.row(2700)
_struck = _g.custom_event("Strike", "Where=struct:/Script/CoreUObject.Vector")
_authority = _g.call(_AC, "HasAuthority")
_g.link(_wearer[0], _wearer[1], _authority, "self")
_on_host = _g.branch((_authority, "ReturnValue"))
_strikes = _count("Seen")
_g.flow(_struck, _on_host, _strikes)
_g.row(3000)
_tfocus = _lightning_focus(_wearer, (_strikes, "then"))
_tjoin = set_value(_g, "Weapon", _v("Weapon"))
_link_exec(_tfocus, _tjoin)
_tbody, _tmob, _ = _hostile_mobs_near((_struck, "Where"), STRIKE_REACH, (_tjoin, "then"))
_tpass, _ = _gap_check(_tmob, _tbody, THUNDER_GAP)
_tamount = _lightning_share(_tmob, _own_share(THUNDER))
_tsome = _g.branch(_math("Greater_FloatFloat", _tamount, 0.0))
_link_exec(_tpass, _tsome)
_g.flow(*([(_tsome, "then")] + _deal(_wearer, _tmob, _tamount, LIGHTNING_DAMAGE)
          + [_count("Bonuses"), set_value(_g, "LastBonus", _tamount)]))
compile_save(_bp, "Thundering (share of max health)")
_switch_off(THUNDERING, _thunder_numbers, "Thundering's numbers (SequelMod.toml)")

# --- Electrified: its zap deals a share of max health (user, 2026-11-08) --------------------------------------------
# Every hostile mob the wearer's Electrified zaps (our copy of its receiver cue, further down, tells every Electrified
# wearer within SPLASH_HITTER_RANGE: Zapped(mob)) takes ELECTRIFY of its max health (bosses BOSS_SHARE of it),
# boosted by Lightning Focus. The game's zap stays (SequelMod.toml's numbers).
ELECTRIFIED = "/Game/Components/Enchantments/Electrified/BP_Electrified"
ELECTRIFY = (_num("electrify_base", 0.02), _num("electrify_per_tier", 0.02))   # 4 / 6 / 8% of max health
_elec_numbers = _toml_numbers("BP_Electrified")
_bp = blueprint(ELECTRIFIED, unreal.load_class(None, _D + "Electrified"))
for _name, _kind in dict(Focus="float", Seen="int", Bonuses="int", LastBonus="float").items():
    check(LIB.add_variable(_bp, _name, _kind), "Electrified: variable " + _name)
LIB.compile(_bp)
_g = Graph(_bp)
_WEARER = (_g.call(_COMPONENT, "GetOwner"), "ReturnValue")
_g.row(0)
_zapped = _g.custom_event("Zapped", "Mob=" + _ACTOR)
_authority = _g.call(_AC, "HasAuthority")
_g.link(_WEARER[0], _WEARER[1], _authority, "self")
_mob_char = _g.cast(_BASE, (_zapped, "Mob"))
_me = _g.cast(_BASE, _WEARER)
_foe = _g.call(_MATH, "Not_PreBool")
_g.link(*(_same_team(_me, _mob_char) + (_foe, "A")))
_alive = _math("Greater_FloatFloat", _attribute((_zapped, "Mob"), _HEALTH_SET, "Health"), 0.0)
_go = _g.branch(_math("BooleanAND", _math("BooleanAND", (_authority, "ReturnValue"), (_foe, "ReturnValue")),
                      _math("BooleanAND", _alive, _is_player(_WEARER))))
_seen = _count("Seen")
_g.flow(_zapped, _mob_char[0], _me[0], _go, _seen)
_g.row(300)
_efocus = _lightning_focus(_WEARER, (_seen, "then"))
_ejoin = set_value(_g, "Seen", _v("Seen"))
_link_exec(_efocus, _ejoin)
_eamount = _lightning_share((_zapped, "Mob"), _own_share(ELECTRIFY))
_g.flow(*([(_ejoin, "then")] + _deal(_WEARER, (_zapped, "Mob"), _eamount, LIGHTNING_DAMAGE)
          + [_count("Bonuses"), set_value(_g, "LastBonus", _eamount)]))
compile_save(_bp, "Electrified (share of max health)")
_switch_off(ELECTRIFIED, _elec_numbers, "Electrified's numbers (SequelMod.toml)")

# --- Shock Web: its beams take a share of max health and charge mobs for Overload (user, 2026-11-12) -----------------
# Every hostile mob a beam of the wearer's web hurts (our copy of its hit cue, further down, tells every Shock Web
# wearer within SHOCK_REACH: Zapped(mob)) loses SHOCK_SHARE of its max health (bosses BOSS_SHARE of it), boosted by
# Lightning Focus - at most once every SHOCK_GAP s per mob (a beam hurts 4 times a second) - and is charged for
# Overload: the ranged half of Thundering + Overload. The game's beams stay (their damage back to the game's).
# Our BP_ShockWeb keeps the game's object defaults (its node actor, the projectiles it ignores) through placeholders.
SHOCK_WEB = "/Game/Content_DLC4/Components/Enchantments/ShockWeb/BP_ShockWeb"
SHOCK_WEB_NODE = "/Game/Content_DLC4/Components/Enchantments/ShockWeb/BP_ShockWebNode"
SHOCK_DENIED = ["/Game/Actors/Items/Arrow/Player/BP_PlayerFireworksArrow", "/Game/Actors/Items/TormentProjectile/BP_TormentProjectile"]
SHOCK_SHARE = (_num("shockweb_base", 0.0), _num("shockweb_per_tier", 0.01))   # 1 / 2 / 3% of max health per zap
SHOCK_GAP = _num("shockweb_gap", 0.5)                                         # so at most 2 / 4 / 6% a second
_shock_numbers = _toml_numbers("BP_ShockWeb")
SHOCK_REACH = _shock_numbers.get("Range", 2400.0) + SPLASH_HITTER_RANGE
compile_save(blueprint(SHOCK_WEB_NODE, unreal.Actor.static_class()),
             "placeholder for the game's Shock Web node")
placeholder(SHOCK_WEB_NODE)
for _path in SHOCK_DENIED:
    compile_save(blueprint(_path, unreal.Actor.static_class()), "placeholder for " + _path.rsplit("/", 1)[1])
    placeholder(_path)
_bp = blueprint(SHOCK_WEB, unreal.load_class(None, _D + "ShockWeb"))
for _name, _kind in dict(Focus="float", Seen="int", Bonuses="int", LastBonus="float",
                         GapMobs="array:" + _ACTOR, GapTimes="array:float").items():
    check(LIB.add_variable(_bp, _name, _kind), "Shock Web: variable " + _name)
LIB.compile(_bp)
_g = Graph(_bp)
_WEARER = (_g.call(_COMPONENT, "GetOwner"), "ReturnValue")
_g.row(0)
_zapped = _g.custom_event("Zapped", "Mob=" + _ACTOR)
_authority = _g.call(_AC, "HasAuthority")
_g.link(_WEARER[0], _WEARER[1], _authority, "self")
_mob_char = _g.cast(_BASE, (_zapped, "Mob"))
_me = _g.cast(_BASE, _WEARER)
_foe = _g.call(_MATH, "Not_PreBool")
_g.link(*(_same_team(_me, _mob_char) + (_foe, "A")))
_alive = _math("Greater_FloatFloat", _attribute((_zapped, "Mob"), _HEALTH_SET, "Health"), 0.0)
_go = _g.branch(_math("BooleanAND", _math("BooleanAND", (_authority, "ReturnValue"), (_foe, "ReturnValue")),
                      _math("BooleanAND", _alive, _is_player(_WEARER))))
_seen = _count("Seen")
_g.flow(_zapped, _mob_char[0], _me[0], _go, _seen)
_g.row(300)
_wpass, _ = _gap_check((_zapped, "Mob"), (_seen, "then"), SHOCK_GAP)
_wjoin = set_value(_g, "Seen", _v("Seen"))
_link_exec(_wpass, _wjoin)
_wfocus = _lightning_focus(_WEARER, (_wjoin, "then"))
_wjoin2 = set_value(_g, "Seen", _v("Seen"))
_link_exec(_wfocus, _wjoin2)
_g.row(600)
_wamount = _lightning_share((_zapped, "Mob"), _own_share(SHOCK_SHARE))
_g.flow(*([(_wjoin2, "then")] + _deal(_WEARER, (_zapped, "Mob"), _wamount, LIGHTNING_DAMAGE)
          + [_count("Bonuses"), set_value(_g, "LastBonus", _wamount)]))
compile_save(_bp, "Shock Web (share of max health)")
_cdo = unreal.get_default_object(assets.load_blueprint_class(SHOCK_WEB))
_cdo.set_editor_property("ActorToSpawn", assets.load_blueprint_class(SHOCK_WEB_NODE))
_cdo.set_editor_property("DeniedProjectiles", [assets.load_blueprint_class(p) for p in SHOCK_DENIED])
check(_cdo.get_editor_property("ActorToSpawn") is not None and len(_cdo.get_editor_property("DeniedProjectiles")) == 2,
      "Shock Web: the game's node actor and ignored projectiles")
_switch_off(SHOCK_WEB, _shock_numbers, "Shock Web's numbers (SequelMod.toml)")


# --- Exploding: kill credit, at once, in chains (user, 2026-11-08) ---------------------------------------------------
# Every kill credited to the wearer (as for Leeching) explodes at once: the game's Exploding look and sound at the mob
# (placeholders), and every hostile mob within EXPLODE_RADIUS takes EXPLODE of the dead mob's max health (20 / 40 /
# 60%, the game's numbers) from the wearer. Those mobs are marked as the wearer's first, so the ones it kills explode
# too (chains; user). The game's own explosion is off: no damage, no reach, no look or sound (our BP_Exploding leaves
# ExplosionEffect / ExplosionSound empty) - it went off a moment after the death. The card number: Formulas.toml.
EXPLODING = "/Game/Components/Enchantments/Exploding/BP_Exploding"
EXPLODE = (_num("explode_base", 0.15), _num("explode_per_tier", 0.1))   # 15 / 25 / 35% (user, 2026-11-08)
EXPLODE_RADIUS = _toml_numbers("BP_Exploding").get("ExplosionRadius", 450.0)
_boom_fx = game_particle("/Game/Components/Enchantments/Exploding/PS_EnchantedExplosion")   # the game's own Exploding look (purple)
BOOM_SOUND = "/Game/AudioForce/04_playback_soundCue/03_sfx_item/sfx_item_genericExplode"
assets.save_loaded_asset(fresh(BOOM_SOUND, unreal.SoundCue, unreal.SoundCueFactoryNew()))
placeholder(BOOM_SOUND)
_kill, _dead, _wearer = kill_credit_host(EXPLODING, _D + "Exploding", "Exploding")
_boom_at = _g.call(_AC, "K2_GetActorLocation")
_g.link(_dead[0], _dead[1], _boom_at, "self")
_keep = set_value(_g, "LastBonus", _math("Multiply_FloatFloat", _attribute(_dead, _HEALTH_SET, "MaxHealth"),
                                          _own_share((EXPLODE[0] - EXPLODE[1], EXPLODE[1]))))
_look = _g.call(_GS, "SpawnEmitterAtLocation", EmitterTemplate=_boom_fx)
if "WorldContextObject" in _g.pins(_look):
    _g.link(_dead[0], _dead[1], _look, "WorldContextObject")
_g.link(_boom_at, "ReturnValue", _look, "Location")
_bang = _g.call(_GS, "SpawnSoundAtLocation", Sound=BOOM_SOUND + "." + BOOM_SOUND.rsplit("/", 1)[1])
if "WorldContextObject" in _g.pins(_bang):
    _g.link(_dead[0], _dead[1], _bang, "WorldContextObject")
_g.link(_boom_at, "ReturnValue", _bang, "Location")
_told = _triggered()
# one explosion per kill: a second copy (a built-in Exploding plus a chosen one) stays quiet - only the wearer's first
# Exploding acts (user, 2026-11-08: copies don't stack, as in the game)
_first = _pure(_g.call(_AC, "GetComponentByClass", ComponentClass=_effect_class(EXPLODING)), "GetComponentByClass")
_g.link(_wearer[0], _wearer[1], _first, "self")
_is_first = _g.call(_MATH, "EqualEqual_ObjectObject")
_g.link(_first, "ReturnValue", _is_first, "A")
_g.link(*(_g.self_node() + (_is_first, "B")))
_only_one = _g.branch((_is_first, "ReturnValue"))
_g.flow(_kill, _only_one)
_g.flow((_only_one, "then"), _keep, _look, _bang, _count("Extra"), _told)
_g.row(2100)
_body, _victim, _ = _hostile_mobs_near((_boom_at, "ReturnValue"), EXPLODE_RADIUS, (_told, "then"), skip=_dead)
_join = _g.branch((_g.call(_MATH, "Not_PreBool"), "ReturnValue"))   # a join point (NOT false: always "then")
_link_exec(_mark(_victim, _body), _join)
_g.flow(*([(_join, "then")] + _deal(_wearer, _victim, _v("LastBonus"))))
compile_save(_bp, "Exploding (kill credit, chains)")
_switch_off(EXPLODING, {"explosionMaxHealthFactorBase": 0.0, "explosionMaxHealthFactorPerLevel": 0.0,
                        "ExplosionRadius": 0.0}, "Exploding's own explosion off")
# its look and sound: left empty, the game still played them a moment later (user, 2026-11-08 - the class's own
# defaults, an empty link isn't saved) - so an empty particle system and an empty sound of ours
_NOTHING_FX = "/Game/Components/Enchantments/Sequel/PS_SequelNothing"
_NOTHING_SOUND = "/Game/Components/Enchantments/Sequel/SC_SequelNothing"
assets.save_loaded_asset(fresh(_NOTHING_FX, unreal.ParticleSystem, unreal.ParticleSystemFactoryNew()))
assets.save_loaded_asset(fresh(_NOTHING_SOUND, unreal.SoundCue, unreal.SoundCueFactoryNew()))
_exploding = assets.load_asset(EXPLODING)
for _prop, _what in (("ExplosionEffect", "ParticleSystem'%s.PS_SequelNothing'" % _NOTHING_FX),
                     ("ExplosionSound", "SoundCue'%s.SC_SequelNothing'" % _NOTHING_SOUND)):
    check(LIB.set_default_property(_exploding, _prop, _what), "Exploding's own " + _prop + " = nothing")
assets.save_loaded_asset(_exploding)
_cdo = unreal.get_default_object(assets.load_blueprint_class(EXPLODING))
check(_cdo.get_editor_property("ExplosionEffect") is not None and _cdo.get_editor_property("ExplosionSound") is not None,
      "Exploding's own look and sound point at nothing")
# (the game's delayed Exploding cue: made silent with the other cues, further down)

# --- Shadowcloak (Sponge Strike) on kill credit (user, 2026-11-08) ---------------------------------------------------
# Before: the mission's kill count every WATCH_SECONDS, one roll for all the kills of a look (so a burst of kills
# gave one try - 4 Shadow Forms in 36 kills) and every player's kills counted. Now: every kill credited to the wearer
# rolls on its own (15 / 20 / 25%), Shadow Form as before (Shadow Shot's way, see above).
_kill, _dead, _wearer = kill_credit_host(SPONGE_STRIKE, _D + "Rushdown", "Shadowcloak")
_chance = _own_share((CLOAK_BASE, CLOAK_PER_TIER))
_roll = _g.call(_MATH, "RandomFloat")
_lucky = _g.branch(_math("Less_FloatFloat", (_roll, "ReturnValue"), _chance))
_asc = _g.call(_GAS, "GetAbilitySystemComponent")
_g.link(_wearer[0], _wearer[1], _asc, "Actor")
_context = _g.call(_ASC, "MakeEffectContext")
_g.link(_asc, "ReturnValue", _context, "self")
_spec = _g.call(_ASC, "MakeOutgoingSpec", GameplayEffectClass=SHADOW_FORM)
_g.link(_asc, "ReturnValue", _spec, "self")
_tier_f = _g.call(_MATH, "Conv_IntToFloat")
_link_value(_tier(), _tier_f, "InInt")
_g.link(_tier_f, "ReturnValue", _spec, "Level")
_g.link(_context, "ReturnValue", _spec, "Context")
_duration = _g.call(_GAS, "AssignSetByCallerMagnitude", DataName="Duration", Magnitude=CLOAK_SECONDS)
_g.link(_spec, "ReturnValue", _duration, "SpecHandle")
_boost = _g.call(_GAS, "AssignSetByCallerMagnitude", DataName="Magnitude", Magnitude=CLOAK_BOOST)
_g.link(_duration, "ReturnValue", _boost, "SpecHandle")
_apply = _g.call(_ASC, "BP_ApplyGameplayEffectSpecToSelf")
_g.link(_asc, "ReturnValue", _apply, "self")
_g.link(_boost, "ReturnValue", _apply, "SpecHandle")
_g.flow(_kill, _lucky)
_g.flow(*([(_lucky, "then")] + _steps(_spec, _duration, _boost) + [_apply, _count("Extra"), _triggered()]))
compile_save(_bp, "Shadowcloak (kill credit)")
# Rushdown's own speed-up (a weapon kill) - its Effect is ours, doing nothing (an empty one would crash: the Levitation
# lesson, 2026-11-08); its numbers stay
_NO_RUSH = "/Game/Content_DLC3/Components/Enchantments/Rushdown/GE_SequelNoRush"
compile_save(blueprint(_NO_RUSH, unreal.load_class(None, _D + "RushdownGameplayEffect")), "Shadowcloak: Rushdown's empty effect")
check(LIB.set_default_property(assets.load_asset(SPONGE_STRIKE), "Effect", "BlueprintGeneratedClass'%s.GE_SequelNoRush_C'" % _NO_RUSH),
      "Rushdown's own effect = ours (does nothing)")
assets.save_loaded_asset(assets.load_asset(SPONGE_STRIKE))
_cdo = unreal.get_default_object(assets.load_blueprint_class(SPONGE_STRIKE))
check(_cdo.get_editor_property("Effect") is not None, "Rushdown's Effect is set")

# --- Rampaging on kill credit (user, 2026-11-08) ---------------------------------------------------------------------
# Every kill credited to the wearer: attack speed x AttackSpeedBoost (1.5) for BoostTime x tier s (2 / 4 / 6 s,
# SequelMod.toml), one copy - a new kill restarts the time. The game's own trigger is off (TriggerChance 0); its card
# number (tier x BoostTime) stays right.
RAMPAGING = "/Game/Components/Enchantments/Rampaging/BP_Rampaging"
_ramp_numbers = _toml_numbers("BP_Rampaging")
_RAMP_FX = timed_effect("/Game/Components/Enchantments/Rampaging/GE_SequelRampaging", "Rampaging",
                        [("/Script/Dungeons.MeleeAttributeSet", "MeleeAttackSpeedMultiplier", _MULTIPLY,
                          _ramp_numbers.get("AttackSpeedBoost", 1.5))])
_kill, _dead, _wearer = kill_credit_host(RAMPAGING, _D + "Rampaging", "Rampaging")
_ramp_tier = _g.call(_MATH, "Conv_IntToFloat")
_link_value(_tier(), _ramp_tier, "InInt")
_seconds = _math("Multiply_FloatFloat", _ramp_numbers.get("BoostTime", 2.0), (_ramp_tier, "ReturnValue"))
_asc, _spec, _spec_steps = timed_spec(_RAMP_FX, _seconds)
_apply = _g.call(_ASC, "BP_ApplyGameplayEffectSpecToSelf")
_g.link(_asc[0], _asc[1], _apply, "self")
_g.link(_spec[0], _spec[1], _apply, "SpecHandle")
_keep = set_value(_g, "LastBonus", _seconds)
_g.flow(*([_kill, _keep] + _spec_steps + [_apply, _count("Extra"), _triggered()]))
compile_save(_bp, "Rampaging (kill credit)")
_switch_off(RAMPAGING, dict(_ramp_numbers, TriggerChance=0.0), "Rampaging's own trigger off")


# --- Guarding Strike on kill credit (user, 2026-11-08: on-kill enchantments count every kill of the wearer's) --------
# Every kill credited to the wearer: our shield effect - damage taken divided by 1 / (1 - DamageReduction) (50% less) -
# for effectBaseDuration + effectDurationPerLevel x tier s (3 / 4 / 5, SequelMod.toml), one copy - a new kill restarts
# the time. The game's own shield is off (DamageReduction 0: its effect still comes on a weapon kill, doing nothing).
GUARDING_STRIKE = "/Game/Content_DLC5/Components/Enchantments/GuardingStrike/BP_GuardingStrike"
_guard_numbers = _toml_numbers("BP_GuardingStrike")
_GUARD_FX = timed_effect("/Game/Content_DLC5/Components/Enchantments/GuardingStrike/GE_SequelGuardingStrike",
                         "Guarding Strike",
                         [(_HEALTH_SET, "TakeDamageMultiplier", _DIVIDE,
                           1.0 / (1.0 - _guard_numbers.get("DamageReduction", 0.5)))],
                         ("Guarding Strike", "/Game/Content_DLC5/Components/Enchantments/GuardingStrike/T_GuardingStrike_Icon"))
_kill, _dead, _wearer = kill_credit_host(GUARDING_STRIKE, _D + "GuardingStrike", "Guarding Strike")
_gseconds = tier_seconds(_guard_numbers.get("effectBaseDuration", 2.0), _guard_numbers.get("effectDurationPerLevel", 1.0))
_asc, _spec, _spec_steps = timed_spec(_GUARD_FX, _gseconds)
_apply = _g.call(_ASC, "BP_ApplyGameplayEffectSpecToSelf")
_g.link(_asc[0], _asc[1], _apply, "self")
_g.link(_spec[0], _spec[1], _apply, "SpecHandle")
_keep = set_value(_g, "LastBonus", _gseconds)
_g.flow(*([_kill, _keep] + _spec_steps + [_apply, _count("Extra"), _triggered()]))
compile_save(_bp, "Guarding Strike (kill credit)")
_switch_off(GUARDING_STRIKE, {"DamageReduction": 0.0}, "Guarding Strike's own shield off")



# the debug readout's graph: every 0.25 s, the counters of player 0's hit enchantments and of the watcher
_bp = _debug_view
_g = Graph(_debug_view)
_g.row(0)
_g.flow(_g.event("/Script/UMG.UserWidget", "Construct"),
        _g.call(_KSL, "K2_SetTimer", FunctionName="Show", Time=0.25, bLooping="true"))
_g.row(300)
_show = _g.custom_event("Show")
_reset = set_value(_g, "Lines", "TEST readout (Debuffs.toml debug)")
_g.flow(_show, _reset)
_last = [(_reset, "then")]


def _num_str(value, is_float=False):
    if is_float:
        r = _g.call(_MATH, "Round")
        _link_value(value, r, "A")
        value = (r, "ReturnValue")
    node = _g.call("/Script/Engine.KismetStringLibrary", "Conv_IntToString")
    _link_value(value, node, "InInt")
    return node, "ReturnValue"


def _add_line(parts):
    """Lines += newline + parts (strings / (node, pin) strings). Returns the set node."""
    return set_value(_g, "Lines", _concat(*([_v("Lines"), chr(10)] + parts)))


_pawn = (_g.call(_GS, "GetPlayerPawn", PlayerIndex=0), "ReturnValue")
for _name, _path, _extra in [("Sweeping Edge", KNOCKBACK, "-"), ("Ignite", EMERALD_DIVINATION, "spread"),
                             ("Venom Siphon", ALTRUISTIC, "heals"), ("Shatter", CHARGING_ACCELERATION, "-"),
                             ("Shockwave", SHOCKWAVE, "-"), ("Swirling", SWIRLING, "-"),
                             ("Thundering", THUNDERING, "-")]:
    _cls = _path + "." + _path.rsplit("/", 1)[1] + "_C"
    _found = _pure(_g.call(_AC, "GetComponentByClass", ComponentClass=_cls), "GetComponentByClass")
    _g.link(_pawn[0], _pawn[1], _found, "self")
    _valid = _g.call(_KSL, "IsValid")
    _g.link(_found, "ReturnValue", _valid, "Object")
    _has = _g.branch((_valid, "ReturnValue"))
    _link_exec(_last, _has)
    _as = _g.cast(_cls, (_found, "ReturnValue"))
    _get = lambda n: (_g.var(n, owner=_cls, target=_as), n)
    _line = _add_line([_name + ": looks ", _num_str(_get("Looks")), "  hits ", _num_str(_get("Hits")),
                       " (last ", _num_str(_get("LastHit"), True), ")  status ", _num_str(_get("Seen")),
                       "  extra ", _num_str(_get("Bonuses")), " (last ", _num_str(_get("LastBonus"), True), ")  " + _extra + " ",
                       _num_str(_get("Extra"))])
    _g.flow((_has, "then"), _as[0], _line)
    _last = [(_has, "else"), (_line, "then")]
for _name, _path, _what in [("Leeching", LEECHING, "heals"), ("Refreshment", REFRESHMENT, "cuts"),
                            ("Exploding", EXPLODING, "explosions"), ("Shadowcloak", SPONGE_STRIKE, "cloaks"),
                            ("Rampaging", RAMPAGING, "boosts"), ("Refreshment (ranged)", REFRESHMENT_RANGED, "cuts")]:
    _cls = _effect_class(_path)
    _found = _pure(_g.call(_AC, "GetComponentByClass", ComponentClass=_cls), "GetComponentByClass")
    _g.link(_pawn[0], _pawn[1], _found, "self")
    _valid = _g.call(_KSL, "IsValid")
    _g.link(_found, "ReturnValue", _valid, "Object")
    _has = _g.branch((_valid, "ReturnValue"))
    _link_exec(_last, _has)
    _as = _g.cast(_cls, (_found, "ReturnValue"))
    _get = lambda n: (_g.var(n, owner=_cls, target=_as), n)
    _line = _add_line([_name + " (kill credit): looks ", _num_str(_get("Looks")), "  hits ", _num_str(_get("Hits")),
                       "  marked ", _num_str((_g.array_call("Array_Length", _get("Marked"), "TargetArray"), "ReturnValue")),
                       "  kills ", _num_str(_get("Kills")), "  " + _what + " ", _num_str(_get("Extra")),
                       " (last ", _num_str(_get("LastBonus"), True), " health)" if _what not in ("cuts", "boosts", "cloaks") else " s)"])
    _g.flow((_has, "then"), _as[0], _line)
    _last = [(_has, "else"), (_line, "then")]
_g.row(900)
_watchers = _g.call(_GS, "GetAllActorsOfClass", ActorClass=WATCHER_CLASS)
_link_exec(_last, _watchers)
_n = _g.array_call("Array_Length", (_watchers, "OutActors"), "TargetArray")
_any = _g.branch(_math("Greater_IntInt", (_n, "ReturnValue"), 0))
_g.flow(_watchers, _any)
_none_line = _add_line(["Fire / poison watcher: not started"])
_g.flow((_any, "else"), _none_line)
_w = _g.cast(WATCHER_CLASS, _g.item_at((_watchers, "OutActors")))
_getw = lambda n: (_g.var(n, owner=WATCHER_CLASS, target=_w), n)
_w_line = _add_line(["Fire / poison watcher: looks ", _num_str(_getw("Ticks")), "  your tiers fire ", _num_str(_getw("LastFire")),
                     " poison ", _num_str(_getw("LastPoison")), "  mobs hurt ", _num_str(_getw("Hurt")),
                     " (last ", _num_str(_getw("LastHurt"), True), ")"])
_g.flow((_any, "then"), _w[0], _w_line)
# the player's artifact numbers (Artifact Amplifier should move them: damage and souls x1.2 / 1.35 / 1.5)
_pct = lambda v: _num_str(_math("Multiply_FloatFloat", v, 100.0), True)
_art_line = _add_line(["Your artifacts: damage x", _pct(_attribute(_pawn, _ITEM_SET, "ItemDamageMultiplier")),
                       "%  cooldown x", _pct(_attribute(_pawn, _ITEM_SET, "ItemCooldownMultiplier")),
                       "%  souls x", _pct(_attribute(_pawn, _ITEM_SET, "SoulGatheringMultiplier")), "%"])
_link_exec([(_none_line, "then"), (_w_line, "then")], _art_line)
_put = _g.call("/Script/UMG.TextBlock", "SetText")
_g.link(_g.var("Info"), "Info", _put, "self")
_as_text = _g.call("/Script/Engine.KismetTextLibrary", "Conv_StringToText")
_g.link(*(_v("Lines") + (_as_text, "InString")))
_g.link(_as_text, "ReturnValue", _put, "InText")
_g.flow(_art_line, _put)
compile_save(_debug_view, "debug readout")

# --- Battle Hardened's graph (the effects: further up) ---------------------------------------------------------------
_bp = blueprint(BARRIER, unreal.load_class(None, "/Script/Dungeons.Barrier"))
for _name, _kind in dict(Stacks="int", LastHit="float", Hits="int", Shots="int").items():
    check(LIB.add_variable(_bp, _name, _kind), "Battle Hardened: variable " + _name)
LIB.compile(_bp)
check(LIB.set_variable_default(_bp, "LastHit", "-100"), "Battle Hardened: LastHit default")
_g = Graph(_bp)


def _stack_limit():
    return HARDENED_STACKS


_WEARER = (_g.call(_COMPONENT, "GetOwner"), "ReturnValue")
_g.row(0)
_struck = _g.custom_event("Struck", "Mob=" + _ACTOR)
_authority = _g.call(_AC, "HasAuthority")
_g.link(_WEARER[0], _WEARER[1], _authority, "self")
_mob_char = _g.cast(_BASE, (_struck, "Mob"))
_me = _g.cast(_BASE, _WEARER)
_foe = _g.call(_MATH, "Not_PreBool")
_g.link(*(_same_team(_me, _mob_char) + (_foe, "A")))
_go = _g.branch(_math("BooleanAND", _math("BooleanAND", (_authority, "ReturnValue"), (_foe, "ReturnValue")),
                      _is_player(_WEARER)))
_g.flow(_struck, _mob_char[0], _me[0], _go)
_g.row(300)
_now = _g.call(_GS, "GetTimeSeconds")
_stale = _math("Greater_FloatFloat", _math("Subtract_FloatFloat", (_now, "ReturnValue"), _v("LastHit")), HARDENED_SECONDS)
_kept = _g.call(_MATH, "SelectInt", A=0)
_link_value(_v("Stacks"), _kept, "B")
_link_value(_stale, _kept, "bPickA")
_set_stacks = set_value(_g, "Stacks", _math("Min", _math("Add_IntInt", (_kept, "ReturnValue"), 1), _stack_limit()))
_set_hit = set_value(_g, "LastHit", (_now, "ReturnValue"))
_asc = _g.call(_GAS, "GetAbilitySystemComponent")
_g.link(_WEARER[0], _WEARER[1], _asc, "Actor")
_context = _g.call(_ASC, "MakeEffectContext")
_g.link(_asc, "ReturnValue", _context, "self")
_spec = _g.call(_ASC, "MakeOutgoingSpec", Level=1.0)
_g.link(_asc, "ReturnValue", _spec, "self")
_pick = _by_tier_and_copy(_hardened, _effect_class(BARRIER))
_g.link(_pick[0], _pick[1], _spec, "GameplayEffectClass")
_g.link(_context, "ReturnValue", _spec, "Context")
_timed = _g.call(_GAS, "AssignSetByCallerMagnitude", DataName="Duration", Magnitude=HARDENED_SECONDS)
_g.link(_spec, "ReturnValue", _timed, "SpecHandle")
_apply = _g.call(_ASC, "BP_ApplyGameplayEffectSpecToSelf")
_g.link(_asc, "ReturnValue", _apply, "self")
_g.link(_timed, "ReturnValue", _apply, "SpecHandle")
_g.flow(*([(_go, "then"), _set_stacks, _set_hit, _pick[0]] + _steps(_spec, _timed) + [_apply, _count("Hits")]))
# every shot fired adds a stack too (user, 2026-11-08; as Relentless)
_g.row(900)
_listen = _on_host_every(1.0, "Listen")
_g.row(1200)
_shot = _listen_shots(_WEARER, _listen, "Shot")
_shot_auth = _g.call(_AC, "HasAuthority")
_g.link(_WEARER[0], _WEARER[1], _shot_auth, "self")
_shot_ok = _g.branch(_math("BooleanAND", (_shot_auth, "ReturnValue"), _is_player(_WEARER)))
_g.flow(_shot, _shot_ok)
_now_s = _g.call(_GS, "GetTimeSeconds")
_stale_s = _math("Greater_FloatFloat", _math("Subtract_FloatFloat", (_now_s, "ReturnValue"), _v("LastHit")), HARDENED_SECONDS)
_kept_s = _g.call(_MATH, "SelectInt", A=0)
_link_value(_v("Stacks"), _kept_s, "B")
_link_value(_stale_s, _kept_s, "bPickA")
_set_stacks_s = set_value(_g, "Stacks", _math("Min", _math("Add_IntInt", (_kept_s, "ReturnValue"), 1), _stack_limit()))
_set_hit_s = set_value(_g, "LastHit", (_now_s, "ReturnValue"))
_asc_s = _g.call(_GAS, "GetAbilitySystemComponent")
_g.link(_WEARER[0], _WEARER[1], _asc_s, "Actor")
_context_s = _g.call(_ASC, "MakeEffectContext")
_g.link(_asc_s, "ReturnValue", _context_s, "self")
_spec_s = _g.call(_ASC, "MakeOutgoingSpec", Level=1.0)
_g.link(_asc_s, "ReturnValue", _spec_s, "self")
_pick_s = _by_tier_and_copy(_hardened, _effect_class(BARRIER))
_g.link(_pick_s[0], _pick_s[1], _spec_s, "GameplayEffectClass")
_g.link(_context_s, "ReturnValue", _spec_s, "Context")
_timed_s = _g.call(_GAS, "AssignSetByCallerMagnitude", DataName="Duration", Magnitude=HARDENED_SECONDS)
_g.link(_spec_s, "ReturnValue", _timed_s, "SpecHandle")
_apply_s = _g.call(_ASC, "BP_ApplyGameplayEffectSpecToSelf")
_g.link(_asc_s, "ReturnValue", _apply_s, "self")
_g.link(_timed_s, "ReturnValue", _apply_s, "SpecHandle")
_g.flow(*([(_shot_ok, "then"), _set_stacks_s, _set_hit_s, _pick_s[0]] + _steps(_spec_s, _timed_s) + [_apply_s, _count("Shots")]))
compile_save(_bp, "Battle Hardened (Barrier)")
_switch_off(BARRIER, {"AffectionRadius": 0.0}, "Barrier's own resistance off")


# --- Thorns -> Overload (user, 2026-11-08: Thorns replaced; lightning deals a share of max health, like fire and
# poison; as strong as Ignite / Venom Siphon; arrows too) ------------------------------------------------------------
# Lightning charges mobs for OVERLOAD_SECONDS: Thundering's strike (the mobs it reaches) and Electrified's zap (the
# zapped mob) - told by their cues (further down). Like Ignite on a burning mob: every hit of the wearer on a charged
# mob - a melee hit (the hit spark) or an arrow (one of the wearer's flying projectiles within ARROW_TOUCH of it, each
# arrow once) - discharges it: it and up to OVERLOAD_ARCS more hostile mobs within ARC_RADIUS take OVERLOAD of their
# max health (bosses BOSS_SHARE of it), boosted by Lightning Focus, and the arcs charge the mobs they reach (as
# Ignite's fire spreads). Each mob takes it at most once every BONUS_GAP s. A charge younger than OVERLOAD_MIN_AGE s
# came from this very hit's strike and waits for the next hit. Lightning damage (the game's colour). Thorns' own
# damage back is off (0 / 0 / 0); Thorns is off in the mob pool (MobPool.toml).
THORNS = "/Game/Components/Enchantments/Thorns/BP_Thorns"
OVERLOAD = (_num("overload_base", 0.02), _num("overload_per_tier", 0.01))     # 3 / 4 / 5% of max health
OVERLOAD_ARCS = (_num("overload_arcs_base", 2.0), _num("overload_arcs_per_tier", 1.0))   # 3 / 4 / 5 more mobs
OVERLOAD_SECONDS, ARC_RADIUS = _num("overload_seconds", 4.0), _num("arc_radius", 500.0)
OVERLOAD_MIN_AGE = 0.3
_body, _mob, _drop, _at, _wearer = measuring_host(THORNS, _D + "Thorns", "Overload",
                                                  dict(Charged="array:" + _ACTOR, ChargedAt="array:float",
                                                       Arcs="int", Focus="float", Charges="int",
                                                       ArrowHits="int"), arrows=True)


# the charge shows on the mob (user, 2026-11-08: a slight electric effect while charged): our effect for the charge's
# time, carrying the game's Electrified status look (the cue the game shows on an electrified character)
_charge_look = timed_effect("/Game/Components/Enchantments/Thorns/GE_SequelOverloadCharge", "Overload charge look", [])
_charge_asset = assets.load_asset("/Game/Components/Enchantments/Thorns/GE_SequelOverloadCharge")
check(LIB.set_default_property(_charge_asset, "GameplayCues",
                               '((GameplayCueTags=(GameplayTags=((TagName="GameplayCue.StatusEffect.Enchantment.Electrified")))))'),
      "Overload charge: the game's electrified look")
assets.save_loaded_asset(_charge_asset)


def _charge_one(mob, after):
    """From the exec (node, pin) after: mob (node, pin) charged now (again), its look on for the charge's time.
    Returns the exec (node, pin)s that end it."""
    asc, spec, spec_steps = timed_spec(_charge_look, _math("Add_FloatFloat", OVERLOAD_SECONDS, 0.0))
    theirs = _g.call(_GAS, "GetAbilitySystemComponent")
    _g.link(mob[0], mob[1], theirs, "Actor")
    show = _g.call(_ASC, "BP_ApplyGameplayEffectSpecToTarget")
    _g.link(asc[0], asc[1], show, "self")
    _g.link(spec[0], spec[1], show, "SpecHandle")
    _g.link(theirs, "ReturnValue", show, "Target")
    _g.flow(*([after] + spec_steps + [show]))
    after = (show, "then")
    now = _g.call(_GS, "GetTimeSeconds")
    known = _g.array_call("Array_Find", _v("Charged"), "TargetArray", ItemToFind=mob)
    again = _g.branch(_math("GreaterEqual_IntInt", (known, "ReturnValue"), 0))
    renew = _g.array_call("Array_Set", _v("ChargedAt"), "TargetArray", Index=(known, "ReturnValue"), Item=(now, "ReturnValue"))
    add_mob = _g.array_call("Array_Add", _v("Charged"), "TargetArray", NewItem=mob)
    add_time = _g.array_call("Array_Add", _v("ChargedAt"), "TargetArray", NewItem=(now, "ReturnValue"))
    one, two = _count("Charges"), _count("Charges")
    _g.flow(after, again)
    _g.flow((again, "then"), renew, one)
    _g.flow((again, "else"), add_mob, add_time, two)
    return [(one, "then"), (two, "then")]


def _discharge_from(mob, after, mob_at):
    """From the exec (node, pin) after: mob (node, pin; standing at mob_at, a location (node, pin)) discharges if its
    gap allows - it and up to OVERLOAD_ARCS hostile mobs within ARC_RADIUS take the share, and those get charged."""
    passed, _ = _gap_check(mob, after)
    plain = set_value(_g, "Arcs", 0)
    _link_exec(passed, plain)
    focused = _lightning_focus(_wearer, (plain, "then"))
    own = _lightning_share(mob, _own_share(OVERLOAD))
    hit_own = _deal(_wearer, mob, own, LIGHTNING_DAMAGE)
    _link_exec(focused, hit_own[0])
    told = _triggered()
    _g.flow(*(hit_own + [_count("Bonuses"), set_value(_g, "LastBonus", own), told]))
    abody, amob, _ = _hostile_mobs_near(mob_at, ARC_RADIUS, (told, "then"), skip=mob)
    arcs_f = _g.call(_MATH, "Conv_IntToFloat")
    _g.link(_g.var("Arcs"), "Arcs", arcs_f, "InInt")
    room = _g.branch(_math("Less_FloatFloat", (arcs_f, "ReturnValue"), _own_share(OVERLOAD_ARCS)))
    _g.flow(abody, room)
    apass, _ = _gap_check(amob, (room, "then"))
    arc = _lightning_share(amob, _own_share(OVERLOAD))
    hurt = _deal(_wearer, amob, arc, LIGHTNING_DAMAGE)
    _link_exec(apass, hurt[0])
    looks = _particle_at(_ARC_FX, amob)
    _g.flow(*(hurt + [_count("Arcs"), _count("Extra")] + looks))
    _charge_one(amob, (looks[-1], "then"))


# ChargeNear(Where, Radius): every hostile mob there is charged (again); the first one starts the arrow look
_g.row(2700)
_charge = _g.custom_event("ChargeNear", "Where=struct:/Script/CoreUObject.Vector;Radius=float")
_authority = _g.call(_AC, "HasAuthority")
_g.link(_wearer[0], _wearer[1], _authority, "self")
_on_host = _g.branch((_authority, "ReturnValue"))
_g.flow(_charge, _on_host)
_g.row(3000)
_cbody, _cmob, _ = _hostile_mobs_near((_charge, "Where"), (_charge, "Radius"), (_on_host, "then"))
_charge_one(_cmob, _cbody)

# a measured melee hit on a charged mob
_g.row(3600)
_dknown = _g.array_call("Array_Find", _v("Charged"), "TargetArray", ItemToFind=_mob)
_is_charged = _g.branch(_math("GreaterEqual_IntInt", (_dknown, "ReturnValue"), 0))
_dnow = _g.call(_GS, "GetTimeSeconds")
_age = _math("Subtract_FloatFloat", (_dnow, "ReturnValue"), _g.item_at(_v("ChargedAt"), (_dknown, "ReturnValue")))
_ready = _g.branch(_math("GreaterEqual_FloatFloat", _age, OVERLOAD_MIN_AGE))
_fresh = _g.branch(_math("LessEqual_FloatFloat", _age, OVERLOAD_SECONDS))
_g.flow(_body, _is_charged, _ready, _fresh)
# a charge run out: out of the lists (the time first - the index is found again for each removal)
_drop_t = _g.array_call("Array_Remove", _v("ChargedAt"), "TargetArray", IndexToRemove=(_dknown, "ReturnValue"))
_drop_m = _g.array_call("Array_Remove", _v("Charged"), "TargetArray", IndexToRemove=(_dknown, "ReturnValue"))
_g.flow((_fresh, "else"), _drop_t, _drop_m)
_g.row(3900)
_discharge_from(_mob, (_fresh, "then"), _at)

compile_save(_bp, "Overload (Thorns)")
_switch_off(THORNS, {"PercentDamageReturnedBase": 0.0, "PercentDamageReturnedPerLevel": 0.0,
                     "PercentDamageReturnedMob": 0.0}, "Thorns' own damage back off")


# --- Levitation Shot -> Relentless (user, 2026-11-08: a damage / attack-speed Battle Hardened) -----------------------
# Every hit of the wearer on any hostile mob - melee (the hit spark) or arrow (one of the wearer's flying projectiles
# within ARROW_TOUCH of a hostile mob, each arrow once; looked at every SPLASH_LOOK s) - adds a stack of RELENTLESS_DAMAGE
# melee and ranged damage and RELENTLESS_SPEED melee and ranged attack speed (added to the multipliers, before the
# others), lasting RELENTLESS_SECONDS (a new stack refreshes them all); 5 / 8 / 10 stacks at most (one effect per tier,
# its stack limit). Players only. Levitation Shot's own launch is off: no "ready" effect (Effect left empty), 0 launch /
# strength / fall damage. The game's class is BP_LevitationShot_C in package BP_levitationShot.
LEVITATION_SHOT = "/Game/Components/Enchantments/LevitationShot/BP_levitationShot"
# 10 stacks at every tier; per stack +2 / 3 / 4% damage and the same attack speed by tier; copies add (as Battle
# Hardened; user, 2026-11-08)
RELENTLESS_DAMAGE = (_num("relentless_damage_base", 0.01), _num("relentless_damage_per_tier", 0.01))
RELENTLESS_SPEED = (_num("relentless_speed_base", 0.01), _num("relentless_speed_per_tier", 0.01))
RELENTLESS_SECONDS, RELENTLESS_STACKS = _num("relentless_seconds", 3.0), HARDENED_STACKS
_MELEE_SET, _RANGED_SET = "/Script/Dungeons.MeleeAttributeSet", "/Script/Dungeons.RangedAttributeSet"


def _relentless_mods(t):
    dmg, spd = RELENTLESS_DAMAGE[0] + RELENTLESS_DAMAGE[1] * t, RELENTLESS_SPEED[0] + RELENTLESS_SPEED[1] * t
    return [(_MELEE_SET, "MeleeAttackDamageMultiplier", _ADD, dmg), (_RANGED_SET, "RangedAttackDamageMultipler", _ADD, dmg),
            (_MELEE_SET, "MeleeAttackSpeedMultiplier", _ADD, spd), (_RANGED_SET, "RangedAttackSpeedMultiplier", _ADD, spd)]


_relentless = stacking_effects("/Game/Components/Enchantments/LevitationShot", "Relentless", _relentless_mods,
                               ("Relentless", "/Game/Components/Enchantments/LevitationShot/T_LevitationShot_Icon"), RELENTLESS_STACKS)

_bp = blueprint(LEVITATION_SHOT, unreal.load_class(None, _D + "LevitationRanged"))
for _name, _kind in dict(Hits="int", ArrowHits="int", Looks="int").items():
    check(LIB.add_variable(_bp, _name, _kind), "Relentless: variable " + _name)
LIB.compile(_bp)
_g = Graph(_bp)
_WEARER = (_g.call(_COMPONENT, "GetOwner"), "ReturnValue")


def _relentless_stack(after):
    """From the exec (node, pin) after: one more stack of the tier's effect on the wearer. Returns the last node."""
    asc = _g.call(_GAS, "GetAbilitySystemComponent")
    _g.link(_WEARER[0], _WEARER[1], asc, "Actor")
    context = _g.call(_ASC, "MakeEffectContext")
    _g.link(asc, "ReturnValue", context, "self")
    spec = _g.call(_ASC, "MakeOutgoingSpec", Level=1.0)
    _g.link(asc, "ReturnValue", spec, "self")
    pick = _by_tier_and_copy(_relentless, _effect_class(LEVITATION_SHOT))
    _g.link(pick[0], pick[1], spec, "GameplayEffectClass")
    _g.link(context, "ReturnValue", spec, "Context")
    timed = _g.call(_GAS, "AssignSetByCallerMagnitude", DataName="Duration", Magnitude=RELENTLESS_SECONDS)
    _g.link(spec, "ReturnValue", timed, "SpecHandle")
    apply = _g.call(_ASC, "BP_ApplyGameplayEffectSpecToSelf")
    _g.link(asc, "ReturnValue", apply, "self")
    _g.link(timed, "ReturnValue", apply, "SpecHandle")
    steps = [pick[0]] + _steps(spec, timed) + [apply]
    _g.flow(*([after] + steps))
    return apply


# Struck(mob): a melee hit
_g.row(0)
_struck = _g.custom_event("Struck", "Mob=" + _ACTOR)
_authority = _g.call(_AC, "HasAuthority")
_g.link(_WEARER[0], _WEARER[1], _authority, "self")
_mob_char = _g.cast(_BASE, (_struck, "Mob"))
_me = _g.cast(_BASE, _WEARER)
_foe = _g.call(_MATH, "Not_PreBool")
_g.link(*(_same_team(_me, _mob_char) + (_foe, "A")))
_go = _g.branch(_math("BooleanAND", _math("BooleanAND", (_authority, "ReturnValue"), (_foe, "ReturnValue")),
                      _is_player(_WEARER)))
_g.flow(_struck, _mob_char[0], _me[0], _go)
_g.row(300)
_g.flow(_relentless_stack((_go, "then")), _count("Hits"))
# Look: the wearer's arrows touching a hostile mob
_host = _on_host_every(1.0, "Look")   # binds the shot listener (again: binding twice keeps one)
_g.row(900)
_player = _g.branch(_is_player(_WEARER))
_g.flow(_host, _count("Looks"), _player)


# every shot fired adds a stack (user, 2026-11-08: ranged on the shot is fine - ammo is limited; melee stays on hits,
# so swinging at the air gives nothing)
_g.row(1500)
_shot = _listen_shots(_WEARER, (_player, "then"), "Shot")
_shot_auth = _g.call(_AC, "HasAuthority")
_g.link(_WEARER[0], _WEARER[1], _shot_auth, "self")
_shot_ok = _g.branch(_math("BooleanAND", (_shot_auth, "ReturnValue"), _is_player(_WEARER)))
_g.flow(_shot, _shot_ok)
_g.flow(_relentless_stack((_shot_ok, "then")), _count("ArrowHits"))
compile_save(_bp, "Relentless (Levitation Shot)")
_switch_off(LEVITATION_SHOT, {"LaunchStrength": 0.0, "EffectStrength": 0.0, "FallDamagePercentagePerLevel": 0.0},
            "Levitation Shot's own launch off")
# its "ready" effect, applied by the game on every roll, must exist (left empty, a roll crashed the game - user,
# 2026-11-08; the dump: the game's roll handler exe+0xA6C460 makes a spec of it, exe+0x7B07E0 reads the empty class):
# our child of the game's LevitationReadyGameplayEffect, with nothing in it
_READY = "/Game/Components/Enchantments/LevitationShot/GE_SequelLevitationReady"
compile_save(blueprint(_READY, unreal.load_class(None, _D + "LevitationReadyGameplayEffect")), "Relentless: empty ready effect")
_lev = assets.load_asset(LEVITATION_SHOT)
check(LIB.set_default_property(_lev, "Effect", "BlueprintGeneratedClass'%s.GE_SequelLevitationReady_C'" % _READY),
      "Levitation Shot's ready effect = ours (does nothing)")
assets.save_loaded_asset(_lev)
_cdo = unreal.get_default_object(assets.load_blueprint_class(LEVITATION_SHOT))
check(_cdo.get_editor_property("Effect") is not None, "Levitation Shot's ready effect is set")


# --- the melee hit spark: the hook of Sweeping Edge, Ignite, Venom Siphon and Shatter -------------------------------
# The game plays GameplayCue.Hit.Melee on every mob a melee swing hits; its handler /Game/Cues/HitCues/
# BP_HitMeleeNotifyStatic only spawns P_Hit_Generic at the mob (read 2026-11-06). Ours, at the same path, overrides
# the same OnExecute (the game's static cue base calls that - the general K2_HandleGameplayCue never ran), spawns the
# same spark (linked through a placeholder - nothing of the game's is copied), starts the status watcher if the mission
# has none, and for every player within SPLASH_HITTER_RANGE of the mob calls Struck(mob) on each of our hit
# enchantments the player wears (Sweeping Edge also spawns the game's Shockwave impact at the mob) - the enchantment
# measures the hit and does its thing (above). The cue's parameters carry no hitter and no damage (seen in game,
# 2026-11-07), hence the range test: in co-op two wearers near one mob both count it.
HIT_CUE = "/Game/Cues/HitCues/BP_HitMeleeNotifyStatic"
HIT_SPARK = "/Game/Effects/ParticleSystems/Combat/P_Hit_Generic.P_Hit_Generic"
SHOCKWAVE_LOOK = "/Game/Components/Enchantments/Shockwave/PS_Shockwave_Impact.PS_Shockwave_Impact"
HIT_ENCHANTMENTS = [KNOCKBACK_CLASS] + [p + "." + p.rsplit("/", 1)[1] + "_C"
                                        for p in (EMERALD_DIVINATION, ALTRUISTIC, CHARGING_ACCELERATION,
                                                  LEECHING, REFRESHMENT, SHOCKWAVE, SWIRLING, EXPLODING,
                                                  THUNDERING, SPONGE_STRIKE, RAMPAGING, REFRESHMENT_RANGED, GUARDING_STRIKE,
                                                  BARRIER, THORNS, LEVITATION_SHOT)]
# Told on their first copy only: Shockwave / Swirling / Thundering already act on every copy's wave / spin / strike
# (each copy makes its own), and Overload keeps one set of charges.
FIRST_COPY_ONLY = [_effect_class(p) for p in (SHOCKWAVE, SWIRLING, THUNDERING, THORNS)]
remove("/Game/Components/Enchantments/Knockback/WBP_SequelHitTest")   # the test line (2026-11-07)

_spark_fx = game_particle(HIT_SPARK.split(".")[0])
_look_fx = game_particle(SHOCKWAVE_LOOK.split(".")[0])
_bp = blueprint(HIT_CUE, unreal.load_class(None, "/Script/Dungeons.DungeonsGameplayCueNotify_Static"))
LIB.compile(_bp)
_g = Graph(_bp, "OnExecute")


def terminals(bp, graph_name):
    """The entry and result nodes of an override graph (made by its first node)."""
    import re
    text = LIB.export_nodes(bp, graph_name)
    found = dict(re.findall(r'Class=/Script/BlueprintGraph\.K2Node_Function(Entry|Result) Name="([^"]+)"', text))
    check("Entry" in found, graph_name + " entry")
    return found.get("Entry"), found.get("Result")


_g.row(0)
_first_node = _g.call(_MATH, "Not_PreBool")   # makes the override graph
_cue, _cue_result = terminals(_bp, "OnExecute")
_TARGET = (_cue, "MyTarget")
_spark = _particle_at(_spark_fx, _TARGET)
_g.flow(_cue, *_spark)
_watching, _had_one = _ensure_watcher(_TARGET, (_spark[-1], "then"))

_g.row(300)
_heroes = _g.call("/Script/Engine.GameplayStatics", "GetAllActorsOfClass", ActorClass="/Script/Dungeons.PlayerCharacter")
if "WorldContextObject" in _g.pins(_heroes):
    _g.link(_TARGET[0], _TARGET[1], _heroes, "WorldContextObject")
_last = _g.array_call("Array_LastIndex", (_heroes, "OutActors"), "TargetArray")
_loop = _g.macro("ForLoop", FirstIndex=0)
_g.link(_last, "ReturnValue", _loop, "LastIndex")
_hero = _g.item_at((_heroes, "OutActors"), (_loop, "Index"))
# the spawn's "then" when there was no watcher; the branch's "else" when there was one
_g.link(_watching, "then", _heroes, "execute")
_g.link(_had_one, "else", _heroes, "execute")
_g.flow(_heroes, _loop)
_close = _g.call("/Script/Engine.Actor", "GetDistanceTo")
_g.link(_hero[0], _hero[1], _close, "self")
_g.link(_TARGET[0], _TARGET[1], _close, "OtherActor")
_near = _math("LessEqual_FloatFloat", (_close, "ReturnValue"), SPLASH_HITTER_RANGE)
_into = [((_loop, "LoopBody"))]
for _cls in HIT_ENCHANTMENTS:
    _g.row(600 + 300 * HIT_ENCHANTMENTS.index(_cls))
    if _cls in FIRST_COPY_ONLY:
        _found = _g.call("/Script/Engine.Actor", "GetComponentByClass", ComponentClass=_cls)
        _g.link(_hero[0], _hero[1], _found, "self")
        _wears = _g.call("/Script/Engine.KismetSystemLibrary", "IsValid")
        _g.link(_found, "ReturnValue", _wears, "Object")
        _is_wearer = _g.branch(_math("BooleanAND", (_wears, "ReturnValue"), _near))
        _link_exec(_into, _is_wearer)
        _wearing = _g.cast(_cls, (_found, "ReturnValue"))
        _tell = _g.call(_cls, "Struck")
        _g.link(_wearing[0], _wearing[1], _tell, "self")
        _g.link(_TARGET[0], _TARGET[1], _tell, "Mob")
        _chain = [_wearing[0], _tell]
        _g.flow(*([(_is_wearer, "then")] + _chain))
        _into = [(_is_wearer, "else"), (_chain[-1], "then")]
        continue
    # every copy the hero wears is told (user rule: a bonus copy of a picked enchantment is never wasted)
    _copies = _pure(_g.call(_AC, "GetComponentsByClass", ComponentClass=_cls), "GetComponentsByClass")
    _g.link(_hero[0], _hero[1], _copies, "self")
    _how_many = _g.array_call("Array_Length", (_copies, "ReturnValue"), "TargetArray")
    _is_wearer = _g.branch(_math("BooleanAND", _math("Greater_IntInt", (_how_many, "ReturnValue"), 0), _near))
    _link_exec(_into, _is_wearer)
    _cloop, _copy, _ = _loop_over((_copies, "ReturnValue"), (_is_wearer, "then"))
    _wearing = _g.cast(_cls, _copy)
    _tell = _g.call(_cls, "Struck")
    _g.link(_wearing[0], _wearing[1], _tell, "self")
    _g.link(_TARGET[0], _TARGET[1], _tell, "Mob")
    _g.flow((_cloop, "LoopBody"), _wearing[0], _tell)
    _after = [(_cloop, "Completed")]
    if _cls == KNOCKBACK_CLASS:
        _look = _particle_at(_look_fx, _TARGET)
        _g.flow(*([(_cloop, "Completed")] + _look))
        _after = [(_look[-1], "then")]
    _into = [(_is_wearer, "else")] + _after
compile_save(_bp, "melee hit spark (hook of Sweeping Edge, Ignite, Venom Siphon, Shatter)")
check(LIB.set_default_property(_bp, "GameplayCueTag", '(TagName="GameplayCue.Hit.Melee")'), "cue tag")
check(LIB.set_default_property(_bp, "GameplayCueName", "GameplayCue.Hit.Melee"), "cue name")
assets.save_loaded_asset(_bp)

def _overload_charge(hero, where, radius, reach=None):
    """In a cue's hero loop: ChargeNear(where, radius) on hero's (node, pin) Overload (first copy), if they wear one
    within SPLASH_HITTER_RANGE of where. Returns the first node (its exec input is the step in)."""
    cls = _effect_class(THORNS)
    has = _pure(_g.call(_AC, "GetComponentByClass", ComponentClass=cls), "GetComponentByClass")
    _g.link(hero[0], hero[1], has, "self")
    valid = _g.call(_KSL, "IsValid")
    _g.link(has, "ReturnValue", valid, "Object")
    at = _g.call(_AC, "K2_GetActorLocation")
    _g.link(hero[0], hero[1], at, "self")
    gap = _g.call(_MATH, "Vector_Distance")
    _g.link(at, "ReturnValue", gap, "V1")
    _g.link(where[0], where[1], gap, "V2")
    wears = _g.branch(_math("BooleanAND", (valid, "ReturnValue"),
                            _math("LessEqual_FloatFloat", (gap, "ReturnValue"), reach or SPLASH_HITTER_RANGE)))
    as_ = _g.cast(cls, (has, "ReturnValue"))
    tell = _g.call(cls, "ChargeNear", Radius=radius)
    _g.link(as_[0], as_[1], tell, "self")
    _g.link(where[0], where[1], tell, "Where")
    _g.flow((wears, "then"), as_[0], tell)
    return wears


# Thundering's strike cue: as the game's (the impact and sound at the strike's location, read 2026-11-08), plus
# Strike(location) on the Thundering of every player within SPLASH_HITTER_RANGE of it that wears one
_thunder_fx = game_particle(THUNDER_FX.split(".")[0])
assets.save_loaded_asset(fresh(THUNDER_SOUND, unreal.SoundCue, unreal.SoundCueFactoryNew()))
placeholder(THUNDER_SOUND)
_bp = blueprint(THUNDER_CUE, unreal.load_class(None, "/Script/Dungeons.DungeonsGameplayCueNotify_Static"))
LIB.compile(_bp)
_g = Graph(_bp, "OnExecute")
_g.row(0)
_g.call(_MATH, "Not_PreBool")   # makes the override graph
_cue, _ = terminals(_bp, "OnExecute")
_TARGET = (_cue, "MyTarget")
_params = _g.call(_GAS, "BreakGameplayCueParameters")
_g.link(_cue, "Parameters", _params, "Parameters")
_fx = _g.call(_GS, "SpawnEmitterAtLocation", EmitterTemplate=_thunder_fx)
if "WorldContextObject" in _g.pins(_fx):
    _g.link(_TARGET[0], _TARGET[1], _fx, "WorldContextObject")
_g.link(_params, "Location", _fx, "Location")
_noise = _g.call(_GS, "SpawnSoundAtLocation", Sound=THUNDER_SOUND + "." + THUNDER_SOUND.rsplit("/", 1)[1])
if "WorldContextObject" in _g.pins(_noise):
    _g.link(_TARGET[0], _TARGET[1], _noise, "WorldContextObject")
_g.link(_params, "Location", _noise, "Location")
_g.flow(_cue, _fx, _noise)
_g.row(300)
_heroes = _g.call(_GS, "GetAllActorsOfClass", ActorClass="/Script/Dungeons.PlayerCharacter")
if "WorldContextObject" in _g.pins(_heroes):
    _g.link(_TARGET[0], _TARGET[1], _heroes, "WorldContextObject")
_g.flow(_noise, _heroes)
_loop, _hero, _ = _loop_over((_heroes, "OutActors"), (_heroes, "then"))
_THUNDER_CLASS = _effect_class(THUNDERING)
_has = _pure(_g.call(_AC, "GetComponentByClass", ComponentClass=_THUNDER_CLASS), "GetComponentByClass")
_g.link(_hero[0], _hero[1], _has, "self")
_valid = _g.call(_KSL, "IsValid")
_g.link(_has, "ReturnValue", _valid, "Object")
_hero_at = _g.call(_AC, "K2_GetActorLocation")
_g.link(_hero[0], _hero[1], _hero_at, "self")
_gap = _g.call(_MATH, "Vector_Distance")
_g.link(_hero_at, "ReturnValue", _gap, "V1")
_g.link(_params, "Location", _gap, "V2")
_wears = _g.branch(_math("BooleanAND", (_valid, "ReturnValue"),
                         _math("LessEqual_FloatFloat", (_gap, "ReturnValue"), SPLASH_HITTER_RANGE)))
_as = _g.cast(_THUNDER_CLASS, (_has, "ReturnValue"))
_tell = _g.call(_THUNDER_CLASS, "Strike")
_g.link(_as[0], _as[1], _tell, "self")
_g.link(_params, "Location", _tell, "Where")
_g.flow((_loop, "LoopBody"), _wears)
_g.flow((_wears, "then"), _as[0], _tell)
_g.row(600)
_charges = _overload_charge(_hero, (_params, "Location"), STRIKE_REACH)
_link_exec([(_wears, "else"), (_tell, "then"), (_as[0], "CastFailed")], _charges)
compile_save(_bp, "Thundering's strike cue")
check(LIB.set_default_property(_bp, "GameplayCueTag", '(TagName="GameplayCue.Trigger.Enchantment.Thundering.Strike")'), "cue tag")
check(LIB.set_default_property(_bp, "GameplayCueName", "GameplayCue.Trigger.Enchantment.Thundering.Strike"), "cue name")
assets.save_loaded_asset(_bp)

# Electrified's receiver cue (on every zapped character): as the game's - its impact and its chain on the target,
# the chain's end at the cue's location (read in its asset's imports, 2026-11-08) - plus Zapped(mob) on the
# Electrified of every player within SPLASH_HITTER_RANGE that wears one, and the zapped mob charged for Overload
ELEC_CUE = "/Game/Cues/Enchantments/BP_ElectrifiedRecieverNotifyStatic"
_elec_impact = game_particle("/Game/Components/Enchantments/Electrified/PS_ElectrifiedImpact")
_elec_chain = game_particle("/Game/Components/Enchantments/Electrified/PS_ElectrifiedChain")
_bp = blueprint(ELEC_CUE, unreal.load_class(None, "/Script/Dungeons.DungeonsGameplayCueNotify_Static"))
LIB.compile(_bp)
_g = Graph(_bp, "OnExecute")
_g.row(0)
_g.call(_MATH, "Not_PreBool")   # makes the override graph
_cue, _ = terminals(_bp, "OnExecute")
_TARGET = (_cue, "MyTarget")
_params = _g.call(_GAS, "BreakGameplayCueParameters")
_g.link(_cue, "Parameters", _params, "Parameters")
_root = _g.call(_AC, "K2_GetRootComponent")
_g.link(_TARGET[0], _TARGET[1], _root, "self")
_fx = _g.call(_GS, "SpawnEmitterAttached", EmitterTemplate=_elec_impact)
_g.link(_root, "ReturnValue", _fx, "AttachToComponent")
_chain = _g.call(_GS, "SpawnEmitterAttached", EmitterTemplate=_elec_chain)
_g.link(_root, "ReturnValue", _chain, "AttachToComponent")
_beam = _g.call("/Script/Engine.ParticleSystemComponent", "SetBeamTargetPoint", EmitterIndex=0, TargetIndex=0)
_g.link(_chain, "ReturnValue", _beam, "self")
_g.link(_params, "Location", _beam, "NewTargetPoint")
_g.flow(_cue, _fx, _chain, _beam)
_g.row(300)
_heroes = _g.call(_GS, "GetAllActorsOfClass", ActorClass="/Script/Dungeons.PlayerCharacter")
if "WorldContextObject" in _g.pins(_heroes):
    _g.link(_TARGET[0], _TARGET[1], _heroes, "WorldContextObject")
_g.flow(_beam, _heroes)
_loop, _hero, _ = _loop_over((_heroes, "OutActors"), (_heroes, "then"))
_ELEC_CLASS = _effect_class(ELECTRIFIED)
_has = _pure(_g.call(_AC, "GetComponentByClass", ComponentClass=_ELEC_CLASS), "GetComponentByClass")
_g.link(_hero[0], _hero[1], _has, "self")
_valid = _g.call(_KSL, "IsValid")
_g.link(_has, "ReturnValue", _valid, "Object")
_close = _g.call(_AC, "GetDistanceTo")
_g.link(_hero[0], _hero[1], _close, "self")
_g.link(_TARGET[0], _TARGET[1], _close, "OtherActor")
_wears = _g.branch(_math("BooleanAND", (_valid, "ReturnValue"),
                         _math("LessEqual_FloatFloat", (_close, "ReturnValue"), SPLASH_HITTER_RANGE)))
_as = _g.cast(_ELEC_CLASS, (_has, "ReturnValue"))
_tell = _g.call(_ELEC_CLASS, "Zapped")
_g.link(_as[0], _as[1], _tell, "self")
_g.link(_TARGET[0], _TARGET[1], _tell, "Mob")
_g.flow((_loop, "LoopBody"), _wears)
_g.flow((_wears, "then"), _as[0], _tell)
_g.row(600)
_where = _g.call(_AC, "K2_GetActorLocation")
_g.link(_TARGET[0], _TARGET[1], _where, "self")
_charges = _overload_charge(_hero, (_where, "ReturnValue"), 60.0)
_link_exec([(_wears, "else"), (_tell, "then"), (_as[0], "CastFailed")], _charges)
compile_save(_bp, "Electrified's receiver cue")
check(LIB.set_default_property(_bp, "GameplayCueTag", '(TagName="GameplayCue.Trigger.Enchantment.Electrified.Reciever")'), "cue tag")
check(LIB.set_default_property(_bp, "GameplayCueName", "GameplayCue.Trigger.Enchantment.Electrified.Reciever"), "cue name")
assets.save_loaded_asset(_bp)

# Shock Web's hit cue (on every character a beam hurts): as the game's - its hit look and sound at the target (read in
# its asset's imports, 2026-11-12) - plus Zapped(mob) on the Shock Web of every player within SHOCK_REACH that wears
# one, and the mob charged for Overload (same reach: a web can be far from its archer)
SHOCK_HIT_CUE = "/Game/Cues/HitCues/BP_HitShockwebNotifyStatic"
SHOCK_HIT_SOUND = "/Game/AudioForce/D4/04_playback_soundCue/sfx_enchantment_shockWebNotifyStatic"
_shock_fx = game_particle("/Game/Content_DLC4/Components/Enchantments/ShockWeb/PS_ShockwebHit")
assets.save_loaded_asset(fresh(SHOCK_HIT_SOUND, unreal.SoundCue, unreal.SoundCueFactoryNew()))
placeholder(SHOCK_HIT_SOUND)
_bp = blueprint(SHOCK_HIT_CUE, unreal.load_class(None, "/Script/Dungeons.DungeonsGameplayCueNotify_Static"))
LIB.compile(_bp)
_g = Graph(_bp, "OnExecute")
_g.row(0)
_g.call(_MATH, "Not_PreBool")   # makes the override graph
_cue, _ = terminals(_bp, "OnExecute")
_TARGET = (_cue, "MyTarget")
_where = _g.call(_AC, "K2_GetActorLocation")
_g.link(_TARGET[0], _TARGET[1], _where, "self")
_fx = _g.call(_GS, "SpawnEmitterAtLocation", EmitterTemplate=_shock_fx)
if "WorldContextObject" in _g.pins(_fx):
    _g.link(_TARGET[0], _TARGET[1], _fx, "WorldContextObject")
_g.link(_where, "ReturnValue", _fx, "Location")
_noise = _g.call(_GS, "SpawnSoundAtLocation", Sound=SHOCK_HIT_SOUND + "." + SHOCK_HIT_SOUND.rsplit("/", 1)[1])
if "WorldContextObject" in _g.pins(_noise):
    _g.link(_TARGET[0], _TARGET[1], _noise, "WorldContextObject")
_g.link(_where, "ReturnValue", _noise, "Location")
_g.flow(_cue, _fx, _noise)
_g.row(300)
_heroes = _g.call(_GS, "GetAllActorsOfClass", ActorClass="/Script/Dungeons.PlayerCharacter")
if "WorldContextObject" in _g.pins(_heroes):
    _g.link(_TARGET[0], _TARGET[1], _heroes, "WorldContextObject")
_g.flow(_noise, _heroes)
_loop, _hero, _ = _loop_over((_heroes, "OutActors"), (_heroes, "then"))
_WEB_CLASS = _effect_class(SHOCK_WEB)
_has = _pure(_g.call(_AC, "GetComponentByClass", ComponentClass=_WEB_CLASS), "GetComponentByClass")
_g.link(_hero[0], _hero[1], _has, "self")
_valid = _g.call(_KSL, "IsValid")
_g.link(_has, "ReturnValue", _valid, "Object")
_close = _g.call(_AC, "GetDistanceTo")
_g.link(_hero[0], _hero[1], _close, "self")
_g.link(_TARGET[0], _TARGET[1], _close, "OtherActor")
_wears = _g.branch(_math("BooleanAND", (_valid, "ReturnValue"),
                         _math("LessEqual_FloatFloat", (_close, "ReturnValue"), SHOCK_REACH)))
_as = _g.cast(_WEB_CLASS, (_has, "ReturnValue"))
_tell = _g.call(_WEB_CLASS, "Zapped")
_g.link(_as[0], _as[1], _tell, "self")
_g.link(_TARGET[0], _TARGET[1], _tell, "Mob")
_g.flow((_loop, "LoopBody"), _wears)
_g.flow((_wears, "then"), _as[0], _tell)
_g.row(600)
_charges = _overload_charge(_hero, (_where, "ReturnValue"), 60.0, SHOCK_REACH)
_link_exec([(_wears, "else"), (_tell, "then"), (_as[0], "CastFailed")], _charges)
compile_save(_bp, "Shock Web's hit cue")
check(LIB.set_default_property(_bp, "GameplayCueTag", '(TagName="GameplayCue.Hit.Shockweb")'), "cue tag")
check(LIB.set_default_property(_bp, "GameplayCueName", "GameplayCue.Hit.Shockweb"), "cue name")
assets.save_loaded_asset(_bp)


# Exploding: the game's Exploding still showed its purple blast at the corpse a moment later, with no damage (user,
# 2026-11-08): its code plays the cue GameplayCue.Trigger.Enchantment.Explode (BP_ExplodeNotifyStatic: PS_EnchantedExplosion,
# the generic explode sound, a rumble) on its own. Only the Exploding enchantment uses that cue (no mob rolls Exploding),
# so ours at the same path does nothing; our instant explosion above shows that look instead.
EXPLODE_CUE = "/Game/Cues/Enchantments/BP_ExplodeNotifyStatic"
_bp = blueprint(EXPLODE_CUE, unreal.load_class(None, "/Script/Dungeons.DungeonsGameplayCueNotify_Static"))
LIB.compile(_bp)
_g = Graph(_bp, "OnExecute")
_g.row(0)
_g.call(_MATH, "Not_PreBool")   # makes the override graph
# the editor wires the entry to a call of the game's own cue (the parent); straight to the end instead
_cue, _end = terminals(_bp, "OnExecute")
_g.flow(_cue, _end)
import re as _re
for _parent in _re.findall(r'Class=/Script/BlueprintGraph\.K2Node_CallParentFunction Name="([^"]+)"',
                           LIB.export_nodes(_bp, "OnExecute")):
    # left out of the flow (never runs), but the compiler wants its by-ref inputs wired
    _g.link(_cue, "MyTarget", _parent, "MyTarget")
    _g.link(_cue, "Parameters", _parent, "Parameters")
compile_save(_bp, "Exploding's delayed cue (silent)")
check(LIB.set_default_property(_bp, "GameplayCueTag", '(TagName="GameplayCue.Trigger.Enchantment.Explode")'), "cue tag")
check(LIB.set_default_property(_bp, "GameplayCueName", "GameplayCue.Trigger.Enchantment.Explode"), "cue name")
assets.save_loaded_asset(_bp)

# Overload: the game's Thorns still played its spikes and sound on every hit taken (no damage - ours sets it to 0; user,
# 2026-11-08). Its cue GameplayCue.Trigger.Enchantment.Thorns (BP_ThornsRecieverNotifyStatic: PS_Thorns_Reciever /
# PS_Thorns_User, the thorns sound) - ours at that path does nothing. (The Ancient Guardian's own thorns may use it
# too: its look goes, its damage stays.)
THORNS_CUE = "/Game/Cues/Enchantments/BP_ThornsRecieverNotifyStatic"
_bp = blueprint(THORNS_CUE, unreal.load_class(None, "/Script/Dungeons.DungeonsGameplayCueNotify_Static"))
LIB.compile(_bp)
_g = Graph(_bp, "OnExecute")
_g.row(0)
_g.call(_MATH, "Not_PreBool")   # makes the override graph
_cue, _end = terminals(_bp, "OnExecute")
_g.flow(_cue, _end)
for _parent in _re.findall(r'Class=/Script/BlueprintGraph\.K2Node_CallParentFunction Name="([^"]+)"',
                           LIB.export_nodes(_bp, "OnExecute")):
    _g.link(_cue, "MyTarget", _parent, "MyTarget")
    _g.link(_cue, "Parameters", _parent, "Parameters")
compile_save(_bp, "Thorns' cue (silent)")
check(LIB.set_default_property(_bp, "GameplayCueTag", '(TagName="GameplayCue.Trigger.Enchantment.Thorns")'), "cue tag")
check(LIB.set_default_property(_bp, "GameplayCueName", "GameplayCue.Trigger.Enchantment.Thorns"), "cue name")
assets.save_loaded_asset(_bp)

# the spin's cue: as the game's, plus Swirled on the wearer's Swirling
_swirl_fx = game_particle(SWIRL_FX.split(".")[0])
_sound = fresh(SWIRL_SOUND, unreal.SoundCue, unreal.SoundCueFactoryNew())
assets.save_loaded_asset(_sound)
placeholder(SWIRL_SOUND)
_bp = blueprint(SWIRL_CUE, unreal.load_class(None, "/Script/Dungeons.DungeonsGameplayCueNotify_Static"))
LIB.compile(_bp)
_g = Graph(_bp, "OnExecute")
_g.row(0)
_g.call(_MATH, "Not_PreBool")   # makes the override graph
_cue, _ = terminals(_bp, "OnExecute")
_TARGET = (_cue, "MyTarget")
_params = _g.call(_GAS, "BreakGameplayCueParameters")
_g.link(_cue, "Parameters", _params, "Parameters")
_size = _g.call(_MATH, "Conv_FloatToVector")
_link_value(_math("Divide_FloatFloat", (_params, "RawMagnitude"), 300.0), _size, "InFloat")
_root = _g.call(_AC, "K2_GetRootComponent")
_g.link(_TARGET[0], _TARGET[1], _root, "self")
_fx = _g.call(_GS, "SpawnEmitterAttached", EmitterTemplate=_swirl_fx)
_g.link(_root, "ReturnValue", _fx, "AttachToComponent")
_g.link(_size, "ReturnValue", _fx, "Scale")
_noise = _g.call(_GS, "SpawnSoundAttached", Sound=SWIRL_SOUND + "." + SWIRL_SOUND.rsplit("/", 1)[1])
_g.link(_root, "ReturnValue", _noise, "AttachToComponent")
_g.flow(_cue, _fx, _noise)
_g.row(300)
_SWIRL_CLASS = _effect_class(SWIRLING)
_has_swirl = _pure(_g.call(_AC, "GetComponentByClass", ComponentClass=_SWIRL_CLASS), "GetComponentByClass")
_g.link(_TARGET[0], _TARGET[1], _has_swirl, "self")
_valid = _g.call(_KSL, "IsValid")
_g.link(_has_swirl, "ReturnValue", _valid, "Object")
_wears = _g.branch((_valid, "ReturnValue"))
_as = _g.cast(_SWIRL_CLASS, (_has_swirl, "ReturnValue"))
_tell = _g.call(_SWIRL_CLASS, "Swirled")
_g.link(_as[0], _as[1], _tell, "self")
_g.link(_params, "RawMagnitude", _tell, "Radius")
_g.flow(_noise, _wears)
_g.flow((_wears, "then"), _as[0], _tell)
compile_save(_bp, "Swirling's spin cue")
check(LIB.set_default_property(_bp, "GameplayCueTag", '(TagName="GameplayCue.Trigger.Enchantment.Swirling")'), "cue tag")
check(LIB.set_default_property(_bp, "GameplayCueName", "GameplayCue.Trigger.Enchantment.Swirling"), "cue name")
assets.save_loaded_asset(_bp)
