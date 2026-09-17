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
| Shared I2C | ESP32 3.3 V; ICM-42688-P, MMC5983MA, BMP581, SHT40, touch, BQ25887, TUSB320LAI and expansion | Logical address map has no known collision; BQ25887 3.3 V bus level is supported by TI's BQ25887EVM-001. Pull-up method, bounds and the disqualification of the EVM resistance are worked in [the I2C bus budget](I2C_BUS_BUDGET.md) | Calculate total capacitance and pull-ups; resolve touch/power-device off-state behavior, external cable limit and stuck-bus recovery. BQ25887 SLUSD89B gives VIH 1.3 V, VIL 0.4 V and 1 uA leakage at a characterized 1.8 V pull-up; TI EVM guide SLUUC12 Table 3 independently implements SDA/SCL/INT pull-ups from an onboard 3.3 V LDO and JP12/JP13 use 10 kOhm. The EVM's 10 kOhm is evidence of the 3.3 V bus level only: at the 400 kHz target it supports about 35 pF of total bus capacitance, far below this board's multi-device bus plus expansion cable, so it must not be copied as a resistance value. Per-device Ci/IOL/Ii transcription remains the blocking input. TUSB320LAI (SLLSEQ8D note 2): with 3.3 V I2C the device VDD must stay at or above 3.0 V or the bus back-powers the device - disposition is to power TUSB320LAI VDD from `3V3_MAIN` and pull VBUS_DET to VBUS through the datasheet 900 kOhm |
| Shared SPI trunk | ESP32 3.3 V to microSD and SX1262; TFT uses a translated branch | Separate chip selects and bounded service policy defined | Exact TFT translator, loading, maximum clocks/modes and concurrency measurement |
| TFT branch | ESP32 3.3 V outputs to 1.8 V display logic | Write-only three-line, nine-bit `101` proposal through fixed A-to-B AXC channels; <=15 MHz panel clock | Controlled clarification of TFT VCC/VDDI/VDD, unused-pin ties, reset/enable startup and validation on two samples |
| PDM microphone | ESP32 3.3 V clock/data domain; T5838 is 1.8 V | `TXU0202DCUR` provides one channel each direction | Confirm OE/rail sequence, PDM clock quality, footprint/acoustic port and RF-noise test |
| GNSS UART/PPS | ESP32 and MAX-M10S both use 3.3 V I/O proposal | Direct logic levels are compatible while powered | Verify startup/reset sequencing and ensure neither side drives beyond the other's powered limits |
| RP2040 UART | ESP32 and RP2040 at 3.3 V, 921600 baud with RTS/CTS | Direct dedicated link candidate; host-side framing behavior passes 20 tests for payload shapes, sequencing, CRC, timestamp wrap, overflow visibility and resynchronization | Define reset/boot ownership and verify timing, sustained throughput and the same contract against real PIO/DMA silicon on the bench |
| USB 2.0 | Native ESP32 D+/D- through USB4105 candidate; four signal lines protected by TPD4E05U06 candidate; TPS259474L is first VBUS eFuse candidate | Connector/signal ESD selected; CC/eFuse are proposals | Footprints, 90-ohm geometry, USB default-current/enumeration policy, eFuse ILIM/OVLO/dVdt/ITIMER/discharge/reverse blocking and attach tests. UFP VBUS connector-side capacitance: 1-10 uF |
| Expansion | 3.3 V I2C/SPI/UART/IRQ through JST GH 12-position candidate | Candidate pin allocation documented | Rail current limit, hot-plug/ESD/backfeed, cable capacitance and mirrored-harness check |

## I2C address and voltage check

| Address | Device | Bus level | Result |
| --- | --- | --- | --- |
| 0x20 | `TCA9535PWR` preferred candidate | 3.3 V | No collision; safe reset defaults and external pulls remain open |
| 0x30 | MMC5983MA | 3.3 V | Compatible |
| 0x44 | SHT40-AD1B-R2 | 3.3 V | Compatible |
| 0x46 | BMP581, SDO low | 3.3 V VDDIO | Compatible; 0x47 alternate is prohibited while TUSB uses 0x47 |
| 0x47 | TUSB320LAI, ADDR low | 3.3 V bus candidate | No collision only while BMP581 stays at 0x46; unpowered state resolved by powering the device from `3V3_MAIN` per the back-power note above, pending schematic capture |
| 0x68 | ICM-42688-P, AD0 low | 3.3 V | Compatible |
| 0x6B | BQ25887 | 3.3 V | Logical address and open-drain behavior verified; TI BQ25887EVM-001 uses a 3.3 V LDO pull-up source for SDA/SCL/INT, closing the bus-voltage question. Final shared pull-up resistance remains open pending capacitance/sink/rise-time calculation; the method and admissible window are in [the I2C bus budget](I2C_BUS_BUDGET.md) |
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

Gate 9 in `PROJECT_STATUS.md` can close only when every OPEN item above has an accepted circuit or explicit no-connect disposition, every peak and pullup is calculated from exact parts, and an independent review finds no voltage, address, boot-state, interrupt or back-power collision. Board tests must then exercise simultaneous Wi-Fi/BLE, LoRa TX, display refresh, SD writes, GNSS, ADS-B, USB insertion/removal and domain power cycling.

Subsystem evidence remains controlled by [the GPIO map](INTERFACE_GPIO_MAP.md), [power rail plan](POWER_RAIL_PLAN.md), [connector architecture](CONNECTOR_ARCHITECTURE.md), [audio architecture](AUDIO_ARCHITECTURE.md), [GNSS architecture](GNSS_ARCHITECTURE.md) and [component source index](../hardware/datasheets/README.md).
