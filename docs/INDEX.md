# Index — where to look
L0: Project orientation map: 8-step reading order + conditional stealth loads.
Last P20-verified: 2026-07-10

> Read this first.  Each doc is one paragraph + a pointer to details.
> Goal: 5-minute orientation, no essay-reading.

Each doc has a short form (this index) and a `_DETAIL.md`
companion for the long version.  Read summary first; click through
to detail only as needed.

| Doc (summary) | Doc (detail) | TL;DR |
| --- | --- | --- |
| [PROJECT_STATE.md](PROJECT_STATE.md) | [PROJECT_STATE_DETAIL.md](PROJECT_STATE_DETAIL.md) | Goal + current state + next step |
| [USER_INSIGHTS.md](USER_INSIGHTS.md) | [USER_INSIGHTS_DETAIL.md](USER_INSIGHTS_DETAIL.md) | Paraphrased rules; detail has verbatim quotes |
| [CONSTRAINTS.md](CONSTRAINTS.md) | [CONSTRAINTS_DETAIL.md](CONSTRAINTS_DETAIL.md) | Invariants the system must preserve |
| [MODEL_STRATEGY.md](MODEL_STRATEGY.md) | [MODEL_STRATEGY_DETAIL.md](MODEL_STRATEGY_DETAIL.md) | Which LLM, why, deployment notes |
| [LITERATURE.md](LITERATURE.md) | [LITERATURE_DETAIL.md](LITERATURE_DETAIL.md) | Papers read + how they constrain our design |
| [PRINCIPLES.md](PRINCIPLES.md) | (no detail — already portable) | Working principles — portable across projects |

## Reading order for a new agent

1. This file (INDEX.md) — 2 min
2. [PROJECT_STATE.md](PROJECT_STATE.md) — 5 min
3. [CONSTRAINTS.md](CONSTRAINTS.md) — 5 min
4. [USER_INSIGHTS.md](USER_INSIGHTS.md) (skim, focus on items dated 2026-07-08) — 10 min
5. [LITERATURE.md](LITERATURE.md) — 5 min
6. [PRINCIPLES.md](PRINCIPLES.md) — 3 min (general, not project-specific)
7. [MODEL_STRATEGY.md](MODEL_STRATEGY.md) — 3 min
8. [../TODO.md](../TODO.md) to see pending work — 2 min

Total: 35 min to full orientation.

## Conditional loads (read ONLY if relevant)

These are **stealth docs** (per P20): they have no summary, only
a pointer.  Read them only when your task matches the trigger.

- [EXTENSIONS.md](EXTENSIONS.md) — only if you're considering
  work that crosses project boundaries (e.g. starting a new
  repo, integrating with another tool, or wondering "is there
  an X for Y?")

If a section is unclear or you need full rationale, follow the
links — each summary points to its `_DETAIL.md` companion.
