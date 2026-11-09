# Balance pass, 2026-11-09

**Decided (user):** Poison Cloud keeps its 100% trigger; Dipping Poison's poison and Shockwave's base damage back to
the game's; Fire / Poison Focus stay +50 / 100 / 150% on the game's own damage (the max-health share unboosted - the
game's Focus doesn't boost it, tested); already-buffed enchantments stay; Soul Focus +25 / 50 / 75%, Soul Siphon 40%,
Health Synergy 5 / 7.5 / 10%, Beast Burst 2x, Deflect 30 / 40 / 50% applied. Supercharge +40 / 60 / 80% and Wild Rage
30 / 45 / 60% added to the launcher's Formulas (their value routines found).

(The proposal as it was sent:)

Aim: every enchantment at least **A** at Apocalypse +25 to +100. Ranks are for the mod as it is now (after the
changes already made), judged at high Apocalypse, where flat damage falls off and max-health damage, scaling with
your weapon, crowd control and survival carry. **S** = build-defining, **A** = good in most builds, **B** = only in
its niche or weak, **C** = a farming / utility pick that combat numbers can't make A.

Already done (your call): burning and poisoned mobs lose their max-health share **anywhere in the mission**, not only
within 20 blocks of you. It goes in with the next build.

## 1. Proc damage now covered by max-health damage - buffs to take back

Fire, poison and lightning procs now take a share of max health, and Shockwave / Swirling scale with your weapon, so
the flat-damage buffs we gave them earlier are no longer needed.

| Enchantment | Mod now | Proposed | Why |
|---|---|---|---|
| Poison Cloud | always triggers (game 30%), cloud 4 blocks (game 2.5) | **trigger back to 30%**, keep the 4-block cloud | Every hit making a cloud keeps every mob poisoned; at 30% fast weapons still keep them poisoned. The wider cloud only decides how many mobs get the share. |
| Dipping Poison | 10 / 15 / 20 arrows, poison 30 / s (game 15) | **poison damage back to 15 / s**, keep the arrow count | The share does the damage; the arrows decide how many mobs get poisoned. |
| Shockwave | base damage 60 (game 30), + 50 / 75 / 100% of your hit | **base damage back to 30** | The weapon scaling does the work. |
| Fire Focus, Poison Focus | +50 / 100 / 150% (game +25 / 50 / 75) | **back to +25 / 50 / 75, and make them boost the max-health share too** (as Lightning Focus does) | Our fire / poison damage is tagged fire / poison, so the game's Focus may already boost it - to be checked in game. Either way the share is where the damage is now. At III: poison 10% → 17.5% a second. |
| Thundering | always strikes, base damage 3.75 (game 12.5 at 30%) | no change | Same flat damage per hit on average as the game (30% x 12.5 = 3.75). |
| Fire Trail, Burning | trail 6 s (game 4), Burning 4 blocks (game 3) | no change | Not damage: how long and how wide mobs get set on fire, which is what feeds the share. |
| Shock Web, Fuse Shot, Shadow Blast, Void Blast | 2x, 2x / 1.5x radius, 3x, 4x damage | no change | No max-health share or weapon scaling, so their buffs are still what keeps them up. |

## 2. Every enchantment, ranked

"Mod now" only lists what the mod changed; "-" = the game's own. **Proposed** is only filled where a change is
suggested (section 1 included).

### Melee

| Rank | Enchantment | Mod now | Proposed |
|---|---|---|---|
| S | Committed | - | |
| S | Critical Hit | x5 damage (game x3) | |
| S | Echo | repeats every 2.1 / 1.1 / 0.1 s | |
| S | Enigma Resonator | 0-30 / 40 / 50% (game 15 / 20 / 25) | |
| S | Exploding | 15 / 25 / 35% max health, instant, chains, kill credit | |
| S | Gravity | - | |
| S | Leeching | 4 / 5 / 6%, kill credit | |
| S | Stunning | 15 / 30 / 45% | |
| S | Swirling | + 50 / 75 / 100% of your hit | |
| S | Void Strike | - | |
| S | Ignite, Venom Siphon, Shatter, Overload (new) | max-health damage / x2-3 on chilled | |
| S | Shadowcloak (new, Powerful now) | 15 / 20 / 25% Shadow Form per kill | |
| A | Ambush | +50 / 100 / 150% | |
| A | Anima Conduit | - | |
| A | Artifact Synergy | 150 / 200 / 250% | |
| A | Chains | 45%, 4 mobs | |
| A | Dynamo | - | |
| A | Fire Aspect | + burning share | |
| A | Freezing | -40 / 55 / 70% speed | |
| A | Guarding Strike | 50% shield 3 / 4 / 5 s, kill credit | |
| A | Pain Cycle | x4 / 6 / 8, 2% drain | |
| A | Poison Cloud | always, 4-block cloud, + poison share | trigger 30% (section 1) |
| A | Radiance | always triggers, smaller heals | |
| A | Rampaging | +50% speed 1 / 2 / 3 s on every kill | |
| A | Refreshment | kill credit | |
| A | Sharpness | - | |
| A | Shockwave | 2x + weapon scaling | base back to 1x (section 1) |
| A | Sweeping Edge (new) | 20 / 30 / 40% splash | |
| A | Thundering | every hit, + 1 / 2 / 3% max health | |
| A | Unchanting | - (lots of enchanted mobs in Endless) | |
| A | Weakening | - | |
| B | Busy Bee | 33 / 67 / 100% bee on a weapon kill | **give it kill credit** (as Guarding Strike: our own copy spawns the bee) - bees are weak alone but every kill makes one; Beast Boss boosts them |
| B | Soul Siphon | - (20% for 1 / 3 / 5 souls) | **40% chance** (Soul builds feed artifacts, Artifact Amplifier, Soul Focus) |
| B (niche) | Illager's Bane, Smiting | +50 / 75 / 100% | **+75 / 125 / 175%** - A in their missions, never a dead pick there |
| C | Looting, Prospector | - | farming picks; leave, or rework later (spare slots) |

### Ranged

| Rank | Enchantment | Mod now | Proposed |
|---|---|---|---|
| S | Chain Reaction | - | |
| S | Critical Hit, Enigma Resonator, Void Strike, Gravity | see melee | |
| S | Growing | full damage at 10 blocks (game 16) | |
| S | Overcharge | - | |
| S | Rapid Fire | +20 / 35 / 50% | |
| S | Relentless (new) | +2 / 3 / 4% damage and speed per stack | |
| A | Accelerate | - | |
| A | Artifact Charge | - | |
| A | Bonus Shot | second arrow 30 / 50 / 75% | |
| A | Burst Bowstring | also on armor | |
| A | Cooldown Shot | - | |
| A | Dipping Poison | 10 / 15 / 20 arrows, 2x poison | poison back to 1x (section 1) |
| A | Dynamo | - | |
| A | Fire Aspect, Poison Cloud | see melee | |
| A | Fuse Shot | instant, 2x, 1.5x radius | |
| A | Infinity, Multishot, Piercing, Power, Ricochet, Roll Charge, Tempo Theft | - | |
| A | Radiance Shot | always triggers | |
| A | Refreshment | 2 / 4 / 6 s, kill credit | |
| A | Shock Web | 2x damage | |
| A | Unchanting | - | |
| B | Supercharge | - (+20 / 30 / 40% on charged shots) | **+40 / 60 / 80%** - charged shots are slow; the game's numbers trail Power |
| B | Wild Rage | - (20 / 30 / 40%) | **30 / 45 / 60%** - enraged mobs fighting each other is real crowd control in Endless packs |
| B | Punch | 700 / 1100 / 1500% knockback | **back to the game's numbers** - pushing mobs away fights every area build; Punch stays a niche (kiting) pick |
| B (niche) | Smiting | see melee | |
| C | Prospector | - | |

### Armor

| Rank | Enchantment | Mod now | Proposed |
|---|---|---|---|
| S | Cool Down | - | |
| S | Potion Barrier | - | |
| S | Protection | -15 / 25 / 35% damage | |
| S | Reckless | +100 / 125 / 150% | |
| S | Death Barter, Final Shout | Final Shout at 50% health, every 8 / 6 / 4 s | |
| S | Battle Hardened, Bottomless Brew, Barrier Brew, Artifact Amplifier (new) | | |
| A | Acrobat, Multi-Roll, Swiftfooted | Swiftfooted 5 s | |
| A | Bag of Souls | 100 / 200 / 300% | |
| A | Beast Boss, Beast Surge | 2.5x pet damage, 20 s surge | |
| A | Burning, Fire Trail, Electrified | + max-health share | |
| A | Chilling | - (feeds Shatter) | |
| A | Cowardice, Frenzied | +40 / 50 / 60% | |
| A | Fire / Poison / Lightning Focus | Fire / Poison +50 / 100 / 150% | Fire / Poison back to +25 / 50 / 75, boosting the share (section 1) |
| A | Last Stand, Buddy Brew, Ancient Alchemy (new) | | |
| A | Shadow Blast | 3x | |
| A | Shadow Surge, Snowball, Soul Speed | Snowball every 3 / 2 / 1 s | |
| B | Soul Focus | - (+10 / 20 / 30%) | **+25 / 50 / 75%** like the other Focuses |
| B | Health Synergy | - (3 / 4 / 5% per artifact) | **5 / 7.5 / 10%** |
| B | Beast Burst | - | **double damage** - a potion's only pet payoff besides Beast Surge |
| B | Rush, Speed Synergy | Rush 50 / 100 / 150%, Speed Synergy +50% | movement only - fine as they are (B is their job) |
| B | Life Boost | 20 / 40 / 60% after a death | leave - only matters once you've died |
| B | Deflect | - | **35 / 50 / 65%** - ranged mobs hit hard in Endless |
| C | Luck of the Sea, Surprise Gift, Prospector, Tumblebee | Luck 25 / 50 / 75% | farming picks; Tumblebee could get kill credit with Busy Bee |

## 3. What this leaves below A

- **Farming picks** (Looting, Prospector, Luck of the Sea, Surprise Gift): numbers can't make them combat picks. They
  could be the next reworks into new enchantments, like Recycler and Food Reserves were - only if you want more.
- **Movement and Life Boost:** fine in their role.

## Needs checking in game

- Whether the game's Fire / Poison Focus already boost our max-health damage (decides how section 1's Focus change is
  built).
- (Fixed: ENCHANTMENTS.md now shows Guarding Strike's 3 / 4 / 5 s.)
