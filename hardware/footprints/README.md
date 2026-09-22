# Project footprint candidates

These KiCad footprint files are review candidates, not a manufacturing release.

Each file must have an exact ordering code, controlling manufacturer drawing, recorded source lineage and independent pad-by-pad review before it is used in the final PCB. See [digital/storage reviews](../../docs/FOOTPRINT_REVIEWS_DIGITAL.md) and [sensor/GNSS/RF reviews](../../docs/FOOTPRINT_REVIEWS_SENSORS_GNSS.md).

The MAX-M10S-00B, ICM-42688-P, MMC5983MA, BMP581, W25Q128JVSIQ and TPD1E0B04DPYR manufacturer-derived candidates are present and passed independent dimensional second passes. The corrected U.FL-R-SMT-1(60) copper/paste/board-cut-out rule and Abracon ABM8-272-T3 land geometry also completed independent dimensional reviews. Every mask/paste strategy remains subject to its recorded assembler gate. The BMP581 also carries Bosch's full no-mask opening and a conservative central no-trace/no-via rule area; final layout review must keep unnecessary routing out from under the complete body.

**2026-09-22 (DIG-04):** eight support-part candidates added from the official KiCad 10 standard library (SOT-23-5/-6, SC-70-5, VSSOP-8, TSSOP-24, X2QFN-12, VQFN-HR-10, VQFN-16 EP) covering TPS7A20, TPS22918, TPS61169, TXU0202, TCA9535, TUSB320LAI, TPS259474L and TPS62130A. All 17 project footprints parse and export in KiCad 10.0.6. Provenance and the remaining exact-MPN comparison gate are recorded in [FOOTPRINT_REVIEWS_DIGITAL.md](../../docs/FOOTPRINT_REVIEWS_DIGITAL.md). USB4105, BM12B, SKSCLCE010, ST1633I connector and T5838 acoustic land remain footprint-open with their controlling documents recorded.
