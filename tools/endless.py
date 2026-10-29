"""Endless Apocalypse: A+ table behaviour past A+25 (see Endless.toml).

The game computes each A+ stat as lerp(MinValue, MaxValue, Curve((L - IntroducedAt) / (25 - IntroducedAt)))
and never clamps the curve input, so past A+25 the curve is read beyond t = 1. The vanilla curve holds
its end value there, which freezes every stat at its A+25 value. Each stat that should keep changing
gets its own copy of the curve with extra keys past t = 1 (or, for stats introduced after A+25, at
negative t - the denominator is negative then). Keys up to t = 1 stay as they are, so A+1-25 are
untouched.

Power past A+25 ([power] in Endless.toml) is done the same way, with one key per A+ level. The game's
own math (from the exe; x = 1 + level/19 at Apocalypse VII, solo):
    gear power     = (1 + K*x) * LootPowerMultiplier       K = 10.482; the number itself has no limit
    gear strength  = 1.25 ** (19 * min(x_gear, 3))         x_gear = (gear power - 1) / K   (exe+0xB87920)
    mob scaling    = 1.25 ** (19 * min(x, 3))                                               (exe+0xB8D9C0)
Both stop at 3, which for gear is power 1 + 3K = 32.4 (shown as 315). Gear above that is no stronger, and
mobs stop at A+38. The 3.0 is one constant shared by ~300 unrelated places in the code: it can't be moved.
"slow" spreads the climb from A+25 to that cap over all levels up to the last one: LootPowerMultiplier
sets gear power to S25 + f * (cap - S25), the mob health and damage multipliers take off what the game's
own scaling adds beyond the "slowed" level L' = 25 + 10.9 * f (the same climb as gear), and f goes 0 -> 1 from A+25 to the last
level (milestone levels count for more, so power jumps there). Nothing in the game's code is touched.

The last level (LAST) is a finale with its own values ([finale] in Endless.toml).
"""
import struct
import settings

from uasset import Package, add_imports, clone_curve, curve_keys, set_export_properties

TABLE = "Dungeons/Content/DataTables/Assets/EndlessStruggle.uasset"
DROPS_MAP = "Dungeons/Content/GameModes/Ingame/Ingame.umap"   # regular mob drops (all missions)
DROPS_ACTOR = "ItemDropChanceActor_2"
GOLD_DEFAULTS = {"enabled": False, "chance_at_26": 0.02, "chance_at_99": 0.08, "min_amount": 1, "max_amount": 3}
CURVE = "Dungeons/Content/DataTables/Assets/EndlessStruggleLinearCurve.uasset"
CURVE_PATH = "/Game/DataTables/Assets/"
SOFT_CAP, TOP, LAST = 25, 99, 100   # vanilla cap, last regular level, the finale (= number of A+ levels)
# 2026-10-05: with 100 levels the mission slider once stopped at +25 although memory was right (cause not
# proven; the user asked for A+100 back). If it happens again, 25, 98, 99 is the known-good setting.
CHANCES = {"MobResurrectionChance", "MobDeflectChance"}  # off = 0 (every other stat: off = 1.0)
POWER_PER_X = 18 * 0.582353   # stored gear power = 1 + POWER_PER_X * x  (exe+0xB8F430)
STEPS = 19                    # x = 1 + level / STEPS at Apocalypse VII
MOB_BASE = 1.25               # mob scaling = MOB_BASE ** (STEPS * min(x, 3))
NATURAL_CAP_X = 3.0           # the game's own cap on x for gear strength and mob scaling (gear power 315)
GEAR_ROW = "LootPowerMultiplier"
MOB_ROWS = ("MobMaxHealthMultiplier", "MobDamageMultiplier")
POWER_MODES = ("slow", "natural", "off")
POWER_DEFAULTS = {"mode": "slow", "milestone_every": 10, "milestone_weight": 5.0, "top_power": None, "cap_level": None}


def curve_name(i):
    return f"EndlessStruggleSequelCrv{i:02d}"  # as long as EndlessStruggleLinearCurve (no offsets move)


def t_at(level, introduced):
    return (level - introduced) / (SOFT_CAP - introduced)


def load(config_path):
    """(profile name, {row: spec}) or exits with a message."""
    cfg = settings.load(config_path)
    profile = cfg.get("profile", "natural")
    if not isinstance(cfg.get(profile), dict):
        raise SystemExit(f"{config_path.name}: no [{profile}] section for profile = \"{profile}\"")
    return profile, cfg[profile]


def gold_settings(config_path):
    """[gold] from Endless.toml, with defaults (also read by the launcher's code patch)."""
    cfg = settings.load(config_path)
    return {**GOLD_DEFAULTS, **cfg.get("gold", {})}


def power_settings(config_path):
    cfg = settings.load(config_path)
    p = {**POWER_DEFAULTS, **cfg.get("power", {})}
    if p["mode"] not in POWER_MODES:
        raise SystemExit(f"{config_path.name}: [power] mode must be one of {', '.join(POWER_MODES)}")
    if not (isinstance(p["milestone_every"], int) and p["milestone_every"] >= 1 and p["milestone_weight"] >= 1):
        raise SystemExit(f"{config_path.name}: [power] milestone_every must be a whole number, milestone_weight >= 1")
    # top_power: the gear power shown at the last level. Gear only gets stronger up to the game's cap (315);
    # above it the number still rises and the mobs keep growing as if gear did, so the levels past the cap
    # have to be met with something else (the launcher switches on extra enchantment options on such gear).
    natural = NATURAL_CAP_X * POWER_PER_X * 10
    top = natural if p["top_power"] is None else p["top_power"]
    if not (isinstance(top, (int, float)) and 260 <= top <= 400):
        raise SystemExit(f"{config_path.name}: [power] top_power must be between 260 and 400")
    p["gear_cap"] = 1 + top / 10                          # stored gear power at the last level
    if p["cap_level"] is not None and not (isinstance(p["cap_level"], int) and SOFT_CAP < p["cap_level"] < LAST):
        raise SystemExit(f"{config_path.name}: [power] cap_level must be a level between 26 and {LAST - 1}")
    p["limit_level"] = STEPS * (NATURAL_CAP_X - 1)        # A+ level where the game's own mob scaling stops
    return p


def finale_settings(config_path):
    cfg = settings.load(config_path)
    return cfg.get("finale", {})


def stored_power(level):
    """Gear power as the game stores it, before LootPowerMultiplier (shown power = (stored - 1) * 10)."""
    return 1 + POWER_PER_X * (1 + level / STEPS)


def progress(power, level):
    """0 at A+25 -> 1 at the last level: how far along the climb to the cap A+level is. Every
    milestone_every-th level counts milestone_weight times a normal one, so power jumps there."""
    weight = lambda lv: power["milestone_weight"] if lv % power["milestone_every"] == 0 else 1.0  # noqa: E731
    total = sum(weight(lv) for lv in range(SOFT_CAP + 1, LAST + 1))
    return sum(weight(lv) for lv in range(SOFT_CAP + 1, min(level, LAST) + 1)) / total


def power_scales(power, level, gear_at_25):
    """(gear, mob): what to multiply the A+25 LootPowerMultiplier and mob health/damage by at A+level.
    gear_at_25: gear power (stored, with LootPowerMultiplier) at A+25."""
    natural = stored_power(level) * gear_at_25 / stored_power(SOFT_CAP)   # with the A+25 multiplier kept
    if power["mode"] == "slow":
        cap = 1 + POWER_PER_X * NATURAL_CAP_X   # where gear stops getting stronger
        if power["cap_level"]:
            # Two stretches: A+25 -> cap_level climbs to the cap; after it the number only counts up to top_power.
            at = power["cap_level"]
            if level <= at:
                target = gear_at_25 + (cap - gear_at_25) * (level - SOFT_CAP) / (at - SOFT_CAP)
            else:
                target = cap + (power["gear_cap"] - cap) * (level - at) / (LAST - at)
            # Mobs keep pace with real gear strength only; past the cap their growth is the profile's rows.
            slowed = SOFT_CAP + STEPS * (min(target, cap) - gear_at_25) / POWER_PER_X
        else:
            target = gear_at_25 + progress(power, level) * (power["gear_cap"] - gear_at_25)
            # Mobs follow the gear number all the way, also above the cap where gear itself stops improving.
            slowed = SOFT_CAP + STEPS * (target - gear_at_25) / POWER_PER_X
        return target / natural, MOB_BASE ** (slowed - min(level, power["limit_level"]))
    if power["mode"] == "natural":
        return min(1.0, power["gear_cap"] / natural), 1.0
    return 1.0, 1.0


def cap_level(power, rows, v1):
    """First A+ level whose gear power reaches the game's cap (315), or TOP if it never does."""
    gmn, gmx, _ = rows[GEAR_ROW]
    at_25 = stored_power(SOFT_CAP) * (gmn + (gmx - gmn) * v1)
    cap = 1 + POWER_PER_X * NATURAL_CAP_X
    for level in range(SOFT_CAP + 1, TOP + 1):
        if at_25 + progress(power, level) * (power["gear_cap"] - at_25) >= cap - 0.05:
            return level
    return TOP


def display_power(level, gear_multiplier):
    return (stored_power(level) * gear_multiplier - 1) * 10


def drop_node(d):
    return [("Category", "enum", ("EDropCategory", d["Category"])),
            ("MinProbability", "float", d["MinProbability"]), ("MaxProbability", "float", d["MaxProbability"]),
            ("MinAmount", "int", d["MinAmount"]), ("MaxAmount", "int", d["MaxAmount"]),
            ("TimeToMaxSeconds", "float", d["TimeToMaxSeconds"]), ("Exclusive", "bool", d["Exclusive"])]


def build_gold(build_root, extract_root, config_path):
    """Add a Gold entry to the regular mob drops at 0% chance. The launcher's code patch gives it a
    chance past A+25 only, so a normal launch never drops gold from mobs."""
    gold = gold_settings(config_path)
    src = build_root / DROPS_MAP if (build_root / DROPS_MAP).exists() else extract_root / DROPS_MAP
    pkg = Package(src)
    exp = next(e for e in pkg.exports if e["name"] == DROPS_ACTOR)
    drops = next(p for p in pkg.export_props(exp) if p["name"] == "Drops")["value"]
    entries = [{x["name"]: x["value"] for x in el} for el in drops]
    entries = [e for e in entries if e["Category"] != "EDropCategory::Gold"]
    entries.append({"Category": "EDropCategory::Gold", "MinProbability": 0.0, "MaxProbability": 0.0,
                    "MinAmount": int(gold["min_amount"]), "MaxAmount": int(gold["max_amount"]),
                    "TimeToMaxSeconds": 0.0, "Exclusive": False})
    node = ("Drops", "structarray", ("DropCategoryDescription", [drop_node(e) for e in entries]))
    head, body = set_export_properties(pkg, DROPS_ACTOR, [node])
    dest = build_root / DROPS_MAP
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(head)
    dest.with_suffix(".uexp").write_bytes(body)

    check = Package(dest)
    got = next(p for p in check.export_props(next(e for e in check.exports if e["name"] == DROPS_ACTOR))
               if p["name"] == "Drops")["value"]
    got = [{x["name"]: x["value"] for x in el} for el in got]
    if len(got) != len(entries) or got[-1]["Category"] != "EDropCategory::Gold" \
            or got[-1]["MaxAmount"] != entries[-1]["MaxAmount"] or got[:-1] != entries[:-1]:
        raise SystemExit(f"Verification failed for the gold drop in {dest.name}")
    print(f"  Gold from regular mobs past A+25: {gold['chance_at_26']:.0%} at A+26 -> "
          f"{gold['chance_at_99']:.0%} at A+99, {gold['min_amount']}-{gold['max_amount']} each")
    return dest


def plan(rows, vanilla, settings, power=None, finale=None):
    """{row: (min, max, introduced_at, [(t, v), ...])} for every row that changes past A+25.

    rows: {row: (min, max, introduced_at)} as built so far; vanilla: the stock curve's [(t, v), ...].
    power: [power] settings; finale: {row: value at the last level}.
    """
    (t0, v0), (t1, v1) = vanilla
    slope = (v1 - v0) / (t1 - t0)
    power, finale = power or {"mode": "off"}, finale or {}
    out, errors = {}, []
    number = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)  # noqa: E731
    scaled = {} if power["mode"] == "off" else {GEAR_ROW: 0, **{r: 1 for r in MOB_ROWS}}  # row: index in power_scales
    for row in dict.fromkeys([*scaled, *settings, *finale]):
        spec = settings.get(row, "freeze")
        if row not in rows:
            errors.append(f"{row}: not a row of the A+ table")
            continue
        if row in finale and not number(finale[row]):
            errors.append(f"{row}: [finale] takes a number, got {finale[row]!r}")
            continue
        mn, mx, intro = rows[row]
        if isinstance(spec, dict):   # a stat that's off up to A+25
            frm, to = spec.get("from"), spec.get("to")
            if not (isinstance(frm, int) and SOFT_CAP < frm < TOP and number(to)):
                errors.append(f"{row}: expected {{ from = <26-98>, to = <number> }}, got {spec!r}")
                continue
            if intro <= SOFT_CAP or row in scaled:
                errors.append(f"{row}: already active by A+25 - use \"grow\" or a number")
                continue
            start = 0.0 if row in CHANCES else 1.0
            until = spec.get("until", TOP)   # level where it reaches `to`; flat after
            if not (isinstance(until, int) and frm < until <= TOP):
                errors.append(f"{row}: until must be a level after from, up to {TOP}")
                continue
            keys = [(t_at(until, frm), 1.0), (0.0, 0.0)]   # t is negative here and falls as the level rises
            if row in finale:
                keys.insert(0, (t_at(LAST, frm), (finale[row] - start) / (to - start)))
            out[row] = (start, float(to), frm, keys)
            continue
        if spec == "freeze" and row not in scaled and row not in finale:
            continue
        if intro >= SOFT_CAP:
            errors.append(f"{row}: off up to A+25 - use {{ from = .., to = .. }}")
            continue
        if mx == mn:
            errors.append(f"{row}: MinValue == MaxValue, can't scale it")
            continue
        # The row's own value: its A+25 value, a straight line to its A+99 value, then the finale.
        # A list of [level, value] points instead draws straight lines through them (flat after the last).
        points = None
        if isinstance(spec, list):
            ok = spec and all(isinstance(pt, list) and len(pt) == 2 and isinstance(pt[0], int) and number(pt[1])
                              for pt in spec)
            levels = [pt[0] for pt in spec] if ok else []
            if not ok or levels != sorted(set(levels)) or levels[0] <= SOFT_CAP or levels[-1] > LAST:
                errors.append(f"{row}: expected [[level, value], ...] with rising levels 26-{LAST}, got {spec!r}")
                continue
            points = [(SOFT_CAP, mn + (mx - mn) * v1)] + [(pt[0], float(pt[1])) for pt in spec]
            end = v1
        elif spec == "freeze":
            end = v1
        elif spec == "grow":
            end = v1 + (t_at(TOP, intro) - 1.0) * slope
        elif number(spec):
            end = (spec - mn) / (mx - mn)
        else:
            errors.append(f"{row}: expected \"freeze\", \"grow\", a number or {{ from, to }}, got {spec!r}")
            continue
        last = TOP
        own = {lv: mn + (mx - mn) * (v1 + (end - v1) * (min(lv, last) - SOFT_CAP) / (last - SOFT_CAP))
               for lv in range(SOFT_CAP + 1, LAST + 1)}
        if points:
            def through(lv):
                for (la, va), (lb, vb) in zip(points, points[1:]):
                    if la <= lv <= lb:
                        return va + (vb - va) * (lv - la) / (lb - la)
                return points[-1][1]
            own = {lv: through(lv) for lv in own}
        if row in finale:
            own[LAST] = finale[row]
        # Keep the stock keys; the stock curve holds v1 from t1 on, so pin t = 1 (A+25) there too.
        keys = [(t0, v0), (t1, v1), (1.0, v1)]
        if row in scaled:   # one key per level: own value times the power scale
            gmn, gmx, _ = rows[GEAR_ROW]
            at_25 = stored_power(SOFT_CAP) * (gmn + (gmx - gmn) * v1)
            keys += [(t_at(lv, intro), (own[lv] * power_scales(power, lv, at_25)[scaled[row]] - mn) / (mx - mn))
                     for lv in own]
        else:
            marks = sorted({pt[0] for pt in points[1:]} | {LAST}) if points else (TOP, LAST)
            keys += [(t_at(lv, intro), (own[lv] - mn) / (mx - mn)) for lv in marks]
        out[row] = (mn, mx, intro, keys)
    return out, errors


def value_at(level, mn, mx, intro, keys):
    """What the game will compute for this row at A+level (for the build summary)."""
    if level < intro:
        return None
    t = t_at(level, intro)
    if t <= keys[0][0]:
        a = keys[0][1]
    elif t >= keys[-1][0]:
        a = keys[-1][1]
    else:
        for (ta, va), (tb, vb) in zip(keys, keys[1:]):
            if ta <= t <= tb:
                a = va + (vb - va) * (t - ta) / (tb - ta) if tb > ta else vb
                break
    return mn + (mx - mn) * a


def trial_settings(config_path):
    cfg = settings.load(config_path)
    return cfg.get("trial", [])


def apply_trials(changes, trials):
    """Trial levels ([[trial]] in Endless.toml): for `levels` levels ending at `level` (1 if not given) a row jumps
    to a multiple of its A+100 value and is back on its curve at the next level. Edits `changes` in place; returns
    error messages."""
    errors, finale_value = [], {}
    for trial in trials:
        level = trial.get("level")
        if not (isinstance(level, int) and SOFT_CAP + 1 < level <= TOP):
            errors.append(f"[[trial]]: level must be {SOFT_CAP + 2}-{TOP}, got {level!r}")
            continue
        span = trial.get("levels", 1)
        if not (isinstance(span, int) and 1 <= span <= level - SOFT_CAP - 1):
            errors.append(f"[[trial]] A+{level}: levels must be a whole number from 1, got {span!r}")
            continue
        first = level - span + 1
        for row, times in trial.items():
            if row in ("level", "name", "levels"):
                continue
            if row not in changes or row == GEAR_ROW or isinstance(times, bool) or not isinstance(times, (int, float)):
                errors.append(f"[[trial]] A+{level} {row}: needs a row that changes past A+25 and a number")
                continue
            mn, mx, intro, keys = changes[row]
            if first - 1 < intro:
                errors.append(f"[[trial]] A+{level} {row}: the row only starts at A+{intro}")
                continue
            finale_value.setdefault(row, value_at(LAST, mn, mx, intro, keys))   # before any trial touches it
            around = {lv: (value_at(lv, mn, mx, intro, keys) - mn) / (mx - mn) for lv in (first - 1, level + 1)}
            lo, hi = sorted((t_at(first - 1, intro), t_at(level + 1, intro)))
            keys = [k for k in keys if not lo <= k[0] <= hi]
            keys += [(t_at(lv, intro), a) for lv, a in around.items()]
            keys += [(t_at(lv, intro), (finale_value[row] * times - mn) / (mx - mn)) for lv in range(first, level + 1)]
            changes[row] = (mn, mx, intro, sorted(keys))
    return errors


def build(build_root, extract_root, config_path):
    """Write the curve packages and the edited table under build_root. Returns the files written."""
    profile, settings = load(config_path)
    # Off by default: growing an actor in a .umap shifts the file, and inline bulk data stored before it
    # (e.g. BodySetup collision data) keeps offsets relative to BulkDataStartOffset - the map then fails to
    # load (crash on mission start, exe+0xB9CFFB). Needs a size-neutral edit or a code-only approach.
    written = [build_gold(build_root, extract_root, config_path)] if gold_settings(config_path)["enabled"] else []
    src = build_root / TABLE if (build_root / TABLE).exists() else extract_root / TABLE
    pkg = Package(src)
    hlen = len(pkg.head)
    raw_rows = pkg.datatable_rows(pkg.exports[0])
    props = {r: {p["name"]: p for p in ps} for r, ps in raw_rows.items()}
    rows = {r: (p["MinValue"]["value"], p["MaxValue"]["value"], p["IntroducedAt"]["value"]) for r, p in props.items()}

    stock = Package(extract_root / CURVE)
    vanilla, _ = curve_keys(stock)
    power = power_settings(config_path)
    changes, errors = plan(rows, [(t, v) for _, t, v in vanilla], settings, power, finale_settings(config_path))
    trials = trial_settings(config_path)
    if not errors:
        errors = apply_trials(changes, trials)
    if errors:
        raise SystemExit("Endless.toml errors - nothing built:\n  " + "\n  ".join(errors))
    if not changes:
        return written

    shown = (SOFT_CAP, 50, TOP, LAST)
    print(f"  Endless Apocalypse profile '{profile}', power '{power['mode']}' ("
          + " -> ".join(f"A+{L}" for L in shown) + "):")
    if GEAR_ROW in changes:
        print("    gear power: " + " -> ".join(f"{display_power(L, value_at(L, *changes[GEAR_ROW])):.0f}" for L in shown))
    for trial in sorted(trials, key=lambda t: t["level"]):
        rows_ = [r for r in trial if r not in ("level", "name", "levels")]
        first = trial["level"] - trial.get("levels", 1) + 1
        print(f"    trial A+{first}-{trial['level']} {trial.get('name', '')}: " + ", ".join(
            f"{r} {value_at(first, *changes[r]):.3g} / {value_at(trial['level'], *changes[r]):.3g} (A+{first - 1}: "
            f"{value_at(first - 1, *changes[r]):.3g}, A+{trial['level'] + 1}: {value_at(trial['level'] + 1, *changes[r]):.3g})" for r in rows_))
    body = bytearray(pkg.body)
    refs = []
    for i, (row, (mn, mx, intro, keys)) in enumerate(sorted(changes.items())):
        p = props[row]
        struct.pack_into("<f", body, p["MinValue"]["pos"] - hlen, mn)
        struct.pack_into("<f", body, p["MaxValue"]["pos"] - hlen, mx)
        struct.pack_into("<i", body, p["IntroducedAt"]["pos"] - hlen, intro)
        name = curve_name(i)
        refs.append(("/Script/Engine", "CurveFloat", CURVE_PATH + name, name))
        head_c, body_c = clone_curve(stock, name, keys)
        dest = build_root / CURVE.replace("EndlessStruggleLinearCurve", name)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(head_c)
        dest.with_suffix(".uexp").write_bytes(body_c)
        got, _ = curve_keys(Package(dest))
        if [(round(t, 4), round(v, 4)) for _, t, v in got] != [(round(t, 4), round(v, 4)) for t, v in keys]:
            raise SystemExit(f"Verification failed for curve {name}")
        written.append(dest)
        fmt = lambda v: "off" if v is None else f"{v:.3g}"  # noqa: E731
        print(f"    {row}: " + " -> ".join(fmt(value_at(L, mn, mx, intro, keys)) for L in shown))

    head, body, indices = add_imports(Package(src, head=pkg.head, body=bytes(body)), refs)
    body = bytearray(body)  # adding imports only grows the header; row positions in the body hold
    for (row, _), index in zip(sorted(changes.items()), indices):
        struct.pack_into("<i", body, props[row]["Curve"]["pos"] - hlen, index)
    dest = build_root / TABLE
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(head)
    dest.with_suffix(".uexp").write_bytes(body)

    check = Package(dest).datatable_rows(Package(dest).exports[0])
    for i, (row, (mn, mx, intro, _)) in enumerate(sorted(changes.items())):
        got = {p["name"]: p["value"] for p in check[row]}
        if (got["Curve"] != curve_name(i) or got["IntroducedAt"] != intro
                or abs(got["MinValue"] - mn) > 1e-5 or abs(got["MaxValue"] - mx) > 1e-5):
            raise SystemExit(f"Verification failed for A+ table row {row}: {got}")
    written.append(dest)
    return written
