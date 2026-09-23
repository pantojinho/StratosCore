# Footprint corrections and rejected local drafts

Reviewed 2026-09-23 against rendered manufacturer drawings. These changes repair candidate geometry; assembler mask/paste, board-level electrical mapping, placement and production release remain open. The Claude comparison snapshot is not modified.

## Corrections integrated into hardware/footprints

| Part and controlling source | Correct interpretation | Change |
| --- | --- | --- |
| MMC5983MA, [MEMSIC Rev A](https://www.memsic.com/Public/Uploads/uploadfile/files/20220119/MMC5983MADatasheetRevA.pdf), p.20, released 2019-04-03 | 2.550 mm is opposing pad-center spacing; 0.450 x 0.300 mm lands, 0.500 mm pitch | Radial centers changed from +/-1.050 to +/-1.275 mm; outer copper span is 3.000 mm. This removes four overlapping corner pairs, including SDA/SCL. Pin 1 remains top-right as shown in the manufacturer top view. The silk index/reference were moved clear of copper and each other. |
| BMP581, [Bosch BST-BMP581-DS004-13](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp581-ds004.pdf), Figures 29/30/32, pp.68-69 | 1.525 mm is opposing pad-center spacing; 0.325 x 0.300 mm lands and at least 0.200 mm gap | Copper and provisional paste centers changed from +/-0.600 to +/-0.7625 mm; outer copper span is 1.850 mm. Bottom-view numbering was mirrored into the PCB top view: pins 1/2 on left, 3/4/5 bottom, 6/7 right, 8/9/10 top. Pin-1 corner and port position agree with Figure 29. The reference was moved away from the silk outline. |
| TXU0202DCUR, [TI SCES942A](https://www.ti.com/lit/ds/symlink/txu0202.pdf), PDF pp.32-34, DCU0008A drawing 4225266/A, 2014-09 | Top-view body is X=2.3 mm, Y=2.0 mm; 3.1 mm is land-row **center spacing**, not outside extent | New `TI_DCU0008A_VSSOP-8_2.3x2mm_P0.5mm_TXU0202.kicad_mod`: centers X=+/-1.55 mm, Y=+/-0.75 and +/-0.25 mm; eight 0.85 x 0.30 mm lands; 3.95 x 1.80 mm copper envelope. Pins 1-4 descend the left side and 5-8 ascend the right. The existing DGS/0.65 mm file is rejected for this MPN and retained only for traceability. |

The sensor corrections supersede the earlier dimensional-review claims in `FOOTPRINT_REVIEWS_SENSORS_GNSS.md`. Those reviews compared files against incorrectly transcribed dimensions and did not detect the resulting copper overlap/clearance defects. Passing a parser or matching an assertion derived from the same mistaken interpretation is not independent drawing validation.

## Rejected local drafts: do not integrate

Uncommitted drafts from earlier agent work were checked before publication. The following claims are withdrawn; they must not override these rendered-drawing results:

- **TCA9535PWR:** the draft `TI_PW0024A_TSSOP-24_4.4x6.4mm_P0.65mm_TCA9535` incorrectly uses the lead span as the body length. [TI SCPS201F](https://www.ti.com/lit/ds/symlink/tca9535.pdf), PDF p.38, PW0024A drawing 4220208/A (2017-02), shows a 4.3-4.5 by 7.7-7.9 mm body, with 6.2-6.6 mm span **across** the leads. The original 4.4 x 7.8 mm body graphic is correct. TI's p.39 land example uses 1.5 x 0.45 mm lands on X=+/-2.9 mm, Y pitch 0.65 mm; the original generic candidate's different pad sizes still need an explicit assembly/density disposition. Do not adopt the 6.4 mm body draft or its approval claim.
- **TXU0202DCUR:** the draft `TI_DCU0008A_VSSOP-8_2x2.3mm_P0.5mm_TXU0202` swapped the body axes and subtracted land length from the 3.1 mm **center** dimension, producing X=+/-1.125 mm. Both are wrong. Use the newly derived 2.3 x 2 mm candidate above, subject to review.
- **TPS259474LRPWR:** both the original RPU assignment and the local rectangular-pad `TI_RPW0010A_VQFN-HR-10_2x2mm_TPS25947` draft are rejected. [TI SLVSFC9C](https://www.ti.com/lit/ds/symlink/tps25947.pdf), PDF pp.72-74, RPW0010A drawing 4225183/A (2019-08), shows L-shaped corner lands and two 0.3 x 2.4 mm center lands. The local draft's straight corner lands and 0.3 x 1.45 mm center lands do not reproduce it. The 1.45 mm annotation is a horizontal center-to-center dimension, not the center-land length. The candidate under `candidates/claude-oneshot-revA/` has a separate RPW construction and still requires its own pad/paste audit; it is not approved by this note.

## Reproducible validation

Run from the repository root with KiCad 10's Python and `pcbnew` installed:

```powershell
& 'C:/Program Files/KiCad/10.0/bin/python.exe' hardware/validation/check_critical_lands.py --drc-output "$env:TEMP/stratos-lands-validation"
```

Linux equivalent, using the Python interpreter supplied/configured with KiCad:

```sh
python3 hardware/validation/check_critical_lands.py --drc-output /tmp/stratos-lands-validation
```

On KiCad 10.0.6, all three source-coordinate/pin-map checks pass and minimum nominal copper bounding-box gap is 0.200 mm for each. A regression run against the two files at commit `6a49704` rejects the MMC5983MA pad-1/pad-16 overlap and the BMP581 0.0375 mm corner gap. The disposable board gives every copper pad a distinct net so same-net assignments cannot conceal internal shorts.

Fresh fixture DRC: **45 solder-mask-bridge findings, zero other violations and zero unconnected items**. All 45 are the pair combinations of the ten BMP581 terminals within its intentionally common 2.2 mm mask opening. They were not suppressed. Bosch's no-mask recommendation does not itself approve an assembler's process: retain that disposition for assembler review and verify mask output on the final board. These fixture results do not describe the full Claude PCB, certify solder yield, or close any 2S/RF/mechanical gate. The BMP581 central routing keepout remains partial; final layout review must enforce the complete under-body requirement.

## Next review actions

1. Independently compare these corrected sensor/DCU files, exported apertures and top-view pin numbering against the cited drawings; then obtain assembler mask/stencil decisions before final board assignment.
2. Derive/review the exact RPW corner, center, mask and paste polygons; do not reuse the rejected draft. Complete the other DIG-04 exact-part reviews.
3. Keep candidate and baseline libraries explicit: correcting a `.kicad_mod` does not automatically update an embedded PCB footprint. Any later board update must show the actual pad diff, rerun DRC and reconcile connectivity.
