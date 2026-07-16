# AGENTS — Operating Rules (detail)

> L0: L2 detail for `AGENTS.md`.  Per P11
> 摘要+引用 + R6, this companion is required
> when summary exceeds 7 KB.

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

- `docs/PRINCIPLES.md` — the principles themselves (P1-P29, 25 working).
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
