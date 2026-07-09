# Index — where to look

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

## Project status (live)

- **Branch**: `v2.0.0-minimal`
- **HEAD commit**: see `git log --oneline -1`
- **Tests**: see TEST output below
- **Active code**: `src/v2_agent.py` (gen) + `src/v2_apply.py` (deploy) + `src/v2_round.py` (decide) — see [PROJECT_STATE.md §Active code](PROJECT_STATE.md)
- **deprecated code**: 11 modules — see [PROJECT_STATE_DETAIL.md §Deprecated](PROJECT_STATE_DETAIL.md#deprecated-modules)
- **Pending work**: [../TODO.md](../TODO.md)
- **Completed work**: [../DONE.md](../DONE.md)

## How the loop works (1 paragraph)

```
Paper ──> v2_agent.improve() ──> Patch ──> v2_apply.apply_patch() ──> file
                                                         |
                                                  run_project_tests()
                                                         |
                                              KEPT / REVERTED (HARD rule, not LLM)
                                                         |
                                                   RoundResult returned
```

Details: [PROJECT_STATE_DETAIL.md §How it works](PROJECT_STATE_DETAIL.md#how-it-works-data-flow).

## Recent commits (1 paragraph)

```
v2.2.0: run_one_round closes the loop (one round: gen → apply → decide)
v2.1.0: atomic apply_patch + defensive None/empty handling
v2.0.0: minimal self-improving agent (~250 LOC, 1 LLM + 1 harness)
```

Full chain: `git log --oneline -20`.

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

If a section is unclear or you need full rationale, follow the
links — each summary points to its `_DETAIL.md` companion.