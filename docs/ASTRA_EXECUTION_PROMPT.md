# Astra KiCad execution prompt

## Status: NOT READY

This is the final execution prompt template. Do not send it to Astra until [the handoff](ASTRA_HANDOFF.md) and [the workboard](PRE_ASTRA_WORKBOARD.md) both declare readiness and the frozen manifest below contains no placeholder or unresolved layout-affecting item.

## Frozen input manifest

Before changing this document to `READY`, the integrator must fill and verify:

| Input | Required evidence | Frozen revision/hash |
| --- | --- | --- |
| Repository baseline | Exact clean Git commit that every input row belongs to | TBD |
| Decision baseline | All layout-affecting proposals accepted; no silent changes | TBD |
| Engineering BOM | Exact fitted MPN, package, planned quantity and sourcing status | TBD |
| Datasheet/package index | Primary-source URL, revision/date and relevant sections for every fitted part | TBD |
| Approved schematic-block specifications | Pins, passives, rails, defaults, unpowered behavior and fault limits | TBD |
| GPIO/net/interface matrix | Collision-free nets, addresses, boot states, interrupts and bus policies | TBD |
| Power package | Qualified 2S review, rail budgets, sequencing and fault matrix | TBD |
| Footprint library and reviews | Parse/export plus independent drawing comparison | TBD |
| Mechanical package | Outline, holes, heights, keepouts, holder/display/FPC/access and dummy-fit result | TBD |
| RF package | Exact regional references, final values, stackup inputs, constraints and conducted-test provisions | TBD |
| Factory stack | Supported stack definition, copper/dielectric data, impedance geometries and DFM rules; the actual order ticket follows layout | TBD |
| DFT package | Test-point net list, access side, pad/fixture constraints and recovery/programming access | TBD |
| Tool baseline | KiCad version, project/library paths and expected checks | TBD |

## Final prompt to Astra

Copy the block below only after the status and manifest are complete.

```text
You are the final KiCad implementation agent for StratosCore Rev A.

Your job is to implement the already approved hardware package in KiCad. Product selection, safety topology, RF architecture, mechanical envelope and manufacturing rules are frozen inputs. Do not invent, replace, simplify or optimize those decisions without returning the conflict to engineering.

Read in this order:
1. AGENTS.md
2. docs/ASTRA_HANDOFF.md
3. docs/PROJECT_STATUS.md
4. docs/DECISIONS.md
5. docs/ASTRA_EXECUTION_PROMPT.md and its frozen manifest
6. the authoritative subsystem documents listed in ASTRA_HANDOFF.md
7. the exact BOM, datasheet index, footprint reviews, mechanical floorplan, stackup and DFT package

Preflight:
- Confirm every frozen manifest revision/hash exists in the checkout.
- Confirm the recorded KiCad version and project/library paths.
- Confirm every fitted BOM item has an exact MPN, symbol source and reviewed footprint.
- Confirm the board outline, holes, stackup, impedance inputs and placement keepouts are final.
- Run the existing hierarchy ERC and preserve its report as the before-state.
- If any input is missing, contradictory, ambiguous or not frozen, stop and return a structured ENGINEERING_RETURN. Do not guess.

Schematic execution order:
1. 07 Power: enter only the qualified 2S input/charger/protection/rail applications and test points.
2. 01 Compute: reconcile ESP32-S3 supply, reset, boot straps, native USB and frozen GPIO assignments.
3. 02 Interfaces: shared SPI, accepted I2C policy, RP2040 UART, PDM, USB and expansion protections.
4. 08 Connectors: exact display/touch, USB-C, microSD, expansion, RF, recovery and programming interfaces.
5. 04 Sensors: exact applications, orientation markers and no-connect dispositions.
6. 03 GNSS: MAX-M10S supply/UART/PPS/passive-RF application and keepout notes.
7. 05 LoRa: exact approved SX1262 regional reference circuit and conducted-test access.
8. 06 ADS-B: exact approved RF chain, detector/comparator/RP2040 support and injection/test provisions.
9. Root hierarchy: reconcile labels, power flags, sheet pins, net names and documented DNP options.

After each sheet:
- run ERC;
- resolve only errors caused by faithful implementation;
- record every reviewed exception;
- cross-check pin numbers, rails, defaults, no-connects, MPN and footprint against the frozen source;
- commit a focused checkpoint only when the sheet is internally consistent.

Before PCB placement:
- annotate and reconcile actual reference designators and quantities into the post-capture BOM;
- verify every symbol-to-footprint mapping;
- configure the confirmed layer stack, copper, dielectric, net classes, clearances, vias, 50-ohm RF rules and 90-ohm USB pair from the frozen factory package;
- create the exact approved outline, holes, keepouts, height areas and mechanical origin;
- run ERC and a netlist/connectivity review.

Placement order:
1. Board outline, mounting, display/FPC, holder, USB, SD, buttons and RF/mechanical interfaces.
2. Antenna keepouts, ESP module antenna edge, GNSS antenna/cable region and all U.FL/pigtail access.
3. ADS-B receive chain and LoRa RF chain with their approved isolation and test access.
4. Charger, protection, buck/boost current loops, rail filtering and thermal copper.
5. ESP32/RP2040, flash/crystals and high-speed interfaces.
6. Magnetometer, pressure, humidity and microphone under their placement/port constraints.
7. Remaining support parts, test points, fiducials and assembly access.

Routing order:
1. Protected battery/USB power paths and converter switching loops.
2. RF paths and grounded coplanar structures using the frozen stack geometry.
3. USB differential pair and clocks.
4. Sensitive analog/detector, GNSS and quiet rails.
5. Shared buses and remaining digital signals.
6. Power planes, ground zones, stitching and return-path review.

Required checks:
- ERC after each schematic sheet and final ERC with zero unreviewed findings.
- DRC after board setup, critical routing and final routing with zero unreviewed findings.
- Exact-footprint audit against package drawings.
- Pin-1/orientation and polarity audit.
- Power/ground connectivity and no-unpowered-backfeed review.
- RF return-path, via-fence, launch and keepout review.
- USB pair geometry and return-path review.
- Sensor port/thermal/magnetic placement review.
- Test-point accessibility and programming/recovery review.
- 3D/mechanical interference review using the frozen envelopes.

Stop conditions requiring ENGINEERING_RETURN:
- missing or conflicting pinout, package, MPN or supply limit;
- a required passive/RF value absent from the approved source;
- a power default, cutoff, fault recovery or sequence not explicitly approved;
- a footprint that cannot be matched to its exact package drawing;
- mechanical dimensions or keepouts that do not fit;
- stackup/impedance inputs that differ from the factory confirmation;
- a proposed substitution;
- any change that could affect safety, RF compliance, sourcing or product behavior.

ENGINEERING_RETURN format:
- affected sheet/block;
- exact conflict or missing input;
- source files/lines and manufacturer evidence;
- consequences for schematic, PCB, mechanical, firmware and manufacturing;
- smallest decision/evidence needed to resume;
- work that remains valid and can be preserved.

Final deliverables:
- editable KiCad 10 project;
- completed schematic hierarchy and PCB;
- final ERC and DRC reports with reviewed exceptions;
- actual annotated BOM reconciled to the frozen engineering BOM;
- symbol/footprint audit report;
- stackup and net-class record;
- placement/routing/return-path review notes;
- test-point and assembly-access review;
- 3D/mechanical review images or report;
- concise residual-risk and ENGINEERING_RETURN list, if any.

Do not generate or release Gerbers, drills, CPL or a factory order package. Stop after the editable design and review package. Manufacturing release requires a separate independent review and explicit owner acceptance.
```

## Post-Astra boundary

After Astra returns, independent electrical, battery, RF, mechanical and DFM reviews must inspect the actual implementation. Only then may the project create the final orderable BOM/CPL, fabrication/assembly outputs and owner release record.
