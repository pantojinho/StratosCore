# Assembler mask strategy and five-unit cost snapshot (evidence package)

**Astra review annotation, 2026-09-24:** [independent review](../../../../docs/ASTRA_AGENT_REVIEW_2026_09_24.md) reproduced the price arithmetic, not current prices/stock. The "absolute lower bound" and infeasibility wording below apply only to the listed channel-price scenarios, not every available supplier. PCB/assembly tariffs here are service charges, not import taxes. Mask and stencil acceptance remain open; later proxy decisions do not prove factory feasibility.

Status: **research evidence for human decisions only.** The assembler (JLCPCB or another house) and the project owner decide. This note does not change any footprint, KiCad file, root document, BOM or locked decision, and it authorizes no order.
Retrieval date for every web figure below: **2026-09-23** (web retrieval about 22:20 UTC unless stated). Prices, stock and fees change. Treat anything older than 30 days as context only (`bom/SOURCING_EVIDENCE.md` rule 2).
Scope: the Claude one-shot candidate (`candidates/claude-oneshot-revA`), 4 layers, 60 x 84 mm, 1.6 mm, candidate stack `JLC04161H-3313` (`docs/PCB_STACKUP.md`).

---

## A. LGA solder-mask strategy for U30 ICM-42688-P and U32 BMP581

### A.1 Manufacturer requirements (primary sources, re-read 2026-09-23)

| Part | Source | Requirement (paraphrased; section cited) |
| --- | --- | --- |
| ICM-42688-P | TDK AN-000393 **Revision 2.4, dated 2/9/2026**, [PDF](https://d17t6iyxenbwp1.cloudfront.net/s3fs-public/2026-06/AN-000393%20TDK%20InvenSense%20IMU%20PCB%20Design%20and%20MEMS%20Assembly%20Guidelines%20v2.4.pdf?VersionId=0JJT_E0010fzx6pG58sIeAXICnPVAVgn) | §2.2: solder mask under the MEMS part is not recommended. If the board process cannot avoid it, mask under the part "will still work". Figure 1 gives the LGA land pattern. The repo transcription of Figure 1 (`FOOTPRINT_REVIEWS_SENSORS_GNSS.md`) is: land = terminal size, and the fallback per-pad mask adds 0.1 mm to each land dimension. §2.3: stencil opening-to-land ratio 90 %, stencil at least 100 µm, aspect ratio ≥ 1.5, area ratio ≥ 0.66. §3 (Figure 7): no traces, vias or copper pour directly under the IMU, and no via inside a pad outline. |
| BMP581 | Bosch **BST-BMP581-DS004-13, document revision 1.13**, [PDF](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp581-ds004.pdf), §8.2 "Landing pattern" (p. 69) and Figure 32 | Land = footprint + 25 µm on each side. At least 200 µm between pads. No vias or traces under the BMP581. No solder mask under the sensor. Recommended horizontal mask clearance 20 µm on each side. §8.2 warns that mask or other material touching the sensor can degrade performance. |

Candidate geometry, read-only from `kicad/libs/SC.pretty`:
- **U30:** lands 0.475 x 0.25 mm at 0.5 mm pitch. The copper gap is 0.25 mm between row neighbours and 0.30 mm at the corners. Paste pads are 0.4506 x 0.2372 mm (90 % area). A 3.0 x 2.5 mm body-sized F.Mask opening is used, plus a pad margin of 0.05.
- **U32:** lands 0.325 x 0.30 mm at ±0.7625 mm. The copper gap is 0.20 mm. Paste is 1:1. A 2.2 x 2.2 mm body-sized F.Mask opening is used.

The candidate DRC currently reports **199+ `solder_mask_bridge`** items (`docs/REFINEMENT_2026_09_23.md` D1). Tracks for 3V3_MAIN, I2C and IMU_INT1, GND/I2C vias and GND pour lie inside those common openings. **This violates the no-trace/no-via rule of both manufacturers, independent of the mask choice.**

### A.2 JLCPCB published capabilities (retrieved 2026-09-23)

| Item | Published value / statement | Source |
| --- | --- | --- |
| Solder-mask expansion | "1:1". LDI equipment upgraded June 2025, so pad size and mask opening can be 1:1. Keep ≥ 0.09 mm between mask openings and neighbouring traces | [PCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities) (no page date shown) |
| Solder-mask bridge (dam) | 0.10 mm. With 1 oz copper, minimum pad spacing is 0.10 mm for green, red, yellow, blue and purple mask and 0.13 mm for black and white. With 2 oz it is 0.20 mm | same page |
| Mask ink | LPI. Dielectric constant 3.8, thickness ≥ 10 µm | same page |
| Pad-to-track clearance | 0.1 mm (0.09 mm locally for BGA pads). SMD pad-to-pad on different nets: 0.15 mm | same page |
| Plugged vias (mask-filled) | Must have no mask opening on either side and **≥ 0.35 mm clearance from other mask openings (e.g. pads)**. Diameter ≤ 0.5 mm | same page |
| Via covering options | Tented, Untented, Plugged, Epoxy-filled & capped, Copper-filled & capped. A tented via is covered with soldermask and gets no surface finish | [Via covering article](https://jlcpcb.com/help/article/pcb-via-covering) (last updated 2026-09-09). The instant quote defaulted a 4-layer board to **Plugged** (observed 2026-09-23) |
| SMD/SMSD mask handling | Without a remark, JLCPCB enlarges the mask clearance of SMD pads to NSMD style. To keep mask as drawn, add a PCB remark naming the parts and select "Confirm Production File" to inspect the processed Gerber | [How to order boards with solder-mask-defined pads](https://jlcpcb.com/help/article/how-to-order-boards-with-solder-mask-defined-pads) (last updated 2025-04-24) |
| PCBA stencil | Generated by JLCPCB SMT engineers from the pad layout, packages and industry guidelines. It is not shipped | [PCBA price guide](https://jlcpcb.com/help/article/pcb-assembly-price) (last updated 2026-09-09) |
| Stencil thickness (standalone stencil product) | Standard thicknesses at no extra cost: 0.10, 0.12, 0.15, 0.18 and 0.20 mm. Special thicknesses from 0.03 to 0.50 mm cost extra. Minimum aperture > 0.08 mm. Step stencil only with framework. By default, apertures for IC packages are adjusted to JLCPCB's "Opening Process Standard". A remark makes them follow the paste layer 1:1 | [Stencil capabilities](https://jlcpcb.com/capabilities/pcb-stencil-manufacturing) |
| PCBA service limits | **Economic:** single-sided placement, 0402 minimum, 0.4 mm minimum IC pitch, "standard stack-up only", reflow 255 ± 5 °C (not adjustable), X-ray only for certain parts. **Standard:** single or double-sided placement, **single-PCB size 70 x 70 mm minimum** (panel 70 x 70 to 250 x 250 mm), 0.35 mm pitch, reflow 240 ± 5 °C. LGA/QFN/BGA get X-ray automatically | [PCBA capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities) |
| Common no-mask opening under an LGA | **No published statement found** accepting or refusing a multi-pad mask window under a component. **TBD, ask the assembler.** | searched jlcpcb.com help and capabilities pages, 2026-09-23 |

### A.3 Compatibility check (arithmetic from the numbers above)

| Strategy | U30 ICM-42688-P | U32 BMP581 | Versus JLCPCB published limits |
| --- | --- | --- | --- |
| **S1: per-pad NSMD openings.** TDK fallback: +0.1 mm per land dimension (+0.05 mm per side). Bosch: 20 µm per side | Openings 0.575 x 0.35 mm. Dam 0.15 mm between row neighbours and 0.20 mm at the corners | Openings 0.365 x 0.34 mm. Dam 0.16 mm | Every dam is ≥ 0.10 mm (green/1 oz), and ≥ 0.13 mm for black or white mask. **Within the published capability.** Mask then lies under the body between lands. TDK accepts this. For Bosch it departs from the "no mask under the sensor" text, so it needs an owner/assembler decision. |
| **S1b: 1:1 openings (LDI)** | Dam 0.25 / 0.30 mm | Dam 0.20 mm | Within capability. It conflicts with TDK's +0.1 mm fallback and Bosch's 20 µm clearance, so it is not recommended. |
| **S2: common body-sized opening** (current candidate) | Allowed by TDK where the process permits | Matches Bosch "no mask under sensor" | JLCPCB has published no acceptance, so this is **undetermined**. It is only viable with **zero other-net copper, tracks, vias or pour inside the window**, and each window edge must be ≥ 0.09 mm from neighbouring traces. Any via within 0.35 mm of the window cannot be mask-plugged (tented or epoxy-filled instead). The window also defeats JLCPCB's default NSMD enlargement logic, so a remark and "Confirm Production File" are needed. |

Stencil check (AN-000393 area/aspect rules, computed from the candidate paste pads):
- **U30** (0.4506 x 0.2372 mm): at t = 0.10 mm the area ratio is 0.777 and the aspect ratio 2.37, which passes. At 0.12 mm the area ratio is 0.648 (**fails** ≥ 0.66). At 0.15 mm it is 0.518 (fails).
- **U32** (0.325 x 0.30 mm): at 0.10 mm the area ratio is 0.78, which passes. At 0.12 mm it is 0.65 (fails narrowly). At 0.15 mm it is 0.52 (fails).
- **Both LGAs therefore need 0.10 mm (or a step-down) at these apertures.** JLCPCB chooses the PCBA stencil thickness and does not publish it per order: **TBD, ask**.

### A.4 Recommendation (for owner/assembler decision)

1. **Primary candidate: S1 per-pad NSMD openings.**
   - U30: TDK fallback +0.1 mm.
   - U32: Bosch 20 µm per side.
   - Both give dams ≥ 0.15 mm, above JLCPCB's published 0.10 mm minimum. This is the only strategy whose feasibility rests on published JLCPCB numbers.
2. **S2 (common opening) needs written assembler acceptance before use.** Even then it requires escape routing that clears the whole body window: no tracks, vias or pour inside it, and vias ≥ 0.35 mm away if plugged. The candidate violates the no-trace/no-via requirement of both manufacturers today in any case (D1). That rework is needed under S1 too.
3. **Whichever mask option is chosen:**
   - Ask for a 0.10 mm stencil (or a step-down) at the LGAs.
   - Keep the paste layer 1:1 as drawn (remark).
   - Choose "Confirm Production File" to verify the processed mask and paste.
   - Prefer ENIG over HASL for the 0.25 mm lands. This is a process preference to confirm with the assembler, not a datasheet requirement.
4. **Service-tier constraint found:**
   - The candidate has SMD part J2 (and holder BT1) on the bottom. Economic PCBA is single-sided only.
   - The 60 mm board side is below Standard PCBA's 70 x 70 mm single-board minimum. Standard PCBA would need a panel or a design change.
   - The owner decides: move J2 to the top, hand-fit it, or panelize.

### A.5 Questions to send to the assembler (copy-ready)

1. Do you accept a **single solder-mask opening covering the whole body** of an LGA (ICM-42688-P 3.0 x 2.5 mm; BMP581 2.2 x 2.2 mm) with no mask between lands? Or will CAM restore per-pad dams? If you accept it, what minimum clearance do you require from the window edge to other-net copper and to vias?
2. If we use **per-pad NSMD openings** (ICM: land +0.05 mm per side; BMP581: land +0.02 mm per side, giving 0.15–0.16 mm dams), will you keep the openings exactly as drawn? Or does your CAM change them (1:1 LDI, NSMD enlargement)? What remark do you need?
3. Which **via covering** do you apply by default on 4-layer PCBA orders? Is a tented or epoxy-filled via acceptable 0.1–0.35 mm from an LGA mask opening?
4. What **stencil thickness** will your SMT engineers use for this board? Can you use 0.10 mm, or a local step-down at U30/U32? Will you keep our paste apertures (ICM 90 % area, 0.4506 x 0.2372 mm; BMP581 1:1, 0.325 x 0.30 mm) or apply your Opening Process Standard?
5. Is the **JLC04161H-3313** stack (with ±10 % impedance control) accepted under **Economic PCBA** ("standard stack-up only")? Or does it force Standard PCBA?
6. Board is 60 x 84 mm with one SMD connector (J2) and a battery holder (BT1) on the bottom. Which service applies: Economic with J2 hand-soldered, or Standard with a panel? What is the minimum panel you would accept?
7. For ICM-42688-P, MMC5983MA, BMP581, SHT40 and T5838 LGA/DFN parts: is Economic PCBA's fixed **255 ± 5 °C** reflow compatible with each part's J-STD-020 limit? (Owner checks each datasheet; assembler states the actual peak and time above liquidus.)
8. Do you recommend **ENIG** over lead-free HASL for 0.25 mm-wide LGA lands on this order?
9. Is X-ray automatically applied to all LGA/QFN/DFN/LFCSP parts here, and to the ESP32-S3-WROOM-1 bottom pad? What is the counted component quantity?

---

## B. Five-unit cost-feasibility snapshot (2026-09-23)

Target (D24): **≤ BRL 200 average per unit** for five units. The target includes the Chinese assembled PCB plus display/touch. It excludes local cells, the enclosure, freight and taxes.
Exchange rate: **BCB PTAX USD/BRL sell 5.1414 BRL per USD** (bid 5.1408), bulletin 2026-09-23 13:04 BRT. Source: [BCB Olinda PTAX API](https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarDia(dataCotacao=@dataCotacao)?@dataCotacao='09-23-2026'&$format=json). The target therefore equals **USD 38.90 per unit**.

### B.1 Bare PCB, JLCPCB instant quote (no Gerber uploaded; coupons, shipping and tax excluded)

Source: [cart.jlcpcb.com/quote](https://cart.jlcpcb.com/quote), observed 2026-09-23. Site currency is USD ("payments must be made in US dollars").

Base configuration: FR-4, 4 layers, 60 x 84 mm, qty 5, single PCB, 1.6 mm, green, 1 oz outer / 0.5 oz inner, flying-probe test.
- The candidate uses 0.2 mm drill / 0.40–0.45 mm vias (605 of 656), so the "0.2mm/(0.3/0.35mm)" via option is required. That option automatically adds FR-4 TG155 and 4-wire Kelvin test.

| Configuration observed | Line items (USD) | Total USD / 5 pcs |
| --- | --- | --- |
| HASL (leaded), plugged, no stack spec, 0.3 mm via default (not valid for this board) | "Special Offer" 8.00 | 8.00 |
| + 0.2 mm via option (required) | + TG155 3.43 + min-via 17.17 + 4-wire Kelvin 16.87 | 45.47 |
| + ENIG | + surface finish 17.20 | 62.67 |
| + stack `JLC04161H-3313` specified (stack table shown: 0.035 / 3313 0.0994 / 1.265 core / 3313 0.0994 / 0.035) | no change | 62.67 |
| + impedance control ±10 % | + 33.08, + Confirm Production File 1.05 | **96.80** |
| same, lead-free HASL instead of ENIG | surface finish 5.10 | **84.70** |

"Special Offer" is a promotional label. Whether it stays available for this order is **TBD**. Build time 3–4 days at USD 0.

### B.2 PCBA fees (JLCPCB published price guide, last updated 2026-09-09)

Source: [PCB Assembly price guide](https://jlcpcb.com/help/article/pcb-assembly-price). The PCBA quote itself requires Gerber/BOM/CPL upload, so the real quote is **TBD**. No manufacturing files exist and the candidate is not released.

| Fee | Economic | Standard | Basis used here |
| --- | --- | --- | --- |
| Setup | 8.18 | 25.56 single / 51.12 double | Economic |
| Stencil | 1.53 | 8.21 single / 16.42 double | Economic |
| Extended-part feeder loading | 3.07 per extended part | 1.53 per basic/extended part | ≥ 16 extended major lines (all B.3 ICs except W25Q C97521 "base", plus BLB01, TA2003A, ADL5513, display excluded). Full count **TBD** (passives not mapped): ≥ 49.12 |
| SMT joints | 0.0016/joint | same (≤ 50k) | 958 SMD pads/board from the candidate PCB x 5 = 4 790, so 7.66 |
| X-ray | 51–200 pcs: 0.49/pc | same | about 20 leadless parts per board: D2, U2, U23, U3, U4, U6, U7, U17, U20, U30–U33, U40, U50, U52, U54, MK1, FL1, FL2. x 5 = 100, so 49.00 (ESP32 module inclusion TBD) |
| Hand-soldering labor | 3.58/order + 0.0164/joint | same | J1 shell (4 THT) x 5, so 3.91. BT1 holder TBD |
| Fixtures, handling | n/a | fixtures 16.42 (1–29 pcs); handling ≥ 14.93 if applicable | not in Economic estimate |
| **Economic estimate** | | | **≥ USD 119.40 per order (≥ 23.88 per unit)**, derived from published tariffs. Not a quote |

### B.3 Major-IC and display prices (per-unit price at the break covering 5 boards)

JLCPCB column = JLCPCB parts-library assembly price. It was retrieved through the public library search endpoint that the parts page uses (`jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList`), with the part page at `https://jlcpcb.com/partdetail/<urlSuffix>`. LCSC column = [LCSC product page](https://www.lcsc.com/product-detail/C2040.html) pattern `https://www.lcsc.com/product-detail/<C#>.html`, values from LCSC's product-detail JSON with `currencySymbol "$"`. All USD.

| MPN (qty/board) | LCSC/JLC # | JLCPCB USD @1–9 (stock, library) | LCSC USD @1 (stock) | Other channel | Price used |
| --- | --- | --- | --- | --- | --- |
| ESP32-S3-WROOM-1-N16R8 (1) | C2913202 | 5.1407 (27 292, extended) | 5.1937 (6 615) | — | 5.1407 |
| RP2040 (1) | C2040 | 0.9891 (74 207, ext) | 0.9968 (68 558) | — | 0.9891 |
| SX1262IMLTRT (1) | C191341 | 3.1983 (2 454, ext) | 3.2219 (2 454) | — | 3.1983 |
| MAX-M10S-00B (1) | C4153167 | 10.7808 (775, ext) | 10.8604 (715) | — | 10.7808 |
| BQ25887RGER (1) | C2761614 | 5.0431 (779, ext) | 5.0804 (779) | — | 5.0431 |
| ICM-42688-P (1) | C1850418 | 19.45 (410, ext) | 19.6358 (**2**) | [DigiKey 11679713](https://www.digikey.com/en/products/detail/tdk-invensense/ICM-42688-P/11679713): 4.91 @1, **4.402 @5**, **stock 0**, 5 000 expected 2027-08-03 | 19.45 (in stock) / 4.402 (lower bound, not available) |
| MMC5983MA (1) | C404329 | 2.2629 (18 548, ext) | 2.2838 (18 548) | — | 2.2629 |
| BMP581 (1) | C5362283 | 2.7998 (1 876, ext) | 2.8286 (1 875) | — | 2.7998 |
| SHT40-AD1B-R2 (1) | C2909890 | 1.905 (22 013, ext) | LCSC detail returned no record | — | 1.905 |
| TPS62130ARGTR (1) | C337502 | 0.9241 (6 884, ext) | 0.9325 (6 884) | — | 0.9241 |
| TPS259474LRPWR (1) | C2864845 | 1.3438 (1 102, ext) | 1.3541 (1 102) | — | 1.3438 |
| TUSB320LAIRWBR (1) | C132554 | 1.3861 (3 812, ext) | 1.4004 (3 751) | — | 1.3861 |
| W25Q128JVSIQ (1) | C97521 | 2.5541 (45 948, **basic**) | 2.5782 (1 465) | alt C113767 ext 2.5086 | 2.5541 |
| TCA9535PWR (1) | C130204 | 1.3243 (14 671, ext) | 1.3365 (14 184) | — | 1.3243 |
| BLB01 (2) | C38893678 | 3.6961 (**0**) | no LCSC record | [DigiKey 17126531](https://www.digikey.com/en/products/detail/berex-corp/BLB01/17126531): **1.772 @10**, stock 3 389, CT | 2 x 1.772 = 3.544 (would need consignment/global sourcing, fee TBD) |
| TA2003A (2) | C5357397 (brand "TST") | placeholder, **stock 0** | no LCSC record | DigiKey: no result. Mouser: bot-protected, not retrieved | **TBD** |
| ADL5513ACPZ-R7 (1) | C579160 | 19.5297 (**0**) | 19.731 (**0**) | [DigiKey 2180444](https://www.digikey.com/en/products/detail/analog-devices-inc/ADL5513ACPZ-R7/2180444): 18.85 @1, **stock 0**, 1 500 expected 2026-12-30 | 18.85 (lower bound, not available) |
| Display AFY240320A1-2.8INTH-C1 (1, with CTP) | not in JLC/LCSC library | — | — | [DigiKey 22531939](https://www.digikey.com/en/products/detail/orient-display/AFY240320A1-2-8INTH-C1/22531939): **31.55 @1** (next break 10 @ 25.489), stock 46, 8-week lead. Orient direct price TBD | 31.55 |

Not researched (**TBD**, cost only adds):
- all passives;
- TPS7A2030/2018, TPS22918 x3, SN74AXC4T245, SN74LVC1G07, TPS61169, TXU0202, TPD4E05U06 x2, TPD1E0B04, PE4259, MCP6566, S-8252 (O05), Q1 (O05), Q2, D1, F1;
- Y1/Y2, L1–L3/L70, all RF passives (E449 values TBD), MK1 T5838;
- USB4105, J2 (plus housing), J3/J4 FPC, three U.FL connectors, DM3AT, 2 x SKSCLCE010;
- BT1 holder (MPN TBD), antennas, pigtails, microSD card;
- consignment/global-sourcing fees for zero-stock lines;
- the real PCBA quote.

### B.4 Arithmetic and verdict

| Line | USD / unit | BRL / unit @ 5.1414 |
| --- | --- | --- |
| 14 in-stock JLCPCB ICs above (ESP32 … TCA9535) | 59.10 | 303.87 |
| + BLB01 x2 (DigiKey) + ADL5513 (DigiKey, 0 stock) + display (DigiKey) = **as-available snapshot (LB1)** | 113.05 | 581.22 |
| **Absolute lower bound (LB2)**: LB1 with ICM-42688-P at DigiKey 4.402 (0 stock) | 98.00 | 503.85 |
| LB2 + PCB (62.67 / 84.70 / 96.80 per 5) + Economic PCBA estimate (≥ 23.88) | 134.41 / 138.82 / 141.24 | **691.07 / 713.72 / 726.16** |
| LB2 without the display and ADL5513 (sensitivity only) | 47.60 | 244.72 |
| D24 target | 38.90 | 200.00 |

**Verdict: INFEASIBLE as of the 2026-09-23 snapshot.**
- The retrieved lines alone come to at least **BRL 504 per unit**, about 2.5x the BRL 200 target. With the published PCB/PCBA tariffs added, the total is about BRL 691–726, about 3.5x.
- Every TBD line (TA2003A, passives, the remaining ICs, connectors, holder, sourcing fees, the real PCBA quote) can only add cost. The verdict therefore does not depend on them.
- It holds even when you:
  - use the cheapest price found in any channel, including channels with zero stock;
  - exclude the display and ADL5513 entirely (BRL 245 > 200).
- The display (BRL 162) plus the in-stock ICM-42688-P (BRL 100) already exceed the target.

What the owner may consider (not proposals, and nothing changed):
- revisit the D24 target or scope;
- request an actual JLCPCB/other-assembler quote to confirm magnitude;
- open AGENTS rule 2 replacement studies (dated cost, availability, electrical, firmware and PCB impact) for the largest contributors: display, ICM-42688-P, MAX-M10S-00B and the ADL5513/ADS-B chain.

**Locked parts must not be substituted without owner acceptance (D-register).**

### B.5 Method notes and limits

- JLCPCB and LCSC values are library list prices. JLCPCB zero-stock rows sometimes show a placeholder price (USD 0.0396). Those rows were ignored, and zero-stock prices are flagged.
- The LCSC search endpoint is blocked (HTTP 403). Only per-C-number detail lookups were used.
- DigiKey values were read from the rendered product pages in a browser on 2026-09-23.
- Mouser was not retrieved: its bot protection was not bypassed.
- The PCBA estimate applies published tariffs to counts derived from the candidate PCB (958 SMD pads per board, about 20 leadless parts, 16+ extended lines). It is an estimate, not a quote.
