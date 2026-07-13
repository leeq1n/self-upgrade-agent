# Recursive decomposition (per user meta-rule, 2026-07-13)

> L0: 5-step loop for big tasks (THINK → DECOMPOSE → ORDER →
> EXECUTE → INTEGRATE).  Load when task is "big" (multi-file,
> multi-project, multi-step).  Don't load for 1-2 step tasks.

## When to use this

Load this doc when:
- Task is multi-file or multi-project scope.
- Task spans more than ~5 tool calls.
- You find yourself unsure of scope.
- User said "大任务" or similar.

Don't load this doc for:
- 1-2 step tasks (e.g. "fix this typo").
- Single-file changes.
- Trivial edits.

## The 5-step loop

For **big tasks** (multi-file changes, multi-project scope,
sustained effort over many turns), do **not** start coding
immediately.  Instead, follow this loop:

```
big task T
  ├─ 1. THINK: what is T actually?  Is it really one task or N?
  ├─ 2. DECOMPOSE: split T into T1, T2, ..., TN (sub-tasks).
  │        Each Ti should be a leaf (1 logical change, 1 commit).
  │        Stop decomposing when each leaf is small enough that
  │        the "1 commit = 1 logical feature" rule (P4) holds.
  ├─ 3. ORDER: detect dependencies between Ti.  If T2 needs T1
  │        done first, mark T2 as 'after T1'.
  ├─ 4. EXECUTE: do T1 (commit + verify), then T2 (commit + verify), ...
  └─ 5. INTEGRATE-AND-THINK: after all Ti done, re-think.  Is the
           whole T actually complete?  Did the sub-tasks reveal
           a new sub-task?  Should any Ti be revisited?
```

This loop is **recursive**: each Ti may itself be a "big task"
relative to its sub-tasks.  Decompose until each leaf is small.

## Real L2 examples (this project)

- "Make SUA doc maintenance self-updating" → decompose into:
  (a) AGENTS.md onboarding contract, (b) commit-msg hook for
  P-n enforcement, (c) bulk Last P20-verified refresh, (d) P2
  search spec with 'search-then-update' contract, (e) future
  pre-commit-doc-check hook.
- "Audit outdated docs" → decompose into:
  (a) grep for Last P20-verified <30 days, (b) per-file review
  for content drift, (c) prioritize fixes by user-facing impact,
  (d) fix in 1-commit-per-doc order.
- "Adjust SUA docs per new-agent-perspective principle" →
  decompose into: (a) bulk L0 add for docs missing it,
  (b) extract Recursive decomposition to this doc, (c) extract
  Operating rules to dedicated doc, (d) rewrite AGENTS.md to
  always-on only, (e) add conditional read-order pointers.

## Anti-patterns (what NOT to do)

- **Don't skip step 1** (THINK).  Jumping straight to coding
  on a big task = "yellow claimed as green" (P17).
- **Don't skip step 5** (INTEGRATE).  After 3 leaf commits, the
  whole task may still be incomplete; re-evaluate.
- **Don't decompose too finely** (1 commit per file is fine;
  1 commit per line is silly).  Stop when leaf size ≈ 1-3 files
  or 1-50 LOC.

## Per P22 (stuck → plan)

When you find yourself unsure mid-task, fall back to step 1
(THINK) and re-decompose.

## Per P14 (docs stay current)

If decomposition reveals a doc drift, fix the doc in the same
task (not a separate one).

## See also

- AGENTS.md — references this doc in "See also"段.
- PRINCIPLES.md P22 (stuck → plan) — meta-rule this loop
  implements.