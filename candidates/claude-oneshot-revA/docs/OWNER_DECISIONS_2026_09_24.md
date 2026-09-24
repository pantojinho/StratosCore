# Owner decisions taken by proxy — 2026-09-24 (lowest-cost criterion)

Gabriel authorized via chat: "tome as decisões pendentes, sempre menor custo".
Scope: **candidate folder only** (`candidates/claude-oneshot-revA`). The
repository baseline (`docs/`, `hardware/`) keeps its owner gates; these
decisions bind the candidate and feed the next owner review.

## D-A5 (GPIO A5): ESP32 GPIO8 → `EXP_CS_N` — hardware SPI2 CS
Adopted recommendation A5-2 from
[GPIO_GAPS_A5_A8_PROPOSAL.md](GPIO_GAPS_A5_A8_PROPOSAL.md).
Cost basis: zero-BOM (net rename + pull-up move to `3V3_EXP`, R55 removed).
A GPIO3 option would demand the same extras and adds strap-risk analysis.

## D-A6 (GPIO A6): P10 renamed `SX_NRESET`, external pull-up stays on
`3V3_MAIN` (100 kΩ R70, parallel with the internal ~50 kΩ)
Adopted A6-1 (rename only; zero cost).

## D-A7 (GPIO A7): P14 = `RP_RUN`, open-drain emulated (sink-only)
Adopted A7-1. Cost basis: zero-BOM. SYS-02 follow-up kept: align the RUN
pull-up rail with RP2040 IOVDD (`3V3_ADSB` vs `3V3_MAIN`) — documents only.

## D-A8 (GPIO A8): P07 = `TOUCH_RST_N` push-pull, 10 kΩ pull-down
Adopted A8-2. Cost basis: one 0402 resistor already in the BOM class.
The 10 kΩ (not 100 kΩ) is the cheap hedge against the undocumented ST1633I
module pull-up; re-measure on samples (TBD) before final value.

## D-MASK (LGA mask strategy U30/U32): **S1 — per-pad NSMD openings**
- ICM-42688-P: openings 0.575 × 0.35 mm (TDK AN-000393 v2.4 fallback, +0.1 mm)
- BMP581: openings 0.365 × 0.34 mm (Bosch 20 µm/side over land)
- All solder dams ≥ 0.15 mm ≥ JLCPCB 0.10 mm (green/1 oz) published dam →
  **no special assembler query, no premium, no order delay.**
- The current common body-sized openings (S2) are "undetermined" at JLC and
  would need a remark + Confirm-Production-File round-trip + zero inner
  copper guarantee — time cost with zero BOM saving.
- Follow-ups recorded: stencil 0.10 mm for both parts (area ratio passes at
  0.10, fails ≥ 0.12); the 199 mask-bridge DRC items retire when the
  candidate footprints adopt S1 openings (footprint edit still needs the
  owner-approved footprint correction pass — not done silently here).
- Green mask confirmed (cheapest, dams within capability for 1 oz).

## D-COST (five-unit target ≤ BRL 200): **target officially INFEASIBLE — keep
the prototype scope, defer target revision**
Evidence: retrieved lines alone ≥ BRL 504/unit (2.5×), with tariffs ~BRL
691–726 (3.5×). Even excluding display + ADL5513 entirely: BRL 245 > 200.
Cheapest path (documented in
[ASSEMBLER_MASK_AND_COST_SNAPSHOT.md](ASSEMBLER_MASK_AND_COST_SNAPSHOT.md)):
keep the five-unit hobby prototype scope (OWN-04), do **not** start
replacement studies now (they cost engineering hours and need owner review);
re-quote at order time. Target revision is a genuine owner decision because
it changes D24 in the baseline — proxy cost-logic only rules **how to
proceed**: no money spent chasing an impossible target.

## D-GND-RESIDUAL (10 U3 clearance items): **accepted for prototype; manual
KiCad pass documented**
Lowest cost = stop automated re-route attempts (three data-backed attempts
converged: each fix trades clearance pairs for shorts; the access window to
the via landing is ~50 µm). The fix (0.35/0.2 via, same-net hole check,
orthogonal re-entry) is specified step-by-step in
[GND_STITCH_2026_09_23.md](GND_STITCH_2026_09_23.md) for the owner's manual
KiCad pass — which AGENTS.md gates require anyway before Astra.
