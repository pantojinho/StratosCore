# Astra KiCad execution handoff

## Status: NOT READY

Do not invoke Astra for StratosCore CAD yet. [Project status](PROJECT_STATUS.md) owns the current Sol/external work queue. This file is reserved for the final KiCad execution package and changes to **READY** only after every entry gate below has objective closure evidence.

## Entry gates

- [ ] Every fitted component has an exact orderable MPN, current manufacturer datasheet and package drawing.
- [ ] Every schematic block has a reviewed application circuit, voltage/current budget, defaults and unpowered-state behavior.
- [ ] The display has the reviewed C1 controlled drawing, independently verified connector footprints, accepted 1.8 V translation/backlight circuit and sample evidence.
- [ ] MAX-M10S-00B supply, backup, UART/timepulse, antenna and layout decisions are complete.
- [ ] The complete two-cell 2S charger, common protection, power path and regulator plan has written qualified electrical/battery approval.
- [ ] Sensor pin maps, physical footprints, orientation, vent, thermal and magnetic placement rules are independently checked.
- [ ] SX1262 and ADS-B RF chains have exact suffixes, reference revisions, stackup inputs, placement constraints and conducted-test provisions.
- [ ] ESP32/RP2040/display/SD/radio/GNSS/audio/expansion interfaces have a collision-free net and GPIO map, including boot states and test points.
- [ ] Exact USB-C, microSD, microphone, expansion and RF connector MPNs and footprints are reviewed.
- [ ] PCB outline, mounting, enclosure, battery holder, display/FPC, access, antenna keepouts and four-layer production stack are confirmed.
- [ ] Preliminary BOM has been converted to an orderable schematic BOM with quantities and approved sourcing status.
- [ ] `PROJECT_STATUS.md` and `OPEN_QUESTIONS.md` contain no unresolved item that affects schematic connectivity, footprint choice, placement or routing.

## Authoritative inputs when READY

| Input | Purpose |
| --- | --- |
| [Decision register](DECISIONS.md) | Locked baseline and accepted proposals |
| [Orderable BOM](../bom/preliminary_bom.csv) | Replace this preliminary path with the final orderable BOM before READY |
| [Interface/GPIO map](INTERFACE_GPIO_MAP.md) | Nets, buses, boot states and ownership |
| [Datasheet index](../hardware/datasheets/README.md) | Exact primary-source revisions |
| [Power review](POWER_ARCHITECTURE_REVIEW.md) | Reviewed 2S application and fault limits |
| [RF architecture](RF_ARCHITECTURE.md) | RF references, stackup and placement constraints |
| [Mechanical/RF floorplan](MECHANICAL_RF_FLOORPLAN.md) | Board outline, keepouts and enclosure interfaces |
| [Manufacturing strategy](MANUFACTURING_STRATEGY.md) | Factory rules and release outputs |

## Astra execution checklist

1. Open the repository KiCad 10 project and verify the tool/library versions recorded in the package.
2. Create or import only the reviewed project symbols and footprints. Compare every custom pad, courtyard, pin number and orientation with its exact package drawing.
3. Capture the approved schematic sheet by sheet. Do not select substitute parts, infer missing connections or resolve product decisions inside KiCad.
4. Run ERC after every sheet, restore temporary one-endpoint diagnostics as nets become complete, and record every reviewed exception.
5. Annotate, assign verified footprints, generate the orderable BOM and reconcile every reference with the source package.
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

The Astra task is complete only with an editable KiCad project, zero-unreviewed ERC/DRC findings, exact-footprint audit, orderable BOM, placement/routing review notes, stackup/net-class record, assembly/test-point review and a concise list of residual risks. Gerbers, drill, CPL and assembly packages remain unreleased until the independent review and owner release acceptance in [manufacturing strategy](MANUFACTURING_STRATEGY.md).
