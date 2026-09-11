# Open questions and closure evidence

Unresolved issues do not authorize changing locked components. All are currently OPEN unless explicitly noted. Prioritize the numbered work sequence in [handoff](ASTRA_HANDOFF.md).

| ID | Decision/question | Owner role | Closure evidence / dependency |
| --- | --- | --- | --- |
| O01 | Exact 2.8-inch LCD, touch controller and connector? | Display/mechanical | Datasheets, sample, dated cost/stock, FPC drawing, power/readability and GPIO budget |
| O02 | Does exact ATGM332D-5NR32 meet Galileo and update-rate needs? | GNSS | Vendor variant/command confirmation and sample tests; current page does not establish Galileo |
| O03 | GNSS antenna type, bias, connector and placement? | RF/mechanical | Link/noise budget, coexistence and both enclosure orientations |
| O04 | ADS-B LNA/filter/detector/comparator and gain plan? | RF | Manufacturer references, pulse/blocker/noise analysis, conducted prototype results |
| O05 | Safe one/two-cell topology and cell/holder model? | Power + owner/reviewer | Fault review, charge/reversal/mismatch/removal tests; no freeze yet |
| O06 | USB-C PMIC, input policy, gauge and regulators? | Power | Load/charge envelope, source capability, thermal/EMI, state-of-charge strategy |
| O07 | Microphone MPN, I2S/PDM, port and optional DNP? | Audio/mechanical | Sample rate/clock budget, supply and acoustic tests |
| O08 | Exact PCB/enclosure dimensions and thickness? | Mechanical | Full one/two-cell tolerance stack, print/fit tests |
| O09 | RF connector MPNs and GNSS/ADS-B connector styles? | RF/mechanical | U.FL retained for LoRa; cable loss, antenna access, mating and assembly drawings |
| O10 | Final four-layer stackup and impedance? | PCB/manufacturer | Approved dielectric/copper values, impedance geometry and return paths |
| O11 | GPIO/bus/peripheral map with all features simultaneous? | Hardware/firmware | USB/PSRAM/straps reserved; UART count, SPI arbitration, I2C addresses, interrupts |
| O12 | RP2040/ESP transport, decode ownership and timing sync? | Firmware | Versioned protocol, throughput/overflow tests, timestamp uncertainty |
| O13 | How will 12 h FLIGHT be achieved? | Power/product | Measured budget; current example yields 11.15 h for two 5 Ah cells |
| O14 | Firmware framework and MeshCore mode/port/dependencies? | Firmware | Compatibility and transitive license audit; supported node roles explicitly scoped |
| O15 | Any reference code/circuit reuse? | Maintainer/license reviewer | File-level provenance and obligations; ADSBee GPL and avBadge uncertainty addressed |
| O16 | Mission temperature/pressure/dynamics and weather resistance? | Product/test | Intended operating envelope, sensor/cell ratings, pressure and thermal limits |
| O17 | Acquisition rates, SD capacity, audio format and allowed data loss? | Product/firmware | User workflow and throughput/power-loss tests; schema and rotation policy |
| O18 | ADS-B sensitivity, range, contact limits and stale time? | Product/RF/firmware | RF performance target and repeatable test plan, not anecdotal reception |

No approval request is pending for creating this foundation. Battery and design-freeze reviews belong to subsequent engineering tasks.
