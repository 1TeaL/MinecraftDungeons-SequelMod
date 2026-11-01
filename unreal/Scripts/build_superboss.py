"""The Sequel Mod's super bosses (built by build_transmog.py before the loader, which starts them; packed into
SequelMod_P.pak by tools/sequel.py, not into the transmog's pak):

    GE_SequelSuperBoss    a gameplay effect that lasts for good: TakeDamageMultiplier x takes_damage,
                          DifficultyDealDamageMultiplier x deals_damage. The game's own effect system does the maths
                          (writing numbers straight in crashed the game in the modifier test).
    BP_SequelSuperBoss    outside camp, every 2 s on the host: if the mission's A+ level is one of `levels`, each mob
                          with the big health bar at the top of the screen (UGlobalHealthBarComponent - bosses only)
                          gets the effect once. Clients do nothing - the game passes the boss's numbers on.

The values come from Build.toml [super_bosses] (via _settings.json, written by tools/blueprints.py). Tested with
build_bosstest.py (2026-10-31): the effect sticks, the boss lasts longer and hits harder, no crash on its death.
"""
import json
import os

from seqbp import *  # noqa: F401,F403

SUPER_FOLDER = "/Game/SequelBosses"
SUPER = SUPER_FOLDER + "/BP_SequelSuperBoss"
SUPER_EFFECT = SUPER_FOLDER + "/GE_SequelSuperBoss"
SUPER_CLASS = SUPER + ".BP_SequelSuperBoss_C"
SUPER_EFFECT_CLASS = SUPER_EFFECT + ".GE_SequelSuperBoss_C"
_MOB = "/Script/Dungeons.MobCharacter"
_ASC = "/Script/GameplayAbilities.AbilitySystemComponent"
_GAS_LIB = "/Script/GameplayAbilities.AbilitySystemBlueprintLibrary"
_MULTIPLY = 1

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "_settings.json")) as _f:
    _cfg = json.load(_f)["super_bosses"]

_effect = blueprint(SUPER_EFFECT, unreal.GameplayEffect)
compile_save(_effect, "super boss effect")
check(LIB.add_effect_modifier(_effect, unreal.load_class(None, "/Script/Dungeons.HealthAttributeSet"),
                              "TakeDamageMultiplier", _MULTIPLY, _cfg["takes_damage"]),
      "super boss: takes damage x%s" % _cfg["takes_damage"])
check(LIB.add_effect_modifier(_effect, unreal.load_class(None, "/Script/Dungeons.DifficultyAttributeSet"),
                              "DifficultyDealDamageMultiplier", _MULTIPLY, _cfg["deals_damage"]),
      "super boss: deals damage x%s" % _cfg["deals_damage"])
assets.save_loaded_asset(_effect)

_bp = blueprint(SUPER, unreal.Actor)
for _name, _kind in [("Bosses", "array:object:" + _MOB), ("Levels", "array:int")]:
    check(LIB.add_variable(_bp, _name, _kind), "super boss variable " + _name)
check(LIB.set_variable_default(_bp, "Levels", "(%s)" % ",".join(str(int(v)) for v in _cfg["levels"])),
      "super boss levels %s" % _cfg["levels"])
_g = Graph(_bp)

# BeginPlay: outside camp, on the host, Scan every 2 s.
_g.row(0)
_begin = _g.event("/Script/Engine.Actor", "ReceiveBeginPlay")
_map = _g.call("/Script/Engine.GameplayStatics", "GetCurrentLevelName", bRemovePrefixString="true")
_in_camp = _g.call("/Script/Engine.KismetStringLibrary", "EqualEqual_StrStr", B="Lobby")
_g.link(_map, "ReturnValue", _in_camp, "A")
_host = _g.call("/Script/Engine.Actor", "HasAuthority")
_not_camp = _g.call("/Script/Engine.KismetMathLibrary", "Not_PreBool")
_g.link(_in_camp, "ReturnValue", _not_camp, "A")
_go = _g.call("/Script/Engine.KismetMathLibrary", "BooleanAND")
_g.link(_not_camp, "ReturnValue", _go, "A")
_g.link(_host, "ReturnValue", _go, "B")
_start = _g.branch((_go, "ReturnValue"))
_timer = _g.call("/Script/Engine.KismetSystemLibrary", "K2_SetTimer", FunctionName="Scan", Time=2.0, bLooping="true")
_g.flow(_begin, _map, _start)
_g.flow((_start, "then"), _timer)

# Scan: on one of the levels, each new mob with the boss bar goes into Bosses and gets the effect.
_g.row(400)
_scan = _g.custom_event("Scan")
_game = _g.call("/Script/Dungeons.ActorQuery", "GetGameBP")
_settings = _g.var("mReplicatedLevelSettings_ONLY_FOR_INITIAL_REPLICATION", owner="/Script/Dungeons.GameBP",
                   target=(_game, "ReturnValue"))
_level = _g.call("/Script/Dungeons.LevelSettingsUtil", "getEndlessStruggle")
_g.link(_settings, "mReplicatedLevelSettings_ONLY_FOR_INITIAL_REPLICATION", _level, "LevelSettings")
_level_parts = _g.node("/Script/BlueprintGraph.K2Node_BreakStruct", StructType="/Script/Dungeons.EndlessStruggle")
_g.link(_level, "ReturnValue", _level_parts, "EndlessStruggle")
_on_level = _g.array_call("Array_Contains", (_g.var("Levels"), "Levels"), "TargetArray",
                          ItemToFind=(_level_parts, "Value"))
_is_level = _g.branch((_on_level, "ReturnValue"))
_mobs = _g.call("/Script/Engine.GameplayStatics", "GetAllActorsOfClass", ActorClass=_MOB)
_g.flow(_scan, _is_level)
_g.flow((_is_level, "then"), _mobs)
_last = _g.array_call("Array_LastIndex", (_mobs, "OutActors"), "TargetArray")
_loop = _g.macro("ForLoop", FirstIndex=0)
_g.link(_last, "ReturnValue", _loop, "LastIndex")
_g.link(_mobs, "then", _loop, "execute")
_mob = _g.item_at((_mobs, "OutActors"), (_loop, "Index"))
_g.row(700)
_as_mob, _as_mob_pin = _g.cast(_MOB, _mob)
_bar = _g.call("/Script/Engine.Actor", "GetComponentByClass", ComponentClass="/Script/Dungeons.GlobalHealthBarComponent")
_g.link(_mob[0], _mob[1], _bar, "self")
_has_bar = _g.call("/Script/Engine.KismetSystemLibrary", "IsValid")
_g.link(_bar, "ReturnValue", _has_bar, "Object")
_known = _g.array_call("Array_Contains", (_g.var("Bosses"), "Bosses"), "TargetArray", ItemToFind=(_as_mob, _as_mob_pin))
_new = _g.call("/Script/Engine.KismetMathLibrary", "Not_PreBool")
_g.link(_known, "ReturnValue", _new, "A")
_new_boss = _g.call("/Script/Engine.KismetMathLibrary", "BooleanAND")
_g.link(_has_bar, "ReturnValue", _new_boss, "A")
_g.link(_new, "ReturnValue", _new_boss, "B")
_is_new = _g.branch((_new_boss, "ReturnValue"))
_g.link(_loop, "LoopBody", _as_mob, "execute")
_g.link(_as_mob, "then", _is_new, "execute")
_g.row(1000)
_remember = _g.array_call("Array_Add", (_g.var("Bosses"), "Bosses"), "TargetArray", NewItem=(_as_mob, _as_mob_pin))
_asc = _g.call(_GAS_LIB, "GetAbilitySystemComponent")
_g.link(_as_mob, _as_mob_pin, _asc, "Actor")
_context = _g.call(_ASC, "MakeEffectContext")
_g.link(_asc, "ReturnValue", _context, "self")
_apply = _g.call(_ASC, "BP_ApplyGameplayEffectToSelf", GameplayEffectClass=SUPER_EFFECT_CLASS, Level=1.0)
_g.link(_asc, "ReturnValue", _apply, "self")
_g.link(_context, "ReturnValue", _apply, "EffectContext")
_steps = [(_is_new, "then"), _remember]
if "execute" in _g.pins(_context):
    _steps.append(_context)
_steps.append(_apply)
_g.flow(*_steps)
compile_save(_bp, "super boss actor")
