# CAD tool use for the final Astra pass

Status: **evaluation only; StratosCore is NOT READY for CAD execution**. Reviewed 2026-09-22 against the [official GPT-6 Astra article](https://openai.com/pt-BR/index/gpt-6-astra/) and the owner's [Hermes KiCad skill](https://github.com/pantojinho/hermes-kicad-pcb). The official example shows KiCad component placement and copper routing; it does not document which GUI, API or autorouter method Astra used. Hermes provides an optional, separate headless `pcbnew`/`kicad-cli`/Freerouting workflow; it is not a required or verified reconstruction of Astra's method.

## Use boundary

1. Keep the frozen StratosCore engineering package and native KiCad project authoritative. Record the exact KiCad and optional Hermes versions/commit in the final [execution manifest](ASTRA_EXECUTION_PROMPT.md). Run the existing hierarchy ERC before any CAD edits.
2. Astra may use the KiCad GUI, `pcbnew`, `kicad-cli`, or a reviewed combination according to the task and installed tools. If Hermes is used, run its environment check and a disposable demo first; do not import demo boards, generic parts or design-rule values into StratosCore.
3. Capture each reviewed schematic block from its exact part and application evidence. Run ERC per sheet. Check symbol pin numbers, supply domains, boot/off states, no-connects, footprint mapping and annotated BOM against the frozen input manifest.
4. Place and route only against the accepted mechanical, stackup, RF, power and DFT constraints. Do critical power/current loops, RF paths, USB, clocks and sensitive analog paths under their own reviewed rules. If optional autorouting is used for remaining ordinary digital nets, preserve the critical routes/keepouts, inspect the resulting SES import, refill zones and rerun all checks. A generic demo's zero-error result is not transferable to this board.
5. Save machine-readable and human-readable ERC/DRC reports. Review **all** errors, warnings, unconnected items and schematic-parity findings. Do not blanket-ignore solder-mask bridges, courtyard overlap, hole clearance or `pin_not_driven`; resolve each against the actual part, fab process and schematic. A clean ERC/DRC does not establish battery safety, RF performance, impedance, thermal behavior, assembly fit or manufacturability.
6. If a missing or conflicting input changes a net, footprint, placement, controlled impedance or safety decision, issue the `ENGINEERING_RETURN` in the [Astra prompt](ASTRA_EXECUTION_PROMPT.md). Do not use automation to fill that gap. Manufacturing files and ordering remain separate post-Astra review/release work.

## Immediate pre-Astra checks

- Complete the exact MPN/footprint/circuit/owner/reviewer gates in [the workboard](PRE_ASTRA_WORKBOARD.md) and [handoff](ASTRA_HANDOFF.md).
- Freeze the four-layer factory stack, solver-based RF/USB geometries, outline, fit dummy and DFT access.
- Record any Hermes commit actually used, command lines, input/output hashes, KiCad version and router settings so another reviewer can reproduce the CAD operation.
