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

## What this is NOT

- ❌ A bug report — harness works as designed
- ❌ A request for code changes — the issue is LLM, not code
- ❌ A claim that 0% KEPT is the expected rate — n=3 is too small

## What this IS

- ✅ Empirical data: harness works, LLM is probabilistic
- ✅ Confirmation that progress markers help (you saw each stage)
- ✅ Confirmation that the retry loop runs (3 attempts, not 1)
- ✅ A reminder: don't conclude from small samples
