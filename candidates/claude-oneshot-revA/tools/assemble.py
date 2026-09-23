"""Combine the KiCad board STEP (with display envelope and 2S holder models) and the printed
enclosure concept into one assembly STEP, and write orthographic SVG views.

    <venv-with-cadquery>/python tools/assemble.py
Requires outputs/StratosCore_Claude_board.step (made by tools/export.py).
"""
from __future__ import annotations

from pathlib import Path

import cadquery as cq

ROOT = Path(__file__).resolve().parent.parent
OUTD = ROOT / "outputs"
board = cq.importers.importStep(str(OUTD / "StratosCore_Claude_board.step"))
front = cq.importers.importStep(str(ROOT / "mech" / "Enclosure_Front_Bezel.step"))
back = cq.importers.importStep(str(ROOT / "mech" / "Enclosure_Back_Shell.step"))
# KiCad STEP exported with --user-origin 0x0: board spans x 0..60, y 0..-84, top copper at z=1.6
loc = cq.Location(cq.Vector(30.0, -42.0, 1.6))
asm = (cq.Assembly(name="StratosCore_RevA_Claude_oneshot")
       .add(board, name="pcba_display_cells")
       .add(front, name="front_bezel", loc=loc, color=cq.Color(0.2, 0.22, 0.25, 0.55))
       .add(back, name="back_shell", loc=loc, color=cq.Color(0.2, 0.22, 0.25, 0.55)))
asm.save(str(OUTD / "StratosCore_Claude_full_assembly.step"))
print("assembly written")
comp = asm.toCompound()
for name, d in (("iso", (1, -1, 1)), ("front", (0, 0, 1)), ("side", (1, 0, 0))):
    cq.exporters.export(cq.Workplane("XY").add(comp), str(OUTD / f"assembly_{name}.svg"),
                        opt={"projectionDir": d, "showHidden": False, "width": 900, "height": 900,
                             "strokeWidth": 0.15})
for svg in OUTD.glob("assembly_*.svg"):
    svg.write_text("\n".join(l.rstrip() for l in svg.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
print("svg views written")
