# Open questions and closure evidence

This file lists unresolved work only. [Project status](PROJECT_STATUS.md) sets priority; [decisions](DECISIONS.md) records accepted and rejected choices. An accepted direction remains open here when exact engineering or test evidence is still required.

| ID | Status | Type / owner | Question or required closure evidence |
| --- | --- | --- | --- |
| O01 | IN PROGRESS + SAMPLE GATE | Display / Sol + procurement | Independently transcribe the exact C1 revision-J FPC geometry; select mating connectors, 1.8 V translation and backlight driver; obtain two labeled samples and verify connector, address, power, touch and readability |
| O03 | IN PROGRESS | GNSS / Sol + RF | Close MAX-M10S-00B exact CAD, supply/backup, UART/timepulse, antenna bias/type/connector, placement and airborne configuration |
| O04 | PROTOTYPE GATE | ADS-B / RF | Simulate and then measure the BLB01/TA2003A/ADL5513/MCP6566 candidate for sensitivity, blockers, gain, pulse timing and coexistence |
| O05 | OWNER ACCEPTED; REVIEW BLOCKED | Power / qualified reviewer | Review the complete two-removable-cell 2S charger, common protection, holder and fault limits before schematic commitment or energizing |
| O06 | IN PROGRESS | Power / Sol | Review Molicel M50A cell candidate; select exact holder and USB-C receptacle/input protection; close the TUSB320LAI and preferred BQ25887 applications, common protection, buck rails, thermistors/fuses/FETs and state estimation; no batteryless operation or USB PD is currently proposed |
| O07 | OPEN | Audio/mechanical / Sol | Select microphone MPN and I2S/PDM interface; close supply, clock, footprint, acoustic port and optional DNP behavior |
| O08 | PROTOTYPE GATE | Mechanical | Verify the 84 x 60 mm PCB and approximately 88 x 64 x 37 mm enclosure with exact component drawings and a printed fit dummy |
| O09 | OPEN | RF/mechanical / Sol | Select exact RF connector MPNs and GNSS/ADS-B styles from cable loss, access, mating-cycle and assembly requirements; LoRa remains U.FL |
| O10 | BLOCKED EXTERNALLY | PCB/manufacturer | Confirm the current four-layer production stack and field-solved 50-ohm RF/90-ohm USB geometries with the chosen factory |
| O11 | IN PROGRESS | Hardware / Sol | Validate boot levels, voltage domains, I2C addresses/pullups, shared-SPI latency, interrupts, unpowered backfeed and complete GPIO/net allocation |
| O12 | IN PROGRESS | RP2040 interface / Sol | Define the UART framing/time synchronization, implement PIO/DMA capture and pass overflow/timestamp/concurrency tests |
| O13 | PROTOTYPE GATE | Power/product | Reduce at least 0.207 W from the current raw FLIGHT allowance or revise the 12-hour target; verify with a full measured profile |
| O14 | DEFERRED | Firmware/license | Select firmware framework and define MeshCore mode/port/dependencies after the hardware baseline; complete transitive license audit |
| O15 | CONTINUOUS | Maintainer/license reviewer | Record any reused circuit/code at file level; resolve ADSBee GPL and avBadge uncertainty before reuse |
| O16 | OWNER INPUT + TEST | Product/test | Define mission temperature, pressure, dynamics, weather resistance and mass; validate sensors/cells/enclosure across that envelope |
| O17 | DEFERRED | Product/firmware | Set acquisition rates, SD capacity, audio format and allowed data loss after hardware interfaces and power profiles are stable |
| O18 | OWNER INPUT + RF TEST | ADS-B/product | Define sensitivity, range, contact/stale-time targets and a repeatable conducted/field test plan |
| O19 | IN PROGRESS | Sensors/procurement | Create and independently review the ICM-42688-P land/mask/stencil footprint; recheck authorized stock and lead time |

## Recently closed owner decisions

| ID | Closed | Outcome |
| --- | --- | --- |
| O02 / P07 | 2026-09-13 | Owner replaced ATGM332D-5NR32 with MAX-M10S-00B for the balloon altitude envelope |
| P08 / P14 | 2026-09-13 | Owner rejected independent 1S bays and accepted two removable matched 21700 cells in 2S with one balanced charger and common protection direction |

P14 is closed as a product direction but O05/O06 remain open engineering and review gates. The qualified electrical/battery review is mandatory before the exact topology is frozen, entered as a committed schematic or energized.
