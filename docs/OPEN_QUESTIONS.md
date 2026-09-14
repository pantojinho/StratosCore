# Open questions and closure evidence

This file lists unresolved work only. [Project status](PROJECT_STATUS.md) sets priority; [decisions](DECISIONS.md) records accepted and rejected choices. An accepted direction remains open here when exact engineering or test evidence is still required.

| ID | Status | Type / owner | Question or required closure evidence |
| --- | --- | --- | --- |
| O01 | PROPOSAL READY + SAMPLE GATE | Display / owner + procurement + CAD | Review P21; obtain a controlled Orient drawing resolving its internal revision/terminal ambiguities; verify XF3M fit on two labeled samples; confirm write-only SPI mode; independently review CAD and prototype TPS61169 current, brightness, faults, EMI, touch and shared-bus behavior |
| O03 | PREFERRED APPLICATION | GNSS / RF + CAD | Review P20 against the final PDN and enclosure: always-on tied 3.3 V VCC/V_IO; open V_BCKP/RESET_N/EXTINT; passive `FXP611.07.0092C` through `U.FL-R-SMT-1(60)` and `TPD1E0B04DPYR`, with no RF bias. Then calculate/VNA-check the path, independently review footprints, and pass cold-start/PPS/AIR4/coexistence tests |
| O04 | PROTOTYPE GATE | ADS-B / RF | Simulate and then measure the BLB01/TA2003A/ADL5513/MCP6566 candidate for sensitivity, blockers, gain, pulse timing and coexistence |
| O05 | OWNER ACCEPTED; REVIEW BLOCKED | Power / qualified reviewer | Review the complete two-removable-cell 2S charger, common protection, holder and fault limits before schematic commitment or energizing |
| O06 | IN PROGRESS | Power / Sol + qualified reviewer | Review M50A and P22/P24; select exact holder and VBUS protection, close TUSB320LAI/BQ25887/common protection/NTC/fuse/FET/state estimation, calculate all rail loads and prove sequencing/back-power; no batteryless operation or USB PD is proposed |
| O07 | PROPOSAL READY | Audio/mechanical / CAD + test | Review P23; independently compare T5838/TXU0202 footprints, close 1.8 V/OE sequence and acoustic port, then verify PDM timing, noise, clipping, timestamping, RF interference and optional DNP behavior |
| O08 | PROTOTYPE GATE | Mechanical | Verify the 84 x 60 mm PCB and approximately 88 x 64 x 37 mm enclosure with exact component drawings and a printed fit dummy |
| O09 | PREFERRED INTERCONNECT | RF/mechanical / RF + CAD | Review P20/P25; independently compare U.FL/CAB.721 drawings, fit all cables/antenna in the enclosure dummy, calculate/VNA-check each 50-ohm path and verify port labeling, tool access, strain relief and coexistence |
| O10 | BLOCKED EXTERNALLY | PCB/manufacturer | Confirm the current four-layer production stack and field-solved 50-ohm RF/90-ohm USB geometries with the chosen factory |
| O11 | IN PROGRESS - EVIDENCE UPDATED 2026-09-14 | Hardware / Sol + CAD + test | Close every OPEN row in `ELECTRICAL_COMPATIBILITY_MATRIX.md`. Matrix rows now carry exact candidate figures: 3V3_MAIN simultaneous peak about 974 mA, TPS7A20 dropout 140 mV maximum, 1V8_LOGIC static load about 400 uA, TUSB320LAI back-power disposition (VDD from 3V3_MAIN, VBUS_DET 900 kohm to VBUS), TPS22918 off-state 9.2/16 uA. Remaining: BQ25887 I2C threshold confirmation for a 3.3 V pull-up rail, GNSS domain switch decision, independent review of the complete net matrix |
| O12 | HOST CONTRACT CLOSED; SILICON GATED | RP2040 interface / Sol | Host-side UART framing contract proven 2026-09-14 by 17 passing tests (`firmware/rp2040_adsb/tests/test_framing.py`): length-delimited records with CRC16-CCITT, rolling sequence, 64-bit timestamp reconstruction across the 32-bit sample-clock wrap, overflow visibility through dedicated OVERFLOW records plus sequence-gap detection, resync after garbage/CRC failure, interleaved-producer and 200-contact stress. Remaining: implement the same contract as RP2040 PIO/DMA firmware and pass the bench overflow/timestamp/concurrency tests against real capture hardware |
| O13 | ARITHMETIC CLOSED; MEASUREMENT GATE REMAINS | Power/product | Power budget re-derived 2026-09-14 from exact component datasheets (ESP32-S3 v2.2 Table 5-9, MAX-M10S Table 15, BLB01/ADL5513/MCP6566/RP2040 Table 637): FLIGHT allowance 1.935 -> 1.684 W, removing 0.251 W against the 0.207 W requirement. Two-cell runtime estimate 12.31 h exceeds 12 h and the raw budget fits with 0.044 W headroom, but this closure inherits unmeasured usable-energy/efficiency assumptions; the full measured 12 h discharge profile is still the PR13 evidence |
| O14 | DEFERRED | Firmware/license | Select firmware framework and define MeshCore mode/port/dependencies after the hardware baseline; complete transitive license audit |
| O15 | CONTINUOUS | Maintainer/license reviewer | Record any reused circuit/code at file level; resolve ADSBee GPL and avBadge uncertainty before reuse |
| O16 | OWNER INPUT + TEST | Product/test | Define mission temperature, pressure, dynamics, weather resistance and mass; validate sensors/cells/enclosure across that envelope |
| O17 | DEFERRED | Product/firmware | Set acquisition rates, SD capacity, audio format and allowed data loss after hardware interfaces and power profiles are stable |
| O18 | OWNER INPUT + RF TEST | ADS-B/product | Define sensitivity, range, contact/stale-time targets and a repeatable conducted/field test plan |
| O19 | IN PROGRESS - EVIDENCE RECORDED | Sensors/procurement | Create and independently review the ICM-42688-P land/mask/stencil footprint: DS-000347 v1.9 package facts and AN-000393 (index lists v2.1) rules recorded in `FOOTPRINT_REVIEWS_SENSORS_GNSS.md`; both source documents were bot-walled to automated retrieval on 2026-09-14, so the spatial transcription needs a human download pass; recheck LCSC C1850418 stock before ordering |
| O20 | IN PROGRESS - PARTIAL CLOSURE | Digital CAD/procurement | W25Q128JVSIQ (SOIC-8 5.3x5.3), ABM8-272-T3 (3225-4Pin) and DM3AT-SF-PEJM5 project footprints vendored from official KiCad libraries with provenance in `FOOTPRINT_REVIEWS_DIGITAL.md`; ABM8 drawing #456603 pad transcription and the DM3 drawing comparison remain PENDING. MAX-M10S Table 44/45 land/paste dimensions extracted; figure transcription pending. DPY0002A ESD footprint built from TI layout values |

## Recently closed owner decisions

| ID | Closed | Outcome |
| --- | --- | --- |
| O02 / P07 | 2026-09-13 | Owner replaced ATGM332D-5NR32 with MAX-M10S-00B for the balloon altitude envelope |
| P08 / P14 | 2026-09-13 | Owner rejected independent 1S bays and accepted two removable matched 21700 cells in 2S with one balanced charger and common protection direction |

P14 is closed as a product direction but O05/O06 remain open engineering and review gates. The qualified electrical/battery review is mandatory before the exact topology is frozen, entered as a committed schematic or energized.
