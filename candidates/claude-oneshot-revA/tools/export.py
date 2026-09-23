"""Run DRC and produce the review outputs (no manufacturing release).

    "C:/Program Files/KiCad/10.0/bin/python.exe" tools/export.py
"""
from __future__ import annotations

import json
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
K = ROOT / "kicad"
O = ROOT / "outputs"
CLI = "C:/Program Files/KiCad/10.0/bin/kicad-cli.exe"
PCB = K / "StratosCore_Claude.kicad_pcb"
SCH = K / "StratosCore_Claude.kicad_sch"
O.mkdir(exist_ok=True)


def run(*a):
    r = subprocess.run([CLI, *a], capture_output=True, text=True)
    return r.returncode, (r.stdout or "")[-400:] + (r.stderr or "")[-400:]


def drc():
    rep = K / "reports" / "drc.json"
    run("pcb", "drc", "--format", "json", "--severity-all", "--schematic-parity", "-o", str(rep), str(PCB))
    d = json.loads(rep.read_text(encoding="utf-8"))
    v, u, p = d.get("violations", []), d.get("unconnected_items", []), d.get("schematic_parity", [])
    c = Counter((x["severity"], x["type"]) for x in v)
    lines = [f"KiCad 10.0.6 DRC of {PCB.name}",
             f"violations: {len(v)} (errors {sum(1 for x in v if x['severity'] == 'error')}), "
             f"unconnected: {len(u)}, schematic parity: {len(p)}"]
    lines += [f"  {s:8s} {t:32s} {n}" for (s, t), n in sorted(c.items())]
    if u:
        nets = Counter()
        for x in u:
            for it in x.get("items", []):
                desc = it.get("description", "")
                if "[" in desc:
                    nets[desc.split("[")[1].split("]")[0]] += 1
        lines.append("unconnected nets (item count): " + ", ".join(f"{n}:{k}" for n, k in nets.most_common(40)))
    (O / "drc_summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


def views():
    for side in ("top", "bottom"):
        run("pcb", "render", "--side", side, "--quality", "high", "--width", "1600", "--height", "2200",
            "-o", str(O / f"render_{side}.png"), str(PCB))
    run("pcb", "render", "--side", "top", "--quality", "high", "--width", "2000", "--height", "1600",
        "--rotate", "-55,0,35", "--zoom", "0.85", "--perspective", "-o", str(O / "render_iso.png"), str(PCB))
    run("pcb", "render", "--side", "bottom", "--quality", "high", "--width", "2000", "--height", "1600",
        "--rotate", "55,0,-35", "--zoom", "0.85", "--perspective", "-o", str(O / "render_iso_back.png"), str(PCB))
    run("pcb", "export", "step", "--force", "--subst-models", "--user-origin", "0x0mm",
        "-o", str(O / "StratosCore_Claude_board.step"), str(PCB))
    run("pcb", "export", "pdf", "--layers", "F.Cu,In1.Cu,In2.Cu,B.Cu,F.SilkS,B.SilkS,Edge.Cuts,F.Fab",
        "--mode-multipage", "-o", str(O / "pcb_layers.pdf"), str(PCB))
    run("sch", "export", "pdf", "-o", str(ROOT / "docs" / "schematic.pdf"), str(SCH))
    run("sch", "export", "netlist", "--format", "kicadsexpr", "-o", str(O / "netlist.net"), str(SCH))
    run("sch", "export", "bom", "--fields",
        "Reference,Value,Footprint,MPN,Status,Source,${QUANTITY},${DNP}", "--labels",
        "Refs,Value,Footprint,MPN,Status,Source,Qty,DNP", "--group-by", "Value,Footprint,MPN,${DNP}",
        "-o", str(O / "bom_candidate.csv"), str(SCH))
    run("pcb", "export", "pos", "--format", "csv", "--units", "mm", "-o", str(O / "positions_REVIEW_ONLY.csv"), str(PCB))


if __name__ == "__main__":
    drc()
    views()
