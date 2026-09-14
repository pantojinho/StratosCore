# Product requirements

StratosCore Rev A is a compact experimental field computer. This document expresses targets; none is a measured performance claim. [DECISIONS.md](DECISIONS.md) controls component choices.

| ID | Requirement | Verification / completion evidence |
| --- | --- | --- |
| PR01 | Use ESP32-S3-WROOM-1-N16R8 with integrated PCB antenna | Exact module ordering code, datasheet, flash/PSRAM bring-up |
| PR02 | 2.8-inch IPS, 320 x 240, capacitive touch, both orientations | Vendor drawing, sample test, rotation/touch corner tests |
| PR03 | Two accessible physical buttons | Debounce, boot behavior, enclosure access in both orientations |
| PR04 | Integrated SX1262 SPI, 915 MHz hardware, U.FL | Semtech reference review, conducted RF and regional configuration tests |
| PR05 | MAX-M10S-00B UART multi-GNSS navigation suitable for balloon altitude | Cold/warm-start, airborne-mode, NMEA/UBX, constellation and 80 km boundary review/tests |
| PR06 | ICM-42688-P + MMC5983MA + BMP581 + SHT40 | Device identity, axes, calibration, pressure and thermal tests |
| PR07 | Core 1090 MHz ADS-B with RP2040 and dedicated frontend | Known frames, invalid-frame rejection, RF replay and coexistence tests |
| PR08 | Traffic model with ICAO, callsign, lat/lon, altitude, velocity, track/heading when available | Field validity, per-field age, CPR and ownship-relative display tests |
| PR09 | Mandatory microSD black-box-style data logging | Long-duration writes, removal/full-card errors, bounded queues, power interruption |
| PR10 | Digital MEMS microphone provision, optional synchronized logging | Audio timestamp mapping, throughput, clock drift, dropped-block flags |
| PR11 | USB-C charging, operation while charging, native data target | Source-current limits, role/orientation, brownout, thermal and fault tests |
| PR12 | Two removable matched 21700 cells in 2S with one balanced charger and common protection | Qualified battery review including mismatch, missing/reversed cell, removal, short, thermal and charge/discharge faults |
| PR13 | Approximately 12 h normal portable runtime | Profile, brightness, battery, temperature and radios documented in discharge test |
| PR14 | 3V3/GND + I2C + SPI/CS + UART + GPIO/IRQ expansion | Pin budget, voltage/current limits, connector and recovery tests |
| PR15 | Four-layer PCB, approximately 80 x 60 mm target footprint | Manufacturer stackup and mechanical fit review; final dimensions open |
| PR16 | Printed enclosure for display and two 21700 cells, approximately 37 mm starting thickness | Exact holder/panel/cable tolerances, printed dummy and sample fit |
| PR17 | Thermal and RF isolation | Temperature bias tests and receiver degradation during each aggressor state |
| PR18 | Open-source provenance and manufacturing readiness | License register; BOM/footprint audits; later ERC/DRC and assembly review |

## Use profiles

| Profile | Display / wireless | Navigation and sensors | ADS-B / logging |
| --- | --- | --- | --- |
| BALLOON | Display mostly off; Wi-Fi off; BLE optional; periodic LoRa | GNSS and sensors active at profile-selected rates | ADS-B optional/off; periodic telemetry log; audio normally off |
| FLIGHT | Display active; Wi-Fi normally off; BLE/LoRa optional | GNSS, pressure/vario and motion active | ADS-B active; continuous event/telemetry logs; audio optional |
| DESKTOP | USB powered; display and Wi-Fi active | All sensors available | ADS-B optional; all logging services available |

Operating altitude, minimum pressure, temperature range, ingress resistance, sunlight brightness, mass, ADS-B sensitivity/range and acceptable log loss are not specified yet. In particular, a balloon use case does not guarantee the BMP581 remains within its specified pressure range throughout ascent. Define the mission envelope and flag out-of-range measurements.

## Data and behavior

Logs must be able to represent UTC/time validity, monotonic timestamp, GNSS fix/position/altitude, barometric altitude with reference pressure, pressure, ambient temperature/humidity, accelerometer, gyroscope, magnetic vector/derived heading, LoRa RX/TX, ADS-B contacts, battery state and system events. Include units, schema/firmware version, calibration ID and data validity. Do not replace missing readings with plausible zeroes.

Microphone logging is optional and experimental; it is not a certified cockpit voice recorder. ADS-B is receive-only, incomplete traffic information; no certified navigation or collision-avoidance claim. MeshCore companion, messaging, tracker and repeater are firmware objectives subject to porting and licensing, not working features.

## Current architecture acceptance

All requested paths exist, locked parts and proposals are explicit in the preliminary BOM, unknown supplier IDs remain TBD, diagrams are conceptual, references have license assessments and official license texts are present. [Project status](PROJECT_STATUS.md) lists ordered work; [Astra handoff](ASTRA_HANDOFF.md) is reserved for final KiCad execution. A valid gated KiCad hierarchy and host ADS-B timing fixture exist. No completed circuit, PCB routing or manufacturing release is included.
