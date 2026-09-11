# KiCad engineering workspace

`StratosCore.kicad_sch` is the top-level architecture sheet. Its eight child sheets partition reviewed work and keep unresolved gates visible; they contain architecture notes, not finished circuits. Add symbols and connections only when exact manufacturer documents and accepted decisions support them.

Current holds:

- display connector/footprint: exact Orient C1 drawing and sample;
- GNSS: owner decision on ATGM332D versus MAX-M10S;
- power: owner and qualified battery/electrical acceptance plus reverse-polarity details;
- ADS-B: S-parameter simulation and conducted prototype measurements.

Use KiCad 10 for new edits. Run ERC from the repository root after every schematic change:

```powershell
& 'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe' sch erc --exit-code-violations --output hardware\kicad\reports\erc-architecture.rpt hardware\kicad\StratosCore.kicad_sch
```

KiCad 10.0.6 reported zero errors and zero warnings on 2026-09-11. This result validates the file hierarchy only. Retain reviewed reports under `hardware/kicad/reports/`. No PCB exists yet.
