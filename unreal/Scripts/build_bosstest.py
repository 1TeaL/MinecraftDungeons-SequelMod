"""Test build: can our blueprint make a mission's boss a super boss (takes less damage, deals more)?

The transmog as usual, plus:
    GE_SequelSuperBoss, a gameplay effect of our own that lasts for good: the boss's TakeDamageMultiplier x0.4
    (2.5 times the health, in effect) and DifficultyDealDamageMultiplier x1.5. The game's own effect system does the
    maths, as for its own effects - writing numbers straight in is what crashed the modifier test.
    BP_SequelBossTest, which the loader also starts. Outside camp, every 2 s it looks for mobs with the big health
    bar at the top of the screen (UGlobalHealthBarComponent - bosses only) and puts the effect on each new one, on
    the host only. A text at the top left shows the A+ level the game reports, whether this PC is the host, and
    each boss's two numbers - before the effect 1.0 / the difficulty's value, after it 0.4 / 1.5 times that.
For the test it does this on every A+ level; the real one is for A+100 boss missions only.

Run headless: python tools/blueprints.py build_bosstest   (the normal build_transmog drops the test again)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from seqbp import *  # noqa: E402,F401,F403
import seqbp  # noqa: E402

seqbp.start(__file__)

TEST = "/Game/SequelMod/BP_SequelBossTest"
VIEW = "/Game/SequelMod/WBP_SequelBossTest"
EFFECT = "/Game/SequelMod/GE_SequelSuperBoss"
TEST_CLASS = TEST + ".BP_SequelBossTest_C"
VIEW_CLASS = VIEW + ".WBP_SequelBossTest_C"
EFFECT_CLASS = EFFECT + ".GE_SequelSuperBoss_C"
MOB = "/Script/Dungeons.MobCharacter"
GAME_BP = "/Script/Dungeons.GameBP"
ASC = "/Script/GameplayAbilities.AbilitySystemComponent"
GAS_LIB = "/Script/GameplayAbilities.AbilitySystemBlueprintLibrary"
HEALTH_SET = unreal.load_class(None, "/Script/Dungeons.HealthAttributeSet")
DIFFICULTY_SET = unreal.load_class(None, "/Script/Dungeons.DifficultyAttributeSet")
MULTIPLY = 1
TAKE_DAMAGE, DEAL_DAMAGE = 0.4, 1.5

# The effect.
effect = blueprint(EFFECT, unreal.GameplayEffect)
compile_save(effect, "effect")
check(LIB.add_effect_modifier(effect, HEALTH_SET, "TakeDamageMultiplier", MULTIPLY, TAKE_DAMAGE),
      "effect: TakeDamageMultiplier x%s" % TAKE_DAMAGE)
check(LIB.add_effect_modifier(effect, DIFFICULTY_SET, "DifficultyDealDamageMultiplier", MULTIPLY, DEAL_DAMAGE),
      "effect: DifficultyDealDamageMultiplier x%s" % DEAL_DAMAGE)
assets.save_loaded_asset(effect)

# The text at the top left.
view = fresh(VIEW, unreal.WidgetBlueprint, unreal.WidgetBlueprintFactory())
widget(view, "", unreal.CanvasPanel, "Root")
line = label(view, "Root", "Info", "Boss test", 18, is_variable=True)
spot = line.get_editor_property("slot")
spot.set_position(unreal.Vector2D(40, 40))
spot.set_size(unreal.Vector2D(1600, 300))
line.set_auto_wrap_text(True)
compile_save(view, "test view")

bp = blueprint(TEST, unreal.Actor)
for name, kind in [("View", "object:" + VIEW_CLASS), ("Lines", "string"), ("Bosses", "array:object:" + MOB)]:
    check(LIB.add_variable(bp, name, kind), "variable " + name)
g = Graph(bp)


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


def each(array):
    """A ForLoop over array (node, pin). Returns (loop, item (node, pin))."""
    last = g.array_call("Array_LastIndex", array, "TargetArray")
    loop = g.macro("ForLoop", FirstIndex=0)
    g.link(last, "ReturnValue", loop, "LastIndex")
    return loop, g.item_at(array, (loop, "Index"))


def attribute_text(actor, attribute_set, prop):
    node = g.call(GAS_LIB, "GetFloatAttribute")
    g.link(actor[0], actor[1], node, "Actor")
    check(LIB.set_attribute_pin(bp, g.name, node, "Attribute", attribute_set, prop), node + ".Attribute = " + prop)
    text = g.call("/Script/Engine.KismetStringLibrary", "Conv_FloatToString")
    g.link(node, "ReturnValue", text, "InFloat")
    return text, "ReturnValue"


# BeginPlay: show the text; outside camp, Scan every 2 s.
g.row(0)
begin = g.event("/Script/Engine.Actor", "ReceiveBeginPlay")
make_view = g.node("/Script/UMGEditor.K2Node_CreateWidget")
g.set(make_view, Class=VIEW_CLASS)
set_view = g.var("View", set_=True)
g.link(make_view, "ReturnValue", set_view, "View")
show = g.call("/Script/UMG.UserWidget", "AddToViewport")
g.link(make_view, "ReturnValue", show, "self")
map_name = g.call("/Script/Engine.GameplayStatics", "GetCurrentLevelName", bRemovePrefixString="true")
in_camp = g.call("/Script/Engine.KismetStringLibrary", "EqualEqual_StrStr", B="Lobby")
g.link(map_name, "ReturnValue", in_camp, "A")
camp = g.branch((in_camp, "ReturnValue"))
scan_timer = g.call("/Script/Engine.KismetSystemLibrary", "K2_SetTimer", FunctionName="Scan", Time=2.0,
                    bLooping="true")
g.flow(begin, make_view, set_view, show, map_name, camp)
g.flow((camp, "else"), scan_timer)

# EndPlay: take the text off the screen (widgets outlive their actor).
g.row(400)
end = g.event("/Script/Engine.Actor", "ReceiveEndPlay")
hide = g.call("/Script/UMG.Widget", "RemoveFromParent")
g.link(g.var("View"), "View", hide, "self")
g.flow(end, hide)

# Scan: each mob with the boss bar that isn't in Bosses yet goes in, and on the host gets the effect.
g.row(700)
scan = g.custom_event("Scan")
mobs = g.call("/Script/Engine.GameplayStatics", "GetAllActorsOfClass", ActorClass=MOB)
g.flow(scan, mobs)
loop, mob = each((mobs, "OutActors"))
g.link(mobs, "then", loop, "execute")
bar = g.call("/Script/Engine.Actor", "GetComponentByClass", ComponentClass="/Script/Dungeons.GlobalHealthBarComponent")
g.link(mob[0], mob[1], bar, "self")
has_bar = g.call("/Script/Engine.KismetSystemLibrary", "IsValid")
g.link(bar, "ReturnValue", has_bar, "Object")
as_mob, as_mob_pin = g.cast(MOB, mob)
known = g.array_call("Array_Contains", (g.var("Bosses"), "Bosses"), "TargetArray", ItemToFind=(as_mob, as_mob_pin))
new = g.call("/Script/Engine.KismetMathLibrary", "Not_PreBool")
g.link(known, "ReturnValue", new, "A")
new_boss = g.call("/Script/Engine.KismetMathLibrary", "BooleanAND")
g.link(has_bar, "ReturnValue", new_boss, "A")
g.link(new, "ReturnValue", new_boss, "B")
is_new = g.branch((new_boss, "ReturnValue"))
g.link(loop, "LoopBody", as_mob, "execute")
g.link(as_mob, "then", is_new, "execute")
g.row(1000)
remember = g.array_call("Array_Add", (g.var("Bosses"), "Bosses"), "TargetArray", NewItem=(as_mob, as_mob_pin))
host = g.call("/Script/Engine.Actor", "HasAuthority")
on_host = g.branch((host, "ReturnValue"))
asc = g.call(GAS_LIB, "GetAbilitySystemComponent")
g.link(as_mob, as_mob_pin, asc, "Actor")
context = g.call(ASC, "MakeEffectContext")
g.link(asc, "ReturnValue", context, "self")
apply = g.call(ASC, "BP_ApplyGameplayEffectToSelf", GameplayEffectClass=EFFECT_CLASS, Level=1.0)
g.link(asc, "ReturnValue", apply, "self")
g.link(context, "ReturnValue", apply, "EffectContext")
steps = [(is_new, "then"), remember, (on_host, "then")]
if "execute" in g.pins(context):
    steps.append(context)
steps.append(apply)
g.flow(*steps)

# Then the text: "Boss test | A+ N | host: true | bosses: K || <name>: takes x, deals y || ...".
g.row(1300)
clear = g.var("Lines", set_=True)
g.link(loop, "Completed", clear, "execute")
bosses, boss = each((g.var("Bosses"), "Bosses"))
g.link(clear, "then", bosses, "execute")
name = g.call("/Script/Engine.KismetTextLibrary", "Conv_TextToString")
display = g.call(MOB, "GetDisplayName")
g.link(boss[0], boss[1], display, "self")
g.link(display, "ReturnValue", name, "InText")
add = g.var("Lines", set_=True)
longer = joined((g.var("Lines"), "Lines"), " || ", (name, "ReturnValue"), ": takes ",
                attribute_text(boss, HEALTH_SET, "TakeDamageMultiplier"), ", deals ",
                attribute_text(boss, DIFFICULTY_SET, "DifficultyDealDamageMultiplier"))
g.link(longer[0], longer[1], add, "Lines")
g.link(bosses, "LoopBody", add, "execute")
g.row(1600)
game = g.call("/Script/Dungeons.ActorQuery", "GetGameBP")
settings_ = g.var("mReplicatedLevelSettings_ONLY_FOR_INITIAL_REPLICATION", owner=GAME_BP, target=(game, "ReturnValue"))
level = g.call("/Script/Dungeons.LevelSettingsUtil", "getEndlessStruggle")
g.link(settings_, "mReplicatedLevelSettings_ONLY_FOR_INITIAL_REPLICATION", level, "LevelSettings")
level_parts = g.node("/Script/BlueprintGraph.K2Node_BreakStruct", StructType="/Script/Dungeons.EndlessStruggle")
g.link(level, "ReturnValue", level_parts, "EndlessStruggle")
level_text = g.call("/Script/Engine.KismetStringLibrary", "Conv_IntToString")
g.link(level_parts, "Value", level_text, "InInt")
host_text = g.call("/Script/Engine.KismetStringLibrary", "Conv_BoolToString")
g.link(g.call("/Script/Engine.Actor", "HasAuthority"), "ReturnValue", host_text, "InBool")
count = g.array_call("Array_Length", (g.var("Bosses"), "Bosses"), "TargetArray")
count_text = g.call("/Script/Engine.KismetStringLibrary", "Conv_IntToString")
g.link(count, "ReturnValue", count_text, "InInt")
said = joined("Boss test | A+ ", (level_text, "ReturnValue"), " | host: ", (host_text, "ReturnValue"), " | bosses: ",
              (count_text, "ReturnValue"), (g.var("Lines"), "Lines"))
as_text = g.call("/Script/Engine.KismetTextLibrary", "Conv_StringToText")
g.link(said[0], said[1], as_text, "InString")
set_text = g.call("/Script/UMG.TextBlock", "SetText")
g.link(g.var("Info", owner=VIEW_CLASS, target=(g.var("View"), "View")), "Info", set_text, "self")
g.link(as_text, "ReturnValue", set_text, "InText")
g.link(bosses, "Completed", set_text, "execute")
compile_save(bp, "test actor")

# The transmog build, with the loader also starting the test.
EXTRA_ACTORS = [TEST_CLASS]
transmog = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_transmog.py")
exec(compile(open(transmog).read(), transmog, "exec"), dict(globals(), __file__=__file__))
