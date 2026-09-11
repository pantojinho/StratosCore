# Rev A interface and GPIO allocation candidate

Status: reviewed allocation entered in KiCad sheet `01_compute`; assignments remain change-controlled until exact display/power/GNSS choices are accepted. ESP32-S3-WROOM-1-N16R8 octal PSRAM reserves GPIO35/36/37.

## ESP32-S3 allocation

| GPIO | Function | Direction / notes |
| ---: | --- | --- |
| 0 | BUTTON_1 / ROM boot | Active-low user button; intentional recovery dual use |
| 1, 2 | I2C SDA, SCL | Sensors, touch, power monitor and expansion; 3.3 V |
| 4 | TOUCH_INT | Input |
| 5 | SX1262_DIO1 | Input/IRQ |
| 6 | SX1262_BUSY | Input |
| 7 | LCD_BL_PWM | PWM to backlight driver enable/dimming |
| 8 | LCD_DC | Output |
| 9 | SX1262_NSS | Shared SPI chip select |
| 10 | LCD_CS | Shared SPI chip select |
| 11, 12, 13 | SPI MOSI, SCLK, MISO | Shared LCD/microSD/SX1262 bus; transactions bounded by owner |
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
| 0x20 | TCA9535 candidate | Slow resets/enables/status only |
| 0x30 | MMC5983MA | Locked magnetometer |
| 0x36 | MAX17048 behind TCA9543A | Same fixed address isolated per bay |
| 0x44 | SHT40 | Locked humidity/temperature sensor |
| 0x46 | BMP581 | SDO-low candidate; 0x47 remains alternate |
| 0x55 expected | ST1633i touch | Must be confirmed from exact C1 document/sample |
| 0x68 | ICM-42688-P | AD0-low candidate; 0x69 remains alternate |
| 0x70 | TCA9543A candidate | A1/A0 low; per-bay gauge branches |

The bus starts at 400 kHz. Interrupt/polling policy: direct touch and IMU interrupts; poll BMP581/MMC5983MA at scheduled rates; aggregate gauge alerts through TCA9543A. Expansion bus capacitance and stuck-bus recovery require a measured cable limit.

## Shared SPI service contract

LCD, microSD and SX1262 share one hardware SPI host with separate chip selects. Drivers must hold the bus only for bounded chunks, restore mode/frequency on every transaction and never wait for radio BUSY while owning the bus. The storage task batches writes; the UI uses partial rectangles; the radio IRQ path preempts between chunks. A logic-analyzer stress test must show that maximum LCD/SD occupancy does not violate SX1262 service timing.

## RP2040 and expansion transport

RP2040 uses a dedicated 921600-baud UART with RTS/CTS. At 8N1 it provides about 92.16 kB/s payload before framing, above the 40 kB/s stress scenario in the ADS-B architecture. Sequence numbers, receiver-overflow counters and protocol CRC make loss visible. The external expansion UART remains independent.

The map closes the logical resource budget, including native USB and recovery paths. Exact electrical pullups, boot-state levels and expander output defaults must be reviewed in each schematic sheet.

## KiCad entry status

`hardware/kicad/01_compute.kicad_sch` implements U1, the EN 10 kΩ pull-up/1 µF reset capacitor, 10 µF plus 100 nF local 3V3 decoupling and every used GPIO net above. Its +3V3 and GND connections are global hierarchy nets so child-sheet loads share the intended rails. GPIO3, GPIO35, GPIO36, GPIO37, GPIO45 and GPIO46 carry explicit no-connect markers. The footprint is KiCad's standard ESP32-S3-WROOM-1 module footprint and must still be checked against Espressif's current land pattern and antenna keepout before PCB placement.
