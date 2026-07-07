# Goals Design — Emergent + Anti-Lock-In + 奥卡姆

> v1.8.1 — Goal machinery that survives the long run.

## User insight (2026-07-07)

> "现在没有设计的最好的目标函数或奖励函数, 所以你应当保留可扩展性,
> 未来动态变化.  当然这个过程你需要小心可扩展性被锁死
> (所以需要在锁死的时候回退, 或者用 harness 之类的避免这件事),
> 当然, 这里也需要注意奥卡姆剃刀原则."

Three constraints at once:
1. **可扩展** — strategies must be addable at runtime
2. **防锁死** — bad strategies must not lock the system
3. **奥卡姆** — keep it simple, no over-design

## Three-layer design

```
┌─────────────────────────────────────────────────────────┐
│  Level 1: EMERGENT                                      │
│  Strategies are data in a mutable registry.             │
│  LLM can add/remove at runtime via patchgen.            │
├─────────────────────────────────────────────────────────┤
│  Level 2: ANTI-LOCK-IN (harness-style)                  │
│  Each strategy has test_fn().  Pipeline checks           │
│  health before using.  Crashes caught, fallback used.   │
├─────────────────────────────────────────────────────────┤
│  Level 3: 奥卡姆 FALLBACK (永远 hardcoded)              │
│  fallback_explore: pick unseen paper.  Never removed.   │
│  If everything else fails, this is the safety net.      │
└─────────────────────────────────────────────────────────┘
```

## Key properties

### 1. Registry is empty by default

```python
from src.goals import list_strategies
list_strategies()  # [] — no hard-coded strategies
```

**Why**: I don't know the right strategies.  The LLM does, eventually.

**Result**: First run of `python run_stable.py 3` will use `fallback_explore`
for all 3 rounds.  That's by design — it forces the LLM to evolve.

### 2. Strategies are pure callables, not code

```python
def my_strategy(state):
    """Return next strategy name.  Pure: no side effects on registry."""
    if state["round_number"] % 2 == 0:
        return "fallback_explore"
    return "my_strategy"  # can chain to self

register("my_strategy", "do something smart", my_strategy)
```

The decide_fn returns a STRING (next strategy name), not a function call.
This enables **chaining**: strategy A can decide strategy B runs next.

### 3. Crashes are caught

```python
def bad(state):
    raise RuntimeError("oops")

register("bad", "always crashes", bad)
pick_strategy({})  # → "fallback_explore" (not crash!)
```

**Why**: a buggy strategy must NOT freeze the pipeline.  Atomic rollback
in switcher.py already protects planner.py; goal machinery protects itself.

### 4. test_fn is the harness layer

```python
def my_test():
    # can be expensive, but it's a sanity check, not a benchmark
    assert my_strategy({"round_number": 1}) == "fallback_explore"
    return True

register("my_strategy", "...", my_strategy, test_fn=my_test)
```

`run_health_check()` returns `{name: passed_bool}`.  Pipeline can use this
to skip broken strategies.  If a patch makes `my_test` fail, the patch
gets REVERTED by the same mechanism that protects `core/planner.py`.

### 5. fallback_explore is NEVER in the registry

It's a module-level `_HARDCODED_FALLBACK` dict.  `clear_registry()` cannot
remove it.  This is the 奥卡姆 guarantee — at least one strategy always exists.

## How LLM evolves goals (future)

### Path 1: patchgen edits `src/goals.py`

LLM reads the file (~150 lines), sees the registry pattern, and patches in
new strategies.  The patch is run through:
1. unit tests (test_goals_*) — must pass
2. sandbox — runs the pipeline
3. harness — protects core/planner.py

### Path 2: LLM creates `upgrades/goals_policies.py`

```python
# upgrades/goals_policies.py
def smart_strategy(state):
    """Pick based on past 3 outcomes' average delta."""
    return "fallback_explore"  # placeholder

# Then via CLI:
python -m self_upgrade evolve  # pipeline auto-loads from upgrades/
```

(Path 2 needs plumbing; for now Path 1 is the documented way.)

### Path 3: harness discovers

`run_health_check()` is called automatically.  If a strategy's test_fn
starts failing in production (due to environmental changes), the pipeline
can decide to unregister it.  **This is the "self-healing" property**.

## What I did NOT do (and why)

| I considered | Rejected because |
|---|---|
| Hard-coded 4 strategies | Violates "no best strategy" insight |
| Long-term goal as a parameter to `register()` | Too clever; long-term goal is *what* to optimize, not *how* |
| Persistence of strategies to learning.db | Adds complexity; LLM can patch goals.py directly |
| Goal history table | Future LLM might add this; not my job |
| Long-term goal evaluator (function that scores delta vs goal) | That IS a strategy; should be emergent too |

## Anti-lock-in tests (these are the harness)

The 9 `test_goals_*` tests verify:
- ✅ Registry starts empty
- ✅ Empty registry → fallback
- ✅ Register/unregister work
- ✅ Crashing strategy doesn't break loop
- ✅ register() validates input (no empty names, no non-callables)
- ✅ test_fn runs via health_check
- ✅ Fallback always works (even after clear_registry)
- ✅ unregister returns bool (atomic semantics)
- ✅ DEFAULT_LONG_TERM_GOAL is non-empty

If a future LLM patch breaks any of these, **patch is REVERTED** by the
existing atomic write mechanism.

## The single hardcoded thing

Only ONE thing is hardcoded: `fallback_explore`.  It does the simplest
possible thing — pick an unseen paper.  This is the 奥卡姆 guarantee.

If you (a future agent) are tempted to "improve" this by hardcoding more
strategies — **don't**.  Make them emergent.  Let the LLM register them.