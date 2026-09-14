# GNSS architecture

Rev A is locked to **u-blox `MAX-M10S-00B` via UART**, accepted by the owner on 2026-09-13. This review prepares a preferred module and RF application for final RF/PDN review before later KiCad entry. No footprint or production RF geometry is released here.

Status terms in this document are intentional:

- **LOCKED:** accepted project decision.
- **VERIFIED:** fact checked against the listed u-blox document and revision.
- **PROPOSED:** engineering choice ready for project review but not a locked decision.
- **TBD:** evidence or a project choice is still missing.

## Controlled source set

The receiver sources were reviewed 2026-09-13 and the antenna-path sources 2026-09-14:

| Document | Revision/date | Sections used |
| --- | --- | --- |
| [MAX-M10S data sheet, UBX-20035208](https://content.u-blox.com/sites/default/files/MAX-M10S_DataSheet_UBX-20035208.pdf) | R08, 2026-01-30 | 1.2-1.5, 3, 4, 5, 6, 9 |
| [MAX-M10S integration manual, UBX-20053088](https://content.u-blox.com/sites/default/files/MAX-M10S_IntegrationManual_UBX-20053088.pdf) | R05, 2026-04-28 | 1.3, 2.1, 3.2-3.4, 4.1-4.4, appendices B-C |
| [u-blox M10 SPG 5.10 interface description, UBX-21035062](https://content.u-blox.com/sites/default/files/u-blox-M10-SPG-5.10_InterfaceDescription_UBX-21035062.pdf) | R03, protocol 34.10 | `CFG-NAVSPG-DYNMODEL`, `CFG-TP-*`, configuration layers |
| [Taoglas FXP611.07.0092C specification](https://www.taoglas.com/datasheets/FXP611.07.0092C.pdf) | SPE-13-8-010-G; document date not stated | Electrical, environmental and mechanical specification; cable and connector |
| [Hirose U.FL catalog](https://www.hirose.com/en/product/document?clcode=CL0321-6226-1-08&documentid=ed_U.FL_CAT&documenttype=Catalog&lang=en&productname=U.FL-2LPHF6-066N2-A-100&series=U.FL) | 2026-04-01 | `U.FL-R-SMT-1(60)` identity, ratings and PCB/mask drawings |
| [TI TPD1E0B04 data sheet](https://www.ti.com/lit/gpn/TPD1E0B04) | Rev C, 2025-06 | `TPD1E0B04DPYR` electrical limits, DPY package and antenna use |

Recheck the controlled sources at design freeze and subscribe to the applicable manufacturer change notices. Distributor and marketplace drawings do not control the symbol, footprint, or antenna circuit.

## Exact identity and verified capability

**VERIFIED:** `MAX-M10S-00B` is the global, professional-grade ordering code. The current data sheet applies to type number `MAX-M10S-00B-01`, ROM firmware SPG 5.10, with mass-production status. The ordering code and type number are different identifiers; procurement uses `MAX-M10S-00B`, while incoming inspection must confirm the `-01` type/revision marking against the purchase record.

The 18-pad LCC module is nominally 9.7 x 10.1 x 2.5 mm and 0.5 g. It supports GPS/QZSS L1C/A, Galileo E1-B/C, GLONASS L1OF, and BeiDou B1I/B1C. The default constellation set is GPS + Galileo + BeiDou B1I with QZSS and SBAS enabled. With the Airborne 4 g platform model, the documented operational limits are 80,000 m altitude, 500 m/s velocity, and 4 g dynamics. These are receiver limits, not a guarantee of antenna performance, fix availability, or environmental suitability in a balloon.

## Exact pin map and Rev A disposition

The directions below are from the module perspective. ESP32 net names are from the ESP32 perspective as defined in `INTERFACE_GPIO_MAP.md`.

| Pin | u-blox name | Verified function | Rev A disposition before KiCad entry |
| ---: | --- | --- | --- |
| 1 | GND | Ground | Connect to the ground plane |
| 2 | TXD | UART output | Connect to `GNSS_RX` / ESP32 GPIO18 |
| 3 | RXD | UART input | Connect from `GNSS_TX` / ESP32 GPIO17; unpowered-state drive must be resolved |
| 4 | TIMEPULSE | Time-pulse output, shared internally with SAFEBOOT_N through 1 kOhm | Connect to `GNSS_PPS` / ESP32 GPIO21; the host pin must remain high-impedance and must not pull this node low during GNSS startup |
| 5 | EXTINT | External interrupt, time/frequency aiding, wake and host-controlled power-save input | **PROPOSED:** leave open in Rev A; no host wake or antenna-supervisor role |
| 6 | V_BCKP | Optional backup-domain supply | **PROPOSED:** leave open in Rev A exactly as u-blox directs; do not tie to ground |
| 7 | V_IO | Digital-I/O and backup-domain supply | **PROPOSED:** tie to the same quiet 3.3 V rail as VCC |
| 8 | VCC | Core and RF main supply | **PROPOSED:** quiet 3.3 V rail sized for startup current |
| 9 | RESET_N | Active-low reset; internal pull-up; low for at least 1 ms | **PROPOSED:** leave open in Rev A; use documented UBX reset commands and a whole-domain power cycle for hard recovery; never add a capacitor to ground |
| 10 | GND | Ground | Connect to the ground plane |
| 11 | RF_IN | 50-ohm GNSS input; DC blocked inside the module | Route only through the selected 50-ohm antenna network |
| 12 | GND | Ground | Connect to the ground plane |
| 13 | LNA_EN | Active-high control for the integrated LNA and optional external LNA/active-antenna switch | **PROPOSED:** leave open because the selected antenna candidate is passive |
| 14 | VCC_RF | Filtered RF supply output, nominally VCC minus 0.1 V, 50 mA maximum operating output current | **PROPOSED:** leave open; the Rev A candidate RF path carries no DC bias and does not support an active antenna |
| 15 | VIO_SEL | V_IO range select | Leave open for the proposed 3.3 V V_IO design; connect to ground only in an accepted 1.8 V design |
| 16 | SDA | I2C data | Leave open because UART is locked for Rev A |
| 17 | SCL | I2C clock | Leave open because UART is locked for Rev A |
| 18 | SAFEBOOT_N | Active-low safeboot at receiver startup | Leave open; do not expose a load that can hold it or TIMEPULSE low at startup |

Pins 1, 10, and 12 are all ground connections, not optional no-connect pads. Pins marked open above remain represented on the symbol with explicit no-connect markers once the choice is final.

## Supply, backup, reset, and power control

### Verified electrical limits

- VCC operates from 1.76 V to 3.6 V. V_IO supports 1.76-1.98 V with VIO_SEL grounded, or 2.7-3.6 V with VIO_SEL open. V_IO must not exceed VCC + 0.3 V.
- V_BCKP operates from 1.65 V to 3.6 V. Typical hardware-backup current is 28 microamps at 3.3 V; normal-operation current from V_BCKP is about 3 microamps.
- Startup inrush can reach 100 mA. The source must support this without violating the rails. u-blox limits added series resistance in the VCC supply path to 0.2 ohm to avoid ripple under dynamic current.
- VCC and V_IO may be tied together for a 3.3 V design. With both at 3.3 V, they may be switched off together. When VCC and V_IO are off in hardware backup mode, module PIOs must not be driven.
- The u-blox minimum 3.3 V application diagram does not prescribe an external bypass-capacitor value. Local rail capacitance, filtering, load-switch choice, ramp rate, and return layout therefore remain a board-PDN design task and must not be invented from another receiver module.

### Proposed Rev A power arrangement

Use the board's quiet, always-on-during-system-operation 3.3 V domain for both VCC and V_IO and leave VIO_SEL open. Do not add a GNSS-only load switch in Rev A. This removes level shifting against the 3.3 V ESP32, matches u-blox's typical 3.3 V design, and eliminates the normal case where the host UART can drive an unpowered receiver. The system 3.3 V regulator and PDN must still meet the documented 100 mA startup demand with no more than 0.2 ohm added VCC series resistance.

There is **no dedicated enable pin** on MAX-M10S. EXTINT can control supported power-save behavior but is not a supply enable. The Rev A proposal leaves EXTINT open and keeps the receiver powered whenever the system 3.3 V rail is present. Any later request for independent hard power-off is a design change that must add a reviewed load switch plus UART/PPS isolation or host-state guarantees.

**PROPOSED backup choice:** leave V_BCKP open for Rev A. The host must reapply and verify configuration after every cold power-up and accept cold-start TTFF, or provide documented time/orbit assistance. This avoids a coin cell, supercapacitor and leakage/service-life path. Adding retention later requires a separately reviewed 1.65-3.6 V source and new sequencing and lifetime evidence.

**PROPOSED reset choice:** leave RESET_N open. A hardware reset clears RAM, battery-backed RAM, receiver configuration, RTC and orbit data and therefore behaves like a cold start. Normal reconfiguration/restart uses documented UBX commands; hard recovery power-cycles the whole switched system domain. Any later RESET_N control must be default-high-impedance, meet the 1 ms low time and place no capacitor from RESET_N to ground.

## Host interface and time pulse

**LOCKED:** UART is the primary host interface. Use `GNSS_TX` GPIO17 to module RXD and module TXD to `GNSS_RX` GPIO18. MAX-M10S has no UART hardware flow control. It powers up at 9600 baud, 8 data bits, no parity, one stop bit, with NMEA and UBX accepted. The supported data-sheet range is 9600 to 921600 bit/s. Buffer capacity and enabled messages must be matched to the selected baud rate.

**PROPOSED:** bring up at 9600 baud, identify the receiver with UBX, then change to 115200 baud and limit periodic output to the messages required by StratosCore. Reapply the complete configuration on every cold start during development; do not burn OTP in prototypes. Verify acknowledgement before changing host baud rate and allow the u-blox-recommended approximately 100 ms transition delay.

The I2C interface is not used in Rev A. If it is evaluated later, it is peripheral-only, Fast-mode up to 400 kbit/s, can stretch SCL for up to 20 ms, and uses seven-bit address 0x42 by default. It does not support Standard-mode compatibility. External pull-ups may be required after the actual bus capacitance is calculated.

TIMEPULSE provides default 1 PPS and is configurable from 0.25 Hz to 10 MHz. The project uses it as `GNSS_PPS`; firmware must qualify it with GNSS time-valid status before treating it as UTC. The default time-pulse output is enabled. Because TIMEPULSE and SAFEBOOT_N share an internal function through 1 kOhm, GPIO21 and any probe/load must never pull the node low while the receiver starts.

For balloon operation, firmware must set `CFG-NAVSPG-DYNMODEL` to `AIR4` (value 8, Airborne <4 g) and verify the accepted configuration after every cold start. The default is `PORT`, so the 80 km airborne envelope is not obtained merely by fitting the module.

## Antenna path

**VERIFIED:** RF_IN is internally DC blocked and presents 50 ohms. MAX-M10S includes a Band 13 notch filter, an LNA, and a SAW filter; u-blox states that no additional RF front-end is needed for the typical passive-antenna design. The default internal-LNA setting is low gain. Bypass mode is recommended when total external gain is 10-15 dB or more; normal-gain mode is not recommended for MAX-M10S.

### Proposed Rev A RF package

Use the passive Taoglas `FXP611.07.0092C` antenna, terminated in its factory 92 mm 1.37 mm coax and I-PEX MHF I plug, mated to a Hirose `U.FL-R-SMT-1(60)` board receptacle. Route the connector center contact to MAX-M10S RF_IN as a short calculated 50-ohm line, with one shunt `TPD1E0B04DPYR` ESD device at the connector. Do not fit a bias tee, external LNA or external SAW filter in the baseline. Leave LNA_EN and VCC_RF open and retain the MAX-M10S default low-gain internal-LNA mode.

This is a **PROPOSED** package pending owner and RF review. It is viable because it avoids the antenna-bias and short-circuit supervisor, covers the complete 1559-1610 MHz L1 span used by GPS, Galileo, GLONASS and BeiDou, and lets the 0.9 g flex attach to the inside of the 3D-printed enclosure. The antenna is 38 x 37 x 0.15 mm, requires a 40 x 40 x 0.2 mm allocation and at least 10 mm clearance from metal or the main device ground plane. Taoglas measured the published 80% efficiency and radiation behavior on a 30 x 30 cm ABS fixture, so those numbers are not claimed for the StratosCore enclosure.

The exact board receptacle is the reel-pack `U.FL-R-SMT-1(60)`, HRS `CL0331-0472-2-60`, 50 ohms, rated beyond the 1.61 GHz GNSS band and for 30 mating cycles. The mechanical team must provide cable bend radius, strain relief, connector tool access and a nonmetallic 40 x 40 mm antenna window. This connector is an internal assembly interconnect, not a user-serviceable external port.

The proposed TI `TPD1E0B04DPYR` is the 0402-class DPY package. TI specifies 3.6 V working voltage, 0.18 pF maximum I/O capacitance, ±8 kV IEC 61000-4-2 contact protection and antenna use. Place it adjacent to the U.FL signal pad with the shortest possible ground return and multiple nearby ground vias. Its S-parameter model and the complete connector/trace/ESD path must be simulated or VNA-checked at 1559-1610 MHz; the data-sheet bandwidth does not prove negligible loss in this layout.

An active antenna is deliberately unsupported by this candidate path because the connector carries no DC bias. Substituting an active antenna requires a new recorded decision and the u-blox bias/supervisor design, current/fault analysis and firmware configuration.

The 915 MHz LoRa transmitter is a documented interferer. At 915 MHz the MAX-M10S R05 manual lists a typical low-gain-mode immunity level of -17 dBm at RF_IN. Antenna isolation, filtering, and acceptable GNSS C/N0/fix degradation must be measured with LoRa TX, Wi-Fi/BLE, display, SD, and charging active.

## Placement, RF layout, and footprint

Follow integration manual R05 sections 4.2-4.4:

- place the module with its digital side toward the digital section and RF_IN toward the antenna/RF edge;
- keep the antenna connection short and keep at least 5 mm from RF components to other circuitry as directed by u-blox;
- use a solid ground reference, many ground vias, no unterminated ground stubs, and no noisy digital supply currents through the RF return area;
- ground below the module on the top and second layers and do not route signals below it on those layers;
- use a 50-ohm grounded coplanar waveguide with an uninterrupted second-layer ground reference; calculate geometry from the accepted production stackup rather than reusing a trace width;
- surround the RF route with ground vias and keep switch nodes, display/SD clocks, radios, batteries, and heat sources away from the GNSS area;
- avoid sudden temperature changes at the module oscillator and include the finished enclosure and both cells in RF/thermal validation.

The project footprint must be created from integration manual R05 Figure 30/Table 44 and Figure 31/Table 45, then independently overlaid against data-sheet R08 Figure 4:

| Item | Verified u-blox value |
| --- | --- |
| Body, typical | 10.1 x 9.7 x 2.5 mm |
| Pads | 18 castellated LCC contacts, 1.1 mm nominal module pitch |
| Footprint keepout | 11.10 x 10.10 mm in Figure 30 |
| Copper/solder-mask table | A 10.1, B 11.1, C 9.7, D 10.1, E 0.3, H 0.35, K 0.8, L 0.7, M 1.0, N 0.8 mm |
| Paste-mask table | C 9.7, E 0.3, H 0.35, K 0.8, L 0.7, M 0.9, N 1.4, P 0.6, R 0.5, S 7.9, T 12.5 mm |
| Stencil recommendation | 150 micrometers; T-shaped/equivalent paste extension to improve castellated wetting |

Do not derive pad centers or shapes from this prose alone; reproduce the manufacturer figures, including pin-1 orientation, corner-pad differences, de-paneling-tab clearance, copper/mask coincidence, and T-shaped paste. The paste geometry is a u-blox recommendation that must be adapted with the selected assembler. No matching generic KiCad footprint has been accepted.

## Release gates for KiCad and prototype validation

The exact identity, 18-pin symbol map, 3.3 V supply option, UART/PPS behavior, manufacturer land-pattern source, and layout constraints are now documented. Before the GNSS circuit or footprint is approved for a prototype:

1. accept or replace the proposed tied always-on 3.3 V VCC/V_IO arrangement, open V_BCKP/RESET_N/EXTINT choice and no-independent-power-gating policy; close rail capacitance, filtering and ramp behavior in the system PDN review;
2. accept or replace the proposed `FXP611.07.0092C` / `U.FL-R-SMT-1(60)` / `TPD1E0B04DPYR` passive RF package and its no-bias restriction;
3. reserve and mechanically verify the 40 x 40 mm enclosure area, 10 mm metal/ground clearance, 92 mm cable path, bend radius, strain relief and connector access;
4. create the project symbol and footprint, then independently compare every pin, dimension, mask layer, paste aperture, courtyard, height and pin-1 mark to R08/R05;
5. calculate the 50-ohm route from the confirmed production stackup and review the complete RF return path;
6. test cold/warm start, receiver identity, configuration acknowledgement/persistence, UART overflow, PPS/UTC validity, Airborne 4 g mode, antenna faults where applicable, and no-sky recovery;
7. measure C/N0, fix stability, spectrum, supply current, and recovery while LoRa TX, Wi-Fi/BLE, display refresh, SD writes and USB charging are active.

No high-altitude, RF, coexistence, or manufacturing result is claimed by this document.
