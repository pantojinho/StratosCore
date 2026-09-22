# Electrical compatibility matrix

Status: system-level pre-schematic review. Created 2026-09-14; evidence rows updated through 2026-09-17 with exact component/manufacturer-EVM figures where noted. A row marked OPEN prevents the affected circuit from being treated as KiCad-ready.

## Supply domains

| Domain | Nominal source | Loads currently assigned | State | Remaining proof |
| --- | --- | --- | --- | --- |
| Protected 2S bus | Two matched removable 21700 cells through common protection, about 6.0-8.4 V planned | Main buck and charger/battery interface | OPEN - TOPOLOGY CONTRADICTION | Resolve BQ25887 autonomous charging/default `CD` state, low-side-protector ground/sense/cutoff conflict, termination under system load, exact FET/fuse/holder/NTCs and qualified battery review |
| 3V3_MAIN | `TPS62130ARGTR` candidate from protected 2S | ESP32-S3, RP2040, microSD, sensors, touch, SX1262, rail-control logic and TPS61169 backlight input | CANDIDATE - LOAD INVENTORY INCOMPLETE | A 974 mA planning subtotal currently includes ESP32-S3 Wi-Fi TX 340 mA, RP2040 IOVDD 35.5 mA, a 200 mA microSD allowance, SX1262 typical TX 118 mA, a 250 mA backlight reserve and 30 mA for sensors/touch/miscellaneous. It is not a worst-case peak: GNSS startup, RP2040 core/flash, complete display logic, ADS-B quiet-rail demand, dynamic overlap and maximum-vs-typical corrections remain. Buck passives, transient, thermal, EMI and brownout analysis remain open |
| `3V3_GNSS` | Filtered always-on branch of `3V3_MAIN` candidate | MAX-M10S VCC and V_IO | PREFERRED APPLICATION P20 | Size/filter for the 100 mA startup response (u-blox R08 Section 4), verify PDN noise and validate UART/PPS behavior during system sequencing |
| `3V3_SWITCHED_*` | One `TPS22918DBVR` per justified load group | ADS-B digital, SD/audio/radio domains only where measurement supports switching | CANDIDATE | Final grouping, rise/discharge values, reset sequence and every connected pin's off-state. Off-state leakage per TPS22918 Rev C: 9.2 uA typical / 16 uA maximum shutdown current at 5.5 V |
| `3V0_RF_QUIET` | `TPS7A2030PDBVR` candidate from `3V3_MAIN` | ADS-B LNA/analog chain | CANDIDATE - DROPOUT CLOSED | Exact RF load, filtering and detector-noise measurement remain. Dropout concern closed by TPS7A20 Rev H: 140 mV maximum at 300 mA for the 3.3 V-output DBV option, so a 3.3-to-3.0 V conversion at the roughly 85 mA analog load has wide margin |
| `1V8_LOGIC` | `TPS7A2018PDBVR` candidate from `3V3_MAIN` | TFT translator low side and T5838 microphone/translator low side | CANDIDATE - PARTIAL STATIC LOAD | Known support-device static current is about 400 uA from SN74AXC4T245, SN74LVC1G07, TXU0202 and MMICT5838-00-012 maximum figures. TFT VDDIO, translator dynamic current, coupling, sequencing and off-state leakage are omitted and keep the rail calculation open |
| LCD backlight | `TPS61169DCKR` boost candidate from `3V3_MAIN` | About 92 mA initial set point into the specified 5.8-6.4 V LED load | CANDIDATE | Start with 2.21 ohm >=0.1 W, 10 uH `LPS4018-103MRC`, >=1 uF input plus local bulk and 1-4.7 uF effective/50 V output. Exact 60 V-class Schottky remains open. Sample voltage/current, open/short LED, dimming, leakage, EMI and thermal tests remain; never connect this 5.5 V maximum-input part to 2S |

The proposed main buck's 3 A rating is an upper component capability, not a verified rail requirement. The 974 mA subtotal above is an incomplete planning inventory, not a simultaneous-peak calculation or a measurement.

## Digital interface compatibility

| Interface | Participants and levels | Current disposition | Blocking issue |
| --- | --- | --- | --- |
| Shared I2C | ESP32 3.3 V at 100 kHz Standard-mode; ICM-42688-P, MMC5983MA, BMP581, SHT40, touch, BQ25887 and expansion (TUSB320LAI removed per D22/P26 — GPIO mode, see [GPIO map](INTERFACE_GPIO_MAP.md)) | 2026-09-22 (SYS-01): bus speed set to 100 kHz and the TUSB320LAI device-level constraint (CBUS 100 pF @ 400 kHz; 1.6 mA weakest sink) eliminated by moving the part to GPIO mode with ADDR NC. Pull-up window recomputed: `Rp_min` 967 ohm (3 mA class), `Rp_max` 2951 ohm at the 400 pF UM10204 ceiling, preferred 2.2 k ohm +/- 1% pair on `3V3_MAIN`; on-board capacitance estimate 110-140 pF, expansion-cable reserve <= 150 pF. Full arithmetic in [the I2C bus budget](I2C_BUS_BUDGET.md) Result 3. Address 0x47 freed; BMP581's 0x47 alternate re-enabled (0x46 stays primary) | Per-device off-state review (touch, BQ25887, switched domains) remains OPEN. Post-placement `Cb` recount and the measured rise-time/VOL validation are gate 8 / post-PCBA items. BQ25887 SLUSD89B gives VIH 1.3 V, VIL 0.4 V and 1 uA leakage at a characterized 1.8 V pull-up; TI EVM guide SLUUC12 Table 3 implements SDA/SCL/INT pull-ups at 10 kOhm from a 3.3 V LDO — valid as bus-level evidence only, never as a resistance value for this 100 kHz multi-device bus. TUSB320LAI back-power note (SLLSEQ8D note 2, 3.0 V VDD floor with a 3.3 V interface) remains satisfied by powering the device from `3V3_MAIN`, and its GPIO outputs are pulled from `3V3_MAIN` and read by the TCA9535 |
| Shared SPI trunk | ESP32 3.3 V to microSD and SX1262; TFT uses a translated branch | Separate chip selects and bounded service policy defined | Exact TFT translator, loading, maximum clocks/modes and concurrency measurement |
| TFT branch | ESP32 3.3 V outputs to 1.8 V display logic | Write-only three-line, nine-bit `101` proposal through fixed A-to-B AXC channels; <=15 MHz panel clock | Controlled clarification of TFT VCC/VDDI/VDD, unused-pin ties, reset/enable startup and validation on two samples |
| PDM microphone | ESP32 3.3 V clock/data domain; T5838 is 1.8 V | `TXU0202DCUR` provides one channel each direction | Confirm OE/rail sequence, PDM clock quality, footprint/acoustic port and RF-noise test |
| GNSS UART/PPS | ESP32 and MAX-M10S both use 3.3 V I/O proposal | Direct logic levels are compatible while powered | Verify startup/reset sequencing and ensure neither side drives beyond the other's powered limits |
| RP2040 UART | ESP32 and RP2040 at 3.3 V, 921600 baud with RTS/CTS | Direct dedicated link candidate; host-side framing behavior passes 20 tests for payload shapes, sequencing, CRC, timestamp wrap, overflow visibility and resynchronization | Define reset/boot ownership and verify timing, sustained throughput and the same contract against real PIO/DMA silicon on the bench |
| USB 2.0 | Native ESP32 D+/D- through USB4105 candidate; four signal lines protected by TPD4E05U06 candidate; TPS259474L eFuse application closed 2026-09-22 (PWR-02, [power input evidence](POWER_INPUT_EVIDENCE.md)): RILM 1.69 k -> 1.97 A breaker, UVLO 3.98 V / OVLO 6.50 V dividers, dVdt open, default-current-only policy via GPIO-mode CC | USB default-current/enumeration policy: fixed sink at the GPIO-mode default class (500 mA floor) — closed by PWR-02; footprints and 90-ohm geometry remain; ITIMER sizing deferred to O06; the TPD4E05U06 +/-12 kV figure is device-level only and must not be quoted as a system rating. UFP VBUS connector-side capacitance: 1-10 uF |
| Expansion | 3.3 V I2C/SPI/UART/IRQ through JST GH 12-position candidate | Candidate pin allocation documented | Rail current limit, hot-plug/ESD/backfeed, cable capacitance and mirrored-harness check |

## I2C address and voltage check

| Address | Device | Bus level | Result |
| --- | --- | --- | --- |
| 0x20 | `TCA9535PWR` preferred candidate | 3.3 V | No collision; safe reset defaults and external pulls remain open |
| 0x30 | MMC5983MA | 3.3 V | Compatible |
| 0x44 | SHT40-AD1B-R2 | 3.3 V | Compatible |
| 0x46 | BMP581, SDO low | 3.3 V VDDIO | Compatible; the 0x47 alternate is available again since D22 removed TUSB320LAI from the bus, and 0x46 stays primary |
| 0x47 | ~~TUSB320LAI, ADDR low~~ **removed from the bus per D22 (GPIO mode)** | n/a since 2026-09-22 | Address freed by D22; the device is wired ADDR-NC (I2C interface physically disabled, SLLSEQ8D §7.2.4) and its GPIO-mode outputs are read by the TCA9535. Unpowered-state concern resolved structurally: VDD sits on `3V3_MAIN`, so no bus participant can back-power the die, and the bus no longer touches the device |
| 0x68 | ICM-42688-P, AD0 low | 3.3 V | Compatible |
| 0x6B | BQ25887 | 3.3 V | Logical address and open-drain behavior verified; TI BQ25887EVM-001 uses a 3.3 V LDO pull-up source for SDA/SCL/INT, closing the bus-voltage question. The shared pull-up value is now proposed at 2.2 k ohm +/- 1% from the 2026-09-22 window update (2.2 k is valid from the on-board estimate to the 400 pF specification ceiling at 100 kHz); the method and admissible window are in [the I2C bus budget](I2C_BUS_BUDGET.md) Result 3 |
| Published `0x70` | ST1633I touch | 3.3 V I/O permitted by display specification | Orient does not state whether `0x70` is a seven-bit address or an eight-bit write byte. Collision result is provisional until the controller source or two samples confirm the convention |

MAX-M10S uses UART in Rev A, so its default I2C address 0x42 is not placed on this bus.

## Boot, reset and off-state audit

| Item | Safe intent | Status |
| --- | --- | --- |
| ESP32 boot straps | GPIO0 is intentionally shared with button 1; GPIO3/45/46 unused; GPIO35/36/37 reserved by octal PSRAM | Logical allocation reviewed; button pull/debounce and manufacturing recovery test remain |
| RP2040 boot | W25Q128JVSIQ and ABM8-272-T3 preferred; expose SWD and a reviewed BOOTSEL recovery method | Parts selected as candidates; exact reset/boot circuit and physical CAD remain |
| Peripheral reset/enable | Slow non-safety controls may use `TCA9535PWR`; rails/protectors must reach safe states without either MCU | Default pull states and rail ownership remain open |
| Switched domains | Host pins become high impedance before rail removal; external pullups must not feed an off device | Must be proven per schematic block and then measured. SN74LVC1G07 Ioff live-insertion protection supports the reset path; TPS22918 QOD provides a defined discharge |
| Cell faults | Missing, reversed, mismatched, removed or deeply discharged cells cannot rely on firmware for primary protection | BQ25887 can start autonomously after POR; fail-safe hardware must inhibit charge until validation. Qualified reviewer must also resolve protection-ground/cutoff recovery and charge-under-load termination |

## Closure criteria

Gate 9 in `PROJECT_STATUS.md` can close before Astra only when every OPEN item above has an accepted circuit or explicit no-connect disposition, every peak and pullup is calculated from exact parts, every off-state and sequence has a defined expected result, and an independent review finds no voltage, address, boot-state, interrupt or back-power collision. The corresponding simultaneous Wi-Fi/BLE, LoRa TX, display refresh, SD write, GNSS, ADS-B, USB insertion/removal and domain power-cycling measurements are post-PCBA DVT work and do not block schematic capture when the pre-Astra analysis and test access are complete.

Subsystem evidence remains controlled by [the GPIO map](INTERFACE_GPIO_MAP.md), [power rail plan](POWER_RAIL_PLAN.md), [connector architecture](CONNECTOR_ARCHITECTURE.md), [audio architecture](AUDIO_ARCHITECTURE.md), [GNSS architecture](GNSS_ARCHITECTURE.md) and [component source index](../hardware/datasheets/README.md).
