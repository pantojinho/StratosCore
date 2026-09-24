# ESP32-S3, USB-C and button audit — 2026-09-23

Scope: the Claude comparison candidate after `6fa29cb`; re-checked after the GND/buck re-layout and U7 swap (U2 ESD ground is now connected, USB_DP moved 0.45 mm, no change to the ESP32 connections). Question: will the board work with the ESP32-S3-WROOM-1-N16R8, are all its connections correct, are the positions correct, and are the USB-C receptacle and the two buttons on the correct side? Correspondence checks (ERC, DRC parity, `tools/reconcile.py`) are necessary, not sufficient; every item below was traced to the exact manufacturer source.

Sources: Espressif ESP32-S3-WROOM-1/1U datasheet **v1.8** (Table 3-1 pin definitions, §4.2 VDD_SPI, note on GPIO47/48); Espressif ESP32-S3 Hardware Design Guidelines, "General Principles of PCB Layout for Modules" and USB section (docs.espressif.com, retrieved 2026-09-23); GCT USB4105 drawing Rev B4 (2023-12-18); Alps Alpine SKSC series catalogue (update 2510), Drawing No. 1; u-blox MAX-M10S data sheet (pin names as captured in the reviewed symbol); RP2040 QFN-56 pin order; project `docs/INTERFACE_GPIO_MAP.md`, `docs/CONNECTOR_ARCHITECTURE.md`, `docs/MECHANICAL_RF_FLOORPLAN.md`, `docs/PRODUCT_REQUIREMENTS.md` PR03.

## 1. ESP32-S3 module connections — **all 41 pads correct**

Every module pad was compared with Espressif Table 3-1 and the project GPIO map:

| Module pin (GPIO) | Board net | Far end (pin function) | Result |
| --- | --- | --- | --- |
| 1, 40, 41 EPAD | GND | plane | OK |
| 2 3V3 | 3V3_MAIN | C41 10 uF at 2.35 mm, C42 100 nF at 5.4 mm, C43 100 nF | OK (move 100 nF closer; Espressif puts the small cap nearest the pin) |
| 3 EN | ESP_EN | R40 10 k to 3V3, C40 1 uF to GND, TP11 | OK (Espressif RC); no reset button — recovery is BOOT + power cycle or USB auto-download |
| 4 IO4 | TOUCH_INT | J4.4 | OK |
| 5 IO5 / 6 IO6 | SX_DIO1 / SX_BUSY | U40 DIO1(13) / BUSY(14) | OK |
| 7 IO7 | LCD_BL_PWM | U16 TPS61169 CTRL(4) | OK |
| 8 IO15 / 9 IO16 | PDM_CLK / PDM_DATA | U24 A1(5) in / A2Y(4) out | OK (directions per TXU0202 Table 6-1) |
| 10 IO17 / 11 IO18 | GNSS_TX / GNSS_RX | U17 RXD(3) / TXD(2) | OK (crossed) |
| 12 IO8 | LCD_AUX | R55 | OK (reserved) |
| 13 IO19 / 14 IO20 | USB_DN / USB_DP | J1 A7+B7 D- / A6+B6 D+, U2 ESD | OK, not swapped |
| 15 IO3, 16 IO46, 26 IO45 | no connect | — | OK: strapping pins left at their internal defaults (GPIO45 low = VDD_SPI per eFuse; GPIO46 low as required for download mode) |
| 17 IO9, 18 IO10, 22 IO14 | SX_NSS, LCD_CS, SD_CS | U40 NSS(19), U14 translator, J8 DAT3/CD | OK |
| 19 IO11 / 20 IO12 / 21 IO13 | SPI_MOSI / SCLK / MISO | U40, J8, U14, J2 | OK |
| 23 IO21 | GNSS_PPS | U17 TIMEPULSE(4) | OK |
| 24 IO47 / 25 IO48 | IMU_INT1 / BUTTON_2 | U30 INT1(4) / SW2 | OK — N16R8 has 3.3 V VDD_SPI, so GPIO47/48 are 3.3 V (the 1.8 V note applies only to R16V parts) |
| 27 IO0 | BUTTON_1 | SW1, R41 10 k pull-up | OK — GPIO0 high at reset = SPI boot; holding SW1 at reset = ROM download (intended dual use) |
| 28-30 IO35-37 | no connect | — | OK (octal PSRAM) |
| 31 IO38 / 32 IO39 / 33 IO40 | EXP_IRQ / EXP_UART_TX / EXP_UART_RX | J2 pins 12 / 10 / 11 | OK per `CONNECTOR_ARCHITECTURE.md` |
| 34 IO41 / 35 IO42 | RP_UART_RTS / RP_UART_CTS | RP2040 GPIO2 (UART0 CTS) / GPIO3 (UART0 RTS) | OK (crossed) |
| 36 RXD0 GPIO44 / 37 TXD0 GPIO43 | RP_UART_RX / RP_UART_TX | RP2040 GPIO0 (UART0 TX) / GPIO1 (UART0 RX) | OK (crossed). Note: the ESP32 ROM prints its boot log on GPIO43; RP2040 firmware must ignore it or the log must be silenced by eFuse/config |
| 38 IO2 / 39 IO1 | I2C_SCL / I2C_SDA | all I2C devices, J2, J4 | OK |

Supply capacity: `3V3_MAIN` is the 3 A TPS62130A rail (PWR-04 inventory ~1.41 A worst case). Correspondence: ERC has no ESP32-related finding; DRC parity 0; `reconcile.py` 970 pins, 0 mismatches.

**Verdict:** electrically the ESP32 is wired correctly and will boot and enumerate over USB, provided the 3V3 rail comes up. The 3V3 rail depends on the 2S pack/protection placeholder (O05), so nothing may be powered from cells until that review.

## 2. ESP32 position and antenna — **correct edge, but two deviations from Espressif**

- The antenna is at the left board edge (module outline x 0.3-6.3 mm) and the KiCad antenna rule area holds no copper on any layer. This matches the floorplan EDGE zone.
- **Deviation A — board material.** Espressif: if the antenna cannot extend beyond the board edge, "cut off the base board on both sides of the antenna and below it". The candidate keeps FR-4 under the antenna and below it, only clearing the copper. Recommendation: rout a notch x 0-6.3 mm, y 0-~20 mm (module pads start at x 7.79, so the module stays supported), or rotate/shift the module so the antenna overhangs the outline. This is an outline change affecting the fit dummy (owner/mechanical decision).
- **Deviation B — display projection.** The display envelope DS1 (x 4.78-55.23, y 13.6-83.5, 5 mm above the PCB) overlaps the antenna footprint by about 1.5 x 5.7 mm (x 4.78-6.3, y 13.6-19.3). `MECHANICAL_RF_FLOORPLAN.md` requires the antenna outside the display metal projection, and Espressif recommends 15 mm clearance in all directions inside the housing. **The current position violates the project rule.** The fix depends on the controlled Orient drawing (display outline and FPC exits), so it stays a display/mechanical ENGINEERING_RETURN. Options: shift the display at least 1.6 mm toward +x (the board has 4.77 mm of margin on the right), or move the module so the antenna overhangs the top-left corner.
- ESP32 USB: the pair is about 75.7 mm (D+) / 79.4 mm (D-), 3.7 mm skew after the re-layout (4.1 mm before), 2/3 vias, 0.16 mm uncoupled tracks. The S3 USB is full-speed (12 Mbit/s), so this works functionally, but it misses Espressif's layout rules: routed as a differential pair, equal length, and "reserve space for resistors and capacitors on the USB traces close to the chip". Recommendation: add 0-ohm series and DNP shunt footprints at U1 and re-route the pair coupled when the USB corner is re-laid out.

## 3. USB-C (J1) — **correct side; 0.3 mm too far inboard; enclosure wall too thick at the plug**

- Position: bottom edge, x = 8 mm, in the lower-third PWR zone required by the floorplan; the receptacle mouth faces out (+y), and the enclosure has a matching 10 x 4 mm opening at x = 8. **Side is correct.**
- Contacts: A6/B6 D+, A7/B7 D-, A5 CC1 and B5 CC2 go to TUSB320LAI CC1/CC2 and the ESD array; four VBUS and four GND pins; shield through R1. Correct for a USB 2.0 sink.
- **Edge offset:** the KiCad USB4105 footprint (GCT recommended layout) marks "PCB Edge" at J1 y + 3.1 = 83.7 mm, but the board edge is at 84.0 mm. The shell front therefore protrudes 0.28 mm instead of 0.58 mm. Correction: move J1 +0.3 mm in y (to 80.9) during the USB-corner re-layout — a direct move was tried and reverted because the D+/D- crossover behind the pad row and a B.Cu VBUS_PROT track then collide (E1).
- **Plug engagement:** GCT's mating view gives 1.85 mm minimum between the plug overmold and the receptacle front. The enclosure puts the outer wall surface 2.1 mm in front of the receptacle today (0.4 mm gap + 2.0 mm wall − 0.28 mm protrusion), so a standard plug risks not seating fully. Moving J1 gives about 1.8 mm, which is marginal. Recommendation: thin the enclosure wall locally to ≤ 1.2 mm around the USB opening (a recessed pocket). Verify with the printed dummy and a real cable.

## 4. Buttons (SW1 BUTTON_1/BOOT, SW2 BUTTON_2) — **correct side, correct contacts; plungers still needed**

- Part and land: Alps SKSCLCE010 = SKSC catalogue Drawing No. 1 (side push, 1.6 N, 0.2 mm travel). The footprint lands are 1.4 x 0.9 mm at X +/-1.8, Y +/-0.65, which match the Drawing No. 1 land (5.0 mm outer span, 2.2 mm inner gap, 2.2 mm row span with a 0.4 mm gap).
- Contacts: Alps circuit diagram — terminals 1-2 are one contact and 3-4 the other. The footprint gives the same-row pair (±1.8 mm) the same pad number, so pad 1 = BUTTON net and pad 2 = GND. Each switch shorts its GPIO to GND. The 10 k pull-ups R41/R42 give active-low buttons as the GPIO map specifies.
- Position: right board edge at y 53.5/59.5 mm, rotated so the 1.6 mm-wide knob points outward (+x). The knob tip is at x 60.85 (0.7 mm knob beyond a body that sits 0.17 mm over the edge). The buttons sit outside the display projection. Enclosure holes are Ø2.8 mm at the same y, centred 0.8 mm above the PCB (Alps push height 0.7 mm). **Side and orientation are correct**, and the buttons are reachable in portrait and landscape (PR03).
- **Open mechanical item:** the knob tip ends 1.55 mm inside the 2 mm wall's outer surface, so the enclosure needs printed plungers/button caps (with retention and about 0.2 mm travel), which are not designed yet.

## Summary of actions

| # | Action | Type | Status |
| --- | --- | --- | --- |
| E1 | Move J1 +0.3 mm in y (GCT PCB-edge line) | CAD, evidence-backed | tried and reverted: the D+/D- crossover behind the pad row and a B.Cu VBUS_PROT track by the shield stakes collide; do it in the USB-corner hand re-layout. E2 alone restores the plug clearance (0.4 + 1.2 - 0.28 = 1.32 mm < 1.85 mm) |
| E2 | Thin the enclosure wall at the USB-C opening to <= 1.2 mm | mechanical | open (fit dummy) |
| E3 | Button plungers for SW1/SW2 | mechanical | open (fit dummy) |
| E4 | Antenna vs display projection overlap (Deviation B) | display/mechanical ENGINEERING_RETURN | open, needs the Orient drawing |
| E5 | FR-4 notch under the ESP32 antenna (Deviation A) | owner/mechanical decision | proposal |
| E6 | USB series/shunt footprints at U1 + coupled pair routing | schematic/layout proposal | open (USB corner re-layout) |
| E7 | Move C42 100 nF closer to U1 pin 2 | layout | open |
