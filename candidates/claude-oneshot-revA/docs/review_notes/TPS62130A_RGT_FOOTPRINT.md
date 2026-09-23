# TPS62130A (U7) RGT footprint audit

Review date: 2026-09-23. Scope: the comparison candidate's TPS62130A land (`U7`, PWR-04 main buck) against TI's current package drawing. This note is a candidate review record, not a release approval. No `.kicad_pcb` or `.kicad_sch` file was changed.

## Sources

| Item | Value |
| --- | --- |
| Primary source | TI *TPS6213x 3-V to 17-V, 3-A Step-Down Converter in 3-mm x 3-mm QFN Package*, literature **SLVSAG7F** (Rev. F, November 2021 body), https://www.ti.com/lit/ds/symlink/tps62130a.pdf |
| Downloaded file | 43 pages, PDF metadata created 2026-09-04, SHA-256 `f9b1af285622c0cf1a5991f9641a6e64c5e6d899e52cc0b1632808742019579f` |
| Pinout | PDF p. 3, Figure 6-1 "16-Pin VQFN With Exposed Thermal Pad (RGT) Top View" and Table 6-1 |
| Orderable/package mapping | PDF p. 32 Package Option Addendum (dated 8-Jan-2026); pp. 35-38 Package Materials Information (dated 3-Sep-2026) |
| Package outline | PDF p. 40, **RGT0016C**, drawing **4222419/E 07/2025** |
| Land pattern example | PDF p. 41, RGT0016C, 4222419/E, scale 20X |
| Stencil example | PDF p. 42, RGT0016C, 4222419/E, scale 25X, 0.125 mm stencil |
| Secondary check | TI part-details page https://www.ti.com/product/TPS62130A/part-details/TPS62130ARGTR (fetched 2026-09-23): package image `rgt0016c.png`; linked `/lit/pdf/MPQF119H` is only a generic "RGT 16" view (4203495/I) that says "Refer to the product data sheet for package details". |

### Which RGT variant controls

- The addendum lists `TPS62130ARGTR`, `.A`, `.B`, `TPS62130ARGTRG4` and `TPS62130ARGTT` as Active, "VQFN (RGT) | 16", NIPDAU, MSL 2/260 C, marking PA6I. The addendum does not print the drawing suffix.
- The only RGT mechanical drawing appended to the current data sheet is **RGT0016C (4222419/E)**. The TI part-details page for `TPS62130ARGTR` also shows the `rgt0016c` package image.
- **No RGT0016A drawing exists in the current TI data sheet.** Nothing in the repository ties the candidate's "RGT0016A" name to a TI source. The candidate footprint's own `descr` cites an **onsemi NCN4555** data sheet. It is a copy of the generic KiCad `QFN-16-1EP_3x3mm_P0.5mm_EP1.75x1.75mm` footprint (the same lineage recorded in `docs/FOOTPRINT_REVIEWS_DIGITAL.md`, DIG-04 table), not a TI RGT0016A derivation.
- Conclusion: **RGT0016C / 4222419/E controls the footprint for `TPS62130ARGTR`.**

## Extraction method

PyMuPDF 1.28.2 rendered pp. 3 and 40-42 and extracted the vector paths with `page.get_drawings()`. Blue (land) and red (stencil) stroke segments were clustered into closed outlines, and their bounding boxes were measured.

- Scale on p. 41 (20X) is 56.693 pt/mm (= 20 x 72 / 25.4). It was confirmed from the dimensioned 0.5 mm pitch (28.346 pt between adjacent land centres) and the (2.8) span.
- Scale on p. 42 (25X) is 70.866 pt/mm, confirmed the same way (35.433 pt pitch).
- Corner radii were measured from the Bezier control points of the rounded corners.

All extracted values fall on the printed reference dimensions to within 0.001 mm.

## TI geometry (RGT0016C, 4222419/E)

Coordinates are KiCad top view: +X right, +Y down, origin at the package centre.

| Feature | Extracted value | Printed callout |
| --- | --- | --- |
| Body | 2.9-3.1 x 2.9-3.1 mm, 0.8-1.0 mm height | p. 40 |
| Terminal | width 0.18-0.30, length 0.3-0.5, pitch 0.5 | p. 40 |
| Package EP | 1.68 +/-0.07 square with pin-1 chamfer (optional) | p. 40 |
| Signal lands | 16x **0.60 x 0.24 mm**, R0.05 all corners | 16X (0.6), 16X (0.24), (R0.05) |
| Land row centres | **+/-1.400 mm**; land spans 1.10 to 1.70 mm from centre | (2.8) both axes |
| Land positions along side | -0.75, -0.25, +0.25, +0.75 | 12X (0.5) |
| Thermal land (pad 17) | **1.68 x 1.68 mm**, R0.05 | (square 1.68) |
| Signal-land to EP gap | 1.100 - 0.840 = **0.26 mm** | derived |
| Optional vias | 5x d0.20: (0,0) and (+/-0.58, +/-0.58) | (d0.2) TYP, (0.58) TYP, note 5 |
| Solder mask | NSMD preferred; opening at most 0.07 mm larger than the metal on each side (SMD alternative: 0.07 min metal under mask) | Solder mask details |
| Stencil: signal | 16x 0.60 x 0.24 mm, same centres (1:1 with the land) | p. 42 |
| Stencil: EP | **one 1.55 x 1.55 mm aperture**, R0.05, centred; "85% printed solder coverage by area" (1.55^2 / 1.68^2 = 85.1%) | p. 42 |
| Pin 1 | left side, top position; pins 1-4 run down the left side, 5-8 left to right along the bottom, 9-12 up the right side, 13-16 right to left along the top | pp. 3, 41 |

## Pad-by-pad comparison

The candidate is `candidates/claude-oneshot-revA/kicad/libs/SC.pretty/TI_RGT0016A_VQFN-16_3x3mm_EP1.75x1.75_TPS62130A.kicad_mod`. The baseline is `hardware/footprints/TI_RGT0016A_VQFN-16_3x3mm_EP1.75x1.75_TPS62130A.kicad_mod`. Their copper, mask and paste are identical; they differ only in the 3D model path (candidate `UQFN-16...EP1.75`, baseline `QFN-16...EP1.75`).

| Item | TI RGT0016C | Candidate / baseline (RGT0016A name) | Delta | New RGT0016C file |
| --- | --- | --- | --- | --- |
| Pin numbering / pin 1 | Pin 1 at left side, top; counter-clockwise | Same: pad 1 at (-1.4625, -0.75), pad 5 at (-0.75, +1.4625), pad 9 at (+1.4625, +0.75), pad 13 at (+0.75, -1.4625) | matches | same order |
| Positions along the side | +/-0.25, +/-0.75 | +/-0.25, +/-0.75 | 0 | same |
| Row centre | 1.400 | 1.4625 | +0.0625 outward | 1.400 |
| Land length | 0.60 | 0.775 | +0.175 | 0.60 |
| Land width | 0.24 | 0.25 | +0.01 | 0.24 |
| Land outer edge | 1.70 | 1.85 | +0.15 | 1.70 |
| Land inner edge | 1.10 | 1.075 | -0.025 (closer to EP) | 1.10 |
| Land corner radius | 0.05 | 0.0625 (rratio 0.25 x 0.25) | +0.0125 | 0.05 (rratio 0.208333) |
| EP copper | 1.68 x 1.68, R0.05 | 1.75 x 1.75, sharp rect | +0.07 per side overall (equals package EP max) | 1.68 x 1.68, R0.05 (rratio 0.029762) |
| Signal-to-EP gap | 0.26 | 0.20 | -0.06 | 0.26 |
| EP paste | 1 x 1.55 x 1.55, R0.05, 85% of 1.68^2 | 4 x 0.71 x 0.71 at (+/-0.44, +/-0.44), rratio 0.25; 2.016 mm^2 = 65.8% of its 1.75^2 land (71.4% of TI's 1.68^2) | about 14 points less paste than TI | 1 x 1.55 x 1.55, R0.05, paste-only unnumbered pad |
| Signal paste | 1:1 0.60 x 0.24 | 1:1 0.775 x 0.25 | follows land | 1:1 0.60 x 0.24 |
| Mask | NSMD, opening <= metal + 0.07 per side | no per-pad margin; board `pad_to_mask_clearance 0`, so opening = copper | within TI's "0.07 MAX" | unchanged (board default); assembler gate |
| Vias | optional 5x d0.2, 0.58 grid | none | n/a | none in copper; positions marked on `Cmts.User` only |
| Courtyard | not specified by TI | cross-shaped, +/-2.10 at pin rows / +/-1.75 at corners | n/a | rectangle +/-1.95 (0.25 beyond the 1.70 land edge) |
| Fab | body 3.0 nominal | 3.0 square with pin-1 chamfer | matches | same |
| Silk | n/a | corner ticks at +/-1.61, pin-1 triangle at x = -2.12..-2.45 | n/a | same (0.2 mm clear of the new lands) |
| 3D model | n/a | UQFN/QFN EP1.75 step | n/a | `WQFN-16-1EP_3x3mm_P0.5mm_EP1.68x1.68mm.step` (visual proxy; see below) |

## Verdict

**Needs change.**

- The candidate and baseline are generic KiCad IPC-style lands (onsemi lineage) and do not match TI's controlling RGT0016C drawing. Pin numbering, pin-1 location and the 0.5 mm positions are correct.
- Every land is longer (0.775 vs 0.60 mm) and extends 0.15 mm further out (row centre 1.4625 vs 1.400). Land width is 0.25 vs 0.24.
- The thermal land is 1.75 vs 1.68 mm, which narrows the land-to-EP gap from 0.26 to 0.20 mm.
- The EP paste is a 4-window 66% pattern rather than TI's single 1.55 mm (85%) aperture.

None of these is a pin-map error. Most packages would probably still solder, but that is untested. What is certain is that the land is not the TI-controlled geometry, and the project rule is to use the exact manufacturer drawing.

**Required change:** replace U7's footprint with the new `SC:TI_RGT0016C_VQFN-16_3x3mm_EP1.68x1.68_TPS62130A`. That file was written directly from the extracted RGT0016C values above.

- Pad numbers 1-17 are unchanged, so the nets carry over when the footprint is swapped.
- Pad 17 keeps the heatsink property and solid zone connection.
- The EP paste is one unnumbered paste-only 1.55 x 1.55 R0.05 pad.

The swap on the board is left to the board owner (this audit did not edit `StratosCore_Claude.kicad_pcb`). After the swap, re-run DRC around U7: the tighter land and the wider land-to-EP gap change copper clearances, and any existing EP vias must still lie inside the 1.68 mm land.

The baseline file in `hardware/footprints/` has the same defect. It was not changed here, so its replacement is a separate integrator decision.

## Validation of the new file

- KiCad 10 `pcbnew.FootprintLoad(...)` loaded the new footprint with 18 pads: 16 signal pads, pad 17, and 1 paste-only pad.
- The pads load at the tabulated centres and sizes.
- The corner radius reads back as 0.050 mm on the signal lands, pad 17 and the EP paste pad.

## Open items (TBD, not closed by this note)

- **3D model:** `VQFN-16-1EP_3x3mm_P0.5mm_EP1.68x1.68mm.step` does **not** exist in `C:/Program Files/KiCad/10.0/share/kicad/3dmodels/Package_DFN_QFN.3dshapes/`, although the stock KiCad `.kicad_mod` of that name references it. The new file therefore references `WQFN-16-1EP_3x3mm_P0.5mm_EP1.68x1.68mm.step` as a visual proxy only. Its body height has not been checked against TI's 0.8-1.0 mm: TBD.
- **Solder mask expansion and stencil thickness/aperture:** the assembler must approve these before release. TI's example assumes a 0.125 mm stencil.
- **Thermal vias under the EP:** optional per TI note 5, and TI recommends filling/plugging/tenting vias under paste. The board-level via count, drill, plating and tenting remain a PCB decision, and the thermal result is TBD until measured.
- **Shared tracking docs:** `candidates/claude-oneshot-revA/docs/ISSUES.md` item D6 and `docs/FOOTPRINT_REVIEWS_DIGITAL.md` (DIG-04 table) still describe the RGT0016A footprint. This note does not edit them; the integrator should update them together with the board swap.
