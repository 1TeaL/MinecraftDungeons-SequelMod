"""Card texts an enchantment's own code can't give it (CardTexts.toml). Data only: no game code is changed.

    python tools/text_patch.py           # apply CardTexts.toml to the running game
    python tools/text_patch.py --show    # which texts each listed enchantment points at now

An enchantment's card texts are set once, by its own registration code, from literal keys: name, description and
tier line. Some have no key of their own for a text - Knockback (= Sweeping Edge) has no tier line key, so its code
uses the shared "label_chanceToTrigger" ("{0} chance to trigger", ten enchantments use it), and Sponge Strike (=
Shadowcloak) has none at all. A text can't be added by data (the keys are literals in the code), but the definition
holds each text as an FText (research/enchant_flags.py; setters read 2026-11-07):
    +0x18 name   (exe+0xA7BAA0)      +0x30 description (exe+0xA79FB0)
    +0x48 bullet (exe+0xA79E60)      +0x60 tier line   (exe+0xA7A0C0)
An FText is a shared reference (text data pointer, reference controller pointer) + flags. This copies a DONOR
enchantment's text into the listed enchantment's slot - the donor is one the game never uses (Blind: its keys hold
only "BLIND_DESC" / "BLIND_EFFECT"), whose key's words SequelText.toml then sets. The donor's reference count is
raised a lot, so the shared text is never freed; the slot's old text is simply no longer used. Rolls read copies of
the definitions (mobpool_patch.COPIES), made at the game's first roll from the definitions - the copies of a text
share the reference, so they follow too.
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aplus_patch import open_game  # noqa: E402
from builtins_patch import write  # noqa: E402
from memprobe import read  # noqa: E402
from mobpool_patch import copies, definition  # noqa: E402
import settings  # noqa: E402

CONFIG = settings.path("CardTexts.toml")
FIELDS = {"name": 0x18, "desc": 0x30, "bullet": 0x48, "effect": 0x60}
TEXT = 0x14          # text data pointer, reference controller pointer, flags
KEEP_ALIVE = 0x10000  # added to the donor text's reference count: never freed, whatever the game copies


def _donor_text(h, base, donor, field):
    at, _ = definition(h, base, donor)
    raw = read(h, at + FIELDS[field], TEXT) if at else None
    if not raw:
        return None
    data, controller, _flags = struct.unpack("<QQI", raw)
    return raw if data and controller else None


def apply(h, base, quiet=False):
    plan = settings.load(CONFIG).get("texts", {})
    done = []
    for name, fields in plan.items():
        at, _ = definition(h, base, name)
        if not at:
            print(f"Card texts: {name} not found")
            continue
        for field, spec in fields.items():
            donor, donor_field = spec.split(".") if "." in spec else (spec, field)
            text = _donor_text(h, base, donor, donor_field)
            if not text:
                print(f"Card texts: {donor}'s {donor_field} not found")
                continue
            targets = [at] + copies(h, base, name)
            fresh = [t for t in targets if read(h, t + FIELDS[field], TEXT) != text]
            if not fresh:
                continue
            controller = struct.unpack_from("<Q", text, 8)[0]
            count = struct.unpack("<i", read(h, controller + 8, 4))[0]
            write(h, controller + 8, struct.pack("<i", count + KEEP_ALIVE * len(fresh)))
            for t in fresh:
                write(h, t + FIELDS[field], text)
            done.append(f"{name} {field} <- {donor} {donor_field}")
    if done and not quiet:
        print("Card texts: " + "; ".join(done))
    return done


def show(h, base):
    plan = settings.load(CONFIG).get("texts", {})
    for name, fields in plan.items():
        at, _ = definition(h, base, name)
        for field, spec in fields.items():
            donor, donor_field = spec.split(".") if "." in spec else (spec, field)
            mine = read(h, at + FIELDS[field], TEXT) if at else None
            theirs = _donor_text(h, base, donor, donor_field)
            print(f"{name} {field}: {'points at ' + donor + ' ' + donor_field if mine and mine == theirs else 'its own'}")


if __name__ == "__main__":
    h, base = open_game()
    show(h, base) if "--show" in sys.argv else apply(h, base)
