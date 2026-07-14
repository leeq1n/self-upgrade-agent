# TODO_SESSION_PERSISTENCE detail (L2 companion)

> L0: L2 detail of t8 proposal — open questions + implementation
> steps.  Companion to `docs/TODO_SESSION_PERSISTENCE.md`
> (per P20 R5 + R6: 7KB-summary / _DETAIL-split pattern; this
> file holds the deferred detail).  Load when: implementing
> the proposal, resolving open questions, or planning the
> commit sequence.
Last P20-verified: 2026-07-13

This file is the L2 detail; the summary in
`docs/TODO_SESSION_PERSISTENCE.md` is the L0/L1.

## Open questions (per M-self-application 4 levels)

These are **deferred** — answer when first snapshot
implementing this proposal is written.

1. **Format enforcement**: should snapshots have a strict
   YAML frontmatter (machine-readable) or stay free-form
   markdown (human-readable)?
2. **Tier 1 vs Tier 2**: default to Tier 2 (in repo) for
   all snapshots, or only when user signals "save
   persistently"?
3. **Snapshot count limit**: should there be a per-topic
   cap (e.g. keep last 5 snapshots of "sua-onboarding")?
4. **Cross-project sharing**: if user works on multiple
   projects, do snapshots conflict by topic name?

## Implementation steps (when ready)

Per "1 commit = 1 logical feature":

1. **Commit 1**: write this proposal doc + add reference
   from `docs/OPERATING_RULES.md` M-context-snapshot 段
   + `AGENTS.md` See-also
2. **Commit 2 (later)**: implement Tier 1 snapshot format
   (write_file helper script)
3. **Commit 3 (later)**: implement Tier 2 archive step
   (move to `.hermes/snapshots/`)
4. **Commit 4 (later)**: implement restore protocol helper
5. **Commit 5 (later)**: write first real snapshot using
   the new format + verify restore works

Per "P23 doc > script with nuance": 1-2 doc-only commits
first, then scripts when design is stable.

## See also

- `docs/TODO_SESSION_PERSISTENCE.md` — parent doc (L0/L1
  summary).
- `docs/OPERATING_RULES.md` — M-context-snapshot rule
  (parent rule for this proposal).
- `docs/SWITCH_SIGNALS.md` — 5 trigger signals for snapshot
  creation.
- `docs/ADD_THEN_REDUCE.md` — 2-phase lifecycle (where
  destroy step fits).
- PRINCIPLES.md P14 (docs stay current) — the principle
  that this proposal operationalizes.
- `~/AppData/Local/Temp/hermes-snapshot-sua-onboarding-20260713.md`
  — first snapshot created in this session (4.6KB, 103L).
- `~/AppData/Local/Temp/hermes-snapshot-self-upgrade-agent-20260713.md`
  — second snapshot created in this session (6.5KB, 153L,
  written after NEW-3 sync).
- agent-onboarding skill, `references/M_RULE_AUTHORING.md`
  (skill) — 7-section recipe for adding M-* rules (apply
  the 3-condition gate before adding any new rule).
  this proposal, it should follow the recipe.