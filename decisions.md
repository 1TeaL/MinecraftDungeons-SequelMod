# Sequel Mod - Decisions

Running log of what we decided, one enchantment at a time (order: Enchantment_Tier_List.xlsx).

## Melee

| # | Enchantment | Current | Decision | Notes |
|---|---|---|---|---|
| 1 | Ambush | +20/40/60% dmg vs mobs not targeting you | **Done:** +50/100/150% (0.5/lvl) | Sized so Ambush+Stunning ~ two strong damage slots. Tooltip text fixed |
| 2 | Anima Conduit | 2/4/6% health per soul (native) | Keep | |
| 3 | Artifact Synergy | +40/60/80% dmg on next attack after artifact use | **Done:** +60/80/100% (base 1.4, +0.2/lvl) | Additive; multiplies Dynamo. Could go to +100/150/200 later |
| 4 | Busy Bee | 20% + 10%/lvl = 20/30/40% bee per kill, max 3 | **Done:** 33% + 34%/lvl = 33/67/101% (matches Tumblebee) | In SequelMod.toml |
| 5 | Chains | 30% chance, chains 2 extra mobs, 1/2/3 s | **Done:** 45% chance, 4 mobs per chain | Verify chain count in-game |
| 6 | Committed | 0-50/75/100% vs wounded mobs (player values hard-coded; only mob value exposed) | Keep | |
| 7 | Critical Hit | 10/15/20% chance for x3 dmg (only multiplier exposed) | **Done:** x5 multiplier - the high-variance crit (avg +80% at III) | Chance still on code-patch list |
| 8 | Dynamo | Stored roll damage, base 25 +15/lvl (scaled by power), stacks to 20 | Keep | Video/experts: S tier |
| 9 | Echo | 5/4/3 s cooldown between echoes (computed in code, nothing exposed) | Code-patch list | Video: weakest melee enchant |
| 10 | Enigma Resonator | 0-15/20/25% chance (by souls) for x3 dmg; only multiplier exposed | Keep for now; raise chance via code patch later | Code-patch list |
| 11 | Exploding | 20% + 20%/lvl of dead mob max HP, radius 450 | Keep | Video: top tier, "mandatory" |
| 12 | Fire Aspect | 30 dmg/s base (x1/1.25/1.5 by level, scaled by power), 3 s | **Done:** 60 dmg/s (x2) | Still steals kill credit |
| 13 | Freezing | -30/40/50% mob speed for 3 s | **Done:** -40/55/70% (base 0.6, -0.15/lvl) | |
| 14 | Gravity | Pull 1.0/1.5/2.0 s, radius 500 | Keep | |
| 15 | Guarding Strike | 50% DR shield for 2/3/4 s after a kill | Keep | Video: strong |
| 8 | Cool Down | -18/29/38% artifact cooldown (code) | Keep | Video: top tier |
| 9 | Cowardice | +20/30/40% dmg at full HP (in effect) | **Done:** +40/50/60% (extra x1.2 modifier in its effect) | Verified loaded in-game |
| 10 | Death Barter | Saves you for 150/100/50 emeralds, 3 s invulnerability | Keep | Video: top tier |
| 11 | Deflect | 25/35/45% chance (code) to reflect projectiles | Keep | |
| 12 | Electrified | Roll zaps 2 mobs for 50 base (X/2X/3X), radius 700 | **Done:** 4 mobs, 100 dmg | Also boosted by Lightning Focus |
| 13 | Explorer | Heal 0.3/0.7/1.0% (code) per 100 new blocks | **Done:** every 10 blocks (10x as often) | Passive regen while exploring |
| 14 | Final Shout | Fires all artifacts below 25% HP, every 12/10/8 s | **Done:** below 50% HP, every 8/6/4 s | Description text says 25% - check tooltip |
| 15 | Fire Focus | +25/50/75% fire dmg | **Done:** +50/100/150% | The "buff fire in general" lever |
| 16 | Fire Trail | 20 dmg/s (X/2X/3X), patches 4 s | **Done:** 60 dmg/s (x3), patches 6 s (block life 8 s) | |
| 17 | Food Reserves | 1/2/3 food items per potion (code) | Keep | Experts value it at extreme difficulty |
| 18 | Frenzied | +10/20/30% attack speed below 50% HP (in effect) | **Done:** +40/50/60% (extra x1.3 modifier) | Verified loaded in-game |
| 19 | Gravity Pulse | Pulls mobs every 3 s, radius 400 (x1/1.5/2) | Keep | Weak by design (can't turn off); numbers can't fix it |
| 20 | Health Synergy | Heal 3/4/5% per artifact use (code) | Keep | Strong in roll builds |
| 21 | Life Boost | +11/22/33% max HP per respawn | Keep | |
| 22 | Lightning Focus | +25/50/75% | **Done:** +50/100/150% (decided with Fire Focus) | |
| 23 | Luck of the Sea | +10/20/30% luck (unique drops) | **Done:** +25/50/75% | Faster farming |
| 24 | Lucky Explorer | 5% per block explored for 1/3/5 emeralds | Keep | Feeds Death Barter |
| 25 | Multi-Roll | Store 2/3/4 rolls (code) | Keep | Slowdown until recharged is the real issue (code) |
| 26 | Poison Focus | +25/50/75% | **Done:** +50/100/150% (decided with Fire Focus) | |
| 27 | Potion Barrier | -90% dmg for 5/7/9 s after a potion | Keep | Video: top tier |
| 28 | Prospector | Shared file with melee | Keep | |
| 29 | Protection | -6/11/15% damage taken (in effect, code) | Keep; buff to -15/25/35% on effect-based list | |
| 30 | Reckless | -40% max HP, +50/70/90% melee dmg (additive pool) | **Done:** keep -40% HP, +100/125/150% | Revisited after the additive-buffs finding |
| 31 | Recycler | Arrow bundle every 30/20/10 projectile hits (code) | Keep; fewer hits on code-patch list | |
| 32 | Rush | +30/60/90% speed for 1 s after taking damage | Keep | |
| 33 | Shadow Blast | Blast on leaving Shadow Form, 100 dmg, 2/3/4 block radius | **Done:** 300 dmg (x3) | |
| 34 | Shadow Surge | 6/12/16 souls per mob killed in Shadow Form | Keep | Strong in anchor build |
| 35 | Snowball | Throw every 5/3/1 s, 2 s stun, radius 1000 | **Done:** every 3/2/1 s (base 3, -1/lvl) | Lvl III unchanged (2 mobs perma-stunned); pairs with Ambush |
| 36 | Soul Focus | +10/20/30% soul dmg | Keep (decided with Fire Focus) | |
| 37 | Soul Speed | +5%/soul stacking speed, 3/5/7 s | **Done:** +10%/soul | ~+50% stacked |
| 38 | Speed Synergy | +20% speed for 1/2/3 s on artifact use | **Done:** +50% | Matches Swiftfooted |
| 39 | Surprise Gift | 50/100/150% chance for a consumable per potion (code) | Keep | |
| 40 | Swiftfooted | +30/40/50% speed for 3 s after a roll | Keep | |
| 41 | Thorns | Return 100/150/200% of damage taken | **Done:** 500/750/1000% (base 5, +2.5/lvl) | Scales with difficulty; mob Thorns stays 10% |
| 42 | Tumblebee | 33/67/101% bee per roll, max 3 | Keep | Busy Bee now matches it |
| 16 | Illager's Bane | +25/35/45% vs Illagers | **Done:** +50/75/100% (matches Unchanting; verified in tooltip) | |
| 17 | Leeching | Heal 5/7/9% of killed mob max HP | Keep | Video: top tier |
| 18 | Looting | +100/200/300% consumable drop chance | Keep | |
| 19 | Pain Cycle | 3% max HP per attack; 5th stack hits x3/x4/x5 (+200/300/400% ADDED to the melee pool) | **Done:** 2% drain, x4/x6/x8 (+300/500/700%) | Revisited after the additive-buffs finding |
| 20 | Poison Cloud | 30% chance, 15 dmg/s base, 2.5 s, radius 250 | **Done:** 30 dmg/s (x2), radius 400 | Radius shared with ranged Poison Cloud |
| 21 | Prospector | +100/200/300% emerald drop chance (shared by melee/ranged/armor) | Keep | |
| 22 | Radiance | 20% chance, heal 30 base (X/1.5X/2X), circle ~375 | **Done:** 100% chance, heal 6 (20% of original = same average healing as vanilla, but steady) | Many circles on fast weapons |
| 23 | Rampaging | 10% chance on kill, +50% attack speed for 5/10/15 s | **Done:** 100% chance, 2/4/6 s (BoostTime 2) | Verify duration scales per level |
| 24 | Refreshment | -1/2/3 s potion cooldown per kill | Keep | Enables permanent Potion Barrier |
| 25 | Sharpness | +10/21/33% flat melee dmg (set inside SharpnessGameplayEffect in code) | Keep - fine as a reliable, unflashy bonus | Effect-based list if we revisit |
| 26 | Shockwave | 30 base dmg (X/1.5X/2X), end of combo | **Done:** 60 base dmg (x2) | Steals kill credit; no pak fix |
| 27 | Smiting | +25/35/45% vs undead | **Done:** +50/75/100% (base 1.25, +0.25/lvl; matches Unchanting) | Confirm in tooltip at next check |
| 28 | Soul Siphon | 20% chance per hit for 1/3/5 souls | Keep | Video: strong on fast weapons |
| 29 | Stunning | 5/10/15% stun chance, 2 s | **Done:** 15/30/45% (0.15/lvl; matches Chains at III) | Watch fast weapons; maybe 1.5 s stun |
| 30 | Swirling | 40 base dmg (X/1.5X/2X), radius 400, end of combo | Keep (not buffed yet) | Shockwave (60) should out-damage it |
| 31 | Thundering | 30% chance, 12.5 base dmg (X/2X/3X), strike radius 150, chain 700 | **Done:** 100% chance, 7.5 base dmg (2x total; user 2026-10-05) | Fast weapons favored |
| 32 | Unchanting | +50/75/100% vs enchanted mobs (code only) | Keep | Benchmark for Bane/Smiting |
| 33 | Void Strike | Multiplier builds to +200/400/600% (code only) | Keep | Glue Strike glitch with Weakening stays |
| 34 | Weakening | Mobs deal -20/30/40% dmg, radius 300, 5 s | Keep | Video: strong |

## Ranged

| # | Enchantment | Current | Decision | Notes |
|---|---|---|---|---|
| 1 | Accelerate | +8/10/12% per shot, stacks 25/20/16 (=+200%), code clamps at 2x | Stack limits raised to 38/30/25 (+300%) | Code clamp GetSpeedLimit()=2.0 likely still caps at +100%; real cap is a code patch |
| 2 | Anima Conduit (Ranged) | 4/6/8% max HP per soul | Keep | Melee version has the same settings (2/4/6%) |
| 3 | Artifact Charge | Next 1/2/3 shots charged after artifact use | Keep | Feeds Cooldown Shot loop |
| 4 | Bonus Shot | Extra arrow at 10/17/24% dmg (player value in code) | Code-patch list | Watch the Torment Quiver/Dynamo glitch |
| 5 | Burst Bowstring | Roll fires 1/2/3 charged arrows at 40% dmg | Keep | Core of the roll build |
| 6 | Chain Reaction | 10/20/30% chance (code) to burst into 5 arrows | Keep | |
| 7 | Committed | Shared with melee (one file) | Keep | |
| 8 | Critical Hit | Shared with melee (one file) | x5 applies to bows too - OK | |
| 9 | Cooldown Shot | -0.5/1.0/1.5 s artifact cooldown per charged shot | Keep | Knob if the roll loop ever needs a nerf |
| 10 | Dynamo (Ranged) | Base 25 +15/lvl stored per roll, stacks to 20 | Keep | Same as melee |
| 11 | Dipping Poison | 6/8/12 poison arrows per potion | **Done:** 10/15/20 arrows | Poison arrow settings (homing, pierce, damage factor) now in config too |
| 12 | Enigma Resonator (Ranged) | 0-15/20/25% chance (code) for x3 | Keep; chance on code-patch list (with melee) | |
| 13 | Fire Aspect | Shared file with melee | Already x2 (60 dmg/s) | |
| 14 | Fuse Shot | Every 5th/4th/3rd shot (code): 100% dmg blast, radius 300, 1 s fuse | **Done:** 200% dmg, radius 450, 0.1 s fuse | |
| 15 | Gravity (Ranged) | Pull 1.0/1.5/2.0 s, radius 500 | Keep | |
| 16 | Growing | Up to +25/50/75% (code) at 1600 distance | **Done:** full bonus at 1000 (~10 blocks) | |
| 17 | Infinity | 16/32/48% chance (code) to keep the arrow | Keep | |
| 18 | Levitation Shot | After roll, next shot floats mob 2 s; fall dmg 0.1/lvl | **Done:** fall dmg 0.25/lvl (x2.5) | Needs a better identity later; confirm in tooltip |
| 19 | Multishot | 20/30/40% chance (code) for +4 arrows | Keep | |
| 20 | Overcharge | Charge 2/3/4 times (code only) | Keep | |
| 21 | Piercing | Every 3rd/2nd/every arrow pierces | Keep | |
| 22 | Poison Cloud (Ranged) | 30%, 15 dmg/s base | **Done:** 30 dmg/s (x2); cloud radius 400 shared with melee | |
| 23 | Power | +10/21/33% arrow dmg (in effect, code) | Keep | Like Sharpness; effect-based list if revisited |
| 24 | Prospector | Shared file with melee | Keep | |
| 25 | Punch | +200/300/400% knockback (code) | Keep for now; higher knockback on code-patch list | Base arrow pushback is shared by all arrows |
| 26 | Radiance Shot | 50% chance, heal 30 at arrow impact | **Done:** 100% chance, heal 20 (~+33% avg) | |
| 27 | Rapid Fire | +10/15/20% attack speed (in effect, code) | Keep; buff on effect-based list | Accelerate is better |
| 28 | Refreshment (Ranged) | -1/2/3 s potion cooldown per kill | **Done:** -3/6/9 s (3x; bows rarely get kills) | Melee stays -1/2/3 |
| 29 | Ricochet | 20/40/60% chance (code), up to 3 bounces | Keep | |
| 30 | Roll Charge | Shots auto-charged for 1/2/3 s after a roll | Keep | |
| 31 | Shock Web | Beams between last 1/2/3 charged arrows, 37.5 dmg/s | **Done:** 75 dmg/s (x2) | Maybe more after playtesting (setup-heavy) |
| 32 | Smiting | Shared file with melee | Already +50/75/100% | |
| 33 | Soul Siphon | Shared file with melee | Keep | |
| 34 | Supercharge | Charged shots +20/30/40% dmg + knockback (code) | Keep | |
| 35 | Tempo Theft | Steal 17/33/50% of mob speed for 4 s | Keep | |
| 36 | Unchanting | Shared, no settings | Keep | |
| 37 | Void Strike (Ranged) | No settings | Keep | Enables Glue Strike |
| 38 | Wild Rage | 20/30/40% chance (code), 5 s rage | Keep | |

## Armor

| # | Enchantment | Original | Decision |
|---|---|---|---|
| 1 | Acrobat | -15/30/45% roll cooldown | Keep |
| 2 | Bag of Souls | +50/100/150% soul capacity | **Done:** +100/200/300% |
| 3 | Beast Boss | +20/40/60% pet damage | **Done:** +50/100/150% |
| 4 | Beast Burst | Pet explosions on potion use, 250 +250/lvl | Keep (best pet enchant already) |
| 5 | Beast Surge | Pet speed x1.5/2/2.5 for 10 s on potion | **Done:** 20 s |
| 6 | Burning | 5 dmg every 0.5 s, radius 300 | **Done:** 15 dmg/tick, radius 400 |
| 7 | Burst Bowstring | Roll fires 1/2/3 charged arrows at 40% dmg | Keep (core of the roll build) |
| 8 | Chilling | Slow blast every 2 s, radius 1000 | Keep (strong) |
| 9 | Cowardice | +20/30/40% dmg at full health | **Done:** +40/50/60% (extra +20% in its effect); tooltip lists all tiers |
| 10 | Death Barter | Cheat death for 150/100/50 emeralds | Keep (top tier) |
| 11 | Dipping Poison | 6/8/12 poison arrows per potion | **Done:** 10/15/20 |
| 12 | Electrified | 2 zaps of 50 on roll | **Done:** 4 zaps of 100 |
| 13 | Explorer | Heal every 100 blocks | **Done:** every 10 blocks (text updated) |
| 14 | Final Shout | Below 25% health, cooldown 12 s | **Done:** below 50% health, cooldown 8 s |
| 15 | Fire Focus / Lightning Focus / Poison Focus | +25% per level | **Done:** +50% per level |
| 16 | Fire Trail | 20 dmg/s for 4 s | **Done:** 60 dmg/s for 6 s |
| 17 | Frenzied | +10/20/30% attack speed under 50% health | **Done:** +40/50/60% (extra +30%); tooltip lists all tiers |
| 18 | Gravity Pulse | Pull every 3 s, radius 400 | Keep (user 2026-10-05: no redeeming it) |
| 19 | Life Boost | Revive bonus 11% per level | **Done 2026-10-05:** 20% per level |
| 20 | Luck of the Sea | +10/20/30% luck | **Done:** +25/50/75% |
| 21 | Lucky Explorer | 5% emerald chance per block | **Done 2026-10-05:** 10% |
| 22 | Potion Barrier | Damage absorbed after a potion | Keep (top tier) |
| 23 | Reckless | +50/70/90% dmg, -40% health | **Done:** +100/125/150% |
| 24 | Roll Charge | Auto-charged shots 1/2/3 s after a roll | Keep |
| 25 | Rush | +30% speed per level after being hit | **Done 2026-10-05:** +50% per level (revert if silly) |
| 26 | Shadow Blast (Shadow Flash) | 100 dmg | **Done:** 300 |
| 27 | Shadow Surge | 6/12/16 souls when leaving shadow form | Keep |
| 28 | Snowball | Every 5/3/1 s | **Done:** every 3/2/1 s |
| 29 | Soul Focus | +10/20/30% soul artifact dmg | Keep (soul artifacts already hit hard) |
| 30 | Soul Speed | +5% speed per soul | **Done:** +10% |
| 31 | Speed Synergy | x1.2 speed after an artifact | **Done:** x1.5 |
| 32 | Swiftfooted | Speed boost 3 s after a roll | **Done 2026-10-05:** 5 s |
| 33 | Thorns | 100/150/200% returned | **Done:** 500/750/1000% |
| 34 | Thrive Under Pressure | Needs 4 mobs nearby | **Done 2026-10-05:** 3 mobs |
| 35 | Tumble Bee | 33/67/100% bee on roll | Keep (user 2026-10-05) |
| 36 | Protection, Deflect, Health Synergy, Recycler, Food Reserves, Surprise Gift, Multi-Roll, Cool Down and others | Numbers in code | Can't tune; built-in tiers on armors raised where it helps |

## Armor decided ahead (Focus family)

- Lightning Focus (22): +50/100/150% (0.5/lvl) - **Done**
- Poison Focus (26): +50/100/150% (0.5/lvl) - **Done**
- Soul Focus (36): keep +10/20/30% (soul artifacts already hit hard; Harvester + infinite artifacts)

## Unique-only

| Enchantment | Current | Decision | Notes |
|---|---|---|---|
| Rushdown | Speed burst on kill (file values unclear vs "200%" text) | Keep | Only on certain unique weapons |

## Notes

- Damage buff math (game effect dump + reddit.com/r/MinecraftDungeons/comments/nvd7e5): buffs that modify the
  same attribute ADD together. Melee pool: Sharpness, Cowardice, Reckless, Pain Cycle, Artifact Synergy,
  Strength (+100%), Shadow Brew (+700%), armor "+X% melee damage", Double Damage. Ranged pool: Power,
  Cowardice, Strength, armor ranged boost, Bow's Boon, Overcharge. True multipliers on top: Critical Hit,
  Committed, Unchanting, Smiting, Illager's Bane, Enigma, Void Strike, Ambush, Gong of Weakening. Focus
  enchants use their own attribute; Dynamo adds flat damage. Defense divisors (Potion Barrier, Protection)
  also add together.

- Kill credit: enchantments that deal their own damage (Fire Aspect, Poison Cloud, Shockwave, Swirling,
  Thundering...) take the kill from the weapon, switching off Leeching/Exploding/etc. No setting controls
  this (Shockwave's wave is not a BaseProjectile, so bCanTriggerEnchantments doesn't apply). Code patch only.

- Critical Hit and Enigma Resonator both tag their bonus as critical damage; they roll separately,
  so they should stack (untested).

- Tooltips follow our values automatically, from the plain .pak (verified 2026-10-03: Busy Bee, Chains,
  Critical Hit "quintuple", Freezing, Illager's Bane). Descriptions with
  numbers written into the text (e.g. Guarding Strike "50%") need a locres edit.

## Code-patch list (hard-coded values; needs patching game code in memory)

- Critical Hit: raise crit chance (currently 10/15/20%).
- Enigma Resonator: raise trigger chance (currently 0-15/20/25% by souls).
- Bonus Shot: raise the extra arrow's damage (currently 10/17/24%).
- Recycler: fewer projectile hits needed (currently 30/20/10).
- Accelerate: raise the 2x attack-speed clamp (GetSpeedLimit returns 2.0 at every level).
- Punch: higher knockback multiplier.
- Echo: rework the fixed 5/4/3 s cooldown (e.g. shorter, or scale with attack speed).

Note: code patches break "plain .pak" distribution (every player would need a launcher/UE4SS).
Alternative to investigate first: blueprint logic authored in UE 4.22 and shipped in the .pak.

## Text fixes - **Done** (SequelText.toml, verified in-game 2026-10-03)

- Ambush effect: "+50% Damage Bonus per level" (game filled {0} from the code default 20/40/60).
- Levitation Shot effect: "250% Fall Damage per level" (same issue).
- Explorer description: "For every ten blocks..." (was "one hundred", written into the text).
- Fuse Shot description: "explodes almost instantly" (0.1 s showed as "zero seconds").
- English only; other languages keep the original text.

## Effect-based list

How it works: these effects get their amount from the enchantment code ("SetByCaller"), so we can't edit
the number - but tools/effects.py rebuilds the effect's modifier list with the original modifiers plus
an extra fixed one. Unreal adds multiplier bonuses together (1 + sum of (x - 1)), so an extra x(1+b)
adds +b at every level. Needs an effect *file* to edit.

Done (verified loaded in-game 2026-10-03; damage/speed math still to playtest):
- Cowardice: +0.2 -> +40/50/60%.
- Frenzied: +0.3 -> +40/50/60%.
- Accelerate: stack limits 38/30/25 (code clamp of 2x probably still applies - see Code-patch list).

Still to do - no effect file exists, so each needs a NEW effect file + the enchantment repointed to it:
- Protection: -15/25/35% damage taken (ProtectingGameplayEffect, Division op).
- Rapid Fire: buff attack speed (e.g. +20/30/40%).
- Poison arrow poison damage (PoisonArrowGameplayEffect, damagePerSecond 15; custom calculation).
- Sharpness / Power: only if we decide they need a nudge.

## Other ideas to revisit


- Loot power cap - **Done (needs playtest):** top A+ dropped 251 vs Tower 263. LootPowerMultiplier switched on:
  x1.0 at A+1 -> x1.046 at A+25 (stored power 26.1 -> 27.3 = display 251 -> 263). Verified the game's
  GetEndlessStruggleConfiguration returns it per level (25 A+ levels total). Mob stats untouched.
  Unverified: whether the multiplier applies to stored power exactly this way, and whether code clamps drops.
- Difficulty: user does NOT want mob balance changed (buffs are for build variety). More A+ levels (count is a
  code constant: 25) and a 999-power display rescale are code-patch / "launcher edition" ideas.
- "Play longer" research (2026-10-04, read-only): A+ count is DifficultyUtil::GetTotalNumEndlessStruggles =
  `mov eax,25; ret` at exe+0xA210D0 (threat+A+ total = 32 at exe+0xA210E0, threat levels = 7). Only Apocalypse
  has A+ levels. Config above A+25 repeats A+25. Default per-level slopes extended past 25 break things: stun
  and knockback go negative ~A+35, mob speed 2x by A+30, player healing hits 0 ~A+67; health/damage only ~3x
  by A+99. Engine item power cap ~320 (user, tower reroll exploit).
  Cap patch WORKS (4 places; tools/aplus_patch.py) - details in EndlessApocalypse.md.
- Endless Apocalypse - **Built 2026-10-04 (needs playtest):** launcher (`Play Endless Apocalypse.bat`)
  raises A+ to 99; power past A+25 rises slowly to the game's limit at A+99 (recommended 252 -> 333);
  A+ table past 25 per Endless.toml (default "natural": health/damage ~3x at A+99, speed/stun/knockback/
  healing frozen at A+25, mob count/resurrection/deflect/XP added from A+30/40/50/26); gold from mobs
  past A+25 (2% -> 8%). A+1-25 and normal Steam launches unchanged. See EndlessApocalypse.md.
- All enchantment options active - TESTED 2026-10-04 (UE4SS experiment, memory only):
  - Items store a flat list of 9 options (TypeID, Level, InvestedPoints); unpicked options are level 0.
  - Raising unpicked options to level 3 and re-equipping: active enchantments went 3 -> 10
    (all 8 Katana options ran). So COMBAT honors every option with level > 0; one-per-slot is a UI rule.
  - UI: invested points recalculated (Katana showed 56), enchant panel shows overlapping icons and
    can't be clicked.
  - The game autosaved the change; save restored from save_backup_2026-10-03 (modified copy kept in
    save_with_all_enchants_2026-10-03).
  - Not possible as a plain .pak (UI/save logic). Options: optional save-editing tool, or UE4SS/launcher.
  - Parked (user, 2026-10-04): maybe unpicked options active at weaker power - only with in-game text that
    clearly lists what else is active. Revisit after the difficulty work.

## Gear review (weapons, armor, artifacts) - started 2026-10-04

Rules (user): make every weapon viable; **every unique must end up better than its base weapon**; built-in
enchant tiers I-III chosen per weapon (stats + effect). Seasonal reskins get the same stats as the unique they copy.

Sheets: Gear_Rebalance.xlsx (detailed), Gear_Tier_List.xlsx (friends). Opinions: Gear_Opinions.md.
- Editable by pak: melee per-hit damage / swing time / range / knockback; ranged damage factor / charge / fire
  rate / arrows per shot / arrow stack; a few artifact values (Eye of the Guardian damage, Ice Wand damage,
  Gong multiplier, Powershaker shockwave, Corrupted Seeds targets...).
- Code patch needed: built-in enchantments, armor properties, artifact cooldowns and most artifact effects.
- **Done:** Dancer's Sword and Sparkler (its seasonal reskin, Cutlass_Year1) 50 -> 75 per hit (both missed the Cutlass buff; now match Cutlass / Nameless Blade). Weapon stats live in SequelGear.toml.
- Review order: go item by item with the user, weakest first (see Gear_Opinions.md "Worst"/"Weak").
- **Done:** Axe family. Baseline (all three): damage 65/65/100 -> 85/85/130, swings 1-2 width 25 -> 35
  (small bump - ShinkuNy rates axe area 5/5 already; value is a half-angle: 35 = 70 deg arc; spin stays 180). Firebrand: damage 105/105/155 (heavy,
  ~203 dmg/s). Highland Axe: baseline damage, swing time 0.5/0.5/0.8 -> 0.42/0.42/0.65 (~201 dmg/s, more
  Stunning procs). Needs playtest: does a shorter AttackAnimationTimeDurationSeconds really speed the swing?

### Built-in enchantments (launcher-only) - **built 2026-10-04**: Builtins.toml + tools/builtins_patch.py, applied by
every launcher start. Verified in memory (13 items changed + read back); needs an in-game look at tooltips/effects.
Uniques get their built-in enchantment from the item definition built at startup (e.g. Firebrand =
FEnchantmentData{FireAspect(5), Level 1}, registered at exe+0x14A910; Highland Axe = Stunning(17), exe+0x14AC00).
Not saved per item, so editing the definition should change every copy, tooltip included (playtest to confirm).
Needs: launcher finds the item registry in memory after startup and edits type/level (code runs before the
safe patch window, so data must be patched, not code).
Policy (user, 2026-10-04): make every weapon viable - each built-in gets tier I, II or III depending on
the weapon's stats and the enchantment's effect; decided case by case.
| Unique | Built-in | Change |
|---|---|---|
| Firebrand | Fire Aspect I | -> III |
| Highland Axe | Stunning I | -> III |
| Maulers | Rampaging I | -> II (already fast; Rampaging now always triggers) |
| Soul Fists | Enigma Resonator I | -> II (edge over Moon Daggers, which keep I) |
| Sponge Striker | Sponge Strike (dead: Mojang removed its power scaling) | swap -> **Pain Cycle III** (no weapon has it built in); stats trimmed to compensate; reword its tooltip line |
| Fangs of Frost | Freezing I | -> III |
| Sheer Daggers | Swirling I | -> III |
| Nightmare's Bite | Poison Cloud I | -> III |
| The Last Laugh | Prospector I | -> III |
| Diamond Sword | Sharpness I | -> III |
| Stormlander | Thundering I | -> III |
| Hawkbrand (+ Sinister Sword) | Critical Hit I | keep I (+40% avg with our x5 crits) |
| Chill Gale Knife | Freezing I | -> III |
| Eternal Knife | Soul Siphon I | -> III |
- **Done:** Gauntlets family. Punches 1 and 4 width 15 -> 30 (rest already 30, finisher 40) on all four.
  Gauntlets: damage 25x5/35/45 -> 30x5/45/60 (~159 dmg/s). Soul Fists: same + finishers 55/80, first three
  punches back to 0.125 s (were slower than the common!) (~178). Maulers: base damage + punches 0.11 s,
  finisher 0.55 s (~183). Combo hits 5-6 0.2 -> 0.17 s on all three (ShinkuNy: the slow end of the combo is
  what drags gauntlet DPS down). Fighter's Bindings: unchanged (SS; width change reverted).
- **Done:** Coral Blade 19/20/45 -> 33/33/75, Sponge Striker 19/20/45 -> 33/33/80, both reach -> 380 on every hit
  (was 280-350). Both were bottom-ranked (ShinkuNy BL, lowest DPS in the game files).
- **Kept vanilla (user):** The Starless Night (its hit speed is lower than the plain Obsidian Claymore's; left as is).
- **Done:** Whip family. Whip and Vine Whip both: damage 100 -> 110, splash 0.1 -> 0.2 (mobs next to the target
  took only 10%). Mirrored on Vine Whip so the unique stays strictly better (same stats + Jungle Poison).
- **Done:** Daggers family. Fangs of Frost 35 -> 41 per hit (~182 dmg/s), Sheer Daggers 35 -> 40 (~178); both
  were below the plain Daggers (39/39/39/35/35/35, unchanged). Moon Daggers untouched (S rank via its soul niche).
- **Done:** Sickles family (all three were identical, ~139 dmg/s). Sickles 30x4/60/70 -> 33x4/65/75 (~160),
  Nightmare's Bite -> 36x4/70/82 (~174), The Last Laugh -> 38x4/75/88 (~185, its Prospector has no combat value).
- **Done:** Swords: Sword 50/50/80 -> 55/55/90, Diamond Sword 58/58/95, Hawkbrand (+ Sinister Sword) 60/60/100;
  first two hits reach 300 -> 350 on all (shorter than the animation). Great Hammers: reach 200 -> 260 on all;
  Great Hammer 100 -> 115, Stormlander 125, Hammer of Gravity (+ Bonehead Hammer) 120.
- **Done:** Tempest Knives (all three): knockback on hits 1-2 1.0 -> 0.2 (it knocked mobs out of the combo;
  finisher keeps 1.2), reach on hits 1-2 300 -> 340. Chill Gale Knife damage 48/48/78 -> 52/52/85. Resolute
  Tempest Knife otherwise unchanged (A rank).
- **Done:** Eternal Knife damage 140 -> 155 (Soul Knife 140, Truthseeker untouched - S rank via Committed I).
- **Endless rewards (2026-10-04):** LootQualityBoost 4.1 (A+25) -> 18 (A+99) straight line; XP x1 (A+26) -> x5 (A+99);
  merchants ShopPriceMultiplier 1.0 (A+26) -> 0.6 (A+99). User intent: near A+99 drops should be (almost) all uniques -
  TODO find how LootQualityBoost maps to unique chance and tune the curve to that. Gold-from-mobs (Ingame.umap edit)
  is under suspicion for a crash on mission load (exe+0xB9CFFB, player controller null); if it repeats, move gold to
  the Emerald drop entry via the drop-roll hook instead of editing the map.
- **Crash on mission start (2026-10-04, twice, exe+0xB9CFFB: character update with no local player controller).**
  Suspect = my Ingame.umap edit (Gold drop entry): the actor grew by 220 bytes, and a BodySetup with inline bulk
  data sits before it (bulk offsets are relative to BulkDataStartOffset, which the writer shifted) -> level
  fails to load. Gold map edit and gold hook switched OFF (Endless.toml [gold] enabled = false). All other
  modified packages checked: none resize an object with bulk-data classes before it. Awaiting user retry.
  If gold comes back: size-neutral edit or code-only (convert Emerald rolls in the drop hook).
- Crash update: still crashed (same spot) with the map edit removed -> the umap edit was NOT the cause (stays off
  anyway; the bulk-data hazard is real). New suspect: the exe protection re-checks its code when a mission loads
  and sabotages the game (null engine objects, like the startup crash) if .text was patched. Test in progress:
  Launcher.toml endless = false (no code patches), builtins = true (data only). If confirmed, Endless needs a
  data-only design (e.g. redirect the Blueprint UFunction pointers for the level counts instead of patching code).

- **Endless rebuilt data-only (2026-10-04):** code patches caused the mission-load crash (Endless off = fine).
  New: `tools/endless_patch.py` repoints the four count UFunctions' Func to copies returning 99/106 and sets
  the last unlock step 25 -> 99 (A+26-99 unlock together with A+25). Power past 25 is in the pak
  (`[power] mode = "slow"`: per-level keys on LootPowerMultiplier, MobMaxHealth/MobDamage). Gear 254 at A+25 ->
  329 at A+99. Launcher.toml endless = true again. Needs playtest (EndlessApocalypse.md). A 4th difficulty: no.
  Playtest 2026-10-04: slider shows +99, A+99 mission starts (no crash). Mission screen's gear range follows
  equipped power (vanilla rule, see EndlessApocalypse.md), so it differs from recommended power.
  User decision 2026-10-04: no staged unlocks past A+25 - A+26-99 stay open together, the player picks the level.
  User changed their mind 2026-10-04: staged unlocks ON - 3 levels per step, 3 different bosses on the top level
  (Endless.toml [unlock]; 24 new step objects added by tools/endless_patch.py). Needs playtest.
- **Hard power cap found (2026-10-04):** gear strength clamps at x = 3 too (exe+0xB87920 / 0xB93340), i.e. gear
  power 315; the 3.0 constant is shared by ~300 places, can't be raised. Curve rebuilt: gear 254 -> 315 over
  A+26-100 with jumps every 10 levels ([power] milestone_every / milestone_weight); mobs follow the same climb.
  A+100 finale added ([finale] in Endless.toml; unlock: 3 bosses on A+99). Unlock steps: 3 levels each to A+79,
  then 4 each to A+99. Open: do loot-quality rerolls reach unique rarity (not traced).
- 2026-10-04: merchant price cuts past A+25 removed (user: not needed if emerald gains are higher). Note: no A+
  stat raises emeralds; they only rise with mob count. Builds made while the game runs go to staged/ and the
  launcher installs them at the next start.
- Open (asked 2026-10-04): raise the 315 cap. Gear strength wrappers exe+0x7AECC0 / 0x7AECE0 / 0x7AED00 are only
  reached through stored pointers (exe+0x347AA00, 0x347AC50, 0x3422988 = vtable entries), so a data-only redirect
  to copies with a higher cap looks possible (other paths: 0x941D90 via 0x94E9F0, 0xB5963E). Mobs past the cap
  via the health/damage rows. +1 power per level to A+100 needs cap x = 3.14 (power 329).
- Open: daily-trial modifiers (EAffectorId, 23 kinds; texts under Affector/ in game_en.json) on A+ levels. Not
  traced where a mission gets its modifier list. Damage is probably a float (GAS mod calculations), so the
  2.1B "ceiling" may only affect how numbers are shown - unverified.
- **Cap raise on trial (2026-10-04):** tools/cap_patch.py points the three `minss xmm6,[3.0]` (exe+0xB8794F,
  0xB9336F, 0xB8D9E0) at our own float: cap 329 = +1 power per level A+25-100 (Endless.toml [power] cap_power,
  milestone_weight 1). This IS a code change (Launcher.toml `cap`). Applied at the menu, game stayed up; mission
  load untested. Data-only wasn't possible: melee goes through per-instance virtuals (exe+0xB62500 -> 0xB590B0).
  If missions crash: cap = false, cap_power back to 315, rebuild.
  RESULT 2026-10-04: cap patch crashed on mission start (user test). So ANY code change crashes missions, even
  12 bytes. Cap stays 315; cap = false, cap_power removed, milestones back (weight 5). Don't retry code patches.
- 2026-10-04: A+100 finale mob health/damage lowered 6.0 -> 3.5 (user: not too much of a boost on top of the other
  modifiers). Blacksmith first look: BlacksmithMerchantDef is native (ctor exe+0xBB96B0); the "3 missions" in its
  text is a code constant, and its upgrade quests are objects built at startup with count 3 (exe+0xB86C30, r9d = 3,
  three of them) - heap data, so the launcher could probably change the count like the unlock steps. Fields not
  located yet (needs the running game). Enchantsmith = EnchantmentMerchantDef, not looked at yet.
- 2026-10-04 QoL: Blacksmith upgrades take 1 mission instead of 3 (QoL.toml, tools/qol_patch.py; quest objects of
  class at exe+0x4548B40, owner +0x28, missions +0x30). Applied live and read back; needs a play check. 0 untested.
- 2026-10-04 Armor: built-in tiers raised (Builtins.toml): Gilded Glory Lucky Explorer + Death Barter 3, Frost Bite
  Snowing 3, Golden Piglin Surprise Gift 3, Nimble Turtle Rush 3, Goat Gear Multi-Roll 2, Ember Robe Burning 3,
  Frost Armor Chilling 3. FOUND: armor perks are a list in the item definition at +0x1A8 (2 bytes each: perk id,
  flag 2 = added by the unique; room for 8), raw dump in research/armor_props_raw.json. Ids worked out so far:
  1 souls, 2 35% damage reduction, 3 30% negate, 5 +50% artifact damage, 6 -40% artifact cooldown, 7 weapon damage
  aura, 8 +10 arrows, 9 +30% melee, 10 melee attack speed, 11 +30% ranged, 12 life steal aura, 13 move speed aura,
  14 pet bat, 15 potions heal allies, 17 potion cooldown, 19 +100% roll cooldown, 30 reset artifact cooldown on
  potion, 33 +healing. Perk numbers stay in code, but perks can be added or swapped per armor (untested).
- 2026-10-04 Armor, user rule: keep each armor's idea, make it better. Black Spot (NatureArmor_Unique1): Food
  Reserves 3 + PotionCooldown perk. Black Wolf (WolfArmor_Unique2): Acrobat 3 + MoveSpeedAura. Cave Crawler
  (+ Year1 reskin): + ArtifactCooldown. Perk adds via Perks.toml / tools/perks_patch.py (launcher, `builtins`
  switch). Untested in play: does the tooltip list an added perk, does it work. item_registry.json repaired
  (Black Spot and Imploding Crossbow pointed at wrong globals; 3 armors were missing).
- 2026-10-04 Saves: character saves = "D001" + AES-256-ECB JSON (tools/savefile.py; key read from the running
  game, research/save_key.bin). Armor perks are stored per item ("armorproperties", names = EArmorPropertyID), so
  perk additions only reach new drops. Perk ids corrected: 17 = IncreasedMobTargeting, 18 = PotionCooldownDecrease
  (Black Spot fixed). tools/add_test_items.py added 25 test items (15 weapons, 10 armors, power 251) to the
  active character; backup in save_backups/.
- 2026-10-05 Armor: user confirmed added perks show on tooltips (orange marker) and Gilded Glory shows Death Barter 3.
  Second pass (weak/middling only, keep the armor's idea): Nimble Turtle + LifeStealAura, Golden Piglin +
  ItemCooldownDecrease, Guard's and Curious + RangedDamageBoost, Archer's + ItemCooldownDecrease, Fox (+ winter
  reskin) + SuperbDamageAbsorption, Frost Bite + IncreasedArrowBundleSize. Perks only reach new drops.
- 2026-10-05 Ranged pass (videos WMpCiE1VrgY + pjx7jpOVgjg; buff D/C/B, light A, meta/top untouched; Snow Bow left
  because Winter's Touch inherits it). Stats (SequelGear.toml): Crossbow damage factor 1.5 -> 1.8, Heavy Crossbow ammo
  15 -> 25, Longbow ammo 40 -> 50, Harpoon + Nautical fire interval 0.42 -> 0.36, Twisting Vine ammo 15 -> 30,
  Power Bow ammo 20 -> 30 (uniques inherit the base instance). Built-ins (Builtins.toml): Slicer Piercing 3, Azure
  Seeker Rapid Fire 3, Doom Punch 3, Slayer Ricochet 3, Twin/Haunted Bonus Shot 3, Red Snake Fuse Shot 3, Bonebow
  and Baby Crossbows Growing 3, Elite Power/Phantom Power 3, Guardian Supercharge 3, Master's Power 3, Hunter's
  Promise Infinity 3, Ancient Dynamo 2, Butterfly Bonus Shot 3, Lightning Harp Ricochet 2, Sabrewing Radiance Shot 2,
  Feral Soul Enigma 2. Not yet seen in game. Armor enchantment table above only goes to #7 - rest never walked through.
- 2026-10-05 Ranged follow-up: unique ranged instances only store the arrow count, everything else is inherited from
  the base, so per-unique stat bumps are limited to arrows per shot. Twin Bow + Haunted Bow now fire 2 real arrows
  (NumberOfProjectiles 1 -> 2). Azure Seeker keeps Rapid Fire (3) and gets the Crossbow family's +20% damage; Doom
  keeps Punch 3 and the Heavy Crossbow ammo 25; Butterfly keeps Bonus Shot 3 (A tier already).
  Tooltips: Cowardice and Frenzied showed the game's own number (user saw Cowardice 40% at tier 3) because the mod's
  bonus is an extra hidden multiplier; text now reads "{0} +20% ..." / "{0} +30% ...".

(Armor enchantment status: see the Armor table near the top.)
Test items: 19 changed ranged uniques added to the character (power 251), backup in save_backups/.
- 2026-10-05: armor enchants: Rush +50%/level, Swiftfooted 5 s, Lucky Explorer 10%, Life Boost +20%/level, Thrive
  Under Pressure at 3 mobs. Gravity Pulse and Tumble Bee left alone (user). Cowardice/Frenzied tooltips now list
  +40/50/60% for all tiers. Endless difficulty: mobs vs matching gear 1.5x (A+25) -> 4.5x (A+99) -> 5x (A+100)
  (user: farming should matter, but the end must stay beatable).
- 2026-10-05: Endless difficulty put back to 1.5x -> 3.0x (A+99) -> 3.5x (A+100) vs matching gear (user: new gear must
  feel like an upgrade, not falling behind). Revisit only if the 'all enchantment options active' idea is ever built.
- 2026-10-05 Artifacts: definitions sit in globals like weapons/armor (research/artifact_globals.json). In the
  definition: soul cost float at +0x94, cooldown float at +0x98, base duration float at +0x9C (e.g. Iron Hide 8,
  Death Cap 8, Gong 5, Soul Lantern 30). All launcher-editable data. Current values: research/artifact_cooldowns.json.
  Tiers from the second artifact video in research/notes_artifacts.md. Proposals sent to the user, not applied yet.
- 2026-10-05 Artifacts applied (user agreed to every row): Artifacts.toml + tools/artifacts_patch.py (launcher, under
  the `builtins` switch). Eye of the Guardian cooldown 22 -> 8, beam damage 200 -> 600, beam 4 -> 6 s; Totem of
  Casting 70 -> 30 souls, 10 -> 5 s; Wonderful Wheat, Enchanted Grass, Golem Kit, Tasty Bone, Flaming Quiver 30 -> 15 s;
  Soul Healer 50 -> 20 souls; Satchel of Snacks 16 -> 8 s; Totem of Regeneration 25 -> 15 s, up 10 -> 15 s; Satchel of
  Elements 10 -> 5 s; Ice Wand 15 -> 8 s, block damage 600 -> 1200; Boots of Swiftness boost 1.5 -> 3 s; Scatter Mines
  12 -> 8 s; Updraft Tome 10 -> 8 s; Ghost Cloak 1.5 -> 2.5 s; Tome of Duplication 40 -> 30 souls; Love Medallion
  30 -> 25 s. Eye and Ice Wand damage are pak values (new [Enchantments.GuardianEye] / [Enchantments.IceWand]
  sections in SequelMod.toml via EXTRA_ASSETS). Not yet seen in game. Pet stats/AI not looked at.
- 2026-10-05 TEST BUILD (user): power = +1 per level (254 at A+25 -> 328 at A+99 -> 331 at A+100; Endless.toml
  [power] top_power = 331, replaces cap_power). Real gear strength still stops at 315 (about A+85); mobs keep growing
  as if gear did (about 2x by A+100). Idea under test: gear above 315 gets extra enchantment options switched on
  (combat honours every option with level > 0). Test items in the save, power 325: Master's Katana, Bubble Burster,
  Full Metal Armor, each slot = picked option tier 3 + the other two at tier 1. Unlocks set to staged = false for
  the test (put back to true afterwards). Backup: save_backups/character_before_ascended_test_*.dat.
- 2026-10-05: "extra active options" idea REJECTED by the user after testing: it works in combat, but the game charges
  enchantment points for every active option (25 per test item; balance went to -22) and the enchant panel stacks
  icons and can't be clicked. Not player friendly. Extras switched off on the three test items.
  Also: with 100 levels the mission slider stopped at +25 even though memory was correct -> back to 99 levels
  (TOP = 98, finale = A+99). Power: +1 per level, 254 -> 327 at A+98 -> 330 at A+99 (top_power = 330); gear strength
  really stops at 315 (about A+85) and mobs now stop growing with gear there too, so 315 gear stays competitive:
  past the cap only the health/damage rows and other modifiers rise. Unlocks still staged = false for testing.
- 2026-10-05 (user): past the 315 mark the modifiers stay put and the mobs keep their natural growth. Health/damage
  multiplier 1.5x (A+25) -> 2.0x where gear hits the cap (A+85), flat after; mobs follow the +1/level power number
  above 315 (x1.9 by A+99). Mobs vs a matched 315 character: 2.0x at A+85 -> about 3.8x at A+99. No separate
  finale health/damage. Extra-enchant idea is dead; a gilded enchantment for gear above 315 is an open idea.
- 2026-10-05: A+100 put back at the user's request (LAST = 100, top_power 331). Watch for the slider stopping at +25.
- 2026-10-05 (user): mob projectile deflect removed everywhere (no counterplay). A+100 = power 330, no mob
  modifiers of its own (rewards only: 100 rerolls, XP x10). Health/damage multiplier now a straight line 1.5x
  (A+25) -> 2.0x (A+99/100) instead of stopping at A+85; mobs still follow the power number past 315.
- 2026-10-05 (user agreed to the numbers): Endless curve v-final. Health/damage multiplier 1.5 (A+25) -> 2.25 (A+85);
  past the cap it eases down while mobs take ~4% per power point: health 1.75, damage 1.5 at A+100 (felt 2.2x /
  1.9x of A+25). Player gets back A+86-100: healing 70 -> 100%, mob stun and knockback 30 -> 60%, stagger
  resistance 10x -> 5x; mob count (1.4x) and revive (8%) stop at A+85. Resistances are never harsher than A+25
  (pushback 0.3, stun 0.3, endurance 10x there). New Endless.toml syntax: [[level, value], ...] and until = N.
- 2026-10-05: mob revive chance tops out at 10% (A+85), user.
- 2026-10-05 overnight (user asleep; ideas for more enchantments / player power):
  * EXTRA BUILT-INS work at the data level: builtins_patch.py `add = { Enchant = level }` rebuilds an item's built-in
    list in memory the tool allocates (game's own lists have no spare room; the game natively has items with 2-3
    built-ins, e.g. Sturdy Shulker Armor). Applied by the launcher and read back; game stayed up at the menu.
    TEST entries: Dark Katana + Leeching 1, Shockwave 1; Bubble Burster + Multishot 1; Full Metal Armor + Protection 1.
    To check in play: tooltip lines, effects firing, no point cost, clean exit (the game was only force-closed).
    Built-ins are per item TYPE (every copy, every power), not per item or per level.
  * Test items in the save (backup character_before_overnight_tests_*): Diamond Sword with a written-in gilded
    Critical Hit 3 (does it show, does it cost points); Stormlander carrying two armor perks, MeleeAttackSpeedBoost and
    LifeStealAura (does a weapon list/apply armor perks).
  * Multiple gilded on one item: no (one netheriteEnchant field). Gilding is per item in the save.
- 2026-10-05 playtest (user): extra built-ins SHOW on the tooltip (Dark Katana lists Leeches Health + Casts
  Shockwaves); all 100 levels show on the slider (so 100 was not what broke it; that time the launcher had not
  finished). Mission screen health/damage lines no longer print the multiplier (it falls past A+25 because it carries
  the slow-down correction): text is now "Mobs have more health" / "Mobs deal more damage". Recommended power jumps
  ~6 from A+25 to A+26 because the game shows the previous level's range: it is the base game's A+24 -> A+25 step.
- 2026-10-05 playtest (user): written-in gilded enchantment SHOWS (Diamond Sword, Critical Hit 3). Armor perks on a
  weapon show on the tooltip but do NOT work (no life steal, no attack speed) -> dead end, don't use. The -1 points
  balance came from the pre-enchanted test items, not from built-ins or gilding.
  Working levers for extra player power: extra built-ins per item type (launcher), gilded per item (save).
- 2026-10-05 DESIGN (user): bonus built-ins by power tier - 1 at 264+, 2 at 290+, 3 at 316+; fixed per item family,
  chosen to fit the family's playstyle so the selectable slots are freed up; gilding left to normal farming. Must work
  at RUNTIME (user rejected "only at game start"): the launcher has to read the live inventory while the game runs.
  Draft table: Bonus.toml (not applied yet). Next: find the live inventory in memory (needs a loaded character).
- 2026-10-05 DESIGN v3 (user agreed, "Sure"): 
  * Ladder: A+26-50 gear 254 -> 315 (about 2.4 a level), mobs keep pace, health/damage multiplier flat at 1.5.
    A+50 = breaking point (gear cap). A+51-100: power label +1 a level to 365; mob health x3 and damage x2.2 of a
    315 mob by A+100 (rows [[50, 1.5], [100, 4.5]] / [[50, 1.5], [100, 3.3]]); healing/stun/knockback/stagger hand-
    back now runs A+50 -> A+100. Endless.toml [power] cap_level = 50, top_power = 365. BUILT into the pak.
  * Bonus built-ins (Bonus.toml, still a draft): one upgrade step per 4 power above 316 (12 steps, 320..364). An
    item's own built-ins rise to tier 3 first, then three bonus enchantments one tier at a time. Weapons/bows: a list
    per family. Armor: the same three for all - Potion Barrier (PotionFortification), Protection, Cool Down
    (Celerity; confirmed from save ids). Gilding left to normal farming.
  * NOT BUILT: the launcher's runtime watcher. Live inventory found read-only: item objects have vtable
    exe+0x346FCF8, 0x140 bytes, type FName at +0x34, stored power float at +0x3C, enchant TArray at +0x40; the
    game holds plain lists of item pointers. Still needed: FName -> item type mapping, the list's owner, the watcher.
  * Shown power = (stored - 1) * 10 + 1 (exe+0xB8DF00), so the cap 32.447 shows as 316.
- 2026-10-05 WATCHER BUILT: tools/bonus_watch.py (Launcher.toml `bonus`), runs in the launcher's wait loop every 3 s.
  Item -> type: an item definition starts with the same FName the item object carries at +0x34 (all 308 live items
  matched). Full heap scan 5.4 s, done once a minute; in between only the pages that held items are re-read (0.01 s).
  Applied by hand to the user's live session: Dark Katana Smiting 1 -> 3, Bubble Burster Reliable Ricochet 1 -> 3,
  Full Metal Armor + Potion Barrier 2 (all three test items are 325 = 2 steps). Last night's test `add` entries
  removed from Builtins.toml. To verify in play: tooltip updates live, new 316+ pickup gets its step within seconds.
- Stacking (minecraft.wiki Dungeons:Enchantment): enchantments are "stackable" (may be rolled in up to three slots)
  or not; copies act INDEPENDENTLY (two Chains III = 51% for at least one, 9% both; two Rampaging III can give 30 s).
  Tiers do not add. An item never rolls its own built-in as a choice. Melee stackable: Chains, Fire Aspect, Leeching,
  Looting, Radiance, Rampaging, Weakening. Ranged: Accelerate, Bonus Shot, Chain Reaction, Gravity, Growing,
  Multishot, Overcharge, Piercing, Poison Cloud, Rapid Fire, Tempo Theft. Armor: Burning, Chilling, Deflect,
  Electrified, Fire Trail, Frenzied, Gravity Pulse, Protection, Rush, Thorns. Whether a NON-stackable enchantment
  doubles when it is both a (bonus) built-in and a pick is untested.
- 2026-10-05 playtest (user): bonus built-ins written while the game runs show on tooltips immediately, both added (Full Metal Armor: Potion Barrier) and removed (Dark Katana lost the test Leeching/Shockwave). Live updating works.
- 2026-10-05: test items added (backup character_before_stack_test_*): two plain Swords at 250, one with Swirling III picked once (Common) and one with it picked in two slots (Rare); a 364 set (Dark Katana, Bubble Burster, Full Metal Armor, unpicked); Firebrand at 319.
- 2026-10-05 playtest (user): two Swirling III on one Sword do NOT stack. Non-stackable enchantments can't be
  doubled; stacking dropped as a power source. Bonuses stay three DIFFERENT enchantments per item. Bonus lists
  may now hold spares (first three not owned are used); Katana got Committed as spare.
- 2026-10-05 (user, from play): the wiki's stackable lists are wrong in places. Weakening does NOT stack on melee,
  and ranged Weakening (not listed at all) doesn't either. Ranged Fire Aspect DOES stack (wiki says no) and its burn
  is based on the melee weapon's damage. Don't rely on the wiki list; test before using a double.
- 2026-10-05: armor bonuses - defensive trio by default; own lists for Soul Robe, Grim, Dark, Evocation, Battle Robe,
  Snow, Emerald, Archer's and Guard's families. Pet armors keep the default (user: pet bonuses not worth it unless
  you build for pets). Weakening stays on Backstabber/Chainsword/Mace lists (player's job not to double it).
- 2026-10-05 (user changed mind): pet armors DO get pet bonuses (Wolf, Spelunker's, Beenest families); soul and
  emerald lists stay.
- 2026-10-05 CRASH (user): clicking the test Curious Armor (CowardsArmor_Unique1) crashed the game - it is an unused
  item with no icon. My mistake to add it. Removed from the save and from Perks.toml. Never add items that the
  game doesn't ship as obtainable (check wiki_gear.json / an icon first).
- 2026-10-05 playtest (user): perks ADDED to armor work in play (not just on the tooltip). Next idea (user): extra perks on armor at key power thresholds above 315 - needs writing to the live item (perks are stored per item), untested.
- 2026-10-05: live item layout: perks are a TArray at item+0x50 (2-byte entries id, flag; capacity 8). TEST: appended LifeStealAura to the user's 364 Full Metal Armor while the game ran (backup character_before_live_perk_test_*).
- 2026-10-05 playtest (user): a perk written to a LIVE armor shows and works at once (life steal on the 364 Full Metal
  Armor). Built into bonus_watch.py: armor at 330+ gets one extra perk, at 350+ a second, from Bonus.toml
  [armor_perks] (per-family lists with spares, generic default: 35% damage reduction, weapon damage aura, life steal
  aura, artifact cooldown). Perks are only added, never removed. Still to confirm: the game saves them (restart).
  Stacking math reminder for picking bonuses: same-pool bonuses add (see Notes), multiplier-group ones multiply.
- 2026-10-05 playtest (user): the two perks written to the live 364 Full Metal Armor are still there afterwards (user: 'still see the perks') - taken as saved by the game; confirm it was after a full restart.
- 2026-10-05: Cowardice/Frenzied tooltips back to the per-tier form: '{0} +20% ...' / '{0} +30% ...' (user disliked the same all-tiers text on every tier; the game can only print its own number, so the mod's part is written after it).
- 2026-10-05 playtest (user): with the 364 test set 'the gear is handling the mobs fine' (level not stated yet). Cowardice/Frenzied '{0} +20%' wording accepted.
- 2026-10-05: STACKING, corrected (each enchantment's own wiki page checked; lines 513-519 above came from a misread
  list page and are wrong). Stackable: Sharpness (multiplies), Smiting, Looting (adds), Prospector (adds), Chains,
  Fire Aspect, Leeching, Rampaging, Radiance melee (2nd copy 75%, 3rd 50%), Cool Down, Thorns. Every other
  enchantment's page says not stackable (no statement: Emerald Shield, Bow's Boon, Backstabber and the built-in-only
  ones). Matches play: Swirling and Weakening don't stack; Fire Aspect does, also on bows (one definition for both).
- 2026-10-05: the game's own stackable marker found. Enchantment definitions (tools/enchant_registry.json) hold a tag
  list at +8 (TArray of bytes). Tag 0 = stackable: on exactly the eleven above plus the unused Knockback. Other tags:
  2 = soul enchantments, 3 = charge/roll-triggered bow ones, 1 = Aiding/Altruistic/Bow's Boon/Chains (meaning unknown).
  Header: byte0 gear mask (1 melee, 2 ranged, 8 armor), byte2 = powerful, byte3 = type id. No tuning numbers in the
  definition (the rest is name/description text) - Echo's 5/4/3 s cooldown stays a code constant.
  tools/stack_patch.py + Stack.toml add tag 0 at runtime (data only). UNTESTED whether the effect then adds up.
- 2026-10-05 playtest (user): stackable tag does NOT make effects add up. Firebrand with two built-in Shockwave III:
  same damage as one, with and without tag 0 on Shockwave. The tag only governs rolling in several slots. Stacking
  non-stackable enchantments is closed for good; Stack.toml stays empty. Side issue: user sees no Swirling damage
  numbers at all (also after the tag was removed) - to check on a clean weapon after a restart.
- 2026-10-05 playtest (user), STACKING REOPENED: copies of a non-stackable enchantment at DIFFERENT tiers both fire.
  Seen: Sword with Swirling I + Swirling III picked = two swirl numbers on a mob behind the player; Firebrand with
  built-in Shockwave III + II, and III + I = two overlapping Shockwave numbers. Identical copies (same tier) merge:
  two Shockwave III built in = no gain, two Swirling III picked = no gain (earlier test). No tag needed.
  So a bonus built-in can add to a pick as long as its tier differs from the pick's (research/stack_test.py).
  Not yet tested: cooldown/proc enchantments (Echo, Leeching, Critical Hit), three copies (I + II + III).
- 2026-10-05 playtest (user): Shockwave III + II + I built in (Firebrand) and Swirling I + III picked (Sword): the
  first trigger after equipping shows one number, later triggers show all copies (3 on the axe). After a live
  built-in change the weapon has to be taken off and put back on for the count to be right. Mechanism built in
  bonus_watch.py ([copies] in Bonus.toml), levels empty = off until the user approves levels and signatures.
- 2026-10-05: [copies] switched ON with defaults (user: the first-trigger quirk is 'no big deal'; no objection to the
  proposal): tier II copy at 340, tier I copy at 360, melee signatures per Bonus.toml [copies.melee]. Unlisted
  families (Daggers, Sickles, Mace, Backstabber, Void Touched Blades, soul weapons, all ranged, all armor) get none
  until tested. Takes effect at the next game start.
- 2026-10-05 (user): the point of stacking is that an innate enchantment must not make picking the same one a waste;
  'I just want more things to stack so they can scale better like poison, fire, lightning etc, really everything'.
  REDESIGN of weapon bonuses (replaces the [copies] lane, removed): each bonus enchantment = a tier I copy, then a
  tier II copy beside it (2 steps), never tier III - I + II beats one III and the player's own tier III pick adds on
  top. step 4 -> 5 (9 steps, 321-361). Armor bonuses unchanged (single entry to tier 3) until tested with copies.
  Play tip for tier III built-ins (uniques): pick the same enchantment and stop at tier II (or I) - it adds.
  Untested: ranged enchantments and non-hit ones (Echo, Leeching, Committed, Stunning) with mixed tiers.
- 2026-10-05 (user, correction): copies at the SAME tier also all fire - they trigger together, so the damage numbers
  overlap and read as one ('they definitely work'). The earlier 'two Swirling III / two Shockwave III don't stack'
  verdicts were wrong (judged by the numbers). So every copy of an enchantment works, any tier, picked or built in;
  the wiki's 'stackable' only says whether the game ROLLS it in several slots. Entries above this that say identical
  copies merge are superseded. Bonus system put back to the simple form (one entry per bonus rising to tier 3,
  step 4); the I + II redesign and the [copies] lane are removed. A bonus adds to the player's own pick.
- 2026-10-05 (user): no forced duplicates of a unique's main enchantment - the player decides with their own picks.
  Bonuses should boost what the weapon already does (fast vs slow). Melee lists revised: Echo (cooldown based) off
  the fast weapons - Daggers, Sickles, Tempest Knife get Thundering; Cutlass, Void Touched Blades get Critical Hit;
  Backstabber Void Strike -> Critical Hit; Bone Club Stunning -> Echo; Pickaxe = Prospector, Committed, Echo.
- 2026-10-05 (user): 'I just want to allow stacking for every enchant so it's not useless'. Stack.toml stackable =
  "all": the launcher (switch `stacking` in Launcher.toml) adds tag 0 to all 154 gear enchantments, so the game may
  roll any of them in several slots. Applied live to the running session too. To verify in play: new drops show the
  same enchantment in more than one slot; whether an item can now roll its own built-in as a choice.
- 2026-10-05: user unsure about 'all' (more repeats in the slots = more rng, less variety). Stack.toml narrowed to my
  recommendation, pending the user's word: flat-damage effects only (Thundering, Shockwave, Swirling, Exploding, Echo,
  Poison Cloud melee/ranged, Fuse Shot, Burning, Electrified, Snowball, Fire Trail). Multipliers and utility stay
  as the game has them. The session running at the time still had all 154 marked (new drops only).
  Also (user): Swirling shows no damage numbers on the camp dummies - that is normal, not caused by the tag.
- 2026-10-05 (user, final): no extra stackable marks. 'Leave it to how it was designed in the base game but let our
  new 3 additional enchants ignore the rules' - Stack.toml stackable = [] (launcher part stays, does nothing). Bonus
  built-ins already add to a pick of the same enchantment. Live marks from the test removed from the running game.
- 2026-10-05 ECHO decoded: UEcho (vtable exe+0x32B9548, object size 0x218, constructor exe+0xA4AB10) keeps three
  plain floats in each object: +0x1F8 = 5.0, +0x1FC = 0.2, +0x200 = 2.0. Gap between repeats = [+0x1F8] - (tier - 1)
  (lambda exe+0xA79610) -> 5/4/3 s; +0x200 is the gap when the owner is of another class (mobs, presumably).
  Not reflected, so not settable from the pak, but it is heap data per object: tools/echo_patch.py (launcher switch
  `echo`, Echo.toml) rewrites it on live Echo objects. User wants tier 3 at ~0.1 s -> tier3_gap = 0.1
  (2.1 / 1.1 / 0.1 s). A gap of 0 would never fire (timer). UNTESTED in game. New objects wait for the next scan
  (tools/live_objects.py: shared scanner, whole heap every 30 s, known pages every 3 s).
  The same trick may work for other 'code constant' enchantments whose numbers sit in the object.
- 2026-10-05 (user): Critical Hit is equally good on every weapon - don't treat it as a fast-weapon enchantment.
  Thundering (100% chance, 6 base damage since the first pass) is fine as a bonus as long as it can stack.
- 2026-10-05 (user): happy with Echo at 2.1 / 1.1 / 0.1 s. Thundering confirmed as 2x the base game (7.5 base).
- 2026-10-05: 'code constant' enchantments, how they are built (research/ctor_members.py): each enchantment object
  holds a std::function 'value for this tier' at +0x110 (pointer at +0x148; called as [vtable+0x10](impl, &tier)).
  The lambdas: Critical Hit chance (tier+1)*0.05 = 10/15/20% (exe+0xA790C0); Bonus Shot damage tier*0.07+0.03 =
  10/17/24% (exe+0x713F70); Recycler hits (4-tier)*10 = 30/20/10 (exe+0xACEDD0); Punch tier+2 (exe+0xACEBB0);
  Echo 5-(tier-1). Constants are in code/.rdata (not writable safely), but the function OBJECT is heap data in every
  enchantment object: pointing it at a small routine of our own (new memory, like the A+ level-count copies) would
  give any per-tier values without touching game code. Not built yet; needs the game running to verify.
  Enigma Resonator and Accelerate's 2x clamp are not simple lambdas - not traced.
- 2026-10-05: tools/formula_patch.py + Formulas.toml built (launcher switch `formulas`): replaces the per-tier value
  function on live enchantment objects with a table routine in new memory (no game code changed). Enigma Resonator
  turned out to be a simple lambda too: chance at full souls tier*0.05+0.1 (exe+0xA792E0), one base class for melee
  and ranged. Values set (user 2026-10-05): Bonus Shot 30/50/75% (user floated 100%; held at 75 because copies
  stack - my call, say if 100 wanted), Recycler 15/10/5, Punch 8/12/16 ('crank it to give it a niche'), Enigma
  Resonator 30/40/50% ('higher chance as the parallel to Critical Hit's low chance, high multiplier'). Critical Hit
  left alone. Routine and vtables checked against the exe dump only - UNTESTED in the running game.
- 2026-10-05 PETS (user: 'don't make them too strong but even in base game they were weak'): pet artifacts' own
  settings exposed (EXTRA_ASSETS in sequel.py: TastyBone, GolemKit, WonderfulWheat, RainbowGrass = Enchanted Grass,
  SoulLantern) and set in SequelMod.toml: Tasty Bone / Golem Kit / Soul Lantern health x3 -> x4.5, damage x1 -> x1.5;
  Wonderful Wheat health x3 -> x4.5, damage x1.25, two llamas; Enchanted Grass health x2.5 -> x4, damage x1.25, two
  sheep. Built into the pak; NOT yet seen in game (PetAmountCap 2 in particular is untested).
- 2026-10-06 TRIAL LEVELS (user idea: at break points one mob stat tuned as if A+100, 'maybe even slightly higher
  since A+100 is everything at once'): [[trial]] in Endless.toml, built by endless.apply_trials - at that one level a
  row jumps to a multiple of its A+100 value, back on the curve at the next level. Set: A+55 Horde (mob count x1.15
  of finale = 1.61), A+65 Titans (health x1.15), A+75 Berserkers (damage x1.15), A+85 Undying (revive 20%), A+95
  Enchanted (enchanted chance and power x1.15). Trials pay loot quality 50 and XP x7. Names are only in the config
  (no in-game text yet). Optional levels, not gates (not decided by the user). Built into the pak, not played.
- 2026-10-06 (user: the order of the trials matters, especially the last one before the final levels): reordered to
  build up - A+55 Horde, A+65 Enchanted, A+75 Undying, A+85 Titans (health x1.25 of finale: the damage check),
  A+95 Berserkers (damage x1.3 of finale: the survival check before A+96-100). Late spikes got bigger multiples
  because the normal curve is already close to the A+100 value there. Order and sizes are my proposal.
- 2026-10-06 (user): trials must sit on block tops ('weird when of the 3 levels suddenly things change') -> moved to
  A+55 / 64 / 76 / 87 / 95 (unlock block tops with 3 per step: 28..79 by 3, then 83, 87, 91, 95, 99, then 100;
  the 4-level blocks exist because the game's step list has only 24 free places for 75 levels).
- 2026-10-06 (user: 'should something happen A26 onwards for some spice, like our first tier of extra enchant as a
  taste'): Bonus.toml [thresholds] early = [257] - gear from about A+26/27 gets its first upgrade step already
  (first bonus at tier I, or a tier-1 own built-in to tier II); the rest still starts at 320. Dry run only.
- 2026-10-06 open (user): A+100 gear (power 365) should carry a 'final upgrade to everything'; ideas proposed, none built.
- 2026-10-06 (user: 'weapons should get another enchant then'): Bonus.toml [thresholds] final = 365 - weapons and
  bows at power 365+ (A+100 drops) get a FOURTH bonus enchantment at tier 3: the next unused name of the family list
  (a 4th name added to every melee and ranged list). Armor unchanged (3 bonus enchantments + perks at 330/350).
  Dry run only. Artifact scaling past 315: options listed to the user, nothing built.
- 2026-10-06 (user): artifacts' weakness late is DAMAGE SCALING, not cooldown ('if we can increase that for each
  level I'm happy'; 'damage also includes healing'). Leads from the exe's reflection data (property name -> offset):
  ItemInstance.ItemPower float at +0x484 of each live artifact (default 1.0, so probably the damage/heal scale
  factor, not the power number); player attribute sets hold plain floats: ItemAttributeSet.ItemDamageMultiplier
  +0x3C, MeleeAttributeSet.MeleeAttackItemPowerFactor +0x34 / MeleeHealItemPowerFactor +0x38, RangedAttributeSet
  RangedAttackItemPowerFactor +0x34 / RangedHealItemPowerFactor +0x38, HealthAttributeSet ArmorAttackItemPowerFactor
  +0x64 / ArmorHealingItemPowerFactor +0x68. If these are the live (already capped) factors, writing uncapped values
  would lift the 315 cap for the player's gear as data - TO VERIFY with the game running.
  Test items added to the save (backup character_before_artifact_power_test_*): Lightning Rod and Soul Healer at
  252, 316 and 364 each, to compare the live values and the damage/heal numbers.
- 2026-10-06 live check: reflection offsets corrected (offset FOLLOWS the name pointer): ItemInstance.ItemPower
  +0x480, SharedPassiveCooldown +0x484; ItemDamageMultiplier +0x38; Melee/RangedAttackItemPowerFactor +0x30, heal
  +0x34; ArmorAttack +0x60, ArmorHealing +0x64. ItemPower on a live artifact is the STORED POWER (26.1 / 32.5 / 37.3
  for 252 / 316 / 364), not a factor - the cap is applied in code when it is used, so raising it does nothing.
  The lever instead: each live artifact actor holds its own damage/heal numbers as reflected floats, e.g.
  TargetingStrikeItem (Lightning Rod, vtable exe+0x3337D20) StrikeDamagePerSoul +0x4F8 = 60; SoulHealer (vtable
  exe+0x3339AE0) HealAmountPerSoul +0x4E8 = 4. A watcher can scale those per actor by its ItemPower.
  TEST running: the user's 364 Lightning Rod set to 180 (3x) in the live game - awaiting the damage comparison.
- 2026-10-06 playtest (user): Lightning Rod with its own StrikeDamagePerSoul tripled dealt 3x - per-actor artifact
  numbers work. Built: tools/artifact_scale.py + ArtifactScaling.toml + tools/artifact_fields.json (from
  research/artifact_fields.py), launcher switch `artifact_scaling`. Above 316 each power point multiplies the
  artifact's damage numbers (to x3 at 365) and healing numbers (to x2.2 at 365); pets: damage and health
  multipliers. Unscaled values come from the class default object, so passes repeat safely. Run live once: the
  user's 364 Lightning Rod went 60 -> 176. Mapped: Lightning Rod, Corrupted Beacon, Corrupted Seeds, Harvester, Ice
  Wand, Redstone Mines, Satchel of Elements, Updraft Tome, Mob Masher?, Nether Wart Spore Grenade, Guardian's Eye,
  Soul Healer, Totem of Regeneration, Tasty Bone, Golem Kit, Wonderful Wheat, Soul Lantern. NOT mapped: Spinblade
  (SpinWheel), Enchanted Grass (class not found), quiver artifacts (damage lives on the arrow), buff/utility ones.
  Only Lightning Rod is confirmed in play.
- 2026-10-06 (user): levels past A+25 missing again until the character was re-entered -> the launcher now tries
  the Endless part from 12 s after game start (every 3 s) instead of only after the 40 s settle; untested.
  Selecting A+1 was possible on that screen (base game: not below the previous difficulty) - cause unknown.
- 2026-10-06 open: user wonders about armor HP scaling past 315 'to make the post-post game feel different' and
  argues a real 364-power mob should be beatable. Attribute-set classes not located yet (research/attributes_live.py).
- 2026-10-06 (user: 'yes 5x as long as my overall damage can match too'): A+100 mob health x3 -> x5 of the A+50
  value (table 7.5); artifact damage_at_top 3 -> 5 to match. Mob damage stays x2.2. Titans trial (A+87) follows at
  1.25x the finale. Weapon side rests on the four bonus enchantments plus stacked picks (my estimate 3-5x for good
  lists, not measured).
- 2026-10-06: armor health scaling past 315 NOT pursued (user's own doubt: flat heals like Radiance fall behind, and
  more mob damage adds little to build variety; my view the same). Mob damage stays near x2.2; variety comes from
  the trials' different threats.
- 2026-10-06 (user): drop the A+1 question; artifact damage should simply keep pace with weapons so both stay
  relevant, healing getting strong is fine (health stays capped), enemies must be harder than A+25. Kept: artifact
  damage x5 at 365 = mob health curve. Fireworks Display added to artifact_fields.json (BombDamage,
  ProjectileDamage). Artifacts that would need a different approach: quivers (damage on the arrow), Spinblade and
  Enchanted Grass (not located), buff/utility ones (no damage number).
- 2026-10-06 (user reverses the 'seasonal reskins copy their unique' rule): the 19 seasonal items should become
  their own uniques, each 'a new playstyle or build that its counterpart or any of the same equipment doesn't do
  yet'. They are all released items (tools/wiki_gear.json) and drop from the Tower (wiki: all seasonal gear except
  the Corrupted Pumpkin; rarely merchants / ancient mobs); no loot table in the pak names them.
  PROPOSED identities (not built, awaiting the user):
  Melee - Sinister Sword: Leeching 3 + Radiance 2 (sustain sword); Frost Slayer: Freezing 3 + Shockwave 2 (control
  claymore); Sparkler: Thundering 3 + Exploding 2 (proc cutlass); Skull Scythe: Enigma Resonator 3 + Soul Siphon 2
  (soul crit); Cackling Broom: Swirling 3 + Gravity 2 (pull and sweep); Spine-Chill Spear: Void Strike 3 +
  Freezing 1 (mark and execute).
  Ranged - Haunted Bow: Ricochet 3 + Piercing 2; Shivering Bow: Anima Conduit 3 + Soul Siphon 2 (heal by souls);
  Sugar Rush: Accelerate 3 + Rapid Fire 2 (ramping speed); Phantom Bow: Void Strike 3 + Supercharge 2 (charged
  sniper); Webbed Bow: Shock Web 3 + Gravity 2 (trap bow); Gloopy Bow: Poison Cloud 3 + Chain Reaction 2.
  Armor - Hungry Horror: Thorns 3 + life steal aura (retaliation tank); Hungriest Horror: Reckless 3 + Frenzied 2
  (low-health berserker); Arctic Fox Armor: Beast Burst 3 + Beast Surge 2 (pack leader); Sweet Tooth: Surprise
  Gift 3 + Food Reserves 3 + potion cooldown perk (consumables); Cauldron Armor: Burning 3 + Fire Focus 2 (furnace
  tank); The Spooky Gourdian: Final Shout 3 + Death Barter 2 (last stand); Cloaked Skull: Electrified 3 +
  Multi-Roll 2 (roll zapper).
- 2026-10-06 HANG (user: stuck on the loading screen at launch): the game sat 'Not Responding' at 1.1 GB, busy, 3
  minutes after start. Cause taken to be yesterday's change that applied the Endless part from 12 s after launch
  (the game is still initialising and now sees 100 levels). Reverted: the Endless part runs only after the 40 s
  settle again, but FIRST, before the other launcher parts. Rule: nothing is written before startup is done.
  Other candidates if it hangs again: the pak (pet settings incl. PetAmountCap 2, trials, health x5), formulas, echo.
- 2026-10-06 (user: chance-based effects shouldn't be too low): Poison Cloud trigger chance 30% -> 60%, melee and
  ranged (damage 30/s and radius 400 as before). Not 100%: a cloud lasts 2.5 s, so fast weapons would litter the
  screen. Whether overlapping clouds add damage is unknown (untested).
- 2026-10-06 (user): no pre-A+25 difficulty bump. Wants seasonal gear from normal missions if possible - to
  investigate with the game running (compare a seasonal item's definition with its counterpart for a flag; look for
  mission loot lists in memory). Merchant stock in the save is 246-255 (263 Tower) despite 364 gear held.
- 2026-10-06 (user): the loading-screen freeze was a login problem (signed in on another PC), not the launcher; and
  'no need to wait 40 seconds, 15 is fine'. Launcher now starts at 15 s IF the game's data is there (eight unlock
  steps + an item definition readable), checking every second, 90 s at most; Endless part still first. Untested.
- 2026-10-06 live read: WHERE AN ITEM DROPS is in its definition. At +0xB0: a map level id (byte) -> drop settings
  (TSet, 0x50-byte elements, key at +0, hash links +0x48/+0x4C; inline allocation bits +0xC0; hash +0xE8/+0xF0,
  size +0xF8; flag byte +0x100 = 1). 207 items have 4-39 entries; exactly 21 have an EMPTY map and flag 0: the 19
  seasonal items plus SkeletonHammer and BatCrossbow (Tower-only). Level ids 2-155 are in use (names not mapped).
  So seasonal gear can probably be made to drop in missions by giving it a map (research/drops_test.py copies a
  donor's into new memory) - NOT yet written/tested; unknown whether the game reads the map at drop time or built
  its tables at startup.
  Merchant stock is live item objects too (same vtable as inventory: Coral Blade 251, Battlestaff 247... found;
  162 objects vs 152 saved items), so raising ware power at runtime is feasible in principle.
- 2026-10-06 GILDED (user: 'start to drop gilded weapons post A+26 as a reward, then start the additional enchants
  at the gear cap anyway'): live item layout read from 12 gilded items: +0x88 int flag = 1, +0x8C enchantment id
  byte, +0x90 tier int, +0x94 bytes 00 03 (same on all). bonus_watch.Watch.gild + Bonus.toml [gilded]: gear at
  power 257+ has a 20% chance to be gilded with an enchantment from its bonus list (tier 1/2/3 at 50/35/15%),
  decided once per item from its name and exact power (sha256), written to the item, never to one that is gilded
  already. The early bonus step at 257 is removed again (early = [] by default): bonuses start at 316.
  Built with the game closed: NOT yet run. Applies to gear already held too, and to merchant stock at 257+.
- 2026-10-06 (user: 'can the gilded enchant not be fully random?' - read as: make it fully random): [gilded]
  pool = "any" (default) picks from every enchantment that can roll on that gear type (tools/enchant_pools.json,
  from the game's enchantment list minus built-in-only ones; soul enchantments only on soul gear); pool = "list"
  keeps it to the item's bonus list. If the user meant the opposite, switch to "list".
- 2026-10-06 (user: 'I only want new drops to have a chance'): the launcher reads every character save at start
  (type + exact power of each item, incl. chest and merchant stock) and never gilds those; only items that appear
  later in the session can be. If the saves can't be read, nothing is gilded. A Blacksmith upgrade changes the
  power, so the upgraded item counts as new (one more roll).
- 2026-10-07 prices: Enchantsmith (wiki): gold; base price rises with item power, +10% per further reroll, capped at
  100 gold. In the exe: UEnchantmentMerchantDef (0x70 bytes, ctor exe+0xB77630) holds names/slots only, no numbers;
  pricing sits in UMerchantPricingComponent / UProgressPowerRarityPricing (constructors not found by my pattern) -
  the exact reroll price is NOT located yet; needs a look at those objects in the running game.
  TEST lever set meanwhile: Endless.toml ShopPriceMultiplier = { from = 26, to = 0.2, until = 27 } (all merchant
  prices x0.2 from A+27). Unknown whether it applies to gold prices and in camp.
  Gold (wiki): from Ancient Hunts, seasonal ranks, and SALVAGING GILDED GEAR - so gilded drops are also a gold
  source. Merchant stock (wiki): 'near the hero's power level', taken when entering camp.
- 2026-10-07 (user): gilded should be rolled 'like the game's gilded system'; seasonal items should drop in the same
  missions as their base weapon's other uniques, then each gets a new variation (stats or enchantments).
- 2026-10-07: tools/drops_patch.py + Drops.toml + launcher switch `seasonal_drops` (ON): at launch each of the 19
  seasonal items gets a copy of the mission-drop map of <Family>_Unique1. Never run; first launch is the test
  (look for a seasonal item in a mission's gear list / the launcher's 'now drops in N levels' lines).
- 2026-10-07 PRICES solved: price = base x power factor x rarity (1/1.4/2) x slot multiplier x 3 if gilded x
  (1 - rebate), code exe+0xB8FA70; the base is an int at +0x30 of each merchant's UProgressPowerRarityPricing
  object (vtable exe+0x34C39C8; second int +0x38 = restock price, my reading), owner actor at +0x28, merchant
  named through its definition (vtable exe+0x334BC28: actor class +0x28, unlock key text +0x30). Game's values:
  Enchantsmith 20, Piglin 12/5, Village 100/50, Luxury 200/200, Mystery 150/50, Blacksmith 150, Gift Wrapper 100.
  tools/prices_patch.py + Prices.toml + launcher switch `prices` (watcher: the actors are remade whenever camp
  loads). Set (user: gold prices cheaper in general, not tied to Apocalypse levels): Enchantsmith x0.1 (20 -> 2),
  Piglin x0.5 (12 -> 6, restock 5 -> 2). Applied to the live game 2026-10-07; awaiting the user's look at the prices.
  The ShopPriceMultiplier test row is removed from Endless.toml again.
- 2026-10-07 (user): merchant stock power does NOT go up with higher-power gear equipped.
- 2026-10-07 merchant stock: with totalGearPower 349 the Village Merchant restocked at 253-256, so stock does NOT
  follow equipped gear here (stays near A+25 power). TEST: the five gear wares of the Village Merchant (matched to
  the save's merchant slots by type + exact power) set to power 330 in the live game by writing the item's power
  float (+0x3C) - first time an item's power is written. Awaiting the user's look (shown power, price, what a
  bought item is like).
- 2026-10-07 playtest (user): gold prices are cheaper in game - the base-price change works.
- 2026-10-07 playtest (user): merchant wares written to power 330 show 330 at a reasonable price. Decisions (user):
  stock should follow OUR power level 'so we don't just buy the best stuff'; and it is fine that owning a higher
  copy unlocks the bonus enchantments on all weaker copies of that item (per-type limit accepted).
  Built: bonus_watch.Watch.stock + Bonus.toml [merchants] follow_power = true, below = 5 - weapon/armor stock of
  every merchant (identified from the save's merchant slots, re-read when the save changes) is raised to the
  save's totalGearPower minus 0-5, never lowered; stock objects no longer count as 'held' for the bonus
  enchantments. Artifacts on the shelves are not handled (not in the item registry).
- 2026-10-07 MISTAKE and fix: the first live run of the stock change also raised the item sitting in the
  Blacksmith's slot (the user's own Gauntlets_Unique3, 252 -> 345) and a Tower reward (Full Metal Armor 263 -> 347),
  because every merchant's slots were treated as shop stock. Both written back to their saved power in the live
  game; code now only treats Village, Luxury and Piglin merchants as shops (SHOPS in bonus_watch.py).
- 2026-10-07 (user): shops keep 'whatever formula they had before but just scale beyond base game'; the Blacksmith
  should upgrade 'up to your average power level'. Stock rule changed: the game's own stock (around its ceiling of
  ~254) is shifted up by (totalGearPower - 254), keeping each merchant's spread; only wares at <= 257 are shifted,
  once. Blacksmith: not built - first see what power an upgraded item comes back at (user to test); if pinned near
  255, raise the upgraded item to totalGearPower once the quest is done.
- 2026-10-07 (user): Apocalypse unlocks back to the real rule - Endless.toml [unlock] staged = true (3 levels per
  step, 3 boss missions; A+100 behind 3 bosses on A+99). The game remembers by itself: the save keeps, per mission,
  "completedEndlessStruggle" = the highest A+ level cleared there (a plain number, no cap seen), and the unlock
  steps are worked out from that at every start. Applied by the launcher at start (not a pak setting).
- 2026-10-07 TEST SETTING (user: raise unique drop chance to see whether seasonal uniques drop in missions):
  SequelMod.toml EndlessStruggle.LootQualityBoost.MaxValue 4.1 -> 100 (loot quality at A+25 = the finale's value;
  it also lifts the Endless curve's start). REVERT to 4.1 after the seasonal-drop test.
- 2026-10-07 armor perks vs the Wiper 'every armor stat' tier list (research/transcripts/i03kWHTvitg.txt): top 5 =
  invincible roll, life steal aura, 35% DR, emerald shield, ghost roll; very good = -40% artifact cooldown, 30%
  negate, swarm resistance, -40% potion cooldown, ink roll, +50% artifact damage, +30% positive duration, potion
  resets artifacts, poison roll, 20% weapon aura. Finding: our 330/350 perks give ~30 of 40 families the same
  top-tier pair (35% DR + weapon aura, life steal next) - homogenising. Perk blueprints in the pak expose values
  (Components/ArmorProperties: AllyDamageBoost 1.2, ItemDamageBoost 1.5, Melee/RangedDamageBoost 1.3, MissChance
  0.3, TeleportChance 0.05, ArrowIncreaseAmount 10, DodgeSpeedIncrease 1.5, EmeraldShield 0.75 s, ...), so weak
  perks can be buffed. Proposal put to the user; nothing changed yet.
- 2026-10-07 ARMOR PERKS reworked (user: 'sure' to both levers; 'every armor getting a damage reduction perk at one
  point helps as the enemies scale damage and we don't scale hp'): Bonus.toml [armor_perks] levels = [330, 345, 360],
  each family list = [archetype perk, 35% DR, second archetype perk, spares: 30% negate, life steal]; an armor takes
  the first it lacks. Weak traits buffed in the pak (perk blueprints added to sequel.py EXTRA_ASSETS): healing boost
  25% -> 50%, movement speed aura 15% -> 25%, ranged damage perk 30% -> 40%, teleport-when-hit 5% -> 15%. Arrow
  bundle size not exposed. In-game perk text will still show the old percentages. Nothing played yet.
- 2026-10-08: perk texts for the four buffed traits written out in SequelText.toml (ArmorProperties/*_description;
  the originals use {0}, which may have followed the new values anyway - not checked in game).
- 2026-10-08 build-craft review (user: do the four points in order; then boost C, then B tiers). MCD2 looked up
  (about 34 enchantments, one per item, books; 4 armor pieces; talismans) - verdict: structural ideas, few new effects.
  Done:
  1. Artifact-centred builds: Artifact Synergy +60/80/100% -> +150/200/250% (base 2.0, 0.5 per level). Health
     Synergy found (tier*0.01+0.02, exe+0xA794E0, in formula_patch KNOWN) but left alone - already top tier.
  2. Armor bonus enchantments by archetype (Bonus.toml [armor]): tanks get Thorns, brawlers Cowardice/Frenzied,
     assassins and roll armors Acrobat/Multi-Roll/Swiftfooted, casters Cool Down + Health/Speed Synergy/Final Shout...
     The Potion Barrier + Protection + Cool Down trio stays only as the fallback.
  3. The 19 seasonal items built as uniques of their own (Builtins.toml, per-item bonus lists, two perks), as in
     the table of 2026-10-06 with three test effects swapped in: Frost Slayer Freezing 3 + Shared Pain, Spine-Chill
     Spear Void Strike 3 + Rushdown, Phantom Bow Void Strike 3 + Supercharge 2 + Shadow Shot. Tests - keep only if
     they work on those items.
  4. Random pool untouched.
  C tier: Broadsword Sharpness 3, Great Axeblade Dynamo 3, The Beginning and The End Void Strike 3 + Leeching 3, The
  Last Laugh + Critical Hit 2, Doom Crossbow + Power 2, Rapid Fire 10/15/20% -> 20/35/50% (formula patch; lifts Azure
  Seeker, Purple Storm, Sugar Rush), llama and sheep damage x1.25 -> x1.75. Gravity Pulse left (user).
  B tier, untouched items only: Growing Staff Committed 3, Fortune Spear Looting 3 + Committed 2, Rugged Climbing
  Gear + 30% negate, Shock Powder cooldown 15 -> 10, Totem of Shielding 20 -> 12. The rest of B was already buffed
  once and is unplayed - no second blind bump.
  All of it built, none of it played.
- 2026-10-08 (user: seasonal items must drop in the same places as their base items): Drops.toml entries are now
  lists - each seasonal item gets the levels of its family's uniques AND its plain base item together.
  drops_patch.give_map builds a fresh TSet (elements, inline allocation bits, 64/128 hash buckets with chains;
  bucket = level id & (buckets - 1)); checked offline against a fake memory (lookups by key succeed). Never run in
  the game.
- 2026-10-08 playtest (user): with LootQualityBoost 100 at A+25 no unique dropped in a run (only a raid captain's
  Hawkbrand). The game's own text for that stat is 'Reroll for rares {0} times': it rerolls common -> rare only.
  Uniques come from LUCK ('boosts the chance that rare drops become unique', Luck of the Sea). So loot quality is
  not the unique lever; the Endless design's 'more uniques via LootQualityBoost' assumption is wrong.
  TEST SETTINGS now on (remove after the seasonal-drop check): Luck of the Sea tier 3 = +3000% (SequelMod.toml
  luck_level_3 30, normal 0.75) and Luck of the Sea 3 built into Full Metal Armor (Builtins.toml); LootQualityBoost
  MaxValue still 100 (normal 4.1).
- 2026-10-08: the launcher now also writes what it prints to Mods/SequelMod/launcher.log (last session only), so a
  session can be reviewed afterwards - until now nothing it printed could be seen from here.
- 2026-10-10 KILL CREDIT (user agreed to split into lanes; idea: a unique may stack its own base enchantment):
  Bonus.toml melee lists now stay in one lane - PROC (Fire Aspect, Poison Cloud, Thundering, Shockwave, Swirling do
  the killing) or ON-KILL (Leeching, Exploding, Rampaging, Prospector, Busy Bee, Rushdown need the weapon's kill) -
  filled with neutral ones (Critical Hit, Committed, Void Strike, Echo, Stunning, Chains). Families changed: Axe,
  Cutlass, Daggers, Double Axe, Gauntlets, Obsidian Claymore, Rapier, Sickles, Tempest Knife. A script check finds
  no list mixing the two groups. Slower-but-heavier stats were NOT applied: at equal damage per second the tick's
  share of kills is unchanged (my reasoning, not measured); Void Strike goes on the fire/poison uniques instead.
  New list syntax "Name!": a second copy of the item's own built-in (bonus_watch.wanted). Used for Firebrand (Fire
  Aspect), Stormlander (Thundering), Venom Glaive and Nightmare's Bite (Poison Cloud), Whirlwind (Shockwave), Sun's
  Grace (Radiance), Cursed Axe and Battlestaff of Terror (Exploding), Heartstealer (Leeching), Dancer's Sword and
  Maulers (Rampaging). Sparkler's second built-in Exploding -> Critical Hit (Thundering would starve Exploding).
  Dry run only.
- 2026-10-10 CORRECTION on Void Strike (user: slow weapons use it best; match the new void weapons to the top
  users' speed and damage). Wiki: the mark resets on each weapon hit and 'if the voided target takes damage from
  another source, the multiplier damage applies and the Voided effect ends' - so burn/poison ticks, lightning and
  shockwaves cash it in early. Void Strike REMOVED from Firebrand, Stormlander, Venom Glaive, Nightmare's Bite
  lists (my suggestion of the same day was wrong). Reference users (SequelGear.toml): Encrusted Anchor 238 dmg
  every 2.5 s; Obsidian Claymore / Starless Night 150 + 285 at 0.7-1.3 s; Void Touched Blades 60-95 at 0.25-0.7 s
  (rated 'not strong'). Spine-Chill Spear (built-in Void Strike 3) retimed to match: thrusts 0.375/0.375/0.5 s ->
  0.9/0.9/1.2 s, damage 60/60/100 -> 140/140/200 (160 dmg/s before void, was 176). How long the mark takes to
  reach its maximum is NOT known (not in the files, not on the wiki). Unknown too whether a longer
  AttackAnimationTimeDurationSeconds really slows the swing (open since the axe pass).
- 2026-10-10 (user, correcting me): indirect damage should NOT disable Void Strike; the point of slower attacks is
  to let the mark build between hits. Void Strike is back on Firebrand, Stormlander and Venom Glaive, and those
  three are retimed slow and heavy at about the same damage per second: Firebrand 0.5/0.5/0.8 s -> 0.9/0.9/1.3 s,
  105/105/155 -> 190/190/270; Stormlander 0.7 s -> 1.1 s, 125 -> 200; Venom Glaive 0.5/0.6/1.0 s -> 0.9/1.0/1.4 s,
  75/75/110 -> 135/135/190. Nightmare's Bite stays fast without Void Strike. Spine-Chill Spear keeps its retiming.
  The wiki's 'damage from another source ends the effect' stands against the user's statement - to settle in play.
- 2026-10-10 (user, from play): the Void Strike mark takes up to 3.5 s to reach its maximum and lasts about 5 s;
  'weapons don't have to be too slow to still make use'. Retiming eased to a middle pace (about 0.75-0.9 s between
  hits, same damage per second): Firebrand 0.7/0.7/1.0 s at 147/147/215; Stormlander 0.9 s at 162; Venom Glaive
  0.7/0.8/1.2 s at 105/110/150; Spine-Chill Spear 0.7/0.7/1.0 s at 110/110/160. If the mark grows evenly (my
  assumption), a hit every 0.8 s carries about 23% of the maximum: tier III = roughly +140% per hit.
- 2026-10-10 TEST (user: a Firebrand with slower swings to test): SequelGear.toml Firebrand swing times set to
  1.4 / 1.4 / 2.0 s (design value 0.7 / 0.7 / 1.0) so a change in speed cannot be missed - RESTORE afterwards. A new
  Firebrand (power 253, Void Strike in every slot's choices) added to the character; backup
  save_backups/character_before_firebrand_test_*.
- 2026-10-10: for the swing-speed comparison a plain Axe and a Highland Axe (both power 253) added next to the test
  Firebrand; backup save_backups/character_before_axe_compare_*. Plain Axe = the game's 0.5/0.5/0.8 s; Highland Axe
  = the mod's faster 0.42/0.42/0.65 s; test Firebrand = 1.4/1.4/2.0 s.
- 2026-10-10 (user: A+22-25 needed 7 boss missions in the base game - key thresholds should too): Endless.toml
  [unlock] key_levels = [49, 55, 64, 76, 87, 95] with key_bosses = 7, finale_bosses 3 -> 7. The step you clear ON
  those levels (to open the next block) asks for 7 different boss missions; all other steps stay at 3. Base game
  counts for reference: 1/2/3/4/5/6/7 bosses for A+6/9/12/15/18/21/25. Applied by the launcher at start; not run.
- 2026-10-10 (user: the base game's requirement rose over time - either one fixed number, or scale up and reset):
  [unlock] ramp = true - between key levels the steps ask for 1, 2, 3... bosses (cap 6) and start again at 1 after
  each key level; key levels and the finale ask for 7. 14 boss missions exist (wiki: Pumpkin Pastures, Soggy Swamp,
  Redstone Mines, Fiery Forge, Desert Temple, Obsidian Pinnacle, ???, Treetop Tangle + 6 DLC: Overgrown Temple,
  Frosted Fjord, Lone Fortress, Gale Sanctum, Abyssal Monument, Broken Citadel), each counted once per level - my
  split into base/DLC is from memory, not from the wiki page. Not run.
- 2026-10-10 (user: we have the DLC so the count can go higher; A+25 -> 26 is a breakpoint and should ask for more):
  [unlock] key_bosses 7 -> 10, finale_bosses 12, key_levels now starts with 25 (10 bosses on A+25 to enter Endless).
  In-between steps still ramp 1, 2, 3... and reset after each key level. 124 boss missions in all from A+25 to 100.
  Counts above 7 have never been tried in the game (the base game's own maximum is 7) - first thing to verify.
- 2026-10-10 (user: no jump to 10; after 50 it should go back down; 'a 3 to 7 limit is ok'): [unlock] key_bosses 7,
  finale 7, ramp_from 3 - in-between steps go 3, 4, 5, 6, 7 and start over at 3 (also after each key level). Key
  levels (25, 49, the five trials) ask for 7. My reading of the request; 120 boss missions in all.
- 2026-10-10 (user: 9 or 10 is fine for the key breakpoints - into 26, 50 and 100): [unlock] major_levels = [25, 49]
  with major_bosses = 10, finale_bosses = 10; trials stay key levels at 7; in-between steps 3-7 rising and resetting.
  129 boss missions in all. Counts above 7 are untried in the game (its own maximum is 7).
- 2026-10-10 (user: the trials should be equidistant, in 3-level gaps): blocks are now listed outright ([unlock]
  tops, endless_patch.step_tops): A+26-49 in seven blocks (4,4,4,3,3,3,3), from A+50 always 3 levels, last stretch
  A+95-99, then A+100. Trials moved to every third block top: A+58 Horde, 67 Enchanted, 76 Undying, 85 Titans,
  94 Berserkers - 9 levels and 3 steps apart, the same from the A+49 gate to the first trial. Boss counts per
  stretch: 3, 4, then 7 on the trial; 10 on A+25, A+49 and A+99. 128 boss missions in all. Pak rebuilt; not run.
- 2026-10-10 (user: why blocks of 4 from 26 to 49 - can it not be 3 throughout? / is it a game limitation): yes -
  the game's unlock list has room for 32 steps, 8 of them its own, and 3-level blocks need 25. The launcher now
  replaces the list with a longer one of its own (64 places; endless_patch GROWN_ROOM) when more than 24 steps are
  asked for. [unlock] tops = 28, 31, ... 49, 52 ... 94, 99, 100 (25 steps, all 3 levels except A+95-99).
  Boss counts 10 / 3,4,5,6,7,3,4 / 10 / then 3,4,7 per trial stretch / 10: 131 in all. The longer list is untried:
  if unlocks misbehave, the fallback is the 24-step layout with three 4-level blocks at the start.
- 2026-10-10 (user: then bigger gaps up to 50 and several steps at the end to 100): tops = 30, 35, 40, 45, 49 /
  52..94 by 3 / 96, 98, 99, 100 - exactly 24 steps, so the game's own list is enough and the longer-list swap is
  not used (code kept). Boss counts: 10 on A+25; 3, 4, 5, 6 on A+30/35/40/45; 10 on A+49; 3, 4, 7 per trial
  stretch; final run 3 on A+96, 4 on A+98, 10 on A+99. 125 boss missions in all. Not run.
- 2026-10-10 (user): the final run asks for 7 bosses on every step (A+94, 96, 98) and 10 on A+99 - 96 and 98 added
  to key_levels. 132 boss missions in all.
- 2026-10-11 RANGED across the board (user: bows were weak in the base game; 'sure let's do it'): about +25% for
  every bow and crossbow family (SequelGear.toml, 49 values). The game files only hold an arrow damage factor for
  12 families, so three levers: (a) damage factor x1.25 - Cog, Crossbow (now 2.25, +50% over the game), Dual,
  Exploding, Heavy, Hunting, Longbow, Power Bow, Rapid, Shortbow, Soul Crossbow, Trickbow; (b) no stored factor:
  charged shots x1.25 and shots 10% faster - Bow, Bubble, Harpoon, Snow, Soul Bow, Twisting Vine, Void, Wind
  (incl. the uniques that carry their own copy of those numbers); (c) neither: fires 25% more often - Bat, Scatter,
  Shadow crossbows; Burst crossbows fire 4 bolts instead of 3. S-tier bows are lifted with the rest (category
  buff); Burst Bowstring left alone, so the roll build gains too. Nested weapon fields can't be added to a
  blueprint that doesn't store them (tried). Not played.
- 2026-10-11 (user): breaking the 'S tier untouched' rule is fine for ranged - it is inherently the weaker category
  ('you can't solo with it'). The rule still holds for melee, armor, artifacts and enchantments. Burst Bowstring
  stays as it is (the roll build keeps its gain).
- 2026-10-11 (user: can an enchantment such as Deflect be removed from the mob pool?): from the 2026-10-05 dump of
  the 162 enchantment definitions, byte +4 = 0 (never on mobs) / 1 (mob-only: Double Damage, Fast Attack, Quick) /
  2 (melee mobs) / 4 (ranged mobs) - my reading, it matches the known mob enchantment lists. tools/mobpool_patch.py
  + MobPool.toml (remove = ["Deflecting"]) + launcher switch `mob_pool` set that byte to 0. Never run.
  Also asked: regenerating arrows like MCD2 - not built; needs the player's arrow count located in the running game.
  Lead for arrow regeneration: the arrow count is a reflected int, ItemSlot.Count, most likely at +0x1FC of the
  player's UArrowItemSlot object (class vtable exe+0x32F7D60, size 0x2B0; from the exe dump, not read live yet). A
  watcher could add arrows over time. Rate and limit to be decided by the user.
- 2026-10-11 ARROW REFILL built (user: refill up to a bundle, every 3 s is fine, only while not shooting):
  tools/arrows_patch.py + Arrows.toml + launcher switch `arrows`. Each 3 s pass: if the player's arrow count
  (UArrowItemSlot +0x1FC) hasn't dropped since the last pass, add bundle*3/30 arrows up to one bundle of the
  equipped bow (bundle size from SequelGear.toml, equipped bow from the save). Offsets come from the exe dump only;
  never run. Class-default objects are skipped by object flag 0x10.
  Left OFF (refill = false) until `python tools/arrows_patch.py --show` has shown, with the game running, that the
  number at that place really is the arrow count - it would be the first write to an offset never read live.
- 2026-10-11 CORRECTION: the 'mob pool marker' (definition byte +4) is wrong. Against the wiki's lists (any mob:
  Burning, Chilling, Deflect, Double Damage, Electrified, Fast Attack, Fire Aspect, Fire Trail, Freezing, Frenzied,
  Gravity Pulse, Heals Allies, Poison Cloud, Protection, Quick, Radiance, Regeneration, Rush, Thorns, Weakening;
  ranged only: Accelerate, Bonus Shot, Chain Reaction, Critical Hit, Gravity, Growing, Levitation Shot, Multishot,
  Power, Radiance Shot, Rapid Fire, Ricochet, Tempo Theft, Void Strike; ancients only: Committed, Cowardice, Echo,
  Fuse Shot, Huge, Leeching, Rampaging, Sharpness, Shockwave, Swirling, Thundering) the byte doesn't fit.
  mob_pool switched OFF, MobPool.toml emptied before it ever ran. User wants Deflect, Thorns and Levitation Shot
  out of the mob pool and asks whether more can be added: open - the pool itself is not located (not in the pak;
  simple searches of the exe dump found nothing). Next: look at MobEnchantmentComponent in the running game.
- 2026-10-11 (user: instead of removing them, can we tweak the damage mob enchantments deal?): yes for most - the
  pak exposes the mob-side numbers (Thorns PercentDamageReturnedMob, Burning MobBurnDamage, Fire Aspect / Poison
  MobDamagePerSecond, Electrified MobZapDamage, Shockwave / Thundering MobDamage, Swirling MobSwirlDamage, Power
  MobDamageMultiplier, Growing, Committed, Radiance MobHealing, Regeneration, Weakening, Tempo Theft, Chains, Gravity).
  Done: mob Thorns returns 5% of the damage dealt (was 10%). Levitation Shot has NO separate mob number, so the
  mod's own x2.5 fall-damage buff probably applied to mobs' shots too - put back to the game's 0.1 per level and
  the text override removed. Deflect has no number in the files (a chance, in code).
- 2026-10-11 (user: for MOBS - nerf Thorns, remove Levitation Shot, nerf Deflect damage; 'spend all the time on how
  to either remove it or nerf it'). Offline findings: Deflect's handler (Deflecting vtable slot 139, exe+0xA6F6B0)
  rolls the chance from the usual per-tier value function (tier*0.1+0.15 = 25/35/45%, lambda vtable 0x32C8290),
  only when its owner's byte +0x118 == 3, then swaps the projectile's class through ProjectileToDeflectedClasses
  (burning/thundering arrows -> plain BP_BowArrow) and sends it back; no damage factor of its own was found, so the
  returned arrow presumably keeps the shooter's damage. Enchantment objects hold their owner at +0xE8 and tier at
  +0x1D8, so a mob's copy can be told from the player's and treated alone - plan: per-object changes on mob-owned
  copies only (Deflect chance via formula patch, Levitation Shot's own numbers set to nothing). Needs one live look
  with enchanted mobs around: research/enchant_owners_live.py (read-only) is ready. Mob Thorns 5% -> 3% now.
- 2026-10-11 (user: no deflect damage to nerf - just take it out): tools/mob_enchants.py + MobEnchants.toml +
  launcher switch `mob_enchants`. Per copy, only when the owner (+0xE8) is a MobCharacter (the game's own ancestor
  test: class +0x30 chain / +0x38 depth; MobCharacter class = global exe+0x454F5A0): Deflecting's chance function
  is replaced by a table of zeros; Levitation / LevitationMelee / LevitationRanged get Duration, EffectStrength,
  LaunchStrength and FallDamage set to 0. The player's copies are untouched. All from the exe dump; the two
  Levitation sub-class vtables (0x32C47A0, 0x32C4CA0) are guessed from their position. Never run. A new mob's copy
  is changed at the next pass (up to 3 s in known memory pages, up to 30 s otherwise), so a mob can still deflect
  in its first seconds.

## 2026-10-12 Ranged bonus lists review, Radiance at the feet (test)
- Reviewed the `[ranged]` lists in Bonus.toml: most lean on generic MultiShot / Infinity / Ricochet instead of the family's identity; no bow unique has a signature copy ("Name!") yet. Revision proposed to the user, NOT applied yet.
- New enchantments cannot be created; existing ones can be re-tuned, reused as built-ins, or changed per object.
- Radiance: RadianceMelee (object 0x220) and RadianceRanged (0x218) are separate classes sharing five numbers (+0x200..+0x210); none of them is the spawn place. Ranged spawns its circle at the arrow's impact.
- TEST: Sabrewing (PowerBow_Unique2) given RadianceMelee 1 as an extra built-in to see whether the melee version (circle at the player) fires from bow shots. Remove after the test.

## 2026-10-12 Gear strength cap moved from A+50 to A+38
- User: the climb to A+25 was fine, so the climb to 38 at the same pace will be too. `[power] cap_level = 38` in Endless.toml (was 50). Gear power 254 at A+25 -> 315 at A+38 (about 4.7 per level, the game's own pace; mobs follow the game's own scaling, which stops at A+38 anyway), then 316 -> 365 over A+39..100 (unlocks only), 324 at A+50.
- Unlock gates and trials unchanged. Pak rebuilt. Not yet played.

## 2026-10-12 Longer trials, higher top, curves start at A+38
- User: with the cap at 38 there is room for trials to last longer, and the final difficulty can be a bit higher.
- Trials now cover their whole 3-level unlock block (`levels = 3`; tools/endless.py apply_trials supports a span): 56-58 Horde, 65-67 Enchanted, 74-76 Undying, 83-85 Titans, 92-94 Berserkers. Gates unchanged.
- `[natural]` curves start at A+38 (were flat to A+50): mob health x6 by A+100 (was x5), damage x2.5 (was x2.2); the healing / stun / knockback / endurance give-backs also start at 38. Trials are multiples of the A+100 value, so they rose with it (Titans = x7.5 of the A+38 health).
- ArtifactScaling.toml follows: damage_at_top 6.0, heal_at_top 2.5. Pak rebuilt. Not yet played.

## 2026-10-12 Seasonal drops: first pass ran too early
- Launcher printed "no usable level list - skipped" for all 19 seasonal items: at the launcher's first pass the donors' level lists were still empty (the game fills them later). Run by hand with the game in camp, all 19 got their lists (8-24 levels each).
- Fix: drops_patch.apply returns how many items are still waiting; a `Drops` watcher in play.py repeats it every pass until none is left. Whether the items then actually drop is still to be seen in a mission.

## 2026-10-12 Test results from the user
- Radiance: both the melee and the ranged enchant spawn their circle at the enemy hit, not at the player. No "healer bow at your feet" this way; Sabrewing's test RadianceMelee removed.
- AttackAnimationTimeDurationSeconds DOES change swing speed (test Firebrand at 1.4/1.4/2.0 was clearly slower). Firebrand set to its design timing 0.7/0.7/1.0 s (game: 0.5/0.5/0.8) with damage 147/147/215 (game: 65/65/100). Takes effect after the next build (game was running).
- Void Strike's mark raises burn damage (user saw it).
- Echo tier 3 "doesn't repeat instantly": the launcher did write the gap (launcher.log), and the one live Echo object read tier 1 with base 2.1. Open: which weapon / tier the user tested, and what the 0.2 at +0x1FC does.

## 2026-10-12 Echo and mob Deflect "not working": new objects were found too late
- User: Echo tier 3 (Gauntlets) not faster in play although the text shows the tiers; mobs still deflect.
- Both patches change one object each (an Echo object's gap, a mob's Deflect chance function) and the launcher only found NEW objects at its heap scan every 30 s - which itself takes ~15 s during which nothing else ran. A freshly equipped weapon or a freshly spawned mob was therefore unpatched for most of the time it mattered. (Echo's code checked again: gap = lambda([+0x1F8] - (tier-1)) for players, [+0x200] for mob owners, timer resets the ready flag +0x210; the patch itself is right.)
- Fix (tools/live_objects.py): the game's object list (GUObjectArray, chunk table at exe+0x4696848, entries 0x18 bytes, found via a known object's index at +0xC; 663k objects) is read and compared every pass (7 ms); new objects of a registered kind are picked up at once. The heap scan now runs in a thread beside the passes (still needed for non-UObjects: items, prices). play.py: passes every 1 s; Echo, mob enchantments and formulas tick every pass, the rest every third.
- A stand-in script runs these three watchers against the user's current game until it is restarted. Not yet confirmed in play.
- 2026-10-12 (user): Echo works with the fast object list. Many uniques in Creeper Woods (luck test armor) but no seasonal one - inconclusive: the lists were given by hand mid-session, the game may build a level's loot table earlier.
- Level ids mapped: the ELevelNames table in the exe dump (name pointer + value pairs ending at 0x3485020) -> tools/level_ids.json (161 levels; creeperwoods = 2). Seasonal items that now list Creeper Woods: Sword_Spooky1, Spear_spooky2, Bow_Spooky1, SoulBow_Winter1, WolfArmor_Winter1. BubbleBow / SlowBow / GhostArmor seasonals have only DLC or non-main levels.
- User asks whether hub merchants could sell seasonal items: not done yet; option = change the type of a stock item (same objects bonus_watch already edits) or see whether the level lists already feed the merchants.
- 2026-10-12: Whispering Spear (Spear_Unique1) built-in Echo raised from tier 1 to 3 (user: its Echo was still slow - tier 1 = 2.1 s gap). Applied live as well.
- 2026-10-12 (user: any weapon with Echo should be buffed, Echo is weak): Swift Striker (Backstabber_Unique1) built-in Echo 1 -> 3 too. With the Whispering Spear these are the only two built-in Echos (Spine-Chill Spear's was replaced by Void Strike).
- 2026-10-12 arrows: live read in Creeper Woods: 33 objects with the ArrowItemSlot vtable, 32 at 0 and one at 117 (the player's, to be confirmed by the user). Refill switched ON (Arrows.toml refill = true); only slots that have been seen holding arrows are refilled. Takes effect at the next launch.
- 2026-10-12 blacksmith (user: 1 run instead of 3? why 'A+6 or higher'?): the save keeps each upgrade as a quest: merchantData.Default__BlacksmithMerchantDef.quests.UpgradeQuestN = {selectedProgressStat: WIN_MISSIONS_APOCALYPSE_PLUS_TIERn, startedAtCount, targetCount = started + 3}. The three quests on record use TIER1 / TIER5 / TIER6, so the difficulty band is chosen per item (the Boots of Swiftness are power 148 -> a low band). The 3 is not in the pak (quests are native) and was not found by a quick heap search; open.
- 2026-10-12 (user): the 10-boss gate moved from A+49 to A+40 (major_levels = [25, 40]): gear now caps at 38, nothing special at 49. Counts A+25..55: 10, 3, 4, 10, 3, 4, 5, 6, 7(58).
- 2026-10-12 (user): the final run A+95-99 repeats the five trials, one level each (Horde, Enchanted, Undying, Titans, Berserkers), then A+100. Added as five more [[trial]] entries; in the pak at the next build.
- 2026-10-12 seasonal drops, second look (user: uniques drop, never a seasonal one): an item definition points at its plain item at +0x228 (Sword_Unique1/2 -> Sword_Steel; plain items have 0). 13 of the 19 seasonal items had 0 there (the 6 with a link: Cutlass_Year1, Spear_spooky2, BubbleBow_Spooky2, Trickbow_Year1, SpelunkersArmor_Year1, and SkeletonHammer). Guess: a unique drop is picked among the definitions whose +0x228 is the plain item that dropped. drops_patch now also writes that link (taken from the family's uniques); applied live. No per-family list of uniques exists by pointer in memory (a unique's definition is referenced only by the registry array, a name map and one all-items weight list), which fits "picked by walking the definitions". NOT confirmed in play.
- 2026-10-12 (user: gold reroll still expensive): live read shows the Enchantsmith base at 2 (of 20) and the piglin merchant at 6 / 2. Likely the same lateness as Echo: camp actors are remade on each return to camp and the old launcher only found them at its 30 s heap scan. The fast object list should cover it from the next launch; to check.
- 2026-10-12 arrows (user: the bow started with 80, files say bundle 60): refill cap = the slot's count when first seen if that is between one and two bundles, else the bundle. Pak rebuilt after the game closed (Firebrand timing, trials 3 levels + final run, cap 38, Sabrewing test out).
- 2026-10-12 (user): arrow refill scrapped for now - it worked (51 -> 60 seen live) but the HUD number only redraws when the game changes the count, and Infinity (stackable) is enough. Arrows.toml refill = false, Launcher.toml arrows = false; code kept.
- 2026-10-12 (user: mobs still deflect, and every time): the handler (exe+0xA6F6B0) deflects when roll < chance OR the object's bAlwaysTrigger byte (+0x1DF) is set. "Every time" fits mob copies carrying that byte, which makes the chance (already zeroed by us) irrelevant. mob_enchants.py now also clears +0x1DF on mob-owned Deflecting copies when the configured chance is all zeros. Inferred from the code; no mob copy was alive to read when checked, and the game was closed before the new watcher could run. (MobDeflectChance exists as an A+ table row but is off - IntroducedAt 999 - so it is not the source.)
- 2026-10-12 TEST: EnchantedMobChanceMultiplier MaxValue 4.25 -> 30 (A+25 gets ~7x the enchanted mobs; the A+26+ curve grows from it too) so mob Deflect / Levitation can be checked. Put back to 4.25 afterwards.

## 2026-10-13 Weapon card bars (power / speed / area / ammo)
- The bars are stored scores, not computed: Dungeons/Content/Packaging/ItemInstanceDataLookup, map item id -> entries {ItemStatsID (AverageDamage, AttackSpeed, AreaDamage, QuiverAmmo), ScoreInt, ScoreFloat, ScoreMax 14}. The game's power score is close to 0.083 x the combo's average damage.
- tools/bars.py (called from `sequel.py build`): for every weapon SequelGear.toml changes, the game's score is scaled by the change (damage, 1/swing time, range^2 x cone; ranged: damage factor or charge multiplier x projectiles, 1/rate, bundle) and clamped to 1-14; ScoreInt and ScoreFloat overwritten in place (file size unchanged). 65 weapons updated, e.g. Firebrand power 6.3 -> 13.9, speed 2.1 -> 1.6. Built; NOT yet seen in game.
- Same day: mob Deflect - user saw mobs no longer deflect after the always-flag fix (not proven by a direct read); Echo confirmed working after the launcher's start-up scan.

## 2026-10-13 Launcher: watchers rebuilt on the game's object list (activation delays)
- User: Echo / Deflect changes come with a delay after start; later "bonus enchants gone" style effects. Causes found: (1) the first heap scan blocked the watch loop for 15-55 s; (2) `pid_of()` (tasklist) cost 0.24 s per pass; (3) the page-based tracking lost objects - the log shows item types flapping between "best copy 364" and "best copy 0", which strips bonus built-ins; a second look with the new scanner found live mob Deflect copies the old launcher had never touched.
- tools/live_objects.py rewritten: every one of the 31 watched kinds is in the game's object list (items too), so objects are tracked from that list alone - first look through it ~1 s (pages read once, not per object), a diff every pass (7 ms), a full re-validation pass 9 ms (still of its kind and still held by the list), a sweep of the whole list every 120 s as a net. The heap scan stays only for kinds that never show up in the list (none today). `Scanner(wait=False)` for the launcher (no blocking), default wait=True for one-off tools.
- tools/play.py: five passes a second; `poll()` passes hand objects first seen in the last 3 s to the quick watchers (Echo, mob enchantments, formulas); every 5th pass everything for those + prices; every 15th the rest. Liveness by `memprobe.alive(h)` (GetExitCodeProcess, 1 us).
- tools/bonus_watch.py: bonuses are only taken away after an item type's best copy has been lower for 90 s (level loads make items vanish for a moment; a character built then would lack its bonuses all mission).
- Tested against the running game with a stand-in loop: everything found 2.1 s after start, 4.4 passes/s, poll 10 ms, second-pass 21 ms. The stand-in's own bonus Watch wrote one extra built-in (Ricochet) on the Bubble Burster for that session - a test artefact, gone with the game's restart.
- Weapon card bars: user confirms they change in game.
- Seasonal drops: user still sees only base-game uniques with level lists AND the base-item link set -> the game does not pick uniques that way; open.

## 2026-10-13 Seasonal drops: the seasonal mark (found in the registration code)
- Every item is registered by its own function. Compared Sword_Unique1 (exe+0x176F10) with Sword_Spooky1 (exe+0x176CA0): the seasonal one sets a byte in its builder (+0x1C9 = 1) and is finished by exe+0xB65A70 instead of exe+0xB659A0 (the same code minus "builder+0x1D0 = plain item" and one inherited flag). The definition's constructor exe+0xB19D90 stores builder+0x1C9 at definition +0x1E1 and builder+0x1D0 at +0x228.
- +0x1E1 is the item's seasonal event (1-5: 1 = Spooky1, 2 = Winter1, 3 = Year1, 4 and 5 = the two halves of Spooky2; 0 = none). exe+0xB654F0 is "is seasonal"; the loot filters (exe+0xB09440, B09690, B09C80, B0E76B ...) all end with "and not seasonal". That is why seasonal gear never drops whatever its level list says.
- Other definition fields learned: +0x80 kind (dword), +0x89 category (0x0A melee, 0x0B ranged, 0x0C armor), +0x1DA/+0x1DB rarity override (2 = unique) and its "is set" byte, +0x1E0 a flag uniques inherit from their plain item.
- tools/drops_patch.py now also writes +0x1E1 = 0 for every item of Drops.toml (besides the level list and the family link). Side effect to expect: the item card may lose its seasonal marker. Not yet played.
- 22 items carry a seasonal mark: the 19 in Drops.toml plus Bonehead Hammer (SkeletonHammer, 5), BatCrossbow (5) and the Corrupted Pumpkin artifact (CorruptedBeacon_Spooky1, 1). Those three are not touched (could be added the same way).

## 2026-10-13 The mob enchantment pool (found in the registration code)
- research/enchant_flags.py lists what each enchantment's registration writes straight into its definition: +0x00 gear, +0x02 powerful, +0x04 (1 / 2 / 4, still unexplained), +0xD0 "not for players' random rolls", +0xD3 switched OFF for every enchantment mobs never roll (Looting, Leeching, Sharpness, Infinity, Punch ...). The enchantments left with +0xD3 on are the wiki's mob lists almost exactly (only Rapid Fire differs).
- The roll: exe+0xA5FFD0 -> exe+0xA7A630 -> exe+0xA7ACB0 walks all definitions (0x140 bytes each; by id through the table at global exe+0x44EF680) and keeps those passing exe+0xA7B780: +0xD5 == 0, +0xD3 != 0, tag list without tag 2, gear byte fits the mob, version not newer. Built per mob, nothing cached.
- tools/mobpool_patch.py rewritten on that (+0xD3; the old +4 theory is gone): MobPool.toml `remove = ["Deflecting", "LevitationShot"]`, `add = []`; launcher switch mob_pool = true. Bosses with an enchantment by design are not rolled, so they keep it - unlike the per-object override in mob_enchants.py, which also silences a boss's own Deflect. Once the pool removal is seen working, MobEnchants.toml should be emptied for that reason.
- "Add enchantments to mobs" is now possible the same way (`add`), untested; candidates the game itself puts on ancients: Leeching, Sharpness, Cowardice, FuseShot.
- Level lists are LAZY (exe+0xB65390, "does this item drop in level X"): the map at +0xB0 has a "made" byte at +0x100 and a maker (a function object, pointer at +0x140); the first question makes the list. That explains why the donors' lists were empty at launcher start, and why exactly the 22 seasonal items had none: the loot filters turn a seasonal item away before ever asking. The lookup itself (bucket = level & (size-1), chain at element +0x48, hash pointer +0xF0 / size +0xF8) matches what give_map builds; the value part holds a minimum difficulty byte and float ranges.
- drops_patch therefore now: seasonal mark off and family link at once; the level list is left to the game (it asks once the mark is off). Only if an item was asked and stayed empty, or its family's lists have been made for 60 s and its own still not, is it given its donors' levels in new memory (the old behaviour, now the fallback - less foreign memory inside a game container). A one-off run by hand doesn't wait. Checked offline against a made-up memory (scratchpad fake_test.py): both tools behave.
- tools/bonus_watch.py: until the game shows its items, the best copy per item type is taken from the save of the character played last (`saved_best`), so bonus built-ins are in the definitions BEFORE the character loads (a built-in only reaches a weapon when it is equipped; written after the camp had loaded, the equipped gear went without until the next level).
- live_objects hardening: an object that fails one full pass (unreadable, or not in the list) gets one more pass before it is forgotten; a different vtable at its address forgets it at once; the whole-list sweep runs every 60 s (shorter than the 90 s the bonus Watch holds before taking bonuses away). Checked offline against a made-up object list (scratchpad scanner_test.py): first look, new object, object seen before its constructor ran, destroyed object, reused slot, ageing of young objects, wait=True.
- Left as it is on purpose: mob_enchants.py still silences Deflect / Levitation Shot on every mob-owned copy, which includes ancient mobs that carry Deflect by design (their blueprints list it). The pool removal alone would leave those their Deflect. To decide with the user once the pool removal is seen working.
- Not done, possible: Bonehead Hammer (SkeletonHammer), BatCrossbow and the Corrupted Pumpkin artifact carry a seasonal mark too and could be made ordinary drops the same way; enchantments can be ADDED to the mob pool (MobPool.toml `add`); rarity chances per source (EItemRarityChanceCategory: Mob, Boss, MissionEnd, chests, merchants...) exist in code and were not traced - a possible lever for unique drops past A+25.
- State for the next launch (nothing of this has run in the game yet): new launcher loop + scanner, seasonal mark off + lazy lists, mob pool without Deflect / Levitation Shot, bonus built-ins seeded from the save. TEST settings still in place: Luck of the Sea on the Full Metal Armor and luck_level_3 = 30, LootQualityBoost MaxValue 100, EnchantedMobChanceMultiplier MaxValue 30.
- 2026-10-13 (user: "all deflect should be gone"): decided - the per-mob Deflect override stays for good, next to the pool removal, so ancient mobs that carry Deflect by design lose it too. Added the Tower Guard's DeflectingWithShield (vtable exe+0x3426C78; its constructor exe+0xED17F0 runs Deflecting's and all 141 vtable entries are the same functions) to the copies mob_enchants.py treats.
- 2026-10-13 wiki check (user gave browser access; minecraft.wiki): CORRECTION of names - SkeletonHammer is the Bonehead Hammer (unique Great Hammer, Spookiest Fall 2022, then Tower; identical to the Hammer of Gravity), NOT the Bone Cudgel (that is the ordinary Boneclub unique, Flames of the Nether, already a mission drop). BatCrossbow is the Shrieking Crossbow (unique of the Shadow Crossbow family, Spookiest Fall 2022, then Tower; identical to the Veiled Crossbow: Shadow Shot + Shadow Barb) - a released item, the wiki just has no page under "Bat Crossbow". Corrupted Pumpkin = unique Corrupted Beacon variant (Spooky Fall 2020, since then Gift Wrapper only).
- Both weapons added to Drops.toml (21 items now). The Corrupted Pumpkin is an artifact: not in tools/item_registry.json (gear only), so not added yet. Neither weapon has an identity of its own yet (the other 19 seasonal items got one in Builtins.toml) - proposed to the user, not applied.
- 2026-10-13 (user: an easy to view, copy-pasteable sheet of every change): tools/change_sheet.py writes CHANGES.md (Markdown tables, facts only, ~700 lines) from the mod's own files - stats via `sequel.py diff`, weapons from SequelGear's defaults, built-ins / perks / artifacts with the game's values from the launcher's last log, plus Bonus, Endless (trials, unlock table), mobs, seasonal items, merchants, texts; test-only settings in their own section. Re-run after changes.
- 2026-10-13 (user): the 10-boss gate at A+40 removed (major_levels = [25]; 'move it out' had meant take it out) - A+25..49 now ask 10, 3, 4, 5, 6, 7. Trial cycles read 3 - 5 - 7 instead of 3 - 4 - 7: new [unlock] level_bosses = {55, 64, 73, 82, 91: 5} (endless_patch.boss_counts takes per-level counts). 134 boss clears from A+25 to A+100. CHANGES.md and the shared page refreshed.
- 2026-10-13 (user: how is the number of enchantments on a mob worked out, is there a limit?): from exe+0xA5FFD0 / exe+0xA7A630 - an enchanted mob gets a random power budget (interpolated between a config's min/max by the difficulty factor, i.e. what EnchantedMobPowerMultiplier scales) and spends it in a loop on options (three kinds, table exe+0x421D570); the result is two counts, 'enchantments' and 'of which powerful', which exe+0xA7A630 clamps to 0-3 (constant 3 in code) and to the first count; every picked enchantment is made at tier 3 (same constant). So: at most 3 per mob, all tier 3, how many depends on the budget, which grows with A+ level (1.25 at A+1 -> 2.25 at A+25; our 'grow' takes it to ~5.3 at A+100, 6.1 in the Enchanted trial). The cap of 3 is a code constant - not changeable by data. Exact costs per option not traced.
- 2026-10-13 (user: keep pull-and-explode on the Bonehead Hammer, pay with stats): SkeletonHammer keeps Gravity 1 and gets Exploding 1 as a second built-in (Builtins.toml); its hit damage goes back to the game's 100 while the Hammer of Gravity stays at the mod's 120 (reach 260 on both). Known: a chosen Exploding stacks with the built-in one. Shrieking Crossbow identity still open.
- 2026-10-13 (user: 'that's ok' to the crossbow swap; reminder that built-ins rise in tier above 315 anyway): Shrieking Crossbow (BatCrossbow) Shadow Barb -> Tempo Theft 1, Shadow Shot kept, stats unchanged. Applied by the launcher (Builtins.toml). Above the cap an item's own built-ins rise to tier 3 first (one tier per 4 power from 316), so the Bonehead Hammer's Gravity and Exploding are both tier 3 at power 328.
- 2026-10-13 (user): Shrieking Crossbow's Tempo Theft built in at tier 2 (was 1), so it stands apart from the Veiled Crossbow before the gear cap; it reaches tier 3 above the cap like every built-in.
- 2026-10-13 (user: will every unique have fully maxed enchantments by A+100?): by the step rule (one tier per 4 power from 320, 12 steps at 365) 130 of 144 uniques were complete; 14 with two to four tier-1 built-ins (Pride of the Piglins, Echo of the Valley, Burst Gale Bow, Encrusted Anchor, Sturdy Shulker Armor, Bubble Burster, Imploding Crossbow, Firebolt Thrower, Veiled Crossbow, Bonehead Hammer, Resolute Tempest Knife, Green Menace, Pink Scoundrel, Call of the Void) stopped 1-5 tiers short. bonus_watch.wanted: at the final power (365) every built-in and all three bonuses are tier 3 regardless. Estimate from the registration data (levels assumed 1 where the launcher log shows none).
- 2026-10-13 (user: remove the post-roll slowdown; from the online opinions gathered - reviewers call the base speed slow, the slowdown after a roll is the named pain point and the sequel removed it): BP_PlayerCharacter's movement component (CharMoveComp) stores DodgeEndSlowSpeedFactor 0.8 and MaxWalkSpeed 700. New Player.toml + tools/player.py (called from sequel.py build): speed_after_roll = 1.0, written in place, read back. Not stored in the blueprint, so unchanged: DodgeEndSlowBrakingFactor (+0x7B8), DodgeEndSlowRotationRateFactor (+0x7B4), PostDodgeDuration - reachable per object at runtime if the roll still feels sticky. Walk speed left at 700 (+10% discussed, not applied). Built; not yet played.
- 2026-10-13 (user: difficulty should ask for skill, 'kind of like Monster Hunter' - players always have a chance to lose; 'you do more damage but you take more'): top-end growth moved from mob health to mob damage - health x5 (was x6), damage x3 (was x2.5) at A+100, both from A+38; healing received stays at 70% (no longer handed back to 100%); stun / knockback / endurance give-backs unchanged. Trials follow (Titans 1.25 x, Berserkers 1.3 x the A+100 value). Artifact damage_at_top 5.0 to match health; heal_at_top stays 2.5. To judge in play: deaths should come from a nameable mistake, not one-shots.
- 2026-10-13 (user): healing received climbs back 70% -> 100% from A+38 to A+100 after all - healing in time is part of the skill of surviving the higher mob damage. Health x5 / damage x3 stay.
- 2026-10-13 18:02 session (user in game; launcher.log): no errors or skipped passes. All 21 seasonal items carried a seasonal mark (cleared), and within the session the GAME made a level list for every one of them (8-24 levels, the same counts as their families) - it never asked for these before, so the loot filters now reach them. Mob pool: Deflecting and LevitationShot both switched (their definitions were found through the id table and had the flag on). Bonus built-ins were written from the save before the character loaded (best copy 364 lines ahead of the first live items). User: Echo works immediately. Still to see: an actual seasonal drop, no Deflect on mobs, roll without slowdown.
- 2026-10-13 (user: rolling has no slowdown now - confirmed; reroll at 5 gold - confirmed; Poison Cloud's description ends '3 second'): that is the game's own text ('ValuesFormat/duration_seconds_more_than_1' = '{0} second'); overridden to '{0} seconds' in SequelText.toml. Pak built aside if the game was running (installed at next start).
- 2026-10-13 (user, in game): Sugar Rush (Trickbow_Year1, a seasonal item) is on sale at a hub merchant - the first seasonal item ever seen outside the Tower: taking the seasonal mark off works, and merchants need nothing more. A mission drop is still to be seen.
- 2026-10-13 (user: done with the test settings): removed - luck_level_3 back to 0.75, Luck of the Sea off the Full Metal Armor, LootQualityBoost MaxValue 4.1, EnchantedMobChanceMultiplier MaxValue 4.25. Pak built aside (game running), installed at the next start. Also confirmed in play this session: no Deflect / Levitation Shot on enchanted mobs for a whole run; no seasonal unique dropped in that run (seasonal items via merchants accepted by the user as the way to get them).
- Stack-test items (tools/add_stack_tests.py, waits for the game to close, backs the save up): 9 items at power 251 whose three slots each offer the same three enchantments, nothing chosen - Sword (Critical Hit / Sharpness / Committed), Daggers (Thundering / Leeching / Rampaging), Axe (Fire Aspect / Shockwave / Swirling), Nightmare's Bite (Poison Cloud / Weakening / Exploding), Glaive (Echo / Stunning / Chains), Bow (Multishot / Bonus Shot / Infinity), Crossbow (Power / Fuse Shot / Poison Cloud), Scale Mail (Thorns / Burning / Protection), Evocation Robe (Cool Down / Electrified / Potion Barrier). Inventory was 279 of 300.
- 2026-10-13 (user: the blacksmith still takes 3 runs): the save showed a hand-in made AFTER the startup change with target = start + 3, so the three quest objects changed at startup are not the ones in use (the count IS what a starting quest reads: exe+0xB937F0, target = current + [quest+0x30]). New watcher qol_patch.Blacksmith: every DynamicProgressStatQuest (vtable exe+0x3445DE0) still at 3 is set to QoL.toml's missions as it turns up (each second). The Light Feather already handed in (start 59, target 62) set to target 60 in the save (game closed, backup character_before_blacksmith_fix_*). Stack-test items were written by the waiting tool when the game closed (inventory 287 of 300). Not yet seen in play.
- 2026-10-13 stacking results (user, in game, test items of batch 1): STACK - Critical Hit, Thundering, Fire Aspect, Shockwave, Swirling, Bonus Shot, Burning, Electrified (Power assumed as in the base game). NO EXTRA EFFECT - Poison Cloud (melee and ranged: several procs, no additional damage), Exploding (same), Echo (several procs shown at the side, only one extra hit). Consequences: the "second copy" entries PoisonedMelee! (Venom Glaive, Nightmare's Bite) and Exploding! (Cursed Axe, Battlestaff of Terror) in Bonus.toml buy nothing - replacements proposed to the user, not applied; the worry about a chosen Exploding on top of the Bonehead Hammer's built-in one is moot.
- Batch 2 of stack-test items prepared (tools/add_stack_tests.py, waits for the game to close; removes batch 1 except anything equipped): 16 items - Sharpness/Committed/Smiting, Leeching/Rampaging/Radiance, Gravity/Stunning/Chains, Freezing/Weakening/Void Strike, Enigma/Anima/Soul Siphon, Dynamo/Ambush/Artifact Synergy, Pain Cycle/Busy Bee/Guarding Strike; Multishot/Infinity/Ricochet, Piercing/Chain Reaction/Fuse Shot, Accelerate/Rapid Fire/Wild Rage, Supercharge/Overcharge/Growing, Enigma/Anima/Tempo Theft, Punch/Gravity/Void Strike; Thorns/Protection/Chilling, Cool Down/Potion Barrier/Snowball, Swiftfooted/Speed Synergy/Health Synergy.
- 2026-10-13 (user: yes): the four dead second copies swapped in Bonus.toml - Venom Glaive [Void Strike, Committed, Critical Hit, Stunning], Nightmare's Bite [Thundering, Critical Hit, Stunning, Chains], Cursed Axe [Leeching, Rampaging, Critical Hit, Committed], Battlestaff of Terror [Leeching, Committed, Critical Hit, Rampaging]. Batch 2 of the stack-test items went in when the game closed (5 of batch 1 removed, inventory 297 of 300). Launcher log: the Blacksmith watcher set quests made after startup to 1 mission.
- 2026-10-13 stacking results, batch 2 (user, in game). STACK: Sharpness, Committed, Smiting, Enigma Resonator, Soul Siphon, Anima Conduit, Protection, Infinity, Wild Rage (probably), Chain Reaction, Fuse Shot (and it explodes at once, as changed). PARTLY: Rampaging (longer in total), Dynamo (stacks build faster to the cap of 20), Multishot (chance up), Radiance (extra copies ~50%), Growing (odd: seems to count only two tier 3s, not mixed tiers), Accelerate (only a third copy adds ~12%, tops out at 100%). NO GAIN: Punch, Artifact Synergy, Tempo Theft, Void Strike on bows, Gravity, Piercing (every Xth arrow), Pain Cycle (worse: overshoots the fifth hit). All results kept in StackNotes.toml and shown in CHANGES.md / the shared page (section 1). Still untried from batch 2: Leeching, Stunning, Chains, Freezing, Void Strike (melee), Ambush, Busy Bee, Guarding Strike, Ricochet, Rapid Fire, Supercharge, Overcharge, Thorns, Chilling, Cool Down, Potion Barrier, Snowball, Swiftfooted, Speed Synergy, Health Synergy.
- 2026-10-13 more stacking results (user): STACK - Leeching, Ambush, Busy Bee (each copy brings its own cap of 3 bees), Supercharge. NO GAIN - Void Strike on melee too, Freezing (procs, slow no stronger), Rapid Fire, Overcharge. Chance-based ones (Stunning, Chains) assumed to work. Ricochet unclear. Accelerate: every copy adds its per-shot speed (limit reached sooner).
- ACCELERATE (user: "it maxes out at 100%", our stack-limit change did nothing): as suspected on day one, the blueprint asks GetSpeedLimit, a native function returning 2.0 (exe+0xA20C80), called only through its script entry exe+0xE9EDD0. The stack limits go back to the game's 25 / 20 / 16 in SequelMod.toml, and new tools/accelerate_patch.py + Accelerate.toml (speed_limit = 2.5, +150%) point the function's UFunction object (+0xC0) at a copy of the entry in new memory that returns our number - the endless_patch technique. Bytes checked by disassembly offline; launcher applies it at startup (switch `formulas`). NOT YET SEEN WORKING.
- RAPID FIRE (user unsure the 20/35/50% took): the launcher reports the per-tier function replaced on live objects; whether the effect reads it is unconfirmed - to check by the tooltip numbers or by counting shots.
- 2026-10-13 stacking, armor (user): STACK - Protection (as in the base game), Snowball, Thorns, Cool Down. NO GAIN - Chilling (same aura slow), Potion Barrier (still 9 s), Swiftfooted, Speed Synergy (several procs, same speed), Artifact Synergy (again). Untried from batch 2: Guarding Strike, Health Synergy. StackNotes.toml and the shared page updated.
- 2026-10-13 (user): Health Synergy does not stack (the earlier 'artifact synergy' in the armor list meant this one; Artifact Synergy doesn't either); Guarding Strike does not stack (same duration and reduction). Batch 2 fully reported.
- 2026-10-13 Ricochet (user: copies raise the chance; how do further bounces work, it didn't chain much): handler exe+0xAB6250 - on a hit the arrow may bounce if (its bounce count + 1) < MaxAllowedRecursionCount (BP_Ricochet, 3) and the usual trigger roll succeeds; the chance (value lambda exe+0xACE980 = tier x 0.2: 20 / 40 / 60%) is the same on every bounce, not reduced. So an arrow bounces at most twice, 60% then 36% at tier 3. MaxAllowedRecursionCount is in SequelMod.toml and could be raised (5 = up to four bounces) - offered to the user, not changed.
- 2026-10-14 batch 3 of stack-test items written (game closed): Mace (Looting / Prospector / Refreshment), Bow (Radiance Shot / Cooldown Shot / Shock Web), Scale Mail (Fire / Lightning / Poison Focus), Evocation Robe (Soul Focus / Bag of Souls / Soul Speed), Scale Mail (Reckless / Frenzied / Fire Trail), Evocation Robe (Cowardice / Rush / Final Shout); batch 2 removed except equipped items.
- 2026-10-14: the stack-test tool now recognises earlier test items by type + rarity + exactly power 251 (the user rerolls their enchantments, so the offered options can't identify them); 17 leftovers of batches 1-2 removed with batch 3, inventory 286 of 300. Two test items the user has equipped stay (Cutlass, Scale Mail). The 25 unique test items of the 2026-10-04 batch and the test artifacts are still in the inventory.
- 2026-10-14 (user: look into customising every seasonal weapon as a new build option / sidegrade, even working quite differently, covering a playstyle or enchantment that isn't used): review proposed, NOT applied - keep 16 as they are; change Frost Slayer (Freezing 3 + Guarding Strike 2: frontline tank), Sparkler (Artifact Synergy 3 + Thundering 2: artifact duelist), Haunted Bow (Burst Bowstring 3 + Roll Charge 2: roll archer), Gloopy Bow (Cooldown Shot 3 + Refreshment 2: utility bow), Hungry Horror (Thorns 3 + Gravity Pulse 2: pull mobs into the thorns). Guarding Strike, Artifact Synergy, Burst Bowstring, Roll Charge, Cooldown Shot, Refreshment and Gravity Pulse are built into no unique today.
- 2026-10-14 (user: yes to the five seasonal identities): Builtins.toml - Frost Slayer Freezing 3 + Guarding Strike 2; Sparkler Artifact Synergy 3 + Thundering 2; Haunted Bow Burst Bowstring 3 + Roll Charge 2; Gloopy Bow Cooldown Shot 3 + Refreshment 2; Hungry Horror Thorns 3 + Gravity Pulse 2. Bonus lists unchanged. Not yet played.
- Ricochet left as it is (user: no need to buff if it is decent): our own notes rate it Good ("many top bows have it built in"); two bounces at most stays.
- (user) every enchantment tried for stacking says so at the end of its description: tools/stack_text.py builds the sentences from StackNotes.toml at `sequel.py build` ("Copies of this enchantment stack." / "Copies stack only in part." / "Copies do not stack."), 55 descriptions; untried enchantments get none. The change sheet folds these into one line of section 10.
- 2026-10-14 (user: how often can duplicates even appear in the base game? if rarely, only mark the non-stackable ones, really short): in the base game an enchantment can be offered in more than one slot only if its definition carries tag 0 - twelve do (Sharpness, Smiting, Looting, Prospector, Chains, Fire Aspect, Leeching, Rampaging, Radiance, Cool Down, Thorns, Knockback; read from the definitions on 2026-10-05). In the mod duplicates come mostly from the bonus built-ins above the gear cap landing on something the player already picked. Descriptions now only carry the exceptions: 'Does not stack.' / 'Stacks only partly.' (29 descriptions); nothing where copies simply stack. Pak rebuilt.
- 2026-10-14 (user: seasonal uniques needn't have two enchantments, they should equal other uniques in power - tone down; the Bonehead Hammer idea is fine): rule = six enchantment points, i.e. one built-in at tier 3 or two at tier 2. Now: Sinister Sword Leeching 2 + Radiance 2; Frost Slayer Freezing 2 + Guarding Strike 2; Sparkler Artifact Synergy 3; Cackling Broom Swirling 2 + Gravity 2; Skull Scythe Enigma 2 + Soul Siphon 2; Spine-Chill Spear Void Strike 3 (Rushdown dropped); Haunted Bow Burst Bowstring 2 + Roll Charge 2; Gloopy Bow Cooldown Shot 2 + Refreshment 2; Phantom Bow Void Strike 2 + Supercharge 2 (Shadow Shot dropped); Webbed Bow Shock Web 2 + Gravity 2; Shivering Bow Anima Conduit 2 + Soul Siphon 2; Sugar Rush Accelerate 3 (Rapid Fire dropped - its change is unconfirmed anyway); armors all 2 + 2 (Cauldron, Cloaked Skull, Gourdian, both Horrors, Sweet Tooth, Arctic Fox). Unchanged by the user's own choice: Bonehead Hammer (Gravity 1 + Exploding 1, damage 100), Shrieking Crossbow (Shadow Shot 1 + Tempo Theft 2).
- 2026-10-14 (user: yes, switch): bonus enchantments now fill up to a fixed total - bonus_watch.bonus_slots: an item gets min(3, max(1, total - own)) bonuses, `total` = 4 ([thresholds] in Bonus.toml), `own` = its built-ins that its family's plain item (definition link +0x228, else by name) doesn't have. One of its own -> three bonuses, two -> two, three or more -> one; a plain item -> three. At 365 weapons still get one more. Checked offline (scratchpad slots_test.py).
- 2026-10-14 (user: look at all bonus enchantments; aim for the stackable ones as the additional enchantments): all 118 lists in Bonus.toml rewritten. Out everywhere: Echo (was in 24 melee lists), Gravity, Weakening, Poison Cloud, Pain Cycle, Piercing (9 ranged lists), Rapid Fire, Potion Barrier (12 armor lists), Swiftfooted, Health / Speed Synergy, Chilling. In: mostly Critical Hit, Committed, Sharpness, Shockwave, Swirling, Thundering, Leeching (melee); Bonus Shot, Infinity, Chain Reaction, Supercharge, Power (ranged); Protection, Cool Down, Thorns, Snowball, Burning, Electrified (armor). Void Strike kept on Firebrand, Stormlander, Venom Glaive and the Obsidian Claymore (the weapons built around it). Backstabber family: a second Ambush ("Backstabber!"). Every list got a spare last entry - before, a unique owning an entry of its family's list (Diamond Sword and Sharpness) ended A+100 with no more enchantments than the plain item. Previous file kept at %TEMP%/Bonus.before.toml. Armor enchantments still untried (the Focus ones, Frenzied, Bag of Souls, Acrobat ...) were left where they were. Not yet played.
- 2026-10-14 (user: test Unchanting too): Sword with Unchanting / Illager's Bane / Smiting added to the save without removing batch 3 (add_stack_tests.py --add).
- 2026-10-14 (user): Unchanting stacks. Not on any melee list yet (only the Shadow Crossbow family and Phantom Bow lists) - offered.
- 2026-10-14 (user: seasonal stats should differ to fit their enchantments; keep the card bars in step): SequelGear.toml - Sinister Sword swings 20% quicker for 20% less damage (more Radiance procs); Frost Slayer 20% slower for 20% more damage (tank); Sparkler 25% slower for 25% more damage (Artifact Synergy boosts one hit); Cackling Broom sweeps 45 / 45 / 120 degrees (was 25 / 25 / 80) for 10% less damage; Skull Scythe 15% quicker for 15% less damage (more hits, more souls); Gloopy Bow charges in 0.26 s (was 0.35) with charged shots x2.8 (was 3.125); Shrieking Crossbow fires every 0.5 s (was 0.56). Damage per second about level in each trade. Not changeable: Haunted, Phantom, Webbed, Shivering Bow and Sugar Rush - their blueprints store no stats of their own beyond projectile count (they take the family's). Pak built aside.
- BUG FIXED in tools/bars.py: the area score never changed - a generator inside the list comprehension saw only the last `k`, so new and old area were the same. With the fix 21 weapons' area bars move (the reach and swing-angle changes from the start of the project: Great Hammers 7.8 -> 13.1, swords, axes, gauntlets, tempest knives, coral blades ...).
- 2026-10-14 stacking, batch 3 (user): STACK - Illager's Bane, Refreshment (appears to), Radiance Shot, Shock Web, all four Focus enchantments, Cooldown Shot, Fire Trail, Reckless (multiplies: 623,119 -> 3,614,092, x5.8 - each tier-3 copy x2.5 in the mod, two copies x6.25). NO GAIN - Final Shout, Cowardice (measured 4985 -> 7477 = +50% at tier 3: the game's 30% plus the mod's flat 20%, so our Cowardice change works), Rush, Frenzied, Soul Speed (buffs). UNCLEAR - Bag of Souls (gauge looks the same), Looting and Prospector (seem to work). Armor bonus lists cleaned of the new non-stackers: Soul Robe and Phantom Armor lose Soul Speed, Mercenary Armor Cowardice (-> Fire Trail), Scale Mail Frenzied (-> Cool Down), Piglin Armor Final Shout (-> Fire Trail). Pak built; shared page updated.
- 2026-10-14 (user: leave Reckless as is; why Unchanting only on heavy weapons, not fast ones too?): no reason - it's a per-hit damage bonus against enchanted mobs, so it pays the same on fast and heavy weapons. New `[final_extra] melee = "Unchanting"` in Bonus.toml: the A+100 extra (power 365) of every melee weapon is Unchanting, unless the item owns it; otherwise the list's next name as before (bonus_watch.wanted; checked offline with scratchpad slots_test.py). Side effect: the A+100 extras that broke the kill lane (Shockwave on Heartstealer, Swirling on Diamond Pickaxe, Thundering on Resolute Tempest Knife and The Beginning and The End) are gone. ExplodingCrossbow list got a sixth name (Bonus Shot): the Firebolt Thrower owns the first two and had no A+100 extra. Mechanical: the stacking sentence on descriptions now reads "Copies do not stack." / "Copies stack only partly." (Soul Speed's own text says "stacking" about its boost, so the old "Does not stack." contradicted it). Change page republished (version 19). Proposed, not applied: Frost Slayer list without Shockwave (Guarding Strike needs the claymore's own kill); Moon Daggers, Soul Fists and Soul Hunter Crossbow (Enigma Resonator built in) to get Soul Siphon + Anima Conduit.
- 2026-10-14 (user: yes, all four): applied - Frost Slayer [Sharpness, Committed, Critical Hit, Stunning, Smiting]; Moon Daggers (Daggers_Unique2) and Soul Fists (Gauntlets_Unique1) [Soul Siphon, Anima Conduit, Critical Hit, Committed, + Thundering / Leeching spare]; Soul Hunter Crossbow (BurstCrossbow_Unique1) [Soul Siphon, Anima Conduit, Infinity, Power, Bonus Shot]. Melee A+100 extra stays Unchanting. Page republished.
- 2026-10-14 (user: Accelerate still stops at 100% in the GUI; descriptions changed - ok; Blacksmith 1 run - CONFIRMED; seasonal merchant rolls rare, user fine with it): launcher.log showed the Accelerate change never ran - two matches for the function object; one (index 0, a code address where the vtable should be) is a table of native functions, not an object. accelerate_patch now keeps only matches the object list has at their own index (listed()); applied to the running game: limit 2.5x. To check in play.
- 2026-10-14 (user: will the Blacksmith still work above A+26 - bring gear up to my power and so on to the bonus enchantments?): unknown yet. Wiki: the result depends on the difficulty of the missions won and the hero's power; each A+ threshold is an upgrade threshold; the range shows before the item is collected. Open risks: the quest's difficulty band (WIN_MISSIONS_APOCALYPSE_PLUS_TIER1..6) for an item above A+25 power, and a result pinned near 254. Asked the user to test with one hand-in and an A+26+ win and read the range shown; fallback (planned 2026-10-07): raise the finished item to the gear power. An item that comes back above 316 counts for bonuses like any other copy. Save now: no upgraded items yet; Blacksmith slots hold a Fishing Rod (113) and a Torment Quiver (249).
- 2026-10-14 (user: add the Blacksmith fix now, matching my power): bonus_watch.Watch.blacksmith + Bonus.toml [blacksmith] match_power = true - a collected upgrade (save: upgraded = true; type + exact power not seen before, upgrades already in the save at launcher start don't count) below the save's totalGearPower is raised to it, once, never lowered; found among the live item objects within 10 min of the save showing it. Artifacts not handled. Checked offline with a fake (241 -> 300 raised, 311 above level left). Starts with the next launcher start. Change page updated.
- 2026-10-14 (user: the Blacksmith gave a 258 item - maybe fine, doesn't want the number to look different, not a big deal): the game's own result already went past A+25 power (user at 251). Fix kept on: it only acts when the result is below the gear power, so this case is untouched. Release: tools/package.py -> dist/SequelMod-1.0.zip (Mods/SequelMod/... to unpack into the game folder: pak at the root - play.install_pak copies it into ~mods -, every module play.py imports, its data files, settings, both .bat, CHANGES.md, INSTALL.txt). Checked: unpacked into a scratch game folder, the launcher's modules import. Multiplayer never tested. Pending design (user): past 365, every 5 power one more tier of a generic damage enchantment as new lines under the others (Sharpness / Power / Protection); needs A+100 drops to climb above 365 and a check that more than 8 built-ins show and work.
- 2026-10-14 (user: build the A+100 ladder first, then multiplayer; asked why not a hidden 1000 at A+100 - answered: the first A+100 drop would jump to the top, no climb): Bonus.toml [ladder] step 5, climb [1, 3], Sharpness / Power / Protection. bonus_watch.wanted: past final, (power - final) // step tiers as new lines (3 tiers a line) under everything else; MAX_ENTRIES 8 -> 16 (our own buffer; whether the game shows and uses more than 8 built-ins is NOT yet seen). bonus_watch.climb (before gild): a new drop at final or more (not from the start-of-session saves, not merchant wares, not raised before - keys of raised items kept, so a re-created object isn't raised twice) goes to the save's gear power + 1..3 (from a hash of item + power), never lowered. Offline checks: ladder lists at 365-440; climb raised 366 -> 374 at level 372, left 380 alone, skipped wares and re-created objects. Change page (version 22) and dist zip rebuilt. Python: friends need 3.11+ (tomllib). Steam Deck: the pak works under Proton; the launcher is Windows-only (kernel32 via ctypes) and would have to run as Windows Python inside the game's Proton prefix - untested.
- 2026-10-14 (user: yes, bundle portable Python): downloaded python-3.12.10-embed-amd64.zip from python.org (user's yes; md5 fe8ef205f2e9c3ba44d0cf9954e1abd3 matches the release page) -> vendor/. package.py puts it in the zip as Mods/SequelMod/python/; both .bat files use python\python.exe when it is there, else the system's python. Checked: unpacked zip, the portable Python imports the launcher's modules. Zip now 11.4 MB, 91 files. Linux / Steam Deck: answered - possible in principle (Windows Python run through Proton in the game's own prefix, so the launcher shares the game's Wine session), not built or tested.
- 2026-10-14 install robustness: play.py finds the game as the first folder above it with Dungeons/Content/Paks (was: two up), so an unzip one level too deep (Windows Extract All adds a folder) still installs the pak; with no game folder above it says where the mod belongs. Checked with the zip unpacked into Game/SequelMod-1.0/. Deck/Linux launcher left for later (user).
- 2026-10-14 (user): 'Play Sequel Mod.bat' at the game folder's top (calls Mods\SequelMod\Play Endless Apocalypse.bat); in the zip at its root and copied into the user's own game folder; INSTALL.txt points to it.
- 2026-10-14: change page header now carries a one-line install note (from CHANGES.md's 'Install (' line; change_page __INSTALL__). Checked the page has every change of today (Unchanting at A+100, ladder + climb, Blacksmith match, Accelerate +150%, 'Copies do not stack', new soul lists, Frost Slayer, 1-mission Blacksmith). Published version 23; zip rebuilt with the same CHANGES.md.
- 2026-10-14 (user: set up the git repo): git init -b main in SequelMod with .gitignore (saves and backups, the game's memory image / disassembly / text / extracted data, save key, transcripts / wiki / images, build output, vendor, dist). First commit: 135 files. Not pushed anywhere - GitHub needs a repository the user creates (gh not installed).
- 2026-10-14: remote origin = https://github.com/1TeaL/MinecraftDungeons-SequelMod (user's repository), main pushed.
- 2026-10-15 (user: put the zip on the changes page, or make it a nice readme page): page turned into a readme (title 'Sequel Mod'): download button, what it does, install steps, good to know, then every change. Artifact pages can't host a .zip (refused at publish), so the button links to the GitHub repo's latest release (change_page.RELEASES) - works once the user pushes, makes the repo public and attaches dist/SequelMod-1.0.zip to a release. The zip no longer carries the save key: savefile.key_bytes reads it from the running game when research/save_key.bin is missing (std::string at exe+0x44F86B8, checked by decrypting a save to JSON; NOT yet seen working live - the user's own copy has the file), and bonus_watch retries reading the saves every 10 s until it works (old items, Blacksmith baseline). Version 24 published.
- 2026-10-15 (user: no way to fix the Cowardice / Frenzied descriptions? they say '{0} +20%'): both use the same per-tier value function as Bonus Shot etc. (research/value_lambda.py: Cowardice tier*0.1+1.1, class vtable 0x32B5358, value vtable 0x32C81D0; Frenzied tier*0.1+1.0, 0x32BE9A8 / 0x32C85C0). Moved the mod's bonus into that number: formula_patch KNOWN + Formulas.toml Cowardice and Frenzied [1.4, 1.5, 1.6] (+40/50/60%, the totals intended since 2026-10-05); the pak's ExtraDamageBonus / ExtraAttackSpeedBonus back to 0; SequelText overrides removed, so the cards say '{0} increased ...' again. Assumes the card's {0} reads the same function (it showed the game's 40% before) - TO CHECK in game: Cowardice III should read 60%, Frenzied III 60%. Without the launcher (Steam Deck) both are now the game's own values. Pak built (game closed), zip, page (version 25) rebuilt.
- 2026-10-15 (user: Accelerate still stops at 100%; Rapid Fire's card says 50%): Rapid Fire's card shows the Formulas value, so cards read the per-tier function (Cowardice / Frenzied should show 60%). Accelerate: GetSpeedLimit (exe+0xA20C80) has no caller but its script thunk (no vtable entry, no direct call; the blueprints BP_Accelerating / LevelNEffect import no such function - the effects are native classes), so the UFunction redirect changes nothing that runs. And the HUD number is not the speed: BP_AcceleratingUIData sets displayPreference = EStackCountDisplayPreference::AsPercentage - the icon shows how full the stacks are, so it always ends at 100%. Whether the real speed is capped at 2x is unknown; next step: read the live attack speed with an Accelerate bow at full stacks, or the user counts shots. accelerate_patch left on (harmless).
- 2026-10-15 CONFIRMED in game (user): Cowardice III card 60% and its damage works at 60%; Frenzied III card 60%; Enigma Resonator card 0-50%; Rapid Fire card 50%. The per-tier formula routine reaches the cards. Still open: Bonus Shot card (75%), Punch / Recycler feel, Accelerate's real speed at full stacks.
- 2026-10-15 CONFIRMED (user): Bonus Shot III card 75%.
- 2026-10-15 (user: then don't say Accelerate has any changes): Accelerate.toml speed_limit back to 2.0 (the launcher does nothing for it), its line gone from CHANGES / the page / README's settings table; stacking note reworded ('the stacks fill sooner'). Page and zip rebuilt.
- 2026-10-16 (user): mob speed may climb past its A+25 value - MobSpeedMultiplier [[38, 1.85], [100, 2.0]] (1.88 at A+50, 2.0 at A+99/100); stun duration and stagger resistance no longer hand back - their rows removed from [natural], so they stay at the A+25 values (30%, 10x) to A+100. Knockback and healing still climb back. Pak built (game closed), zip and page (version 27) rebuilt.
- 2026-10-17 (user: enable rolling in several slots for every tested full stacker, Reckless too - 'by stacking you sacrifice other parts of the build'): Stack.toml stackable = the 32 'full' enchantments of StackNotes.toml not already tagged by the game (melee 13, ranged 9, armor 10 incl. Reckless). Applied by the launcher at the next start (game closed now). Whether the tag alone makes the Enchantsmith / drops offer them in several slots is NOT yet seen in play. Listed in CHANGES / the page (section 1). Cross-gear enchantments (Fire Focus or Potion Barrier on a weapon): answered - untested; proposed a one-session test via a built-in.
- 2026-10-17 TEST set up (user: cheap rerolls make a bigger pool fine - first see if off-gear enchantments work): Builtins.toml test block - plain Spear (equipped) + Potion Barrier 3, Snowball 3, Burning 3; plain Scale Mail (equipped) + melee Radiance 3. Marked in change_sheet.TEST_BUILTINS so the page leaves them out. TAKE OUT after the test. Also builtins_patch.builtins accepts up to 16 entries (was 8: a launcher restart mid-session would have skipped items carrying the A+100 ladder).
- 2026-10-17 (user: never mind, too complicated - enchantments stay on their own gear): cross-gear test removed from Builtins.toml before it ran; TEST_BUILTINS empty again. Enchantment gear rules stay as the game has them.
- 2026-10-17 (user: README and release for Beta 1.1): package VERSION 1.1 + LABEL 'Beta 1.1' (zip SequelMod-1.1.zip, VERSION.txt, INSTALL.txt, page header); README: download step no longer names a version, 'Stacking builds' bullet; dist/release_notes.md for 1.1. GitHub check: the v1.0-beta release ('Sequel Mod v1.0-beta') has NO file attached - told the user. Tag scheme v1.0-beta -> v1.1-beta kept (one tag per release is the norm).
- 2026-10-18 (user: seasonal bows should handle differently from their siblings; Haunted keeps its 2 arrows): the four bows store only their arrow count and inherit the rest from their base bow, so the builder couldn't change them. Now: sequel.INHERITED + inherited_stats - the scan lists a ranged weapon's inherited stats (fire rate, charge time, charged damage, damage factor, bundle size) as settings with the inherited game value as default (140 new lines in SequelGear.toml, nothing else changed); a changed one is written into the weapon's own file at build time (uasset.add_properties into_struct = AttackDefintion; bundle size at the top), checked by reading the built file back. Set: Sugar Rush 0.483 s between shots, damage factor 0.99 (TrickBow 0.42 / 0.9: x1.15 / x1.1); Phantom Bow charge 0.455 s, factor 3.25, 24 arrows (Power Bow 0.35 / 2.5 / 30: x1.3 / x1.3); Webbed Bow charge 0.28 s, charged x2.656, 75 arrows (Snow Bow 0.35 / 3.125 / 60); Shivering Bow 0.302 s, charge 0.28 s, charged x2.48 (Soul Bow 0.378 / 0.35 / 3.125, x0.8 - 2.48 not 2.5: a value equal to the default means 'inherit'). bars.py now also matches 'Bp_' blueprints (Shivering Bow). NOT yet seen in game.
- 2026-10-18 (user: expose as many settings as possible; a setting for every mob enchantment, for completeness): MobPool.toml is now a [pool] table - every enchantment the wiki lists as rollable by mobs (any mob / ranged mobs) with true, Deflect and Levitation Shot false, and the ancient-only ones (Committed, Cowardice, Echo, Fuse Shot, Huge, Leeching, Rampaging, Sharpness, Shockwave, Swirling, Thundering) false = as the game has them; true adds one (untested). mobpool_patch reads [pool] (old remove / add still work). Names checked against enchant_ids.json; the real pool to compare with --show next time the game runs.
- 2026-10-18 (user: yes, restore the three): their hits were never weaker - their swings were slower; swing times set to the base weapon's: Master's Katana 2nd slash 0.6 -> 0.48; Battlestaff of Terror hits 1, 3-7, 9 to the Battlestaff's (0.35 / 0.5 / 0.65 / 0.45 / 0.45 / 0.25 / 0.35); The Starless Night 0.77 / 1.32 -> 0.7 / 1.2 (Obsidian Claymore). TEST (take out, NOT in any zip): the user's equipped Trickbow_Unique1 given 0.1 s between shots, damage factor 5.0, 300 arrows - to see in play that stats written into a unique's own file (the inherited-stats change) work. Pak built (game closed); zip NOT rebuilt while the test is in.
- 2026-10-18 (user: everything since the published 1.1 is 1.2): VERSION 1.2. GitHub had v1.1-beta with the first 1.1 zip (8,029,154 bytes, 2026-10-17 07:01) and v1.0-beta now with its zip. 1.2 = seasonal bow stats, the three uniques' swing speeds, the MobPool on/off table, inherited bow stats as settings. dist/SequelMod-1.2.zip built with the Green Menace test taken out (checked: no TEST line in the zip's SequelGear.toml, no Trickbow_Unique1 change in the pak); the test is put back locally afterwards, not committed.
- 2026-10-18 (user): 1.2 is not released yet - it stays open for more per-weapon stat changes; the 1.2 zip gets rebuilt (without the Green Menace test) when it's done. User testing now.
- 2026-10-18 TEST RESULT (user, in game): Green Menace with stats written into its own file - fire rate clearly higher, 400 arrows (300 + the usual third more, as 60 -> 80 before), card bars maxed. So values inserted into a unique's AttackDefintion and at the top level both work: the seasonal bow changes are live. Test removed; pak rebuilt (staged while the game runs).
- 2026-10-18 (user: yes to the bow roles; keep the three melee speed-ups - uniques should just be better; README should name the biggest enchantment changes, and highlight them): Bubble Bow 0.34 + 0.28 s x2.7 (quicker, lighter), Snow Bow 0.42 + 0.42 s x3.6 (slower, heavier), Soul Bow 0.32 + 0.30 s x2.7 (a bit quicker), Twisting Vine Bow 0.45 + 0.50 s x4.5 (slow, very heavy; Weeping Vine follows), Bow unchanged. Uniques that store their own values (Bubble Burster, Gloopy, Winter's Touch, Shivering) unaffected; Nocturnal Bow and Bow of Lost Souls (strong tier, inherit) locked at their old 0.378 / 0.351 / 3.125 (0.351: equal-to-default means inherit); Webbed Bow now inherits the Snow Bow's 0.42 s. Change page: rows whose value doubles, halves or becomes certain are highlighted (change_page.big_change, 83 rows) with a legend. README: a 'biggest enchantment changes' table. Second ranged tier list saved in Gear_Opinions.md.
- 2026-10-19 (user: any way to raise storage?): no - GetMaxInventoryCount's script entry (exe+0xF281D0) writes the constant 300 (0x12C) itself, so the inventory size is a number in the code, like Accelerate's limit. The camp storage chest (Season 2) is the game's own extra room. Player sentiment research saved in research/player_sentiment.md (web search; Reddit not used).
- 2026-10-19 (user: yes to the melee pass; glaives left alone - the stat guide rates them A): Rapier family (Rapier, Bee Stinger, Freezing Foil) damage x1.25; Tempest Knife family x1.15, then Resolute Tempest Knife x1.15 time / x1.3 damage (heavier, Committed), Chill Gale Knife x0.85 / x0.95 (quicker, Freezing); Swift Striker x0.85 / x0.95; Broadsword x0.8 / x0.85 (sword-like); Great Axeblade x1.2 / x1.3, reach x1.1 (Dynamo); Diamond Sword x1.15 / x1.3 (heavier); Hawkbrand x0.85 / x0.95 (quicker, crit); Eternal Knife x0.85 / x0.85 (more soul hits); Flail reach x1.2. Top/strong tier untouched. README 'Building it yourself': the balance is the author's own take, every number can be changed.
- 2026-10-19 (user: glaives are weak, so they get a boost - the rule is to buff everything weak as far as needed to match the S tier): Glaive, Grave Bane, Venom Glaive damage x1.4 and their first two thrusts 25 -> 60 degrees; Cackling Broom damage x1.5 (keeps its 45/45/120 cones). Glaive damage per second 124 -> ~174 against the S-tier families' ~190-205 (Mace, Katana, Battlestaff), with longer reach. Standing rule updated in memory.
- 2026-10-19 (user: go by the stat guide always; Bee Stinger is busted - 'damage isn't everything'): reverted today's changes to the stat guide's S/SS weapons - Rapier, Freezing Foil (S) and Bee Stinger (SS) damage, Swift Striker (S) swing time and damage, Flail (S) reach - back to the game's values. Kept: Broadsword, Great Axeblade, Resolute Tempest Knife, Glaives (A), Chill Gale, Hawkbrand, Eternal Knife (B), Diamond Sword (Sword C). Memory: melee tiers by ShinkuNy's stat guide first. Older changes on stat-guide S/SS weapons, noted for the user: Master's Katana, The Starless Night, Battlestaff of Terror speed-ups (user chose to keep), Whispering and Swift Striker Echo III (user asked), Growing Staff Committed I -> III, The Beginning and the End Void Strike III + Leeching III, Spine-Chill Spear rework (seasonal).
- 2026-10-19 (user: keep Growing Staff and The Beginning and the End weak - they gain it past 316): their Builtins.toml entries removed (game: Committed I; Void Strike I + Leeching I). The change page's built-in table comes from the last launcher log, so it still lists them until the next launch.
- 2026-10-19 (user: 'the core of this mod is that part of the fun of build crafting is finding crazy OP builds' - taken as yes to the six): Frost Scythe x1.15 swing time / x1.3 damage; Jailor's Scythe 80 degree swings, x0.9 damage; Hammer of Gravity reach x1.15; Axe, Soul Knife and Bonehead Hammer damage x1.15. Design principle saved in memory (never nerf strong combos; lift weak things) and added to the README's 'Why it was made'.
- 2026-10-19 (user: rebundle what we have as 1.0, the starting point, instead of 1.1 / 1.2): VERSION 1.0, label 'v1.0' (tag v1.0 suggested: v1.0-beta is taken by the old release). dist/SequelMod-1.0.zip rebuilt with Slayer at its planned 0.6 s (no test values); release notes rewritten as a first release. The older v1.0-beta / v1.1-beta releases on GitHub are for the user to delete or keep. Slayer test (0.15 s) put back locally only.
- 2026-10-19 TEST RESULT (user): Slayer Crossbow with its own fire rate (0.15 s) fired that fast - the added fire-rate setting works, so the Heavy / Burst / Exploding Crossbows' unstored rate really is the 1 s default. Slayer set to its planned 0.6 s (as in the 1.0 zip); test removed.
- 2026-10-19 (user: Unstable Robes - can we raise its explosion or give its rolls i-frames?): both. Its explosion is its built-in Void Blast, whose damage the robe's blueprint set to 40 (code default 150): BP_VoidBlast.blastDamage 40 -> 160, and Void Blast I -> III (Builtins.toml). Perks.toml adds DodgeInvulnerability (invulnerable while rolling, as Shadow Walker / Glow Squid) - perks are stored per item, so it reaches new drops; whether i-frames apply to a teleport roll is to be seen in play.
- 2026-10-19 (user: sure): the user's own Unstable Robes (storage chest, 244) given DodgeInvulnerability in the save (game closed; backup character_before_unstable_robes_perk_*).
- 2026-10-19 (user: sure): Cave Crawler and Sweet Tooth (stat guide BL) + 35% damage reduction, Souldancer Robe (A) + 35% damage reduction (Perks.toml: new drops); Ghost Kindler (C) Fire Trail III, Opulent Armor (B) Lucky Explorer III (Builtins.toml). Void Quiver: its value is the Void Touched area mark (up to 15 mobs in 4 blocks), not the 50-damage arrow - proposed a shorter cooldown and a 6-block splash instead of 2x arrow damage.
- 2026-10-19 (user: sounds good): Void Quiver - cooldown 25 -> 15 s (Artifacts.toml) and its Void Touched splash 4 -> 6 blocks (BP_VoidArrow SearchRadius 400 -> 600, both actions; BP_VoidArrow added to sequel.EXTRA_ASSETS, scan added only that section). The user's owned Souldancer Robes and Cave Crawlers given SuperbDamageAbsorption in the save (game closed, backup character_before_dr_perks_*).
- 2026-10-24 (user: easy to change the bonus enchantments? a legend of the names?): Bonus.toml lists are plain edits; added NAMES.md (tools/names_legend.py) - every enchantment's internal name, in-game name, the gear it rolls on and whether copies add up, plus every item id with its in-game name. In the zip and the README's settings table.
- 2026-10-26 (user: seasonal items should feel like brand-new uniques - compared with the whole roster, what's missing): Skull Scythe Anima Conduit II + Soul Siphon II (the only melee with Anima Conduit); Spine-Chill Spear Ambush II + Void Strike II (stealth spear); Sugar Rush Overcharge II + Accelerate II (the only Overcharge bow); Sinister Sword Unchanting II + Leeching II; Cloaked Skull Electrified II + Lightning Focus II with perks ghost roll / +30% ranged / 30% negate; Sweet Tooth perks potions heal allies / -40% potion cooldown / healing aura / 35% DR; Arctic Fox Bow's Boon II + Beast Surge II with perks +30% ranged / bigger bundles / 35% DR. The three SS copies (Cauldron, Spooky Gourdian, Horrors) keep their perks. perks_patch: Perks.toml 'set' replaces an armor's whole perk list (new list in fresh memory when the game's has no room). Bonus lists changed so seasonal items don't end up like their originals at A+100: SoulScythe family drops Anima Conduit for Enigma, Skull Scythe [Swirling, Sharpness, Committed, Critical Hit, Thundering], Sugar Rush [Power, Supercharge, Bonus Shot, Infinity, Fuse Shot], Arctic Fox [Roll Charge, Recycler, Burst Bowstring, Protection]; each now shares at most 1-2 enchantments (mostly the universal Unchanting) with its originals. User owns none of the three armors. Not yet seen in game.
- 2026-10-26 (user: sure - each armor should cover its own niche): perk lists replaced (Perks.toml set) - Black Wolf: pet bat, bees, weapon aura, 35% DR (the summoner; Fox beat it); Cave Crawler: +50% artifact damage, -40% artifact cooldown, pet bat, 35% DR (weapon aura dropped, the bat kept for the cave theme); Frost Bite: +30% ranged, bigger bundles, 30% negate (+50% souls dropped - base game had souls + ranged); Curious Armor: teleport when hit, 30% negate, faster rolls, -40% artifact cooldown (the blink armor; its own Guard's Armor beat it), bonus list Acrobat / Multi-Roll / Swiftfooted / Protection. Living Vines: Poison Focus II + Acrobat II (the poison armor; video list 'Strong niche', not in the stat guide). Save: 16 owned armors (Black Wolf x10, Frost Bite x4, Cave Crawler x2) given their new perk lists (game closed, backup character_before_armor_identities_*). Mystery Armor (stat guide SS) untouched: random perks per item, plus the 'all' extra perks past the cap.
- 2026-10-27 (user: the default armor set shouldn't have Thorns - Potion Barrier or similar; a doubled pick is fine): armor bonus lists - Thorns -> Potion Barrier in the 11 non-tank lists (Dark, Snow, Shulker, Scale Mail, End Robes, Piglin, Nature, Climbing Gear, Bard's Garb, Sweet Tooth, Spooky Gourdian); kept on the tanks (Plate, Reinforced Mail, Champion's, Turtle, Mercenary, Cauldron). Default (Mystery Armor): Protection, Cool Down, Potion Barrier, Health Synergy spare.
- 2026-10-27 (user: start in Apocalypse with a starter kit; uniques grow only once in the A+ levels, same end; ancient-mob enchantments for normal mobs, varied difficulty rather than numbers): tools/start_kit.py + QoL.toml [start] (apocalypse = true, kit_power 70, kit Sword / Bow / Scale Mail / Fireworks Arrow / Iron Hide Amulet / Death Cap Mushroom) - a character without Apocalypse gets it unlocked (save: difficulties.unlocked/selected = Difficulty_3) and, if its gear power is below 70, the kit (fresh enchantment options from the gear pools, Scale Mail with its own perks); run by the launcher before the game starts and after it closes (saves backed up first); tested on a scratch copy. 'Apocalypse I at power 1' isn't possible: per-difficulty power is in code (Apocalypse VII ~105, I ~70). Bonus.toml early = [110, 215]: own built-ins rise a tier at about A+1 and A+20; bonus_watch.wanted keeps bonuses to the past-cap steps (a plain item gets nothing early; checked offline); A+100 unchanged. Gilded: early_from 110 / early_chance 8% up to 257, 20% after. A+1-25 rewards: XP x1 -> x2 by A+25 (Endless XP 5 by A+99 as a number now), loot quality 4.1 -> 6 at A+25. MobPool: Echo, Fuse Shot, Leeching, Rampaging, Shockwave, Swirling, Thundering on for all enchanted mobs (Committed, Cowardice, Huge, Sharpness stay off: plain numbers). None seen in play yet.
- 2026-10-27 (user: pure-number enchantments on mobs are fine - Double Damage exists already; what's not wanted is plain extra health and damage on every mob early): Committed, Cowardice, Huge, Sharpness also on in MobPool.toml - all 11 ancient-only enchantments can now roll on enchanted mobs.
- 2026-10-27 (user: could only Adventure be required before Apocalypse?): QoL.toml [start] start = 'apocalypse' | 'adventure' | 'off', kit_power per difficulty (apocalypse 70; adventure 30 is an estimate). Early power ranges per difficulty: in code, not changed (would need research like the A+ count redirect).
- 2026-10-27 (user: yes, starting XP): start_kit gives a character skipping ahead a starting level (QoL.toml start_level: apocalypse 30, adventure 15) by raising its saved xp to 100 x (L-1) x (3L-1) (Minecraft Wiki, Dungeons:Experience; the user's 12.5M xp = level ~205 fits); one enchantment point per level, so the kit can be enchanted. Never lowers xp. Tested on a scratch copy (xp 258,100 = level 30).
- 2026-10-27 (user: fix the two weaker seasonals, as long as they're similar to the other uniques): Webbed Bow own fire rate 0.378 s and charged x2.8 (it had inherited the Snow Bow's new 0.42 s: -12% -> -1%); Spine-Chill Spear damage 110/110/160 -> 121/121/176 (-10% -> level with the Spear); Phantom Bow damage factor 3.25 -> 3.0 (+14% -> +6% over Elite Power Bow / Sabrewing). The other seasonals were already within a few percent of their family's uniques.
- 2026-10-27 (user: a single config.ini-like file so players know what can be changed): Settings.toml - the player settings in one file (switches, start difficulty/level/kit, Blacksmith, gilded chances, reroll and Piglin prices, Deflect/Levitation Shot on mobs, staged A+ unlocks). tools/settings.py lays its values over the detailed files; every launcher tool reads its file through settings.load(), so a value in Settings.toml wins and a line left out falls back to the detailed file. Launcher-only, no rebuild. Unknown keys are printed at launch and ignored; cap is left out on purpose (changes game code). Values match the detailed files, so nothing changes in play.
- 2026-10-27 (user: make starting at Apocalypse or Adventure off by default): start = "off" in Settings.toml and QoL.toml; players turn it on in Settings.toml section START. README and CHANGES.md say so.
- 2026-10-27 (user: one central launcher settings file and one builder settings file, other files cleaned up): Settings.toml (launcher) and Build.toml (pak: mob health/damage/speed/knockback/count/revives, healing received, XP, loot, finale rewards, movement) in the main folder; the detailed files moved to settings/launcher/ and settings/build/ (git mv). Each setting lives in one place: values in a central file were taken out of the detailed file, with a note in their place. QoL.toml and Player.toml removed (all their settings are central); Endless.toml [unlock] moved to settings/launcher/Unlock.toml (it's read by the launcher); the unused [climb] profile and the profile switch removed. Build.toml leaves out [power] cap_level / top_power on purpose: they must stay in step with Bonus.toml and ArtifactScaling.toml. Checked: every tool reads the same values as before, the pak is byte-identical (331/331 files), NAMES.md identical, CHANGES.md the same rows in a new order. The zip ships Settings.toml, settings/launcher/ and the two build files the launcher reads (Endless.toml gold, SequelGear.toml bundles), not Build.toml. Found in passing: the zip lacked research/armor_props_raw.json, which start_kit needs at import (the launcher would have stopped at start) - added.
- 2026-10-28 (user test: new character, no Apocalypse): Settings.toml still had start = "off" (set to "apocalypse" for the test - set back to "off" before packaging). Also fixed: settings.py read the central files once per launcher run, so a change made mid-session was missed even by the start-kit pass after the game closes; it now re-reads them when their file time changes.
- 2026-10-28 (user: 'Start in Apocalypse NOT applied: NoneType has no attribute get'): empty character slots (never played) have difficulties = null; start_kit now skips them (they're handled once played) instead of stopping at the first one. Dry run on copies of the saves: the new character (A659A7D2) gets Apocalypse, level 30, the kit. Two older level-40 characters below Apocalypse (A8E58639 Adventure, D455EC08) would be moved too - asked the user.
- 2026-10-28 (user: only new characters): start_kit changes only characters still below the starting level (below level 10 if the starting level is 1). Dry run on copies: only the new character A659A7D2 changes; the two level-40 characters are left alone.
- 2026-10-28: start set back to "off" after the user's test (worked: level 30, kit at power 70-71); zip rebuilt (dist/SequelMod-1.0.zip, new settings layout, armor_props_raw.json included). Not uploaded.
- 2026-10-28 (user): starting level apocalypse 60, adventure 30 (was 30 / 15). 'New character' = below that level. Zip rebuilt.
- 2026-10-29 (user: keep Head Start on): start = "apocalypse" by default again (README, CHANGES say on by default and how to turn it off). Zip rebuilt.

- 2026-10-30 Transmog (user): players should choose looks themselves; prototype later, NOT part of the 1.0 zip. Found: each item has a look file (BP_<Item>: model + material, e.g. BP_Axe_Unique1 -> SM_Axe_Unique1) separate from its gameplay file (BP_<Item>Instance, which the pak edits), so looks can swap per item type without touching stats. Plan: (1) Settings.toml [looks] -> launcher makes a small second pak at start (restart, same kind only, icon stays the real item's); (2) research a live swap in memory (model pointer of the look file) for a floating menu window over the game. Per single item is impossible without game code (the save has no look field).
- 2026-10-30 Transmog prototype: tools/looks.py writes the gameplay file (BP_<Item>Instance) with GearActor pointing at another item's look file (BP_<Look>_C, new import) into a second pak, ~mods/SequelLooks_P.pak; `--off` removes it. Same kind only; refuses items whose file the mod's pak already changes (load order between the two paks untested). First test built: ScaleMail=WolfArmor. NOT tested in game yet.
- 2026-10-30 Transmog test RESULT (user, in game): ScaleMail=WolfArmor works - Scale Mail looks like Wolf Armor (test character is level 30, made before the level-60 change). The GearActor swap in a second pak is a working data-only route. Next: weapons test, then player choice (Settings.toml [looks], applied at start).
- 2026-10-30 Transmog weapon test built: Axe=Axe_Unique1 (+ ScaleMail=WolfArmor). looks.py now starts from the mod's build/ copy when the pak changes that file (stats kept: Axe 98/98/150 carried over), and the pak is SequelLooks_2_P.pak (Unreal ranks <name>_<n>_P above <name>_P, so it should win over SequelMod_P.pak - to confirm in game). Every gameplay file sets its own GearActor, so a swap never leaks to the item's uniques. Game must be closed before rebuilding the looks pak; it's stale after a mod rebuild (the launcher version will remake it at each start).
- 2026-10-30 Transmog weapon test RESULT (user): Axe looks like the Firebrand and attacks like an Axe. The look swapped, so the game loaded SequelLooks_2_P.pak's BP_AxeInstance over SequelMod_P.pak's (the numbered name wins) - and that file carries the mod's stats (98/98/150, read back), so mod stats + new look work together. Cross-type melee looks allowed (swings stay the item's own; animations are not swapped - hits must match what's seen).
- 2026-10-30 RULE CHANGE (user): "we can break the rule as long as the game doesn't crash". UE4SS mission test set up: dwmapi.dll.disabled -> dwmapi.dll (Dungeons/Binaries/Win64), our SequelProbe Lua mod off (enabled.txt -> enabled.txt.off), stock UE4SS mods as they were (mods.txt), old log kept as UE4SS.log.2026-10-04. Undo: rename dwmapi.dll back to dwmapi.dll.disabled. Transmog design (user): hover an item, press T, a menu with item pictures; offer only what the character has earned - the save's itemsFound list (every item type the character ever found; 199 on the lv200 character).
- 2026-10-30 (user, before the test ran): no UE4SS - "keep it to as minimal dependencies as required": the pak, the launcher, or a separate program for transmog. UE4SS switched off again (dwmapi.dll.disabled, SequelProbe as before); never tested in a mission. Test looks pak removed (looks.py --off). Transmog to go through the launcher/a separate program: hover + T, a picture menu of the character's itemsFound, applied by data writes in memory (to research).
- 2026-10-30 UE4SS research: RE-UE4SS issue #1211 (Mar 2026, "Minecraft Dungeons crash at launch (Locating KismetSystemLibrary:Conv_NameToString...)") - the startup crash is MCD's customised engine object layout (UObjectBase/UField), not (only) the packed exe; fixed by the maintainer with MemberVariableLayout_MinecraftDungeons.ini next to UE4SS.dll (attached zip in the issue; DebugBuild must stay 0). So stock UE4SS may load normally at startup (dwmapi.dll), no late injection. Our one-byte UE4SS.dll patch + inject_ue4ss.py was probably a workaround for the same thing. Still untested: missions with UE4SS hooks (the .text re-check theory). Also found: MCD1 has a pak-only Blueprint Loader (Dokucraft, CurseForge, 2021: /Game/BPLoader/Menu|Lobby|Ingame levels), used by Too Many Outfits (custom menus), Invisible Armor, PVP Mod. UE 4.22 at G:\NVME2 Games\UE_4.22, VS 2017/2019/2022 installed, UHTHeaderDump (2339 Dungeons headers) for stub classes.
- 2026-10-30 UE4SS clean test set up (user: "as long as we can get a working ue4ss method then yes do everything"; prefers UE4SS: auto-loads via the proxy dll, no launcher): stock UE4SS.dll v3.0.1 back in place (from UE4SS.dll.orig; our one-byte patched copy kept as UE4SS.dll.onebyte), the issue #1211 fix files MemberVariableLayout.ini + VTableLayout.ini (UObjectBase has an extra StatID at 0x28, size 0x30) next to UE4SS.dll, dwmapi.dll enabled (loads at game start), SequelProbe off, old log kept as UE4SS.log.2026-10-04. Test: does the game start, then missions. Undo: dwmapi.dll -> dwmapi.dll.disabled. Git commit/branch of today's work was blocked by the permission check - waiting for the user.
- 2026-10-30 UE4SS at-startup tests (Claude launched the game via Steam, read UE4SS.log / WER / UE4 crash folders):
  1. stock UE4SS.dll + issue-1211 layout files: crash in UE4SS.dll+0xC1F2B2 within 2 s, before any log - the exact spot our one-byte patch skips (UE4SS.dll file offset 0xC1E699, js -> jmp, RVA 0xC1F299: an import-thunk ordinal check; the packed exe's import data trips it). So the one-byte patch is needed.
  2. one-byte UE4SS + layout files: loads at start, waits ~59 scans for the exe to unpack, scans OK, crash at "Locating KismetStringLibrary:Conv_NameToString" (the #1211 crash).
  3. + Stats = true: gets one step further, crash at "Locating KismetStringLibrary CDO". The layout files are WRONG for the Steam exe: they put UFunction::Func at 0xC8, the game has 0xC0 (endless_patch, proven in game) = stock 4.22 shipping. The #1211 reporter compiled the game themselves (stats build). Layout files kept aside in ue4ss/layout_issue1211/.
  4. one-byte UE4SS, default layout, at start: UE4SS fully starts (all mods, "Event loop start"), then the GAME crashes ~10 s later at exe+0xD930FC (calls a getter returning [obj+0xCA8] = null, then a virtual on it).
  5. same with every optional hook off and all stock mods off (only the core FName/StaticConstructObject hooks): same crash at exe+0xD930FC. => UE4SS's hooks installed at startup trip the exe's protection ("null engine objects" sabotage, as 2026-10-04). Late injection after the menu (inject_ue4ss.py, 2026-10-04) worked in menus; missions with UE4SS never tested.
  Restored: dwmapi.dll.disabled, one-byte UE4SS.dll, settings/mods.txt as before, SequelProbe on. Next: late-load + mission test (needs the user to play); if missions hold, our own small dwmapi.dll that loads UE4SS late (automatic, no launcher); if not, UE4SS is out for the Steam exe -> Blueprint Loader (pak) route.
  Note: a CrashReportClient.exe left open makes Steam think the game still runs (launch silently does nothing).
- 2026-10-30 UE4SS late-load mission test (user): UE4SS injected at the main menu (inject_ue4ss.py, one-byte DLL, stock mods, SequelProbe off), ran fine in the menu; loading Creeper Woods crashed at exe+0xB9CFFB - the SAME spot as the 2026-10-04 mission crashes caused by our code patches (character update with no local player controller). Confirms: any change to the game's code, including UE4SS's hooks, makes the exe's protection sabotage the next mission load. UE4SS is OUT for the Steam game (at start: crash ~10 s in; late: crash on mission load). Not trying to defeat the protection. In-game UI must come from blueprints in a pak (Blueprint Loader route) or windows outside the game (launcher). UE4SS left as before (dwmapi.dll.disabled, SequelProbe on); inject_ue4ss.py stays a menu-only research tool.
- 2026-10-30 Route 1 (user): blueprints in a pak. Downloaded Dokucraft's Blueprint Loader (CurseForge file 3385182, "Blueprint Loader.zip", 10.3 KB, game 1.9.3.0, Jul 2021; by CCCode; no re-uploading allowed - credit, don't redistribute). Inside: BP_Tent (replaces the game's tent; the Menu.umap tent on Tick creates UMG_BlueprintLoader once on the main menu) + UMG_BlueprintLoader (widget: on game-mode change Menu/Lobby/Ingame -> AssetRegistry GetAssetsByPath(/Game/BPLoader/<mode>) -> LoadLevelInstance each; shows "Blueprint Loader v1.0 by CCCode" on the main menu). Its tent is the 2021 one: today's BP_Tent has NavModifier + visibility culling (PlayerEntered/LeftVisibleRange, SetOnOff) that the old copy lacks, and it replaces every tent (missions too). Later: our own hook on the current tent. Installed as ~mods/Blueprint-Loader_P.pak for a first check (menu text visible?).
- 2026-10-30 Blueprint Loader test (user): the main menu shows "Blueprint Loader v1.0 by CCCode" - the tent hook works in today's game. Blueprint route open.
- 2026-10-30 Blueprint authoring setup: our own copy of the mod kit's UE 4.22 project in SequelMod/unreal (MIT, DokucraftSaga), PythonScriptPlugin + EditorScriptingUtilities enabled. Headless editor runs work: UE4Editor-Cmd.exe Dungeons.uproject -run=pythonscript -script=... (engine 4.22.3-7053642), using the mod kit's 2021 UE4Editor-Dungeons.dll. 4.22's Python can create Blueprint / WidgetBlueprint assets and levels (BlueprintFactory, WidgetBlueprintFactory, EditorLevelLibrary) but has NO way to add graph nodes. Plan: a small editor-only C++ module exposing FEdGraphUtilities::ImportNodesFromText (graphs written as copy-paste text) + widget-tree helpers + compile to Python. Needs the VS 2019 compiler (v142): only VS 2022 (MSVC 14.44) is installed; 4.22's build tool looks for VS 2017/2019.
- 2026-10-30 Blueprint pipeline works end to end (headless, no hand work): VS 2019 Build Tools installed (user OK; MSVC 14.29 + SDK 10.0.19041; UBT actually picked VS 2022's 14.44 as "VS2019" and built fine). Editor-only C++ module unreal/Source/SequelEditor (USequelEditorLib, called from Python as unreal.SequelEditorLib): AddWidget, AddEvent, AddCall, AddNode, AddVariableNode, AddVariable, Link, SetPin, Pins, ImportNodes/ExportNodes (copy-paste text), ClearGraph, MakeLevel (EditorLevelLibrary crashes headless: needs the editor's world), Compile. unreal/Scripts/build_hello.py builds WBP_SequelHello (text "Sequel Mod"), BP_SequelHello (BeginPlay -> Create Widget -> Add to Viewport) and /Game/BPLoader/Lobby/SequelHello.umap; cook: UE4Editor-Cmd -run=cook -targetplatform=WindowsNoEditor -> unreal/Saved/Cooked; packed our files with u4pak into ~mods/SequelBlueprints_P.pak (14 KB). Awaiting the in-game check (text top left in camp).
- 2026-10-30 User: "Sequel Mod" text shows in camp - the blueprint route works (blueprints built by script, cooked, loaded by the Blueprint Loader). Next: proof #2, live look swap. The game's classes (UE4SS header dump) give blueprints all transmog needs: GearItemInstance.GearActor (look file, per item, BlueprintReadWrite), EquipmentComponent.GetSlotsOfType, ItemSlot.GetItem, EquipmentDisplayComponent.OnGearItemSlotUpdated (rebuilds a slot's look; protected in the game, callable from bytecode), ItemStashComponent.HasPreviouslyFoundItem (the save's itemsFound = "earned"), ItemFunctionLibrary.GetIconTextureForItemType / GetNameForItemType / GetSlotTypeForItemType (icons and names for the menu - no extraction needed). Stand-ins for these in unreal/Source/Dungeons/GameClasses.h (names only matter; never shipped). Editor lib gained AddMemberNode, SetNodeProperty, SetVariableDefault, softclass:/softobject: variables. 4.22 notes: no LoadClassAsset_Blocking (load the look's Default__ object with LoadAsset_Blocking, then GetObjectClass); const functions like GetComponentByClass become pure nodes; array Get is K2Node_GetArrayItem (pins Array, Dimension 1, Output). tools/blueprints.py <script> = run script + cook + pack ~mods/SequelBlueprints_P.pak. Proof #2 = unreal/Scripts/build_transmog_test.py: camp, press T -> equipped melee weapon gets Firebrand's look; status text top left reports success or which step failed. Replaces the hello proof.
- 2026-10-30 Proof #2 works (user): in camp, T -> equipped Axe shows Firebrand's look live, no crash. Live look swap from a blueprint is proven. User asked whether the menu "Blueprint Loader" text and the camp status text must stay: no - the camp text is test-only (final: nothing on screen until T opens the menu), and the menu text comes from CCCode's loader pak, which we can't ship anyway (no re-uploading); plan is our own hook on today's tent, which shows nothing.
- 2026-10-30 Transmog step 1 (remember + reapply) built, awaiting test: unreal/Scripts/build_transmog.py (+ shared seqbp.py; test and hello scripts removed). Choice stored per item TYPE in the engine's own save file SequelLooks.sav (BP_SequelLooksSave: Items names + Looks soft paths) - never the game's save. BP_SequelTransmog sits in BPLoader/Lobby and BPLoader/Ingame; a 0.2 s timer runs ApplySlot for melee/ranged/armor: first sight of an equipped item records its own look (Applied/Originals arrays) and applies the saved choice. Refresh(Item, Slot) sets chosen or own look and rebuilds the slot. T (test until the menu) toggles Firebrand for the equipped melee type and saves. Editor lib: AddCustomEvent, AddSelfCall, AddArrayCall, enum: pin types. 4.22: DoesSaveGameExist has exec pins.
- 2026-10-30 Step 1 per-type version worked (user: Firebrand survives restart). User then changed the design: transmog is a LAYER per slot - pick one look for melee, one for ranged, one for armor; while chosen, every item in that slot wears it; off = items wear their own. Rebuilt: save holds Melee/Ranged/Armor soft look paths (same SequelLooks.sav; old per-type fields ignored). Actor: LoadLooks -> MeleeLook/RangedLook/ArmorLook classes; ApplySlot(Type, Look) every 0.2 s swaps the equipped item to Look (or back to its recorded own look) only when it differs, then rebuilds the slot. Test keys T melee Firebrand, Y bow Bone Bow (Bow_Unique1), B armor Wolf Armor. Note: T is the game's Chat key and Ctrl+U toggles UI; free keys include B, O, P, Y - pick the menu key with the user.
- 2026-10-30 Per-slot layers worked (user). User: one key (Y for now, changeable to anything) opens an in-game menu to pick each slot's look. Built (awaiting test): WBP_SequelMenu (tabs Melee/Ranged/Armor, wrap grid of icons of FOUND items only via ItemStashComponent.HasPreviouslyFoundItem, icons from ItemFunctionLibrary.StreamIconTextureForItemIdHigh, names from GetNameForItemType, "Own looks", "Menu key: Y - change", Close), WBP_SequelLookEntry (icon button -> menu Pick(Index)). The key setting lives in the menu (Change -> press any key; Esc keeps the old; mouse buttons ignored), stored as MenuKey in SequelLooks.sav - no launcher setting, no files to edit. Actor listens with an AnyKey node that does NOT consume input. Test keys and the top-left status text are gone. Item list: tools/transmog_items.py reads every BP_*Instance (ItemIdName + GearActor) for the 228 registered gear ids -> unreal/Scripts/transmog_items.json (221; 7 have no gameplay file: CowardsArmor_Unique1, MysteryArmor_Unique1, Pickaxe_Steel x3, SpiderCrossbow, Sword_Steel). Input mode is left alone (the game's own cursor/mode). Editor lib: AddMacro (StandardMacros: ForLoop pins execute/FirstIndex/LastIndex/LoopBody/Index/Completed), AddBoundEvent (widget button OnClicked), struct: pin type. tools/blueprints.py now needs "ok   done" at the end of a script's log and prints Python errors.
- 2026-10-30 Menu test (user): Y, tabs, buttons all work, but every icon read "Anchor" (right count per tab). Cause: the item id built in the loop (Make struct from Ids[Index]) kept the first item. Fix: Ids is now an array of ready-made SerializableItemId structs (default text ((SerializedId="Anchor"),...)), and each loop pass first copies Ids[Index] into the variable CurId (an impure Set), which everything else reads. Rule for later blueprints: inside loops, copy per-pass values into a variable before using them in several places.
- 2026-10-30 Crash after the Anchor fix (user; minidump %LOCALAPPDATA%/Dungeons/Saved/Crashes, read with a small parser + capstone on research/dungeons_image.bin): access violation at exe+0xA0DC8A = USlotActorManager map lookup (SlotActors[slot], map at manager+0x28) returning nothing, called from exe+0x9B9650 = EquipmentDisplayComponent's slot rebuild (OnGearItemSlotUpdated; item GearActor at +0x4E8, slot type byte at slot+0x1F8). I.e. we rebuilt a slot the display doesn't show (yet). Fix: ApplySlot rebuilds only when display.SlotActorManager.SlotActors contains the slot (Map_Contains); stand-ins gained USlotActorManager.SlotActors and EquipmentDisplayComponent.SlotActorManager. Not this mod's own code path in the exe - a data guard in our blueprint. Asked the user what they were doing when it crashed.
- 2026-10-30 Transmog menu works end to end (user): Y opens it, each tab lists found items with their own icons and names, picks apply to every item in the slot, own looks, key change, saved across missions and restarts, no crash with the SlotActors guard. Left: our own loader instead of the Blueprint Loader pak (can't be shipped), layout polish, gamepad, commit.
- 2026-10-30 Own loader (user: do it, commit to blueprints). Hook: /Game/Actors/BP_AvatarInfo - the game's empty helper (native AvatarInfo : AInfo, only a DefaultSceneRoot, no graph, tick off), placed in Menu.umap, Lobby.umap, Ingame.umap and 3 sublevels. Our copy has the same parent and scene root plus BeginPlay: if the map isn't "Menu" and no BP_SequelTransmog exists, spawn one. No levels, no Blueprint Loader, no game-mode watching; and since the Blueprint Loader replaces the tent, not this, both can be installed together (our actor is no longer in /Game/BPLoader, so it isn't loaded twice). Transmog actor now enables input from its 0.2 s timer once a player controller exists (Listening flag), as it can be spawned before the controller. Blueprint-Loader_P.pak renamed to .pak.disabled in ~mods for the test. Awaiting in-game test (menu: no loader text; camp and missions: Y menu works).
- 2026-10-30 Name (user): the transmog is its own mod, "MCD Transmog". Pak renamed SequelBlueprints_P.pak -> ~mods/MCDTransmog_P.pak (tools/blueprints.py OUT_PAK; installed file renamed, no rebuild). It needs nothing from SequelMod_P.pak and vice versa. Inside the pak the folder (/Game/SequelMod), asset names and the save file name (SequelLooks.sav) stay as they are: renaming the save would drop the looks players already chose.
- 2026-10-30 Own loader works in game (user): no loader text on the main menu, Y menu in camp and missions, saved looks kept. Menu title "Transmog" -> "MCD Transmog" (rebuilt and packed).
- 2026-10-30 Release zip (user): tools/package_transmog.py -> dist/MCD-Transmog-1.0.zip (32 KB): Dungeons/Content/Paks/~mods/MCDTransmog_P.pak + "MCD Transmog README.txt" beside it (install, Y menu, key change, save file place, uninstall). Unpacked into the game folder; no launcher, no Blueprint Loader.
- 2026-10-30 Bundle (user): python tools/package_transmog.py --bundle -> dist/SequelMod-1.0-with-Transmog.zip = the released SequelMod-1.0.zip plus MCDTransmog_P.pak and its readme in ~mods, and a note at the end of INSTALL.txt (delete the pak to leave it out). Safe together: the two paks share no files, and the launcher (play.py install_pak) only places/replaces SequelMod_P.pak.
