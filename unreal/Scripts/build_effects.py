"""The Sequel Mod's own copies of game effects (exec'd by build_transmog.py; packed into SequelMod_P.pak by
tools/sequel.py, which also points the game's assets at them - see REPOINT there):

    GE_SequelPoisonArrow  the Dipping Poison arrows' poison: the game's own PoisonArrowGameplayEffect with a higher
                          damagePerSecond (game: 15). Everything else - the 10 s duration, how the damage scales -
                          stays the game's, inherited from its class. BP_PlayerPoisonArrow applies it instead.
"""
from seqbp import *  # noqa: F401,F403

EFFECTS_FOLDER = "/Game/SequelEffects"
POISON_ARROW = EFFECTS_FOLDER + "/GE_SequelPoisonArrow"
POISON_ARROW_DPS = 15.0   # the game's (user, 2026-11-09: back from 30 - the poison max-health share does the work)

_poison = blueprint(POISON_ARROW, unreal.PoisonArrowGameplayEffect)
compile_save(_poison, "poison arrow effect")
_cdo = unreal.get_default_object(assets.load_blueprint_class(POISON_ARROW))
_cdo.set_editor_property("damagePerSecond", POISON_ARROW_DPS)
check(abs(_cdo.get_editor_property("damagePerSecond") - POISON_ARROW_DPS) < 1e-4,
      "poison arrow: %s damage per second" % POISON_ARROW_DPS)
assets.save_loaded_asset(_poison)
