# BMP581 Indicative Pressure and Vario Validation Plan

Status: **PROPOSED TEST PLAN; no sensor or board measurements are claimed.** The locked BMP581 remains an indicative secondary pressure/altitude/vario sensor under D08, D25 and D29. This document defines the reviewable validation plan and sample validity contract; it does not establish measured performance or qualify the device as a flight instrument.

Reviewed: 2026-09-22.

## Source basis and operating envelope

Primary component source: Bosch Sensortec, [BMP581 datasheet BST-BMP581-DS004-13, revision 1.13, released April 2025](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp581-ds004.pdf), reviewed 2026-09-22. Use the exact Bosch source for design decisions. Relevant sections are §2/Table 1 (pressure measurement range and pressure accuracy conditions), §2/Table 2 (temperature performance), §4.3 (power modes), §4.4 (measurement enable, oversampling and IIR filtering), §4.5 (data registers and shadowing), §4.7.2 (data-ready and pressure out-of-range interrupt sources), §6.2.5/Figure 28 (fast supply ramp application), and §10 (package drawing). The exact package and board application remain governed by the existing component evidence and CAD review.

For reference only, the U.S. National Weather Service [standard-atmosphere table](https://www.weather.gov/index.php/ama/conversions), reviewed 2026-09-22, lists approximately 697 hPa at 10,000 ft and 301 hPa at 30,000 ft. These are standard-atmosphere examples, not expected field pressure at a given geometric altitude: weather and local pressure reference change the relationship. The 10,000 ft example is within the BMP581 300–1250 hPa measurement range. The 30,000 ft example is only about 1 hPa above the 300 hPa lower limit, so it has essentially no margin for weather, port error or transient pressure excursions and is not a coverage claim.

Bosch specifies pressure measurement across 300–1250 hPa and pressure measurement over -40 to +85 °C. Its Table 1 gives typical absolute pressure accuracy of ±30 Pa across 300–1100 hPa and -5 to +65 °C; that typical figure is not a guaranteed maximum and does not apply outside its stated temperature conditions. The NWS standard-atmosphere temperature at 10,000 ft is about -4.8 °C, near the lower edge of the stated accuracy-temperature interval; this is outside-air reference temperature, not the unknown BMP581 board temperature. Board temperature, thermal gradients and pressure-port response therefore remain measured inputs to any performance claim. At 30,000 ft the standard outside-air temperature is about -44.5 °C, below the sensor operating minimum; exposed operation there is out of range even before considering pressure margin.

## Validation stages

### Before Astra / before PCBA

Close only design and software-contract items that can be established without a physical sensor:

- Confirm the selected sensor remains the locked BMP581, the existing manufacturer-derived application/footprint remains the candidate, and the 100 kHz shared I2C policy is used. Do not revise the part, schematic, footprint or pin map through this plan.
- Review the exact BOM ordering code, rail ramp behavior, bus address, I2C pull-ups, data-ready/status handling, pressure and temperature conversion, unit scaling, pressure validity bounds, stale-data handling, and logged calibration/reference metadata against the current Bosch datasheet and project interface documents.
- Add host-side tests using synthetic samples for range boundaries, startup/not-ready, sensor/status/bus faults, stale samples, missing reference pressure, conversion overflow, and positive/negative vario sign. These tests validate software behavior only; they do not validate the sensor, pressure path, accuracy, temperature response or board layout.
- Record the intended ODR, oversampling, IIR settings and effective vario window as configuration inputs. Select these from noise/response tradeoffs during bench work; do not assert an unmeasured noise floor or response time before PCBA.
- Keep assembler approval for lands/mask/paste, under-body no-route compliance, and the existing mechanical fit/routing reviews as separate release gates.

### After PCBA: pressure and vario bench characterization

Use at least one assembled board and a calibrated pressure reference or pressure controller with documented uncertainty and calibration status. A controlled chamber is needed to exercise the realistic 10,000 ft pressure case; do not infer it from an altitude calculator or a hand pump without a pressure reference. Proposed sequence:

1. Record board revision, sensor lot/marking, firmware/configuration, supply rails, chamber/reference model and calibration, reference uncertainty, ambient and BMP581-reported temperature, setup photographs, test date, and operator. Preserve raw timestamped pressure, temperature, status/validity flags and reference readings.
2. At ambient pressure, verify device identity, stable communication, data-ready behavior, pressure/temperature register handling, and repeatability after power cycles. Confirm timestamps and sample age are monotonic and faults become invalid samples instead of plausible numeric readings.
3. With pressure changed slowly, characterize ascending and descending steps from local ambient down through approximately 697 hPa (the NWS 10,000 ft standard-atmosphere example), then return to ambient. Include intermediate steps sufficient to reveal hysteresis, lag, jumps, or chamber/port leaks. Record actual reference pressure; use the 697 hPa point as a test point, not as a universal 10,000 ft mapping.
4. Compare BMP581 pressure to the calibrated reference over repeated stabilized points. Report error, repeatability, hysteresis, settling behavior, reference uncertainty and board temperature separately. Do not label a typical datasheet value as the acceptance limit. Any numeric project acceptance band remains TBD until reviewed against reference uncertainty, board temperature and intended indicative use.
5. At constant reference pressure, capture baseline noise and vario output at each candidate filter/window configuration. Then apply repeatable pressure ramps or steps in both directions; measure sign, noise, lag, overshoot and settling. Choose a documented configuration only after this data is reviewed. Keep vario marked indicative.
6. Repeat a smaller run after a full power cycle and, if practical, after a representative operating-temperature soak once a board-temperature range has been decided. Keep within the BMP581 specified operating temperature; do not use the chamber to imply qualification outside it.
7. Exercise invalid-data handling by disconnecting or faulting the sensor bus in a controlled bench setup, suppressing data-ready updates, forcing stale timestamps, and using validly obtained samples outside the configured reference/calibration state. Verify display/log status and recovery behavior. No environmental or pressure-limit abuse is needed to test firmware gating.

The optional 30,000 ft exploratory point is not part of the acceptance plan. If later explored, approximately 301 hPa is too close to Bosch's lower measurement limit for a useful operating guarantee; any sensor pressure below 300 hPa or temperature outside -40 to +85 °C must be reported out of range. Do not present a 30,000 ft reading as supported performance.

## Pressure path and temperature caveats

The sensor needs representative static pressure at the enclosure port. Follow the [mechanical/RF floorplan](MECHANICAL_RF_FLOORPLAN.md): the planned enclosure static vent is 1.0–2.0 mm, away from direct airflow; keep the BMP581 body free of routing/vias underneath and maintain the documented separation from switching heat sources. The actual port, board opening and enclosure response still require fit-dummy and assembled-board review. A moving vehicle or aircraft can create local dynamic pressure, suction, blockage and pressure lag; the bench test does not qualify those installations. The acoustic and pressure openings must remain separated per the floorplan.

BMP581 reported temperature is a sensor reading and must not be treated as outside-air temperature or proof of the whole board's temperature. Heat from the backlight, regulators, processor, charging and sunlight can bias the board environment. Measure local board temperature next to the sensor during characterization and describe the test mounting, airflow and nearby heat loads. Temperature-induced pressure shift, enclosure thermal gradients, solder drift, long-term drift and calibration effects must be reported as observed; no correction is assumed until evidenced.

## Proposed validity and data contract

This is a proposed interface contract for review and implementation. It gives downstream display/logging code the context needed to distinguish a usable pressure sample from an unqualified value.

| Field | Contract |
| --- | --- |
| `pressure_pa` | Unrounded absolute sensor pressure in pascals. Preserve the source resolution; display rounding is separate. Never substitute a standard-atmosphere pressure for a missing sensor reading. |
| `temperature_c` | BMP581-reported temperature in degrees Celsius, explicitly labeled as sensor temperature. |
| `sample_time` / `sample_age` | Monotonic acquisition time and derived age. A stale or missing update is invalid; the timeout is a firmware configuration to be set from the selected ODR and verified bench behavior. |
| `sensor_state` | At minimum: `valid`, `not_ready`, `bus_error`, `device_error`, `stale`, `pressure_out_of_range`, `temperature_out_of_range`, or `uncalibrated_reference`. Preserve the reason in logs. |
| `pressure_valid` | True only when communication and device status are healthy, a fresh data-ready sample has been acquired, pressure is within 300–1250 hPa inclusive, and reported sensor temperature is within -40 to +85 °C inclusive. A value at/beyond a boundary should be treated conservatively if rounding or sensor uncertainty makes its status ambiguous. |
| `altitude_m` | Optional calculated, indicative value. Must carry the reference pressure value/source and a mode: reference-calibrated pressure altitude or session-relative change. Without a valid explicit reference, do not label it absolute altitude or silently assume local sea-level pressure. |
| `vario_mps` | Optional indicative rate derived from fresh valid pressure samples using a documented filter/window. Positive means ascent, negative descent. Mark invalid during startup, stale data, pressure faults or filter reset; record filter/window and effective delay. |
| `calibration` | Record the reference pressure, source, timestamp and method used for any altitude zero/reference. A missing or expired reference invalidates absolute altitude, but need not invalidate fresh absolute pressure. |
| `quality` | Distinguish manufacturer-range validity from tested performance. In-range is not a claim of accuracy. Tag all BMP581 pressure/altitude/vario outputs as secondary and indicative; never use them as the sole safety or primary-flight indication. |

## Results record and closure

No tests are recorded as complete in this plan. After PCBA, add a dated result record with board/sensor identity, setup, reference uncertainty, raw-data path, plots or summaries, configuration, deviations, failures, reviewer and disposition. Do not edit this plan to imply a pass until the owner/reviewer has assessed the evidence. Keep any measured project limits clearly labeled as accepted limits, observed results or open TBD values, as appropriate.

Closure evidence for the sensor gate should include the reviewed firmware validity contract, assembler land-pattern approval, fit-dummy and routing/vent conformance, pressure/reference comparison near the 10,000 ft standard pressure, temperature notes, and vario noise/lag/sign results. Balloon or exposed-airframe use remains a separate installation and environment review.
