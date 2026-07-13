# Operating rules DETAIL (M-intent-parsing + M-learn full text)
Last P20-verified: 2026-07-13

> L0: L2 detail of M-intent-parsing and M-learn rules.
> Companion to `docs/OPERATING_RULES.md` (per P20 R5 +
> R6: 7KB-summary / _DETAIL-split pattern).  Load when:
> you need the full 3-action steps of M-intent-parsing,
> or the 3 sub-actions + dual-track triggers of M-learn.

This file is the L2 detail; the summary in
`docs/OPERATING_RULES.md` is the L0/L1.

## M-intent-parsing (full text)

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

## M-learn (full text)

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

## See also

- `docs/OPERATING_RULES.md` — parent doc (L0/L1 summary).
- PRINCIPLES.md P22 (stuck→plan) — meta-rule M-learn's
  recursive-decomposition trigger lives in step 5.
- `docs/RECURSIVE_DECOMPOSITION.md` — 5-step loop; step 5
  is M-learn's structural trigger.
- `docs/RECURSIVE_QUALITY.md` — "loop = decomposition +
  analogy + self-reference"; M-learn is the "analogy" arm
  applied to project memory.
- PRINCIPLES.md P7 (奥卡姆) — supports M-learn's
  no-op-leaves-no-trace discipline.
- `docs/MEMORY_TOOLS.md` — full decision matrix for memory
  tools (M-learn's "update knowledge base" sub-action uses
  this matrix).