# Astra prompt: review and refine the Claude PCB candidate

**Use now for bounded candidate review/refinement under Astra's active project leadership.** Read [project control and the latest handover](ASTRA_PROJECT_CONTROL.md) for delegated roles, the received `912894b` snapshot and inherited T1–T8 tasks. Historical counts below describe the initial review packet; current reports and later accepted corrections take precedence. This prompt does not declare the candidate or final Astra handoff ready for manufacture. Work only in `candidates/claude-oneshot-revA/`; keep `hardware/` as the reviewed architecture baseline unless the project owner explicitly accepts a documented decision change. Do not create manufacturing outputs or energize the 2S design.

Before opening KiCad, fetch the latest `origin/main`, record the exact commit, and confirm the working tree is clean. The review packet was prepared on 2026-09-23 at commit `9e909f3`; use later current-main corrections as authoritative. Read `AGENTS.md`, `docs/DECISIONS.md`, `docs/PROJECT_STATUS.md`, `docs/FOOTPRINT_CORRECTIONS_2026_09_23.md`, `docs/CLAUDE_CANDIDATE_INDEPENDENT_REVIEW.md`, and `candidates/claude-oneshot-revA/docs/ISSUES.md`.

```text
You are reviewing and refining the Claude one-shot KiCad candidate for StratosCore Rev A. The owner wants you to use the existing schematic, routed PCB and enclosure model to correct provable errors and improve the candidate in KiCad.

The candidate is at candidates/claude-oneshot-revA/kicad/StratosCore_Claude.kicad_pro and its associated schematic, board and SC libraries. It is a comparison candidate, not the released project baseline. Work only inside candidates/claude-oneshot-revA/. Do not copy it into hardware/ or silently change any locked choice. The hardware baseline contains manufacturer-drawing corrections that may postdate the candidate's embedded footprints; compare the exact copper, mask, paste, pad numbers and orientation, and apply an evidenced correction inside the candidate where appropriate.

Read first:
1. AGENTS.md
2. docs/DECISIONS.md and docs/PROJECT_STATUS.md
3. docs/FOOTPRINT_CORRECTIONS_2026_09_23.md
4. docs/CLAUDE_CANDIDATE_INDEPENDENT_REVIEW.md
5. candidates/claude-oneshot-revA/README.md and docs/ISSUES.md
6. The exact manufacturer datasheet/package drawing for each item you touch.

Preflight:
- Fetch latest origin/main and state its exact commit; the original review packet is based on 9e909f3 but later accepted commits supersede it.
- Open the candidate in KiCad 10. Confirm file paths, libraries, layer stack, board outline and current generated reports before editing.
- Re-run ERC, DRC with schematic parity, unconnected-item and BOM checks. Preserve before reports, commands and KiCad version in the candidate review record.
- Inspect the complete schematic in KiCad, not just netlist text or rendered images. Trace each reported board item to its schematic pin and exact part drawing.

Fix and refine only what is supported by the existing approved requirements and primary-source evidence:
- Resolve the schematic/board DRC error by changing placement/outline as needed to satisfy the ESP32 module's antenna requirements and actual adjacent parts. Do not shrink or remove the manufacturer's antenna keepout to silence courtyard overlap.
- Audit the BMP581 INT connection and all four candidate sensor footprints. Use the revised baseline drawings/geometry described in the correction record; verify pad numbering against the manufacturer's top view. Do not treat zero parity findings as electrical validation.
- Inspect all 11 reported unconnected items. Complete ordinary power, ground and I2C connections only when the reviewed schematic and source pin maps determine the intended net. Preserve a structured blocker for unresolved SX1262 matching-network/RF connections; do not guess values, route stubs as if complete, or claim RF readiness.
- Review the candidate's TXU0202 DCU and TPS259474L RPW land patterns against the exact TI package drawings. Correct pad polygons, numbering, paste/mask, fab outline and courtyard only when the drawing supports the change. Do not copy a rejected generic DGS/RPU footprint or the rejected local straight-pad RPW draft.
- Refine silkscreen, test-point access, ordinary routing, clearances and 3D placement when this does not alter unknown circuit behavior. Inspect the charger/buck/backlight loops and all RF/USB paths, and clearly label anything that remains provisional.
- Keep every DRC warning visible and disposition it by type and affected reference. Correct genuine defects; document justified intentional conditions narrowly. Never blanket-ignore warnings or change global design rules just to get a green report.

Stop and report an ENGINEERING_RETURN instead of guessing if a proposed edit depends on an unresolved pin function, component value, battery protection/charger behavior, display wiring, antenna/matching design, stackup/impedance, holder dimension or owner choice. In particular, O05 still requires a qualified electrical/battery review of the complete removable 2S system before schematic commitment or energizing. Do not represent the current placeholder as safe or solved. The display drawing/sample, RF matching and stackup/solver, exact holder, enclosure tolerance fit and cost target also remain open engineering gates.

After every edit:
- Save the editable KiCad schematic, board and candidate libraries. Record a concise changed-file list and why each edit is supported.
- Re-run ERC, DRC with schematic parity, unconnected-item and net/pad reconciliation checks; save fresh reports and review each finding. Compare the counts and actual findings with the before-state. A lower count is not a pass by itself.
- Re-render front/back and inspect the board plus assembly/enclosure in 3D. Treat current display, cell-holder and case solids as conceptual until exact samples and a tolerance-checked fit dummy exist.
- Update only the candidate's README/issues/review record with corrected facts, unresolved evidence, commands, tool versions and report locations. Do not claim manufacturability, performance or the BRL 200 target without supporting quotes/calculations.

Return a concise summary with: the commit reviewed; files changed; each verified correction and its primary-source evidence; before/after ERC, DRC, unconnected and parity results; unresolved blockers grouped as battery, display/mechanical, RF/stackup, digital and cost/factory; and the exact next engineering actions. Stop before Gerbers, drill/CPL, orderable production package, real-cell energizing or manufacturing release. The project owner's explicit manufacturing acceptance is still required later.
```

## Current readiness boundary

Astra already owns candidate refinement and complete project coordination. It should return the unresolved engineering gates rather than inventing answers. The final `docs/ASTRA_HANDOFF.md` and `docs/ASTRA_EXECUTION_PROMPT.md` remain **NOT READY** for final implementation/manufacturing entry until the frozen BOM, exact circuits, qualified battery review, display samples, RF/stackup, mechanical fit and other gates have objective closure evidence.
