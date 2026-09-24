# Decision register

Baseline established from the owner's foundation brief; register last updated 2026-09-24. Dated evidence and sourcing snapshots retain their individual review dates. LOCKED means a product constraint, not a validated design. OPEN means selection incomplete. PROPOSED means an engineering starting point requiring validation.

## Locked baseline

| ID | Decision | Qualification |
| --- | --- | --- |
| D01 | Project/repository name StratosCore | Independent of legacy projects |
| D02 | ESP32-S3-WROOM-1-N16R8 | 16 MB Flash, 8 MB PSRAM, Wi-Fi/BLE, module PCB antenna; no bare SoC substitution |
| D03 | 2.8-inch IPS 320 x 240 and capacitive touch | Orient C1 is the sample candidate; connector, translation, driver and sample evidence remain open; no speculative footprint |
| D04 | Portrait and landscape support; two physical buttons | Mechanical access and coordinate transforms required |
| D05 | SX1262 directly on PCB, SPI, 915 MHz class hardware | No E220/E32, UART radio module, or plug-in radio board; regional TX settings configurable. Exact ordering code SX1262IMLTRT confirmed 2026-09-14 (QFN-24 4 x 4 mm; Rev 1.2 Table 3-6: 118 mA typical TX at +22 dBm, 915 MHz) |
| D06 | LoRa PCB U.FL | Optional enclosure SMA via pigtail; exact connector ordering code open |
| D07 | u-blox MAX-M10S-00B GNSS, UART | Owner accepted P07 on 2026-09-13; 80 km airborne mode resolves the balloon-altitude conflict; antenna open |
| D08 | ICM-42688-P, MMC5983MA, BMP581, SHT40-AD1B-R2 | No BME688 baseline; isolate environmental sensors from heat |
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
| D20 | Current execution priority is hardware and PCBA readiness | Owner revised 2026-09-24: Astra leads the complete project, coordinates engineering and CAD, reviews and integrates results; Claude, Hermes, Sol and other AI agents execute bounded delegated tasks. Existing baseline and release gates remain mandatory |
| D21 | The unit must operate while USB charging is active | Does not require batteryless operation; the power design must prove safe charge-under-load behavior and valid termination |
| D22 | Run the shared peripheral I2C bus at 100 kHz and remove TUSB320LAI from that bus | Use the TUSB320LAI GPIO-mode interface. SYS-01 (PR #140, merged 2026-09-22) closed the GPIO allocation, pull-up value and cable limit; per-device off-state review and the independent net-matrix review remain engineering work |
| D23 | Rev A is a personal, non-commercial, open-community hobby prototype | This classification does not waive applicable radio or flight rules during operation |
| D24 | Target an average cost no higher than BRL 200 per unit for the initial five-unit batch | Owner clarified 2026-09-22: includes Chinese assembled PCB and display/touch; excludes locally bought cells, locally made 3D enclosure, freight and taxes. Actual five-unit quotes and allocation remain to be verified |
| D25 | Low-cost, easy-to-assemble hobby prototype for use on a desk, in a car, and in protected but unpressurized aircraft cabins; possible experimental drone, model-aircraft, balloon, ultralight, hang-glider and paramotor use | Owner revised the realistic operating altitude to approximately 10,000 ft on 2026-09-22. 30,000 ft is an optional stretch scenario, not a verified performance requirement. Balloon use and exposed installations require separate assessment. Minimum runtime remains 8 hours on two 21700 cells. Temperature and flight dynamics remain open; no mass or rain/ingress target is imposed on Rev A |
| D26 | The owner will purchase the two removable 21700 cells locally | Shipping the assembled unit with cells and its UN38.3 logistics path are outside the current prototype scope; exact cell and holder still require engineering evidence |
| D27 | Rev A has no conformal-coating, rain/ingress or special environmental-protection requirement | Preserve required pressure, humidity and acoustic openings; the owner accepts that the hobby prototype is not environmentally qualified |
| D28 | Initial five PCBA units are programmed and tested locally via USB-C | Owner confirmed 2026-09-22: no factory firmware flashing or credential injection. Preserve USB-C recovery/programming access and local SWD test access; board identification/labels may be applied locally |
| D29 | Keep the locked BMP581 as a secondary, indicative pressure/altitude/vario sensor for the hobby prototype | Owner explicitly withdrew the mandatory 30,000 ft barometric-coverage requirement and rejected P27 on 2026-09-22. Approximately 10,000 ft is the realistic use case; 30,000 ft is exploratory only. Flag readings outside the manufacturer's specified pressure/temperature range or invalid calibration; do not present this as a primary flight instrument or claim measured performance before testing |

## Open selections

The display's revision-J serial straps are verified and Rev A provisionally prefers write-only three-line SPI; controlled power/FPC drawings and sample validation remain OPEN. The 2S protection/VBUS protection/holder/state estimation, RF circuits, exact PCB dimensions, enclosure thickness and production stackup also remain OPEN. Preferred candidates now exist for the display connectors/translation/backlight, GNSS package, microphone, USB-C, expansion, regulators, buttons and RF interconnects, but their review/test gates below still prevent footprint or schematic release. The LoRa connector family remains locked to U.FL.

## Proposals, not freezes

| ID | Proposal | Evidence needed |
| --- | --- | --- |
| P01 | Prefer serial LCD interface and shared sensor I2C; budget buses before GPIO assignment | Panel datasheet, bandwidth, interrupts, boot and memory constraints |
| P02 | UART as first ESP32/RP2040 transport candidate; SPI alternative | Simultaneous GNSS/expansion/debug UART allocation and contact burst throughput |
| P03 | Evaluate one protected 1S bay first; independently managed dual bays for larger version | SUPERSEDED by the owner-approved P14 two-cell-only 2S direction |
| P04 | L1 components/signals, L2 solid ground, L3 power/signals, L4 signals/components | Manufacturer stackup, return-current review, controlled impedance |
| P05 | ESP-IDF/FreeRTOS with separate board support and services | Toolchain/license audit and MeshCore port feasibility; no firmware build selected |
| P06 | Orient `AFY240320A1-2.8INTH-C1` as display sample candidate using SPI | Revision-J verifies three-line `101` and four-line `110` straps; Rev A provisionally prefers unambiguous write-only three-line SPI. Controlled power/FPC clarification, independent CAD, labeled samples and prototype tests still gate release |
| P07 | Replace ATGM332D-5NR32 with u-blox `MAX-M10S-00B` | ACCEPTED by owner 2026-09-13; verify exact symbol/footprint, antenna and configuration before schematic entry |
| P08 | Two BQ25185 independent 1S bays feeding LTC4415, with per-bay fuse/reverse protection/NTC/gauge | REJECTED by owner 2026-09-13 as excessive complexity; retained only as comparison evidence |
| P09 | 84 x 60 mm PCB and approximately 37 mm two-cell enclosure | Printed dummy and final component/connector tolerance stack |
| P10 | JLCPCB 1.6 mm four-layer stack as field-solver candidate — current official identifier JLC04161H-3313 (3313 prepreg replaced 2313, same thickness/Dk; verified from JLCPCB pages 2026-09-17, candidate geometries in PCB_STACKUP.md) | Current manufacturer order confirmation and impedance geometries before layout |
| P11 | BLB01/TA2003A/ADL5513/MCP6566 ADS-B frontend | S-parameter simulation, supply quote, conducted sensitivity/blocker/pulse tests and RF review |
| P12 | Shared SPI plus dedicated high-speed flow-controlled RP2040 UART; GPIO map in `INTERFACE_GPIO_MAP.md` | Boot-state electrical review and full concurrency logic-analyzer test |
| P13 | Implement ICM-42688-P, MMC5983MA, BMP581 and SHT40-AD1B-R2 on the 3.3 V I2C bus; direct interrupt only for the IMU | Logical pin maps/application evidence are complete; ICM retains its dated dimensional review; MMC/BMP candidates were corrected 2026-09-23 after prior dimensional-pass claims proved wrong (see FOOTPRINT_CORRECTIONS_2026_09_23.md). Independent review of the corrected files remains open. Remaining assembler/process review, bus capacitance, identity tests and magnetic/thermal/pressure-port validation still gate release |
| P14 | Two removable matched 21700 cells in series, one balanced 2S charger and common 2S protection; BQ25887 is the first charger candidate | OWNER ACCEPTED 2026-09-13; qualified electrical/battery review, exact holder continuity, missing/reversed-cell handling, discharge protection, power-path behavior, regulator design and fault tests remain mandatory before freeze or energizing |
| P15 | Molicel `INR-21700-M50A` as the first matched-cell sample candidate | Official sheet matches the 5 Ah runtime basis and exact mechanical envelope; owner/reviewer acceptance, Brazilian sourcing, mission-temperature and holder-fit evidence remain |
| P16 | Keep `BQ25887RGER` as preferred charger candidate without batteryless operation; compare `BQ25792RQMR` only if an NVDC power path becomes required | BQ25887 integrates 2S balancing but TI confirms no power path. Autonomous charge after POR, hardware `CD` gating, protection-ground/cutoff compatibility and termination under system load are explicit qualified-review gates |
| P17 | Evaluate `TUSB320LAIRWBR` as the fixed-UFP USB-C CC controller and `TPS259474LRPWR` as the VBUS eFuse; remain at 5 V without USB PD | TI documents default/1.5 A/3 A detection at 0x47. Hardware keeps charger CD disabled until valid cells and an accepted USB current state. PWR-02 (PR #147, 2026-09-22) closed the TPS259474L eFuse network (RILM 1.69 k -> 1.97 A breaker, UVLO 3.98 V / OVLO 6.50 V dividers, dVdt open) and fixed the TUSB320LAI GPIO-mode default-current-only sink policy; corrected the ESD claim to device-level only. Remaining: ITIMER sizing (O06), back-power, discharge, thermal review and sourcing |
| P18 | Use `W25Q128JVSIQ` and `ABM8-272-T3` as the preferred RP2040 flash/clock candidates | Both manufacturer-derived lands passed independent dimensional reviews and KiCad export. Assembler mask/paste/courtyard decisions plus oscillator/flash corner bring-up remain gates |
| P19 | Use Hirose `DM3AT-SF-PEJM5` as the preferred microSD socket candidate on shared SPI | Exact drawing `0000947170 / EDC-325165-00-00` Rev 4, card detect, lands and operational card envelope reviewed. DIG-02 (PR #154, 2026-09-22) closed the power/signal/ESD/card-detect/power-fail circuit: switched `3V3_SD` behind the DIG-03 enable, SPI-mode SD_CS->DAT3 mapping, CLK pull-up exclusion, socket-edge ESD array (device-level claim only), power-fail fresh-init rule. Remaining: assembler process, enclosure access and insertion-surge measurement (PWR-04) gates |
| P20 | Use the passive Taoglas `FXP611.07.0092C` on Hirose `U.FL-R-SMT-1(60)` with TI `TPD1E0B04DPYR`; tie MAX-M10S VCC/V_IO to the always-on system 3.3 V rail and leave V_BCKP, RESET_N, EXTINT, LNA_EN and VCC_RF open | PREFERRED APPLICATION; RF/PDN review required. Reserve the antenna's 40 x 40 mm enclosure area and 10 mm metal/ground clearance, validate cable/strain relief, calculate the 50-ohm path, simulate/VNA-check ESD loading, measure coexistence and independently review all footprints before KiCad release |
| P21 | Use `XF3M-4015-1B` and `XF3M-0615-1B` display connectors, `SN74AXC4T245PWR` plus `SN74LVC1G07DBVR` translation, and `TPS61169DCKR` backlight drive from `3V3_MAIN` | Preferred candidates only. Exact Omron lands and three-line `101` straps are documented; obtain controlled Orient power/FPC clarification, validate fit/mode on two samples, independently review CAD and prototype backlight current/fault/EMI behavior |
| P22 | Use `TPS62130ARGTR` for `3V3_MAIN`, `TPS7A2030PDBVR` for quiet ADS-B 3.0 V, `TPS7A2018PDBVR` for 1.8 V logic and `TPS22918DBVR` for justified switchable domains | Preferred rail candidates only; close simultaneous peak loads, passives, grouping, sequencing, back-power, transient, thermal and EMI evidence; exact 2S protection and VBUS path remain separate safety gates |
| P23 | Use TDK `MMICT5838-00-012` PDM microphone with TI `TXU0202DCUR` translator | Preferred candidates only. AUD-01 (PR #159) closed channel directions, mic supply/bypass/HQ clock and acoustic rules. Integration found the original direct `1V8_LOGIC` OE/mic assignment inconsistent with the switched-audio control; [audio-domain review](AUDIO_DOMAIN_REVIEW.md) proposes a separate `1V8_AUDIO_SW` branch, with exact TPS22918 CT/QOD/ramp/off-state application open as AUD-02. Independent CAD/footprints, port/gasket and audio/RF tests remain |
| P24 | Use GCT `USB4105-GF-A`, TI `TPD4E05U06DQARG4`, JST `BM12B-GHS-TBT`/`GHR-12V-S`, Alps `SKSCLCE010` buttons and TI `TCA9535PWR` slow I/O | Preferred support candidates only. DIG-03 (PR #149 + polarity fix #152, 2026-09-22) closed the TCA9535 16-port map with per-net external safe-state resistors: switched-domain enables use pull-down + active-high EN per TPS22918, so a dead/reset/powered-down expander leaves every domain OFF (`*_EN` net rename recorded for Astra); expander VDD on always-on `3V3_MAIN`; ESP32/RP2040 recovery routes counted without the expander. Remaining: VBUS protection, per-pin off-state proof (SYS-04), hot-plug/back-power and enclosure fit review |
| P25 | Standardize PCB RF receptacles on Hirose `U.FL-R-SMT-1(60)` and use Taoglas `CAB.721` for the ADS-B and optional LoRa SMA bulkheads | PREFERRED INTERCONNECT; RF/CAD review required. U.FL is an internal 30-cycle interface. Confirm complete RF loss/match, exact footprints, factory stackup, panel/cable fit, port labels and coexistence before layout release |
| P26 | ACCEPTED by owner 2026-09-21 — run the shared peripheral I2C bus at 100 kHz and remove TUSB320LAI from the bus, using its GPIO mode per SLLSEQ8D | Basis: `I2C_BUS_BUDGET.md` Result 3. This removes the TUSB320LAI 100 pF/1.6 mA constraint and address concern. SYS-01 (PR #140, merged 2026-09-22) calculated the remaining bus, allocated GPIOs and chose pull-ups; per-device off-state behavior and the independent net-matrix review remain open (O11) |
| P27 | Replace BMP581 with ST `LPS22HBTR` to meet the former 30,000 ft barometric requirement | **REJECTED by owner 2026-09-22; historical comparison only.** [Comparison and impacts](BAROMETER_30K_PROPOSAL.md) remain for traceability. D08 BMP581 stays fitted; no replacement work is required for the revised D29 |

## Conflicts requiring explicit resolution

See [legacy comparison](../references/LEGACY_PROJECTS.md). Legacy AMOLED, QMI8658, BME688, BMM350, AT6558R and UART LoRa assumptions do not apply. P07 resolves the GNSS altitude conflict with MAX-M10S-00B. P14 replaces the rejected independent-bay proposal, but remains gated by qualified battery review. ADSBee GPL reuse and MeshCore dependency licensing require review against the MIT objective.

## Accepted change records

### 2026-09-24: D20 revised — Astra assumes full project leadership

- **Owner acceptance:** the project owner explicitly requested that the documentation record Astra as already in control of the complete project, with Claude and Hermes acting as delegated workers.
- **Outcome:** Astra is the technical lead, coordinator, reviewer of contributions and integrator throughout engineering closure, candidate refinement and release preparation. Sol and other AI agents also operate as bounded workers when delegated; the former Astra-only-final-CAD allocation is superseded.
- **Scope:** governance only. No component, circuit, footprint, BOM, cost target or safety acceptance changes. D24 and qualified battery review O05 remain in force. Workers cannot accept their own results or publish to `main`.
- **Handover:** [Astra project control](ASTRA_PROJECT_CONTROL.md) records the received agent evidence at `912894b`, unresolved discrepancies and the inherited T1–T8 queue. Candidate decision records do not silently amend the root product baseline.

### 2026-09-22: D25/D29 altitude scope revised; P27 rejected

- **Owner:** project owner, clarified in the Codex session after reviewing the barometer replacement proposal.
- **Reason:** the project is a low-cost, readily sourced and assembled hobby prototype. Approximately 10,000 ft is the realistic use case; 30,000 ft is aspirational. Barometric data are indicative backup data, not a primary flight instrument.
- **Cost/availability:** the dated BMP581/LPS22HBTR component comparison remains in [P27 history](BAROMETER_30K_PROPOSAL.md). Keeping the fitted BMP581 avoids a replacement footprint and driver; neither a five-board PCBA quote nor AliExpress authenticity/availability has been verified.
- **Electrical/firmware/PCB impact:** retain the reviewed BMP581 circuit, I2C address, footprint candidate and vent constraints. Firmware must mark pressure/altitude/vario invalid when outside specified sensor limits or without valid calibration. No new LPS22HBTR circuit or footprint is authorized.
- **Outcome:** D08 remains locked; D25/D29 are revised, and P27 is closed as rejected. The former mandatory 30,000 ft barometric gate is removed from the Astra handoff.

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
- **Firmware impact:** configure and monitor the 2S charger over I2C, report both cell voltages and request inhibition for missing, reversed, out-of-range or badly mismatched cells. Firmware cannot guarantee a pre-charge inspection because BQ25887 starts autonomously after POR; fail-safe hardware gating is now an explicit qualified-review requirement.
- **PCB/mechanical impact:** one 4 x 4 mm VQFN charger candidate replaces two WSON chargers plus the OR stage; holder wiring/midpoint, clearance, heat, cell-removal access and approximately 37 mm enclosure depth require validation.
- **Outcome:** 2S architecture direction accepted by the owner. This is not a circuit or safety freeze; a qualified electrical/battery reviewer and the documented fault tests remain mandatory before prototype energizing.

### 2026-09-21: owner operating and prototype constraints

- **Owner:** project owner, accepted in the Codex session.
- **Operating policy:** operation while charging is required; batteryless operation remains outside scope.
- **Bus policy:** P26 option set accepted as D22: 100 kHz shared I2C, with TUSB320LAI moved to GPIO mode.
- **Product scope:** personal, non-commercial, open-community hobby prototype; unpressurized protected aircraft cabin/car/desk use is primary and balloon use is secondary.
- **Cost and quantity:** average target no higher than BRL 200 per unit for five Chinese PCBAs including display/touch; local cells/enclosure, freight and taxes are excluded.
- **Mission boundary (superseded 2026-09-22):** the original 30,000 ft reference was revised by the owner to approximately 10,000 ft realistic use with 30,000 ft as an exploratory stretch. BMP581 remains an indicative backup, not a primary flight instrument. Minimum runtime remains 8 hours on two 21700 cells; temperature range remains open. No mass or rain/ingress target is required.
- **Factory provisioning:** local USB-C flashing and testing; no factory firmware or credential injection.
- **Battery/logistics:** cells are locally purchased and removable; the project does not ship the prototype with cells in the current scope.
- **Environmental process:** no conformal coating or special environmental protection is required for Rev A.
- **Impact:** these decisions unblock the charge-under-load design, I2C rework, regulatory classification, local-cell logistics and no-coating process path. They do not approve the 2S circuit, exact cell/holder, radio operation, flight plan or unqualified environmental reliability.

## Change record template

Record date, decision ID/status, owner/reviewer, reason, alternatives, dated cost and availability comparisons, electrical/firmware/PCB/mechanical impact, source evidence, validation plan, and explicit accepted/rejected outcome. Update affected documents and BOM in the same change.

### 2026-09-14: Pre-Astra engineering review

- **Owner:** standing main authorization; no locked decision changed.
- **Work recorded:** confirmed exact `SX1262IMLTRT` ordering code; implemented and hardened the RP2040 UART host framing model; added candidate footprints with explicit provenance for W25Q128JVSIQ, ABM8-272-T3, DM3AT-SF-PEJM5, U.FL-R-SMT-1(60) and TPD1E0B04DPYR; added exact regulator/interface facts to the compatibility matrix; refined the ADS-B candidate bias/loss evidence.
- **Review corrections:** retained the conservative 1.935 W FLIGHT budget and open 12-hour runtime gate; treated the 974 mA main-rail value as an incomplete subtotal; removed ICM-42688-P and MAX-M10S footprint candidates whose geometry was not independently derived from the exact manufacturer source; kept all remaining footprint files gated from manufacture.
- **Outcome:** no locked product decision changed. Evidence advanced, but power, CAD, RF, sample and qualified-review gates remain open as listed in [project status](PROJECT_STATUS.md) and [open questions](OPEN_QUESTIONS.md).
