"""Smoke test for the editor's Python: report the engine and which graph/blueprint helpers 4.22 offers."""
import os
import unreal

names = [n for n in dir(unreal) if any(k in n for k in ("Blueprint", "Widget", "Kismet", "Graph", "Level", "Factory"))]
with open(os.path.join(os.path.dirname(__file__), "hello_out.txt"), "w") as f:
    f.write("engine " + unreal.SystemLibrary.get_engine_version() + "\n")
    f.write("\n".join(sorted(names)))
