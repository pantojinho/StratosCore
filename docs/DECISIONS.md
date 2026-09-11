# Decision register

Baseline established from the owner's foundation brief; research reviewed 2026-09-11 UTC (2026-09-10 local session). LOCKED means a product constraint, not a validated design. OPEN means selection incomplete. PROPOSED means an engineering starting point requiring validation.

## Locked baseline

| ID | Decision | Qualification |
| --- | --- | --- |
| D01 | Project/repository name StratosCore | Independent of legacy projects |
| D02 | ESP32-S3-WROOM-1-N16R8 | 16 MB Flash, 8 MB PSRAM, Wi-Fi/BLE, module PCB antenna; no bare SoC substitution |
| D03 | 2.8-inch IPS 320 x 240 and capacitive touch | Exact panel/controller/connector open; no speculative footprint |
| D04 | Portrait and landscape support; two physical buttons | Mechanical access and coordinate transforms required |
| D05 | SX1262 directly on PCB, SPI, 915 MHz class hardware | No E220/E32, UART radio module, or plug-in radio board; regional TX settings configurable |
| D06 | LoRa PCB U.FL | Optional enclosure SMA via pigtail; exact connector ordering code open |
| D07 | ATGM332D-5NR32 GNSS, UART | Capabilities must be reconciled with vendor evidence; antenna open |
| D08 | ICM-42688-P, MMC5983MA, BMP581, SHT40 | No BME688 baseline; isolate environmental sensors from heat |
| D09 | Integrated 1090 MHz ADS-B in Rev A | Independent RF chain; RP2040 baseline for timing-critical decoding |
| D10 | Mandatory microSD | Timestamped telemetry, contacts, events and system state |
| D11 | Digital MEMS microphone provision | Optional synchronized audio; I2S preferred, PDM possible; later DNP by documented decision |
| D12 | USB-C charging | Native USB data where practical; connector is not a PD negotiation controller |
| D13 | Removable 21700 concept | Compact one-cell / larger two-cell enclosure; electrical topology explicitly open; no direct removable-cell parallel connection |
| D14 | I2C/SPI/UART expansion | Also 3V3, GND, dedicated CS, GPIO/IRQ; 5V optional |
| D15 | Four-layer PCB | Exact materials, thickness, copper and impedance geometry open |
| D16 | Approximately 80 x 60 mm footprint target | Exact PCB and enclosure boundaries must be reconciled; not a fixed outline |
| D17 | 3D-printed enclosure | 25-32 mm desired thickness, subject to display/cell/holder stack |
| D18 | CERN-OHL-P-2.0 hardware; MIT original firmware | Official texts; third-party terms remain intact |
| D19 | ADS-B receiver baseline remains RP2040 | Better architectures may be proposed with evidence; no replacement accepted |

## Open selections

Exact LCD manufacturer/MPN, touch controller, display connector, GNSS antenna, ADS-B RF frontend, microphone MPN, USB-C charger/PMIC, fuel gauge, one/two-cell topology, exact PCB dimensions, enclosure thickness, RF connector MPNs and GNSS/ADS-B connector styles, and PCB stackup remain OPEN. The LoRa connector *family* remains U.FL despite the general connector-selection TODO.

## Proposals, not freezes

| ID | Proposal | Evidence needed |
| --- | --- | --- |
| P01 | Prefer serial LCD interface and shared sensor I2C; budget buses before GPIO assignment | Panel datasheet, bandwidth, interrupts, boot and memory constraints |
| P02 | UART as first ESP32/RP2040 transport candidate; SPI alternative | Simultaneous GNSS/expansion/debug UART allocation and contact burst throughput |
| P03 | Evaluate one protected 1S bay first; independently managed dual bays for larger version | [Power options](POWER_ARCHITECTURE_OPTIONS.md) fault review and measured runtime; topology remains open |
| P04 | L1 components/signals, L2 solid ground, L3 power/signals, L4 signals/components | Manufacturer stackup, return-current review, controlled impedance |
| P05 | ESP-IDF/FreeRTOS with separate board support and services | Toolchain/license audit and MeshCore port feasibility; no firmware build selected |

## Conflicts requiring explicit resolution

See [legacy comparison](../references/LEGACY_PROJECTS.md). Legacy AMOLED, QMI8658, BME688, BMM350, AT6558R and UART LoRa assumptions do not apply. Galileo and configurable update rate are desired but not established for the exact GNSS. ADSBee GPL reuse and MeshCore dependency licensing require review against the MIT objective. No architecture change was accepted to resolve these issues automatically.

## Change record template

Record date, decision ID/status, owner/reviewer, reason, alternatives, dated cost and availability comparisons, electrical/firmware/PCB/mechanical impact, source evidence, validation plan, and explicit accepted/rejected outcome. Update affected documents and BOM in the same change.
