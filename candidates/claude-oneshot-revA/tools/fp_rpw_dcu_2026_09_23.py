"""Regenerate the 2026-09-23 corrected TPS259474L RPW and TXU0202 DCU candidate footprints.

Run from candidates/claude-oneshot-revA/kicad/libs/SC.pretty with any Python 3.
Sources (see ../docs/REFINEMENT_2026_09_23.md):
  RPW0010A: TI SLVSFC9C PDF pp.72-74, drawing 4225183/A 08/2019 (copper p.73, stencil p.74)
  DCU0008A: TI SCES942A PDF pp.32-34, drawing 4225266/A 09/2014 (exact copy of the reviewed
            hardware/footprints baseline file plus a 3D model reference)
"""
import uuid


def U():
    return f'(uuid "{uuid.uuid4()}")'

# --- TXU0202 DCU: exact baseline copy + candidate 3D model reference
src = open('../../../../../hardware/footprints/TI_DCU0008A_VSSOP-8_2.3x2mm_P0.5mm_TXU0202.kicad_mod', encoding='utf-8').read().rstrip()
assert src.endswith(')')
src = src[:-1] + ' (model "${KICAD10_3DMODEL_DIR}/Package_SO.3dshapes/VSSOP-8_2.3x2mm_P0.5mm.step" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))\n)\n'
open('TI_DCU0008A_VSSOP-8_2.3x2mm_P0.5mm_TXU0202.kicad_mod', 'w', encoding='utf-8', newline='\n').write(src)

# --- RPW0010A
L = []
L.append('(footprint "TI_RPW0010A_VQFN-HR-10_2x2mm_P0.45mm" (version 20241229) (generator "stratos_claude_oneshot") (generator_version "10.0")')
L.append('  (layer "F.Cu") (descr "TPS259474LRPWR; TI RPW0010A (SLVSFC9C PDF pp.72-74, drawing 4225183/A 08/2019). Copper from p.73 land example (vector-extracted 2026-09-23): L-shaped corner lands 1/4/7/10 = 0.6x0.3 + 0.25x0.65 union, side lands 0.6x0.25 at X+/-0.9 Y+/-0.225, center lands 5/6 0.3x2.4 at X+/-0.25. Paste from p.74 stencil example (0.100 mm stencil): corner 93 pct, center split 2x 0.28x1.06 (82 pct), side 1:1. NSMD mask. CANDIDATE - assembler mask/stencil approval and independent review required") (attr smd)')
L.append(f'  (property "Reference" "REF**" (at 0 -1.8 0) (layer "F.SilkS") {U()} (effects (font (size 0.6 0.6) (thickness 0.1))))')
L.append(f'  (property "Value" "TI_RPW0010A_VQFN-HR-10_2x2mm_P0.45mm" (at 0 1.8 0) (layer "F.Fab") {U()} (effects (font (size 0.5 0.5) (thickness 0.08))))')


def pad(num, x, y, w, h, layers, rr):
    L.append(f'  (pad "{num}" smd roundrect (at {x:.4f} {y:.4f} 0) (size {w:.4f} {h:.4f}) (layers {layers}) (roundrect_rratio {rr:.4f}) {U()})')

CM = '"F.Cu" "F.Mask"'
CMP = '"F.Cu" "F.Mask" "F.Paste"'
P = '"F.Paste"'
for num, sx, sy in (('1', -1, -1), ('4', -1, 1), ('7', 1, 1), ('10', 1, -1)):
    pad(num, sx * 0.9, sy * 0.7, 0.6, 0.3, CM, 0.05 / 0.3)          # horizontal leg x[0.6,1.2] y[0.55,0.85]
    pad(num, sx * 0.725, sy * 0.875, 0.25, 0.65, CM, 0.05 / 0.25)   # vertical leg x[0.6,0.85] y[0.55,1.2]
    pad('', sx * 0.9, sy * 0.6875, 0.6, 0.275, P, 0.05 / 0.275)     # paste y[0.55,0.825]
    pad('', sx * 0.7125, sy * 0.875, 0.225, 0.65, P, 0.05 / 0.225)  # paste x[0.6,0.825]
for num, x, y in (('2', -0.9, -0.225), ('3', -0.9, 0.225), ('8', 0.9, 0.225), ('9', 0.9, -0.225)):
    pad(num, x, y, 0.6, 0.25, CMP, 0.05 / 0.25)
for num, x in (('5', -0.25), ('6', 0.25)):
    pad(num, x, 0, 0.3, 2.4, CM, 0.05 / 0.3)
    for y in (-0.63, 0.63):
        pad('', x, y, 0.28, 1.06, P, 0.05 / 0.28)
L.append(f'  (fp_rect (start -1.45 -1.45) (end 1.45 1.45) (stroke (width 0.05) (type default)) (fill no) (layer "F.CrtYd") {U()})')
L.append(f'  (fp_poly (pts (xy -0.75 -1) (xy 1 -1) (xy 1 1) (xy -1 1) (xy -1 -0.75)) (stroke (width 0.1) (type default)) (fill no) (layer "F.Fab") {U()})')
L.append(f'  (fp_text user "${{REFERENCE}}" (at 0 0 0) (layer "F.Fab") {U()} (effects (font (size 0.4 0.4) (thickness 0.06))))')
L.append(f'  (fp_circle (center -1.35 -1.35) (end -1.27 -1.35) (stroke (width 0.16) (type default)) (fill yes) (layer "F.SilkS") {U()})')
L.append('  (model "${KIPRJMOD}/libs/SC.3dshapes/TI_RPW0010A_VQFN-HR-10_2x2mm_P0.45mm.step" (offset (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))')
L.append(')')
open('TI_RPW0010A_VQFN-HR-10_2x2mm_P0.45mm.kicad_mod', 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
