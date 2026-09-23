"""Small A* grid router used to close the connections Freerouting left open.

Routes on F.Cu / In2.Cu / B.Cu (In1.Cu is the GND plane), 0.1 mm grid, 0.15 mm tracks,
0.45/0.2 mm vias, >= 0.2 mm clearance to foreign copper (conservative rasterisation). Every
path is committed only if the new copper does not collide with foreign copper according to
KiCad's own shape engine. Run after tools/finalize.py:

    "C:/Program Files/KiCad/10.0/bin/python.exe" tools/gridroute.py
"""
from __future__ import annotations

import heapq
import json
import math
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pcbnew

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_pcb as B  # noqa: E402
import finalize as FZ  # noqa: E402

mm = pcbnew.FromMM
RES = 0.05 if "--fine" in sys.argv else 0.1
NX, NY = int(B.W / RES), int(B.H / RES)
LAYERS = [pcbnew.F_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]
TW, VD, CLR = 0.15, 0.45, 0.2
if "--tight" in sys.argv:          # second pass: Default-class minimums (0.127 mm) and 0.4/0.2 vias
    TW, VD, CLR = 0.127, 0.40, 0.13
INF_T = CLR + TW / 2 + 0.05
INF_V = CLR + VD / 2 + 0.05
KEEP = -1
MULTI = -2


class Grid:
    def __init__(self):
        self.t = [np.zeros((NY, NX), np.int32) for _ in LAYERS]   # track-blocking occupancy
        self.v = [np.zeros((NY, NX), np.int32) for _ in LAYERS]   # via-blocking occupancy
        ys = (np.arange(NY) + 0.5) * RES
        xs = (np.arange(NX) + 0.5) * RES
        self.X, self.Y = np.meshgrid(xs, ys)

    def _mark(self, arr, mask, net):
        cur = arr[mask]
        new = np.where(cur == 0, net, np.where((cur == net) | (cur == KEEP), cur, MULTI))
        if net == KEEP:
            new = np.full_like(cur, KEEP)
        arr[mask] = new

    def _window(self, x0, y0, x1, y1):
        i0, i1 = max(0, int(x0 / RES) - 1), min(NX, int(x1 / RES) + 2)
        j0, j1 = max(0, int(y0 / RES) - 1), min(NY, int(y1 / RES) + 2)
        return i0, i1, j0, j1

    def segment(self, li, x1, y1, x2, y2, w, net):
        for arr, inf in ((self.t[li], INF_T), (self.v[li], INF_V)):
            r = w / 2 + inf
            i0, i1, j0, j1 = self._window(min(x1, x2) - r, min(y1, y2) - r, max(x1, x2) + r, max(y1, y2) + r)
            X, Y = self.X[j0:j1, i0:i1], self.Y[j0:j1, i0:i1]
            dx, dy = x2 - x1, y2 - y1
            L2 = dx * dx + dy * dy
            if L2 == 0:
                d = np.hypot(X - x1, Y - y1)
            else:
                t = np.clip(((X - x1) * dx + (Y - y1) * dy) / L2, 0, 1)
                d = np.hypot(X - (x1 + t * dx), Y - (y1 + t * dy))
            sub = arr[j0:j1, i0:i1]
            self._mark(sub, d <= r, net)

    def rect(self, li, x0, y0, x1, y1, net, inflate=True, extra=0.0):
        for arr, inf in ((self.t[li], INF_T), (self.v[li], INF_V)):
            e = inf if inflate else extra
            i0, i1, j0, j1 = self._window(x0 - e, y0 - e, x1 + e, y1 + e)
            X, Y = self.X[j0:j1, i0:i1], self.Y[j0:j1, i0:i1]
            dx = np.maximum(np.maximum(x0 - X, X - x1), 0)
            dy = np.maximum(np.maximum(y0 - Y, Y - y1), 0)
            self._mark(arr[j0:j1, i0:i1], np.hypot(dx, dy) <= e, net)

    def blocked_t(self, li, net):
        a = self.t[li]
        return (a == KEEP) | (a == MULTI) | ((a > 0) & (a != net))

    def blocked_v(self, net):
        m = np.zeros((NY, NX), bool)
        for a in self.v:
            m |= (a == KEEP) | (a == MULTI) | ((a > 0) & (a != net))
        return m


def build_grid(board):
    g = Grid()
    for t in board.GetTracks():
        net = t.GetNetCode()
        if t.Type() == pcbnew.PCB_VIA_T:
            p = t.GetPosition()
            for li in range(3):
                g.segment(li, p.x / 1e6, p.y / 1e6, p.x / 1e6, p.y / 1e6, t.GetWidth(pcbnew.F_Cu) / 1e6, net)
        else:
            if t.GetLayer() not in LAYERS:
                continue
            li = LAYERS.index(t.GetLayer())
            s, e = t.GetStart(), t.GetEnd()
            g.segment(li, s.x / 1e6, s.y / 1e6, e.x / 1e6, e.y / 1e6, t.GetWidth() / 1e6, net)
    for f in board.GetFootprints():
        for p in f.Pads():
            bb = p.GetBoundingBox()
            net = p.GetNetCode() or KEEP
            for li, layer in enumerate(LAYERS):
                if p.IsOnLayer(layer) or (p.GetDrillSize().x > 0):
                    g.rect(li, bb.GetLeft() / 1e6, bb.GetTop() / 1e6, bb.GetRight() / 1e6, bb.GetBottom() / 1e6, net)
    # keepouts: board edge band, ESP antenna, SHT40 slots, rule areas
    edge = 0.45
    for li in range(3):
        for arr in (g.t[li], g.v[li]):
            arr[:, : int(edge / RES)] = KEEP
            arr[:, NX - int(edge / RES):] = KEEP
            arr[: int(edge / RES), :] = KEEP
            arr[NY - int(edge / RES):, :] = KEEP
        g.rect(li, *B.KEEPOUT[0], KEEP, inflate=False)
        for (x0, y0, x1, y1) in ((41.8, 0.0, 42.6, 4.4), (45.4, 0.0, 46.2, 4.4)):
            g.rect(li, x0 - 0.5, y0, x1 + 0.5, y1 + 0.5, KEEP, inflate=False)
        # no vias on the SHT40 thermal tab
        kx0, ky0, kx1, ky1 = B.KEEPOUT[1]
        g.v[li][int(ky0 / RES):int((ky1 + 0.6) / RES) + 1, int((kx0 - 0.3) / RES):int((kx1 + 0.3) / RES) + 1] = KEEP
    for z in FZ._rule_areas(board):
        bb = z.GetBoundingBox()
        for li in range(3):
            g.rect(li, bb.GetLeft() / 1e6, bb.GetTop() / 1e6, bb.GetRight() / 1e6, bb.GetBottom() / 1e6, KEEP,
                   inflate=False, extra=TW / 2 + 0.05)
    # rounded corners of the outline (3 mm radius)
    for li in range(3):
        for arr in (g.t[li], g.v[li]):
            for cx, cy in ((3, 3), (B.W - 3, 3), (3, B.H - 3), (B.W - 3, B.H - 3)):
                m = (np.hypot(g.X - cx, g.Y - cy) > 3 - edge) & (np.abs(g.X - cx) < 3.01) & (np.abs(g.Y - cy) < 3.01)
                m &= ((g.X - cx) * np.sign(cx - B.W / 2) > 0) & ((g.Y - cy) * np.sign(cy - B.H / 2) > 0)
                arr[m] = KEEP
    return g


def item_cells(board, desc, pos):
    """Cells (layer, j, i) of the item a DRC 'unconnected' entry names."""
    cells = []
    m = re.search(r"Ilha (\S+) \[([^\]]+)\] de (\S+) no (\S+)", desc)
    if m:
        num, net, ref, lay = m.groups()
        f = board.FindFootprintByReference(ref)
        for p in f.Pads():
            if p.GetNumber() != num:
                continue
            bb = p.GetBoundingBox()
            lis = [li for li, l in enumerate(LAYERS) if p.IsOnLayer(l)] or ([0] if not f.IsFlipped() else [2])
            for li in lis:
                for j in range(int(bb.GetTop() / 1e6 / RES), int(bb.GetBottom() / 1e6 / RES) + 1):
                    for i in range(int(bb.GetLeft() / 1e6 / RES), int(bb.GetRight() / 1e6 / RES) + 1):
                        cells.append((li, j, i))
        return net, cells
    m = re.search(r"(Trilha|Via) \[([^\]]+)\] no ([\w.]+)", desc)
    if m:
        kind, net, lay = m.groups()
        best = None
        for t in board.GetTracks():
            if t.GetNetname() != net:
                continue
            if kind == "Via" and t.Type() == pcbnew.PCB_VIA_T:
                d = math.hypot(t.GetPosition().x / 1e6 - pos[0], t.GetPosition().y / 1e6 - pos[1])
            elif kind == "Trilha" and t.Type() != pcbnew.PCB_VIA_T and t.GetLayerName() == lay:
                s = t.GetStart()
                d = min(math.hypot(s.x / 1e6 - pos[0], s.y / 1e6 - pos[1]),
                        math.hypot(t.GetEnd().x / 1e6 - pos[0], t.GetEnd().y / 1e6 - pos[1]))
            else:
                continue
            if best is None or d < best[0]:
                best = (d, t)
        if best:
            t = best[1]
            if t.Type() == pcbnew.PCB_VIA_T:
                p = t.GetPosition()
                return net, [(li, int(p.y / 1e6 / RES), int(p.x / 1e6 / RES)) for li in range(3)]
            li = LAYERS.index(t.GetLayer())
            s, e = t.GetStart(), t.GetEnd()
            n = max(2, int(math.hypot(e.x - s.x, e.y - s.y) / 1e6 / RES) + 1)
            for k in range(n + 1):
                x = (s.x + (e.x - s.x) * k / n) / 1e6
                y = (s.y + (e.y - s.y) * k / n) / 1e6
                cells.append((li, int(y / RES), int(x / RES)))
        return net, cells
    return None, []


def astar(g, net, starts, goals):
    bt = [g.blocked_t(li, net) for li in range(3)]
    bv = g.blocked_v(net)
    goal = set(goals)
    gi = np.array([[c[2], c[1]] for c in goals], float)
    def h(j, i):
        return float(np.min(np.hypot(gi[:, 0] - i, gi[:, 1] - j))) if len(gi) < 400 else 0.0
    openq, came, cost = [], {}, {}
    for s in starts:
        li, j, i = s
        if 0 <= j < NY and 0 <= i < NX:
            cost[s] = 0.0
            heapq.heappush(openq, (h(j, i), 0.0, s))
    steps = ((1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0), (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414))
    n = 0
    while openq:
        f, c, cur = heapq.heappop(openq)
        if cur in goal:
            path = [cur]
            while path[-1] in came:
                path.append(came[path[-1]])
            return path[::-1]
        if c > cost.get(cur, 1e18):
            continue
        n += 1
        if n > (4_000_000 if RES < 0.1 else 1_500_000):
            return None
        li, j, i = cur
        for dj, di, sc in steps:
            nj, ni = j + dj, i + di
            if not (0 <= nj < NY and 0 <= ni < NX):
                continue
            nxt = (li, nj, ni)
            if bt[li][nj, ni] and nxt not in goal:
                continue
            nc = c + sc + (0.3 if li == 1 else 0.0)
            if nc < cost.get(nxt, 1e18):
                cost[nxt] = nc
                came[nxt] = cur
                heapq.heappush(openq, (nc + h(nj, ni), nc, nxt))
        if not bv[j, i]:
            for nl in range(3):
                if nl == li:
                    continue
                nxt = (nl, j, i)
                nc = c + 25.0
                if nc < cost.get(nxt, 1e18):
                    cost[nxt] = nc
                    came[nxt] = cur
                    heapq.heappush(openq, (nc + h(j, i), nc, nxt))
    return None


def commit(board, g, net_name, path):
    net = board.FindNet(net_name)
    new = []
    k = 0
    while k < len(path) - 1:
        li, j, i = path[k]
        # extend straight run on same layer and direction
        m = k + 1
        if path[m][0] != li:   # via
            v = pcbnew.PCB_VIA(board)
            v.SetPosition(pcbnew.VECTOR2I(mm((i + 0.5) * RES), mm((j + 0.5) * RES)))
            v.SetWidth(mm(VD))
            v.SetDrill(mm(0.2 if VD >= 0.4 else 0.15))
            v.SetNet(net)
            new.append(v)
            k = m
            continue
        d = (path[m][1] - j, path[m][2] - i)
        while m + 1 < len(path) and path[m + 1][0] == li and (path[m + 1][1] - path[m][1], path[m + 1][2] - path[m][2]) == d:
            m += 1
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pcbnew.VECTOR2I(mm((i + 0.5) * RES), mm((j + 0.5) * RES)))
        t.SetEnd(pcbnew.VECTOR2I(mm((path[m][2] + 0.5) * RES), mm((path[m][1] + 0.5) * RES)))
        t.SetWidth(mm(TW))
        t.SetLayer(LAYERS[li])
        t.SetNet(net)
        new.append(t)
        k = m
    # first/last cells are inside pads: connect cell centre to pad centre is implicit (cells lie on copper)
    # verify against foreign copper with KiCad shapes
    items = list(board.GetTracks()) + [p for f in board.GetFootprints() for p in f.Pads()]
    for n_ in new:
        nb = n_.GetBoundingBox()
        nb.Inflate(mm(0.5))
        for it in items:
            if it.GetNetCode() == net.GetNetCode() or not it.GetBoundingBox().Intersects(nb):
                continue
            for layer in (LAYERS + [pcbnew.In1_Cu]):
                if n_.IsOnLayer(layer) and it.IsOnLayer(layer):
                    if it.GetEffectiveShape(layer).Collide(n_.GetEffectiveShape(layer), mm(0.127 if CLR < 0.2 else 0.2)):
                        return False, f"collides with {it.GetFriendlyName()} {getattr(it, 'GetNetname', lambda: '')()}"
    for n_ in new:
        board.Add(n_)
        if n_.Type() == pcbnew.PCB_VIA_T:
            p = n_.GetPosition()
            for li in range(3):
                g.segment(li, p.x / 1e6, p.y / 1e6, p.x / 1e6, p.y / 1e6, VD, net.GetNetCode())
        else:
            li = LAYERS.index(n_.GetLayer())
            s, e = n_.GetStart(), n_.GetEnd()
            g.segment(li, s.x / 1e6, s.y / 1e6, e.x / 1e6, e.y / 1e6, TW, net.GetNetCode())
    return True, f"{len(new)} items"


def isolated_gnd_pads(board):
    """One GND pad per filled GND fragment (F/In2/B) that contains no GND via/PTH."""
    gnd = board.FindNet("GND").GetNetCode()
    vias = [t.GetPosition() for t in board.GetTracks() if t.Type() == pcbnew.PCB_VIA_T and t.GetNetCode() == gnd]
    vias += [p.GetPosition() for f in board.GetFootprints() for p in f.Pads()
             if p.GetNetCode() == gnd and p.GetDrillSize().x > 0]
    pads = [p for f in board.GetFootprints() for p in f.Pads() if p.GetNetCode() == gnd and p.GetDrillSize().x == 0]
    out = []
    for z in board.Zones():
        if z.GetIsRuleArea() or z.GetNetCode() != gnd or z.GetLayer() == pcbnew.In1_Cu:
            continue
        layer = z.GetLayer()
        polys = z.GetFilledPolysList(layer)
        for i in range(polys.OutlineCount()):
            ol = polys.Outline(i)
            if any(ol.PointInside(v) for v in vias):
                continue
            inside = [p for p in pads if p.IsOnLayer(layer) and ol.PointInside(p.GetPosition())]
            if inside:
                out.append(inside[0])
    return out


def stitch_route(board, g, pad):
    """Route from an isolated GND pad to the nearest cell where a via is legal; drop a via."""
    net = pad.GetNetCode()
    li = LAYERS.index(pcbnew.B_Cu) if pad.IsOnLayer(pcbnew.B_Cu) and not pad.IsOnLayer(pcbnew.F_Cu) else 0
    bt = g.blocked_t(li, net)
    bv = g.blocked_v(net)
    bb = pad.GetBoundingBox()
    starts = [(li, j, i) for j in range(int(bb.GetTop() / 1e6 / RES), int(bb.GetBottom() / 1e6 / RES) + 1)
              for i in range(int(bb.GetLeft() / 1e6 / RES), int(bb.GetRight() / 1e6 / RES) + 1)]
    pc = (bb.Centre().x / 1e6, bb.Centre().y / 1e6)
    half = max(bb.GetWidth(), bb.GetHeight()) / 2e6
    openq, came, cost = [], {}, {}
    for s in starts:
        cost[s] = 0.0
        heapq.heappush(openq, (0.0, s))
    steps = ((1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0), (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414))
    n = 0
    while openq:
        c, cur = heapq.heappop(openq)
        _, j, i = cur
        x, y = (i + 0.5) * RES, (j + 0.5) * RES
        if not bv[j, i] and math.hypot(x - pc[0], y - pc[1]) > half + VD / 2 + 0.1:
            path = [cur]
            while path[-1] in came:
                path.append(came[path[-1]])
            path = path[::-1]
            path.append((1 if li == 0 else 0, j, i))   # layer change -> via at the goal cell
            return commit(board, g, board.GetNetInfo().GetNetItem(net).GetNetname(), path)
        n += 1
        if n > 400000:
            break
        for dj, di, sc in steps:
            nj, ni = j + dj, i + di
            if not (0 <= nj < NY and 0 <= ni < NX) or bt[nj, ni]:
                continue
            nxt = (li, nj, ni)
            if c + sc < cost.get(nxt, 1e18):
                cost[nxt] = c + sc
                came[nxt] = cur
                heapq.heappush(openq, (c + sc, nxt))
    return False, "no via spot reachable"


def main():
    if "--gnd" in sys.argv:
        board = pcbnew.LoadBoard(str(B.BOARD))
        g = build_grid(board)
        pads = isolated_gnd_pads(board)
        ok = 0
        for p in pads:
            r, msg = stitch_route(board, g, p)
            print("gnd", p.GetParentFootprint().GetReference(), p.GetNumber(), "ok" if r else "FAIL", msg)
            ok += r
        pcbnew.SaveBoard(str(B.BOARD), board)
        print("gnd stitch routes:", ok, "/", len(pads))
        return
    rep = B.OUT / "reports" / "drc_route.json"
    subprocess.run([B.CLI, "pcb", "drc", "--format", "json", "-o", str(rep), str(B.BOARD)], capture_output=True, text=True)
    unc = json.loads(rep.read_text(encoding="utf-8"))["unconnected_items"]
    board = pcbnew.LoadBoard(str(B.BOARD))
    g = build_grid(board)
    done = 0
    for u in unc:
        (a, b) = u["items"][:2]
        if a["description"].startswith("Zona") or b["description"].startswith("Zona"):
            continue
        na, ca = item_cells(board, a["description"], (a["pos"]["x"], a["pos"]["y"]))
        nb, cb = item_cells(board, b["description"], (b["pos"]["x"], b["pos"]["y"]))
        if not ca or not cb or na != nb:
            print("skip", a["description"][:50], "|", b["description"][:50])
            continue
        code = board.FindNet(na).GetNetCode()
        path = astar(g, code, ca, cb)
        if path is None:
            print("NO PATH", na, a["description"][:40], "->", b["description"][:40])
            continue
        ok, msg = commit(board, g, na, path)
        print("routed" if ok else "REJECT", na, len(path), msg)
        done += ok
    pcbnew.SaveBoard(str(B.BOARD), board)
    print("connections added:", done)


if __name__ == "__main__":
    main()
