# AGENTS — Operating Rules for AI Agents in This Project
Last P20-verified: 2026-07-13

> L0: AI agents entering this repo MUST read `docs/PRINCIPLES.md`
> FIRST.  Treat each P-n as binding unless the user explicitly
> overrides it for a task.  Commits that ignore PRINCIPLES will
> be caught by the commit-msg hook (P-n cite required).

## Read first (in order)

1. `docs/PRINCIPLES.md` — operating principles (P1-P27).  Read
   the FULL file (~11 KB).  Do not skim.
2. `docs/INDEX.md` — orientation map (8-step reading order
   + conditional stealth loads).  Follow the numbered steps
   until you have a project overview.
3. `docs/PROJECT_STATE.md` — current goal, version, next
   step (1-paragraph snapshot).
4. `docs/PRINCIPLES_DETAIL.md` — full text of each P-n (L2
   detail).  Read when you need the rationale behind a rule.
5. `docs/SWITCH_SIGNALS.md` — switch signals + action
   protocol (consulted before every user-message response;
   see conditional load below for trigger reminder).
6. `docs/HOW_TO_READ_GRAPH.md` — read pattern for new
   agents (per c57, the 3-step pattern: L0 → L1 → L2,
   with cross-ref traversal rules + 5 essence families
   + 7-check self-org).  Read when entering the project
   or when stuck on graph traversal.

## Hard rules (top 6 from PRINCIPLES.md, binding)

If you violate these, your commit is rejected by the commit-msg
hook (it scans for the `P##` reference; the rule cited is the one
that motivated the change).

- **P5** — measure twice, commit once.  Tests must pass before
  commit.
- **P11** — write the summary BEFORE the detail; do not
  duplicate.
- **P14** — if you change code that drifts a doc, update the
  doc in the same commit.
- **P17** — never claim green when it is yellow.  If you
  cannot verify, say so explicitly.
- **P20** — every doc must have an L0 line (≤ 120 chars).
  Prefer existing file; split if a doc does two jobs.
- **P22** — when stuck, STOP.  Look at the project state, then
  write a plan.  Do not brute-force past a wrong assumption.

## What NOT to do

- Do not create parallel doc structures (M33).  If PRINCIPLES.md
  covers it, point to it; do not restate.
- Do not commit to `../knowledge-graph-seed/` from this project
  (P21).  Cross-project links use relative paths.
- Do not invent features you have not verified (M79 — test
  before claiming; M82 — commit gate before declaration).
- Do not stuff conditional content into always-read files
  (per "storage layered / read flat" principle — see
  `docs/RECURSIVE_DECOMPOSITION.md`).

## Commit message contract

Every commit message MUST contain at least one `P##` reference
(one of P1-P27) explaining which principle motivated the
change.  The `commit-msg` hook enforces this.

**Hook install** (one-time per clone):

```bash
cp hooks/commit-msg .git/hooks/commit-msg
chmod +x .git/hooks/commit-msg
```

The hook template is tracked in this repo at `hooks/commit-msg`.
After install, git runs it automatically on every commit.

Format:

```
<type>(<scope>): <short description>

Cite one of P1-P27 here, e.g.:
- P5 — "added tests before commit"
- P11 — "rewrote L0/L1 boundary"
- P17 — "documented what is NOT shipped"

Detailed body.
```

Allowed `P##` values: P1, P2, P3, P4, P5, P7, P8, P9, P10,
P11, P12, P13, P14, P16, P17, P18, P19, P20, P21, P22, P23,
P15 (demoted to P5 实操 per c79), P24 (merged into P3 per c78),
P25, P26, P27.  See PRINCIPLES.md / PRINCIPLES_DETAIL.md for the complete
list.

## When in doubt

State the ambiguity, list the options you considered, pick one,
apply, and cite the principle in your commit message.  Same as
if you were the maintainer reading your PR.

## See also (project docs, conditional load)

These are **conditional** docs — load only when the task type
matches the trigger.  Default: don't load.

- `docs/RECURSIVE_DECOMPOSITION.md` — load when task is big
  (multi-file, multi-project, multi-step).  5-step loop.
- `docs/OPERATING_RULES.md` — load when ending task, switching
  task, unsure which tools to use, **or before declaring "all
  pass"**, **or after encountering any new rule/pattern**, **or
  when user input is messy**, **or at a decomposition
  integration point**, **or when context feels cluttered**.
  Also load **at the start of every user message** to check
  whether the message is a switch (per
  `docs/SWITCH_SIGNALS.md` "Switch action protocol");
  switching without loading is the most common fresh-agent
  miss.
  9 M-* rules: M-task-summary, M-must-read, M-context-snapshot,
  M-subtask-summary, M-intent-parsing, M-learn,
  M-add-then-reduce, M-self-audit, M-self-application.
- `docs/OPERATING_RULES_DETAIL.md` — load when implementing
  M-intent-parsing (full 3-action steps, anti-pattern) or
  M-learn (full dual-track triggers, 3 sub-actions, M-rule
  relationships).  Per P20 R5+R6: 7KB-summary / _DETAIL-split
  pattern; this is the L2 detail companion.
- `docs/M_SELF_AUDIT.md` — load before "all pass", before
  any Edit/Write on a previously-read file (per step 6
  "verify-before-edit"), or after big doc changes
  (fresh-agent discoverability check; 4 triggers,
  6-step audit checklist, anti-patterns).
- `docs/M_SELF_APPLICATION.md` — load when encountering any
  new rule or pattern, or when debugging "rule didn't apply"
  (4 levels: object / rule itself / memory / self behavior).
- `docs/SUMMARY_LIFECYCLE.md` — load when implementing a
  parent-level M-task-summary (M-task-summary child-summary
  destroy contract — pull, write, destroy in same commit).
- `docs/SWITCH_SIGNALS.md` — load when evaluating whether
  current context is a "switch" that needs M-context-snapshot
  (5 signal types, what goes in a snapshot, location).
- `docs/TODO_SESSION_PERSISTENCE.md` — proposal for formal
  snapshot/restore mechanism (format, location 2-tier,
  restore protocol, lifecycle per M-add-then-reduce).
  Implementation deferred (proposal-only).
- `docs/TODO_SESSION_PERSISTENCE_DETAIL.md` — L2 detail
  companion (per P20 R5 + R6: 7KB-summary / _DETAIL-split
  pattern; holds open questions + implementation steps).
  Load when: implementing the proposal or resolving the
  questions.
- `docs/TODO_KNOWLEDGE_LIFECYCLE.md` — proposal for KG
  priority scoring + 3-tier pruning + search bypass
  (composite priority score, active/stale/dead policy,
  top-N by priority at search).  Implementation
  deferred (KG frozen; last activity 2026-07-13).
- `docs/ADD_THEN_REDUCE.md` — load when planning a multi-leaf
  task or applying M-learn (Add phase + Reduce phase, signal
  triggers, anti-patterns).
- `docs/COMMON_PITFALLS.md` — load when context-switching
  or about to start non-trivial work.  4 categories of clues
  fresh agents often miss.
- `docs/MEMORY_TOOLS.md` — load when unsure which memory
  tool to use.  Decision matrix.

**Before declaring any task "all pass"**: apply M-self-audit
(from `docs/M_SELF_AUDIT.md`).  Ask: "If a new agent
entered this project right now, could it read what it needs
to do the task?"  Per M82: verify before claiming.  Per P17:
never claim green when it is yellow.

**After encountering any new rule or pattern**: apply
M-self-application (from `docs/M_SELF_APPLICATION.md`).
Ask "does this rule apply at 4 levels — to current task,
to the rule itself, to memory / project structure, to my
own operating behavior?"  This is the most common class
of agent failure mode: knowing a rule but not self-applying
it.

## See also (project docs, always-load if relevant)

These are project-wide pointers; load if your task type matches.

- `docs/PRINCIPLES.md` — the principles themselves (P1-P27).
  **Read FULLY before modifying any P-n / M-* rule** (per
  "P-n / M-* modification discipline" 段).
- `docs/INDEX.md` — orientation map.
- `docs/PROJECT_STATE.md` — current state (1-paragraph).
- `docs/PROJECT_STATE_DETAIL.md` — version history + vision.
- `docs/PRINCIPLES_DETAIL.md` — full text of each P-n.
- `docs/OBSERVATIONS.md` — empirical context from past runs
  (68KB, use `search_files` to find specific items, don't
  load fully).
- `docs/LITERATURE.md` + `docs/LITERATURE_DETAIL.md` — past
  research citations (per P2 搜资料 workflow).
- `DONE.md` — project log (51KB, use `search_files` to find
  specific items, don't load fully).
- `README.md`, `PROJECT_BRIEF.md`, `ISSUES.md`, `TODO.md` —
  root project docs (load when starting broad project work).
- `docs/CONSTRAINTS.md` + `docs/CONSTRAINTS_DETAIL.md` — hard
  must-not-violate rules (C1, C2...).

## See also (session-specific, conditional)

Load only when context has overflowed or task has switched.

- `C:\Users\LQ\AppData\Local\Temp\hermes-verify-sua-onboarding-20260713.py`
  — ad-hoc verify script for the 8-commit onboarding batch
  (30 checks; 30/30 PASS).
- `C:\Users\LQ\AppData\Local\Temp\hermes-snapshot-sua-onboarding-20260713.md`
  — session snapshot (recent commits, open todos, decisions).
  Load this on resume after context overflow.