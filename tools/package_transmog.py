"""Make the MCD Transmog zip to give other players: the pak and a readme, nothing else.

    python tools/package_transmog.py            # -> dist/MCD-Transmog-<version>.zip
    python tools/package_transmog.py --bundle   # also dist/SequelMod-<v>-with-Transmog.zip: the Sequel Mod zip
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
MODS = "Dungeons/Content/Paks/~mods/"
README = f"""MCD Transmog {VERSION} for Minecraft Dungeons

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
- Tabs Melee / Ranged / Armor list the items your character has found, with their icons. Click one to wear its
  look in that slot. "Own looks" goes back to each item's own look for that tab's slot.
- Your choices are saved and come back after missions and restarts.
- Another key: click "Menu key: Y - change" at the bottom of the menu and press the new key (Esc keeps the old one).

Good to know
- Works on its own or together with other pak mods, the Sequel Mod included.
- Only items your character has found show up, so it never shows anything you haven't earned.
- Keyboard and mouse only for now (no gamepad).
- Tested on the Steam version, in single player.
- Looks and the menu key are kept in %LOCALAPPDATA%\\Dungeons\\Saved\\SaveGames\\SequelLooks.sav, apart from your
  characters. Your character saves are never touched.

Uninstall
Delete {PAK} and this readme from Dungeons\\Content\\Paks\\~mods. Your items go back to their own looks.
(Delete SequelLooks.sav too if you want your chosen looks forgotten.)
"""


def windows_text(text):
    """Notepad-friendly line ends."""
    return text.replace("\r\n", "\n").replace("\n", "\r\n").encode()


def bundle(pak, sequel_version="1.0"):
    """The Sequel Mod's release zip with the transmog added: its pak goes straight into ~mods (the launcher only
    installs and replaces its own SequelMod_P.pak, never other paks), and INSTALL.txt says it can be deleted."""
    src = ROOT / "dist" / f"SequelMod-{sequel_version}.zip"
    if not src.exists():
        sys.exit(f"no {src.name} - run python tools/package.py first")
    out = ROOT / "dist" / f"SequelMod-{sequel_version}-with-Transmog.zip"
    note = (f"\nOptional, already included: MCD Transmog {VERSION} - press Y in camp or a mission to change how your\n"
            f"gear looks (stats stay the same). It is a separate mod: to leave it out, delete\n"
            f"Dungeons\\Content\\Paks\\~mods\\{PAK} (its readme is next to it).\n")
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for info in zin.infolist():
            data = zin.read(info)
            if info.filename == "Mods/SequelMod/INSTALL.txt":
                data = windows_text(data.decode() + note)
            z.writestr(info, data)
        z.write(pak, MODS + PAK)
        z.writestr(MODS + "MCD Transmog README.txt", windows_text(README))
    print(f"wrote {out} ({out.stat().st_size // 1024} KB)")


def main():
    pak = GAME / "Dungeons" / "Content" / "Paks" / "~mods" / PAK
    if not pak.exists():
        sys.exit(f"no {PAK} built yet - run python tools/blueprints.py build_transmog first")
    out = ROOT / "dist" / f"MCD-Transmog-{VERSION}.zip"
    out.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(pak, MODS + PAK)
        z.writestr(MODS + "MCD Transmog README.txt", README.replace("\n", "\r\n"))
        names = z.namelist()
    print(f"wrote {out} ({out.stat().st_size // 1024} KB)")
    for name in names:
        print("  " + name)
    if "--bundle" in sys.argv:
        bundle(pak)


if __name__ == "__main__":
    main()
