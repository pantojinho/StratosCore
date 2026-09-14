# Footprint reviews: RP2040 support and storage parts

Status: created 2026-09-14. Project-owned footprints for the RP2040 support and storage candidates. Provenance is recorded per part; anything not yet verified against the exact manufacturer drawing is explicitly marked PENDING. Fabrication of unverified dimensions is prohibited by `AGENTS.md`, so this document records source lineage instead of pretending a completed independent transcription.

## Winbond `W25Q128JVSIQ` — boot flash

- **Footprint:** `hardware/footprints/Winbond_W25Q128JVSIQ_SOIC-8_5.3x5.3mm_P1.27mm.kicad_mod`
- **Source lineage:** vendored from the official KiCad footprint library `Package_SO.pretty/SOIC-8_5.3x5.3mm_P1.27mm.kicad_mod` (footprint-generator output, JEITA ED-7311-19 variation 08-001-BBA, 208-mil body width). This is the 5.3 x 5.3 mm, 1.27 mm pitch SOIC-8 body family that the Winbond W25Q128JV DTR Rev B datasheet specifies.
- **Key geometry (from the vendored library file):** 8 x SMD rect pads 1.625 x 0.65 mm, X = +/-3.5875 mm, Y pitch 1.905 mm; courtyard 4.65 mm half-span; pin-1 silk triangle.
- **Verdict:** standard library matches the package family; the project owns a vendored copy so PCB data does not depend on external library versions.
- **Remaining:** pad-to-datasheet cross-check against the Winbond package drawing page, and status-register/boot bring-up per [digital support review](DIGITAL_SUPPORT_REVIEW.md) remain PENDING (bring-up is a prototype gate regardless).
- **Supply snapshot:** DigiKey showed 57,555 units at USD 4.21 (quantity 1) on 2026-09-14 (project snapshot; recheck at purchase).

## Abracon `ABM8-272-T3` — 12 MHz RP2040 reference clock

- **Footprint:** `hardware/footprints/Abracon_ABM8-272-T3_Crystal_SMD_3225-4Pin_3.2x2.5mm.kicad_mod`
- **Source lineage:** vendored from the official KiCad library `Crystal.pretty/Crystal_SMD_3225-4Pin_3.2x2.5mm.kicad_mod` (standard 4-pad 3225 crystal land, generated from the TXC 7M-family drawing). The exact-MPN Abracon source-control drawing #456603 Rev B (2024-09-16, official `abracon.com/datasheets/ABM8-272-T3.pdf`) confirms the 3.2 x 2.5 x 0.8 mm package, 4 pads, 50 ohm max ESR, 10 pF CL, 30 ppm tolerance/stability, and Raspberry Pi RP2040/RP235x approval.
- **Application context (not footprint data):** Raspberry Pi's *Hardware design with RP2040* recommends this exact crystal with two 15 pF load capacitors and a 1 kohm series damping resistor.
- **Verdict:** standard 3225 land geometry vendored; **independent pad-to-drawing transcription of drawing #456603 is PENDING** — the drawing's dimension figures are vector-only and automated image transcription failed on 2026-09-14. Do not release for layout until a human or CAD tool verifies pad width/length/spacing against page 4 of the drawing.
- **Supply snapshot:** DigiKey showed 29,393 units at USD 0.71 (quantity 1) on 2026-09-14 (project snapshot; recheck at purchase).

## Hirose `DM3AT-SF-PEJM5` — microSD socket

- **Footprint:** `hardware/footprints/Hirose_DM3AT-SF-PEJM5_microSD_HC.kicad_mod`
- **Source lineage:** vendored from the official KiCad library `Connector_Card.pretty/microSD_HC_Hirose_DM3AT-SF-PEJM5.kicad_mod`. Its embedded description cites Hirose's own 2D drawing for the exact part (download key `DM3AT-SF-PEJM5`, doc_file_id 44099), which is the same controlled drawing family as the official Hirose "DRAWING FOR REFERENCE" PDF dated Aug. 1, 2026 retrieved during this review (8 contacts + card-detect switch + 4 shell stakes; 13.85 x 15.95 x 1.68 mm body per the [digital support review](DIGITAL_SUPPORT_REVIEW.md)).
- **Key geometry (from the vendored library file):** pads 1-8 (contacts), 9-10 (card detect), SH x4 (shell stakes), SMD rect, right-angle top-board orientation.
- **Verdict:** exact-MPN official library footprint vendored; **independent pad-by-pad comparison against the Aug. 2026 Hirose drawing is PENDING** and must include the card insertion/locked/eject envelope before the enclosure edge is fixed.
- **Supply snapshot:** DigiKey regional pages showed about 29,700 units at about USD 5.20 (quantity 1) on 2026-09-14 (project snapshot; recheck at purchase).

## Process note

Automated image transcription of vector drawing PDFs was attempted repeatedly on 2026-09-14 and failed (provider timeouts), so the vendor-and-record approach above was used for these three parts: official generated libraries with controlled-drawing citations, vendored into the project, with the residual human verification explicitly listed instead of silently claimed. The sensors/GNSS/RF footprints are covered by [FOOTPRINT_REVIEWS_SENSORS_GNSS.md](FOOTPRINT_REVIEWS_SENSORS_GNSS.md).
