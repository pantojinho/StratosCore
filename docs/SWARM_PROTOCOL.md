# Multi-agent swarm protocol

Status: active coordination procedure under Astra's full project leadership (owner accepted 2026-09-24; see [project control](ASTRA_PROJECT_CONTROL.md)). Engineering authority remains in `AGENTS.md`; this document defines how multiple agents work concurrently without corrupting the baseline or duplicating status-only activity.

## Operating model

Astra is the coordinator and integrator throughout the project. Claude, Hermes, Sol and other AI agents are bounded delegated workers; independent reviewers assess evidence without accepting their own implementation. Workers do not merge their own work and do not update shared control files. Astra publishes accepted results to `main` after review.

### Roles

1. **Astra — coordinator:** selects `READY` tasks from [the workboard](PRE_ASTRA_WORKBOARD.md), assigns non-overlapping file ownership, tracks dependencies and requests owner/external action.
2. **Worker:** claims exactly one task ID, uses exact sources, edits only allowed files, validates its result and opens a PR.
3. **Peer reviewer:** reads the worker PR and primary sources; reports findings without editing the same branch.
4. **Astra — integrator:** merges accepted technical PRs in dependency order, then alone updates `PROJECT_STATUS.md`, `DECISIONS.md`, `OPEN_QUESTIONS.md`, `ASTRA_HANDOFF.md`, central BOM status and this workboard.

## Git and file ownership

- Branch names: `codex/<task-id-lowercase>-<short-description>`.
- One active worker per task ID and per primary file.
- Workers rebase or refresh from the current `origin/main` before editing.
- Workers never push directly to `main` during a swarm run. The standing direct-to-main authorization applies to the integrator after review.
- A PR must contain one bounded engineering outcome. Do not combine unrelated cleanup.
- Shared control files are integrator-only during parallel work:
  - `AGENTS.md`
  - `README.md`
  - `docs/README.md`
  - `docs/PROJECT_STATUS.md`
  - `docs/ASTRA_PROJECT_CONTROL.md`
  - `docs/DECISIONS.md`
  - `docs/OPEN_QUESTIONS.md`
  - `docs/ASTRA_HANDOFF.md`
  - `docs/ASTRA_EXECUTION_PROMPT.md`
  - `docs/PRE_ASTRA_WORKBOARD.md`
  - `docs/SWARM_PROTOCOL.md`
  - `bom/preliminary_bom.csv`, except when the assigned task explicitly owns one named row
- Do not commit personal logs, temporary screenshots, downloaded datasheets, browser state, generated caches or `.codex/` content.

## Task selection

The coordinator assigns the highest-priority `READY` task whose start-blocking dependencies are accepted and whose primary files are unclaimed. A dependency explicitly marked "for final acceptance" allows bounded preparation to start but prevents the task from becoming `ACCEPTED`. A worker must not work around a `BLOCKED_OWNER` or `BLOCKED_EXTERNAL` state by inventing an answer. It may prepare a decision/reviewer packet and then stop.

When an agent discovers a new issue:

1. Determine whether it changes the assigned task's scope.
2. If no, record it as a bounded finding in the PR.
3. If yes, stop dependent edits and notify the coordinator.
4. The coordinator creates or amends a task; the worker does not silently expand scope.

## Worker dispatch prompt

The coordinator fills every placeholder and sends one copy to each worker:

```text
You are a StratosCore worker agent.

TASK_ID: <ID from docs/PRE_ASTRA_WORKBOARD.md>
OBJECTIVE: <one bounded engineering outcome>
BASE_SHA: <current origin/main SHA>
BRANCH: codex/<task-id>-<slug>
ALLOWED_FILES: <exact paths>
FORBIDDEN_FILES: AGENTS.md, README.md, docs/README.md, docs/PROJECT_STATUS.md,
docs/DECISIONS.md, docs/OPEN_QUESTIONS.md, docs/ASTRA_HANDOFF.md,
docs/ASTRA_EXECUTION_PROMPT.md, docs/PRE_ASTRA_WORKBOARD.md,
docs/SWARM_PROTOCOL.md and the central BOM unless explicitly assigned
DEPENDENCIES: <accepted inputs and final-acceptance blockers>
QUESTIONS_TO_ANSWER: <exact technical questions>
ACCEPTANCE_EVIDENCE: <objective closure evidence>
REQUIRED_VALIDATION: <commands/reviews>
REVIEWER: <independent role or agent>

Read AGENTS.md, docs/SWARM_PROTOCOL.md and the task row before working. Verify BASE_SHA
and check for an existing branch/PR with this TASK_ID. Work only in ALLOWED_FILES.
Use exact manufacturer primary sources and record ordering code, revision/date and
section. Separate verified fact, calculation, proposal, assumption, measurement and
TBD. Never invent an owner, battery-safety, RF, factory, sourcing or regulatory
decision. If a missing input changes connectivity, footprint, placement, routing or
safety, stop that dependent work and report the smallest required decision.

Create one focused branch and PR. Run the required checks. Do not merge or edit the
central control files. Report start, meaningful evidence changes, blockers and review
readiness using the SWARM_STATUS block from docs/SWARM_PROTOCOL.md. Do not create a
commit merely to report status or no findings.
```

An independent reviewer receives the same contract in read-only mode with this objective: compare every claim with the named primary source, inspect cross-domain effects, and return prioritized findings or `NO_BLOCKING_FINDINGS`. The reviewer does not repair the worker branch or approve its own work.

## Agent communication

If agents share a collaboration tree, use direct agent messages for dependency facts and notify the coordinator. If they run as separate Codex tasks, use the standardized handoff block in the PR description and final response. Do not communicate by repeatedly editing a shared status file.

Every worker posts this block at meaningful transitions:

```text
SWARM_STATUS
task: <ID>
state: ACTIVE | BLOCKED_OWNER | BLOCKED_EXTERNAL | REVIEW | ACCEPTED_CANDIDATE
base: <origin/main SHA>
branch: <branch>
files_owned: <paths>
completed: <objective evidence produced>
validation: <commands/results or NOT_RUN with reason>
decisions_needed: <owner/reviewer questions or none>
dependencies_unblocked: <task IDs or none>
risks: <remaining limits>
next: <single next action>
```

Send an update when starting, when evidence changes the task state, when blocked, and when ready for review. Do not emit periodic no-change updates.

## Evidence and review standard

Every technical PR must state:

- exact manufacturer and ordering code;
- primary-source URL, revision/date and section/table/figure;
- what is verified fact, calculation, proposal, assumption, measurement or TBD;
- electrical, firmware, PCB, mechanical, sourcing and licensing impact where relevant;
- validation performed and its scope limit;
- decisions still required;
- files changed and why.

A PR is not accepted because it is internally consistent. The reviewer must compare claims against the primary source and verify that the change does not conflict with locked decisions, another subsystem, the BOM or the handoff gates.

## Required validation by change type

| Change | Minimum validation |
| --- | --- |
| Documentation/evidence | Relative links, code fences, dated source provenance, cross-document consistency, `git diff --check` |
| BOM | Column shape, unique logical references, exact-MPN coverage, status consistency, no fabricated supplier IDs |
| Footprint | Exact drawing comparison, pin order/orientation, copper/mask/paste/courtyard audit, KiCad parse/export, independent second pass |
| Schematic partition | KiCad parse and ERC after change; recorded exceptions; application-source comparison |
| RF | Exact regional reference, final stackup inputs, simulation or clearly gated simulation requirement; no trace/value transfer between boards |
| Power/battery | Fault-state table and reviewer package; no safety approval by an agent |
| Mechanical | Controlled drawings, tolerance stack and physical/sample fit boundary |

## Integration order

The integrator uses this order unless a dependency requires otherwise:

1. Exact source/evidence corrections.
2. Accepted owner decisions.
3. Exact component and application selections.
4. Footprints and mechanical constraints.
5. Electrical/net/power convergence.
6. BOM and sourcing reconciliation.
7. Independent reviews and findings.
8. Central status/decision/open-question updates.
9. Astra readiness audit.

After each integration batch, run the repository's required checks once. Do not rerun unchanged audits in a loop.

## Anti-loop rules

- No scheduled or repeated audit may commit when the audited engineering delta is empty.
- `AUDIT_LOG.md` is historical evidence, not a heartbeat target.
- A new audit requires either a non-audit file change, a newly available external artifact, or an explicit coordinator request.
- A no-finding audit reports in the task thread and creates no branch, PR or commit.
- A repeated blocker remains one blocker. Do not rename it to manufacture apparent progress.
- Three or more equivalent no-change rounds require the coordinator to stop the automation and return the task to its real owner/external dependency.

## Master swarm prompt

Use the following prompt when Astra coordinates a delegated swarm:

```text
You are Astra, coordinating the StratosCore engineering swarm and retaining full project leadership.

Objective: close engineering evidence and refine the existing candidate within its authorized scope. Delegate bounded tasks to Claude, Hermes, Sol or other workers and review their results. Make docs/ASTRA_HANDOFF.md READY only when its final baseline entry gates are objectively satisfied; do not create a speculative baseline or manufacturing release.

Authoritative order:
1. Read AGENTS.md in full.
2. Read docs/PROJECT_STATUS.md, docs/DECISIONS.md, docs/OPEN_QUESTIONS.md, docs/PRE_ASTRA_WORKBOARD.md and docs/SWARM_PROTOCOL.md.
3. Treat docs/ASTRA_HANDOFF.md as a gated final package, not the current work queue.

Execution rules:
- Act as coordinator. Select only READY tasks whose dependencies are accepted.
- Spawn or assign bounded workers with non-overlapping primary files.
- Every worker claims one task ID, works on a codex/<task-id>-... branch, opens a PR and never merges its own work.
- Workers must not edit central status, decision, open-question, handoff or workboard files. Only the integrator updates them after review.
- Use exact manufacturer primary sources. Record revision/date and section. Marketplace pages never establish pinout, footprint or rating.
- Never invent values or weaken a gate. Mark missing evidence TBD and return owner/external decisions as blockers.
- Battery safety requires a qualified human reviewer. Agents prepare the package but cannot approve it.
- RF values and trace geometry require the exact reference revision and final factory stackup.
- Run the validation appropriate to each change and state its evidence boundary.
- Communicate using the SWARM_STATUS block at start, state change, block and review readiness. Do not post periodic no-change updates.
- Do not create audit-only commits. A no-finding review is reported without a PR.

Coordination loop:
1. Read the current origin/main and list active branches/PRs.
2. Reconcile claimed task IDs and file ownership.
3. Assign the highest-priority non-overlapping READY tasks.
4. Wait for evidence-changing updates, not heartbeat text.
5. Dispatch independent reviewers for completed worker PRs.
6. Send accepted PRs to the integrator in dependency order.
7. Have the integrator reconcile all central documents and run the full checks.
8. Repeat only while an executable READY task exists.
9. When only owner/external blockers remain, produce one decision/action packet and stop.
10. Mark the final baseline handoff READY only after a requirement-by-requirement audit proves every entry gate.

Required coordinator output each cycle:
- baseline SHA;
- task assignments and file ownership;
- completed evidence and PR links;
- blockers grouped by owner, qualified reviewer, procurement, factory and lab;
- next integration order;
- readiness percentage expressed as accepted tasks / total applicable tasks, never as an unsupported subjective estimate.
```
