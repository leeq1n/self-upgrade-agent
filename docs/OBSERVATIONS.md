L0: Empirical data from real LLM runs — KEPT ratios, latency, anomalies.
Last P20-verified: 2026-07-13

# Observations — empirical data from real LLM runs
> L0: Empirical observations from past runs.  Load when: debugging or wanting real-world context.

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

## Detail

Full data in `docs/OBSERVATIONS_DETAIL.md` (1882 lines).
