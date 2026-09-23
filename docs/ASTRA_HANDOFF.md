# Astra KiCad execution handoff

## Status: NOT READY

Do not invoke Astra for StratosCore CAD yet. [Project status](PROJECT_STATUS.md) owns the current Sol/external work queue. This file is reserved for the final KiCad execution package and changes to **READY** only after every entry gate below has objective closure evidence.

The owner may invoke Astra **now to review and refine provable issues in the Claude comparison candidate** using the [candidate refinement prompt](ASTRA_CANDIDATE_REFINEMENT_PROMPT.md). This is candidate work; it does not grant final implementation or manufacturing readiness.

## Entry gates

- [ ] Every fitted component has an exact orderable MPN, current manufacturer datasheet and package drawing.
- [ ] Every schematic block has a reviewed application circuit, voltage/current budget, defaults and unpowered-state behavior.
- [ ] The display has the reviewed C1 controlled drawing, independently verified connector footprints, accepted 1.8 V translation/backlight circuit and sample evidence.
- [ ] MAX-M10S-00B supply, backup, UART/timepulse, antenna and layout decisions are complete.
- [ ] The complete two-cell 2S charger, common protection, power path and regulator plan has written qualified electrical/battery approval.
- [ ] Sensor pin maps, physical footprints, orientation, vent, thermal and magnetic placement rules are independently checked, including a new review of the [2026-09-23 corrected sensor/DCU candidates](FOOTPRINT_CORRECTIONS_2026_09_23.md); historical pass claims are superseded. Keep locked BMP581 as an indicative backup per revised D29; P27 is rejected. Define invalid/out-of-range handling and the realistic ~10,000 ft test case without claiming 30,000 ft qualification.
- [ ] SX1262 and ADS-B RF chains have exact suffixes, reference revisions, stackup inputs, placement constraints and conducted-test provisions.
- [ ] ESP32/RP2040/display/SD/radio/GNSS/audio/expansion interfaces have a collision-free net and GPIO map, including boot states and the pre-placement DFT coverage, pad and access constraints in O28. Astra will assign references and coordinates; access is reviewed again after placement.
- [ ] Exact USB-C, microSD, microphone, expansion and RF connector MPNs and footprints are reviewed.
- [ ] PCB outline, mounting, enclosure, battery holder, display/FPC, required sensor/acoustic openings, access, antenna keepouts and four-layer production stack are confirmed under D27's no-coating/no-ingress-qualification baseline, including manufacturer-solver geometry for controlled impedances. The final order ticket, coupon and TDR remain post-layout controls.
- [ ] The preliminary BOM has been converted to an engineering parts baseline with exact fitted/DNP parts, passives, packages, approved footprints, planned quantities and sourcing status (O27). Astra will create the annotated BOM and final captured quantities.
- [ ] `PROJECT_STATUS.md` and `OPEN_QUESTIONS.md` contain no unresolved item that affects schematic connectivity, footprint choice, placement or routing. Apply accepted owner constraints D21-D27 and close the remaining mission, ADS-B, regulatory, cost-boundary and factory-provisioning inputs O16/O18/O21-O23/O25, plus the engineering-baseline and pre-placement DFT items O27/O28.

## Authoritative inputs when READY

| Input | Purpose |
| --- | --- |
| [Decision register](DECISIONS.md) | Locked baseline and accepted proposals |
| [Engineering parts baseline](../bom/preliminary_bom.csv) | Replace the planning content with the frozen pre-Astra baseline before READY; annotated references and final quantities follow capture |
| [Interface/GPIO map](INTERFACE_GPIO_MAP.md) and [electrical matrix](ELECTRICAL_COMPATIBILITY_MATRIX.md) | Nets, buses, voltage domains, boot/off states and ownership |
| [Datasheet index](../hardware/datasheets/README.md) | Exact primary-source revisions |
| [Power review](POWER_ARCHITECTURE_REVIEW.md) and [rail plan](POWER_RAIL_PLAN.md) | Reviewed 2S application, fault limits, rails and sequencing |
| [Display](DISPLAY_REQUIREMENTS.md), [GNSS](GNSS_ARCHITECTURE.md), [audio](AUDIO_ARCHITECTURE.md) and [connector package](CONNECTOR_ARCHITECTURE.md) | Exact accepted subsystem circuits, parts and implementation constraints |
| [RF architecture](RF_ARCHITECTURE.md) and [RF connector selection](RF_CONNECTOR_SELECTION.md) | RF references, stackup, interconnect and placement constraints |
| [Mechanical/RF floorplan](MECHANICAL_RF_FLOORPLAN.md) | Board outline, keepouts and enclosure interfaces |
| [BMP581 validation plan](BMP581_VALIDATION_PLAN.md) | Indicative backup data/validity contract and realistic pressure test plan; no 30,000 ft performance claim |
| [Audio domain review](AUDIO_DOMAIN_REVIEW.md) | Proposed separate 1.8 V audio switch branch and the unresolved exact application review |
| [Concurrency contract](CONCURRENCY_CONTRACT.md) | Shared-bus/UART/PDM resource limits and remaining numerical timing gates |
| [BOM gap audit](BOM_BASELINE_GAP_AUDIT.md) | Exact-part, quantity, footprint, sourcing and fit/DNP gaps to close before manifest freeze |
| [Manufacturing strategy](MANUFACTURING_STRATEGY.md) | Factory rules and release outputs |
| [CAD tooling review](CAD_TOOLING_REVIEW.md) | Optional KiCad automation, verification limits and reproducibility rules |

## Astra execution checklist

1. Open the repository KiCad 10 project and verify the tool/library versions recorded in the package.
2. Create or import only the reviewed project symbols and footprints. Compare every custom pad, courtyard, pin number and orientation with its exact package drawing.
3. Capture the approved schematic sheet by sheet. Do not select substitute parts, infer missing connections or resolve product decisions inside KiCad.
4. Run ERC after every sheet, restore temporary one-endpoint diagnostics as nets become complete, and record every reviewed exception.
5. Annotate, assign verified footprints, generate the annotated BOM and reconcile every reference and captured quantity with the frozen engineering parts baseline.
6. Create the approved board outline and production stack; configure net classes, differential pairs, impedance targets, clearances and via rules from current manufacturer data.
7. Place mechanical interfaces and keepouts first, then RF receive chains, antennas, power conversion, compute, sensors and remaining digital circuits under the approved floorplan constraints.
8. Route power/current loops, USB, clocks/high-speed signals and RF paths according to their reviewed references; maintain return paths and isolation constraints.
9. Run DRC and connectivity review, inspect zones and return paths, and record all exceptions. Generate review plots and 3D/mechanical checks.
10. Stop before manufacturing release. Return the completed KiCad project, ERC/DRC reports, updated BOM and an issue list for independent schematic/PCB review.

## Astra may decide

Astra may make ordinary CAD choices within the approved constraints: symbol arrangement, reference placement, via location, tuning of noncritical trace geometry, zone cleanup and routing order. It must record choices that materially affect EMI, thermals, assembly or test access.

## Astra must return to engineering

Return any missing or conflicting pinout, footprint, supply limit, boot state, protection behavior, RF value, impedance, mechanical dimension or part substitution. Do not guess and do not weaken a review gate to finish the board.

## Exit package

The Astra task is complete only with an editable KiCad project, zero-unreviewed ERC/DRC findings, exact-footprint audit, annotated BOM reconciled to the engineering baseline, placement/routing review notes, stackup/net-class record, assembly/test-point review and a concise list of residual risks. The final orderable BOM, Gerbers, drill, CPL and assembly packages remain unreleased until the independent review and owner release acceptance in [manufacturing strategy](MANUFACTURING_STRATEGY.md).
