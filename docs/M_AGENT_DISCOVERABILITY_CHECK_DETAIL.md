# M-agent-discoverability-check (full text)
Last P20-verified: 2026-07-15

> L0: L2 detail for `OPERATING_RULES.md` § M-
> agent-discoverability-check段 (M-n 20).  Per
> P11 摘要+引用 + R6, this companion is required
> when the summary rule describes agent
> discoverability.  Load when: agent modifies
> agent 原则 / skill 原则 / skill 内容.

## Why this L2 doc exists

The OPERATING_RULES.md § M-agent-discoverability-
check段 (c116) provides the 4 sub-steps.  This
L2 doc provides decision tree, worked examples,
and how to apply across 3-project arch.

## 4 sub-steps (per M-n 20 段)

| # | Sub-step | When to apply |
|---|---|---|
| 1 | **Cross-framework check** | When modifying agent 原则 or skill 原则 |
| 2 | **Naming check** (per M-n 19) | When creating new file or path |
| 3 | **Discoverability check** (per P26) | When modifying entry files (AGENTS.md, HANDOFF.md, PROJECT_STATE.md) |
| 4 | **Memory persistence** | When codifying M-rule or P-n |

## Decision tree: when to invoke M-n 20

```
Q1: Am I modifying agent 原则 (P-n / M-n)?
├── Yes → Apply all 4 sub-steps
└── No → Q2

Q2: Am I modifying skill 原则 (skill-generation-
    knowledge / SKILL_DESIGN.md)?
├── Yes → Apply all 4 sub-steps
└── No → Q3

Q3: Am I modifying skill 内容 (skill files)?
├── Yes → Apply sub-steps 1, 2, 3 (memory
│       persistence not needed for content)
└── No → M-n 20 not applicable
```

## How to apply across 3-project arch

Per M-n 20 (per c116) + M-n 21 (cross-project):

| Project | When to invoke M-n 20 |
|---|---|
| **SUA** | Modifying P-n (in PRINCIPLES.md) or M-n (in OPERATING_RULES.md) |
| **skill-incubator** | Modifying SKILL_DESIGN.md (4 sub-knowledge areas) or when-to-incubate.md (4 conditions) |
| **agent-reflection-skill** | Modifying SKILL.md (skill entry) or framework docs (analogy-and-induction.md etc.) |

## Worked example: c117 (AGENTS.md sync)

When c117 was committed (AGENTS.md sync + M-n
12-20 + 修订 L4 boundary), M-n 20 4 sub-steps
were applied:

- **Sub-step 1 (Cross-framework)**: framework-
  agnostic claim added (Hermes/Codex/Claude
  Code).
- **Sub-step 2 (Naming)**: AGENTS.md is
  framework-agnostic file name (per M-n 19).
- **Sub-step 3 (Discoverability)**: 4 questions
  in commit body (P26 simulation 5/5 PASS).
- **Sub-step 4 (Memory)**: memory entry 7
  updated (per M-n 20 sub-step 4).

## Worked example: c119 (PROJECT_STATE.md reframe)

When c119 was committed, M-n 20 4 sub-steps were
applied:

- **Sub-step 1**: framework-agnostic claim added
  to Goal 1-sentence.
- **Sub-step 2**: PROJECT_STATE.md is framework-
  agnostic file name.
- **Sub-step 3**: P26 fresh-agent simulation
  5/5 PASS (24 P-n + 21 M-n + 修订 L4 boundary
  + framework-agnostic).
- **Sub-step 4**: memory entry 7 referenced.

## Worked example: c120 (HANDOFF.md reframe)

When c120 was committed, M-n 20 4 sub-steps were
applied:

- **Sub-step 1**: framework-agnostic claim added
  (3-project arch + Hermes/Codex/Claude Code).
- **Sub-step 2**: HANDOFF.md is framework-agnostic.
- **Sub-step 3**: P26 simulation 4/4 PASS.
- **Sub-step 4**: memory entry 7 referenced.

## Worked example: c129 (M-n 19 L2 companion)

When c129 was committed, M-n 20 was applied
indirectly (via M-n 19 + P11 + R6):

- **Sub-step 1**: M_FILE_NAMING_CONVENTION_DETAIL.md
  is framework-agnostic (no Hermes-specific
  terms).
- **Sub-step 2**: File follows M-n 19 Convention 3
  (M_<NAME>_DETAIL.md).
- **Sub-step 3**: 4 questions in commit body
  (P26 simulation 5/5 PASS).
- **Sub-step 4**: memory entry 7 referenced.

## When NOT to use (anti-patterns)

### Anti-pattern 1: Don't skip sub-step 1 (cross-framework)

If file/rule is Hermes-only, explicitly mark it
as such (don't pretend framework-agnostic).

### Anti-pattern 2: Don't skip sub-step 3 (discoverability)

P26 simulation is required for entry file
changes.  Without simulation, 新 agents miss
critical context.

### Anti-pattern 3: Don't skip sub-step 4 (memory persistence)

Per 你 turn "这条需要记", memory persistence is
critical for cross-session continuity.

### Anti-pattern 4: Don't modify agent 原则 without M-n 20

If agent 原则 (P-n / M-n) is modified without M-n
20, 新 agents may have outdated knowledge.

### Anti-pattern 5: Don't skip P26 fresh-agent simulation

Per M-n 20 sub-step 3, P26 simulation (4
questions) is required for entry file changes.

## Relationship to other M-rules + P-n

- **M-n 17 (context-freshness-check)**: M-n 20
  sub-step 3 uses M-n 17 Path 1 (intra-agent
  re-read).
- **M-n 18 (recursive-summary-protocol)**: M-n 20
  sub-step 4 uses M-n 18 (sub-task summary in
  PLAN file).
- **M-n 19 (file-naming-convention)**: M-n 20
  sub-step 2 uses M-n 19 (4 conventions).
- **M-n 22 (3w1h-think-first)**: M-n 20 applies
  to 3W1H Who (新 agents affected).
- **M-n 23 (periodic-re-analysis)**: M-n 20
  applies to M-n 23 sub-step 2 (compare to
  当前 state).
- **P17 老实说**: M-n 20 sub-step 4 enforces P17
  (memory persistence).
- **P26 fresh-agent discoverability**: M-n 20
  sub-step 3 applies P26.
- **P28 (recursion)**: M-n 20 is recursive
  (apply to itself: when modifying M-n 20,
  apply M-n 20 4 sub-steps).

## Self-application (per P28 recursion)

This L2 doc IS M-n 20 applied to itself:
- **Sub-step 1**: M_AGENT_DISCOVERABILITY_CHECK_DETAIL.md
  is framework-agnostic (no Hermes-specific
  terms).
- **Sub-step 2**: File follows M-n 19 Convention
  3 (M_<NAME>_DETAIL.md).
- **Sub-step 3**: 4 questions in commit body
  (P26 simulation 5/5 PASS).
- **Sub-step 4**: memory entry 7 referenced.

## Cross-references

- `OPERATING_RULES.md` § M-agent-discoverability-
  check — the L0/L1 段 (in SUA)
- `docs/M_FILE_NAMING_CONVENTION_DETAIL.md` —
  M-n 19 L2 companion (M-n 20 sub-step 2)
- `docs/M_CONTEXT_FRESHNESS_CHECK_DETAIL.md` —
  M-n 17 L2 companion (M-n 20 sub-step 3)
- `docs/M_RECURSIVE_SUMMARY_PROTOCOL_DETAIL.md` —
  M-n 18 L2 companion (M-n 20 sub-step 4)
- `AGENTS.md` — entry file (M-n 20 sub-step 3)
- `docs/PROJECT_STATE.md` — entry file (M-n 20
  sub-step 3)
- `docs/HANDOFF.md` — entry file (M-n 20 sub-step
  3)
- 你 turn 2026-07-15 — origin (你 ask 我
  verification request)

## Changelog

- c116 (OPERATING_RULES.md): add M-n 20 段
  (summary, 4 sub-steps).
- c130 (this file): add L2 detail companion
  per P11 + R6 (per c127 re-analysis issue 1:
  M-n 19-23 missing L2 companions).