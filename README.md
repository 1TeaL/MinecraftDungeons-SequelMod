# ![Minecraft Dungeons: Sequel Mod](docs/headers/sequel-mod.svg)

A rebalance mod for **Minecraft Dungeons** that makes more builds worth playing, also adding **Endless Apocalypse**:
Apocalypse Plus all the way to A+100, with rewards past the gear cap of 315.

**[Download the latest release](https://github.com/1TeaL/MinecraftDungeons-SequelMod/releases/latest)** ·
**[Every change, base game vs mod](CHANGES.md)**

## ![What it does](docs/headers/what-it-does.svg)

- **Head Start (optional).** A new character can skip the Default and Adventure difficulties: Apocalypse is
  unlocked, the character starts at level 60, and a starter kit of gear at Apocalypse power waits in the inventory.
  Only the difficulty is skipped - the map, the missions, the camp's merchants and every unique are still yours to
  unlock and grind out, now with Apocalypse loot from the first mission. On by default; in `Settings.toml`
  (section HEAD START) `"off"` plays from the start as normal, `"adventure"` starts at Adventure and level 30.
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

**The biggest enchantment changes** (tier III unless noted):

| Enchantment | Base game | Mod |
|---|---|---|
| Rampaging, Thundering, Radiance, Radiance Shot | trigger 10-50% of the time | **always trigger** (Radiance heals less per proc, Thundering's bolt is smaller) |
| Critical Hit | x3 damage | **x5** |
| Bonus Shot | second arrow 24% damage | **75%** |
| Echo | repeats every 3 s | **every 0.1 s** |
| Thorns | returns part of the damage you take | **5x as much** (mobs' Thorns weakened instead) |
| Burning, Fire Trail | 5 / 20 damage | **3x** |
| Stunning | +5% chance per tier | **+15%** |
| Fire, Lightning and Poison Focus | +25% per tier | **+50%** |
| Fuse Shot | explodes after 1 s | **almost at once, 2x damage, 1.5x radius** |
| Cowardice, Frenzied | +40% / +30% | **+60%** |
| Explorer | heals every 100 blocks explored | **every 10** |

The full list, with every number, is in [CHANGES.md](CHANGES.md).

## ![Why it was made](docs/headers/why-it-was-made.svg)

I loved Minecraft Dungeons with my friends. When Minecraft Dungeons 2 was announced I was pretty hyped. An open world, new items, new gear systems. But as release went on it got frustrating. The quality-of-life changes the first game picked up over the years, like storage, were gone again. Playing with friends is tedious with the split between
offline and online play and progress that doesn't carry over. Enchanting exactly what you want sounds good, but with only one slot and the new random effects it's still a chore. Then there are the arbitrary currency caps, the level
cap that limits how many builds you can have, and no difficulty levels in the endgame, there's just a lot of issues and you can tell they doing the thing where the DLC is where the content of the game will be..

So I wanted to update the first game instead and make it feel like a sequel. The main goal was more build variety;
the other was more content, so there's more of the game to play. Part of the fun of build crafting is finding crazy, overpowered builds, so the mod lifts weak gear and enchantments up rather than cutting the strong ones down.

- **Build variety:** the low-tier weapons and enchantments are buffed so more of them are worth using.
- **More to play:** more Apocalypse levels to keep the grind going.
- **Growing past the cap:** as the Tower glitch showed, gear power naturally caps out around 316. So past that point the mod adds extra enchantments to weapons and extra perks to armor, so gear keeps getting stronger and there are
  new ways to build. The enchantments build on each weapon's or armor's playstyle: what's core to the item stays,
  and more interesting enchantments get slotted in beside it. Each item type has a set list of these bonus
  enchantments, and they gain a tier every few power levels, up to Apocalypse 100. Artifacts scale with gear power
  too, so they stay relevant.
- **Mobs past the cap:** mobs stop scaling past that point as well, so their stats are raised by the mod from there.
  Letting them scale the game's own way all the way to A+100 would have made the numbers insane (around a million
  times the health and damage) - more than the game is likely to handle, and more than any build could fight.
- **New items without new items:** the seasonal uniques are reworked from their base uniques, with different stats
  and different enchantments, which adds new items to the pool without making new ones from scratch.
- **Full customisability:** don't like any of my changes? want to tweak things on your own? that's completely fine. I've tried to expose as much as possible under the settings so that anyone can build the mod themselves. The mod will always be open source and free.

## ![Playing it](docs/headers/playing-it.svg)

You need the **Steam version** of Minecraft Dungeons on **Windows**. Nothing else: the release brings its own Python.

1. Download `SequelMod-1.0-with-Transmog.zip` from the [latest release](https://github.com/1TeaL/MinecraftDungeons-SequelMod/releases/latest).
   Only want the Sequel Mod? Take `SequelMod-1.0.zip`. Only want the transmog? See [MCD Transmog](#mcd-transmog) below.
2. In Steam, right-click Minecraft Dungeons → **Manage** → **Browse local files**.
3. Extract the zip into that folder. You get `Mods\SequelMod` and `Play Sequel Mod.bat` next to the game.
4. Start the game with **`Play Sequel Mod.bat`** and keep its window open while you play.

Your saves are backed up at every start (`Mods\SequelMod\save_backups`). In multiplayer, everyone needs the mod.
To uninstall, delete `Mods\SequelMod` and `Dungeons\Content\Paks\~mods\SequelMod_P.pak`.

**Settings:** `Mods\SequelMod\Settings.toml` has the options most players want in one file: starting in
Apocalypse and at what level, Blacksmith missions, gilded drop chances, reroll prices, which mob enchantments
are on, and a switch for each part of the mod. Edit it with Notepad, save, and start through `Play Sequel Mod.bat`;
no rebuild needed. The detailed files behind it are in `settings\launcher`.

To start it from Steam's Play button instead, set Minecraft Dungeons → Properties → General → Launch Options to
`"<game folder>\Mods\SequelMod\steam_launch.bat" %command%`.

## ![MCD Transmog](docs/headers/mcd-transmog.svg)

**MCD Transmog** is an optional, separate mod made alongside the Sequel Mod: change how your gear looks without
changing what it does.

- **One look per slot.** Pick one look for your melee weapon, one for your ranged weapon and one for your armor.
  Every item in that slot wears it while it's chosen; swings, stats, shots and enchantments stay the item's own.
- **In-game menu.** Press **Y** in camp or in a mission. The Melee / Ranged / Armor tabs show the items your
  character has found, with their icons. Click one to wear its look; "Own looks" switches that slot back. Choices
  are saved across missions and restarts, and the menu key can be changed at the bottom of the menu.
- **Separate.** It's its own pak file (`MCDTransmog_P.pak`) and needs neither the Sequel Mod nor the launcher; the
  Sequel Mod doesn't need it either. It comes in `SequelMod-1.0-with-Transmog.zip`, or on its own in
  `MCD-Transmog-1.0.zip` from the [MCD Transmog release](https://github.com/1TeaL/MinecraftDungeons-SequelMod/releases/tag/transmog-v1.0)
  (unpack into the game folder; nothing else to run).
- **To remove it,** delete `Dungeons\Content\Paks\~mods\MCDTransmog_P.pak` and its readme. Your items go back to
  their own looks and the Sequel Mod keeps working.

It never touches your character saves: the looks are kept in their own file, `SequelLooks.sav`. Keyboard and mouse
only for now; tested in single player. It's built from blueprints made by script (`unreal/Scripts/build_transmog.py`,
packed with `python tools/blueprints.py build_transmog`), which needs the Unreal 4.22 editor - players don't.

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

I designed the Sequel Mod and made all the balance decisions; I built it with the help of Claude, an AI assistant. Claude did the technical work I couldn't do myself: reading the game's packed files, working out where the game keeps its values while it runs, and writing the tools that change them. I tested everything in game and decided what stayed - every decision, with its reasons, is in [decisions.md](decisions.md).

Most Dungeons mods stop at the pak: unpack the game's files, change the numbers Mojang left in them, repack.
This mod also reads the asset files with its own reader to find every tunable value, and adds settings that only
exist in the game's code (dumped with UE4SS) into the assets so the pak can change them too. For the rest, it reads
the running game: where item and enchantment definitions, built-in enchantments, quests, shop stock and the
Apocalypse level count live in memory, and, from a disassembled copy of the game's program, how code-calculated
values like an enchantment's per-tier numbers are worked out. The launcher then changes only that data.

## ![Building it yourself](docs/headers/building-it-yourself.svg)

The balance in this mod is my own take on the game - what felt weak, what felt right. If you see it differently, every number is yours to change: weapon stats, enchantments, armor perks, artifacts, mob scaling, rewards and the camp are all plain settings files with the game's own value next to each line.

You'll need Python 3.11+, the game's files extracted to `Mods/Dungeons BMS/BMS output`, and the
Dungeons Mod Kit in `Mods/Dungeons-Mod-Kit-master` (for `u4pak.py`).

1. Change what you like. `Build.toml` has the big dials (mob health, damage and speed per A+ level, healing, XP,
   loot, movement); `settings/build/SequelMod.toml` holds every value from the game's files, each line with the
   game's default as a comment; the other files cover the rest (table below).
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
| `python tools/sequel.py scan` | Re-read the game files and refresh `settings/build/SequelMod.toml`, keeping your changes (run after a game update) |
| `python tools/change_sheet.py` | Rebuild `CHANGES.md` from the settings |
| `python tools/package.py` | Make the release zip in `dist/` |

### ![Settings](docs/headers/settings.svg)

| File | What it sets |
|---|---|
Two central files sit in the mod's main folder; the detailed files are in `settings/`. Each setting lives in
one place only.

| File | What it sets | After a change |
|---|---|---|
| `Settings.toml` | The player settings: a switch for each part, starting difficulty and kit, Blacksmith, gilded chances, prices, mob enchantments, A+ unlocks | Restart through the launcher |
| `Build.toml` | The big dials: mob health, damage and speed per A+ level, healing, XP, loot, movement | Rebuild |
| `settings/launcher/Builtins.toml` | Unique items' built-in enchantments | Restart |
| `settings/launcher/Bonus.toml` | Rewards past the gear cap: bonus enchantments, armor perks, the A+100 ladder, merchant stock | Restart |
| `settings/launcher/Perks.toml`, `Artifacts.toml`, `ArtifactScaling.toml` | Armor perks, artifact cooldowns, artifacts above the cap | Restart |
| `settings/launcher/Formulas.toml`, `Echo.toml`, `Stack.toml` | Enchantment values the game calculates in code, which enchantments stack | Restart |
| `settings/launcher/Drops.toml`, `MobPool.toml`, `MobEnchants.toml` | Seasonal drops, what enchanted mobs can roll | Restart |
| `settings/launcher/Prices.toml`, `Unlock.toml` | The other merchants' prices, boss missions per A+ step | Restart |
| `settings/build/SequelMod.toml` | Every value stored in the game's files: enchantments, perks, artifacts, A+1-25 | Rebuild |
| `settings/build/SequelGear.toml` | Weapon and bow stats: damage, swing time, reach, fire rate, ammo | Rebuild |
| `settings/build/SequelText.toml` | In-game text: descriptions and tooltips | Rebuild |
| `settings/build/Endless.toml` | Gear power past A+25, trial levels, the finale | Rebuild |
| `settings/build/StackNotes.toml` | Which enchantments stack when an item carries several copies (tested in game) | Rebuild |
| `NAMES.md` | The legend: every internal enchantment and item name next to its in-game name |

### ![Research tools](docs/headers/research-tools.svg)

`research/` holds the scripts used to find where things live in the game's memory, with notes per gear type.
UE4SS was used to dump classes and default values: the Steam exe is packed, so stock UE4SS crashes it. A
one-byte patched `UE4SS.dll`, loaded late with `python tools/inject_ue4ss.py`, works; `tools/probe.py` then runs
Lua in the game. `tools/dumpimage.py` and `tools/disasm.py` save and disassemble the unpacked exe offline.

The spreadsheets (`Enchantment_Rebalance.xlsx`, `Gear_Rebalance.xlsx` and the two tier lists) and the
`*_Opinions.md` notes are the community research behind the balance choices.
