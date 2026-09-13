# Power architecture options

**Status: option D was accepted by the owner on 2026-09-13 as the engineering direction.** The exact circuit is not frozen and may not be energized until a qualified electrical/battery reviewer accepts the schematic, protection thresholds and fault-test limits. See the concrete [power architecture review](POWER_ARCHITECTURE_REVIEW.md).

## Compared options

| Option | Energy/charge paths | Advantages | Issues and disposition |
| --- | --- | --- | --- |
| A: one managed 1S bay | Cell protection and reverse-insertion stage; 1S charger with separate system power path | Lowest part count | Does not meet the owner's two-cell requirement; rejected for Rev A |
| B: two independently managed 1S bays | Each bay has protection, temperature monitoring and a charger; reverse-blocked outputs feed an OR stage | Either bay can operate alone; prevents cell equalization | Rejected by owner as excessive complexity on 2026-09-13; retained as comparison evidence |
| C: two bays with mutually exclusive selection | Hardware interlocked battery selection; charger connects only to the selected bay | Potentially one 1S charger | Selection, charging and removal fault behavior remain complicated; rejected for Rev A |
| **D: managed 2S removable pair** | Two series cells with midpoint sensing, balancing, one 2S charger, common 2S protection and buck regulation | Meets two-cell/removable-holder requirement with one charger; lower system current for equal power | **Owner accepted direction.** Both cells are required; qualified safety review and fault tests remain mandatory |
| E: fixed matched 1S2P pack | Factory-assembled matched parallel pack, protection and pack connector | Simple 1S charging | Conflicts with the owner's removable-cell holder requirement; rejected for Rev A |

## Accepted 2S constraints

- Use two cells of the same approved model, capacity class, age and verified state; service them as a pair.
- The holder must expose pack negative, series midpoint and pack positive with a documented 2S connection. A marketplace photo or title does not establish its wiring or rating.
- A single charger must measure both cells and actively balance them. TI `BQ25887` is the first candidate, not a frozen selection.
- A common 2S discharge-protection path must cover pack overvoltage, per-cell undervoltage, overcurrent/short and temperature. The charger alone is not assumed to provide all discharge protection.
- Missing-cell, reversed-cell, mixed-state, hot insertion/removal and USB transitions require hardware-safe behavior. Firmware is monitoring and policy, not the only safety layer.
- The system must regulate from the approximately 6.0-8.4 V 2S pack range. Exact buck rails, charging-while-operating behavior and shutdown thresholds remain open.

## Candidate references

| Function | Candidate / source | Relevance and limitation |
| --- | --- | --- |
| Balanced 2S USB-input charger | [TI BQ25887](https://www.ti.com/product/BQ25887), Rev B data sheet | 2S boost charger, I2C, per-cell ADC and integrated balancing; no claim here that it provides the complete system power path or discharge protection |
| Previous independent 1S charger | [TI BQ25185](https://www.ti.com/product/BQ25185) | Historical P08 comparison only; no longer the Rev A direction |
| Previous source OR | [ADI LTC4415](https://www.analog.com/en/products/ltc4415.html) | Historical P08 comparison only; removed by the accepted 2S direction |

No exact 2S protection IC/FETs, fuse, holder, thermistor, fuel gauge, buck regulator or USB-C input controller is assigned here. Those parts and values require the selected cells, exact holder evidence, power-path choice and accepted fault-test limits.
