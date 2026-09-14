# Decision register

Baseline established from the owner's foundation brief; register last updated 2026-09-14. Dated evidence and sourcing snapshots retain their individual review dates. LOCKED means a product constraint, not a validated design. OPEN means selection incomplete. PROPOSED means an engineering starting point requiring validation.

## Locked baseline

| ID | Decision | Qualification |
| --- | --- | --- |
| D01 | Project/repository name StratosCore | Independent of legacy projects |
| D02 | ESP32-S3-WROOM-1-N16R8 | 16 MB Flash, 8 MB PSRAM, Wi-Fi/BLE, module PCB antenna; no bare SoC substitution |
| D03 | 2.8-inch IPS 320 x 240 and capacitive touch | Orient C1 is the sample candidate; connector, translation, driver and sample evidence remain open; no speculative footprint |
| D04 | Portrait and landscape support; two physical buttons | Mechanical access and coordinate transforms required |
| D05 | SX1262 directly on PCB, SPI, 915 MHz class hardware | No E220/E32, UART radio module, or plug-in radio board; regional TX settings configurable |
| D06 | LoRa PCB U.FL | Optional enclosure SMA via pigtail; exact connector ordering code open |
| D07 | u-blox MAX-M10S-00B GNSS, UART | Owner accepted P07 on 2026-09-13; 80 km airborne mode resolves the balloon-altitude conflict; antenna open |
| D08 | ICM-42688-P, MMC5983MA, BMP581, SHT40 | No BME688 baseline; isolate environmental sensors from heat |
| D09 | Integrated 1090 MHz ADS-B in Rev A | Independent RF chain; RP2040 baseline for timing-critical decoding |
| D10 | Mandatory microSD | Timestamped telemetry, contacts, events and system state |
| D11 | Digital MEMS microphone provision | Optional synchronized audio; I2S preferred, PDM possible; later DNP by documented decision |
| D12 | USB-C charging | Native USB data where practical; connector is not a PD negotiation controller |
| D13 | Two removable 21700 cells in a 2S series holder | Owner accepted the architecture direction on 2026-09-13: one balanced 2S charger and common 2S protection; exact circuit is not frozen pending qualified electrical/battery review |
| D14 | I2C/SPI/UART expansion | Also 3V3, GND, dedicated CS, GPIO/IRQ; 5V optional |
| D15 | Four-layer PCB | Exact materials, thickness, copper and impedance geometry open |
| D16 | Approximately 80 x 60 mm footprint target | Exact PCB and enclosure boundaries must be reconciled; not a fixed outline |
| D17 | 3D-printed enclosure for display plus two 21700 cells | Approximately 37 mm starting thickness from the current stack study; verify with a printed dummy |
| D18 | CERN-OHL-P-2.0 hardware; MIT original firmware | Official texts; third-party terms remain intact |
| D19 | ADS-B receiver baseline remains RP2040 | Better architectures may be proposed with evidence; no replacement accepted |
| D20 | Current execution priority is hardware and PCBA readiness | Sol closes evidence, selections, interfaces and review gates; Astra is reserved for efficient KiCad schematic/PCB execution after the handoff is decision-complete |

## Open selections

Display mating connectors/translation/backlight, GNSS antenna, microphone MPN, USB-C input controller, exact 2S charger/protection/regulators, holder ordering code, exact PCB dimensions, enclosure thickness, RF connector MPNs and GNSS/ADS-B connector styles remain OPEN. The display, ADS-B frontend, BQ25887 charger candidate, mechanical envelope and stackup are proposals or sample candidates with explicit gates below. The LoRa connector *family* remains U.FL despite the general connector-selection TODO.

## Proposals, not freezes

| ID | Proposal | Evidence needed |
| --- | --- | --- |
| P01 | Prefer serial LCD interface and shared sensor I2C; budget buses before GPIO assignment | Panel datasheet, bandwidth, interrupts, boot and memory constraints |
| P02 | UART as first ESP32/RP2040 transport candidate; SPI alternative | Simultaneous GNSS/expansion/debug UART allocation and contact burst throughput |
| P03 | Evaluate one protected 1S bay first; independently managed dual bays for larger version | SUPERSEDED by the owner-approved P14 two-cell-only 2S direction |
| P04 | L1 components/signals, L2 solid ground, L3 power/signals, L4 signals/components | Manufacturer stackup, return-current review, controlled impedance |
| P05 | ESP-IDF/FreeRTOS with separate board support and services | Toolchain/license audit and MeshCore port feasibility; no firmware build selected |
| P06 | Orient `AFY240320A1-2.8INTH-C1` as display sample candidate using SPI | Exact revision-J specification reviewed 2026-09-14; independently transcribe FPC geometry, select mating connectors/1.8 V translation/backlight driver, inspect labeled samples and run readability/power tests; footprint remains prohibited |
| P07 | Replace ATGM332D-5NR32 with u-blox `MAX-M10S-00B` | ACCEPTED by owner 2026-09-13; verify exact symbol/footprint, antenna and configuration before schematic entry |
| P08 | Two BQ25185 independent 1S bays feeding LTC4415, with per-bay fuse/reverse protection/NTC/gauge | REJECTED by owner 2026-09-13 as excessive complexity; retained only as comparison evidence |
| P09 | 84 x 60 mm PCB and approximately 37 mm two-cell enclosure | Printed dummy and final component/connector tolerance stack |
| P10 | JLCPCB 1.6 mm four-layer JLC2313 stack as field-solver candidate | Current manufacturer order confirmation and impedance geometries before layout |
| P11 | BLB01/TA2003A/ADL5513/MCP6566 ADS-B frontend | S-parameter simulation, supply quote, conducted sensitivity/blocker/pulse tests and RF review |
| P12 | Shared SPI plus dedicated high-speed flow-controlled RP2040 UART; GPIO map in `INTERFACE_GPIO_MAP.md` | Boot-state electrical review and full concurrency logic-analyzer test |
| P13 | Implement ICM-42688-P, MMC5983MA, BMP581 and SHT40-AD1B-R2 on the 3.3 V I2C bus; direct interrupt only for the IMU | MMC5983MA/BMP581 logical pin maps and exact SHT40 entry complete; ICM v1.9 pin/application evidence released and custom footprint pending; physical CAD reviews, bus capacitance, identity tests and magnetic/thermal/pressure-port validation remain |
| P14 | Two removable matched 21700 cells in series, one balanced 2S charger and common 2S protection; BQ25887 is the first charger candidate | OWNER ACCEPTED 2026-09-13; qualified electrical/battery review, exact holder continuity, missing/reversed-cell handling, discharge protection, power-path behavior, regulator design and fault tests remain mandatory before freeze or energizing |
| P15 | Molicel `INR-21700-M50A` as the first matched-cell sample candidate | Official sheet matches the 5 Ah runtime basis and exact mechanical envelope; owner/reviewer acceptance, Brazilian sourcing, mission-temperature and holder-fit evidence remain |
| P16 | Keep `BQ25887RGER` as preferred charger candidate without batteryless operation; compare `BQ25792RQMR` only if an NVDC power path becomes required | BQ25887 integrates 2S balancing but TI confirms no power path; exact protection, current, termination-under-load and USB behavior remain review gates |
| P17 | Evaluate `TUSB320LAIRWBR` as the fixed-UFP USB-C CC controller; remain at 5 V without USB PD | TI documents default/1.5 A/3 A current detection at address 0x47. Hardware caps BQ25887 input at 500 mA until valid detection; exact connector, back-power, ESD/inrush and factory availability remain open |

## Conflicts requiring explicit resolution

See [legacy comparison](../references/LEGACY_PROJECTS.md). Legacy AMOLED, QMI8658, BME688, BMM350, AT6558R and UART LoRa assumptions do not apply. P07 resolves the GNSS altitude conflict with MAX-M10S-00B. P14 replaces the rejected independent-bay proposal, but remains gated by qualified battery review. ADSBee GPL reuse and MeshCore dependency licensing require review against the MIT objective.

## Accepted change records

### 2026-09-13: P07 / D07 GNSS replacement

- **Owner:** project owner, accepted in the Codex session.
- **Reason:** ATGM332D-5NR32 is limited to 18,000 m; the balloon profile requires operation above that ceiling.
- **Cost and availability snapshot:** comparison reviewed 2026-09-11 in [component evidence](COMPONENT_EVIDENCE.md); MAX-M10S-00B was approximately USD 9.60 more at prototype quantity but had broader authorized-distributor stock.
- **Electrical/firmware/PCB impact:** new 1.76-3.6 V module, UBX configuration/driver work, smaller non-pin-compatible 18-pad LCC footprint, and new backup/antenna/startup review.
- **Outcome:** accepted as the Rev A GNSS baseline; exact CAD and antenna evidence remain gates.

### 2026-09-13: P08 rejected; P14 / D13 2S direction accepted

- **Owner:** project owner, accepted in the Codex session.
- **Reason:** two complete independent charge/power channels were rejected as excessive complexity. The owner requires two removable 21700 cells in a holder and one charger/control solution.
- **Cost and availability snapshot:** the rejected BQ25185/LTC4415 option is preserved in [power review history](POWER_ARCHITECTURE_OPTIONS.md). For the first 2S charger candidate, Mouser listed 7,531 BQ25887RGER at USD 5.01 each and DigiKey listed 235 BQ25887RGET at USD 6.62 each when checked 2026-09-13; LCSC listed no stock. Prices and stock require recheck at purchase.
- **Electrical impact:** pack changes from 1S-class rails to 6.0-8.4 V nominal operating range planning; USB charging needs boost conversion, midpoint sensing/balancing and a separate reviewed discharge-protection path. Downstream rails require buck conversion.
- **Firmware impact:** configure and monitor the 2S charger over I2C, report both cell voltages and reject missing, reversed, out-of-range or badly mismatched cells before charging.
- **PCB/mechanical impact:** one 4 x 4 mm VQFN charger candidate replaces two WSON chargers plus the OR stage; holder wiring/midpoint, clearance, heat, cell-removal access and approximately 37 mm enclosure depth require validation.
- **Outcome:** 2S architecture direction accepted by the owner. This is not a circuit or safety freeze; a qualified electrical/battery reviewer and the documented fault tests remain mandatory before prototype energizing.

## Change record template

Record date, decision ID/status, owner/reviewer, reason, alternatives, dated cost and availability comparisons, electrical/firmware/PCB/mechanical impact, source evidence, validation plan, and explicit accepted/rejected outcome. Update affected documents and BOM in the same change.
