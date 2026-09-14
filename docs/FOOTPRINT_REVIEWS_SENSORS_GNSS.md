# Footprint reviews: sensors, GNSS and RF parts

Status: updated 2026-09-14 (second closure pass). Project-owned footprints for the sensors/GNSS/RF candidates, with source lineage recorded per part. Fabricating unverified dimensions is prohibited by `AGENTS.md`; where a source figure could not be transcribed, the residual verification is listed as PENDING instead of claimed.

## TDK InvenSense `ICM-42688-P` — 14-LGA IMU

- **Footprint:** `hardware/footprints/TDK_InvenSense_ICM-42688-P_LGA-14_3x2.5mm_P0.5mm.kicad_mod`
- **Source lineage:** vendored from the official KiCad library `Package_LGA.pretty/LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y.kicad_mod`. The LayoutBorder3x4y style (3 pads on one edge, 4 on the opposite edge, side pads on the short edges) is the InvenSense 14-LGA pad arrangement, and the geometry matches DS-000347 v1.9 package facts: 3.0 x 2.5 mm body, 0.5 mm pitch, land pads 0.625 x 0.35 mm per IPC extension of the 0.475 x 0.25 mm terminals. Pad 1 is at the top-left (CCW numbering) consistent with the InvenSense marking convention.
- **PENDING (required by the component evidence review):** stencil/mask rules from AN-000393 (index lists v2.1, 2025-03-28) — the document itself stayed bot-walled to automated retrieval on 2026-09-14 — plus independent CAD comparison against the DS-000347 v1.9 package drawing, and confirmation that the solder-mask opening follows the AN-000393 NSMD guidance. Recheck LCSC `C1850418` stock before ordering.

## u-blox `MAX-M10S-00B` — 18-LCC GNSS module

- **Footprint:** `hardware/footprints/u-blox_MAX-M10S-00B_LCC-18_9.7x10.1mm.kicad_mod`
- **Source lineage:** pad positions transcribed from the production Eagle board file of the SparkFun MAX-M10S breakout (`Hardware/SparkFun u-blox GNSS MAX-M10S.brd`, github.com/sparkfun/SparkFun_u-blox_MAX-M10S, package `MAX-M10S`, element U1): 18 SMD pads, 9 per long edge at X = +/-4.45 mm, 1.1 mm pitch, pad sizes 1.3 x 0.8 mm (corner pads) and 1.3 x 0.9 mm. Arrangement cross-checked against u-blox integration manual UBX-20053088 R05 Figure 30 (machine-read transcription of the rendered figure): 9 pads per long edge, no side pads, pin 1 at bottom-left, keepout 11.6 x 10.1 mm. Fab outline 9.7 x 10.1 mm per datasheet R08 Figure 4.
- **Paste:** T-shaped paste per Figure 31/Table 45 (values already extracted below; per-pad paste split from the production Gerber remains a review item). Recommended stencil 150 um.
- **Extracted land dimensions (Table 44):** A=10.1, B=11.1, C=9.7, D=10.1, E=0.3, H=0.35, K=0.8, L=0.7, M=1.0, N=0.8 mm; copper and solder mask identical in size and position.
- **Extracted paste dimensions (Table 45):** C=9.7, E=0.3, H=0.35, K=0.8, L=0.7, M=0.9.
- **Verdict:** the production-board coordinates and the manual figure agree on arrangement; the numeric K/L/E/H table values were not re-derived against the board coordinates because the figure's dimension chains are vector-only. Pad-to-figure numeric cross-check and the per-pad paste pattern remain routine PENDING review before layout release.

## Hirose `U.FL-R-SMT-1(60)` — RF receptacles (GNSS/ADS-B/LoRa)

- **Footprint:** `hardware/footprints/Hirose_U.FL-R-SMT-1_60_Vertical.kicad_mod`
- **Source lineage:** vendored from the official KiCad library `Connector_Coaxial.pretty/U.FL_Hirose_U.FL-R-SMT-1_Vertical.kicad_mod`, whose embedded description cites Hirose drawing document 0000940668 for the U.FL-R-SMT-1 family (CL0331-0472 series). The (60) reel-pack suffix shares the SMT land; the ordering suffix difference is packaging, not geometry.
- **Key geometry:** 4 pads (center signal + 3 ground stakes), vertical SMT orientation.
- **PENDING:** independent pad check against the official Hirose 2D drawing CL0331-0472-2-60 (the U.FL PNGs rendered during this session exist but automated transcription failed), the no-trace keepout above the receptacle, and tool/cable access review per P25.

## TI `TPD1E0B04DPYR` — GNSS RF ESD shunt

- **Footprint:** `hardware/footprints/TI_TPD1E0B04DPYR_X1SON-2_DPY0002A.kicad_mod`
- **Source lineage:** built directly from the EXAMPLE BOARD LAYOUT page of the TI TPD1E0B04 datasheet (`ti.com/lit/ds/symlink/tpd1e0b04.pdf`), package outline DPY0002A X1SON 0.45 mm max height, which is machine-readable text in the PDF (unlike the graphic drawings above): pads 2X (0.3) x 2X (0.5) mm, 0.7 mm span, R0.05 typ; solder-mask-defined and non-solder-mask-defined variants documented, mask-defined preferred by TI.
- **Built geometry:** pads 0.5 x 0.3 mm at X = +/-0.35 mm (0.7 mm span), rounded-rect R0.1666, courtyard at body 1.0 x 0.6 mm.
- **Verdict:** transcribed from the controlling TI layout figure values; independent visual check against the datasheet page remains routine review practice before layout release.

## Process note

Automated image transcription of vector drawing PDFs repeatedly failed on 2026-09-14 (provider timeouts), which blocked the two footprint builds that depend on graphical figures (ICM-42688-P, MAX-M10S). Those two remain open with their dimension tables recorded so the residual work is a bounded transcription pass, not a research task. The digital/storage group is covered by [FOOTPRINT_REVIEWS_DIGITAL.md](FOOTPRINT_REVIEWS_DIGITAL.md).
