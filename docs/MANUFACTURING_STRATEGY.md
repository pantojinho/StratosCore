# Manufacturing strategy

Target four-layer PCB and automated assembly at JLCPCB or a comparable Chinese PCBA supplier, followed by shipment of assembled prototypes. The requested stack is conceptual: L1 components/signals, L2 ground, L3 power/signals, L4 signals/components. Manufacturer-approved dielectric/copper stack, board thickness, impedance tolerances and return paths must be established before layout.

The current priority is hardware readiness. Sol should close exact component evidence, compatibility, voltage/current domains, pin maps, application circuits, footprints, constraints and review gates. Astra should then execute the prepared work in KiCad: complete schematic entry, ERC, placement, routing and DRC. Manufacturing files are generated only after those reviews pass and the owner explicitly accepts the release.

## Sourcing

Use the exact locked MPNs and validated manufacturer package drawings. SHT40-AD1B-R2 is selected; generic names that still lack an ordering suffix remain explicitly TBD. Record supplier, region/currency, quantity, quotation date, stock, lead time, package/reel and assembly fees. No price, stock or LCSC ID is guessed. Multiple suppliers are preferable, but substitute MPNs require a decision proposal.

The [preliminary BOM](../bom/preliminary_bom.csv) is a functional planning list, not a purchasing or pick-and-place file. Before Astra, convert it into a frozen engineering parts baseline with every fitted/DNP item, passive value and rating, exact MPN/package, approved footprint, planned quantity range and sourcing status. Astra then creates the annotated reference-designator BOM and captured quantities. Reconcile that output into the final orderable BOM only after independent schematic review.

Validate PCBA handling of WROOM modules, small MEMS, microphone port, sensor contamination controls, SD socket and USB mechanical tabs. Do not blanket-clean, coat or apply paste over acoustic/pressure/humidity openings. Reserve board fiducials, tooling/panel features and test access after assembly-provider review. Ask the chosen manufacturer for current design/assembly rules rather than copying stale minimum dimensions.

## Release gates

1. Approved requirements, safe power topology and mechanical/RF floorplan; manufacturer datasheets and reuse terms recorded.
2. Schematic review: pinouts, voltage domains, boot/recovery, no unpowered backfeed, protection and complete BOM.
3. Placement/route review against approved stackup, RF references, sensor thermal/mechanical rules and enclosure fit.
4. ERC and DRC with tool version, settings, reports and signed exceptions; independent electrical/RF/power review.
5. Gerber/drill review, fabrication drawing, stackup/impedance note, orderable BOM, CPL consistency and rotations, assembly drawings, programming/test procedure, revision/hash and explicit release acceptance.

`manufacturing/gerbers`, `pickplace` and `assembly` are reserved areas, not ready-to-order deliverables. No manufacturing output is generated in this phase. See [test plan](../manufacturing/test/README.md).
