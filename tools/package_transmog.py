"""Make the MCD Transmog and Loadouts zip to give other players: the pak and a readme, nothing else.

    python tools/package_transmog.py            # -> dist/MCD-Transmog-and-Loadouts-<version>.zip
    python tools/package_transmog.py --bundle   # also dist/SequelMod-<v>-with-Transmog-and-Loadouts.zip: the Sequel Mod zip
                                                #   (tools/package.py) plus this pak, optional for players

The zip holds Dungeons/Content/Paks/~mods/... so it is unpacked straight into the game folder (the one with
Dungeons/ in it). The pak is the installed one (tools/blueprints.py builds it there). A mod of its own: it needs
neither the Sequel Mod nor its launcher, and holds nothing of the Blueprint Loader.
"""
import sys
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GAME = ROOT.parents[1]
VERSION = "1.0"
PAK = "MCDTransmog_P.pak"
SEQUEL_VERSION = "1.0"   # the Sequel Mod zip the bundle starts from (tools/package.py VERSION)
MODS = "Dungeons/Content/Paks/~mods/"
README = f"""MCD Transmog and Loadouts {VERSION} for Minecraft Dungeons

Change how your gear looks without changing what it does. Pick one look for your melee weapon, one for your
ranged weapon and one for your armor: every item in that slot wears it while it's chosen. Swings, stats, shots
and enchantments stay the item's own - only the look changes.

Install
1. In Steam: right-click Minecraft Dungeons > Manage > Browse local files. That opens the game folder (the one
   with the Dungeons folder in it).
2. Unpack this zip there. You get Dungeons\\Content\\Paks\\~mods\\{PAK} (and this readme next to it).
3. Start the game as usual. Nothing else to install or run.

Use
- In camp or in a mission, press Y to open the menu (press Y again or Close to shut it).
- Controller: D-pad left opens it. Move with the D-pad or stick (the selected button turns gold), A presses,
  LB / RB switch tabs, B closes. While it's open the game ignores the controller.
- Tabs Melee / Ranged / Armor list the items your character has found, with their icons. Click one to wear its
  look in that slot. "Own looks" goes back to each item's own look for that tab's slot.
- Your choices are saved and come back after missions and restarts.
- Loadouts tab: "Save gear" keeps what you wear (melee, ranged, armor, 3 artifacts); "Save gear + looks" keeps
  your chosen looks too. Type a name first, or leave it empty for "Loadout 1", "Loadout 2"... Up to 100.
  Each loadout has Load, Save over and Delete (click twice); click its name to rename it. Load moves each item
  in from your inventory, like dragging it in the inventory screen, so enchantment points stay on their items.
  An item you no longer have is skipped.
- Another key: click "Menu key: Y - change" at the bottom of the menu and press the new key (Esc keeps the old one).

Good to know
- Works on its own or together with other pak mods, the Sequel Mod included.
- Only items your character has found show up, so it never shows anything you haven't earned.
- Keyboard and mouse, or a controller. Typing a loadout name needs a keyboard (without one they're numbered).
- Tested on the Steam version, in single player.
- Looks, loadouts and the menu key are kept in %LOCALAPPDATA%\\Dungeons\\Saved\\SaveGames\\SequelLooks.sav, apart
  from your characters. The mod never writes your character saves; when a loadout moves items, the game saves
  that itself, as after the inventory screen.
- Using the Sequel Mod too? Take both from the same release (they share the small loader that starts them).

Uninstall
Delete {PAK} and this readme from Dungeons\\Content\\Paks\\~mods. Your items go back to their own looks.
(An older download's "MCD Transmog README.txt" there can be deleted too.)
(Delete SequelLooks.sav too if you want your chosen looks and loadouts forgotten.)
"""


def windows_text(text):
    """Notepad-friendly line ends."""
    return text.replace("\r\n", "\n").replace("\n", "\r\n").encode()


def bundle(pak, sequel_version=None):
    """The Sequel Mod's release zip with the transmog added: its pak goes straight into ~mods (the launcher only
    installs and replaces its own SequelMod_P.pak, never other paks), and INSTALL.txt says it can be deleted."""
    sequel_version = sequel_version or SEQUEL_VERSION
    src = ROOT / "dist" / f"SequelMod-{sequel_version}.zip"
    if not src.exists():
        sys.exit(f"no {src.name} - run python tools/package.py first")
    out = ROOT / "dist" / f"SequelMod-{sequel_version}-with-Transmog-and-Loadouts.zip"
    note = (f"\nOptional, already included: MCD Transmog and Loadouts {VERSION} - press Y in camp or a mission to change how your\n"
            f"gear looks (stats stay the same). It is a separate mod: to leave it out, delete\n"
            f"Dungeons\\Content\\Paks\\~mods\\{PAK} (its readme is next to it).\n")
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for info in zin.infolist():
            data = zin.read(info)
            if info.filename == "Mods/SequelMod/INSTALL.txt":
                data = windows_text(data.decode() + note)
            z.writestr(info, data)
        z.write(pak, MODS + PAK)
        z.writestr(MODS + "MCD Transmog and Loadouts README.txt", windows_text(README))
    print(f"wrote {out} ({out.stat().st_size // 1024} KB)")


def main():
    pak = GAME / "Dungeons" / "Content" / "Paks" / "~mods" / PAK
    if not pak.exists():
        sys.exit(f"no {PAK} built yet - run python tools/blueprints.py build_transmog first")
    out = ROOT / "dist" / f"MCD-Transmog-and-Loadouts-{VERSION}.zip"
    out.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(pak, MODS + PAK)
        z.writestr(MODS + "MCD Transmog and Loadouts README.txt", README.replace("\n", "\r\n"))
        names = z.namelist()
    print(f"wrote {out} ({out.stat().st_size // 1024} KB)")
    for name in names:
        print("  " + name)
    if "--bundle" in sys.argv:
        bundle(pak)


if __name__ == "__main__":
    main()
