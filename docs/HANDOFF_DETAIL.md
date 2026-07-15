---
description: "L2 detail companion for HANDOFF.md — operational defaults, anti-patterns, health-check, see-also."
status: "active, detail"
last_updated: "2026-07-14"
---

# HANDOFF — Detail (L2)

> L0: L2 detail for `HANDOFF.md`.  Per P11 摘要+引用, the
> summary file is the L0/L1 layer (≤ 7KB); this file is
> the L2 layer (operational defaults + anti-patterns +
> health-check + see-also).  Per R6, this companion is
> referenced from the summary.

---

## Operational defaults for any new agent

1. **Always apply P25 step 7 (post-modify re-apply new rules
   check)**.  After modifying any principle, check that the
   modified principle still applies to your change.

2. **Always 7-check BEFORE commit** (7 checks):
   top-down / 5-family / ordering / cross-ref / cap (R5: ≤7KB,
   R8: ≤300 lines) / L0 + R10 / inductive.

3. **Commit message MUST cite a P##** — the `hooks/commit-msg`
   hook enforces this.  Empty citations = commit rejected.

4. **Sub-tasks need M-task-summary**; parent verification is
   an empty commit citing consumed children (see
   `docs/SUMMARY_LIFECYCLE.md`).

5. **Default decision = EXECUTE when user says trust/go/next**.
   Exception: 真歧义 (real ambiguity) → state ambiguity, list
   options, pick one, apply, cite principle (per AGENTS.md
   "When in doubt").


## What NOT to do (per AGENTS.md + refactor audit findings)

- Don't create parallel doc structures (M33 in M-self-application)
- Don't commit to sibling projects from this repo (P21)
- Don't fix mechanically at 1st occurrence (P7 — wait for 3+)
- Don't write a script for what a doc could state (P23)
- Don't claim green when yellow (P17)


## Quick health check before starting work

Run this 4-item check before declaring "ready":

- [ ] Have you read this HANDOFF.md? (yes/no)
- [ ] Have you read `docs/HOW_TO_READ_GRAPH.md`?  (yes/no)
- [ ] Have you read `docs/PROJECT_STATE.md` Goal段? (yes/no)
- [ ] Have you read the L0 of `docs/PRINCIPLES.md`? (yes/no)

If yes to all 4, you can start.  If no, go back.


## See also

- `AGENTS.md` — root operating rules (load first)
- `docs/PROJECT_STATE.md` — current state snapshot
- `docs/HOW_TO_READ_GRAPH.md` — 3-step reading pattern
- `docs/SELF_ORG.md` — P27 candidate (project self-org)
- `docs/MERGE_EVAL.md` — c47 P-n merge candidates (47c/47d pending)
- `docs/PLAN_TOPDOWN_REORG.md` — recent plan iterations
- `../agent-reflection-skill/README.md` — sibling project (downstream)
