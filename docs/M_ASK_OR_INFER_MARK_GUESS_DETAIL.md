# M-ask-or-infer-mark-guess (full text)
Last P20-verified: 2026-07-15

> L0: L2 detail for `OPERATING_RULES.md` § M-
> ask-or-infer-mark-guess段 (M-n 21).  Per P11
> 摘要+引用 + R6, this companion is required
> when the summary rule describes decision-
> making under uncertainty.  Load when: agent
> uncertain about what / why / whether.

## Why this L2 doc exists

The OPERATING_RULES.md § M-ask-or-infer-mark-
guess段 (c118) provides the 3 sub-steps.  This
L2 doc provides decision tree, worked examples,
and how to apply across 3-project arch.

## 3 sub-steps (per M-n 21 段)

| # | Sub-step | When to apply |
|---|---|---|
| 1 | **问 (ask)** | When agent uncertain, before action |
| 2 | **推理 (infer)** | When user no-response OR insufficient |
| 3 | **标注 猜测 (mark guess)** | Always when inference used (per P17 老实说) |

## Decision tree: when to invoke M-n 21

```
Q1: Am I uncertain about what / why / whether?
├── No → M-n 21 not applicable
└── Yes → Q2

Q2: Have I asked user yet (per sub-step 1)?
├── No → Ask via clarify tool or direct question
│       (sub-step 1: 问)
└── Yes → Q3

Q3: Did user respond sufficiently?
├── Yes → Proceed with user-specified action
└── No → Q4

Q4: Apply 类比 + 逻辑 reasoning (per M-n 14)
    (sub-step 2: 推理)
    │
    ├── Found similar prior pattern → Use it
    └── No prior pattern → Q5

Q5: Mark action as "猜测" or "inferred, unverified"
    (sub-step 3: 标注 猜测)
    Per P17: never claim green when yellow
```

## How to apply across 3-project arch

Per M-n 21 (per c118) + M-n 14 (类比+逻辑):

| Project | When to invoke M-n 21 |
|---|---|
| **SUA** | When modifying P-n/M-n and uncertain about rationale or scope |
| **skill-incubator** | When designing new skill and uncertain about 4 conditions |
| **agent-reflection-skill** | When extending primitive and uncertain about framework-agnostic claim |

## Worked example: c118 (M-n 21 codify)

When M-n 21 was codified (c118), the 3 sub-
steps were applied:

- **Sub-step 1 (问)**: 你 turn explicit codify
  request → no clarify needed
- **Sub-step 2 (推理)**: M_RULE_AUTHORING gate
  (4 observed cases: c86-r87 + c106-c117 anti-
  examples + 你 turn)
- **Sub-step 3 (标注 猜测)**: not needed (你 turn
  explicit, not a guess)

This demonstrates M-n 21 applied to itself.

## Worked example: c119 (PROJECT_STATE.md reframe)

When c119 was committed, M-n 21 was applied:

- **Sub-step 1**: 你 turn "继续按规划推进任务" =
  directive, no clarify
- **Sub-step 2**: 类比 c117 AGENTS.md + M-n 14
  (类比 Track 1)
- **Sub-step 3**: 推理 was inferred (based on
  M-n 20 + M-n 14 类比), commit body marked
  "this 推理 is inferred (标注 猜测)"

This demonstrates M-n 21 in action.

## Worked example: c127 (M-n 23 re-analysis)

When M-n 23 was codified (c127), M-n 21 was
applied:

- **Sub-step 1**: 你 turn "如果做了很久, 重新
  分析" = directive, no clarify
- **Sub-step 2**: 类比 to M-n 15 (principle-
  reordering) + M-n 17 (context-freshness-check)
- **Sub-step 3**: not needed (M_RULE_AUTHORING
  gate met, 4 observed cases explicit)

This demonstrates M-n 21 + M-n 23 + M-n 15
composition.

## Worked example: c130 (M-n 20 L2)

When M-n 20 L2 was created (c130), M-n 21 was
applied to verification (你 turn):

- **Sub-step 1**: 你 turn "对吧？" = verification
  request
- **Sub-step 2**: M-n 17 Path 1 (intra-agent
  re-read) to verify M-n 20 4 sub-steps
- **Sub-step 3**: 0 标注 猜测 (this is
  verification, not inference)

This demonstrates M-n 21 applied to verification.

## When NOT to use (anti-patterns)

### Anti-pattern 1: Skip sub-step 1 (ask trivially)

Don't ask when answer is obvious (e.g., file
path query).  Per M-n 21: "Don't ask trivially
(only 真歧义)".

### Anti-pattern 2: Skip sub-step 2 (infer without reasoning)

Don't jump from "no answer" to "guess" without
applying 类比+逻辑 reasoning.  Per M-n 14: both
tracks required.

### Anti-pattern 3: Skip sub-step 3 (mark guess without disclosure)

Don't claim certainty when uncertain.  Per P17
老实说: never claim green when yellow.

### Anti-pattern 4: Always ask (over-ask)

If user explicit, no need to ask.  Per M-n 21:
clarify only 真歧义.

### Anti-pattern 5: Never mark guess (over-confidence)

If inferred, must mark "猜测" or "inferred,
unverified".  Per P17 老实说.

## Relationship to other M-rules + P-n

- **M-n 14 (two-track reasoning)**: M-n 21 sub-
  step 2 uses M-n 14 (类比+逻辑).
- **M-n 16 (observe-think-execute)**: M-n 21
  top-down 默认 applies M-n 16 stage 3.
- **M-n 18 (recursive-summary-protocol)**: M-n
  21 sub-step 3 uses M-n 18 (sub-task summary).
- **M-n 22 (3w1h-think-first)**: M-n 21 sub-
  step 2 (推理) aligns with M-n 22 Why dimension.
- **P17 老实说**: M-n 21 sub-step 3 enforces P17.
- **P28 (recursion)**: M-n 21 is recursive
  (apply to itself).

## Self-application (per P28 recursion)

This L2 doc IS M-n 21 applied to itself:
- **Sub-step 1**: 你 turn explicit directive →
  no clarify
- **Sub-step 2**: 类比 to c118 + c119 + c127
  + c130 worked examples
- **Sub-step 3**: not needed (M_RULE_AUTHORING
  gate met, 4 observed cases)

## Cross-references

- `OPERATING_RULES.md` § M-ask-or-infer-mark-guess
  — the L0/L1 段 (in SUA)
- `docs/M_TWO_TRACK_REASONING_DETAIL.md` —
  M-n 14 L2 companion (M-n 21 sub-step 2)
- `docs/M_OBSERVE_THINK_EXECUTE_DETAIL.md` —
  M-n 16 L2 companion (M-n 21 top-down 默认)
- `docs/M_RECURSIVE_SUMMARY_PROTOCOL_DETAIL.md` —
  M-n 18 L2 companion (M-n 21 sub-step 3)
- `docs/M_3W1H_THINK_FIRST_DETAIL.md` (future,
  c132) — M-n 22 L2 companion
- 你 turn 2026-07-15 — origin (你 turn explicit
  codify request)

## Changelog

- c118 (OPERATING_RULES.md): add M-n 21 段
  (summary, 3 sub-steps + top-down 默认).
- c131 (this file): add L2 detail companion
  per P11 + R6 (per c127 re-analysis issue 1:
  M-n 19-23 missing L2 companions).