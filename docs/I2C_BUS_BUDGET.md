# Shared I2C bus capacitance and pull-up budget

Status: calculation worksheet opened and substantially filled 2026-09-17. **2026-09-22 (SYS-01): the owner's D22/P26 decision is applied in this worksheet — the shared peripheral I2C bus runs at 100 kHz Standard-mode and the TUSB320LAI is removed from the bus in favor of its GPIO mode.** The remaining open element is the block-by-block off-state review (touch and power devices), not the bus arithmetic; see the Result 3 disposition and the closure-criteria notes.

**No number in this document is a measurement, and no per-device figure has been invented.** Every quantity is either (a) arithmetic derived in-document from the stated inputs, (b) a figure already cited elsewhere in this repository with its source, or (c) an explicit TBD naming the document and section that must supply it.

## Bus definition

| Parameter | Value | Source |
| --- | --- | --- |
| Bus speed target | **100 kHz (I2C Standard-mode)** per accepted decision D22/P26 (owner, 2026-09-21) | Previously 400 kHz; see Result 3 for why the device-level evidence selected 100 kHz |
| Bus logic level | 3.3 V | [Electrical compatibility matrix](ELECTRICAL_COMPATIBILITY_MATRIX.md) I2C address and voltage check |
| Maximum rise time `tr` at Standard-mode | 1000 ns | **Primary source retrieved 2026-09-17: NXP UM10204 Rev. 7.0 (1 October 2021)** — Table 10 Standard-mode `tr` 1000 ns; rise-time relation `T = t2 - t1 = 0.8473 x Rp x Cb` derived in §7.2 (Eq. 1 / Figure 41). Corroborated in-repo by Bosch BMP581 §5.2.2 (quotes UM10204 Rev.6) and Sensirion SHT4x Table 4 (same 0.8473 formula) |
| Maximum bus capacitance `Cb` at Standard-mode | 400 pF | UM10204 Rev. 7.0 Table 10 (400 pF max; identical to Fast-mode) |
| Pull-up source rail | `3V3_MAIN` proposed | Proposal only, see "Pull-up rail ownership" |

**PENDING CITATION:** ~~the `tr` and `Cb` limits and the rise-time formula below are the standard I2C-bus specification values...~~ **RESOLVED 2026-09-17, primary source:** UM10204 **Rev. 7.0** (1 October 2021) was retrieved directly from NXP and its Fast-mode values confirmed: `tr` 300 ns (Table 10), `Cb` 400 pF (Table 10), rise-time relation `T = 0.8473 x Rp x Cb` (§7.2 Eq. 1). Note the BMP581/SHT4x in-repo citations reference **Rev. 6 (2014)**; Rev. 7.0 changed terminology (master/slave to controller/target) and Table 5 only — the electrical values used here are unchanged between the revisions, so the second-hand citations remain valid corroboration.

## Governing relations

Three constraints bound the pull-up resistance `Rp`. All three must hold simultaneously.

**1. Rise time (upper bound on Rp).** The bus rises through an RC from the pull-up into the total bus capacitance. Between the 0.3 x VDD and 0.7 x VDD I2C thresholds this gives

```
tr = 0.8473 x Rp x Cb        =>        Rp_max = tr / (0.8473 x Cb)
```

**2. Sink capability (lower bound on Rp).** Every device that pulls the line low must reach its specified `VOL` while sinking the pull-up current. The binding limit is the *weakest* driver on the bus:

```
Rp_min = (VDD - VOL_max) / IOL_min          over all devices on the bus
```

**3. Leakage and high-level margin (upper bound on Rp).** When every device releases the line, the sum of input leakage currents drops the idle level below VDD. The result must still clear the highest `VIH` on the bus:

```
VDD - (Rp x SUM(Ii))  >=  VIH_max          over all devices on the bus
```

The admissible window is `Rp_min <= Rp <= min(Rp_max_risetime, Rp_max_leakage)`.

## Result 1: the BQ25887 EVM 10 kOhm value is disqualified for this bus

The electrical matrix currently records, with its source, that TI's `BQ25887EVM-001` guide `SLUUC12` Table 3 implements SDA/SCL/INT pull-ups at **10 kOhm** from an onboard 3.3 V LDO. That figure is cited in this repository as evidence that a **3.3 V bus level** is supported by the manufacturer. It is **not** transferable as this board's resistance value.

Inverting the rise-time relation for `Rp` = 10 kOhm at the 400 kHz target:

```
Cb_max = tr / (0.8473 x Rp) = 300e-9 / (0.8473 x 10e3) = 35.4 pF
```

A 10 kOhm pull-up therefore supports a total bus capacitance of only about **35 pF** at 400 kHz. StratosCore's shared bus carries nine or more device pin loads plus board traces plus an external expansion cable (inventory below), which cannot plausibly stay under 35 pF. Even relaxed to 100 kHz Standard-mode (`tr` = 1000 ns) the same resistance supports only about **118 pF**.

**Disposition:** `SLUUC12` Table 3 remains valid evidence for the 3.3 V bus level and for BQ25887 open-drain behavior, and is unaffected as such. Its 10 kOhm resistance must not be copied into StratosCore. This is the `AGENTS.md` rule 5 prohibition on transferring values between boards without validation, applied to a digital bus. The electrical matrix has been annotated accordingly.

## Result 2: admissible pull-up window as a function of bus capacitance

`Rp_max` from rise time, computed at the 400 kHz / 300 ns target:

| Total `Cb` | `Rp_max` at 400 kHz | `Rp_max` at 100 kHz | Note |
| ---: | ---: | ---: | --- |
| 50 pF | 7.08 kOhm | 23.6 kOhm | Optimistic; internal devices only, short traces |
| 100 pF | 3.54 kOhm | 11.8 kOhm | |
| 150 pF | 2.36 kOhm | 7.87 kOhm | |
| 200 pF | 1.77 kOhm | 5.90 kOhm | |
| 250 pF | 1.42 kOhm | 4.72 kOhm | |
| 300 pF | 1.18 kOhm | 3.94 kOhm | |
| 400 pF | 885 Ohm | 2.95 kOhm | I2C specification ceiling; bus is non-compliant above this |

`Rp_min` from sink capability. The binding value depends on the weakest `IOL` on the bus, which is TBD per device below. Evaluated against the I2C Fast-mode reference sink of 3 mA at `VOL` = 0.4 V:

```
Rp_min = (3.3 - 0.4) / 3e-3 = 967 Ohm
```

**Reading of the table:** if any device on the bus guarantees only the 3 mA reference sink, then `Rp` >= 967 Ohm, and the bus is simultaneously capped at 885 Ohm once `Cb` reaches the 400 pF specification ceiling. The two constraints cross at approximately 370 pF. **Total bus capacitance must therefore be held meaningfully below the specification ceiling** — there is no valid resistance at 400 kHz for a 3 mA-sink device on a bus at or near 400 pF. Reducing `Cb`, raising the guaranteed sink, splitting the bus or dropping to 100 kHz are the available levers; none is selected here.

## Device inventory and required transcription

Participants are taken from the [electrical compatibility matrix](ELECTRICAL_COMPATIBILITY_MATRIX.md) I2C rows and the [GPIO map](INTERFACE_GPIO_MAP.md). Each row needs three figures before `Cb`, `Rp_min` and the leakage check can be evaluated.

| Device | Address | Pin capacitance `Ci` | Sink `IOL` at `VOL` | Input leakage `Ii` | Source to transcribe from |
| --- | --- | --- | --- | --- | --- |
| ESP32-S3-WROOM-1-N16R8 (master) | — | CIN 2 pF typ (generic pin) | GPIO open-drain master: IOL 28 mA typ @ VOL = 0.495 V, VDD 3.3 V, PAD_DRIVER = 3 (module datasheet v1.8 §DC characteristics; note VOL spec is 0.1 x VDD) | IIH/IIL 50 nA max | Espressif ESP32-S3-WROOM-1 v1.8, DC table, recorded 2026-09-17 |
| `TCA9535PWR` | 0x20 | CI 8 pF max (SCL); Cio 9.5 pF max (SDA); Cio 9.5 pF max (P port) | SDA/INT 3.5 mA @ Tj <= 85 °C class; P-port 18 mA @ Tj <= 85 °C | II +/-1 uA max (SCL/SDA/A2-A0, VI = VCC or GND); P port +/-1 uA | TI SCPS201F (Rev F, revised 2026-09), §5.5 EC tables, recorded 2026-09-17 |
| MMC5983MA | 0x30 | not stated | not stated; VOL max 0.6 V @ VIO 3.0 V with sink current unspecified | Ii +/-10 uA max (0.1-0.9 VIO) | MEMSIC MMC5983MA Rev A, DC + I2C interface tables, recorded 2026-09-17 |
| SHT40-AD1B-R2 | 0x44 | not stated; SHT4x Table 4 ties Cb to Rp via `Cb < trise/(0.8473*Rp)` (400 pF @ Rp <= 820 ohm FM; 340 pF @ Rp = 390 ohm FM+) | not stated; VOL 0.2 x VDD max with Rpullup > 390 ohm (VDD 1.62-2.0 V) / > 820 ohm (general) | not stated separately | Sensirion SHT4x v7.3 §3 Electrical Specifications Table 4, recorded 2026-09-17 |
| BMP581 | 0x46 | not stated | not stated; BMP581 defers I2C timing entirely to UM10204 Rev.6 (BST-BMP581-DS004-13 §5.2.2); IOL drive-strength tables (§5.3 Tables 20/21) are image-only in extraction — values not transcribed | I_IL/I_IH 1 uA max (§5.2 Table 17 general interface parameters) | Bosch BST-BMP581-DS004-13 rev 1.13, recorded 2026-09-17 |
| TUSB320LAI | **REMOVED FROM BUS per D22/P26** (2026-09-22) — GPIO mode, ADDR pin NC | Was: 0x47 | Was: not stated; **device bus-load limit CBUS = 400 pF @ <=100 kHz but only 100 pF @ 400 kHz** (SLLSEQ8D §6.6) — the constraint that originally selected the 100 kHz option | Was: **IOL 1.6 mA @ VOL 0.4 V (open-drain SDA/SCL)** — was the weakest sink on the bus | TI SLLSEQ8D (Rev D, May 2017) §6.5 + §6.6 + §7.2.4, recorded 2026-09-17; GPIO-mode removal recorded 2026-09-22. Figures retained for the record; the device no longer loads SDA/SCL |
| ICM-42688-P | 0x68 | CI < 10 pF (digital inputs) | IOL 3 mA @ VOL = 0.4 V (6 mA @ 0.6 V); output leakage 100 nA | (covered by leakage row) | TDK DS-000347 v1.9, Digital DC table, recorded 2026-09-17 |
| BQ25887 | 0x6B | not stated in SLUSD89B | **VOL <= 0.4 V @ 5 mA sink** (I2C INTERFACE SCL/SDA sub-table) | 1 uA high-level leakage characterized at a 1.8 V pull-up rail (SDA/SCL IBIAS row; CD 2.5 uA, PSEL 1 uA) | TI SLUSD89B §7.5, recorded 2026-09-17 |
| ST1633I touch | `0x70` published | TBD | TBD | TBD | Orient specification revision J; address convention is itself unresolved (O01) |

Non-device contributions to `Cb`:

| Contribution | Status | Note |
| --- | --- | --- |
| PCB trace capacitance | TBD | Not calculable before placement and the confirmed four-layer stack (gate 8, O10). Depends on routed length and reference-plane spacing |
| Expansion connector and external cable | TBD — **dominant unknown** | [Expansion interface](EXPANSION_INTERFACE.md) states the cable limit is unchosen; the GPIO map already requires "a measured cable limit". An external cable can exceed every on-board contribution combined |
| Any series/ESD part placed on SDA/SCL | None currently proposed | If added, its shunt capacitance counts. For scale, the `TPD1E0B04DPYR` used on the GNSS feed is cited at 0.18 pF maximum |

## Result 3: evaluated window with transcribed figures — UPDATED 2026-09-22 for D22 (100 kHz, TUSB320LAI off-bus)

The original 2026-09-17 evaluation (recorded below for the evidence trail) showed the TUSB320LAI binding the 400 kHz option twice over: its 1.6 mA sink caps `Rp_min` at 1812 ohm and its own CBUS limit caps total capacitance at 100 pF at 400 kHz. **The owner accepted option (a) plus (b) as decision D22 on 2026-09-21 (proposal P26): run the shared peripheral I2C bus at 100 kHz and remove the TUSB320LAI from it in favor of its GPIO mode.** Both constraints therefore leave the shared-bus arithmetic:

- **Weakest remaining sink:** the I2C-specification 3 mA reference class, implemented by ICM-42688-P (3 mA @ 0.4 V, DS-000347 v1.9) and approximated by BQ25887 (5 mA @ 0.4 V, stronger) and TCA9535 SDA/INT (3.5 mA @ Tj <= 85 C class, stronger). MMC5983MA's VOL 0.6 V with unspecified sink remains the conservative outlier; at 100 kHz with 2.2 k ohm the pull-up sink demand is 1.32 mA, and a 0.6 V VOL at any sink >= 1.32 mA still holds the line at or below the 0.4 V threshold every other receiver specifies, so the 3 mA-class bound stands:
  ```
  Rp_min = (3.3 - 0.4) / 3e-3 = 967 ohm
  ```
- **Rise-time bound at 100 kHz** (UM10204 Rev. 7.0 Table 10 Standard-mode `tr` = 1000 ns):

| Total `Cb` | `Rp_max` at 100 kHz | Window vs Rp_min 967 ohm |
| ---: | ---: | --- |
| 150 pF | 7868 ohm | open |
| 200 pF | 5901 ohm | open — 2.2 k, 3.3 k, 4.7 k all fit |
| 250 pF | 4721 ohm | open — 2.2 k/3.3 k fit |
| 300 pF | 3934 ohm | open — 2.2 k/3.3 k fit |
| 400 pF | 2951 ohm | open — 2.2 k/2.7 k fit; spec ceiling |

- **Leakage bound:** participant input leakages transcribed above total about 16 uA (ESP32 10 uA + MMC 10 uA are the dominant terms; both are conservative maxima). Idle drop at the preferred resistance: 2.2 k x 16 uA = 35 mV — negligible against the ~2.31 V VIH (0.7 x VDD) class requirement. Non-binding by more than an order of magnitude (Rp_leak_max ~61 k).
- **Preferred pull-up: 2.2 k ohm +/- 1%, 1/16 W or larger, one pair on `3V3_MAIN` at the ESP32 connector side of the bus.** It holds `tr <= 1000 ns` up to the full 400 pF specification ceiling (2.2 k valid to Cb = 538 pF), survives any single-device hot-attach without violating `Rp_min`, and dissipates 5 mW worst case per line. A 4.7 k pair would also clear the 400 pF ceiling but is kept as the alternate, not the default, because cable/certificate margin favors the stiffer bus.
- **On-board capacitance estimate (unrouted, for the cable limit):** transcribed pin capacitances (ESP32 2 pF/pin, TCA9535 8+9.5 pF, ICM 10 pF/pin, six devices at the 10 pF I2C-spec allowance where the datasheet is silent) sum to about 82 pF; allowing 30-60 pF for unrouted traces gives an on-board window of roughly **110-140 pF**. Post-placement this must be recomputed from real lengths (O28/gate 8 inputs), but the residual to the 400 pF ceiling is >= 260 pF.
- **Expansion-cable limit (now closed at the analysis level):** reserve at most **150 pF** for the external expansion cable plus its connector pair (0.5-0.8 pF/cm unshielded ribbon class, 10 pF connector pair), which keeps the worst case at about 290 pF — below the 400 pF specification ceiling with margin even if post-placement traces land at the high end. The [expansion interface](EXPANSION_INTERFACE.md) 30 cm guidance stays within this; **harnesses longer than about 20-25 cm of unshielded ribbon must be measured or re-evaluated before use.** This is the declared cable rule O11 requires; the measured validation remains post-PCBA per the gate 9 boundary.

**Conclusion (supersedes the 2026-09-17 400 kHz analysis, which is retained below for the record):** at the accepted 100 kHz the shared bus has a **non-empty admissible window for every Cb from the on-board estimate to the 400 pF specification ceiling** with standard E24 values (2.2 k ohm preferred). The pull-up item of O11 is closed at the engineering-analysis level; what remains for gate 9 is the block-by-block off-state review (touch, BQ25887, switched domains), the post-placement `Cb` recount and the post-PCBA rise-time/VOL measurement already declared in the closure criteria.

### Historical record: 2026-09-17 evaluation at the 400 kHz target (superseded by D22)

`Rp_min` was set by the **weakest sink**, which the transcriptions above showed was the TUSB320LAI at 1.6 mA / 0.4 V:

```
Rp_min = (3.3 - 0.4) / 1.6e-3 = 1812 ohm      (TUSB320LAI, SLLSEQ8D)
```

Cross-check against the other sinks: ICM-42688-P 967 ohm; TCA9535 SDA 967 ohm-class (3.5 mA/0.4 V = 829 ohm); ESP32-S3 GPIO open-drain 106 ohm class; MMC5983MA VOL 0.6 V with unstated sink -> treated as TUSB-class or weaker (conservative; its I2C table quotes VOL 0.6 V max, which at any sink still clears 0.4 V if the bus keeps Rp near this window's low edge).

`Rp_max` from rise time at the 400 kHz target:

| Total `Cb` | `Rp_max` @ 400 kHz | Window vs Rp_min 1812 Ω |
| ---: | ---: | --- |
| 100 pF | 3541 Ω | open — 1.8/2.2 k fit |
| 150 pF | 2360 Ω | open — 2.2 k fits |
| 180 pF | 1967 Ω | closing — no common E24 fit, 1.9-1.96 k E96 only |
| 197 pF | 1812 Ω | **hard ceiling at 400 kHz with the TUSB320LAI sink** |
| 200 pF | 1770 Ω | **empty** — no valid resistance at 400 kHz |
| 400 pF | 885 Ω | empty |

**Historical 400 kHz conclusion (this is the analysis that motivated D22; D22 has since been accepted and the Result 3 update above supersedes it):** at 400 kHz the bus capacitance budget was bound by **two** constraints: the rise-time window (Rp_min 1812 Ω caps Cb at ~197 pF) and — tighter — the **TUSB320LAI's own device limit of CBUS = 100 pF at 400 kHz** (SLLSEQ8D §6.6). The effective 400 kHz ceiling was therefore **100 pF total**. Three options were offered to the owner: (a) run the shared bus at 100 kHz (or drop to 100 kHz whenever the expansion cable is attached); (b) move TUSB320LAI off the shared I2C — it is USB-C control with a GPIO mode per SLLSEQ8D §7.2.4, its CC-line function does not need the bus during flight, and removing it also clears the 0x46/0x47 address constraint; (c) accept 400 kHz on-board only with a measured, enforced <=100 pF limit (unrealistic with the touch controller and expander attached). **The owner accepted (a) and (b) together as decision D22 on 2026-09-21** (see DECISIONS.md), and the Result 3 update of 2026-09-22 applies that decision in this worksheet.

## Pull-up rail ownership — proposal, not a decision

The pull-ups must sit on a rail that is present whenever any bus participant is powered, and must not back-feed an unpowered device. Two constraints already recorded in the electrical matrix bear directly on this:

- "External pullups must not feed an off device" (boot/reset/off-state audit).
- TUSB320LAI per `SLLSEQ8D` note 2: with a 3.3 V I2C bus the device `VDD` must stay at or above 3.0 V or the bus back-powers the device. The recorded disposition is to power TUSB320LAI `VDD` from `3V3_MAIN`.

**Proposal:** source the shared-bus pull-ups from `3V3_MAIN`, which is the same always-on rail the TUSB320LAI disposition already requires, and keep every bus participant either on `3V3_MAIN` or behind a device whose off-state is proven not to be fed through its I2C pins. This is consistent with the existing dispositions but is **not** an accepted decision and does not appear in [decisions](DECISIONS.md). It requires block-by-block off-state review, which the matrix already lists as open.

The touch controller and the power devices are the specific unresolved cases: the matrix records "resolve touch/power-device off-state behavior" as part of this same item.

## Evidence access blocker — RESOLVED 2026-09-17

The session that opened this worksheet could not reach the manufacturer hosts, so it correctly left the columns TBD rather than invent figures. The blocker was lifted the same day: a session with outbound access retrieved the exact datasheets (Espressif v1.8, TI SCPS201F, MEMSIC Rev A, Sensirion v7.3, Bosch DS004-13, TI SLLSEQ8D, TDK DS-000347 v1.9, TI SLUSD89B), and the inventory table above was transcribed from those documents with revision/section provenance. Figures marked "not stated" are genuine absences from the manufacturer text, verified by two independent extractions; they are not outstanding work unless the closure criteria below require a value the datasheet does not publish.

## Closure criteria for this item

This worksheet closes, and the O11 / gate 9 pull-up item with it, when all of the following hold:

1. The `UM10204` revision and section backing `tr`, `Cb` and the rise-time relation are recorded above.
2. Every `Ci`, `IOL`/`VOL` and `Ii` cell in the device inventory is resolved — either a transcribed figure with datasheet revision, section and review date, or an explicit **"not stated"** backed by a named review of that exact document. Six devices currently read "not stated" for `Ci`; that is a verified property of those datasheets, not outstanding transcription work, so this criterion is met for them and the burden moves to item 3.
3. `Cb` is totalled from the transcribed figures plus a routed-length trace estimate and an accepted expansion-cable limit, **with a declared substitute for every "not stated" device** — the I2C-specification per-pin allowance, a manufacturer application figure, or measurement. The substitute and its basis are recorded here; an unmeasured device is never assumed to contribute zero.
4. `Rp_min` and both `Rp_max` bounds are evaluated from the real figures, the admissible window is shown to be non-empty, and a preferred value with tolerance and power rating is proposed.
5. The pull-up rail and every participant's off-state behavior are accepted, including touch and the power devices.
6. The result is confirmed by measured rise time and `VOL` on a prototype, per the gate 9 board tests.

Items 1-4 are analysis. Item 5 requires the circuit review already tracked by O11. Item 6 is a prototype gate and cannot close before hardware exists.
