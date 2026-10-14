# Endless Apocalypse (launcher edition)

Apocalypse+ goes up to A+100. A+1-25 play exactly as before; past A+25 gear and mobs keep climbing
slowly, with a jump every 10 levels, and reach the game's hard power cap (315) at A+100, which is a
finale level with its own extreme stats.

Status (2026-10-04): **no game-code changes.** Confirmed in play: slider past +25, A+99 mission starts,
staged unlock shows "Complete 3 boss missions on Apocalypse+25". The 100-level build with milestones
and the finale is applied and read back, not yet played. Playtest list at the end.

## How to play

- Steam's Play button, with the game's Launch Options set to
  `"G:\SteamLibrary\steamapps\common\MinecraftDungeons\Mods\SequelMod\steam_launch.bat" %command%`.
  Steam runs the launcher, which backs up the saves, starts the game, waits ~40 s for it to finish
  starting, then switches the built-in enchantments and Endless Apocalypse on. It stays open until the
  game closes.
- Or `Play Endless Apocalypse.bat` (`python tools/play.py --endless`). If the game is already running it
  just switches things on.
- Switches: `Launcher.toml` (`builtins`, `endless`). Settings: `Endless.toml`; rebuild the pak after
  changing it (`python tools/sequel.py build`, game closed).
- Without the launcher it's the plain Sequel Mod with the usual 25 A+ levels.

## The level cap (launcher, `tools/endless_patch.py`, data only)

The mission screen's A+ slider is a Blueprint widget (UMG_MissionThreatSlider). It creates its level
markers in a loop and scrolls, so more levels need no new UI. It asks four native functions how many
levels there are, each hard-coded:

| Function | Native | Vanilla | Endless |
|---|---|---|---|
| GetTotalNumEndlessStruggles | exe+0xA210D0 | 25 | 100 |
| GetTotalNumThreatLevelsAndEndlessStruggles | exe+0xA210E0 | 32 | 107 |
| GetNumEndlessStrugglesInDifficulty | exe+0xA1E720 | 25 (Apocalypse) | 100 |
| GetNumThreatLevelsAndEndlessStrugglesInDifficulty | exe+0xA1EA40 | 32 (Apocalypse) | 107 |

Nothing else calls them. Each is a UFunction object on the heap holding a pointer to its native code
(Func, +0xC0). The launcher finds the four objects (scan for the thunk addresses, keep the hits that
share one vtable), writes copies of the thunks + natives with the new numbers into a freshly allocated
page, and repoints Func. The game's own code is never written to.

**Unlocks** (`[unlock]` in `Endless.toml`). Eight unlock steps are built at startup (exe+0x136ED0 ..
0x137120): Apocalypse VII boss -> A+3, then 1/2/3/4/5/6/7 bosses on the top unlocked level ->
A+6/9/12/15/18/21/25. The highest unlocked level is the level of the best step whose rule is met
(exe+0x9DE6A0 -> 0xA3D5B0).

A step is 0x150 bytes: four rules (std::function, 0x40 bytes each, stored inline with a pointer to
itself at +0x38), then the level it unlocks (+0x100) and a milestone id (+0x148, 8-15).

| Rule | vtable | Holds | Does |
|---|---|---|---|
| +0x00 | exe+0x329AAD8 | level | does finishing this mission count towards the step |
| +0x40 | exe+0x329AAA8 | level, bosses | reached: boss missions beaten on A+level or higher >= bosses (exe+0xA3B660) |
| +0x80 | exe+0x329AB08 | level, bosses | description text ("Defeat X boss missions on Y") |
| +0xC0 | exe+0x329AB38 | level, bosses | progress text |

All steps sit in one list (exe+0x44EE690, 8 used of 32). Two copies sorted by level (exe+0x44EF418
ascending, exe+0x44EF430 descending) are made from it the first time the game needs them.

`staged = true` (chosen 2026-10-04): the launcher writes 24 new steps into memory it allocates in the
game (copies of the last vanilla step with their own numbers and the same milestone id 15) and appends
them to the list: 3 different boss missions on your top unlocked level open the next 3 levels
(A+25 -> 28 -> 31 ... -> 79), then the next 4 (-> 83 -> 87 -> 91 -> 95 -> 99, because only 24 places
are free), and 3 bosses on A+99 open the A+100 finale. The sorted copies don't exist yet at
launch (~40 s), so they pick the new steps up by themselves. If they already exist (launcher run late
in a session) and have no room, the launcher says so and leaves unlocks alone.
`staged = false`: the last vanilla step's 25 becomes 99, so A+26-99 open together with A+25.

The milestone id is only a key for a per-tier counter (exe+0x99F860, called from exe+0xE3AA00) and for a
lookup by id (exe+0xA3DFC0, ids 8-15 only), which searches the ascending copy and so still finds the
vanilla step first.

**Why not code patches.** The first version changed the count constants in place and hooked the power
math. With those active the game crashed when a mission started (exe+0xB9CFFB: a level actor's Tick
gets no player controller). With them off, missions load. The old patch is `tools/aplus_patch.py`
(retired).

## What the levels do past A+25 (pak, `tools/endless.py`, `Endless.toml`)

Each A+ stat is lerp(Min, Max, curve(t)), t = (L - IntroducedAt) / (25 - IntroducedAt). The game never
clamps t and the stock curve holds its end value, so past A+25 every stat stays at its A+25 value. Stats
that should keep moving get their own copy of the curve (`EndlessStruggleSequelCrvNN`) with keys past
t = 1 (or negative t for stats introduced after A+25). A+1-25 are untouched.

**Power** (`[power]`). The game's own math, x = 1 + level/19 at Apocalypse VII solo:
- gear power = (1 + 10.482·x) · LootPowerMultiplier. The number has no limit.
- gear strength = 1 + 1.5·(1.25^(19·min(x_gear, 3)) - 1), x_gear = (gear power - 1)/10.482
  (attack exe+0xB87920; the health/heal factor exe+0xB93340 is the same shape).
- mob scaling = k·0.75·1.25^(19·min(x, 3)) (exe+0xB8D9C0).

**The cap is hard.** Gear and mobs both stop at 3: for gear that is power 32.4, shown as 315; mobs get
there at A+38 at the game's own pace. A 330 item hits exactly like a 315 one. The 3.0 is one float in
read-only data (exe+0x3101950) used by about 300 unrelated places, so it can't be raised. What can still
grow past the cap: the A+ table's mob multipliers and the rewards.

`"slow"` (default) spreads the climb from A+25 (254) to the cap over A+26-100, one curve key per level:
- f(level) goes 0 -> 1; every `milestone_every`-th level (30, 40 ... 100) counts `milestone_weight`
  times a normal level, so power jumps there (+2.8 instead of +0.56 with the defaults 10 and 5).
- LootPowerMultiplier sets gear power to 254.4 + f·(314.5 - 254.4).
- MobMaxHealthMultiplier and MobDamageMultiplier take off what the game's own scaling adds beyond the
  slowed level L' = 25 + 10.9·f (the same climb as gear). So with matching gear the only extra
  difficulty is the profile's own health/damage growth.

| A+ | 25 | 30 | 40 | 50 | 60 | 70 | 80 | 90 | 99 | 100 |
|---|---|---|---|---|---|---|---|---|---|---|
| Gear power | 254 | 259 | 267 | 275 | 283 | 291 | 299 | 307 | 312 | 315 |
| Mobs vs matching gear | 1.5x | 1.6x | 1.8x | 2.0x | 2.2x | 2.4x | 2.6x | 2.8x | 3.0x | 6.0x |
| Shown on the mission screen | 1.5x | 0.64x | 0.17x | 0.25x | 0.38x | 0.58x | 0.86x | 1.27x | 1.66x | 3.75x |

Side effect: the mission screen's health/damage figures for A+26+ show the correction (last row), not
the real strength. Assumption to confirm in play: mob health and damage both scale with the one mob
factor. In multiplayer the game's cap is reached a few levels earlier, so mobs come out slightly weaker
there between about A+35 and A+38.

`"natural"`: the game's own pace until the cap, flat from there. `"off"`: power left alone.

**Finale** (`[finale]`): A+100 takes its own values, set per stat.

**Other stats**, profile `natural` (A+25 -> A+50 -> A+99 -> A+100 finale):

| Stat | A+25 | A+50 | A+99 | A+100 |
|---|---|---|---|---|
| Mob health / damage (vs matching gear) | 1.5x | 2.0x | 3.0x | 6.0x |
| Loot quality (rarity rerolls) | 4.1 | 8.8 | 18 | 100 |
| Enchanted mob chance / power | 4.25 / 2.25 | 5.55 / 3.29 | 8.09 / 5.32 | 12 / 8 |
| XP | 1.0 | 2.3 | 5.0 (from A+26) | 10 |
| Mob count | 1.0 | 1.14 | 1.5 (from A+30) | 2.0 |
| Mob resurrection chance | 0 | 1.7% | 10% (from A+40) | 25% |
| Mob projectile deflect chance | 0 | 0 | 15% (from A+50) | 30% |
| Speed, stun, knockback, endurance, mob healing, player healing | frozen at A+25 | | | |

Profile `climb`: the same, but health/damage climb to 6.75x at A+99.

**Gold from mobs**: off. It needed a map edit (broke the map file) and a code hook. Open: another
reward that works from data only.

## Reference

Power code map: GetRecommendedTotalGearItemPower thunk exe+0xF42EF0 -> 0xBD3100 -> 0xBC1BB0 (difficulty
context, exe+0xA03430) + 0xBCBEA0 (recommended = previous step) -> 0xBE9790 -> 0xA02B40 -> 0xA3AE10
(x -> power via 0xB8F430). Mob factor: 0xA3AC20 -> 0xB8D9C0; it returns
k·0.75·1.25^(19·min(x,3)) - 1 with k between 1.35 and 1.6 on Apocalypse. A+ table builder:
exe+0xA1A660. Offline disassembly: `tools/dumpimage.py` + `tools/disasm.py`.

**"Gear and artifact power: X-Y" on the mission screen** (text built at exe+0xBCD9A0) is not the
mission's own range. The mission range M is power(x) .. power(x + 1.3/19) (exe+0xA02B40); recommended
power is its midpoint. The line shows M blended with a player range P (exe+0xAF4900 gear, 0xAF5FB0
artifacts, joined by 0xE4A500): min = min(M, P); gear max = P + f·(M - P) when M is higher, artifacts
P + g·(M - P), with f/g = 0.3/0.5 normally and 0.1/0.2 on any A+ level. P comes from the player's
EquipmentComponent (exe+0xAF1A50 -> 0x99AC90): the average equipped power (exe+0x98F9E0, the "your
power" number) is mapped to the difficulty it corresponds to (exe+0x9ACFF0 -> 0xA02990) and P is that
difficulty's range. Seen 2026-10-04: A+99 with 251 equipped shows 249-272 next to recommended 331
(P = 249-256, M = 329-333 with the curve of that build). Vanilla behaviour: drops follow your equipped power and catch up to the
mission a slice at a time. The slices are constants in the code.

A fourth difficulty (after Default / Adventure / Apocalypse) isn't practical: the difficulty is a
3-value enum in the code, the select screen has three fixed panels, and power, unlocks and saves all
key off it. A+ levels are the game's own "more of the same list" mechanism.

- Multiple gilded enchants per item: not possible (one NetheriteEnchantData field in the save format).
- Breaking the 315 cap: see **The cap is hard** above. It would take code changes in several functions.

## Needs a playtest

1. Mission select: the A+ slider goes past 25; A+26-28 are locked until 3 different boss missions are
   beaten on A+25, then open (and so on every 3 levels). The lock text names the right level and count.
2. A mission starts and finishes on A+25 and on A+26+ with Endless on.
3. A+26+: mobs feel like A+25 plus a bit (health and damage); drops around 255+.
4. The save keeps A+26+ progress; a normal launch afterwards still loads the save. (Backups:
   `save_backups/`.)
5. Resurrection (A+40+) and deflect (A+50+) actually happen.
