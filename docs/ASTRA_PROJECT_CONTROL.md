# Astra project control and agent handover

Effective: **2026-09-24 — owner accepted; Astra leadership ACTIVE**. Integration base: `912894b7dc1f4f4c764267f3bca375b8237b2e48` (`origin/main` when this handover was reviewed).

## Responsibility and authority

The owner has assigned Astra full technical leadership of StratosCore: planning, engineering closure, KiCad candidate refinement, review of contributions, integration, documentation and release preparation. Astra has already assumed this role; it is not waiting for a final CAD handoff. This supersedes the previous Sol-led preparation / Astra-only-final-CAD division in D20.

Claude, Hermes, Sol and other AI agents are delegated workers. They execute bounded tasks assigned by Astra and return evidence for review. They do not independently direct the project, change its baseline, accept their own work or publish to `main`. Astra acts as coordinator and integrator under the [swarm protocol](SWARM_PROTOCOL.md), retains responsibility for the complete result and may perform work directly. The owner retains authority over locked product decisions and manufacturing acceptance; qualified reviewers retain their engineering acceptance responsibilities, including O05 battery safety.

Each assignment must identify its task ID, current base SHA, objective, allowed files, dependencies, primary sources, required checks and acceptance evidence. Workers use isolated branches and reviewable PRs. Astra reconciles contributions and alone updates shared control records and publishes reviewed integration to `main`. A reported result is not automatically an accepted or independently verified result.

## Handover received from other agents

The owner supplied the summary titled "StratosCore — fechamento candidato Rev A (KiCad GUI + cotação)" on 2026-09-24. This document incorporates its operational content without importing local paths or personal logs. Repository evidence is available in the [candidate README](../candidates/claude-oneshot-revA/README.md), [GND stitch record](../candidates/claude-oneshot-revA/docs/GND_STITCH_2026_09_23.md), [candidate decision record](../candidates/claude-oneshot-revA/docs/OWNER_DECISIONS_2026_09_24.md) and [review notes](../candidates/claude-oneshot-revA/docs/review_notes/).

The following preserves the **received evidence at the integration base**. Astra subsequently ran independent checks and corrected discrepancies in [the September 24 agent review](ASTRA_AGENT_REVIEW_2026_09_24.md); that review supplies the current validated report counts.

| Item | Reported state | Acceptance boundary |
| --- | --- | --- |
| Candidate | Claude's 12-sheet schematic, routed PCB and conceptual enclosure, subsequently refined by agents | Remains outside the `hardware/` baseline and unreleased |
| GND continuity | Hermes reports U2 USB ESD, U24.2 translator and U3.8 eFuse connected to the ground plane | Recheck actual connectivity and return paths after further CAD edits |
| U7 buck footprint | RGT0016C correction reported, exposed pad 1.68 mm | Exact drawing, thermal and routing review remain required |
| DRC/connectivity | 2 unconnected LoRa items, 0 shorts, 0 schematic-parity findings; 10 U3 clearance findings, 199 mask-bridge findings, 117 silkscreen findings and 1 dangling track | Counts are a report snapshot, not a pass. The candidate notes report truncation at 199 per type; mask findings are a lower bound |
| Digital choices | A5: GPIO8 `EXP_CS_N`; A6: P10 `SX_NRESET`; A7: P14 `RP_RUN`, sink-only; A8: P07 `TOUCH_RST_N` with 10 kohm pull-down | A5/A8 CAD edits remain pending. A6/A7 nets already exist; sink-only behavior and interface checks remain open. A7 pull-up rail remains unresolved |
| Mask choice | D-MASK selects S1 per-pad NSMD treatment for the candidate | Not yet implemented or independently accepted against exact package and assembler requirements |
| Cost | Previous estimate reports at least BRL 504/unit | Historical snapshot requiring fresh comparable quotes. Root D24 remains BRL 200/unit with its existing scope; no budget revision or purchase is accepted here |

Two discrepancies need explicit handling. The supplied summary calls U2 `TPD1E0B04`, whereas the candidate identifies USB ESD U2 as `TPD4E05U06`; confirm the full MPN and reference before any placement edit. Descriptions of the 10 U3 clearance findings as "cosmetic" or accepted for a prototype do not close electrical clearance defects or authorize fabrication. Permission to continue candidate refinement is distinct from accepting those defects.

## Astra-owned next work

These are inherited tasks, not completions claimed by this documentation change. Astra assigns execution and reviews the result; the [engineering workboard](PRE_ASTRA_WORKBOARD.md) retains the existing subsystem task IDs and dependencies.

| ID | Next action | Required evidence / dependency |
| --- | --- | --- |
| T1 | Review the USB corner and prepare 2–3 placement options before moving parts | Reconcile U2 identity; show connector/ESD/eFuse paths and obtain the requested owner choice before moving the proposed arrangement |
| T2 | Review U7 buck routing, current loops and thermal vias | Exact RGT0016C drawing and TI application evidence; preserve ground connections and record thermal/routing checks |
| T3 | Resolve the 10 reported U3 clearance defects | Inspect actual nets and geometry; apply supported local corrections and rerun DRC without weakening global rules |
| T4 | Evaluate and implement the candidate S1 mask choice when supported | Exact sensor land/mask requirements, feasible assembler process and per-pad evidence; fresh DRC and independent review |
| T5 | Implement and check A5–A8 candidate digital decisions | Resolve A7 pull-up rail and off-state behavior first; check boot states, collisions, schematic/PCB parity and ERC |
| T6 | Inspect the complete candidate in KiCad GUI and 3D | Review every sheet and board region; document proposals before edits dependent on unresolved choices |
| T7 | Obtain current five-unit PCBA/display quotes and reconcile D24 | Dated supplier/stock/MPN evidence, explicit cost scope and exclusions; cost gap stays visible, no order |
| T8 | Regenerate review evidence after authorized CAD changes | Versioned ERC/DRC, net/pad reconciliation, renders, STEP and review-only BOM/positions; update issues and report unresolved findings |

The two LoRa connections remain gated by exact RF topology, values and stackup evidence; ordinary routing cannot substitute for RF closure. Battery/protection/charger O05, display/sample fit, RF performance, factory confirmation and independent reviews remain open as recorded in [project status](PROJECT_STATUS.md).

## Execution and release boundaries

Astra leadership is **ACTIVE**. The [final KiCad handoff](ASTRA_HANDOFF.md) and [final execution template](ASTRA_EXECUTION_PROMPT.md) remain **NOT READY** for frozen-baseline implementation. The [candidate refinement prompt](ASTRA_CANDIDATE_REFINEMENT_PROMPT.md) governs bounded CAD work now. `ENGINEERING_RETURN` means Astra owns resolution or delegation of the missing evidence and pauses only dependent work; it does not transfer project leadership away from Astra.

This handover changes responsibility and records the work queue. It does not change components, the BOM, locked hardware requirements, accepted safety gates or CAD. No Gerbers, drill/CPL, orderable production package, battery energizing, procurement or manufacturing release is authorized by it.
