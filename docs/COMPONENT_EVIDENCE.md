# Component evidence and sourcing review

Review date: 2026-09-11 UTC. Prices and stock are snapshots, not purchase commitments. Manufacturer documents control electrical and mechanical data; distributor pages are used only for orderability and dated availability.

## Display selection for validation

**Selected sample candidate:** Orient Display `AFY240320A1-2.8INTH-C1`.

This candidate satisfies the locked 2.8-inch, 240 x 320 IPS and capacitive-touch requirement. Orient's current catalogue identifies ST7789VI display control, ST1633i touch, RGB/MCU/SPI interfaces, 900 cd/m2 luminance and a 50.45 x 69.90 x 4.21 mm module envelope. DigiKey listed 42 units, active status, an eight-week lead time and USD 31.55 at quantity one on the review date; the price was USD 25.489 at quantity ten.

The currently published drawing is for the closely related `AFY240320A1-2.8INTH-C`, not the full C1 ordering code. It shows a 40-contact 0.5 mm display FPC, separate six-contact touch FPC, 2.8 V logic, 0.625 W module power and 125 mA backlight current, but its ST1633 controller suffix differs. These facts may guide budgets only. **They do not authorize a C1 connector pinout or footprint.**

Procurement gate before schematic connector entry:

1. Obtain the exact C1 revision-controlled drawing and controller initialization material from Orient.
2. Buy two samples from an authorized source and verify the ordering labels.
3. Inspect FPC pitch, contact side, bend radius and touch/display connector separation.
4. Measure logic compatibility, backlight voltage/current, sleep leakage, sunlight readability and partial-refresh performance.

Sources: [Orient current catalogue](https://orientdisplay.com/product-catelogue/), [Orient sunlight-readable list](https://orientdisplay.com/our-products/color-tft/sunlight-readable-ips/), [related C drawing](https://orientdisplay.com/wp-content/uploads/2020/12/AFY240320A1-2.8INTH-C-spec.pdf), and [DigiKey C1 listing](https://www.digikey.com/en/products/detail/orient-display/AFY240320A1-2-8INTH-C1/17863493).

## GNSS finding and replacement proposal

The locked `ATGM332D-5NR32` is orderable as LCSC `C3037611`. LCSC listed 1,454 units and USD 1.8239 at quantity one, USD 1.5071 at quantity 100 and USD 1.4386 at quantity 1,000 on the review date.

The full 18-page manufacturer manual resolves the earlier constellation discrepancy: its technical table lists BDS, GPS, GLONASS, Galileo, QZSS and SBAS, 1 Hz default with 10 Hz maximum, NMEA0183, 2.7-3.6 V supply, less than 26 mA at 3.3 V, 15.9 x 12.1 x 2.4 mm and a maximum altitude of **18,000 m**. That altitude ceiling is below ordinary high-altitude balloon missions and conflicts with StratosCore's balloon use case. The exact part can remain suitable for ground, handheld and normal flight profiles, but cannot be the only Rev A navigation source if operation above 18 km is required.

### Proposed replacement: u-blox `MAX-M10S-00B`

| Required comparison | ATGM332D-5NR32 | MAX-M10S-00B | Impact |
| --- | --- | --- | --- |
| Reason | Locked low-cost choice; 18 km ceiling | Airborne modes rated to 80 km | Removes a mission-stopping balloon limitation |
| Supply, 2026-09-11 UTC | LCSC: 1,454 | DigiKey: 6,600; Mouser pages showed over 22,000 | Both available; u-blox has broader authorized distribution evidence |
| Unit price | LCSC USD 1.8239 at 1 | DigiKey USD 11.42 at 1, USD 9.32826 at 500 | About USD 9.60 higher at prototype quantity |
| Constellations/rate | Six systems listed; 1 Hz default, 10 Hz maximum | GPS, Galileo, GLONASS, BeiDou/QZSS; 3-10 Hz default and 10-20 Hz high-performance depending on constellation set | Firmware configuration changes; desired Galileo is explicit |
| Electrical | 2.7-3.6 V, under 26 mA at 3.3 V | 1.76-3.6 V, about 25 mW continuous tracking; UART and I2C | Lower typical GNSS power; new backup/antenna and startup review |
| PCB/mechanical | 15.9 x 12.1 x 2.4 mm | 9.7 x 10.1 x 2.5 mm, 18-pad LCC | New verified symbol/footprint; saves board area; not pin-compatible |
| Firmware | NMEA/commands for CASIC module | UBX configuration plus NMEA/UBX parsing | New driver and airborne dynamic-model configuration |

Primary sources: [ATGM332D-5NR32 manual](https://datasheet.lcsc.com/lcsc/2206231830_ZHONGKEWEI-ATGM332D-5NR32_C3037611.pdf), [u-blox MAX-M10S data sheet](https://beta-content.u-blox.com/sites/default/files/MAX-M10S_DataSheet_UBX-20035208.pdf), and [u-blox integration manual](https://content.u-blox.com/sites/default/files/MAX-M10S_IntegrationManual_UBX-20053088.pdf). Supply sources: [LCSC C3037611](https://www.lcsc.com/product-detail/Satellite-Positioning-Modules_ZHONGKEWEI-ATGM332D-5NR32_C3037611.html) and [DigiKey MAX-M10S-00B](https://www.digikey.com/en/products/detail/u-blox/MAX-M10S-00B/15712906).

This is a complete replacement proposal, not an accepted baseline change. Until the owner accepts it, schematic sheet `03_gnss` remains on hold and D07 remains locked to ATGM332D-5NR32.

## Locked sensor audit

The four locked sensor families were checked against primary documents and current distributor listings. MMC5983MA, BMP581 and SHT40 have document evidence sufficient for gated schematic entry. The ICM-42688-P electrical facts below came from retrieved DS-000347 v1.6, while TDK's current product page advertises v1.9; its symbol and footprint therefore remain on hold pending that revision's delta review. The proposed common implementation is 3.3 V I2C at an initial 400 kHz bus rate, with a direct ESP32 interrupt only for the ICM-42688-P. BMP581 and MMC5983MA are scheduled/polled; SHT40 is sampled slowly at the board edge. This is proposal P13 and still requires thermal, magnetic, pressure-port and bus-loading measurements.

| Device | Exact electrical/package evidence | Supply snapshot, 2026-09-11 UTC | CAD consequence |
| --- | --- | --- | --- |
| `ICM-42688-P` | 1.71-3.6 V VDD/VDDIO; 14-LGA 2.5 x 3.0 mm; I2C address 0x68 with AD0 low; WHO_AM_I 0x47; 1 MHz I2C maximum | DigiKey: zero stock, USD 4.91 at one and 45-week standard lead; recent LCSC `C1850418`: 336 and USD 19.2845 at one | Keep exact MPN but flag sourcing risk. Use 0.1 µF + 2.2 µF on VDD and 10 nF on VDDIO per the typical application; route INT1 directly. |
| `MMC5983MA` | 2.8-3.6 V; 16-LGA 3 x 3 x 1 mm; I2C/SPI; ±8 G and 18-bit output; I2C up to 400 kHz | DigiKey: 39,571 and USD 3.32 at one | Use I2C address 0x30 and keep the device away from cells, inductors and high-current loops. Verify SET/RESET behavior and calibration on hardware. |
| `BMP581` | VDD 1.71-3.6 V, VDDIO 1.08-3.6 V; 10-LGA 2 x 2 x 0.75 mm; 300-1250 hPa; I2C/SPI/I3C | DigiKey: 27,077 and USD 3.07 at one | Use I2C, tie CSB to VDDIO and all VSS pads to ground. If either rail ramps in under 10 µs, Bosch Figure 28 requires 10 Ω in series with VDD and 100 Ω with VDDIO. Ground unused INT only with the matching register configuration. |
| `SHT40-AD1B-R2` | Exact selected suffix; 1.08-3.6 V; four-pad DFN 1.5 x 1.5 x 0.5 mm; I2C address 0x44; ±1.8 %RH and ±0.2 °C typical accuracy class | DigiKey: 28,262 and USD 1.88 at one | Do not place copper or solder beneath the center die area. Put it at the vented board edge and use the heater only for controlled condensation recovery; data sheet maximum heater duty is below 10%. |

Primary sources: [TDK ICM-42688-P product/document page](https://www.invensense.tdk.com/en-us/products/6-axis/icm-42688-p) (current page advertises DS-000347 v1.9; the detailed audit above used retrieved v1.6 and therefore does not yet release CAD), [MEMSIC MMC5983MA Rev A](https://www.memsic.com/Public/Uploads/uploadfile/files/20220119/MMC5983MADatasheetRevA.pdf), [Bosch BMP581](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp581-ds004.pdf), and [Sensirion SHT4x v7.3](https://sensirion.com/media/documents/33FD6951/6A7C10A0/HT_DS_Datasheet_SHT4x_V7.3.pdf). Supply sources: [DigiKey ICM-42688-P](https://www.digikey.com/en/products/detail/tdk-invensense/ICM-42688-P/11679713), [LCSC C1850418](https://www.lcsc.com/product-detail/C1850418.html?is_substitute=1&original_product_code=C2655100&original_unit_price=4.2396), [DigiKey MMC5983MA](https://www.digikey.com/en/products/detail/memsic-inc/MMC5983MA/10452801), [DigiKey BMP581](https://www.digikey.com/en/products/detail/bosch-sensortec/BMP581/16036134), and [DigiKey SHT40-AD1B-R2](https://www.digikey.com/en/products/detail/sensirion-ag/SHT40-AD1B-R2/13532084).

ICM-42688-P availability is volatile and the two distributor snapshots disagree materially with older cached listings. No silent substitute is authorized. Recheck authorized stock immediately before prototype ordering; any alternate IMU requires the full replacement record defined in `AGENTS.md`.
