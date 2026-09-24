"""Integration after the GND/buck re-layout (2026-09-23).

Run with KiCad 10 python from candidates/claude-oneshot-revA/kicad. Not idempotent.
- U7 TPS62130A -> SC:TI_RGT0016C_VQFN-16_3x3mm_EP1.68x1.68_TPS62130A (TI SLVSAG7F p.41,
  see ../docs/review_notes/TPS62130A_RGT_FOOTPRINT.md); nets, fields and position preserved.
- J1 is NOT moved (see the note below and ESP32_USB_BUTTONS_AUDIT.md, E1).
"""
import pcbnew

MM = 1e6
BOARD = 'StratosCore_Claude.kicad_pcb'
b = pcbnew.LoadBoard(BOARD)


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
    print('swap', ref, '->', libnick + ':' + name)


swap_footprint('U7', 'libs/SC.pretty', 'TI_RGT0016C_VQFN-16_3x3mm_EP1.68x1.68_TPS62130A')
# J1 +0.3 mm was tried and reverted: the D+/D- crossover behind the pad row and a B.Cu VBUS_PROT
# track by the shield stakes then collide (DRC shorts). Left as a USB-corner hand re-layout item.
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(BOARD)
