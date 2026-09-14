# Architecture validation record

Phase: Rev A pre-KiCad engineering closure, last reviewed 2026-09-14. These are documentation, file-format and host-model checks, not hardware qualification results.

| Check | Result |
| --- | --- |
| Required engineering and reference documents | Present; project status and documentation index now provide the controlled entry points |
| Preliminary BOM | Exact 13-column schema and 38 functional rows; MAX-M10S, 2S direction and exact C1 electrical evidence synchronized |
| Locked part coverage | All eight selected MPNs present; no BME688 component row |
| Supplier identifiers | Verified C3037611 recorded; other unknown supplier IDs remain TBD |
| Relative Markdown links and code fences | Resolved/balanced in repository files |
| License provenance | Included SHA-256 values match retrieved official texts; MIT substitutions limited to holder/year |
| Power calculation | 2S energy, totals, margin and runtime independently recomputed; FLIGHT example remains 10.72 h |
| ADS-B host fixture | Known DF17 decode/CRC, corruption rejection and sample-jitter tests pass |
| Display evidence | Exact AFY240320A1-2.8INTH-C1 revision-J electrical/pin tables reviewed; 1.8 V TFT logic and touch address 0x70 propagated; connectors/footprints remain gated |
| GNSS evidence | MAX-M10S-00B exact 18-pin map, supply/reset/backup limits, UART/PPS, RF input and manufacturer CAD sources reviewed; remaining circuit choices stay explicit |
| KiCad structure | KiCad 10.0.6 parsed the root/eight children, populated ESP32 compute entry and reviewed MMC5983MA/BMP581/SHT40 sensor subset; ERC rerun 2026-09-14: 0 errors, 0 warnings |
| Whitespace / patch integrity | `git diff --check` clean at review |
| Scope | Gated `.kicad_sch` hierarchy only; no completed circuit, `.kicad_pcb`, Gerber, drill or legacy code/circuit import |

The tracked ERC report is [hardware/kicad/reports/erc-architecture.rpt](../hardware/kicad/reports/erc-architecture.rpt). It covers the root hierarchy, ESP32 compute entry and reviewed sensor subset. The only project-stage changes from the standard ERC profile are temporary ignores for `isolated_pin_label` and `single_global_label` while several architecture nets still have one endpoint. Restore these two severities to `warning` as peer sheets are populated; the report also enumerates KiCad's unchanged standard ignores. MMC5983MA and BMP581 use logical pin carriers with no footprint; this avoids asserting an unverified physical CAD model. DRC is not applicable because no PCB exists. RP2040 target firmware is not implemented; the current ADS-B test is a host timing model.

Battery safety, RF performance, GNSS high-altitude operation, display connectors/samples, enclosure fit and 12-hour runtime remain unvalidated and are tracked in [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md). Downloaded reference inspection files remain outside the repository; only independently authored validation code and cited test fixtures are tracked.
