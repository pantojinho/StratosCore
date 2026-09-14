# Project status

Last updated: 2026-09-14. Current phase: **pre-KiCad hardware engineering closure**.

The immediate objective is to finish exact component selection, electrical compatibility, application circuits, interfaces, footprints, mechanical constraints and review evidence with Sol-class work. Astra is reserved for final KiCad schematic capture, PCB placement/routing and ERC/DRC after this document declares the handoff ready.

## Completed and verified

| Area | Current result | Evidence boundary |
| --- | --- | --- |
| Repository foundation | Licensing, contribution rules, source/reuse tracking and direct-to-main workflow established | Does not release hardware for manufacture |
| Rev A product baseline | Compute, display class, sensors, LoRa, ADS-B/RP2040, storage, audio provision, expansion and four-layer construction recorded | Exact open parts remain below |
| Display evidence | C1 electrical/contact data plus XF3M connector, AXC/LVC translator and TPS61169 backlight candidates reviewed | Controlled drawing/SPI ambiguity, samples, independent CAD and prototype tests still gate release |
| GNSS product decision | MAX-M10S-00B accepted; exact pin/land pattern reviewed and P20 provides a preferred passive antenna/U.FL/ESD application | RF/PDN review, antenna fit, RF geometry, independent CAD and prototype tests remain |
| Battery product decision | Two removable matched 21700 cells in 2S; one balanced charger and common protection direction accepted | Exact circuit needs qualified electrical/battery review |
| ESP32 compute | ESP32-S3-WROOM-1-N16R8 entry, decoupling/reset and complete GPIO allocation present in KiCad | Board-level concurrency and boot-state validation remain |
| Sensors | MMC5983MA, BMP581 and SHT40 entries present; ICM-42688-P pin/application evidence reviewed | Physical CAD and placement checks remain for several sensors |
| ADS-B digital feasibility | Host timing/CRC fixture passes four tests | Analog RF sensitivity and RP2040 PIO/DMA hardware remain unproven |
| Remaining support candidates | Exact candidates documented for main/quiet/1.8 V rails, PDM audio, USB-C/signal ESD, expansion, buttons, slow I/O and common RF interconnects | Application/footprint/mechanical review and board tests remain; VBUS/protection are still open |
| KiCad structure | Root plus eight sheets parse in KiCad 10; latest ERC has zero violations | Several sheets are intentional holds, not completed circuits |
| Mechanical planning | 84 x 60 mm PCB and about 88 x 64 x 37 mm two-cell enclosure are starting envelopes | Printed dummy, exact holder and display connector/sample fit remain |
| Manufacturing plan | Four-layer Chinese PCBA workflow and release gates documented | No Gerbers, CPL or orderable BOM exist yet |

## Remaining gates before Astra

| Priority | Gate | Sol/external work needed | Closure evidence |
| ---: | --- | --- | --- |
| 1 | Exact display | Review P21; obtain controlled Orient drawing, two labeled samples and confirmed SPI mode; independently compare CAD and prototype the translated interface/backlight | Verified footprints plus backlight, address, power, touch/readability, fault, EMI and shared-bus results |
| 2 | 2S power | Review P22/P24; accept exact cell/holder, close BQ25887/TUSB320LAI, common protection, VBUS protection, buck/passives, NTC/fuse/FET/state estimation and every fault state | Qualified reviewer signs the complete schematic plan and fault limits before KiCad commitment |
| 3 | GNSS implementation package | RF/PDN review P20: always-on tied 3.3 V, no backup/reset/EXTINT, passive FXP611/U.FL/TPD1E0B04 path; reserve the enclosure keepout, calculate/VNA-check RF and independently compare footprints | Accepted choices, exact reviewed footprints, antenna fit/layout checklist and cold-start/PPS/AIR4/coexistence results |
| 4 | Remaining digital parts | Review P23/P24; independently compare RP2040 flash/clock, microSD, microphone/translator, USB-C/ESD, expansion, buttons and TCA9535 footprints; close reset/off-state behavior | Orderable reviewed MPNs, pin maps, footprints and interface/voltage evidence |
| 5 | Sensors | Create/review ICM-42688-P and other gated physical footprints; close thermal, magnetic and vent constraints | Independent CAD comparison and placement rules |
| 6 | LoRa RF | Review P25; freeze exact SX1262 ordering code, clock/RF switch, 915 MHz manufacturer reference network and U.FL/CAB.721 option | Reference revision, independent CAD, simulation/stackup inputs and conducted-test plan |
| 7 | ADS-B RF | Review P22/P25; close exact suffixes, gain/filter chain, quiet power, RP2040 capture interface, U.FL/CAB.721 path and RF coupon | RF review plus testable schematic and conducted acceptance limits |
| 8 | PCB/mechanical inputs | Confirm four-layer order stack, impedance geometry, exact outline, connectors, antenna keepouts and printed fit dummy | Manufacturer stack confirmation and signed mechanical fit review |
| 9 | System-level electrical review | Close every OPEN item in `ELECTRICAL_COMPATIBILITY_MATRIX.md`, including current peaks, bus pullups/capacitance, reset defaults, interrupts, hot-plug and unpowered states | Independently reviewed net/interface matrix with no unresolved collision |

## Work reserved for Astra

Astra should be invoked only after all nine gates above have closure evidence and [the final handoff](ASTRA_HANDOFF.md) says **READY**. Astra then performs KiCad library integration, schematic capture, annotation, ERC, PCB setup, placement, routing and DRC. Any newly discovered product or safety decision returns to this engineering phase instead of being invented during CAD entry.

## After Astra

An independent review must inspect the completed schematic and PCB, especially power and RF. Only then generate and cross-check Gerbers, drill files, fabrication notes, orderable BOM, component-placement file, assembly drawings and programming/test instructions. The project owner must explicitly accept the manufacturing release before an order is placed.
