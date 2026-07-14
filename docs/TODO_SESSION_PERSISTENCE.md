# TODO: session persistence (snapshot/restore mechanism)

> L0: Proposal for formalizing M-context-snapshot —
> snapshot format, location, restore protocol, lifecycle.
> Load when: ending a long session, designing the snapshot
> workflow, or evaluating whether to keep / promote / drop
> snapshot files.
Last P20-verified: 2026-07-13

**Status**: TODO (proposal only — not yet implemented).
**Priority**: LOW (M-context-snapshot rule is mature; this
doc captures design intent for future implementation).
**Triggered by**: snapshot files are being created (e.g.
`~/AppData/Local/Temp/hermes-snapshot-sua-onboarding-20260713.md`)
but no formal design doc exists.  The M-context-snapshot
rule exists in 3 places (skill, project, AGENTS.md See-also)
but the **mechanism** (what to capture, how to restore,
when to destroy) is implicit.

## Current state (per audit)

- **M-context-snapshot rule**: CODIFIED in 3 places:
  1. agent-onboarding skill, `references/OPERATING_RULES.md`
     (M-context-snapshot 段)
  2. `docs/OPERATING_RULES.md` (project, M-context-snapshot 段)
  3. `AGENTS.md` See-also (pointer to `docs/SWITCH_SIGNALS.md`
     + `docs/OPERATING_RULES.md`)

- **Snapshot files**: created ad-hoc in
  `~/AppData/Local/Temp/hermes-snapshot-<topic>-<date>.md`.
  Examples observed:
  - `hermes-snapshot-sua-onboarding-20260713.md` (4.6KB,
    103 lines)
  - `hermes-snapshot-self-upgrade-agent-20260713.md`
    (6.5KB, 153 lines, written this session)

- **Restore mechanism**: NONE.  Snapshot files are **read**
  manually by fresh agent (or not at all).

- **Lifecycle**: implicit.  Snapshot files **accumulate** in
  Temp directory; not destroyed (Temp gets cleared on
  session restart per OS convention, but not actively
  managed).

- **Cross-session search**: not integrated.  Snapshot files
  are session_search-able by title (per M-context-snapshot
  rule) but no explicit search ritual is documented.

## What's missing (the gap)

Per P22 (stuck→plan), the snapshot mechanism has **rule +
practice** but no **design**:

1. **Snapshot format**: not standardized.  Current
   snapshots are free-form markdown with whatever content
   the agent felt was relevant.  Should there be a
   minimum schema?

2. **Snapshot location**: Temp is fine for ephemeral, but
   is it the right place?  Per user 2026-07-13: "snapshot
   在 Temp: session restart 会丢失, 真正 persistent snapshot
   应该 in repo (待 t8 设计)".  This doc is exactly that
   design.

3. **Restore protocol**: no recipe for "I have a snapshot
   file, how do I use it?".  Current practice is "read it,
   use context".  Could be more structured.

4. **Lifecycle**: when create, when destroy, when archive.
   Per M-add-then-reduce: snapshot is **intermediate state**
   that should be **destroyed** when consumed.  But what
   counts as "consumed"?

5. **Cross-session search**: integration with session_search
   (title-based) is mentioned in M-context-snapshot rule,
   but no specific search ritual (e.g. "search for
   'hermes-snapshot' tag" or "search for 'snapshot-{topic}'").

## Proposal (the design)

### Snapshot format (minimum schema)

```yaml
# Header (always required)
topic: <short-name>           # e.g. "sua-onboarding"
date: YYYY-MM-DD              # creation date
session_id: <id>              # Hermes session id (if known)
task: <1-line description>    # what was being worked on

# Body sections (recommended)
## Project state            # git status, branches, key files
## Recent commits            # last N commits
## Pending TODOs            # active todo list
## Decisions made           # key decisions with rationale
## Open questions           # things that need resolution
## Next action              # what to do when resuming
## See also                 # pointers to project docs
```

### Snapshot location (2-tier)

- **Tier 1 (ephemeral, default)**: `~/AppData/Local/Temp/hermes-snapshot-<topic>-<date>.md`
  - Pros: no repo clutter, cleared on OS restart
  - Cons: lost on restart, no cross-session persistence
  - Use when: within-session resume only

- **Tier 2 (persistent, opt-in)**: `<project>/.hermes/snapshots/<topic>-<date>.md`
  - Pros: persists across restarts, in-repo for version control
  - Cons: clutter if over-used, needs .gitignore if not tracked
  - Use when: cross-session resume (e.g. next-day pickup)

  Per user preference: "真正 persistent snapshot 应该 in repo".

### Restore protocol (recipe)

When resuming from a snapshot:

1. **Locate snapshot**: `find . -name "hermes-snapshot-*.md"` (Tier 2)
   or `ls ~/AppData/Local/Temp/hermes-snapshot-*.md` (Tier 1)
2. **Read header**: extract topic + date (decides if relevant)
3. **Read "Project state"**: git log --oneline -N to confirm state
4. **Read "Pending TODOs"**: load into todo list (per M-task-summary invariant)
5. **Read "Next action"**: this is the **first** thing to do on resume
6. **Per "Open questions"**: resolve or defer (per M-intent-parsing)
7. **Skip "Decisions made"**: context, not action

### Lifecycle (per M-add-then-reduce)

- **Add phase**: M-context-snapshot fires → write snapshot to Tier 1
- **Reduce phase**: M-task-summary consumes snapshot → write summary to commit message body → destroy Tier 1 snapshot (per M-add-then-reduce destroy contract)

Lifecycle trigger:
- **Create**: per M-context-snapshot signal (5 signals in SWITCH_SIGNALS.md)
- **Consume**: at task resume (read once, then "consumed")
- **Archive**: when consumed, archive to Tier 2 (per user "in repo" preference)
- **Destroy**: when archive is complete (record in commit message body per M-add-then-reduce "auditable destroy")

### Cross-session search ritual

- `session_search(query="hermes-snapshot", limit=10)` — find all snapshots by topic
- Filter by date (most recent first)
- Read header to decide relevance
- Use "Project state" + "Next action" to resume

## Integration with existing M-rules

| M-rule | Role |
|---|---|
| M-context-snapshot | Triggers snapshot creation (5 signals in SWITCH_SIGNALS.md) |
| M-task-summary | Consumes snapshot (reads "Pending TODOs" + "Next action") |
| M-add-then-reduce | Owns destroy step (Tier 1 snapshot → archive → destroy) |
| M-self-audit | Audits snapshot mechanism (does it work? are snapshots discoverable?) |

## Open questions

See `docs/TODO_SESSION_PERSISTENCE_DETAIL.md` §Open questions
for the 4 deferred questions.

## Implementation steps (when ready)

See `docs/TODO_SESSION_PERSISTENCE_DETAIL.md` §Implementation
steps for the 5-commit roadmap.

## See also

- `docs/TODO_SESSION_PERSISTENCE_DETAIL.md` — L2 detail
  companion (per P20 R5 + R6: 7KB-summary / _DETAIL-split
  pattern; holds open questions + implementation steps +
  extra see-also references).
- `docs/OPERATING_RULES.md` — M-context-snapshot rule
  (parent rule for this proposal).
- `docs/SWITCH_SIGNALS.md` — 5 trigger signals for snapshot
  creation.
- `docs/ADD_THEN_REDUCE.md` — 2-phase lifecycle (where
  destroy step fits).
- PRINCIPLES.md P14 (docs stay current) — the principle
  that this proposal operationalizes.