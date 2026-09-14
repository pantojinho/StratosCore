# Project status

Last updated: 2026-09-14. Current phase: **pre-KiCad hardware engineering closure**.

The immediate objective is to finish exact component selection, electrical compatibility, application circuits, interfaces, footprints, mechanical constraints and review evidence with Sol-class work. Astra is reserved for final KiCad schematic capture, PCB placement/routing and ERC/DRC after this document declares the handoff ready.

## Completed and verified

| Area | Current result | Evidence boundary |
| --- | --- | --- |
| Repository foundation | Licensing, contribution rules, source/reuse tracking and direct-to-main workflow established | Does not release hardware for manufacture |
| Rev A product baseline | Compute, display class, sensors, LoRa, ADS-B/RP2040, storage, audio provision, expansion and four-layer construction recorded | Exact open parts remain below |
| Display evidence | Exact AFY240320A1-2.8INTH-C1 revision-J specification, electrical limits and 40-plus-6 contact maps reviewed | Mating connector geometry, 1.8 V translation, backlight driver and samples still gate footprint release |
| GNSS product decision | MAX-M10S-00B accepted for documented airborne modes to 80 km; exact pin/application/land-pattern sources reviewed | Antenna, backup/power behavior and independent footprint review still being closed |
| Battery product decision | Two removable matched 21700 cells in 2S; one balanced charger and common protection direction accepted | Exact circuit needs qualified electrical/battery review |
| ESP32 compute | ESP32-S3-WROOM-1-N16R8 entry, decoupling/reset and complete GPIO allocation present in KiCad | Board-level concurrency and boot-state validation remain |
| Sensors | MMC5983MA, BMP581 and SHT40 entries present; ICM-42688-P pin/application evidence reviewed | Physical CAD and placement checks remain for several sensors |
| ADS-B digital feasibility | Host timing/CRC fixture passes four tests | Analog RF sensitivity and RP2040 PIO/DMA hardware remain unproven |
| KiCad structure | Root plus eight sheets parse in KiCad 10; latest ERC has zero violations | Several sheets are intentional holds, not completed circuits |
| Mechanical planning | 84 x 60 mm PCB and about 88 x 64 x 37 mm two-cell enclosure are starting envelopes | Printed dummy, exact holder and display connector/sample fit remain |
| Manufacturing plan | Four-layer Chinese PCBA workflow and release gates documented | No Gerbers, CPL or orderable BOM exist yet |

## Remaining gates before Astra

| Priority | Gate | Sol/external work needed | Closure evidence |
| ---: | --- | --- | --- |
| 1 | Exact display | Independently transcribe revision-J FPC geometry; select mating connectors, 1.8 V translation and backlight driver; obtain two labeled samples | Verified connector footprints plus backlight, address, power, touch/readability and shared-bus tests |
| 2 | 2S power | Accept exact cell and holder; close preferred BQ25887 application, TUSB320LAI candidate/unpowered states, common protection, USB-C input protection, buck rails, NTC/fuse/FETs and state estimation | Qualified reviewer signs schematic plan and fault limits before KiCad commitment |
| 3 | GNSS implementation package | Decide MAX-M10S-00B backup/power-gating and exact antenna/connector/ESD; construct and independently compare the footprint | Accepted circuit choices, exact footprint and antenna/layout checklist with official revisions |
| 4 | Remaining digital parts | Select exact microSD socket, microphone, USB-C connector, expansion connector, RP2040 flash/clock and support parts | Orderable MPNs, pin maps, footprints and interface/voltage review |
| 5 | Sensors | Create/review ICM-42688-P and other gated physical footprints; close thermal, magnetic and vent constraints | Independent CAD comparison and placement rules |
| 6 | LoRa RF | Freeze exact SX1262 ordering code, clock/RF switch and the chosen 915 MHz manufacturer reference network | Reference revision, simulation/stackup inputs and conducted-test plan |
| 7 | ADS-B RF | Close exact suffixes, gain/filter chain, power rails, RP2040 capture interface and RF coupon | RF review plus testable schematic and conducted acceptance limits |
| 8 | PCB/mechanical inputs | Confirm four-layer order stack, impedance geometry, exact outline, connectors, antenna keepouts and printed fit dummy | Manufacturer stack confirmation and signed mechanical fit review |
| 9 | System-level electrical review | Reconcile every voltage, current peak, bus address, boot state, interrupt, pullup, unpowered state and test point | Decision-complete net/interface matrix with no unresolved collision |

## Work reserved for Astra

Astra should be invoked only after all nine gates above have closure evidence and [the final handoff](ASTRA_HANDOFF.md) says **READY**. Astra then performs KiCad library integration, schematic capture, annotation, ERC, PCB setup, placement, routing and DRC. Any newly discovered product or safety decision returns to this engineering phase instead of being invented during CAD entry.

## After Astra

An independent review must inspect the completed schematic and PCB, especially power and RF. Only then generate and cross-check Gerbers, drill files, fabrication notes, orderable BOM, component-placement file, assembly drawings and programming/test instructions. The project owner must explicitly accept the manufacturing release before an order is placed.
