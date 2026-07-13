# Switch signals (M-context-snapshot when-to-snapshot heuristic)
Last P20-verified: 2026-07-13

> L0: When to take a session snapshot (M-context-snapshot
> rule trigger).  Load when: ending a task, noticing context
> overflow risk, or evaluating whether the current
> conversation is "a switch" that needs a snapshot.

## The 5 switch signals (any 1 fires the trigger)

A "switch" is any of these, regardless of perceived size
or duration:

1. **User says "switch"**: "switch to X" / "let's do
   something else" / mentions a different topic.
2. **Long pause**: User's message arrives after a long
   pause (context may have rotated out).
3. **Overflow risk**: Agent notices context overflow risk
   (file reads in this session > 50, multiple M-task-
   summary points, or conversation > N turns without a
   summary).
4. **New task type**: A new task type appears (debugging →
   design → write → ...).
5. **Agent self-switch**: Agent itself is about to switch
   focus (delegate_task, process management, long sleep).

## Why "small switch" can still need snapshot

Don't judge by perceived task size: a "small switch" can
still lose critical in-flight state (open todos,
uncommitted snapshots, mid-iteration assumptions).

Snapshot cost is low; recovery from missing snapshot is
high.

## Auto-trigger (not user-requested)

Snapshot trigger is **automatic, not user-requested**.
User should not have to remind agent to snapshot.

## Snapshot location convention

`C:\Users\LQ\AppData\Local\Temp\hermes-snapshot-<topic>-<date>.md`
(session_search-able by title).  NOT in repo unless user
asks (Temp gets cleared on session restart, so don't rely
on long-term).

## What goes in a snapshot

Per M-context-snapshot rule: capture the current session's
state to a `session_search`-able artifact.  Typical
content:

- Recent commits (last 5-10) with 1-line summaries
- Open todos (your todo list, or a M-context-snapshot
  specific list)
- Key decisions (especially non-obvious ones)
- Recurring patterns (per M-learn)
- User meta-rules (e.g. "trust you / next / go → execute")
- Verification status (tests pass / fail / skip)

## Anti-patterns

- **Don't** judge by perceived size — small switches can
  lose critical state.
- **Don't** wait for user to ask — snapshot is automatic.
- **Don't** put snapshots in repo (cleared on session
  restart anyway; use Temp convention).
- **Don't** snapshot a context that's already
  session_search-able (search instead).

## See also

- `docs/OPERATING_RULES.md` — M-context-snapshot rule
  (parent doc).
- `docs/TODO_SESSION_PERSISTENCE.md` — TODO (formal
  proposal for snapshot/restore mechanism).
- `docs/MEMORY_TOOLS.md` — when to use which memory tool
  (snapshots are 1 of several memory layers).
- PRINCIPLES.md P11 (摘要+引用) — the principle that keeps
  this doc focused on signals (other detail in OPERATING_RULES
  + M-context-snapshot parent rule).
- PRINCIPLES.md P22 (stuck→plan) — the principle that
  motivates proactive snapshot (don't lose context when
  switching mid-thought).