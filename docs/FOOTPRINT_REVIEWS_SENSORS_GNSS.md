# Footprint reviews: sensors, GNSS and RF parts

Status: reviewed 2026-09-14. This file separates accepted project candidates from examined geometry that is not safe to release. A filename that names an exact component is not evidence that its land pattern matches that component.

## TDK InvenSense `ICM-42688-P` — manufacturer-derived candidate

- **Candidate footprint:** `hardware/footprints/TDK_ICM-42688-P_LGA-14_3x2.5mm_P0.5mm.kicad_mod`.
- **Controlling sources:** DS-000347 v1.9, dated 2024-11-12, Figure 5 and Section 10.2; AN-000393 v2.4, dated 2026-02-09, Sections 2.1-2.4 and Figure 1. Exact PDFs were retrieved from TDK's versioned CloudFront resources and visually reviewed 2026-09-14.
- **Package and pin order:** nominal 3.0 x 2.5 x 0.91 mm body, 14 terminals and 0.5 mm pitch. In the datasheet top view, pins 1-4 run down the left, 5-7 left-to-right along the bottom, 8-11 up the right and 12-14 right-to-left along the top. Pin 1 is the top-left side terminal.
- **Copper:** AN-000393 says LGA land length and width equal the package-terminal length and width. DS-000347 gives nominal 0.475 x 0.25 mm terminals. Left/right row centers are X = +/-1.1625 mm with Y = -0.75, -0.25, 0.25 and 0.75 mm; top/bottom centers are Y = +/-0.9125 mm with X = -0.5, 0 and 0.5 mm.
- **Solder mask:** AN-000393 recommends no solder mask under the package where the board process permits it. The candidate therefore includes a nominal 3.0 x 2.5 mm body opening. The per-pad rule also adds 0.1 mm to both land dimensions as the documented fallback. The assembler must choose and approve the final opening against registration and process capability.
- **Paste:** AN-000393 specifies a 90% stencil-opening-to-land ratio and at least 100 micrometer stencil thickness subject to aspect ratio >= 1.5 and area ratio >= 0.66. The candidate preserves pad aspect ratio and interprets 90% as copper area (linear scale `sqrt(0.90)`). At 100 micrometers the smallest aperture calculates to aspect ratio 2.372 and area ratio 0.777; at 125 micrometers the area ratio is only 0.622. The calculated thickness ceiling is about 117.7 micrometers. The assembler must confirm whether 90% means area or linear dimension and choose a compatible approximately 100 micrometer/step-down process or revise the aperture.
- **Placement/assembly:** a central 1.8 x 1.3 mm rule area blocks traces, vias and copper pours on all four locked copper layers while leaving perimeter fanout possible. Final layout review must confirm that the complete under-body area outside the necessary symmetrical fanout also remains clear. Keep power, charger/DC-DC and high-speed/high-current signals away; place VDD/VDDIO decoupling close; place the sensor on a mechanically stable region away from anchors, board edges, buttons, connectors, speakers and heat sources. Do not snap panel tabs or use ultrasonic cleaning.
- **Independent second pass:** a separate pad-by-pad review on 2026-09-14 found no critical/high mismatch in identity, package, top-view pin order, centers, pitch, copper or per-pad mask expansion. It identified the paste/stencil ambiguity, full-body mask-registration gate, missing keepout and an out-of-courtyard pin-1 marker. The marker and central keepout were corrected; their final parse/audit is recorded below.
- **Validation boundary:** KiCad 10 parses and exports the footprint, and an automated geometry audit passes for 14 numbered lands, 14 paste apertures, pitch, positions, sizes, pin order, 90% paste area, body mask opening and central keepout. **Assembler mask/paste approval and final PCB placement/routing review still gate schematic/PCB release.**
- The upstream KiCad `LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y` file remains rejected for this exact part: its embedded source is an STMicroelectronics package and its 0.625 x 0.35 mm pads are larger than the TDK rule.

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

The ICM-42688-P, MAX-M10S, U.FL and TPD1E0B04 candidate files remain in `hardware/footprints/` from this review. None is released for manufacture until the remaining independent checks are recorded. The RP2040 support and storage group is covered by [the digital footprint review](FOOTPRINT_REVIEWS_DIGITAL.md).
