# Footprint reviews: sensors, GNSS and RF parts

Status: created 2026-09-14. Project-owned footprints for the sensors/GNSS/RF candidates, with source lineage recorded per part. Fabricating unverified dimensions is prohibited by `AGENTS.md`; where an automated transcription of a vector-only drawing was not possible, the residual verification is explicitly listed as PENDING instead of claimed.

## TDK InvenSense `ICM-42688-P` — 14-LGA IMU

- **Footprint:** NONE RELEASED YET — custom land/mask/stencil work remains the owning task (O19).
- **Extracted electrical/package facts:** DS-000347 v1.9 confirms the 2.5 x 3.0 x 0.91 mm 14-LGA, 0.5 mm pitch, terminals 0.475 x 0.25 mm nominal, 1 MHz I2C maximum, WHO_AM_I 0x47 (recorded in [component evidence](COMPONENT_EVIDENCE.md) 2026-09-11/14 review).
- **Assembly rules source:** AN-000393 (IMU PCB Design and MEMS Assembly Guidelines; the official index lists v2.1, 2025-03-28) controls land pattern, solder-paste printing, keep-out over the MEMS die, routing-under-package and board-edge rules.
- **Blocking issue:** both the TDK download portal and reseller mirrors of AN-000393 returned bot-walled HTML to automated retrieval on 2026-09-14, and the package drawing in DS-000347 is vector-only; the spatial land geometry cannot be transcribed without either document. Do not build this footprint from generic LGA-14 library pads (explicitly prohibited by the component evidence review).
- **PENDING:** retrieve AN-000393 (human download) and the DS-000347 package drawing; transcribe land, mask, stencil and keep-out; independent CAD comparison; recheck LCSC `C1850418` stock before ordering.

## u-blox `MAX-M10S-00B` — 18-LCC GNSS module

- **Footprint:** NONE RELEASED YET — the dimension tables were extracted, the T-shaped paste pattern layout remains pending.
- **Extracted land dimensions (integration manual UBX-20053088 R05, Figure 30 / Table 44):** A=10.1, B=11.1, C=9.7, D=10.1, E=0.3, H=0.35, K=0.8, L=0.7, M=1.0, N=0.8 mm. Copper and solder mask have identical size and position.
- **Extracted paste dimensions (Figure 31 / Table 45):** C=9.7, E=0.3, H=0.35, K=0.8, L=0.7, M=0.9, plus remaining table symbols; recommended stencil thickness 150 um; T-shaped paste extending beyond the copper mask to improve half-via wetting (manual text quoted in the review session log).
- **Blocking issue:** Figures 30/31 encode the pad arrangement (18 pads: 3+5 per long side pattern plus corner castellations per the LCC style) graphically. Writing a `.kicad_mod` from the tables alone requires assuming the per-pad placement, which would be fabrication. The exact figure-to-coordinates mapping needs the rendered figure or a human transcription pass.
- **PENDING:** transcribe Figure 30 pad positions from the rendered drawing (human or CAD tool), build the footprint with paste per Table 45, independent CAD comparison per P20.

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
