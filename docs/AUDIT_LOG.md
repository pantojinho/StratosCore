# Readiness audit log

Purpose: carry the read-only readiness-audit loop across agent sessions. A session that picks up the audit starts from the **current baseline** below, compares `git log <baseline>..HEAD`, and appends a new row. This file records audit state only — it never closes an engineering gate and is not evidence for one.

**Current baseline: `b3d0506`** (2026-09-17) — the commit on `main` that carried round 5.

Set the baseline to the commit on `main` that carries the round you just appended. When a round lands through a pull request that hash does not exist yet as you write the round, so update this line **after** the merge, in the next commit. Round 5 was appended in `8426c09` while this line still read `4c94263`; a vigil run in that window would have re-reported rounds 4 and 5 as a fresh delta.

## Rounds

| Round | Range audited | Findings | Disposition |
| ---: | --- | --- | --- |
| 1 | up to `0e20406` | 7 internal-consistency failures (obsolete egress-blocker block and stale header in `I2C_BUS_BUDGET.md`; unsourced `~45-65 pF` estimate; `§5.2.2`/`§5.22` mismatch; gate 9 desynced from O11; gate 4 vs O20 conflating datasheet evidence with bench proof; superseded `JLC2313` in the BOM). Bus decision had no entry in `DECISIONS.md`. 6 blind spots with no O/P at all: regulatory (ANATEL), flight rules (ANAC/DECEA), cost target, UN38.3 cell transport, factory firmware/provisioning, conformal coating/condensation | Closed by `36a748e` and `3bb00bd`: fixes applied, P26 opened, O21-O26 created, O16 extended with drop/vibration |
| 2 | `0e20406..3bb00bd` | 8 of 9 prior findings resolved. **Persisting:** UM10204 cited second-hand via BMP581/SHT4x instead of the primary document (rule 3). **New:** O21-O26 created but orphaned — no gate, `ASTRA_HANDOFF.md` or `DECISIONS.md` referenced them | Closed by `07ba33a` (gate 10 created; O26 wired into gate 8; O21-O26 into the Astra entry gates) and `3092791` (NXP UM10204 Rev. 7.0, 1 October 2021, retrieved directly; Table 10, note [5], §7.2) |
| 3 | `3bb00bd..3092791` | Both prior findings resolved. **New:** adding gate 10 left a stale count — "nine gates" in `PROJECT_STATUS.md` and `CLAUDE.md` | Closed by `4c94263` |
| 4 (vigil) | `3092791..4c94263` | Delta is the gate-count correction only. No new finding. Zero residual "nine gates"; gate count reconciles at 10 | Converged — no action |
| 5 | full sweep at `4c94263`, Astra entry gates | Swept all 12 Astra entry gates rather than the commit delta. **3 findings:** (a) `I2C_BUS_BUDGET.md` closure criterion 2 was unsatisfiable as written — it demanded a transcribed figure in every cell, but six devices genuinely publish no `Ci`, which is a datasheet property, not pending work; (b) the orderable-BOM requirement (entry gate 11) had no O/P — the CSV has no quantity column and `PASSIVES_DEBUG` is flagged "Not quantity-complete"; (c) the test-point requirement (entry gate 8) had no O/P — `manufacturing/test/README.md` defers it to "after schematic review", which is after placement needs it | Fixed in this round: criterion 2 rewritten to separate "not stated" from untranscribed and to require a declared substitute in criterion 3; O27 (orderable BOM) and O28 (test access) created and wired into the entry gates and `PROJECT_STATUS.md` at creation, avoiding the orphaning seen in round 2 |

## Active blockers

None of these can be closed by an agent working from documents. Verified unchanged as of `4c94263`.

| ID | Waiting on | Where |
| --- | --- | --- |
| O05 | Qualified battery/electrical reviewer's signature; includes the BQ25887 autonomous-start fail-safe gating | `OPEN_QUESTIONS.md` |
| O10 | JLCPCB order-time stack ticket confirmation and factory-solved 50/90-ohm geometry | `OPEN_QUESTIONS.md` |
| P26 | Owner decision on the shared I2C bus: (a) 100 kHz, (b) remove TUSB320LAI from the bus, (c) 400 kHz with an enforced <=100 pF | `DECISIONS.md` |
| O01 | Orient controlled TFT-power/FPC clarification and two labeled samples | `OPEN_QUESTIONS.md` |
| O21-O26 | Owner answers: ANATEL regime, ANAC/DECEA flight rules, cost target, UN38.3 transport, factory firmware/provisioning, conformal coating/condensation | `OPEN_QUESTIONS.md` |

## Vigil procedure

Read-only. Do not edit, commit or open a pull request while running it; report the delta and stop.

1. `git pull origin main`, then `git log <baseline>..HEAD --oneline` — any new commit, and what does it change?
2. Did any of the five blocker rows above change state?
3. BOM drift:

```
python3 -c "import csv;r=list(csv.DictReader(open('bom/preliminary_bom.csv')));print(sum(1 for x in r if x['MPN'].strip().upper()=='TBD'), sum(1 for x in r if x['Status'].startswith('PROPOSED')))"
# expected: 7 6
```

   Also confirm `MAIN_PCB` still reads `JLC04161H-3313`. A bare `grep -c 'TBD\|PROPOSED'` over the CSV is **not** the right check — it counts the 36 rows whose LCSC column is TBD and returns 43.
4. New blind spot: any essential topic present in the docs with no O/P entry? Minimum categories — regulatory, cost, cell transport, factory firmware, coating/condensation, drop/vibration.
5. Report only differences since the baseline, as `Item | Status | Evidence (file:line) | Action`, and close with the readiness verdict. Nothing changed → one line naming the baseline and the outstanding blockers.

`AGENTS.md` applies throughout; never fabricate evidence to fill a gap.
