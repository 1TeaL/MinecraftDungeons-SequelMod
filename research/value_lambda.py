"""For enchantment classes: class vtable, the 'value for this tier' function and its code (exe dump).
    python research/value_lambda.py RapidFire HealthSynergy ..."""
import re, struct, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import artifact_fields as af
d, md, BASE = af.d, af.md, af.BASE
for name in sys.argv[1:]:
    ctor, size, vt = af.class_info(name)
    if not ctor:
        print(name, "not found"); continue
    print(f"== {name}: ctor exe+0x{ctor:X}, class vtable 0x{vt:X}")
    for ins in md.disasm(d[ctor:ctor + 0x300], ctor):
        if ins.mnemonic == "lea" and "rip" in ins.op_str:
            t = af.rip_target(ins)
            if 0x3000000 < t < len(d) - 48:
                q = [struct.unpack_from("<Q", d, t + 8 * k)[0] - BASE for k in range(3)]
                if all(0 < x < 0x3000000 for x in q):
                    body = []
                    for b in md.disasm(d[q[2]:q[2] + 0x60], q[2]):
                        extra = ""
                        if "rip" in b.op_str and "ss" in b.mnemonic:
                            extra = f"  ; {struct.unpack_from('<f', d, af.rip_target(b))[0]:g}"
                        body.append(f"{b.mnemonic} {b.op_str}{extra}")
                        if b.mnemonic in ("ret", "jmp", "int3"): break
                    if len(body) <= 10 and any("xmm0" in x for x in body):
                        print(f"   value function vtable 0x{t:X}:", " | ".join(body))
        if ins.mnemonic in ("ret", "int3"): break
