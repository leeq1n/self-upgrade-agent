# Self-Upgrade Agent — System Constraints

> **What MUST hold**, derived from real failures observed during
> v1.5.0 → v1.7.2 development.  These are *invariants* — the
> system is allowed to behave however it wants as long as these
> remain true.

This document is the **contract** for the self-upgrade loop.  Every
change should preserve these.  If you intentionally break one, write
down why in the commit message and add a new issue.

---

## C1. `core/planner.py` MD5 stability across rounds

**Rule**: After every `pipeline.run()` call (success or failure,
graceful exit or SIGTERM), the byte content of `core/planner.py`
must be **identical** to `git ls-tree HEAD core/planner.py`
(LF-normalized, since git stores LF but working tree has CRLF on
Windows).

**Why it matters**: This file is the **primary target for
self-improvement**.  A self-upgrade agent that corrupts its own
planner defeats its own purpose.  Also, `core/agent.py` imports
`plan_task` at module-load time, so a syntactically broken planner
**crashes the whole agent**.

**Failure mode this guards against**:
- `node_evaluate` runs an A/B benchmark that surgically applies a
  candidate patch to `core/planner.py`, then runs `upgraded`
  trials.  If the process is killed between the patched-file write
  and the `finally: shutil.move(bak_path, orig_path)` restore,
  `core/planner.py` stays patched.
- v1.7.1 之前 this happened once during stress testing:
  `core/planner.py` was left at 2928 bytes (patched version) and
  only `git checkout HEAD -- core/planner.py` fixed it.

**Mitigations in place**:
- `src/pipeline_lg._safety_restore_planner()`: called at the start
  of `node_evaluate`.  Compares working tree to HEAD; if dirty,
  runs `git checkout HEAD -- core/planner.py`.
- `tests/test_bloat_invariants.py::test_core_planner_md5_matches_head`:
  invariant test that runs on every `pytest`.
- `tests/test_safety_restore_planner_idempotent`: verifies the
  safety net works.

**How to verify**:
```bash
pytest tests/test_bloat_invariants.py -v
# or manually:
md5sum core/planner.py  # if on a system with md5sum
python -c "import hashlib, subprocess; print(hashlib.md5(open('core/planner.py','rb').read().replace(b'\r\n',b'\n')).hexdigest())"
# then compare to git:
git ls-tree HEAD core/planner.py
```

---

## C2. Recoverable from any tagged version

**Rule**: At any point, `git checkout v1.7.1 -- core/planner.py`
(or `v1.7.0`, `v1.6.0`) must restore a working, importable
planner.  This means **every tag in the repo** must point to a
planner that:
- Has `def plan_task(task, llm_call) -> List[str]` as a public function
- Passes the existing `tests/test_planner.py` (or equivalent)
- Does not depend on modules not in the tag's tree

**Why it matters**: The whole point of having git tags is to give
the user a known-good escape hatch.  If a tag is broken, the user
has no way to recover from a corrupted state.

**Failure mode this guards against**:
- Tagging a commit that "passed tests" but used a renamed function
  or added a missing import.
- Tagging a commit that depends on `src/llm.py` in a state that
  was later refactored.

**How to verify**:
```bash
git checkout v1.7.1 -- core/planner.py
python -c "from core.planner import plan_task; print(plan_task('test', lambda p: '1.\n2.\n3.'))"
# Should print: ['1.', '2.', '3.']
```

---

## C3. Bounded growth of `upgrades/`

**Rule**: After N pipeline runs (N ≥ 10), the total size of
`upgrades/` and the row count of `upgrades/history.db` should be
**predictable and bounded**.

Empirically (from v1.7.2 stress test):
- `upgrades/arxiv_cache/`: **grows by ≤ 2 files per real round**
  (only papers actually fetched).  Observed 13 files / 330 KB after
  multiple rounds; expect ~13 + 2N files after N rounds.
- `upgrades/history.db`: **grows by 1 row per pipeline.run()**,
  regardless of success.  ~200 bytes per row.
- `upgrades/manifest.json`: grows by 1 entry per non-reverted
  outcome (rare — v1.5.0 has 1 entry, v1.7.2 has 0).
- `upgrades/snapshots/`: grows by 1 file per non-reverted outcome.

**Why it matters**: The user said "我担心系统越来越臃肿".  This
constraint makes "bloat" measurable.  A system with `upgrades/`
growing 10x per week is buggy; one growing linearly is fine.

**How to verify**:
```bash
pytest tests/test_bloat_invariants.py::test_history_db_is_well_formed_sqlite -v
du -sh upgrades/
sqlite3 upgrades/history.db "SELECT COUNT(*) FROM upgrades"
```

**Operational note**: For long-running deployments, archive
`history.db` monthly:
```bash
mv upgrades/history.db upgrades/history_archive_$(date +%Y%m).db
# history.db will be re-created on next pipeline run
```

---

## C4. Quota-aware operation

**Rule**: The system must not consume LLM API quota faster than
the user expects.  Concretely:
- 1 `pipeline.run()` round with `trials_per_test=1` uses **~50
  ModelScope calls** (filter 1 + patchgen 1 + reflect 3 + evaluate
  42 + decide 0 = 47).
- 8 ModelScope keys at ~200-500 calls/day each = **~1600-4000
  calls/day total**.
- Therefore: **maximum 30 rounds/day** of real LLM end-to-end,
  with 60-75s inter-round wait to avoid RPM rate limits.

**Why it matters**: The user explicitly said
"使用modelscope key一定要谨慎,每天是限额的,每天测试几轮就不够用了吧?"
on 2026-07-02.  This is a hard operational constraint, not a
preference.

**Failure modes this guards against**:
- Stress tests that run 10 rounds in a row and exhaust the daily
  quota, making the system useless for the rest of the day.
- Pipeline code that retries on transient failures forever
  (`max_retries > 3` with 30s timeout = 90s per call × 3 = wasted
  quota).
- `node_evaluate` running `trials_per_test=10` by default, which
  multiplies the 21-task benchmark to 420 calls per round.

**Mitigations in place**:
- `src/llm.py` has `total_timeout` (180s by default) to bound any
  one call's retry budget.
- `src/llm.py` distinguishes 401/403 (permanent auth failure) from
  429 (quota, may be daily or minute-level).
- `run.py --unlock-keys` lets the user manually clear quota marks
  after a network blip.
- `tests/conftest.py` and `tests/test_bloat_invariants.py` are
  mock-free, so they consume **0 quota**.

**How to verify** (operational):
```bash
# Check daily quota burn rate
grep "Daily quota exhausted" upgrades/quota_state.json
# Check available keys
python -c "import json; state=json.load(open('upgrades/quota_state.json')); print(sum(1 for v in state['keys'].values() if v.get('dead_until',0)==0), 'alive keys')"
```

---

## C5. No silent promotion without evidence

**Rule**: The system must never write a new `core/planner.py`
version to disk unless **all** of the following hold:
1. A/B benchmark actually ran (baseline + upgraded trials both
   have at least 1 success/failure result, not 0/21)
2. The upgraded rate is **statistically significantly higher**
   than the baseline (delta > 5% threshold; CI excludes 0)
3. The cost-increase ratio is within the configured limit
   (default 1.2× baseline)

**Why it matters**: The user said "对比这个功能的效果提升和代价,
最终决定是否留下".  "决定是否留下" implies a deliberate
decision based on real data, not a coin flip.

**Failure modes this guards against**:
- LLM-generated patch passes sandbox (by chance) but the upgraded
  benchmark is actually worse than baseline (LLM-generated tests
  that don't measure what we care about).
- A flaky benchmark (e.g. 1 trial of 21 tasks) giving a false
  positive due to small sample size.

**Mitigations in place**:
- `src/evaluate.py::should_promote` enforces all three conditions
  before flipping `decision` to "kept".
- v1.7.1 `tests/test_bloat_invariants.py::test_safety_restore_planner_idempotent`
  ensures that even if a promotion happens, the safety net restores
  on next entry.

**How to verify**:
```bash
# Check that the latest decision is "reverted" (means safety net was exercised)
sqlite3 upgrades/history.db "SELECT decision, notes FROM upgrades ORDER BY id DESC LIMIT 5"
# Should NOT see "kept" without statistical significance
```

---

## C6. Failure modes are observable

**Rule**: Every failure (LLM error, sandbox fail, evaluate fail)
must produce a row in `upgrades/history.db` with the failure type
recorded.  The user must be able to look at history.db and
understand **why** a given attempt was rejected.

**Why it matters**: The user said "我希望能够查看每次运行的详细
日志" (implied).  Without failure logging, debugging is impossible
and the system appears to "just not work sometimes".

**Failure modes this guards against**:
- A pipeline exception that crashes before writing to history.db,
  making the failure invisible.
- An LLM error that's swallowed by the fallback chain, leaving no
  trace of which models / keys were tried.

**Mitigations in place**:
- `src/pipeline_lg.run` wraps every node in try/except and writes
  the error to `state["errors"]`, which is persisted to
  `history.db` even on overall failure.
- `src/llm.py` logs every 401/403/429 to `quota_state.json`
  with `last_error` field.
- The benchmark failures are recorded in `state["evaluation"]`
  with the success rate delta and CI.

**How to verify**:
```bash
sqlite3 upgrades/history.db "SELECT id, decision, substr(notes, 1, 60) FROM upgrades ORDER BY id DESC LIMIT 10"
# Every row should have a non-empty notes column
```

---

## C7. Reproducible from clean state

**Rule**: `git clean -fdx` + `git checkout v1.7.1` + `pip install -r
requirements.txt` + `pytest tests/ --ignore=tests/test_e2e.py
--ignore=tests/test_evaluate.py` must produce a working system
with all 154 tests passing.

**Why it matters**: "The system works on my machine" is not a
deployment story.  The user must be able to clone the repo on a
fresh machine, follow the README, and have a working system.

**Failure modes this guards against**:
- Tests that pass only because of an uncommitted change.
- Hidden dependency on a specific Python version, OS, or env var
  that's not in `requirements.txt`.
- `tests/conftest.py` that loads `.env` (which is gitignored) and
  fails on a fresh clone.

**Mitigations in place**:
- `requirements.txt` is in the repo and pinned.
- `tests/conftest.py` is the only place that loads `.env`; tests
  that don't need LLM keys skip gracefully.
- `tests/test_bloat_invariants.py` is mock-free and works without
  any env vars.

**How to verify** (on a fresh clone):
```bash
git clone <repo> /tmp/fresh-clone
cd /tmp/fresh-clone
pip install -r requirements.txt
pytest tests/ --ignore=tests/test_e2e.py --ignore=tests/test_evaluate.py
# Expected: 154 passed, 5 skipped in ~10s
```

---

## C8. Prompt-as-interface (per user 2026-07-08)

All static prompts (system + always-on user messages) live in
`src/prompts.py` as named constants.  Each prompt must be < 500
tokens.  Harness-implementation details (typing imports, sandbox
setup, file paths) belong to entity code — NOT the prompt.

Verification:
- `tests/test_v2_agent.py::TestHarnessStandalone::test_prompt_is_minimal_no_harness_rules`
  asserts the prompt does NOT mention harness / subprocess
- `tests/test_v2_agent.py::TestHarnessStandalone::test_harness_injects_typing_imports_via_prelude`
  asserts entity (v2_agent._PRELUDE) handles typing imports

Why this is the rule:
- Per user feedback 2026-07-08 ("启动 prompt 越少越好, 实体承担重要作用")
- The prompt changes if and only if the task description changes
- The entity changes if and only if the implementation changes
- Treating prompts as OOP abstract methods: 1 file = 1 role

---

## Constraint summary

| ID | Rule | Verified by |
|----|------|-------------|
| C1 | `core/planner.py` MD5 stable | `test_core_planner_md5_matches_head` |
| C2 | Recoverable from any tag | Manual: `git checkout v1.7.1 -- core/planner.py` |
| C3 | Bounded `upgrades/` growth | `test_history_db_is_well_formed_sqlite` |
| C4 | Quota-aware | Operational: `--unlock-keys`, `total_timeout` |
| C5 | No silent promotion | `should_promote` enforces 3 conditions |
| C6 | Failure modes observable | `state["errors"]` + `quota_state.json` |
| C7 | Reproducible from clean state | `pytest` on fresh clone |

These constraints were derived from real failures during
v1.5.0 → v1.7.2 development.  Each is a hard requirement that
should be re-checked whenever the system is modified.
