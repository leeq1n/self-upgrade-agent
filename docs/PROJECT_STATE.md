---
description: "Project goal, status, mistakes, constraints, next step"
status: "summary"
---

# PROJECT_STATE — brief

**Goal (1 sentence)**: a self-improving agent that reads papers,
modifies its own code in `core/planner.py`, verifies via the project
test suite, and either keeps or reverts.  Local framework + remote
minimax LLM API.

**Tests**: 438 PASS + 6 skip + 0 fail (last commit `9915a9e`).

**Active code** (~620 LOC across 3 modules):

- `src/v2_agent.py` — generate Patch from paper via 1 LLM call + harness
- `src/v2_apply.py` — atomically deploy Patch to source (snapshot +
  AST-based replace + revert on fail)
- `src/v2_round.py` — close the loop (improve → apply → tests → KEPT/REVERTED)

For deeper details on each module, see its module docstring + tests
(`tests/test_v2_*.py`).

**Deprecated (do not extend)**: 11 modules in `src/` are listed for
historical reasons only.  See
[`PROJECT_STATE_DETAIL.md → Deprecated modules`](PROJECT_STATE_DETAIL.md#deprecated-modules).

## Mistakes made (do not repeat)

See full table in
[`PROJECT_STATE_DETAIL.md §Mistakes`](PROJECT_STATE_DETAIL.md#mistakes-made-do-not-repeat);
short version: 8 specific bugs (LLM timeout misinterpreted, key bypass
missing, hardcoded pre-filter, etc.) — don't re-introduce them.

## Constraints

See [CONSTRAINTS.md](CONSTRAINTS.md) for the full list (奥卡姆,
fail-OPEN, atomic, user-edits-keys-never-agent, etc.).  Project
constraints change rarely; that file is the source of truth.

## Next step

See [../TODO.md](../../TODO.md) for pending work.  Top three (in
priority order):

1. **Failure → regression test pipeline** — every NO_PATCH /
   APPLY_FAILED / REVERTED outcome should become a permanent
   regression test (per production-agent literature).
2. **5 consecutive KEPT rounds** — user runs the loop repeatedly with
   FIXED_PAPER (DyLAN) to prove stability.
3. **Multi-paper reading** (5+ papers) — informs the v3.0 multi-paper
   selection design.

## References

- INDEX: [INDEX.md](INDEX.md)
- User intent (verbatim quotes): [USER_INSIGHTS.md](USER_INSIGHTS.md)
- Hard rules: [CONSTRAINTS.md](CONSTRAINTS.md)
- LLM choice: [MODEL_STRATEGY.md](MODEL_STRATEGY.md)
- Pending tasks: [../../TODO.md](../../TODO.md)
- Done tasks: [../../DONE.md](../../DONE.md)
- **Detailed technical history** (the long form): [PROJECT_STATE_DETAIL.md](PROJECT_STATE_DETAIL.md)
