# Context for LLM — How to Use the Self-Upgrade Agent

> You are an LLM (qwen3.6-27B or similar) that has been given the
> `self-upgrade-agent` project.  This document tells you what you need
> to know to actually USE the system, not just read its code.

## Your situation

You have been asked to improve a self-evolving agent.  The agent has:

- **Hard-coded invariants** (do NOT modify these):
  - harness-first decision logic (`src/decide.py:should_promote_with_harness`)
  - atomic manifest write (`src/switcher.py:_write_manifest`)
  - safety net (`src/pipeline_lg.py:_safety_restore_planner`)
  - surgical-merge single-function enforcement (`src/pipeline_lg.py:_extract_target_function`)

- **Emergent subsystems** (you are EXPECTED to add to these):
  - `src/goals.py` — goal strategies (currently empty registry)
  - `src/learning.py:apply_memory_policy` — memory compression (currently noop)

- **Things you can patch** (within harness limits):
  - `core/planner.py` — the main target
  - `src/pipeline_lg.py` — but only specific functions, not the graph structure
  - Anything in `src/` except `_archived/`

## What you should know about THIS project (before patching)

### The target: `core/planner.py`

```python
def plan_task(task: str, llm_call: Callable) -> List[str]:
    """Decompose a task into ordered steps."""
    prompt = f"Break this task into 3-5 numbered steps. Reply only with the steps:\n{task}"
    result = llm_call(prompt)
    steps = []
    for line in result.split("\n"):
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith("- ")):
            steps.append(line)
    if not steps:
        steps = [f"Do: {task}"]
    return steps
```

**Constraints when patching**:
- Function signature MUST stay `plan_task(task: str, llm_call: Callable) -> List[str]`
- Must handle empty result → fallback to `[f"Do: {task}"]`
- Must handle malformed lines (numbered, bulleted, or freeform)
- The 8 harness tests in `tests/auto/test_planner_harness.py` will run on your patch

### What's in the project (Python version, dependencies)

- Python 3.11.15
- httpx (HTTP client)
- sqlite3 (stdlib)
- pydantic (config)
- langgraph (state machine)
- pytest (tests)

**You CANNOT** add new pip dependencies — patches must use stdlib only.

### What the agent can / cannot search

- arxiv API (configured in `config.yaml`, lookback_days=90)
- Semantic Scholar API
- Papers With Code
- GitHub repos

**It CANNOT** search beyond arxiv's API limits.  If you want broader coverage,
modify `config.yaml:research.lookback_days` — but that increases token cost.

## How to use `src/goals.py` (if you want to add a strategy)

```python
from src.goals import register, describe

def my_strategy(state):
    """decide_fn signature: takes state dict, returns next strategy name.

    state contains:
      - "round_number": int
      - "last_outcome": dict | None (decision, delta, harness_pass_rate, errors)
      - "long_term_goal": str | None
      - "next_strategy": str | None (pre-declared hint, optional)
    """
    last = state.get("last_outcome") or {}
    decision = last.get("decision")
    if decision == "kept":
        return "my_strategy"  # chain to self or another
    return "fallback_explore"

register(
    name="my_strategy",                        # unique identifier
    description="retry when last was kept",     # goes into LLM prompts
    decide_fn=my_strategy,                     # callable
    test_fn=lambda: True,                       # optional: harness check
)
```

**Good strategy names**: `retry_kept`, `expand_after_3_kepts`, `avoid_seen_topic`
**Bad strategy names**: `s1`, `test`, `tmp` (harness will pass but unclear)

## How to use `src/learning.py:apply_memory_policy` (if you want memory policy)

Two ways:

**A. Patch `apply_memory_policy` directly** — high effort, high control
**B. Pass `--memory-policy module:fn` to `self_upgrade gc`** — opt-in, easy

For (B), create `upgrades/memory_policies.py`:

```python
def trim_low_quality(c):
    """Delete papers with applicability_score < 2 OR seen > 5 times."""
    n_before = c.execute("SELECT COUNT(*) FROM seen_papers").fetchone()[0]
    c.execute("""
        DELETE FROM seen_papers
        WHERE paper_id IN (
            SELECT paper_id FROM seen_papers
            WHERE last_outcome = 'reverted'
            AND times_seen > 3
        )
    """)
    c.commit()
    n_deleted = c.rowcount
    return {"policy": "trim_low_quality", "before": n_before,
            "after": n_before - n_deleted, "deleted": n_deleted}
```

Then: `python -m self_upgrade gc --memory-policy upgrades.memory_policies:trim_low_quality`

## What context you'll see in prompts (current state)

**v1.8.1 prompt contents**:
- `node_filter` prompt: just the paper + abstract
- `node_implement` prompt: just the paper + the existing `plan_task`
- `node_reflect` prompt: just the failure trace

**What's MISSING from prompts** (planned for Step 3-5 of project_state plan):
- ❌ `last_outcome` ("last round was REVERTED because harness 0/8")
- ❌ seen_papers summary ("we've already tried these N papers in this topic")
- ❌ sandbox compat info ("Python 3.11.15, langgraph 0.x")
- ❌ long_term_goal

When you patch, you can ADD these to prompts by modifying `node_research`,
`node_implement`, `node_filter`.  This will help you avoid repeating failed
approaches.

## Common pitfalls

| Pitfall | What happens | How to avoid |
|---|---|---|
| Patch breaks harness | REVERTED, no promote | Read `tests/auto/test_planner_harness.py` first |
| Patch uses pydantic but not imported | Sandbox ImportError, reflect runs | Use stdlib only |
| Patch imports torch | Module not found, sandbox fails | Don't add deps |
| Patch returns wrong type (str instead of List[str]) | Harness 8/8 fail | Match signature |
| Patch has no `def plan_task` | `_extract_target_function` rejects | Always include `def plan_task(...)` |
| Patch too long (>2KB) | Beyond max_tokens | Be concise |

## How to debug a failing round

When `decision != "kept"`, check `upgrades/history.db`:

```bash
sqlite3 upgrades/history.db "SELECT id, decision, notes FROM upgrades ORDER BY id DESC LIMIT 5"
```

`notes` column has the reason.  Common ones:
- `"harness_failed: 8/0"` → your patch broke tests
- `"llm_delta_low: +1%"` → not enough improvement
- `"llm_cost_high: 1.5x"` → too expensive
- `"patch_rejected: missing plan_task"` → schema violation

## Test before you propose

Before submitting a patch, run locally:

```bash
# Does the patch break harness?
pytest tests/auto/test_planner_harness.py -v

# Does the patch break unit tests?
pytest tests/ --tb=short --deselect tests/test_bloat_invariants.py::test_working_tree_has_only_ignored_upgrades
```

If either fails, your patch will be REVERTED.

## You're expected to evolve these (priority order)

1. **`src/goals.py`**: register smarter strategies (most impactful)
2. **`src/learning.py:apply_memory_policy`**: smarter memory trim
3. **`src/pipeline_lg.py:node_research`**: better context for yourself (loop feedback)
4. **`src/llm.py`**: smarter quota rotation (only if you see quota issues)

## TL;DR for you

- The system works.  Read `docs/PROJECT_STATE.md` first.
- Don't break invariants (harness, atomic write, safety net).
- Add to emergent subsystems (goals, memory) — don't replace.
- Test before committing.
- Loop feedback (last_outcome, seen_papers, sandbox compat) is missing — adding it is a high-value patch.