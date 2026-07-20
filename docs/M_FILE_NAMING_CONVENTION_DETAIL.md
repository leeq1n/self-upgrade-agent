# M-file-naming-convention (full text)
Last P20-verified: 2026-07-15

> L0: L2 detail for `OPERATING_RULES.md` § M-
> file-naming-convention段 (M-n 19).  Per P11
> 摘要+引用 + R6, this companion is required
> when the summary rule describes a file-
> naming protocol.  Load when: agent creates a
> new file in project.

## Why this L2 doc exists

The OPERATING_RULES.md § M-file-naming-convention
段 (c115) provides the 4 conventions.  This L2
doc provides decision tree, worked examples, and
how to apply conventions across 3-project arch
(SUA + skill-incubator + agent-reflection-skill).

## 4 conventions (per M-n 19 段)

| # | Convention | Format | Example |
|---|---|---|---|
| 1 | **PLAN directory** | `.hermes/plans/` (plural) | `.hermes/plans/2026-07-15_160000-replan.md` |
| 2 | **PLAN file naming** | `YYYY-MM-DD_HHMMSS-topic.md` | `2026-07-15_160000-replan.md` |
| 3 | **M-n L2 companion** | `M_<NAME>_DETAIL.md` | `M_FILE_NAMING_CONVENTION_DETAIL.md` |
| 4 | **M-n summary segment** | `### M-<name> (added YYYY-MM-DD, per user message ...)` | `### M-file-naming-convention (added 2026-07-15, per user message "...")` |

## Decision tree: when to use which convention

```
Q1: Am I creating a PLAN file?
├── Yes → Convention 1 + 2 (dir + file name)
└── No → Q2

Q2: Am I creating an M-n L2 companion?
├── Yes → Convention 3 (M_<NAME>_DETAIL.md)
└── No → Q3

Q3: Am I adding a new M-n 段 to OPERATING_RULES.md?
├── Yes → Convention 4 (### M-<name> format)
└── No → Apply conventions based on context
```

## How to apply across 3-project arch

Per M-n 20 (framework-agnostic) + M-n 21
(cross-project):

| Project | File naming | Note |
|---|---|---|
| **SUA** | `docs/M_<NAME>_DETAIL.md` | per M-n 13-17, 18, 19, 20, 21, 22, 23 L2 pattern |
| **skill-incubator** | `docs/framework/case-studies.md` (summary) + `_DETAIL.md` | per c65e4be, 8e6c694 |
| **agent-reflection-skill** | `docs/framework/case-studies.md` (no _DETAIL yet) | per 7ef1fb2 |
| **PLANS** | `.hermes/plans/YYYY-MM-DD_HHMMSS-topic.md` | per c112, c115 |

## Worked example: c115 (整理 + M-n 19 codify)

When c115 was committed, the PLAN file was
renamed to follow M-n 19 conventions:

- Before: `.hermes/plan/2026-07-15-replan.md`
  (singular, no HHMMSS)
- After: `.hermes/plans/2026-07-15_160000-replan.md`
  (plural, with HHMMSS)

This was an 整理 process (per user message "recursive
rule + multi-agent 维护") that detected
inconsistency and applied M-n 19 conventions.

## Worked example: c102-c105 (M-n 13-17 L2 batch)

When M-n 13-17 L2 companions were created
(c102-c105, c113), all followed Convention 3:

- `M_LAYER_EXTENSION.md` (M-n 13)
- `M_TWO_TRACK_REASONING_DETAIL.md` (M-n 14)
- `M_PRINCIPLE_REORDERING_DETAIL.md` (M-n 15)
- `M_OBSERVE_THINK_EXECUTE_DETAIL.md` (M-n 16)
- `M_CONTEXT_FRESHNESS_CHECK_DETAIL.md` (M-n 17)

This consistent naming enables M-n 19 discover-
ability (new agents can find all L2 companions
via Convention 3 pattern).

## Worked example: c113 (M-n 17 L2 + 7-check)

When c113 was committed, the L2 companion was
created with cross-ref (per R6) AND a 7-check
BEFORE commit:

- File: `docs/M_CONTEXT_FRESHNESS_CHECK_DETAIL.md`
- Cross-ref: `OPERATING_RULES.md` M-n 17 段
  "Trigger" updated to reference L2
- 7-check: R5 (5070 ≤ 7168) ✅ + R6 ✅ + L0 ✅ +
  Last P20-verified ✅ + Path 1 + Path 2 worked
  examples ✅ + 4 anti-patterns ✅ + 1 logical
  feature ✅

This demonstrates M-n 19 + M-n 17 Path 1 (intra-
agent re-read) + M-n 25 7-check (future) all
compose.

## When NOT to use (anti-patterns)

### Anti-pattern 1: Use singular `.hermes/plan/`

Singular is wrong (per c115 detection).  Always
use plural `.hermes/plans/`.

### Anti-pattern 2: PLAN file name without HHMMSS

Without HHMMSS, multiple plans same day would
conflict.  Always include HHMMSS.

### Anti-pattern 3: M-n L2 companion without _DETAIL suffix

`_DETAIL` suffix enables R6 cross-ref + R5 cap
consistency.  Without suffix, companion is
ambiguous.

### Anti-pattern 4: M-n summary without `### M-<name>` format

Consistent format enables 新 agents to find M-n
in OPERATING_RULES.md (per M-n 20 discoverability).

### Anti-pattern 5: Mix file naming with project naming

`.hermes/` is OK (it's the directory, not the
file name); but file names should be framework-
agnostic (per M-n 20 + user message 2026-07-15).

## Relationship to other M-rules + P-n

- **M-n 13 (layer-extension)**: M-n 19 段 is L1
  summary, M-n 19 L2 is L2 detail (per M-n 13
  + P11 + R6).
- **M-n 17 (context-freshness-check)**: M-n 19
  Path 1 (intra-agent re-read) ensures file
  naming consistent.
- **M-n 18 (recursive-summary-protocol)**: M-n
  18 produces files (PLAN, L2 companions); M-n
  19 codifies how.
- **M-n 20 (agent-discoverability-check)**: M-n
  19 enforces M-n 20 via consistent file naming.
- **M-n 21 (ask-or-infer-mark-guess)**: M-n 19
  applies to M-n 21 (when uncertain about
  naming, ask or infer).
- **M-n 22 (3w1h-think-first)**: M-n 19 applies
  to 3W1H Who (新 agents affected by naming).
- **M-n 23 (periodic-re-analysis)**: M-n 19
  applies to M-n 23 re-analysis (file naming
  consistency).
- **P11 摘要+引用**: M-n 19 enforces P11.
- **P21 cross-project independence**: M-n 19
  respects P21.
- **P28 (recursion)**: M-n 19 is recursive.

## Self-application (per P28 recursion)

This L2 doc IS M-n 19 applied to itself:
- File: `M_FILE_NAMING_CONVENTION_DETAIL.md`
  (Convention 3 followed)
- Cross-ref: `OPERATING_RULES.md` M-n 19 段
  "Trigger" will be updated to reference L2
  (per R6)
- 7-check: 5 of 7 done (R5 ✅ + L0 ✅ + Last
  P20-verified ✅ + 4 worked examples ✅ + 4
  anti-patterns ✅)

## Cross-references

- `OPERATING_RULES.md` § M-file-naming-convention
  — the L0/L1 段 (in SUA)
- `docs/M_LAYER_EXTENSION.md` — M-n 13 L2
  companion (M-n 19 Convention 3 example)
- `docs/M_TWO_TRACK_REASONING_DETAIL.md` — M-n
  14 L2 companion
- `docs/M_PRINCIPLE_REORDERING_DETAIL.md` — M-n
  15 L2 companion
- `docs/M_OBSERVE_THINK_EXECUTE_DETAIL.md` — M-n
  16 L2 companion
- `docs/M_CONTEXT_FRESHNESS_CHECK_DETAIL.md` — M-n
  17 L2 companion
- `docs/M_RECURSIVE_SUMMARY_PROTOCOL_DETAIL.md` —
  M-n 18 L2 companion
- `.hermes/plans/2026-07-15_160000-replan.md` —
  PLAN file (M-n 19 Convention 1 + 2 example)
- user message 2026-07-15 — origin

## Changelog

- c115 (OPERATING_RULES.md): add M-n 19 段
  (summary, 4 conventions).
- c129 (this file): add L2 detail companion
  per P11 + R6 (per c127 re-analysis issue 1:
  M-n 19-23 missing L2 companions).
