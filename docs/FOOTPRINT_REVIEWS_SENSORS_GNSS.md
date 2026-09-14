# Footprint reviews: sensors, GNSS and RF parts

Status: reviewed 2026-09-14. This file separates accepted project candidates from examined geometry that is not safe to release. A filename that names an exact component is not evidence that its land pattern matches that component.

## TDK InvenSense `ICM-42688-P` — footprint still open

- No project footprint is accepted yet.
- An upstream KiCad `LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y` footprint was examined and rejected as an exact-part project footprint because its embedded provenance points to an STMicroelectronics LSM6DS3TR-C package rather than the controlling TDK drawing.
- DS-000347 v1.9 establishes the body, pitch and terminal facts, but the land, solder-mask and stencil geometry still needs a direct comparison with the exact TDK package drawing and AN-000393.
- AN-000393 remained unavailable to automated retrieval on 2026-09-14. A human-controlled download and independent CAD review are required before a footprint is created or released.

## u-blox `MAX-M10S-00B` — footprint still open

- No project footprint is accepted yet.
- A candidate copied from a SparkFun production board was examined and rejected as the project footprint because its pad coordinates were not independently derived from the official u-blox land-pattern figure and its required paste pattern was incomplete.
- The controlling sources remain the MAX-M10S datasheet R08 package drawing and integration manual UBX-20053088 R05 Figure 30, Figure 31 and Tables 44/45.
- The next CAD pass must transcribe the official copper, mask, paste, keepout and pin-1 geometry, then obtain an independent pad-by-pad comparison before release.

## Hirose `U.FL-R-SMT-1(60)` — RF receptacles

- **Candidate footprint:** `hardware/footprints/Hirose_U.FL-R-SMT-1_60_Vertical.kicad_mod`
- **Source lineage:** vendored from the upstream KiCad library `Connector_Coaxial.pretty/U.FL_Hirose_U.FL-R-SMT-1_Vertical.kicad_mod`, whose embedded description cites Hirose drawing 0000940668 for the U.FL-R-SMT-1 family. The `(60)` suffix is reel packaging and does not change the SMT land.
- **Status:** candidate only. Independent comparison against Hirose drawing CL0331-0472-2-60, the manufacturer no-trace area and the cable/tool access envelope remains mandatory before layout release.

## TI `TPD1E0B04DPYR` — GNSS RF ESD shunt

- **Candidate footprint:** `hardware/footprints/TI_TPD1E0B04DPYR_X1SON-2_DPY0002A.kicad_mod`
- **Source lineage:** built from the example-board-layout dimensions in TI datasheet `TPD1E0B04`, package DPY0002A: two 0.3 x 0.5 mm lands on a 0.7 mm span, with TI's solder-mask-defined preference recorded.
- **Status:** direct manufacturer transcription completed; an independent visual/dimensional check still gates layout release.

## Release boundary

Only the U.FL and TPD1E0B04 candidate files remain in `hardware/footprints/` from this review. None of the footprints in this directory is released for manufacture until the remaining independent checks are recorded. The RP2040 support and storage group is covered by [the digital footprint review](FOOTPRINT_REVIEWS_DIGITAL.md).
