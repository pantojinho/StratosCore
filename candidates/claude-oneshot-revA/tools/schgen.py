"""Hierarchical KiCad 10 schematic writer used by the Claude one-shot candidate.

Design notes (several ideas adapted from pantojinho/hermes-kicad-pcb `sch_gen.py`, MIT,
commit c87e8d4; see ../README.md "Tool provenance"):

* library Y grows up, sheet Y grows down: pin (px, py) of a symbol at (x, y) sits at
  (x + px, y - py);
* derived (`extends`) library symbols are flattened before embedding;
* every connected pin gets a short wire stub pointing away from the body followed by a
  global label (signals and rails) or, on vertical two-pin passives, a power symbol;
* pins without a net get an explicit no-connect flag, and the list is reported so
  nothing is left open silently;
* every coordinate is snapped to the 1.27 mm grid.

The generator is netlist-first: `design.py` states (reference, pin number, net); this
module only draws it.
"""
from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path


def _strip_ws(text: str) -> str:
    return re.sub(r"[ 	]+
", "
", text)

GRID = 1.27
DIRS = {0: (1, 0), 90: (0, -1), 180: (-1, 0), 270: (0, 1)}
KICAD_SYM = Path("C:/Program Files/KiCad/10.0/share/kicad/symbols")
PAPERS = [("A4", 297, 210), ("A3", 420, 297), ("A2", 594, 420), ("A1", 841, 594), ("A0", 1189, 841)]


def snap(v: float) -> float:
    return round(round(v / GRID) * GRID, 4)


def uid(*parts: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "/".join(parts)))


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def balanced(text: str, start: int) -> str:
    depth = 0
    instr = False
    j = start
    while j < len(text):
        ch = text[j]
        if instr:
            if ch == "\\":
                j += 2
                continue
            if ch == '"':
                instr = False
        else:
            if ch == '"':
                instr = True
            elif ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    return text[start:j + 1]
        j += 1
    raise ValueError("unbalanced s-expression")


def strip_blocks(text: str, head: str) -> str:
    out, i = [], 0
    while (k := text.find(head, i)) >= 0:
        out.append(text[i:k])
        i = k + len(balanced(text, k))
    return "".join(out) + text[i:]


@dataclass
class Pin:
    number: str
    name: str
    etype: str
    x: float
    y: float
    angle: int
    length: float


@dataclass
class LibSymbol:
    lib_id: str
    block: str
    pins: dict
    bbox: tuple
    power: bool


_LIB_TEXT: dict = {}


def _lib_text(path: Path) -> str:
    if path not in _LIB_TEXT:
        _LIB_TEXT[path] = path.read_text(encoding="utf-8", errors="replace")
    return _LIB_TEXT[path]


def _raw_block(lib_file: Path, name: str) -> str:
    text = _lib_text(lib_file)
    m = re.search(r'\n\s*\(symbol\s+"%s"\s*\n' % re.escape(name), text)
    if not m:
        raise KeyError(f"symbol {name} not in {lib_file}")
    return balanced(text, text.index("(", m.start()))


def parse_symbol(block: str, lib: str, name: str, lib_file: Path | None = None) -> LibSymbol:
    if (m := re.search(r'\(extends\s+"([^"]+)"\)', block)):
        parent = m.group(1)
        pblock = _raw_block(lib_file, parent)
        if re.search(r'\(extends\s+"', pblock):
            pblock = parse_symbol(pblock, "__tmp", parent, lib_file).block.replace(
                f'(symbol "__tmp:{parent}"', f'(symbol "{parent}"', 1)
        child_props = re.findall(r'\(property\s+"([^"]+)"\s+"((?:[^"\\]|\\.)*)"', block)
        for key, val in child_props:
            pblock = re.sub(r'(\(property\s+"%s"\s+)"(?:[^"\\]|\\.)*"' % re.escape(key),
                            lambda mm, v=val: f'{mm.group(1)}"{v}"', pblock, count=1)
        block = pblock.replace(f'(symbol "{parent}_', f'(symbol "{name}_')
        block = block.replace(f'(symbol "{parent}"', f'(symbol "{name}"', 1)
    block = block.replace(f'(symbol "{name}"', f'(symbol "{lib}:{name}"', 1)
    pins = {}
    for m in re.finditer(r'\(pin\s+(\w+)\s+\w+', block):
        pb = balanced(block, m.start())
        at = re.search(r'\(at\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\)', pb)
        num = re.search(r'\(number\s+"([^"]*)"', pb)
        nam = re.search(r'\(name\s+"([^"]*)"', pb)
        ln = re.search(r'\(length\s+([-\d.]+)\)', pb)
        hidden = "(hide yes)" in pb.split("(name")[0]
        if at and num and num.group(1) not in pins:
            pins[num.group(1)] = Pin(num.group(1), nam.group(1) if nam else "",
                                     "hidden" if hidden else m.group(1),
                                     float(at.group(1)), float(at.group(2)),
                                     int(float(at.group(3))) % 360, float(ln.group(1)) if ln else 0)
            pins[num.group(1)].etype = m.group(1)
    geo = strip_blocks(strip_blocks(block, "(property "), "(pin ")
    pts = [(float(a), float(b)) for a, b in
           re.findall(r'\((?:start|end|xy|mid|center)\s+([-\d.]+)\s+([-\d.]+)\)', geo)]
    for p in pins.values():
        dx, dy = DIRS.get(p.angle, (0, 0))
        pts += [(p.x, p.y), (p.x + dx * p.length, p.y - dy * p.length)]
    xs, ys = [p[0] for p in pts] or [0], [p[1] for p in pts] or [0]
    return LibSymbol(f"{lib}:{name}", block, pins, (min(xs), min(ys), max(xs), max(ys)),
                     power="(power" in block[:300])


class SymbolSource:
    """Resolves lib ids against the KiCad install and the project library."""

    def __init__(self, project_lib_name: str, project_lib_text: str):
        self.plib = project_lib_name
        self.ptext = project_lib_text
        self.cache: dict = {}

    def get(self, lib_id: str) -> LibSymbol:
        if lib_id in self.cache:
            return self.cache[lib_id]
        lib, name = lib_id.split(":", 1)
        if lib == self.plib:
            m = re.search(r'\n\s*\(symbol\s+"%s"\s' % re.escape(name), self.ptext)
            if not m:
                raise KeyError(f"{lib_id} not in project library")
            block = balanced(self.ptext, self.ptext.index("(", m.start()))
            sym = parse_symbol(block, lib, name)
        else:
            f = KICAD_SYM / f"{lib}.kicad_sym"
            sym = parse_symbol(_raw_block(f, name), lib, name, f)
        self.cache[lib_id] = sym
        return sym


FONT = '(effects (font (size {s} {s})){extra})'


def font(extra: str = "", size: float = 1.27) -> str:
    return FONT.format(s=size, extra=extra)


@dataclass
class Placed:
    ref: str
    sym: LibSymbol
    x: float
    y: float
    uid: str

    def pin_xy(self, num: str):
        p = self.sym.pins[num]
        return snap(self.x + p.x), snap(self.y - p.y)


@dataclass
class Part:
    ref: str
    lib_id: str
    value: str
    footprint: str
    conns: dict                      # pin number -> net ("" = explicit no-connect)
    fields: dict = field(default_factory=dict)
    dnp: bool = False
    group: str = ""


class Sheet:
    """One child sheet: parts are placed by a shelf packer, then connected."""

    def __init__(self, project: str, root_uuid: str, name: str, file: str, title: str,
                 page: int, src: SymbolSource, power_nets: set, notes: list):
        self.project, self.root_uuid = project, root_uuid
        self.name, self.file, self.title, self.page = name, file, title, page
        self.uuid = uid(project, "sheet", file)
        self.src = src
        self.power_nets = power_nets
        self.notes = notes
        self.items: list = []
        self.lib: dict = {}
        self.placed: dict = {}
        self.taken: dict = {}
        self.nc_report: list = []
        self._n = 0
        self.paper = ("A3", 420, 297)

    # ------------------------------------------------------------------ placement
    def _envelope(self, part: Part, sym: LibSymbol):
        x0, y0, x1, y1 = sym.bbox
        left = right = up = down = 0.0
        for num, net in part.conns.items():
            if num not in sym.pins or not net:
                continue
            p = sym.pins[num]
            out = (p.angle + 180) % 360
            ln = 3.2 + len(net) * 1.05 if not (self._is_power_sym(net) and self._vertical2(sym)) else 6
            if out == 180:
                left = max(left, ln)
            elif out == 0:
                right = max(right, ln)
            elif out == 90:
                up = max(up, ln)
            else:
                down = max(down, ln)
        # text for reference/value fields
        tw = max(len(part.ref), len(part.value)) * 1.05 + 1.5
        if (x1 - x0) < 6:
            right = max(right, (x1 - x0) / 2 + tw)
            up, down = max(up, 2.5), max(down, 2.5)
        else:
            up += 6
            right = max(right, tw - (x1 - x0))
        return (x0 - left - 1.0, -y1 - up, x1 + right + 1.0, -y0 + down)

    def _vertical2(self, sym: LibSymbol) -> bool:
        return len(sym.pins) <= 2 and (sym.bbox[2] - sym.bbox[0]) < 6

    def _is_power_sym(self, net: str) -> bool:
        return net in self.power_nets

    def layout(self, parts: list):
        """Group-aware shelf packing: parts with the same `group` stay together."""
        groups: list = []
        for p in parts:
            if groups and groups[-1][0] == p.group and p.group:
                groups[-1][1].append(p)
            else:
                groups.append((p.group, [p]))
        blocks = []
        for gname, gparts in groups:
            # inside a group: first part (usually the IC) on the left, passives in columns
            cells = []
            for p in gparts:
                sym = self.src.get(p.lib_id)
                ex = self._envelope(p, sym)
                cells.append((p, sym, ex))
            blocks.append((gname, cells))

        margin = 20.0
        for paper in PAPERS[1:]:
            ok, placement = self._try_pack(blocks, paper[1] - 2 * margin, paper[2] - 2 * margin - 25)
            if ok:
                self.paper = paper
                break
        else:
            ok, placement = self._try_pack(blocks, PAPERS[-1][1] - 2 * margin, 1e9)
            self.paper = PAPERS[-1]
        for p, sym, x, y in placement:
            self._place(p, sym, margin + x, margin + 12 + y)

    def _try_pack(self, blocks, width, height):
        placement = []
        cx = cy = 0.0
        row_h = 0.0
        for gname, cells in blocks:
            # pack the group internally: main part, then passives in columns of max 30 mm
            gplace = []
            gx = 0.0
            col_x = 0.0
            col_y = 0.0
            col_w = 0.0
            gh = 0.0
            first = True
            for p, sym, (ex0, ey0, ex1, ey1) in cells:
                w, h = ex1 - ex0, ey1 - ey0
                if first or w > 25:
                    if not first:
                        col_x += col_w + 4
                        col_y = 0.0
                        col_w = 0.0
                    gplace.append((p, sym, col_x - ex0, -ey0))
                    col_x += w + 4
                    gh = max(gh, h)
                    first = False
                    continue
                if col_y + h > max(gh, 45) and col_y > 0:
                    col_x += col_w + 3
                    col_y = 0.0
                    col_w = 0.0
                gplace.append((p, sym, col_x - ex0, col_y - ey0))
                col_y += h + 2
                col_w = max(col_w, w)
                gh = max(gh, col_y)
            gw = col_x + col_w
            if cx > 0 and cx + gw > width:
                cx = 0.0
                cy += row_h + 10
                row_h = 0.0
            for p, sym, x, y in gplace:
                placement.append((p, sym, cx + x, cy + y))
            cx += gw + 12
            row_h = max(row_h, gh)
            if cy + row_h > height:
                return False, placement
        return True, placement

    def _place(self, part: Part, sym: LibSymbol, x: float, y: float):
        x, y = snap(x), snap(y)
        su = uid(self.project, "sym", part.ref)
        pl = Placed(part.ref, sym, x, y, su)
        self.placed[part.ref] = pl
        self.lib[sym.lib_id] = sym
        bx0, by0, bx1, by1 = sym.bbox
        narrow = (bx1 - bx0) < 6
        if narrow:
            fx, jr = x + bx1 + 1.27, " (justify left)"
            ry, vy = y - 1.27, y + 1.27
        else:
            fx, jr = x + bx0, " (justify left)"
            ry, vy = y - by1 - 3.81, y - by1 - 1.27
        props = [
            f'(property "Reference" "{part.ref}" (at {snap(fx)} {snap(ry)} 0) {font(jr)})',
            f'(property "Value" "{esc(part.value)}" (at {snap(fx)} {snap(vy)} 0) {font(jr)})',
            f'(property "Footprint" "{esc(part.footprint)}" (at {x} {y} 0) {font(" (hide yes)")})',
        ]
        for k, v in part.fields.items():
            props.append(f'(property "{esc(k)}" "{esc(str(v))}" (at {x} {y} 0) {font(" (hide yes)")})')
        pins = "".join(f'(pin "{n}" (uuid "{uid(su, n)}"))' for n in sym.pins)
        self.items.append(
            f'(symbol (lib_id "{sym.lib_id}") (at {x} {y} 0) (unit 1)\n'
            f'  (exclude_from_sim no) (in_bom {"no" if part.ref.startswith(("#", "TP", "FID")) or part.ref[:1] == "H" else "yes"}) (on_board yes) (dnp {"yes" if part.dnp else "no"})\n'
            f'  (uuid "{su}")\n  ' + "\n  ".join(props) + f'\n  {pins}\n'
            f'  (instances (project "{self.project}" (path "/{self.root_uuid}/{self.uuid}" '
            f'(reference "{part.ref}") (unit 1)))))')
        # connections
        for num, net in part.conns.items():
            if num not in sym.pins:
                raise KeyError(f"{part.ref}: pin {num} not in {sym.lib_id}")
            if net:
                self.connect(pl, num, net)
        for num, p in sym.pins.items():
            tip = pl.pin_xy(num)
            if num in part.conns and part.conns[num]:
                continue
            if tip in self.taken:
                continue
            self.taken[tip] = ""
            if p.etype == "no_connect":
                continue
            self.items.append(f'(no_connect (at {tip[0]} {tip[1]}) (uuid "{uid(self.uuid, "nc", part.ref, num)}"))')
            if num not in part.conns:
                self.nc_report.append(f"{part.ref}.{num} ({p.name}) not assigned -> NC flag")

    # ------------------------------------------------------------------ drawing
    def _wire(self, a, b):
        self.items.append(f'(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) '
                          f'(stroke (width 0) (type default)) (uuid "{uid(self.uuid, "w", str(a), str(b))}"))')

    def _label(self, net, at, out):
        just = "left" if out in (0, 90) else "right"
        self.items.append(
            f'(global_label "{esc(net)}" (shape passive) (at {at[0]} {at[1]} {out}) '
            f'(fields_autoplaced yes) {font(f" (justify {just})")} (uuid "{uid(self.uuid, "gl", net, str(at))}")'
            f' (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {at[0]} {at[1]} 0) {font(" (hide yes)")}))')

    def _power(self, net, at, out):
        lib_id = self.power_nets[net]
        sym = self.src.get(lib_id)
        self.lib[lib_id] = sym
        body = next(iter(sym.pins.values())).angle
        rot = (out - body) % 360
        self._n += 1
        ref = f"#PWR{self.page:02d}{self._n:03d}"
        dx, dy = DIRS[out]
        tx, ty = at[0] + dx * 3.81, at[1] + dy * 3.81
        su = uid(self.uuid, "pwr", str(at), net)
        self.items.append(
            f'(symbol (lib_id "{lib_id}") (at {at[0]} {at[1]} {rot}) (unit 1)\n'
            f'  (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no) (uuid "{su}")\n'
            f'  (property "Reference" "{ref}" (at {at[0]} {at[1]} 0) {font(" (hide yes)")})\n'
            f'  (property "Value" "{esc(net)}" (at {snap(tx)} {snap(ty)} 0) {font()})\n'
            f'  (property "Footprint" "" (at {at[0]} {at[1]} 0) {font(" (hide yes)")})\n'
            f'  (pin "1" (uuid "{uid(su, "1")}"))\n'
            f'  (instances (project "{self.project}" (path "/{self.root_uuid}/{self.uuid}" '
            f'(reference "{ref}") (unit 1)))))')

    def connect(self, pl: Placed, num: str, net: str):
        tip = pl.pin_xy(num)
        if (have := self.taken.get(tip)) is not None:
            if have != net:
                raise ValueError(f"{pl.ref}.{num}: point {tip} carries {have}, not {net}")
            return
        self.taken[tip] = net
        out = (pl.sym.pins[num].angle + 180) % 360
        stub = 2.54
        end = (snap(tip[0] + DIRS[out][0] * stub), snap(tip[1] + DIRS[out][1] * stub))
        self._wire(tip, end)
        if net in self.power_nets and self._vertical2(pl.sym) and out in (90, 270):
            natural = 270 if net.startswith("GND") else 90
            if natural == out:
                self._power(net, end, out)
                return
        self._label(net, end, out)

    def add_flag(self, net: str, x: float, y: float):
        """PWR_FLAG for nets fed from outside the drawn circuit (connector, cells)."""
        sym = self.src.get("power:PWR_FLAG")
        self.lib[sym.lib_id] = sym
        self._n += 1
        at = (snap(x), snap(y))
        su = uid(self.uuid, "flag", net)
        ref = f"#FLG{self.page:02d}{self._n:03d}"
        self.items.append(
            f'(symbol (lib_id "power:PWR_FLAG") (at {at[0]} {at[1]} 0) (unit 1)\n'
            f'  (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no) (uuid "{su}")\n'
            f'  (property "Reference" "{ref}" (at {at[0]} {at[1]} 0) {font(" (hide yes)")})\n'
            f'  (property "Value" "PWR_FLAG" (at {at[0]} {snap(at[1] - 3.81)} 0) {font()})\n'
            f'  (property "Footprint" "" (at {at[0]} {at[1]} 0) {font(" (hide yes)")})\n'
            f'  (pin "1" (uuid "{uid(su, "1")}"))\n'
            f'  (instances (project "{self.project}" (path "/{self.root_uuid}/{self.uuid}" '
            f'(reference "{ref}") (unit 1)))))')
        end = (at[0], snap(at[1] + 2.54))
        self._wire(at, end)
        self._label(net, end, 270)

    def text(self, s: str, x: float, y: float, size: float = 1.27, bold: bool = False):
        b = " (bold yes)" if bold else ""
        self.items.append(f'(text "{esc(s)}" (exclude_from_sim no) (at {snap(x)} {snap(y)} 0) '
                          f'(effects (font (size {size} {size}){b}) (justify left top)) (uuid "{uid(self.uuid, "t", s[:40], str(y))}"))')

    def write(self, path: Path, company: str, rev: str):
        # title + notes at the top of the sheet
        self.text(self.title, 20, 8, 2.5, True)
        ny = 14.0
        for n in self.notes:
            self.text(n, 20, ny, 1.27)
            ny += 2.54
        libs = "\n    ".join(s.block for s in self.lib.values())
        body = "\n  ".join(self.items)
        path.write_text(_strip_ws(
            f'(kicad_sch (version 20250114) (generator "stratos_claude_oneshot") (generator_version "10.0")\n'
            f'  (uuid "{self.uuid}")\n  (paper "{self.paper[0]}")\n'
            f'  (title_block (title "{esc(self.title)}") (rev "{rev}") (company "{esc(company)}") '
            f'(comment 1 "CANDIDATE - NOT FOR MANUFACTURE - see README gates"))\n'
            f'  (lib_symbols\n    {libs}\n  )\n  {body}\n  (embedded_fonts no)\n)\n'), encoding="utf-8")


def write_root(path: Path, project: str, root_uuid: str, sheets: list, title: str,
               company: str, rev: str, notes: list):
    items = []
    x0, y0 = 25.4, 40.64
    w, h = 60.96, 20.32
    for i, s in enumerate(sheets):
        col, row = i % 4, i // 4
        x, y = snap(x0 + col * (w + 22.86)), snap(y0 + row * (h + 17.78))
        items.append(
            f'(sheet (at {x} {y}) (size {w} {h}) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)\n'
            f'  (fields_autoplaced yes) (stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0.0000))\n'
            f'  (uuid "{s.uuid}")\n'
            f'  (property "Sheetname" "{esc(s.name)}" (at {x} {snap(y - 0.7112)} 0) {font(" (justify left bottom)")})\n'
            f'  (property "Sheetfile" "{s.file}" (at {x} {snap(y + h + 0.5)} 0) {font(" (justify left top)")})\n'
            f'  (instances (project "{project}" (path "/{root_uuid}" (page "{s.page}")))))')
    ny = 20.32
    items.append(f'(text "{esc(title)}" (exclude_from_sim no) (at 25.4 {ny} 0) '
                 f'(effects (font (size 3 3) (bold yes)) (justify left top)) (uuid "{uid(project, "roottitle")}"))')
    ny = snap(y0 + ((len(sheets) + 3) // 4) * (h + 17.78) + 5)
    for n in notes:
        items.append(f'(text "{esc(n)}" (exclude_from_sim no) (at 25.4 {ny} 0) '
                     f'(effects (font (size 1.5 1.5)) (justify left top)) (uuid "{uid(project, "rootnote", n[:30])}"))')
        ny = snap(ny + 3.0)
    body = "\n  ".join(items)
    path.write_text(
        f'(kicad_sch (version 20250114) (generator "stratos_claude_oneshot") (generator_version "10.0")\n'
        f'  (uuid "{root_uuid}")\n  (paper "A3")\n'
        f'  (title_block (title "{esc(title)}") (rev "{rev}") (company "{esc(company)}") '
        f'(comment 1 "CANDIDATE - NOT FOR MANUFACTURE - see README gates"))\n'
        f'  (lib_symbols)\n  {body}\n  (sheet_instances (path "/" (page "1")))\n  (embedded_fonts no)\n)\n',
        encoding="utf-8")
