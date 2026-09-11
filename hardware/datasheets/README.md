# Primary technical source index

Research review date: 2026-09-11 UTC. This folder contains an index only, not redistributed manufacturer PDFs. Product pages identify primary resources but do not replace a verified exact-part pinout/package drawing before CAD. Recheck revisions at design freeze.

| Locked part | Primary source / reviewed evidence | Remaining verification |
| --- | --- | --- |
| ESP32-S3-WROOM-1-N16R8 | [Espressif module datasheet](https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.html), v1.8 page | Exact module drawing, antenna keepout, N16R8 memory/GPIO restrictions |
| SX1262 | [Semtech device and reference library](https://www.semtech.com/products/wireless-rf/lora-connect/sx1262) | Download/review current full datasheet and selected 915 MHz RF reference revision before schematic |
| ATGM332D-5NR32 | [Manufacturer exact product page](https://www.icofchina.com/daohang/danpin/2441.html), undated | Full module/command manual; Galileo/rate discrepancy; backup/PPS and antenna interface |
| ICM-42688-P | [TDK DS-000347 v1.6](https://product.tdk.com/system/files/dam/doc/product/sensor/mortion-inertial/imu/data_sheet/ds-000347-icm-42688-p-v1.6.pdf) | Electrical/package/initialization sections and operating-mode budget before CAD |
| MMC5983MA | [MEMSIC Rev A](https://www.memsic.com/Public/Uploads/uploadfile/files/20220119/MMC5983MADatasheetRevA.pdf) | Connection diagram, supply/CAP, SET/RESET and package checks |
| BMP581 | [Bosch BST-BMP581-DS004-13](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp581-ds004.pdf) | Mission pressure range, pinout, vent/reflow rules and measurement settings |
| SHT40 | [Sensirion product and linked SHT4x documentation](https://sensirion.com/products/catalog/SHT40) | Exact ordering suffix, handling and interface/package limits |
| RP2040 | [Raspberry Pi datasheet](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf), build 2025-02-20 | Boot flash/clock/support, PIO budget, supply and SWD/programming design |

Unknown LCD/touch, RF analog parts, microphone, charger, gauge, cell and connectors require new entries when selected. For each future local download record title, source URL, revision/date, relevant sections, SHA-256 and permission to redistribute. Supplier IDs remain TBD until independently matched to the full MPN.
