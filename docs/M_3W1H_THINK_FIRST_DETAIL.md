# M-3w1h-think-first (full text)
Last P20-verified: 2026-07-15

> L0: L2 detail for `OPERATING_RULES.md` § M-
> 3w1h-think-first段 (M-n 22).  Per P11 摘要+引用
> + R6, this companion is required when the
> summary rule describes decision-making
> framework.  Load when: agent needs to make
> major decision or analysis.

## Why this L2 doc exists

The OPERATING_RULES.md § M-3w1h-think-first段
(c122) provides the 3W1H framework.  This L2
doc provides decision tree, worked examples,
and how to apply across 3-project arch.

## 4 dimensions of 3W1H (per M-n 22 段)

| # | 3W1H | Question | 中文 |
|---|---|---|---|
| 1 | **What** | What is the problem / task? | 什么 |
| 2 | **Why** | Why is this important / rationale? | 为什么 |
| 3 | **Who** | Who is involved / affected? | 谁 |
| 4 | **How** | How to approach / execute? | 怎么 |

## Decision tree: when to invoke M-n 22

```
Q1: Am I about to make a major decision?
├── No → M-n 22 not strictly applicable
└── Yes → Apply 3W1H FIRST, then top-down

3W1H sequence (per M-n 22):
1. What?  (clarify problem)
2. Why?   (clarify rationale, per M-n 21)
3. Who?   (clarify stakeholders, per M-n 20)
4. How?   (high-level approach, per M-n 16)

Then top-down 分治 (per M-n 16 stage 3):
- 目标 (per 3W1H What)
- 倒推 节点 (per 3W1H How)
- 分治 拆解 (per 3W1H How)
- 做下去 (per 3W1H How)
```

## How to apply across 3-project arch

Per M-n 22 (per c122) + M-n 21 (sub-step 2):

| Project | When to invoke M-n 22 |
|---|---|
| **SUA** | Before modifying P-n/M-n, before declaring "all pass" |
| **skill-incubator** | Before designing new skill, before 4 conditions check |
| **agent-reflection-skill** | Before extending primitive, before framework-agnostic claim |

## Worked example: c122 (M-n 22 codify)

When M-n 22 was codified (c122), 3W1H was
applied first:

- **What**: Codify 3W1H 分析法 BEFORE top-down
- **Why**: Per 你 turn "自顶向下之前, 往上思考
  一步"
- **Who**: Agent (any framework) doing major
  decision
- **How**: M-n 16 stage 3 (top-down 分治) +
  M-n 18 (sub-task summary)

This demonstrates M-n 22 + M-n 21 (Why 推理)
composition.

## Worked example: c127 (M-n 23 re-analysis)

When M-n 23 was codified (c127), M-n 22 was
applied:

- **What**: Codify M-periodic-re-analysis
- **Why**: Per 你 turn "如果做了很久, 重新分析"
- **Who**: Agent (me) + future agents
- **How**: 3 sub-steps (re-analyze / compare /
  plan) + M-n 16 top-down

This demonstrates M-n 22 + M-n 23 (3W1H +
periodic re-analysis) composition.

## Worked example: c131 (M-n 21 L2 companion)

When M-n 21 L2 was created (c131), M-n 22 was
applied:

- **What**: M_ASK_OR_INFER_MARK_GUESS_DETAIL.md
- **Why**: Per c127 re-analysis issue 1 (M-n
  19-23 missing L2)
- **Who**: Future agents (per M-n 20)
- **How**: 1 file new + 1 file edit (per M-n 16
  top-down)

This demonstrates M-n 22 systematic application.

## Worked example: c130 (verification request)

When c130 was committed, M-n 22 was applied to
你 turn verification request:

- **What**: 你 ask 我 确认 M-n 20 已 codified +
  apply
- **Why**: Verification request
- **Who**: 你 (verify) + me (confirm)
- **How**: M-n 17 Path 1 (intra-agent re-read)
  to audit M-n 20 4 sub-steps

This demonstrates M-n 22 applied to verification.

## When NOT to use (anti-patterns)

### Anti-pattern 1: Skip 3W1H, go directly to top-down

Per 你 turn: "需要往上思考一步".  Don't skip
the 3W1H abstract level.

### Anti-pattern 2: Answer 3W1H trivially

Don't say "What: stuff" without specifics.
3W1H must be concrete.

### Anti-pattern 3: Confuse 3W1H (abstract) with top-down (concrete)

3W1H is "above" (per 你 turn), top-down is
"below".  Different abstraction levels.

### Anti-pattern 4: Apply 3W1H AFTER top-down

3W1H must be BEFORE top-down (per 你 turn +
M-n 22 sequence).

### Anti-pattern 5: Apply 3W1H only for explicit plans

Per M-n 22 "Top-down 默认": apply M-n 22
always, not just for explicit plans.

## Relationship to other M-rules + P-n

- **M-n 16 (observe-think-execute)**: M-n 22
  applies BEFORE M-n 16 stage 3 (top-down 分治).
- **M-n 21 (ask-or-infer-mark-guess)**: M-n 22
  Why aligns with M-n 21 sub-step 2 (推理).
- **M-n 23 (periodic-re-analysis)**: M-n 22
  sub-step 1 uses M-n 23 (re-analyze at 最终
  目标).
- **P17 老实说**: M-n 22 3W1H answers must
  follow P17 (老实说).
- **P28 (recursion)**: M-n 22 is recursive
  (apply to itself: when modifying M-n 22,
  apply M-n 22 3W1H).

## Self-application (per P28 recursion)

This L2 doc IS M-n 22 applied to itself:
- **What**: M_3W1H_THINK_FIRST_DETAIL.md
- **Why**: Per c127 re-analysis issue 1
- **Who**: Future agents (per M-n 20)
- **How**: 1 file new + 1 file edit (per M-n
  16 top-down)

## Cross-references

- `OPERATING_RULES.md` § M-3w1h-think-first —
  the L0/L1 段 (in SUA)
- `docs/M_OBSERVE_THINK_EXECUTE_DETAIL.md` —
  M-n 16 L2 companion (M-n 22 How applies M-n
  16)
- `docs/M_ASK_OR_INFER_MARK_GUESS_DETAIL.md` —
  M-n 21 L2 companion (M-n 22 Why aligns with
  M-n 21)
- `docs/M_PERIODIC_RE_ANALYSIS_DETAIL.md` (future,
  c133) — M-n 23 L2 companion (M-n 22 sub-step
  1)
- 你 turn 2026-07-15 — origin (你 turn explicit
  codify request)

## Changelog

- c122 (OPERATING_RULES.md): add M-n 22 段
  (summary, 3W1H + top-down sequence).
- c132 (this file): add L2 detail companion
  per P11 + R6 (per c127 re-analysis issue 1:
  M-n 19-23 missing L2 companions).