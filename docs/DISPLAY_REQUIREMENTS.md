# Display interface specification

Locked product target: **2.8-inch IPS LCD, 320 x 240 in landscape or 240 x 320 in portrait, capacitive touch and both orientations**. Orient Display `AFY240320A1-2.8INTH-C1` remains the selected sample candidate; the exact part is not locked until sample and sourcing review.

Status: the exact manufacturer specification is now available and releases electrical planning. The mating connectors and PCB footprints remain gated until the FPC drawing/contact orientation is independently reviewed and labeled samples are inspected.

## Controlled sources

Reviewed 2026-09-14:

- [Orient AFY240320A1-2.8INTH-C1 specification](https://www.orientdisplay.com/wp-content/uploads/2021/11/AFY240320A1-2.8INTH-C1.pdf), revision J dated 2021-07-20; sections 1-10 and drawing page 5.
- [Orient product page](https://orientdisplay.com/products/2-8-sunlight-readable-ips-240x320-900-nits-with-capacitive-touch-panel-rgb-mcu-spi-interface-new-ctp-ic/), exact SKU.
- [DigiKey exact-part listing](https://www.digikey.com/en/products/detail/orient-display/AFY240320A1-2-8INTH-C1/22531939), checked 2026-09-14 for dated price/availability only.

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
| Backlight | Specification states 5.8-6.4 V, 100 mA typical, 125 mA absolute maximum and 0.60 W typical; five white LEDs |
| Power | 0.625 W module figure in the general table; backlight dominates and must be measured at the selected brightness |

The 1.8 V TFT logic requirement is incompatible with direct 3.3 V ESP32 drive. The SPI path needs a reviewed 3.3-to-1.8 V translation strategy and appropriate 1.8 V rail. Touch can use 3.3 V supply/I/O within the published range, subject to the separate ST1633I specification and sample confirmation.

The backlight description combines a 5.8-6.4 V forward range with a five-LED statement. Do not reconstruct the internal LED topology from prose. Select a current-regulated, dimmable driver only after measuring the exact sample and confirming anode/cathode behavior.

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

The module drawing calls for ZIF connection, but the exact connector MPN, pitch, contact side, insertion direction, FPC stiffener thickness and PCB landing are not yet independently transcribed and checked. Do not create or assign either connector footprint until that review is complete.

## Host and sequencing plan

SPI remains the selected first interface because it fits the GPIO budget. The published module supports 3-line and 4-line serial timing, but the exact Rev A mode, IM0-IM2 straps, command/data signaling and unused-pin ties remain a review item. RGB or 8080 MCU mode requires a new documented GPIO/bandwidth decision.

The TFT reset and supply sequence diagrams must be transcribed into the power design. For the touch controller, revision J states RESET must be low before power-on and power-off and must remain low for at least 5 ms after its supplies reach normal voltage. Confirm reset polarity/timing for both controllers against their exact controller specifications and samples.

At RGB565, a full 320 x 240 frame is 153,600 bytes. Thirty full frames/s requires 4.608 MB/s, or 36.864 Mbit/s of payload before command overhead and bus gaps. Prefer partial updates and measure contention with microSD and SX1262 on the shared SPI host.

Firmware must separate panel driver, touch driver, orientation transform, backlight policy and UI. Test all four corners in both orientations, sleep/wake, display-off logging and brightness profiles.

## Sourcing snapshot and remaining gates

Checked 2026-09-14: the exact Orient store page listed 50 units at USD 35.36 each, USD 31.39 at 25-49 and USD 27.42 at 50+. DigiKey listed zero immediately available, one expected 2026-10-19, USD 31.55 at quantity one and an eight-week manufacturer lead time. Recheck before purchase.

Before connector or footprint freeze:

1. independently inspect revision J drawing page 5 and record both FPC geometries, contact sides, pitch/tolerance and mating connector requirements;
2. obtain at least two labeled C1 samples and confirm controller markings/identification, connector geometry and continuity;
3. select and review the 1.8 V rail, SPI level translation, TFT supply, touch supply, resets and backlight driver;
4. verify SPI mode straps and unused-pin ties from revision J plus the exact controller documentation;
5. run brightness, power, temperature, touch-address, orientation and shared-bus tests;
6. create connector footprints from exact connector manufacturer drawings and independently overlay them before release.
