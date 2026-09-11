# Legacy project study

Reviewed read-only on 2026-09-11 UTC. Commit-pinned links make the observations reproducible. These projects are references, not the StratosCore starting design.

## HAT project

Repository: [ESP32-S3 High Precision Avionics HAT](https://github.com/pantojinho/ESP32-S3-High-Precision-Avionics---Advanced-Meteorological-HAT--GPS---LoRa/tree/ede42aea0a62b0821dacf69886a06be7529f59e8).

Reviewed [README](https://github.com/pantojinho/ESP32-S3-High-Precision-Avionics---Advanced-Meteorological-HAT--GPS---LoRa/blob/ede42aea0a62b0821dacf69886a06be7529f59e8/README.md), [PINMAP](https://github.com/pantojinho/ESP32-S3-High-Precision-Avionics---Advanced-Meteorological-HAT--GPS---LoRa/blob/ede42aea0a62b0821dacf69886a06be7529f59e8/docs/hardware/PINMAP.md) and [pins.h](https://github.com/pantojinho/ESP32-S3-High-Precision-Avionics---Advanced-Meteorological-HAT--GPS---LoRa/blob/ede42aea0a62b0821dacf69886a06be7529f59e8/src/config/pins.h).

The HAT depends on a Waveshare 1.64-inch baseboard, QMI8658 and BME688, external GNSS and inherited battery rails. It illustrates separate LoRa/SD buses and nonblocking services, but does not establish StratosCore's standalone power or enclosure design. No repository-wide license was found in its tree/API metadata; reuse permission is unestablished.

Its pin table and header agree on I2C 47/48, GNSS 44/43, SD 38-41 and seven LoRa signals. These are historical observations only. The header labels the AMOLED RM67162; StratosBrain labels CO5300. The GPS header aliases in the code use host-side TX/RX names while the connector documentation describes device-side TXD/RXD, an ambiguity to avoid with explicit signal direction. No original file was changed.

## StratosBrain S3

Repository: [StratosBrain_S3](https://github.com/pantojinho/StratosBrain_S3/tree/943de16ff35f0b5c77d04f515245bce8342be79b).

Reviewed [README and stability summary](https://github.com/pantojinho/StratosBrain_S3/blob/943de16ff35f0b5c77d04f515245bce8342be79b/README.md) and [MIT license](https://github.com/pantojinho/StratosBrain_S3/blob/943de16ff35f0b5c77d04f515245bce8342be79b/LICENSE). Original software reuse can be permitted under MIT with notices; bundled dependencies/assets still need individual review. Nothing imported.

Useful concepts: separate flight/weather/comms views, CSV logging and local web status. Reported dashboard degradation despite continued local updates motivates bounded service workloads, smaller status responses and long-duration UI/network tests. These are lessons, not independently reproduced test results.

## Conflicts with StratosCore baseline

| Legacy assumption | StratosCore resolution |
| --- | --- |
| Waveshare 1.64-inch AMOLED, CO5300/FT3168; HAT header mentions RM67162 | 2.8-inch 320 x 240 IPS/PCAP; exact controllers open; do not inherit driver or footprint |
| QMI8658 | Locked ICM-42688-P |
| BME688 / BMM350 | Locked SHT40 + BMP581 / MMC5983MA |
| AT6558R or generic external GPS connector | Locked ATGM332D-5NR32; verified module interface and separate antenna design |
| StratosBrain E220/E32 UART LoRa | Direct PCB SX1262 SPI; HAT's SX1262/CC68 module assumptions also require reference redesign |
| Inherited baseboard power and pins | New USB-C/removable-cell architecture and full resource allocation |
| Legacy removal of MAX17048 | Fuel gauge required for study here; exact device remains open |
| No integrated RP2040 ADS-B baseline in these descriptions | Dedicated RF/decoder core feature in StratosCore Rev A |

Only sampled documentation and the HAT pin header were reviewed; no full legacy firmware correctness, CAD, BOM or electrical audit is claimed. Upstream-local rules and old "locked" decisions do not govern StratosCore.
