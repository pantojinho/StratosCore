# USB eFuse and 2S charger evidence (O05/O06 desk preparation)

Status: desk evidence recorded 2026-09-17 from the exact manufacturer datasheets. This document feeds the O06 calculations and the mandatory O05 qualified battery review. **Nothing here closes O05.** Provenance: TI TPS25947 family data sheet **SLVSFC9C (October 2020, revised May 2026)** and TI BQ25887 data sheet **SLUSD89B (February 2019, revised November 2019)**, both retrieved and text-reviewed 2026-09-17.

**2026-09-22 (PWR-02): the USB input application is closed at the design level below** — exact resistor network proposed from the SLVSFC9C equations, default-current policy fixed to the reviewed CC output states, TUSB320LAI integration set to the D22 GPIO-mode wiring, and unsupported ESD claims corrected. The qualified battery review (O05) remains the gate for anything that touches charger enable/fault behavior.

## PWR-02 design closure: USB input application (2026-09-22)

### Current policy (fixed sink, no PD — implements D12/P17)

- **The device is a fixed-UFP 5 V sink.** No USB PD negotiation exists (no PD controller on the board; D12). The advertised/accepted current class comes only from the TUSB320LAI fixed-UFP detection: **default (500/900 mA class per Table 2 of SLLSEQ8D) in GPIO mode** — GPIO-mode devices advertise/accept default current only (SLLSEQ8D §7.2.1.1). 1.5 A and 3.0 A classes are never advertised and cannot be accepted in GPIO mode.
- **Charge input budget:** the charger input setpoint (BQ25887 IINDPM/ILIM) must be configured at or below the **default current class (500 mA conservative floor; 900 mA USB3-class sources only when OUT1/OUT2 report an attached source at that class — which GPIO mode cannot distinguish, so the firmware policy floor is 500 mA until PWR-03 proves a higher hardware-gated value)**. This figure is a PWR-03/O06 calculation input, not a charger setting selected here.
- **System load on VBUS (charge-under-load, D21):** the eFuse budget below protects the path; whether the 2 A circuit-breaker ceiling is appropriate with the system running is an O05/O06 qualified-review item (the 2 A threshold protects wiring and the connector; it does not authorize 2 A of charger draw).

### TPS259474L application network (exact values, from the SLVSFC9C equations recorded above)

| Element | Value | Derivation |
| --- | --- | --- |
| RILM (circuit-breaker threshold) | **1.69 kohm, 1%** -> IILM = 3334/1690 = **1.97 A typ** (~2.2 A worst at +10%) | §7.3.5.2 Eq. 5; sits below the 3 A Type-C source ceiling with margin; 2 A was the provisional figure, 1.97 A is the nearest E96 |
| UVLO divider | **R1 = 232 kohm / R2 = 100 kohm, 1%** -> VIN_UV = 1.20 x (232+100)/100 = **3.98 V rising** | §7.3.2 Eq. 1, VUVLO(R) 1.183-1.223 V; rides through a 5 V -5% source (4.75 V) with margin, drops out on a sagging/bad cable before the charger sees brown-out |
| OVLO divider | **R1 = 442 kohm / R2 = 100 kohm, 1%** -> VOVLO = 1.20 x (442+100)/100 = **6.50 V rising** | §7.3.3 Eq. 2; above the 5.5 V USB worst case, far below the 23 V operating max; internal OVLO response of the charger stage remains the secondary guard |
| dVdt | **Leave open (fastest slew)** for Rev A | §7.3.5.1 Eq. 3-4; the BQ25887 input stage and the 10 uF-class VBUS bulk (UFP connector capacitance 1-10 uF per the matrix) set the inrush; revisit only if attach testing shows source droop |
| ITIMER | **TBD at O06** — sized against the charger's worst inrush/input-capacitance charge transient, not invented here | §7.3.5.2 |
| EN/UVLO tie | EN tied to the UVLO divider node (single-divider enable+UVLO arrangement of the typical application) | §7.3.2 |
| Fault behavior | Latch-off (L suffix): a breaker trip stays off until VBUS or EN re-cycles | §4 device table; combined with the autonomous-start gating below this is an O05 reviewer item, unchanged |

### TUSB320LAI integration (points at the D22 wiring; CONNECTOR_ARCHITECTURE CC row superseded)

- CC1/CC2 through the TPD4E05U06 channels to the TUSB320LAI; **PORT = GND (fixed UFP), ADDR = NC (GPIO mode, I2C physically disabled), EN_N = GND, VDD = `3V3_MAIN`, VBUS_DET via the 900 kohm datasheet resistor, OUT1/OUT2/OUT3 via 100 kohm pulls to the TCA9535** — the complete disposition recorded in [the GPIO map](INTERFACE_GPIO_MAP.md) on 2026-09-22 supersedes any I2C-mode reading of the CC row.
- **Out-of-the-box behavior this produces:** the board enumerates/charges at default current from any compliant Type-C source, in both plug orientations, with no firmware dependency for the CC function; the expander reports attachment/current class for the UI and for future charger gating (PWR-03).
- **ESD claims corrected:** the +/-12 kV IEC 61000-4-2 contact figure in the TPD4E05U06 data sheet is a **device-level** qualification in TI's test fixture; it does not assert a system-level rating for this board (layout, connector, enclosure and ground path determine the realized level). No system-level ESD number may be quoted for Rev A until an attachment/surge test says so. The same correction applies to any reuse of that figure elsewhere.


## TPS259474L eFuse (USB VBUS input protection)

The `TPS259474L` variant (device comparison table, SLVSFC9C §4): adjustable OVLO + **circuit-breaker** overcurrent response + **latch-off** fault behavior (vs the `A` suffix auto-retry). Package VQFN-HR (RPW) 10-pin 2 x 2 mm; orderable `TPS259474LRPWR` (production, 3000/reel).

| Fact | Value | Source (SLVSFC9C) |
| --- | --- | --- |
| Input range | 2.7-23 V operating, 28 V abs max, -15 V reverse withstand | §1 Features, §6 Abs Max |
| RDS(on) | 28.3 mΩ typ back-to-back FETs, true reverse-current blocking | §1, §2 |
| Overcurrent threshold | ILM pin, RILM 549-6650 Ω for 0.5-6 A, ±10% accuracy (>1 A) | §6.5, §7.3.5.2 Eq. 5 |
| **RILM equation** | **RILM [Ω] = 3334 / IILM [A]** | §7.3.5.2 Eq. 5 |
| Fast-trip (short) | 2 x IILM scalable threshold | §7.3.5 |
| ITIMER blanking | capacitor on ITIMER; 1.8 µA pull-down discharge by ΔVITIMER; allows transients to 2x IILIM | §5-1 pin table, §7.3.5.2 |
| UVLO adjust | EN/UVLO divider: VIN_UV = VUVLO x (R1+R2)/R2, VUVLO(R) = 1.20 V typ (1.183-1.223) | §7.3.2 Eq. 1, §6.5 |
| OVLO adjust | OVLO divider, same equation form, VOV(R) = 1.20 V typ | §7.3.3 Eq. 2 |
| Inrush/slew | dVdt pin capacitor sets output slew; SR[ms] = IINRUSH[mA]/COUT[µF]; leave open for fastest | §7.3.5.1 Eq. 3-4 |
| Current monitor | IOUT = VILM / (RILM x GIMON), analog output on ILM pin | §7.3.6 Eq. 9 |
| Quiescent / off | IQ(ON) 428 µA typ / 610 µA max; IQ(OFF) 73 µA typ / 130 µA max | §6.5 |
| EN pull-up note | >5 V supplies or reverse-polarity exposure: EN pull-up >= 350 kΩ | §6 abs-max note 2 |

**Circuit proposals (for O06, not decisions):** for a USB-C 5 V VBUS with 3 A source capability: RILM = 3334/2.0 ≈ **1.67 kΩ** (2.0 A circuit-breaker threshold, below the 3 A Type-C limit with margin for tolerance ±10% → 2.2 A worst case); UVLO divider for ~4.0 V falling (brown-out ride-through of a 5 V ±5% source: VUV = 1.20 x (R1+R2)/R2); OVLO divider for ~6.5 V rising (above USB 5.5 V worst case, below VBUS OVP classes used downstream). Exact resistor pairs, ITIMER and dVdt capacitors to be computed in the O06 worksheet against the chosen input cap and COUT.

**Latch-off interaction (O05 input):** after a circuit-breaker fault the `L` variant stays off until input or EN is cycled. Combined with the BQ25887 default-mode behavior below, the fail-safe chain must ensure a latched eFuse does not silently re-enable charging on the next USB plug event without host validation — tied to the already-recorded USB/charger default-disable requirement.

## BQ25887 2S boost charger

**I2C-controlled 2-cell, 2-A boost-mode battery charger with cell balancing for USB input** (SLUSD89B title). VQFN-24 4 x 4 mm. Boost topology: charges a 2S pack (6.0-8.4 V) from a 5 V-class USB input.

| Fact | Value | Source (SLUSD89B) |
| --- | --- | --- |
| **Integrated cell balancing** | Internal FETs, up to **400 mA** balancing current; CBSET pin to midpoint through current-limit resistor; automatic balancing with default register settings | §1 Features; pin table (CBSET §5); CELL BALANCING §6.5 |
| MID pin protection | 300 Ω series resistor protects bottom-cell reverse plug | pin table (MID) |
| **CD pin (chip disable)** | Active-high; pull CD high → charge disabled, HIZ mode; I2C/ADC still alive; internal **900 kΩ pull-down** default | pin table (CD) |
| **Autonomous charging** | With EN_CHG=1 (register default after POR) and CD LOW, completes a full charge cycle with no host; default parameters per Table 2; starts in "default mode" after POR with watchdog expired, charging enabled, 12-h safety timer | §8.3.4.1, §8.3.4 (Table 2), watchdog §8.3.6 |
| Host mode | Any I2C write → host mode; watchdog must be reset (WD_RST) within 160 s or registers reset to defaults | §8.3.6 watchdog |
| Termination | VBAT above recharge threshold AND current below termination threshold; STAT high + INT pulse; taper continues if top-off enabled | §8.3.4.4 |
| Recharge | Auto new cycle below VCELL_RECHG (selectable bits) | §8.3.4 |
| Input current limit | ILIM pin hardware: **IINMAX = K_ILIM / R_ILIM**; register IINDPM (lower of the two governs); ILIM short-to-GND → max by ILIM pin | §8.3.7 Eq. 3 + pin table |
| VINDPM | Register range 3.9-5.5 V, 100 mV steps | §6.5 EC table |
| 16-bit ADC | Monitors VBUS, battery/cell voltages, currents, TS per mode of operation | §8.3.5 |
| TS / NTC | Thermistor divider from REGN; charge suspends out of window; recommends **103AT-2**; T1 0 °C / T2 10 °C thresholds (73.25%/68.25% of REGN typ) with hysteresis | pin table (TS), §6.5 TS table |
| VBUS protections | VVBUS_OV stops switching; poor-source VPOORSRC detection; auto restart | §8.3.8.1 |
| I2C address | 0x6B (matrix) | device comparison |
| I2C leakage | High-level input 1 µA (characterized at 1.8 V pull-up rail) | §6.5 IBIAS |

**Autonomous-start gating (the O05 core conflict, now with exact figures).** After POR the device sits in default mode with charging enabled, CD pulled LOW internally by 900 kΩ, and a 12-hour safety timer. USB insertion into a pack in any state can therefore start an autonomous charge before the ESP32 boots. The fail-safe options the reviewer must choose between (recorded for O05, none selected here): (a) hardware strap forcing CD high at POR (e.g. pull-up to VBUS through a divider that the host can override with an open-drain GPIO), (b) accept default-mode autonomous charging but pre-configure EN_CHG=0 permanently via a non-volatile scheme — **not supported on BQ25887 (registers are volatile)**, so (b) reduces to accepting the default-mode charge, or (c) series gating of the charger VBUS feed behind the eFuse latch/off-state policy above. Cell-balancing default settings and MID/CBSET resistor sizing (<=400 mA) belong to the same review.

**Reviewer package reminders (O05, unchanged):** low-side pack protector ground/cutoff interaction with the charger, single-cell-removal behavior, reversed-cell behavior through MID 300 Ω, charge-under-load termination, TS window with the chosen NTC, fault matrix (protector trip in flight, VBUS OVP, TSHUT), and the required closure evidence list per AGENTS.md rule 6.

## O06 calculation worksheet inputs

- eFuse RILM/UVLO/OVLO/dVdt/ITIMER: equations above with exact resistor proposals to be computed against the final USB input network.
- Charger: IINMAX resistor (K_ILIM from the EC table), ICHG/termination register targets vs the 2 A boost limit, VINDPM setting vs the eFuse UVLO, TS divider with the chosen 103AT-2 NTC, CBSET resistor for the balancing target.
- Charge-while-operating tradeoff: buck input is the protected 2S bus; charger output is the same bus — boost-charging under a 1.68 W FLIGHT load must show the charger stays within its 2 A input/boost limits with the buck load active, and that termination detection is not defeated by the load current. Decision is the owner's (O06).

Primary sources: [TPS25947 SLVSFC9C](https://www.ti.com/lit/ds/symlink/tps25947.pdf), [BQ25887 SLUSD89B](https://www.ti.com/lit/ds/symlink/bq25887.pdf).
