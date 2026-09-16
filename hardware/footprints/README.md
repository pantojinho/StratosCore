# Project footprint candidates

These KiCad footprint files are review candidates, not a manufacturing release.

Each file must have an exact ordering code, controlling manufacturer drawing, recorded source lineage and independent pad-by-pad review before it is used in the final PCB. See [digital/storage reviews](../../docs/FOOTPRINT_REVIEWS_DIGITAL.md) and [sensor/GNSS/RF reviews](../../docs/FOOTPRINT_REVIEWS_SENSORS_GNSS.md).

The MAX-M10S-00B, ICM-42688-P, MMC5983MA and BMP581 manufacturer-derived candidates are present. ICM, MMC and BMP passed independent dimensional second passes; MAX still requires independent pad-by-pad review. Every mask/paste strategy remains subject to its recorded assembler gate. The BMP581 also carries Bosch's full no-mask opening and a conservative central no-trace/no-via rule area; final layout review must keep unnecessary routing out from under the complete body.
