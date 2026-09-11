# KiCad engineering workspace

`StratosCore.kicad_sch` is the top-level architecture sheet. Its eight child sheets partition reviewed work and keep unresolved gates visible. `01_compute.kicad_sch` now contains the reviewed ESP32-S3-WROOM-1-N16R8 entry, EN pull-up/reset capacitor, local 3V3 decoupling and the global nets defined in `INTERFACE_GPIO_MAP.md`. The other sheets still contain architecture notes rather than finished circuits. Add symbols and connections only when exact manufacturer documents and accepted decisions support them.

Current holds:

- display connector/footprint: exact Orient C1 drawing and sample;
- GNSS: owner decision on ATGM332D versus MAX-M10S;
- power: owner and qualified battery/electrical acceptance plus reverse-polarity details;
- ADS-B: S-parameter simulation and conducted prototype measurements.

Use KiCad 10 for new edits. Run ERC from the repository root after every schematic change:

```powershell
& 'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe' sch erc --exit-code-violations --output hardware\kicad\reports\erc-architecture.rpt hardware\kicad\StratosCore.kicad_sch
```

KiCad 10.0.6 reported zero errors and zero warnings on 2026-09-11 for the hierarchy plus the compute sheet. The two project-stage changes from the standard ERC profile are `isolated_pin_label` and `single_global_label`: both are temporarily ignored because the new global nets have one endpoint until their peer sheets are populated. Restore both diagnostics to `warning` as those sheets gain the matching endpoints; the standard KiCad ignores remain listed in the report. The result proves connectivity consistency within the present scope; it does not qualify the circuits that remain gated. Retain reviewed reports under `hardware/kicad/reports/`. No PCB exists yet.
