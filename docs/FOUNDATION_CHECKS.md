# Architecture validation record

Phase: Rev A architecture validation, reviewed 2026-09-11 UTC. These are documentation, file-format and host-model checks, not hardware qualification results.

| Check | Result |
| --- | --- |
| Required engineering and reference documents | Present; new evidence, power, mechanical/RF, stackup, ADS-B and GPIO records linked |
| Preliminary BOM | Exact 13-column schema, unique logical references and no empty fields |
| Locked part coverage | All eight selected MPNs present; no BME688 component row |
| Supplier identifiers | Verified C3037611 recorded; other unknown supplier IDs remain TBD |
| Relative Markdown links and code fences | Resolved/balanced in repository files |
| License provenance | Included SHA-256 values match retrieved official texts; MIT substitutions limited to holder/year |
| Power calculation | Revised totals, margin, cell-energy assumptions and runtime examples independently recomputed |
| ADS-B host fixture | Known DF17 decode/CRC, corruption rejection and sample-jitter tests pass |
| KiCad structure | KiCad 10.0.6 parsed the root and eight child sheets; ERC: 0 errors, 0 warnings |
| Whitespace / patch integrity | `git diff --check` clean at review |
| Scope | Gated `.kicad_sch` hierarchy only; no completed circuit, `.kicad_pcb`, Gerber, drill or legacy code/circuit import |

The tracked ERC report is [hardware/kicad/reports/erc-architecture.rpt](../hardware/kicad/reports/erc-architecture.rpt). It validates syntax and hierarchy only because the child sheets intentionally contain no electrical symbols yet. DRC is not applicable because no PCB exists. RP2040 target firmware is not implemented; the current ADS-B test is a host timing model.

Battery safety, RF performance, GNSS high-altitude operation, display connector/pinout, enclosure fit and 12-hour runtime remain unvalidated and are tracked in [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md). Downloaded reference inspection files remain outside the repository; only independently authored validation code and cited test fixtures are tracked.
