# StratosCore

Compact open-source field, aviation, meteorological, navigation, and radio computer based on **ESP32-S3-WROOM-1-N16R8**.

**Status: Rev A architecture and validation phase.** A reviewed schematic hierarchy and host-side ADS-B timing fixture exist, but no completed circuit, PCB layout, hardware prototype, or manufacturing package exists yet. This is an experimental platform, **not a certified aviation instrument**, collision-avoidance system, or cockpit voice recorder.

## Rev A baseline

| Block | Baseline |
| --- | --- |
| Compute | ESP32-S3-WROOM-1-N16R8; 16 MB Flash, 8 MB PSRAM; Wi-Fi/BLE and module PCB antenna |
| User interface | 2.8-inch IPS, 320 x 240, capacitive touch; portrait/landscape; two physical buttons |
| LoRa | Directly integrated SX1262, 915 MHz class hardware, SPI, PCB U.FL; optional SMA pigtail |
| GNSS | ATGM332D-5NR32 remains locked, but its verified 18 km ceiling triggers a MAX-M10S replacement proposal |
| Motion/environment | ICM-42688-P, MMC5983MA, BMP581, SHT40; no baseline BME688 |
| ADS-B | Dedicated 1090 MHz RF frontend and RP2040 timing processor, feeding ESP32-S3 |
| Logging | Mandatory microSD and digital MEMS microphone provision for optional synchronized audio |
| Power | USB-C charging and native USB data target; removable 21700 cells; safe 1/2-cell topology open |
| Expansion | 3V3, GND, I2C, SPI with separate CS, UART, GPIO/IRQ |
| Construction | Four-layer PCB; approximately 80 x 60 mm footprint target; printed enclosure, 25-32 mm thickness target |

Potential uses include flight/vario instrumentation, traffic visualization, balloon experiments, weather stations, trackers, LoRa/MeshCore experiments, and portable or desktop logging. Hardware inclusion does not imply every feature runs in every power profile.

## Start here

1. [Product requirements](docs/PRODUCT_REQUIREMENTS.md) and [decision register](docs/DECISIONS.md).
2. [System architecture](docs/SYSTEM_ARCHITECTURE.md) and [block diagram](docs/BLOCK_DIAGRAM.md).
3. [Power options](docs/POWER_ARCHITECTURE_OPTIONS.md), [power budget](docs/POWER_BUDGET.md), and [RF architecture](docs/RF_ARCHITECTURE.md).
4. [Open questions](docs/OPEN_QUESTIONS.md), [preliminary BOM](bom/preliminary_bom.csv), and [reference/reuse register](references/REUSE_REGISTER.md).
5. [Engineering handoff and next five tasks](docs/ASTRA_HANDOFF.md); contributors must read [AGENTS.md](AGENTS.md).

The 12-hour runtime is a target, not a demonstrated result. The Orient C1 display is selected for sample validation, but its exact drawing/connector remains on hold. The locked GNSS was documented more fully and has an 18 km altitude ceiling, so a MAX-M10S replacement proposal awaits owner acceptance. Battery and ADS-B circuits remain prototype candidates pending the reviews described in [component evidence](docs/COMPONENT_EVIDENCE.md), [power review](docs/POWER_ARCHITECTURE_REVIEW.md) and [ADS-B validation](docs/ADSB_VALIDATION.md).

## Repository layout

```text
StratosCore/
|-- AGENTS.md
|-- README.md
|-- LICENSES/          Official texts and scope
|-- docs/              Requirements, architecture, decisions, handoff
|-- hardware/          KiCad, library, datasheet and reference placeholders
|-- bom/               Preliminary planning BOM; not an assembly BOM
|-- firmware/          ESP32, RP2040 and bring-up plans
|-- mechanical/        Enclosure and PCB dummy placeholders
|-- manufacturing/     Empty release areas and verification plans
`-- references/        Read-only research notes and reuse/license evidence
```

## Licensing

Original hardware, mechanical designs and hardware engineering documentation: **CERN-OHL-P-2.0**. Original firmware and its software documentation: **MIT**. See [license scope and provenance](LICENSES/README.md). Third-party work retains its own terms; no reference circuit or implementation code has been imported.
