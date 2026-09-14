# Buttons and slow-control I/O review

Status: preferred part candidates selected for independent mechanical/CAD and reset-state review. The two physical buttons remain a locked product requirement.

## Physical buttons

Use two Alps Alpine `SKSCLCE010` side-push tactile switches as the first enclosure/PCB candidate. The manufacturer lists this exact part as a standard-production, surface-mount SKSC-family switch with 3.5 x 3.55 x 1.25 mm body, 1.6 N operating force, 0.2 mm travel, 100,000-cycle operating life and -30 to +85 degrees C operating range. Its side actuation is compatible with an enclosure-wall plunger and avoids placing both controls behind the display, but the exact board edge and enclosure geometry still need a printed fit test.

Button 1 connects to ESP32 GPIO0 and deliberately doubles as ROM recovery. Button 2 connects to GPIO48. Each button is active low with a local pull-up and reviewed debounce/ESD provisions. Mechanical plungers must not hold either switch during assembly, impact or thermal movement. Button 1 must be clearly documented because holding it while resetting changes the boot path.

Do not release the footprint from the web summary alone. Compare the project pad, mounting face, actuation datum, body/courtyard and enclosure plunger position with the current Alps Alpine SKSC drawing. Confirm that the no-guide-boss version is mechanically retained by its solder joints under the accepted shock requirement; otherwise evaluate the guide-boss `SKSCLDE010` without silently substituting it.

## Slow-control I/O expander

Use TI `TCA9535PWR` as the preferred 16-bit I2C expander candidate at address 0x20 with A2:A0 grounded. TI lists the exact TSSOP-24 part active and specifies 1.65-5.5 V operation, 400 kHz I2C, active-low interrupt and all I/O configured as inputs after power-on or reset. That default is useful only when every attached enable/reset has an external resistor that creates its safe state without firmware.

The expander may own card detect and low-speed status/reset/enable signals. It must not own charger/protector safety, cell cutoff, main-rail enable, watchdog survival or any function needed to make a failed MCU safe. Connect RESET_N to a defined host/reset supervisor only if system review shows a recovery benefit; do not rely on I2C software to establish safe power-up levels.

### Candidate signal inventory

| Class | Candidate expander use | Required reset behavior |
| --- | --- | --- |
| Inputs | microSD card detect, charger/status interrupts where latency permits, connector presence/status | External pulls and input protection define state while expander is off |
| Outputs | peripheral reset lines, load-switch enables for non-safety domains, optional display reset | External pulls force the safe disabled/reset state until firmware intentionally changes it |
| Reserved | Spare pins for bring-up/test only | Keep as inputs; no exposed floating copper without a test purpose |

The final pin map must count every signal and preserve at least one recovery route for ESP32 and RP2040 without the expander.

## Validation gates

- obtain current manufacturer drawings and independently compare both project footprints;
- test both buttons through the printed enclosure in portrait and landscape handling positions;
- verify button bounce, ESD, long-press and GPIO0 recovery behavior at power-up and reset;
- document every TCA9535 port's external pull, off-state, attached rail and software ownership;
- simulate and measure power sequencing when the expander, host or target peripheral is unpowered;
- prove that an I2C lockup cannot leave the battery, charger or high-current load in an unsafe state.

Primary sources reviewed 2026-09-14: Alps Alpine [SKSCLCE010 product page](https://tech.alpsalpine.com/e/products/detail/SKSCLCE010/) and [SKSC family drawing](https://tech.alpsalpine.com/cms.media/product_catalog_ta_02_sksc_en_f9e52a07d5.pdf); Texas Instruments [TCA9535 Rev E data sheet and exact `TCA9535PWR` status](https://www.ti.com/lit/gpn/tca9535).
