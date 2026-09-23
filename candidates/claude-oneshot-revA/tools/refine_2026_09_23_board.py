"""Candidate refinement pass 1 (2026-09-23). Evidence per edit is in ../docs/REFINEMENT_2026_09_23.md. Applies to the e1f75a3 board only (not idempotent).

Run with KiCad 10 python from candidates/claude-oneshot-revA/kicad.
"""
import sys
import pcbnew

MM = 1e6
BOARD = 'StratosCore_Claude.kicad_pcb'
b = pcbnew.LoadBoard(BOARD)
log = []
TR = list(b.GetTracks())


def V(x, y):
    return pcbnew.VECTOR2I(int(round(x * MM)), int(round(y * MM)))


def near(p, x, y, tol=0.002):
    return abs(p.x / MM - x) <= tol and abs(p.y / MM - y) <= tol


def find_track(net, layer, a, c):
    out = []
    for t in TR:
        if t.GetClass() == 'PCB_VIA' or t.GetNetname() != net or t.GetLayerName() != layer:
            continue
        s, e = t.GetStart(), t.GetEnd()
        if (near(s, *a) and near(e, *c)) or (near(s, *c) and near(e, *a)):
            out.append(t)
    assert len(out) == 1, (net, layer, a, c, len(out))
    return out[0]


def find_via(net, x, y):
    out = [t for t in TR if t.GetClass() == 'PCB_VIA' and t.GetNetname() == net and near(t.GetPosition(), x, y)]
    assert len(out) == 1, (net, x, y, len(out))
    return out[0]


PENDING = []


def delete(item, why):
    TR.remove(item)
    PENDING.append(item)
    log.append('delete %s: %s' % (item.GetClass(), why))


def add_track(net, layer, pts, w):
    n = b.FindNet(net)
    for a, c in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(b)
        t.SetStart(V(*a))
        t.SetEnd(V(*c))
        t.SetWidth(int(w * MM))
        t.SetLayer(b.GetLayerID(layer))
        t.SetNet(n)
        b.Add(t)
        TR.append(t)
    log.append('add track %s %s %s w%.3f' % (net, layer, pts, w))


def add_via(net, x, y, d=0.45, drill=0.2):
    v = pcbnew.PCB_VIA(b)
    v.SetPosition(V(x, y))
    v.SetWidth(int(d * MM))
    v.SetDrill(int(drill * MM))
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    v.SetNet(b.FindNet(net))
    b.Add(v)
    log.append('add via %s (%.3f,%.3f) %.2f/%.2f' % (net, x, y, d, drill))
    return v


def swap_footprint(ref, libdir, name, libnick='SC'):
    old = b.FindFootprintByReference(ref)
    nets = {}
    for p in old.Pads():
        if p.GetNumber():
            nets.setdefault(p.GetNumber(), p.GetNetname())
    new = pcbnew.FootprintLoad(libdir, name)
    new.SetFPID(pcbnew.LIB_ID(libnick, name))
    new.SetParent(b)
    for fld in old.GetFields():
        nm = fld.GetName()
        tgt = new.GetField(nm) if new.HasField(nm) else None
        if tgt is None:
            nf = pcbnew.PCB_FIELD(fld, pcbnew.FIELD_T_USER, nm)
            nf.SetParent(new)
            nf.SetFPRelativePosition(fld.GetFPRelativePosition())
            new.Add(nf)
        else:
            tgt.SetText(fld.GetText())
            tgt.SetVisible(fld.IsVisible())
            tgt.SetLayer(fld.GetLayer())
            tgt.SetTextSize(fld.GetTextSize())
            tgt.SetTextThickness(fld.GetTextThickness())
            tgt.SetFPRelativePosition(fld.GetFPRelativePosition())
    new.SetPath(old.GetPath())
    new.SetSheetname(old.GetSheetname())
    new.SetSheetfile(old.GetSheetfile())
    new.SetAttributes(old.GetAttributes())
    new.SetOrientation(old.GetOrientation())
    new.SetPosition(old.GetPosition())
    if old.IsFlipped():
        new.Flip(new.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
    for p in new.Pads():
        if p.GetNumber():
            p.SetNet(b.FindNet(nets[p.GetNumber()]))
    b.Remove(old)
    b.Add(new)
    log.append('swap footprint %s -> %s:%s' % (ref, libnick, name))


# J. TXU0202 exact TI DCU0008A land (SCES942A pp.32-34)
swap_footprint('U24', 'libs/SC.pretty', 'TI_DCU0008A_VSSOP-8_2.3x2mm_P0.5mm_TXU0202')
# K. TPS259474L RPW: same copper, TI stencil/fab corrections (SLVSFC9C pp.72-74)
swap_footprint('U3', 'libs/SC.pretty', 'TI_RPW0010A_VQFN-HR-10_2x2mm_P0.45mm')

# A. J5 (GNSS U.FL) out of U1 body courtyard (0.09 mm overlap); straight feed to D2
j5 = b.FindFootprintByReference('J5')
j5.SetPosition(V(29.4, 2.9))
log.append('move J5 (29.0,2.9)->(29.4,2.9)')
for a, c, w in (((27.475, 3.425), (27.475, 2.9), 0), ((27.625, 6.4), (27.625, 3.575), 0),
                ((27.625, 3.575), (27.475, 3.425), 0), ((27.875, 6.65), (27.625, 6.4), 0)):
    delete(find_track('GNSS_RF', 'F.Cu', a, c), 'old GNSS_RF detour to moved J5 pad 1')
add_track('GNSS_RF', 'F.Cu', [(27.875, 2.9), (27.875, 6.65)], 0.15)

# B. ICM-42688-P pin 9 INT2/FSYNC/CLKIN -> GND (TDK DS-000347 v1.9 Table 10)
u30 = b.FindFootprintByReference('U30')
for p in u30.Pads():
    if p.GetNumber() == '9':
        p.SetNet(b.FindNet('GND'))
log.append('U30 pad 9 net -> GND')
add_track('GND', 'F.Cu', [(31.1625, 42.25), (31.654, 42.25), (31.654, 41.75)], 0.2)

# C. Remove footprint-level solder-mask-bridge suppression (match SC/baseline library)
for ref in ('U30', 'U32'):
    b.FindFootprintByReference(ref).SetAllowSolderMaskBridges(False)
    log.append('%s allow_soldermask_bridges -> False (findings stay visible)' % ref)

# D1. I2C_SCL duplicate via pair (hole-to-hole 0.0385 mm)
delete(find_via('I2C_SCL', 47.45, 2.55), 'duplicate SCL via 0.24 mm from (47.32,2.35)')
delete(find_track('I2C_SCL', 'In2.Cu', (47.75, 2.85), (47.45, 2.55)), 'stub of removed via')
delete(find_track('I2C_SCL', 'In2.Cu', (47.85, 2.85), (47.75, 2.85)), 'stub of removed via')
t = find_track('I2C_SCL', 'B.Cu', (47.45, 2.55), (46.65, 3.35))
t.SetStart(V(47.32, 2.35)) if near(t.GetStart(), 47.45, 2.55) else t.SetEnd(V(47.32, 2.35))
log.append('B.Cu SCL segment re-anchored to via (47.32,2.35)')
# D2. SCL In2 path under the BMP581 body (Bosch DS004-13 s8.2: no traces/vias under sensor)
for a, c in (((43.224, 9.449), (49.027, 3.646)), ((49.027, 3.646), (49.027, 3.203)),
             ((49.027, 3.203), (48.678, 2.854)), ((48.678, 2.854), (47.824, 2.854)),
             ((47.824, 2.854), (47.32, 2.35))):
    delete(find_track('I2C_SCL', 'In2.Cu', a, c), 'In2 SCL route under BMP581 body')
add_track('I2C_SCL', 'In2.Cu', [(43.224, 9.449), (44.65, 8.023), (44.65, 5.55)], 0.15)
# D3. LED_A duplicate via (hole-to-hole 0.1054 mm)
delete(find_via('LED_A', 21.75, 69.45), 'redundant LED_A via overlapping (22.084,69.327)')
delete(find_track('LED_A', 'In2.Cu', (21.75, 69.45), (21.75, 69.35)), 'stub of removed via')
t = find_track('LED_A', 'F.Cu', (21.75, 68.05), (21.75, 69.45))
t.SetEnd(V(21.75, 69.0)) if near(t.GetEnd(), 21.75, 69.45) else t.SetStart(V(21.75, 69.0))
add_track('LED_A', 'F.Cu', [(21.75, 69.0), (22.084, 69.327)], 0.15)

# E. SHT40 SDA (pad 1) around the slot top to the In2 SDA trunk (outside SHT40 keepout, >=0.25 mm to slots)
add_track('I2C_SDA', 'F.Cu', [(43.3, 1.5), (42.95, 1.5), (42.95, 0.7), (42.8, 0.55), (41.55, 0.55), (41.3, 0.8), (41.3, 4.953)], 0.15)
add_via('I2C_SDA', 41.3, 4.953)

# F. join the two 3V3_MAIN fragments at the vent edge (SHT40/C37 side <-> BMP581/C35 side)
delete(find_track('3V3_MAIN', 'F.Cu', (45.85, 4.85), (45.95, 4.75)), 'dangling stub replaced by the link below')
add_track('3V3_MAIN', 'F.Cu', [(45.85, 4.85), (46.426, 4.85), (47.026, 4.25), (47.026, 4.2)], 0.25)

# G. C57 (touch 3V3 decoupling; no courtyard-free spot exists at J4 because the J8 card envelope covers it)
#    moved 3.97 mm onto the 3V3_MAIN feed at R104.2 so both pads connect (pad 1 on the 3V3 track end, pad 2 in GND pour)
c57 = b.FindFootprintByReference('C57')
c57.SetPosition(V(16.8, 43.1))
c57.SetOrientationDegrees(270)
p1 = [p for p in c57.Pads() if p.GetNumber() == '1'][0].GetPosition()
if abs(p1.y / MM - 43.58) > 0.05:
    c57.SetOrientationDegrees(90)
    p1 = [p for p in c57.Pads() if p.GetNumber() == '1'][0].GetPosition()
log.append('move C57 (13.05,44.4,0) -> (16.8,43.1,%s); pad1 at (%.3f,%.3f)' % (c57.GetOrientationDegrees(), p1.x / MM, p1.y / MM))
add_track('3V3_MAIN', 'F.Cu', [(p1.x / MM, p1.y / MM), (16.82, 43.6)], 0.3)

# H. Isolated GND islands (DRC unconnected items)
# H1. TPS62130A U7: AGND/PGND/EP must connect directly to the system ground plane (TI SLVSAG7F s11.1).
#     The autorouted In2 BUCK_SW and B.Cu SD_CT tracks under U7 leave room for only one legal 0.2 mm via
#     inside the EP (TI RGT0016C example shows a 0.58 mm via grid); the rest stays a layout action.
add_via('GND', 22.35, 48.0)
# H2. ICM-42688-P pads 9/10/11 (pad 9 now GND): the 3V3 loop and In2 SX_NSS leave one legal via spot, on the
#     new pad-9/10 GND link just outside the pad row (0.05 mm inside the body outline; exposed by the common
#     no-mask opening, so it joins the open ICM mask-strategy item)
add_via('GND', 31.675, 41.8)
# H3. BMP581 SDO strap + C35 decoupling ground: tented via between C35 lands to In1 GND
add_track('GND', 'F.Cu', [(49.18, 4.2), (48.87, 4.0)], 0.2)
add_via('GND', 48.87, 4.0)

for it in PENDING:
    b.Remove(it)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(BOARD)
print('\n'.join(log))
