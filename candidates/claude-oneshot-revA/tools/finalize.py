"""Post-route clean-up: reviewed mask-bridge exceptions, copper pours, GND via stitching for pads
the autorouter left on the plane net, zone refill. Every added via is checked against copper of
other nets on all layers before it is committed.

    "C:/Program Files/KiCad/10.0/bin/python.exe" tools/finalize.py
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_pcb as B  # noqa: E402

mm = pcbnew.FromMM
CU = [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]


def unconnected(board_path):
    rep = B.OUT / "reports" / "drc_tmp.json"
    subprocess.run([B.CLI, "pcb", "drc", "--format", "json", "-o", str(rep), str(board_path)],
                   capture_output=True, text=True)
    return json.loads(rep.read_text(encoding="utf-8")).get("unconnected_items", [])


def _rule_areas(board):
    zs = [z for z in board.Zones() if z.GetIsRuleArea()]
    for f in board.GetFootprints():
        zs += [z for z in f.Zones() if z.GetIsRuleArea()]
    return zs


def via_ok(board, pos, net, clearance=0.2, size=0.45, drill=0.2, rule_areas=()):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pos)
    v.SetWidth(mm(size))
    v.SetDrill(mm(drill))
    v.SetNet(net)
    x, y = pos.x / 1e6, pos.y / 1e6
    if x < 0.9 or y < 0.9 or x > B.W - 0.9 or y > B.H - 0.9:
        return None
    for (x0, y0, x1, y1) in B.KEEPOUT[:2]:
        if x0 - 0.5 <= x <= x1 + 0.5 and y0 <= y <= y1 + 0.5:
            return None
    for z in rule_areas:
        if z.Outline().Contains(pos) or z.Outline().Collide(pos, mm(0.4)):
            return None
    cl = mm(clearance)
    win = pcbnew.BOX2I(pcbnew.VECTOR2I(pos.x - mm(1), pos.y - mm(1)), pcbnew.VECTOR2I(mm(2), mm(2)))
    for it in list(board.GetTracks()) + [p for f in board.GetFootprints() for p in f.Pads()]:
        if not it.GetBoundingBox().Intersects(win):
            continue
        if it.Type() == pcbnew.PCB_VIA_T or (it.Type() == pcbnew.PCB_PAD_T and it.GetDrillSize().x > 0):
            d = math.hypot((it.GetPosition().x - pos.x) / 1e6, (it.GetPosition().y - pos.y) / 1e6)
            if d < 0.6:
                return None
        same = it.GetNetCode() == net.GetNetCode()
        for layer in CU:
            if not it.IsOnLayer(layer):
                continue
            if same and it.Type() != pcbnew.PCB_PAD_T:
                continue
            if it.GetEffectiveShape(layer).Collide(v.GetEffectiveShape(layer), 0 if same else cl):
                if same:
                    continue   # touching our own copper is fine except drilling through a pad (below)
                return None
        if it.Type() == pcbnew.PCB_PAD_T and it.GetEffectiveShape(pcbnew.F_Cu if not it.IsOnLayer(pcbnew.B_Cu) else pcbnew.B_Cu).Collide(
                v.GetEffectiveShape(pcbnew.F_Cu), 0):
            return None
    return v


def stitch_gnd(board):
    gnd = board.FindNet("GND")
    areas = _rule_areas(board)
    added = 0
    for f in board.GetFootprints():
        if f.GetReference() in ("U1", "BT1"):
            continue
        for p in f.Pads():
            if p.GetNetCode() != gnd.GetNetCode() or p.GetAttribute() != pcbnew.PAD_ATTRIB_SMD:
                continue
            layer = pcbnew.B_Cu if f.IsFlipped() else pcbnew.F_Cu
            c = p.GetPosition()
            # already has a via on/near the pad?
            near = [t for t in board.GetTracks() if t.Type() == pcbnew.PCB_VIA_T and t.GetNetCode() == gnd.GetNetCode()
                    and math.hypot((t.GetPosition().x - c.x) / 1e6, (t.GetPosition().y - c.y) / 1e6) < 1.0]
            if near:
                continue
            placed = False
            for r in (0.55, 0.75, 0.95, 1.2):
                for k in range(12):
                    a = 2 * math.pi * k / 12
                    pos = pcbnew.VECTOR2I(int(c.x + mm(r) * math.cos(a)), int(c.y + mm(r) * math.sin(a)))
                    v = via_ok(board, pos, gnd, rule_areas=areas)
                    if v is None:
                        continue
                    t = pcbnew.PCB_TRACK(board)
                    t.SetStart(c)
                    t.SetEnd(pos)
                    t.SetWidth(mm(0.25))
                    t.SetLayer(layer)
                    t.SetNet(gnd)
                    # track must also be clear of other nets
                    bad = False
                    tb = t.GetBoundingBox()
                    for it in list(board.GetTracks()) + [q for g in board.GetFootprints() for q in g.Pads()]:
                        if not it.GetBoundingBox().Intersects(tb):
                            continue
                        if it.GetNetCode() == gnd.GetNetCode() or not it.IsOnLayer(layer):
                            continue
                        if it.GetEffectiveShape(layer).Collide(t.GetEffectiveShape(layer), mm(0.15)):
                            bad = True
                            break
                    if bad:
                        continue
                    board.Add(v)
                    board.Add(t)
                    added += 1
                    placed = True
                    break
                if placed:
                    break
    return added


def reroute(passes=12, timeout=3600):
    """Incremental Freerouting pass: existing wiring is kept in the DSN, only open connections are routed."""
    board = pcbnew.LoadBoard(str(B.BOARD))
    for z in list(board.Zones()):
        if not z.GetIsRuleArea() and z.GetLayer() != pcbnew.In1_Cu:
            board.Remove(z)
        elif z.GetIsRuleArea() and z.GetZoneName() == "BMP581 no copper under body":
            board.Remove(z)
    B.rule_area(board, [(48.05, 1.55), (49.15, 1.55), (49.15, 2.65), (48.05, 2.65)],
                [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu], "BMP581 no copper under body")
    pcbnew.SaveBoard(str(B.BOARD), board)
    dsn, ses = B.OUT / "route" / "board2.dsn", B.OUT / "route" / "board2.ses"
    pcbnew.ExportSpecctraDSN(board, str(dsn))
    r = subprocess.run([str(B.JAVA), "-jar", str(B.FREEROUTING), "-de", str(dsn), "-do", str(ses), "-mp", str(passes),
                        "-mt", "8", "--gui.enabled=false"], capture_output=True, text=True, timeout=timeout)
    (B.OUT / "route" / "freerouting2.log").write_text((r.stdout or "") + (r.stderr or ""), encoding="utf-8")
    if ses.exists():
        board = pcbnew.LoadBoard(str(B.BOARD))
        pcbnew.ImportSpecctraSES(board, str(ses))
        pcbnew.SaveBoard(str(B.BOARD), board)
        print("reroute imported", len(board.GetTracks()))


def grid_stitch(board, pitch=2.5):
    """Tie the outer GND pours to the In1 plane on a grid wherever F.Cu AND B.Cu GND copper
    exist and a via fits (joins pour fragments the autorouter isolated)."""
    gnd = board.FindNet("GND")
    areas = _rule_areas(board)
    zf = [z for z in board.Zones() if not z.GetIsRuleArea() and z.GetNetname() == "GND" and z.GetLayer() == pcbnew.F_Cu]
    zb = [z for z in board.Zones() if not z.GetIsRuleArea() and z.GetNetname() == "GND" and z.GetLayer() == pcbnew.B_Cu]
    added = 0
    y = 1.5
    while y < B.H - 1.0:
        x = 1.5
        while x < B.W - 1.0:
            pos = pcbnew.VECTOR2I(mm(x), mm(y))
            onf = any(z.HitTestFilledArea(pcbnew.F_Cu, pos, mm(0.35)) for z in zf)
            onb = any(z.HitTestFilledArea(pcbnew.B_Cu, pos, mm(0.35)) for z in zb)
            if onf or onb:
                v = via_ok(board, pos, gnd, clearance=0.25, rule_areas=areas)
                if v is not None:
                    board.Add(v)
                    added += 1
            x += pitch
        y += pitch
    return added


def fragment_stitch(board):
    """Every filled GND fragment on F/In2/B without a GND via gets one (fine grid search)."""
    gnd = board.FindNet("GND")
    areas = _rule_areas(board)
    vias = [t.GetPosition() for t in board.GetTracks() if t.Type() == pcbnew.PCB_VIA_T and t.GetNetCode() == gnd.GetNetCode()]
    thru = [p.GetPosition() for f in board.GetFootprints() for p in f.Pads()
            if p.GetNetCode() == gnd.GetNetCode() and p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH]
    added = 0
    for z in list(board.Zones()):
        if z.GetIsRuleArea() or z.GetNetname() != "GND" or z.GetLayer() == pcbnew.In1_Cu:
            continue
        layer = z.GetLayer()
        polys = z.GetFilledPolysList(layer)
        for i in range(polys.OutlineCount()):
            ol = polys.Outline(i)
            if any(ol.PointInside(v) for v in vias + thru):
                continue
            bb = ol.BBox()
            step = mm(0.25)
            done = False
            y = bb.GetTop()
            while y <= bb.GetBottom() and not done:
                x = bb.GetLeft()
                while x <= bb.GetRight():
                    pos = pcbnew.VECTOR2I(x, y)
                    if ol.PointInside(pos) and ol.SquaredDistance(pos) > mm(0.25) ** 2:
                        v = via_ok(board, pos, gnd, clearance=0.2, rule_areas=areas)
                        if v is not None:
                            board.Add(v)
                            vias.append(pos)
                            added += 1
                            done = True
                            break
                    x += step
                y += step
    return added


def relocate_fiducials(board):
    """Put each fiducial on the nearest spot with >= 1.0 mm clear copper around its 1 mm pad."""
    items = [t for t in board.GetTracks() if t.IsOnLayer(pcbnew.F_Cu)]
    for ref in ("FID1", "FID2", "FID3"):
        f = board.FindFootprintByReference(ref)
        if f is None:
            continue
        others = items + [p for g in board.GetFootprints() if g.GetReference() != ref for p in g.Pads() if p.IsOnLayer(pcbnew.F_Cu)]
        pad = list(f.Pads())[0]
        c0 = f.GetPosition()
        best = None
        for r in [0.0] + [0.5 * k for k in range(1, 30)]:
            for k in range(1 if r == 0 else 24):
                a = 2 * math.pi * k / 24
                pos = pcbnew.VECTOR2I(int(c0.x + mm(r) * math.cos(a)), int(c0.y + mm(r) * math.sin(a)))
                if not (mm(2) < pos.x < mm(B.W - 2) and mm(2) < pos.y < mm(B.H - 2)):
                    continue
                f.SetPosition(pos)
                sh = pad.GetEffectiveShape(pcbnew.F_Cu)
                if not any(o.GetEffectiveShape(pcbnew.F_Cu).Collide(sh, mm(1.0)) for o in others):
                    best = pos
                    break
            if best is not None:
                break
        f.SetPosition(best if best is not None else c0)


def main():
    if "--reroute" in sys.argv:
        reroute()
    board = pcbnew.LoadBoard(str(B.BOARD))
    for ref in ("U30", "U32"):
        f = board.FindFootprintByReference(ref)
        if f:
            f.SetAllowSolderMaskBridges(True)   # vendor mask strategy (open mask area) - reviewed exception
    B.add_zones(board)
    relocate_fiducials(board)
    n = stitch_gnd(board)
    print("GND pad vias added:", n)
    B.add_zones(board)
    n = grid_stitch(board)
    print("GND grid stitching vias added:", n)
    B.add_zones(board)
    for _ in range(2):
        n = fragment_stitch(board)
        print("GND fragment vias added:", n)
        B.add_zones(board)
    pcbnew.SaveBoard(str(B.BOARD), board)


if __name__ == "__main__":
    main()
