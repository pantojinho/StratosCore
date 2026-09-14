# Display interface specification

Locked product target: **2.8-inch IPS LCD, 320 x 240 in landscape or 240 x 320 in portrait, capacitive touch and both orientations**. Orient Display `AFY240320A1-2.8INTH-C1` remains the selected sample candidate; the exact part is not locked until sample and sourcing review.

Status: the exact manufacturer specification and candidate support circuit are now documented. Aratas/Omron `XF3M-4015-1B` and `XF3M-0615-1B`, TI `SN74AXC4T245PWR` plus `SN74LVC1G07DBVR`, and TI `TPS61169DCKR` are preferred candidates, not frozen parts. Connector footprints and schematic entry remain gated by the drawing ambiguity, exact SPI-mode confirmation, independent CAD review and labeled samples.

## Controlled sources

Reviewed 2026-09-14:

- [Orient AFY240320A1-2.8INTH-C1 specification](https://www.orientdisplay.com/wp-content/uploads/2021/11/AFY240320A1-2.8INTH-C1.pdf), revision J dated 2021-07-20; sections 1-10 and drawing page 5.
- [Orient product page](https://orientdisplay.com/products/2-8-sunlight-readable-ips-240x320-900-nits-with-capacitive-touch-panel-rgb-mcu-spi-interface-new-ctp-ic/), exact SKU.
- [Omron XF3M/XF2M catalog](https://components.omron.com/us-en/system/files/2025-03/datasheet_pdf/G146-E1.pdf), catalog G146-E1-05 dated 2025-03; exact 0.5 mm dual-contact connector family and recommended FPC geometry.
- [TI SN74AXC4T245 data sheet](https://www.ti.com/lit/ds/symlink/sn74axc4t245.pdf), SCES877B revised 2024-04; and [TI SN74LVC1G07 data sheet](https://www.ti.com/lit/ds/symlink/sn74lvc1g07.pdf), SCES296AG revised 2025-10.
- [TI TPS61169 data sheet](https://www.ti.com/lit/ds/symlink/tps61169.pdf), SNVSA40B revised 2024-06.
- [DigiKey exact-part listing](https://www.digikey.com/en/products/detail/orient-display/AFY240320A1-2-8INTH-C1/22531939), checked 2026-09-14 for dated price/availability only.
- DigiKey dated sourcing pages: [XF3M-4015-1B](https://www.digikey.com/en/products/detail/omron-electronics-inc-emc-div/XF3M-4015-1B/4331809), [XF3M-0615-1B](https://www.digikey.com/en/products/detail/aratas-formerly-omron-components/XF3M-0615-1B/4840775), [SN74AXC4T245PWR](https://www.digikey.com/en/products/detail/texas-instruments/SN74AXC4T245PWR/10060449), [SN74LVC1G07DBVR](https://www.digikey.com/en/products/detail/texas-instruments/SN74LVC1G07DBVR/377455) and [TPS61169DCKR](https://www.digikey.com/en/products/detail/texas-instruments/TPS61169DCKR/5048578).

The specification identifies ST7789VI or compatible for the TFT and ST1633I for touch. A compatible-controller substitution by the display manufacturer could change initialization or behavior without changing the module MPN; incoming inspection and sample identification remain required.

## Verified module data

| Item | Manufacturer specification |
| --- | --- |
| Module / active area | 50.45 x 69.90 x 4.22 mm; active area 43.20 x 57.60 mm; 28.1 g |
| Optical | IPS, normally black, transmissive, anti-glare, 900 cd/m2 typical, 600 cd/m2 minimum |
| Environment | -20 to +70 °C operation; -30 to +80 °C storage; no condensation |
| TFT supply | 2.4-3.6 V, 2.8 V typical; 9 mA typical in the published condition |
| TFT logic | VDDIO specified at 1.8 V; VIH >= 0.7 x VDDIO |
| Touch supply | 2.8-3.6 V, 3.3 V typical; 16.1 mA typical, 24 mA maximum |
| Touch I/O | 1.6-3.6 V; I2C address `0x70` in the module specification; top-left coordinate origin |
| Backlight | Specification states 5.8-6.4 V, 100 mA typical, 125 mA absolute maximum and 0.60 W typical; it describes five LEDs in parallel |
| Power | 0.625 W module figure in the general table; backlight dominates and must be measured at the selected brightness |

The 1.8 V TFT logic requirement is incompatible with direct 3.3 V ESP32 drive. The SPI path needs a reviewed 3.3-to-1.8 V translation strategy and appropriate 1.8 V rail. Touch can use 3.3 V supply/I/O within the published range, subject to the separate ST1633I specification and sample confirmation.

The backlight description combines a 5.8-6.4 V forward range with a five-parallel-LED statement. Treat LEDA/LEDK as one two-terminal 100 mA load; do not infer the number of dies within each published LED element. Measure voltage/current and polarity on each labeled sample before committing the driver current.

## Exact module interfaces

The TFT interface table defines a 40-contact FPC:

| Pins | Names | Verified function / Rev A handling |
| --- | --- | --- |
| 1, 2 | LEDK, LEDA | Backlight cathode/anode; use reviewed current driver |
| 3, 14 | GND | Ground |
| 4-6 | IM0, IM1, IM2 | Interface-mode straps; exact SPI strap table must be checked visually against revision J before schematic entry |
| 7 | SDA | SPI data input |
| 8-11 | DOTCLK, DE, VSYNC, HSYNC | RGB signals; unused in the selected SPI mode only after the exact mode table defines required ties |
| 12 | VCC | TFT supply |
| 13 | RESET | TFT reset |
| 15-32 | DB17-DB0 | Parallel/RGB data bus; unused-pin treatment follows the exact selected SPI mode and controller specification |
| 33, 34 | RD, WR | Mode-dependent inputs; revision J says tie to VCC or ground for RGB but does not by itself release SPI strapping |
| 35 | RS | Serial-interface clock in the module table |
| 36 | CS | Active-low chip select |
| 37-40 | XR, YD, XL, YU | Marked NC for this capacitive-touch variant |

The capacitive-touch interface is a separate six-contact FPC:

| Pin | Name | Function |
| ---: | --- | --- |
| 1 | RESET | Active-low reset |
| 2 | VDD | Touch supply |
| 3 | GND | Ground |
| 4 | INT | State-change interrupt |
| 5 | SCL | I2C clock |
| 6 | SDA | I2C data |

## FPC geometry and connector candidates

The official specification is revision J, but its embedded page-5 external-dimensions title block says revision G and its latest visible internal drawing entry is G dated 2021-01-19. The revision record says J dated 2021-07-20 updated page 5. This mismatch prevents treating the raster drawing as a controlled release; request a current native/controlled drawing from Orient before footprint freeze.

Values transcribed from page 5:

| Tail | Contacts | Pitch/span | Contact / terminal geometry | Thickness | Candidate consequence |
| --- | ---: | --- | --- | --- | --- |
| TFT | 40 | 0.50 mm; `0.5 x (40-1) = 19.50 +/- 0.05 mm` | Contact width `0.35 +/- 0.05 mm`; tail width `20.50 +/- 0.20 mm`; exposed-contact length `3.50 +/- 0.30 mm`; end setback `0.50 +/- 0.10 mm` | `0.30 +/- 0.03 mm` | Pitch, nominal tail width and thickness match `XF3M-4015-1B`; sample insertion and contact engagement still required |
| CTP | 6 | 0.50 mm; `0.5 x (6-1) = 2.50 +/- 0.05 mm` | Contact width `0.35 +/- 0.05 mm`; exposed-contact length `3.50 +/- 0.30 mm`; end setback `0.50 +/- 0.10 mm`; one nearby `4.70 +/- 0.50 mm` callout is not unambiguously attributable to the terminal width in the raster drawing | `0.30 +/- 0.03 mm` | Pitch and thickness match `XF3M-0615-1B`; exact tip width and insertion clearance require Orient confirmation/sample measurement |

The drawing explicitly identifies a contact side for the TFT tail, but the CTP tail contact-side callout is not independently clear. Preferred connector candidates are therefore the dual-sided-contact, 0.5 mm-pitch, 0.30 mm FPC/FFC Aratas/Omron `XF3M-4015-1B` and `XF3M-0615-1B`. The current manufacturer catalog lists both exact pin counts, right-angle rotary backlock construction, 2.0 mm installed height, 0.5 A rating, gold-flash contacts, 20 mating cycles and -30 to +85 degC operation. Dual contacts remove the electrical top/bottom-contact ambiguity, but they do not prove tip width, stiffener, insertion depth, actuator access or strain-relief fit.

The Omron recommended FPC drawing calls for at least 3.5 mm in the terminal region, while the Orient nominal exposed length is 3.50 mm with a -0.30 mm tolerance. Resolve that tolerance boundary with Orient before connector release. Secure both tails against vibration and reserve actuator-operating space as required by the connector manufacturer.

Do not create or assign either connector footprint until the exact manufacturer land pattern is independently overlaid, the controlled Orient drawing is obtained or its ambiguity is dispositioned, and two labeled display samples pass insertion/retention/continuity checks.

## TFT logic translation proposal

Use a display-only branch; the shared 3.3 V SPI trunk to microSD and SX1262 remains unshifted.

- Preferred bus translator: TI `SN74AXC4T245PWR`, TSSOP-16. Connect VCCA to `3V3_MAIN`, VCCB to the existing `1V8_LOGIC` candidate rail, and fix both direction groups A-to-B. Allocate SCLK, SDA/MOSI, CS and D/C if four-line SPI is confirmed. In three-line SPI, the fourth channel is spare.
- Pull each active-low OE to VCCA so outputs remain high impedance during power-up/down, as TI requires. A host-controlled pull-down may enable the translator only after `1V8_LOGIC` and TFT VCC are valid. Place one local bypass capacitor at each supply pin pair and keep translated traces short.
- Preferred reset translator: TI `SN74LVC1G07DBVR` powered from `1V8_LOGIC`, with its 5.5 V-tolerant input driven from the 3.3 V reset control, an input pull-down to hold reset asserted at boot, and an output pull-up to `1V8_LOGIC`. This open-drain path prevents a 3.3 V high level at the TFT reset pin and keeps reset asserted while 1.8 V is present and the host is not driving.
- The AXC device supports either rail from 0.65 to 3.6 V, Ioff partial-power-down protection, VCC isolation and supply sequencing in either order. The LVC buffer supports 1.65-5.5 V operation, overvoltage-tolerant input and Ioff. These properties reduce back-power risk but do not replace a measured rail/reset sequence.

The module labels SDA as I/O. The fixed direction above intentionally provides write-only display traffic. If register/pixel readback is required, the design must add controlled turnaround and prove there is no bus contention; do not change direction dynamically without a timing review. Exact IM0-IM2 straps, D/C pin mapping and unused inputs remain blocked because the module exposes no IM3 pin and its interface table is ambiguous about `WR`/`RS` behavior in four-line SPI. Obtain Orient confirmation or validate a manufacturer-provided sample interface board before schematic freeze.

`1V8_LOGIC` is supplied by the already proposed `TPS7A2018PDBVR`; this display work does not replace that regulator. The rail load calculation remains open because Orient does not publish a VDDIO current maximum.

## Backlight driver proposal

Preferred candidate: TI `TPS61169DCKR`, an active SC70-5 boost WLED driver with 2.7-5.5 V input, 38 V output capability, 204 mV feedback reference, 1.2 MHz switching, soft start, open-LED protection, UVLO, PWM control and thermal protection. Feed it from `3V3_MAIN`, never directly from the 6.0-8.4 V protected 2S bus.

Application starting point from the TI topology:

1. `3V3_MAIN` through a 10 uH inductor to SW; the TI-listed `LPS4018-103ML` is a candidate with 1.3 A saturation rating. Final inductor MPN remains gated by peak-current, DCR, temperature and PCBA sourcing review.
2. Use a low-capacitance Schottky from SW to LEDA with reverse rating above the driver's open-LED protection voltage; TI recommends `NSR0240`. Confirm its exact suffix/package and stock before BOM freeze.
3. Place 1 uF ceramic at VIN and 1-4.7 uF ceramic from LEDA/output to ground, with voltage derating checked. Connect LEDK to FB and place the current-set resistor from FB to ground next to the IC.
4. Start with `RSET = 2.21 ohm, 1%`, which gives about 92.3 mA at the typical 204 mV reference. Using the published 188-220 mV feedback range and resistor tolerance gives approximately 84.2-100.5 mA, below the panel's 125 mA absolute maximum and near/below its 100 mA life-test current. Verify actual sample current, luminance and temperature before freeze.
5. Drive CTRL from `LCD_BL_PWM` with a pull-down that guarantees off at reset. TI recommends 5-100 kHz PWM; use 20 kHz as the initial bring-up setting. A constant high CTRL requests the set current.

At 0.60 W output, estimated input current from 3.3 V is about 202 mA at TI's 90% peak efficiency or 214 mA at an 85% planning efficiency. Reserve at least 250 mA of `3V3_MAIN` peak budget pending measured efficiency and transient data. Because the panel's minimum 5.8 V LED forward voltage exceeds the 3.3 V driver input, the TPS61169 shutdown-path condition for keeping the LEDs off is met on paper; verify leakage on both samples.

Keep the SW/inductor/diode loop short, place CIN/COUT and RSET at the IC, separate signal and power return until the IC ground point, and locate the boost stage away from GNSS, LoRa, ADS-B, the magnetometer and their antennas. Measure conducted/radiated noise at full brightness and PWM corners. Open LED, LED short, CTRL stuck high/low and hot-enclosure tests remain mandatory.

## Host and sequencing plan

SPI remains the selected first interface because it fits the GPIO budget. The published module supports 3-line and 4-line serial timing, but the exact Rev A mode, IM0-IM2 straps, command/data signaling and unused-pin ties remain a review item. RGB or 8080 MCU mode requires a new documented GPIO/bandwidth decision.

Keep the TFT translator disabled and TFT reset asserted while `3V3_MAIN`, TFT VCC and `1V8_LOGIC` rise; release reset and then enable bus traffic only after the official timing is satisfied. Before shutting down a display rail, stop SPI traffic, disable the translator and assert reset. For the touch controller, revision J states RESET must be low before power-on and power-off and must remain low for at least 5 ms after its supplies reach normal voltage. Its 3.3 V reset implementation must guarantee that behavior without relying on an undefined expander default. Confirm reset polarity/timing for both controllers against their exact controller specifications and samples.

At RGB565, a full 320 x 240 frame is 153,600 bytes. Thirty full frames/s requires 4.608 MB/s, or 36.864 Mbit/s of payload before command overhead and bus gaps. Prefer partial updates and measure contention with microSD and SX1262 on the shared SPI host.

Firmware must separate panel driver, touch driver, orientation transform, backlight policy and UI. Test all four corners in both orientations, sleep/wake, display-off logging and brightness profiles.

## Sourcing snapshot and remaining gates

Checked 2026-09-14: the exact Orient store page listed 50 units at USD 35.36 each, USD 31.39 at 25-49 and USD 27.42 at 50+. DigiKey listed zero immediately available, one expected 2026-10-19, USD 31.55 at quantity one and an eight-week manufacturer lead time. DigiKey also listed 9,902 `XF3M-4015-1B` at USD 2.93 each, 975 `XF3M-0615-1B` at USD 1.23 cut-tape, 16,834 `SN74AXC4T245PWR` at USD 1.17, 165,134 `SN74LVC1G07DBVR` at USD 0.14 and 2,019 `TPS61169DCKR` at USD 1.18. These are dated prototype snapshots from an authorized distributor; recheck before purchase and confirm PCBA-factory availability separately.

Before connector or footprint freeze:

1. obtain a controlled/current Orient mechanical drawing that resolves the revision-J/revision-G mismatch and ambiguous CTP terminal width/contact side;
2. obtain at least two labeled C1 samples and confirm controller identification, both tail geometries, contact engagement, retention, continuity and bend/actuator clearances with the proposed XF3M connectors;
3. review the `SN74AXC4T245PWR` plus `SN74LVC1G07DBVR` circuit, exact 1.8 V/TFT/touch rails, resets and back-power behavior; confirm whether write-only three-line or four-line SPI is supported and select exact straps/unused-pin ties;
4. prototype `TPS61169DCKR` from 3.3 V with the proposed 2.21 ohm limit; measure current, luminance, leakage, efficiency, temperature, PWM behavior, startup and open/short faults;
5. run address, touch, orientation, shared-bus, sleep/wake and RF-coexistence tests;
6. create connector and IC footprints only from exact manufacturer drawings and independently overlay/review them before release.
