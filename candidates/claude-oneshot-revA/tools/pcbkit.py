"""Small pcbnew helper layer used by the Rev A2 layout script (tools/layout_a2.py).

Everything is expressed in board millimetres (origin top-left, x right, y down). The kit builds a
board from the schematic netlist, places footprints at explicit coordinates and adds explicit
tracks, vias and zones, so the critical parts of the layout are engineered by hand and are
reproducible; only the remaining ordinary signals are left to an autorouter.
"""
from __future__ import annotations

import math
import xml.etree.ElementTree as ET
from pathlib import Path

import pcbnew

from kipaths import KICAD_FP

mm = pcbnew.FromMM
MM = pcbnew.ToMM
LAYER = {"F.Cu": pcbnew.F_Cu, "In1.Cu": pcbnew.In1_Cu, "In2.Cu": pcbnew.In2_Cu, "B.Cu": pcbnew.B_Cu}


def V(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))


class Kit:
    def __init__(self, netlist_xml: Path, sc_pretty: Path, board_path: Path):
        self.sc_pretty = Path(sc_pretty)
        self.board = pcbnew.NewBoard(str(board_path))
        self.path = str(board_path)
        self.fps: dict = {}
        self.nets: dict = {}
        self.comps, self.pad_nets = self._read_netlist(netlist_xml)
        self.placed: set = set()

    # ------------------------------------------------------------------ netlist / footprints
    @staticmethod
    def _read_netlist(xml):
        root = ET.parse(xml).getroot()
        comps = []
        for c in root.iter("comp"):
            sp = c.find("sheetpath")
            fields = {f.get("name"): (f.text or "") for f in c.iter("field")}
            dnp = any(p.get("name") == "dnp" for p in c.iter("property"))
            comps.append({"ref": c.get("ref"), "value": c.findtext("value") or "",
                          "footprint": (c.findtext("footprint") or "").strip(), "fields": fields, "dnp": dnp,
                          "sheet": sp.get("names") if sp is not None else "/",
                          "path": (sp.get("tstamps") if sp is not None else "/") + (c.findtext("tstamps") or "").strip()})
        pad_nets = {}
        for n in root.iter("net"):
            name = n.get("name")
            if name.startswith(("unconnected-(", "Net-(")):
                head, body = name.split("(", 1)
                name = f"{head}({body.replace('/', '{slash}')}"
            for node in n.iter("node"):
                pad_nets[(node.get("ref"), node.get("pin"))] = name
        return comps, pad_nets

    def net(self, name):
        if name not in self.nets:
            n = self.board.FindNet(name)
            if n is None:
                n = pcbnew.NETINFO_ITEM(self.board, name)
                self.board.Add(n)
            self.nets[name] = n
        return self.nets[name]

    def _lib(self, nick):
        return str(self.sc_pretty) if nick == "SC" else str(KICAD_FP / f"{nick}.pretty")

    def add_footprints(self):
        for c in self.comps:
            if c["ref"].startswith("#") or not c["footprint"]:
                continue
            nick, _, name = c["footprint"].partition(":")
            f = pcbnew.FootprintLoad(self._lib(nick), name)
            if f is None:
                raise RuntimeError(f"missing footprint {c['ref']} {c['footprint']}")
            f.SetFPID(pcbnew.LIB_ID(nick, name))
            f.SetPath(pcbnew.KIID_PATH(c["path"]))
            f.SetReference(c["ref"])
            f.SetValue(c["value"])
            for k in ("MPN", "Status", "Source"):
                if c["fields"].get(k):
                    f.SetField(k, c["fields"][k])
            for fld in f.GetFields():
                if fld.GetName() in ("MPN", "Status", "Source"):
                    fld.SetVisible(False)
            if c["dnp"]:
                f.SetDNP(True)
            self.board.Add(f)
            for pad in f.Pads():
                n = self.pad_nets.get((c["ref"], pad.GetNumber()))
                if n:
                    pad.SetNet(self.net(n))
            f.Value().SetVisible(False)
            self.fps[c["ref"]] = f

    def add_extra_footprint(self, ref, nick, name, value=""):
        f = pcbnew.FootprintLoad(self._lib(nick), name)
        f.SetFPID(pcbnew.LIB_ID(nick, name))
        f.SetReference(ref)
        f.SetValue(value)
        f.SetBoardOnly(True)
        self.board.Add(f)
        self.fps[ref] = f
        return f

    # ------------------------------------------------------------------ placement
    def place(self, ref, x, y, rot=0, side="F"):
        f = self.fps[ref]
        if side == "B" and not f.IsFlipped():
            f.Flip(f.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        f.SetOrientationDegrees(rot)
        f.SetPosition(V(x, y))
        self.placed.add(ref)
        return f

    def pads(self, ref, num):
        out = []
        for p in self.fps[ref].Pads():
            if p.GetNumber() == str(num):
                q = p.GetPosition()
                out.append((MM(q.x), MM(q.y)))
        if not out:
            raise KeyError(f"{ref}.{num}")
        return out

    def P(self, ref, num, near=None):
        ps = self.pads(ref, num)
        if near is None or len(ps) == 1:
            return ps[0]
        return min(ps, key=lambda q: math.hypot(q[0] - near[0], q[1] - near[1]))

    def netof(self, ref, num):
        return self.pad_nets.get((ref, str(num)), "")

    def two_pin(self, ref, pin, at, direction, side="F"):
        """Place a two-terminal part so pad `pin` sits at `at` and the other pad lies in `direction`
        (degrees, 0 = +x, 90 = up/-y, 180 = -x, 270 = down/+y)."""
        f = self.fps[ref]
        want = (math.cos(math.radians(direction)), -math.sin(math.radians(direction)))
        best = None
        for rot in (0, 90, 180, 270):
            self.place(ref, 0, 0, rot, side)
            a = self.P(ref, pin)
            nums = sorted({p.GetNumber() for p in f.Pads() if p.GetNumber()})
            other = [n for n in nums if n != str(pin)][0]
            b = self.P(ref, other)
            d = (b[0] - a[0], b[1] - a[1])
            L = math.hypot(*d) or 1
            score = (d[0] * want[0] + d[1] * want[1]) / L
            if best is None or score > best[0]:
                best = (score, rot, a)
        _, rot, a = best
        self.place(ref, at[0] - a[0], at[1] - a[1], rot, side)
        return self.fps[ref]

    def center_between(self, ref, at, rot=0, side="F"):
        return self.place(ref, at[0], at[1], rot, side)

    # ------------------------------------------------------------------ copper
    def tr(self, net, pts, w=0.2, layer="F.Cu"):
        n = self.net(net)
        for a, b in zip(pts, pts[1:]):
            if abs(a[0] - b[0]) < 1e-6 and abs(a[1] - b[1]) < 1e-6:
                continue
            t = pcbnew.PCB_TRACK(self.board)
            t.SetStart(V(*a))
            t.SetEnd(V(*b))
            t.SetWidth(mm(w))
            t.SetLayer(LAYER[layer])
            t.SetNet(n)
            self.board.Add(t)

    def via(self, net, x, y, size=0.5, drill=0.3):
        v = pcbnew.PCB_VIA(self.board)
        v.SetPosition(V(x, y))
        v.SetViaType(pcbnew.VIATYPE_THROUGH)
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        v.SetWidth(pcbnew.F_Cu, mm(size))
        v.SetDrill(mm(drill))
        v.SetNet(self.net(net))
        self.board.Add(v)
        return (x, y)

    def zone(self, net, layer, poly, prio=0, clearance=0.2, connect="solid", min_w=0.2, name="", island="always"):
        z = pcbnew.ZONE(self.board)
        if isinstance(layer, (list, tuple)):
            ls = pcbnew.LSET()
            for l in layer:
                ls.AddLayer(LAYER[l])
            z.SetLayerSet(ls)
        else:
            z.SetLayer(LAYER[layer])
        if net:
            z.SetNet(self.net(net))
        ch = pcbnew.SHAPE_LINE_CHAIN()
        for px, py in poly:
            ch.Append(mm(px), mm(py))
        ch.SetClosed(True)
        z.AddPolygon(ch)
        z.SetAssignedPriority(prio)
        z.SetLocalClearance(mm(clearance))
        z.SetMinThickness(mm(min_w))
        z.SetPadConnection({"solid": pcbnew.ZONE_CONNECTION_FULL, "thermal": pcbnew.ZONE_CONNECTION_THERMAL,
                            "none": pcbnew.ZONE_CONNECTION_NONE}[connect])
        z.SetIslandRemovalMode({"always": pcbnew.ISLAND_REMOVAL_MODE_ALWAYS, "never": pcbnew.ISLAND_REMOVAL_MODE_NEVER}[island])
        z.SetThermalReliefGap(mm(0.2))
        z.SetThermalReliefSpokeWidth(mm(0.3))
        if name:
            z.SetZoneName(name)
        self.board.Add(z)
        return z

    def keepout(self, poly, layers, name="", tracks=True, vias=True, copper=True):
        z = pcbnew.ZONE(self.board)
        z.SetIsRuleArea(True)
        z.SetDoNotAllowTracks(tracks)
        z.SetDoNotAllowVias(vias)
        z.SetDoNotAllowZoneFills(copper)
        z.SetDoNotAllowPads(False)
        z.SetDoNotAllowFootprints(False)
        ls = pcbnew.LSET()
        for l in layers:
            ls.AddLayer(LAYER[l])
        z.SetLayerSet(ls)
        z.SetZoneName(name)
        ch = pcbnew.SHAPE_LINE_CHAIN()
        for px, py in poly:
            ch.Append(mm(px), mm(py))
        ch.SetClosed(True)
        z.AddPolygon(ch)
        self.board.Add(z)
        return z

    def edge(self, pts, width=0.1):
        for a, b in zip(pts, pts[1:] + pts[:1]):
            s = pcbnew.PCB_SHAPE(self.board)
            s.SetShape(pcbnew.SHAPE_T_SEGMENT)
            s.SetStart(V(*a))
            s.SetEnd(V(*b))
            s.SetLayer(pcbnew.Edge_Cuts)
            s.SetWidth(mm(width))
            self.board.Add(s)

    def edge_rect(self, x0, y0, x1, y1):
        s = pcbnew.PCB_SHAPE(self.board)
        s.SetShape(pcbnew.SHAPE_T_RECT)
        s.SetStart(V(x0, y0))
        s.SetEnd(V(x1, y1))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(mm(0.1))
        self.board.Add(s)

    def text(self, s, x, y, layer=pcbnew.F_SilkS, size=0.8, rot=0):
        t = pcbnew.PCB_TEXT(self.board)
        t.SetText(s)
        t.SetPosition(V(x, y))
        t.SetLayer(layer)
        t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
        t.SetTextThickness(mm(size * 0.15))
        t.SetTextAngleDegrees(rot)
        if layer == pcbnew.B_SilkS:
            t.SetMirrored(True)
        self.board.Add(t)

    def save(self):
        pcbnew.SaveBoard(self.path, self.board)


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
