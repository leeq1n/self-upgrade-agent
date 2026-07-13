# Operating workflow rules (per user 2026-07-13)
Last P20-verified: 2026-07-13

> L0: 6 operating rules (M-task-summary, M-must-read,
> M-context-snapshot, M-subtask-summary, M-intent-parsing,
> M-learn) for how agent should work, not what the work is.
> Load when ending a task, switching tasks, unsure which
> tools to use, processing messy user input, or at a
> decomposition integration point.

## When to use this

Load this doc when:
- Ending a task (M-task-summary).
- Switching tasks (M-context-snapshot).
- Unsure which docs to read first (M-must-read).
- Mid multi-leaf task and need to summarize (M-subtask-summary).
- User input is messy / scattered / mixes multiple asks
  (M-intent-parsing).
- At a decomposition integration point (all sub-tasks of a
  parent task complete; M-learn).

## What these rules are

These are **operating workflow rules** (M-* prefix), not P-n
— they govern how the agent *works*, not what the work *is*.
Full context lives in PRINCIPLES.md (P-n list) and
PRINCIPLES_DETAIL.md (P-n full text).

Per P23 (doc > script with nuance): "Don't write a script
until doc rule has been broken 3+ times" — same applies to
adding new P-n.  These 6 rules are workflow guidance, not
principles, so they live in OPERATING_RULES.md, not
PRINCIPLES.md.

## The 6 rules

### M-task-summary

After every task completion, briefly state what went well
(and what could improve).  Decide whether the project's docs
should be updated based on what you learned; if yes, include
the doc fix in the same task (per P14 docs-stay-current).

### M-must-read

For principles that are needed *every* session (e.g. P5 测通,
P11 摘要+引用, P17 老实说, P22 stuck→plan), surface them in
`AGENTS.md` "Hard rules" above (already done).  **Do NOT**
add to AGENTS.md the full text of every P-n — that bloats
context.  AGENTS.md is a pointer to PRINCIPLES.md, not a
copy (per P11).

### M-context-snapshot

Before switching tasks, capture the current session's state
to a `session_search`-able artifact (or to a brief note).
On return, load the snapshot to restore context.  **Don't**
try to keep all context in the live conversation — overflow
silently breaks the agent.  Implementation details
(snapshot format, restore mechanism) are TODO (see todo
list, task 8).

Snapshot location convention:
`C:\Users\LQ\AppData\Local\Temp\hermes-snapshot-<topic>-<date>.md`
(session_search-able by title).  NOT in repo unless user
asks (Temp gets cleared on session restart, so don't rely
on long-term).

### M-subtask-summary

For multi-leaf tasks, each leaf commit should include a
1-2 line summary in its commit message body.  When the agent
returns for the integration step (5-step loop step 5), it
should NOT need to re-read every leaf's diff — the summaries
suffice.

### M-intent-parsing

When user input is messy — multiple asks interleaved,
self-corrections mid-sentence, terse fragments, mixed
languages, contradictions — **first find the user's actual
goal** (the "main contradiction", per Chinese 主要矛盾),
**then plan backward from the goal**.  This is structurally
identical to agent self-planning: identify the target, then
derive the path.  The difference is that the target comes
from parsing messy input, not from a clean task description.

Three actions, in order:

1. **Extract the goal**: ignore phrasing, surface the
   underlying intent.  The user may say "this and that and
   also..."; the goal is one of those things, often the last
   one.  State the goal in one sentence back to the user (or
   to yourself if context-only).
2. **Identify the main contradiction**: among multiple asks,
   which one is the **central problem**?  The others are
   either prerequisites, examples, or noise.  Per 抓主要
   矛盾: do not enumerate all asks, rank them.
3. **Plan backward**: from the goal, derive the steps needed.
   Compare to user's stated steps; the user's path may be
   incomplete or out-of-order.  Correct in your plan, but
   only after confirming the goal.

**Don't** apply this to clean task descriptions (overhead > value).

**Anti-pattern**: don't ask the user to clarify before you
have an interpretation.  State your interpretation + the
inference steps, then ask only the question that remains
ambiguous.  Per user 2026-07-10 'trust you / next / go →
default EXECUTE, not ask again'.

### M-learn

After a decomposition **integration point** (i.e. all
sub-tasks of a parent task complete — RECURSIVE_DECOMPOSITION
5-step loop step 5), ask: did this task surface something
that generalizes beyond itself?  If yes, capture it.

**Trigger is structural, not time-based**: fires at every
parent-task integration point, NOT at every leaf-end (those
use M-task-summary).  Leaf-level summary is reflection on
"this task"; M-learn is reflection on "this class of tasks".

Three sub-actions, in order:

1. **总结归纳 (Summarize and generalize)**: from the leaf
   summaries (or M-task-summary outputs), extract the
   pattern.  What repeats?  What was the common shape across
   the sub-tasks?
2. **类比外推 (Analogical extrapolation)**: compare the
   pattern to prior rules / skills / past failures.  Does it
   match an existing principle (P-n)?  Does it extend one?
   Or is it genuinely new?  Per RECURSIVE_QUALITY.md:
   loop = decomposition + analogy + self-reference; this
   step is the "analogy" arm.
3. **更新知识库 (Update knowledge base)**: if the
   generalization is real, update the appropriate artifact:
   - New principle?  → propose in PRINCIPLES.md + PRINCIPLES_DETAIL.md
   - New workflow rule?  → propose in OPERATING_RULES.md
   - New tool quirk / env fact?  → memory tool
   - New project-specific pattern?  → relevant docs/*.md
   - None of the above (one-off)?  → DONE.md or discard

**Per 奥卡姆 (P7) — no-op leaves no trace**: if the three
sub-actions surface nothing generalizable, do nothing
visible.  Don't write "checked, nothing new".  Silent
no-op is the discipline — every "checked" line is itself
a candidate P-n violation (writing work, not the work).

**Relationship to other M-* rules**:
- **M-task-summary**: leaf-end (1 task done).  M-learn:
  integration-end (N sub-tasks done + parent re-evaluated).
- **M-subtask-summary**: per-leaf commit message.  M-learn
  reads M-subtask-summary outputs as input.
- **M-context-snapshot**: before task switch.  M-learn is
  AFTER integration, not before switch.

**Anti-pattern**: don't trigger M-learn at every leaf
end (that's M-task-summary's job).  Don't write a
"checked, nothing new" line — silent no-op.  Don't update
a doc unless the pattern is genuinely reusable (奥卡姆).

## Anti-patterns (what NOT to do)

- **Don't** skip M-task-summary at task end (lose
  meta-learning).
- **Don't** duplicate P-n full text in AGENTS.md (violates
  M-must-read + bloat).
- **Don't** try to keep all context in live conversation
  (silent overflow risk).
- **Don't** skip M-subtask-summary in multi-leaf tasks
  (integration step will need to re-read every diff).
- **Don't** enumerate every ask in messy user input before
  identifying the goal (M-intent-parsing anti-pattern).
- **Don't** write "M-learn checked, nothing new" — silent
  no-op is the discipline (奥卡姆; M-learn anti-pattern).

## See also

- AGENTS.md "Operating workflow rules"段 will be removed in
  a follow-up commit (it should be a 1-line pointer, not the
  full text).
- PRINCIPLES.md P11 (摘要+引用) — the principle that keeps
  AGENTS.md short.
- PRINCIPLES.md P14 (docs stay current) — the principle that
  M-task-summary operationalizes.
- PRINCIPLES.md P17 (honest reporting) — the principle that
  M-task-summary's "what could improve" enforces.
- PRINCIPLES.md P22 (stuck→plan) — meta-rule M-learn's
  recursive-decomposition trigger lives in step 5.
- docs/RECURSIVE_DECOMPOSITION.md — 5-step loop; step 5 is
  M-learn's structural trigger.
- docs/RECURSIVE_QUALITY.md — "loop = decomposition +
  analogy + self-reference"; M-learn is the "analogy" arm
  applied to project memory.
- docs/COMMON_PITFALLS.md — context-switching pitfalls
  (related but distinct from this doc).
- docs/MEMORY_TOOLS.md — full decision matrix for memory
  tools (M-learn's "update knowledge base" sub-action uses
  this matrix).