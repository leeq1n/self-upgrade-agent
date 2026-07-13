# Add-then-reduce cycle (M-add-then-reduce M-rule)

> L0: 2-phase task lifecycle — Add (gather) + Reduce
> (consolidate).  Load when: planning a multi-leaf task,
> noticing doc/context bloat, or evaluating whether to
> apply M-learn's 3 sub-actions.

## The 2-phase cycle

Tasks have a 2-phase lifecycle; the cycle repeats:

- **Add (执行期)**: gather information, write code, push
  commits, draft docs, add Temp snapshots.  Permitted to
  be redundant during this phase — exploration needs
  slack.  No premature compression.
- **Reduce (整理期)**: compress, abstract, dedupe, destroy
  intermediate state.  Only triggered by signal (see
  below).  This is where M-learn's 3 sub-actions run.

## Trigger for reduce (3 signal types)

| Signal type | What triggers it | Who runs M-learn |
|---|---|---|
| Structural | parent-task INTEGRATE point (all sub-tasks done) | always |
| Context | user says "乱" / "compress" / "整理"; or agent notices context overflow risk | when signaled |
| Doc drift | > 2 files with Last P20-verified > 30 days, or M-self-audit flags multiple drifts | when signaled |

## Why signal-triggered, not always-on

Premature compression kills nuance; "I'll reduce later"
never happens.  Signal trigger balances both failure modes.

## Add phase MUST end before reduce phase begins

Don't mix.  Mixing = partial reductions leaving
inconsistencies (violates P11 摘要+引用).

## Reduce phase actions (per M-learn)

1. Pull all relevant intermediate state (child summaries,
   Temp snapshots, draft commits) into context
2. Run M-learn's 3 sub-actions (总结归纳 + 类比外推 + 更新知识库)
3. **Destroy intermediate state** — child summaries that
   have been consumed go to git history / Temp cleanup /
   `git rm` of intermediate files.  Destroy is a
   *postcondition* of reduce, not an afterthought.

## Anti-patterns

- **Don't** trigger reduce during add phase (premature).
- **Don't** skip reduce entirely (additive without reduce
  = doc bloat, per P13 + P14).
- **Don't** silent-destroy — every destroy must be a
  `git rm` / `os.unlink()` in a commit, with the destroy
  action recorded in commit message body (auditable,
  per P17).

## Relationship to other M-* rules

- **M-task-summary**: leaf reflection (always-on, no signal)
- **M-learn**: the *mechanism* of reduce; dual-track trigger
  (structural always + signal when noticed); 3 sub-actions
- **M-context-snapshot**: storage for add-phase
- **M-add-then-reduce**: the *cycle* of which M-learn is
  the reduce arm and M-task-summary is the per-leaf pause

## See also

- `docs/OPERATING_RULES.md` — M-add-then-reduce rule
  (parent doc, brief pointer).
- `docs/SUMMARY_LIFECYCLE.md` — M-task-summary child-
  summary destroy contract (related: a specific
  destroy pattern that fits the "destroy intermediate
  state" step).
- PRINCIPLES.md P11 (摘要+引用) — the principle that
  Add-phase-then-Reduce-phase is sequential (don't mix).
- PRINCIPLES.md P13 (concise) + P14 (docs stay current) —
  the principles that justify the Reduce phase.
- PRINCIPLES.md P17 (honest reporting) — the principle
  that makes "destroy action in commit body" auditable.