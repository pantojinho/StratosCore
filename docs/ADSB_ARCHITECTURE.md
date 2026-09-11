# ADS-B architecture

**Core Rev A hardware feature: 1090 MHz receive-only path with dedicated RP2040 timing.** LoRa SX1262 cannot serve this function. No analog component selection is frozen.

## Proposed signal chain

Separate antenna -> RF preselection/SAW -> LNA and further filtering as needed -> fast envelope/log detector -> threshold/comparator -> RP2040 PIO/DMA/frame processing -> framed UART or SPI -> ESP32-S3 contact store, relative traffic UI and microSD logger.

Pre-LNA filtering reduces blockers but adds noise loss; assess both against the required sensitivity and nearby LoRa emissions. Select LNA gain/noise/linearity, filter insertion loss and rejection, detector pulse response, comparator delay/jitter/hysteresis and logic swing together. A detector specified for 1090 MHz carrier frequency can still be too slow to preserve ADS-B pulses. Threshold adaptation must not hide or distort valid pulse trains.

[ADSBee 1090](../references/ADSBEE_NOTES.md) provides a relevant RP2040 PIO/frontend architectural reference. [avBadge](../references/AVBADGE_NOTES.md) instead uses an analog receiver path into an SoC TV input and a Linux/DSP software chain; its circuit is not a drop-in digital comparator interface. Neither implementation is copied.

## Timing and decoding contract proposal

Plan capture for 1 microsecond Mode-S symbols with half-symbol pulse positions, an 8 microsecond preamble and 56/112-bit frame lengths. Verify exact framing and parity handling against protocol sources during implementation. Source for observed timing model: [ADSBee capture PIO](https://github.com/PantsForBirds/adsbee/blob/2942116b726f3b014605fc78af5373c6452c721d/firmware/adsbee_1090/pico/application/pio/capture.pio). Its constants are reference observations, not approved StratosCore firmware.

RP2040 owns pulse capture, timestamping, frame length checks, CRC/parity assessment appropriate to each downlink format, and bounded buffering. Initially prioritize DF17 extended squitter; declare supported formats explicitly. A naive CRC-equals-zero filter for all Mode-S formats is insufficient because some use overlaid parity. Reject or flag suspect frames; do not silently "repair" unverified addresses.

Proposed transport record: protocol version, message type, sequence, capture timestamp with units, 7/14-byte raw frame when present, downlink format, parity/validation flags, optional signal metric with calibration status, payload length and transport integrity check. Separate health messages report FIFO/DMA overruns, rejected frames, reset reason and supply/frontend state. Signal strength is not calibrated RSSI unless measured as such. Set maximum packet size, endianness, escaping/framing, reset handshake and link rate in a future interface specification.

ESP32 builds per-aircraft state keyed by ICAO address: callsign, latitude/longitude, barometric/geometric altitude with type/units, horizontal/vertical velocity, track/heading with type/reference, last-seen time and per-field validity/age. Never derive valid coordinates from a callsign-only message. CPR requires correct airborne/surface handling, even/odd timing and geographic ambiguity checks; local-reference decoding must use valid recent ownship position. Report unavailable/stale values explicitly and expire contacts with configurable, tested policy.

## Link and data capacity

Illustrative budget: 1,000 received frames/s x 40 bytes/framed record = 40 kB/s. UART 8N1 requires at least 400 kbit/s before margin; 115200 baud would carry only about 11.52 kB/s. This is a sizing scenario, not expected traffic. A 921600-baud candidate or SPI should be evaluated against bus availability, sustained throughput and bursts. Raw capture must continue when host queues are full, with explicit drop counts. Timestamp mapping is described in [system architecture](SYSTEM_ARCHITECTURE.md).

## Comparison and reuse disposition

Keep RP2040 as baseline: its independent timing hardware is directly relevant and avoids sharing ESP32 UI/network scheduling with RF capture. Current ADSBee also describes an LR2021/CC1314-based alternative; it is a future comparison candidate only. No verified cost, availability or StratosCore integration analysis establishes a sufficiently better replacement. Do not expand Rev A into 978 MHz UAT by implication.

ADSBee's GPL-3.0 terms cover its published designs/code; copying requires a licensing decision and retention of obligations, not relabeling to MIT/CERN-OHL-P. avBadge hardware reuse permission remains unestablished. See [reuse register](../references/REUSE_REGISTER.md). An independent implementation from permitted specifications/manufacturer references is the planning direction, pending license review of every actual dependency.

## Required proof before integration

Use legally obtained test frames and controlled conducted RF; test valid/invalid parity, burst overlaps, near/far signals, saturation recovery, comparator threshold sweeps, clock tolerances, FIFO stress, UART resynchronization, CPR edge cases and stale fields. Compare decoded records with independently validated fixtures. Measure sensitivity, false positives and drop rate under LCD/SD/Wi-Fi/LoRa/charging stress. Range targets are TBD; antenna sightings alone are not a receiver qualification.
