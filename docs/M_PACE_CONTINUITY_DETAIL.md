# M-pace-continuity (full text)
Last P20-verified: 2026-07-15

> L0: L2 detail for `OPERATING_RULES.md` § M-
> pace-continuity段 (M-n 24).  Per P11 摘要+引用
> + R6, this companion is required when the
> summary rule describes project pacing.  Load
> when: agent has plan AND no 真问题.

## Why this L2 doc exists

The OPERATING_RULES.md § M-pace-continuity段 (c134)
provides the 3 sub-steps.  This L2 doc provides
decision tree, worked examples, and how to apply
across 3-project arch.

## 3 sub-steps (per M-n 24 段)

| # | Sub-step | When to apply |
|---|---|---|
| 1 | **Commit + continue** | After any commit when no 真问题 |
| 2 | **Only interrupt for 真问题** | P17 honest blocker only |
| 3 | **你 vision "主动 + 不打扰"** | Default mode |

## Decision tree: when to interrupt

```
Q1: Is there a 真问题 (per P17)?
├── Yes → Interrupt (ask user)
└── No → Continue (no interrupt)

Q2: Is the question trivial (per M-n 21)?
├── Yes → Don't ask (infer instead, mark guess)
└── No → Q3

Q3: Did user explicitly ask for status update?
├── Yes → Brief response
└── No → Continue silently (don't add verbose
        ending)
```

## How to apply across 3-project arch

Per M-n 24 + 你 vision "主动 + 不打扰":

| Project | Default behavior |
|---|---|
| **SUA** | Continue per PLAN (M-n 16 top-down + M-n 18 sub-task summary) |
| **skill-incubator** | Continue per PLAN (5 phase process + 4 conditions) |
| **agent-reflection-skill** | Continue per PLAN (6 primitives + when-to-reflect) |

## Worked example: c134 (M-n 24 codify)

When M-n 24 was codified (c134), the 3 sub-steps
were applied:

- **Sub-step 1 (commit + continue)**: After c134,
  agent should directly continue c135 (PLAN
  Changelog update) without verbose ending段.
- **Sub-step 2 (only 真问题)**: No 真问题 in
  c134 context, so no interrupt.
- **Sub-step 3 (你 vision)**: Default mode 主动
  continue per PLAN.

## Worked example: anti-pattern (c106-c133)

When c106-c133 were committed (28 commits), M-n
24 was NOT yet codified.  Each commit had
verbose "end this turn" + "active next plan"
段, which 你 turn 第 2 部分 identified as
打断 项目 节奏.

This is the anti-example that motivated M-n 24
codification.

## When NOT to use (anti-patterns)

### Anti-pattern 1: Add "end this turn"段 after commit

Per M-n 24 sub-step 1: don't add verbose ending.

### Anti-pattern 2: Add "active next plan"段 after commit

Per M-n 24 sub-step 1: plan is in PLAN file +
commit body, not in response.

### Anti-pattern 3: Ask user for trivial confirmation

Per M-n 24 sub-step 2 + M-n 21: only ask when
真歧义 (not trivially).

### Anti-pattern 4: Say "等下次 next trigger"

Per M-n 12 + M-n 24 sub-step 3: phrasing
revision.

### Anti-pattern 5: "撞到一起" without replanning

Per M-n 12: refine to "replan" with explicit
replan action.

## Relationship to other M-rules + P-n

- **M-n 12 (terminology-clarity)**: M-n 24
  sub-step 3 uses M-n 12 phrasing revisions.
- **M-n 16 (observe-think-execute)**: M-n 24
  sub-step 1 uses M-n 16 top-down 分治.
- **M-n 18 (recursive-summary-protocol)**: M-n 24
  sub-step 1 uses M-n 18 (sub-task summary in
  PLAN file).
- **M-n 21 (ask-or-infer-mark-guess)**: M-n 24
  sub-step 2 uses M-n 21 (only ask when 真歧义).
- **M-n 23 (periodic-re-analysis)**: M-n 24
  uses M-n 23 to verify plan still valid.
- **P17 老实说**: M-n 24 sub-step 2 enforces P17
  (真问题 = honest "I can't proceed because...").
- **P28 (recursion)**: M-n 24 is recursive (apply
  to itself: when modifying M-n 24, follow M-n 24).

## Self-application (per P28 recursion)

This L2 doc IS M-n 24 applied to itself:
- **Sub-step 1**: After this commit, continue
  per PLAN (c135+ audit).
- **Sub-step 2**: No 真问题, no interrupt.
- **Sub-step 3**: Default mode 主动 continue.

## Cross-references

- `OPERATING_RULES.md` § M-pace-continuity — the
  L0/L1 段 (in SUA)
- `docs/M_TERMINOLOGY_CLARITY.md` + `_DETAIL` —
  M-n 12 L2 companion (M-n 24 sub-step 3)
- `docs/M_OBSERVE_THINK_EXECUTE_DETAIL.md` —
  M-n 16 L2 companion (M-n 24 sub-step 1)
- `docs/M_RECURSIVE_SUMMARY_PROTOCOL_DETAIL.md` —
  M-n 18 L2 companion (M-n 24 sub-step 1)
- `docs/M_ASK_OR_INFER_MARK_GUESS_DETAIL.md` —
  M-n 21 L2 companion (M-n 24 sub-step 2)
- `docs/M_PERIODIC_RE_ANALYSIS_DETAIL.md` — M-n
  23 L2 companion (M-n 24 uses M-n 23)
- 你 turn 2026-07-15 — origin (你 turn explicit
  codify request)

## Changelog

- c134 (OPERATING_RULES.md): add M-n 24 段
  (summary, 3 sub-steps + 你 vision).
- c136 (this file): add L2 detail companion per
  P11 + R6 (per c127 re-analysis issue 2:
  OPERATING_RULES.md Path 1 audit found M-n 24
  missing L2).