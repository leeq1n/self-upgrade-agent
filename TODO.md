L0: Pending tasks — backlog of next-up features.  Done items live in DONE.md.
Last P20-verified: 2026-07-13

# TODO —

Each task is a checkbox.  To claim: change `[ ]` to `[x]` and move
the line into DONE.md.  Keep this list SHORT and CURRENT; older
completed work lives in DONE.md.

> Convention: `- [ ]` = not started, `- [x]` = done, `- [/]` = in progress.

## Task ID + sub-task pointer convention (per user 2026-07-14)

When adding a new task to this file, use a hierarchical
ID scheme (per user 顿悟: "任务不一定是代码任务，
也可能是问题拆解汇总，写材料之类的任务"):

- **Top-level task**: `T-NNN` (3-digit sequence)
- **Sub-task**: `T-NNN.M` (parent ID + dot + sub-sequence)
- **Sub-sub-task**: `T-NNN.M.K` (deeper levels as needed)

Examples:
- `T-042`: top-level task "improve memory tool"
- `T-042.1`: sub-task "add doc layer"
- `T-042.1.2`: sub-sub-task "update USER_INSIGHTS cross-ref"

Format in entries: `T-NNN **Task title** ...` placed
at the start of the line, before the `**bold**` title.

When done, replace `[ ]` with `[x]`.  When the parent
task is complete and parent summary written, prefix
the entry with `[x-archived]` to signal "sub-tasks
consumed; no longer active" (per SUMMARY_LIFECYCLE
destroy contract pattern).

**When to use IDs** (trigger condition):

- Tasks that span multiple commits → use sub-task IDs.
- Tasks that have explicit dependencies on other
  tasks → use IDs for cross-references.
- Single-commit trivial tasks → no ID needed (existing
  convention `- [ ] **title**` is sufficient).

**Anti-patterns** (per P7 奥卡姆 + P23 doc>script):

- **Don't add IDs to every existing entry** — scope
  creep.  This is a forward-looking convention, not
  a back-fill mandate.
- **Don't create parallel task tree files** (e.g.
  TASK_TREE.md) — TODO.md is the single source of
  truth.  Per P11 摘要+引用, no duplicate.
- **Don't use a separate file-based task system**
  until multi-layer recursion is actually needed
  (P23 0-violations rule + M-add-then-reduce
  signal-trigger).  Current commit history + this
  TODO.md are sufficient for current scope.

**Why this is needed** (per user 2026-07-14):

"每次做完一条整理一下优先级，需要分成子任务的写
一下指向，方便新 agent 确认任务进行到哪里了".
Cross-task referencing (e.g. "this is part of T-042")
was previously ad-hoc; ID convention makes it
explicit and machine-parseable.

**Scope** (per P7 奥卡姆 + M-self-audit 4-level):

This is **1 logical feature**: "TODO.md gains a
task-ID convention for forward-compatibility".  No
back-fill of existing entries, no new files, no
script.  Future tasks use IDs; existing entries
keep their current form (forward-only).


## Detail (per R6)

> L0: Per P11 摘要+引用 + R5, this L0/L1 summary (≤ 7KB).  Detail in `TODO_DETAIL.md`.

## See also

- `TODO_DETAIL.md` (L2 companion: Completed + In progress + Backlog + Lesson)
