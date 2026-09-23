"""Post-route polish: widen autorouter neck-downs below the class width when that creates no
clearance problem, delete dangling vias, and re-seat fiducials on a spot with >= 1 mm clear
copper and no courtyard overlap.

    "C:/Program Files/KiCad/10.0/bin/python.exe" tools/polish.py
"""
import json
import math
import subprocess
import sys
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_pcb as B  # noqa: E402

mm = pcbnew.FromMM
rep = B.OUT / "reports" / "drc_polish.json"
subprocess.run([B.CLI, "pcb", "drc", "--format", "json", "-o", str(rep), str(B.BOARD)], capture_output=True, text=True)
d = json.loads(rep.read_text(encoding="utf-8"))
rep.unlink()
b = pcbnew.LoadBoard(str(B.BOARD))
tracks = list(b.GetTracks())
items = tracks + [p for f in b.GetFootprints() for p in f.Pads()]

widened = removed = 0
for x in d["violations"]:
    pos = x["items"][0]["pos"]
    if x["type"] == "track_width":
        for t in tracks:
            if t.Type() == pcbnew.PCB_VIA_T or t.GetWidth() >= mm(0.149):
                continue
            s, e = t.GetStart(), t.GetEnd()
            if min(math.hypot(s.x / 1e6 - pos["x"], s.y / 1e6 - pos["y"]),
                   math.hypot((s.x + e.x) / 2e6 - pos["x"], (s.y + e.y) / 2e6 - pos["y"])) > 0.06:
                continue
            old = t.GetWidth()
            t.SetWidth(mm(0.15))
            bad = any(o.GetNetCode() != t.GetNetCode() and o.IsOnLayer(t.GetLayer()) and
                      o.GetEffectiveShape(t.GetLayer()).Collide(t.GetEffectiveShape(t.GetLayer()), mm(0.127))
                      for o in items if o.GetBoundingBox().Intersects(t.GetBoundingBox()))
            if bad:
                t.SetWidth(old)
            else:
                widened += 1
    if x["type"] == "via_dangling":
        for t in tracks:
            if t.Type() == pcbnew.PCB_VIA_T and math.hypot(t.GetPosition().x / 1e6 - pos["x"], t.GetPosition().y / 1e6 - pos["y"]) < 0.02:
                b.Remove(t)
                removed += 1
                break

fcu = [t for t in tracks if t.IsOnLayer(pcbnew.F_Cu)]
for ref in ("FID1", "FID2", "FID3"):
    f = b.FindFootprintByReference(ref)
    if f is None:
        continue
    pad = list(f.Pads())[0]
    others = [g for g in b.GetFootprints() if g.GetReference() != ref]
    pads = [p for g in others for p in g.Pads() if p.IsOnLayer(pcbnew.F_Cu)]
    crts = []
    for g in others:
        g.BuildCourtyardCaches()
        bb = g.GetCourtyard(pcbnew.F_CrtYd).BBox()
        if bb.GetWidth() > 0 and g.GetReference() != "U1":
            crts.append(bb)
    c0 = f.GetPosition()
    found = None
    for r in [0.0] + [0.5 * k for k in range(1, 40)]:
        for k in range(1 if r == 0 else 24):
            a = 2 * math.pi * k / 24
            pos = pcbnew.VECTOR2I(int(c0.x + mm(r) * math.cos(a)), int(c0.y + mm(r) * math.sin(a)))
            if not (mm(2.5) < pos.x < mm(B.W - 2.5) and mm(2.5) < pos.y < mm(B.H - 2.5)):
                continue
            f.SetPosition(pos)
            f.BuildCourtyardCaches()
            cb = f.GetCourtyard(pcbnew.F_CrtYd).BBox()
            if any(cb.Intersects(c) for c in crts):
                continue
            sh = pad.GetEffectiveShape(pcbnew.F_Cu)
            if any(o.GetEffectiveShape(pcbnew.F_Cu).Collide(sh, mm(1.0)) for o in fcu + pads):
                continue
            found = pos
            break
        if found:
            break
    f.SetPosition(found or c0)
    print(ref, "->", (round(found.x / 1e6, 2), round(found.y / 1e6, 2)) if found else "unchanged")
pcbnew.SaveBoard(str(B.BOARD), b)
print("neck-downs widened:", widened, "dangling vias removed:", removed)
