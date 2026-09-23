"""Custom footprints for the one-shot candidate, generated from the dimensions recorded in
docs/ and the manufacturer drawings cited next to each function. Every footprint carries
its source in the description; none is a released land pattern."""
from __future__ import annotations

import uuid
from pathlib import Path


def _u(*p):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "/".join(map(str, p))))


class FP:
    def __init__(self, name: str, descr: str, smd: bool = True, board_only: bool = False,
                 exclude_bom: bool = False):
        self.name, self.descr = name, descr
        self.items: list = []
        self.attr = "smd" if smd else "through_hole"
        self.board_only = board_only
        self.exclude_bom = exclude_bom
        self.model = None

    def pad(self, num, x, y, w, h, shape="roundrect", layers=None, rr=0.25, paste=True,
            drill=None, rot=0, extra=""):
        if drill is not None:
            lay = layers or '"*.Cu" "*.Mask"'
            kind = "thru_hole" if num != "" else "np_thru_hole"
            dr = f"(drill {drill})"
        else:
            lay = layers or ('"F.Cu" "F.Paste" "F.Mask"' if paste else '"F.Cu" "F.Mask"')
            kind = "smd"
            dr = ""
        rrs = f" (roundrect_rratio {rr})" if shape == "roundrect" else ""
        self.items.append(f'(pad "{num}" {kind} {shape} (at {x:.4f} {y:.4f} {rot}) (size {w:.4f} {h:.4f}) {dr} '
                          f'(layers {lay}){rrs}{extra} (uuid "{_u(self.name, "pad", num, x, y)}"))')

    def rect(self, layer, x0, y0, x1, y1, width=0.1, fill=False):
        f = "yes" if fill else "no"
        self.items.append(f'(fp_rect (start {x0:.4f} {y0:.4f}) (end {x1:.4f} {y1:.4f}) '
                          f'(stroke (width {width}) (type default)) (fill {f}) (layer "{layer}") '
                          f'(uuid "{_u(self.name, layer, x0, y0, x1, y1)}"))')

    def line(self, layer, x0, y0, x1, y1, width=0.12):
        self.items.append(f'(fp_line (start {x0:.4f} {y0:.4f}) (end {x1:.4f} {y1:.4f}) '
                          f'(stroke (width {width}) (type default)) (layer "{layer}") '
                          f'(uuid "{_u(self.name, "l", layer, x0, y0, x1, y1)}"))')

    def circle(self, layer, x, y, r, width=0.12, fill=False):
        f = "yes" if fill else "no"
        self.items.append(f'(fp_circle (center {x:.4f} {y:.4f}) (end {x + r:.4f} {y:.4f}) '
                          f'(stroke (width {width}) (type default)) (fill {f}) (layer "{layer}") '
                          f'(uuid "{_u(self.name, "c", layer, x, y, r)}"))')

    def text(self, layer, s, x, y, size=0.8):
        self.items.append(f'(fp_text user "{s}" (at {x:.3f} {y:.3f}) (layer "{layer}") '
                          f'(uuid "{_u(self.name, "t", s, layer)}") (effects (font (size {size} {size}) (thickness {size * 0.15:.3f}))))')

    def keepout(self, x0, y0, x1, y1, layers='"F.Cu" "B.Cu" "In1.Cu" "In2.Cu"', tracks=True,
                vias=True, pads=True, pours=True):
        def a(b):
            return "not_allowed" if b else "allowed"
        self.items.append(
            f'(zone (net 0) (net_name "") (layers {layers}) (uuid "{_u(self.name, "ko", x0, y0)}") '
            f'(hatch edge 0.5) (connect_pads (clearance 0)) (min_thickness 0.25) (filled_areas_thickness no) '
            f'(keepout (tracks {a(tracks)}) (vias {a(vias)}) (pads {a(pads)}) (copperpour {a(pours)}) (footprints allowed)) '
            f'(fill (thermal_gap 0.5) (thermal_bridge_width 0.5)) '
            f'(polygon (pts (xy {x0} {y0}) (xy {x1} {y0}) (xy {x1} {y1}) (xy {x0} {y1}))))')

    def model3d(self, path, offset=(0, 0, 0), rotate=(0, 0, 0)):
        self.model = (path, offset, rotate)

    def write(self, d: Path):
        attrs = self.attr
        if self.board_only:
            attrs += " board_only"
        if self.exclude_bom:
            attrs += " exclude_from_pos_files exclude_from_bom"
        mdl = ""
        if self.model:
            p, o, r = self.model
            mdl = (f'(model "{p}" (offset (xyz {o[0]} {o[1]} {o[2]})) (scale (xyz 1 1 1)) '
                   f'(rotate (xyz {r[0]} {r[1]} {r[2]})))')
        body = "\n  ".join(self.items)
        (d / f"{self.name}.kicad_mod").write_text(
            f'(footprint "{self.name}" (version 20241229) (generator "stratos_claude_oneshot") (generator_version "10.0")\n'
            f'  (layer "F.Cu") (descr "{self.descr}") (attr {attrs})\n'
            f'  (property "Reference" "REF**" (at 0 -1.5 0) (layer "F.SilkS") (uuid "{_u(self.name, "ref")}") '
            f'(effects (font (size 0.8 0.8) (thickness 0.12))))\n'
            f'  (property "Value" "{self.name}" (at 0 1.5 0) (layer "F.Fab") (uuid "{_u(self.name, "val")}") '
            f'(effects (font (size 0.8 0.8) (thickness 0.12))))\n'
            f'  {body}\n  {mdl}\n)\n', encoding="utf-8")


def courtyard(fp: FP, x0, y0, x1, y1, fab=True, silk=False):
    fp.rect("F.CrtYd", x0, y0, x1, y1, 0.05)
    if fab:
        fp.rect("F.Fab", x0 + 0.1, y0 + 0.1, x1 - 0.1, y1 - 0.1, 0.1)
    if silk:
        fp.rect("F.SilkS", x0, y0, x1, y1, 0.12)


def rpw0010a(d: Path):
    """TI RPW0010A VQFN-HR-10 2x2 mm, 0.45 mm side pitch. Lands transcribed from the
    TPS25947 data sheet SLVSFC9C (rev. May 2026) package drawing 4225183/A 08/2019,
    'Example board layout' page 73 (pixel-measured where only reference dims printed)."""
    fp = FP("TI_RPW0010A_VQFN-HR-10_2x2mm_P0.45mm",
            "TI RPW0010A VQFN-HR-10 (TPS259474L) from SLVSFC9C drawing 4225183/A example board layout; "
            "L-shaped corner pads = two rectangles per pad. CANDIDATE - independent review required")
    # corner feet (0.6 x 0.30) + legs (0.25 wide, to y=+/-1.2)
    for num, sx, sy in (("1", -1, -1), ("4", -1, 1), ("7", 1, 1), ("10", 1, -1)):
        fp.pad(num, sx * 0.9, sy * 0.70, 0.6, 0.30, rr=0.15)
        fp.pad(num, sx * 0.725, sy * 0.875, 0.25, 0.65, rr=0.15)
    for num, sx, sy in (("2", -1, -1), ("3", -1, 1), ("8", 1, 1), ("9", 1, -1)):
        fp.pad(num, sx * 0.9, sy * 0.225, 0.6, 0.25, rr=0.15)
    fp.pad("5", -0.25, 0, 0.30, 2.4, rr=0.1)
    fp.pad("6", 0.25, 0, 0.30, 2.4, rr=0.1)
    courtyard(fp, -1.45, -1.45, 1.45, 1.45)
    fp.circle("F.SilkS", -1.35, -1.35, 0.08, 0.16, True)
    fp.model3d("${KICAD10_3DMODEL_DIR}/Package_DFN_QFN.3dshapes/Texas_RPU0010A_VQFN-HR-10_2x2mm_P0.5mm.step")
    fp.write(d)
    return fp.name


M3D = "${KIPRJMOD}/libs/SC.3dshapes"


def xf3m(d: Path, pins: int, A: float, B: float, F: float, G: float, mpn: str):
    """Omron/Aratas XF3M-xx15-1B, 0.5 mm FPC, dual contact, rear-flip lock.
    Omron catalog G146-E1 "PCB Dimensions (TOP VIEW)": signal lands 0.30 x 1.30 on 0.50 pitch
    (span A); hold-down lands 2.2 tall, top edge 1.5 below the signal lands, inner span F, outer
    span G (-> width (G-F)/2 = 1.8 mm; repo text quotes 1.50 x 2.20 from G146-E1-05 - CONFLICT,
    check the controlled catalog). FPC enters from +Y (away from the signal row)."""
    name = f"Omron_{mpn}_1x{pins:02d}-1MP_P0.5mm_Horizontal"
    fp = FP(name, f"Omron {mpn} FPC connector from catalog G146-E1 PCB dimensions (A={A}, F={F}, G={G}); "
                  "hold-down width derived (G-F)/2. CANDIDATE - O01 sample/controlled drawing hold")
    for i in range(pins):
        fp.pad(str(i + 1), -A / 2 + i * 0.5, 0, 0.30, 1.30, rr=0.1)
    hw = (G - F) / 2
    for sx in (-1, 1):
        fp.pad("MP", sx * (F / 2 + hw / 2), 0.65 + 1.5 + 1.1, hw, 2.2, rr=0.1)
    y0, y1 = -1.0, 5.55
    courtyard(fp, -G / 2 - 0.25, y0 - 0.25, G / 2 + 0.25, y1 + 0.35, fab=False)
    fp.rect("F.Fab", -B / 2, y0, B / 2, y1, 0.1)
    fp.line("F.Fab", -B / 2 + 0.6, y1, B / 2 - 0.6, y1, 0.2)
    fp.text("F.Fab", "FPC IN", 0, y1 - 0.8, 0.6)
    fp.line("F.SilkS", -B / 2, y1 + 0.2, B / 2, y1 + 0.2, 0.12)
    fp.circle("F.SilkS", -A / 2 - 0.6, -0.9, 0.12, 0.2, True)
    fp.model3d(f"{M3D}/{name}.step")
    fp.write(d)
    return name


def sksc(d: Path):
    """Alps Alpine SKSCLCE010 side-push, SKSC drawing No.1 land dimensions (update 2510):
    4 lands 1.4 x 0.9 mm, outer span 5.0, inner gap 2.2, row gap 0.4. Terminals 1-2 and 3-4 are
    internally common (circuit diagram) -> pads 1,2 = pin 1 ; pads 3,4 = pin 2. Actuator at +Y."""
    name = "SW_Alps_SKSCLCE010_SidePush"
    fp = FP(name, "Alps SKSCLCE010 side-push tact switch, lands from SKSC family drawing No.1; "
                  "body-to-land datum and plunger position need native CAD check. CANDIDATE")
    for num, x, y in (("1", -1.8, 0.65), ("1", 1.8, 0.65), ("2", -1.8, -0.65), ("2", 1.8, -0.65)):
        fp.pad(num, x, y, 1.4, 0.9, rr=0.15)
    fp.rect("F.Fab", -1.75, -1.775, 1.75, 1.775, 0.1)
    fp.rect("F.Fab", -0.8, 1.775, 0.8, 2.45, 0.1)
    fp.text("F.Fab", "PUSH", 0, 2.9, 0.5)
    courtyard(fp, -2.75, -2.0, 2.75, 2.75, fab=False)
    fp.model3d(f"{M3D}/{name}.step")
    fp.write(d)
    return name


def t5838(d: Path):
    """TDK T5838 bottom-port PDM microphone. DS-000383 rev 1.0 Figure 32 land pattern (1:1),
    Figure 3 pin map rotated 90 deg CW into the Figure 32 orientation. Origin = sound port.
    Rev 1.1 could not be retrieved -> reconcile before release. No paste on the port."""
    name = "TDK_T5838_LGA-7_3.5x2.65mm_BottomPort"
    fp = FP(name, "TDK InvenSense T5838 (MMICT5838-00-012) land pattern from DS-000383 rev1.0 Fig.32; "
                  "0.6 mm NPTH sound hole (DS: 0.5-1.0 mm); ring paste simplified (Fig.33 segmented ring). CANDIDATE")
    for num, x, y in (("7", -2.072, -0.8375), ("6", -1.252, -0.8375), ("1", -2.072, 0.8375), ("2", -1.252, 0.8375)):
        fp.pad(num, x, y, 0.522, 0.725, rr=0.05)
    fp.pad("5", 0.74, -1.025, 0.30, 0.30, rr=0.05)
    fp.pad("4", 0.74, 1.025, 0.30, 0.30, rr=0.05)
    fp.items.append(
        f'(pad "3" smd custom (at 0.6625 0) (size 0.3 0.3) (layers "F.Cu" "F.Mask") '
        f'(options (clearance outline) (anchor circle)) '
        f'(primitives (gr_circle (center -0.6625 0) (end 0 0) (width 0.3) (fill no))) '
        f'(uuid "{_u(name, "ring")}"))')
    fp.items.append(f'(fp_circle (center 0 0) (end 0.6375 0) (stroke (width 0.25) (type default)) '
                    f'(fill no) (layer "F.Paste") (uuid "{_u(name, "ringpaste")}"))')
    fp.pad("", 0, 0, 0.6, 0.6, shape="circle", drill=0.6, layers='"*.Cu" "*.Mask"')
    fp.rect("F.Fab", -2.5, -1.325, 1.0, 1.325, 0.1)
    courtyard(fp, -2.75, -1.6, 1.25, 1.6, fab=False)
    fp.circle("F.SilkS", -2.7, -1.5, 0.08, 0.16, True)
    fp.model3d(f"{M3D}/{name}.step")
    fp.write(d)
    return name


def ta2003a(d: Path):
    """TAI-SAW TA2003A 1090 MHz SAW, spec rev 1 (2016-05-17) section E PCB footprint: 3.20 SQ,
    pads 0.81 wide on 1.19 pitch, rows 1.05 tall separated 1.09; pad A 1.70 tall.
    Pad letters from the outline drawing rotated into the footprint view: top row F,E,D;
    bottom row A,B,C. B = input, E = output, A/C/D/F = GND."""
    name = "TAI-SAW_TA2003A_SMD-6_3.0x3.0mm"
    fp = FP(name, "TAI-SAW TA2003A SAW filter footprint from product spec rev1 section E; pad-letter "
                  "orientation derived from outline drawing. CANDIDATE - verify with sample")
    for num, x in (("F", -1.19), ("E", 0.0), ("D", 1.19)):
        fp.pad(num, x, -1.07, 0.81, 1.05, rr=0.1)
    for num, x in (("B", 0.0), ("C", 1.19)):
        fp.pad(num, x, 1.07, 0.81, 1.05, rr=0.1)
    fp.pad("A", -1.19, 0.745, 0.81, 1.70, rr=0.1)
    fp.rect("F.Fab", -1.5, -1.5, 1.5, 1.5, 0.1)
    courtyard(fp, -1.85, -1.85, 1.85, 1.85, fab=False)
    fp.text("F.Fab", "IN=B OUT=E", 0, 0, 0.35)
    fp.model3d(f"{M3D}/{name}.step")
    fp.write(d)
    return name


def blb01(d: Path):
    """BeRex BLB01 DFN8 2x2, datasheet rev 6.6 p.15 suggested land pattern: 8 pads 0.56 x 0.25
    on 0.5 pitch, column centres +/-0.96 (1.92), exposed pad 0.5 x 1.0 (pin 9 GND)."""
    name = "BeRex_BLB01_DFN-8-1EP_2x2mm_P0.5mm"
    fp = FP(name, "BeRex BLB01 DFN8 2x2 suggested land pattern rev 6.6 p.15. CANDIDATE")
    for i in range(4):
        fp.pad(str(i + 1), -0.96, -0.75 + i * 0.5, 0.56, 0.25, rr=0.1)
        fp.pad(str(8 - i), 0.96, -0.75 + i * 0.5, 0.56, 0.25, rr=0.1)
    fp.pad("9", 0, 0, 0.5, 1.0, rr=0.05)
    fp.rect("F.Fab", -1.0, -1.0, 1.0, 1.0, 0.1)
    courtyard(fp, -1.5, -1.3, 1.5, 1.3, fab=False)
    fp.circle("F.SilkS", -1.35, -1.15, 0.08, 0.16, True)
    fp.model3d(f"{M3D}/{name}.step")
    fp.write(d)
    return name


def holder_2s(d: Path):
    """Two-cell 21700 series holder envelope (82.2 x 45.1 x 17.3 mm class, Keystone 1123
    dimensional reference) with three solder/wire tabs B+/MID/B- grouped at one end (MID sense lead from the series link). Exact holder MPN and its drawing
    are TBD (O05/MECH): pad positions are placeholders. Placed on the board BOTTOM."""
    name = "BatteryHolder_2S_21700_TBD"
    fp = FP(name, "2S 21700 holder envelope 82.2 x 45.1 mm; B+/MID/B- tab positions PLACEHOLDER (holder MPN TBD)",
            smd=False)
    fp.pad("1", -11.0, 38.0, 3.2, 3.2, shape="roundrect", drill=1.6, rr=0.2)
    fp.pad("3", 11.0, 38.0, 3.2, 3.2, shape="roundrect", drill=1.6, rr=0.2)
    fp.pad("2", 0.0, 38.0, 3.2, 3.2, shape="roundrect", drill=1.6, rr=0.2)
    fp.rect("F.Fab", -22.55, -41.1, 22.55, 41.1, 0.15)
    fp.circle("F.Fab", -11, 0, 10.85, 0.1)
    fp.circle("F.Fab", 11, 0, 10.85, 0.1)
    fp.text("F.Fab", "B+", -11, 35.5, 1.2)
    fp.text("F.Fab", "B-", 11, 35.5, 1.2)
    fp.text("F.Fab", "MID", 0, 35.5, 1.2)
    fp.text("F.SilkS", "+", -11, 35.2, 1.5)
    fp.text("F.SilkS", "-", 11, 35.2, 1.5)
    courtyard(fp, -22.8, -41.35, 22.8, 41.35, fab=False)
    fp.model3d(f"{M3D}/{name}.step")
    fp.write(d)
    return name


def display_outline(d: Path, standoff: float):
    """Board-only mechanical footprint carrying the Orient AFY240320A1-2.8INTH-C1 module
    envelope (50.45 x 69.90 x 4.22 mm) for the 3D assembly. No pads; not in BOM/CPL."""
    name = "Display_Orient_AFY240320A1-2.8INTH-C1_Envelope"
    fp = FP(name, "Orient AFY240320A1-2.8INTH-C1 module envelope (rev J spec) for 3D/fit; "
                  f"module underside {standoff} mm above the PCB top on a printed frame (assumption)",
            board_only=True, exclude_bom=True)
    fp.rect("F.Fab", -25.225, -34.95, 25.225, 34.95, 0.15)
    fp.rect("Cmts.User", -25.225, -34.95, 25.225, 34.95, 0.15)
    fp.text("F.Fab", "DISPLAY 2.8in ENVELOPE (module above PCB)", 0, 0, 1.5)
    fp.model3d(f"{M3D}/{name}.step", offset=(0, 0, standoff))
    fp.write(d)
    return name


def corrected_from_repo(d: Path, repo_fp: Path, new_name: str, mapping: dict, note: str):
    """Copy a repository footprint and move pad centres whose |coordinate| equals a key of
    `mapping` to the mapped magnitude (sign kept). Used for the MMC5983MA and BMP581 land
    corrections documented in docs/ISSUES.md (A13/A14)."""
    import re as _re
    t = repo_fp.read_text(encoding="utf-8")

    def fix(m):
        x, y = float(m.group(1)), float(m.group(2))
        nx = (1 if x >= 0 else -1) * mapping.get(round(abs(x), 4), abs(x))
        ny = (1 if y >= 0 else -1) * mapping.get(round(abs(y), 4), abs(y))
        return f"(pad {m.group(0)[5:m.group(0).index('(at')]}(at {nx:g} {ny:g}"
    t = _re.sub(r'\(pad [^()]*?\(at ([-\d.]+) ([-\d.]+)', fix, t)
    old = _re.search(r'\(footprint "([^"]+)"', t).group(1)
    t = t.replace(f'(footprint "{old}"', f'(footprint "{new_name}"', 1)
    t = _re.sub(r'\(descr "', f'(descr "{note} ', t, count=1)
    (d / f"{new_name}.kicad_mod").write_text(t, encoding="utf-8")
    return new_name
