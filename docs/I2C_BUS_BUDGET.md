# Shared I2C bus capacitance and pull-up budget

Status: calculation worksheet opened 2026-09-17. This document closes the method, the bounds and the disqualifying results for the shared-bus pull-up item named in [open questions](OPEN_QUESTIONS.md) O11 and gate 9 of [project status](PROJECT_STATUS.md). It does **not** yet publish a final resistance: the per-device figures marked TBD below must be transcribed from the exact datasheets already indexed in [the datasheet index](../hardware/datasheets/README.md) before a value enters a schematic.

**No number in this document is a measurement, and no per-device figure has been invented.** Every quantity is either (a) arithmetic derived in-document from the stated inputs, (b) a figure already cited elsewhere in this repository with its source, or (c) an explicit TBD naming the document and section that must supply it.

## Bus definition

| Parameter | Value | Source |
| --- | --- | --- |
| Bus speed target | 400 kHz (I2C Fast-mode) | "The bus starts at 400 kHz" — [GPIO and interface map](INTERFACE_GPIO_MAP.md) |
| Bus logic level | 3.3 V | [Electrical compatibility matrix](ELECTRICAL_COMPATIBILITY_MATRIX.md) I2C address and voltage check |
| Maximum rise time `tr` at Fast-mode | 300 ns | I2C-bus specification Fast-mode limit — PENDING CITATION, see below |
| Maximum bus capacitance `Cb` at Fast-mode | 400 pF | I2C-bus specification limit — PENDING CITATION, see below |
| Pull-up source rail | `3V3_MAIN` proposed | Proposal only, see "Pull-up rail ownership" |

**PENDING CITATION:** the `tr` and `Cb` limits and the rise-time formula below are the standard I2C-bus specification values. The exact NXP `UM10204` revision, section and table must be recorded here before this worksheet is treated as closed. The current session could not reach any manufacturer or standards host (see "Evidence access blocker"), so the revision is deliberately not asserted.

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
| ESP32-S3-WROOM-1-N16R8 (master) | — | TBD | TBD | TBD | Espressif module datasheet v1.8 and the ESP32-S3 chip datasheet electrical tables |
| `TCA9535PWR` | 0x20 | TBD | TBD | TBD | TI TCA9535 Rev E |
| MMC5983MA | 0x30 | TBD | TBD | TBD | MEMSIC Rev A |
| SHT40-AD1B-R2 | 0x44 | TBD | TBD | TBD | Sensirion SHT4x v7.3 |
| BMP581 | 0x46 | TBD | TBD | TBD | Bosch BST-BMP581-DS004-13 Rev 1.13 |
| TUSB320LAI | 0x47 | TBD | TBD | TBD | TI TUSB320LAI Rev D |
| ICM-42688-P | 0x68 | TBD | TBD | TBD | TDK DS-000347 v1.9 |
| BQ25887 | 0x6B | TBD | TBD | TBD | TI `SLUSD89B`. `VIH` 1.3 V / `VIL` 0.4 V / 1 uA leakage at a characterized 1.8 V pull-up are already transcribed in the electrical matrix; the 3.3 V-rail figures and `Ci` still require the datasheet |
| ST1633I touch | `0x70` published | TBD | TBD | TBD | Orient specification revision J; address convention is itself unresolved (O01) |

Non-device contributions to `Cb`:

| Contribution | Status | Note |
| --- | --- | --- |
| PCB trace capacitance | TBD | Not calculable before placement and the confirmed four-layer stack (gate 8, O10). Depends on routed length and reference-plane spacing |
| Expansion connector and external cable | TBD — **dominant unknown** | [Expansion interface](EXPANSION_INTERFACE.md) states the cable limit is unchosen; the GPIO map already requires "a measured cable limit". An external cable can exceed every on-board contribution combined |
| Any series/ESD part placed on SDA/SCL | None currently proposed | If added, its shunt capacitance counts. For scale, the `TPD1E0B04DPYR` used on the GNSS feed is cited at 0.18 pF maximum |

## Pull-up rail ownership — proposal, not a decision

The pull-ups must sit on a rail that is present whenever any bus participant is powered, and must not back-feed an unpowered device. Two constraints already recorded in the electrical matrix bear directly on this:

- "External pullups must not feed an off device" (boot/reset/off-state audit).
- TUSB320LAI per `SLLSEQ8D` note 2: with a 3.3 V I2C bus the device `VDD` must stay at or above 3.0 V or the bus back-powers the device. The recorded disposition is to power TUSB320LAI `VDD` from `3V3_MAIN`.

**Proposal:** source the shared-bus pull-ups from `3V3_MAIN`, which is the same always-on rail the TUSB320LAI disposition already requires, and keep every bus participant either on `3V3_MAIN` or behind a device whose off-state is proven not to be fed through its I2C pins. This is consistent with the existing dispositions but is **not** an accepted decision and does not appear in [decisions](DECISIONS.md). It requires block-by-block off-state review, which the matrix already lists as open.

The touch controller and the power devices are the specific unresolved cases: the matrix records "resolve touch/power-device off-state behavior" as part of this same item.

## Evidence access blocker

The session that opened this worksheet could not reach `ti.com`, `sensirion.com`, `bosch-sensortec.com`, `invensense.tdk.com`, `memsic.com`, `documentation.espressif.com`, `microchip.com` or `semtech.com`. All were refused by the execution environment's network egress policy, not by the hosts. Transcribing the TBD columns therefore requires either a session with outbound access to those hosts or a manual download by the maintainer.

Per `AGENTS.md` rule 3 and rule 12, no pin capacitance, sink current or leakage figure has been supplied from memory, inference or a marketplace listing. The columns stay TBD.

## Closure criteria for this item

This worksheet closes, and the O11 / gate 9 pull-up item with it, when all of the following hold:

1. The `UM10204` revision and section backing `tr`, `Cb` and the rise-time relation are recorded above.
2. Every `Ci`, `IOL`/`VOL` and `Ii` cell in the device inventory carries a transcribed figure with datasheet revision, section and review date.
3. `Cb` is totalled from those figures plus a routed-length trace estimate and an accepted expansion-cable limit.
4. `Rp_min` and both `Rp_max` bounds are evaluated from the real figures, the admissible window is shown to be non-empty, and a preferred value with tolerance and power rating is proposed.
5. The pull-up rail and every participant's off-state behavior are accepted, including touch and the power devices.
6. The result is confirmed by measured rise time and `VOL` on a prototype, per the gate 9 board tests.

Items 1-4 are analysis. Item 5 requires the circuit review already tracked by O11. Item 6 is a prototype gate and cannot close before hardware exists.
