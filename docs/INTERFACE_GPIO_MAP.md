# Rev A interface and GPIO allocation candidate

Status: reviewed allocation entered in KiCad sheet `01_compute`; assignments remain change-controlled until exact display, power and GNSS applications are reviewed. ESP32-S3-WROOM-1-N16R8 octal PSRAM reserves GPIO35/36/37.

## ESP32-S3 allocation

| GPIO | Function | Direction / notes |
| ---: | --- | --- |
| 0 | BUTTON_1 / ROM boot | Active-low user button; intentional recovery dual use |
| 1, 2 | I2C SDA, SCL | Sensors, touch, power monitor and expansion; 3.3 V |
| 4 | TOUCH_INT | Input |
| 5 | SX1262_DIO1 | Input/IRQ |
| 6 | SX1262_BUSY | Input |
| 7 | LCD_BL_PWM | PWM to backlight driver enable/dimming |
| 8 | LCD_AUX | Reserved display control / recovery GPIO; three-line SPI carries command/data in-band, so this is not a D/C requirement |
| 9 | SX1262_NSS | Shared SPI chip select |
| 10 | LCD_CS | Shared SPI chip select; TFT branch requires 1.8 V translation |
| 11, 12, 13 | SPI MOSI, SCLK, MISO | Shared LCD/microSD/SX1262 bus; TFT MOSI/SCLK branch requires 1.8 V translation; transactions bounded by owner |
| 14 | SD_CS | Shared SPI chip select |
| 15, 16 | PDM_CLK, PDM_DATA | Two-wire digital microphone candidate |
| 17, 18 | GNSS_TX, GNSS_RX | UART1 candidate; names are from ESP32 perspective |
| 19, 20 | USB_D-, USB_D+ | Native USB; never reassigned |
| 21 | GNSS_PPS | Input; exact module must expose PPS |
| 38 | EXP_IRQ_GPIO | Direct expansion interrupt/GPIO |
| 39, 40 | EXP_UART_TX, EXP_UART_RX | UART2 candidate |
| 41, 42 | RP_UART_RTS, RP_UART_CTS | Hardware flow control |
| 43, 44 | RP_UART_TX, RP_UART_RX | UART0 candidate; console uses native USB |
| 47 | ICM42688_INT1 | Direct inertial timing interrupt |
| 48 | BUTTON_2 | Active-low user button |

GPIO3, GPIO45 and GPIO46 remain unused because they are strapping pins; GPIO46 is also input-only. GPIO35-37 remain unavailable due to octal PSRAM. Slow resets, enables, card detect and power status move to an I2C GPIO expander; no safety function depends on the expander or MCU.

## I2C map

| Address | Device | Notes |
| --- | --- | --- |
| 0x20 | TCA9535 candidate | Slow resets/enables/status only; now also reads the TUSB320LAI GPIO-mode outputs (see below) |
| 0x30 | MMC5983MA | Locked magnetometer |
| 0x6B | BQ25887 2S charger candidate | Seven-bit default address verified in TI SLUSD89B section 8.3.11.5/Table 6; any separate state-of-charge gauge remains open |
| 0x44 | SHT40 | Locked humidity/temperature sensor |
| 0x46 | BMP581 | SDO-low candidate; the 0x47 alternate is available again now that TUSB320LAI is off the bus (D22), and stays secondary |
| Published `0x70` | ST1633I touch | Orient C1 revision J does not identify seven-bit versus eight-bit-write convention; confirm controller source and both labeled samples before declaring the address map collision-free |
| 0x68 | ICM-42688-P | AD0-low candidate; 0x69 remains alternate |

~~The bus starts at 400 kHz.~~ **The bus runs at 100 kHz Standard-mode per accepted decision D22 (owner, 2026-09-21); the pull-up window, cable limit and arithmetic are maintained in [the I2C bus budget](I2C_BUS_BUDGET.md) Result 3 (2026-09-22 update): 2.2 k ohm +/- 1% preferred pair on `3V3_MAIN`, expansion cable reserve <= 150 pF.** Interrupt/polling policy: direct touch and IMU interrupts; poll BMP581/MMC5983MA at scheduled rates. The BQ25887 interrupt/status allocation and any separate gauge alert remain open until the exact power application is reviewed. Stuck-bus recovery: GPIO1/GPIO2 are ordinary GPIO-capable pins, so firmware implements the standard recovery — detect a stuck SDA, reconfigure the pins as GPIO, toggle SCL up to nine times until SDA releases, issue STOP, then re-enable the peripheral; no dedicated hardware line is required.

### TUSB320LAI in GPIO mode (D22/P26, SLLSEQ8D Rev D)

The TUSB320LAI is removed from the shared I2C bus. Applied wiring intent, all from TI SLLSEQ8D Rev D (May 2017):

- **ADDR (pin 5): no connect** — §7.2.4: ADDR floating selects GPIO output mode and physically disables the I2C interface; the device never drives or loads SDA/SCL (former pins 7/8 become open-drain outputs OUT1/OUT2).
- **PORT (pin 3): tied to GND** — §7.2.1.2: fixed UFP (sink), presenting Rd on both CC lines; matches the P17 fixed-UFP policy. In GPIO mode the device advertises/accepts default USB Type-C current only (§7.2.1.1/Table 2) — consistent with the no-PD, 5 V-only baseline (D12/P17).
- **EN_N (pin 11): tied to GND** — pin description (SLLSEQ8D page 4): EN_N is the enable input; the part is disabled when the pin sits at its internal pull-up-to-VDD default, so floating it would leave the USB-C controller off. A hard tie to GND selects the always-enabled state required by a fixed-UFP charging port (P17) and needs no dynamic control; the "held low at least 50 ms after VDD valid" external-control note is satisfied statically by the tie.
- **VBUS_DET (pin 4): divider from VBUS through the datasheet 900 k ohm** (unchanged from the existing electrical-matrix disposition).
- **VDD (pin 12): `3V3_MAIN`** — keeps the device out of the back-power scenario: all TUSB input/output pins are pulled from `3V3_MAIN`-domain nets, and an always-on VDD prevents any pin from feeding an unpowered die.
- **OUT1 (pin 7), OUT2 (pin 8), OUT3 (pin 6): open-drain outputs, each pulled to `3V3_MAIN` through 100 k ohm (weak; slow status only), read as inputs on TCA9535PWR expander port pins** — allocation at the expander pin-map freeze (DIG-03). Table 3 defines the decoding: H/H = default current unattached, H/L = default attached, L/H = 1.5 A attached, L/L = 3.0 A attached. OUT3 is the audio-accessory flag in GPIO mode and must never assert on this product; it is read-only status, not a control.
- **No ESP32-S3 GPIO pins are consumed.** Direct allocation was evaluated and rejected: the only free pins (GPIO3, GPIO45, GPIO46) are strapping pins — GPIO45 selects VDD_SPI voltage at boot and must not hang on an externally pulled open-drain net; GPIO46 is input-only and also a strap.
- **Interaction with charger gating:** P17 requires the charger `CD` to stay disabled until cells are valid and an accepted USB current state exists. Whether that gating reads OUT1/OUT2 in hardware or firmware-via-expander is a PWR-02/PWR-03 design decision; this map only reserves the signals and the expander inputs.
- **Static load for PWR-04:** SLLSEQ8D §6.5 lists IUNATTACHED_UFP = 70 uA typical for the unattached-UFP state; with the always-enabled, always-powered disposition above this is a permanent `3V3_MAIN` load whenever the unit is on. Switching TUSB VDD is only acceptable together with removing or reviewing the expander-side 100 k pulls (back-power path); the default disposition accepts the 70 uA and lets PWR-04 trade it in the rail inventory.

## Shared SPI service contract

LCD, microSD and SX1262 share one hardware SPI host with separate chip selects. The provisional three-line TFT branch needs reviewed unidirectional 3.3-to-1.8 V translation for clock, data and chip select plus a separate open-drain reset path; its ninth serial bit carries command/data. Do not place a translator on the entire shared bus. Drivers must hold the bus only for bounded chunks, restore mode/frequency on every transaction and never wait for radio BUSY while owning the bus. The storage task batches writes; the UI uses partial rectangles; the radio IRQ path preempts between chunks. A logic-analyzer stress test must show that maximum LCD/SD occupancy does not violate SX1262 service timing.

## RP2040 and expansion transport

RP2040 uses a dedicated 921600-baud UART with RTS/CTS. At 8N1 it provides about 92.16 kB/s payload before framing, above the 40 kB/s stress scenario in the ADS-B architecture. Sequence numbers, receiver-overflow counters and protocol CRC make loss visible. The external expansion UART remains independent.

The map closes the logical resource budget, including native USB and recovery paths. Exact electrical pullups, boot-state levels and expander output defaults must be reviewed in each schematic sheet.

## KiCad entry status

`hardware/kicad/01_compute.kicad_sch` implements U1, the EN 10 kΩ pull-up/1 µF reset capacitor, 10 µF plus 100 nF local 3V3 decoupling and every used GPIO net above. Its +3V3 and GND connections are global hierarchy nets so child-sheet loads share the intended rails. GPIO3, GPIO35, GPIO36, GPIO37, GPIO45 and GPIO46 carry explicit no-connect markers. The footprint is KiCad's standard ESP32-S3-WROOM-1 module footprint and must still be checked against Espressif's current land pattern and antenna keepout before PCB placement.
