# AGENTS — Operating Rules for AI Agents in This Project

> L0: AI agents entering this repo MUST read `docs/PRINCIPLES.md`
> FIRST.  Treat each P-n as binding unless the user explicitly
> overrides it for a task.  Commits that ignore this rule will
> be caught by the `commit-msg` hook (it requires a `P##`
> reference in the commit message, per "Commit message contract"
> below).

## Read first (in order)

1. **`docs/PRINCIPLES.md`** — operating principles (P1-P24).
   Read the FULL file (~10 KB).  Do not skim.  The principles
   are the project's operating contract; they override your
   default behavior.
2. **`docs/INDEX.md`** — orientation map (8-step reading order
   + conditional stealth loads).  Follow the numbered steps
   until you have a project overview.
3. **`docs/PROJECT_STATE.md`** — current goal, version, next
   step (1-paragraph snapshot).
4. **`docs/PRINCIPLES_DETAIL.md`** — full text of each P-n (L2
   detail).  Read when you need the rationale behind a rule.

For specific subsystems, follow INDEX.md's "Conditional loads":

- **`docs/LITERATURE.md`** — only if designing a feature or
  evaluating a research idea (P2 — read sources before designing).
- **`docs/OBSERVATIONS.md`** — only if you need empirical context
  from past LLM runs (latency, KEPT ratios, anomalies).
- **`docs/USER_INSIGHTS.md`** — only if confused about user
  intent or paraphrasing rules from past sessions.
- **`docs/EXTENSIONS.md`** — only if work crosses project
  boundaries (e.g. integrating with the knowledge-graph seed).
- **`docs/CONSTRAINTS.md`** — only if you're about to do
  something that might violate a must-not-violate rule (C1, C2...).

## Hard rules (top 6 from PRINCIPLES.md, binding)

If you violate these, the `commit-msg` hook will reject your
commit (it scans for the `P##` reference; the rule cited should
be the one that motivated the change).

- **P1** — 整理→思考→行动.  Don't jump straight to code.
  Look at project state + plan first.
- **P2** — 搜资料, 不拍脑门.  Before designing a feature,
  read 5+ sources.  Open `LITERATURE.md` first; if a relevant
  paper exists, cite it.  If not, `web_search` + add 1-line to
  LITERATURE.
- **P5** — 测通再 commit.  Tests must pass before commit; never
  commit broken tests to a passing baseline.
- **P14** — if you change code that drifts a doc, update the
  doc in the same commit.  Docs must stay current.
- **P17** — never claim green when it is yellow.  If you cannot
  verify a claim, say so explicitly or read the file first.
- **P22** — when stuck, STOP.  Look at the project state, then
  write a plan.  Do not brute-force past a wrong assumption.

## What NOT to do

- Do **not** create parallel doc structures (M33).  If
  PRINCIPLES.md covers it, point to it; do not restate.
- Do **not** commit to the `knowledge-graph-seed/` repo from
  this project (P21 — cross-project independence).  This
  project's scope is self-upgrade-agent only; KG-side work
  lives in its own repo.
- Do **not** invent features you have not verified (M79 / M82).
  "Yellow claimed as green" is the textbook failure mode.
- Do **not** `git add -A` (M25) except when explicitly doing a
  squashed initial commit (the user must authorize that
  exception in advance).
- Do **not** skip the "Read first" order.  PRINCIPLES.md is the
  project's operating contract; it must come before any code
  change.

## Commit message contract

Every commit message MUST contain at least one `P##` reference
(one of P1-P24) explaining which principle motivated the change.
The `commit-msg` hook enforces this.

**Hook install** (one-time per clone):

```bash
cp hooks/commit-msg .git/hooks/commit-msg
chmod +x .git/hooks/commit-msg
```

The template lives at `hooks/commit-msg` (in this repo, tracked).
After install, git will run it automatically on every commit.

Format:

```
<type>(<scope>): <short description> [P##]

[Detailed body, optionally citing more P-n values.]

[Cite one of P1-P24 here, e.g.:
 - P1  — "made a plan before coding"
 - P2  — "searched literature first"
 - P5  — "added tests before commit"
 - P14 — "fixed doc drift to match code"
 - P17 — "documented what is NOT shipped"
 - P22 — "stopped and planned when stuck"]
```

Allowed `P##` values: P1, P2, P3, P4, P5, P6, P7, P8, P9, P10,
P11, P12, P13, P14, P15, P16, P17, P18, P19, P20, P21, P22, P23,
P24.  See PRINCIPLES.md / PRINCIPLES_DETAIL.md for the complete
list.

## When in doubt

State the ambiguity, list the options you considered, pick one,
apply, and cite the principle in your commit message.  Same as
if you were the maintainer reading your PR.

## Recursive decomposition (per user meta-rule, 2026-07-13)

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

**Real L2 examples** (this project):

- "Make SUA doc maintenance self-updating" → decompose into:
  (a) AGENTS.md onboarding contract, (b) commit-msg hook for
  P-n enforcement, (c) bulk Last P20-verified refresh, (d) P2
  search spec with 'search-then-update' contract, (e) future
  pre-commit-doc-check hook.
- "Audit outdated docs" → decompose into:
  (a) grep for Last P20-verified <30 days, (b) per-file review
  for content drift, (c) prioritize fixes by user-facing impact,
  (d) fix in 1-commit-per-doc order.

**Anti-patterns** (what NOT to do):

- **Don't skip step 1** (THINK).  Jumping straight to coding
  on a big task = "yellow claimed as green" (P17).
- **Don't skip step 5** (INTEGRATE).  After 3 leaf commits, the
  whole task may still be incomplete; re-evaluate.
- **Don't decompose too finely** (1 commit per file is fine;
  1 commit per line is silly).  Stop when leaf size ≈ 1-3 files
  or 1-50 LOC.

Per P22 (stuck → plan) — when you find yourself unsure mid-task,
fall back to step 1 (THINK) and re-decompose.

Per P14 — if decomposition reveals a doc drift, fix the doc in
the same task (not a separate one).

## Operating workflow rules (per user 2026-07-13)

These are operating rules, not P-n — they govern how an agent
should *work*, not what the work *is*.  Keep them short; full
context lives in PRINCIPLES.md.

- **M-task-summary** — after every task completion, briefly
  state what went well (and what could improve).  Decide
  whether the project's docs should be updated based on what
  you learned; if yes, include the doc fix in the same task
  (per P14).
- **M-must-read** — for principles that are needed *every*
  session (e.g. P5 测通, P11 摘要+引用, P17 老实说, P22
  stuck→plan), surface them in `AGENTS.md` "Hard rules"
  above (already done).  **Do NOT** add to AGENTS.md the full
  text of every P-n — that bloats context.  AGENTS.md is a
  pointer to PRINCIPLES.md, not a copy (per P11).
- **M-context-snapshot** — before switching tasks, capture
  the current session's state to a `session_search`-able
  artifact (or to a brief note).  On return, load the snapshot
  to restore context.  **Don't** try to keep all context in
  the live conversation — overflow silently breaks the
  agent.  Implementation details (snapshot format, restore
  mechanism) are TODO (see todo list, task 8).
- **M-subtask-summary** — for multi-leaf tasks, each leaf
  commit should include a 1-2 line summary in its commit
  message body.  When the agent returns for the integration
  step (5-step loop step 5), it should NOT need to re-read
  every leaf's diff — the summaries suffice.

## See also

- `docs/PRINCIPLES.md` — the principles themselves (P1-P24)
- `docs/INDEX.md` — orientation map
- `docs/PROJECT_STATE.md` — current state (1-paragraph)
- `docs/PROJECT_STATE_DETAIL.md` — version history + vision
- `docs/PRINCIPLES_DETAIL.md` — full text of each P-n
- `docs/OBSERVATIONS.md` — empirical context from past runs

## Common pitfalls for new agents (per 2026-07-13 review)

These are the 4 categories of clue a fresh agent most often
ignores.  Read this section *before* starting any non-trivial work.

- **Open-work categories** — this project has 2 TODO items that
  are *not* in this file: (a) **knowledge lifecycle** (priority
  scoring + pruning for an ever-growing KG; user signal
  2026-07-13); (b) **session snapshot/restore mechanism** (for
  task-switching across context overflow; user signal 2026-07-13).
  Both are explicit-future, not immediate.  Don't start them
  without user prompt.
- **Snapshot location convention** — per M-context-snapshot,
  save session state to `C:\Users\LQ\AppData\Local\Temp\hermes-snapshot-<topic>-<date>.md`
  (session_search-able by title).  NOT in repo unless user asks
  (Temp gets cleared on session restart, so don't rely on
  long-term).
- **Session scope boundary** — this project's current session
  scope is `SUA-side onboarding + knowledge-base architecture`
  (8 commits since 2026-07-12, ending with `a37c33b`).  Don't
  touch `self-upgrade-agent/src/*` or `tests/*` (sibling's code)
  unless explicitly asked.  Don't touch `knowledge-graph-seed/`
  (P21 cross-project independence) unless explicitly asked.
- **M-task-summary vs M-subtask-summary** — M-task-summary is
  for *the whole task* (after all leaves commit, a 1-paragraph
  reflection on what went well).  M-subtask-summary is for
  *each leaf commit* (a 1-2 line summary in the commit message
  body).  Both are needed; do not skip either.  The integration
  step (5-step loop step 5) relies on leaf summaries to avoid
  re-reading every diff.

## Pre-existing pytest failure context (per 2026-07-13)

SUA has a pre-existing test failure in
`auto/test_planner_harness.py::test_plan_task_returns_list_of_strings`
(expects `list`, gets `RoundResult` from `core/planner.py`).
This is **sibling's** return-type change, NOT introduced by
this session's commits (verified via `git stash` in commit
`f10c604`).  Per M-rules: sibling's code = sibling's
responsibility.  Document but don't fix unless asked.

## Open work categories (per 2026-07-13)

- **Task 7 (TODO)**: SUA `docs/TODO_KNOWLEDGE_LIFECYCLE.md` —
  proposal for KG priority scoring + pruning + search bypass.
  User signaled: "knowledge base grows, need priority marking".
  Future; no implementation yet.
- **Task 8 (TODO)**: SUA `docs/TODO_SESSION_PERSISTENCE.md` —
  proposal for session snapshot/restore mechanism design.
  M-context-snapshot (above) is the rule; the *implementation*
  (snapshot format, restore mechanism, cross-session search) is
  task 8.  Future; no implementation yet.

## See also (session-specific)

- `C:\Users\LQ\AppData\Local\Temp\hermes-verify-sua-onboarding-20260713.py`
  — ad-hoc verify script for the 8-commit onboarding batch
  (30 checks; 30/30 PASS).
- `C:\Users\LQ\AppData\Local\Temp\hermes-snapshot-sua-onboarding-20260713.md`
  — session snapshot (recent commits, open todos, decisions).
  Load this on resume after context overflow.