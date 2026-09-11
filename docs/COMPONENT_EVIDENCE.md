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
