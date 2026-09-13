# Verification and production-test planning

No electrical tests have been executed. Define test points, fixture, current limits, instrumentation and acceptance values after schematic review.

| Area | Planned evidence |
| --- | --- |
| Power and battery | Short/leakage, rails under transient load, USB/charge limits, either cell reversed/missing/removed, 2S mismatch/balance and thermal protection |
| Compute | Boot/recovery, exact Flash/PSRAM capacity, RP2040 programming/watchdog |
| Sensors/GNSS | IDs, axes, calibration sanity, pressure/temperature response, GNSS fix/UTC and antenna behavior |
| UI | Pixel/touch tests, orientation mapping, two buttons, dim/sleep/wake |
| Logging/audio | Sustained writes, bounded latency, full/removed card, reset/power-loss behavior, synchronized sample timestamps |
| LoRa | Conducted RF power/frequency and RX, BUSY/IRQ handling, regional configuration gating |
| ADS-B | Known-frame acceptance/rejection, capture timing, analog dynamic range, queue/host saturation and contact validity |
| Complete assembly | RF coexistence, thermal drift, both cell populations, long-duration FLIGHT/BALLOON/DESKTOP and measured runtime |

Separate design qualification from fast production screening. Production records should identify serial/board revision, BOM variant, firmware hash, fixture/instrument calibration and measured pass/fail limits. ERC/DRC are design checks, not substitutes for these measurements.
