# Digital microphone architecture

Status: pre-schematic candidate reviewed 2026-09-14. Audio remains an optional fitted function in Rev A; disabling or later marking it DNP requires a recorded decision.

## Proposed parts and interface

Use TDK InvenSense `MMICT5838-00-012` as the first microphone candidate. Manufacturer data sheet DS-000383 revision 1.1 identifies a bottom-port PDM microphone in a 3.5 x 2.65 x 0.98 mm surface-mount package, with 1.62-1.98 V supply, -40 to 85 °C range, 68 dBA high-quality SNR, 133 dB SPL acoustic overload point and high-quality clock range of 2.0-3.7 MHz. DigiKey displayed 73,381 pieces in stock on 2026-09-14; recheck lifecycle and PCBA supply before freeze.

The ESP32 GPIO map already reserves `PDM_CLK` and `PDM_DATA`, so PDM closes the interface with two signals. Because the microphone is a 1.8 V device, use TI `TXU0202DCUR` as the first translation candidate: one fixed-direction channel carries clock from 3.3 V to 1.8 V and the opposite channel carries PDM data from 1.8 V to 3.3 V. TI specifies independent 1.1-5.5 V rails, opposite channel directions, up to 200 Mbps, partial-power-down isolation and VSSOP-8. Tie output enable to a reviewed rail-valid/reset policy so neither side back-powers an off domain.

Power the microphone and its low-voltage translator side from the proposed `1V8_LOGIC` rail. Place the manufacturer's required local bypass at the microphone and keep digital clock routing away from GNSS/RF inputs and the magnetometer. Confirm that the display and microphone sharing the 1.8 V regulator does not couple visible or acoustic noise; split filtering or the rail if measurement requires it.

## Mechanical and validation gates

- The microphone is bottom-port. The PCB needs the exact manufacturer acoustic-hole/land pattern, copper and solder-mask keepout, and no solder paste over the port.
- The enclosure needs a short sealed acoustic path that does not expose the microphone to direct condensation. Gasket/compression details remain mechanical inputs.
- Validate 3.3-to-1.8 V clock and 1.8-to-3.3 V data levels, PDM duty/frequency, startup, sleep, off-state leakage and recovery after rail switching.
- Record a synchronized audio fixture with known tone/SPL, check sample rate, clipping, noise floor, missing blocks and timestamp mapping to system monotonic time.
- Measure RF self-interference during Wi-Fi, LoRa TX and ADS-B operation. Audio may be disabled in low-power profiles.

Primary evidence: [TDK T5838 product family](https://www.invensense.tdk.com/en-us/microphone), [T5838 DS-000383 revision 1.1](https://invensense.tdk.com/wp-content/uploads/2023/06/DS-000383-T5838-Datasheet-v1.1.pdf), [TI TXU0202 product page and revision-A data sheet](https://www.ti.com/product/TXU0202), and [DigiKey MMICT5838-00-012 snapshot](https://www.digikey.com/en/products/detail/tdk-invensense/MMICT5838-00-012/16903860).

## Disposition

The microphone and translator are preferred engineering candidates, not footprint releases. Final acceptance requires exact manufacturer CAD comparison, enclosure/acoustic decision, sourcing and board-level audio/RF tests.
