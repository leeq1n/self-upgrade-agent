# M-self-audit (full text)
Last P20-verified: 2026-07-13

> L0: Self-audit rule for new-agent discoverability.
> Load when: ending a task, before declaring "all pass",
> or when adding new doc/section.  Per 3-condition gate
> (M_RULE_AUTHORING.md): reusable across projects ✓,
> triggerable (before "all pass" or after big doc change) ✓,
> 3+ occurrences observed ✓ → promoted to full M-rule
> (per 2026-07-13 session).

## When to apply

Apply M-self-audit at multiple points:

- **Before declaring a task done** (per M-task-summary): did
  I leave the project in a state where a fresh agent could
  pick up?
- **After adding a new doc / section / reference**: is it
  discoverable from L0 (AGENTS.md, INDEX.md, skill's
  decision table)?  Or is it buried?
- **After adding a 4th section to AGENTS.md** (per
  EXTENSIONS.md X2 agent-onboarding skill, M_RULE_AUTHORING
  Pitfall 1: "AGENTS.md has a 300-line soft cap; beyond
  ~10 M-* rules the enumeration alone consumes significant
  AGENTS.md budget"): am I bloating AGENTS.md past its
  300-line cap?  Should I extract to a dedicated doc instead?
- **Before saying "all pass" / "complete"**: did I trace
  what a fresh agent would do with the current state?  Or
  did I just verify my own work?

## The question (always-asked)

> "If a new agent entered this project right now, could it
> read what it needs to do the task?"

This is the **single question** to keep asking.  If yes,
proceed.  If no, **fix in same task** (per P14 docs stay
current + M-add-then-reduce's "fix in same task" rule).

## Audit checklist (per 2026-07-13 batch)

1. **New-agent simulation**: load always-read files
   (AGENTS.md, PRINCIPLES.md), trace what fresh agent would
   know.  Can the agent find the answer to "what should I do
   next?" in those files?
2. **Audit ALL docs/*.md for L0 line** (P20 R9 ≤120 chars).
   Any doc missing L0 is a discoverability gap.
3. **Check AGENTS.md read-order references ALL non-trivial
   docs** (P20 R2 + R3 + L0 brief principle).  Any doc
   referenced in PRINCIPLES.md or OPERATING_RULES.md should
   be in AGENTS.md See-also.
4. **Verify "conditional vs always-on" split** (per
   P20 R3).  Conditional docs need trigger annotations
   ≥ 3 words.
5. **Cap check**: AGENTS.md ≤ 300 lines, SKILL.md ≤ 100 lines.
   If over, extract to dedicated docs (per M_RULE_AUTHORING
   "split pattern").
6. **Verify-before-edit** (per user 2026-07-14 +
   Claude Code "read before edit" pattern, lightweight
   adaptation; uses project's existing R10 marker):
   before any Edit / Write on a file you have read
   previously in this session, **read the file's
   Last P20-verified marker** (per R10 / P10) and
   compare to your memory of when you last read it.
   If you can't recall, or your memory is from BEFORE
   the marker, **re-read the full file** before
   editing.  After successful edit, bump the file's
   Last P20-verified to today's date (and the new
   commit hash if you're committing in the same turn).

   **Rationale**: agents can hold stale state in
   memory after context compactions; the file's
   marker is the cross-session truth.  This rule
   applies at the audit-checkpoint, not at every
   tool call — the trigger is "before Edit/Write
   on a previously-read file" (per M-add-then-reduce
   signal-trigger design; not per-tool-call).

   **Anti-patterns**:
   - Trust "I remember this file" without
     checking the marker first.
   - Skip the check for "small edits" — small
     edits on stale state are the most common
     cause of silently overwritten changes.
   - Update the marker without actually editing
     the file (marker must be true).

   **Caveats** (per P17 honest reporting):
   - Date-only marker has same-day granularity.
     Future: extend to "date + commit hash" via
     separate commit.
   - "Memory" is implicit; long sessions may
     have rotated context.  Safe default: if you
     can't recall, re-read.
   - This rule applies at audit-checkpoint
     (before "all pass" / before commit), not
     automatically at every tool call.  For
     per-tool-call verification, see Claude
     Code's "Read before Edit" hook (out of
     scope here).

## Anti-patterns (what NOT to do)

- **Don't** declare "all pass" without M-self-audit
  (per M82 + P17 never claim green when yellow).
- **Don't** apply M-self-audit to a single file when
  the change is project-wide (audit all relevant files).
- **Don't** add 4th section to AGENTS.md without checking
  cap (per M_RULE_AUTHORING 7-section recipe — same
  "bloating" pattern is the trigger for this rule).
- **Don't** skip M-self-audit because "I just verified
  my own work" (M-self-audit's purpose is to detect what
  self-verification misses — per M-self-application caveat).

## Relationship to other M-* rules

- **M-task-summary**: M-self-audit fires **before** declaring
  task done; M-task-summary fires **at** task end.
  M-self-audit = pre-task-summary check.
- **M-intent-parsing**: M-self-audit = "could new agent read
  this?".  M-intent-parsing = "did I parse user's goal
  correctly?".  Both audit the agent's understanding.
- **M-add-then-reduce**: M-self-audit is a **signal trigger**
  for reduce phase (per M-add-then-reduce: "M-self-audit
  flags multiple drifts" → fire reduce).

## See also

- `docs/OPERATING_RULES.md` — M-self-audit brief pointer.
- `docs/RECURSIVE_DECOMPOSITION.md` — 5-step loop; step 5
  (INTEGRATE) is when M-self-audit is most valuable.
- `docs/COMMON_PITFALLS.md` — 4 categories of fresh-agent
  misses (M-self-audit's audit checklist covers these).
- PRINCIPLES.md P17 (老实说) — the principle that M-self-
  audit's "verify before claiming" enforces.
- PRINCIPLES.md P14 (docs stay current) — the principle
  that M-self-audit's "fix in same task" enforces.