# StratosCore agent rules

## Scope and authority

Read `docs/DECISIONS.md` before modifying hardware and `docs/ASTRA_HANDOFF.md` before starting work. This is a new project; legacy repositories are read-only references. The architecture phase may create reviewed documentation, tests and gated schematic partitions. Do not create a speculative finished schematic, display footprint, routed PCB, or manufacturing release.

1. Never silently change a locked decision. Record proposals in `docs/DECISIONS.md` and obtain the project owner's acceptance before changing the baseline.
2. Every component replacement proposal must include reason, dated cost comparison, availability comparison, electrical impact, firmware impact, and PCB/mechanical impact. Mark unverified data TBD.
3. Use the exact manufacturer's datasheet as the primary technical source. Prefer semiconductor manufacturer reference designs. Record URL, revision, review date, and relevant section.
4. Never infer a pinout, footprint, antenna circuit, or supply range from a marketplace listing. Match the full ordering code and package drawing.
5. Verify RF circuits against manufacturer references and the selected stackup. Do not transfer matching values or trace widths between boards without validation.
6. Battery safety decisions require explicit review before topology freeze, schematic commitment, or energizing a prototype. Document reviewer, evidence, fault tests, and acceptance. Researching and documenting options is authorized in the foundation phase.
7. Do not connect two independently removable Li-ion cells directly in parallel. Protection, charging, reverse insertion, mismatch, and removal behavior must be resolved together.
8. Run ERC after every schematic change and DRC before manufacturing output. Record versions, reports, and reviewed exceptions. A zero-item architecture sheet ERC proves file/hierarchy integrity only, never circuit correctness.
9. Maintain source/license/reuse/modification records in `references/REUSE_REGISTER.md`. Public access is not permission to relicense. Preserve upstream notices and review dependencies individually.
10. Maintain `docs/ASTRA_HANDOFF.md` after meaningful changes; keep it concise and execution-oriented. Update decisions, open questions, requirements, architecture, and BOM together when affected.
11. Do not modify either legacy project or avBadge/ADSBee. Do not import their pin maps as StratosCore assignments.
12. Keep every assumption distinguishable from a locked requirement, verified fact, proposal, or measured result. Supplier IDs, prices, runtime, RF performance, and test outcomes must never be fabricated.
13. ADS-B is a core Rev A hardware feature with its own 1090 MHz RF path and RP2040 baseline. SX1262 is for LoRa, never the ADS-B receiver. Runtime profiles may power ADS-B down.
14. Keep region/channel/power/duty-cycle settings configurable. No universal 915 MHz transmit configuration; require an appropriate regional configuration before enabling TX.
15. Keep hardware under CERN-OHL-P-2.0 and original firmware under MIT as described in `LICENSES/README.md`. Do not copy GPL code into MIT firmware or assume a processor boundary resolves licensing.
16. Avoid unrelated changes, credentials, personal logs, generated caches, and local `.codex/` settings in commits. The owner has granted standing authorization to work and publish directly to `main` without pull requests for this project. Continue to honor all engineering review and safety gates above.
17. The current priority is hardware and PCBA readiness. Use Sol-class work to close exact parts, evidence, interfaces, application circuits, footprints, review gates and the Astra handoff. Reserve Astra for efficient KiCad schematic/PCB execution after decisions are prepared. Limit firmware work to evidence or interface fixtures required to validate the hardware until the hardware baseline is ready.

## Verification for the current phase

Check required files/directories, relative Markdown links, BOM columns and locked-part coverage, official license text provenance, power arithmetic, decision consistency, host ADS-B tests, KiCad hierarchy ERC and `git diff --check`. Schematic circuits remain gated by exact component evidence and accepted owner decisions; PCB placement/routing is a later phase.
