# Engineering documentation index

Start with [project status](PROJECT_STATUS.md). It is the concise source for what is complete, what remains and who owns each next action. [Decisions](DECISIONS.md) is the change-controlled baseline. [Astra handoff](ASTRA_HANDOFF.md) is reserved for final KiCad execution and must not be used while it says **NOT READY**.

## Control and current status

| Document | Purpose |
| --- | --- |
| [Footprint corrections](FOOTPRINT_CORRECTIONS_2026_09_23.md) | Corrected sensor/DCU geometry, rejected local drafts and reproducible clearance checks |
| [Claude candidate independent review](CLAUDE_CANDIDATE_INDEPENDENT_REVIEW.md) | Fresh KiCad triage, original findings and correction context |
| [Astra candidate refinement prompt](ASTRA_CANDIDATE_REFINEMENT_PROMPT.md) | Start Astra on the Claude PCB candidate now; fix evidenced issues and return unresolved engineering gates |
| [Project status](PROJECT_STATUS.md) | Current phase, completed work, remaining gates and ordered next work |
| [Pre-Astra workboard](PRE_ASTRA_WORKBOARD.md) | Task IDs, dependencies, owners, parallel waves and objective closure evidence |
| [Swarm protocol](SWARM_PROTOCOL.md) | Multi-agent branches, file ownership, status, review, integration and master prompt |
| [Decision register](DECISIONS.md) | Locked requirements, accepted/rejected proposals and owner decisions |
| [Open questions](OPEN_QUESTIONS.md) | Closure evidence for every unresolved engineering item |
| [Historical 30,000 ft barometer comparison](BAROMETER_30K_PROPOSAL.md) | Rejected P27 replacement and dated alternative comparison; BMP581 remains locked |
| [BMP581 validation plan](BMP581_VALIDATION_PLAN.md) | Indicative pressure/vario data contract and pre-/post-PCBA test boundary |
| [BOM baseline gap audit](BOM_BASELINE_GAP_AUDIT.md) | Exact MPN, quantity, footprint, fit/DNP and sourcing gaps before Astra |
| [Product requirements](PRODUCT_REQUIREMENTS.md) | Verifiable Rev A behavior and operating profiles |
| [Astra final handoff](ASTRA_HANDOFF.md) | Final KiCad execution checklist; currently gated |
| [Astra execution prompt](ASTRA_EXECUTION_PROMPT.md) | Frozen-manifest template and final KiCad execution prompt; currently NOT READY |
| [CAD tooling review](CAD_TOOLING_REVIEW.md) | Optional Hermes/KiCad automation, verification limits and reproducibility |
| [Validation record](FOUNDATION_CHECKS.md) | Checks already run and their limited meaning |
| [Readiness audit log](AUDIT_LOG.md) | Audit-loop baseline, rounds, active blockers and the vigil procedure |

## System and interfaces

| Document | Purpose |
| --- | --- |
| [System architecture](SYSTEM_ARCHITECTURE.md) | MCU ownership, buses, timing, storage and power domains |
| [Block diagram](BLOCK_DIAGRAM.md) | Visual functional interconnect |
| [GPIO and interface map](INTERFACE_GPIO_MAP.md) | ESP32 allocation, I2C addresses and shared-SPI contract |
| [Electrical compatibility matrix](ELECTRICAL_COMPATIBILITY_MATRIX.md) | Rail, voltage, address, boot-state and back-power closure map |
| [I2C bus budget](I2C_BUS_BUDGET.md) | Shared-bus capacitance, pull-up window and per-device transcription worksheet |
| [Concurrency contract](CONCURRENCY_CONTRACT.md) | Shared SPI, UART, PDM and interrupt resource arithmetic and remaining timing gates |
| [Audio-domain review](AUDIO_DOMAIN_REVIEW.md) | Preferred separate switched-audio rail and exact application work still needed |
| [Power input evidence](POWER_INPUT_EVIDENCE.md) | USB eFuse and 2S charger datasheet facts feeding O05/O06 |
| [Expansion interface](EXPANSION_INTERFACE.md) | External I2C/SPI/UART/GPIO requirements |

## Hardware subsystems

| Area | Primary documents |
| --- | --- |
| Components and sourcing | [Component evidence](COMPONENT_EVIDENCE.md), [datasheet index](../hardware/datasheets/README.md), [preliminary BOM](../bom/preliminary_bom.csv) |
| Digital support | [RP2040 flash/clock and microSD review](DIGITAL_SUPPORT_REVIEW.md), [digital footprint review](FOOTPRINT_REVIEWS_DIGITAL.md), [buttons and slow-control I/O](CONTROL_IO_REVIEW.md) |
| Display | [Display requirements](DISPLAY_REQUIREMENTS.md) |
| GNSS | [GNSS architecture](GNSS_ARCHITECTURE.md) |
| Sensors and GNSS CAD | [Sensor architecture](SENSOR_ARCHITECTURE.md), [sensor/GNSS/RF footprint review](FOOTPRINT_REVIEWS_SENSORS_GNSS.md) |
| Audio | [Digital microphone architecture](AUDIO_ARCHITECTURE.md) |
| Power and wired connectors | [Accepted options](POWER_ARCHITECTURE_OPTIONS.md), [2S review](POWER_ARCHITECTURE_REVIEW.md), [rail plan](POWER_RAIL_PLAN.md), [USB-C/expansion connectors](CONNECTOR_ARCHITECTURE.md), [power budget](POWER_BUDGET.md) |
| RF | [RF architecture](RF_ARCHITECTURE.md), [RF connector selection](RF_CONNECTOR_SELECTION.md), [ADS-B architecture](ADSB_ARCHITECTURE.md), [ADS-B validation](ADSB_VALIDATION.md) |
| PCB and mechanics | [Stackup](PCB_STACKUP.md), [mechanical requirements](MECHANICAL_REQUIREMENTS.md), [mechanical/RF floorplan](MECHANICAL_RF_FLOORPLAN.md) |

## Production

| Document | Purpose |
| --- | --- |
| [Manufacturing strategy](MANUFACTURING_STRATEGY.md) | Chinese PCBA target, sourcing rules and release gates |
| [Production-test plan](../manufacturing/test/README.md) | Qualification and factory screening plan |
| [KiCad workspace](../hardware/kicad/README.md) | Current hierarchy, holds and ERC command |
| [Reuse register](../references/REUSE_REGISTER.md) | Source, license and modification tracking |

The documents are separated by engineering responsibility so evidence is reviewable without turning the root README into a design specification. Do not duplicate changing pinouts, thresholds or part status in several summaries; link to the subsystem source and update [project status](PROJECT_STATUS.md).
