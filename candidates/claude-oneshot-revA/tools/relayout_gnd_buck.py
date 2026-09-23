"""GND island closure (U2/U3/U24) and TPS62130A exposed-pad via grid (U7) - 2026-09-23.

Out-of-baseline comparison candidate only. Applies to the board produced by
refine_2026_09_23_board.py (commit 6fa29cb); not idempotent (every lookup asserts
the exact pre-edit geometry). Evidence and before/after DRC are recorded in
../docs/review_notes/GND_BUCK_RELAYOUT.md.

Run with KiCad 10 python from candidates/claude-oneshot-revA/kicad:
    python ../tools/relayout_gnd_buck.py
"""
import pcbnew

MM = 1e6
BOARD = 'StratosCore_Claude.kicad_pcb'
b = pcbnew.LoadBoard(BOARD)
log = []
TR = list(b.GetTracks())
PENDING = []
NEW = []


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


def delete(item, why):
    TR.remove(item)
    PENDING.append(item)
    if item.GetClass() == 'PCB_VIA':
        q = item.GetPosition()
        log.append('delete via %s (%.3f,%.3f): %s' % (item.GetNetname(), q.x / MM, q.y / MM, why))
    else:
        s, e = item.GetStart(), item.GetEnd()
        log.append('delete track %s %s (%.3f,%.3f)->(%.3f,%.3f) w%.3f: %s' % (
            item.GetNetname(), item.GetLayerName(), s.x / MM, s.y / MM, e.x / MM, e.y / MM, item.GetWidth() / MM, why))


def add_track(net, layer, pts, w, why=''):
    n = b.FindNet(net)
    assert n is not None, net
    for a, c in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(b)
        t.SetStart(V(*a))
        t.SetEnd(V(*c))
        t.SetWidth(int(round(w * MM)))
        t.SetLayer(b.GetLayerID(layer))
        t.SetNet(n)
        b.Add(t)
        TR.append(t)
        NEW.append((t, net))
    log.append('add track %s %s %s w%.3f%s' % (net, layer, ' -> '.join('(%.3f,%.3f)' % p for p in pts), w, (': ' + why) if why else ''))


def add_via(net, x, y, d=0.45, drill=0.2, why=''):
    v = pcbnew.PCB_VIA(b)
    v.SetPosition(V(x, y))
    v.SetWidth(int(round(d * MM)))
    v.SetDrill(int(round(drill * MM)))
    v.SetViaType(pcbnew.VIATYPE_THROUGH)
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    v.SetNet(b.FindNet(net))
    b.Add(v)
    TR.append(v)
    NEW.append((v, net))
    log.append('add via %s (%.3f,%.3f) %.2f/%.2f%s' % (net, x, y, d, drill, (': ' + why) if why else ''))
    return v


# ---------------------------------------------------------------------------
# 1. U2 TPD4E05U06 (USB ESD, USON-10) GND pads 3/8 -> via next to pad 8.
#    The F.Cu USB_DP run at x 8.296 sat 0.29 mm from pad 8 and the J4.MP GND via
#    (8.85,70.65) blocked moving it. DP is moved to x 8.84 (+0.45 mm length, no
#    stubs), the J4.MP stitching via moves above the hold-down, and the In2
#    3V3_MAIN link that ran under the new via position moves to x 8.84.
# ---------------------------------------------------------------------------
delete(find_via('GND', 8.85, 70.65), 'J4.MP stitching via in the new USB_DP corridor (relocated)')
delete(find_track('GND', 'F.Cu', (10.05, 70.65), (8.85, 70.65)), 'stub to the relocated J4.MP via')
add_via('GND', 10.4, 69.35, why='J4.MP stitching via relocated above the hold-down')
add_track('GND', 'F.Cu', [(10.4, 69.35), (10.4, 69.9)], 0.25, 'link into J4.MP')

delete(find_track('USB_DP', 'F.Cu', (8.042, 70.033), (8.296, 70.287)), 'DP run beside U2 pad 8')
delete(find_track('USB_DP', 'F.Cu', (8.296, 70.287), (8.296, 73.927)), 'DP run beside U2 pad 8')
add_track('USB_DP', 'F.Cu', [(8.042, 70.033), (8.84, 70.831), (8.84, 73.383), (8.296, 73.927)], 0.16,
          'DP moved 0.54 mm right, same endpoints, no stub')

delete(find_track('3V3_MAIN', 'In2.Cu', (8.75, 70.05), (8.35, 70.45)), 'In2 3V3 link under the new GND via')
delete(find_track('3V3_MAIN', 'In2.Cu', (8.35, 70.45), (8.35, 72.45)), 'In2 3V3 link under the new GND via')
delete(find_track('3V3_MAIN', 'In2.Cu', (8.35, 72.45), (7.75, 73.05)), 'In2 3V3 link under the new GND via')
add_track('3V3_MAIN', 'In2.Cu', [(8.75, 70.05), (8.84, 70.14), (8.84, 72.36), (8.15, 73.05), (7.75, 73.05)], 0.127,
          'same vias, moved 0.49 mm right')

add_via('GND', 8.38, 71.40, why='U2 GND (pads 3/8) to In1 plane')
add_track('GND', 'F.Cu', [(7.735, 71.45), (8.38, 71.40)], 0.25, 'U2 pad 8 -> GND via')

# ---------------------------------------------------------------------------
# 2. U3 TPS259474L eFuse GND pad 8 -> via right of the pad.
#    In2 VBUS no longer crosses the pad-8 escape diagonally; it turns at y 75.439
#    and drops into the unchanged VBUS via (23.562,76.544). The EFUSE_ILM via moves
#    0.76 mm up-right along its own In2 route to make room.
# ---------------------------------------------------------------------------
delete(find_via('EFUSE_ILM', 23.213, 75.570), 'ILM via relocated along its In2 route')
delete(find_track('EFUSE_ILM', 'F.Cu', (23.108, 75.675), (23.213, 75.570)), 'stub to relocated ILM via')
delete(find_track('EFUSE_ILM', 'In2.Cu', (25.220, 73.563), (23.213, 75.570)), 'shortened to relocated ILM via')
add_via('EFUSE_ILM', 23.75, 75.033, why='ILM via relocated')
add_track('EFUSE_ILM', 'F.Cu', [(23.108, 75.675), (23.75, 75.033)], 0.15)
add_track('EFUSE_ILM', 'In2.Cu', [(25.220, 73.563), (23.75, 75.033)], 0.15)

delete(find_track('VBUS', 'In2.Cu', (20.978, 74.117), (23.404, 76.544)), 'In2 VBUS diagonal under U3 pad 8 escape')
delete(find_track('VBUS', 'In2.Cu', (23.404, 76.544), (23.562, 76.544)), 'In2 VBUS diagonal under U3 pad 8 escape')
add_track('VBUS', 'In2.Cu', [(20.978, 74.117), (22.3, 75.439), (23.2, 75.439), (23.562, 75.801), (23.562, 76.544)], 0.4,
          'same width, same end via')

add_via('GND', 22.98, 76.125, why='U3 eFuse GND pad 8 to In1 plane')
add_track('GND', 'F.Cu', [(22.45, 76.125), (22.98, 76.125)], 0.25, 'U3 pad 8 -> GND via')

# ---------------------------------------------------------------------------
# 3. U24 TXU0202 GND pad 2 -> via left of the pad.
#    B.Cu I2C_SDA jog under the pour moved 0.46 mm left (x 5.556 -> 5.1).
# ---------------------------------------------------------------------------
delete(find_track('I2C_SDA', 'B.Cu', (6.336, 41.387), (5.556, 42.167)), 'SDA jog under U24 GND escape')
delete(find_track('I2C_SDA', 'B.Cu', (5.556, 42.167), (5.556, 42.937)), 'SDA jog under U24 GND escape')
delete(find_track('I2C_SDA', 'B.Cu', (5.556, 42.937), (4.278, 44.214)), 'SDA jog under U24 GND escape')
add_track('I2C_SDA', 'B.Cu', [(6.336, 41.387), (5.1, 42.623), (5.1, 43.392), (4.278, 44.214)], 0.15,
          'same endpoints')
add_via('GND', 5.6, 43.2, why='U24 TXU0202 GND pad 2 to In1 plane')
add_track('GND', 'F.Cu', [(6.5, 43.2), (5.6, 43.2)], 0.25, 'U24 pad 2 -> GND via')

# ---------------------------------------------------------------------------
# 4. U7 TPS62130A exposed pad: 2 x 2 via grid at EP centre +/-0.29 mm
#    (TI SLVSAG7F RGT land example, 0.58 mm pitch). In2 BUCK_SW and B.Cu SD_CT /
#    SPI_SCLK moved off the grid; the old single EP via conflicts (hole-to-hole)
#    with the grid and is replaced.
# ---------------------------------------------------------------------------
delete(find_via('GND', 22.35, 48.0), 'single EP via replaced by the 2x2 grid (hole-to-hole 0.12 mm to grid via)')

delete(find_track('BUCK_SW', 'In2.Cu', (20.538, 47.046), (23.042, 49.550)), 'In2 SW diagonal under the EP')
delete(find_track('BUCK_SW', 'In2.Cu', (23.042, 49.550), (25.615, 49.550)), 'rebuilt with the new corner')
add_track('BUCK_SW', 'In2.Cu', [(20.538, 47.046), (20.538, 48.55), (21.538, 49.55), (25.615, 49.55)], 0.4,
          'same end vias; clears the EP grid')

delete(find_track('SD_CT', 'B.Cu', (21.921, 42.864), (21.921, 52.999)), 'SD_CT straight under the EP')
add_track('SD_CT', 'B.Cu', [(21.921, 42.864), (21.921, 47.30), (22.73, 48.109), (22.73, 49.10), (21.921, 49.909),
                            (21.921, 52.999)], 0.15, 'jog right of the EP grid')
delete(find_track('SPI_SCLK', 'B.Cu', (22.865, 42.296), (22.865, 53.722)), 'make room for the SD_CT jog')
add_track('SPI_SCLK', 'B.Cu', [(22.865, 42.296), (22.865, 47.40), (23.02, 47.555), (23.02, 49.70), (22.865, 49.855),
                               (22.865, 53.722)], 0.15, 'parallel 0.155 mm jog')

for x in (21.71, 22.29):
    for y in (48.31, 48.89):
        add_via('GND', x, y, why='U7 EP grid')

for it in PENDING:
    b.Remove(it)

# Guard against silent net reassignment before the fill.
for it, net in NEW:
    assert it.GetNetname() == net, (it.GetClass(), net, it.GetNetname())

pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(BOARD)
for line in log:
    print(line)
print('items added', len(NEW), 'removed', len(PENDING))
