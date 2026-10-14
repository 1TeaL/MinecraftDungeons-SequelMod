"""Endless Apocalypse: raise the Apocalypse+ cap in the running game without changing its code.

    python tools/endless_patch.py [levels]     # default 100

The earlier version (aplus_patch.py) edited the game's code and the game then crashed when a mission
started. This one only changes data the game keeps on the heap (gone when the game closes):

1. Level count. The mission screen is a Blueprint widget; it asks four native functions how many A+
   levels there are, and builds its slider from the answers. Each Blueprint-callable function is a
   UFunction object holding a pointer to its native code (Func). Those four pointers are pointed at
   copies of the originals, in newly allocated memory, that answer `levels` instead of 25:
       GetTotalNumEndlessStruggles, GetTotalNumThreatLevelsAndEndlessStruggles,
       GetNumEndlessStrugglesInDifficulty, GetNumThreatLevelsAndEndlessStrugglesInDifficulty
   Nothing else in the game calls them.

2. Unlocks. The game has eight unlock steps (objects built at startup): Apocalypse VII boss -> A+3,
   then 1/2/3/4/5/6/7 bosses on the top unlocked level -> A+6/9/12/15/18/21/25. The highest unlocked
   level is the level of the best step whose rule is met. A step is 0x150 bytes: four rules
   (std::function, 0x40 bytes each: "does this mission count", "is it reached", its description, its
   progress), each holding {level to beat bosses on, number of bosses}; then the level it unlocks
   (+0x100) and a milestone id (+0x148). All steps sit in one list with room for 32.
   [unlock] in Endless.toml:
     staged = true   new steps are added after the vanilla eight (copies of the last one with their own
                     numbers): `bosses` different boss missions on the top unlocked level open the next
                     `levels_per_step` levels. The last level is a finale with a step of its own
                     (`finale_bosses`). The game's list has 24 places free; with more steps than that the
                     launcher swaps in a longer list of its own.
                     `key_levels`: top levels whose step asks for `key_bosses` boss missions instead.
     staged = false  the last vanilla step unlocks everything up to A+`levels` at once.

What each level does past A+25 (power, mob stats, rewards) is in the pak: see endless.py / Endless.toml.
"""
import ctypes
import ctypes.wintypes as wt
import struct
import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aplus_patch import alloc_near, open_game  # noqa: E402
from endless import LAST  # noqa: E402
from memprobe import k32, main_module, read  # noqa: E402

ENDLESS_CONFIG = Path(__file__).resolve().parent.parent / "Endless.toml"
UNLOCK_DEFAULTS = {"staged": True, "levels_per_step": 3, "bosses": 3, "finale_bosses": 3,
                   "key_levels": [], "key_bosses": 7, "ramp": False, "ramp_from": 1,
                   "major_levels": [], "major_bosses": 10, "tops": [], "level_bosses": {}}
VANILLA_LEVELS, THREAT_LEVELS = 25, 7
BOSS_MISSIONS = 14            # missions that count as boss missions with every DLC (8 without, by the wiki's list)
FUNC = 0xC0                   # UFunction::Func
# (name, thunk the UFunction points at, thunk length, offsets of its `call rel32`s (last one calls the
#  native), native, native's bytes, offset of the count inside them, count to write)
COUNTS = [
    ("GetTotalNumEndlessStruggles", 0xED32D0, 0x29, [0x1C], 0xA210D0, "b8 19 00 00 00 c3", 1, 0),
    ("GetTotalNumThreatLevelsAndEndlessStruggles", 0xED3330, 0x29, [0x1C], 0xA210E0, "b8 20 00 00 00 c3", 1, THREAT_LEVELS),
    ("GetNumEndlessStrugglesInDifficulty", 0xED30A0, 0x75, [0x28, 0x46, 0x63], 0xA1E720,
     "33 c0 ba 19 00 00 00 80 f9 03 0f 44 c2 c3", 3, 0),
    ("GetNumThreatLevelsAndEndlessStrugglesInDifficulty", 0xED3120, 0x75, [0x28, 0x46, 0x63], 0xA1EA40,
     "80 f9 03 b8 07 00 00 00 ba 20 00 00 00 0f 44 c2 c3", 9, THREAT_LEVELS),
]
SLOT = 0x100                  # page space per function: native copy at +0, thunk copy at +0x40

STEPS = 0x44EE690             # TArray of step pointers (data, num, max), filled at startup
STEP_CACHES = (0x44EF418, 0x44EF430)  # copies of it sorted by level, made the first time they're needed
VANILLA_STEPS = [3, 6, 9, 12, 15, 18, 21, 25]
STEP_SIZE, STEP_LEVEL = 0x150, 0x100
GROWN_ROOM = 64               # places in the longer step list the launcher swaps in when 32 aren't enough
# The rules inside a step: (offset, vtable, holds the boss count too)
RULES = [(0x00, 0x329AAD8, False), (0x40, 0x329AAA8, True), (0x80, 0x329AB08, True), (0xC0, 0x329AB38, True)]
RULE_SELF = 0x38              # rule: pointer to itself (it is stored inline)


class MBI(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_void_p), ("AllocationBase", ctypes.c_void_p),
                ("AllocationProtect", wt.DWORD), ("PartitionId", wt.WORD), ("RegionSize", ctypes.c_size_t),
                ("State", wt.DWORD), ("Protect", wt.DWORD), ("Type", wt.DWORD)]


k32.VirtualQueryEx.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.POINTER(MBI), ctypes.c_size_t]
k32.VirtualQueryEx.restype = ctypes.c_size_t
k32.WriteProcessMemory.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t,
                                   ctypes.POINTER(ctypes.c_size_t)]
k32.VirtualProtectEx.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.c_size_t, wt.DWORD, ctypes.POINTER(wt.DWORD)]
k32.FlushInstructionCache.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.c_size_t]
k32.VirtualAllocEx.restype = ctypes.c_void_p
k32.VirtualAllocEx.argtypes = [wt.HANDLE, ctypes.c_void_p, ctypes.c_size_t, wt.DWORD, wt.DWORD]


def poke(h, addr, data):
    if not k32.WriteProcessMemory(h, ctypes.c_void_p(addr), data, len(data), None):
        sys.exit(f"couldn't write to the game at 0x{addr:X}")


def find_pointers(h, values):
    """{value: [addresses]} of 8-byte values in the game's private read-write memory (its heap)."""
    wanted = {struct.pack("<Q", v): v for v in values}
    found = {v: [] for v in values}
    addr, info, chunk = 0x10000, MBI(), 1 << 24
    while k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(info), ctypes.sizeof(info)):
        start, size = info.BaseAddress or 0, info.RegionSize
        if info.State == 0x1000 and info.Type == 0x20000 and info.Protect == 0x04:  # commit, private, RW
            for off in range(0, size, chunk):
                data = read(h, start + off, min(chunk, size - off)) or b""
                for pat, v in wanted.items():
                    i = data.find(pat)
                    while i >= 0:
                        if i % 8 == 0:
                            found[v].append(start + off + i)
                        i = data.find(pat, i + 1)
        addr = start + size
    return found


def build_copy(h, base, at, levels, thunk, length, calls, native, native_hex, imm, extra):
    """(native copy, thunk copy) for one count function, placed at `at` / `at + 0x40`."""
    orig = bytes.fromhex(native_hex)
    if read(h, base + native, len(orig)) != orig:
        sys.exit(f"exe+0x{native:X}: unexpected code - not raising the level cap")
    code = bytearray(read(h, base + thunk, length))
    if code[-1] != 0xC3 or any(code[c] != 0xE8 for c in calls):
        sys.exit(f"exe+0x{thunk:X}: unexpected code - not raising the level cap")
    new_thunk = at + 0x40
    for c in calls:
        target = base + thunk + c + 5 + struct.unpack_from("<i", code, c + 1)[0]
        if c == calls[-1]:
            if target != base + native:
                sys.exit(f"exe+0x{thunk:X}: unexpected call - not raising the level cap")
            target = at
        struct.pack_into("<i", code, c + 1, target - (new_thunk + c + 5))
    return orig[:imm] + struct.pack("<i", levels + extra) + orig[imm + 4:], bytes(code)


def raise_count(h, base, size, levels):
    found = find_pointers(h, [base + thunk for _, thunk, *_ in COUNTS])
    # The pointers also sit in each class's name -> native lookup table. A UFunction starts with its
    # vtable (inside the exe), and all four are the same class: keep the hits that share one vtable.
    vtable_at = lambda a: struct.unpack("<Q", read(h, a - FUNC, 8) or bytes(8))[0]  # noqa: E731
    by_vtable = [{vtable_at(a): a - FUNC for a in found[base + thunk]} for _, thunk, *_ in COUNTS]
    common = [v for v in set.intersection(*(set(d) for d in by_vtable)) if base <= v < base + size]
    if not common and unlocked_top(h, base) > VANILLA_LEVELS:
        top = unlocked_top(h, base)
        print(f"A+ levels: already raised to {top} in this session" + ("" if top == levels else
              f" - restart the game to change it to {levels}"))
        return False
    if len(common) != 1 or any(sum(vtable_at(a) == common[0] for a in hits) != 1 for hits in found.values()):
        sys.exit("A+ level count: couldn't identify the four functions - nothing changed")
    objects = {name: d[common[0]] for (name, *_), d in zip(COUNTS, by_vtable)}
    page = alloc_near(h, base)
    writes = []
    for i, (name, thunk, length, calls, native, native_hex, imm, extra) in enumerate(COUNTS):
        at = page + SLOT * i
        new_native, new_thunk = build_copy(h, base, at, levels, thunk, length, calls, native, native_hex, imm, extra)
        poke(h, at, new_native)
        poke(h, at + 0x40, new_thunk)
        writes.append((objects[name] + FUNC, at + 0x40))
    old = wt.DWORD()
    k32.VirtualProtectEx(h, ctypes.c_void_p(page), 0x1000, 0x20, ctypes.byref(old))  # read + execute
    k32.FlushInstructionCache(h, ctypes.c_void_p(page), 0x1000)
    for where, target in writes:   # everything is in place: now switch the four pointers
        poke(h, where, struct.pack("<Q", target))
    return True


def read_array(h, addr):
    """(data pointer, [pointers], capacity) of a TArray of pointers in the game."""
    data, num, cap = struct.unpack("<QII", read(h, addr, 16) or bytes(16))
    raw = read(h, data, 8 * num) if data and 0 < num <= cap <= 4096 else b""
    return data, list(struct.unpack(f"<{len(raw) // 8}Q", raw)), cap


def step_level(h, step):
    raw = read(h, step + STEP_LEVEL, 4)
    return struct.unpack("<i", raw)[0] if raw else None


def read_steps(h, base):
    """([(step pointer, level it unlocks)], list data pointer, list capacity)."""
    data, ptrs, cap = read_array(h, base + STEPS)
    return [(p, step_level(h, p)) for p in ptrs], data, cap


def unlocked_top(h, base):
    return max(level or 0 for _, level in read_steps(h, base)[0])


def plan_steps(levels, per_step, places):
    """Levels the new steps unlock, in order. The last level is a finale with a step of its own; the
    levels before it open `per_step` at a time. If that takes more steps than there are places, the
    steps are made just big enough to fit, the bigger ones last."""
    span = levels - 1 - VANILLA_LEVELS
    count = min(places - 1, -(-span // per_step))
    size, bigger = divmod(span, count)
    targets, top = [], VANILLA_LEVELS
    for i in range(count):
        top += size + (i >= count - bigger)
        targets.append(top)
    return targets + [levels]


def step_tops(levels, settings, places):
    """The top level each new step opens. [unlock] tops lists them outright (it must rise, end on the last level and
    fit the free places); without it they are worked out from levels_per_step."""
    tops = settings.get("tops") or []
    if not tops:
        return plan_steps(levels, settings["levels_per_step"], places)
    if (not all(isinstance(t, int) for t in tops) or tops != sorted(set(tops)) or tops[0] <= VANILLA_LEVELS
            or tops[-1] != levels or len(tops) > places or len(tops) < 2 or tops[-2] != levels - 1):
        sys.exit(f"Endless.toml [unlock] tops: must be rising levels above {VANILLA_LEVELS}, at most {places} of them, "
                 f"ending ..., {levels - 1}, {levels}")
    return tops


def fill_step(template, at, needs_level, bosses, unlocks):
    """Bytes of a step at address `at`: `bosses` boss missions on A+`needs_level` unlock A+`unlocks`."""
    step = bytearray(template)
    for off, _, has_count in RULES:
        struct.pack_into("<i", step, off + 8, needs_level)
        if has_count:
            struct.pack_into("<i", step, off + 12, bosses)
        struct.pack_into("<Q", step, off + RULE_SELF, at + off)
    struct.pack_into("<i", step, STEP_LEVEL, unlocks)
    return bytes(step)


def unlock_settings():
    cfg = tomllib.loads(ENDLESS_CONFIG.read_text(encoding="utf-8")) if ENDLESS_CONFIG.exists() else {}
    s = {**UNLOCK_DEFAULTS, **cfg.get("unlock", {})}
    if not (isinstance(s["levels_per_step"], int) and 1 <= s["levels_per_step"] <= 74
            and all(isinstance(s[k], int) and 1 <= s[k] <= BOSS_MISSIONS for k in ("bosses", "finale_bosses", "key_bosses", "ramp_from", "major_bosses"))
            and s["ramp_from"] <= s["key_bosses"]
            and isinstance(s["key_levels"], list) and all(isinstance(k, int) for k in s["key_levels"])
            and isinstance(s["level_bosses"], dict)
            and all(str(k).isdigit() and isinstance(v, int) and 1 <= v <= BOSS_MISSIONS for k, v in s["level_bosses"].items())):
        sys.exit("Endless.toml [unlock]: levels_per_step must be 1-74, the boss counts 1-14, key_levels a list of levels")
    return s


def boss_counts(needs, settings):
    """Boss missions each step asks for. `needs` = the level each step is cleared on; the last one is the finale's.
    Key levels ask for key_bosses. With ramp on, the steps in between count up from ramp_from to key_bosses, one more
    per step, and start again at ramp_from after reaching it or after a key level - the base game's rising count,
    repeated. Otherwise they all ask for `bosses`."""
    out, run = [], 0
    low, high = settings["ramp_from"], settings["key_bosses"]
    own = {int(level): count for level, count in settings.get("level_bosses", {}).items()}
    for need in needs[:-1]:
        if need in own:                                      # a count of its own; the ramp goes on as if not
            out.append(own[need])
            run += 1
        elif need in settings["major_levels"]:                 # the big breakpoints ask for more than a key level
            out.append(settings["major_bosses"])
            run = 0
        elif need in settings["key_levels"]:
            out.append(high)
            run = 0
        else:
            out.append(low + run % (high - low + 1) if settings["ramp"] else settings["bosses"])
            run += 1
    return out + [settings["finale_bosses"]]


def set_unlocks(h, base, levels, settings):
    steps, data, cap = read_steps(h, base)
    vanilla, extra = steps[:len(VANILLA_STEPS)], steps[len(VANILLA_STEPS):]
    last, last_level = vanilla[-1] if vanilla else (None, None)
    if [lv for _, lv in vanilla[:-1]] != VANILLA_STEPS[:-1] or last_level not in (VANILLA_LEVELS, levels):
        sys.exit("A+ unlock steps: the game's list isn't what this was built for - unlocks not changed")
    if not settings["staged"]:
        if last_level != levels:
            poke(h, last + STEP_LEVEL, struct.pack("<i", levels))
        print(f"A+{VANILLA_LEVELS + 1}-{levels} unlock together with A+{VANILLA_LEVELS} (7 bosses on A+21 or higher)")
        return

    targets = step_tops(levels, settings, (cap if extra else GROWN_ROOM) - len(VANILLA_STEPS))
    needs = [VANILLA_LEVELS] + targets[:-1]
    # Like the game's own last step (7 bosses for A+22-25): the blocks that end on a key level ask for more.
    bosses = boss_counts(needs, settings)
    sizes = sorted({t - n for t, n in zip(targets[:-1], needs)})
    usual = (f"{settings['ramp_from']} to {settings['key_bosses']}, rising and starting over," if settings["ramp"]
             else str(settings["bosses"]))
    summary = (f"A+{VANILLA_LEVELS + 1}-{levels - 1} unlock in {len(targets) - 1} steps: {usual} different "
               f"boss missions on your top level open the next {'-'.join(map(str, sizes))}; "
               f"{settings['finale_bosses']} on A+{levels - 1} open A+{levels}")
    majors = [n for n in needs[:-1] if n in settings["major_levels"]]
    if majors:
        summary += f"; {settings['major_bosses']} bosses on A+" + ", ".join(map(str, majors))
    keys = [n for n in needs[:-1] if n in settings["key_levels"] and n not in settings["major_levels"]]
    if keys:
        summary += f"; {settings['key_bosses']} bosses on the key levels A+" + ", ".join(map(str, keys))
    if extra and len(extra) != len(targets):
        sys.exit("A+ unlock steps: this session already has a different set of steps - restart the game to change it")
    template = read(h, last, STEP_SIZE) or b""
    ok = len(template) == STEP_SIZE and all(
        struct.unpack_from("<Q", template, off)[0] == base + vt
        and struct.unpack_from("<Q", template, off + RULE_SELF)[0] == last + off
        and struct.unpack_from("<i", template, off + 8)[0] == VANILLA_STEPS[-2]
        and struct.unpack_from("<i", template, off + 12)[0] == (7 if has_count else 0)
        for off, vt, has_count in RULES)
    if not ok:
        sys.exit("A+ unlock steps: the last step doesn't look as expected - unlocks not changed")
    template = template[:STEP_LEVEL] + struct.pack("<i", VANILLA_LEVELS) + template[STEP_LEVEL + 4:]

    if extra:   # same session, run again: refresh the numbers in place
        for (at, _), need, count, target in zip(extra, needs, bosses, targets):
            poke(h, at, fill_step(template, at, need, count, target))
    else:
        # The sorted copies are made from the main list the first time the game needs them (opening the
        # mission screen, finishing a mission). Before that, adding to the main list is all it takes.
        caches = [(base + c, *read_array(h, base + c)) for c in STEP_CACHES]
        if any(cdata and ccap < len(steps) + len(targets) for _, cdata, _, ccap in caches):
            sys.exit("A+ unlock steps: the game has already loaded its unlock list and there's no room to add to it.\n"
                     "  Close the game and start it through the launcher (it adds the steps before that happens).")
        size = STEP_SIZE * len(targets)
        mem = k32.VirtualAllocEx(h, None, size, 0x3000, 0x04)   # commit + reserve, read/write
        if not mem:
            sys.exit("A+ unlock steps: couldn't get memory in the game - unlocks not changed")
        new = [mem + STEP_SIZE * i for i in range(len(targets))]
        for at, need, count, target in zip(new, needs, bosses, targets):
            poke(h, at, fill_step(template, at, need, count, target))
        if len(steps) + len(new) <= cap:
            poke(h, data + 8 * len(steps), struct.pack(f"<{len(new)}Q", *new))
            poke(h, base + STEPS + 8, struct.pack("<I", len(steps) + len(new)))
        else:
            # The game's list has room for 32 steps. More than that: a longer list of our own takes its place
            # (the steps themselves stay where they are; the list only holds pointers to them).
            longer = k32.VirtualAllocEx(h, None, 8 * GROWN_ROOM, 0x3000, 0x04)
            if not longer:
                sys.exit("A+ unlock steps: couldn't get memory for a longer list - unlocks not changed")
            everything = [at for at, _ in steps] + new
            poke(h, longer, struct.pack(f"<{len(everything)}Q", *everything))
            poke(h, base + STEPS, struct.pack("<QII", longer, len(everything), GROWN_ROOM))
        for addr, cdata, cptrs, _ in caches:
            if not cdata:
                continue
            down = step_level(h, cptrs[0]) > step_level(h, cptrs[-1])   # keep the copy's own order
            merged = new[::-1] + cptrs if down else cptrs + new
            poke(h, cdata, struct.pack(f"<{len(merged)}Q", *merged))
            poke(h, addr + 8, struct.pack("<I", len(merged)))
    if last_level != VANILLA_LEVELS:
        poke(h, last + STEP_LEVEL, struct.pack("<i", VANILLA_LEVELS))
    print(summary)


def apply(h, base, levels=LAST):
    assert VANILLA_LEVELS < levels < 128, "keep it to a sensible range"
    settings = unlock_settings()
    size = main_module(h)[1]
    if raise_count(h, base, size, levels):
        print(f"A+ levels raised to {levels} (game code untouched)")
    set_unlocks(h, base, levels, settings)


if __name__ == "__main__":
    h, base = open_game()
    if not h:
        sys.exit("Minecraft Dungeons isn't running")
    apply(h, base, int(sys.argv[1]) if len(sys.argv) > 1 else LAST)
