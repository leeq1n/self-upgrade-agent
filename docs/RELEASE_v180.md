# v1.8.0-alpha Release Notes

> **Status**: alpha — proven but not stable
> **Date**: 2026-07-06
> **Commits**: 9 (f37e48c → 5401f0b)
> **Tag**: v1.8.0-alpha (after this commit)

---

## What is v1.8.0?

v1.8.0 is the **first release where the system has a real harness**.
In v1.7.x, "should we promote this patch?" was decided by the LLM
itself — the LLM that generated the patch also judged the patch.
That's "LLM grading LLM" — not a real verification.

In v1.8.0, "should we promote?" is decided by **two independent
signals**:

1. **Harness** (8 real Python unit tests for `core/planner.py`)
   - Run as `pytest tests/auto/test_planner_harness.py`
   - Independent of any LLM call
   - 0 LLM tokens consumed
   - If any test fails → **REVERTED, no matter what LLM says**

2. **LLM 21-task benchmark** (v1.7.x's existing path)
   - Baseline vs patched planner on 21 real tasks
   - LLM delta ≥ 5% AND cost ≤ 1.2x → candidate for promote
   - LLM delta < 5% OR cost > 1.2x → REVERTED

**Decision priority** (4-step):
```
1. harness < 100%?        → REVERTED (LLM delta is ignored)
2. LLM delta < 5%?         → REVERTED
3. LLM cost > 1.2x?         → REVERTED
4. all pass?               → KEPT (candidate for promote)
```

This is the **first time the system has a harness-first decision
process** that doesn't depend on the LLM being honest.

---

## What's new

### Harness (Day 1)
- `tests/auto/test_planner_harness.py`: 8 real Python unit tests
  - `test_plan_task_returns_list_of_strings`
  - `test_plan_task_handles_empty_task`
  - `test_plan_task_handles_very_long_input`
  - `test_plan_task_handles_unicode`
  - `test_plan_task_handles_llm_returning_nonsense`
  - `test_plan_task_handles_llm_returning_unstructured_text`
  - `test_plan_task_extracts_numbered_steps`
  - `test_plan_task_handles_special_characters`
- `src/evaluate.py:run_harness()`: runs the harness via subprocess pytest
- `src/evaluate.py:should_promote_with_harness()`: 4-step decision logic

### Pipeline integration (Day 2)
- `src/pipeline_lg.py:node_evaluate`: calls `run_harness()` while the
  patch is applied (between arm 2 and restore).  Harness result is
  included in `state["evaluation"]["harness"]`.
- `src/decide.py:make_decision`: delegates to `should_promote_with_harness`
  when `harness` key is present in `eval_data`.

### Skill lifecycle (Day 3-5)
- `src/skill_lifecycle.py:evaluate_all_skills_static`: 0-LLM skill
  quality scoring (use_count × avg_improvement).
- `src/pipeline_lg.py:node_skill_audit`: 8th node in the graph
  (after `decide`).  Reads skill_registry, computes quality scores,
  auto-culls skills with score < 0, persists to audit_history.
- `src/db.py:audit_history` table: tracks every audit run
  (n_skills, n_culled, n_kept, details_json).
- `self_upgrade audit` (7th subcommand): show audit history + run
  ad-hoc audits.

### CLI (Day 5-6)
- 7 subcommands: `run`, `evolve`, `status`, `unlock`, `cull`, `audit`, `gc`
- `self_upgrade gc`: garbage-collect cache + temp files
- `self_upgrade audit`: show audit history
- `run_1round.py`: clean wrapper for 1 round live (replaces Day 3 wrapper)
- `run_5rounds_day6.py`: 5-round stress test wrapper

---

## Live verification (5 rounds, 2026-07-06)

User ran `run_5rounds_day6.py` for 5 rounds.  Result:

| Round | Paper | Elapsed | Done | Decision | LLM Δ | Harness | Notes |
|------:|-------|--------:|:----:|:---------|------:|:-------:|-------|
| 1 | 2406.01574 Multi-Agent | 21.7s | False | None | — | — | patchgen fail |
| **2** | **2606.30639 WorldEvolver** | **164.9s** | **True** | **KEPT** | **+6.93%** | **8/8** | **REAL PROMOTE** |
| 3 | 2310.02170 AutoGen | 360.7s | True | reverted | +4.76% | 0/0 | harness missing |
| 4 | 2304.14733 Generative Agents | 375.6s | True | reverted | -4.76% | 0/0 | harness missing |
| 5 | 2210.03629 ReAct | 320.5s | True | reverted | +4.76% | 0/0 | harness missing |

- **Total elapsed**: 1243s (20.7 min)
- **Done rate**: 4/5 (80%)
- **True promote (decision=KEPT)**: 1/5 (R2 only)
- **History.db**: +4 rows
- **Audit_history**: 9 rows total
- **planner.py MD5**: stable across all 5 rounds (safety net ✓)

**Critical v1.8.0 evidence**:
- R2 had **real 21-task benchmark** + **harness 8/8** + **+6.9% LLM delta**
- That decision would have been KEPT in v1.7.x but **with no harness
  verification**.  In v1.8.0, the harness confirmed the patch didn't
  break any of 8 real Python unit tests.
- R3-R5 had `harness: 0/0` because the LLM run_all fallback path
  produced simulated data without going through real benchmark — a
  known v1.7.x fallback path that v1.8.0 should disable in the future.

---

## Known limitations (alpha status)

1. **1/5 success rate is not stable convergence.**  Need 5+ rounds of
   consecutive KEPT to call this stable.
2. **R3-R5 harness 0/0**: when the LLM benchmark fails, the fallback
   path doesn't run the harness.  v1.8.1 should always run harness
   even on LLM failure (harness is independent of LLM).
3. **`claude-*` model names in LLM_MODELS** were a real bug: the
   `claude-sonnet-4-5` and `claude-haiku-4-5` model names do NOT
   exist on `api.minimaxi.com`.  They were 401/404-ing 2-3 calls per
   round.  Fixed to `MiniMax-M3, MiniMax-M2.7, MiniMax-M2.5`.
4. **Auto-promote is off** by default.  Decision=KEPT is a candidate;
   manual approval required (`python run.py --promote <name>`).
5. **Selenium scraper is not exercised** (chromedriver is not installed
   in this environment).  arxiv API is the primary search path.

---

## What's next (v1.8.1 candidates)

1. **Always-run-harness**: even if LLM benchmark fails, harness must
   run.  This is what v1.8.0 promised but didn't deliver.
2. **Auto-promote option**: when `cfg.pipeline.auto_promote=True` and
   decision=KEPT, auto-apply the patch to `core/planner.py`.
3. **Multi-paper rounds**: instead of 1 paper per round, evaluate N
   papers and pick the best.  Reduces 1/5 noise.
4. **Stable harness for all modules**: today only `core/planner.py`
   has harness.  `core/agent.py` and `core/tools.py` need their own.
5. **Multi-MiniMax key rotation**: today uses 1 key.  5 keys would
   multiply daily quota 5x.

---

## How to use

```bash
# 1 round (recommended for daily use)
python -m self_upgrade unlock
python run_1round.py

# 5 round stress test
python -m self_upgrade unlock
python run_5rounds_day6.py

# Just audit (no LLM, 0 quota)
python -m self_upgrade audit --run
python -m self_upgrade audit --limit 5

# Garbage-collect cache
python -m self_upgrade gc
```

See `docs/CLI_GUIDE.md` for full reference.

---

## Test coverage

- **235 unit tests + 5 skip = 0 fail** (Day 6, 47.6s)
- 9 test files added/modified during v1.8.0
- 0 LLM calls during test runs (deterministic + mocked)
