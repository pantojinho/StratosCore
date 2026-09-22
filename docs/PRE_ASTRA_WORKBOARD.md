# Pre-Astra execution workboard

Status: **ACTIVE**. This is the operational queue for taking StratosCore from the current pre-KiCad engineering state to an Astra-ready input package. It does not replace [project status](PROJECT_STATUS.md), [decisions](DECISIONS.md), [open questions](OPEN_QUESTIONS.md), or the gated [Astra handoff](ASTRA_HANDOFF.md).

The workboard separates work an agent can complete from owner decisions, qualified reviews, procurement, factory confirmation, and physical tests. Writing a document is not completion by itself: each task closes only when its evidence column is satisfied.

Coordination snapshot: `origin/main` at `b0f4ebb` reconciled on 2026-09-22 (GOV-02 vigil retired; SYS-01 #140, ADSB-01 #142, DIG-01 #144 and PWR-02 #147 accepted). The next coordinator must replace this snapshot with the current baseline before assigning work.

[PR #137](https://github.com/pantojinho/StratosCore/pull/137) was merged automatically while this decision update was in progress. It changed only `AUDIT_LOG.md` and explicitly reported no engineering action. **GOV-02 closed 2026-09-22:** the vigil was retired (see GOV-02 and `AUDIT_LOG.md`) and future equivalent no-change PRs must not be opened or merged.

## Roles and state model

| Role | Authority |
| --- | --- |
| Coordinator | Assigns tasks, prevents overlap, reviews status and sequences integration; does not silently decide product or safety questions |
| Worker agent | Completes one bounded task in its allowed files and opens a reviewable PR; never merges its own work |
| Integrator | Reconciles accepted worker PRs into the central status/decision/BOM documents and publishes to `main` |
| Independent reviewer | Reviews evidence without editing the implementation under review |
| Owner | Accepts product, cost, operating-policy and regulatory decisions |
| Qualified electrical/battery reviewer | Is the only role that may approve the complete 2S safety design |
| Factory/assembler | Confirms stackup, impedance, stencil, assembly and DFM constraints |

Task states are `BACKLOG`, `READY`, `ACTIVE`, `REVIEW`, `BLOCKED_OWNER`, `BLOCKED_EXTERNAL`, `ACCEPTED`, and `SUPERSEDED`. A task may move to `ACCEPTED` only with the named evidence. Repeated status-only audits do not change task state and must not create commits.

## Dependency path

```mermaid
flowchart TD
  G[Governance and owner decisions] --> P[Exact parts and subsystem circuits]
  P --> E[Electrical and interface convergence]
  P --> C[Verified CAD libraries]
  P --> M[Mechanical and factory inputs]
  E --> R[Independent system review]
  C --> R
  M --> R
  R --> F[Pre-Astra freeze and manifest]
  F --> A[Astra KiCad execution]
```

## Wave 0: control the parallel workflow

| ID | State | Owner | Task | Depends on | Allowed files | Closure evidence |
| --- | --- | --- | --- | --- | --- | --- |
| GOV-01 | ACCEPTED | Coordinator | Reconcile the current `origin/main` baseline and review substantive changes separately from audit-only commits | none | read-only | Baseline `3d45c37` reconciled 2026-09-21; its latest delta was the audit-only PR #137, separated from substantive engineering changes |
| GOV-02 | ACCEPTED | Automation owner | Stop any recurring job that creates audit-only `AUDIT_LOG.md` commits when no engineering delta exists | none | automation configuration only | 2026-09-22: no external automation existed (no Actions/webhooks/cron); the loop was session-driven by the frozen procedure itself. `AUDIT_LOG.md` carries the GOV-02 retirement banner; duplicate audit-only PRs #138/#139 closed unmerged; the procedure is frozen as history |
| GOV-03 | ACCEPTED | Integrator | Enforce [swarm protocol](SWARM_PROTOCOL.md), branch ownership and central-file integration rules | GOV-01 | `AGENTS.md`, `SWARM_PROTOCOL.md` | Workers use isolated branches/PRs; no concurrent central-file edits |
| GOV-04 | ACCEPTED | Integrator | Resolve the BOM circularity: pre-Astra engineering BOM versus post-capture annotated/orderable BOM | GOV-03 | `ASTRA_HANDOFF.md`, `MANUFACTURING_STRATEGY.md` | Handoff distinguishes exact pre-Astra MPN/planned-quantity input from post-Astra reference-designator BOM |

## Wave 1: owner and external inputs

These tasks can run in parallel. Agents prepare decision packets; only the named human or organization accepts them.

| ID | State | Owner | Task | Maps to | Closure evidence |
| --- | --- | --- | --- | --- | --- |
| OWN-01 | ACCEPTED | Owner | Require operation while charging; batteryless operation remains out of scope | D21, O06, Gate 2 | Owner acceptance recorded 2026-09-21; engineering must prove charge-under-load behavior |
| OWN-02 | ACCEPTED | Owner + electrical reviewer | Use 100 kHz shared I2C and move TUSB320LAI to GPIO mode | D22/P26, O11, Gate 9 | Owner acceptance recorded 2026-09-21; SYS-01 closes pull-ups, GPIOs, cable and off-state review |
| OWN-03 | ACCEPTED | Owner | Classify Rev A as a personal, non-commercial, open-community hobby prototype | D23, O21, Gate 10 | Owner classification recorded 2026-09-21; applicable operating rules remain REG-01 work |
| OWN-04 | BLOCKED_OWNER | Owner | BRL 200 average/unit target for five units accepted; define which costs are included | D24, O23, Gate 10 | Confirm display, enclosure, shipping/tax and locally purchased cell treatment |
| OWN-05 | BLOCKED_OWNER | Owner | Terrestrial and balloon use accepted; quantify altitude, duration and temperature plus any dynamics/drop/vibration expectations | D25, O16/O22, Gate 10 | Quantified mission/environment table; mass and rain/ingress are not targets |
| OWN-06 | ACCEPTED | Owner + logistics reviewer | Source removable cells locally and do not ship the current prototype with cells | D26, O24, Gate 10 | Owner disposition recorded 2026-09-21; exact cell provenance remains EXT-02 engineering input |
| OWN-07 | BLOCKED_OWNER | Owner | Decide whether the assembler flashes firmware, serial numbers or keys. Recommendation for five prototypes: PCBA assembly only; flash and test locally through USB/SWD, with no factory secrets | O25, Gate 10 | Accepted factory-versus-local programming and labeling policy |
| OWN-08 | ACCEPTED | Owner + mechanical/process reviewer | Use no conformal coating, ingress qualification or special environmental protection in Rev A | D27, O26, Gates 8/10 | Owner disposition recorded 2026-09-21; preserve required sensor and acoustic openings |
| OWN-09 | BLOCKED_OWNER | Owner + RF reviewer | Define ADS-B sensitivity, range, contact and stale-time targets | O18, Gate 7 | Quantified conducted and field acceptance targets |
| EXT-01 | BLOCKED_EXTERNAL | Procurement | Obtain the controlled Orient C1 power/FPC drawing and two traceable display samples | O01, Gate 1 | Controlled drawing revision plus sample labels/photos/measurements |
| EXT-02 | BLOCKED_EXTERNAL | Procurement | Obtain an exact documented 2S 21700 holder exposing B-/MID/B+ and authentic cell samples | O05/O06, Gate 2 | Manufacturer MPN/drawing, ratings, continuity and physical samples |
| EXT-03 | BLOCKED_EXTERNAL | Qualified reviewer | Review and sign the complete 2S charger/protection/power-path design | O05, Gate 2 | Named reviewer, evidence reviewed, fault limits and written acceptance |
| EXT-04 | BLOCKED_EXTERNAL | Factory | Confirm the supported JLCPCB stack service, official 50-ohm/90-ohm solver geometries and assembly rules for layout | O10, Gate 8 | Current factory stack/solver/DFM outputs; the actual order ticket and coupon/TDR remain post-layout controls |
| EXT-05 | BLOCKED_EXTERNAL | Assembler | Approve stencil/mask/paste decisions for MEMS, GNSS, U.FL, flash, crystal and fine-pitch support parts | O19/O20, Gates 3-5 | Part-by-part written process disposition |
| EXT-06 | BLOCKED_EXTERNAL | RF lab/reviewer | Provide simulation/VNA/spectrum capability and conducted test fixtures | O03/O04/O09/O18, Gates 3/6/7 | Calibrated test plan, fixture definition and reviewer assignment |

## Wave 2: subsystem engineering

Workers in this wave must use exact manufacturer sources and stay inside their subsystem files. Work may proceed in parallel unless the dependency column says otherwise.

| ID | State | Gate | Task | Depends on | Primary files | Closure evidence |
| --- | --- | ---: | --- | --- | --- | --- |
| DSP-01 | BLOCKED_EXTERNAL | 1 | Resolve TFT VCC/VDDI/VDD, both FPC pinouts, unused pins and ST1633I address convention | EXT-01 | `DISPLAY_REQUIREMENTS.md` | Controlled-drawing transcription with no ambiguous supply or pin |
| DSP-02 | READY | 1 | Complete the three-line SPI translator/reset/backlight application and all startup/off-state calculations | DSP-01 for final acceptance | `DISPLAY_REQUIREMENTS.md`, `ELECTRICAL_COMPATIBILITY_MATRIX.md` | Exact values, tolerances, power, faults and sequence reviewed |
| DSP-03 | BLOCKED_EXTERNAL | 1 | Create and independently review exact display/touch connector footprints | EXT-01 | `hardware/footprints/`, footprint review document | KiCad export plus independent dimensional review and sample-fit result |
| DSP-04 | BLOCKED_EXTERNAL | 1 | Run two-sample display/touch/backlight bench qualification | DSP-01/02/03, EXT-01 | test report only | SPI/readability/touch/address/current/fault/EMI results |
| PWR-01 | BLOCKED_EXTERNAL | 2 | Freeze exact cells, holder, service-pair rules, fuse and temperature-sensing requirements | OWN-01, EXT-02 | `POWER_ARCHITECTURE_REVIEW.md` | Exact MPNs and accepted electrical/mechanical limits |
| PWR-02 | ACCEPTED | 2 | Close USB4105, TPD4E05U06, TUSB320LAI and TPS259474L application; remove unsupported ESD claims | OWN-02 for final bus choice | `CONNECTOR_ARCHITECTURE.md`, `POWER_INPUT_EVIDENCE.md` | Delivered 2026-09-22 (PR #147): eFuse network exact (RILM 1.69 k -> 1.97 A, UVLO 3.98 V, OVLO 6.50 V, dVdt open, ITIMER at O06), default-current-only sink policy from GPIO-mode CC, TUSB320LAI wired per D22, device-level-only ESD claim corrected; O05 untouched |
| PWR-03 | BLOCKED_EXTERNAL | 2 | Produce the complete BQ25887 plus common-protection topology and fault matrix | PWR-01/02, OWN-01 | `POWER_ARCHITECTURE_REVIEW.md`, `POWER_RAIL_PLAN.md` | Exact circuit proposal ready for qualified review; no unresolved ground/cutoff conflict |
| PWR-04 | READY | 2/9 | Complete rail peak inventory, regulator passives, sequencing, back-power, thermal and transient calculations | subsystem current data | `POWER_BUDGET.md`, `POWER_RAIL_PLAN.md`, matrix | Every load has sourced max/allowance; simultaneous peak and margins shown |
| PWR-05 | BLOCKED_EXTERNAL | 2 | Obtain qualified approval of PWR-03/04 and the fault-test limits | EXT-03, PWR-03/04 | reviewer record | Signed acceptance before committed schematic capture or energizing |
| GNSS-01 | READY | 3 | Finalize MAX-M10S supply/UART/PPS/no-connect/backup and passive RF application | PWR-04 | `GNSS_ARCHITECTURE.md` | Complete net/application table and PDN calculation |
| GNSS-02 | BLOCKED_EXTERNAL | 3 | Close antenna/U.FL/ESD/keepout/cable and factory process | EXT-04/05/06 | `GNSS_ARCHITECTURE.md`, `RF_CONNECTOR_SELECTION.md` | Approved RF layout constraints and mechanical fit |
| GNSS-03 | BLOCKED_EXTERNAL | 3 | Define cold-start/PPS/AIR4/coexistence tests and any pre-layout sample/fixture checks | GNSS-01/02 | test plan/report | Executable quantified plan plus available pre-layout evidence; final board results remain post-PCBA |
| DIG-01 | ACCEPTED | 4 | Freeze RP2040 reset, BOOTSEL, SWD, flash and oscillator circuit | none | `DIGITAL_SUPPORT_REVIEW.md` | Delivered 2026-09-22 (PR #144): pin-complete power/reset/BOOTSEL/SWD/oscillator specification from the RP2040 datasheet and the Raspberry Pi hardware design guide (RUN 10 k/100 n RC + host control, reference BOOTSEL R1/R2 arrangement, tag-connect-class SWD, 24 MHz SWD max); corner test plan declared; switched-domain flash-quiesce TBD retained for SYS-02 |
| DIG-02 | READY | 4 | Close microSD power, ESD, card detect, power-fail and enclosure access | MECH-02 for final fit | `DIGITAL_SUPPORT_REVIEW.md`, connector docs | Exact circuit, footprint/process and mechanical access |
| DIG-03 | ACCEPTED | 4 | Close USB, expansion, buttons, GPIO expander and all reset/off-state defaults | OWN-02, PWR-02 | connector/control docs, matrix | Delivered 2026-09-22 (PR #149): full TCA9535 16-port map (12 used, 4 spare) with per-net external safe-state resistors; active-low-release convention for every switched-domain enable (dead expander = domains OFF); expander VDD on always-on `3V3_MAIN` with back-power rationale recorded; ESP32/RP2040 recovery routes counted without the expander; electrical-matrix defaults row closed. Remaining: per-pin off-state proof against switched-rail removal is explicit gate-9/board-stage work; CHG_INT direct-vs-expander routing stays with PWR-03 |
| DIG-04 | READY | 4 | Create/review remaining support footprints from exact drawings | DIG-01/02/03 | `hardware/footprints/`, footprint reviews | Parse/export, automated geometry check and independent review |
| SNS-01 | BLOCKED_EXTERNAL | 5 | Obtain assembler process decisions for ICM/MMC/BMP/SHT40 | EXT-05 | sensor/footprint reviews | Written paste/mask/stencil disposition |
| SNS-02 | READY | 5/8 | Freeze orientation, magnetic, thermal, pressure-port, humidity-vent and keepout rules | OWN-05/08 for final environment | `SENSOR_ARCHITECTURE.md`, floorplan | Dimensioned placement constraints accepted |
| LORA-01 | READY | 6 | Obtain official native Semtech regional drawing/BOM; replace mirror/OCR evidence | none | `RF_ARCHITECTURE.md`, datasheet index | Blocked evidence note 2026-09-22: Semtech's public Salesforce CDN returns "content deleted" for all four SX1262DVK1 design-file packages (E428V03A/E449V01A); official-channel retrieval requires an owner/Semtech support request. Mirror AN1200.40 Rev 1.1 (MD5 985aa7de4bedd036de94bdb7f642e981) remains the verified evidence base |
| LORA-02 | BLOCKED_EXTERNAL | 6 | Finalize SX1262 DC-DC, oscillator, switch, matching, balun, filter, supply and U.FL application | LORA-01, EXT-04/06 | `RF_ARCHITECTURE.md` | Exact application reviewed against final stackup; no copied trace geometry |
| LORA-03 | BLOCKED_EXTERNAL | 6 | Define conducted TX/RX/harmonic/coexistence acceptance plan | OWN-03, LORA-02 | RF validation plan | Regional settings and calibrated test limits |
| ADSB-01 | ACCEPTED | 7 | Resolve MCP6566 base/R/U pin-map variant and pull-up/threshold network | OWN-09 for final threshold target | `ADSB_VALIDATION.md` | Delivered 2026-09-22 (PR #142): base `MCP6566T-E/OT` pin map frozen (Table 3-1, DS20002143G Rev G; R/U documented as non-drop-in alternates), pull-up 2.2 kohm with RC/sink/dissipation math, threshold divider formula recorded with the value explicitly blocked on OWN-09 |
| ADSB-02 | BLOCKED_EXTERNAL | 7 | Simulate BLB01/TA2003A/ADL5513 chain, bias, gain, noise, blockers and pulse response | EXT-04/06, OWN-09 | ADS-B architecture/validation | Reviewable RF files/results and testable circuit specification |
| ADSB-03 | BLOCKED_EXTERNAL | 7 | Define conducted injection/coupon and field acceptance procedure | ADSB-02 | ADS-B validation/test docs | Quantified fixtures, stimuli, limits and coexistence tests |
| AUD-01 | READY | 4/9 | Close T5838/TXU0202 pins, OE sequence, 1.8 V load, footprint and acoustic requirements | PWR-04, OWN-05/08 | `AUDIO_ARCHITECTURE.md` | Exact application and dimensioned port/gasket rules |

## Wave 3: convergence, mechanics and manufacturing

| ID | State | Gate | Task | Depends on | Closure evidence |
| --- | --- | ---: | --- | --- | --- |
| SYS-01 | ACCEPTED | 9 | Apply D22/P26: remove TUSB320LAI from I2C, allocate its GPIO mode, and compute the 100 kHz pull-ups/capacitance/cable limit and stuck-bus recovery | OWN-02 | Required: non-empty electrical window and declared cable/off-state rule. Delivered 2026-09-22 via PR #140: 100 kHz window non-empty to the 400 pF ceiling (Rp_min 967 ohm, preferred 2.2 k +/-1%), expansion-cable reserve <=150 pF declared, stuck-bus recovery assigned, TUSB320LAI GPIO-mode wiring pinned to SLLSEQ8D Rev D; per-device off-state review explicitly retained as remaining gate-9/board work |
| SYS-02 | BACKLOG | 9 | Complete rail/net/boot/off-state/interface matrix | Wave 2 circuits, SYS-01 | No OPEN electrical row affecting schematic connectivity |
| SYS-03 | BACKLOG | 9 | Define shared-SPI/UART/PDM/interrupt concurrency and bench stress cases | subsystem specs | Timing/resource contract with measurable limits |
| SYS-04 | BACKLOG | 9 | Perform independent full net-matrix review | SYS-02/03 | Reviewer finds no voltage/address/boot/back-power collision |
| MECH-01 | BLOCKED_EXTERNAL | 8 | Create exact component-envelope/tolerance inventory | EXT-01/02, Wave 2 exact parts | Dimensioned source table with drawing provenance |
| MECH-02 | BACKLOG | 8 | Freeze board outline, holes, display/FPC, cell removal, connectors and antenna/sensor keepouts | MECH-01, SNS-02 | Dimensioned floorplan suitable for KiCad board setup |
| MECH-03 | BLOCKED_EXTERNAL | 8 | Print and inspect a full fit dummy | MECH-02 | Signed fit review: access, retention, cables, FPC, wrapper safety and drop orientations |
| MFG-01 | BLOCKED_EXTERNAL | 8 | Freeze the supported stackup and official impedance geometries used for routing | EXT-04 | Factory-confirmed stack/solver output and tolerances; final order ticket is a post-layout control |
| MFG-02 | BLOCKED_EXTERNAL | 5/8 | Apply D27 no-coating policy and freeze DFM rules, cleaning exclusions, stencil and panel assumptions | OWN-08, EXT-05 | Factory/assembler checklist accepted |
| DFT-01 | READY | 9 | Define test access for SWD, BOOTSEL, UART, USB, every rail, B-/MID/B+, charger and RF conducted ports | subsystem circuits | Named nets, pad class, access side, fixture clearance and purpose |
| REG-01 | BLOCKED_OWNER | 10 | Convert OWN-03/05/06 into a regulatory evidence plan | owner inputs | Applicable ANATEL/ANAC/DECEA/UN38.3 actions and exclusions recorded |
| BOM-01 | BACKLOG | 1-9 | Replace all seven `MPN=TBD` rows or explicitly remove/DNP them | subsystem closure | Every fitted line has exact orderable MPN |
| BOM-02 | READY | 1-9 | Collect authorized suppliers, dated availability and assembly status | exact MPNs | Sourcing evidence without fabricated IDs/stock |
| BOM-03 | BACKLOG | all | Produce the pre-Astra engineering BOM with planned quantity per block | BOM-01/02 | Exact fitted MPN/package/planned quantity/source status; no unresolved substitution |

## Wave 4: freeze and handoff

| ID | State | Owner | Task | Depends on | Closure evidence |
| --- | --- | --- | --- | --- | --- |
| INT-01 | BACKLOG | Integrator | Merge accepted subsystem PRs in dependency order and resolve only documented conflicts | Waves 1-3 | Clean, reviewable integration; no silent decision changes |
| INT-02 | BACKLOG | Integrator | Reconcile requirements, decisions, open questions, status, evidence index and BOM | INT-01 | No cross-document status/MPN/pin/power contradiction |
| REV-01 | BACKLOG | Independent reviewers | Review power, RF, digital interfaces, footprints, mechanical and sourcing packages without editing them | INT-02 | Findings resolved or explicitly retained as post-Astra/non-layout risks |
| READY-01 | BACKLOG | Coordinator + owner | Audit every Astra entry gate and create the frozen input manifest | REV-01 | Every entry-gate row has objective evidence, reviewer and date |
| READY-02 | BACKLOG | Integrator | Mark `ASTRA_HANDOFF.md` and `ASTRA_EXECUTION_PROMPT.md` READY | READY-01 | No unresolved item can change connectivity, footprint, placement, routing or factory constraints |

## Pre-Astra versus post-Astra evidence

Do not create circular gates:

- **Before Astra:** exact fitted MPNs, planned quantities, reviewed circuits, footprints, net ownership, test-point requirements, outline, stackup and placement constraints.
- **Astra produces:** annotated schematic, actual reference-designator quantities, final netlist, PCB placement/routing, ERC/DRC and review plots.
- **After Astra, before manufacturing:** final orderable BOM/CPL, RF/PDN/layout review, mechanical 3D check, Gerber/drill inspection, programming/production-test procedure and explicit owner release.

Physical validation that requires the final PCB is a post-Astra manufacturing-release gate. Pre-Astra tests use samples, EVMs, coupons or fixtures only when they can validate an input decision without depending on the final layout.

## Readiness audit

The coordinator may declare the package ready only after checking every row above and every entry gate in [ASTRA_HANDOFF.md](ASTRA_HANDOFF.md). A search that finds no obvious issue is not proof. Each accepted task needs a source, revision/date, reviewer, validation result and remaining-risk statement.
