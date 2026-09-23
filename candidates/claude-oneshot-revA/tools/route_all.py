"""End-to-end routing pipeline after tools/build_pcb.py placement. Every stage runs in its own
KiCad-Python process (pcbnew proxies degrade after bulk edits in one session).

    "C:/Program Files/KiCad/10.0/bin/python.exe" tools/route_all.py [--passes 40]
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = sys.executable
passes = sys.argv[sys.argv.index("--passes") + 1] if "--passes" in sys.argv else "40"


def run(code_or_args, label):
    args = [PY, "-c", code_or_args] if not isinstance(code_or_args, list) else [PY] + code_or_args
    r = subprocess.run(args, capture_output=True, text=True, cwd=str(HERE.parent))
    out = "\n".join(l for l in (r.stdout + r.stderr).splitlines()
                    if l and "PROPERTY" not in l and "swig" not in l.lower() and "image handler" not in l)
    print(f"== {label}\n{out}", flush=True)


run(f"import sys; sys.path.insert(0, 'tools'); import build_pcb as B; B.do_route({passes}, 7200)", "freerouting")
run(["tools/finalize.py"], "finalize (pours, GND pad + grid stitching, fiducials)")
run(["tools/gridroute.py"], "grid router (standard rules)")
run(["tools/refill.py"], "refill")
run(["tools/gridroute.py", "--gnd", "--tight"], "GND fragment stitch routes")
run(["tools/gridroute.py", "--tight"], "grid router (minimum rules)")
run(["tools/refill.py"], "refill")
run(["tools/polish.py"], "polish (neck-downs, dangling vias, fiducials)")
run(["tools/refill.py"], "refill")
run("import sys; sys.path.insert(0, 'tools'); import export; export.drc()", "DRC")
