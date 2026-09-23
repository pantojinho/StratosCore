"""STEP models for the parts that have no KiCad library model, plus the display module and a
printed-enclosure concept. Geometry = published envelope dimensions only (no invented detail
beyond simple visual cues). Run with a Python that has CadQuery:

    <venv-with-cadquery>/python tools/models3d.py

Outputs: kicad/libs/SC.3dshapes/*.step (per-footprint models) and mech/*.step (enclosure).
All models are ENVELOPES for fit/collision review, not manufacturer CAD.
"""
from __future__ import annotations

from pathlib import Path

import cadquery as cq

ROOT = Path(__file__).resolve().parent.parent
LIB = ROOT / "kicad" / "libs" / "SC.3dshapes"
MECH = ROOT / "mech"
LIB.mkdir(parents=True, exist_ok=True)
MECH.mkdir(parents=True, exist_ok=True)

# KiCad footprint coordinates are y-down; STEP/3D is y-up. Every model below is authored in
# footprint coordinates with y already negated where it matters.


def save(shape, name, folder=LIB):
    cq.exporters.export(shape, str(folder / f"{name}.step"))
    print("wrote", name)


def box(x0, y0, x1, y1, z0, z1):
    """Box from footprint-coordinate rectangle (y down) to 3D (y up)."""
    return (cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False)
            .translate((x0, -y1, z0)))


def display(standoff=5.0):
    """Orient AFY240320A1-2.8INTH-C1: 50.45 x 69.90 x 4.22 mm, active area 43.20 x 57.60 mm
    (rev J spec). Active-area offset inside the outline and FPC tail geometry are TBD from the
    controlled drawing -> active area centred horizontally, 1.6 mm toward the FPC end; tails
    drawn as a flat fold toward the PCB connectors at the bottom edge. Origin = module centre,
    z = 0 at the module underside (the footprint adds the standoff)."""
    W, H, T = 50.45, 69.90, 4.22
    frame = box(-W / 2, -H / 2, W / 2, H / 2, 0, T - 0.7)
    glass = box(-W / 2 + 0.2, -H / 2 + 0.2, W / 2 - 0.2, H / 2 - 0.2, T - 0.7, T)
    aa = box(-21.6, -28.8 - 1.6, 21.6, 28.8 - 1.6, T - 0.05, T + 0.01)
    # FPC tails (40 p: 20.5 wide; 6 p: ~4.7 wide) folding down behind the module bottom edge
    tail40 = box(1.0 - 10.25, H / 2, 1.0 + 10.25, H / 2 + 1.2, -standoff + 0.3, T - 1.0)   # centred on J3 (board x 31)
    tail6 = box(-16.8 - 2.35, H / 2, -16.8 + 2.35, H / 2 + 1.2, -standoff + 0.3, T - 1.0)   # centred on J4 (board x 13.2)
    asm = (cq.Assembly(name="AFY240320A1_envelope")
           .add(frame, name="frame", color=cq.Color(0.75, 0.75, 0.78))
           .add(glass, name="cover_glass", color=cq.Color(0.08, 0.08, 0.1, 0.9))
           .add(aa, name="active_area", color=cq.Color(0.05, 0.25, 0.55))
           .add(tail40, name="fpc40", color=cq.Color(0.85, 0.55, 0.1))
           .add(tail6, name="fpc6", color=cq.Color(0.85, 0.55, 0.1)))
    asm.save(str(LIB / "Display_Orient_AFY240320A1-2.8INTH-C1_Envelope.step"))
    print("wrote display")


def holder_2s():
    """Two 21700 cells in a series holder, envelope 82.2 x 45.1 x 17.3 mm (Keystone 1123 class
    reference). Footprint origin = holder centre; model modelled on the component side (+z),
    KiCad mirrors it to the board bottom when the footprint is flipped."""
    L, Wd, Hh = 82.2, 45.1, 17.27
    base = box(-Wd / 2, -L / 2, Wd / 2, L / 2, 0, 2.0)
    walls = (box(-Wd / 2, -L / 2, Wd / 2, -L / 2 + 3, 0, Hh)
             .union(box(-Wd / 2, L / 2 - 3, Wd / 2, L / 2, 0, Hh)))
    cells = None
    for cx in (-11.0, 11.0):
        c = (cq.Workplane("XZ").center(cx, 2.0 + 10.85).circle(10.85).extrude(70.2 / 2, both=True))
        cells = c if cells is None else cells.union(c)
    asm = (cq.Assembly(name="holder_2S_21700")
           .add(base.union(walls), name="holder", color=cq.Color(0.1, 0.1, 0.1))
           .add(cells, name="cells_M50A_envelope", color=cq.Color(0.15, 0.45, 0.2)))
    asm.save(str(LIB / "BatteryHolder_2S_21700_TBD.step"))
    print("wrote holder")


def xf3m(pins, B, name):
    body = box(-B / 2, -1.0, B / 2, 5.55, 0, 2.0)
    slot = box(-B / 2 + 0.8, 3.8, B / 2 - 0.8, 5.6, 0.6, 1.4)
    lever = box(-B / 2 + 0.4, 4.2, B / 2 - 0.4, 5.55, 1.6, 2.0)
    asm = (cq.Assembly(name=name).add(body.cut(slot), name="housing", color=cq.Color(0.9, 0.9, 0.85))
           .add(lever, name="lock", color=cq.Color(0.2, 0.2, 0.2)))
    asm.save(str(LIB / f"{name}.step"))


def simple(name, x0, y0, x1, y1, h, color=(0.2, 0.2, 0.2), extra=None):
    s = box(x0, y0, x1, y1, 0, h)
    if extra is not None:
        s = s.union(extra)
    asm = cq.Assembly(name=name).add(s, name="body", color=cq.Color(*color))
    asm.save(str(LIB / f"{name}.step"))


def enclosure(board_w=60.0, board_h=84.0, wall=2.0, depth=37.0):
    """Printed two-part enclosure concept (about 64 x 88 x 37 mm, MECHANICAL_RF_FLOORPLAN.md):
    front bezel with display window and back shell with a battery door. Openings: USB-C, microSD,
    two side buttons, JST expansion (rear), three U.FL->SMA bulkhead holes, vent/acoustic holes.
    Board coordinates: origin at the board top-left, y down; enclosure built around it."""
    ox, oy = board_w / 2, board_h / 2
    W, H = board_w + 2 * wall + 0.8, board_h + 2 * wall + 0.8
    front_h, back_h = 11.5, depth - 11.5   # display top = PCB + 5.0 standoff + 4.22 -> 9.2 mm < 11.5 - 2 wall
    # z: PCB top at 0; front shell above, back shell below
    fb = (cq.Workplane("XY").box(W, H, front_h).translate((0, 0, front_h / 2))
          .edges("|Z").fillet(4.0))
    fb = fb.cut(cq.Workplane("XY").box(W - 2 * wall, H - 2 * wall, front_h - wall)
                .translate((0, 0, (front_h - wall) / 2)))
    # display viewing window over the active area (display centred at board y 48.55)
    dy = -(48.55 - oy) + 1.6
    fb = fb.cut(cq.Workplane("XY").box(44.0, 58.4, 3 * wall).translate((0, dy, front_h)))
    bs = (cq.Workplane("XY").box(W, H, back_h).translate((0, 0, -back_h / 2))
          .edges("|Z").fillet(4.0))
    bs = bs.cut(cq.Workplane("XY").box(W - 2 * wall, H - 2 * wall, back_h - wall)
                .translate((0, 0, -(back_h - wall) / 2)))
    # battery door outline (separate part) - cut as a thin groove to show it
    door = cq.Workplane("XY").box(46.0, 83.0, wall).translate((37.35 - ox, 0, -back_h + wall / 2))
    bs = bs.cut(door.faces(">Z").shell(-0.4)) if False else bs

    def at(x, y):
        return x - ox, -(y - oy)
    # USB-C (bottom edge, board x 13.5), 9.5 x 3.6 mm opening centred 1.6 mm above PCB top
    ux, _ = at(8.0, 84)
    bs = bs.cut(cq.Workplane("XY").box(10.0, 3 * wall, 4.0).translate((ux, -H / 2, 1.6)))
    fb = fb.cut(cq.Workplane("XY").box(10.0, 3 * wall, 4.0).translate((ux, -H / 2, 1.6)))
    # microSD slot (left edge, board y 50)
    _, sy = at(0, 50)
    fb = fb.cut(cq.Workplane("XY").box(3 * wall, 12.5, 2.2).translate((-W / 2, sy, 1.0)))
    # side buttons (right edge, board y 52 / 59): plunger holes
    for by in (53.5, 59.5):
        _, py = at(60, by)
        fb = fb.cut(cq.Workplane("YZ").circle(1.4).extrude(3 * wall).translate((W / 2 - 2 * wall, py, 0.8)))
    # SMA bulkheads for GNSS / ADS-B (top edge) and LoRa (bottom edge): 6.5 mm holes in the back shell
    for bx, by, edge in ((29.0, 0, "top"), (57.2, 0, "top"), (57.2, 84, "bottom")):
        x, _ = at(bx, by)
        yy = H / 2 if edge == "top" else -H / 2
        bs = bs.cut(cq.Workplane("XZ").circle(3.25).extrude(3 * wall, both=True)
                    .translate((min(max(x, -W / 2 + 6), W / 2 - 6), yy, -8.0)))
    # vents: static pressure (BMP581) and humidity (SHT40) at the top edge, acoustic port on the back
    for vx, d in ((48.6, 1.5), (44.0, 1.5)):
        x, _ = at(vx, 0)
        fb = fb.cut(cq.Workplane("XZ").circle(d / 2).extrude(3 * wall, both=True).translate((x, H / 2, 1.0)))
    mx, my = at(3.4, 47.2)
    bs = bs.cut(cq.Workplane("XY").circle(0.6).extrude(3 * wall, both=True).translate((mx, my, -back_h)))
    # expansion connector opening (rear, JST GH vertical at board 4.2,16 rotated)
    ex, ey = at(4.2, 58.3)
    bs = bs.cut(cq.Workplane("XY").box(6.0, 20.0, 3 * wall).translate((ex + 1.0, ey, -back_h)))
    save(fb, "Enclosure_Front_Bezel", MECH)
    save(bs, "Enclosure_Back_Shell", MECH)


if __name__ == "__main__":
    display()
    holder_2s()
    xf3m(40, 23.1, "Omron_XF3M-4015-1B_1x40-1MP_P0.5mm_Horizontal")
    xf3m(6, 6.1, "Omron_XF3M-0615-1B_1x06-1MP_P0.5mm_Horizontal")
    plunger = box(-0.8, 1.775, 0.8, 2.45, 0.2, 1.05)
    simple("SW_Alps_SKSCLCE010_SidePush", -1.75, -1.775, 1.75, 1.775, 1.25, (0.75, 0.75, 0.75), plunger)
    simple("TDK_T5838_LGA-7_3.5x2.65mm_BottomPort", -2.5, -1.325, 1.0, 1.325, 0.98, (0.8, 0.8, 0.82))
    simple("TAI-SAW_TA2003A_SMD-6_3.0x3.0mm", -1.5, -1.5, 1.5, 1.5, 1.4, (0.8, 0.8, 0.82))
    simple("BeRex_BLB01_DFN-8-1EP_2x2mm_P0.5mm", -1.0, -1.0, 1.0, 1.0, 0.55, (0.1, 0.1, 0.1))
    enclosure()
