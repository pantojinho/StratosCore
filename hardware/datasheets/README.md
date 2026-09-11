# Primary technical source index

Research review date: 2026-09-11 UTC. This folder contains an index only, not redistributed manufacturer PDFs. Product pages identify primary resources but do not replace a verified exact-part pinout/package drawing before CAD. Recheck revisions at design freeze.

| Locked part | Primary source / reviewed evidence | Remaining verification |
| --- | --- | --- |
| ESP32-S3-WROOM-1-N16R8 | [Espressif module datasheet](https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.html), v1.8 page | Exact module drawing, antenna keepout, N16R8 memory/GPIO restrictions |
| SX1262 | [Semtech device and reference library](https://www.semtech.com/products/wireless-rf/lora-connect/sx1262) | Download/review current full datasheet and selected 915 MHz RF reference revision before schematic |
| ATGM332D-5NR32 | [Full user manual](https://datasheet.lcsc.com/lcsc/2206231830_ZHONGKEWEI-ATGM332D-5NR32_C3037611.pdf), 18 pages | Pin/package check, backup/PPS and antenna interface; 18 km altitude limit triggers replacement proposal |
| ICM-42688-P | [TDK product/document page](https://www.invensense.tdk.com/en-us/products/6-axis/icm-42688-p), current listing DS-000347 v1.9 | Retrieved v1.6 established provisional pin/electrical facts; obtain and delta-review v1.9 plus assembly guide before CAD entry; recheck supply risk |
| MMC5983MA | [MEMSIC Rev A](https://www.memsic.com/Public/Uploads/uploadfile/files/20220119/MMC5983MADatasheetRevA.pdf) | I2C/supply/package reviewed; verify SET/RESET, placement and calibrated heading on hardware |
| BMP581 | [Bosch BST-BMP581-DS004-13](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp581-ds004.pdf) | I2C ties, supplies, pressure range and fast-ramp resistor condition reviewed; vent/reflow and settings remain |
| SHT40-AD1B-R2 | [Sensirion SHT4x v7.3, June 2026](https://sensirion.com/media/documents/33FD6951/6A7C10A0/HT_DS_Datasheet_SHT4x_V7.3.pdf) | Exact 0x44 suffix selected; preserve no-copper center area and validate edge/vent thermal behavior |
| RP2040 | [Raspberry Pi datasheet](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf), build 2025-02-20 | Boot flash/clock/support, PIO budget, supply and SWD/programming design |
| Display candidate AFY240320A1-2.8INTH-C1 | [Orient catalogue](https://orientdisplay.com/our-products/color-tft/sunlight-readable-ips/) and [related C drawing](https://orientdisplay.com/wp-content/uploads/2020/12/AFY240320A1-2.8INTH-C-spec.pdf) | Exact C1 drawing and sample required; related drawing cannot define footprint |
| GNSS proposal MAX-M10S-00B | [Data sheet R07](https://beta-content.u-blox.com/sites/default/files/MAX-M10S_DataSheet_UBX-20035208.pdf) and [integration manual](https://content.u-blox.com/sites/default/files/MAX-M10S_IntegrationManual_UBX-20053088.pdf) | Owner acceptance, exact package drawing, antenna design and airborne configuration |
| BQ25185DLHR | [TI data sheet Rev B](https://www.ti.com/lit/ds/symlink/bq25185.pdf) | Per-bay settings, reverse-insertion stage, thermal layout and fault tests |
| LTC4415IDHC#PBF | [ADI data sheet](https://www.analog.com/media/en/technical-documentation/data-sheets/4415fa.pdf) | Current-limit values, ORing transient and thermal validation |
| ADS-B candidates | [BLB01](https://documents.berex.com/BLB01-V6.6.pdf), [TA2003A](https://www.taisaw.com/assets/PDF/TA2003A%20_Rev.1.0_.pdf), [ADL5513](https://www.analog.com/media/en/technical-documentation/data-sheets/adl5513.pdf), [MCP6566](https://ww1.microchip.com/downloads/aemDocuments/documents/MSLD/ProductDocuments/DataSheets/MCP6566-6R-6U-7-9-1.8V-Low-Power-Open-Drain-Output-Comparator-DS20002143G.pdf) | Exact orderable suffixes, RF simulation and conducted prototype results |

Unknown connectors, microphone, reverse-protection parts and regulators require new entries when selected. For each future local download record title, source URL, revision/date, relevant sections, SHA-256 and permission to redistribute. Supplier IDs remain TBD until independently matched to the full MPN.
