---
description: "Hard rules the code must preserve"
status: "summary"
---

# CONSTRAINTS — brief

These are invariants derived from real failures during v1.5.0 →
v1.7.2 development.  The system can behave however it wants as
long as these hold.

Most-cited in user feedback (2026-07-08):

- C1. `core/planner.py` MD5 stability — no corruption across rounds
- C2. Memory growth bounded by `MAX_LEARNING_ROWS = 10000` (hard limit)
- C3. Atomic apply — file-level atomic write, revert restores byte-perfect
- C4. Fail-OPEN — pre-filters / hardcode rules must let LLM decide
- C5. No `.env` key mutations by the agent
- C6. Logs preserved; pre-run no GC, post-run archive-only
- C7. Tests: 438 PASS + 6 skip + 0 fail contract (without regression)

Full list with rationale and verification in
[`CONSTRAINTS_DETAIL.md`](CONSTRAINTS_DETAIL.md).

## References

- INDEX: [INDEX.md](INDEX.md)
- Project state: [PROJECT_STATE.md](PROJECT_STATE.md)
- User intent: [USER_INSIGHTS.md](USER_INSIGHTS.md)
- LLM choice: [MODEL_STRATEGY.md](MODEL_STRATEGY.md)
- Pending tasks: [../../TODO.md](../../TODO.md)
- Done tasks: [../../DONE.md](../../DONE.md)
- Full constraint list: [CONSTRAINTS_DETAIL.md](CONSTRAINTS_DETAIL.md)
