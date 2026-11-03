"""Build the blueprints - MCD Transmog, Loadouts and Reroll's (a mod of its own) and the Sequel Mod's super bosses - with the Unreal editor:
pack the transmog into ~mods/MCDTransmog_P.pak, and keep the Sequel Mod's cooked files in blueprints/, which
tools/sequel.py build puts into SequelMod_P.pak.

    python tools/blueprints.py build_transmog          run unreal/Scripts/<script>.py, cook, pack
    python tools/blueprints.py --pack                  only cook and pack what the project has

Needs the Unreal 4.22 editor (UE_ROOT below) and the editor modules built once (unreal/Source; see decisions.md).
The transmog pak holds /Game/SequelMod and /Game/Actors/BP_AvatarInfo (the loader, a copy of the game's own empty
helper that starts our actors); blueprints/ holds /Game/SequelBosses, /Game/SequelEffects (our copies of game
effects) and the same loader. Both paks carry the same
loader, which starts whichever mod's actors are installed. The super boss values come from Build.toml
[super_bosses], handed to the editor's scripts in unreal/Scripts/_settings.json.
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
GAME = os.path.normpath(os.path.join(MOD, "..", ".."))
UE_ROOT = r"G:\NVME2 Games\UE_4.22"
EDITOR = os.path.join(UE_ROOT, "Engine", "Binaries", "Win64", "UE4Editor-Cmd.exe")
PROJECT = os.path.join(MOD, "unreal", "Dungeons.uproject")
COOKED = os.path.join(MOD, "unreal", "Saved", "Cooked", "WindowsNoEditor", "Dungeons", "Content")
STAGE = os.path.join(MOD, "unreal", "Saved", "pak_stage")
U4PAK = os.path.join(MOD, "..", "Dungeons-Mod-Kit-master", "Tools", "py", "u4pak.py")
OUT_PAK = os.path.join(GAME, "Dungeons", "Content", "Paks", "~mods", "MCDTransmog_P.pak")
# Actors: only BP_AvatarInfo, the loader (unreal/Content holds nothing else under Actors).
FOLDERS = ["SequelMod", "Actors"]
SEQUEL_FOLDERS = ["SequelBosses", "SequelEffects", "Actors"]   # into SequelMod_P.pak, by sequel.py
SEQUEL_COOKED = os.path.join(MOD, "blueprints")
SETTINGS_JSON = os.path.join(MOD, "unreal", "Scripts", "_settings.json")
FLAGS = ["-unattended", "-nop4", "-nosplash"]


def write_settings():
    """The Build.toml values the editor's scripts need (its Python can't read TOML)."""
    sys.path.insert(0, HERE)
    import settings
    cfg = settings.load(settings.path("Endless.toml")).get("super_bosses", {})
    values = {"levels": cfg.get("levels", [55, 64, 73, 82, 91, 100]), "takes_damage": cfg.get("takes_damage", 0.6),
              "deals_damage": cfg.get("deals_damage", 1.25)}
    with open(SETTINGS_JSON, "w") as f:
        json.dump({"super_bosses": values}, f, indent=1)


def keep_sequel_files():
    """The Sequel Mod's cooked blueprints, for sequel.py build."""
    shutil.rmtree(SEQUEL_COOKED, ignore_errors=True)
    for folder in SEQUEL_FOLDERS:
        src = os.path.join(COOKED, folder)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(SEQUEL_COOKED, "Dungeons", "Content", folder))
    print("kept the Sequel Mod's blueprints in %s - run python tools/sequel.py build to put them in its pak"
          % SEQUEL_COOKED)


def run_script(name):
    write_settings()
    script = os.path.join(MOD, "unreal", "Scripts", name + ".py")
    out = script[:-3] + "_out.txt"
    if os.path.exists(out):
        os.remove(out)
    result = subprocess.run([EDITOR, PROJECT, "-run=pythonscript", "-script=" + script] + FLAGS,
                            capture_output=True, text=True, errors="replace")
    text = open(out).read() if os.path.exists(out) else "(the script wrote nothing - it stopped early)"
    print(text)
    if "ok   done" not in text:
        # a Python error stops the script without a FAIL line: show the editor's error lines
        print("\n".join(l for l in result.stdout.splitlines() if "Error" in l or "Traceback" in l)[-3000:])
        sys.exit("blueprint script failed")


def cook():
    shutil.rmtree(os.path.join(MOD, "unreal", "Saved", "Cooked"), ignore_errors=True)
    result = subprocess.run([EDITOR, PROJECT, "-run=cook", "-targetplatform=WindowsNoEditor"] + FLAGS,
                            capture_output=True, text=True, errors="replace")
    errors = [l for l in result.stdout.splitlines() if "Error:" in l]
    print("\n".join(errors[:20]) or "cook: no errors")
    if not os.path.isdir(COOKED):
        sys.exit("cook failed")


def game_running():
    tasks = subprocess.run(["tasklist"], capture_output=True, text=True, errors="replace").stdout
    return "Dungeons-Win64-Shipping" in tasks


def pack():
    if game_running():
        sys.exit("close the game first - it holds the pak open (the cook is done: run again with --pack)")
    shutil.rmtree(STAGE, ignore_errors=True)
    for folder in FOLDERS:
        src = os.path.join(COOKED, folder)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(STAGE, "Dungeons", "Content", folder))
    subprocess.run([sys.executable, U4PAK, "pack", OUT_PAK, "Dungeons"], cwd=STAGE, check=True)
    for root, _, files in os.walk(STAGE):
        for f in files:
            print("  " + os.path.relpath(os.path.join(root, f), STAGE))
    print("packed %s (%d bytes)" % (OUT_PAK, os.path.getsize(OUT_PAK)))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    if sys.argv[1] != "--pack":
        run_script(sys.argv[1])
    cook()
    keep_sequel_files()
    pack()
