# SX1262 E449V01A reference values vs candidate sheet `08_lora`

Status: evidence note for the Claude one-shot candidate (review only). No `.kicad_sch`/`.kicad_pcb` file was changed. Retrieval and review date: **2026-09-23**.

> **Scope warning (AGENTS.md rules 3, 5, 12).** Every value below is a **Semtech reference-board value**. Semtech tuned these values on its own 1.00 mm four-layer FR4 board, with its own 0402 pads, trace geometry, SMA end-launch and PE4259 placement. They are **not** StratosCore values. Before anyone makes an RF claim (output power, harmonics, sensitivity, match), the network must be laid out on the chosen stack (`JLC04161H-3313` or whatever stack is confirmed at order time), simulated or EM-checked with that stack's parasitics, tuned on a VNA on real boards, and then pass conducted TX-power, harmonic and RX-sensitivity tests into calibrated 50-ohm loads. Region, power and duty-cycle settings stay configurable, and TX stays disabled until a regional configuration is selected (rule 14). None of this is done yet. Gate 6 is **not** closed by this note.

## 1. Sources

Every Semtech file came from the SX1262 product-page documentation table. Each link goes to a Semtech Salesforce content distribution page. The binary was fetched with `curl -A "Mozilla/5.0"` through `https://semtech.my.salesforce.com/sfc/dist/version/download/?oid=00DE0000000JelG&ids=<versionId>&d=/a/<dist>&operationContext=DELIVERY`. The `versionId` came from the distribution page's own `getContentDistributionInfo` call. No login was used.

| # | Document / package | Revision / date | Link (distribution page) | File retrieved | SHA-256 |
| --- | --- | --- | --- | --- | --- |
| S1 | Semtech SX1262 product page (documentation index) | page read 2026-09-23 | https://www.semtech.com/products/wireless-rf/lora-connect/sx1262 | HTML | — |
| S2 | **Shield: SX1262MB1PAS 915 MHz RF Module (SX1262DVK1PAS kit), design package** | listing date 2023-12-19; zip name `SX1262MB1PAS_915MHz_e449v01a_prod_folder.zip`, versionId `068RQ000003DWZwYAO` | https://semtech.my.salesforce.com/sfc/p/E0000000JelG/a/RQ000001HOv7/pWXGM5FZAsyaIejVS3wjO6cRnBwl8.BGAIAgmCBb358 (the same file is also linked from the SX1262DVK1PAS page as `.../a/RQ000001HNdy/...`, byte-identical) | zip, 2,929,055 B | `88c743ad0d0601df14ad75af013722be67d07b9b2a0500143ce3fd6bdb6d3c19` |
| S2a | ↳ `SX1262MB1PAS_915MHz_e449v01a_BOM.xlsx` | BOM # V1a, SCH # e449v01a, PCB # e449v01a, dated 2023-09-25 | inside S2 | xlsx | `0dccb6dea18b395ab97dac9467ae85d0981eca7dd313a7d1e609946913dc3813` |
| S2b | ↳ `SX1262MB1PAS_915MHz_e449v01a_sch_layout.pdf` | title block "SX1261/2 Evaluation Board - 4-Layers with TCXO", `PCB_E449V01A - SEMTECH`, Rev V1a, date 10.04.2021, file `SX126x_e449v01a.SchDoc`; p.1 schematic, pp.2-5 layer plots | inside S2 | pdf | `5c46e11c2ac2e42bd889aa29d053a454bd706f2df019cbc008700b313ce2467e` |
| S2c | ↳ `SX1262MB1xAS_e449v01a_gerbers.zip`: Gerbers, `.RUL` DRC export, `layers_description_pcb_e449v01a.doc`, `Quote_pcb_e449v01a.doc` | Gerber report 15.01.2018; layer description 15/01/2018 | inside S2 | zip | `ecb33780531e2eaa7192cbe64d0d2d63ec0d9f52dbe1cd7ff1cabd98f0e15010` |
| S2d | ↳ `Pick Place for SX1262MB1xAS_e449v01a.txt`, `SX1262MB1xAS_e449v01a_Altium_PCB_package.zip` (PcbDoc/SchDoc) | 15.01.18 | inside S2 | txt/zip | — |
| S3 | Shield: SX1262MB1CAS 915 MHz (SX1262DVK1CAS, North America), design package, `SX1262MB1CAS_915MHz_e428v03a_prod_folder.zip` (E428V03A, crystal) | listing 2024-09-27; BOM V1a dated 2023-09-25 | https://semtech.my.salesforce.com/sfc/p/E0000000JelG/a/RQ000005lBjV/pzRkOWpAD9knBS.Pfim2_2MVEoJ9lNIH7tO2ISIYTzc | zip, 2,910,989 B | `c140e5bb…fb36b4756` |
| S4 | Shield: SX1262MB2CAS 915 MHz mbed shield, `SX1262MB2CAS_915MHz_e499v01b_prod_folder.zip` (E499V01B, crystal) | listing 2023-12-19; BOM V1a dated 2023-09-25 | https://semtech.my.salesforce.com/sfc/p/E0000000JelG/a/RQ000001HRKz/YRmHo9Xiba3MCMAka9vgH5XqelE5NjVVPsmm4KgVk4Q | zip, 2,474,621 B | `1b8dd7bb…3566b634` |
| S5 | AN1200.40 "SX1261/2 Reference Design Explanation" | **Rev 1.1, May 2018** (listing 2019-07-02) | https://semtech.my.salesforce.com/sfc/p/E0000000JelG/a/2R000000HSSf/GT2IXjK2nH8bw6JdEXfFBd.HmFATeLOpL402mZwpSho | pdf, 25 pp | `1447fa94…3df8f9b6b` |
| S6 | SX1261/2 Data Sheet DS.SX1261-2.W.APP (`60852689.DS_SX1261_2 V2-2.pdf`) | **Rev 2.2, Dec 2024** (listing 2025-04-07) | https://semtech.my.salesforce.com/sfc/p/E0000000JelG/a/RQ000008nKCH/hp2iKwMDKWl34g1D3LBf_zC7TGBRIo2ff5LMnS8r19s | pdf, 118 pp | `6d783125…c4306c2` |
| S7 | AN1200.59 "Selecting the Optimal Reference Clock" | V1.8, Jul 2026 | https://semtech.my.salesforce.com/sfc/p/E0000000JelG/a/RQ00000EL5RF/ln2sXYN6aiaOR7p5xPRcg9h5P1l2pBLV0nOFab1FKz4 | pdf, 21 pp | `ac57740e…2ac` |
| S8 | "SX126x Development Kits Part Numbers description" | 2021-06-07 | https://semtech.my.salesforce.com/sfc/p/E0000000JelG/a/2R000000UTon/FwsERkp5yvRbKsL15R4Uz8bavQavWT7E_XU0DsavTiY | pdf, 1 p | `6e46a7ad…8a0` |
| S9 | pSemi PE4259 data sheet | **DOC-03694-5.01 (07/2026)** | https://www.psemi.com/pdf/datasheets/pe4259ds.pdf | pdf, 14 pp | `422ba4c6…8b53` |

Files were saved to the session scratchpad. They are not committed: this is Semtech/pSemi material, and no reuse-register entry is proposed.

Board identity (S8, S5 Table 1): **SX1262DVK1PAS / SX1262MB1PAS = PCB E449V01A, 4 layers, TCXO, "Australia / NA 923 MHz / 915 MHz", 22 dBm, RF switch.** The E449 BOM header says "4-Layers **922MHz** BOM" and its release sheet says "Updated BOM for 922MHz Australia Operations", although the file is named `915MHz`. The RF-path values are **identical** in the E449 (S2a), E428V03A 915 MHz North America (S3) and E499V01B 915 MHz (S4) BOMs. So one value set covers Semtech's 902-928 MHz SX1262 boards. That is still not a StratosCore validation.

## 2. E449V01A reference circuit (S2b p.1 schematic, S2a BOM)

Topology read from the native vector schematic (S2b p.1, "SX1261/2 Reference Design" and "RF Output Options and filter" blocks):

- **PA bias:** VR_PA (pin 24) → C1 ∥ C2 to GND. L1 runs from VR_PA to node A.
- **TX:** RFO (pin 23) → L2 (0 Ω) → node A. Node A: C3 shunt (not populated) and **L3 ∥ C4** (2nd-harmonic trap) → node B. C5 shunt at B → **C6 series** (DC block, AN §3) → L4 series → node C. C7 shunt at C → PE4259 RF1 (pin 1).
- **RX balun:** PE4259 RF2 (pin 3) → node F (C13 shunt, not populated) → **C11 series → RFI_N (pin 22)**. **L6 between RFI_N and RFI_P**. **C12 from RFI_P (pin 21) to GND.**
- **Antenna side:** PE4259 RFC (pin 5) → C8 series → C9 shunt → L5 series → C10 shunt → SMA "RFIO". In the drawing, the dashed boundary "Antenna matching not included here" sits to the right of C10, so C8/C9/L5/C10 fall under "Harmonics filter and Rx filter included in the Reference Design". AN1200.40 §3.1.3 describes C8/C9/L5/C10 as the place for additional filtering/antenna matching.
- **Switch control (complementary mode):** DIO2 (pin 12) → R3 → PE4259 CTRL (pin 4), C15 to GND. The **ANT_SW** net (mbed header J2 pin 1, a host GPIO) → R4 → PE4259 pin 6 (CTRL-bar), C14 to GND.
- **Clock:** Q2 32.0 MHz TCXO. VCC comes from **DIO3 (pin 6) → FB1**, with C28 to GND. OUT → **C27 → R5 → XTA (pin 3)**. **XTB (pin 4) is not connected** (X marker).
- **Supply:** VDD_RADIO → R18 (0 Ω, "SX1262: L8 unpopulated → R18 populated") → VDD_IN (pin 1), with C16. DCC_SW (pin 9) → L7 → VREG (pin 7), with C17 on VREG. VBAT/VBAT_IO (pins 10/11) on VDD_RADIO, with C18.

## 3. Value table mapped to `08_lora.kicad_sch`

Candidate designators and nets come from `candidates/claude-oneshot-revA/kicad/08_lora.kicad_sch` and `outputs/netlist.net` (read 2026-09-23). All E449 values are from S2a (sheet `SX1262MB1PAS`, BOM rows 7-64), unless marked otherwise. "Match" means the candidate position is **topologically equivalent** in the netlist, not that the value is valid on the StratosCore stack.

### 3a. TX path and PA supply

| E449 ref | Function (S2b p.1) | E449 value | Tol. | Dielectric / series | Exact MPN (mfr) | Size | Candidate | Topology match |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| U1 | Transceiver | SX1262 | — | — | SX1262IMLTRT (Semtech) | VQFN24 4x4 | U40 | Yes |
| C1 | VR_PA decoupling | 47 nF | ±10 % | X7R 16 V | GRM155R71C473KA01D (Murata) | 0402 | C74 (value TBD) | Partial: candidate has one cap; E449 has C1 + C2 |
| C2 | VR_PA RF decoupling | 47 pF | ±5 % | C0G 50 V | GJM1555C1H470JB01D (Murata) | 0402 | — | **Missing in candidate** |
| L1 | PA feed choke VR_PA → RFO node | 47 nH | ±5 % | wirewound LQW15AN | LQW15AN47NJ00D (Murata) | 0402 | L71 (TBD) | Yes |
| L2 | Series RFO → node A | 0 Ω | ±1 % | thick film | CRCW04020000Z0ED (Vishay) | 0402 | — | Candidate connects RFO directly (0 Ω equivalent; no tuning position) |
| C3 | Shunt at RFO node A | **not populated** (not in BOM) | — | — | — | 0402 | C75 ("TX match shunt", TBD) | Position exists; **E449 leaves it empty** |
| L3 | Match / notch series | 2.5 nH | ±0.2 nH | wirewound LQW15AN | LQW15AN2N5C00D (Murata) | 0402 | L72 (TBD) | Yes |
| C4 | Parallel with L3 (2nd-harmonic trap, AN §3.1.3) | 3.0 pF | ±0.1 pF | C0G 50 V | GJM1555C1H3R0BB01D (Murata) | 0402 | — | **Missing in candidate** |
| C5 | Match + pi-filter shunt | 5.6 pF | ±0.25 pF | C0G 50 V | GJM1555C1H5R6CB01D (Murata) | 0402 | C76 (TBD) | Yes |
| C6 | Series DC block ahead of L4 (AN §3: "protect the input of the RF switch") | 39 pF | ±5 % | C0G 50 V | GJM1555C1H390JB01D (Murata) | 0402 | C78 ("DC block to PE4259 RF1", TBD) | **Function matches, position differs:** E449 has C5 → C6 → L4 → C7 → RF1; candidate has C76 → L73 → C77 → C78 → RF1 |
| L4 | Pi-filter series | 4.7 nH | ±0.2 nH | wirewound LQW15AN | LQW15AN4N7C00D (Murata) | 0402 | L73 (TBD) | Yes (order vs C6 differs, see above) |
| C7 | Pi-filter shunt at RF1 | 1.8 pF | ±0.1 pF | C0G 50 V | GJM1555C1H1R8BB01D (Murata) | 0402 | C77 (TBD) | Yes |

### 3b. RX balun

| E449 ref | Function | E449 value | Tol. | Dielectric / series | MPN | Candidate | Topology match |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C11 | Series **RF2 → RFI_N** | 2.4 pF | ±0.1 pF | C0G 50 V | GJM1555C1H2R4BB01D (Murata) | C79 (TBD): netlist **RF2 (LORA_RX_SW) → RFI_P** | **No:** lands on the wrong LNA pin |
| L6 | **RFI_N ↔ RFI_P** | 15 nH | ±3 % | wirewound LQW15AN | LQW15AN15NH00D (Murata) | L74 (TBD): netlist **RF2 → RFI_N** | **No:** candidate inductor is in series from RF2, not across the differential pair |
| C12 | **RFI_P → GND** | 1.8 pF | ±0.1 pF | C0G 50 V | GJM1555C1H1R8BB01D (Murata) | C80 (TBD): netlist **RFI_N → GND** | **No:** shunt on the other pin |
| C13 | Optional interferer-rejection shunt at RF2 side of C11 (AN §4) | not populated | — | — | — | — | Candidate has no position (optional) |

### 3c. Switch, antenna side and control

| E449 ref | Function | E449 value | Tol. | Dielectric / series | MPN | Candidate | Topology match |
| --- | --- | --- | --- | --- | --- | --- | --- |
| U2 | SPDT T/R switch | PE4259 | — | UltraCMOS | PE4259 (Peregrine/pSemi) | U41 PE4259 | **Yes, same part as the project's PE4259 proposal** |
| C8 | Series from RFC | 39 pF | ±5 % | C0G 50 V | GJM1555C1H390JB01D (Murata) | C83 ("antenna DC block", TBD) | Yes |
| C9 | Shunt after C8 | 3.3 pF | ±0.1 pF | C0G 50 V | GJM1555C1H3R3BB01D (Murata) | — | **Missing** |
| L5 | Series | 9.1 nH | ±3 % | wirewound LQW15AN | LQW15AN9N1H00D (Murata) | — | **Missing** |
| C10 | Shunt at connector | 3.3 pF | ±0.1 pF | C0G 50 V | GJM1555C1H3R3BB01D (Murata) | — | **Missing** |
| RFIO | Antenna port | SMA end launch 50 Ω | — | — | 32K145-400L5 (Rosenberger) | J6 U.FL-R-SMT-1(60) | Different connector (project P25); transition must be re-modelled |
| R3 | DIO2 → CTRL (pin 4) | 100 Ω | ±1 % | thick film 1/16 W | CRCW0402100RFKED (Vishay) | R71 100R | Yes |
| C15 | CTRL filter | 1 nF | ±10 % | X7R 100 V | GRM155R72A102KA01D (Murata) | C81 1nF | Yes (value matches; MPN TBD in candidate) |
| R4 | ANT_SW (host GPIO) → pin 6 CTRL-bar | 100 Ω | ±1 % | thick film | CRCW0402100RFKED (Vishay) | R72 100R, but from **3V3_MAIN** | Different mode, see §5 |
| C14 | Pin 6 filter | 1 nF | ±10 % | X7R 100 V | GRM155R72A102KA01D (Murata) | C82 1nF | Yes (value) |

### 3d. Regulator / supply decoupling

| E449 ref | Net | E449 value | Tol. | Dielectric | MPN | Candidate | Match |
| --- | --- | --- | --- | --- | --- | --- | --- |
| L7 | DCC_SW ↔ VREG | **15 µH** (populated) | ±20 % | multilayer shielded | MLZ2012M150W (TDK), 0805. BOM alternatives "recommended for new design": MLZ1608N100LT000 10 µH or MLZ1608N150LT000 15 µH, 0603 | L70 15uH 0805 | Yes (value) |
| C17 | VREG | 470 nF | ±10 % | X7R 10 V | GRM155R71A474KE01D (Murata) | C73 470nF | Yes |
| C16 | VDD_IN (pin 1) | 1 µF | ±10 % | X5R 16 V | GRM155R61C105KA12D (Murata) | — (candidate C71 is **470 nF** on 3V3_MAIN) | **Value/placement differ** |
| C18 | VBAT/VBAT_IO | 100 nF | ±10 % | X7R 50 V | GRM155R71H104KE14D (Murata) | C72 100nF | Yes (value) |
| R18 | VDD_RADIO → VDD_IN (SX1262 option) | 0 Ω | ±1 % | thick film | CRCW04020000Z0ED | — (direct) | Equivalent |
| L8 | VREG → VDD_IN (SX1261 option) | not populated | — | — | — | — | N/A for SX1262 |
| C20, C21 / C22, C26 / C23, C24 | Board rails VDD_3V3, VDD_RADIO / VDD_MBED, VUSB / display | 1 µF / 10 µF / 100 nF, 1 µF | ±10 % | X5R / X7R (GRM188Z71A106KA73D for 10 µF) | see S2a | C70 10uF | Board-level bulk only, not SX1262-local decoupling |

### 3e. Reference clock, DIO3 and DIO2

| Item | E449V01A (S2a/S2b) | E428V03A / E499V01B (S3/S4) | Candidate `08_lora` |
| --- | --- | --- | --- |
| Reference | **Q2 32.000 MHz TCXO NDK NT2016SF-32MHz END4263D**, alternative **Rakon RST2016N 32 MHz Ref. T6393** (2.0x1.6 mm). The BOM Qty cell for Q2 reads "-", recorded verbatim; the schematic shows Q2 fitted. Both parts are "Qualified" in AN1200.59 V1.8 Table 6 | **Q1 crystal NDK EXS00A-CS06465 (NX2016SA 2.0x1.6), 32 MHz, ±10 ppm, CL = 10 pF, 2 ppb/g**; alternative Rakon FTR5123-B0 | Y2 32 MHz crystal, CL 10 pF, **MPN TBD**, 2016 4-pin footprint (crystal approach = E428-type, not E449) |
| TCXO coupling | C27 10 pF ±5 % C0G GJM1555C1H100JB01D + R5 220 Ω ±5 % CRCW0402220RJNED into XTA; XTB NC. Matches DS Rev 2.2 §4.1.4 p.25 ("220 Ω resistor and a 10 pF DC-cut capacitor", XTB not connected) | — | not present |
| TCXO supply | DIO3 → FB1 Murata BLM15PG100SN1D (10 Ω @ 100 MHz, 1 A) → TCXO VCC, C28 100 nF GRM155R71H104KE14D. DS §4.1.4: DIO3 regulated 1.6-3.3 V, VBAT ≥ VTCXO + 200 mV, 1.5 mA nominal, 4 mA max, clipped-sine ≤ 1.2 Vpp | DIO3 unused | DIO3 unconnected (TCXO fallback noted on sheet) |
| DIO2 | Drives PE4259 CTRL via R3/C15. DS §8.3.2 p.57: with `SetDio2AsRfSwitchCtrl`, DIO2 = 1 in TX, 0 otherwise | same | Same (R71/C81 → U41 CTRL) |
| Crystal limits (DS Rev 2.2 Table 3-4, p.16) | — | — | 32 MHz, CL 10 pF typ, C0 0.3/0.6/2 pF, ESR 30 typ / 60 Ω max, Cm 1.3-2.5 fF, drive ≤ 100 µW |

AN1200.40 Rev 1.1 §2.2/§2.3 (pp.9, 13) explains the difference. E428 (crystal) targets regions where the maximum packet duration is under 400 ms. E449 needs "a four-layer board PCB and TCXO" where packets can last up to 2.8 s. Crystal boards with thermal insulation "were still exceeding the tolerable frequency drifts" there. For StratosCore's configurable region/SF plan, crystal versus TCXO is therefore an **open owner decision** tied to the longest allowed packet airtime, not a detail.

## 4. Topology mismatches in `08_lora` (candidate vs E449)

1. **RX balun wired differently** (C79/L74/C80 vs C11/L6/C12). The E449 order is RF2 → C11 → RFI_N, L6 across RFI_N/RFI_P, C12 RFI_P → GND. The candidate uses RF2 → C79 → RFI_P, L74 RF2 → RFI_N, C80 RFI_N → GND. E449 values cannot be dropped into the candidate positions.
2. **No C4** (3.0 pF, parallel to L3). The 2nd-harmonic trap is missing.
3. **DC block in the wrong place.** E449 has C6 39 pF between the C5 node and L4. The candidate places C78 between C77 and PE4259 RF1.
4. **Extra shunt at RFO.** Candidate C75 corresponds to E449 C3, which Semtech leaves unpopulated.
5. **No L2 position.** E449 has a 0 Ω jumper in the RFO path, which leaves room for tuning.
6. **Only one VR_PA capacitor.** E449 has C1 47 nF + C2 47 pF.
7. **Antenna-side pi (C9/L5/C10) missing.** The candidate has only C83 (≈ C8). E449 populates all four parts.
8. **Supply decoupling differs.** E449 has C16 1 µF at VDD_IN. Candidate C71 is 470 nF, and all three candidate supply caps sit on one 3V3_MAIN net without pin-local assignment.
9. **Connector differs.** U.FL instead of SMA end launch, so the launch/transition must be re-modelled.
10. **Clock source differs.** Crystal (E428-style) vs TCXO (E449). See §3e.

Items 1-7 mean the candidate RF block does not follow E449 today. It must be re-drawn to the E449 topology before E449 values mean anything on it.

## 5. RF switch: PE4259 vs project proposal

- The reference uses the **same part** the project proposes: **PE4259** (Peregrine, now pSemi), SC70-6, in all three BOMs (S2a/S3/S4 row "U2").
- **Control mode differs.** E449 uses **complementary-pin mode**: DIO2 → CTRL (pin 4) and a separate host GPIO `ANT_SW` → CTRL-bar (pin 6). The candidate uses **single-pin mode**: pin 6 to 3V3_MAIN through R72/C82, and DIO2 alone on pin 4. pSemi DOC-03694-5.01 Table 5 (PDF p.5) defines single-pin mode: pin 6 = VDD; CTRL High → RFC–RF1; CTRL Low → RFC–RF2. Combined with DS §8.3.2 (DIO2 = 1 in TX), RF1 = TX, which matches the candidate (RF1 = LORA_TX_SW). The mode is legitimate per the switch datasheet, but it is **not** the reference configuration.
- **VDD headroom check needed.** DOC-03694-5.01 operating range (PDF p.2): VDD 1.8 / 3.0 / **3.3 V max**. Pin 6 on 3V3_MAIN sits at the maximum, so the regulator tolerance of 3V3_MAIN must be checked against 3.3 V max. That check is open, and the rail tolerance is not verified here.
- Firmware must call `SetDio2AsRfSwitchCtrl` (DS §13.3.5) before TX.

## 6. Reference stackup vs project candidate stack

| Parameter | E449V01A (S2c `layers_description_pcb_e449v01a.doc`, `.RUL`, `.GTL`; S2b pp.2-5) | JLC04161H-3313 candidate (`docs/PCB_STACKUP.md`) |
| --- | --- | --- |
| Layers / thickness | 4 layers, FR4, **1.00 mm** | 4 layers, **1.6 mm** |
| L1 copper | 35 µm | 35 µm (1 oz) |
| L1-L2 dielectric | **FR4 0.15 mm** (Dk not stated in the package) | **3313 prepreg 0.0994 mm pressed, Dk 4.1** |
| L2 | 18 µm inner. Plot (S2b p.3) shows continuous copper under the RF chain (net name not printed on the plot) | 0.5 oz (15.2 µm), proposed unbroken GND |
| Core | FR4 ~0.53 mm | 1.265 mm |
| L3 / L3-L4 | 18 µm / FR4 0.15 mm | 0.5 oz / 3313 0.0994 mm |
| L4 | 35 µm | 35 µm |
| RF trace width (L1) | **0.250 mm**. Every RF-chain segment U1 → U2 → SMA uses Gerber aperture D27 = C0.250 (`SX126x_e449v01a.GTL`, region X 60-88 / Y 26-36 mm) | 50 Ω candidate **W ≈ 0.133 mm** (first-order calc, not solver-confirmed) |
| RF-to-ground clearance | DRC rule `Clearance_RF_GND` = 9.84 mil (0.25 mm) (`SX126x_e449v01a.RUL`). Top-layer plot shows coplanar GND pour with a via fence along the chain | not defined |
| Other rules | min width 5.91 mil, min clearance 5.91 mil | per JLC capability |
| Placement | All matching parts 0402, top side, in line within ~25 mm (U1 at 59.2/30.9 mm, U2 at 75.5/30.3 mm, SMA at 86.65/29.7 mm, Pick Place file). Optional Laird BMI-S-209 shield outline (qty 0) | Candidate RF block autorouted 0.15 mm tracks, not GCPW (see `ISSUES.md`) |

Implication: the E449 values were tuned on a 0.15 mm L1-L2 dielectric with 0.25 mm lines and 0.25 mm coplanar gaps. The candidate stack has a 0.0994 mm L1-L2 dielectric with a different Dk. Pad-to-ground parasitics, line impedance and electrical lengths all change. **No value or trace width transfers without re-simulation on the chosen stack and VNA tuning (AGENTS rule 5).** No impedance figure for the E449 line is computed here, because its Dk is not published in the package.

## 7. Corrections to existing repo evidence (not edited; flagged for the integrator)

`docs/RF_ARCHITECTURE.md` "Gate-6 reference-design evidence" (recorded 2026-09-17/19, figure OCR of the AN raster) conflicts with the native Semtech files:

- **"L7 = 15 nH" is wrong.** The native BOM gives **15 µH** (MLZ2012M150W). The candidate's 15uH is correct.
- **"C1 = 0.1 uF" is wrong.** The native BOM gives **47 nF** X7R.
- **"PCB_E428V03A (2-layer, crystal)" is wrong.** AN1200.40 Table 1, S8 and the E428 layer description all say **4-layer**, 1.00 mm FR4, same stack as E449.
- **C22/C26 10 µF are board-level bulk capacitors** on VDD_MBED/VUSB, not SX1262 supply decoupling.
- **R915/R868/R490/R434 ("Frequency band" block) plus the SX1261/SX1262/TCXO/FR0/FR1 resistors are board-identification straps**, not RF band selection. Region selection in the reference is done by the regional BOM.
- The claim that the AN documents an **SX1262** load-pull is not supported. AN1200.40 §3.1.1 gives only the **SX1261** 915 MHz load-pull (max 14.6 dBm at 11.7 + j4.8 Ω; 13.5 + j7.6 Ω for efficiency) and §4 the SX1261 LNA Zopt of 74 + j134 Ω. §3.1 itself says the data "may not be the most up-to-date".
- The "matching values illegible / AN prints designators only" statements (`RF_ARCHITECTURE.md`, `ISSUES.md`, the `08_lora` sheet note) are superseded. The native E449 BOM is publicly retrievable (S2).

## 8. What remains open (not closed by this note)

- Owner decision: TCXO (E449) versus crystal (E428), given the maximum packet airtime under the configurable regional plans.
- Re-draw `08_lora` to the E449 topology (§4 items 1-8). This is a schematic change that needs owner/Astra gating and was not done here.
- Exact StratosCore values: layout on the confirmed stack, then simulation/EM with the real pads, U.FL transition and ESD part (the BOM recommends Semtech RClamp2451ZA at the antenna port; not evaluated here), then VNA tuning of TX match/harmonic trap/pi filter and RX balun.
- Conducted tests: TX power per regional setting, harmonics (2nd-harmonic trap depth), RX sensitivity, TCXO or crystal start-up and frequency error. No result exists yet, so every RF performance figure remains **TBD**.
- 3V3_MAIN tolerance versus the PE4259 3.3 V maximum (§5).
