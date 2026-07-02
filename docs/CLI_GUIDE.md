# Self-Upgrade Agent — CLI Guide

> **Status**: v1.8.0 alpha (2026-07-02)
> **Audience**: users who want to *use* the agent or *evolve* it

This is the complete usage manual.  It assumes you've cloned the
repo, installed deps, and configured `.env`.

---

## 1. Setup (one time)

```bash
git clone <repo-url> self-upgrade-agent
cd self-upgrade-agent
pip install -r requirements.txt
cp .env.example .env
# Edit .env:
#   LLM_API_KEY_0=ms-...   (ModelScope API key)
#   LLM_BASE_URL=https://api-inference.modelscope.cn/v1
#   LLM_MODEL=Qwen/Qwen3-235B-A22B
# Optional: more LLM_API_KEY_1..7 for rotation
```

**Verify setup**:
```bash
python -m self_upgrade status
```
Should print planner version, history.db row count, manifest entries.

---

## 2. Use the agent (`run`)

```bash
python -m self_upgrade run "<your task>"
```

**Examples**:
```bash
python -m self_upgrade run "Plan a 3-day trip to Tokyo"
python -m self_upgrade run "Write a palindrome check in Python"
python -m self_upgrade run "Organize a 50-person conference"
```

**What happens**:
1. `core/agent.py::quick_test` runs the agent loop
2. LLM is called once to get a plan
3. Plan is printed to stdout
4. **No 21-task benchmark, no harness, no eval** — just LLM call

**Cost**: ~1 LLM call.  ~5-30 seconds.

---

## 3. Self-evolve (`evolve`)

```bash
python -m self_upgrade evolve          # dry-run (no real LLM, fast)
python -m self_upgrade evolve --live   # real LLM calls (slow, costly)
```

**What happens** (7 stages):
1. `research` — search arxiv (or use mock if API down)
2. `filter` — LLM scores each paper (applicability / novelty / abstract)
3. `patchgen` — LLM writes a Python patch for `core/planner.py`
4. `sandbox` — run the patched code in isolation
5. `reflect` — if sandbox fails, LLM retries with feedback (max 3)
6. `evaluate` — A/B benchmark: baseline vs upgraded, 21 tasks
7. `decide` — promote or revert based on `should_promote`

**Cost (--live)**:
- ~50 LLM calls per round (1 filter + 1-3 patchgen + 42 benchmark + 3 reflect)
- ~14 minutes wall time on stable network
- Quota: **1 round/day recommended** (you have ~30 round/day budget)

**Cost (default, dry-run)**:
- 0 LLM calls (uses placeholder data)
- ~30 seconds

---

## 4. Maintenance subcommands

### `status` — see history
```bash
python -m self_upgrade status
```
Output:
```
SELF-UPGRADE AGENT STATUS
========================

core/planner.py: 807 bytes, __version__ = "1.3.0"

upgrades/history.db: 40 total attempts
  reverted: 40
  latest 3:
    id=40 decision='reverted' notes='Success rate delta 4.76% ...'

upgrades/manifest.json: 36 promoted
```

### `unlock` — reset quota state
```bash
python -m self_upgrade unlock
```
When ModelScope marks your keys as `dead_until: <24h>` (after a 429),
run this to reset all keys.  Useful when the quota was never actually
exhausted but the API gateway mis-classified.

### `cull` — prune skills
```bash
python -m self_upgrade cull
```
Removes low-effectiveness skills from the registry.  Idempotent.

### `gc` — garbage-collect cache + temp files
```bash
python -m self_upgrade gc --dry-run       # preview what would be deleted
python -m self_upgrade gc                  # actually delete (default: 30-day cache TTL)
python -m self_upgrade gc --arxiv-cache-max-age-days 0   # delete ALL cache files
python -m self_upgrade gc --archive-history-older-than-rows 100  # archive oldest 100 rows of history.db
```

**What it cleans** (default 30-day TTL):
- `upgrades/arxiv_cache/*.pkl` older than 30 days
- `upgrades/s2_cache/*`, `gh_cache/*`, `pwc_cache/*` (same rule)
- All `__pycache__/` directories in the project (Python rebuilds on import)
- Sandbox residue: `*.bench_bak`, `*.bench_tmp`, `*.v17_test_bak`, `*.stress_bak`, `*.e2e_test_bak`
- (optional) Oldest N rows of `history.db` archived to `upgrades/history_archive_<ts>.json`

**What it does NOT clean** (intentionally):
- `core/planner.py` (the upgrade target)
- `src/llm.py`, `src/pipeline_lg.py` (production code)
- `tests/` test files
- `upgrades/manifest.json` (audit log of promoted changes)
- `upgrades/quota_state.json` (key health tracking)

**When to run**:
- After running `run_3rounds_manual.py` (which itself auto-cleans `__pycache__`)
- Monthly as part of routine maintenance
- When `du -sh upgrades/` shows > 100MB (unusual growth)

**Notes**:
- The `run_3rounds_manual.py` script ALSO auto-cleans `__pycache__` at the end
  (so you don't need to run `gc` immediately after)
- `gc` is idempotent: running it twice in a row does nothing on the second run
- `gc` does NOT touch the committed `3round_run_results.json` (historical snapshot)

---

## 5. Running the 3-round stress test (manual)

**The script is already in the repo**: `run_3rounds_manual.py`
(commit `0b89fb0`, 233 lines).  It runs 3 rounds with the same 3
papers, reports real-time state of `core/planner.py` and
`history.db`, and saves results to
`upgrades/3round_manual_<timestamp>.json`.

**To run**:
```bash
python -m self_upgrade unlock    # clear dead marks
python run_3rounds_manual.py     # 3 rounds × ~150s each = ~7-15 min
```

**What it does** (per round):
1. `git checkout HEAD -- core/planner.py` (preflight safety)
2. `quota_state.json` reset (clear dead marks)
3. Inject one of 3 papers (multi-agent / WorldEvolver / AutoGen)
4. Run `pipeline.run(cfg, dry_run=False)` (full 7 stages)
5. Snapshot pre/post `core/planner.py` MD5 + history.db delta
6. Wait 70s before next round (avoid RPM rate limit)
7. Stop early if any round successfully promotes

**To customize papers**, edit the `PAPERS` list at the top of
`run_3rounds_manual.py`.  The default 3 papers test 3 directions:
- WorldEvolver (memory-augmented agent)
- Multi-Agent Collaboration (multi-agent)
- AutoGen (multi-agent conversation framework)

**If you want a different script (e.g. dry-run, fewer rounds,
different papers)**, the source is short and easy to modify.

**To run**:
```bash
# 1. Make sure your .env has at least 1 working ModelScope key
python -m self_upgrade unlock         # clear dead marks

# 2. Run 3 round (~7-15 min)
python run_3rounds_manual.py

# 3. Inspect
python -m self_upgrade status
cat upgrades/3round_manual_*.json     # timestamped results
```

**Expected outcomes** (under current ModelScope network):
- All 3 rounds: `done=False` (LLM calls fail with 401/403/timeout)
- `planner.py` size unchanged (807 bytes)
- `history.db` may have 0-3 new rows depending on whether the failure was recorded

**Expected outcomes** (under stable ModelScope):
- 1-3 rounds: at least 1 reaches `done=True`
- If patch passes sandbox + benchmark: `decision='kept'`, `planner.py` modified
- If patch fails: `decision='reverted'`, `planner.py` unchanged

---

## 6. Version management

**Tags in the repo**:
| Tag | Status | Use when |
|-----|--------|----------|
| v1.6.0 | Old | (Superseded by v1.7.x) |
| v1.7.0 | Old | (Anthropic provider experiment) |
| **v1.7.1** | **Stable** | **Production** — stress test verified |
| master (v1.8.0-alpha) | Alpha | **Experimentation only** |

**To use a stable version**:
```bash
git clone -b v1.7.1 <repo>
```

**To track v1.8.0 alpha**:
```bash
git clone -b master <repo>
# Warning: v1.8.0 alpha is incomplete.  Phase A is partial,
# real LLM end-to-end not yet verified.
```

**When will v1.8.0 be tagged**:
- After Phase A complete (A1-A5 all real)
- After Phase B at least B1 (CORE_MODULES whitelist) + 1 round
  live LLM end-to-end succeeds

---

## 7. Troubleshooting

### "All API keys marked dead"
Run `python -m self_upgrade unlock`.  If still failing, check
`.env` keys are valid and `LLM_BASE_URL` is set.

### "core/planner.py modified unexpectedly"
```bash
git checkout v1.7.1 -- core/planner.py
# or
git checkout HEAD -- core/planner.py
```

### "Real LLM end-to-end keeps failing"
This is **ModelScope gateway instability**, not a code bug.
- Wait 24h for daily quota reset
- Or switch to Anthropic provider in `.env` (see docs/LLM_CALLS.md)

### "Tests fail with import errors"
```bash
pip install -r requirements.txt
pytest tests/ --ignore=tests/test_e2e.py --ignore=tests/test_evaluate.py
```

### "How do I know which paper was last tried?"
```bash
sqlite3 upgrades/history.db "SELECT id, decision, substr(notes, 1, 80) FROM upgrades ORDER BY id DESC LIMIT 5"
```

### "How do I see what papers have been seen?"
```bash
sqlite3 upgrades/learning.db "SELECT paper_id, times_seen, last_outcome FROM seen_papers ORDER BY first_seen_at DESC LIMIT 10"
```

---

## 8. Backward compatibility

Old entry points still work:
- `python -m core.agent "task"` — equivalent to `python -m self_upgrade run "task"`
- `python run.py [--live]` — equivalent to `python -m self_upgrade evolve [--live]`
- `python run.py --stats` — equivalent to `python -m self_upgrade status`
- `python run.py --unlock-keys` — equivalent to `python -m self_upgrade unlock`
- `python run.py --cull` — equivalent to `python -m self_upgrade cull`

**No deprecation warning yet**, but the unified CLI is the recommended path.
