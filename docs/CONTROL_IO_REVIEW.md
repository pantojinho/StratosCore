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

## TCA9535 port map (DIG-03, 2026-09-22)

**VDD and signal-domain rule:** TCA9535PWR VDD sits on `3V3_MAIN` (always-on, gate-9 review input). Rationale: the expander reads TUSB320LAI OUT1/OUT2/OUT3 pulled to `3V3_MAIN` (D22 disposition) and card-detect/status lines owned by always-on domains; powering the expander from a switched rail would put switched-rail voltage on `3V3_MAIN`-pulled inputs through the TCA9535 input clamp structure whenever the rail falls — a back-power path the off-state review would have to re-open. Address A2:A0 = GND (0x20), as recorded.

**Every output net carries the external resistor that creates its safe state before and independent of firmware** (TI: all I/O are inputs at power-on/reset; outputs float until configured). No safe state depends on the expander output stage.

### Port allocation (16 ports; 12 used, 4 spare inputs)

| Port | Net | Dir | External default (no firmware) | Purpose |
| --- | --- | --- | --- | --- |
| P00 | SD_CD | In | 100 kohm pull-up to `3V3_MAIN` (on-board; card switch to GND) | microSD card detect (slow, no safety function) |
| P01 | TUSB_OUT1 | In | 100 kohm pull-up to `3V3_MAIN` (TUSB side; D22 wiring) | USB-C current class bit 1 (Table 3 decode) |
| P02 | TUSB_OUT2 | In | 100 kohm pull-up to `3V3_MAIN` (TUSB side) | USB-C current class bit 2 |
| P03 | TUSB_OUT3 | In | 100 kohm pull-up to `3V3_MAIN` (TUSB side) | Audio-accessory flag; expected never asserted on Rev A |
| P04 | CHG_INT | In | charger-side open-drain; expander reads via `3V3_MAIN` domain | BQ25887 interrupt/status (non-latency-critical routing; direct-ESP32 alternative stays with PWR-03) |
| P05 | EXP_PRESENT | In | 100 kohm pull-up to `3V3_MAIN` | Expansion cable/hood detect if the harness provides it; otherwise spare |
| P06 | LCD_RST_N | Out | 100 kohm pull-up to `1V8_LOGIC` (display side rail) | Display reset, active-low; expander output open-drain-configured drive low only; safe state = released |
| P07 | — | In | — | Spare input (bring-up/test) |
| P10 | SX_NSS_HOLD | Out | 100 kohm pull-up to `3V3_MAIN` | Reserved radio service hold/aux (non-safety; final use with LORA-02) |
| P11 | SD_SW_EN_N | Out | 100 kohm pull-**down** to GND (see polarity correction below) | microSD domain load-switch enable; default OFF |
| P12 | AUD_SW_EN_N | Out | 100 kohm pull-**down** to GND | Audio/1.8 V domain load-switch enable; default OFF |
| P13 | ADSB_SW_EN_N | Out | 100 kohm pull-**down** to GND | ADS-B digital domain load-switch enable; default OFF (runtime profile may power down ADS-B; O13) |
| P14 | — | In | — | Spare input |
| P15 | — | In | — | Spare input |
| P16 | EXP_PERIPH_RST | Out | 100 kohm pull-up to `3V3_MAIN` (released) | Optional expansion-peripheral reset line (active-low, released by default) |
| P17 | — | In | — | Spare input |

**Enable polarity correction (2026-09-22, follow-up to PR #149):** the P11/P12/P13 rows above originally specified pull-ups to an active-low-release convention. That was wrong for the selected regulator family: the `TPS22918DBVR` (P22 candidate) has an **active-high EN pin**, so a pull-up would force every switched domain ON through the expander's power-on input default or any expander fault — the exact inverse of the intended safe state. Corrected disposition: **pull-downs to GND on P11/P12/P13; domains power up OFF and stay OFF through expander reset, hang or power loss; firmware enables a domain by driving the port high (or configuring it push-pull high)**. The "dead expander means domains off" rule is preserved with the physically correct resistor. Naming stays `*_EN_N` only as the historical net label; the schematic net rename to `*_EN` is recorded for Astra capture.

### Recovery routes without the expander (counted, as required)

- **ESP32:** ROM recovery via BUTTON_1/GPIO0 (direct), console via native USB (direct), charger inhibit is NOT expander-dependent (BQ25887 CD/default-mode chain remains PWR-03's hardware-gated design — the expander never owns charger/protector safety).
- **RP2040:** RUN reset via its direct 10 k/100 n RC + test point (DIG-01), BOOTSEL via the direct `USB_BOOT` point (DIG-01), SWD via the direct tag-connect access (DIG-01). The expander is not in any RP2040 recovery path.
- **Domains:** every load-switch enable defaults to OFF by its own pull-down when the expander is unpowered, hung or mid-boot (corrected convention above); firmware turns a domain ON only by deliberately driving its port high.

### Off-state boundaries recorded for the gate-9 review

- SD_SW_EN_N / AUD_SW_EN_N / ADSB_SW_EN_N: the switched rails feed SD, T5838/TXU0202 audio, and RP2040 ADS-B digital respectively; each switched rail's inputs that face always-on logic need the per-pin off-state check already listed in the electrical matrix (host pins high-Z before rail removal; external pulls never feed an off device). The TCA9535 itself is on `3V3_MAIN` and never switched.
- LCD_RST_N pulls from `1V8_LOGIC`: acceptable only because the display reset is a display-side rail with a defined 1.8 V domain (DSP-02 sequence); if DSP-02 moves display logic rails, this pull moves with it.


## Validation gates

- obtain current manufacturer drawings and independently compare both project footprints;
- test both buttons through the printed enclosure in portrait and landscape handling positions;
- verify button bounce, ESD, long-press and GPIO0 recovery behavior at power-up and reset;
- document every TCA9535 port's external pull, off-state, attached rail and software ownership;
- simulate and measure power sequencing when the expander, host or target peripheral is unpowered;
- prove that an I2C lockup cannot leave the battery, charger or high-current load in an unsafe state.

Primary sources reviewed 2026-09-14: Alps Alpine [SKSCLCE010 product page](https://tech.alpsalpine.com/e/products/detail/SKSCLCE010/) and [SKSC family drawing](https://tech.alpsalpine.com/cms.media/product_catalog_ta_02_sksc_en_f9e52a07d5.pdf); Texas Instruments [TCA9535 Rev E data sheet and exact `TCA9535PWR` status](https://www.ti.com/lit/gpn/tca9535).
