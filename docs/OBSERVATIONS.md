L0: Empirical data from real LLM runs — KEPT ratios, latency, anomalies.
Last P20-verified: 2026-07-10

# Observations — empirical data from real LLM runs

> **Status**: empirical notes.  Per P17 honest reporting: data
> here may be partial / biased.  Don't draw strong conclusions
> from small samples.
>
> **Origin**: user-driven runs of
> `python -m self_upgrade improve-multi` and
> `python -m self_upgrade improve-harness` in their environment.

## 2026-07-10 — 3-round multi-paper run (harness)

**Command**:
```bash
python -m self_upgrade improve-harness --target core/planner.py
# Default: max_retries=2 (so 3 attempts total)
```

**Result**:
| Attempt | Judge winner | LLM call | Patch | Stage |
|---------|--------------|----------|-------|-------|
| 1 | self-harness (8.0s) | 99.0s | False | NO_PATCH |
| 2 | harness-engineering (14.4s) | 106.9s | False | NO_PATCH |
| 3 | self-harness (8.0s) | 24.6s | False | NO_PATCH |
| **Total** | | **~230s** | | **NO_PATCH** |

**Harness output**:
```
[261.0s] Harness done: NO_PATCH after 3 attempt(s)
decision=NO_PATCH elapsed=261.0s tests_passed=0 tests_failed=0
target=core/planner.py
error=improve() returned None — LLM did not produce valid Patch
```

**Observations**:
1. **Harness works correctly** — 3 attempts, stage markers, retry.
2. **0% KEPT** (0/3) — LLM probabilistic, all 3 attempts failed
   to produce a valid patch.
3. **Judge picks different papers** between attempts (1st and
   3rd both self-harness, 2nd harness-engineering).  LLM
   temperature is non-zero.
4. **No tests run** (patch=False) — so `tests_passed=0,
   tests_failed=0` is correct, not a bug.
5. **0% < 33% (prior single-paper 3-round run)** — but n=3 is
   too small to conclude anything statistically.

## 2026-07-10 — earlier 3-round single-paper run

**Result**: 1/3 KEPT (33%), 2/3 NO_PATCH.

**Comparison**: this run's 0% KEPT is lower, but within LLM
probabilistic noise.  Need 10+ runs to estimate KEPT ratio
reliably.

## Per LITERATURE: this is expected

- **One Step Forward, Two Steps Back** (2024): Self-Refine
  doesn't work for code gen.  We're not using Self-Refine, but
  the underlying LLM-via-prompt pattern has the same
  stochastic nature.
- **Failure-Aware Enhancements** (2024): Self-Critique 0% on
  some cases.  We're not using Self-Critique, but
  `improve() returned None` is essentially "LLM did not
  produce valid output" — the same failure mode.

## Action items (NOT yet done)

### User-side (you run)

- [ ] **5+ consecutive multi-paper runs** to estimate KEPT
      ratio reliably.  Use:
      ```bash
      python -m self_upgrade test-scale 5 --harness
      # (--harness flag not yet implemented; use improve-harness
      # in a shell loop for now)
      ```

### Code-side (out of scope per P7 奥卡姆)

- [ ] (optional) Add `save_harness_metric()` for observability.
      Per P19: persist attempt details.  Reuse v3_persist
      infrastructure.  **Defer** until we have more data.

- [ ] (optional) Improve retry policy: skip retry on NO_PATCH
      (LLM probabilistic, retry has same expected outcome).
      **Defer** until we have more data to justify the change.

## 2026-07-10 — 5-round multi-paper run (--count 5)

**Command**:
```bash
python -m self_upgrade improve-multi --count 5
# 5 consecutive rounds, --no-judge-llm not used (default = LLM judge)
```

**Result**:
| Round | Judge winner | LLM call | Patch | Result |
|-------|--------------|----------|-------|--------|
| 1 | harness-engineering (22.0s) | 115.4s | False | NO_PATCH |
| 2 | self-harness (7.6s) | 117.9s | False | NO_PATCH |
| 3 | self-harness (8.0s) | 102.6s | False | NO_PATCH |
| 4 | harness-engineering (26.1s) | 26.8s | False | NO_PATCH |
| 5 | harness-engineering (9.3s) | 97.9s | **True** | **KEPT** (16/16) |
| **Total** | | **~460s** | | **1/5 KEPT (20%)** |

**Round 5 KEPT details**:
- LLM modified `core/planner.py`: added `generate_tests: bool = False`
  parameter to `plan_task()`, which when True generates regression
  tests for each step
- 16/16 tests in `tests/test_v2_round.py` passed
- This is **Self-Harness-style** improvement (per LITERATURE:
  "Harness as important as model") — the LLM recognized that
  test generation is a valuable capability and added it

**KEPT ratio**:
- v1.8.x single-paper: 33% (1/3)
- v3.0.1 single-paper: 33% (1/3)  
- v3.0.1 multi-paper (single run): 0% (0/3)
- v3.0.2 multi-paper (single run): 0% (0/3)
- v3.0.2 multi-paper (5-round batch): 20% (1/5)

**Trend**: 20% KEPT is within expected range. n=5 is still too
small to be statistically significant. But **the LLM is producing
real improvements when it succeeds** (not just valid syntax).

**Working tree after run** (uncommitted):
- `M core/planner.py` — LLM's patch
- `M docs/INDEX.md` — possibly from another agent
- `?? docs/EXTENSIONS.md` — possibly from another agent

**Action items**:
- [ ] **User decides**: commit core/planner.py (real improvement)
      or revert (don't trust LLM changes)?
- [ ] **More 5-round runs** to get statistical signal (target n>=10)
- [ ] **Investigate** why Round 4 LLM call was so short (26.8s vs
      100s+ in other rounds) — was it cut off?

## What this is NOT

- ❌ A bug report — harness works as designed
- ❌ A request for code changes — the issue is LLM, not code
- ❌ A claim that 0% KEPT is the expected rate — n=3 is too small

## What this IS

- ✅ Empirical data: harness works, LLM is probabilistic
- ✅ Confirmation that progress markers help (you saw each stage)
- ✅ Confirmation that the retry loop runs (3 attempts, not 1)
- ✅ A reminder: don't conclude from small samples


## 2026-07-10 — daily-loop --max-rounds 3 --interval 0 (1/3 KEPT)

User ran `python -m self_upgrade daily-loop --max-rounds 3 --interval 0`
after my v3.1.0 commit (9d75533).  Output:

| Round | Round winners | KEPT? | Tests | Time |
|---|---|---|---|---|
| 1 | self-harness → self-refine → the-agent-improvement-loop (3 attempts) | No | 0/0 | 274.3s |
| 2 | harness-engineering → harness-engineering (2 attempts) | **Yes** | **16/16** | 222.3s |
| 3 | harness-engineering → the-agent-improvement-loop → harness-engineering (3 attempts) | No | 0/0 | 217.0s |

Total: 3 rounds, 1 KEPT (33%), 713.6s.

**Observations**:
- 33% KEPT (n=3) is within range of n=5=20% and n=2=0% from earlier
  runs — LLM probability, not a code issue
- Round 2 KEPT is real: 16/16 tests pass after harness retry
  (1st attempt NO_PATCH, 2nd attempt KEPT)
- **Auto-revert**: core/planner.py modified by LLM, then reverted by
  Harness atomic mechanism (per P18).  Working tree clean after
  run — NO permanent change.  (KEPT-but-not-committed = same as
  no run, from a code-state perspective.)
- Total time 12 min matches expectation (3 rounds × ~4 min avg)

**Implication for autonomous vision**:
Per user vision '我希望这个项目之后可以自己独立运行':
daily-loop currently runs rounds but does NOT auto-commit KEPT
patches.  KEPT patches are immediately auto-reverted because no
agent/user commits them.  For true autonomous improvement, the
harness should auto-commit KEPT patches (or write a patch bundle
for human review).
- This is a TODO item, not a code bug
- User decides: auto-commit or human-in-the-loop

**Related commits**:
- 9d75533 feat: autonomous daily-loop + P20 doc-only alignment
- de5213d docs(PRINCIPLES): sync L0 to P23 + R7 split-aware


## 2026-07-10 — `--auto-commit` flag added (auto vs manual boundary)

Per user 2026-07-10: '继续, 但是我觉得自动更新的和你更新的应该
区分开, 不然感觉会有些问题'.

Solution: `--auto-commit` opt-in flag on `improve` and `daily-loop`.
When set, KEPT patches auto-commit with:
- Author: `Auto Upgrade <auto@self-upgrade.local>` (distinct)
- Commit message prefix: `[auto]`
- Patch bundle: `upgrades/auto-patches/<date>-<hash>.patch`
  for human review, selective apply, rejection
- `git log --author="Auto"` filters auto commits in 1 step

Default behavior unchanged: no `--auto-commit` = file stays in
working tree (or auto-revert).  User stays in control.

**Why opt-in (not default)**:
- Per P7 奥卡姆: minimal default, opt-in for opt-out behavior
- Per P9: hard rule that user reviews KEPT patches before commit
- Per LITERATURE Signal-to-Fix Loop: deploy = patch bundle,
  not commit, unless explicitly opted in

**Bug fix in v2_round.py (pre-existing)**: fallback RoundResult
in `run_one_round_with_harness` was missing `paper` field (P9
hard rule: required field).  Now passes `paper=None` per P18
fallback pattern.
