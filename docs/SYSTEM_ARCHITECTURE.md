# System architecture

Status: conceptual Rev A allocation. No final pin map or complete schematic. Read [decisions](DECISIONS.md), [diagram](BLOCK_DIAGRAM.md) and [RF architecture](RF_ARCHITECTURE.md) together.

## Responsibilities

The ESP32-S3 owns UI, navigation, sensor fusion, LoRa services, storage, audio, profiles and Wi-Fi/BLE. RP2040 owns ADS-B timing acquisition and frame extraction independently of display refresh, SD stalls and network traffic. It reports validated decoded messages and health counters to ESP32; aircraft state assembly may remain on ESP32.

Use bounded queues between acquisition, processing, UI, networking and storage. One storage owner serializes microSD writes. Every stream includes timestamps, validity and overflow counts. A stalled dashboard must not stop sensor sampling or ADS-B acquisition. A failed radio, missing GNSS fix or full SD must degrade explicitly without resetting unrelated services.

## Interface allocation candidates

| Function | Candidate resource | Still to resolve |
| --- | --- | --- |
| LCD | SPI or QSPI serial interface preferred | Panel choice, bus count, DMA and refresh budget; no connector pinout |
| Touch + sensors + gauge | I2C; IMU SPI option if acquisition budget demands | Addresses, clock/stretch limits, interrupts, power domains and bus capacitance |
| SX1262 | SPI + NSS, BUSY, DIO1, RESET | Clock/TCXO, DIO2 RF switch policy, arbitration and IRQ latency |
| GNSS | UART; PPS provision if supported | Exact module command set, backup supply, PPS pin verification |
| RP2040 link | UART candidate; SPI alternative | Peak traffic, UART inventory, IRQ/reset/flow-control pins |
| microSD | SPI candidate; SDMMC alternative | SD and LCD contention, card detect, power switching, pullups |
| Microphone | I2S preferred; PDM alternative | Clock/data pins and ESP peripheral mode for selected microphone |
| Expansion | Shared I2C/SPI, dedicated CS, UART, IRQ | Can all interfaces coexist without consuming recovery paths? |
| USB | ESP32 native USB D-/D+ | ESD, VBUS detection, connector/charger ownership; separate RP SWD recovery |
| Buttons / rail enables | GPIO, possible reviewed expander for slow signals | Wake, boot straps, power domain and minimum two controls |

GPIO allocation is a Phase 2 gate. ESP32-S3-WROOM-1 N16R8's octal PSRAM reserves GPIO35/36/37; GPIO19/20 are native USB. Review boot straps GPIO0/3/45/46 and GPIO46's input-only restriction before use. Do not reuse legacy assignments. Source: [Espressif module datasheet](https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.html), pin definitions and peripheral sections.

Only a limited number of external SPI hosts and UART controllers exist; pin-matrix flexibility does not create new controllers. UART0 console, GNSS, RP2040 and expansion cannot all be assumed dedicated simultaneously. Prefer USB console and evaluate link migration to SPI. Sharing LCD/SD/radio requires bounded transaction sizes and a worst-case service-latency calculation. A wide parallel LCD may exhaust the GPIO budget.

## Timing and storage

Acquire monotonic timestamps close to data capture. GNSS UTC disciplines an explicit mapping with validity and uncertainty; never jump monotonic time on GNSS reacquisition. RP2040 timestamps need a measured mapping to ESP32, via time sync messages or a verified shared pulse. Audio sample counter and dropped-block events join that mapping.

Maintain per-field age in contacts; callsign, position and velocity arrive in different messages. Distinguish barometric and geometric altitude, ground track and heading, and magnetic and true north. Relative traffic requires valid ownship position and a specified coordinate transform. See [ADS-B](ADSB_ARCHITECTURE.md).

## Power domains and startup

Conceptual domains: always-needed control/gauge, digital 3V3, quiet GNSS/sensors, switchable ADS-B analog/RP2040, radio, display/backlight, and SD/audio. These are functional domains, not frozen rails or LDO counts. Sequence power and keep signals high impedance when a peripheral is off to avoid back-powering.

Startup: validate rails and configuration; initialize memory, time and logger; probe sensors and peripherals with deadlines; enable selected profile; enable LoRa TX only with regional settings. Provide independent watchdog/recovery for both MCUs and accessible ESP recovery plus RP2040 SWD/BOOTSEL strategy. RP2040 requires its own boot flash and clock/support circuitry; exact parts remain TBD ([RP2040 datasheet](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf)).

Original firmware scaffolding is deferred; [firmware plans](../firmware/README.md) describe boundaries without claiming a successful build.
