"""Make the zip to give other players: everything needed to PLAY the mod, nothing of the development tools.

    python tools/package.py            # -> dist/SequelMod-<version>.zip

The zip holds Mods/SequelMod/... so it is unpacked straight into the game folder (the one with Dungeons/ in it):
the launcher finds the game two folders up from tools/ (play.py: the first folder above with Dungeons/Content/Paks).
Inside: the pak (the newest build: staged/ if a build is waiting there, else the installed one), the launcher's
Python files (every module play.py imports, found by modulefinder), the data files they read, the settings,
the two .bat files, CHANGES.md and an INSTALL.txt - and a portable Python in python/ (python.org's Windows
embeddable package, vendor/: nothing to install; the .bat files use it when it is there, else the system's python).
"""
import modulefinder
import sys
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
GAME = ROOT.parents[1]
VERSION = "1.2"
LABEL = f"Beta {VERSION}"     # what the release is called (GitHub release "Sequel Mod v<version>-beta", tag v<version>-beta)
PAK = "SequelMod_P.pak"
PYTHON = ROOT / "vendor" / "python-3.12.10-embed-amd64.zip"   # md5 fe8ef205f2e9c3ba44d0cf9954e1abd3 (python.org)
# Parts of that Python the launcher never loads (secure connections, databases, XML, sound, async...): left out to
# keep the zip small (under 10 MB). hashlib falls back to its built-in SHA-256 without _hashlib / libcrypto.
UNUSED = {"libcrypto-3.dll", "libssl-3.dll", "_ssl.pyd", "_hashlib.pyd", "sqlite3.dll", "_sqlite3.pyd", "pyexpat.pyd",
          "_elementtree.pyd", "_msi.pyd", "winsound.pyd", "_asyncio.pyd", "_overlapped.pyd", "_wmi.pyd",
          "_multiprocessing.pyd", "_zoneinfo.pyd", "_socket.pyd", "select.pyd", "pythonw.exe"}
DATA = ["tools/item_registry.json", "tools/enchant_ids.json", "tools/enchant_pools.json", "tools/enchant_registry.json",
        "tools/artifact_fields.json", "research/artifact_globals.json"]   # no save key: the launcher reads it from the game
SETTINGS = ["Launcher.toml", "Endless.toml", "Builtins.toml", "Bonus.toml", "Perks.toml", "Artifacts.toml",
            "ArtifactScaling.toml", "Drops.toml", "Echo.toml", "Formulas.toml", "Prices.toml", "QoL.toml",
            "MobPool.toml", "MobEnchants.toml", "Accelerate.toml", "Arrows.toml", "Stack.toml", "SequelGear.toml",
            "Play Endless Apocalypse.bat", "steam_launch.bat", "CHANGES.md"]
INSTALL = f"""Sequel Mod {LABEL} for Minecraft Dungeons (Steam version)

Needs
- Minecraft Dungeons from Steam, updated. (The Microsoft Store / Xbox app version won't work: the launcher
  reads the Steam game's memory at fixed places.)
- Nothing else: a portable Python comes with it (in the python folder).

Install
1. In Steam: right-click Minecraft Dungeons > Manage > Browse local files. That opens the game folder (the one
   with the Dungeons folder in it).
2. Unpack this zip there, so you get <game folder>\\Mods\\SequelMod\\.
3. Start the game with "Play Sequel Mod.bat" in the game folder (keep its window open while you play).
   The first start copies the mod into the game, backs up your saves, then starts the game.
   Optional: to use Steam's Play button instead, set Minecraft Dungeons > Properties > General > Launch Options to
       "<game folder>\\Mods\\SequelMod\\steam_launch.bat" %command%

Multiplayer: everyone in the party needs the mod, started this way.
Every change is listed in CHANGES.md.
To uninstall: delete Dungeons\\Content\\Paks\\~mods\\{PAK} and the Mods\\SequelMod folder (clear the Launch Options too
if you set them). Save backups are in Mods\\SequelMod\\save_backups.
"""


def newest_pak():
    staged, installed = ROOT / "staged" / PAK, GAME / "Dungeons" / "Content" / "Paks" / "~mods" / PAK
    found = [p for p in (staged, installed) if p.exists()]
    if not found:
        sys.exit(f"no {PAK} built yet - run python tools/sequel.py build first")
    return max(found, key=lambda p: p.stat().st_mtime)


def launcher_modules():
    finder = modulefinder.ModuleFinder(path=[str(TOOLS)] + sys.path)
    finder.run_script(str(TOOLS / "play.py"))
    return sorted(["play.py"] + [f"{m}.py" for m in finder.modules if (TOOLS / f"{m}.py").exists()])


def main():
    out = ROOT / "dist" / f"SequelMod-{VERSION}.zip"
    out.parent.mkdir(exist_ok=True)
    prefix = "Mods/SequelMod/"
    pak = newest_pak()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(pak, prefix + PAK)
        for name in launcher_modules():
            z.write(TOOLS / name, prefix + "tools/" + name)
        for name in DATA + SETTINGS:
            z.write(ROOT / name, prefix + name)
        if PYTHON.exists():
            with zipfile.ZipFile(PYTHON) as py:
                for info in py.infolist():
                    if info.filename not in UNUSED:
                        z.writestr(prefix + "python/" + info.filename, py.read(info))
        else:
            print("warning: no portable Python in vendor/ - players will need Python 3.11+ installed")
        z.write(ROOT / "Play Sequel Mod.bat", "Play Sequel Mod.bat")   # in the game folder itself, for easy access
        z.writestr(prefix + "INSTALL.txt", INSTALL)
        z.writestr(prefix + "VERSION.txt", f"{LABEL} ({date.today().isoformat()})\n")
        count = len(z.namelist())
    print(f"wrote {out} ({count} files, {out.stat().st_size // 1024} KB; pak from {pak.parent.name})")


if __name__ == "__main__":
    main()
