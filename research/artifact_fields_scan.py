"""Candidates: every artifact blueprint -> native class -> its damage/heal-looking properties (name, type, default)."""
import csv, glob, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import sequel
rows = list(csv.DictReader(open(sequel.ROOT / "data" / "native_defaults.tsv", encoding="utf-8"), delimiter="\t"))
by_class = {}
for r in rows:
    by_class.setdefault(r["class"], []).append(r)
SKIP = {"ItemInstance", "Actor", "GearItemInstance"}
seen = {}
for f in sorted(glob.glob(str(sequel.EXTRACT / "Dungeons/Content/**/Items/**/*Instance.uasset"), recursive=True)):
    try:
        pkg, _ = sequel.scan_asset(Path(f))
        bp, native = sequel.native_parent(pkg)[:2]
    except Exception as e:
        continue
    props = [r for r in by_class.get(native, []) if r["declared_in"] not in SKIP]
    if native in seen or not props:
        seen.setdefault(native, []).append(bp); continue
    seen[native] = [bp]
    print(f"{native}  <- {bp}")
    for r in props:
        mark = "*" if re.search(r"damage|heal|dps|explo|multiplier|amount|strength|power", r["property"], re.I) else " "
        print(f"   {mark} {r['property']:42} {r['type']:14} {r['default'][:12]:12} {r['declared_in']}")
