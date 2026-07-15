# Operating workflow rules (per user 2026-07-13)
Last P20-verified: 2026-07-13

|> L0: 9 operating rules (M-task-summary, M-must-read,
|> M-context-snapshot, M-subtask-summary, M-intent-parsing,
|> M-learn, M-add-then-reduce, **M-self-audit, M-self-
|> application**) for how agent should work, not what the
|> work is.  Load when ending a task, switching tasks (even
|> briefly), unsure which tools to use, processing messy
|> user input, at a decomposition integration point, before
|> declaring "all pass", or when encountering any new rule.
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
- Before declaring "all pass" (M-self-audit) — fresh-
  agent discoverability check.
- Encountering any new rule or pattern (M-self-application)
  — apply at 4 levels (task, rule itself, memory, self).

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

## The 9 rules

### M-task-summary

After every task completion, briefly state what went well
(and what could improve).  Decide whether the project's docs
should be updated based on what you learned; if yes, include
the doc fix in the same task (per P14 docs-stay-current).

**Child-summary destroy contract** (per user 2026-07-13):
when M-task-summary completes for a parent task that has
N child tasks, the summary commit MUST pull N child
summaries, write the parent summary, then destroy the
N child summaries (auditable via commit message body,
per P17).  Silent destroy = drift.

Full contract (3 steps, why explicit destroy, 奥卡姆
alignment, code-task variant, relationship to M-subtask-
summary + M-add-then-reduce) lives in
`docs/SUMMARY_LIFECYCLE.md` — load when implementing a
parent-level M-task-summary.

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
(snapshot format, restore mechanism) are in
`docs/TODO_SESSION_PERSISTENCE.md` (proposal — t8).

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

Full heuristic (5 signals in detail, anti-patterns,
what goes in a snapshot, location convention) lives in
`docs/SWITCH_SIGNALS.md` — load when evaluating whether
current context is a switch.  **Action when a signal
fires** (decision tree: same-topic refinement vs new
topic vs tiny insertion) lives in SWITCH_SIGNALS.md
"Switch action protocol" 段 — load that段 BEFORE
responding to the message.

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

When user input is messy (multiple asks, scattered,
contradicts itself), **first find the user's actual goal**
(the "main contradiction", per 主要矛盾), then plan
backward from the goal.  3 actions in order: extract goal →
identify main contradiction → plan backward.

Default to EXECUTE, not ask-again (per user 2026-07-10
'trust you / next / go').

Full text (3 actions detail, anti-pattern, trust-trigger
quote) lives in `docs/OPERATING_RULES_DETAIL.md` —
load when implementing M-intent-parsing on messy input.

### M-learn

After a decomposition **integration point** (all sub-tasks
of a parent task complete — RECURSIVE_DECOMPOSITION 5-step
loop step 5), ask: did this task surface something that
generalizes beyond itself?  If yes, capture it.

Trigger is dual-track: structural (always at INTEGRATE) +
signal (context overflow / 乱 / doc drift > 2 files).  3
sub-actions in order: 总结归纳 → 类比外推 → 更新知识库.

**Per 奥卡姆 (P7)** — silent no-op (don't write "checked,
nothing new"; every "checked" line is itself a P-n violation).

Full text (dual-track triggers in detail, 3 sub-actions
in detail, relationship to other M-* rules, anti-pattern)
lives in `docs/OPERATING_RULES_DETAIL.md` — load when
applying M-learn at an integration point.

### M-add-then-reduce

Tasks have a 2-phase lifecycle; the cycle repeats: Add
(gather / write / push) + Reduce (consolidate / dedupe /
destroy).  Full rule (trigger table, why signal-triggered,
add-then-reduce sequence, reduce phase actions, anti-patterns,
relationship to other M-* rules) lives in
`docs/ADD_THEN_REDUCE.md` — load when planning a multi-
leaf task or applying M-learn.

### M-self-audit

Frequently ask yourself: "If a new agent entered this
project right now, could it read what it needs to do the
task?"  Triggers: before declaring "all pass" (per M-task-
summary invariant), after adding new doc/section (is it
discoverable from L0?), or after adding 4th section to
AGENTS.md (am I bloating past 300-line cap?).

Full rule (when-to-apply, 6-step audit checklist
including step 6 "verify-before-edit" — see
`docs/M_SELF_AUDIT.md` for detail) lives in
`docs/M_SELF_AUDIT.md` — load before "all pass",
before any Edit/Write on a previously-read file
(per step 6), or after big doc changes.

### M-self-application

When you encounter a rule or pattern, apply it at 4 levels:
(1) to current task, (2) to the rule itself (meta), (3) to
memory / project structure (organizational), (4) to your
own operating behavior (self).  If you find a class of
cases where the rule applies but you didn't apply it,
that's a "self-application gap" — surface and fix.

Bootstrap exception: M-self-application does NOT apply to
itself (infinite recursion).  Per honest reporting (P17):
60-70% reduction realistic, not 100% (LLM training data may
lack self-referential examples).

### User-provided meta-rules → codify to doc (per user 2026-07-14)

When user provides a meta-rule (a rule about how agent
should work, often phrased as "if you don't X, you'll
Y"), agent MUST codify it to a doc — **not just
"remember" it implicitly**.

**Rationale**: per user "你不说我会忽略" — agent's
implicit memory is volatile; cross-session agents
won't have user's last-message context.  Only doc
codification persists.  Per M-self-application 4-level
level 4 (own operating behavior): user meta-rules
without codification = silent gap.

**Trigger** (any of these user phrases):

- "我觉得应该..." / "我做..." (a working principle)
- "下次..." / "从现在开始..." (forward-looking rule)
- "应该记住..." / "记到..." (explicit codification
  request)
- "X 时应该 Y" / "如果 Z 怎么办" (rule statement)

**Action**:

1. Read relevant existing rule (per "P-n / M-*
   modification discipline" 段 in PRINCIPLES.md).
2. Determine M-* vs P-n (per P-n vs M-* boundary
   in PRINCIPLES.md, codified in commit 5263030).
3. Draft the rule 段, including:
   - Trigger condition (when this fires)
   - Action (what to do)
   - Anti-patterns (what NOT to do)
   - Rationale (per P17 — why this rule)
4. Commit with detailed message: cite P-n / M-*,
   trace user message as source, acknowledge
   impact on future agents.

**Anti-patterns**:

- **"I'll remember this"** — implicit memory is not
  durable.  ALWAYS codify to doc.
- Codify without reading existing rules — risk
  duplication, contradiction, or breaking
  M-self-audit 6-step checks.
- Skip commit message P-n / M-* citation — others
  won't know which rule was modified.

**Self-application** (per M-self-application 4-level):

- Level 2 (rule itself): this rule itself is a
  user-provided meta-rule.  Apply recursively?  No —
  bootstrap exception (M-self-application does NOT
  apply to itself, by definition).
- Level 4 (own operating behavior): next time user
  gives a meta-rule, this 段 triggers the codification
  action.

Full rule (4 levels detail, examples of self-application
gaps caught in this project, bootstrap exception, caveat,
anti-patterns, relationship to other M-rules) lives in
`docs/M_SELF_APPLICATION.md` — load when encountering any
new rule or pattern, or when debugging "rule didn't apply".

### M-skill-synchronize (added 2026-07-15, per user meta-rule)

**Trigger**: when the user mentions a skill concept (whether
the existing `agent-reflection-skill/` or a future skill),
or when SUA's commits involve pattern-extraction to skill.

**Action** (4 sub-steps):

1. **Check SUA's skill-generation-knowledge**: does SUA
   already have a 段 about this skill topic?  Per
   information-topology 方案 C (c81), SUA 维护
   skill-generation-knowledge as flat content (in
   `docs/SKILL_GENERATION.md` or this 段).
2. **Decide sync direction**: SUA → skill (pattern
   extraction) or skill → SUA (pattern absorption)?
   Per sibling awareness protocol (HANDOFF_DETAIL.md
   61aab30).
3. **Mirror appropriately**: if SUA → skill, write a
   skill commit that captures the framework-agnostic
   pattern (without SUA-specific code).  If skill →
   SUA, document the lesson in SUA's HANDOFF_DETAIL.md
   "Sibling project awareness" 段.
4. **Verify skill self-preservation**: does the new
   content preserve the skill's portability, cross-ref
   to SUA, and not break existing 4 reasoning primitives
   (analogy / induction / reflection / abduction)?

**Anti-patterns**:

- Don't blindly mirror SUA-specific code into skill
  (breaks portability).
- Don't add new skill primitives without explicit
  user meta-rule (P7 奥卡姆).
- Don't break the lightweight sync protocol
  (HANDOFF_DETAIL.md 04a2935) — sync is "review at
  parent-verify", not "every commit".

**Why this M-rule exists**: per user meta-rule
2026-07-15: "当我提到跟 skill 有关的内容时, 你需要看
看 SUA 能不能学到对应知识, 并且在提炼到 skill 项目
的时候提供给对方这类知识, 避免破坏自己, 做好维护".
This rule is the operational form of that meta-rule.

**Cross-references**:
- `docs/SKILL_GENERATION.md` (committed next, c83) —
  SUA 维护的 skill-generation-knowledge
- `docs/M_SKILL_SYNCHRONIZE.md` — full text with
  case studies
- `../agent-reflection-skill/HANDOFF_DETAIL.md` 04a2935
  — skill side mirror
- `../agent-reflection-skill/docs/framework/analogy-and-induction.md`
  — the 4 (now 6) reasoning primitives that skill teaches

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