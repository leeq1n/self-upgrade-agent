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

## Sibling project awareness (per user meta-rule 2026-07-15)

Per user meta-rule "skill 项目是基于 SUA 的": SUA is upstream,
agent-reflection-skill is downstream.  This means:

### When SUA changes, skill needs attention

Every SUA commit that establishes a **new reusable pattern**
(e.g., P-n merge, M-n addition, R-n fix, 7-check discovery)
should trigger the question: "Should this pattern be lifted
to `../agent-reflection-skill/`?"

### Decision tree (when a SUA commit is "skill-extractable")

A SUA commit is skill-extractable if:

1. The commit demonstrates a **meta-cognitive pattern**
   (about how to reason, not what to do in this project).
2. The pattern has **3+ observed occurrences** (per
   M_RULE_AUTHORING 3-condition gate; not just 1 case).
3. The pattern is **framework-agnostic** (would work in
   Hermes / Claude Code / Codex, not just SUA).

### Sync protocol (lightweight, not auto)

SUA does **not** automatically update skill.  Instead:

- SUA commits cite the pattern in their commit message
  (per `"this commit demonstrates X"` parenthetical).
- The skill project maintains a "patterns pending extraction"
  list in its HANDOFF.md.
- When SUA becomes stable (parent verify batch), the agent
  reviews the "patterns pending" list and extracts those
  that meet the 3-condition gate.

This is **lightweight**: no auto-sync, no CI cron.  Just a
discipline: when SUA's project self-org (per P27) detects
a stable pattern, the next agent opens the skill project.

### Reverse direction

Skill project changes do **not** require SUA changes (skill
is downstream).  But: if skill codifies a pattern that SUA
**doesn't already have**, that's a signal to add it to SUA
too (per "skill 等 SUA").

### When NOT to sync

- When SUA change is **specific to SUA** (e.g., OKR update,
  P-n specific to SUA's tests) — NOT skill-extractable.
- When skill change is **specific to a framework** (e.g.,
  Hermes-specific invocation syntax) — irrelevant to SUA.



## Sub-project-for-experimentation pattern (per user 2026-07-15)

Per user meta-rule 2026-07-15: "如果当前经验不足以
支撑项目，可以考虑新建一个子项目用来做实验积累失败
经验".

**When to consider**: when current project lacks
experience to handle a task, or when a sub-task
becomes too complex to handle in the main project.

**Anti-pattern**: 可能陷进子任务，需要设定好目标.

**Lifecycle**: 子项目 → 经验积累完成，知道怎么处理后
→ 切回主项目.

**Codification status (2026-07-15)**: 1st occurrence
in SUA; not yet lifted to P-n (M_RULE_AUTHORING
3-condition gate; bootstrap exception applies per
user-explicit ask).  Plan: codify as M-experiment-in-
subproject段 in OPERATING_RULES.md (commit c89), then
L2 detail companion (commit c90), then parent verify
(commit c91).  See queue in this turn's planning
response.

**Related principles**: P21 (sub-project is sibling
per cross-project independence), P22 (stuck→plan
could route to sub-project), P27 (project self-org
allows sub-project for self-development).

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
- `../agent-reflection-skill/README.md` — sibling project (downstream)
