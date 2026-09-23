"""Close short open connections (DRC 'unconnected' pairs) with a straight or single-bend track on
the pad layer when KiCad's shape engine shows >= 0.127 mm to foreign copper and the board edge.

    "C:/Program Files/KiCad/10.0/bin/python.exe" tools/direct_connect.py
"""
import json
import math
import re
import subprocess
import sys
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_pcb as B  # noqa: E402

mm = pcbnew.FromMM
rep = B.OUT / "reports" / "drc_direct.json"
subprocess.run([B.CLI, "pcb", "drc", "--format", "json", "-o", str(rep), str(B.BOARD)], capture_output=True, text=True)
unc = json.loads(rep.read_text(encoding="utf-8"))["unconnected_items"]
rep.unlink()
b = pcbnew.LoadBoard(str(B.BOARD))
edges = [d for d in b.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts]
items = list(b.GetTracks()) + [p for f in b.GetFootprints() for p in f.Pads()]


def endpoints(desc, pos):
    m = re.search(r"Ilha (\S+) \[([^\]]+)\] de (\S+) no ([\w.]+)", desc)
    if m:
        num, net, ref, lay = m.groups()
        for p in b.FindFootprintByReference(ref).Pads():
            if p.GetNumber() == num:
                return net, [p.GetPosition()], b.GetLayerID(lay)
    m = re.search(r"Trilha \[([^\]]+)\] no ([\w.]+)", desc)
    if m:
        net, lay = m.groups()
        L = b.GetLayerID(lay)
        pts = []
        for t in b.GetTracks():
            if t.Type() != pcbnew.PCB_VIA_T and t.GetNetname() == net and t.GetLayer() == L:
                for q in (t.GetStart(), t.GetEnd()):
                    if math.hypot(q.x / 1e6 - pos[0], q.y / 1e6 - pos[1]) < 3.0:
                        pts.append(q)
        return net, pts, L
    return None, [], None


def clear(t, netcode):
    lay = t.GetLayer()
    sh = t.GetEffectiveShape(lay)
    bb = t.GetBoundingBox()
    bb.Inflate(mm(0.5))
    for o in items:
        if o.GetNetCode() == netcode or not o.IsOnLayer(lay) or not o.GetBoundingBox().Intersects(bb):
            continue
        if o.GetEffectiveShape(lay).Collide(sh, mm(0.127)):
            return False
    for e in edges:
        if e.GetEffectiveShape().Collide(sh, mm(0.25)):
            return False
    for z in b.Zones():
        if z.GetIsRuleArea() and z.GetDoNotAllowTracks() and z.IsOnLayer(lay) and z.Outline().Collide(sh):
            return False
    return True


added = 0
for u in unc:
    a, c = u["items"][:2]
    if a["description"].startswith("Zona") or c["description"].startswith("Zona"):
        continue
    na, pa, la = endpoints(a["description"], (a["pos"]["x"], a["pos"]["y"]))
    nc, pc, lc = endpoints(c["description"], (c["pos"]["x"], c["pos"]["y"]))
    if not pa or not pc or na != nc or la != lc:
        print("skip", a["description"][:40], "|", c["description"][:40])
        continue
    net = b.FindNet(na)
    done = False
    width = 0.15 if "LORA" not in na else 0.15
    for p in pa:
        for q in sorted(pc, key=lambda q: math.hypot(q.x - p.x, q.y - p.y)):
            if math.hypot(q.x - p.x, q.y - p.y) > mm(4):
                continue
            # straight, then two 45/90-degree bends
            dx, dy = q.x - p.x, q.y - p.y
            k = min(abs(dx), abs(dy))
            mids = [None,
                    pcbnew.VECTOR2I(p.x + int(math.copysign(k, dx)), p.y + int(math.copysign(k, dy))),
                    pcbnew.VECTOR2I(q.x - int(math.copysign(k, dx)), q.y - int(math.copysign(k, dy))),
                    pcbnew.VECTOR2I(p.x, q.y), pcbnew.VECTOR2I(q.x, p.y)]
            for mid in mids:
                pts = [p, q] if mid is None else [p, mid, q]
                segs = []
                for s, e in zip(pts, pts[1:]):
                    if s == e:
                        continue
                    t = pcbnew.PCB_TRACK(b)
                    t.SetStart(s)
                    t.SetEnd(e)
                    t.SetWidth(mm(width))
                    t.SetLayer(la)
                    t.SetNet(net)
                    segs.append(t)
                if segs and all(clear(t, net.GetNetCode()) for t in segs):
                    for t in segs:
                        b.Add(t)
                        items.append(t)
                    done = True
                    break
            if done:
                break
        if done:
            break
    print("direct" if done else "no direct path", na, a["description"][:40], "->", c["description"][:40])
    added += done
pcbnew.SaveBoard(str(B.BOARD), b)
print("direct connections added:", added)
