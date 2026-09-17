# Four-layer PCB stackup candidate

Status: pre-layout manufacturer study. Review date: 2026-09-17 UTC.

Use JLCPCB's published 1.6 mm four-layer **`JLC04161H-3313`** impedance-controlled stack as the pricing and field-solver baseline. JLCPCB's official impedance-calculator user guide states: "The 3313 prepreg replaces the previously available 2313. Their thickness and dielectric constant (εr) are the same." The earlier `JLC2313` identifier used in this document is therefore superseded; the former Dk 4.05 figure for 2313 is replaced by the official published 3313 value Dk 4.1 (resin content 57%, nominal 4.2 mil / 0.1067 mm; pressed 0.0994 mm in the current stackup table).

| Layer | Proposed use | Published nominal construction |
| --- | --- | --- |
| L1 | Components, RF and critical signals | 35 um outer copper (1 oz) |
| L1-L2 | RF reference dielectric | 3313 prepreg x1, pressed 0.0994 mm, published Dk 4.1 |
| L2 | Unbroken ground plane | 0.5 oz inner copper (15.2 um after process) |
| L2-L3 | Core | 1.265 mm core including copper construction (total build 1.3 mm class) |
| L3 | Power islands plus slow signals with controlled returns | 0.5 oz inner copper |
| L3-L4 | Dielectric | 3313 prepreg x1, pressed 0.0994 mm, published Dk 4.1 |
| L4 | Low-speed signals/components; ground pours where continuous | 35 um outer copper (1 oz) |

Sources (both accessed 2026-09-17): [JLCPCB controlled-impedance stackup page](https://jlcpcb.com/impedance) and [JLCPCB impedance-calculator user guide](https://jlcpcb.com/help/article/user-guide-to-the-jlcpcb-impedance-calculator). The guide's parameter table: prepreg Dk 7628 = 4.4, 3313 = 4.1, 1080 = 3.91, 2116 = 4.16; core Dk 4.6; soldermask 1.2 mil over substrate / 0.6 mil over trace, Dk 3.8; external copper 1.6 mil; trace top width = base width - 0.7 mil.

## Candidate impedance geometries (calculation candidates only — NOT routing rules)

First-order Hammerstad microstrip calculations with the official parameters above (er 4.1, h = 0.0994 mm pressed prepreg, t = 35 um copper, 0.6 mil soldermask Dk 3.8 over the trace), shown work:

| Target | Geometry candidate | Computed result |
| --- | --- | --- |
| 50 Ω single-ended microstrip, L1 over L2 | W ≈ 0.133 mm (5.3 mil) | Z0 = 50.0 Ω, εeff ≈ 3.24 (with mask) |
| 50 Ω, nominal 4.2 mil prepreg variant | W ≈ 0.147 mm (5.8 mil) | Z0 = 50.0 Ω |
| 90 Ω USB differential pair, L1 over L2 (Bahl coupling factor) | W ≈ 0.160 mm (6.3 mil), S ≈ 0.329 mm (13.0 mil) | Zdiff = 90.0 Ω |
| 90 Ω differential, nominal 4.2 mil prepreg variant | W ≈ 0.145 mm (5.7 mil), S ≈ 0.169 mm (6.7 mil) | Zdiff = 90.0 Ω |

Method note: Hammerstad-Z0 with finite-thickness correction, soldermask overlay treated as coverage-weighted εr (first-order). Sanity check: a 0.20 mm trace over 0.0994 mm with no mask computes ≈ 42 Ω, consistent with standard calculators. These widths are **candidates pending factory confirmation** — the differential solution is not unique (W/S trade off), and the final pair must come from JLCPCB's own calculator/solver against the order-time stack identifier. At order time obtain the current stack ID, run JLCPCB's field solver / order impedance table for 50 Ω single-ended RF and 90 Ω USB differential geometry, add coupons if the service permits, and record the manufactured stack from the order data.

Rules before layout:

- no splits or voids in L2 under RF, USB, clocks or their return transitions;
- ground stitching at RF layer transitions and shield perimeters based on the final geometry;
- separate noisy switch-node copper from GNSS, ADS-B, MMC5983MA and pressure/humidity zones;
- every L4 high-speed segment needs an intentional reference/return path; move it to L1 if that cannot be shown;
- do not reuse matching values or trace widths from a different stackup;
- run a PDN/thermal review for the 2S boost charger, common protection/current path and all downstream buck rails before copper pours freeze.

The stack is accepted as a calculation candidate only. Fabrication cannot be released until the manufacturer confirms the exact stack and KiCad constraints are updated from that confirmation.
