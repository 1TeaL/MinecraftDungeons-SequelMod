The Sequel Mod for Minecraft Dungeons, version 1.0: more builds worth playing, new enchantments, and **Endless Apocalypse** - Apocalypse Plus all the way to A+100, with rewards past the gear cap of 315.

**Start here**
1. Extract `SequelMod-1.0-with-Transmog-Loadouts-and-Reroll.zip` into the game folder (Steam → right-click Minecraft Dungeons → Manage → Browse local files). Only want the Sequel Mod? Use `SequelMod-1.0.zip` instead.
2. Start the game with `Play Sequel Mod.bat` and keep its window open while you play. Your saves are backed up first, to `Mods\SequelMod\save_backups`.
3. Make a **new character**: Head Start puts it straight into Apocalypse at level 60 with a starter kit. The map, missions, merchants and uniques are still yours to earn. Characters you already have are left as they are.
4. Want to change something? Open `Mods\SequelMod\Settings.toml` in Notepad, save, and start the game again. Everything has a header and a note; set Head Start to `"off"` there to play from the beginning, or `"adventure"` to start at Adventure and level 30.

Had an earlier download (the 1.0 beta)? Extract the new zip over it. `Settings.toml` is replaced with the new file, so note any changes you made first.

**What it does**
- **Endless Apocalypse:** Apocalypse Plus all the way to A+100, unlocked a few levels at a time by beating boss missions, with trial levels along the way. A+1 to A+25 are unchanged.
- **Super bosses:** on A+25, the gates into each trial (A+55, 64, 73, 82, 91) and A+100, bosses take 0.6x damage and hit 1.25x harder. The gates drop better loot than the levels around them.
- **Rewards past the gear cap:** gear power reaches 315 at A+38 and keeps rising to 365 at A+100, adding bonus built-in enchantments, extra armor perks and stronger artifacts. A+100 never stops: drops keep climbing and every 5 power adds another Sharpness / Power / Protection tier.
- **Every weapon a build of its own:** weak and middling weapons, bows, artifacts and armor perks lifted toward the top tier; the strongest are left alone. Uniques got new or stronger built-ins and a feel of their own, and every unique beats its base item. Past the gear cap each item gains bonus enchantments picked for its build - fire, poison, frost, lightning, soul, stealth, crits, area damage, charged shots, explosives and more - and no two items get the same set.
- **Seasonal uniques outside the Tower:** they drop in missions and show up at merchants, each with its own build.
- **Fairer mobs:** no Deflect, Levitation Shot or Gravity Pulse on enchanted mobs; mobs get tougher past A+38 (more health, damage and a little speed) while your healing comes back.
- **Less grind in camp:** one-mission Blacksmith, rerolls at a tenth of the price, gilded gear at half price, merchants that stock gear at your power, no slowdown after a roll.
- **Head Start:** skip the early difficulties on a new character (on by default, see above).

**Enchantments**
- **Every enchantment reworked or tuned:** each combat enchantment is a real pick at any difficulty - Critical Hit x5, Bonus Shot's second arrow 75%, Echo every 0.1 s, Radiance always triggers, Cowardice and Frenzied up to +60%, Supercharge x1.8, Soul Focus like the other Focuses, and more. Copies of most enchantments add up, and 27 that make a stacking build can roll in more than one slot.
- **Kill credit:** on-kill enchantments (Leeching, Refreshment, Exploding, Rampaging, Guarding Strike, Shadowcloak) count every kill that is yours - by fire, poison, lightning, Shockwave, explosions or artifacts too, not only your weapon's last hit.
- **Fire, poison and lightning keep up:** burning and poisoned mobs (wherever they are), and the mobs your lightning strikes, lose a share of their max health, so they stay useful at any difficulty. Fire Aspect also sets mobs on fire with your arrows (and rolls on bows), and Shock Web's beams charge mobs for Overload.
- **New enchantments:**
  - **Status payoffs:** Ignite (burning mobs), Venom Siphon (poisoned mobs, and it heals you), Shatter (chilled or frozen mobs) and Overload (lightning that charges mobs and arcs between them).
  - **Continuous attacking:** Relentless (stacking damage and attack speed) and Battle Hardened (stacking damage resistance).
  - **Melee and kills:** Sweeping Edge (every melee hit splashes the mobs around) and Shadowcloak (Shadow Form on a kill).
  - **Potions:** Bottomless Brew (extra potion drinks), Barrier Brew (less damage for you and allies), Buddy Brew (healing over time for you, allies and pets) and Ancient Alchemy (souls).
  - **Armor:** Last Stand (less damage below half health) and Artifact Amplifier (more artifact damage and souls).
- The mod changes no game code, so each new enchantment takes over the slot of a weak or unused one, and some cards show their numbers in the description instead of the tier rows. The README explains why.

**MCD Transmog, Loadouts and Reroll (bundled by default)**
- **What it does:** change how your gear looks without changing what it does, save whole sets of gear (looks included), and reroll the gear you wear - a new copy of the same kind, or an exact copy of a unique with its gilding, for emeralds or gold. A way to target the drops you want, at a cost.
- **How to use it:** press **Y** in camp or in a mission (on a controller: D-pad left), or the button at the bottom left in camp. Your looks and loadouts are saved across missions and restarts.
- **Separate from the Sequel Mod:** it's its own pak file and needs neither the Sequel Mod nor the launcher. Using both? Keep them from the same release: they share the small loader that starts the transmog and the super bosses. On its own: the [MCD Transmog, Loadouts and Reroll release](https://github.com/1TeaL/MinecraftDungeons-SequelMod/releases/tag/transmog-v1.0).
- **To remove it:** delete `Dungeons\Content\Paks\~mods\MCDTransmog_P.pak` and its readme next to it. Your items go back to their own looks; the Sequel Mod keeps working.

**Fixes**
- The Dancer's Sword and the Sparkler missed the damage boost the rest of the Cutlass family got - they hit as hard as the Cutlass and Nameless Blade now.
- Rushdown's burst on the Tempest Knives could hurt you; the knives carry Shadowcloak in that slot instead.

**Good to know**
- In multiplayer, everyone in the party needs the mod, started with `Play Sequel Mod.bat`.
- Every change, item by item: `CHANGES.md` in the mod folder; every enchantment with its tiers: [ENCHANTMENTS.md](https://github.com/1TeaL/MinecraftDungeons-SequelMod/blob/main/ENCHANTMENTS.md). Item and enchantment names for the settings: `NAMES.md`.
- To uninstall: delete `Dungeons\Content\Paks\~mods\SequelMod_P.pak` and the `Mods\SequelMod` folder (and `MCDTransmog_P.pak` if you have the transmog).
