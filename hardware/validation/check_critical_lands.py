"""Check selected land patterns against drawing dimensions and pairwise spacing.

Run with KiCad 10's Python (pcbnew). Sources and interpretation are recorded in
docs/FOOTPRINT_CORRECTIONS_2026_09_23.md. This is not an assembly-process approval.
"""

import argparse
import math
import subprocess
import sys
from pathlib import Path

import pcbnew


def export_drc_fixture(library, names, output):
    """Disposable board: unique net on each copper pad exposes internal shorts."""
    output.mkdir(parents=True, exist_ok=True)
    board = pcbnew.BOARD()
    vector = lambda x, y: pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))
    for index, name in enumerate(names):
        fp = pcbnew.FootprintLoad(str(library), name)
        fp.SetReference(f"U{index + 1}")
        board.Add(fp)
        fp.SetPosition(vector(10 + 10 * index, 10))
        for pad in fp.Pads():
            if pad.IsOnLayer(pcbnew.F_Cu):
                net = pcbnew.NETINFO_ITEM(board, f"{fp.GetReference()}_PIN_{pad.GetNumber()}")
                board.Add(net)
                pad.SetNet(net)
    corners = [(2, 2), (38, 2), (38, 18), (2, 18)]
    for start, end in zip(corners, corners[1:] + corners[:1]):
        edge = pcbnew.PCB_SHAPE()
        edge.SetShape(pcbnew.SHAPE_T_SEGMENT)
        edge.SetLayer(pcbnew.Edge_Cuts)
        edge.SetStart(vector(*start))
        edge.SetEnd(vector(*end))
        edge.SetWidth(pcbnew.FromMM(0.05))
        board.Add(edge)
    path = output / "lands.kicad_pcb"
    pcbnew.SaveBoard(str(path), board)
    cli = Path(sys.executable).with_name("kicad-cli.exe")
    command = str(cli) if cli.exists() else "kicad-cli"
    subprocess.run([command, "pcb", "drc", "--format", "json", "--severity-all",
                    "--output", str(output / "drc.json"), str(path)], check=True)
    print(f"Review ALL reported DRC items in {output / 'drc.json'}; no checks are suppressed.")


def check(library, name, expected, envelope):
    footprint = pcbnew.FootprintLoad(str(library), name)
    if footprint is None:
        raise ValueError(f"Cannot load {name}")
    pads = [pad for pad in footprint.Pads() if pad.IsOnLayer(pcbnew.F_Cu)]
    actual = {}
    for pad in pads:
        number = pad.GetNumber()
        if number in actual or not number:
            raise ValueError(f"{name}: duplicate or unnumbered copper pad {number!r}")
        if abs(pad.GetOrientationDegrees()) > 1e-6:
            raise ValueError(f"{name}: rotated pad needs polygon-distance review")
        pos, size = pad.GetPosition(), pad.GetSize()
        actual[number] = tuple(pcbnew.ToMM(v) for v in (pos.x, pos.y, size.x, size.y))
    if actual.keys() != expected.keys():
        raise ValueError(f"{name}: pad-number set differs from manufacturer map")
    errors = []
    for number, geometry in actual.items():
        if any(abs(a - b) > 0.000001 for a, b in zip(geometry, expected[number])):
            errors.append(f"pad {number}: {geometry}, source expected {expected[number]}")
    minimum = math.inf
    for i, (number, (x, y, w, h)) in enumerate(actual.items()):
        for other, (xx, yy, ww, hh) in list(actual.items())[i + 1:]:
            dx, dy = abs(x - xx) - (w + ww) / 2, abs(y - yy) - (h + hh) / 2
            gap = math.hypot(max(dx, 0), max(dy, 0))
            minimum = min(minimum, gap)
            if dx < -1e-6 and dy < -1e-6:
                errors.append(f"copper boxes overlap: pads {number}/{other}")
            elif gap < 0.2 - 1e-6:
                errors.append(f"pads {number}/{other}: gap {gap:.6f} mm < 0.200 mm")
    bounds = (
        max(x + w / 2 for x, y, w, h in actual.values()) - min(x - w / 2 for x, y, w, h in actual.values()),
        max(y + h / 2 for x, y, w, h in actual.values()) - min(y - h / 2 for x, y, w, h in actual.values()),
    )
    if any(abs(a - b) > 1e-6 for a, b in zip(bounds, envelope)):
        errors.append(f"copper envelope {bounds}, expected {envelope}")
    if errors:
        raise ValueError(name + "\n  " + "\n  ".join(errors))
    print(f"PASS {name}: {len(pads)} pads; minimum bounding-box gap {minimum:.3f} mm; copper {bounds}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, default=Path(__file__).resolve().parents[1] / "footprints")
    parser.add_argument("--drc-output", type=Path, help="Create a disposable DRC fixture/report here; inspect all findings")
    args = parser.parse_args()
    mmc = {}
    for i, t in enumerate([0.75, 0.25, -0.25, -0.75]):
        mmc[str(i + 1)] = (t, -1.275, 0.3, 0.45)
        mmc[str(i + 5)] = (-1.275, -t, 0.45, 0.3)
        mmc[str(i + 9)] = (-t, 1.275, 0.3, 0.45)
        mmc[str(i + 13)] = (1.275, t, 0.45, 0.3)
    bmp = dict(zip(map(str, range(1, 11)), [
        (-0.7625, -0.25, 0.325, 0.3), (-0.7625, 0.25, 0.325, 0.3),
        (-0.5, 0.7625, 0.3, 0.325), (0, 0.7625, 0.3, 0.325), (0.5, 0.7625, 0.3, 0.325),
        (0.7625, 0.25, 0.325, 0.3), (0.7625, -0.25, 0.325, 0.3),
        (0.5, -0.7625, 0.3, 0.325), (0, -0.7625, 0.3, 0.325), (-0.5, -0.7625, 0.3, 0.325),
    ]))
    txu = dict(zip(map(str, range(1, 9)), [
        (x, y, 0.85, 0.3) for x, y in [(-1.55, -0.75), (-1.55, -0.25), (-1.55, 0.25), (-1.55, 0.75),
                                    (1.55, 0.75), (1.55, 0.25), (1.55, -0.25), (1.55, -0.75)]
    ]))
    failures = []
    cases = [
        ("MEMSIC_MMC5983MA_LGA-16_3x3mm_P0.5mm", mmc, (3.0, 3.0)),
        ("Bosch_BMP581_LGA-10_2x2mm", bmp, (1.85, 1.85)),
        ("TI_DCU0008A_VSSOP-8_2.3x2mm_P0.5mm_TXU0202", txu, (3.95, 1.8)),
    ]
    for name, expected, envelope in cases:
        try:
            check(args.library, name, expected, envelope)
        except ValueError as exc:
            failures.append(str(exc))
    if failures:
        raise SystemExit("\n".join(failures))
    if args.drc_output:
        export_drc_fixture(args.library, [name for name, _, _ in cases], args.drc_output)


if __name__ == "__main__":
    main()
