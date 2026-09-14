# KiCad engineering workspace

`StratosCore.kicad_sch` is the top-level architecture sheet. Its eight child sheets partition reviewed work and keep unresolved gates visible. `01_compute.kicad_sch` contains the reviewed ESP32-S3-WROOM-1-N16R8 entry, EN pull-up/reset capacitor, local 3V3 decoupling and the global nets defined in `INTERFACE_GPIO_MAP.md`. `04_sensors.kicad_sch` contains a reviewed subset: MMC5983MA and BMP581 pin maps use clearly marked logical carriers with no footprints, while SHT40-AD1B-R2 uses the exact KiCad symbol and manufacturer-derived footprint. Current TDK documents release the ICM-42688-P pin/application entry; its project footprint and independent CAD review remain pending. Other sheets still contain architecture notes rather than finished circuits. Add symbols and connections only when exact manufacturer documents and accepted decisions support them.

Current holds:

- display connector/footprint: exact Orient C1 revision-J specification is reviewed; independent FPC/connector transcription, 1.8 V translation, backlight design and samples remain;
- GNSS: MAX-M10S-00B accepted; exact CAD, supply/backup application and antenna circuit review remain;
- power: owner accepted two removable 21700 cells in 2S with one balanced charger; qualified battery/electrical review, exact holder, common protection, power path and regulators remain;
- ICM-42688-P physical CAD: create/review the project footprint and stencil geometry from DS-000347 v1.9 and AN-000393 v2.4;
- ADS-B: S-parameter simulation and conducted prototype measurements.

Use KiCad 10 for new edits. Run ERC from the repository root after every schematic change:

```powershell
& 'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe' sch erc --exit-code-violations --output hardware\kicad\reports\erc-architecture.rpt hardware\kicad\StratosCore.kicad_sch
```

KiCad 10.0.6 reported zero errors and zero warnings on 2026-09-11 for the hierarchy, compute sheet and reviewed sensor subset. The two project-stage changes from the standard ERC profile are `isolated_pin_label` and `single_global_label`: both remain temporarily ignored because several architecture nets still have one endpoint. Restore both diagnostics to `warning` as peer sheets gain their matching endpoints; the standard KiCad ignores remain listed in the report. The result proves connectivity consistency within the present scope; it does not qualify the circuits that remain gated. Retain reviewed reports under `hardware/kicad/reports/`. No PCB exists yet. Current preparation should leave Astra an evidence-complete execution list so its work is concentrated on KiCad entry, placement/routing and ERC/DRC rather than component research.
