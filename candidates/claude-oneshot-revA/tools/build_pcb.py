"""Build the candidate PCB from the schematic netlist: 4-layer 60 x 84 mm outline, zoned
placement per docs/MECHANICAL_RF_FLOORPLAN.md, automatic passive placement next to the part
each passive serves, keepouts, net classes, optional Freerouting, zones, DRC and exports.

Run with KiCad's bundled Python (pcbnew):
    "C:/Program Files/KiCad/10.0/bin/python.exe" tools/build_pcb.py [--route]
"""
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_sch import CLI, DISPLAY_STANDOFF, OUT, PROJECT  # noqa: E402

KFP = Path("C:/Program Files/KiCad/10.0/share/kicad/footprints")
mm = pcbnew.FromMM
W, H = 60.0, 84.0
BOARD = OUT / f"{PROJECT}.kicad_pcb"
TOOLS = Path(os.environ.get("STRATOS_TOOLS", "D:/claude_scratch/stratos/tools"))
JAVA = TOOLS / "jdk-25.0.4.1+1-jre" / "bin" / "java.exe"
FREEROUTING = TOOLS / "freerouting-2.4.1.jar"

# --------------------------------------------------------------------------- placement
# (x, y, rotation deg, side) in board mm, origin top-left, y down. "B" = bottom side.
PLACE = {
    # ESP32-S3 rotated so its PCB antenna sits at the LEFT board edge (x 0.3-6.3 mm), clear of
    # the 2S holder (back side, x >= 14.7 mm). Footprint keepout covers x 0-6.3, y 0-34.3 in-board.
    "U1": (13.05, 10.3, 90, "F"),
    # top strip (x 27-60): GNSS feed, vent group, ADS-B input
    "J5": (29.0, 2.9, 0, "F"), "D2": (29.0, 6.3, 90, "F"), "U17": (36.0, 12.6, 0, "F"),
    "U33": (44.0, 1.9, 0, "F"), "U32": (48.6, 2.1, 0, "F"),
    "J7": (57.2, 2.9, 0, "F"), "U50": (56.4, 9.6, 90, "F"), "FL1": (56.4, 14.4, 90, "F"),
    "U52": (56.4, 19.6, 90, "F"), "FL2": (56.4, 24.6, 90, "F"), "U54": (55.4, 30.2, 0, "F"),
    "U55": (50.8, 33.6, 0, "F"), "U20": (47.5, 42.5, 0, "F"), "U21": (56.2, 44.8, 90, "F"),
    "Y1": (41.0, 38.4, 0, "F"),
    # sensors: IMU near the centroid, magnetometer in the upper-left (far from cells/inductors)
    "U30": (30.0, 42.0, 0, "F"), "U31": (3.6, 42.9, 0, "F"), "MK1": (3.4, 47.2, 90, "F"),
    # control
    "U13": (22.5, 33.5, 90, "F"), "SW1": (58.4, 53.5, 90, "F"), "SW2": (58.4, 59.5, 90, "F"),
    # storage: microSD at the left edge (card inserts from the left); expansion on the back-left
    "J8": (9.35, 57.8, 270, "F"), "J2": (4.2, 58.3, 90, "B"),
    # display FPC connectors; FPC tails fold around the display bottom edge (lengths TBD)
    "J3": (31.0, 67.4, 0, "F"), "J4": (13.2, 67.4, 0, "F"), "U14": (26.8, 61.2, 90, "F"),
    "U16": (41.8, 59.0, 0, "F"), "L3": (41.8, 55.2, 0, "F"),
    # LoRa bottom-right corner
    "U40": (50.4, 67.2, 0, "F"), "Y2": (45.4, 67.2, 90, "F"), "U41": (54.6, 75.2, 0, "F"),
    "J6": (57.2, 80.8, 0, "F"),
    # power: USB-C at the bottom edge, charger between the holder tabs, buck in the core
    "J1": (8.0, 80.6, 0, "F"), "U6": (31.8, 79.6, 0, "F"), "U7": (22.0, 48.6, 0, "F"),
    "L2": (26.8, 51.8, 0, "F"),
    # 2S holder on the back, right-aligned; B+/MID/B- tabs grouped at the bottom end (placeholders)
    "BT1": (37.35, 42.0, 180, "B"),
    # mechanical
    "H1": (3.2, 37.6, 0, "F"), "H2": (3.2, 72.0, 0, "F"), "H3": (12.0, 28.0, 0, "F"),
    "FID1": (44.0, 8.6, 0, "F"), "FID2": (40.0, 33.0, 0, "F"), "FID3": (20.6, 82.8, 0, "F"),
}
PASSIVE_PREFIX = ("R", "C", "L", "D", "TP", "FL", "Q", "TH", "F", "Y")
# regions where no auto-placed part may land (board mm): ESP32 antenna copper keepout,
# SHT40 thermal tab, display FPC tail fold zone in front of J3/J4 mouths
KEEPOUT = [(0.0, 0.0, 6.7, 34.6), (41.5, 0.0, 46.5, 4.8), (4.0, 73.3, 43.2, 74.4)]
# ADS-B/LoRa/GNSS RF nets (routed first-choice short; 0.15 mm ~ 50 ohm on L1/L2 per PCB_STACKUP.md)
RF_NETS = ("GNSS_RF", "ADSB_", "LORA_")
POWER_NETS = ("GND", "VBUS", "VBUS_PROT", "PACK_P", "BAT_P", "BAT_N", "BAT_MID", "CHG_PMID", "CHG_SW",
              "CHG_SNS", "BUCK_SW", "3V3_MAIN", "BL_SW", "LED_A", "PROT_DRAIN")


def read_netlist():
    xml = OUT / "reports" / "netlist.xml"
    subprocess.run([CLI, "sch", "export", "netlist", "--format", "kicadxml", "-o", str(xml),
                    str(OUT / f"{PROJECT}.kicad_sch")], capture_output=True, text=True, check=True)
    root = ET.parse(xml).getroot()
    comps = []
    for c in root.iter("comp"):
        sp = c.find("sheetpath")
        fields = {f.get("name"): (f.text or "") for f in c.iter("field")}
        dnp = any(p.get("name") == "dnp" for p in c.iter("property"))
        comps.append({"ref": c.get("ref"), "value": c.findtext("value") or "",
                      "footprint": (c.findtext("footprint") or "").strip(), "fields": fields, "dnp": dnp,
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


def fp_lib(nick: str) -> str:
    if nick == "SC":
        return str(OUT / "libs" / "SC.pretty")
    return str(KFP / f"{nick}.pretty")


def bbox_mm(f):
    f.BuildCourtyardCaches()
    layer = pcbnew.B_CrtYd if f.IsFlipped() else pcbnew.F_CrtYd
    bb = f.GetCourtyard(layer).BBox()
    if bb.GetWidth() <= 0:
        boxes = [p.GetBoundingBox() for p in f.Pads()]
        if not boxes:
            p = f.GetPosition()
            return (p.x / 1e6 - 0.5, p.y / 1e6 - 0.5, p.x / 1e6 + 0.5, p.y / 1e6 + 0.5)
        return (min(b.GetLeft() for b in boxes) / 1e6 - 0.25, min(b.GetTop() for b in boxes) / 1e6 - 0.25,
                max(b.GetRight() for b in boxes) / 1e6 + 0.25, max(b.GetBottom() for b in boxes) / 1e6 + 0.25)
    return (bb.GetLeft() / 1e6, bb.GetTop() / 1e6, bb.GetRight() / 1e6, bb.GetBottom() / 1e6)


def overlap(a, b, gap=0.1):
    return not (a[2] + gap <= b[0] or b[2] + gap <= a[0] or a[3] + gap <= b[1] or b[3] + gap <= a[1])


def set_rules(board):
    ds = board.GetDesignSettings()
    ds.SetCopperLayerCount(4)
    board.SetCopperLayerCount(4)
    ds.m_TrackMinWidth = mm(0.1)
    ds.m_MinClearance = mm(0.1)
    ds.m_ViasMinSize = mm(0.35)
    ds.m_MinThroughDrill = mm(0.2)
    ds.m_ViasMinAnnularWidth = mm(0.075)
    ds.m_CopperEdgeClearance = mm(0.25)
    ds.m_HoleClearance = mm(0.15)
    ds.m_HoleToHoleMin = mm(0.25)
    ds.SetBoardThickness(mm(1.6))
    board.SetLayerType(pcbnew.In1_Cu, pcbnew.LT_POWER)
    board.SetLayerName(pcbnew.In1_Cu, "In1.Cu")


def netclasses():
    """Write net classes into the project so Freerouting's DSN carries the widths."""
    pro = OUT / f"{PROJECT}.kicad_pro"
    data = json.loads(pro.read_text(encoding="utf-8"))
    base = {"bus_width": 12, "diff_pair_gap": 0.25, "diff_pair_via_gap": 0.25, "diff_pair_width": 0.2,
            "line_style": 0, "microvia_diameter": 0.3, "microvia_drill": 0.1, "pcb_color": "rgba(0, 0, 0, 0.000)",
            "schematic_color": "rgba(0, 0, 0, 0.000)", "wire_width": 6, "priority": 2147483647,
            "tuning_profile": ""}
    classes = [
        dict(base, name="Default", clearance=0.127, track_width=0.15, via_diameter=0.45, via_drill=0.2),
        dict(base, name="Power", clearance=0.127, track_width=0.4, via_diameter=0.6, via_drill=0.3, priority=1),
        dict(base, name="RF50", clearance=0.2, track_width=0.15, via_diameter=0.45, via_drill=0.2, priority=0),
        dict(base, name="USB90", clearance=0.15, track_width=0.16, via_diameter=0.45, via_drill=0.2,
             diff_pair_width=0.16, diff_pair_gap=0.33, priority=0),
    ]
    pats = [{"netclass": "Power", "pattern": p} for p in POWER_NETS]
    pats += [{"netclass": "RF50", "pattern": "GNSS_RF"}, {"netclass": "RF50", "pattern": "ADSB_ANT"},
             {"netclass": "RF50", "pattern": "ADSB_L*"}, {"netclass": "RF50", "pattern": "ADSB_S*"},
             {"netclass": "RF50", "pattern": "ADSB_DET_IN"}, {"netclass": "RF50", "pattern": "LORA_*"},
             {"netclass": "USB90", "pattern": "USB_D*"}]
    ns = data.setdefault("net_settings", {})
    ns["classes"] = classes
    ns["netclass_patterns"] = pats
    ns.setdefault("meta", {"version": 4})
    pro.write_text(json.dumps(data, indent=2), encoding="utf-8")


def outline(board):
    r = 3.0
    pts = []
    for cx, cy, a0 in ((W - r, r, -90), (W - r, H - r, 0), (r, H - r, 90), (r, r, 180)):
        for k in range(0, 91, 10):
            a = math.radians(a0 + k)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    for i in range(len(pts)):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        a, b = pts[i], pts[(i + 1) % len(pts)]
        s.SetStart(pcbnew.VECTOR2I(mm(a[0]), mm(a[1])))
        s.SetEnd(pcbnew.VECTOR2I(mm(b[0]), mm(b[1])))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(mm(0.1))
        board.Add(s)


def text(board, s, x, y, layer=pcbnew.F_SilkS, size=0.8):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(s)
    t.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
    t.SetTextThickness(mm(size * 0.15))
    if layer in (pcbnew.B_SilkS,):
        t.SetMirrored(True)
    board.Add(t)


def zone(board, net, layer, poly, priority=0, clearance=0.2):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    if net:
        z.SetNet(board.FindNet(net))
    ch = pcbnew.SHAPE_LINE_CHAIN()
    for px, py in poly:
        ch.Append(mm(px), mm(py))
    ch.SetClosed(True)
    z.AddPolygon(ch)
    z.SetAssignedPriority(priority)
    z.SetLocalClearance(mm(clearance))
    z.SetMinThickness(mm(0.2))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL if net == "GND" else pcbnew.ZONE_CONNECTION_THERMAL)
    z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    z.SetThermalReliefGap(mm(0.25))
    z.SetThermalReliefSpokeWidth(mm(0.3))
    board.Add(z)
    return z


def rule_area(board, poly, layers, name):
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True)
    z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True)
    z.SetDoNotAllowZoneFills(True)
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowFootprints(False)
    ls = pcbnew.LSET()
    for l in layers:
        ls.AddLayer(l)
    z.SetLayerSet(ls)
    z.SetZoneName(name)
    ch = pcbnew.SHAPE_LINE_CHAIN()
    for px, py in poly:
        ch.Append(mm(px), mm(py))
    ch.SetClosed(True)
    z.AddPolygon(ch)
    board.Add(z)


def build(route: bool, passes: int, timeout: int):
    netclasses()
    comps, pad_nets = read_netlist()
    board = pcbnew.NewBoard(str(BOARD))
    set_rules(board)
    outline(board)
    nets = {}

    def net(name):
        if name not in nets:
            nets[name] = pcbnew.NETINFO_ITEM(board, name)
            board.Add(nets[name])
        return nets[name]

    fps = {}
    for c in comps:
        if c["ref"].startswith("#") or not c["footprint"]:
            continue
        nick, _, name = c["footprint"].partition(":")
        f = pcbnew.FootprintLoad(fp_lib(nick), name)
        if f is None:
            print("MISSING footprint", c["ref"], c["footprint"])
            continue
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
        board.Add(f)
        for pad in f.Pads():
            n = pad_nets.get((c["ref"], pad.GetNumber()))
            if n:
                pad.SetNet(net(n))
        f.Value().SetVisible(False)
        f.Reference().SetTextSize(pcbnew.VECTOR2I(mm(0.6), mm(0.6)))
        f.Reference().SetTextThickness(mm(0.1))
        fps[c["ref"]] = f

    placed = {}   # ref -> (side, bbox)

    def put(f, x, y, rot, side):
        if side == "B" and not f.IsFlipped():
            f.Flip(f.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        f.SetOrientationDegrees(rot)
        f.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
        placed[f.GetReference()] = (side, bbox_mm(f))

    for ref, (x, y, rot, side) in PLACE.items():
        if ref in fps:
            put(fps[ref], x, y, rot, side)
    # the huge ESP32 antenna-clearance courtyard would block half the board: use its body
    placed["U1"] = ("F", (0.3, 0.3, 26.4, 20.4))
    # through-hole pads of back-side parts also block the front
    for ref, (side, _) in list(placed.items()):
        if side != "B" or ref not in fps:
            continue
        for k, pad in enumerate(fps[ref].Pads()):
            if pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH:
                b = pad.GetBoundingBox()
                placed[f"{ref}#pad{k}"] = ("F", (b.GetLeft() / 1e6 - 0.4, b.GetTop() / 1e6 - 0.4,
                                                 b.GetRight() / 1e6 + 0.4, b.GetBottom() / 1e6 + 0.4))

    # anchors for passives: connected non-passive part, preferring the most shared nets
    net_members = {}
    for (ref, pin), n in pad_nets.items():
        net_members.setdefault(n, set()).add(ref)

    def is_passive(ref):
        return ref.rstrip("0123456789").upper() in PASSIVE_PREFIX and ref not in PLACE

    # engineering anchors: parts that must sit next to a specific part (hot loops, protection at
    # the connector, local switches next to their load)
    ANCHOR = {"U2": "J1", "U3": "J1", "U4": "J1", "Q2": "U6", "L1": "U6", "TH1": "U6", "R15": "U6",
              "D1": "U16", "U8": "U54", "U10": "J8", "U23": "J8", "U11": "U20", "U12": "MK1", "U24": "MK1",
              "U15": "J3", "U9": "U14", "U5": "BT1", "Q1": "U5", "F1": "BT1", "L70": "U40", "U41": "J6"}
    GLOBAL = {"GND", "3V3_MAIN", "1V8_LOGIC", "3V0_RF_QUIET", "PACK_P", "3V3_ADSB", "I2C_SDA", "I2C_SCL",
              "SPI_SCLK", "SPI_MOSI", "SPI_MISO"}
    import design as _D
    group = {p.ref: (sd.file, p.group) for sd in _D.build().sheets for p in sd.parts}

    def anchor_pad(ref):
        f = fps[ref]
        if ref in ANCHOR and ANCHOR[ref] in placed:
            o = fps[ANCHOR[ref]]
            shared = [op for op in o.Pads() for pd in f.Pads()
                      if op.GetNetname() and op.GetNetname() == pd.GetNetname() and op.GetNetname() != "GND"]
            p = shared[0].GetPosition() if shared else o.GetPosition()
            return p.x / 1e6, p.y / 1e6, placed[ANCHOR[ref]][0]
        nets = {pd.GetNetname() for pd in f.Pads() if pd.GetNetname()}
        best, best_s = None, 0.0
        for other in placed:
            if other not in fps or other == ref or is_passive(other):
                continue
            o = fps[other]
            onets = {op.GetNetname() for op in o.Pads()}
            s_ = sum(1.0 for n in nets & onets if n not in GLOBAL) + 0.1 * len((nets & onets) - {"GND"})
            if group.get(other) == group.get(ref) and group.get(ref, ("", ""))[1]:
                s_ += 0.6
            if s_ > best_s:
                cand = [op for op in o.Pads() if op.GetNetname() in (nets - GLOBAL)] or                        [op for op in o.Pads() if op.GetNetname() in (nets - {"GND"})] or list(o.Pads())
                p = cand[0].GetPosition()
                best, best_s = (p.x / 1e6, p.y / 1e6, placed[other][0]), s_
        return best

    def free(box, side):
        if box[0] < 0.6 or box[1] < 0.6 or box[2] > W - 0.6 or box[3] > H - 0.6:
            return False
        for k in KEEPOUT:
            if side == "F" and overlap(box, k, 0):
                return False
        for s, b in placed.values():
            if s == side and overlap(box, b, 0.15):
                return False
        # holder body occupies the back
        return True

    order = [r for r in fps if r not in placed]
    # ICs and engineering-anchored parts first, then passives, bigger ones first
    order.sort(key=lambda r: (0 if (not is_passive(r) or r in ANCHOR) else 1,
                              -((lambda b: (b[2] - b[0]) * (b[3] - b[1]))(bbox_mm(fps[r])))))
    unplaced = []
    for ref in order:
        f = fps[ref]
        a = anchor_pad(ref)
        if a is None:
            a = (30.0, 48.0, "F")
        ax, ay, side = a
        side = "F"
        done = False
        for rad in [0.0] + [0.5 * k for k in range(1, 80)]:
            steps = max(1, int(2 * math.pi * rad / 0.5))
            for s in range(steps):
                t = 2 * math.pi * s / steps
                x, y = ax + rad * math.cos(t), ay + rad * math.sin(t)
                for rot in (0, 90):
                    f.SetOrientationDegrees(rot)
                    f.SetPosition(pcbnew.VECTOR2I(mm(round(x * 20) / 20), mm(round(y * 20) / 20)))
                    b = bbox_mm(f)
                    if free(b, side):
                        placed[ref] = (side, b)
                        done = True
                        break
                if done:
                    break
            if done:
                break
        if not done:
            unplaced.append(ref)
            f.SetPosition(pcbnew.VECTOR2I(mm(70), mm(10 + len(unplaced) * 3)))
    print("auto-placed", len(order) - len(unplaced), "unplaced", unplaced)

    # board-only display envelope (3D / fit), centred on the lower 70 mm of the board
    disp = pcbnew.FootprintLoad(fp_lib("SC"), "Display_Orient_AFY240320A1-2.8INTH-C1_Envelope")
    disp.SetReference("DS1")
    disp.SetValue("AFY240320A1-2.8INTH-C1 (envelope)")
    disp.SetPosition(pcbnew.VECTOR2I(mm(30.0), mm(48.55)))
    board.Add(disp)

    # keepouts: ESP32 antenna comes with the footprint; add BMP581 under-body and SHT40 tab
    rule_area(board, [(48.05, 1.55), (49.15, 1.55), (49.15, 2.65), (48.05, 2.65)],
              [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu], "BMP581 no copper under body")
    # SHT40 thermal tab: milled slot around three sides
    for (x0, y0, x1, y1) in ((41.8, 0.0, 42.6, 4.4), (45.4, 0.0, 46.2, 4.4)):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_RECT)
        s.SetStart(pcbnew.VECTOR2I(mm(x0), mm(y0 + 0.9)))
        s.SetEnd(pcbnew.VECTOR2I(mm(x1), mm(y1)))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(mm(0.05))
        board.Add(s)
    text(board, "StratosCore Rev A - Claude one-shot candidate", 30.0, 62.0 - 0.0 + 21.2, pcbnew.B_SilkS, 1.0)
    text(board, "NOT FOR MANUFACTURE - review gates open", 30.0, 82.0 - 0.0 + 0.2, pcbnew.B_SilkS, 0.8)
    board.Save(str(BOARD))

    if route:
        do_route(passes, timeout)
    board = pcbnew.LoadBoard(str(BOARD))
    add_zones(board)
    board.Save(str(BOARD))
    return unplaced


def add_zones(board):
    full = [(0.3, 0.3), (W - 0.3, 0.3), (W - 0.3, H - 0.3), (0.3, H - 0.3)]
    for z in list(board.Zones()):
        if not z.GetIsRuleArea():
            board.Remove(z)
    zone(board, "GND", pcbnew.In1_Cu, full, 0)
    zone(board, "3V3_MAIN", pcbnew.In2_Cu, [(19.0, 27.0), (W - 0.3, 27.0), (W - 0.3, 78.0), (44.0, 78.0), (44.0, 64.0), (19.0, 64.0)], 1)
    zone(board, "GND", pcbnew.In2_Cu, full, 0)
    zone(board, "GND", pcbnew.F_Cu, full, 0)
    zone(board, "GND", pcbnew.B_Cu, full, 0)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())


def do_route(passes, timeout):
    board = pcbnew.LoadBoard(str(BOARD))
    # keep only the In1 GND plane for Freerouting (it connects GND pads by vias); the outer and
    # In2 pours are re-created after the SES import
    for z in list(board.Zones()):
        if not z.GetIsRuleArea():
            board.Remove(z)
    full = [(0.3, 0.3), (W - 0.3, 0.3), (W - 0.3, H - 0.3), (0.3, H - 0.3)]
    zone(board, "GND", pcbnew.In1_Cu, full, 0)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.Save(str(BOARD))
    dsn, ses = OUT / "route" / "board.dsn", OUT / "route" / "board.ses"
    dsn.parent.mkdir(exist_ok=True)
    ok = pcbnew.ExportSpecctraDSN(board, str(dsn))
    print("DSN", ok)
    cmd = [str(JAVA), "-jar", str(FREEROUTING), "-de", str(dsn), "-do", str(ses), "-mp", str(passes), "-mt", "8",
           "--gui.enabled=false"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        (OUT / "route" / "freerouting.log").write_text((r.stdout or "") + "\n" + (r.stderr or ""), encoding="utf-8")
    except subprocess.TimeoutExpired:
        print("freerouting timeout")
    if ses.exists():
        board = pcbnew.LoadBoard(str(BOARD))
        pcbnew.ImportSpecctraSES(board, str(ses))
        pcbnew.SaveBoard(str(BOARD), board)
        print("routed items:", len(board.GetTracks()))
    else:
        print("no SES produced")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--route", action="store_true")
    ap.add_argument("--passes", type=int, default=40)
    ap.add_argument("--timeout", type=int, default=3000)
    a = ap.parse_args()
    build(a.route, a.passes, a.timeout)
