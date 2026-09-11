# Power architecture options

**Status: OPEN. No battery topology, charger, protection circuit or fuel gauge is selected.** These are engineering candidates for review, not wiring instructions. Target: one removable 21700 in a compact enclosure or two in a larger enclosure, USB-C charging and operation while charging.

## Candidate architectures

| Option | Energy/charge paths | Advantages | Issues and disposition |
| --- | --- | --- | --- |
| A: one managed 1S bay | Cell protection and reverse-insertion stage; 1S charger with separate system power path; regulated system supply | Lowest part count and easiest fault characterization; fits one-cell concept | Runtime may miss 12 h in FLIGHT; second loose spare gives no continuous dual-cell operation. Evaluation reference only, not frozen |
| B: two independently managed 1S bays | Each bay has protection, temperature monitoring, controlled charger and protected discharge path; reverse-blocked outputs feed a power mux/OR stage | Either bay can operate alone; mismatched state of charge need not equalize between cells | Highest duplicated circuitry; current/thermal limits must coordinate both chargers; dual gauge addressing; validate every backfeed path. Preferred dual-bay study candidate |
| C: two bays with mutually exclusive selection | Hardware interlocked break-before-make battery selection; charger connects only to selected bay; system hold-up or USB covers transition | Potentially one charger; avoids simultaneous direct cell connection | Charge sequencing and removal can reset system; charger/sense/NTC switching complicates fault safety. Reject any firmware-only interlock |
| D: managed 2S removable pack | Series cells with per-cell monitoring, balancing, 2S charger and buck regulation | Lower system current for equal power | Missing cell breaks pack; mismatched loose cells problematic; one-cell mode needs separate engineered path. Not a drop-in answer to 1-or-2 loose cells |
| E: fixed matched 1S2P pack | Factory-assembled matched pack, protection and pack connector | Simpler charging than independent bays | Changes the independently removable-cell concept; only a future replacement proposal, not baseline |

**Excluded: directly paralleling two user-removable cells, even if each is sold as protected.** An ideal diode at the combined output cannot stop cell-to-cell equalization upstream. A discharge OR stage also cannot provide a safe charge path through a reverse-blocked cell output. Option B therefore requires separately managed charging to each cell and a full parasitic/body-diode/backfeed review, including USB present and controller unpowered states.

An ideal-diode OR generally lets the higher-voltage source carry the load; it does not guarantee equal sharing. A power mux chooses a source rather than combining capacity into a physically parallel pack. Runtime and SOC calculations must reflect the chosen policy.

## Manufacturer-backed candidates (not BOM selections)

| Function | Candidate / source | Relevance and limitation |
| --- | --- | --- |
| Simple 1S linear charging | [TI BQ24074](https://www.ti.com/product/BQ24074), BQ2407x datasheet and evaluation circuit | Separate system power path; simpler switching-noise environment; enclosure dissipation may limit charge current |
| 1S switching charging | [TI BQ25895](https://www.ti.com/product/BQ25895), datasheet | Power-path charger candidate; switching layout/EMI and configuration burden; neither dual-cell balancing nor USB-C PD controller |
| Cell fault protection | [TI BQ2970 family](https://www.ti.com/product/BQ2970), datasheet | Per-cell over/undervoltage and current fault detection with external FETs; exact thresholds and reverse insertion path still require selection |
| Source selection | [TI TPS2121](https://www.ti.com/product/TPS2121), datasheet | Power mux candidate; assess input range, voltage drop, quiescent current and switching behavior; does not replace charger or cell protection |
| Low-loss source OR | [ADI LTC4412 datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/ltc4412.pdf) | External FET ideal diode; battery reversal rating and external-device limits must be checked for the exact arrangement |
| 1S state of charge | [ADI MAX17048](https://www.analog.com/en/products/max17048.html), datasheet | Voltage-model gauge candidate; needs cell/profile characterization and insertion handling; per-bay measurement for independent cells |

The [BQ25895 datasheet](https://www.ti.com/lit/ds/symlink/bq25895.pdf) and [TPS2121 datasheet](https://www.ti.com/lit/ds/symlink/tps2121.pdf) are starting electrical references. No exact current limits, MOSFETs, resistors or charger termination settings are assigned here. Costs, assembled area and supplier availability are TBD; these options cannot yet support a purchasing decision.

## USB-C and operation while charging

Provide sink-side CC detection/termination appropriate to the chosen Type-C architecture, input ESD/overvoltage/inrush protection, and a current limit that respects the source's advertised/negotiated capability. Do not assume every USB source supplies 3 A, or that a charger IC negotiates PD. Native USB data routing and charging must coexist; PD is optional unless selected power demands require it. See [TI Type-C controller TUSB320](https://www.ti.com/product/TUSB320) as a research reference, not a selected part.

Budget USB input for simultaneous system load and charging. Reduce or suspend charge current when needed; prioritize a stable system rail. Check termination accuracy with system load, absent/deeply discharged battery startup, USB insertion/removal, both connector orientations, suspend/current policy and VBUS backfeed.

## Required review before topology freeze

| Hazard / state | Required evidence |
| --- | --- |
| Reverse insertion, damaged wrapper, shorted bay | Mechanical keying/contact insulation, electrically safe polarity handling, independent overcurrent response |
| Two different SOC/capacity/age cells | No uncontrolled equalization; per-bay isolation; worst-case current at insertion |
| Empty bay, one/both cells removed under load | Defined shutdown/continued-operation policy; no live accessible contacts or rail collapse outside limits |
| Charge too cold/hot, ambient solar heating | Cell-specific operating limits; per-cell temperature sense; charge inhibition and thermal measurement |
| USB present, charger disabled, MCU crashed | Safe default hardware state; leakage/backfeed map; no firmware-only safety dependency |
| Gauge and bus power interactions | Per-bay SOC/voltage; fixed-address collision solution; no I2C back-powering when bay is off |
| Cell depletion while writing SD | Low-battery warning and bounded shutdown; quantify hold-up, flush time and possible last-record loss |

Document exact cell model and dimensional limits, fault tree, schematic review, charger/FET thermal calculations, and controlled current-limited bench results. The owner and a qualified battery/electrical reviewer must explicitly accept the topology before design freeze. This review is for the later electrical design, not a blocker to this documentation commit.
