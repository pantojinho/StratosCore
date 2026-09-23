# Independent review of the Claude one-shot candidate

Review date: 2026-09-23. Reviewed commit: `e0efd1071a47e68cb20cd15a8e71ae4ae0c7cd4d` on `origin/main`. Scope: the [comparison candidate](../candidates/claude-oneshot-revA/README.md), its [issue register](../candidates/claude-oneshot-revA/docs/ISSUES.md), fresh KiCad CLI checks, and the two sensor land patterns below. This is an independent **triage**, not a complete pad-by-pad electrical, RF, mechanical, or safety sign-off.

## Disposition

The candidate is substantial and useful as an editable review target: a 12-page KiCad schematic, four-layer routed board, 3D assembly concept, BOM and generated reports. Keep it separate from the authoritative `hardware/` baseline. **Astra may start a review-only task now** to inspect it in KiCad and return a prioritized engineering issue list. The final implementation handoff in [ASTRA_HANDOFF.md](ASTRA_HANDOFF.md) remains **NOT READY**. No manufacturing output or battery-powered prototype is approved.

## Independent checks

KiCad 10.0.6 was run afresh against `candidates/claude-oneshot-revA/kicad/StratosCore_Claude.kicad_sch` and `.kicad_pcb` with all severities and schematic parity enabled. Temporary JSON reports were kept outside the repository. Results reproduce the candidate's recorded counts:

| Check | Fresh result | Meaning |
| --- | --- | --- |
| ERC | 1 error, 4 warnings | The BMP581 `INT` output is tied to a net with a power-output flag; review the pin disposition, rather than waiving the error by count. |
| DRC | 1 error, 579 warnings | The error is an ESP32 antenna-courtyard/GNSS U.FL overlap. Warnings include 3 dangling tracks, 2 hole-to-hole clearances, 2 footprint-library mismatches and many silkscreen items. Each non-cosmetic item still needs a disposition. |
| Unconnected items | 11 | Includes RF stubs and power/I2C/GND links; the board is not fully routed. |
| Schematic/PCB parity | 0 reported issues | This checks correspondence, not electrical correctness or manufacturability. |

The [MEMSIC MMC5983MA Rev A land pattern, p.20](https://www.memsic.com/Public/Uploads/uploadfile/files/20220119/MMC5983MADatasheetRevA.pdf) gives 2.550 mm centre-to-centre across opposite outer pads. The baseline footprint in `hardware/footprints/` places those centres at ±1.05 mm, causing adjacent corner pads to overlap by 0.075 mm. This is a **baseline blocker**; the candidate's ±1.275 mm correction is a plausible starting point, still requiring independent pin-1/orientation, mask/paste and assembler review.

The [Bosch BMP581 DS004-13, §8.2 Fig.32](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp581-ds004.pdf) gives 1.525 mm centre-to-centre and at least 0.2 mm between pads. The baseline footprint uses ±0.6 mm and leaves about 0.0375 mm at corner neighbours. This is another **baseline blocker**; the candidate's ±0.7625 mm correction must be checked against the drawing's bottom-view orientation and then reviewed for assembly. Earlier status saying these two baseline footprints passed an independent dimensional review was incorrect and must not be treated as release evidence.

## Follow-up baseline correction (2026-09-23)

The [correction record](FOOTPRINT_CORRECTIONS_2026_09_23.md) documents repaired sensor land centers in `hardware/footprints/`, a new exact-DCU candidate, and rejected unpublished support drafts. This does not alter or revalidate the embedded footprints in the Claude snapshot. The findings above describe reviewed commit `e0efd10`; use the follow-up for the current baseline candidate status.

## Priority engineering returns before final Astra execution

1. **Battery/power:** Resolve the exact removable 2S holder, charger/protection/power-path topology, load-while-charge behavior, cell mismatch/reverse/removal faults, protection FETs/fuse/NTCs and main on/off state. Obtain the qualified electrical/battery review required by O05 before committing or energizing the circuit. The candidate contains a placeholder and conflict, not a safe proven implementation.
2. **Display and mechanical:** Obtain controlled Orient C1 power/FPC drawing and labeled samples; prove the selected connectors, display/touch power and reset, backlight, flex path, holder tabs, mounting holes, access, clearances and printed fit. Its 3D display, cells and enclosure are concept envelopes, not tolerance-checked production models.
3. **Electrical/footprint corrections:** Independently review the corrected baseline MMC5983MA/BMP581 footprints (see follow-up); verify TXU0202 DCU and TPS259474L RPW packages and all fitted pads/pin-1/mask/paste. Decide the JST expansion header's vertical versus right-angle MPN, power switch, expansion CS, SX1262 reset, RP2040 RUN and touch reset. Reconcile GPIO and boot/off states without silently changing locked decisions.
4. **RF and stackup:** Complete exact SX1262 matching/filter/balun values and crystal; ADS-B detector/comparator thresholds and exposed-pad geometry; GNSS/LoRa/ADS-B antenna and return-path layouts; manufacturer-solver 50-ohm RF and 90-ohm USB geometry on a confirmed four-layer stack. The current autorouted paths are not controlled impedance or reviewed RF layouts.
5. **CAD and orderability:** Resolve every ERC/DRC/unconnected finding; independently inspect charger/buck/backlight loops, decoupling, thermals and test-point access; reconcile exact fitted BOM/quantities, five-unit PCBA plus display cost, assembly rules and the production package. A fresh error count alone cannot close these items.

## Review-only prompt for Astra

```text
Review StratosCore origin/main at the named commit or a newer explicitly identified commit. Read AGENTS.md, docs/DECISIONS.md, docs/PROJECT_STATUS.md, docs/CLAUDE_CANDIDATE_INDEPENDENT_REVIEW.md and candidates/claude-oneshot-revA/docs/ISSUES.md. Open candidates/claude-oneshot-revA/kicad/StratosCore_Claude.kicad_pro in KiCad 10. This candidate is for comparison, not the approved hardware baseline.

Independently inspect every schematic sheet, critical symbol/pin/net and exact package/footprint; reproduce ERC, DRC, unconnected and parity reports; review power, USB, RF and decoupling loop geometry; inspect display flex, 2S holder, enclosure, connector direction, antenna keepouts, sensor openings and 3D fit. Check the candidate's issue list rather than assuming it is complete. Cite exact manufacturer drawings and project references for each finding. Return a prioritized defect/gate table with file, reference/net/pad, evidence, proposed correction, owner of the decision, and whether a physical sample or qualified reviewer is required. Do not copy the candidate into hardware/, approve or energize the 2S circuit, claim a clean board, or generate manufacturing release files. Escalate any missing safety, RF, display, mechanical or product input; make no silent substitutions. The deliverable is a review report and a concrete path to a later READY handoff.
```
