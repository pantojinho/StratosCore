"""(Run from candidates/claude-oneshot-revA/kicad with KiCad 10 python.)
Silkscreen refinement: passive refdes -> Fab (assembly drawing); keep U/J/TP/SW/BT/H/Y/FID on silk at 0.8 mm."""
import re, pcbnew
b = pcbnew.LoadBoard('StratosCore_Claude.kicad_pcb')
KEEP = ('U', 'J', 'TP', 'SW', 'BT', 'H', 'Y', 'FID')
moved = kept = 0
for f in b.GetFootprints():
    r = f.Reference()
    pre = re.match(r'[A-Z]+', f.GetReference()).group(0)
    if not r.IsVisible():
        continue
    silk = r.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS)
    if not silk:
        continue
    if pre in KEEP:
        r.SetTextSize(pcbnew.VECTOR2I(800000, 800000))
        r.SetTextThickness(150000)
        kept += 1
    else:
        r.SetLayer(pcbnew.B_Fab if f.IsFlipped() else pcbnew.F_Fab)
        moved += 1
b.Save('StratosCore_Claude.kicad_pcb')
print('refdes moved to Fab:', moved, 'kept on silk at 0.8 mm:', kept)
