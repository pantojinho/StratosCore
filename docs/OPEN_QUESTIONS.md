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
| O11 | IN PROGRESS - MATRIX CREATED | Hardware / Sol + CAD + test | Close every OPEN row in `ELECTRICAL_COMPATIBILITY_MATRIX.md`: peak loads, pullups/capacitance, boot levels, reset defaults, interrupts, unpowered backfeed, hot-plug and shared-bus concurrency; then independently review the complete net matrix |
| O12 | IN PROGRESS | RP2040 interface / Sol | Define the UART framing/time synchronization, implement PIO/DMA capture and pass overflow/timestamp/concurrency tests |
| O13 | PROTOTYPE GATE | Power/product | Reduce at least 0.207 W from the current raw FLIGHT allowance or revise the 12-hour target; verify with a full measured profile |
| O14 | DEFERRED | Firmware/license | Select firmware framework and define MeshCore mode/port/dependencies after the hardware baseline; complete transitive license audit |
| O15 | CONTINUOUS | Maintainer/license reviewer | Record any reused circuit/code at file level; resolve ADSBee GPL and avBadge uncertainty before reuse |
| O16 | OWNER INPUT + TEST | Product/test | Define mission temperature, pressure, dynamics, weather resistance and mass; validate sensors/cells/enclosure across that envelope |
| O17 | DEFERRED | Product/firmware | Set acquisition rates, SD capacity, audio format and allowed data loss after hardware interfaces and power profiles are stable |
| O18 | OWNER INPUT + RF TEST | ADS-B/product | Define sensitivity, range, contact/stale-time targets and a repeatable conducted/field test plan |
| O19 | IN PROGRESS | Sensors/procurement | Create and independently review the ICM-42688-P land/mask/stencil footprint; recheck authorized stock and lead time |
| O20 | IN PROGRESS | Digital CAD/procurement | Independently compare W25Q128JVSIQ, ABM8-272-T3 and DM3AT-SF-PEJM5 footprints with current drawings; validate RP2040 boot/clock and microSD mechanical/power-fail behavior |

## Recently closed owner decisions

| ID | Closed | Outcome |
| --- | --- | --- |
| O02 / P07 | 2026-09-13 | Owner replaced ATGM332D-5NR32 with MAX-M10S-00B for the balloon altitude envelope |
| P08 / P14 | 2026-09-13 | Owner rejected independent 1S bays and accepted two removable matched 21700 cells in 2S with one balanced charger and common protection direction |

P14 is closed as a product direction but O05/O06 remain open engineering and review gates. The qualified electrical/battery review is mandatory before the exact topology is frozen, entered as a committed schematic or energized.
