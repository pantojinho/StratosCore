# Architecture validation record

Phase: Rev A pre-KiCad engineering closure, last reviewed 2026-09-21. These are documentation, file-format and host-model checks, not hardware qualification results.

| Check | Result |
| --- | --- |
| Required engineering and reference documents | Present; project status and documentation index now provide the controlled entry points |
| Preliminary BOM | Exact 13-column schema, 57 unique functional rows and no duplicate references; display, GNSS, USB-C/2S power, rail, audio, expansion, control, RF interconnect, RP2040 and microSD candidates synchronized |
| Locked part coverage | All nine baseline MPNs checked by the validation script are present; no BME688 component row |
| Supplier identifiers | Verified C3037611, C1850418 and C1975594 recorded; other unknown supplier IDs remain TBD |
| Relative Markdown links and code fences | 65 Markdown files checked; all relative links resolved and fences balanced |
| License provenance | Included SHA-256 values match retrieved official texts; MIT substitutions limited to holder/year |
| Power calculation | 2S energy, totals, margin and runtime independently recomputed; FLIGHT example remains 10.72 h |
| ADS-B host models | 24 tests pass: four sampled-capture tests plus 20 UART-record framing, validation and resynchronization tests; no UART/PIO/DMA throughput claim |
| Display evidence | Revision-J three-line/four-line straps, exact XF3M lands and AXC/LVC/TPS61169 starting circuits reviewed; controlled TFT-power/FPC clarification, samples, footprints and board tests remain gated |
| GNSS evidence | MAX-M10S exact application evidence plus preferred passive FXP611/U.FL/TPD1E0B04 proposal documented; RF/PDN review, fit, footprints and RF tests remain gated |
| Electrical compatibility | Candidate rail tree and complete voltage/address/boot/off-state matrix added; OPEN rows remain explicit and prevent Astra readiness |
| Footprint candidates | Nine files have recorded provenance and parse/export in KiCad. Corrected W25Q and TPD1E0B04 passed independent dimensional second passes on 2026-09-17; MAX-M10S, ICM-42688-P, MMC5983MA, BMP581, U.FL and ABM8 also have dimensional reviews. Every retained file still requires its recorded release/process checks |
| KiCad structure | KiCad 10.0.6 parsed the root/eight children, populated ESP32 compute entry and reviewed MMC5983MA/BMP581/SHT40 sensor subset; ERC rerun 2026-09-17: 0 violations |
| Whitespace / patch integrity | `git diff --check` clean at review |
| Scope | Gated `.kicad_sch` hierarchy only; no completed circuit, `.kicad_pcb`, Gerber, drill or legacy code/circuit import |

The tracked ERC report is [hardware/kicad/reports/erc-architecture.rpt](../hardware/kicad/reports/erc-architecture.rpt). It covers the root hierarchy, ESP32 compute entry and reviewed sensor subset. The only project-stage changes from the standard ERC profile are temporary ignores for `isolated_pin_label` and `single_global_label` while several architecture nets still have one endpoint. Restore these two severities to `warning` as peer sheets are populated; the report also enumerates KiCad's unchanged standard ignores. MMC5983MA and BMP581 still use logical pin carriers with no assigned footprint; their physical candidates passed dimensional reviews but remain gated until assembler/process review. DRC is not applicable because no PCB exists. RP2040 target firmware is not implemented; the current ADS-B test is a host timing model.

Battery safety, RF performance, GNSS high-altitude operation, display connectors/samples, enclosure fit and the owner's 8-hour primary-use runtime target remain unvalidated and are tracked in [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md). Downloaded reference inspection files remain outside the repository; only independently authored validation code and cited test fixtures are tracked.
