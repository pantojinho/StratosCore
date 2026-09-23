"""Build the candidate KiCad project (symbols, footprints, hierarchical schematic) and run ERC.

Run with any Python 3.11+ (KiCad's bundled python works):
    "C:/Program Files/KiCad/10.0/bin/python.exe" tools/build_sch.py
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import design as D  # noqa: E402
import fpgen  # noqa: E402
import schgen  # noqa: E402
import symlib  # noqa: E402

ROOT = HERE.parent
REPO = ROOT.parent.parent
OUT = ROOT / "kicad"
PROJECT = "StratosCore_Claude"
CLI = "C:/Program Files/KiCad/10.0/bin/kicad-cli.exe"
REV = "A-claude-oneshot-1"
DISPLAY_STANDOFF = 5.0   # mm, module underside above PCB top (printed frame; assumption)
COMPANY = "StratosCore (CERN-OHL-P-2.0) - Claude one-shot candidate"


def build_libs(extra_fp_builders=()):
    libdir = OUT / "libs"
    (libdir / f"{D.PLIB}.pretty").mkdir(parents=True, exist_ok=True)
    blocks = []
    for name, c in D.CUSTOM.items():
        blocks.append(symlib.ic_symbol(name, c["pins"], c["ref"], c["fp"], c["ds"], c.get("desc", ""),
                                       c.get("value")))
    for rail in D.RAILS:
        if rail != "GND":
            blocks.append(symlib.power_symbol(rail))
    symlib.write_library(libdir / f"{D.PLIB}.kicad_sym", blocks)
    # reviewed repository footprint candidates, copied unchanged
    for f in (REPO / "hardware" / "footprints").glob("*.kicad_mod"):
        shutil.copy2(f, libdir / f"{D.PLIB}.pretty" / f.name)
    pretty = libdir / f"{D.PLIB}.pretty"
    fpgen.rpw0010a(pretty)
    fpgen.xf3m(pretty, 40, 19.5, 23.1, 21.5, 25.1, "XF3M-4015-1B")
    fpgen.xf3m(pretty, 6, 2.5, 6.1, 4.5, 8.1, "XF3M-0615-1B")
    fpgen.sksc(pretty)
    fpgen.t5838(pretty)
    fpgen.ta2003a(pretty)
    fpgen.blb01(pretty)
    fpgen.holder_2s(pretty)
    fpgen.display_outline(pretty, DISPLAY_STANDOFF)
    hw = REPO / "hardware" / "footprints"
    fpgen.corrected_from_repo(pretty, hw / "MEMSIC_MMC5983MA_LGA-16_3x3mm_P0.5mm.kicad_mod",
                              "MEMSIC_MMC5983MA_LGA-16_3x3mm_P0.5mm_CORRECTED", {1.05: 1.275},
                              "CORRECTED (one-shot A13): pad centres +/-1.275 = MEMSIC Rev A land pattern 2.550 centre-to-centre; repo file used +/-1.05 (corner pads overlap).")
    fpgen.corrected_from_repo(pretty, hw / "Bosch_BMP581_LGA-10_2x2mm.kicad_mod",
                              "Bosch_BMP581_LGA-10_2x2mm_CORRECTED", {0.6: 0.7625},
                              "CORRECTED (one-shot A14): pad centres +/-0.7625 = Bosch DS004-13 Fig.32 1.525 centre-to-centre; repo used +/-0.6 (0.04 mm corner gap). Pin-1 orientation to re-verify.")
    fpgen.fix_models(pretty)
    for b in extra_fp_builders:
        b(libdir / f"{D.PLIB}.pretty")
    return (libdir / f"{D.PLIB}.kicad_sym").read_text(encoding="utf-8")


def lib_tables(sym_libs: set, fp_libs: set):
    def row(n, uri):
        return f'  (lib (name "{n}") (type "KiCad") (uri "{uri}") (options "") (descr ""))'
    srows = [row(D.PLIB, "${KIPRJMOD}/libs/SC.kicad_sym")]
    srows += [row(n, f"${{KICAD10_SYMBOL_DIR}}/{n}.kicad_sym") for n in sorted(sym_libs - {D.PLIB})]
    frows = [row(D.PLIB, "${KIPRJMOD}/libs/SC.pretty")]
    frows += [row(n, f"${{KICAD10_FOOTPRINT_DIR}}/{n}.pretty") for n in sorted(fp_libs - {D.PLIB})]
    (OUT / "sym-lib-table").write_text("(sym_lib_table\n  (version 7)\n" + "\n".join(srows) + "\n)\n", encoding="utf-8")
    (OUT / "fp-lib-table").write_text("(fp_lib_table\n  (version 7)\n" + "\n".join(frows) + "\n)\n", encoding="utf-8")


def project_file():
    pro = OUT / f"{PROJECT}.kicad_pro"
    data = json.loads(pro.read_text()) if pro.exists() else {}
    data.setdefault("meta", {"filename": pro.name, "version": 3})
    erc = data.setdefault("erc", {})
    rs = erc.setdefault("rule_severities", {})
    # global labels are used as the inter-sheet connection method on purpose
    rs.update({"global_label_dangling": "error", "isolated_pin_label": "warning",
               "single_global_label": "warning", "lib_symbol_mismatch": "warning"})
    data.setdefault("sheets", [])
    pro.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main(extra_fp_builders=()):
    OUT.mkdir(parents=True, exist_ok=True)
    ptext = build_libs(extra_fp_builders)
    design = D.build()
    design.sheets.sort(key=lambda sd: sd.file)
    src = schgen.SymbolSource(D.PLIB, ptext)
    power = {r: ("power:GND" if r == "GND" else f"{D.PLIB}:PWR_{r}") for r in D.RAILS}
    root_uuid = schgen.uid(PROJECT, "root")
    sheets = []
    nc_all = []
    sym_libs, fp_libs = {"power"}, set()
    for i, sd in enumerate(design.sheets):
        sh = schgen.Sheet(PROJECT, root_uuid, sd.name, sd.file, sd.title, i + 2, src, power, sd.notes)
        sh.layout(sd.parts)
        for k, net in enumerate(sd.flags):
            sh.add_flag(net, 25.4 + k * 17.78, sh.paper[2] - 30)
        sh.write(OUT / sd.file, COMPANY, REV)
        sheets.append(sh)
        nc_all += sh.nc_report
        for p in sd.parts:
            sym_libs.add(p.lib_id.split(":")[0])
            if p.footprint:
                fp_libs.add(p.footprint.split(":")[0])
    schgen.write_root(OUT / f"{PROJECT}.kicad_sch", PROJECT, root_uuid, sheets,
                      "StratosCore Rev A - Claude one-shot candidate (NOT FOR MANUFACTURE)", COMPANY, REV, [
                          "Candidate produced for owner comparison with the Astra pass. docs/ASTRA_HANDOFF.md is NOT READY;",
                          "every open gate (O05 battery safety, display controlled drawing/samples, RF values, assembler approvals) remains open.",
                          "Values marked TBD are deliberately not invented. See ../README.md and ../docs/ISSUES.md.",
                      ])
    lib_tables(sym_libs, fp_libs)
    project_file()
    (OUT / "reports").mkdir(exist_ok=True)
    (OUT / "reports" / "unassigned_pins.txt").write_text("\n".join(nc_all) + "\n", encoding="utf-8")
    r = subprocess.run([CLI, "sch", "erc", "--format", "json", "--severity-all", "--output",
                        str(OUT / "reports" / "erc.json"), str(OUT / f"{PROJECT}.kicad_sch")],
                       capture_output=True, text=True)
    print(r.stdout[-2000:], r.stderr[-2000:])
    rep = json.loads((OUT / "reports" / "erc.json").read_text(encoding="utf-8"))
    counts = {}
    for s in rep.get("sheets", []):
        for v in s.get("violations", []):
            counts[(v["severity"], v["type"])] = counts.get((v["severity"], v["type"]), 0) + 1
    for k, v in sorted(counts.items()):
        print(f"ERC {k[0]:8s} {k[1]:35s} {v}")
    print("unassigned pins auto-NC:", len(nc_all))
    return rep


if __name__ == "__main__":
    main()
