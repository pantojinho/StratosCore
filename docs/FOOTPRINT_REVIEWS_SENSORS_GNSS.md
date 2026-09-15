# Footprint reviews: sensors, GNSS and RF parts

Status: reviewed 2026-09-14. This file separates accepted project candidates from examined geometry that is not safe to release. A filename that names an exact component is not evidence that its land pattern matches that component.

## TDK InvenSense `ICM-42688-P` — footprint still open

- No project footprint is accepted yet.
- An upstream KiCad `LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y` footprint was examined and rejected as an exact-part project footprint because its embedded provenance points to an STMicroelectronics LSM6DS3TR-C package rather than the controlling TDK drawing.
- DS-000347 v1.9 establishes the body, pitch and terminal facts, but the land, solder-mask and stencil geometry still needs a direct comparison with the exact TDK package drawing and AN-000393.
- AN-000393 remained unavailable to automated retrieval on 2026-09-14. A human-controlled download and independent CAD review are required before a footprint is created or released.

## u-blox `MAX-M10S-00B` — manufacturer-derived candidate

- **Candidate footprint:** `hardware/footprints/u-blox_MAX-M10S-00B_LCC-18_10.1x9.7mm.kicad_mod`
- **Controlling sources:** MAX-M10S datasheet UBX-20035208 R08 Figures 2/4 and integration manual UBX-20053088 R05 Figure 30/Table 44 plus Figure 31/Table 45, visually reviewed 2026-09-14 from the official u-blox PDFs.
- **Copper and solder mask:** 18 rectangular lands at 1.1 mm pitch. Pads 1/9/10/18 are 0.7 x 1.8 mm; the other pads are 0.8 x 1.8 mm. Land centers are X = -4.4 through +4.4 mm and Y = +/-4.75 mm in the Figure 30 orientation. Copper and mask are coincident, as u-blox requires.
- **Pin order:** Figure 30 puts pin 1 at bottom-left; pins 1-9 run left-to-right on the bottom row and 10-18 run right-to-left on the top row. This was cross-checked against the datasheet top view, which is rotated 90 degrees relative to Figure 30.
- **Paste:** each terminal uses the u-blox T-shaped recommendation. The outer segment is 1.4 mm long at full 0.7/0.8 mm land width; the inner segment is 0.9 mm long at 0.5/0.6 mm width. Outer-to-outer paste span is 12.5 mm and the inner gap is 7.9 mm. The manual recommends a 150 micrometer stencil and says the assembler must adapt the recommendation to its process.
- **Mechanical/review boundary:** the 10.1 x 9.7 mm nominal body, 11.1 x 10.1 mm manufacturer keepout and de-paneling-tab warning are recorded. KiCad 10 parsed and exported the footprint to SVG, and an automated geometry audit passed. **Independent pad-by-pad review and assembler paste approval still gate release.**
- A previous SparkFun-derived candidate was rejected and removed because it lacked a direct manufacturer derivation and the prescribed paste pattern.

## Hirose `U.FL-R-SMT-1(60)` — RF receptacles

- **Candidate footprint:** `hardware/footprints/Hirose_U.FL-R-SMT-1_60_Vertical.kicad_mod`
- **Source lineage:** vendored from the upstream KiCad library `Connector_Coaxial.pretty/U.FL_Hirose_U.FL-R-SMT-1_Vertical.kicad_mod`, whose embedded description cites Hirose drawing 0000940668 for the U.FL-R-SMT-1 family. The `(60)` suffix is reel packaging and does not change the SMT land.
- **Status:** candidate only. Independent comparison against Hirose drawing CL0331-0472-2-60, the manufacturer no-trace area and the cable/tool access envelope remains mandatory before layout release.

## TI `TPD1E0B04DPYR` — GNSS RF ESD shunt

- **Candidate footprint:** `hardware/footprints/TI_TPD1E0B04DPYR_X1SON-2_DPY0002A.kicad_mod`
- **Source lineage:** built from the example-board-layout dimensions in TI datasheet `TPD1E0B04`, package DPY0002A: two 0.3 x 0.5 mm lands on a 0.7 mm span, with TI's solder-mask-defined preference recorded.
- **Status:** direct manufacturer transcription completed; an independent visual/dimensional check still gates layout release.

## Release boundary

The MAX-M10S, U.FL and TPD1E0B04 candidate files remain in `hardware/footprints/` from this review. None is released for manufacture until the remaining independent checks are recorded. The RP2040 support and storage group is covered by [the digital footprint review](FOOTPRINT_REVIEWS_DIGITAL.md).
