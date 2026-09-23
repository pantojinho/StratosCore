# Candidate refinement record — 2026-09-23

Scope: evidence-backed correction of the Claude one-shot comparison candidate only (`candidates/claude-oneshot-revA/`), following `docs/ASTRA_CANDIDATE_REFINEMENT_PROMPT.md`. Nothing here modifies `hardware/`, changes a LOCKED decision, closes a gate in `docs/PROJECT_STATUS.md`, or approves manufacture/energizing. **The candidate is still not a baseline and still must not be energized with cells (O05).**

## Preflight

| Item | Result |
| --- | --- |
| Commit reviewed | `origin/main` = `e1f75a3b2f02fe6f4a534bb87b36f5b7327184e8` (fetched 2026-09-23; supersedes the `9e909f3` review packet) |
| Tools | KiCad 10.0.6 (`kicad-cli`, bundled Python `pcbnew`), PyMuPDF 1.28.2 (datasheet rendering and vector extraction), `pdftotext` |
| Project/libraries | `kicad/StratosCore_Claude.kicad_pro`; `sym-lib-table`/`fp-lib-table` resolve `SC` to `${KIPRJMOD}/libs/`, standard libraries to `${KICAD10_*}` |
| Board | 60.0 x 84.0 mm, rounded corners, two 0.8 x 3.5 mm SHT40 thermal slots; 4 copper layers F.Cu/In1.Cu/In2.Cu/B.Cu, 1.6 mm; rules: clearance 0.127 (RF50 class 0.2), copper-edge 0.25, hole-to-hole 0.25, min silk text 0.8 mm |
| Inspection method | Every sheet exported by `kicad-cli sch export pdf` and read as rendered KiCad output; board geometry, nets and pads read through the KiCad 10 `pcbnew` API and zoomed `kicad-cli pcb export svg` layers; 3D via `kicad-cli pcb render`. The interactive KiCad GUI was not driven by the agent; a human should still open the files in KiCad before any acceptance. |

Commands (run from `kicad/`):

```text
kicad-cli sch erc --format json --severity-all -o <dir>/erc.json StratosCore_Claude.kicad_sch
kicad-cli pcb drc --format json --severity-all --schematic-parity --all-track-errors -o <dir>/drc.json StratosCore_Claude.kicad_pcb
kicad-cli sch export netlist --format kicadxml -o <dir>/netlist.xml StratosCore_Claude.kicad_sch
python ../tools/reconcile.py <dir>/netlist.xml StratosCore_Claude.kicad_pcb > <dir>/reconcile.txt
python ../tools/check_net_islands.py StratosCore_Claude.kicad_pcb GND
```

Reports: [`kicad/reports/before_2026-09-23/`](../kicad/reports/before_2026-09-23/) and [`kicad/reports/after_2026-09-23/`](../kicad/reports/after_2026-09-23/) (the top-level `kicad/reports/{erc,drc}.json` and `netlist.xml` now equal the after set).

## Before / after

KiCad reports at most **199 items per violation type**; a count of exactly 199 is a lower bound (proved by `text_height`: 274 references were 0.6 mm, 199 reported).

| Check | Before (`e1f75a3`) | After | Meaning of the change |
| --- | --- | --- | --- |
| ERC | 1 error, 4 warnings | 1 error, 5 warnings | New warning is the intended ICM pin 9 GND strap (same class as the existing AD0/SDO straps). The error is the intended BMP581 INT GND strap (below). |
| DRC errors | 1 `courtyards_overlap` (U1/J5) | 199+ `solder_mask_bridge` (U30, U32 only) | Courtyard defect corrected. The mask-bridge findings were previously **hidden** by a footprint-level `allow_soldermask_bridges` flag on U30/U32 that did not exist in the library; they are now visible (see dispositions). |
| DRC warnings | 579 (2 hole_to_hole, 2 lib_footprint_mismatch, 3 track_dangling, 11 silk_edge, 199+ silk_over_copper, 163 silk_overlap, 199+ text_height) | 119 (6 silk_edge, 76 silk_over_copper, 36 silk_overlap, 1 track_dangling) | Real hole/library/dangling defects removed; silk refined (below). |
| Unconnected items | 11 | 5 | 6 fixed; 3 GND islands need local re-layout; 2 SX1262 RF items are the intended RF blocker. |
| Schematic parity | 0 | 0 | Correspondence only. |
| Net/pad reconciliation (`tools/reconcile.py`) | 970 pins, 0 mismatches | 970 pins, 0 mismatches | Correspondence only, not electrical validation. |

A lower count is not a pass: the after board still has visible errors, open RF/ground connections and every gate listed at the end.

## Verified corrections (changed copper, nets or libraries)

| # | Item | Primary-source evidence | Change |
| --- | --- | --- | --- |
| R1 | **DRC error U1/J5.** The README called it an antenna-keepout overlap; the actual overlap was 0.09 mm between the GNSS U.FL J5 courtyard (x 26.41) and the ESP32 module-**body** courtyard edge (x 26.50) at the pin end. The antenna rule area (x <= 6.3 mm, 48 x 21 mm, no tracks/vias/fills/footprints) contains no copper and was not touched. | KiCad `RF_Module:ESP32-S3-WROOM-1` courtyard/rule area; Espressif placement guidance as already recorded in `hardware/datasheets/README.md` | J5 moved +0.4 mm (29.0 -> 29.4); GNSS_RF J5->D2 feed replaced by one straight 0.15 mm segment (removes a four-segment detour). Still not a controlled-impedance GCPW path. |
| R2 | **ICM-42688-P pin 9 (INT2/FSYNC/CLKIN) was a no-connect.** | TDK DS-000347 v1.9 Table 10 p.20: "FSYNC … Connect to GND if FSYNC not used"; §14.3 INT_CONFIG reset 0x00 (INT2 open-drain, active low); INTF_CONFIG5 reset PIN9_FUNCTION = INT2. Project `docs/SENSOR_ARCHITECTURE.md` already requires it grounded. | Schematic `06_sensors`: no-connect replaced by a `GND` label and the sheet note updated; board pad 9 -> GND with a 0.2 mm link to pads 10/11 and one via. Firmware must keep INT2 open-drain/unrouted. |
| R3 | **TXU0202 U24 used the generic KiCad DCU land** (1.25 x 0.35 mm at X +/-1.4). | TI SCES942A PDF pp.32-34, DCU0008A 4225266/A: 8 x 0.85 x 0.30 mm lands, 3.1 mm row-centre spacing (X +/-1.55), 0.5 mm pitch, R0.05, NSMD 0.05 mm max, stencil 1:1 (0.125 mm). Pins 1 B2, 2 GND, 3 VCCA, 4 A2Y, 5 A1, 6 OE, 7 VCCB, 8 B1Y match the board nets. | New `SC:TI_DCU0008A_VSSOP-8_2.3x2mm_P0.5mm_TXU0202` = exact copy of the corrected `hardware/footprints` file plus a 3D reference; board footprint swapped (nets preserved), schematic and `SC.kicad_sym` footprint fields updated. |
| R4 | **TPS259474L U3 RPW paste and fab.** Copper was audited against TI's vector drawing and **matches exactly** (not changed): corner lands = 0.6 x 0.3 (X 0.6-1.2, Y 0.55-0.85) plus 0.25 x 0.65 (X 0.6-0.85, Y 0.55-1.2); side lands 0.6 x 0.25 at X +/-0.9, Y +/-0.225; centre lands 0.3 x 2.4 at X +/-0.25; pin order 1-4 left top-down, 5 IN, 6 OUT, 7-10 right bottom-up (TI top view). Defects: paste was 1:1 on every land, and the fab body was 2.7 mm. | TI SLVSFC9C PDF pp.72-74, RPW0010A 4225183/A 08/2019; coordinates extracted from the PDF vector paths (2.4 mm = 204.1 pt). p.74 stencil (0.100 mm): corner pads 93 %, pads 5/6 82 % as two 0.28 x 1.06 apertures at Y +/-0.63, side pads 1:1. p.72 body 1.9-2.1 mm. The parenthesised reference dimension (1.75) on p.73 is not reproduced by the vector geometry (which gives 1.70 outer span for the horizontal legs); every other dimension is. | Library and board updated: copper/mask unchanged, TI paste apertures as separate paste-only pads, fab body 2.0 x 2.0 with pin-1 chamfer, R0.05 corner ratios. Not the rejected straight-pad draft and not RPU. |
| R5 | Hidden mask-bridge suppression on U30/U32 (`lib_footprint_mismatch` x2). | Library/baseline files have no such flag; the baseline correction record keeps BMP581 mask findings visible for assembler review. | Flag removed, board equals library. Findings now visible (see D1). |
| R6 | Two hole-to-hole violations (SCL vias 0.24 mm apart; LED_A 0.45 mm via overlapping a 0.6 mm via). | Board rule 0.25 mm. | Duplicate vias and their stubs removed; SCL B.Cu and LED_A F.Cu re-anchored to the remaining vias. |
| R7 | I2C_SCL In2 route crossed under the BMP581 body. | Bosch BST-BMP581-DS004-13 §8.2 p.69: no vias or traces under the BMP581. | Replaced by In2 (43.224,9.449)->(44.65,8.023)->existing SCL via (44.65,5.55); BMP581 SCL is reached through the existing B.Cu/F.Cu chain. |
| R8 | SHT40 SDA (U33 pad 1) unrouted. | Sensirion SHT4x v7.3 Figure 18: pin 1 SDA (transparent top view); Figure 17 / keepout: no copper under the sensor except the lands. | 0.15 mm F.Cu route from pad 1 around the top of the left thermal slot (>= 0.25 mm edge clearance, outside the footprint keepout) to a new via on the existing In2 SDA trunk. |
| R9 | Two `3V3_MAIN` fragments at the vent edge and one dangling end. | Same net on both sides (schematic). | 0.25 mm link (45.85,4.85)->(46.426,4.85)->(47.026,4.25); dangling stub removed. |
| R10 | C57 (100 nF, `3V3_MAIN`, display sheet) pad 1 unconnected. It sat 23 mm from the touch connector J4 it is meant to decouple; **no courtyard-free location exists near J4** because the microSD J8 card envelope covers that area. | Schematic nets only. | Moved 3.97 mm onto the existing 3V3_MAIN feed at R104.2 (16.8, 43.1, 90 deg) so both pads connect. Proper placement at J4 remains a layout item. |
| R11 | Three of six isolated GND copper groups. | TI SLVSAG7F §11.1: TPS62130A AGND/PGND/exposed pad direct connection to the ground plane is mandatory. | U7 TPS62130A exposed pad: one 0.2 mm via at the only legal position (autorouted In2 BUCK_SW and B.Cu SD_CT run under the IC and block TI's via grid). U30 pads 9-11: via at (31.675,41.8). BMP581 SDO strap + C35 ground: tented via between the C35 lands. |
| R12 | Silkscreen: 274 references at 0.6 mm violated the board's own 0.8 mm minimum; many were over pads. | Board design rule. | 202 passive references moved to F.Fab/B.Fab (assembly drawing); 75 U/J/TP/SW/BT/H/Y/FID references kept on silk at 0.8 mm; 7 nudged clear. |

## Reviewed with no change

- **BMP581 INT (ERC error).** Bosch DS004-13 Table 28 note a and §6.2 p.46: GND is the recommended connection for an unused INT **provided `INT_CONFIG.int_en` stays disabled**; §7.5 reset value of `int_en` is 0. The strap is kept and the ERC error is left visible (not excluded). Firmware requirement: never set `INT_CONFIG.int_en`. SDO=GND gives 0x46; CSB=VDDIO selects I2C; no Figure 28 fast-ramp resistors because `3V3_MAIN` has a 3.3 nF soft start (confirm the actual ramp on the bench).
- **Sensor lands versus drawings and top views:** BMP581 embedded = corrected baseline (centres +/-0.7625 mm, 0.325 x 0.3 mm; numbering is a pure 90-degree rotation of the Figure 23 top view, not a mirror); MMC5983MA embedded = corrected baseline (+/-1.275 mm; pin 1 top-right per the p.20 top view); SHT40 (0.5 x 0.3 mm at +/-0.7, 0.8 mm pitch, pin order per Figure 18); ICM-42688-P embedded = baseline except the removed mask flag. All four pin maps match the board nets. Parser/parity agreement is not treated as electrical validation.
- **TPS62130A RGT land:** the current TI package page shows RGT0016C with a 1.68 mm exposed pad; the candidate footprint is RGT0016A with 1.75 mm. Not changed; add to the DIG-04 exact-MPN pass.

## Dispositions of remaining DRC/ERC findings

| Type | Count | References | Disposition |
| --- | --- | --- | --- |
| `solder_mask_bridge` (error) | 199+ (capped) | U30 ICM-42688-P, U32 BMP581 only | The footprints use a common no-mask opening (Bosch §8.2; TDK AN-000393 "where the process permits"). Of the 199 reported, 59 pair a land with the opening (intended); the rest are copper exposed inside the openings — 3V3_MAIN/I2C/IMU_INT1/GND tracks, GND/I2C_SCL/I2C_SDA vias (including the R11 ICM via) and GND pour — which is a real consequence of this strategy. **Open:** assembler mask decision (TDK fallback: per-pad 0.1 mm expansion) and escape routing that leaves the opening quickly. Not suppressed. |
| `silk_over_copper` / `silk_overlap` / `silk_edge_clearance` | 76 / 36 / 6 | kept references of dense ICs/TPs and passive body silk (list in `after_2026-09-23/drc.json`); edge: U1 module outline at the antenna edge, U33 slot-side silk | Cosmetic; clipped by the fab. Final reference placement belongs to the hand layout. |
| `track_dangling` | 1 | LORA_RFI_P stub | Part of the RF blocker; left untouched. |
| ERC `pin_to_pin` error | 1 | U32 pin 7 INT to GND | Intended per Bosch (above). |
| ERC `pin_to_pin` warnings | 4 | U30 pins 1 (AD0) and 9, U32 pin 5 (SDO), U14 pin 7 (spare translator input) to GND | Intended straps. |
| ERC `lib_symbol_mismatch` | 1 | Q2 2N7002 flattened copy | Pin order G1/S2/D3 still to be checked against the exact FET MPN (TBD). |

## Unconnected items left open (structured blockers)

| Item | Why it is not closed here | Required action |
| --- | --- | --- |
| GND U2 pads 3/8 (TPD4E05U06 USB ESD) | Boxed in by USB_DP/DN, CC1/CC2 routing and the CC2 via; exact-geometry search found no legal via/escape within 3 mm. **Without this ground the ESD array provides no protection.** | Hand re-layout of the USB-C/ESD corner (flow-through DQA routing, GND via at the package). |
| GND U3 pad 8 (TPS259474L) | An In2 VBUS 0.4 mm track runs diagonally under U3 and the ILM/ITIMER/PROT vias fill the surroundings. **The eFuse ground is floating.** | Re-route In2 VBUS away from U3 and add a GND via at pad 8. |
| GND U24 pad 2 (TXU0202) | B.Cu I2C_SDA runs under the only open pour area. | Local reroute plus via. |
| LORA_RFO (U40.23), LORA_RFI_P (U40.21) | Matching/filter/balun values and E449-derived layout are TBD. | ENGINEERING_RETURN (RF) — do not route as if complete. |

## Layout observations (not changed; recorded for the hand layout)

- **BQ25887 (U6):** BTST cap C12 17.2 mm and REGN cap C13 15.8 mm from the IC, SYS/BAT caps C14/C15 about 11 mm; TI requires these adjacent. Part of the O05-gated power block, so not touched.
- **TPS62130A (U7):** L2 5.9 mm from SW pins with BUCK_SW routed on In2 under the IC; FB/SS parts 5.6-7.9 mm; only one EP via. Input C20 2.0 mm and output C22 2.4 mm are reasonable.
- **TPS61169 (U16):** D1 2.3 mm, L3 4.1 mm, C55 2.5 mm; loop not optimised.
- **RF/USB:** GNSS, ADS-B and LoRa paths and the USB pair remain 0.15/0.16 mm autorouted tracks without solver-confirmed GCPW/90-ohm geometry.
- **3D:** re-rendered top/bottom/isometric views show J5 moved and no new collisions in the board model. Display, cell holder, cells and enclosure remain conceptual envelopes; the zipped assembly STEP and `outputs/positions_REVIEW_ONLY.csv` predate this refinement (J5 +0.4 mm, C57 moved) and were intentionally not regenerated (no CPL/production output).

## ENGINEERING_RETURN (unchanged gates)

- **Battery (O05):** removable 2S holder, protection placeholder/conflict, BQ25887 autonomous start/CD gating, charge-under-load termination, fault behaviour. Qualified electrical/battery review required before schematic commitment or energizing.
- **Display/mechanical:** controlled Orient power/FPC drawing and samples, XF3M fit, touch reset sharing, holder MPN/tabs, enclosure tolerance fit dummy, J3/J4 decoupling placement against the J8 card envelope.
- **RF/stackup:** SX1262 E449 values/layout and crystal, ADS-B threshold (OWN-09)/ADL5513 EP, antenna layouts, factory-solver 50/90-ohm geometry.
- **Digital:** GPIO gaps A5-A8, Q2 FET MPN, TPS62130A RGT0016A vs RGT0016C, BM12B orientation, TXU0202/RPW/sensor assembler mask and stencil approval.
- **Cost/factory:** BRL 200 five-unit target unverified; no quotes; no Gerbers/drill/CPL/orderable BOM generated.

## Changed files

- `kicad/06_sensors.kicad_sch` — R2.
- `kicad/10_storage_audio.kicad_sch`, `kicad/libs/SC.kicad_sym` — U24 footprint field (R3).
- `kicad/libs/SC.pretty/TI_DCU0008A_VSSOP-8_2.3x2mm_P0.5mm_TXU0202.kicad_mod` (new), `kicad/libs/SC.pretty/TI_RPW0010A_VQFN-HR-10_2x2mm_P0.45mm.kicad_mod` — R3, R4.
- `kicad/StratosCore_Claude.kicad_pcb` — R1-R12.
- `kicad/reports/` — before/after reports, reconciliation; top-level reports replaced by the after set.
- `docs/schematic.pdf`, `images/schematic_06_sensors.png`, `images/render_*.png`, `outputs/render_*.png`, `outputs/pcb_layers.pdf`, `outputs/bom_candidate.csv` (only the U24 footprint changed), `outputs/netlist.net`, `outputs/drc_summary.txt` — regenerated.
- `tools/refine_2026_09_23_board.py`, `tools/refine_2026_09_23_silk.py`, `tools/refine_2026_09_23_refplace.py`, `tools/fp_rpw_dcu_2026_09_23.py`, `tools/reconcile.py`, `tools/check_net_islands.py` — reproducible scripts (MIT tooling). The original `design.py`/`build_*.py` generators predate this record; re-running them would revert R1-R12, so the KiCad files are now the source of truth.
