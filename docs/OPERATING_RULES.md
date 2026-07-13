# Operating workflow rules (per user 2026-07-13)
Last P20-verified: 2026-07-13

> L0: 7 operating rules (M-task-summary, M-must-read,
> M-context-snapshot, M-subtask-summary, M-intent-parsing,
> M-learn, M-add-then-reduce) for how agent should work,
> not what the work is.  Load when ending a task, switching
> tasks (even briefly), unsure which tools to use, processing
> messy user input, at a decomposition integration point,
> or when context feels cluttered.
>
> **Every task completion = automatic M-task-summary** (this
> is the workflow's invariant, not a choice).  Multi-leaf
> tasks additionally fire M-subtask-summary per leaf.
> Per user 2026-07-13 '做完大任务记得自动写总结': the rule
> fires on task-end, not on user request.

## When to use this

Load this doc when:
- Ending a task (M-task-summary).
- Switching tasks (M-context-snapshot) — even briefly,
  even if the switched-away task is small.
- Unsure which docs to read first (M-must-read).
- Mid multi-leaf task and need to summarize (M-subtask-summary).
- User input is messy / scattered / mixes multiple asks
  (M-intent-parsing).
- At a decomposition integration point (all sub-tasks of a
  parent task complete; M-learn).
- Context / docs / commit history feels cluttered, or
  multiple docs drifted (M-add-then-reduce signal).

## What these rules are

These are **operating workflow rules** (M-* prefix), not P-n
— they govern how the agent *works*, not what the work *is*.
Full context lives in PRINCIPLES.md (P-n list) and
PRINCIPLES_DETAIL.md (P-n full text).

Per P23 (doc > script with nuance): "Don't write a script
until doc rule has been broken 3+ times" — same applies to
adding new P-n.  These 7 rules are workflow guidance, not
principles, so they live in OPERATING_RULES.md, not
PRINCIPLES.md.

## The 7 rules

### M-task-summary

After every task completion, briefly state what went well
(and what could improve).  Decide whether the project's docs
should be updated based on what you learned; if yes, include
the doc fix in the same task (per P14 docs-stay-current).

**Child-summary destroy contract** (per user 2026-07-13):
when M-task-summary completes for a parent task that has
N child tasks, the summary commit MUST:

1. **Pull** all N child summaries (from commit messages or
   Temp snapshots) into context.  Without this step,
   parent summary is incomplete (per P14).
2. **Write** the parent's own summary (per the rule above).
3. **Destroy** the N child summaries.  For in-commit-message
   summaries: leave in commit history (permanent by git
   design — destroy = "consumed, no longer needed in
   working set").  For Temp snapshot summaries: `git rm` /
   `os.unlink()` them in the same commit, with the destroy
   action **recorded in commit message body** (auditable,
   per P17).  Silent destroy = drift (violates P17).

**Why explicit destroy, not GC**: silent deletion hides
work (violates P17); GC may delete before parent consumes
(race condition); explicit destroy makes the consume-then-
delete cycle an auditable event.

**奥卡姆 aligned**: keeping all summaries forever = doc
bloat.  Child summaries are intermediate state, not
knowledge.  Only parent summary (and grandparent + above)
enters the knowledge base.

**Code-task variant**: for code-bearing parent tasks,
M-task-summary fires only AFTER joint / integration test
passes (P5 测通).  Test gate is the precondition; destroy
is the postcondition.  Both must hold for "task done" to
be true.

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

**Switch signals** (per user 2026-07-13): a "switch" is any
of these, regardless of perceived size or duration:
- User says "switch to X" / "let's do something else" /
  mentions a different topic
- User's message arrives after a long pause (context may
  have rotated out)
- Agent notices context overflow risk (file reads in this
  session > 50, multiple M-task-summary points, or
  conversation > N turns without a summary)
- A new task type appears (debugging → design → write → ...)
- Agent itself is about to switch focus (delegate_task,
  process management, long sleep)

**Don't** judge by perceived task size: a "small switch"
can still lose critical in-flight state (open todos,
uncommitted snapshots, mid-iteration assumptions).
Snapshot cost is low; recovery from missing snapshot is
high.

**Snapshot trigger is automatic, not user-requested**.
User should not have to remind agent to snapshot.

**Snapshot location convention**:
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

**Trigger is dual-track** (per M-add-then-reduce cycle):
- **Structural** (always): at every parent-task INTEGRATE
  point (RECURSIVE_DECOMPOSITION step 5).  Cheap and
  default — runs the 3 sub-actions at minimal depth.
- **Signal** (when signaled): context overflow risk, user
  says "乱" / "compress" / "整理", doc drift detected
  (> 2 files with Last P20-verified > 30 days), or
  agent notices clutter.  Runs deeper — may catch
  patterns the structural trigger would miss.

Both tracks run the same 3 sub-actions; only the depth
differs.  Per M-add-then-reduce: leaf-end is NOT a
trigger (that's M-task-summary's job; structural trigger
fires at parent INTEGRATE only).

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

### M-add-then-reduce

Tasks have a 2-phase lifecycle; the cycle repeats:

- **Add (执行期)**: gather information, write code, push
  commits, draft docs, add Temp snapshots.  Permitted to
  be redundant during this phase — exploration needs
  slack.  No premature compression.
- **Reduce (整理期)**: compress, abstract, dedupe, destroy
  intermediate state.  Only triggered by signal (see
  below).  This is where M-learn's 3 sub-actions run.

**Trigger for reduce (3 signal types)**:

| Signal type | What triggers it | Who runs M-learn |
|---|---|---|
| Structural | parent-task INTEGRATE point (all sub-tasks done) | always |
| Context | user says "乱" / "compress" / "整理"; or agent notices context overflow risk | when signaled |
| Doc drift | > 2 files with Last P20-verified > 30 days, or M-self-audit flags multiple drifts | when signaled |

**Why signal-triggered, not always-on**: premature
compression kills nuance; "I'll reduce later" never
happens.  Signal trigger balances both failure modes.

**Add phase MUST end before reduce phase begins** — don't
mix.  Mixing = partial reductions leaving inconsistencies
(violates P11 摘要+引用).

**Reduce phase actions** (per M-learn):
1. Pull all relevant intermediate state (child summaries,
   Temp snapshots, draft commits) into context
2. Run M-learn's 3 sub-actions (总结归纳 + 类比外推 + 更新知识库)
3. **Destroy intermediate state** — child summaries that
   have been consumed go to git history / Temp cleanup /
   `git rm` of intermediate files.  Destroy is a
   *postcondition* of reduce, not an afterthought.

**Don't** trigger reduce during add phase (premature).
**Don't** skip reduce entirely (additive without reduce =
doc bloat, per P13 + P14).  **Don't** silent-destroy —
every destroy must be a `git rm` / `os.unlink()` in a
commit, with the destroy action recorded in commit
message body (auditable, per P17).

**Relationship to other M-* rules**:
- **M-task-summary**: leaf reflection (always-on, no signal)
- **M-learn**: the *mechanism* of reduce; dual-track trigger
  (structural always + signal when noticed); 3 sub-actions
- **M-context-snapshot**: storage for add-phase
- **M-add-then-reduce**: the *cycle* of which M-learn is
  the reduce arm and M-task-summary is the per-leaf pause

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
- **Don't** silent-destroy intermediate state — every
  destroy goes in a commit message (M-add-then-reduce
  anti-pattern).
- **Don't** skip M-context-snapshot because "the switch is
  brief / task is small" — small switches lose critical
  in-flight state (M-context-snapshot anti-pattern;
  per user 2026-07-13).

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
- PRINCIPLES.md P7 (奥卡姆) — supports M-add-then-reduce's
  destroy step (奥卡姆 = no redundant storage).
- PRINCIPLES.md P17 (honest reporting) — supports
  M-add-then-reduce's auditable-destroy requirement.
- docs/COMMON_PITFALLS.md — context-switching pitfalls
  (related but distinct from this doc).
- docs/MEMORY_TOOLS.md — full decision matrix for memory
  tools (M-learn's "update knowledge base" sub-action uses
  this matrix).