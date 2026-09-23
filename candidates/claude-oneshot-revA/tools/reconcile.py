"""Net/pad reconciliation between the exported schematic netlist and the board.

Run with KiCad 10 python from candidates/claude-oneshot-revA/kicad:
    python ../tools/reconcile.py reports/<dir>/netlist.xml StratosCore_Claude.kicad_pcb > reports/<dir>/reconcile.txt

Compares every (reference, pad) -> net pair. Unconnected single-pin schematic nets are
normalised because KiCad names them differently in the schematic and on the board.
This is a correspondence check only; it does not validate the circuit.
"""
import sys
import xml.etree.ElementTree as ET
import pcbnew

sch = {}
for net in ET.parse(sys.argv[1]).getroot().iter('net'):
    name = net.get('name').lstrip('/')
    nodes = list(net.iter('node'))
    for n in nodes:
        key = (n.get('ref'), n.get('pin'))
        sch[key] = '<unconnected>' if name.startswith('unconnected-') or (len(nodes) == 1 and name.startswith('Net-')) else name.split('/')[-1]

b = pcbnew.LoadBoard(sys.argv[2])
pcb = {}
for f in b.GetFootprints():
    for p in f.Pads():
        if not p.GetNumber():
            continue
        n = p.GetNetname()
        pcb[(f.GetReference(), p.GetNumber())] = '<unconnected>' if (not n or n.startswith('unconnected-')) else n.split('/')[-1]

only_sch = sorted(k for k in sch if k not in pcb)
only_pcb = sorted(k for k in pcb if k not in sch and pcb[k] != '<unconnected>')
diff = sorted(k for k in sch if k in pcb and sch[k] != pcb[k])
print('schematic pins: %d, board pads (numbered, unique): %d' % (len(sch), len(pcb)))
print('pins missing on board: %d' % len(only_sch))
for k in only_sch:
    print('  ', k, sch[k])
print('connected board pads missing in schematic: %d' % len(only_pcb))
for k in only_pcb:
    print('  ', k, pcb[k])
print('net mismatches: %d' % len(diff))
for k in diff:
    print('  ', k, 'sch', sch[k], 'pcb', pcb[k])
