# Audio power-domain consistency review

Review date: 2026-09-22  
Status: engineering review and preferred net/domain proposal integrated into the subsystem documents on 2026-09-22. The exact load-switch circuit, off-state behavior and independent review remain open; this is not a schematic or safety freeze.

## Finding

The documents describe two incompatible meanings for the audio 1.8 V net:

- `AUDIO_ARCHITECTURE.md` assigns T5838 VDD, TXU0202 VCCB and TXU0202 OE pull-up to `1V8_LOGIC`.
- `POWER_RAIL_PLAN.md` shows `1V8_LOGIC` as the TPS7A2018 output, directly feeding both TFT logic and the optional microphone. It is not shown as a switched rail.
- `CONTROL_IO_REVIEW.md` says `AUD_SW_EN_N` controls a switched audio/1.8 V domain, and that this switch feeds both T5838 and TXU0202.

As written, those names do not define whether the 1.8 V net is always on or switchable. If the schematic connects the audio loads directly to `1V8_LOGIC`, asserting `AUD_SW_EN_N` cannot turn off the microphone or the translator's B port. If the switch instead disconnects the shared `1V8_LOGIC` rail, it also removes power from the TFT logic. That conflicts with the stated shared always-on display/audio rail architecture and makes the documented audio off-state test ambiguous.

This is a real domain-control inconsistency, not evidence of an unsafe device pin voltage by itself. TXU0202 explicitly supports either rail being disconnected: TI states that if either supply is below 100 mV or disconnected, outputs become high-impedance; partial-power-down Ioff and glitch-free rail sequencing are specified. The mismatch is that the currently named audio control may not control the loads it is supposed to control.

## Proposed disposition

Keep `1V8_LOGIC` as the always-on LDO output serving the TFT, and create a distinct switched branch named `1V8_AUDIO_SW` (or another unambiguous name) from `1V8_LOGIC` through the already selected TPS22918 load-switch candidate. Connect T5838 VDD and TXU0202 VCCB to this switched branch. Keep TXU0202 VCCA on `3V3_MAIN`; pull OE up to the switched audio branch through the reviewed 100 kohm resistor. The TCA9535 audio control then drives the TPS22918 active-high EN, with its existing external pull-down keeping audio off through expander reset or loss of power. Rename the historical `AUD_SW_EN_N` to an active-high name such as `AUD_SW_EN` at schematic capture, consistent with the recorded TPS22918 polarity correction.

This preserves the display's always-on 1.8 V feed while making the documented audio enable actually switch both the microphone and its low-voltage translator supply. The load-switch input remains within the TPS22918's documented 1 V to 5.5 V range at 1.8 V. Its CT, output capacitor and QOD treatment should follow the existing TPS22918 application review; do not assume the SD domain's chosen values without checking this audio load and its discharge behavior.

When disabling audio, firmware should stop PDM clocking and put host-side pins in the reviewed high-impedance/low state before disabling the load switch; on enable, wait for the switched rail to settle before starting the PDM clock. TI specifies Ioff isolation and high-Z outputs when a supply is absent, but this does not replace review of the ESP32 pin states, T5838 input voltage limits, and actual rail ramp at schematic/bench review.

A lower-scope alternative exists if audio power-down is not required: leave both audio devices on `1V8_LOGIC` and use a host-controlled TXU0202 OE to isolate PDM buses. That only disables the translated interface; it does not switch off T5838 or implement the switched audio-power behavior documented by `CONTROL_IO_REVIEW.md`. It is therefore not the recommended reconciliation unless the owner deliberately changes the intended control function.

## Electrical impact and remaining evidence

- T5838 DS-000383 Rev 1.1 gives a 1.62-1.98 V operating supply. Both `1V8_LOGIC` and the proposed switched branch nominally meet that range; verify LDO tolerance, load-switch drop, ramp, and transient at the microphone pins in the final application review.
- T5838 current is small relative to the rail allowance (AUD-01 records 340 uA max in high-quality mode at 2.4 MHz). Switching it does not materially alter regulator sizing, but the always-on 1V8 load inventory should distinguish the TFT and audio branch, and the switched-branch startup/discharge behavior remains to be checked.
- TXU0202 data sheet SCES942A Rev A allows each supply from 1.1 V to 5.5 V. Section 6 identifies OE as enabled by a high referenced to either VCCA or VCCB; sections 9.1 and 9.3.4 document isolation/high impedance when either supply is below 100 mV or disconnected. With VCCB and OE pull-up moved together to `1V8_AUDIO_SW`, the translator rail-valid enable policy remains coherent.
- `POWER_RAIL_PLAN.md` currently counts the TPS7A2018 chain as a 25 mA `3V3_MAIN` allowance. This remains conservative after splitting the branch; no new regulator or part replacement is proposed. Update that load decomposition only during the integrator's shared-document reconciliation.
- Exact switch schematic, enable polarity/net naming, output-discharge choice, rail ramp, GPIO reset state, and powered-off pin behavior remain schematic/application-review gates. No circuit is frozen by this note.

## Primary sources reviewed

Reviewed 2026-09-22. Datasheet revisions and sections are included so the facts can be rechecked against the exact candidates.

- Texas Instruments, **TXU0202**, data sheet SCES942A Rev A (November 2021, revised March 2022): sections 3 and 6, pp. 1 and 4 (rail range, port references and OE); sections 9.1 and 9.3.4, pp. 20-21 (Ioff, VCC disconnect, <100 mV isolation and sequencing). [Official TI data sheet](https://www.ti.com/lit/ds/symlink/txu0202.pdf)
- TDK InvenSense, **T5838**, DS-000383 Rev 1.1: sections 5-6 (operating supply and mode/current requirements). [Official TDK data sheet](https://invensense.tdk.com/wp-content/uploads/2023/06/DS-000383-T5838-Datasheet-v1.1.pdf)
- Texas Instruments, **TPS22918**, data sheet Rev C: recommended operating conditions and load-switch application sections; TI product page states 1 V to 5.5 V input range. [Official TI data sheet](https://www.ti.com/lit/ds/symlink/tps22918.pdf) · [Official TI product page](https://www.ti.com/product/TPS22918)

## Disposition boundary

The integrator reconciled the preferred net names and branch boundary in the audio, control-I/O, power-rail, matrix and status records. This does not change D11 or any locked decision, select a replacement component, authorize schematic commitment, or close the system off-state review. AUD-02 owns the exact application and independent review before Astra capture.
