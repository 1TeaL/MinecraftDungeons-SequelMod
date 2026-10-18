# ![Minecraft Dungeons: Sequel Mod](docs/headers/sequel-mod.svg)

A rebalance mod for **Minecraft Dungeons** that makes more builds worth playing, also adding **Endless Apocalypse**:
Apocalypse Plus all the way to A+100, with rewards past the gear cap of 315.

**[Download the latest release](https://github.com/1TeaL/MinecraftDungeons-SequelMod/releases/latest)** ·
**[Every change, base game vs mod](https://claude.ai/artifact/4V6GgHUFDLGujvyUG6YNCz)**

## ![What it does](docs/headers/what-it-does.svg)

- **Endless Apocalypse.** Apocalypse Plus goes past 25, all the way to A+100; A+1 to A+25 are unchanged. Higher
  levels open a few at a time as you beat different boss missions on your top level, with trial levels along the
  way that push one thing hard (more mobs, more enchanted mobs, tankier or harder-hitting ones).
- **Rewards past the gear cap.** Gear power reaches the game's cap (315) at A+38, and from there it keeps rising to
  365 at A+100. Instead of raw stats, the higher power adds **bonus built-in enchantments**: extra enchantments on
  the item card that cost no enchantment points, growing a tier at a time. Armor gets extra perks, artifacts keep
  getting stronger (up to 5x damage), and from A+26 a drop can come gilded with a free enchantment.
- **A+100 never stops.** A+100 drops come in a little above your power level, so your gear keeps climbing, and every
  5 power past 365 adds another tier of Sharpness, Power or Protection under the other enchantments.
- **Tougher mobs to match.** From A+38 to A+100 mobs get up to 5x the health, 3x the damage and a little faster;
  your healing, which Apocalypse cuts, comes back to full.
- **Rebalanced gear.** Weak and middling weapons, bows, enchantments, artifacts and armor perks are brought up to
  the strong ones; the top tier is left alone. Bonus Shot's second arrow deals 75% instead of 24%, Echo repeats
  every 0.1 s at tier III instead of 3 s, Cowardice and Frenzied give up to +60%.
- **Uniques with more identity.** Many uniques got new or stronger built-in enchantments - the Whispering Spear's
  Echo is tier III, the Bonehead Hammer pulls mobs in *and* explodes them - and every unique beats its base item.
- **Seasonal uniques outside the Tower.** Event items, normally only from the Tower, drop in missions and show up at
  merchants, each with built-in enchantments for a build of its own.
- **Stacking builds.** 32 enchantments that add up when an item has them more than once (Critical Hit, Swirling,
  Infinity, Protection, the Focuses and more) can roll in more than one slot. The ones that don't add up say so in
  their description.
- **Fairer mobs.** Enchanted mobs no longer roll Deflect or Levitation Shot.
- **Less grind in camp.** Blacksmith upgrades take one mission, Enchantsmith rerolls cost a tenth, gilded gear at
  the Piglin merchant costs half, merchants stock gear at your power level, and there's no slowdown after a roll.

The full list, with every number, is on the [changes page](https://claude.ai/artifact/4V6GgHUFDLGujvyUG6YNCz)
and in [CHANGES.md](CHANGES.md).

## ![Why it was made](docs/headers/why-it-was-made.svg)

I loved Minecraft Dungeons with my friends. When Minecraft Dungeons 2 was announced I was hyped: an open world,
new items, new gear systems. But as release went on it got frustrating. The quality-of-life changes the first game
picked up over the years, like storage, were gone again. Playing with friends is tedious with the split between
offline and online play and progress that doesn't carry over. Enchanting exactly what you want sounds good, but with
only one slot and the new random effects it's still a chore. Then there are the arbitrary currency caps, the level
cap that limits how many builds you can have, and no difficulty levels in the endgame - the list goes on.

So I wanted to update the first game instead and make it feel like a sequel. The main goal was more build variety;
the other was more content, so there's more of the game to play.

- **Build variety:** the low-tier weapons and enchantments are buffed so more of them are worth using.
- **More to play:** more Apocalypse levels to keep the grind going.
- **Growing past the cap:** as the Tower glitch showed, gear power naturally caps out around 316. So past that point
  the mod adds extra enchantments to weapons and extra perks to armor, so gear keeps getting stronger and there are
  new ways to build. The enchantments build on each weapon's or armor's playstyle: what's core to the item stays,
  and more interesting enchantments get slotted in beside it. Each item type has a set list of these bonus
  enchantments, and they gain a tier every few power levels, up to Apocalypse 100. Artifacts scale with gear power
  too, so they stay relevant.
- **Mobs past the cap:** mobs stop scaling past that point as well, so their stats are raised by the mod from there.
  Letting them scale the game's own way all the way to A+100 would have made the numbers insane (around a million
  times the health and damage) - more than the game is likely to handle, and more than any build could fight.
- **New items without new items:** the seasonal uniques are reworked from their base uniques, with different stats
  and different enchantments, which adds new items to the pool without making new ones from scratch.

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

## ![How it was made](docs/headers/how-it-was-made.svg)

Most Dungeons mods stop at the pak: unpack the game's files, change the numbers Mojang left in them, repack.
This mod also reads the asset files with its own reader to find every tunable value, and adds settings that only
exist in the game's code (dumped with UE4SS) into the assets so the pak can change them too. For the rest, it reads
the running game: where item and enchantment definitions, built-in enchantments, quests, shop stock and the
Apocalypse level count live in memory, and, from a disassembled copy of the game's program, how code-calculated
values like an enchantment's per-tier numbers are worked out. The launcher then changes only that data.

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
