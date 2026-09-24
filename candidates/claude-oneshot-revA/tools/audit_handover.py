"""Read-only evidence inventory for the Astra handover review; run with KiCad Python."""
import hashlib
import json
from collections import Counter
from pathlib import Path

import pcbnew

candidate = Path(__file__).resolve().parents[1]
board_path = candidate / "kicad/StratosCore_Claude.kicad_pcb"
board = pcbnew.LoadBoard(str(board_path))
refs = {fp.GetReference(): fp for fp in board.GetFootprints()}
result = {
    "kicad_version": pcbnew.GetBuildVersion(),
    "board_sha256": hashlib.sha256(board_path.read_bytes()).hexdigest(),
    "footprints": len(refs),
    "selected_parts": {},
    "zones": [],
    "reports": {},
}
for ref in ("U1", "U2", "U3", "U7", "U13", "U24", "U30", "U32", "J4", "R55"):
    fp = refs[ref]
    result["selected_parts"][ref] = {
        "value": fp.GetValue(),
        "footprint": str(fp.GetFPID().GetLibItemName()),
        "pads": [{"number": p.GetNumber(), "net": p.GetNetname(),
                  "size_mm": [pcbnew.ToMM(p.GetSize().x), pcbnew.ToMM(p.GetSize().y)]}
                 for p in fp.Pads()],
    }
for z in board.Zones():
    result["zones"].append({"net": z.GetNetname(), "rule_area": z.GetIsRuleArea(),
                            "layers": [board.GetLayerName(layer) for layer in z.GetLayerSet().Seq()]})
report_dir = candidate / "kicad/reports/astra_audit_2026-09-24"
for name in ("drc_refilled.json", "erc.json"):
    data = json.loads((report_dir / name).read_text(encoding="utf-8"))
    violations = data.get("violations", []) if name.startswith("drc") else [
        v for sheet in data["sheets"] for v in sheet.get("violations", [])]
    result["reports"][name] = {
        "types": dict(Counter(v["type"] for v in violations)),
        "severities": dict(Counter(v["severity"] for v in violations)),
        "unconnected": len(data.get("unconnected_items", [])),
        "parity": len(data.get("schematic_parity", [])),
        "ignored_checks": data.get("ignored_checks", []),
    }
prices = [5.1407, .9891, 3.1983, 10.7808, 5.0431, 19.45, 2.2629,
          2.7998, 1.905, .9241, 1.3438, 1.3861, 2.5541, 1.3243]
lb1 = sum(prices) + 2 * 1.772 + 18.85 + 31.55
lb2 = lb1 - 19.45 + 4.402
result["historical_cost_arithmetic_only"] = {
    "priced_14_usd": sum(prices), "lb1_usd": lb1, "lb2_usd": lb2,
    "lb2_brl_at_recorded_fx": lb2 * 5.1414,
    "scope": "Recomputed supplied prices; not current prices, stock or a quote.",
}
(report_dir / "inventory.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps({k: v for k, v in result.items() if k not in ("selected_parts", "zones")}, indent=2))
