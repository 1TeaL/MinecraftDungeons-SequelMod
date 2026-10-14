"""Build tools/artifact_fields.json: for each artifact class, its vtable and the offsets of its damage/heal numbers.

Sources, all from the exe dump: the class constructor (vtable, object size; found like research/ctor_members.py)
and the reflection data (property name -> offset; the offset is 36 bytes after the pointer to the name).
A property name can belong to several classes, so only offsets inside this class's own part of the object count
(past AItemInstance's 0x4E8 bytes, before the class's size) and the float/int found there must be the known default.
"""
import csv
import json
import re
import struct
import sys
from pathlib import Path

from capstone import Cs, CS_ARCH_X86, CS_MODE_64

ROOT = Path(__file__).resolve().parent.parent
d = (ROOT / "research" / "dungeons_image.bin").read_bytes()
BASE = 0x7ff6b16e0000
text = d[:0x3000000]
md = Cs(CS_ARCH_X86, CS_MODE_64)
ITEM_INSTANCE_SIZE = 0x4E8

# native class -> {property: kind}; kind decides which growth curve applies (ArtifactScaling.toml)
FIELDS = {
    "TargetingStrikeItem": {"StrikeDamagePerSoul": "damage"},                      # Lightning Rod
    "CorruptedBeacon": {"DamagePerSoulPerTick": "damage"},
    "CorruptedSeeds": {"PoisonDamageScale": "damage"},
    "HarvesterInstance": {"DamagePerSoul": "damage"},
    "IceWandInstance": {"IceDamageOverride": "damage"},
    "ChargedRedstoneMinesInstance": {"DamagePerMine": "damage"},
    "SatchelOfTheElementsInstance": {"LightningDamage": "damage", "FireDamage": "damage"},
    "UpdraftTomeInstance": {"UpdraftDamage": "damage"},
    "MobMasherInstance": {"ShockwaveDamage": "damage"},
    "NetherWartSporeGrenadeInstance": {"Damage": "damage"},
    "SpinWheelInstance": {"Damage": "damage"},
    "GuardianEyeInstance": {"BaseDamage": "damage"},
    "FireworkBombInstance": {"BombDamage": "damage", "ProjectileDamage": "damage"},   # Fireworks Display
    "BeeNestItemInstance": {},
    "SoulHealer": {"HealAmountPerSoul": "heal"},
    "TotemOfRegenerationInstance": {"HealthHealedPerSecond": "heal"},
    # pets: the summoned mob's damage and health multipliers
    "PileOfBones": {"DealDamageMultiplier": "damage", "IncreasedMaxHealthMultiplier": "heal"},          # Tasty Bone
    "VillagersWhistle": {"DealDamageMultiplier": "damage", "IncreasedMaxHealthMultiplier": "heal"},     # Golem Kit
    "WonderfulWheat": {"DealDamageMultiplier": "damage", "IncreasedMaxHealthMultiplier": "heal"},
    "RandomMobSummonItem": {"DealDamageMultiplier": "damage", "IncreasedMaxHealthMultiplier": "heal"},  # Enchanted Grass
    "SoulLanternInstance": {"DealDamageMultiplier": "damage", "IncreasedMaxHealthMultiplier": "heal"},
}

LEA = re.compile(rb"[\x48\x4c]\x8d[\x05\x0d\x15\x1d\x25\x2d\x35\x3d]")
leas = {}
for m in LEA.finditer(text):
    j = m.start()
    leas.setdefault(j + 7 + struct.unpack_from("<i", text, j + 3)[0], []).append(j)


def rip_target(ins):
    return ins.address + ins.size + int(ins.op_str.split("rip")[1].replace("]", "").replace(" ", ""), 16)


def last_vtable_store(start, length=0x400):
    """The vtable a constructor leaves in the object: the last `lea rax, [rip+X]` / `mov [this], rax` pair."""
    prev, this, vtable = None, None, None
    for ins in md.disasm(d[start:start + length], start):
        m = re.match(r"qword ptr \[(r\w+)\], rax$", ins.op_str) if ins.mnemonic == "mov" else None
        if prev is not None and m and this in (None, m.group(1)):
            this, vtable = m.group(1), prev              # the most derived class stores last
        if ins.mnemonic == "lea" and ins.op_str.startswith("rax, [rip"):
            prev = rip_target(ins)
        elif ins.mnemonic == "call" or ins.op_str.startswith(("rax,", "eax,")):
            prev = None                                  # rax no longer holds that address
        if ins.mnemonic in ("ret", "int3"):
            break
    return vtable


def class_info(name):
    """(constructor, object size, vtable) of AName / UName.

    Found through the class's GetPrivateStaticClass (it passes the wide class name and the object size and
    registers a constructor wrapper). The wrapper either jumps to the real constructor (`mov rcx, [rcx]` ...) or,
    for small classes, has the constructor inlined (`push rbx; sub rsp, 0x20; mov rbx, [rcx]` ...)."""
    for prefix in "AU":
        wide = b"\0\0" + (prefix + name).encode("utf-16le") + b"\0\0"
        for m in re.finditer(re.escape(wide), d):
            for site in leas.get(m.start() + 4, []):
                f = site
                while d[f - 1] != 0xCC and f > site - 0x400:
                    f -= 1
                size, jumps, inline = None, [], []
                for ins in md.disasm(d[f:f + 0x120], f):
                    if ins.mnemonic == "mov" and ins.op_str.startswith("dword ptr [rsp + 0x20],"):
                        size = int(ins.op_str.split(",")[1], 16)
                    if ins.mnemonic == "lea" and "rip" in ins.op_str:
                        t = rip_target(ins)
                        if 0 < t < len(text) and d[t:t + 3] == b"\x48\x8b\x09":      # mov rcx, [rcx]
                            jumps.append(t)
                        elif 0 < t < len(text) and d[t:t + 9] == b"\x40\x53\x48\x83\xec\x20\x48\x8b\x19":
                            inline.append(t)
                    if ins.mnemonic == "ret":
                        break
                for t in jumps:
                    for ins in md.disasm(d[t:t + 0x20], t):
                        if ins.mnemonic in ("jne", "jmp") and ins.op_str.startswith("0x"):
                            ctor = int(ins.op_str, 16)
                            vtable = last_vtable_store(ctor)
                            if vtable:
                                return ctor, size, vtable
                for t in inline:
                    vtable = last_vtable_store(t, 0x100)
                    if vtable:
                        return t, size, vtable
    return None, None, None


def offsets_of(prop):
    out = set()
    for m in re.finditer(b"\x00" + prop.encode() + b"\x00", d):
        ref = struct.pack("<Q", BASE + m.start() + 1)
        for r in re.finditer(re.escape(ref), d):
            out.add(struct.unpack_from("<I", d, r.start() + 36)[0])
    return out




def ctor_values(ctor):
    """{offset: raw 32-bit value} the constructor writes into the object."""
    out = {}
    for ins in md.disasm(d[ctor:ctor + 0x400], ctor):
        m = re.match(r"dword ptr \[r\w+ \+ (0x[0-9a-f]+)\], (0x[0-9a-f]+|\d+)$", ins.op_str)
        if ins.mnemonic == "mov" and m:
            out[int(m.group(1), 16)] = int(m.group(2), 0)
        if ins.mnemonic in ("ret", "int3"):
            break
    return out


if __name__ == "__main__":
    rows = list(csv.DictReader(open(ROOT / "data" / "native_defaults.tsv", encoding="utf-8"), delimiter="\t"))
    defaults = {(r["class"], r["property"]): (r["type"], r["default"]) for r in rows}
    result, problems = {}, []
    for cls, fields in FIELDS.items():
        ctor, size, vtable = class_info(cls)
        if not vtable or not size:
            problems.append(f"{cls}: class not found")
            continue
        entry = {"vtable": hex(vtable), "size": hex(size), "fields": {}}
        for prop, kind in fields.items():
            typ, default = defaults.get((cls, prop), (None, None))
            inside = sorted(o for o in (offsets_of(prop) | offsets_of(prop[0].lower() + prop[1:])) if ITEM_INSTANCE_SIZE <= o < size)
            if len(inside) > 1 and typ:                 # several classes use the name: the constructor's value decides
                want = struct.unpack("<I", struct.pack("<f", float(default)))[0] if typ == "FloatProperty" else int(float(default))
                written = ctor_values(ctor)
                inside = [o for o in inside if written.get(o) == want]
            if typ not in ("FloatProperty", "IntProperty") or len(inside) != 1:
                problems.append(f"{cls}.{prop}: type {typ}, offsets in the class {[hex(o) for o in inside]}")
                continue
            entry["fields"][prop] = {"offset": hex(inside[0]), "type": "float" if typ == "FloatProperty" else "int",
                                     "kind": kind, "default": float(default)}
        result[cls] = entry
        print(cls, entry["vtable"], entry["size"],
              {p: (f["offset"], f["type"], f["default"]) for p, f in entry["fields"].items()})
    (ROOT / "tools" / "artifact_fields.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
    print("\n".join(["PROBLEMS:"] + problems) if problems else "no problems")
