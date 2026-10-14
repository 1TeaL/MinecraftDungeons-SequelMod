"""List editable numbers in each artifact's blueprints/effects (read-only) -> tools/artifact_values.json.

    python tools/artifact_values.py
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sequel import EXTRACT, scan_asset  # noqa: E402

CONTENT = EXTRACT / "Dungeons" / "Content"
SKIP = re.compile(r"^(MI_|M_|T_|SM_|SK_|P_|A_|AM_|Mat|PS_|NS_|sfx|S_|Cue|ABP_|PA_|BS_|L_|MF_|Default)", re.I)
NOISE = re.compile(r"Sound|Color|Scale|Offset|Visual|Mesh|Material|Light|Particle|Camera|Bloom|Fade|Emissive|Rotation|"
                   r"Anim|Montage|Audio|UI|Icon|Debug|Tick|bReplicat|Net|Priority|Spawn.*Index|Z$|Pitch|Yaw|Roll\b", re.I)

ids = {}
for f in CONTENT.rglob("BP_*Instance.uasset"):
    if "Items" not in f.parts or "Equipment" in f.parts:
        continue
    ids.setdefault(f.parent, f)
out = {}
for folder, inst in sorted(ids.items()):
    vals = []
    for f in sorted(folder.glob("*.uasset")):
        if SKIP.match(f.stem):
            continue
        try:
            _, fields = scan_asset(f)
        except Exception:  # noqa: BLE001
            continue
        for path, t, v, _ in fields:
            if t in ("float", "int") and not NOISE.search(path) and v not in (0, 0.0):
                vals.append(f"{f.stem.replace('BP_', '')}.{path} = {round(v, 3) if isinstance(v, float) else v}")
    out[folder.name] = vals
Path(__file__).with_name("artifact_values.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
print(len(out), "artifact folders;", sum(1 for v in out.values() if v), "with values")
