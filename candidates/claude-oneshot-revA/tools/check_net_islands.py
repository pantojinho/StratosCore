"""Find disconnected copper groups of one net (zone islands + tracks + vias + pads).

Usage: python islands.py board.kicad_pcb NET
Prints every connected group except the largest, with a representative location.
Approximate geometric model: point-in-polygon for zone islands, pad hit-test for
track ends, endpoint coincidence (+/- 5 um) between track segments.
"""
import sys
import pcbnew

board, netname = sys.argv[1], sys.argv[2]
b = pcbnew.LoadBoard(board)
net = b.FindNet(netname).GetNetCode()

parent = {}


def find(a):
    parent.setdefault(a, a)
    while parent[a] != a:
        parent[a] = parent[parent[a]]
        a = parent[a]
    return a


def union(a, c):
    parent[find(a)] = find(c)


islands = []  # (key, layer, SHAPE_POLY_SET single outline)
for zi, z in enumerate(b.Zones()):
    if z.GetIsRuleArea() or z.GetNetCode() != net:
        continue
    for layer in z.GetLayerSet().Seq():
        fp = z.GetFilledPolysList(layer)
        for i in range(fp.OutlineCount()):
            ps = pcbnew.SHAPE_POLY_SET()
            ps.AddOutline(fp.Outline(i))
            for h in range(fp.HoleCount(i)):
                ps.AddHole(fp.Hole(i, h))
            key = ('Z', zi, layer, i)
            islands.append((key, layer, ps))
            find(key)


def islands_at(pt, layer):
    return [k for k, l, ps in islands if l == layer and ps.Contains(pt)]


pads = []
for f in b.GetFootprints():
    for p in f.Pads():
        if p.GetNetCode() != net:
            continue
        key = ('P', f.GetReference(), p.GetNumber(), p.m_Uuid.AsString())
        find(key)
        pads.append((key, p))
        for layer in p.GetLayerSet().CuStack():
            for k in islands_at(p.GetPosition(), layer):
                union(key, k)

vias = []
tracks = []
for t in b.GetTracks():
    if t.GetNetCode() != net:
        continue
    key = ('T', t.m_Uuid.AsString())
    find(key)
    if t.GetClass() == 'PCB_VIA':
        vias.append((key, t))
        for layer in t.GetLayerSet().CuStack():
            for k in islands_at(t.GetPosition(), layer):
                union(key, k)
    else:
        tracks.append((key, t))
        for pt in (t.GetStart(), t.GetEnd()):
            for k in islands_at(pt, t.GetLayer()):
                union(key, k)


def close(a, c, tol=5000):
    return abs(a.x - c.x) <= tol and abs(a.y - c.y) <= tol

for key, t in tracks:
    ends = (t.GetStart(), t.GetEnd())
    for key2, v in vias:
        if any(close(e, v.GetPosition(), v.GetWidth(pcbnew.F_Cu) // 2) for e in ends):
            union(key, key2)
    for key2, p in pads:
        if p.IsOnLayer(t.GetLayer()) and any(p.HitTest(e) for e in ends):
            union(key, key2)
    for key2, t2 in tracks:
        if key2 <= key or t2.GetLayer() != t.GetLayer():
            continue
        e2 = (t2.GetStart(), t2.GetEnd())
        if any(close(a, c) for a in ends for c in e2) or any(t2.HitTest(e) for e in ends) or any(t.HitTest(e) for e in e2):
            union(key, key2)

groups = {}
for k in list(parent):
    groups.setdefault(find(k), []).append(k)
ordered = sorted(groups.values(), key=len, reverse=True)
print(netname, 'groups', len(ordered), 'largest', len(ordered[0]))


def where(k):
    if k[0] == 'P':
        for kk, p in pads:
            if kk == k:
                return 'pad %s.%s @(%.3f,%.3f)' % (k[1], k[2], p.GetPosition().x / 1e6, p.GetPosition().y / 1e6)
    if k[0] == 'T':
        for kk, t in vias + tracks:
            if kk == k:
                q = t.GetPosition() if t.GetClass() == 'PCB_VIA' else t.GetStart()
                return '%s %s @(%.3f,%.3f)' % (t.GetClass(), t.GetLayerName() if t.GetClass() != 'PCB_VIA' else '', q.x / 1e6, q.y / 1e6)
    for kk, l, ps in islands:
        if kk == k:
            bb = ps.BBox()
            return 'zone island %s bbox (%.2f,%.2f)-(%.2f,%.2f) area %.3f mm2' % (pcbnew.LayerName(l), bb.GetX() / 1e6, bb.GetY() / 1e6, bb.GetRight() / 1e6, bb.GetBottom() / 1e6, ps.Area() / 1e12)
    return str(k)

for g in ordered[1:]:
    print('--- isolated group of', len(g))
    for k in g[:8]:
        print('   ', where(k))
