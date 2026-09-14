# Four-layer PCB stackup candidate

Status: pre-layout manufacturer study. Review date: 2026-09-11 UTC.

Use JLCPCB's published 1.6 mm four-layer `JLC2313` impedance-controlled stack as the pricing and field-solver baseline:

| Layer | Proposed use | Published nominal construction |
| --- | --- | --- |
| L1 | Components, RF and critical signals | 35 um outer copper |
| L1-L2 | RF reference dielectric | 0.10 mm 2313 prepreg, published Dk 4.05 |
| L2 | Unbroken ground plane | 17.5 um inner copper |
| L2-L3 | Core | 1.265 mm core including copper construction |
| L3 | Power islands plus slow signals with controlled returns | 17.5 um inner copper |
| L3-L4 | Dielectric | 0.10 mm 2313 prepreg |
| L4 | Low-speed signals/components; ground pours where continuous | 35 um outer copper |

Source: [JLCPCB controlled-impedance stackup table](https://jlcpcb.com/quote/pcbOrderFaq/PCB%20Stackup).

A first-order no-mask microstrip estimate places a 50 ohm L1-to-L2 trace near 0.18 mm width. Copper thickness, soldermask and the manufacturer's actual process shift that value, so **0.18 mm is not a routing rule yet**. At order time, obtain the current stack identifier and use JLCPCB's field solver/order impedance table for 50 ohm single-ended RF and 90 ohm USB differential geometry. Add coupons if the service permits and record the manufactured stack from the order data.

Rules before layout:

- no splits or voids in L2 under RF, USB, clocks or their return transitions;
- ground stitching at RF layer transitions and shield perimeters based on the final geometry;
- separate noisy switch-node copper from GNSS, ADS-B, MMC5983MA and pressure/humidity zones;
- every L4 high-speed segment needs an intentional reference/return path; move it to L1 if that cannot be shown;
- do not reuse matching values or trace widths from a different stackup;
- run a PDN/thermal review for the 2S boost charger, common protection/current path and all downstream buck rails before copper pours freeze.

The stack is accepted as a calculation candidate only. Fabrication cannot be released until the manufacturer confirms the exact stack and KiCad constraints are updated from that confirmation.
