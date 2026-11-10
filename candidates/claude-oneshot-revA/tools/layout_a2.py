"""StratosCore candidate Rev A2 - engineered placement and critical routing.

Run:  python3 tools/layout_a2.py            (writes kicad/StratosCore_Claude.kicad_pcb, pre-route state)
Then: python3 tools/route_a2.py             (autoroutes the remaining ordinary nets, fills, checks)

Coordinates are board mm, origin top-left, x right, y down. Every critical block (charger, buck,
backlight boost, eFuse, RF chains, crystals, USB pair) is placed and routed explicitly here from the
manufacturer layout guidance cited in docs/REVIEW_A2_2026_11_10.md; nothing in those blocks is left
to the autorouter.
"""
from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path

import pcbnew
from shapely.geometry import Polygon, box

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from kipaths import CLI  # noqa: E402
from pcbkit import MM, Kit, mm, rect  # noqa: E402

ROOT = HERE.parent
OUT = ROOT / "kicad"
PROJECT = "StratosCore_Claude"
W, H = 60.0, 84.0
NOTCH = (6.5, 21.3)          # board removed under the ESP32 antenna: x < 6.5, y < 21.3

RF_W = 0.15                  # 50 ohm microstrip on L1 over L2 (tools/zsolve.py: 49.9 ohm)
RF_GAP = 0.30                # coplanar ground gap (49.5 ohm with pour)
USB_W, USB_S = 0.15, 0.20    # 90 ohm edge-coupled pair (tools/zsolve.py: 91.2 ohm)
SIG_W = 0.15
VIA = dict(size=0.5, drill=0.3)


SHAPE = []


class Frame:
    """Local block frame: rotation in multiples of 90 deg (counter-clockwise on screen) about an origin."""

    def __init__(self, k: Kit, ox, oy, rot=0):
        self.k, self.ox, self.oy, self.rot = k, ox, oy, rot % 360

    def pt(self, x, y):
        r = self.rot
        if r == 0:
            dx, dy = x, y
        elif r == 90:
            dx, dy = y, -x
        elif r == 180:
            dx, dy = -x, -y
        else:
            dx, dy = -y, x
        return (round(self.ox + dx, 4), round(self.oy + dy, 4))

    def pts(self, lst):
        return [self.pt(*p) for p in lst]

    def ic(self, ref, x=0, y=0, rot=0):
        return self.k.place(ref, *self.pt(x, y), (rot + self.rot) % 360)

    def two(self, ref, pin, x, y, direction):
        return self.k.two_pin(ref, pin, self.pt(x, y), (direction + self.rot) % 360)

    def tr(self, net, lst, w=0.2, layer="F.Cu"):
        self.k.tr(net, self.pts(lst), w, layer)

    def via(self, net, x, y, **kw):
        return self.k.via(net, *self.pt(x, y), **{**VIA, **kw})

    def zone(self, net, lst, layer="F.Cu", prio=20, clearance=0.2, **kw):
        return self.k.zone(net, layer, self.pts(lst), prio=prio, clearance=clearance, **kw)

    def rzone(self, net, x0, y0, x1, y1, **kw):
        return self.zone(net, rect(x0, y0, x1, y1), **kw)

    def loc(self, ref, pad, near=None):
        """Pad position expressed in this frame."""
        x, y = self.k.P(ref, pad, near)
        dx, dy = x - self.ox, y - self.oy
        r = self.rot
        if r == 0:
            return (dx, dy)
        if r == 90:
            return (-dy, dx)
        if r == 180:
            return (-dx, -dy)
        return (dy, -dx)


# ============================================================================== board setup
def outline_points():
    board = box(0, 0, W, H).buffer(-3.0).buffer(3.0, quad_segs=9)
    notch = box(-1, -1, NOTCH[0], NOTCH[1])
    shape = board.difference(notch)
    shape = shape.buffer(0.8, quad_segs=6).buffer(-0.8, quad_segs=6)      # concave corner radius (router bit)
    shape = shape.buffer(-0.6, quad_segs=6).buffer(0.6, quad_segs=6)      # new convex corners
    pts = list(shape.exterior.coords)[:-1]
    return [(round(x, 4), round(y, 4)) for x, y in pts], shape


def setup(k: Kit):
    b = k.board
    ds = b.GetDesignSettings()
    ds.SetCopperLayerCount(4)
    b.SetCopperLayerCount(4)
    ds.m_TrackMinWidth = mm(0.127)
    ds.m_MinClearance = mm(0.127)
    ds.m_ViasMinSize = mm(0.45)
    ds.m_MinThroughDrill = mm(0.2)
    ds.m_ViasMinAnnularWidth = mm(0.1)
    ds.m_CopperEdgeClearance = mm(0.3)
    ds.m_HoleClearance = mm(0.15)
    ds.m_HoleToHoleMin = mm(0.25)
    ds.SetBoardThickness(mm(1.6))
    b.SetLayerType(pcbnew.In1_Cu, pcbnew.LT_POWER)
    b.SetLayerType(pcbnew.In2_Cu, pcbnew.LT_MIXED)
    pts, shape = outline_points()
    k.edge(pts)
    SHAPE.append(shape)
    return shape


# ============================================================================== power: BQ25887 charger
def blk_charger(k: Kit, ox, oy, rot=0):
    """TI SLUSD89B 11.1 priority list: (1) SNS caps at SNS/GND, (2) PMID cap at PMID/GND, (3) inductor at SW
    with minimum SW copper, (4) decoupling next to the IC, (6) thermal-pad vias, (8) MID away from SW.
    Local frame = datasheet top view (pins 19-24 on top, 13-18 on the right)."""
    f = Frame(k, ox, oy, rot)
    f.ic("U6")
    # --- thermal pad to L2 and the two GND pins straight into the pad (single power/analog ground point)
    for x, y in ((0, 0), (-0.85, -0.85), (0.85, -0.85), (-0.85, 0.85), (0.85, 0.85)):
        f.via("GND", x, y)
    f.tr("GND", [(0.75, -1.962), (0.75, -1.25)], 0.25)
    f.tr("GND", [(1.25, -1.962), (1.25, -1.25)], 0.25)
    # --- inductor: SW pad 0.7 mm from the SW pins, PMID pad above it
    f.two("L1", 2, 4.25, -1.1, 90)
    f.zone("CHG_SW", [(1.95, -1.45), (5.35, -1.75), (5.35, -0.5), (1.95, -0.58)], prio=30, name="chg SW")
    # --- PMID capacitor directly above the PMID pins, strip to the inductor
    f.two("C11", 1, 0.2, -3.2, 90)
    f.zone("CHG_PMID", [(-0.42, -1.6), (0.42, -1.6), (0.42, -2.7), (3.1, -2.7), (5.35, -2.7), (5.35, -3.95),
                        (-0.53, -3.95), (-0.53, -2.7), (-0.42, -2.7)], prio=30, name="chg PMID")
    f.via("GND", 1.45, -5.1)
    f.via("GND", -1.05, -5.75)
    f.tr("GND", [(0.2, -5.1), (1.45, -5.1)], 0.5)
    # --- VBUS capacitor
    f.two("C10", 1, -1.4, -3.4, 90)
    f.tr("VBUS_PROT", [(-0.75, -1.962), (-0.75, -2.9), (-1.0, -3.15)], 0.25)
    f.tr("GND", [(-1.4, -4.95), (-1.05, -5.75)], 0.4)
    # --- SNS (boost output) capacitors: first priority, 0.9 mm from the SNS pins, ground vias at the pads
    f.two("C14", 1, 3.75, 0.5, 0)
    f.two("C15", 1, 3.75, 2.35, 0)
    f.zone("CHG_SNS", [(1.95, -0.42), (3.2, -0.42), (4.27, -0.25), (4.27, 3.1), (3.23, 3.1), (3.23, 0.42), (1.95, 0.42)],
           prio=30, name="chg SNS")
    for y in (0.0, 0.95, 1.9, 2.85):
        f.via("GND", 6.65, y)
    f.zone("GND", [(5.15, -0.25), (6.95, -0.25), (6.95, 3.1), (5.15, 3.1)], prio=30, name="chg SNS gnd")
    # --- BAT (pack) pins: 0.5 mm neck between the IC and the SNS pads, BAT capacitor below
    f.two("C16", 1, 3.3, 4.3, 0)
    f.zone("PACK_P", [(1.95, 0.62), (3.03, 0.62), (3.03, 3.32), (3.85, 3.32), (3.85, 5.05), (2.25, 5.05), (2.25, 1.4), (1.95, 1.4)],
           prio=28, name="chg BAT")
    f.via("GND", 6.3, 4.3)
    f.tr("GND", [(5.2, 4.3), (6.3, 4.3)], 0.5)
    # --- bootstrap capacitor at the BTST pin; its SW side returns on L4 to the SW copper
    f.two("C12", 1, 1.72, 3.1, 270)
    f.tr("CHG_BTST", [(1.25, 1.962), (1.25, 2.55), (1.72, 3.0)], 0.2)
    f.via("CHG_SW", 1.72, 4.85)
    f.tr("CHG_SW", [(1.72, 4.06), (1.72, 4.85)], 0.3)
    f.via("CHG_SW", 5.85, -1.1)
    f.tr("CHG_SW", [(5.3, -1.1), (5.85, -1.1)], 0.4)
    f.tr("CHG_SW", [(1.72, 4.85), (2.6, 4.85), (5.85, 1.6), (5.85, -1.1)], 0.3, "B.Cu")
    # --- REGN capacitor at the REGN pin
    f.two("C13", 1, 0.75, 3.25, 270)
    f.tr("CHG_REGN", [(0.75, 1.962), (0.75, 3.0)], 0.2)
    f.via("GND", 0.85, 5.6)
    f.tr("GND", [(0.75, 4.8), (0.85, 5.6)], 0.4)
    # --- sense pins leave downwards, away from SW (item 8)
    f.tr("CHG_CBSET", [(0.25, 1.962), (0.25, 2.45), (-0.05, 2.75), (-0.05, 5.9), (0.5, 6.45), (0.5, 7.4)], 0.2)
    f.tr("CHG_MID", [(-0.25, 1.962), (-0.25, 2.45), (-0.5, 2.7), (-0.5, 6.9)], 0.2)
    f.two("R14", 1, -0.5, 6.9, 270)                        # 300R MID limiter (0603)
    f.two("R18", 1, -1.75, 3.25, 180)                      # ILIM
    f.tr("CHG_ILIM", [(-0.75, 1.962), (-0.75, 2.55), (-1.45, 3.25), (-1.75, 3.25)], 0.2)
    f.via("GND", -3.45, 3.25)
    f.tr("GND", [(-2.71, 3.25), (-3.45, 3.25)], 0.25)
    # TS network: R16 REGN-TS, R17 TS-GND, TH1 TS-GND
    f.two("R17", 1, -1.75, 4.35, 180)
    f.tr("CHG_TS", [(-1.25, 1.962), (-1.25, 3.85), (-1.75, 4.35)], 0.2)
    f.two("R16", 2, -1.75, 5.45, 180)
    f.tr("CHG_TS", [(-1.75, 4.35), (-1.75, 5.45)], 0.2)
    f.two("TH1", 1, -2.3, 6.75, 180)
    f.tr("CHG_TS", [(-1.75, 5.45), (-2.3, 6.0), (-2.3, 6.75)], 0.2)
    # PSEL pull-up
    f.two("R19", 1, -3.0, -2.5, 180)
    f.tr("CHG_PSEL", [(-1.25, -1.962), (-1.25, -2.5), (-3.0, -2.5)], 0.15)
    # status / control side (left): pull-ups and the CD fail-safe transistor
    f.two("R24", 1, -3.4, -1.55, 180)                      # PG pull-up
    f.tr("CHG_PG", [(-1.962, -1.25), (-2.6, -1.25), (-2.9, -1.55), (-3.4, -1.55)], 0.15)
    f.two("R23", 1, -3.4, -0.75, 180)                      # STAT pull-up
    f.tr("CHG_STAT", [(-1.962, -0.75), (-3.4, -0.75)], 0.15)
    f.two("R22", 1, -3.4, 1.9, 180)                        # INT pull-up
    f.tr("CHG_INT", [(-1.962, 1.25), (-2.5, 1.25), (-3.15, 1.9), (-3.4, 1.9)], 0.15)
    # CD: fail-safe pull-up to REGN, 2N7002 enable, DNP service link
    f.ic("Q2", -7.2, 0.0, 0)
    f.tr("CHG_CD", [(-1.962, -0.25), (-2.6, -0.25), (-2.85, 0.0), (-6.26, 0.0)], 0.15)
    f.two("R20", 1, -5.3, 0.0, 90)
    f.two("R26", 1, -5.3, 0.0, 270)
    f.two("R21", 1, -9.2, -0.95, 270)
    f.tr("CHG_EN", [(-8.14, -0.95), (-9.2, -0.95)], 0.15)
    return f


# ============================================================================== power: TPS62130A buck
def blk_buck(k: Kit, ox, oy, rot=0):
    """TI SLVSAG7F 11.1/11.2: input capacitor directly at PVIN/PGND, minimum SW copper, VOS routed as a
    quiet sense line to the output capacitor, FB divider at the pin with a short AGND return, thermal pad vias.
    Local frame = package top view (pins 1-3 SW on the left, 10-12 VIN on the right, 15/16 PGND on top)."""
    f = Frame(k, ox, oy, rot)
    f.ic("U7")
    for x, y in ((-0.45, -0.45), (0.45, -0.45), (-0.45, 0.45), (0.45, 0.45)):
        f.via("GND", x, y, size=0.45, drill=0.25)
    # PGND 15/16 and AGND/FSW/DEF 6/7/8 into the pad
    for x in (-0.75, -0.25):
        f.tr("GND", [(x, -1.4), (x, -0.7)], 0.24)
    for x in (-0.25, 0.25, 0.75):
        f.tr("GND", [(x, 1.4), (x, 0.7)], 0.24)
    # input capacitor: VIN pad over the PVIN corner, GND pad over the PGND pins (hot loop about 2 x 2 mm)
    f.two("C20", 1, 1.45, -3.35, 180)
    f.zone("PACK_P", [(1.1, -4.15), (3.6, -4.15), (3.6, 0.5), (1.12, 0.5), (1.12, -0.9), (1.75, -1.55), (1.1, -2.0)],
           prio=30, name="buck VIN")
    f.zone("GND", [(-1.05, -4.15), (0.02, -4.15), (0.02, -1.15), (-1.05, -1.15)], prio=30, name="buck PGND")
    for x, y in ((-1.45, -3.9), (-1.45, -2.9)):
        f.via("GND", x, y)
    f.tr("GND", [(-0.35, -3.9), (-1.45, -3.9)], 0.5)
    f.tr("GND", [(-0.35, -2.9), (-1.45, -2.9)], 0.5)
    # EN pull-up bridges the corner onto the VIN copper
    f.two("R27", 2, 1.0, -2.25, 0)
    f.tr("BUCK_EN", [(0.75, -1.4), (0.75, -1.9), (1.0, -2.25)], 0.15)
    # AVIN decoupling and soft-start capacitor on the right
    f.two("C21", 1, 2.6, 0.2, 270)
    f.via("GND", 2.6, 2.0)
    f.tr("GND", [(2.6, 1.16), (2.6, 2.0)], 0.3)
    f.two("C25", 1, 1.75, 1.75, 270)
    f.tr("BUCK_SS", [(1.4, 0.75), (1.75, 0.75), (1.75, 1.75)], 0.15)
    f.via("GND", 1.75, 3.5)
    f.tr("GND", [(1.75, 2.71), (1.75, 3.5)], 0.3)
    # inductor: SW pad 1.2 mm from the SW pins; output capacitors beyond it
    f.two("L2", 1, -3.45, -0.25, 180)
    f.zone("BUCK_SW", [(-1.15, -0.95), (-1.15, 0.45), (-3.95, 1.45), (-3.95, -1.95), (-2.9, -1.95)], prio=30, name="buck SW")
    f.two("C22", 1, -7.75, -1.3, 270)
    f.two("C23", 1, -7.75, -1.3, 90)
    f.zone("3V3_MAIN", [(-8.5, -2.05), (-5.3, -2.05), (-5.3, 1.5), (-6.35, 1.5), (-6.35, -0.55), (-8.5, -0.55)],
           prio=30, name="buck VOUT")
    for x, y in ((-6.3, 0.3), (-6.3, 1.05), (-5.75, 2.0), (-6.35, -2.55), (-5.65, -2.55)):
        f.via("3V3_MAIN", x, y)
    f.zone("3V3_MAIN", [(-6.7, -2.9), (-5.35, -2.9), (-5.35, 2.35), (-6.7, 2.35)], prio=29, name="buck VOUT vias")
    for x, y in ((-9.0, 0.6), (-9.0, 1.4), (-9.0, -3.2), (-9.0, -4.0)):
        f.via("GND", x, y)
    f.tr("GND", [(-7.75, 0.6), (-9.0, 0.6)], 0.6)
    f.tr("GND", [(-7.75, 1.0), (-9.0, 1.4)], 0.6)
    f.tr("GND", [(-7.75, -3.2), (-9.0, -3.2)], 0.6)
    f.tr("GND", [(-7.75, -3.6), (-9.0, -4.0)], 0.6)
    # VOS: quiet sense line over the top of the block to the output copper
    f.tr("3V3_MAIN", [(0.25, -1.4), (0.25, -1.75), (0.35, -1.95), (0.35, -4.4), (0.1, -4.65), (-5.5, -4.65), (-6.0, -4.15), (-6.0, -2.9)], 0.15)
    # feedback divider below the IC, PG pull-up, test pads
    f.two("R29", 1, -0.75, 2.6, 0)                          # FB - GND 100k
    f.tr("BUCK_FB", [(-0.75, 1.4), (-0.75, 2.6)], 0.15)
    f.via("GND", 0.21, 3.45)
    f.tr("GND", [(0.21, 2.6), (0.21, 3.45)], 0.25)
    f.two("R28", 2, -0.75, 2.6, 180)                        # 3V3 - FB 312k
    f.two("C24", 2, -0.75, 3.7, 180)                        # DNP feed-forward position
    f.tr("BUCK_FB", [(-0.75, 2.6), (-0.75, 3.7)], 0.15)
    f.tr("3V3_MAIN", [(-1.71, 2.6), (-1.71, 3.7)], 0.15)
    f.two("R30", 1, -2.5, 1.95, 270)                        # PG pull-up
    f.tr("BUCK_PG", [(-1.4, 0.75), (-1.75, 0.75), (-2.5, 1.5), (-2.5, 1.95)], 0.15)
    f.tr("3V3_MAIN", [(-1.71, 2.6), (-2.2, 2.6), (-2.5, 2.91), (-2.5, 3.85)], 0.2)
    f.via("3V3_MAIN", -2.5, 3.85)
    return f


# ============================================================================== display backlight boost
def blk_backlight(k: Kit, ox, oy, rot=0):
    """TI SNVSA40B 7.5: CIN at VIN/GND, shortest SW connection, COUT at the diode with its ground returned to
    the GND pin, FB resistor at the FB pin. Local frame = TPS61169 top view (pins 1-3 left, 5/4 right)."""
    f = Frame(k, ox, oy, rot)
    f.ic("U16")
    f.two("L3", 2, -1.25, -3.35, 180)                      # SW pad directly above pin 1
    f.zone("BL_SW", [(-2.0, -1.5), (-0.5, -1.5), (-0.38, -0.45), (-2.72, -0.6), (-2.72, -1.1)], prio=30, name="bl SW")
    f.two("D1", 2, -2.4, -0.85, 180)                       # anode at SW, cathode to COUT
    f.two("C56", 1, -4.55, 0.55, 0)                        # COUT: LED_A pad under the diode cathode, GND pad to pin 2
    f.zone("LED_A", [(-5.1, -1.15), (-4.0, -1.15), (-4.0, 1.3), (-5.1, 1.3)], prio=30, name="bl VOUT")
    f.zone("GND", [(-3.15, -0.2), (-0.35, -0.2), (-0.35, 0.2), (-2.05, 0.2), (-2.05, 1.3), (-3.15, 1.3)], prio=30, name="bl PGND")
    f.via("GND", -2.6, 1.85)
    f.tr("GND", [(-2.6, 1.0), (-2.6, 1.85)], 0.5)
    f.two("C55", 1, 2.25, -0.65, 0)                        # CIN at VIN
    f.tr("3V3_MAIN", [(0.838, -0.65), (2.25, -0.65)], 0.3)
    f.via("3V3_MAIN", 2.25, -1.75)
    f.tr("3V3_MAIN", [(2.25, -0.65), (2.25, -1.75)], 0.4)
    f.via("GND", 3.8, 0.45)
    f.tr("GND", [(3.8, -0.65), (3.8, 0.45)], 0.4)
    for x, y in ((-5.7, -2.4), (-5.7, -4.3)):
        f.via("3V3_MAIN", x, y)
    f.tr("3V3_MAIN", [(-4.78, -2.4), (-5.7, -2.4)], 0.5)
    f.tr("3V3_MAIN", [(-4.78, -4.3), (-5.7, -4.3)], 0.5)
    f.two("R56", 1, -0.84, 1.85, 270)                      # LED current sense at FB
    f.tr("LED_K", [(-0.838, 0.65), (-0.838, 1.85)], 0.25)
    f.via("GND", -0.84, 4.5)
    f.tr("GND", [(-0.84, 3.5), (-0.84, 4.5)], 0.3)
    f.two("R57", 1, 2.25, 0.65, 270)                       # PWM pull-down
    f.tr("LCD_BL_PWM", [(0.838, 0.65), (2.25, 0.65)], 0.15)
    return f


# ============================================================================== mechanical
SLOTS = [(41.2, 0.8, 42.2, 4.4), (45.8, 0.8, 46.8, 4.4)]    # SHT40 thermal-isolation slots (1.0 mm routed)


def blk_mech(k: Kit):
    k.place("H1", 3.2, 37.6)
    k.place("H2", 3.2, 72.0)
    k.place("H3", 12.0, 28.0)
    for x0, y0, x1, y1 in SLOTS:
        k.edge_rect(x0, y0, x1, y1)
    ds = k.add_extra_footprint("DS1", "SC", "Display_Orient_AFY240320A1-2.8INTH-C1_Envelope", "display envelope")
    k.place("DS1", 30.0, 48.55)
    # SHT40 tab: no copper pours on any layer (thermal isolation, SNS-02)
    k.keepout(rect(42.2, 0.0, 45.8, 4.9), ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"], "SHT40 tab: no pours", tracks=False, vias=True)
    # BMP581: no copper/vias under the sensing cavity (Bosch DS004-13 8.2)
    k.keepout(rect(48.65, 1.55, 49.75, 2.65), ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"], "BMP581 no copper under body")
    k.keepout(rect(48.15, 1.05, 50.25, 3.15), ["F.Cu"], "BMP581 body: no top pour", tracks=False, vias=True)


# ============================================================================== ESP32-S3 module
def blk_esp(k: Kit):
    """Module rotated so the PCB antenna overhangs the board cut-out at the left edge (Espressif hardware design
    guidelines 1.4.7: antenna outside the base board / board cut away under it, feed point at the board edge)."""
    k.place("U1", 13.05, 10.3, 90)
    # 3V3 decoupling directly under pins 1 (GND) / 2 (3V3)
    k.two_pin("C42", 1, (8.91, 20.6), 180)
    k.two_pin("C41", 1, (9.2, 21.9), 180)
    k.tr("GND", [(7.79, 19.4), (7.95, 20.6), (7.65, 21.9), (7.4, 23.0)], 0.4)
    k.tr("3V3_MAIN", [(9.06, 19.4), (8.91, 20.6), (9.2, 21.9), (9.2, 23.0)], 0.4)
    k.tr("3V3_MAIN", [(9.2, 21.9), (10.05, 21.9)], 0.4)
    k.tr("3V3_MAIN", [(9.06, 18.6), (9.06, 17.5)], 0.5)
    for p in ((9.2, 23.0), (10.05, 21.9), (9.06, 17.5)):
        k.via("3V3_MAIN", *p, **VIA)
    k.via("GND", 7.4, 23.0, **VIA)
    # module ground: pin 40 and the exposed pad
    k.via("GND", 7.79, 3.3, **VIA)
    k.tr("GND", [(7.79, 1.9), (7.79, 3.3)], 0.5)
    # EN: 10k / 1 uF and test pad
    k.tr("ESP_EN", [(10.33, 19.4), (10.33, 20.3), (10.75, 20.7), (10.75, 23.5), (10.0, 24.2)], 0.15)
    k.two_pin("C40", 1, (10.0, 24.2), 180)
    k.two_pin("R40", 1, (10.0, 25.2), 180)
    k.tr("ESP_EN", [(10.0, 24.2), (10.0, 25.2), (10.0, 26.0), (8.3, 26.0)], 0.15)
    k.place("TP11", 7.75, 26.0)
    k.via("GND", 8.2, 24.2, **VIA)
    k.tr("GND", [(9.04, 24.2), (8.2, 24.2)], 0.25)
    k.via("3V3_MAIN", 8.2, 25.05, **VIA)
    k.tr("3V3_MAIN", [(9.04, 25.2), (8.2, 25.05)], 0.25)


# ============================================================================== GNSS
def blk_gnss(k: Kit):
    """MAX-M10S: U.FL rotated so its centre pad faces RF_IN; 1.3 mm of 50-ohm line, TPD1E0B04 shunt at the line."""
    k.place("U17", 34.2, 12.6, 0)
    k.place("J5", 37.5, 3.55, 90)
    k.tr("GNSS_RF", [(37.5, 5.075), (37.5, 7.2)], RF_W)
    k.two_pin("D2", 1, (37.02, 6.2), 180)
    k.tr("GNSS_RF", [(37.5, 6.2), (37.02, 6.2)], RF_W)
    k.tr("GND", [(36.32, 6.2), (36.32, 7.0)], 0.3)
    k.tr("GND", [(36.32, 6.2), (35.9, 5.8), (35.55, 5.45)], 0.3)
    for p in ((35.55, 5.45), (39.45, 5.45), (39.45, 6.6), (36.0, 1.75), (39.0, 1.75), (34.9, 3.55), (40.1, 3.55)):
        k.via("GND", *p, **VIA)
    k.tr("GND", [(36.025, 4.3), (35.55, 5.45)], 0.4)
    k.tr("GND", [(38.975, 4.3), (39.45, 5.45)], 0.4)
    k.tr("GND", [(38.6, 7.2), (39.45, 6.6)], 0.4)
    k.tr("GND", [(36.025, 2.8), (36.0, 1.75)], 0.4)
    k.tr("GND", [(38.975, 2.8), (39.0, 1.75)], 0.4)
    k.tr("GND", [(36.025, 3.55), (34.9, 3.55)], 0.4)
    k.tr("GND", [(38.975, 3.55), (40.1, 3.55)], 0.4)
    # supply branch: 0R link (bead option, GNSS-01) and module-local capacitors under pins 7/8
    k.two_pin("C60", 1, (36.4, 19.15), 270)
    k.two_pin("C61", 1, (37.5, 19.15), 270)
    k.tr("3V3_GNSS", [(36.4, 18.0), (36.4, 19.15)], 0.4)
    k.tr("3V3_GNSS", [(37.5, 18.0), (37.5, 19.15)], 0.4)
    k.tr("3V3_GNSS", [(36.4, 18.75), (37.5, 18.75)], 0.4)
    k.two_pin("R31", 2, (39.0, 19.6), 0)
    k.tr("3V3_GNSS", [(37.5, 18.75), (38.3, 18.75), (39.0, 19.45)], 0.4)
    k.via("3V3_MAIN", 41.6, 19.6, **VIA)
    k.tr("3V3_MAIN", [(40.65, 19.6), (41.6, 19.6)], 0.4)
    for x in (36.4, 37.5):
        k.via("GND", x, 21.05, **VIA)
        k.tr("GND", [(x, 20.11), (x, 21.05)], 0.3)
    k.via("GND", 29.8, 19.0, **VIA)
    k.tr("GND", [(29.8, 17.9), (29.8, 19.0)], 0.4)
    k.place("TP16", 30.9, 20.2)
    k.tr("GNSS_RX", [(30.9, 18.0), (30.9, 20.2)], 0.15)
    k.place("TP15", 33.1, 20.2)
    k.tr("GNSS_PPS", [(33.1, 18.0), (33.1, 20.2)], 0.15)


# ============================================================================== sensors
def blk_env_sensors(k: Kit):
    """SHT40 on the slotted tab (no pours, four traces down the margins, nothing under the body);
    BMP581 with nothing routed under the body (Bosch DS004-13 8.2)."""
    k.place("U33", 44.0, 1.9, 0)
    k.tr("I2C_SDA", [(43.3, 1.5), (42.72, 1.5), (42.72, 6.3)], 0.15)
    k.tr("I2C_SCL", [(43.3, 2.3), (43.05, 2.3), (43.05, 6.3)], 0.15)
    k.tr("GND", [(44.7, 1.5), (45.28, 1.5), (45.28, 5.4)], 0.15)
    k.tr("3V3_MAIN", [(44.7, 2.3), (44.95, 2.3), (44.95, 5.4)], 0.15)
    k.two_pin("C37", 1, (44.6, 5.85), 0)
    k.tr("3V3_MAIN", [(44.95, 5.4), (44.6, 5.85)], 0.15)
    k.tr("GND", [(45.28, 5.4), (45.56, 5.85)], 0.15)
    k.via("3V3_MAIN", 44.6, 6.8, **VIA)
    k.tr("3V3_MAIN", [(44.6, 5.85), (44.6, 6.8)], 0.2)
    k.via("GND", 45.6, 6.8, **VIA)
    k.tr("GND", [(45.56, 5.85), (45.6, 6.8)], 0.2)
    # BMP581
    bx = 49.2
    k.place("U32", bx, 2.1, 0)
    k.tr("3V3_MAIN", [(bx - 0.5, 1.338), (bx - 0.5, 0.75), (bx - 1.62, 0.75), (bx - 1.62, 1.85), (bx - 0.762, 1.85)], 0.15)
    k.tr("3V3_MAIN", [(bx - 1.62, 1.85), (bx - 1.62, 5.3)], 0.15)
    k.tr("I2C_SCL", [(bx - 0.762, 2.35), (bx - 1.0, 2.35), (bx - 1.22, 2.6), (bx - 1.22, 4.6)], 0.15)
    k.tr("I2C_SDA", [(bx, 2.862), (bx, 4.6)], 0.15)
    k.tr("GND", [(bx, 1.338), (bx, 0.8), (bx + 0.5, 0.8), (bx + 0.5, 1.338)], 0.15)
    k.tr("GND", [(bx + 0.5, 0.8), (bx + 1.35, 0.8), (bx + 1.35, 1.85), (bx + 0.762, 1.85)], 0.15)
    k.tr("GND", [(bx + 1.35, 0.8), (bx + 2.2, 0.8)], 0.15)
    k.via("GND", bx + 2.3, 1.0, **VIA)
    k.tr("GND", [(bx - 0.5, 2.862), (bx - 0.5, 3.9)], 0.15)
    k.tr("GND", [(bx + 0.5, 2.862), (bx + 0.5, 3.9)], 0.15)
    k.via("GND", bx - 0.55, 4.05, size=0.45, drill=0.3)
    k.via("GND", bx + 0.55, 4.05, size=0.45, drill=0.3)
    k.two_pin("C36", 1, (bx + 1.85, 2.35), 0)
    k.tr("3V3_MAIN", [(bx + 0.762, 2.35), (bx + 1.85, 2.35)], 0.15)
    k.via("3V3_MAIN", bx + 1.85, 3.3, **VIA)
    k.tr("3V3_MAIN", [(bx + 1.85, 2.35), (bx + 1.85, 3.3)], 0.2)
    k.via("GND", bx + 2.81, 3.3, **VIA)
    k.tr("GND", [(bx + 2.81, 2.35), (bx + 2.81, 3.3)], 0.2)
    k.two_pin("C35", 1, (bx - 1.62, 5.3), 270)
    k.via("3V3_MAIN", bx - 0.7, 5.75, **VIA)
    k.tr("3V3_MAIN", [(bx - 1.62, 5.3), (bx - 0.7, 5.75)], 0.2)
    k.via("GND", bx - 1.62, 7.15, **VIA)
    k.tr("GND", [(bx - 1.62, 6.26), (bx - 1.62, 7.15)], 0.2)


# ============================================================================== USB-C input
def blk_usb(k: Kit):
    """USB4105 at the bottom edge. ESD array in straight-through routing 1.1 mm from the pads (TI SLVSBO7 layout),
    TUSB320LAI next to it, D+/D- joined at the connector and taken to L4 as a 90-ohm pair (FS only on ESP32-S3)."""
    k.place("J1", 8.0, 80.6, 0)
    k.place("U2", 8.0, 74.6, 90)            # columns x: 7.0 CC1, 7.5 D-, 8.0 GND, 8.5 D+, 9.0 CC2
    yb, yt = 74.985, 74.215
    # connector -> ESD array
    k.tr("USB_CC1", [(6.75, 76.4), (6.75, 76.0), (7.0, 75.6), (7.0, yb)], 0.2)
    k.tr("USB_DN", [(7.25, 76.4), (7.25, 76.0), (7.5, 75.6), (7.5, yb)], 0.2)
    k.tr("USB_DN", [(7.25, 77.4), (7.25, 78.3), (8.25, 78.3), (8.25, 77.4)], 0.2)        # B7-A7 under the shell
    k.tr("USB_DP", [(7.75, 76.4), (7.75, 75.95), (8.75, 75.95), (8.75, 76.4)], 0.2)        # A6-B6 link
    k.tr("USB_DP", [(8.5, 75.95), (8.5, yb)], 0.2)
    k.tr("USB_CC2", [(9.75, 76.4), (9.75, 76.0), (9.0, 75.3), (9.0, yb)], 0.2)
    # straight through the array
    for net, x in (("USB_CC1", 7.0), ("USB_DN", 7.5), ("GND", 8.0), ("USB_DP", 8.5), ("USB_CC2", 9.0)):
        k.tr(net, [(x, yb), (x, yt)], 0.2)
    # D+/D- to L4, ground via of the array between them
    k.tr("USB_DN", [(7.5, yt), (7.5, 73.75), (7.4, 73.45)], 0.2)
    k.tr("USB_DP", [(8.5, yt), (8.5, 73.75), (8.6, 73.45)], 0.2)
    k.via("USB_DN", 7.4, 73.4, **VIA)
    k.via("USB_DP", 8.6, 73.4, **VIA)
    k.tr("GND", [(8.0, yt), (8.0, 72.9)], 0.25)
    k.via("GND", 8.0, 72.85, **VIA)
    # CC controller
    k.place("U4", 7.4, 70.9, 90)            # CC1 pad at x 7.2, CC2 pad at x 7.6 on the bottom side
    k.tr("USB_CC1", [(7.0, yt), (6.6, 73.8), (6.6, 72.6), (7.2, 72.0), (7.2, 71.7)], 0.15)
    k.tr("USB_CC2", [(9.0, yt), (9.0, 72.35), (8.75, 72.1), (7.85, 72.1), (7.6, 71.85), (7.6, 71.7)], 0.15)
    # VDD decoupling at pins 12 (3V3) / 10-11 (GND) on the left side
    k.two_pin("C3", 1, (5.6, 71.5), 90)
    k.tr("3V3_MAIN", [(6.575, 71.5), (5.6, 71.5)], 0.2)
    k.tr("GND", [(6.575, 71.1), (6.1, 71.1), (6.1, 70.7), (6.575, 70.7)], 0.2)
    k.tr("GND", [(6.1, 70.7), (5.6, 70.54)], 0.2)
    k.via("3V3_MAIN", 5.6, 72.45, **VIA)
    k.tr("3V3_MAIN", [(5.6, 71.5), (5.6, 72.45)], 0.25)
    k.via("GND", 5.6, 69.65, **VIA)
    k.tr("GND", [(5.6, 70.54), (5.6, 69.65)], 0.25)
    k.tr("GND", [(8.225, 71.5), (9.4, 71.5)], 0.2)                 # pin 3 into the J4 hold-down (GND) land
    # VBUS_DET 900k, OUT1..3 pull-ups above the controller
    k.two_pin("R10", 2, (8.85, 67.6), 0)
    k.tr("TUSB_VDET", [(8.225, 71.1), (8.85, 71.1), (8.85, 67.6)], 0.15)
    k.two_pin("R11", 1, (7.6, 69.2), 90)
    k.tr("TUSB_OUT1", [(7.6, 70.175), (7.6, 69.2)], 0.15)
    k.two_pin("R12", 1, (6.6, 69.2), 90)
    k.tr("TUSB_OUT2", [(7.2, 70.175), (7.2, 69.75), (6.65, 69.2)], 0.15)
    k.two_pin("R13", 1, (8.3, 69.25), 90)
    k.tr("TUSB_OUT3", [(8.225, 70.3), (8.3, 70.0), (8.3, 69.25)], 0.15)
    k.tr("3V3_MAIN", [(6.6, 68.24), (8.3, 68.29)], 0.2)
    k.via("3V3_MAIN", 5.75, 68.24, **VIA)
    k.tr("3V3_MAIN", [(6.6, 68.24), (5.75, 68.24)], 0.25)
    # VBUS: right pads on top to the eFuse, left pads joined on L4
    k.tr("VBUS", [(10.4, 76.4), (10.4, 75.45)], 0.5)
    k.tr("VBUS", [(5.6, 76.4), (5.6, 75.5)], 0.5)
    k.via("VBUS", 5.6, 75.35, **VIA)
    k.via("VBUS", 10.4, 75.3, **VIA)
    k.tr("VBUS", [(5.6, 75.35), (6.3, 76.05), (9.7, 76.05), (10.4, 75.3)], 0.6, "B.Cu")
    k.tr("GND", [(4.8, 76.4), (4.8, 75.9), (4.45, 75.55)], 0.5)
    k.via("GND", 4.4, 75.45, **VIA)
    k.tr("GND", [(11.2, 76.4), (11.2, 75.6)], 0.5)
    k.via("GND", 11.3, 75.45, **VIA)
    # shell: four stakes tied together, single 0R to ground (treatment TBD)
    k.tr("USB_SHIELD", [(3.68, 77.5), (3.68, 81.67)], 0.4, "B.Cu")
    k.tr("USB_SHIELD", [(12.32, 77.5), (12.32, 81.67)], 0.4, "B.Cu")
    k.tr("USB_SHIELD", [(3.68, 81.67), (4.4, 82.9), (11.6, 82.9), (12.32, 81.67)], 0.4, "B.Cu")
    k.two_pin("R1", 1, (13.6, 81.67), 0)
    k.tr("USB_SHIELD", [(12.32, 81.67), (13.6, 81.67)], 0.3)
    k.via("GND", 14.56, 82.7, **VIA)
    k.tr("GND", [(14.56, 81.67), (14.56, 82.7)], 0.3)


def blk_efuse(k: Kit, ox, oy):
    """TPS259474L (TI SLVSFC9C 8.4): RILM / ITIMER parts at the pins, single ground point at pin 8, >= 1 uF at OUT,
    IN and OUT copper with vias. IN enters from the top end of the centre pads, OUT leaves at the bottom end.
    The 232k/442k divider taps to VBUS/GND are high-impedance and left to the router."""
    f = Frame(k, ox, oy, 0)
    f.ic("U3")
    f.zone("VBUS", [(-0.42, -0.9), (-0.42, -1.75), (-1.35, -1.75), (-1.35, -3.4), (0.3, -3.4), (0.3, -1.75), (-0.08, -1.75), (-0.08, -0.9)],
           prio=30, name="efuse IN")
    f.two("C1", 1, -0.55, -2.65, 0)
    f.via("GND", 1.0, -3.7)
    f.tr("GND", [(1.0, -2.65), (1.0, -3.7)], 0.4)
    f.zone("VBUS_PROT", [(0.08, 0.9), (0.42, 0.9), (0.42, 1.75), (1.3, 1.75), (1.3, 4.3), (-0.3, 4.3), (-0.3, 1.75), (0.08, 1.75)],
           prio=30, name="efuse OUT")
    f.two("C2", 1, 0.55, 2.45, 0)
    for x, y in ((0.05, 3.75), (0.95, 3.75)):
        f.via("VBUS_PROT", x, y)
    f.two("R6", 1, 1.95, -0.3, 0)
    f.tr("EFUSE_ILM", [(0.9, -0.225), (1.5, -0.225), (1.67, -0.3), (1.95, -0.3)], 0.15)
    f.two("C9", 1, 1.95, -1.35, 0)
    f.tr("EFUSE_ITIMER", [(0.9, -0.7), (1.3, -0.7), (1.67, -1.1), (1.67, -1.35), (1.95, -1.35)], 0.15)
    f.tr("GND", [(0.9, 0.225), (1.6, 0.225), (2.0, 0.6), (2.91, 0.6)], 0.2)
    f.tr("GND", [(2.91, -1.35), (2.91, 1.2)], 0.3)
    f.via("GND", 2.91, 1.25)
    f.tr("GND", [(2.1, 2.45), (2.91, 1.7), (2.91, 1.25)], 0.4)
    # UV divider
    f.two("R2", 2, -1.95, -0.95, 180)
    f.tr("EFUSE_UV", [(-0.9, -0.7), (-1.4, -0.7), (-1.65, -0.95), (-1.95, -0.95)], 0.15)
    f.two("R3", 1, -1.95, -2.0, 180)
    f.tr("EFUSE_UV", [(-1.95, -0.95), (-1.95, -2.0)], 0.15)
    # OV divider
    f.two("R4", 2, -4.6, -0.225, 90)
    f.tr("EFUSE_OV", [(-0.9, -0.225), (-4.6, -0.225)], 0.15)
    f.two("R5", 1, -4.6, 0.85, 270)
    f.tr("EFUSE_OV", [(-4.6, -0.225), (-4.6, 0.85)], 0.15)
    # PG pull-up, PGTH divider from OUT
    f.two("R7", 1, -2.6, 1.2, 180)
    f.tr("EFUSE_PG", [(-0.9, 0.225), (-1.7, 0.225), (-2.3, 0.85), (-2.6, 1.2)], 0.15)
    f.two("R8", 2, -1.1, 2.4, 270)
    f.tr("EFUSE_PGTH", [(-0.725, 0.875), (-0.725, 1.5), (-1.1, 1.9), (-1.1, 2.4)], 0.15)
    f.tr("VBUS_PROT", [(-1.1, 3.36), (-0.3, 3.36)], 0.2)
    f.two("R9", 1, -2.1, 2.4, 180)
    f.tr("EFUSE_PGTH", [(-1.1, 2.4), (-2.1, 2.4)], 0.15)
    return f


# ============================================================================== project rules
POWER_NETS = ["VBUS", "VBUS_PROT", "PACK_P", "BAT_P", "BAT_N", "BAT_MID", "PROT_DRAIN", "CHG_PMID", "CHG_SW", "CHG_SNS",
              "CHG_CBSET", "BUCK_SW", "BL_SW", "LED_A"]
RAIL_NETS = ["3V3_MAIN", "3V3_GNSS", "3V3_SD", "3V3_ADSB", "3V3_EXP", "3V0_RF_QUIET", "1V8_LOGIC", "1V8_AUDIO_SW",
             "1V1_ADSB", "LCD_VCC", "ADSB_DET_VP", "CHG_REGN", "SX_VREG", "SX_DCC_SW", "SX_VR_PA", "LED_K"]
RF_NETS = ["GNSS_RF", "ADSB_ANT", "ADSB_L1_IN", "ADSB_L1_OUT", "ADSB_S1_IN", "ADSB_S1_OUT", "ADSB_L2_IN", "ADSB_L2_OUT",
           "ADSB_S2_IN", "ADSB_DET_IN", "ADSB_INHI", "LORA_RFO", "LORA_PA", "LORA_TXF1", "LORA_TXF2", "LORA_TX_SW",
           "LORA_RX_SW", "LORA_RFI_N", "LORA_RFI_P", "LORA_RFC", "LORA_ANTF", "LORA_ANT"]

DRU = """(version 1)
# StratosCore candidate A2 - custom rules. Stack: JLC04161H-3313 candidate (docs/PCB_STACKUP.md).
(rule rf_pour_gap
  (condition "A.NetClass == 'RF50' && B.Type == 'Zone'")
  (constraint clearance (min 0.3mm)))
(rule usb_pair
  (condition "A.NetClass == 'USB90' && A.inDiffPair('USB_D')")
  (constraint diff_pair_gap (min 0.18mm) (opt 0.2mm) (max 0.6mm)))
"""


def project_rules():
    import json
    pro = OUT / f"{PROJECT}.kicad_pro"
    data = json.loads(pro.read_text(encoding="utf-8"))
    base = {"bus_width": 12, "diff_pair_gap": 0.25, "diff_pair_via_gap": 0.25, "diff_pair_width": 0.2,
            "line_style": 0, "microvia_diameter": 0.3, "microvia_drill": 0.1, "pcb_color": "rgba(0, 0, 0, 0.000)",
            "schematic_color": "rgba(0, 0, 0, 0.000)", "wire_width": 6, "priority": 2147483647, "tuning_profile": ""}
    classes = [
        dict(base, name="Default", clearance=0.15, track_width=0.15, via_diameter=0.5, via_drill=0.3),
        dict(base, name="Power", clearance=0.2, track_width=0.5, via_diameter=0.6, via_drill=0.3, priority=1),
        dict(base, name="Rail", clearance=0.15, track_width=0.3, via_diameter=0.5, via_drill=0.3, priority=2),
        dict(base, name="RF50", clearance=0.2, track_width=RF_W, via_diameter=0.5, via_drill=0.3, priority=0),
        dict(base, name="USB90", clearance=0.15, track_width=USB_W, via_diameter=0.5, via_drill=0.3,
             diff_pair_width=USB_W, diff_pair_gap=USB_S, priority=0),
    ]
    pats = [{"netclass": "Power", "pattern": p} for p in POWER_NETS]
    pats += [{"netclass": "Rail", "pattern": p} for p in RAIL_NETS]
    pats += [{"netclass": "RF50", "pattern": p} for p in RF_NETS]
    pats += [{"netclass": "USB90", "pattern": "USB_D*"}]
    ns = data.setdefault("net_settings", {})
    ns["classes"] = classes
    ns["netclass_patterns"] = pats
    ns.setdefault("meta", {"version": 4})
    pro.write_text(json.dumps(data, indent=2), encoding="utf-8")
    (OUT / f"{PROJECT}.kicad_dru").write_text(DRU, encoding="utf-8")


# ============================================================================== planes
def planes(k: Kit, shape):
    pts = [(x, y) for x, y in shape.buffer(-0.3).exterior.coords][:-1]
    k.zone("GND", "F.Cu", pts, prio=0, clearance=0.2, connect="solid", name="GND top pour")
    k.zone("GND", "In1.Cu", pts, prio=0, clearance=0.2, connect="solid", name="GND plane L2 (unbroken)")
    k.zone("3V3_MAIN", "In2.Cu", pts, prio=0, clearance=0.2, connect="solid", name="3V3_MAIN plane L3")
    k.zone("GND", "B.Cu", pts, prio=0, clearance=0.2, connect="solid", name="GND bottom pour")
    # L2 stays a pure plane, L3 carries no routed signal: block the router from both
    k.keepout(pts, ["In1.Cu"], "L2: plane only (no tracks)", tracks=True, vias=False, copper=False)


def park_unplaced(k: Kit):
    """Development aid: anything not yet placed is parked right of the board."""
    x, y = 66.0, 2.0
    for ref in sorted(k.fps):
        if ref in k.placed:
            continue
        k.place(ref, x, y, 0)
        y += 4.0
        if y > 82:
            y = 2.0
            x += 6.0


def main(only=None):
    netlist = OUT / "reports" / "netlist.xml"
    subprocess.run([CLI, "sch", "export", "netlist", "--format", "kicadxml", "-o", str(netlist),
                    str(OUT / f"{PROJECT}.kicad_sch")], check=True, capture_output=True)
    project_rules()
    k = Kit(netlist, OUT / "libs" / "SC.pretty", OUT / f"{PROJECT}.kicad_pcb")
    setup(k)
    k.add_footprints()
    blk_mech(k)
    blk_esp(k)
    blk_gnss(k)
    blk_env_sensors(k)
    blk_usb(k)
    blk_efuse(k, 18.6, 76.9)
    k.place("TP1", 12.4, 74.0)
    k.place("TP2", 21.4, 74.0)
    k.zone("VBUS", "F.Cu", [(10.0, 75.7), (10.0, 73.5), (18.9, 73.5), (18.9, 74.3), (10.8, 74.3), (10.8, 75.7)], prio=29, name="VBUS feed")
    blk_charger(k, 32.0, 48.0, 0)
    blk_buck(k, 48.5, 54.5, 0)
    blk_backlight(k, 25.3, 61.2, 0)
    planes(k, SHAPE[0])
    park_unplaced(k)
    k.save()
    return k


if __name__ == "__main__":
    main()
