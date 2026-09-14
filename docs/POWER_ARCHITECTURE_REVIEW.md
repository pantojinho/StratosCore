# Power architecture engineering review

Status: **2S direction accepted by owner 2026-09-13; qualified electrical/battery review pending; circuit not frozen**.

## Accepted architecture direction

Use two removable, matched 21700 cells in series. Treat them as one service pair. One balanced 2S charger manages charging, while a separate common 2S protection path guards discharge and fault states. Downstream buck regulators power the system from the 2S pack.

```mermaid
flowchart LR
  USB[USB-C 5 V input and protection] --> CHG[Balanced 2S boost charger candidate]
  H[Documented 2S holder: B- / MID / B+] --> PROT[Common 2S protection and current cutoff]
  H --> CHG
  CHG --> H
  H --> SENSE[Per-cell voltage and NTC sensing]
  PROT --> PACK[Protected 2S bus, approximately 6.0-8.4 V]
  PACK --> BUCK[Reviewed buck rails]
  BUCK --> LOADS[Digital, sensors and switched RF domains]
```

This meets the owner's requirement for two removable cells and one charger/control solution. It does not permit direct parallel connection. Both cells are required for operation; removing either opens the series pack. Use cells of the same qualified model, capacity class, age and verified state, and replace them as a pair.

The [low-cost marketplace holder shown by the owner](https://pt.aliexpress.com/item/1005005491570611.html) is a mechanical sample candidate only. Its listing does not establish a manufacturer, ordering code, current rating, contact material, series wiring or midpoint terminal. Verify continuity with no cells installed, obtain dimensions, inspect polarity markings and contact retention, and reject any two-terminal parallel version. The PCB needs all three 2S nodes: pack negative, midpoint and pack positive.

## First charger candidate

TI `BQ25887RGER` is the first candidate for engineering review. TI data sheet SLUSD89B, revised November 2019 and reviewed 2026-09-13, documents a 2-cell boost-mode Li-ion charger for 3.9-6.2 V USB input, up to 2 A charge current, I2C control at the default seven-bit address `0x6B`, a 16-bit ADC, per-cell measurement, NTC input and automatic balancing up to 400 mA. It is a 24-pin 4 x 4 mm VQFN.

TI's device-comparison table explicitly marks the BQ25887 as **no power path**. The load therefore remains on the protected battery bus; USB does not create an independently regulated system rail and the design does not promise batteryless operation. This is compatible with the accepted requirement that both cells be installed, but charging while the system is operating, termination under load, cold-start with a deeply discharged pack and every USB transition require review and measurement. Do not assume the charger replaces common discharge protection.

### Charger topology comparison refreshed 2026-09-14

| Candidate | What it resolves | Added consequence | Current disposition |
| --- | --- | --- | --- |
| `BQ25887RGER` | 5 V USB boost charging, per-cell ADC and automatic 2S balancing in one 4 x 4 mm device | No integrated power path or batteryless operation; system load can affect charge behavior; separate protection and downstream bucks remain | **Preferred engineering candidate** for the owner's simpler two-cell direction, pending the complete review |
| `BQ25792RQMR` | 3.6-24 V buck-boost charging and an NVDC power path that can run the system from USB with depleted/removed cells | No per-cell balancing; needs separate cell monitor/balancer/protection; 5 A capability and 29-pin 4 x 4 mm implementation add unnecessary scope if batteryless operation is not required | Keep only as an alternative if batteryless USB operation becomes a requirement |

On 2026-09-14 DigiKey displayed 848 `BQ25792RQMR` in stock at EUR 5.18 quantity one with a 12-week standard lead time. The earlier BQ25887 snapshot remains below. Prices use different regional storefronts and are comparison evidence only.

### Common-protection candidates

The charger is not the pack protector. Two candidate families were reviewed without selecting an exact protection circuit:

| Candidate | Evidence | Blocking issue before selection |
| --- | --- | --- |
| TI `BQ77307RGRR` | Active 2S-7S protector; per-cell over/undervoltage, charge/discharge overcurrent, short-circuit, external-NTC limits, open-wire detection and low-side charge/discharge FET drivers; 20-pin 3.5 x 3.5 mm VQFN | Low-volume parts require host-loaded settings after reset/shutdown unless TI supplies a production OTP configuration. A reviewer must prove safe startup defaults, 2S unused-pin connections, FET/sense design and behavior when the host is unavailable |
| ABLIC `S-8252` family | Autonomous six-pin 2S overcharge, overdischarge, discharge/charge overcurrent and short-circuit protection with external FETs | The long ordering code fixes thresholds, delays, zero-volt charging and power-down behavior. Exact suffix cannot be selected before the cell and current/fault limits are accepted; it has no integrated temperature protection |

DigiKey displayed 2,296 `BQ77307RGRR` at USD 1.95 quantity one on 2026-09-14. ABLIC lists S-8252 as a family with multiple factory configurations; exact authorized stock remains TBD. The simpler S-8252 path currently better satisfies firmware-independent protection, but no suffix is proposed until the cell/reviewer limits are known.

Primary evidence: [BQ25887 Rev B](https://www.ti.com/lit/ds/symlink/bq25887.pdf), especially device comparison table 5 and sections 8.3/9/11; [BQ25792 Rev C](https://www.ti.com/lit/ds/symlink/bq25792.pdf), especially section 9.3.8; [BQ77307 production data](https://www.ti.com/lit/ds/symlink/bq77307.pdf), especially sections 7.3-7.5 and 8; and [ABLIC S-8252 revision 4.0](https://www.ablic.com/en/doc/datasheet/battery_protection/S8252_E.pdf). Distributor snapshots: [DigiKey BQ25792RQMR](https://www.digikey.com/en/products/detail/texas-instruments/BQ25792RQMR/13577777) and [DigiKey BQ77307RGRR](https://www.digikey.com/en/products/detail/texas-instruments/BQ77307RGRR/22119518).

## USB-C input policy candidate

`TUSB320LAIRWBR` is the first Type-C CC controller candidate for a fixed upstream-facing-port/sink implementation. TI data sheet SLLSEQ8D revision D, reviewed 2026-09-14, documents attach, cable orientation and default/1.5 A/3 A source-current detection without USB Power Delivery. In I2C mode, pulling `PORT` low fixes UFP operation and pulling `ADDR` low selects seven-bit address `0x47`; `VBUS_DET`, CC1/CC2, enable, decoupling, pullups and the 1-10 uF UFP VBUS capacitance require the exact TI application review. The 12-pin RWB X2QFN is 1.6 x 1.6 mm.

The hardware policy remains conservative if either MCU or the CC controller is unavailable: hold the BQ25887 `PSEL` high and cap input current at 500 mA until a valid attached-source current advertisement has been read. Firmware may raise `IINDPM` only to a reviewed value no greater than the detected advertisement, and must return to the conservative limit on detach, reset, invalid state or I2C failure. This controller manages CC only; USB D+/D- remain on the ESP32 native USB path through separately selected ESD protection. No USB PD or input above 5 V is proposed.

The candidate adds one I2C address, one interrupt/status path and a small package. It also creates an unpowered-state review: if the controller is supplied from VBUS while the shared 3.3 V I2C pullups remain active, the final design must prevent back-powering in either direction. Exact USB-C receptacle, ESD/inrush components, VBUS discharge and connector mechanics remain open. The part is a proposal, not a frozen schematic selection.

Primary evidence: [TI TUSB320LAI product page](https://www.ti.com/product/TUSB320LAI) and [revision-D data sheet](https://www.ti.com/lit/ds/symlink/tusb320lai.pdf), especially sections 7.2.1.2, 8.2.3 and the RWB package drawing. TI lists `TUSB320LAIRWBR` as active; distributor price and factory-assembly availability must be rechecked when the connector and PCBA supplier are selected.

## Cell candidate for review

The exact 21700 model is still open. `Molicel INR-21700-M50A` is the first sample candidate because its official manufacturer sheet matches the 5.0 Ah, 3.6 V planning basis already used in the runtime calculation. The reviewed sheet `INR21700M50A-V1-80097` specifies 5,000 mAh typical/4,800 mAh minimum, 4.2 V charge, 2.5 V discharge limit, 2.5 A standard charge, 0 to 45 °C charging, -30 to 45 °C discharging, 21.7 x 70.2 mm maximum and 68 g typical. It is an unprotected flat-top cell; board protection remains mandatory.

An authorized US specialty distributor displayed the M50A at USD 2.80 sale price and USD 7.99 regular price per cell on 2026-09-14. Brazilian availability, dangerous-goods shipping and authenticity controls remain open. Source: [Molicel M50A manufacturer sheet](https://www.molicel.com/wp-content/uploads/INR21700M50A-V1-80097.pdf) and [authorized-distributor listing](https://liionwholesalecorp.shop/products/molicel-npe-inr-21700-m50a-15a-5000mah-flat-top-21700-battery-authorized-distributor).

This candidate does not set the charge rate or protection thresholds. Mission temperature, runtime at cold soak, holder contact geometry and cell provenance must be accepted before the cell becomes locked.

### Cost and availability comparison checked 2026-09-13

| Architecture/candidate | Prototype parts | Snapshot | Disposition |
| --- | --- | --- | --- |
| Rejected independent 1S P08 | 2x BQ25185 + LTC4415 before gauges/protection | Earlier review: about USD 4.56 for two chargers plus USD 10.89 ORing at quantity one | Rejected by owner as excessive complexity |
| Accepted 2S direction, first charger candidate | 1x BQ25887RGER/RGET before common protection/regulators | Mouser listed 7,531 RGER at USD 5.01; DigiKey listed 235 RGET at USD 6.62; LCSC listed no stock | Candidate is cheaper and smaller than P08; recheck at purchase |

Historical BQ25887 supply sources: [TI BQ25887 product page](https://www.ti.com/product/BQ25887), [Mouser BQ25887 search](https://www.mouser.com/c/ds/?q=BQ25887RGER), [DigiKey BQ25887RGET](https://www.digikey.com/en/products/detail/texas-instruments/BQ25887RGET/10270194), and [LCSC BQ25887RGET](https://www.lcsc.com/product-detail/Battery-Management_Texas-Instruments-BQ25887RGET_C2862617.html).

## Electrical, firmware and mechanical impact

| Area | Accepted-direction impact |
| --- | --- |
| Electrical | Battery bus changes to a two-cell range; USB charging requires boost conversion; the system requires buck regulation plus common 2S over/undervoltage, overcurrent/short and thermal protection; Type-C source current starts at a 500 mA hardware cap |
| Firmware | Configure the charger conservatively, never exceed the CC-detected source-current class, log both cell voltages/temperature/current, detect imbalance or missing-cell states, and enter safe shutdown; firmware may not be the sole protection layer |
| PCB | Replace two 1S chargers and source-OR circuitry with one 2S charger candidate, CC controller, protection FETs/current path, midpoint sensing and reviewed switching layouts; preserve RF and magnetometer separation |
| Mechanical | Two cells and holder are mandatory; provide polarity markings, wrapper-safe insertion, retention, insulated contacts and a battery door; current stack study starts near 37 mm enclosure depth |

## Required fault review and prototype tests

| Fault/state | Required hardware behavior | Prototype acceptance test |
| --- | --- | --- |
| One or both cells inserted backwards | No damaging current, charging or hot exposed contact | Current-limited cell emulators, USB absent/present, every insertion order |
| One cell missing or loses contact | Charging disabled; system shuts down without corrupting storage | Open each cell/contact during off, boot, load and charge states |
| Cells badly mismatched in voltage/capacity | Charging inhibited outside accepted entry window; no cell exceeds limits | Programmable cell emulators at boundary and fault combinations |
| Cell overvoltage/undervoltage | Independent hardware cutoff at accepted thresholds | Slowly sweep each emulator while logging charger and protection response |
| Pack short/overcurrent | Common protection and fuse strategy interrupt current within accepted energy/time | Electronic load and current-limited source before real cells |
| Cold/hot cells | Charging disabled outside the selected cells' qualified temperature window | NTC decade box and thermal chamber/controlled fixtures |
| Cell removed during logging | Defined shutdown; no SD corruption or uncontrolled reconnect cycling | Scope rails and verify logs/filesystem after contact interruption |
| USB insertion/removal | No cell overcharge, reverse VBUS current or unsafe rail transient | Scope VBUS, pack, midpoint and every regulated rail |
| Both MCUs reset or unpowered | Conservative charge/protection defaults remain enforced in hardware | Hold control interfaces reset while sweeping all sources |

## Runtime result

Two 5 Ah, 3.6 V example cells contain the same 36 Wh nameplate energy whether considered as 2S 5 Ah or two independent 1S cells. Under the existing 80% usable-energy and 90% conversion assumptions, the FLIGHT estimate remains about **10.72 h**, not 12 h. The actual 2S-to-load conversion efficiency must be measured; at least 0.207 W raw average still needs to be removed under the current budget assumptions.

## Review disposition

The owner approved the 2S direction, not an exact circuit. Before schematic commitment or prototype energizing, a qualified electrical/battery reviewer must accept the exact cell, holder, charger application, common protection, FET/fuse/current limits, NTC placement, buck conversion, creepage/clearance, firmware-independent defaults and the complete fault-test matrix above.
