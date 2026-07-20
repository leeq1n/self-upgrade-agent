# 9 primitives (5 constructive + 4 critical) — Phase A record

> L0: Per Phase A codification (commits 35a25d3 through
> 6a26b7c, tag `v2.0.0-critical-thinking-injection`).
> Per user message 2026-07-16 + M-n 14 two-track-reasoning.

## What changed (per Phase A)

Phase A injected 4 critical-thinking primitives into
SUA's thinking framework.  Before Phase A:
- 5 constructive primitives (Analyze / Reason /
  联想 / 归纳 / 总结)

After Phase A:
- **5 constructive primitives** (existing)
- **4 critical-thinking primitives** (new M-n 35):
  - **质疑 (Challenge)** — what's uncertain / wrong
  - **逆向 (Invert)** — what if OPPOSITE were true
  - **预演失败 (Pre-mortem)** — "this FAILED in 30
    days, why?" (Klein 2007)
  - **对立论证 (Steelman-the-opposite)** —
    construct strongest case AGAINST
- **9 primitives total** (5 + 4 = M-n 14 two-track pair)

## Integration points (committed in Phase A)

| # | Repo | Commit | Content |
|---|---|---|---|
| 1 | SUA | 35a25d3 | docs/M_CRITICAL_THINKING_PRIMITIVES_DETAIL.md |
| 2 | SUA | f0ba8b7 | M_ACCEPTANCE_PROTOCOL Step 2 add 4 critical |
| 3 | SUA | d31e9de | AGENTS.md Task-done reminder 4 critical |
| 4 | SUA | b3b56a1 | m_n29_5step.py add Step 2a |
| 5 | SUA | 80cad53 | prepare-commit-msg add 4 ct keyword check |
| 6 | SUA | 411e043 | VERIFICATION add 9-primitives 段 |
| 7 | SUA | c6fbdf8 | INDEX add M-n 35 row |
| 8 | SUA | 6a26b7c | AGENTS.md Read first item 9 = ct detail |
| 9 | skill | ba3376e | VERIFICATION add 4 ct cross-ref |
| 10 | skill-incubator | f3b4f5d | VERIFICATION add 4 ct cross-ref |
| 11 | KG | 9395424 | VERIFICATION add 4 ct cross-ref |

## Default-on / Optional / Skip boundaries

- **Default-on** (apply all 4 critical-thinking):
  - High-stakes commits (architecture / cross-project /
    new P-n or M-n lifts)
  - Before claiming task done
- **Optional** (apply 质疑 + 预演失败 minimum):
  - Single-file refactors
- **Skip** (apply 5 constructive only):
  - Trivial fixes (typo / formatting)
  - Emergency hotfixes (per 你 directive)

## Why this is in 核心 layer

Per user message 2026-07-16 3-layer architecture:
- 核心 layer = agent behavior + skill behavior rules
- 修改 governance: agent-self-edit only with eval-
  before + verify-after gate
- This 9-primitives record IS core layer content
  (defines thinking methodology that applies to
  all agent actions)

## Tag

`v2.0.0-critical-thinking-injection` (commit 6a26b7c)

## P-n / M-n cited

P11 (摘要+引用), P14 (docs stay current), P17
(老实说), P22 (when stuck→plan), P25 (post-modify
re-apply), P29 (recursion).

M-n 14 (two-track-reasoning), M-n 28 (plan-
conditional), M-n 29 (acceptance-protocol),
M-n 32 (self-learning-guardrail Guardrail #1+5),
M-n 34 (pre-task scan), M-n 35 (4 critical-
thinking primitives).
