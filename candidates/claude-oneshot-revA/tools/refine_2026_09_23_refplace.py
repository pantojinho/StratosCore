"""(Run from candidates/claude-oneshot-revA/kicad with KiCad 10 python.)
Nudge silkscreen reference texts listed by DRC to a nearby spot free of pads, other silk and edges.

Bounding-box model; every result is re-checked by KiCad DRC afterwards.
usage: refplace.py drc.json
"""
import json, re, sys, math
import pcbnew

MM = 1e6
b = pcbnew.LoadBoard('StratosCore_Claude.kicad_pcb')
d = json.load(open(sys.argv[1]))
refs = set()
for v in d['violations']:
    if v['type'] in ('silk_over_copper', 'silk_overlap', 'silk_edge_clearance'):
        for i in v['items']:
            m = re.search(r'refer[eê]ncia do (\S+)', i['description'])
            if m:
                refs.add(m.group(1))


def box(item, grow=0.0):
    bb = item.BBox() if hasattr(item, 'BBox') else item.GetBoundingBox()
    return (bb.GetX() / MM - grow, bb.GetY() / MM - grow, bb.GetRight() / MM + grow, bb.GetBottom() / MM + grow)


def inter(a, c):
    return not (a[2] <= c[0] or a[0] >= c[2] or a[3] <= c[1] or a[1] >= c[3])

side_silk = {False: pcbnew.F_SilkS, True: pcbnew.B_SilkS}
obst = {False: [], True: []}
for f in b.GetFootprints():
    for p in f.Pads():
        for flipped, cu in ((False, pcbnew.F_Cu), (True, pcbnew.B_Cu)):
            if p.IsOnLayer(cu):
                obst[flipped].append(('pad', f.GetReference(), box(p, 0.1)))
    for g in f.GraphicalItems():
        if g.GetClass() in ('PCB_TEXT', 'PCB_FIELD'):
            continue
        for flipped in (False, True):
            if g.GetLayer() == side_silk[flipped]:
                obst[flipped].append(('gfx', f.GetReference(), box(g, 0.1)))
for dr in b.GetDrawings():
    for flipped in (False, True):
        if dr.GetLayer() == side_silk[flipped]:
            obst[flipped].append(('gfx', '', box(dr, 0.1)))
edge = b.GetBoardEdgesBoundingBox()
E = (edge.GetX() / MM + 0.3, edge.GetY() / MM + 0.3, edge.GetRight() / MM - 0.3, edge.GetBottom() / MM - 0.3)
slots = [box(dr, 0.25) for dr in b.GetDrawings() if dr.GetLayer() == pcbnew.Edge_Cuts and dr.GetShapeStr() == 'Rect']
texts = {}
for f in b.GetFootprints():
    r = f.Reference()
    if r.IsVisible() and r.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS):
        texts[f.GetReference()] = (f, r)

moved = []
for ref in sorted(refs):
    if ref not in texts:
        continue
    f, r = texts[ref]
    fl = f.IsFlipped()
    fb = box(f.GetCourtyard(pcbnew.B_CrtYd if fl else pcbnew.F_CrtYd)) if f.GetCourtyard(pcbnew.B_CrtYd if fl else pcbnew.F_CrtYd).OutlineCount() else box(f)
    w, h = box(r)[2] - box(r)[0], box(r)[3] - box(r)[1]
    cx, cy = (fb[0] + fb[2]) / 2, (fb[1] + fb[3]) / 2
    cands = []
    for gap in (0.15, 0.4, 0.8, 1.3):
        cands += [(cx, fb[1] - gap - h / 2), (cx, fb[3] + gap + h / 2), (fb[0] - gap - w / 2, cy), (fb[2] + gap + w / 2, cy)]
        for sx in (-1, 1):
            for sy in (-1, 1):
                cands.append((cx + sx * ((fb[2] - fb[0]) / 2 + gap + w / 2), cy + sy * ((fb[3] - fb[1]) / 2 + gap + h / 2)))
    others = [box(t[1], 0.08) for k, t in texts.items() if k != ref and t[0].IsFlipped() == fl]
    best = None
    fx, fy = f.GetPosition().x / MM, f.GetPosition().y / MM
    lim = max(2.0, math.hypot(fb[2] - fb[0], fb[3] - fb[1]) / 2 + 0.9)
    for x, y in sorted(cands, key=lambda q: math.hypot(q[0] - fx, q[1] - fy)):
        if math.hypot(x - fx, y - fy) > lim:
            continue
        tb = (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
        if tb[0] < E[0] or tb[1] < E[1] or tb[2] > E[2] or tb[3] > E[3]:
            continue
        if any(inter(tb, s) for s in slots):
            continue
        if any(inter(tb, o[2]) for o in obst[fl]):
            continue
        if any(inter(tb, o) for o in others):
            continue
        best = (x, y)
        break
    if best:
        old = r.GetPosition()
        r.SetPosition(pcbnew.VECTOR2I(int(best[0] * MM), int(best[1] * MM)))
        texts[ref] = (f, r)
        moved.append('%s (%.2f,%.2f)->(%.2f,%.2f)' % (ref, old.x / MM, old.y / MM, best[0], best[1]))
    else:
        moved.append('%s: no free spot (left in place)' % ref)
b.Save('StratosCore_Claude.kicad_pcb')
print('\n'.join(moved))
