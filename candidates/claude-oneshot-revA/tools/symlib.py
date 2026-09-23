"""Project symbol library writer: rectangular IC symbols from datasheet pin tables and
named power symbols for every project rail."""
from __future__ import annotations

import math
import re
from pathlib import Path

from schgen import KICAD_SYM, balanced, esc

G = 2.54


def _f(size=1.27, extra=""):
    return f'(effects (font (size {size} {size})){extra})'


def ic_symbol(name: str, pins: list, ref: str = "U", footprint: str = "", datasheet: str = "",
              description: str = "", value: str | None = None) -> str:
    """pins: list of (number, name, etype, side) with side in L/R/T/B.
    Order within a side is top-to-bottom (L/R) or left-to-right (T/B)."""
    sides = {s: [p for p in pins if p[3] == s] for s in "LRTB"}
    maxlen = max([len(p[1]) for p in pins] + [4])
    lr_rows = max(len(sides["L"]), len(sides["R"]), 1)
    tb_cols = max(len(sides["T"]), len(sides["B"]), 1)
    # body size (multiples of 2*G so half sizes stay on grid)
    char = 0.9
    half_w = max(math.ceil((maxlen * char * (2 if sides["L"] and sides["R"] else 1) + 3) / 2 / G) * G,
                 math.ceil(((tb_cols + 1) * G) / 2 / G) * G, 2 * G)
    half_h = max(math.ceil(((lr_rows + 1) * G) / 2 / G) * G, 2 * G)
    if sides["T"] or sides["B"]:
        half_h += math.ceil(maxlen * char / G) * G
    lines = []
    for side in "LRTB":
        plist = sides[side]
        n = len(plist)
        for i, (num, pname, etype, _) in enumerate(plist):
            if side in "LR":
                y = (n - 1) * G / 2 - i * G
                y = round(round(y / 1.27) * 1.27, 3)
                x = -half_w - G if side == "L" else half_w + G
                ang = 0 if side == "L" else 180
            else:
                x = -(n - 1) * G / 2 + i * G
                x = round(round(x / 1.27) * 1.27, 3)
                y = half_h + G if side == "T" else -half_h - G
                ang = 270 if side == "T" else 90
            lines.append(
                f'(pin {etype} line (at {x} {y} {ang}) (length {G}) '
                f'(name "{esc(pname)}" {_f()}) (number "{esc(num)}" {_f()}))')
    body = (f'(rectangle (start {-half_w} {half_h}) (end {half_w} {-half_h}) '
            f'(stroke (width 0.254) (type default)) (fill (type background)))')
    val = value or name
    return (
        f'(symbol "{name}" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)\n'
        f'  (property "Reference" "{ref}" (at {-half_w} {half_h + 1.27} 0) {_f(1.27, " (justify left bottom)")})\n'
        f'  (property "Value" "{esc(val)}" (at {-half_w} {-half_h - 1.27} 0) {_f(1.27, " (justify left top)")})\n'
        f'  (property "Footprint" "{esc(footprint)}" (at 0 0 0) {_f(1.27, " (hide yes)")})\n'
        f'  (property "Datasheet" "{esc(datasheet)}" (at 0 0 0) {_f(1.27, " (hide yes)")})\n'
        f'  (property "Description" "{esc(description)}" (at 0 0 0) {_f(1.27, " (hide yes)")})\n'
        f'  (symbol "{name}_0_1" {body})\n'
        f'  (symbol "{name}_1_1"\n    ' + "\n    ".join(lines) + '\n  )\n  (embedded_fonts no)\n)')


def power_symbol(net: str, ground: bool = False) -> str:
    """Global power symbol named after the rail (net name == Value)."""
    src = (KICAD_SYM / "power.kicad_sym").read_text(encoding="utf-8")
    base = "GND" if ground else "+3V3"
    m = re.search(r'\n\s*\(symbol\s+"%s"\s*\n' % re.escape(base), src)
    block = balanced(src, src.index("(", m.start()))
    name = "PWR_" + re.sub(r"[^A-Za-z0-9_]", "_", net)
    block = block.replace(f'(symbol "{base}_', f'(symbol "{name}_')
    block = block.replace(f'(symbol "{base}"', f'(symbol "{name}"', 1)
    block = re.sub(r'(\(property\s+"Value"\s+)"[^"]*"', lambda mm: f'{mm.group(1)}"{esc(net)}"', block, count=1)
    block = re.sub(r'(\(property\s+"Description"\s+)"(?:[^"\\]|\\.)*"',
                   lambda mm: f'{mm.group(1)}"Power symbol creates a global net named {esc(net)}"', block, count=1)
    return block


def write_library(path: Path, blocks: list):
    body = "\n".join(blocks)
    path.write_text(f'(kicad_symbol_lib (version 20241209) (generator "stratos_claude_oneshot") '
                    f'(generator_version "10.0")\n{body}\n)\n', encoding="utf-8")
