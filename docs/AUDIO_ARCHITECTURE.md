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

## Audio circuit specification (AUD-01 closure, 2026-09-22)

Facts below were re-verified in the retrieved primary documents this session: TDK `DS-000383` rev 1.1 (retrieved via the Mouser-hosted copy of the identical vendor file after invensense.tdk.com returned HTML) and TI `TXU0202` data sheet (retrieved from ti.com).

### Microphone application (T5838, DS-000383 v1.1)

- **Supply:** VDD 1.62-1.98 V on `1V8_LOGIC`, **100 nF local bypass at the mic pad plus 1 uF at the translator low side** (manufacturer bypass requirement class; final DC blocking/bulk split confirmed at capture).
- **Current inventory (feeds the PWR-04 `1V8_LOGIC` allowance):** high-quality mode supply current **310 uA typical / 340 uA maximum** at 2.4 MHz clock (DS section 6.1); low-power mode 120/140 uA at 768 kHz; sleep states 20-137 uA class. The microphone does **not** threaten the 25 mA `1V8_LOGIC` allowance; translator static is in the uA class (TXU0202 6 uA max control class).
- **Clock:** high-quality mode requires **2.0-3.7 MHz** (DS mode table); `PDM_CLK` (GPIO15) drives it through the translator at a firmware-selectable 2.048/3.072/3.2544 MHz-class rate; low-power 400-800 kHz and turbo 4.2-4.8 MHz windows exist but are not the Rev A default. CLK duty 50% class per DS.
- **PCB acoustic requirement (DS section 9):** land pattern is **1:1 with the package pads**; **no solder paste over the PCB sound hole**; PCB hole **0.5-1.0 mm diameter recommended** (never smaller than the 0.375 mm mic port); align the package port with the PCB hole. These are DIG-04 footprint constraints verbatim.
- **Acoustic path/enclosure (mechanical boundary, MECH-02/03):** short sealed path to an enclosure opening; gasket/compression and condensation exclusion remain the recorded mechanical inputs. No SPL/condensation claim is made here.

### Translator application (TXU0202, VSSOP-8)

- **Pin map (DS section 6, pin functions):** VCCA = port A supply, VCCB = port B supply, GND; A1/A2Y and B1/B2Y are the two fixed-direction channel pairs (one A->B, one B->A; orientation pinned at capture per the signal directions below); **OE pin 6: low = all outputs high-impedance, high (to VCCA or VCCB) = enabled**.
- **Signal assignment:** channel 1 A->B: `PDM_CLK` 3.3 V side -> 1.8 V mic clock; channel 2 B->A: mic PDM data 1.8 V -> `PDM_DATA` 3.3 V side. VCCA = `3V3_MAIN` on the 3.3 V channels' reference, VCCB = `1V8_LOGIC` on the mic side (A/B naming fixed to this assignment at schematic capture; the DS allows either rail on either port within 1.1-5.5 V).
- **OE policy (the aud-01 "reviewed rail-valid/reset policy"):** OE (pin 6) pulled up to `1V8_LOGIC` through 100 kohm, no pulldown: the channels enable only when the microphone rail is present, and the TXU0202's Ioff/partial-power-down isolation (both directions high-Z when either rail is <100 mV or disconnected; Ioff +/-1.5-2.5 uA class) guarantees that an off `1V8_LOGIC` leaves both the ESP32 and microphone sides floating, never driven. When `1V8_LOGIC` rises, OE goes high and the channels enable monotonically after both rails are valid - no firmware dependency, no back-drive path into an off microphone or an off ESP32 bank.
- **Off-state/recovery test row (board stage):** toggle `1V8_LOGIC` (the existing DIG-03 `AUD_SW_EN_N` domain switch drives the mic side; the translator OE follows automatically) and verify PDM recovery, no latch-up, and no `PDM_CLK`/`PDM_DATA` disturbance on the 3.3 V side while off.
- **Routing constraints:** keep `PDM_CLK`/`PDM_DATA` short and away from GNSS RF_IN, the MMC5983MA magnetometer area and the SX1262 switch node, per the standing architecture note; series termination not required at the short board lengths (translator drive and mic load only); revisit only if post-layout length exceeds ~50 mm.

### AUD-01 closure boundary

Delivered: pin-complete translator application, mic supply/clock/acoustic constraints, OE rail-valid policy, current inputs to PWR-04, routing constraints, and the off-state/recovery test row. **Deliberately open:** DIG-04 footprints (T5838 port-avoidance land, TXU0202 VSSOP-8) from the manufacturer CAD; enclosure acoustic path (MECH-02/03); post-PCBA audio/RF measurements; sourcing recheck at purchase.
