"""A closing sentence on enchantment descriptions saying whether copies of the enchantment stack.

Built from StackNotes.toml (what was tried in game) by `sequel.py build`: the ones found not to stack, or only partly, get a
short sentence at the end of their in-game description.
    partly  "Copies stack only partly."
    none    "Copies do not stack."
Enchantments whose copies simply stack get no sentence (user, 2026-10-14: keep it short, only the exceptions).
An enchantment's description key isn't always its internal name (PoisonedMelee -> Enchantment/Poisoned_desc,
VoidTouchedMelee -> Enchantment/VoidStrikeMelee_desc ...): the key is looked up by the name, then by the name
without Melee / Ranged / Shot, then in KEYS below.
"""
import tomllib
from pathlib import Path

NOTES = Path(__file__).resolve().parent.parent / "StackNotes.toml"
SENTENCE = {"partly": "Copies stack only partly.", "none": "Copies do not stack."}   # "copies": some descriptions already say "stacking" about the effect itself (Soul Speed)
KEYS = {"CriticalHit": ["Critical"], "FireAspect": ["Fire"], "Shockwave": ["Shock"], "SoulSiphon": ["Soul"],
        "EnigmaResonatorMelee": ["Enigma"], "EnigmaResonatorRanged": ["EnigmaRanged"],
        "AnimaConduitMelee": ["Anima"], "AnimaConduitRanged": ["AnimaRanged"], "ChainReaction": ["Chain"],
        "TempoTheft": ["Tempo"], "MultiShot": ["Multi"], "VoidTouchedMelee": ["VoidStrikeMelee"],
        "VoidTouchedRanged": ["VoidStrikeRanged"], "Gravity": ["GravityRanged"]}


def sentences(known_keys):
    """{description key: sentence} for the enchantments of StackNotes.toml; `known_keys`: the game's text keys."""
    if not NOTES.exists():
        return {}
    notes = tomllib.loads(NOTES.read_text(encoding="utf-8"))
    groups = {"full": notes.get("full", []), "partly": list(notes.get("partly", {})), "none": list(notes.get("none", {}))}
    out = {}
    for group, names in groups.items():
        if group not in SENTENCE:
            continue
        for name in names:
            candidates = KEYS.get(name) or [name, name.removesuffix("Melee"), name.removesuffix("Ranged"),
                                            name.removesuffix("Shot")]
            key = next((f"Enchantment/{c}_desc" for c in candidates if f"Enchantment/{c}_desc" in known_keys), None)
            if key:
                out.setdefault(key, SENTENCE[group])
    return out
