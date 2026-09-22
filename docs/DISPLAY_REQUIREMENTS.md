# Display interface specification

Locked product target: **2.8-inch IPS LCD, 320 x 240 in landscape or 240 x 320 in portrait, capacitive touch and both orientations**. Orient Display `AFY240320A1-2.8INTH-C1` remains the selected sample candidate; the exact part is not locked until sample and sourcing review.

Status: the exact manufacturer specification and candidate support circuit are now documented. The revision-J mode table verifies three-line, nine-bit SPI at `IM2/IM1/IM0 = 1/0/1` and four-line, eight-bit SPI at `1/1/0`; Rev A provisionally prefers the unambiguous three-line write-only path. Aratas/Omron `XF3M-4015-1B` and `XF3M-0615-1B`, TI `SN74AXC4T245PWR` plus `SN74LVC1G07DBVR`, and TI `TPS61169DCKR` are preferred candidates, not frozen parts. Connector footprints and schematic entry remain gated by the controlled-drawing power/FPC ambiguities, independent CAD review and labeled samples.

## Controlled sources

Reviewed through 2026-09-17:

- [Orient AFY240320A1-2.8INTH-C1 specification](https://www.orientdisplay.com/wp-content/uploads/2021/11/AFY240320A1-2.8INTH-C1.pdf), revision J dated 2021-07-20; sections 1-10 and drawing page 5.
- [Orient product page](https://orientdisplay.com/products/2-8-sunlight-readable-ips-240x320-900-nits-with-capacitive-touch-panel-rgb-mcu-spi-interface-new-ctp-ic/), exact SKU.
- [Omron XF3M/XF2M catalog](https://components.omron.com/us-en/system/files/2025-03/datasheet_pdf/G146-E1.pdf), catalog G146-E1-05 dated 2025-03; exact 0.5 mm dual-contact connector family and recommended FPC geometry.
- [TI SN74AXC4T245 data sheet](https://www.ti.com/lit/ds/symlink/sn74axc4t245.pdf), SCES877B revised 2024-04; and [TI SN74LVC1G07 data sheet](https://www.ti.com/lit/ds/symlink/sn74lvc1g07.pdf), SCES296AG revised 2025-10.
- [TI TPS61169 data sheet](https://www.ti.com/lit/ds/symlink/tps61169.pdf), SNVSA40B revised 2024-06.
- [TI TPS61169EVM guide](https://www.ti.com/lit/pdf/snvu455), SNVU455, for the manufacturer evaluation topology.
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
| Touch I/O | 1.6-3.6 V; module specification publishes I2C value `0x70` without stating whether it is seven-bit or an eight-bit write byte; top-left coordinate origin |
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
| 4-6 | IM0, IM1, IM2 | Revision-J straps: three-line, nine-bit SPI = `IM2/IM1/IM0 1/0/1`; four-line, eight-bit SPI = `1/1/0`. Rev A provisionally uses three-line `101` because its command/data bit is carried in-band |
| 7 | SDA | SPI data input |
| 8-11 | DOTCLK, DE, VSYNC, HSYNC | RGB signals; unused in the selected SPI mode only after the exact mode table defines required ties |
| 12 | VCC | TFT supply |
| 13 | RESET | TFT reset |
| 15-32 | DB17-DB0 | Parallel/RGB data bus; unused-pin treatment follows the exact selected SPI mode and controller specification |
| 33, 34 | RD, WR | Mode-dependent inputs. Four-line timing names `D/CX` without mapping it to an FPC contact; pin 34 is only labeled `WR`, so four-line remains blocked |
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

The exact Omron recommended board lands are available for later controlled CAD: signal lands are `0.30 x 1.30 mm` on `0.50 mm` pitch and hold-down lands are `1.50 x 2.20 mm`. For the 40-pin part, catalog dimensions A/B/C/D/E/F/G are `19.50/23.10/24.10/20.55/20.50/21.50/25.10 mm`; for the six-pin part they are `2.50/6.10/7.10/3.55/3.50/4.50/8.10 mm`. These values close manufacturer-land availability, but do not override the unresolved Orient tail tolerance or authorize a footprint yet.

Do not create or assign either connector footprint until the exact manufacturer land pattern is independently overlaid, the controlled Orient drawing is obtained or its ambiguity is dispositioned, and two labeled display samples pass insertion/retention/continuity checks.

## TFT logic translation proposal

Use a display-only branch; the shared 3.3 V SPI trunk to microSD and SX1262 remains unshifted.

- Preferred bus translator: TI `SN74AXC4T245PWR`, TSSOP-16. Connect pin 1 VCCA to `3V3_MAIN`, pin 16 VCCB to `1V8_LOGIC`, and hold both direction inputs (pins 2 and 3) high for A-to-B. Use channels pins 4-to-13, 5-to-12 and 6-to-11 for SCLK, SDA and CS. Give unused A4 pin 7 a defined level if B4 pin 10 is unused.
- The approved DSP-02 application below uses **10 kohm pull-downs on both OE inputs** (OE high tri-states this exact AXC device). The earlier pull-up proposal was superseded. Place one local bypass capacitor at each supply pin pair and keep translated traces short; validate startup and shutdown with the exact display samples.
- Preferred reset translator: TI `SN74LVC1G07DBVR`: pin 2 input from the 3.3 V reset control, pin 3 ground, pin 4 open-drain TFT reset, pin 5 `1V8_LOGIC`, pin 1 NC. An input pull-down holds reset asserted at boot and an output pull-up to `1V8_LOGIC` prevents a 3.3 V high level at the TFT reset pin.
- The AXC device supports either rail from 0.65 to 3.6 V, Ioff partial-power-down protection, VCC isolation and supply sequencing in either order. The LVC buffer supports 1.65-5.5 V operation, overvoltage-tolerant input and Ioff. These properties reduce back-power risk but do not replace a measured rail/reset sequence.

The module labels SDA as I/O. The fixed direction above intentionally provides write-only display traffic. In the preferred three-line mode, the ninth serial bit carries command/data state, so the unexplained four-line `D/CX` contact is avoided. The published 66 ns minimum serial write cycle limits the panel clock to about 15.15 MHz. If register/pixel readback is required, the design must add controlled turnaround and prove there is no bus contention. Four-line SPI remains blocked until Orient maps `D/CX` to an exact FPC contact.

Revision J still contains a supply-domain contradiction: timing/sequencing pages refer to separate `VDDI` and `VDD`, the DC table names `VDDIO = 1.8 V`, and the FPC exposes only one TFT `VCC` contact. Obtain a controlled electrical clarification before freezing TFT power, even though the serial strap table itself is now readable.

`1V8_LOGIC` is supplied by the already proposed `TPS7A2018PDBVR`; this display work does not replace that regulator. The rail load calculation remains open because Orient does not publish a VDDIO current maximum.

## Backlight driver proposal

Preferred candidate: TI `TPS61169DCKR`, an active SC70-5 boost WLED driver with 2.7-5.5 V input, 38 V output capability, 204 mV feedback reference, 1.2 MHz switching, soft start, open-LED protection, UVLO, PWM control and thermal protection. Feed it from `3V3_MAIN`, never directly from the 6.0-8.4 V protected 2S bus.

Application starting point from the TI topology:

1. `3V3_MAIN` through a 10 uH `LPS4018-103MRC` candidate to SW. The older `-103ML` suffix is not the current ordering code. A pessimistic 2.7 V input/6.62 V output calculation gives roughly 0.44-0.46 A peak; final saturation current, DCR, temperature and sourcing remain gated.
2. Use a Schottky from SW to LEDA. The EVM's 40 V `NSR0240V2T1G` leaves only 1 V above the published 39 V maximum OVP corner, so select an exact 60 V-class part with adequate repetitive peak current before freeze.
3. Place at least 1 uF ceramic at VIN; 4.7 uF local bulk is a reasonable prototype start. Use 1-4.7 uF **effective** output capacitance with a 50 V rating because an open LED can raise the node toward the 36-39 V OVP range. Connect LEDK to FB and place RSET from FB to ground at the IC.
4. Start with `RSET = 2.21 ohm, 1%, at least 0.1 W`, which gives about 92.3 mA at the typical 204 mV reference. Using 188-220 mV and resistor tolerance gives approximately 84.2-100.5 mA. Verify sample current, luminance and temperature before freeze.
5. Drive CTRL from `LCD_BL_PWM`; the IC already has a 300 kOhm internal pull-down, while an external pull-down may reinforce reset behavior. TI recommends 5-100 kHz PWM; use 20 kHz as the initial bring-up setting.

At 0.60 W output, estimated input current from 3.3 V is about 202 mA at TI's 90% peak efficiency or 214 mA at an 85% planning efficiency. Reserve at least 250 mA of `3V3_MAIN` peak budget pending measured efficiency and transient data. Because the panel's minimum 5.8 V LED forward voltage exceeds the 3.3 V driver input, the TPS61169 shutdown-path condition for keeping the LEDs off is met on paper; verify leakage on both samples.

Keep the SW/inductor/diode loop short, place CIN/COUT and RSET at the IC, separate signal and power return until the IC ground point, and locate the boost stage away from GNSS, LoRa, ADS-B, the magnetometer and their antennas. Measure conducted/radiated noise at full brightness and PWM corners. Open LED, LED short, CTRL stuck high/low and hot-enclosure tests remain mandatory.

## Host and sequencing plan

SPI remains the selected first interface because it fits the GPIO budget. Rev A provisionally uses write-only three-line, nine-bit SPI with `IM2/IM1/IM0 = 1/0/1` and a panel clock no faster than 15 MHz. Sample validation, unused-pin ties and the TFT supply clarification remain gates. RGB or 8080 MCU mode requires a new documented GPIO/bandwidth decision.

Keep the TFT translator disabled and TFT reset asserted while `3V3_MAIN`, TFT VCC and `1V8_LOGIC` rise; release reset and then enable bus traffic only after the official timing is satisfied. Before shutting down a display rail, stop SPI traffic, disable the translator and assert reset. Touch RESET needs its own 3.3 V-safe implementation: revision J requires it low before power-on/off, held low for at least 5 ms after rails become valid, and asserted at least 100 us before power-off. Do not rely on an undefined expander default.

At RGB565, a full 320 x 240 frame is 153,600 bytes. Thirty full frames/s requires 4.608 MB/s, or 36.864 Mbit/s of payload before command overhead and bus gaps. Prefer partial updates and measure contention with microSD and SX1262 on the shared SPI host.

Firmware must separate panel driver, touch driver, orientation transform, backlight policy and UI. Test all four corners in both orientations, sleep/wake, display-off logging and brightness profiles.

## Display support circuit — exact values (DSP-02, 2026-09-22)

Facts re-verified in the retrieved TI documents this session: `SN74AXC4T245` SCES877B (April 2024) and `SN74LVC1G07` SCES296AG (October 2025). This section completes the DSP-02 engineering deliverable; **final acceptance remains gated by the controlled-drawing clarification (DSP-01/EXT-01) and two-sample validation as recorded in the release-gate list.**

### SN74AXC4T245PWR (TSSOP-16) — 3.3 V-to-1.8 V SPI branch

- **Pin-level assignment (SCES877B pin table):** VCCA pin 1 = `3V3_MAIN`; VCCB pin 16 = `1V8_LOGIC`; 1DIR pin 2 = high (tie to `3V3_MAIN`); 2DIR pin 3 = high (tie to `3V3_MAIN`); 1OE pin 15 = host-controlled enable net (see policy below); 2OE pin 14 = host-controlled enable net; ports: 1A1 pin 4 -> 1B1 pin 13 (SCLK), 1A2 pin 5 -> 1B2 pin 12 (SDA), 2A1 pin 6 -> 2B1 pin 11 (CS); 2A2 pin 7 is the unused A-side input and **must be tied to GND** per the TI rule that all unused inputs sit at VCC or GND (section 5.4 note) — its partner 2B2 pin 10 then idles and stays unconnected.
- **DIR polarity correction:** the previous proposal text said "hold both direction inputs high for A-to-B"; this is confirmed correct (DIR high = A->B, section 7.1) and is now pinned to the datasheet section.
- **OE polarity fact:** **OE high = outputs in tri-state** for this family (section 7.1: "When OE is set to high, both Ax and Bx pins are in the high-impedance state"). The safe power-up policy therefore is **10 kohm pull-downs from both OE pins to GND** — the branch wakes enabled, which is safe here because the display is write-only and reset-held; a host-enable option may raise OE later for a controlled bus release. This supersedes the earlier "pull each active-low OE to VCCA" phrasing in the proposal above (that phrasing belonged to a different device family convention and would have left the branch permanently disabled).
- **Static load:** ICCA <= 12 uA, ICCB <= 16 uA max at 3.6 V, IO = 0 (section 5) — inside the PWR-04 `1V8_LOGIC`/`3V3_MAIN` allowances; no inventory change.
- **Bypass:** 100 nF at VCCA pin 1 and at VCCB pin 16 (device class; already the recorded proposal).

### SN74LVC1G07DBVR (SOT-23-5) — open-drain display reset

- **Pin-level assignment (DBV):** pin 2 = input from the 3.3 V reset control (TCA9535 `LCD_RST_N` through the expander-side network); pin 3 = GND; pin 4 = open-drain output to TFT RESET with **10 kohm pull-up to `1V8_LOGIC`** (not `3V3_MAIN` — the reset pin is a 1.8 V-domain input); pin 5 = VCC = `1V8_LOGIC`; pin 1 = NC.
- **Polarity fact (TI SCES296AG Rev AG, section 7.4 function table):** input **low** makes the open-drain output **low** and asserts active-low TFT RESET; input **high** leaves the output high impedance and its 10 kohm display-side pull-up releases RESET. A **100 kohm input pull-down (3.3 V control domain)** therefore holds the display in reset while the expander is unconfigured. The expander must drive its control output high to release reset; verify its push-pull configuration and the TFT timing on samples.
- **Cross-reference to DIG-03:** expander P06 drives the LVC1G07 **input** in the `3V3_MAIN` domain, with a 100 kohm input pull-down; firmware must configure it push-pull high to release reset. The `1V8_LOGIC` pull-up is on the LVC1G07 **output** at the display connector. No rail-crossing pull exists. TI SCES296AG Rev AG section 7.4 confirms low input = low output, high input = open-drain high impedance.
- **IOL margin:** the LVC1G07 sinks 8 mA at 0.3 V class (section 6) against a 10 kohm/1.8 V pull-up demand of 0.18 mA — non-binding.
- **TFT RESET pin rule retained:** never add a capacitor from TFT RESET to ground (module rule); the reset waveform belongs to the display sample validation.

### Startup/shutdown sequence (values from the standing plan, now resistor-backed)

1. Rails rise: `3V3_MAIN` (buck soft-start) -> `1V8_LOGIC` tracks up. AXC OEs held low by pull-downs = branch **enabled** but the ESP32 has not clocked anything; LVC1G07 input pull-down asserts TFT RESET low through the sink path.
2. ESP32 boots and configures TCA9535 P06 as a push-pull high output; LVC1G07 input rises, its output becomes high impedance and the TFT-side pull-up releases RESET after the module's reset-low requirement is satisfied (>= 1 ms low per the module record; sample validation remains required).
3. SPI traffic begins at <= 15 MHz panel-clock bound; IM straps `101` selected on the FPC (hardware straps, not firmware).
4. Shutdown: stop SPI traffic -> drive P06 low to assert TFT RESET -> rails fall with the input pull-down maintaining RESET while the translator output is enabled. Touch reset timing (5 ms post-rails, 100 us pre-power-off) stays with the touch branch and its expander row.

### DSP-02 closure boundary

Delivered: pin-complete translator and reset applications with datasheet-pinned polarities and resistor values, static-load confirmation against PWR-04, corrected OE/DIR conventions, and the integrated startup/shutdown sequence. **Deliberately open (final acceptance):** controlled-drawing clarification and sample validation (DSP-01/EXT-01/release gates 1-2), unused-pin ties for the wider FPC (gate 3), backlight sample measurements (gate 4), and footprints (gate 6/DIG-04 deferral list).

## Sourcing snapshot and remaining gates

Checked 2026-09-14: the exact Orient store page listed 50 units at USD 35.36 each, USD 31.39 at 25-49 and USD 27.42 at 50+. DigiKey listed zero immediately available, one expected 2026-10-19, USD 31.55 at quantity one and an eight-week manufacturer lead time. DigiKey also listed 9,902 `XF3M-4015-1B` at USD 2.93 each, 975 `XF3M-0615-1B` at USD 1.23 cut-tape, 16,834 `SN74AXC4T245PWR` at USD 1.17, 165,134 `SN74LVC1G07DBVR` at USD 0.14 and 2,019 `TPS61169DCKR` at USD 1.18. These are dated prototype snapshots from an authorized distributor; recheck before purchase and confirm PCBA-factory availability separately.

Before connector or footprint freeze:

1. obtain a controlled/current Orient mechanical drawing that resolves the revision-J/revision-G mismatch and ambiguous CTP terminal width/contact side;
2. obtain at least two labeled C1 samples and confirm controller identification, both tail geometries, contact engagement, retention, continuity and bend/actuator clearances with the proposed XF3M connectors;
3. review the `SN74AXC4T245PWR` plus `SN74LVC1G07DBVR` circuit, exact 1.8 V/TFT/touch rails, resets and back-power behavior; validate the provisional write-only three-line `101` mode on both samples and select unused-pin ties;
4. prototype `TPS61169DCKR` from 3.3 V with the proposed 2.21 ohm limit; measure current, luminance, leakage, efficiency, temperature, PWM behavior, startup and open/short faults;
5. run address, touch, orientation, shared-bus, sleep/wake and RF-coexistence tests;
6. create connector and IC footprints only from exact manufacturer drawings and independently overlay/review them before release.
