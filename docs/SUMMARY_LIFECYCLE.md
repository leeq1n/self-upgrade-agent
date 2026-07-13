# Summary lifecycle (M-task-summary child-summary destroy contract)

> L0: How parent tasks consume + destroy N child summaries
> when M-task-summary fires.  Load when: parent task with
> N>1 child tasks completes; or when implementing M-task-
> summary's "summarize + clean up" cycle; or before
> committing a parent-level M-task-summary.

## The contract (3 steps, in order)

When M-task-summary completes for a parent task that has
N child tasks, the summary commit MUST:

1. **Pull** all N child summaries (from commit messages or
   Temp snapshots) into context.  Without this step, the
   parent summary is incomplete (per P14 docs-stay-current).
2. **Write** the parent's own summary (per the M-task-summary
   rule).
3. **Destroy** the N child summaries.  For in-commit-message
   summaries: leave in commit history (permanent by git
   design — destroy = "consumed, no longer needed in
   working set").  For Temp snapshot summaries: `git rm` /
   `os.unlink()` them in the same commit, with the destroy
   action **recorded in commit message body** (auditable,
   per P17 honest reporting).  Silent destroy = drift
   (violates P17).

## Why explicit destroy, not GC

- Silent deletion hides work (violates P17).
- GC may delete before parent consumes (race condition).
- Explicit destroy makes the consume-then-delete cycle an
  auditable event (commit message records the action).

## 奥卡姆 alignment

Keeping all summaries forever = doc bloat.  Child summaries
are intermediate state, not knowledge.  Only parent summary
(and grandparent + above) enters the knowledge base.

Per P7 (奥卡姆): destroy the temporary, keep the durable.

## Code-task variant

For code-bearing parent tasks, M-task-summary fires only
**after** joint / integration test passes (per P5 测通).
Test gate is the precondition; destroy is the postcondition.
**Both** must hold for "task done" to be true.

## Relationship to other rules

- **M-task-summary** (parent doc): the rule that fires this
  contract.  Parent M-task-summary = N child consumes + 1
  parent write + N child destroys.
- **M-subtask-summary** (child doc): the rule that produces
  each child summary (in commit message body).  This
  contract consumes M-subtask-summary outputs.
- **M-add-then-reduce** (OPERATING_RULES.md): the cycle that
  contains this contract.  Add = N child commits with
  M-subtask-summary; Reduce = parent M-task-summary + this
  destroy contract.

## See also

- `docs/OPERATING_RULES.md` — the parent doc with
  M-task-summary rule.
- `docs/COMMON_PITFALLS.md` § 3-way table — how
  M-task-summary vs M-subtask-summary vs M-learn relate.
- PRINCIPLES.md P17 (honest reporting) — the principle that
  makes "destroy action recorded in commit body" auditable.
- PRINCIPLES.md P5 (测通) — the test-gate precondition for
  code-bearing parent tasks.
- PRINCIPLES.md P7 (奥卡姆) — the principle that justifies
  destroy (don't keep redundant state forever).
- PRINCIPLES.md P14 (docs stay current) — the principle
  that makes the parent summary complete.