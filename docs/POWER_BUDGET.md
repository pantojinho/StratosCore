# Preliminary power budget

**All values below are engineering allowances, not measurements or promised component performance.** They describe average power delivered to loads, before battery-to-load conversion loss. ADS-B allowance includes RP2040, its flash and frontend; compute allowance includes ESP32 memory and wireless activity. Do not count either twice.

| Block | BALLOON W | FLIGHT W | DESKTOP W | Basis to replace with measurement |
| --- | ---: | ---: | ---: | --- |
| ESP32 + Flash/PSRAM + wireless | 0.12 | 0.40 | 0.65 | CPU duty, Wi-Fi/BLE state and clock not fixed |
| LCD + backlight + touch | 0.01 | 0.625 | 0.625 | Orient candidate related drawing; exact C1 sample and brightness profile still unmeasured |
| GNSS | 0.09 | 0.09 | 0.09 | Planning allowance near vendor listing; acquisition/antenna bias still unresolved |
| Four sensors | 0.02 | 0.03 | 0.03 | Sample rate/filter/heater policy not fixed |
| ADS-B complete subsystem | 0.00 | 0.60 | 0.60 | Two 3 V BLB01 stages, ADL5513, comparator, RP2040/support allowance; unmeasured |
| SX1262 and RF support | 0.02 | 0.03 | 0.03 | Duty-cycle allowance only; no universal TX settings |
| microSD | 0.03 | 0.10 | 0.10 | Card and batching-dependent; write peaks much larger |
| Microphone/audio increment | 0.00 | 0.03 | 0.03 | Audio enabled for conservative FLIGHT/DESKTOP example |
| Gauge, control and other loads | 0.02 | 0.03 | 0.04 | PMIC idle, enables and miscellaneous allowances |
| **Load total** | **0.31** | **1.935** | **2.195** | Sum of above |
| **With 25% design margin** | **0.3875** | **2.41875** | **2.74375** | Used in runtime examples |

## Energy and runtime arithmetic

Example only: one 5.0 Ah cell at 3.6 V nominal gives 18 Wh nameplate energy. Cell MPN/capacity is **not selected**. Assume 80% usable energy for capacity reserve/temperature/aging combined and 90% conversion efficiency. Delivered usable energy = 18 x 0.80 x 0.90 = **12.96 Wh per cell**.

`runtime_h = cell_count x nominal_V x capacity_Ah x usable_fraction x efficiency / margin_adjusted_load_W`

| Scenario | One example cell | Two example cells | 12 h implication |
| --- | ---: | ---: | --- |
| BALLOON | 33.45 h | 66.89 h | Arithmetic suggests margin; actual duty and cold operation remain untested |
| FLIGHT | 5.36 h | 10.72 h | Neither example reaches 12 h with chosen allowances |
| DESKTOP, battery equivalent | 4.72 h | 9.45 h | Intended use is USB powered; charging power is additional |

Two-cell energy uses the accepted 2S direction: 7.2 V nominal at 5 Ah has the same 36 Wh nameplate energy as two 3.6 V, 5 Ah cells counted separately. It assumes a matched, qualified pair and does not include unmeasured 2S charger, protection or buck losses beyond the general efficiency allowance.

For 12 h, maximum margin-adjusted delivered load is **1.08 W** with one example cell, or **2.16 W** with two. Under the separate 25% load margin, raw design budgets become **0.864 W** and **1.728 W** respectively. FLIGHT's 1.935 W allowance exceeds the two-cell raw budget by **0.207 W**. Required nameplate energy at the margin-adjusted FLIGHT load is 2.41875 x 12 / (0.80 x 0.90) = **40.31 Wh**, versus 36 Wh for two example cells.

This is a sensitivity analysis, not evidence that a larger cell alone solves runtime. Measure display brightness, ADS-B power, actual conversion efficiency and cold-cell capacity first. Every additional continuous 0.1 W costs 1.2 Wh over 12 h at the loads.

## Peaks, thermal load and measurement plan

Regulators must support concurrent RF bursts, SD writes, backlight startup and CPU transients. Do not size them from averages. Record datasheet maximum/peak envelopes and scope current/voltage at both battery and rails; define permitted rail droop only after all part limits are known. SX1262 antenna power is not the same as battery input power.

Charging a 2S pack to 8.4 V from nominal 5 V USB requires a boost charger. Input current, inductor current, switch loss, cell-balancing heat and system load while charging must be calculated from the selected circuit and then measured. The BQ25887 candidate supports up to 2 A charge current, but no charge rate is selected. See [power options](POWER_ARCHITECTURE_OPTIONS.md).

Measure each domain individually, then concurrent FLIGHT load; repeat with USB charging, low battery and expected ambient limits. Run a full 12 h profile with logged brightness/radio settings, capacity, cutoff and resets. Measure converter efficiency over the 2S discharge range; update this table with measured min/typ/max and uncertainty. The 90 mW GNSS row remains a conservative allowance until MAX-M10S-00B plus antenna-bias power is measured.
