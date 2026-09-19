# RF architecture before layout

Status: mandatory pre-layout concept; no antenna placement or matching network is frozen. Four independent RF functions must coexist within a very small device.

| System | RF path | Constraints |
| --- | --- | --- |
| Wi-Fi / BLE | ESP32-S3-WROOM-1 module PCB antenna, 2.4 GHz | Preserve exact module antenna keepout in all relevant layers and enclosure materials; no external-antenna module substitution |
| GNSS | P20 passive FXP611/U.FL/TPD1E0B04 proposal for accepted MAX-M10S-00B | Separate no-bias receive path; RF/PDN review, fit, calculated geometry and VNA/coexistence tests remain |
| LoRa | SX1262, reference matching/filter/switch network, U.FL, 915 MHz class antenna | Direct IC integration; oscillator/TCXO and RF switch policy chosen with Semtech reference; region-specific transmission |
| ADS-B | Separate 1090 MHz antenna, preselection, LNA/filtering, detector/comparator, RP2040 | Receiver blocker tolerance and analog bandwidth must be demonstrated; never shared with SX1262 |

Start SX1262 work from [Semtech's SX1262 product/reference-design library](https://www.semtech.com/products/wireless-rf/lora-connect/sx1262), including the 915 MHz-capable SX1262MB1LDCS reference. The reference device is the `SX1262IMLTRT` (QFN-24 4 x 4 mm, confirmed orderable 2026-09-14: DigiKey 37,715 units at USD 9.04, 8-week lead).

### Gate-6 reference-design evidence (recorded 2026-09-17)

Primary sources, retrieved and text-reviewed 2026-09-17: Semtech **AN1200.40 Rev 1.1 (May 2018), "SX1261/2 Reference Design Explanation"** (25 pages; official Semtech document, retrieved via the Reichelt CDN mirror of the identical file after semtech.com blocked direct PDF fetch) and the **SX1261/2 datasheet** (Rev 1.2 class, 20-page abridged edition via SparkFun CDN).

**Reference-design revision selection.** AN1200.40 documents exactly two SX1262 reference designs: `PCB_E428V03A` (2-layer, **crystal** reference, regional BOMs incl. USA 902-928) and `PCB_E449V01A` (4-layer, **TCXO**, regional BOMs incl. Australia 915-928). Neither is the Mbed shield (SX1262MB1LDCS/MB2CAS are development boards built around these designs). For StratosCore the **E449V01A (4-layer TCXO) topology is the proposed starting point** because StratosCore is a 4-layer board with co-located GNSS/ADS-B/Wi-Fi radios where frequency accuracy and phase noise matter; final BOM values must come from the E449 regional BOM sheet, which is a drawing-embedded table not present in the AN text — transcription of exact component values remains a drawing-review task, not desk-closed here.

**Figure-read values from Figure 10 (E449V01A schematic), recorded 2026-09-19.** The AN PDF embeds the schematic as a compressed raster; a multi-pass 6x-zoom vision transcription (three consistent passes, contradictions discarded) read the following values with confidence: **TCXO = 32.0 MHz** (designator Q2); **L7 = 15 nH**; **C17 = 470 nF, C18 = 100 nF, C22 = 10 uF, C26 = 10 uF** (supply decoupling net); **C14 = 1 nF, C15 = 1 nF, R3 = 100 ohm, R4 = 100 ohm** (PE4259 RF-switch control/bias network, U2 confirmed); **C1 = 0.1 uF**; title block "SX1262 Evaluation Board - 4-Layers with TCXO", `PCB_E449V01A` rev V1a dated 14.03.2018; and a **frequency-band selection resistor network (R915 / R868 / R490 / R434, one populated per region)** — the same configurability AGENTS.md rule 14 requires, confirming the reference selects region by population, not firmware. The **TX/RX matching-network values (C8/C9/C10/L5 class) are illegible in the AN raster at any zoom** — they remain blocked on the native E449 drawing/BOM sheet. Evidence class for everything read here: single-source figure OCR, pending verification against the native Semtech drawing before schematic commitment; do not transfer to StratosCore's stackup without that verification (AGENTS.md rule 5).

**Matching/filter topology (AN1200.40 §3.1-3.1.3, §4, Figures 15-18).** TX: L3+C5 impedance-match stage to 50 ohm; second-harmonic notch = L3 replaced by parallel LC (L ≈ ¾·L3, C4 resonant at 2·f0); higher-order harmonic pi-filter on C5/L4/C6/C7 (C5 shared between matching and filtering); optional antenna-side C8/C9/L5/C10. RX: discrete balun C11/C12/L6 (C13 optional interferer rejection) transforming 50 ohm to the differential LNA Zopt. At 915 MHz the documented SX1261 source-pull Zopt is 74 + j134 ohm (Figure 18; SX1262 PA Zopt is a different, higher-power pull documented on the load-pull figure of the same AN). Simulated values must be fine-tuned for PCB parasitics — no value transfers between boards (AGENTS.md rule 5).

**Oscillator and regulator topology (AN1200.40 §2.1/§2.2; datasheet §4.1 oscillator).** Default reference configuration powers the PA from the **internal DC-DC** (inductor VDD_IN↔DCC_SW; datasheet: 100 nF on DCC pins, 1.5-4 V range); the LDO option shorts that inductor and removes the DCC_SW inductor, saving cost/size at lower efficiency. The AN states the DC-DC efficiency gain plus thermal relief **enables a low-cost crystal instead of a TCXO**; the TCXO path (E449V01A) exists when accuracy demands it. Datasheet TCXO connection: XTA pin 3 via 220 ohm + 10 pF DC-block, DIO3 can supply the TCXO rail. **Proposal:** DC-DC (flight endurance priority, consistent with the O13 power budget) + crystal with the datasheet trimming-cap defaults (XTB trim 11.3-33.4 pF range documented); TCXO/DIO3 remains the fallback if bench phase-noise/frequency-error against GNSS PPS fails.

**Antenna switch (AN1200.40 §2.1.1).** Both reference designs combine TX/RX through a **Peregrine PE4259 SPDT RF switch**, which the AN credits with independently optimizable TX and RX matching (better sensitivity, output power and harmonics). SX1262 DIO2 can also drive an internal RF-switch control path. **Proposal:** follow the reference discrete PE4259-class switch; DIO2-as-switch-drive recorded as the integration alternative. Coexistence on 84 x 60 mm with GNSS (1.575 GHz) and ADS-B (1.090 GHz) antennas keeps the U.FL ports and keepouts already assigned in P25/O09.

**Conducted test plan outline (915 MHz, per datasheet tables):** verify conducted TX power at the antenna port across the configured regional power setting (SX1262 PA is +22 dBm-capable — the Brazilian 915-928 MHz band limit and LoRaWAN ERP/duty rules must be applied before any TX enable; region config per AGENTS.md rule 14), harmonic levels vs the AN1200.40 filter targets (2nd harmonic notch depth), RX sensitivity at target SF/BW, and DIO3/TCXO or crystal startup behavior. All conducted, into calibrated 50-ohm loads, before any radiated test. Do not assume a regional development-board frequency/power configuration is lawful everywhere.

For the ESP antenna, use [Espressif hardware layout guidance](https://documentation.espressif.com/esp-hardware-design-guidelines/en/latest/esp32s3/pcb-layout-design.html) and exact module drawings. A nominally isolated corner can still be detuned by the battery can, display metal, screws, hands and SMA pigtails. No universal keepout distance is assigned here.

## Placement and stackup study

First place volume/keepout envelopes for module antenna, display FPC, cell holder, connectors and all RF zones. Keep high-current loops and fast display/SD clocks away from receive inputs and their matching networks. Use short controlled-impedance RF paths over continuous return planes, stitching as determined by RF frequency and geometry, and local decoupling/rail filtering. Shield cans and partitions are options; leave area until coexistence is measured. The current spatial proposal and section view are in [the mechanical/RF floorplan](MECHANICAL_RF_FLOORPLAN.md).

L2 is proposed solid ground. L1 RF referenced to L2 is a starting point. L3 power/signal allocation must also provide coherent return paths for L4 signals; the conceptual stack is not automatically suitable for high-speed routing on every layer. Ask the manufacturer for dielectric thickness, copper, soldermask and impedance capability; calculate 50-ohm geometries from that stack. No trace width is specified before then. See [manufacturing](MANUFACTURING_STRATEGY.md).

## Coexistence tests and remedies

| Aggressor | Victim / observation | Evidence and mitigation candidates |
| --- | --- | --- |
| LoRa TX at allowed power/duty settings | ADS-B compression/packet loss; GNSS C/N0/fix degradation | Sweep channels/power and physical antennas; measure blocking, filtering, shielding, coupling and recovery |
| Wi-Fi traffic / BLE | GNSS, ADS-B; pressure/IMU supply noise | Compare receiver metrics and sensor noise with radios idle/active |
| LCD/SD/USB clocks and DC/DC switching | Receive sensitivity and spurious response | Max refresh/write/charge state, near-field scan, conducted noise checks |
| Battery/holder/magnets/current loops | MMC5983MA heading bias; antenna detuning | Test both cell populations and charge currents, final enclosure and user grip |

Use conducted input first, known ADS-B messages and known GNSS signal/sky conditions, then assembled radiated comparison. Record baseline and delta, not just "works." Simultaneous LoRa TX and reception are not guaranteed. If blanking receivers is necessary, explicitly log blind intervals and evaluate the FLIGHT impact before acceptance.

Power the analog RF path from a domain with noise and headroom verified against selected components. Add low-capacitance ESD appropriate to RF ports; select its parasitics in matching analysis. Reserve instrument access and antenna strain relief. P25 proposes one exact Hirose U.FL receptacle for all three board RF paths and Taoglas CAB.721 for ADS-B plus optional LoRa SMA bulkheads. These remain RF/CAD/test gates as detailed in [RF connector selection](RF_CONNECTOR_SELECTION.md).
