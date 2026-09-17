# CLAUDE.md — StratosCore agent instructions

## Authority

`AGENTS.md` at the repo root is the complete, authoritative rule set for this project. Read it in full before doing anything. This file only adds orientation; if anything here conflicts with `AGENTS.md`, `AGENTS.md` wins.

## Project context (quick orientation)

- Open-source portable field computer (ESP32-S3-WROOM-1-N16R8, RP2040 ADS-B coprocessor, LoRa SX1262, GNSS MAX-M10S, 2S 21700 battery).
- Current phase: **pre-KiCad hardware engineering closure**. Read `docs/PROJECT_STATUS.md` (nine gates), `docs/OPEN_QUESTIONS.md` and `docs/DECISIONS.md` before changing anything hardware-related.
- `docs/ASTRA_HANDOFF.md` is **NOT READY**; Astra (final KiCad capture) may not run yet.
- All repo docs are written in **English**; keep it that way.

## Hard rules recap (violations are unacceptable)

1. Never fabricate a number, price, stock state, measurement or test result. Unverified = `TBD`, stated explicitly.
2. Exact manufacturer datasheet is the primary source for every electrical/mechanical claim. Record URL, document revision, section/table and review date.
3. Never silently change a locked decision (`docs/DECISIONS.md`, LOCKED rows). Propose in the doc and wait for owner acceptance.
4. No speculative finished schematic, routed PCB, display footprint or manufacturing release in this phase.
5. Battery safety (O05) requires a qualified human reviewer — no agent may close it.
6. Do not modify or import from legacy repos (avBadge, ADSBee) beyond read-only reference.
7. Licenses: hardware CERN-OHL-P-2.0, firmware MIT; no GPL code into MIT firmware.

## Workflow

- Owner has authorized direct commits to `main` without PRs, but every engineering/review gate above still applies. Commits: focused, no credentials, no caches, no personal logs.
- After meaningful changes update the cross-referenced docs together (status, decisions, open questions, BOM) and run the checks listed at the end of `AGENTS.md`.
- Respond to the operator in Portuguese (PT-BR) unless the task output itself is repo documentation.
