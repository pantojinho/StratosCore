# Future bring-up sequence

Planning only. No executable test or energization procedure is released. Battery energization depends on accepted safety review.

1. Inspect assembled board and shorts; validate approved power subsystem with current-limited source and defined rails/load limits.
2. Verify ESP32 recovery, flash/PSRAM and RP2040 SWD/boot flash independently.
3. Probe sensor IDs/interfaces and GNSS UART, then verify timestamps, axes and failure recovery.
4. Enable panel/backlight/touch and both buttons only with verified connector and power sequence; test rotations.
5. Exercise microSD bounded writes, full/removed card, reset recovery and synchronized audio if populated.
6. Test SX1262 conducted into suitable RF load under selected regional profile; check reset/BUSY/IRQ behavior.
7. Exercise ADS-B capture with known inputs and host backpressure; then RF coexistence and long-duration complete-profile tests.

Record board revision, BOM population, firmware hash, instruments/settings, expected limits and actual results. Never mark plans as passed tests.
