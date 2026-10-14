"""Gameplay-effect modifier trees for the Sequel Mod (used by sequel.py build)."""

MODOP = "EGameplayModOp"
CALC = "EGameplayEffectMagnitudeCalculation"
SETS = {"Melee": "MeleeAttributeSet", "Ranged": "RangedAttributeSet", "Health": "HealthAttributeSet"}


def attribute(set_key, attr):
    owner = ("/Script/CoreUObject", "Class", "/Script/Dungeons", SETS[set_key])
    prop = ("/Script/CoreUObject", "FloatProperty", owner, attr)
    return ("Attribute", "struct", ("GameplayAttribute", [
        ("AttributeName", "str", attr),
        ("Attribute", "object", prop),
        ("AttributeOwner", "object", owner),
    ]))


def modifier(set_key, attr, op, set_by_caller=None, value=None):
    """One FGameplayModifierInfo. op: Additive / Multiplicitive / Division / Override."""
    if set_by_caller:
        mag = [("MagnitudeCalculationType", "enum", (CALC, f"{CALC}::SetByCaller")),
               ("SetByCallerMagnitude", "struct", ("SetByCallerFloat", [("DataName", "name", set_by_caller)]))]
    else:
        mag = [("MagnitudeCalculationType", "enum", (CALC, f"{CALC}::ScalableFloat")),
               ("ScalableFloatMagnitude", "struct", ("ScalableFloat", [("Value", "float", float(value))]))]
    return [attribute(set_key, attr),
            ("ModifierOp", "byteenum", (MODOP, f"{MODOP}::{op}")),
            ("ModifierMagnitude", "struct", ("GameplayEffectModifierMagnitude", mag))]


def modifiers_node(mods):
    return ("Modifiers", "structarray", ("GameplayModifierInfo", mods))


# Plain effect settings a spec may expose next to its modifiers: config key -> (property, type).
EXTRA_PROPS = {"StackLimit": ("StackLimitCount", "int")}


# Effect files we rebuild, with the config keys they expose. Each build function returns the full
# modifier list: the game's original modifiers (still fed by the enchantment code) plus ours.
# Multiplier bonuses add up in Unreal's buff math (1 + sum of (x - 1)), so an extra x(1 + b)
# modifier adds +b to the enchantment's bonus at every level.
def _cowardice(v):
    mods = [modifier("Melee", "MeleeAttackDamageMultiplier", "Multiplicitive", "CowardiceMeleeDamageEffectMagnitude"),
            modifier("Ranged", "RangedAttackDamageMultipler", "Multiplicitive", "CowardiceRangedDamageEffectMagnitude")]
    b = v["ExtraDamageBonus"]
    if b:
        mods += [modifier("Melee", "MeleeAttackDamageMultiplier", "Multiplicitive", value=1 + b),
                 modifier("Ranged", "RangedAttackDamageMultipler", "Multiplicitive", value=1 + b)]
    return mods


def _frenzied(v):
    mods = [modifier("Melee", "MeleeAttackSpeedMultiplier", "Multiplicitive", "FenziedSpeedMagnitude"),
            modifier("Ranged", "RangedAttackSpeedMultiplier", "Multiplicitive", "FenziedSpeedMagnitude")]
    b = v["ExtraAttackSpeedBonus"]
    if b:
        mods += [modifier("Melee", "MeleeAttackSpeedMultiplier", "Multiplicitive", value=1 + b),
                 modifier("Ranged", "RangedAttackSpeedMultiplier", "Multiplicitive", value=1 + b)]
    return mods


def _accelerate(v):
    return [modifier("Ranged", "RangedAttackSpeedMultiplier", "Additive", value=v["SpeedPerShot"])]


EFFECTS = [
    # (config folder, file relative to the extraction root, {key: default}, build)
    ("Cowardice", "Components/Enchantments/Cowardice/BP_CowardiceGameplayEffect.uasset",
     {"ExtraDamageBonus": 0.0}, _cowardice),
    ("Frenzied", "Components/Enchantments/Frenzied/BP_FrenziedGameplayEffect.uasset",
     {"ExtraAttackSpeedBonus": 0.0}, _frenzied),
    ("Accelerating", "Components/Enchantments/Accelerating/BP_AcceleratingLevelOneEffect.uasset",
     {"SpeedPerShot": 0.08, "StackLimit": 25}, _accelerate),
    ("Accelerating", "Components/Enchantments/Accelerating/BP_AcceleratingLevelTwoEffect.uasset",
     {"SpeedPerShot": 0.10, "StackLimit": 20}, _accelerate),
    ("Accelerating", "Components/Enchantments/Accelerating/BP_AcceleratingLevelThreeEffect.uasset",
     {"SpeedPerShot": 0.12, "StackLimit": 16}, _accelerate),
]
