# Component evidence and sourcing review

Last updated: 2026-09-14. Prices and stock are snapshots, not purchase commitments. Manufacturer documents control electrical and mechanical data; distributor pages are used only for orderability and dated availability.

## Display selection for validation

**Selected sample candidate:** Orient Display `AFY240320A1-2.8INTH-C1`.

The exact [Orient AFY240320A1-2.8INTH-C1 specification](https://www.orientdisplay.com/wp-content/uploads/2021/11/AFY240320A1-2.8INTH-C1.pdf), revision J dated 2021-07-20, was reviewed on 2026-09-14. It satisfies the locked 2.8-inch, 240 x 320 IPS and capacitive-touch requirement and identifies ST7789VI or compatible display control, ST1633I touch, RGB/MCU/SPI interfaces, 900 cd/m2 typical luminance and a 50.45 x 69.90 x 4.22 mm module envelope.

The exact document specifies a 40-contact TFT interface and a separate six-contact CTP interface. It also exposes a previously unresolved electrical requirement: TFT VDDIO is 1.8 V, so ESP32 3.3 V signals cannot drive the display directly. Rev A therefore needs a reviewed 1.8 V rail and branch-specific 3.3-to-1.8 V translation for the TFT serial controls. Touch accepts a 3.3 V supply/I/O and its specified seven-bit I2C address is `0x70`. The backlight is specified at 5.8-6.4 V and 100 mA typical, 125 mA absolute maximum; its driver remains open until sample behavior is confirmed.

Availability checked 2026-09-14: the Orient store page displayed 50 units at USD 35.36 each, USD 31.39 at 25-49 and USD 27.42 at 50+. The [DigiKey exact-part listing](https://www.digikey.com/en/products/detail/orient-display/AFY240320A1-2-8INTH-C1/22531939) displayed zero immediately available, one expected 2026-10-19, USD 31.55 at quantity one and an eight-week manufacturer lead time. Recheck before purchase.

Remaining gate before connector/footprint release:

1. Independently transcribe and compare both FPC geometries, contact sides, pitch/tolerance and mating-connector requirements from revision-J drawing page 5.
2. Buy two labeled C1 samples and verify controller identity, FPC geometry and continuity.
3. Select and review the 1.8 V rail, TFT translator, TFT/touch supplies, reset sequence and current-regulated backlight driver.
4. Verify the exact SPI mode straps and unused-pin handling from revision J plus the controller documents.
5. Measure backlight voltage/current, sleep leakage, touch address, sunlight readability, orientation and shared-bus behavior.

See [display interface specification](DISPLAY_REQUIREMENTS.md) for the controlled pin tables and acceptance plan. The exact module document releases electrical planning but does not yet authorize connector footprints.

## GNSS finding and replacement proposal

The locked `ATGM332D-5NR32` is orderable as LCSC `C3037611`. LCSC listed 1,454 units and USD 1.8239 at quantity one, USD 1.5071 at quantity 100 and USD 1.4386 at quantity 1,000 on the review date.

The full 18-page manufacturer manual resolves the earlier constellation discrepancy: its technical table lists BDS, GPS, GLONASS, Galileo, QZSS and SBAS, 1 Hz default with 10 Hz maximum, NMEA0183, 2.7-3.6 V supply, less than 26 mA at 3.3 V, 15.9 x 12.1 x 2.4 mm and a maximum altitude of **18,000 m**. That altitude ceiling is below ordinary high-altitude balloon missions and conflicts with StratosCore's balloon use case. The exact part can remain suitable for ground, handheld and normal flight profiles, but cannot be the only Rev A navigation source if operation above 18 km is required.

### Accepted replacement: u-blox `MAX-M10S-00B`

| Required comparison | ATGM332D-5NR32 | MAX-M10S-00B | Impact |
| --- | --- | --- | --- |
| Reason | Locked low-cost choice; 18 km ceiling | Airborne modes rated to 80 km | Removes a mission-stopping balloon limitation |
| Supply, 2026-09-11 UTC | LCSC: 1,454 | DigiKey: 6,600; Mouser pages showed over 22,000 | Both available; u-blox has broader authorized distribution evidence |
| Unit price | LCSC USD 1.8239 at 1 | DigiKey USD 11.42 at 1, USD 9.32826 at 500 | About USD 9.60 higher at prototype quantity |
| Constellations/rate | Six systems listed; 1 Hz default, 10 Hz maximum | GPS, Galileo, GLONASS, BeiDou/QZSS; 3-10 Hz default and 10-20 Hz high-performance depending on constellation set | Firmware configuration changes; desired Galileo is explicit |
| Electrical | 2.7-3.6 V, under 26 mA at 3.3 V | 1.76-3.6 V, about 25 mW continuous tracking; UART and I2C | Lower typical GNSS power; new backup/antenna and startup review |
| PCB/mechanical | 15.9 x 12.1 x 2.4 mm | 9.7 x 10.1 x 2.5 mm, 18-pad LCC | New verified symbol/footprint; saves board area; not pin-compatible |
| Firmware | NMEA/commands for CASIC module | UBX configuration plus NMEA/UBX parsing | New driver and airborne dynamic-model configuration |

Primary sources for the accepted module were refreshed on 2026-09-13: [u-blox MAX-M10S data sheet UBX-20035208 R08, 2026-01-30](https://content.u-blox.com/sites/default/files/MAX-M10S_DataSheet_UBX-20035208.pdf), [u-blox integration manual UBX-20053088 R05, 2026-04-28](https://content.u-blox.com/sites/default/files/MAX-M10S_IntegrationManual_UBX-20053088.pdf), and [u-blox M10 SPG 5.10 interface description UBX-21035062 R03](https://content.u-blox.com/sites/default/files/u-blox-M10-SPG-5.10_InterfaceDescription_UBX-21035062.pdf). Historical ATGM evidence remains the [ATGM332D-5NR32 manual](https://datasheet.lcsc.com/lcsc/2206231830_ZHONGKEWEI-ATGM332D-5NR32_C3037611.pdf). Supply sources for the dated comparison were [LCSC C3037611](https://www.lcsc.com/product-detail/Satellite-Positioning-Modules_ZHONGKEWEI-ATGM332D-5NR32_C3037611.html) and [DigiKey MAX-M10S-00B](https://www.digikey.com/en/products/detail/u-blox/MAX-M10S-00B/15712906).

The project owner accepted this replacement on 2026-09-13. D07 is now locked to MAX-M10S-00B.

### MAX-M10S-00B application evidence reviewed 2026-09-13

- **Exact identity verified:** the ordering code is global professional-grade `MAX-M10S-00B`; data-sheet R08 applies to mass-production type number `MAX-M10S-00B-01` with ROM SPG 5.10 firmware. The `-01` type suffix is not a replacement ordering code.
- **Pin map verified:** 18 LCC contacts are GND, TXD, RXD, TIMEPULSE, EXTINT, V_BCKP, V_IO, VCC, RESET_N, GND, RF_IN, GND, LNA_EN, VCC_RF, VIO_SEL, SDA, SCL, and SAFEBOOT_N in pins 1 through 18 respectively. TIMEPULSE and SAFEBOOT_N are internally linked through 1 kOhm.
- **Supply facts verified:** VCC is 1.76-3.6 V; V_IO is 1.76-1.98 V with VIO_SEL grounded or 2.7-3.6 V with it open; V_BCKP is 1.65-3.6 V. Startup inrush can reach 100 mA, VCC series resistance must not exceed 0.2 ohm, and PIOs must not be driven when VCC/V_IO are off in hardware backup.
- **Interface facts verified:** UART has no hardware flow control and defaults to 9600 baud 8N1; Rev A maps module TXD to ESP32 GPIO18, RXD from GPIO17, and TIMEPULSE to GPIO21. I2C remains unused; if reconsidered, its default seven-bit address is 0x42 and it is Fast-mode peripheral-only with up to 20 ms clock stretching.
- **Reset/enable facts verified:** RESET_N has an internal pull-up, needs at least 1 ms low, must not have a capacitor to ground, and clears BBR/RTC/orbit data. There is no dedicated enable pin. EXTINT is a configurable wake/power-save input, not a supply enable.
- **RF facts verified:** RF_IN is internally DC blocked and 50 ohms. The module includes a Band 13 notch, LNA and SAW filter. Passive antennas need no additional RF front-end in the typical u-blox design; an active antenna requires a selected bias/supervisor implementation.
- **Footprint source verified:** data-sheet R08 Figure 4 controls the module package; integration-manual R05 Figure 30/Table 44 controls copper and solder-mask openings and Figure 31/Table 45 the recommended T-shaped paste. The recommended stencil is 150 micrometers. No generic KiCad footprint has been accepted.
- **Firmware constraint verified:** the module defaults to the portable dynamic model. Balloon operation must set and verify `CFG-NAVSPG-DYNMODEL=AIR4` (value 8) after cold start; fitting the module alone does not select its 80 km Airborne 4 g envelope.

The exact symbol map and manufacturer CAD source are released for project symbol/footprint construction. Circuit entry remains gated by acceptance of the proposed tied 3.3 V VCC/V_IO arrangement, backup/reset/power-gating choices, exact antenna/connector/ESD path, calculated production-stackup impedance, and independent footprint review. See [GNSS architecture](GNSS_ARCHITECTURE.md).

## Locked sensor audit

The four locked sensor families were checked against primary documents and current distributor listings. MMC5983MA, BMP581 and SHT40 have document evidence sufficient for gated schematic entry. TDK DS-000347 v1.9, dated 2024-11-12 and published by TDK on 2026-06-01, now directly confirms the ICM-42688-P pin table, application circuit and package dimensions. Its revision history records a pin-out figure update in v1.7, notch-filter/CLKDIV changes in v1.8 and removal of Raise to Wake/Sleep plus a reference update in v1.9; use the v1.9 axes drawing in firmware and CAD. The proposed common implementation is 3.3 V I2C at an initial 400 kHz bus rate, with a direct ESP32 interrupt only for the ICM-42688-P. BMP581 and MMC5983MA are scheduled/polled; SHT40 is sampled slowly at the board edge. This is proposal P13 and still requires thermal, magnetic, pressure-port and bus-loading measurements.

| Device | Exact electrical/package evidence | Supply snapshot, 2026-09-11 UTC | CAD consequence |
| --- | --- | --- | --- |
| `ICM-42688-P` | 1.71-3.6 V VDD/VDDIO; 14-LGA 2.5 x 3.0 x 0.91 mm; 0.5 mm pitch; I2C address 0x68 with AD0 low; WHO_AM_I 0x47; 1 MHz I2C maximum | DigiKey: zero stock, USD 4.91 at one and 45-week standard lead; recent LCSC `C1850418`: 336 and USD 19.2845 at one | Pin map/application entry released from v1.9. Use 0.1 µF + 2.2 µF on VDD and 10 nF on VDDIO; route INT1 directly. Create/review a project footprint from the 0.475 x 0.25 mm nominal terminals and current AN-000393 mask/stencil rules; do not reuse the larger generic KiCad LGA pads. |
| `MMC5983MA` | 2.8-3.6 V; 16-LGA 3 x 3 x 1 mm; I2C/SPI; ±8 G and 18-bit output; I2C up to 400 kHz | DigiKey: 39,571 and USD 3.32 at one | Use I2C address 0x30 and keep the device away from cells, inductors and high-current loops. Verify SET/RESET behavior and calibration on hardware. |
| `BMP581` | VDD 1.71-3.6 V, VDDIO 1.08-3.6 V; 10-LGA 2 x 2 x 0.75 mm; 300-1250 hPa; I2C/SPI/I3C | DigiKey: 27,077 and USD 3.07 at one | Use I2C, tie CSB to VDDIO and all VSS pads to ground. If either rail ramps in under 10 µs, Bosch Figure 28 requires 10 Ω in series with VDD and 100 Ω with VDDIO. Ground unused INT only with the matching register configuration. |
| `SHT40-AD1B-R2` | Exact selected suffix; 1.08-3.6 V; four-pad DFN 1.5 x 1.5 x 0.5 mm; I2C address 0x44; ±1.8 %RH and ±0.2 °C typical accuracy class | DigiKey: 28,262 and USD 1.88 at one | Do not place copper or solder beneath the center die area. Put it at the vented board edge and use the heater only for controlled condensation recovery; data sheet maximum heater duty is below 10%. |

Primary sources: [TDK ICM-42688-P DS-000347 v1.9 download](https://www.invensense.tdk.com/en-us/download-resource/ds-000347-icm-42688-p-datasheet) and [AN-000393 v2.4 download](https://www.invensense.tdk.com/en-us/download-resource/000393-imu-pcb-design-and-mems-assembly-guidelines), both reviewed 2026-09-11; [MEMSIC MMC5983MA Rev A](https://www.memsic.com/Public/Uploads/uploadfile/files/20220119/MMC5983MADatasheetRevA.pdf); [Bosch BMP581](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp581-ds004.pdf); and [Sensirion SHT4x v7.3](https://sensirion.com/media/documents/33FD6951/6A7C10A0/HT_DS_Datasheet_SHT4x_V7.3.pdf). Supply sources: [DigiKey ICM-42688-P](https://www.digikey.com/en/products/detail/tdk-invensense/ICM-42688-P/11679713), [LCSC C1850418](https://www.lcsc.com/product-detail/C1850418.html?is_substitute=1&original_product_code=C2655100&original_unit_price=4.2396), [DigiKey MMC5983MA](https://www.digikey.com/en/products/detail/memsic-inc/MMC5983MA/10452801), [DigiKey BMP581](https://www.digikey.com/en/products/detail/bosch-sensortec/BMP581/16036134), and [DigiKey SHT40-AD1B-R2](https://www.digikey.com/en/products/detail/sensirion-ag/SHT40-AD1B-R2/13532084).

ICM-42688-P availability is volatile and the two distributor snapshots disagree materially with older cached listings. No silent substitute is authorized. Recheck authorized stock immediately before prototype ordering; any alternate IMU requires the full replacement record defined in `AGENTS.md`.
