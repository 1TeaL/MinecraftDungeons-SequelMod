"""Dev tool: run a Lua snippet through the SequelProbe UE4SS mod and print its [PROBE] output.

    python tools/probe.py "<lua code>"        e.g.  python tools/probe.py "out(rec(25))"
    python tools/probe.py --file snippet.lua

Needs the game running with UE4SS injected (inject_ue4ss.py) and SequelProbe enabled. Helpers inside
the snippet: out(text), rec(level), conf(level) - see the mod's main.lua.
"""
import sys
import time
from pathlib import Path

UE4SS = Path(__file__).resolve().parents[3] / "Dungeons" / "Binaries" / "Win64" / "ue4ss"
REQUEST = UE4SS / "Mods" / "SequelProbe" / "request.lua"
LOG = UE4SS / "UE4SS.log"

if __name__ == "__main__":
    code = Path(sys.argv[2]).read_text() if sys.argv[1] == "--file" else sys.argv[1]
    start = LOG.stat().st_size if LOG.exists() else 0
    REQUEST.write_text(code)
    for _ in range(60):
        time.sleep(0.5)
        new = LOG.read_bytes()[start:].decode("utf-8", "replace")
        if "[PROBE] request done" in new:
            for line in new.splitlines():
                if "[PROBE]" in line and "request done" not in line:
                    print(line.split("[PROBE] ", 1)[1])
            sys.exit(0)
    sys.exit("no answer from the probe (is the game running with UE4SS injected?)")
