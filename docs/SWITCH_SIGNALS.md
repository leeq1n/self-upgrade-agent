# Switch signals (M-context-snapshot when-to-snapshot heuristic)
Last P20-verified: 2026-07-14

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

`sua-snapshot-<topic>-<date>.md` (use
`tempfile.mkstemp(prefix="sua-snapshot-",
dir=os.environ.get("TEMP", "/tmp"))` per OS-safe
tempfile path convention)
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

## Switch action protocol (per user 2026-07-13)

When a switch signal fires (any of the 5 above), the
agent MUST take ONE of these actions.  No silent merges;
no "do nothing".

**Decision tree**:

1. **Same-topic refinement** (user clarifies or adds detail
   to current task): M-context-snapshot only — capture
   state to Temp (`sua-snapshot-<topic>-<date>.md`),
   then continue current batch.  No parent verification,
   no batch close.

2. **New topic / clear boundary** (user explicitly shifts
   focus or starts a different task type):
   - Close current batch: fire M-task-summary → write
     parent verification commit (per
     `docs/SUMMARY_LIFECYCLE.md`).
   - M-context-snapshot: capture pre-switch state to Temp.
   - Begin new batch with its own child commits.

3. **Tiny insertion** ("对了" / "补充一句" / 1-2 sentence
   rule clarification): inline action — apply the
   clarification immediately.  Snapshot only if it
   changes the current batch's context in a way future
   steps need to know about.

**Anti-patterns**:

- **Don't merge switch task into current batch.** This
  bloats the parent's child-summary list and breaks
  M-task-summary's destroy contract (the parent wasn't
  the actual parent of the merged work).
- **Don't ignore switch signals.** Even small insertions
  must be classified (refinement / new topic / tiny) —
  silent "this looks small enough to ignore" leads to
  lost state.
- **Don't fire M-task-summary for 1-commit insertions**
  unless it's actually a new task boundary.  Parent
  verification commits are git history — keep them
  reserved for actual batch boundaries.

**Why this matters (real failure case)**:

2026-07-13 session: user said "对了，刚刚我在你任务中间
切换了个其他任务" (switch signal) during the workflow-rules
batch.  Agent merged the new task (orphan-reference cleanup)
into the existing batch instead of closing + starting new.
Result: workflow-rules batch ended up with no parent
verification of its own; the orphan-cleanup batch's parent
verification retroactively covered it.  This protocol
codifies the fix.