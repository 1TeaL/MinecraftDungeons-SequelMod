# ![Minecraft Dungeons: Sequel Mod](docs/headers/sequel-mod.svg)

A rebalance mod for **Minecraft Dungeons** that makes more builds worth playing, also adding **Endless Apocalypse**:
Apocalypse Plus all the way to A+100, with rewards past the gear cap of 315.

**[Download the latest release](https://github.com/1TeaL/MinecraftDungeons-SequelMod/releases/latest)** ·
**[Every change, base game vs mod](https://claude.ai/artifact/4V6GgHUFDLGujvyUG6YNCz)**

## ![What it does](docs/headers/what-it-does.svg)

- **Endless Apocalypse.** A+26 to A+100. Gear power climbs to the game's cap (315) by A+38. Past that, levels
  unlock bonus built-in enchantments, extra armor perks, a final enchantment at A+100 and an endless
  Sharpness / Power / Protection ladder after it. Mobs keep getting tougher; loot, XP and gold keep improving.
  A+1 to A+25 are unchanged.
- **Rebalanced gear.** Weak and middling weapons, bows, enchantments, artifacts and armor perks are brought up to
  the strong ones. The top tier is left alone, and every unique beats its base item.
- **Seasonal uniques are back.** Event items drop in missions and show up at merchants, each with a build of its own.
- **Fairer mobs.** Enchanted mobs no longer roll Deflect or Levitation Shot.
- **Less grind in camp.** Blacksmith upgrades take one mission, merchants stock gear at your power level,
  and there's no slowdown after a roll.
- **Stacking builds.** 32 enchantments whose copies add up in full (Critical Hit, Swirling, Infinity, Protection,
  the Focuses and more) can roll in more than one slot of an item. The ones whose copies don't add up say so in
  their description.

The full list, with every number, is on the [changes page](https://claude.ai/artifact/4V6GgHUFDLGujvyUG6YNCz)
and in [CHANGES.md](CHANGES.md).

## ![Playing it](docs/headers/playing-it.svg)

You need the **Steam version** of Minecraft Dungeons on **Windows**. Nothing else: the release brings its own Python.

1. Download the `SequelMod` zip from the [latest release](https://github.com/1TeaL/MinecraftDungeons-SequelMod/releases/latest).
2. In Steam, right-click Minecraft Dungeons → **Manage** → **Browse local files**.
3. Extract the zip into that folder. You get `Mods\SequelMod` and `Play Sequel Mod.bat` next to the game.
4. Start the game with **`Play Sequel Mod.bat`** and keep its window open while you play.

Your saves are backed up at every start (`Mods\SequelMod\save_backups`). In multiplayer, everyone needs the mod.
To uninstall, delete `Mods\SequelMod` and `Dungeons\Content\Paks\~mods\SequelMod_P.pak`.

To start it from Steam's Play button instead, set Minecraft Dungeons → Properties → General → Launch Options to
`"<game folder>\Mods\SequelMod\steam_launch.bat" %command%`.

## ![How it works](docs/headers/how-it-works.svg)

The mod has two halves.

**The pak** (`SequelMod_P.pak`) replaces parts of the game's own data files: weapon stats, enchantment values,
artifact and armor perk values, descriptions, the card bars, and how the Apocalypse levels past A+25 scale.
The game loads it by itself from `~mods`, so it works anywhere the game runs.

**The launcher** (`tools/play.py`) handles what isn't in any data file. It runs next to the game and changes
values in the game's memory: the A+ level count, unique items' built-in enchantments, bonus enchantments that
follow the gear you own, merchant stock, Blacksmith upgrades and a few values the game calculates in code.
It only ever changes data, never the game's code; where it needs more room it reserves new memory and points
the game at it. It uses only Python's standard library, calling the Windows API through `ctypes`, which is
why it needs Windows for now (I believe on steam deck it shouldn't work but untested).

Every decision, with its reasons and what was tested, is logged in [decisions.md](decisions.md).

## ![Building it yourself](docs/headers/building-it-yourself.svg)

You'll need Python 3.11+, the game's files extracted to `Mods/Dungeons BMS/BMS output`, and the
Dungeons Mod Kit in `Mods/Dungeons-Mod-Kit-master` (for `u4pak.py`).

1. Change what you like in the settings. `SequelMod.toml` holds every value from the game's files, each line with
   the game's default as a comment; the other `.toml` files cover the rest (table below).
2. Build the pak:

   ```
   python tools/sequel.py build
   ```

   It goes straight into `Dungeons/Content/Paks/~mods`. If the game is running, it waits in `staged/` and the
   launcher installs it at the next start.
3. Start the game with `Play Sequel Mod.bat`.

| Command | What it does |
|---|---|
| `python tools/sequel.py diff` | List every value changed from the game's default |
| `python tools/sequel.py scan` | Re-read the game files and refresh `SequelMod.toml`, keeping your changes (run after a game update) |
| `python tools/change_sheet.py` | Rebuild `CHANGES.md` from the settings |
| `python tools/package.py` | Make the release zip in `dist/` |

### ![Settings](docs/headers/settings.svg)

| File | What it sets |
|---|---|
| `SequelMod.toml` | Every value stored in the game's files: enchantments, perks, A+ scaling |
| `SequelGear.toml` | Weapon and bow stats: damage, swing time, reach, fire rate, ammo |
| `SequelText.toml` | In-game text: descriptions and tooltips |
| `Endless.toml` | Endless Apocalypse: power and mob scaling past A+25, trials, unlocks |
| `Builtins.toml` | Unique items' built-in enchantments |
| `Bonus.toml` | Rewards past the gear cap: bonus enchantments, armor perks, the A+100 ladder, gilding, merchants, Blacksmith |
| `Perks.toml`, `Artifacts.toml`, `ArtifactScaling.toml` | Armor perks, artifact cooldowns, artifacts above the cap |
| `Formulas.toml`, `Echo.toml` | Enchantment values the game calculates in code |
| `Drops.toml`, `MobPool.toml`, `MobEnchants.toml` | Seasonal drops, what enchanted mobs can roll |
| `Prices.toml`, `QoL.toml`, `Player.toml` | Merchant prices, Blacksmith, movement |
| `Launcher.toml` | Turn each part of the launcher on or off |
| `StackNotes.toml` | Which enchantments stack when an item carries several copies (tested in game) |

### ![Research tools](docs/headers/research-tools.svg)

`research/` holds the scripts used to find where things live in the game's memory, with notes per gear type.
UE4SS was used to dump classes and default values: the Steam exe is packed, so stock UE4SS crashes it. A
one-byte patched `UE4SS.dll`, loaded late with `python tools/inject_ue4ss.py`, works; `tools/probe.py` then runs
Lua in the game. `tools/dumpimage.py` and `tools/disasm.py` save and disassemble the unpacked exe offline.

The spreadsheets (`Enchantment_Rebalance.xlsx`, `Gear_Rebalance.xlsx` and the two tier lists) and the
`*_Opinions.md` notes are the community research behind the balance choices.
