# Common pitfalls for new agents (per 2026-07-13 review)
Last P20-verified: 2026-07-13

> L0: 4 categories of clue fresh agents most often miss.
> Load when context-switching, starting non-trivial work, or
> about to make a doc/code change.

## When to use this

Load this doc when:
- Context-switching (resuming after task switch).
- Starting a non-trivial task.
- About to make a code change (avoid sibling's pre-existing
  failures).
- About to add a new TODO / open work item.

Don't load for:
- Trivial edits (typo, single-line change).
- Tasks fully covered by AGENTS.md hard rules.

## The 4 categories

### 1. Open-work categories

This project has 2 TODO items that are *not* in AGENTS.md:
- **Knowledge lifecycle** (priority scoring + pruning for an
  ever-growing KG; user signal 2026-07-13).
- **Session snapshot/restore mechanism** (for task-switching
  across context overflow; user signal 2026-07-13).

Both are explicit-future, not immediate.  Don't start them
without user prompt.

See `docs/TODO_SESSION_PERSISTENCE.md` for full TODO proposal
(both written 2026-07-13; implementation deferred).

### 2. Snapshot location convention

Per M-context-snapshot (`docs/OPERATING_RULES.md`), save
session state to:
`hermes-snapshot-<topic>-<date>.md` (use
`tempfile.mkstemp(prefix="hermes-snapshot-",
dir=os.environ.get("TEMP", "/tmp"))` per OS-safe
tempfile path convention)

This is **session_search-able** by title.  NOT in repo unless
user asks (Temp gets cleared on session restart, so don't
rely on long-term).

### 3. Session scope boundary

This project's current session scope is "SUA-side onboarding
+ knowledge-base architecture" (10+ commits since 2026-07-12,
ending with `43f1d09` / `8b4ec77` / `ac7e6c4` / `2d7448a` /
plus this doc + AGENTS.md rewrite).

**Don't touch**:
- `self-upgrade-agent/src/*` or `tests/*` (sibling's code)
  unless explicitly asked.
- `../knowledge-graph-seed/` (P21 cross-project independence)
  unless explicitly asked.

### 4. M-task-summary vs M-subtask-summary vs M-learn

These are three distinct rules (per
`docs/OPERATING_RULES.md`); they fire at different points
and on different scales.  Don't conflate.

| Rule | When | What |
|---|---|---|
| **M-task-summary** | After every task completion (leaf or 1-step) | 1-paragraph reflection: what went well, what could improve, did docs need updating? |
| **M-subtask-summary** | Per leaf commit (inside multi-leaf task) | 1-2 line summary in commit message body.  Feeds the parent task's INTEGRATE step. |
| **M-learn** | At a parent-task INTEGRATE point (all sub-tasks done) | 3 sub-actions: 总结归纳 + 类比外推 + 更新知识库.  Silent no-op per 奥卡姆 if nothing generalizes. |

**Common confusion** (per recent sessions):
- Treating M-task-summary as M-learn → update docs for
  every leaf task → doc bloat.  M-task-summary asks "did
  the docs drift?"; M-learn asks "did this surface a new
  pattern that generalizes?".
- Skipping M-subtask-summary → parent INTEGRATE must
  re-read every diff → O(code) instead of O(summaries)
  (per RECURSIVE_DECOMPOSITION.md "Context flow across
  recursion layers").
- Treating M-learn like M-context-snapshot (writing
  "checked, nothing new" lines) → doc bloat.  M-learn's
  silent no-op is the discipline.

All three are needed; do not skip any.  The integration
step (5-step loop step 5) relies on leaf summaries to
avoid re-reading every diff; the leaf reflection
relies on M-task-summary; the project's memory quality
relies on M-learn firing correctly.

## Pre-existing pytest failure context

SUA has a pre-existing test failure in
`auto/test_planner_harness.py::test_plan_task_returns_list_of_strings`
(expects `list`, gets `RoundResult` from `core/planner.py`).
This is **sibling's** return-type change, NOT introduced by
this session's commits (verified via `git stash` in commit
`f10c604`).  Per M-rules: sibling's code = sibling's
responsibility.  Document but don't fix unless asked.

## Open work categories

  User signaled: "knowledge base grows, need priority marking".
  Written 2026-07-13; implementation deferred (KG frozen).
- **Task 8 (TODO)**: `docs/TODO_SESSION_PERSISTENCE.md` —
  proposal for session snapshot/restore mechanism design.
  M-context-snapshot (`docs/OPERATING_RULES.md`) is the rule;
  the *implementation* (snapshot format, restore mechanism,
  cross-session search) is task 8.  Future; no implementation
  yet.

## See also

- `docs/OPERATING_RULES.md` — full text of all 6 M-* rules
  (M-task-summary, M-must-read, M-context-snapshot,
  M-subtask-summary, M-intent-parsing, M-learn).
- `docs/MEMORY_TOOLS.md` — full decision matrix for memory
  tools.
- `docs/RECURSIVE_DECOMPOSITION.md` — 5-step loop for big
  tasks (M-learn's trigger is step 5).