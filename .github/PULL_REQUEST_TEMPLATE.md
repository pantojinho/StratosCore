# StratosCore engineering task

## Task contract

- Task ID:
- Gate:
- Base `origin/main` SHA:
- Branch:
- Files owned:
- Dependencies:
- Reviewer:

## Engineering outcome

State the one bounded result this PR delivers. Separate verified facts, calculations, proposals, assumptions, measurements and remaining TBDs.

## Primary evidence

For every technical claim, list the exact manufacturer/ordering code, source URL, document revision/date, section/table/figure and review date. Marketplace listings may support procurement context only.

## Cross-domain impact

- Electrical/power:
- Firmware/interface:
- PCB/footprint/layout:
- RF:
- Mechanical/enclosure:
- Manufacturing/test:
- Sourcing/cost/availability:
- Licensing/reuse:

## Validation

- [ ] Diff contains only the assigned scope and allowed files.
- [ ] Relative links and code fences were checked.
- [ ] Exact MPN/package/footprint claims match primary evidence.
- [ ] Affected interfaces and unpowered/default states were reviewed.
- [ ] Required repository checks were run and results are recorded below.
- [ ] No owner, safety, RF, factory or sourcing decision was silently inferred.
- [ ] Remaining blockers and post-PCBA validation are explicit.
- [ ] `git diff --check` passes.

Commands/results:

```text
<command and concise result>
```

## Swarm handoff

```text
SWARM_STATUS
task: <ID>
state: REVIEW
base: <origin/main SHA>
branch: <branch>
files_owned: <paths>
completed: <objective evidence produced>
validation: <commands/results>
decisions_needed: <owner/reviewer questions or none>
dependencies_unblocked: <task IDs or none>
risks: <remaining limits>
next: independent evidence/interface review
```

Workers do not merge their own PRs or edit integrator-only central files. A no-finding review does not require a commit or PR.
