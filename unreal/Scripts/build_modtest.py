"""Test build: does the map read the game's Daily Trials lists - can our blueprint change a trial's modifiers?

Writing the mission's modifier list directly (GameBP.mReplicatableAffectorsRules) crashed the game: it keeps its own
list of active modifiers that only its own setup builds. Trials are set up by the game itself when the mission loads.

The transmog as usual, plus BP_SequelModTest, which the loader also starts. In camp:
    every 3 s a text at the top left lists the game's trials (GameBP.mTrialDefs): each one's ID, type, modifiers
    (key=value, the format the game uses) and rewards;
    1 s after camp loads it gives the first trial (trial I on the map) one more modifier, MobSpeed=1.5, in the
    mission's list (then OnRep_TrialDefs) and in the game's store of the server's trials (TrialsProvider). Tests 3-4
    showed the map ignores an added trial; this shows whether it reads these lists at all - trial I's panel should
    list faster mobs - and whether the game then sets the modifier up itself when that trial is played.
In a mission it only shows the text. The text removes itself at EndPlay (widgets outlive their actor).

Run headless: python tools/blueprints.py build_modtest   (the normal build_transmog drops the test again)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from seqbp import *  # noqa: E402,F401,F403
import seqbp  # noqa: E402

seqbp.start(__file__)

TEST = "/Game/SequelMod/BP_SequelModTest"
VIEW = "/Game/SequelMod/WBP_SequelModTest"
TEST_CLASS = TEST + ".BP_SequelModTest_C"
VIEW_CLASS = VIEW + ".WBP_SequelModTest_C"
GAME_BP = "/Script/Dungeons.GameBP"
PACK = "/Script/Dungeons.ReplicatableTrialDefPack"
TRIAL = "/Script/Dungeons.ReplicatableTrialDef"
MAP = "/Script/Dungeons.ReplicatableMap"
PAIR = "/Script/Dungeons.Pair"
PROVIDER = "/Script/Dungeons.TrialsProvider"
ADDED_KEY, ADDED_VALUE = "MobSpeed", "1.5"

# The text at the top left.
view = fresh(VIEW, unreal.WidgetBlueprint, unreal.WidgetBlueprintFactory())
widget(view, "", unreal.CanvasPanel, "Root")
line = label(view, "Root", "Info", "Trial test", 14, is_variable=True)
spot = line.get_editor_property("slot")
spot.set_position(unreal.Vector2D(40, 40))
spot.set_size(unreal.Vector2D(1840, 1000))
line.set_auto_wrap_text(True)
compile_save(view, "test view")

bp = blueprint(TEST, unreal.Actor)
for name, kind in [("View", "object:" + VIEW_CLASS), ("Lines", "string"), ("Trials", "array:struct:" + TRIAL),
                   ("Cached", "array:struct:" + TRIAL), ("TrialsPairs", "array:struct:" + PAIR),
                   ("CachedPairs", "array:struct:" + PAIR)]:
    check(LIB.add_variable(bp, name, kind), "variable " + name)
g = Graph(bp)


def game_bp():
    node = g.call("/Script/Dungeons.ActorQuery", "GetGameBP")
    return node, "ReturnValue"


def broken(struct, value, pin):
    parts = g.node("/Script/BlueprintGraph.K2Node_BreakStruct", StructType=struct)
    g.link(value[0], value[1], parts, pin)
    return parts


def trial_pack():
    """The game's trials: (GameBP (node, pin), break node of its mTrialDefs)."""
    game = game_bp()
    pack = g.var("mTrialDefs", owner=GAME_BP, target=game)
    return game, broken(PACK, (pack, "mTrialDefs"), "ReplicatableTrialDefPack")


def trial_cache():
    """The game's store of the server's trials: (cast node - it has exec pins - , TrialsProvider (node, pin)),
    break node of its CachedTrialDefs)."""
    instance = g.call("/Script/Engine.GameplayStatics", "GetGameInstance")
    cast, as_game = g.cast("/Script/Dungeons.DungeonsGameInstance", (instance, "ReturnValue"))
    api = g.var("MinecraftAPI", owner="/Script/Dungeons.DungeonsGameInstance", target=(cast, as_game))
    provider = g.var("TrialsProvider", owner="/Script/Dungeons.MinecraftAPI", target=(api, "MinecraftAPI"))
    pack = g.var("CachedTrialDefs", owner=PROVIDER, target=(provider, "TrialsProvider"))
    return (cast, (provider, "TrialsProvider")), broken(PACK, (pack, "CachedTrialDefs"), "ReplicatableTrialDefPack")


def joined(*parts):
    """A string from parts: plain strings or (node, pin) of strings."""
    out = None
    for part in parts:
        concat = g.call("/Script/Engine.KismetStringLibrary", "Concat_StrStr")
        if out:
            g.link(out[0], out[1], concat, "A")
        for pin, value in [("B", part)] if out else [("A", part), ("B", "")]:
            if isinstance(value, tuple):
                g.link(value[0], value[1], concat, pin)
            else:
                g.set(concat, **{pin: value})
        out = (concat, "ReturnValue")
    return out


def add_lines(*parts):
    """A setter: Lines = Lines + parts."""
    node = g.var("Lines", set_=True)
    longer = joined((g.var("Lines"), "Lines"), *parts)
    g.link(longer[0], longer[1], node, "Lines")
    return node


def each(array):
    """A ForLoop over array (node, pin). Returns (loop, item (node, pin))."""
    last = g.array_call("Array_LastIndex", array, "TargetArray")
    loop = g.macro("ForLoop", FirstIndex=0)
    g.link(last, "ReturnValue", loop, "LastIndex")
    return loop, g.item_at(array, (loop, "Index"))


def pairs_text(start, map_value, sep):
    """From exec (node, pin), loop over a ReplicatableMap's pairs adding "key=value<sep>". Returns the loop."""
    pair_map = broken(MAP, map_value, "ReplicatableMap")
    loop, item = each((pair_map, "pairs"))
    pair = broken(PAIR, item, "Pair")
    add = add_lines((pair, "Key"), "=", (pair, "Value"), sep)
    g.link(start[0], start[1], loop, "execute")
    g.link(loop, "LoopBody", add, "execute")
    return loop


# BeginPlay: show the text, Report every 3 s, and in camp add our trial after 1 s.
g.row(0)
begin = g.event("/Script/Engine.Actor", "ReceiveBeginPlay")
make_view = g.node("/Script/UMGEditor.K2Node_CreateWidget")
g.set(make_view, Class=VIEW_CLASS)
set_view = g.var("View", set_=True)
g.link(make_view, "ReturnValue", set_view, "View")
show = g.call("/Script/UMG.UserWidget", "AddToViewport")
g.link(make_view, "ReturnValue", show, "self")
report_timer = g.call("/Script/Engine.KismetSystemLibrary", "K2_SetTimer", FunctionName="Report", Time=3.0,
                      bLooping="true")
map_name = g.call("/Script/Engine.GameplayStatics", "GetCurrentLevelName", bRemovePrefixString="true")
in_camp = g.call("/Script/Engine.KismetStringLibrary", "EqualEqual_StrStr", B="Lobby")
g.link(map_name, "ReturnValue", in_camp, "A")
camp = g.branch((in_camp, "ReturnValue"))
add_timer = g.call("/Script/Engine.KismetSystemLibrary", "K2_SetTimer", FunctionName="AddTrial", Time=1.0,
                   bLooping="false")
g.flow(begin, make_view, set_view, show, report_timer, map_name, camp)
g.flow((camp, "then"), add_timer)

# EndPlay: take the text off the screen.
g.row(400)
end = g.event("/Script/Engine.Actor", "ReceiveEndPlay")
hide = g.call("/Script/UMG.Widget", "RemoveFromParent")
g.link(g.var("View"), "View", hide, "self")
g.flow(end, hide)

# AddTrial: in both lists - the mission's (GameBP.mTrialDefs) and the game's store of the server's trials
# (DungeonsGameInstance.MinecraftAPI.TrialsProvider.CachedTrialDefs) - give the first trial (on the map as trial I,
# Pumpkin Pastures) one more modifier, MobSpeed=1.5, unless its last modifier is MobSpeed already.
g.row(700)
add_event = g.custom_event("AddTrial")


def with_ours(pack, holder):
    """For a pack (break node): a branch (has trials, first not yet changed), the setter of holder (Trials or
    Cached) to the list, the last step putting the changed first trial back, and the new pack (make node)."""
    pairs_holder = holder + "Pairs"
    count = g.array_call("Array_Length", (pack, "trialDefs"), "TargetArray")
    any_trial = g.call("/Script/Engine.KismetMathLibrary", "Greater_IntInt", B=0)
    g.link(count, "ReturnValue", any_trial, "A")
    first = broken(TRIAL, g.item_at((pack, "trialDefs")), "ReplicatableTrialDef")
    mods = broken(MAP, (first, "Modifiers"), "ReplicatableMap")
    last_index = g.array_call("Array_LastIndex", (mods, "pairs"), "TargetArray")
    last = broken(PAIR, g.item_at((mods, "pairs"), (last_index, "ReturnValue")), "Pair")
    is_ours = g.call("/Script/Engine.KismetStringLibrary", "EqualEqual_StrStr", B=ADDED_KEY)
    g.link(last, "Key", is_ours, "A")
    not_ours = g.call("/Script/Engine.KismetMathLibrary", "Not_PreBool")
    g.link(is_ours, "ReturnValue", not_ours, "A")
    both = g.call("/Script/Engine.KismetMathLibrary", "BooleanAND")
    g.link(any_trial, "ReturnValue", both, "A")
    g.link(not_ours, "ReturnValue", both, "B")
    go = g.branch((both, "ReturnValue"))
    copy_all = g.var(holder, set_=True)
    g.link(pack, "trialDefs", copy_all, holder)
    copy_pairs = g.var(pairs_holder, set_=True)
    g.link(mods, "pairs", copy_pairs, pairs_holder)
    pair = g.node("/Script/BlueprintGraph.K2Node_MakeStruct", StructType=PAIR)
    g.set(pair, Key=ADDED_KEY, Value=ADDED_VALUE)
    append = g.array_call("Array_Add", (g.var(pairs_holder), pairs_holder), "TargetArray", NewItem=(pair, "Pair"))
    new_mods = g.node("/Script/BlueprintGraph.K2Node_MakeStruct", StructType=MAP)
    g.link(g.var(pairs_holder), pairs_holder, new_mods, "pairs")
    changed = g.node("/Script/BlueprintGraph.K2Node_MakeStruct", StructType=TRIAL)
    for pin in ["Level", "ExtraChallenge", "rewards", "ID", "Type", "Theme"]:
        g.link(first, pin, changed, pin)
    g.link(new_mods, "ReplicatableMap", changed, "Modifiers")
    put_back = g.array_call("Array_Set", (g.var(holder), holder), "TargetArray", Item=(changed, "ReplicatableTrialDef"))
    g.set(put_back, Index=0)
    new_pack = g.node("/Script/BlueprintGraph.K2Node_MakeStruct", StructType=PACK)
    g.link(g.var(holder), holder, new_pack, "trialDefs")
    g.set(new_pack, isSet="true")
    g.flow((go, "then"), copy_all, copy_pairs, append, put_back)
    return go, put_back, new_pack


game, pack = trial_pack()
go_game, append_game, game_pack = with_ours(pack, "Trials")
set_pack = g.var("mTrialDefs", set_=True, owner=GAME_BP, target=game)
g.link(game_pack, "ReplicatableTrialDefPack", set_pack, "mTrialDefs")
notify = g.call(GAME_BP, "OnRep_TrialDefs")
g.link(game[0], game[1], notify, "self")
g.flow(add_event, go_game)
g.flow(append_game, set_pack, notify)
g.row(1000)
provider, cache = trial_cache()
go_cache, append_cache, cache_pack = with_ours(cache, "Cached")
set_cache = g.var("CachedTrialDefs", set_=True, owner=PROVIDER, target=provider[1])
g.link(cache_pack, "ReplicatableTrialDefPack", set_cache, "CachedTrialDefs")
g.link(notify, "then", provider[0], "execute")
g.link(go_game, "else", provider[0], "execute")
g.link(provider[0], "then", go_cache, "execute")
g.flow(append_cache, set_cache)

# Report: "Trial test | map: <map> | trials: N | in the game's store: M || <ID> [<type>] mods: k=v, ... rewards: k=v; ... || ...".
g.row(1100)
report = g.custom_event("Report")
map_now = g.call("/Script/Engine.GameplayStatics", "GetCurrentLevelName", bRemovePrefixString="true")
game, pack = trial_pack()
count = g.array_call("Array_Length", (pack, "trialDefs"), "TargetArray")
count_text = g.call("/Script/Engine.KismetStringLibrary", "Conv_IntToString")
g.link(count, "ReturnValue", count_text, "InInt")
store, store_pack = trial_cache()
store_count = g.array_call("Array_Length", (store_pack, "trialDefs"), "TargetArray")
store_text = g.call("/Script/Engine.KismetStringLibrary", "Conv_IntToString")
g.link(store_count, "ReturnValue", store_text, "InInt")
clear = g.var("Lines", set_=True)
g.flow(report, map_now, store[0], clear)
trials, trial = each((pack, "trialDefs"))
g.link(clear, "then", trials, "execute")
g.row(1400)
parts = broken(TRIAL, trial, "ReplicatableTrialDef")
head = add_lines(" || ", (parts, "ID"), " [", (parts, "Type"), "] mods: ")
g.link(trials, "LoopBody", head, "execute")
mods = pairs_text((head, "then"), (parts, "Modifiers"), ", ")
g.row(1700)
tail = add_lines(" rewards: ")
g.link(mods, "Completed", tail, "execute")
rewards, reward = each((parts, "rewards"))
g.link(tail, "then", rewards, "execute")
pairs_text((rewards, "LoopBody"), reward, "; ")
g.row(2000)
said = joined("Trial test | map: ", (map_now, "ReturnValue"), " | trials: ", (count_text, "ReturnValue"),
              " | in the game's store: ", (store_text, "ReturnValue"),
              (g.var("Lines"), "Lines"))
as_text = g.call("/Script/Engine.KismetTextLibrary", "Conv_StringToText")
g.link(said[0], said[1], as_text, "InString")
set_text = g.call("/Script/UMG.TextBlock", "SetText")
g.link(g.var("Info", owner=VIEW_CLASS, target=(g.var("View"), "View")), "Info", set_text, "self")
g.link(as_text, "ReturnValue", set_text, "InText")
g.link(trials, "Completed", set_text, "execute")
compile_save(bp, "test actor")

# The transmog build, with the loader also starting the test.
EXTRA_ACTORS = [TEST_CLASS]
transmog = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_transmog.py")
exec(compile(open(transmog).read(), transmog, "exec"), dict(globals(), __file__=__file__))
