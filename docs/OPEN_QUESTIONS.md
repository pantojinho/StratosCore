# Open questions and closure evidence

Unresolved issues do not authorize changing locked components. All are currently OPEN unless explicitly noted. Prioritize the numbered work sequence in [handoff](ASTRA_HANDOFF.md).

| ID | Decision/question | Owner role | Closure evidence / dependency |
| --- | --- | --- | --- |
| O01 | PARTIAL: exact C1 display drawing and connector? | Display/mechanical | Orient C1 selected for samples; obtain exact drawing, two samples, connector and power/readability measurements |
| O02 | CLOSED 2026-09-13: replace ATGM332D-5NR32 for balloon altitude | GNSS | Owner accepted MAX-M10S-00B; exact CAD, antenna and configuration move to O03/implementation review |
| O03 | GNSS antenna type, bias, connector and placement? | RF/mechanical | Link/noise budget, coexistence and both enclosure orientations |
| O04 | PARTIAL: ADS-B conducted performance? | RF | BLB01/TA2003A/ADL5513/MCP6566 candidate selected; simulate S-parameters and pass conducted pulse/blocker tests |
| O05 | OWNER ACCEPTED / REVIEW PENDING: two removable 21700 cells in 2S? | Power + reviewer | P14 accepted 2026-09-13; qualified electrical/battery review, exact 2S protection, holder verification and fault tests remain before freeze |
| O06 | PARTIAL: USB-C input, 2S charger, regulators and state estimation? | Power | BQ25887 is the first balanced-charger candidate; USB current detection, discharge protection, system power path, buck rails and thermal settings remain |
| O07 | Microphone MPN, I2S/PDM, port and optional DNP? | Audio/mechanical | Sample rate/clock budget, supply and acoustic tests |
| O08 | PARTIAL: exact PCB/enclosure dimensions? | Mechanical | 84 x 60 mm PCB, 31/37 mm enclosure candidates; print/fit dummies and tolerances remain |
| O09 | RF connector MPNs and GNSS/ADS-B connector styles? | RF/mechanical | U.FL retained for LoRa; cable loss, antenna access, mating and assembly drawings |
| O10 | PARTIAL: production stackup and impedance? | PCB/manufacturer | JLC2313 1.6 mm candidate documented; confirm order stack and field-solver geometries |
| O11 | PARTIAL: validate GPIO/bus map electrically? | Hardware/firmware | Resource allocation closes on paper; verify boot levels, exact peripherals and shared-SPI latency |
| O12 | PARTIAL: implement RP2040/ESP transport and timing sync? | Firmware | UART 921600 with RTS/CTS selected; define record framing and run overflow/timestamp tests |
| O13 | How will 12 h FLIGHT be achieved? | Power/product | Revised example yields 10.72 h for two 5 Ah cells; remove at least 0.207 W raw average and measure |
| O14 | Firmware framework and MeshCore mode/port/dependencies? | Firmware | Compatibility and transitive license audit; supported node roles explicitly scoped |
| O15 | Any reference code/circuit reuse? | Maintainer/license reviewer | File-level provenance and obligations; ADSBee GPL and avBadge uncertainty addressed |
| O16 | Mission temperature/pressure/dynamics and weather resistance? | Product/test | Intended operating envelope, sensor/cell ratings, pressure and thermal limits |
| O17 | Acquisition rates, SD capacity, audio format and allowed data loss? | Product/firmware | User workflow and throughput/power-loss tests; schema and rotation policy |
| O18 | ADS-B sensitivity, range, contact limits and stale time? | Product/RF/firmware | RF performance target and repeatable test plan, not anecdotal reception |
| O19 | PARTIAL: can ICM-42688-P be sourced and assigned a production CAD footprint? | Procurement/hardware | DS-000347 v1.9 and AN-000393 v2.4 release the pin/application entry; create and independently review the custom land/mask/stencil geometry, then recheck authorized stock/lead time |

The owner accepted P07 and the P14 2S direction on 2026-09-13, and rejected P08. P14 still requires a separate qualified electrical/battery reviewer before topology freeze, schematic commitment or prototype energizing.
