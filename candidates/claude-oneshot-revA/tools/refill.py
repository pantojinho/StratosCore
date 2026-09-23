"""Refill all pours, stitch isolated GND fragments and re-seat fiducials.

pcbnew SWIG proxies degrade after BOARD.Remove() in the same session (KiCad 10.0.6), so the
zone re-creation and the later edits run in separate processes.

    "C:/Program Files/KiCad/10.0/bin/python.exe" tools/refill.py
"""
import subprocess
import sys
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_pcb as B  # noqa: E402

if len(sys.argv) == 1:
    py = sys.executable
    for stage in ("zones", "stitch", "fill"):
        r = subprocess.run([py, str(Path(__file__)), stage], capture_output=True, text=True)
        print("\n".join(l for l in (r.stdout + r.stderr).splitlines()
                        if l and "PROPERTY" not in l and "swig" not in l.lower() and "image handler" not in l))
    sys.exit(0)

import finalize as F  # noqa: E402

board = pcbnew.LoadBoard(str(B.BOARD))
stage = sys.argv[1]
if stage == "zones":
    B.add_zones(board)
elif stage == "stitch":
    print("fragment vias", F.fragment_stitch(board))
    F.relocate_fiducials(board)
elif stage == "fill":
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(str(B.BOARD), board)
print("stage", stage, "saved")
