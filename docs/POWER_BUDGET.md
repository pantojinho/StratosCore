# Preliminary power budget

**All values below are engineering allowances, not measurements or promised component performance.** They describe average power delivered to loads, before battery-to-load conversion loss. ADS-B allowance includes RP2040, its flash and frontend; compute allowance includes ESP32 memory and wireless activity. Do not count either twice.

Revision 2026-09-14: the ESP32-S3, GNSS and ADS-B rows were re-derived from exact component datasheet figures recorded in the table notes and in the [power architecture review](POWER_ARCHITECTURE_REVIEW.md); the earlier rows used generic allowances. O13 closure arithmetic: the revised FLIGHT allowance removes 0.251 W (target: at least 0.207 W) and fits the two-cell 12-hour budget under the existing margin policy. All rows still require the measurement plan below before release.

| Block | BALLOON W | FLIGHT W | DESKTOP W | Basis to replace with measurement |
| --- | ---: | ---: | ---: | --- |
| ESP32 + Flash/PSRAM + wireless | 0.26 | 0.36 | 0.42 | ESP32-S3 datasheet v2.2 Table 5-9 at 240 MHz: modem-sleep dual-core 128-bit access 107.9 mA typ2, WAITI 47.6 mA typ2. BALLOON duty 70% WAITI / 30% active, FLIGHT 30% / 70%, DESKTOP FLIGHT basis plus 20% duty receive allowance (88 mA, Table 5-7). A uniform +20% factor covers the R8 PSRAM/flash note in Section 5.6.2. Wi-Fi TX bursts to 340 mA remain peak-transient items, not average rows |
| LCD + backlight + touch | 0.01 | 0.625 | 0.625 | Exact Orient C1 revision-J module figure; 0.60 W backlight dominates; sample and brightness profile still unmeasured |
| GNSS | 0.027 | 0.027 | 0.027 | MAX-M10S-00B datasheet UBX-20035208 Table 15 at 3.0 V: acquisition 13 mA + V_IO 2.3 mA, continuous tracking 5 mA + 2.3 mA; duty 20% acquisition / 80% tracking. Replaces the superseded ATGM-class allowance |
| Four sensors | 0.02 | 0.03 | 0.03 | Sample rate/filter/heater policy not fixed |
| ADS-B complete subsystem | 0.00 | 0.46 | 0.46 | Analog: two BLB01 at 27 mA and ADL5513 at 31 mA from 3.0 V plus MCP6566 IQ 0.1 mA maximum at 3.3 V (datasheet electrical characteristics). Digital: RP2040 datasheet Table 637 worst-case IOVDD 35.5 mA, DVDD 16.6 mA referred to the 3.3 V input through the internal LDO, flash active-read allowance 20 mA. Unmeasured; protocol-stage block reviews must confirm |
| SX1262 and RF support | 0.02 | 0.03 | 0.03 | Duty-cycle allowance only; no universal TX settings |
| microSD | 0.03 | 0.10 | 0.10 | Card and batching-dependent; write peaks much larger |
| Microphone/audio increment | 0.00 | 0.03 | 0.03 | Audio enabled for conservative FLIGHT/DESKTOP example |
| Gauge, control and other loads | 0.02 | 0.03 | 0.04 | PMIC idle, enables and miscellaneous allowances |
| **Load total** | **0.387** | **1.684** | **1.822** | Sum of above |
| **With 25% design margin** | **0.484** | **2.105** | **2.278** | Used in runtime examples |

## Energy and runtime arithmetic

Example only: one 5.0 Ah cell at 3.6 V nominal gives 18 Wh nameplate energy. Molicel `INR-21700-M50A` now matches this basis as the first sample candidate, but the cell is **not locked**. Assume 80% usable energy for capacity reserve/temperature/aging combined and 90% conversion efficiency. Delivered usable energy = 18 x 0.80 x 0.90 = **12.96 Wh per cell**.

`runtime_h = cell_count x nominal_V x capacity_Ah x usable_fraction x efficiency / margin_adjusted_load_W`

| Scenario | One example cell | Two example cells | 12 h implication |
| --- | ---: | ---: | --- |
| BALLOON | 26.78 h | 53.55 h | Arithmetic suggests margin; actual duty and cold operation remain untested |
| FLIGHT | 6.16 h | 12.31 h | Revised 2026-09-14: the two-cell estimate now exceeds 12 h by about 0.31 h, but the 0.044 W raw-budget headroom is thinner than every allowance uncertainty; measurement, not arithmetic, closes PR13 |
| DESKTOP, battery equivalent | 5.69 h | 11.38 h | Intended use is USB powered; charging power is additional |

Two-cell energy uses the accepted 2S direction: 7.2 V nominal at 5 Ah has the same 36 Wh nameplate energy as two 3.6 V, 5 Ah cells counted separately. It assumes a matched, qualified pair and does not include unmeasured 2S charger, protection or buck losses beyond the general efficiency allowance.

For 12 h, maximum margin-adjusted delivered load is **1.08 W** with one example cell, or **2.16 W** with two. Under the separate 25% load margin, raw design budgets become **0.864 W** and **1.728 W** respectively. The revised FLIGHT allowance of 1.684 W now fits the two-cell raw budget with 0.044 W to spare, and the required margin-adjusted nameplate energy of 2.105 x 12 / (0.80 x 0.90) = **35.08 Wh** fits 36 Wh. This closure is arithmetic only: it inherits the unmeasured 80% usable-energy and 90% efficiency assumptions, and a real 12 h discharge profile remains the PR13 evidence.

This is a sensitivity analysis, not evidence that a larger cell alone solves runtime. Measure display brightness, ADS-B power, actual conversion efficiency and cold-cell capacity first. Every additional continuous 0.1 W costs 1.2 Wh over 12 h at the loads.

## Peaks, thermal load and measurement plan

Regulators must support concurrent RF bursts, SD writes, backlight startup and CPU transients. Do not size them from averages. The current TPS61169 proposal reserves at least 250 mA peak on `3V3_MAIN` for backlight conversion alone, pending sample efficiency/transient measurements; that reserve is not an extra average-power row. Record datasheet maximum/peak envelopes and scope current/voltage at both battery and rails; define permitted rail droop only after all part limits are known. SX1262 antenna power is not the same as battery input power.

Charging a 2S pack to 8.4 V from nominal 5 V USB requires a boost charger. Input current, inductor current, switch loss, cell-balancing heat and system load while charging must be calculated from the selected circuit and then measured. The BQ25887 candidate supports up to 2 A charge current, but no charge rate is selected. See [power options](POWER_ARCHITECTURE_OPTIONS.md).

Measure each domain individually, then concurrent FLIGHT load; repeat with USB charging, low battery and expected ambient limits. Run a full 12 h profile with logged brightness/radio settings, capacity, cutoff and resets. Measure converter efficiency over the 2S discharge range; update this table with measured min/typ/max and uncertainty. The 90 mW GNSS row remains a conservative allowance until MAX-M10S-00B with the proposed passive no-bias antenna path is measured.
