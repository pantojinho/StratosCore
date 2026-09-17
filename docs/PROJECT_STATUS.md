# Project status

Last updated: 2026-09-17. Current phase: **pre-KiCad hardware engineering closure**.

The immediate objective is to finish exact component selection, electrical compatibility, application circuits, interfaces, footprints, mechanical constraints and review evidence with Sol-class work. Astra is reserved for final KiCad schematic capture, PCB placement/routing and ERC/DRC after this document declares the handoff ready.

## Completed and verified

| Area | Current result | Evidence boundary |
| --- | --- | --- |
| Repository foundation | Licensing, contribution rules, source/reuse tracking and direct-to-main workflow established | Does not release hardware for manufacture |
| Rev A product baseline | Compute, display class, sensors, LoRa, ADS-B/RP2040, storage, audio provision, expansion and four-layer construction recorded | Exact open parts remain below |
| Display evidence | C1 serial straps verified; write-only three-line `101` preferred; exact XF3M lands and AXC/LVC/backlight starting circuits documented | Controlled TFT power/FPC clarification, samples, connector footprints, independent CAD and prototype tests still gate release |
| GNSS product decision | MAX-M10S-00B accepted; pin/application evidence and P20 passive antenna/U.FL/ESD proposal reviewed; manufacturer-derived copper/mask/T-paste footprint parses in KiCad, passes its automated geometry audit and completed an independent dimensional review | Assembler paste approval, RF/PDN review, antenna fit and prototype tests remain |
| Battery product decision | Two removable matched 21700 cells in 2S; one balanced charger and common protection direction accepted | Exact circuit needs qualified electrical/battery review |
| ESP32 compute | ESP32-S3-WROOM-1-N16R8 entry, decoupling/reset and complete GPIO allocation present in KiCad | Board-level concurrency and boot-state validation remain |
| Sensors | All four logical entries are present; manufacturer-derived ICM-42688-P, MMC5983MA and BMP581 footprint candidates parse/export, pass automated geometry audits and passed independent dimensional second passes | Assembler mask/paste/stencil decisions and final magnetic/thermal/pressure-port/full under-body placement/routing checks remain |
| ADS-B digital feasibility | Host timing/CRC fixture passes four tests; UART framing behavior passes 20 additional host tests | UART throughput and RP2040 PIO/DMA hardware remain unproven; analog RF sensitivity is also open |
| Remaining support candidates | Exact candidates documented for main/quiet/1.8 V rails, PDM audio, USB-C/signal ESD, expansion, buttons, slow I/O and RF interconnects; nine footprints carry explicit provenance. Corrected W25Q and TPD1E0B04 candidates parse/export and passed independent dimensional reviews | DM3 enclosure/process closure, assembler approvals, application/mechanical review, VBUS/protection and board tests remain open |
| KiCad structure | Root plus eight sheets parse in KiCad 10; latest ERC has zero violations | Several sheets are intentional holds, not completed circuits |
| Mechanical planning | 84 x 60 mm PCB and about 88 x 64 x 37 mm two-cell enclosure are starting envelopes | Printed dummy, exact holder and display connector/sample fit remain |
| Manufacturing plan | Four-layer Chinese PCBA workflow and release gates documented | No Gerbers, CPL or orderable BOM exist yet |

## Remaining gates before Astra

| Priority | Gate | Sol/external work needed | Closure evidence |
| ---: | --- | --- | --- |
| 1 | Exact display | Obtain controlled Orient TFT-power/FPC clarification and two labeled samples; validate provisional three-line `101` mode and XF3M fit; independently compare CAD and prototype translation/backlight | Verified footprints plus backlight, address, power, touch/readability, fault, EMI and shared-bus results |
| 2 | 2S power | Accept exact cell/holder and whether charging while operating is required; resolve BQ25887 autonomous-start hardware gating and charger/protector ground/cutoff conflict; close TUSB320LAI/TPS259474L, protection/FET/fuse/NTCs, buck, state estimation and every fault state | Qualified reviewer signs the complete schematic plan and fault limits before KiCad commitment |
| 3 | GNSS implementation package | Obtain assembler approval of the independently reviewed MAX-M10S T-paste pattern; review P20 against the final PDN/enclosure; reserve keepout and calculate/VNA-check RF | Accepted choices, independently reviewed footprint, antenna fit/layout checklist and cold-start/PPS/AIR4/coexistence results |
| 4 | Remaining digital parts | Datasheet-level evidence closed 2026-09-17 (W25Q JVSIQ ordering/QE/BOOTSEL/XIP, RP2040 boot/circuit, ABM8-272-T3 reference circuit); O20 keeps the corresponding bench tests (RP2040 boot/clock measurement, microSD power-fail) explicitly open — evidence is not bench proof. Remaining: DM3 enclosure/process, residual U.FL process/tool gates, bench tests | Orderable reviewed MPNs, pin maps, footprints and interface/voltage evidence |
| 5 | Sensors | ICM-42688-P, MMC5983MA and BMP581 candidates are derived from exact manufacturer drawings, pass automated geometry audits and passed independent dimensional reviews. Obtain assembler approval for every mask/paste/stencil choice, then close thermal, magnetic, pressure-port, vent and full under-body routing constraints | Assembler approval and accepted placement/routing rules |
| 6 | LoRa RF | AN1200.40 Rev 1.1 evidence recorded: E449V01A 4-layer TCXO design proposed as starting topology, matching/notch/pi-filter topology and RX balun documented, DC-DC + crystal proposal with TCXO/DIO3 fallback, PE4259-class switch proposal, conducted test outline. Remaining: exact E449 regional BOM values (drawing-embedded) and RF CAD | Reference revision BOM values, independent CAD, simulation/stackup inputs and conducted-test plan |
| 7 | ADS-B RF | BLB01/TA2003A/ADL5513/MCP6566 bias and loss figures transcribed; MCP6566 suffix closed 2026-09-17 (MCP6566T-E/OT preferred, /LT alternative, package drawings recorded, pull-up-above-VDD fact). Remaining: RF coupon/stackup verification with the factory | RF review plus testable schematic and conducted acceptance limits |
| 8 | PCB/mechanical inputs | JLC04161H-3313 stack verified from official JLCPCB pages 2026-09-17 (3313 replaced 2313, same thickness/Dk; candidate 50/90-ohm geometries computed and recorded in PCB_STACKUP.md). Remaining: order-time stack confirmation, impedance via factory solver, outline/connectors/keepouts/fit dummy | Manufacturer stack confirmation and signed mechanical fit review |
| 9 | System-level electrical review | Close the remaining OPEN rows in `ELECTRICAL_COMPATIBILITY_MATRIX.md` (complete peak loads, shared-bus pull-up value, sequencing and back-power); then independently review the complete net matrix. The pull-up method, admissible window, per-device Ci/IOL/Ii transcription and the evaluated window (TUSB320LAI 1.6 mA sink; 100 pF device cap at 400 kHz makes 100 kHz or bus re-architecture the realistic options) are worked in `I2C_BUS_BUDGET.md`; the blocking input is now the owner/reviewer bus decision recorded as proposal P26 | Independently reviewed net/interface matrix with no unresolved collision |

## Work reserved for Astra

Astra should be invoked only after all nine gates above have closure evidence and [the final handoff](ASTRA_HANDOFF.md) says **READY**. Astra then performs KiCad library integration, schematic capture, annotation, ERC, PCB setup, placement, routing and DRC. Any newly discovered product or safety decision returns to this engineering phase instead of being invented during CAD entry.

## After Astra

An independent review must inspect the completed schematic and PCB, especially power and RF. Only then generate and cross-check Gerbers, drill files, fabrication notes, orderable BOM, component-placement file, assembly drawings and programming/test instructions. The project owner must explicitly accept the manufacturing release before an order is placed.
