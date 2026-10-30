"""Build the MCD Transmog blueprints (a mod of its own, apart from the Sequel Mod) and pack them into ~mods/MCDTransmog_P.pak.

    python tools/blueprints.py build_transmog          run unreal/Scripts/<script>.py, cook, pack
    python tools/blueprints.py --pack                  only cook and pack what the project has

Needs the Unreal 4.22 editor (UE_ROOT below) and the editor modules built once (unreal/Source; see decisions.md).
The pak holds only our folders: /Game/SequelMod and /Game/Actors/BP_AvatarInfo (the loader, a copy of the game's
own empty helper that starts our actors).
"""
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
FLAGS = ["-unattended", "-nop4", "-nosplash"]


def run_script(name):
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
    pack()
