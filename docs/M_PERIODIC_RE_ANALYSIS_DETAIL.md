# M-periodic-re-analysis (full text)
Last P20-verified: 2026-07-15

> L0: L2 detail for `OPERATING_RULES.md` § M-
> periodic-re-analysis段 (M-n 23).  Per P11 摘要
> +引用 + R6, this companion is required when
> the summary rule describes self-correction
> protocol.  Load when: agent has been working
> a long time OR needs to re-analyze at 最终
> 目标 level.

## Why this L2 doc exists

The OPERATING_RULES.md § M-periodic-re-analysis
段 (c127) provides the 3 sub-steps.  This L2
doc provides decision tree, worked examples,
and how to apply across 3-project arch.

## 3 sub-steps (per M-n 23 段)

| # | Sub-step | When to apply |
|---|---|---|
| 1 | **Re-analyze at 最终目标 level** | After 10+ commits OR 1+ hour OR user explicit |
| 2 | **Compare to 当前 state** (per M-n 17 Path 1) | Always when re-analyzing |
| 3 | **Plan for re-analysis-driven changes** | After identifying gaps |

## Decision tree: when to invoke M-n 23

```
Q1: Has agent worked 10+ commits in single
    session?
├── No → Q2
└── Yes → Apply M-n 23 3 sub-steps

Q2: Has agent worked 1+ hour without re-analysis?
├── No → Q3
└── Yes → Apply M-n 23 3 sub-steps

Q3: Did user explicitly ask for re-analysis?
├── No → Q4
└── Yes → Apply M-n 23 3 sub-steps

Q4: Is agent about to declare "all pass" (per P26)?
├── No → M-n 23 not strictly applicable
└── Yes → Apply M-n 23 3 sub-steps (per M-n 23
        when-to-invoke conditions)
```

## 3 sub-steps sequence (per M-n 23 段)

### Sub-step 1: Re-analyze at 最终目标 level

Apply M-n 22 3W1H:
- **What**: 最终目标 (per PROJECT_STATE.md +
  3-project arch)
- **Why**: Rationale (per P22 case-3 boundary)
- **Who**: Future agents (per M-n 20 framework-
  agnostic)
- **How**: High-level approach (per M-n 16 top-
  down)

### Sub-step 2: Compare to 当前 state

Per M-n 17 Path 1 (intra-agent re-read):
- List 实际 完成 state
- Compare to 最终目标
- Identify gaps (R-n violations, missing L2
  companions, stale entry files, etc.)

### Sub-step 3: Plan for re-analysis-driven changes

- Per P7 奥卡姆: 哪些 changes 真正 需要?
- Per M-n 16 stage 3 top-down: 优先级
- Apply M-n 18 节点 生命周期管理 to sub-task
  summary

## How to apply across 3-project arch

Per M-n 23 (per c127) + M-n 22 + M-n 17:

| Project | When to invoke M-n 23 |
|---|---|
| **SUA** | After 10+ M-n/P-n commits OR before declaring "all pass" |
| **skill-incubator** | After multiple case studies OR before skill 孵化 |
| **agent-reflection-skill** | After multiple primitives OR before framework extension |

## Worked example: c127 (M-n 23 codify + re-analysis)

When M-n 23 was codified (c127), the 3 sub-
steps were applied:

- **Sub-step 1**: Re-analyzed at 最终目标
  (3W1H + M-n 22)
- **Sub-step 2**: Compared to 当前 state
  (table with SUA/skill/skill-incubator
  完成度)
- **Sub-step 3**: Planned for re-analysis-
  driven changes (3 issues found):
  1. M-n 19-23 missing L2 (P11 + R6)
  2. OPERATING_RULES.md Path 1 audit
  3. PLAN file Changelog noise

This demonstrates M-n 23 + M-n 22 + M-n 17
composition.

## Worked example: c129-c132 (M-n 19-22 L2 batch)

When c129-c132 were committed (M-n 19-22 L2
companions), M-n 23 was applied to issue 1:

- **Sub-step 1**: Re-analyzed M-n 19-22 (3W1H:
  What = L2 companions, Why = P11 + R6, Who =
  future agents, How = M-n 13 pattern)
- **Sub-step 2**: Compared to 当前 state (5 of
  13 M-n missing L2)
- **Sub-step 3**: Planned batch (c129-c133
  sequence)

This demonstrates M-n 23 systematic application.

## Worked example: c133 (M-n 23 L2 companion)

When M-n 23 L2 was created (c133), M-n 23 was
applied to itself:

- **Sub-step 1**: Re-analyzed M-n 23 (3W1H:
  What = L2 companion, Why = c127 issue 1, Who
  = future agents, How = M-n 13 pattern)
- **Sub-step 2**: Compared (M-n 23 was the
  last missing L2 of 5)
- **Sub-step 3**: Planned (c133 = 1 commit)

This demonstrates M-n 23 self-application (per
P28 recursion).

## When NOT to use (anti-patterns)

### Anti-pattern 1: Continue mechanical queue mode without re-analysis

Per user message: "如果做了很久, 重新分析".  Don't
mechanical follow queue.

### Anti-pattern 2: Skip 3W1H first

Per M-n 22: 3W1H BEFORE top-down.  Don't skip
the 抽象 level.

### Anti-pattern 3: Miss critical gaps (R-n violations)

R-n violations (R3/R8/R12 per c110 audit) must
be identified in re-analysis.

### Anti-pattern 4: 修订 L4 boundary without end vision check

Before 修订 L4 boundary (mid/high risk), apply
M-n 23 to verify end vision.

### Anti-pattern 5: Re-analyze without writing plan

Sub-step 3 (plan for changes) is critical.
Without plan, re-analysis is wasted.

## Relationship to other M-rules + P-n

- **M-n 17 (context-freshness-check)**: M-n 23
  sub-step 2 uses M-n 17 Path 1.
- **M-n 18 (recursive-summary-protocol)**: M-n 23
  sub-step 3 uses M-n 18 (sub-task summary).
- **M-n 22 (3w1h-think-first)**: M-n 23 sub-step
  1 uses M-n 22 3W1H.
- **M-n 20 (agent-discoverability-check)**: M-n
  23 sub-step 2 considers M-n 20 (entry files
  current).
- **P7 奥卡姆**: M-n 23 sub-step 3 enforces P7.
- **P22 case-3 boundary**: M-n 23 is meta
  (about how project should self-correction).
- **P26 fresh-agent discoverability**: M-n 23
  when-to-invoke conditions include "before
  declaring all pass".
- **P28 (recursion)**: M-n 23 is recursive.

## Self-application (per P28 recursion)

This L2 doc IS M-n 23 applied to itself:
- **Sub-step 1**: Re-analyzed M-n 23 (3W1H:
  What/Why/Who/How)
- **Sub-step 2**: Compared to current state
  (M-n 23 was last missing L2)
- **Sub-step 3**: Planned (c133 = 1 commit)

## Cross-references

- `OPERATING_RULES.md` § M-periodic-re-analysis
  — the L0/L1 段 (in SUA)
- `docs/M_3W1H_THINK_FIRST_DETAIL.md` — M-n 22
  L2 companion (M-n 23 sub-step 1)
- `docs/M_CONTEXT_FRESHNESS_CHECK_DETAIL.md` —
  M-n 17 L2 companion (M-n 23 sub-step 2)
- `docs/M_RECURSIVE_SUMMARY_PROTOCOL_DETAIL.md` —
  M-n 18 L2 companion (M-n 23 sub-step 3)
- `docs/M_AGENT_DISCOVERABILITY_CHECK_DETAIL.md`
  — M-n 20 L2 companion (M-n 23 sub-step 2)
- `docs/PROJECT_STATE.md` — 最终目标 reference
- user message 2026-07-15 — origin (user message explicit
  codify request)

## Changelog

- c127 (OPERATING_RULES.md): add M-n 23 段
  (summary, 3 sub-steps + re-analysis output).
- c133 (this file): add L2 detail companion
  per P11 + R6 (per c127 re-analysis issue 1:
  M-n 19-23 missing L2 companions — last of 5).