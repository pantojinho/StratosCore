# StratosCore

StratosCore is an open-source portable field, aviation, meteorological, navigation and radio computer based on the **ESP32-S3-WROOM-1-N16R8**.

## Current status

**Rev A is in pre-KiCad hardware engineering closure.** Sol-class work is closing exact parts, electrical compatibility, application circuits, footprints, mechanical constraints and review evidence. The final Astra task is deliberately held until it can concentrate on KiCad schematic capture and PCB implementation.

| Complete | In progress | Externally blocked |
| --- | --- | --- |
| Product baseline and licensing | Display connectors/translation/driver; GNSS antenna and power choices | Display C1 samples and connector confirmation |
| MAX-M10S GNSS decision | Complete 2S charger/protection/regulator selection | Qualified electrical/battery review |
| Two removable 21700 cells in 2S decision | Review Molicel M50A cells, USB-C CC/input and remaining digital parts/footprints | RF performance and runtime measurements need prototypes |
| ESP32 compute sheet and GPIO allocation | Sensor CAD, LoRa/ADS-B RF, stackup and mechanical dummy | Final factory stack confirmation |
| KiCad hierarchy; latest ERC: zero violations | Orderable BOM and manufacturing inputs | |
| ADS-B host fixture: four tests passing | | |

There is no finished schematic, PCB layout, prototype or manufacturing package yet. Do not order boards from the current repository. See [project status](docs/PROJECT_STATUS.md) for the complete gate list.

## Rev A baseline

| Block | Baseline |
| --- | --- |
| Compute | ESP32-S3-WROOM-1-N16R8; 16 MB Flash, 8 MB PSRAM; Wi-Fi/BLE and module PCB antenna |
| User interface | 2.8-inch IPS 320 x 240 with capacitive touch; portrait/landscape; two physical buttons |
| GNSS | u-blox MAX-M10S-00B, selected for documented airborne modes to 80 km |
| Motion/environment | ICM-42688-P, MMC5983MA, BMP581 and SHT40-AD1B-R2 |
| LoRa | SX1262 directly integrated, 915 MHz class hardware, SPI and PCB U.FL; regional TX configuration required |
| ADS-B | Independent 1090 MHz receive chain with RP2040 timing processor |
| Logging/audio | Mandatory microSD and provision for an optional digital MEMS microphone |
| Power | USB-C target; two removable matched 21700 cells in 2S; one balanced charger and common protection direction |
| Expansion | 3V3, GND, I2C, SPI with separate CS, UART and GPIO/IRQ |
| Construction | Four-layer PCB; 84 x 60 mm planning outline; approximately 88 x 64 x 37 mm printed enclosure starting envelope |

Potential uses include flight/vario instruments, traffic visualization, balloon experiments, weather stations, trackers, LoRa/MeshCore experiments and portable logging. This experimental platform is not a certified aviation instrument, collision-avoidance system or cockpit voice recorder.

## Start here

1. [Project status: completed work and remaining gates](docs/PROJECT_STATUS.md)
2. [Engineering documentation index](docs/README.md)
3. [Locked decisions and accepted proposals](docs/DECISIONS.md)
4. [Open engineering questions](docs/OPEN_QUESTIONS.md)

[Astra final KiCad handoff](docs/ASTRA_HANDOFF.md) is intentionally marked **NOT READY**. It is not the current work queue.

## Repository layout

```text
StratosCore/
|-- AGENTS.md          Engineering and review rules
|-- README.md          Public project status and entry points
|-- docs/              Status, decisions and subsystem specifications
|-- bom/               Preliminary planning BOM; not orderable yet
|-- hardware/          KiCad project and primary-source index
|-- mechanical/        Enclosure and fit-study workspace
|-- manufacturing/     Release and production-test placeholders
|-- firmware/          Hardware-interface fixtures and future firmware
|-- references/        Read-only research and reuse/license records
`-- LICENSES/          Official license texts and scope
```

## Manufacturing path

The target is four-layer PCB fabrication and automated assembly at JLCPCB or a comparable Chinese PCBA supplier. Release requires an independently reviewed schematic and layout, clean ERC/DRC, confirmed stackup, exact orderable BOM, CPL, Gerbers/drill files, assembly drawings and a programming/production-test procedure. The owner must explicitly accept the manufacturing release before ordering.

## Licensing

Original hardware, mechanical designs and hardware engineering documentation use **CERN-OHL-P-2.0**. Original firmware and its software documentation use **MIT**. See [license scope and provenance](LICENSES/README.md). Third-party work retains its own terms.
