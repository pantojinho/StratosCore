# GPIO and slow-control gaps A5-A8: options and proposal

Status: **PROPOSAL ONLY. Nothing in the repository baseline changes because of this note.** Review date: 2026-09-23. Scope: issues A5-A8 in [the candidate issue list](../ISSUES.md). The baseline documents ([GPIO map](../../../../docs/INTERFACE_GPIO_MAP.md) / P12, [DIG-03 port map](../../../../docs/CONTROL_IO_REVIEW.md) / P24, [DIG-01](../../../../docs/DIGITAL_SUPPORT_REVIEW.md), [DSP-02](../../../../docs/DISPLAY_REQUIREMENTS.md), [connector map](../../../../docs/CONNECTOR_ARCHITECTURE.md)) are change-controlled. None of the options below changes a LOCKED row in [the decision register](../../../../docs/DECISIONS.md). D14 needs a "dedicated CS" and says nothing about how it is driven. Each recommendation still changes a reviewed allocation, so **the owner must accept it before any baseline, KiCad or BOM edit**. No KiCad file, root `docs/` file or commit was touched.

Conventions: **[Sx §/Table]** points to the source table below. "Calculated" means arithmetic from cited figures, not a measurement. Anything not in a primary source is marked **TBD**.

## 1. Primary sources (retrieved 2026-09-23)

| ID | Document | Revision | URL | Used sections | Retrieval note |
| --- | --- | --- | --- | --- | --- |
| S1 | Espressif ESP32-S3-WROOM-1/1U datasheet | v1.8 | https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf (redirects to documentation.espressif.com) | Table 3-1 + notes b/c; Ch. 4 Tables 4-1..4-5; Ch. 8 schematic note on GPIO45 | Official |
| S2 | Espressif ESP32-S3 Series datasheet | v2.2 | https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf | Table 2-1 Pin Overview (reset states), Table 2-2 Power-Up Glitches, §4.2.1.5 SPI | Official |
| S3 | TI TCA9535 data sheet | SCPS201F, Aug 2009, revised Sep 2026 | https://www.ti.com/lit/ds/symlink/tca9535.pdf | Fig. 4-1 (PW pinout), Table 4-1, §5.5, §5.6, §5.7, §6.4.1, Fig. 6-7, Tables 6-3/6-5/6-7 | Official. The repo cites Rev E; F is current |
| S4 | Semtech SX1261/2 data sheet | DS.SX1261-2.W.APP Rev 1.2, June 2019 (111 pages) | Mirror: https://cdn.sparkfun.com/assets/6/b/5/1/4/SX1262_datasheet.pdf (MD5 `2799e668e547da509d7fe271cb86fcc2`; the waveshare copy is byte-identical) | §3.5.5 Table 3-10, §5.2, §8.1, §8.2.2, §8.3.1, §8.4 Table 8-3, §9.1 | The semtech.com URL returned HTML to a non-browser client. Re-confirm against Semtech's own copy (same practice as LORA-01) |
| S5 | Raspberry Pi RP2040 datasheet | build-date 2025-02-20, build-version 3184e62-clean | https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf | §1.4.2, §2.12.5, §2.12.7, §5.5.2 Tables 614/619, §5.5.3 Table 625 | Official |
| S6 | Orient AFY240320A1-2.8INTH-C1 specification | Revision J (2021-07-20) | https://www.orientdisplay.com/wp-content/uploads/2021/11/AFY240320A1-2.8INTH-C1.pdf | CTP interface table (p. 8); §10.1 and §10.2 Power Sequence (p. 15, figures read visually) | Direct URL returned HTTP 403 to curl. Retrieved the identical path via the Wayback `id_` snapshot, MD5 `12d6c5d0341926526e66af3d0234666f`, title page "Revision J" |
| S7 | Espressif ESP-IDF Programming Guide, SPI Master driver (ESP32-S3) | v6.1 (stable) | https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/spi_master.html | `spics_io_num` (-1 = not used), bus acquiring | Firmware-behavior reference only, not an electrical source |
| — | Sitronix ST1633I controller data sheet | **not retrieved** | — | Touch RESET internal pull, VIL/VIH, minimum pulse | **TBD**: Orient rev J is the only touch source used |

## 2. Facts that drive the options

ESP32-S3 / WROOM-1-N16R8

- **F1** On Octal-PSRAM modules, IO35/IO36/IO37 connect to the PSRAM and are not available **[S1 Table 3-1 note b]**. The baseline map already allocates every other module GPIO except GPIO3/45/46 ([GPIO map](../../../../docs/INTERFACE_GPIO_MAP.md)).
- **F2** Strapping pins: GPIO0+GPIO46 set the boot mode, GPIO45 sets VDD_SPI, GPIO46 controls ROM message printing and GPIO3 selects the JTAG source. Defaults: GPIO0 weak pull-up (1), GPIO3 floating, GPIO45 and GPIO46 weak pull-down (0). The chip latches the straps at reset, and afterwards they work as ordinary IO **[S1 Ch. 4, Table 4-1]**.
- **F3** GPIO3 matters only when `EFUSE_STRAP_JTAG_SEL`=1. With the default eFuses (all 0) the GPIO3 level is "Ignored" **[S1 §4.4 Table 4-5]**.
- **F4** Joint Download Boot needs GPIO0=0 **and** GPIO46=0. SPI boot needs GPIO0=1 with GPIO46 at any value **[S1 §4.1 Table 4-3]**. A pull-up on GPIO46 would break the BUTTON_1/GPIO0 ROM-recovery path that D28 relies on.
- **F5** For modules with PSRAM, "the VDD_SPI voltage is fixed ... via eFuse, so their VDD_SPI voltage will not be affected by the GPIO45 level" **[S1 Ch. 8 note]**. This is a statement about Espressif's eFuse programming. This note does not rely on it (see A5 option table).
- **F6** GPIO8 is an ordinary GPIO (RTC_GPIO8, TOUCH8, ADC1_CH7, SUBSPICS1) with no strapping role **[S1 Table 3-1]**. Table 2-1 lists no internal pull for GPIO8, at reset or after reset **[S2 Table 2-1]**.
- **F7** GPIO1-GPIO14 and GPIO17 show a typical **60 us low-level glitch at power-up** **[S2 Table 2-2]**. GPIO3 and GPIO8 are in that list, and so are the existing chip selects GPIO9 (SX1262_NSS), GPIO10 (LCD_CS) and GPIO14 (SD_CS).
- **F8** As an SPI master, SPI2 "provides six SPI_CS pins for connection with six independent SPI slaves" with configurable CS setup and hold time **[S2 §4.2.1.5]**. LCD, SD, SX1262 and the expansion port need four.

TCA9535PWR

- **F9** The PW pinout is INT, A1, A2, P00-P07, GND, P10-P17, A0, SCL, SDA, VCC. There is **no RESET pin** **[S3 Fig. 4-1]**. The part resets only through its VCC power-on reset **[S3 §6.4.1]**, so an ESP32 EN/software/watchdog reset leaves every expander output in its last state.
- **F10** Power-up defaults: Configuration 0xFF (all inputs), **Output Port 0xFF (all ones)**, Polarity 0x00 **[S3 Table 6-3, Tables 6-5/6-7]**. The P-ports are push-pull **[S3 Table 4-1]**. The TCA9535 has no internal pull-ups **[S3 §3]**.
- **F11** VOL ≤ 0.5 V at IOL = 8 mA **[S3 §5.5]**. An output changes within tpv ≤ 200 ns of the data-byte ACK (VCC 2.3-5.5 V) **[S3 §5.7, Fig. 6-7]**. Writing one output register takes address + command + data, three bytes, each followed by an ACK **[S3 Fig. 6-5/6-7]**.
- **C1 (calculated)** At the D22 bus rate of 100 kHz, one output-register write is 27 SCL periods = 270 us, plus START/STOP set-up/hold (4-4.7 us each, **[S3 §5.6]**). That is about **0.27-0.28 ms per output edge**, so an assert/deassert pair adds **≥ 0.55 ms**. ESP-IDF I2C driver overhead is not included and is **TBD** (measure). A read-modify-write without a firmware shadow register adds a read (about 36 SCL periods, ≈ 0.37 ms). If another I2C transfer is already on the bus (sensor burst, touch read), the wait grows by that transfer.

SX1262

- **F12** NRESET (pin 15) is an active-low reset input **[S4 pin table]**. Toggling it performs a "factory reset" that is followed automatically by calibration, and "any previous context will be lost". The pin should be held low **typically 100 us** **[S4 §8.1]**. The data sheet gives no minimum/maximum pair: **TBD**.
- **F13** NRESET is referred to VBAT (not VBAT_IO), with VIL_N ≤ 0.2 × VBAT **[S4 §3.5.5 Table 3-10 and note 1]**. That is 0.66 V at 3.3 V, against the TCA9535 VOL of ≤ 0.5 V at 8 mA.
- **F14** NRESET has an internal pull-up of about 50 kΩ (typical) in Start-up, Sleep, STBY and active modes **[S4 §8.4 Table 8-3]**.
- **F15** After power-up or a hard reset, BUSY stays high until the chip reaches STDBY_RC. The host must wait for BUSY low before the first command **[S4 §8.2.2, §9.1, §8.3.1]**. Semtech's split-supply figure shows NRESET driven by the host controller **[S4 §5.2 Fig. 5-5]**.

RP2040

- **F16** RUN is a global asynchronous reset: low = reset, high = run. If no external reset is needed it "can be tied directly to IOVDD" **[S5 §1.4.2]**. Taking RUN low holds the chip in reset regardless of DVDD/POR/BOD state, and it can be driven "from an external source to start and stop the chip" **[S5 §2.12.5]**.
- **F17** RUN is pin 26, type Digital In (FT), IOVDD domain, reset state Pull-Up **[S5 Table 619]**. "Fault tolerant" means "very little current flows into the pin whilst it is below 3.63V and IOVDD is 0V" **[S5 Table 614]**. The standard/FT pull-up is 50-80 kΩ **[S5 Table 625]**. Whether that value applies to RUN is inferred from the table scope: **TBD**.
- **F18** The CHIP_RESET register field HAD_RUN records a RUN-pin reset **[S5 §2.12.7]**. **No minimum RUN low-pulse width was found in S5: TBD.**

Orient C1 touch (ST1633I)

- **F19** CTP FPC pin 1 is RESET, "Reset low" **[S6 CTP interface table, p. 8]**.
- **F20** RESET "should be held low before power on and power off". After VDD and IOVDD are at normal voltage, it must stay low **≥ 5 ms**. It must be asserted **≥ 100 us** before VDD falls **[S6 §10.2, p. 15 figure]**.
- **F21** TFT (for the shared-reset option): in Sleep-Out mode, VDD/VDDI may be powered down only ≥ 120 ms after RESX falls. In Sleep-In mode the wait is ≥ 0 ms. Note 1 says the display module is not damaged if its sequences are not met **[S6 §10.1]**. Rev J has no equivalent no-damage statement for the CTP (**TBD**). The internal or module pull on CTP RESET is **not documented: TBD** (measure on the two labeled samples).

## 3. Port and pin budget

The TCA9535 map in DIG-03 uses 12 ports. P07, P14, P15 and P17 are spare, and P10 is reserved as radio aux. The candidate filled all 16 ports. Two of them are candidate-only proposals outside A5-A8: P15 `BUCK_PG` and P17 `CHG_EN`. **That is why ISSUES.md A8 found "no port left". It does not hold for the DIG-03 baseline.**

| Port | DIG-03 baseline | Candidate (one-shot) | This proposal |
| --- | --- | --- | --- |
| P00-P05 | SD_CD, TUSB_OUT1-3, CHG_INT, EXP_PRESENT | same | same |
| P06 | LCD_RST_N (100 k pull-down) | LCD_RST_CTRL, shared with touch RESET | LCD_RST_N, TFT only (DSP-02 unchanged) |
| P07 | spare | EXP_CS_N | **TOUCH_RST_N** (A8) |
| P10 | reserved SX_NSS_HOLD (100 k pull-up) | SX_NRESET | **SX_NRESET** (A6) |
| P11-P13 | SD/AUD/ADSB `*_EN` (pull-downs) | same | same |
| P14 | spare | RP_RUN | **RP_RUN** (A7) |
| P15 | spare | BUCK_PG (candidate proposal) | spare. BUCK_PG is a separate owner decision |
| P16 | EXP_PERIPH_RST | same | same |
| P17 | spare | CHG_EN (candidate proposal; O05/PWR-03 territory) | spare. CHG_EN is a separate O05/qualified-review decision, because the expander must not own charger safety ([control review](../../../../docs/CONTROL_IO_REVIEW.md)) |
| ESP32 GPIO8 | LCD_AUX (reserved, no committed function) | LCD_AUX → 0R (R55) → translator OE | **EXP_CS_N** (A5). R55 removed; OE stays on its DSP-02 10 k pull-downs |

Result: A5-A8 close with **P15 and P17 still spare**. If the owner also accepts BUCK_PG and CHG_EN, no port remains for optional host control of the translator OE. That control is optional under DSP-02, because the branch wakes enabled.

## 4. A5: expansion SPI chip select `EXP_CS_N` (connector pin 9)

| # | Option | CS timing | Boot / ESP32-reset / off behavior | Main risks | Verdict |
| --- | --- | --- | --- | --- | --- |
| A5-1 | TCA9535 port (candidate: P07, 100 k pull-up) | ≥ 0.55 ms added per transaction (C1), plus I2C contention; no hardware CS | Expander POR → input → pull-up deselects. **ESP32 reset/panic does not reset the expander (F9): a CS held low survives the reset**, and the expansion device stays selected on the shared SCLK/MOSI/MISO | A stuck-selected accessory drives shared MISO during SD/SX1262/LCD traffic and treats their SCLK/MOSI as its own commands. The SPI bus lock is held across I2C transfers, which conflicts with the bounded-chunk SPI contract and SX1262 service timing ([GPIO map](../../../../docs/INTERFACE_GPIO_MAP.md) shared-SPI contract). Cannot drive CS from ISR/queued DMA transactions | Reject |
| A5-2 | **ESP32 GPIO8 (release the LCD_AUX reservation)** | Hardware CS on SPI2: ns-class, configurable setup/hold (F8) | Table 2-1 lists no internal pull (F6), so an external pull-up holds CS deasserted through reset/boot. A 60 us typical low glitch at power-up (F7) is the same exposure the existing SD/SX/LCD CS lines already have. ESP32 reset returns the pin to its reset state, so the accessory is deselected | Loses the unassigned GPIO8 reserve and the optional GPIO8 → translator OE link (R55 in the candidate). DSP-02 already makes OE default-enabled through pull-downs | **Recommended** |
| A5-3 | ESP32 GPIO3 (strap) | Same as A5-2 | Strap ignored with default eFuses (F3). If `EFUSE_STRAP_JTAG_SEL` is ever burned, the CS pull-up selects USB Serial/JTAG (Table 4-5), which is consistent with D28. 60 us power-up glitch (F7) | Breaks the current map rule "strapping pins unused". Creates a latent dependency on eFuse policy, and an accessory that back-drives the pin at reset would matter only if that eFuse is burned | Fallback if the owner wants to keep GPIO8 reserved |
| A5-4 | ESP32 GPIO45 (strap) | Same | CS needs a pull-up, which changes the VDD_SPI strap to 1 (F2). Safe only if the module's VDD_SPI eFuse is fixed, as Espressif states for PSRAM modules (F5). The project has not verified this per lot | A wrong strap selects 1.8 V for the 3.3 V flash | Reject |
| A5-5 | ESP32 GPIO46 (strap) | Same | A pull-up sets GPIO46=1, so GPIO0=0 (BUTTON_1) no longer yields Download Boot (F4) | Breaks D28 recovery | Reject |
| A5-6 | Move a direct signal to the expander to free a GPIO (e.g. BUTTON_2/GPIO48 or EXP_IRQ/GPIO38 as polled expander inputs) | Frees a direct CS | The expander INT is not wired to an ESP32 GPIO in the baseline, so the moved signal becomes I2C-polled | A D04 user button or the D14 expansion IRQ would depend on I2C/expander health, adding polling load on the 100 kHz bus (D22). Every remaining direct signal (BUSY, DIO1, PPS, IMU INT, PWM, RTS/CTS, UARTs, USB, PDM) is latency- or peripheral-bound | Reject: GPIO8 is already free of committed function |
| A5-7 | Share/decode CS (demux or daisy chain) | — | Needs extra silicon and a decode GPIO anyway | New part, new review | Reject |

**Recommendation A5-2.** Assign ESP32 **GPIO8 → `EXP_CS_N`** (active low), driven as a hardware SPI2 CS.

- **Electrical:** pull-up from `EXP_CS_N` to **`3V3_EXP`** (not `3V3_MAIN`), so an unpowered accessory is never fed through the pull-up if `3V3_EXP` becomes switched. `3V3_EXP` is currently a 0R from `3V3_MAIN` in the candidate. Pull-up value **TBD** (10-100 kΩ class, chosen with the cable/ESD review). Series resistor and ESD at the connector: **TBD** under the existing connector release gates. Remove the candidate's R55 (GPIO8 → `LCD_XLT_OE`). `LCD_XLT_OE` keeps only its DSP-02 10 k pull-downs, so the branch is always enabled. A GPIO3 alternative would need the same pull-up.
- **Firmware:** register the expansion device on the SPI2 host with `spics_io_num = 8` **[S7]**. SPI2 supports six hardware CS lines **[S2 §4.2.1.5]**, but S7 describes "three CS pins" per master generically, so confirm the driver's per-host CS count on the selected ESP-IDF version (**TBD**). A software-toggled GPIO CS is the fallback in either case. Keep the shared-SPI contract (bounded chunks, restore mode/frequency). While `3V3_EXP` is off, never drive CS high into the accessory.
- **PCB:** one net moves from a TCA9535 pin (U13 pin 11) to WROOM pin 12 (IO8). Route to J2 pin 9. No new footprint.
- **Cost:** no new part. Resistor count unchanged (the pull-up moves; R55 is deleted). Dated price not quoted: **TBD / none expected**.
- **Boot/off-state:** unpowered ESP32 → CS held at `3V3_EXP` by the pull-up (deselected). ESP32 reset/boot → pin not driven, pull-up deselects, typical 60 us low glitch possible at power-up with no SCLK (F7). Whether a given accessory tolerates that glitch is device-specific: **TBD**. Panic/watchdog → CS released by the chip reset. The expander is not involved.

**OWNER DECISION REQUIRED (A5):** accept GPIO8 = `EXP_CS_N` and release the `LCD_AUX` reservation, or choose GPIO3 (A5-3). Until the owner accepts, the baseline GPIO map, DIG-03 and `hardware/kicad/01_compute.kicad_sch` stay unchanged.

## 5. A6: SX1262 `NRESET`

| # | Option | Timing fit | Boot / reset / off behavior | Risks | Verdict |
| --- | --- | --- | --- | --- | --- |
| A6-1 | **TCA9535 P10** (DIG-03 already reserves it as radio aux, with a 100 k pull-up) | Reset needs about 100 us low (F12). I2C latency (C1) only makes the pulse longer, and it is not timing-critical | Expander POR → input → internal 50 k (F14) + external pull-up release NRESET, and the SX1262 runs its own POR/calibration. **ESP32 warm reset does not reset the expander (F9)**, so the radio stays in whatever state the port was left in until firmware re-initializes the expander | Must never be driven high by push-pull: use open-drain emulation (below) | **Recommended** |
| A6-2 | No host control (internal pull-up only, or RC) | — | The radio sits on always-on `3V3_MAIN` (candidate; rail plan), so a hung radio can be recovered only by a full power cycle | Loses recovery; §8.1 frames reset as "on request" | Reject |
| A6-3 | Tie to ESP32 EN (CHIP_PU) | — | Follows only hardware resets. Software panic/watchdog resets do not pulse EN. Adds the SX1262 pull-up to the EN RC network | No firmware control; perturbs ESP32 EN timing | Reject |
| A6-4 | Direct ESP32 GPIO3 | ns-class | 60 us power-up low glitch (F7) coincides with the radio's own POR | Uses the last non-risky strap pin for a slow signal | Keep in reserve |

**Recommendation A6-1.** Rename `SX_NSS_HOLD` → **`SX_NRESET`** on P10.

- **Electrical:** keep the external pull-up on the **SX1262 VBAT rail** (`3V3_MAIN` today; the net is referred to VBAT, F13). 100 kΩ (candidate R70) in parallel with the internal ≈ 50 kΩ is acceptable. VIL_N 0.66 V vs VOL ≤ 0.5 V at 8 mA (F11/F13). With the pull-ups the sink current is ≈ 0.1 mA (calculated), so there is margin.
- **Firmware:** open-drain emulation. At every boot, first write Output bit P10 = 0 (the default is 1, F10). Then assert reset = Config bit P10 → 0 (output low) and release = Config bit P10 → 1 (input). Hold low ≥ 1 ms (engineering margin above the "typically 100 us", not a data-sheet minimum). After release, wait for BUSY low before the first command (F15). Re-apply all radio configuration, because context is lost (F12).
- **PCB:** unchanged from the candidate (U13 pin 13 → U40 pin 15).
- **Cost:** none (existing port and resistor).
- **Boot/off-state:** unpowered expander on `3V3_MAIN`: expander and radio share the rail and fall together, so there is no back-power path. Expander POR → radio released. ESP32 crash with NRESET asserted → radio held in reset until the next firmware init (safe, silent radio).

**OWNER DECISION REQUIRED (A6):** accept P10 = `SX_NRESET` (the rename frees the "radio aux" reservation; LORA-02 has no other identified use for it).

## 6. A7: RP2040 `RUN` host control

| # | Option | Timing fit | Boot / reset / off behavior | Risks | Verdict |
| --- | --- | --- | --- | --- | --- |
| A7-1 | **TCA9535 P14** (DIG-01 already requires expander host control; P14 is a DIG-03 spare) | No minimum RUN pulse in S5 (F18: TBD). With the 10 k/100 nF RC (τ = 1 ms, calculated) the release edge is slow. I2C latency is irrelevant | Expander POR → input → RUN released by the RC pull-up. ESP32 warm reset leaves the port state unchanged (F9) | Push-pull high can fight a debugger/fixture pulling RUN low at the DFT RUN pad (DIG-01/O28). If the pull-up rail is switched (candidate: `3V3_ADSB`), a push-pull high would back-feed that rail **through the 10 k pull-up**. The RUN pin itself is fault-tolerant (F17) | **Recommended, with mandatory open-drain emulation** |
| A7-2 | No RUN control; recover by power-cycling the ADS-B domain (P13) | — | Works only if the RP2040 is on the switched domain (SYS-02 **TBD**; the rail plan currently shows it on `3V3_MAIN`) | A power cut during a flash program/erase can corrupt the flash (W25Q Rev M §8.2.19, already recorded in DIG-01). No graceful reset | Keep only as a secondary recovery |
| A7-3 | Direct ESP32 GPIO3 | ns-class | 60 us power-up glitch on RUN = a brief extra reset during ESP32 power-up | Spends the reserve pin on a slow signal | Keep in reserve |
| A7-4 | SWD from the ESP32 (Rescue DP reset) | — | — | Needs two GPIOs that do not exist | Reject |

**Recommendation A7-1.** P14 = **`RP_RUN`**, open-drain emulated.

- **Electrical:** the RUN pull-up (DIG-01 10 kΩ + 100 nF) must go to the **same rail as RP2040 IOVDD**. DIG-01 text says `3V3_MAIN`; the candidate uses switched `3V3_ADSB`. SYS-02 must pick one, and the pull-up must follow it. The expander never sources current into RUN: sink only, released by the pull-up. The RUN pad/Tag-Connect pin stays directly on the net for DFT, so no expander path lies in the recovery chain ([control review](../../../../docs/CONTROL_IO_REVIEW.md) recovery rule).
- **Firmware:** Output bit P14 = 0 at every boot before any Config write (F10). Assert = Config → output. Hold low for **TBD** (no data-sheet minimum; propose ≥ 10 ms of margin for the 100 nF RC, to be validated in the DIG-01 corner test). Release = Config → input. RP2040 firmware reports HAD_RUN over the UART (F18). Quiesce RP2040 flash writes before asserting RUN (DIG-01 flash rule). RUN control plus the existing UART is the precondition for any future ESP32-hosted RP2040 update path. That path is not designed here.
- **PCB:** unchanged from the candidate (U13 pin 17 → RP2040 pin 26, RC and test point local to the RP2040).
- **Cost:** none.
- **Boot/off-state:** RP2040 domain off → RUN sits at 0 V through its own pull-up. The expander input sees a low level, which is harmless, and there is no back-feed because the port never drives high. Expander unpowered → it shares `3V3_MAIN` with its pull-ups, so no path. ESP32 crash while RUN is asserted → RP2040 held in reset until the next init (ADS-B silent, acceptable, non-safety).

**OWNER DECISION REQUIRED (A7):** accept P14 = `RP_RUN` with the open-drain-only rule, and record that its pull-up rail is bound to the SYS-02 RP2040 domain choice.

## 7. A8: touch-controller `RESET`

| # | Option | Timing fit (F20) | Boot / off behavior | Risks | Verdict |
| --- | --- | --- | --- | --- | --- |
| A8-1 | Share P06 `LCD_RST_CTRL` (candidate) | Power-on ≥ 5 ms is met if firmware holds the shared line low ≥ 5 ms after the rails are valid. Before a controlled power-off it must assert ≥ 120 ms ahead (TFT in Sleep-Out, F21) or put the TFT into Sleep-In first; that covers the CTP 100 us | The 100 k pull-down holds both in reset at power-up **only if** the module adds no stronger pull-up on CTP RESET. That pull is undocumented (F21: **TBD**), and a divider could leave RESET indeterminate | Every touch recovery (e.g. a touch controller holding the shared I2C SDA low) forces a full TFT reset and re-init (ST7789-class timing), and vice versa | Acceptable fallback only |
| A8-2 | **Dedicated TCA9535 port (P07, freed by A5-2) `TOUCH_RST_N`** | Same F20 rules, enforced independently of the TFT | Pull-down holds reset asserted from power-up until firmware releases it. Touch VDD and I/O on `3V3_MAIN` (candidate J4) share the expander rail, so there is no rail crossing | Uses a spare port (P15 and P17 still remain) | **Recommended** |
| A8-3 | RC-delayed reset, no host control | Meets ≥ 5 ms at power-up by RC | Cannot pre-assert before power-off; no recovery of a hung controller | Loses I2C bus recovery | Reject |
| A8-4 | Direct ESP32 GPIO3 | Fine | 60 us power-up glitch is inside the reset-asserted window anyway | Spends the reserve pin | Keep in reserve |

**Recommendation A8-2.** P07 = **`TOUCH_RST_N`**, output; release by driving push-pull high (touch I/O is specified 1.6-3.6 V in the [display spec](../../../../docs/DISPLAY_REQUIREMENTS.md)).

- **Electrical:** pull-down to GND on the net. Proposed **10 kΩ** instead of 100 kΩ, so the net still reads low if the undocumented module/controller pull-up exists. Confirm the final value after measuring the RESET pull on both labeled samples (**TBD**). A high level sources 0.33 mA into 10 k (calculated), which is within TCA9535 drive. Touch VDD must stay on the expander's always-on rail; otherwise, move the pull-down and review back-power.
- **Firmware:** keep reset asserted ≥ 5 ms after `3V3_MAIN` is valid. Firmware must enforce that time explicitly; ESP32 boot time is not counted on. On controlled shutdown, assert ≥ 100 us before the touch rail falls. Uncontrolled power loss (cell removal; no main switch, see ISSUES A10) cannot meet the 100 us pre-assert. CTP consequences are **TBD** on samples. Reset the touch controller as the first step of I2C stuck-bus recovery if it is the device holding SDA.
- **PCB:** J4 pin 1 moves from `LCD_RST_CTRL` to the new net (U13 pin 11, which EXP_CS_N vacated). The candidate's R51 stays on P06 for the TFT, and one resistor is added for the touch pull-down.
- **Cost:** +1 resistor, −1 (R55, from A5). Dated price not quoted: **TBD / none expected**.
- **Boot/off-state:** expander unpowered or at POR → input → pull-down → touch held in reset (the required "low before power on"). ESP32 crash → the port keeps its last state (F9). Firmware re-init at boot asserts reset again before the touch driver starts.

**OWNER DECISION REQUIRED (A8):** accept P07 = `TOUCH_RST_N` (this depends on A5-2 being accepted). If A5 goes to the expander after all, choose between A8-1 (shared reset) and using P15/P17.

## 8. Expander firmware contract implied by A6-A8 (for review, not a baseline change)

1. Re-initialize all TCA9535 registers on **every** ESP32 boot, because a warm reset never resets the expander (F9). Do not assume POR defaults.
2. Write the Output registers (0x02/0x03) **before** the Configuration registers (0x06/0x07). Otherwise a port switched to output drives the default `1` (F10).
3. P10 `SX_NRESET` and P14 `RP_RUN` are **sink-only**: Output bit 0, toggled through Config. P06/P07 are push-pull, released high. P11-P13 are enables, driven high to turn a domain on (DIG-03).
4. Keep one shadow copy of Output/Config under the I2C bus mutex. Port 0 holds LCD and touch resets, and port 1 holds enables and resets, so concurrent read-modify-writes must be serialized.
5. No function in this note is a safety function (DIG-03 rule preserved).

## 9. Side findings for independent review (outside A5-A8; no edits made)

- [GPIO map](../../../../docs/INTERFACE_GPIO_MAP.md) says GPIO46 is "input-only". S2 Table 2-1 lists GPIO46 as type IO, and S1 Table 3-1 lists I/O/T. The conclusion (avoid it: boot strap, F4) is unchanged; the stated reason is not. The same map's GPIO45 rationale should also cite the S1 Ch. 8 eFuse note (F5).
- [Control review](../../../../docs/CONTROL_IO_REVIEW.md) says to "connect RESET_N ... only if system review shows a recovery benefit". The TCA9535 has no RESET pin (F9); that is a TCA9539 feature. It also cites TCA9535 Rev E; the current revision is SCPS201F.
- The candidate's `RP_RUN` pull-up goes to `3V3_ADSB`, while DIG-01 states `3V3_MAIN`. That is an open SYS-02 inconsistency (see A7).
- [RF architecture](../../../../docs/RF_ARCHITECTURE.md) calls the SparkFun-hosted SX1261/2 file a "20-page abridged edition". The file retrieved today from that CDN (MD5 above) opens as the full 111-page Rev 1.2 document. Some tools misreport the page count of this encrypted PDF, so the description may be mistaken. Verify before relying on it.

## 10. Owner decision summary

| Gap | Recommended | Fallback | Baseline documents that would change after acceptance |
| --- | --- | --- | --- |
| A5 | GPIO8 → `EXP_CS_N`, pull-up to `3V3_EXP`, R55 removed | GPIO3 | GPIO map (P12), `01_compute` sheet, connector map note, DSP-02 note on GPIO8/OE |
| A6 | P10 → `SX_NRESET`, sink-only | — | DIG-03 port table, RF/LoRa application |
| A7 | P14 → `RP_RUN`, sink-only, pull-up on RP2040 IOVDD rail | ADS-B domain power cycle as secondary | DIG-03 port table, DIG-01 (pull-up rail with SYS-02) |
| A8 | P07 → `TOUCH_RST_N`, 10 k pull-down (TBD after samples) | Shared P06 (A8-1) | DIG-03 port table, DSP-02 touch-reset row |

**OWNER DECISION REQUIRED for each row. No baseline document, KiCad sheet or BOM is to be changed until the owner accepts it and records the outcome in `docs/DECISIONS.md`.**
