# StratosCore handoff

## Current state

Rev A foundation only. Requirements, architecture, power options/budget, preliminary BOM, references and official licenses are present. No KiCad schematic/board, firmware build, electrical prototype or manufacturing outputs exist. No legacy repository was modified. Owner authorized direct publication to `main`, without PR, for this foundation.

Read [DECISIONS.md](DECISIONS.md), [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md) and [AGENTS.md](../AGENTS.md) first. Locked hardware must remain unchanged without an accepted proposal. Never assign a display footprint from an assumed panel or directly parallel removable cells.

## Critical findings

- Exact GNSS manufacturer listing does not confirm Galileo or a configurable higher output rate; keep ATGM332D-5NR32 pending evidence.
- ADSBee GPL-3.0 and avBadge's unestablished hardware license prohibit treating published work as freely relicensable. No code/circuit was copied.
- Legacy pin maps and AMOLED/sensor/UART-LoRa drivers conflict with this baseline. avBadge uses SoC TV input/DSP, not RP2040.
- Two illustrative 5 Ah cells yield 11.15 h FLIGHT under conservative allowances; 12 h is unproven.
- GPIO/serial-resource budget and 21700/display/antenna mechanical fit remain unresolved.

## Next five engineering tasks, in order

1. **Close component evidence and sourcing gaps.** Obtain exact LCD/touch sample/drawings and GNSS variant/commands; verify locked-part datasheets/orderable suffixes; gather dated quotes and audit firmware/reuse licenses. Record proposals for unmet requirements without changing baseline.
2. **Review power architecture and runtime feasibility.** Compare one/two-bay circuits and cell/holder candidates, choose charger/gauge candidates, refine rail/peak/thermal budget, and complete explicit battery safety review before topology freeze.
3. **Complete mechanical/RF floorplan and manufacturer stackup study.** Fit both enclosure variants, establish antenna and environmental-sensor zones, connector access and impedance constraints. No routing yet.
4. **Prove ADS-B frontend and timing independently.** Evaluate manufacturer-backed RF chain with RP2040 capture, known frames and coexistence; specify ESP32 link, timestamping, validation and overflow behavior. Resolve reuse licensing before importing code.
5. **Freeze reviewed interfaces and begin schematic/bring-up planning.** Complete GPIO/bus/address/rail map, then create verified KiCad symbols and schematic blocks with ERC and a testable BOM. Placement/routing requires the preceding reviews; manufacturing later requires DRC and release review.

## Validation boundary

Foundation checks cover file/link/BOM/license/decision integrity and power arithmetic only. ERC/DRC and firmware tests are not applicable yet. Stop after this phase; do not interpret placeholders as authorization to continue to PCB routing.
