"""Start Minecraft Dungeons with the Sequel Mod.

    python tools/play.py              # back up saves, install the pak if needed, start the game,
                                      # then apply Builtins.toml (unique items' built-in enchantments)
    python tools/play.py --endless    # same, plus Endless Apocalypse: A+ up to 100

The .pak works on its own; a normal Steam launch plays the mod with the usual 25 A+ levels. Endless
Apocalypse needs this launcher because the level cap is built into the game: the launcher changes it
in the running game's memory (data only - no game code is modified, nothing on disk changes, and it's
gone when the game closes). If the game is already running, --endless just applies it.
"""
import ctypes
import ctypes.wintypes as wt
import filecmp
import os
import shutil
import subprocess
import sys
import time
import tomllib
import zipfile
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import accelerate_patch  # noqa: E402
import aplus_patch  # noqa: E402
import builtins_patch  # noqa: E402
import bonus_watch  # noqa: E402
import cap_patch  # noqa: E402
import drops_patch  # noqa: E402
import echo_patch  # noqa: E402
import endless_patch  # noqa: E402
import formula_patch  # noqa: E402
import arrows_patch  # noqa: E402
import artifact_scale  # noqa: E402
import artifacts_patch  # noqa: E402
import perks_patch  # noqa: E402
import prices_patch  # noqa: E402
import live_objects  # noqa: E402
import memprobe  # noqa: E402
import mob_enchants  # noqa: E402
import mobpool_patch  # noqa: E402
import qol_patch  # noqa: E402
import stack_patch  # noqa: E402
import start_kit  # noqa: E402
import settings  # noqa: E402

STEAM_APP_ID = 1672970
# The game folder: the first folder above this one with Dungeons/Content/Paks in it - normally two up
# (<game>/Mods/SequelMod/tools), also when the zip was unpacked one folder too deep (Windows "Extract All").
GAME = next((p for p in HERE.parents if (p / "Dungeons" / "Content" / "Paks").is_dir()), None)
MODS_DIR = GAME / "Dungeons" / "Content" / "Paks" / "~mods" if GAME else None
PAK = "SequelMod_P.pak"
SAVES = Path.home() / "Saved Games" / "Mojang Studios" / "Dungeons"
BACKUPS = HERE.parent / "save_backups"
SWITCHES = settings.path("Launcher.toml")
KEEP_BACKUPS = 10
SETTLE = 15  # seconds after start before the launcher looks (user, 2026-10-06; was 40)
SETTLE_MAX = 90  # ...and the longest it waits for the game's data to be there


def backup_saves():
    if not SAVES.exists():
        print(f"No saves found at {SAVES} - skipping backup")
        return
    BACKUPS.mkdir(exist_ok=True)
    dest = BACKUPS / f"saves_{datetime.now():%Y-%m-%d_%H%M%S}.zip"
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for f in SAVES.rglob("*"):
            if f.is_file():
                z.write(f, f.relative_to(SAVES))
    for old in sorted(BACKUPS.glob("saves_*.zip"))[:-KEEP_BACKUPS]:
        old.unlink()
    print(f"Saves backed up to {dest}")


def install_pak():
    """A build made while the game was running waits in staged/: move it into the game. A release bundle
    ships the pak next to the launcher; copy it into the game if it's newer."""
    if MODS_DIR is None:
        print(f"Can't find the game folder above {HERE.parent} - the SequelMod folder belongs in the Minecraft Dungeons "
              "folder (Steam: right-click the game > Manage > Browse local files), as Mods/SequelMod. "
              "The mod's stat changes aren't installed.")
        return
    staged = HERE.parent / "staged" / PAK
    if staged.exists() and not aplus_patch.pid_of():
        MODS_DIR.mkdir(parents=True, exist_ok=True)
        shutil.move(str(staged), str(MODS_DIR / PAK))
        print(f"Installed the rebuilt {PAK}")
    for src in (HERE / PAK, HERE.parent / PAK):
        if src.exists():
            dest = MODS_DIR / PAK
            if not dest.exists() or not filecmp.cmp(src, dest, shallow=False):
                MODS_DIR.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dest)
                print(f"Installed {PAK}")
            return
    if not (MODS_DIR / PAK).exists():
        print(f"Warning: {PAK} isn't installed - the stat changes won't be active")


def game_age(h):
    """Seconds since the game process started."""
    times = [wt.FILETIME() for _ in range(4)]
    ctypes.windll.kernel32.GetProcessTimes(h, *[ctypes.byref(t) for t in times])
    now = wt.FILETIME()
    ctypes.windll.kernel32.GetSystemTimeAsFileTime(ctypes.byref(now))
    ticks = lambda t: t.dwHighDateTime << 32 | t.dwLowDateTime  # noqa: E731
    return (ticks(now) - ticks(times[0])) / 1e7


def ready(h, base):
    """True once the data the launcher changes exists: the eight A+ unlock steps and an item definition."""
    try:
        steps = endless_patch.read_steps(h, base)[0]
        _, cur = builtins_patch.builtins(h, base, builtins_patch.TEMPLATE_ITEM)
        return len(steps) >= 8 and all(level for _, level in steps) and bool(cur)
    except (SystemExit, Exception):  # noqa: B014 - not there yet
        return False


def wait_for_game(timeout=240):
    """Wait until the game has unpacked its code and built the data the launcher changes; returns (handle, base).

    The item definitions, Blueprint functions and A+ unlock steps are made during startup. From SETTLE seconds
    after start the launcher checks every second whether they are there, and goes ahead when they are
    (or at SETTLE_MAX seconds regardless; each part then says for itself if it could not be applied).
    """
    end = time.time() + timeout
    said = False
    while time.time() < end:
        h, base = aplus_patch.open_game()
        if h and aplus_patch.unpacked(h, base):
            age = game_age(h)
            if age >= SETTLE_MAX or (age >= SETTLE and ready(h, base)):
                return h, base
            if not said:
                print("Waiting for the game to finish starting...")
                said = True
        time.sleep(1)
    sys.exit("Minecraft Dungeons didn't start in time")


class Tee:
    """Everything the launcher prints also goes to launcher.log (the last session's messages, to look at afterwards)."""

    def __init__(self, stream, path):
        self.stream = stream
        self.file = open(path, "w", encoding="utf-8", buffering=1)
        self.file.write(f"launcher started {datetime.now():%Y-%m-%d %H:%M:%S}\n")

    def write(self, text):
        self.file.write(text)
        return self.stream.write(text) if self.stream else len(text)

    def flush(self):
        self.file.flush()
        if self.stream:
            self.stream.flush()


if __name__ == "__main__":
    try:
        sys.stdout = Tee(sys.stdout, Path(__file__).resolve().parent.parent / "launcher.log")
    except OSError:
        pass
    # --run <command...>: start this command instead of going through Steam. Used from Steam's Launch
    # Options ("...steam_launch.bat" %command%), so the Play button runs the launcher.
    run = sys.argv[sys.argv.index("--run") + 1:] if "--run" in sys.argv else None
    endless = "--endless" in sys.argv[:sys.argv.index("--run")] if run is not None else "--endless" in sys.argv
    for problem in settings.problems():   # a typo in Settings.toml: say so, keep going
        print(problem)
    install_pak()
    h, base = aplus_patch.open_game()
    if not h:
        backup_saves()
        try:
            start_kit.apply()            # Settings.toml [start]: Apocalypse unlocked, starter kit (save edit, game closed)
        except Exception as e:  # noqa: BLE001 - never stop the launcher
            print(f"Start in Apocalypse NOT applied: {e}")
        # A crash reporter left open from an earlier crash makes Steam think the game is still running.
        subprocess.run(["taskkill", "/IM", "CrashReportClient.exe", "/F"], capture_output=True)
        if run:
            subprocess.Popen(run)
        else:
            os.startfile(f"steam://rungameid/{STEAM_APP_ID}")
        print("Starting Minecraft Dungeons...")
    switches = settings.load(SWITCHES)
    endless_on = endless and switches.get("endless", True)
    endless_done = []

    def early_endless(h, base):
        try:
            endless_patch.apply(h, base)
        except (SystemExit, Exception):  # noqa: B014 - not ready yet: tried again, and once more after startup
            return False
        print("Endless Apocalypse is on for this session (A+ up to 100 in the mission select).")
        endless_done.append(True)
        return True

    # The Endless part goes first: the mission map keeps the level list it saw when first opened.
    h, base = wait_for_game()
    if endless_on:
        early_endless(h, base)
    # A part that can't be applied (e.g. after a game update) says why and is skipped; the game runs on.
    try:
        if switches.get("builtins", True):
            builtins_patch.apply(h, base)
        else:
            print("Built-in enchantments: off (Settings.toml)")
    except (SystemExit, Exception) as e:  # noqa: B014 - never let a failed part stop the launcher
        print(f"Built-in enchantments NOT applied: {e}")
    try:
        if switches.get("builtins", True):
            perks_patch.apply(h, base)
            artifacts_patch.apply(h, base)
    except (SystemExit, Exception) as e:  # noqa: B014
        print(f"Armor perks NOT applied: {e}")
    try:
        if switches.get("seasonal_drops", True):
            drops_patch.apply(h, base, quiet=True)      # usually too early: the watcher below repeats it
    except (SystemExit, Exception) as e:  # noqa: B014
        print(f"Seasonal mission drops NOT applied: {e}")
    try:
        if switches.get("mob_pool", True):
            mobpool_patch.apply(h, base)
    except (SystemExit, Exception) as e:  # noqa: B014
        print(f"Mob enchantment pool NOT changed: {e}")
    try:
        if switches.get("formulas", True):
            accelerate_patch.apply(h, base)
    except (SystemExit, Exception) as e:  # noqa: B014
        print(f"Accelerate's speed limit NOT changed: {e}")
    try:
        if switches.get("qol", True):
            qol_patch.apply(h, base)
    except (SystemExit, Exception) as e:  # noqa: B014
        print(f"Quality-of-life changes NOT applied: {e}")
    try:
        if switches.get("stacking", True):
            stack_patch.apply(h, base)
    except (SystemExit, Exception) as e:  # noqa: B014
        print(f"Enchantment stacking NOT applied: {e}")
    try:
        if endless_on:
            endless_patch.apply(h, base)      # again after startup: harmless when already done, a retry when not
            if not endless_done:
                print("Endless Apocalypse is on for this session (A+ up to 100 in the mission select).")
        elif endless:
            print("Endless Apocalypse: off (Settings.toml)")
    except (SystemExit, Exception) as e:  # noqa: B014 - never let a failed part stop the launcher
        print(f"Endless Apocalypse NOT applied: {e}")
    try:
        if endless and switches.get("endless", True) and switches.get("cap", False):
            cap_patch.apply(h, base)
    except (SystemExit, Exception) as e:  # noqa: B014 - never let a failed part stop the launcher
        print(f"Power cap NOT raised: {e}")
    # Stay until the game closes: Steam counts the game as running while this launcher runs, and gear above the
    # power cap gets its bonus built-in enchantments as it turns up (Bonus.toml).
    scanner = live_objects.Scanner(h, base, wait=False)   # results come in as the game is looked through
    watchers = []
    if switches.get("seasonal_drops", True):
        watchers.append(drops_patch.Drops(h, base))
    if endless and switches.get("endless", True) and switches.get("bonus", True):
        watchers.append(bonus_watch.Watch(h, base, scanner))
        print("Watching for gear above the power cap (bonus enchantments)...")
    if switches.get("echo", True):
        watchers.append(echo_patch.EchoWatch(h, base, scanner))
    if endless_on and switches.get("artifact_scaling", True):
        watchers.append(artifact_scale.ArtifactScale(h, base, scanner))
    if switches.get("prices", True):
        watchers.append(prices_patch.Prices(h, base, scanner))
    if switches.get("arrows", True):
        watchers.append(arrows_patch.Arrows(h, base, scanner))
    if switches.get("mob_enchants", True):
        watchers.append(mob_enchants.MobEnchants(h, base, scanner))
    if switches.get("formulas", True):
        watchers.append(formula_patch.Formulas(h, base, scanner))
    if switches.get("qol", True):
        watchers.append(qol_patch.Blacksmith(h, base, scanner))
    # Five passes a second. Most of them only ask the game's object list what is new (a few milliseconds) and let
    # the watchers that must catch an object as it appears - a mob's Deflect, a newly equipped Echo - deal with
    # just that; every fifth pass goes over everything known for those watchers and the prices, every fifteenth
    # (3 s) for the rest, as before.
    quick = (echo_patch.EchoWatch, mob_enchants.MobEnchants, formula_patch.Formulas)
    each_second = quick + (prices_patch.Prices, qol_patch.Blacksmith)
    passes, complained = 0, {}

    def trouble(where, e):
        """A bad read (level loading, game closing) must not end the launcher, nor one watcher stop the others."""
        key = f"{where}: {e!r}"
        if memprobe.alive(h) and time.time() - complained.get(key, 0) > 60:
            complained[key] = time.time()                  # the same trouble at most once a minute
            print(f"  (watchers: {where} skipped a pass: {e!r})")

    def run(chosen):
        for watch in chosen:
            try:
                watch.tick()
            except Exception as e:  # noqa: BLE001
                trouble(type(watch).__name__, e)

    while memprobe.alive(h):
        try:
            if watchers and passes % 5 == 0:
                scanner.refresh()
                run(w for w in watchers if passes % 15 == 0 or isinstance(w, each_second))
            elif watchers:
                young = scanner.poll()
                if young:
                    everything, scanner.found = scanner.found, young
                    try:
                        run(w for w in watchers if isinstance(w, quick))
                    finally:
                        scanner.found = everything
        except Exception as e:  # noqa: BLE001
            trouble("the object list", e)
        passes += 1
        time.sleep(0.2 if watchers else 5)
    # The game closed: characters made this session get Apocalypse and the kit now, ready for the next start.
    time.sleep(10)                       # let the game finish writing its saves
    try:
        start_kit.apply()
    except Exception as e:  # noqa: BLE001
        print(f"Start in Apocalypse NOT applied: {e}")
