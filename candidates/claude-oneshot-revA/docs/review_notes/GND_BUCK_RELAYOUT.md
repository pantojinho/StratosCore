# GND island closure and TPS62130A exposed-pad vias — U2 / U3 / U24 / U7

Review date: 2026-09-23. Scope: `candidates/claude-oneshot-revA/kicad/StratosCore_Claude.kicad_pcb` only (out-of-baseline comparison candidate). Nothing in `hardware/` or root `docs/` was changed, no locked decision was touched, and no gate was closed. The candidate still must not be energized with cells (O05).

Script: [`tools/relayout_gnd_buck.py`](../../tools/relayout_gnd_buck.py). It applies to the board at `bccd4b3` (identical to `6fa29cb`), asserts every pre-edit segment/via by exact coordinates, removes items only after the edit list is built, refills zones and saves. It is not idempotent. Reports: [`kicad/reports/relayout_gnd_buck_2026-09-23/`](../../kicad/reports/relayout_gnd_buck_2026-09-23/).

Tools: KiCad 10.0.6 `kicad-cli` and bundled Python `pcbnew`. The KiCad GUI was not used. A human should still open the board before accepting anything.

## Result

| Check | Before | After |
| --- | --- | --- |
| DRC errors | 199 `solder_mask_bridge` (capped; U30/U32 only) | 199 `solder_mask_bridge` (capped; U30/U32 only) |
| DRC warnings | 6 silk_edge_clearance, 76 silk_over_copper, 36 silk_overlap, 1 track_dangling (LORA_RFI_P) | identical items (set-compared) |
| Unconnected items | 5 (3 GND islands + LORA_RFO + LORA_RFI_P) | **2** (LORA_RFO, LORA_RFI_P: the intended RF blocker) |
| Schematic parity | 0 | 0 |
| `reconcile.py` | 970 pins, 0 mismatches | 970 pins, 0 mismatches |
| `check_net_islands.py GND` | 4 groups (U2 3/8, U3 8, U24 2 isolated) | **1 group** |

Notes:

- **Mask-bridge cap.** Both runs hit KiCad's 199-per-type cap, so the reported mask-bridge subset shifted (28 items only in the before list, 4 only in the after list, all U30/U32 openings). To show that no new mask bridge appeared, both boards were copied to a scratch folder with `allow_soldermask_bridges` set on U30/U32 only. Both copies then gave **0** `solder_mask_bridge` findings, with the other counts identical and 5 → 2 unconnected. The flag was never set on the real board. Every other violation item is identical by type, description and position.
- The DRC command was `kicad-cli pcb drc --format json --severity-all --schematic-parity --all-track-errors`. The netlist came from `kicad-cli sch export netlist --format kicadxml`.
- After reloading the saved board, all 9 new vias still have their intended nets (8 GND, 1 EFUSE_ILM). No via was silently reassigned.

## Changes (coordinates in mm, board origin)

### 1. U2 TPD4E05U06 (USB ESD) — GND pads 3/8

The F.Cu USB_DP run at x 8.296 passed 0.29 mm from pad 8. The J4.MP stitching via at (8.85, 70.65) blocked moving it. An In2 3V3_MAIN link at x 8.35 and B.Cu VBUS at y 71.968 limited where a via could go.

| Action | Item |
| --- | --- |
| delete | via GND (8.850, 70.650); F.Cu GND (10.050,70.650)->(8.850,70.650) w0.25 |
| add | via GND (10.400, 69.350) 0.45/0.20 + F.Cu GND (10.400,69.350)->(10.400,69.900) w0.25 (J4.MP stitching via relocated above the hold-down) |
| delete | F.Cu USB_DP (8.042,70.033)->(8.296,70.287) and (8.296,70.287)->(8.296,73.927) w0.16 |
| add | F.Cu USB_DP (8.042,70.033)->(8.840,70.831)->(8.840,73.383)->(8.296,73.927) w0.16. Same endpoints, no stub. |
| delete | In2 3V3_MAIN (8.75,70.05)->(8.35,70.45)->(8.35,72.45)->(7.75,73.05) w0.127 |
| add | In2 3V3_MAIN (8.750,70.050)->(8.840,70.140)->(8.840,72.360)->(8.150,73.050)->(7.750,73.050) w0.127. Same vias. |
| add | **via GND (8.380, 71.400) 0.45/0.20** + F.Cu GND (7.735,71.450)->(8.380,71.400) w0.25. Pads 3 and 8 were already joined under the package. |

USB length: DP 75.273 → 75.724 mm (+0.451), DN unchanged at 79.397 mm, so DP−DN skew goes from −4.12 to −3.67 mm. The pair was not coupled near U2 before this change, and it is not coupled now: DN still loops on In2 under U2. This is not a 90-ohm differential implementation (see "Not fixed").

### 2. U3 TPS259474L (eFuse) — GND pad 8

| Action | Item |
| --- | --- |
| delete | via EFUSE_ILM (23.213, 75.570); F.Cu EFUSE_ILM (23.108,75.675)->(23.213,75.570); In2 EFUSE_ILM (25.220,73.563)->(23.213,75.570) |
| add | via EFUSE_ILM (23.750, 75.033) 0.45/0.20; F.Cu (23.108,75.675)->(23.750,75.033) w0.15; In2 (25.220,73.563)->(23.750,75.033) w0.15. The via moved 0.76 mm along its own route. |
| delete | In2 VBUS (20.978,74.117)->(23.404,76.544)->(23.562,76.544) w0.40 |
| add | In2 VBUS (20.978,74.117)->(22.300,75.439)->(23.200,75.439)->(23.562,75.801)->(23.562,76.544) w0.40. Same width, same VBUS via (23.562, 76.544). VBUS +0.435 mm. |
| add | **via GND (22.980, 76.125) 0.45/0.20** + F.Cu GND (22.450,76.125)->(22.980,76.125) w0.25 |

No battery/protection net was touched (PROT_*, BAT_N, Q1, U5 unchanged).

### 3. U24 TXU0202 — GND pad 2

| Action | Item |
| --- | --- |
| delete | B.Cu I2C_SDA (6.336,41.387)->(5.556,42.167)->(5.556,42.937)->(4.278,44.214) w0.15 |
| add | B.Cu I2C_SDA (6.336,41.387)->(5.100,42.623)->(5.100,43.392)->(4.278,44.214) w0.15. Same endpoints, same length (194.095 mm). |
| add | **via GND (5.600, 43.200) 0.45/0.20** + F.Cu GND (6.500,43.200)->(5.600,43.200) w0.25 |

The U31 MMC5983MA footprint was not touched. As before, the SDA jog passes under the corner of its body on B.Cu.

### 4. U7 TPS62130A — exposed-pad via grid

| Action | Item |
| --- | --- |
| delete | via GND (22.350, 48.000). It was 0.116 mm hole-to-hole from the (22.29, 48.31) grid position (rule 0.25), so it could not be kept. |
| add | **4 x via GND 0.45/0.20 at (21.71, 48.31), (22.29, 48.31), (21.71, 48.89), (22.29, 48.89)** = EP centre (22.0, 48.6) ±0.29 mm, 0.58 mm pitch |
| delete | In2 BUCK_SW (20.538,47.046)->(23.042,49.550)->(25.615,49.550) w0.40 |
| add | In2 BUCK_SW (20.538,47.046)->(20.538,48.550)->(21.538,49.550)->(25.615,49.550) w0.40. Same end vias. **SW node +0.88 mm (13.650 → 14.530 mm).** |
| delete | B.Cu SD_CT (21.921,42.864)->(21.921,52.999) w0.15 |
| add | B.Cu SD_CT (21.921,42.864)->(21.921,47.300)->(22.730,48.109)->(22.730,49.100)->(21.921,49.909)->(21.921,52.999) w0.15 (+0.67 mm) |
| delete | B.Cu SPI_SCLK (22.865,42.296)->(22.865,53.722) w0.15 |
| add | B.Cu SPI_SCLK (22.865,42.296)->(22.865,47.400)->(23.020,47.555)->(23.020,49.700)->(22.865,49.855)->(22.865,53.722) w0.15 (+0.13 mm) |

Fit with the planned RGT0016C swap (`SC:TI_RGT0016C_VQFN-16_3x3mm_EP1.68x1.68_TPS62130A`):

- The via rings reach 0.29 + 0.225 = 0.515 mm from the EP centre, inside the 0.84 mm half-width of the 1.68 mm land.
- No track was added to a U7 signal pad. Existing U7 track ends sit at the current pad centres, 1.4625 mm from the IC centre, which is inside the RGT0016C land span of 1.10–1.70 mm.
- Re-run DRC after the swap, because the land-to-EP gap changes.

## Not fixed / open (with reasons)

1. **EP via pattern needs a check against TI's land example.** The ±0.29 mm 4-via grid follows the task instruction. The sibling audit [`TPS62130A_RGT_FOOTPRINT.md`](TPS62130A_RGT_FOOTPRINT.md), extracted from SLVSAG7F p.41 (4222419/E), records TI's optional vias as **5 x d0.20 at (0,0) and (±0.58, ±0.58)**. That pattern was not built here: B.Cu BUCK_PG at x 21.21, the new SD_CT jog and SPI_SCLK would all need more rerouting. A 0.45 mm ring at ±0.58 would also sit only 0.035 mm inside the 1.68 mm land. Choose the pattern before the RGT0016C swap. The via-in-pad fill/plug/tent treatment is an assembler decision, and the thermal result is TBD until measured.
2. **BUCK_SW is not on F.Cu and is longer.** The SW pins (1–3) are on the left side of U7, and L2 is 4–6 mm away at the lower right beyond the PG/FB/SS/PVIN pins. No legal F.Cu path exists without moving parts. The SW node still transitions through two 0.6/0.3 vias and runs 0.4 mm wide on In2, now 0.88 mm longer, because clearing the EP forces a detour. The correct fix is placement: put L2 (and the C23/TP8 group it displaces) next to pins 1–3 as in TI's layout example. That is a hand-layout item and was not attempted.
3. **SD_CT placement.** C120, the CT capacitor for U10, sits about 10 mm from U10 pin 4. That was not changed.
4. **USB pair.** DP/DN are still 0.16 mm autorouted tracks with no solver-confirmed 90-ohm geometry. DN loops on In2 under U2. TI's flow-through DQA routing (lines passing across pads 1/10 and 2/9) was not implemented, because pads 6/7/9/10 are schematic no-connects and changing their nets would alter the schematic.
5. **Untouched by instruction:** LORA_* (2 unconnected + 1 dangling remain, RF blocker), the BQ25887/U6 area and battery nets (O05), sensor footprints, the ESP32 antenna keepout, and U1/J1/SW1/SW2 positions.
6. The recorded clearances were checked by `kicad-cli` DRC only. There is no field-solver, current-density or thermal analysis of the moved VBUS/BUCK_SW copper.
