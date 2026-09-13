# StratosCore handoff

## Current state

Rev A has moved from foundation into architecture validation. Component evidence, an owner-approved 2S power direction, runtime update, mechanical/RF floorplan, JLC stack candidate, ADS-B frontend candidate, clean-room timing tests and a complete ESP32 GPIO allocation are present. The KiCad 10 hierarchy now includes the reviewed ESP32 compute entry plus the MMC5983MA/BMP581/SHT40 sensor subset and has zero ERC findings under the documented two-label temporary exception; no sheet or PCB is manufacturing-ready.

Read [DECISIONS.md](DECISIONS.md), [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md), [component evidence](COMPONENT_EVIDENCE.md), [power review](POWER_ARCHITECTURE_REVIEW.md) and [AGENTS.md](../AGENTS.md) first. Never assign the display footprint from the related C drawing or directly connect removable cells in parallel.

## Critical findings

- Orient `AFY240320A1-2.8INTH-C1` is selected for samples and has authorized-distributor stock, but its exact C1 drawing is still missing. Its schematic connector remains on hold.
- The owner accepted `MAX-M10S-00B` as the Rev A GNSS baseline on 2026-09-13. Its exact symbol/footprint, supply/backup application, antenna path and airborne configuration still need manufacturer-document review before entry.
- The owner rejected the independent BQ25185/LTC4415 approach and accepted two removable 21700 cells in 2S with one balanced charger and common protection. BQ25887 is the first charger candidate. A qualified electrical/battery reviewer must still accept the exact circuit and fault matrix before schematic commitment or energizing.
- The accepted two-cell enclosure needs about 37 mm with the current stack; the original 32 mm maximum is not realistic with the reviewed display/cell stack.
- Revised two-cell FLIGHT runtime is 10.72 h under conservative allowances. At least 0.207 W raw average must be removed to reach 12 h with the example cells.
- The independent ADS-B candidate is BLB01/TA2003A/ADL5513/MCP6566. Host timing/CRC tests pass; analog sensitivity and RP2040 PIO/DMA remain unproven.
- MMC5983MA and BMP581 pin maps and SHT40-AD1B-R2 entry are present in the sensor sheet. MMC5983MA/BMP581 deliberately have no physical footprint. ICM-42688-P DS-000347 v1.9 and AN-000393 v2.4 now release its pin/application entry; a project-specific footprint and independent CAD review remain because the generic KiCad LGA pads are larger than TDK's terminals. ICM sourcing also remains a material risk.

## Next engineering work

1. Use Sol to close evidence and exact part selections before Astra: obtain the C1 display drawing/two samples; verify MAX-M10S CAD/application; select the documented 2S holder, protection, charger application, buck rails, connectors and microphone.
2. Obtain a qualified second-person review of the complete 2S schematic plan and fault limits. Keep the power sheet gated until that review is recorded.
3. Complete the remaining evidence-backed logical circuits and project footprints, including ICM-42688-P, without speculative display, RF or power details. Run ERC and review every exception after each schematic change.
4. Finish ADS-B/RP2040 transport evidence, RF coupon requirements, stackup confirmation and mechanical dummy dimensions.
5. Hand Astra a decision-complete KiCad execution package: exact parts/datasheets, reviewed application circuits, footprints, net/interface map, placement constraints, stackup, test points and a short ordered checklist. Astra should perform KiCad entry, placement/routing and ERC/DRC execution rather than repeat product research.

## Validation boundary

Current tests prove documentation consistency and the host ADS-B timing fixture only. They do not prove battery safety, RF sensitivity, 12-hour autonomy, display pinout, antenna performance, enclosure fit or flight suitability. PCB placement/routing and manufacturing outputs remain prohibited until their gates close.
