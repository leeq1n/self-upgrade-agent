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

---

## 5. Running the 3-round stress test (manual)

The user has a script that runs 3 rounds of the live pipeline
and saves results to `upgrades/3round_run_results.json`.  It is
**not yet committed** because the version that was used (2026-07-02)
is no longer in the repo (it was cleaned up after the test ran).

**To recreate it**:
```python
# /tmp/run_3rounds.py
import os, sys, time, json
sys.path.insert(0, r"C:\Users\LQ\Documents\agent-workspace\hermes-root\self-upgrade-agent")
os.chdir(r"C:\Users\LQ\Documents\agent-workspace\hermes-root\self-upgrade-agent")

# Load .env
with open(".env", encoding="utf-8-sig") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        if " #" in v: v = v.split(" #", 1)[0].rstrip()
        if k and k not in os.environ: os.environ[k] = v

PAPERS = [
    {"arxiv_id": "2606.30639", "title": "Self-Evolving World Models for LLM Agent Planning",
     "abstract": "WorldEvolver introduces self-evolving world model...",
     "authors": "Anon", "published": "2026-06-30", "categories": "cs.AI, cs.CL"},
    {"arxiv_id": "2406.01574", "title": "Multi-Agent Collaboration Mechanisms",
     "abstract": "Survey of multi-agent LLM collaboration...",
     "authors": "Han et al.", "published": "2024-06-03", "categories": "cs.CL, cs.MA"},
    {"arxiv_id": "2310.02170", "title": "AutoGen: Multi-Agent Conversation",
     "abstract": "AutoGen framework for multi-agent LLM systems...",
     "authors": "Wu et al.", "published": "2023-10-03", "categories": "cs.CL, cs.MA"},
]

import src.pipeline_lg as plg
from src.research import Paper
from src.config import load_config
import src.research as research_mod
import subprocess

def head_md5():
    r = subprocess.run(["git", "ls-tree", "HEAD", "core/planner.py"], capture_output=True, text=True)
    sha = r.stdout.strip().split()[2]
    r2 = subprocess.run(["git", "cat-file", "blob", sha], capture_output=True)
    import hashlib
    return hashlib.md5(r2.stdout).hexdigest()

results = []
for n, paper in enumerate(PAPERS, 1):
    print(f"\nROUND {n}: {paper['arxiv_id']}")
    # restore planner.py
    subprocess.run(["git", "checkout", "HEAD", "--", "core/planner.py"], capture_output=True)
    # unlock quota
    qf = "upgrades/quota_state.json"
    if os.path.exists(qf):
        state = json.load(open(qf))
        for info in state.get("keys", {}).values():
            info["dead_until"] = 0; info["failures_today"] = 0
        json.dump(state, open(qf, "w"), indent=2)
    P = Paper(**paper)
    research_mod.search_arxiv = lambda cfg: [P]
    plg.search_arxiv = lambda cfg: [P]
    cfg = load_config("config.yaml")
    cfg.evaluate.trials_per_test = 1
    t0 = time.time()
    try:
        state = plg.run(cfg, dry_run=False)
    except Exception as e:
        state = {"done": False, "errors": [str(e)]}
    elapsed = time.time() - t0
    results.append({
        "round": n, "paper": paper["arxiv_id"], "elapsed_s": round(elapsed, 1),
        "done": state.get("done"),
        "decision": (state.get("decision") or {}).get("decision"),
    })
    print(f"  Elapsed: {elapsed:.1f}s, done={state.get('done')}, decision={results[-1]['decision']}")
    if n < 3: time.sleep(70)

with open("upgrades/3round_run_results.json", "w") as f:
    json.dump({"rounds": results, "head_md5": head_md5()}, f, indent=2)
print("Done. Results in upgrades/3round_run_results.json")
```

**To run**:
```bash
# 1. Make sure your .env has at least 1 working ModelScope key
python -m self_upgrade unlock    # clear dead marks

# 2. Run 3 round (~7-15 min)
python /tmp/run_3rounds.py

# 3. Inspect
python -m self_upgrade status
cat upgrades/3round_run_results.json
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
