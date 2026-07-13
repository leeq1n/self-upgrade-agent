L0: Project state — goal, current version, next step (1-paragraph).
Last P20-verified: 2026-07-13

---
description: "Project goal, status, mistakes, constraints, next step"
status: "summary"
last_updated: "2026-07-10 (v3.0.2 OVERALL COMPLETE)"
---

# PROJECT_STATE — brief

**Goal (1 sentence)**: a self-improving agent that reads papers,
modifies its own code in `core/planner.py`, verifies via the project
test suite, and either keeps or reverts.  Local framework + remote
minimax LLM API.

**Tests**: 621 PASS + 6 skip + 0 fail (last commit `2b88a79`).
*Excludes* 1 deselected test (`test_core_planner_md5_matches_head`)
because the user modified `core/planner.py` directly (LLM Round 5
KEPT, commit `20e958d`) — user decides keep/revert.

## Current status (v3.0.2 OVERALL COMPLETE)

Per LITERATURE (Self-Harness 40→62%, Lilian Weng "harness as
important as model"), v3.0.2 implements a think-execute harness:

| Module | Purpose | LOC |
|--------|---------|-----|
| `src/v3_multipaper.py` | read all 11 papers from catalog | 180 |
| `src/v3_judge.py` | LLM judge picks best paper (with mock fallback) | 265 |
| `src/v3_persist.py` | save summaries + decisions (P19) | 167 |
| `src/v3_replay.py` | inspect failures (fast, no LLM) | 81 |
| `src/v4_thinker.py` | Thinker abstract (plan API + 5 fallback paths) | 169 |
| `src/v4_executor.py` | Executor abstract (skill dispatcher) | 129 |
| `src/v4_loop.py` | Loop controller (Think → Execute → Observe) | 124 |
| `src/v2_round.py` | extended: `run_one_round_with_harness()` | 360+ |

**CLI (unified, 3 visible subcommands)**:
```bash
python -m self_upgrade improve --multi --max-retries 2 --count 5
python -m self_upgrade replay   # inspect failures (default) or --live
python -m self_upgrade test-scale 5  # N consecutive single-paper rounds
```

**Hidden aliases** (backward compat): `improve-multi`, `improve-harness`.

## Real LLM data (v3.0.2 follow-up #4 + #5)

- `--count 5` multi-paper run (commit `20e958d`): **1/5 KEPT (20%)**
- Round 5 KEPT: LLM added `generate_tests` option to `core/planner.py`
  (Self-Harness-style improvement, 16/16 tests pass)
- `core/planner.py` is LLM-modified, **user decides keep/revert**

## Mistakes made (do not repeat)

See full table in
[`PROJECT_STATE_DETAIL.md §Mistakes`](PROJECT_STATE_DETAIL.md#mistakes-made-do-not-repeat);
short version: 12 specific bugs (LLM timeout misinterpreted, key bypass
missing, hardcoded pre-filter, `git add -A` danger, retry logic
status confusion, etc.) — don't re-introduce them.

## Constraints

See [CONSTRAINTS.md](CONSTRAINTS.md) for the full list (奥卡姆,
fail-OPEN, atomic, user-edits-keys-never-agent, etc.).  Project
constraints change rarely; that file is the source of truth.

## Next step

See [../../TODO.md](../../TODO.md) for pending work.  Top priority
is **v3.0.3 — autonomous daily loop** (per user 2026-07-10
"我希望这个项目之后可以自己独立运行"):

1. **More 5-round data** — `--count 5` 拿 10+ runs 拿统计 KEPT ratio
2. **Decide `core/planner.py`** — keep (LLM 真贡献) or revert
3. **`daily-loop --interval 24h`** — autonomous, cron-driven
4. **state.json + failure recovery** (P18 + P19)
5. **Skill registry** (per LITERATURE: SkillOpt)

## References

- INDEX: [INDEX.md](INDEX.md)
- User intent (verbatim quotes): [USER_INSIGHTS.md](USER_INSIGHTS.md)
- Hard rules: [CONSTRAINTS.md](CONSTRAINTS.md)
- LLM choice: [MODEL_STRATEGY.md](MODEL_STRATEGY.md)
- Working principles: [PRINCIPLES.md](PRINCIPLES.md)
- Real-run data: [OBSERVATIONS.md](OBSERVATIONS.md)
- Pending tasks: [../../TODO.md](../../TODO.md)
- Done tasks: [../../DONE.md](../../DONE.md)
- **Detailed technical history** (the long form): [PROJECT_STATE_DETAIL.md](PROJECT_STATE_DETAIL.md)
- **Knowledge Graph (P1, deferred)**: [TODO_KNOWLEDGE_GRAPH.md](TODO_KNOWLEDGE_GRAPH.md)
