# StratosCore handoff

## Current state

Rev A has moved from foundation into architecture validation. Component evidence, an independent dual-bay power proposal, runtime update, mechanical/RF floorplan, JLC stack candidate, ADS-B frontend candidate, clean-room timing tests and a complete ESP32 GPIO allocation are present. The KiCad 10 hierarchy now includes the reviewed ESP32 compute entry and has zero ERC findings under the documented two-label temporary exception; no sheet or PCB is manufacturing-ready.

Read [DECISIONS.md](DECISIONS.md), [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md), [component evidence](COMPONENT_EVIDENCE.md), [power review](POWER_ARCHITECTURE_REVIEW.md) and [AGENTS.md](../AGENTS.md) first. Never assign the display footprint from the related C drawing or directly connect removable cells in parallel.

## Critical findings

- Orient `AFY240320A1-2.8INTH-C1` is selected for samples and has authorized-distributor stock, but its exact C1 drawing is still missing. Its schematic connector remains on hold.
- The ATGM332D-5NR32 manual confirms Galileo and 10 Hz maximum but imposes an 18 km altitude ceiling. `MAX-M10S-00B` is the documented 80 km replacement proposal and needs owner acceptance because D07 is locked.
- The recommended battery architecture uses two independent BQ25185 channels and an LTC4415 reverse-blocked OR. It needs owner and qualified electrical/battery review before schematic freeze or energizing.
- The 84 x 60 mm PCB/31 mm one-cell envelope is plausible. The two-cell enclosure needs about 37 mm; the original 32 mm maximum is not realistic with the reviewed display/cell stack.
- Revised two-cell FLIGHT runtime is 10.72 h under conservative allowances. At least 0.207 W raw average must be removed to reach 12 h with the example cells.
- The independent ADS-B candidate is BLB01/TA2003A/ADL5513/MCP6566. Host timing/CRC tests pass; analog sensitivity and RP2040 PIO/DMA remain unproven.
- The four locked sensors have exact voltage/package/interface evidence. ICM-42688-P is electrically suitable but currently has a material sourcing risk: the recent DigiKey listing had no stock and a 45-week lead time, while the recent LCSC snapshot was low-stock and expensive.

## Next engineering work

1. Obtain two labeled C1 display samples and its exact controlled drawing; identify the mating connectors and measure backlight/readability.
2. Record the owner's decision on the MAX-M10S GNSS proposal and the independent dual-bay power concept. Then perform a second-person battery schematic review.
3. Continue the non-RF schematic sheets from the reviewed ESP32 entry with verified manufacturer symbols; keep display, GNSS and power fault details explicitly gated. Restore the two temporary one-endpoint label checks as peer nets land, run KiCad ERC and review every exception.
4. Build RF evaluation coupons for BLB01/TA2003A/ADL5513/MCP6566 on the confirmed stack and implement RP2040 PIO/DMA plus the flow-controlled transport.
5. Print the 84 x 60 mm fit dummy and both rear covers; test antenna/pigtail, vent, button, SD, USB and battery service clearances.

## Validation boundary

Current tests prove documentation consistency and the host ADS-B timing fixture only. They do not prove battery safety, RF sensitivity, 12-hour autonomy, display pinout, antenna performance, enclosure fit or flight suitability. PCB placement/routing and manufacturing outputs remain prohibited until their gates close.
