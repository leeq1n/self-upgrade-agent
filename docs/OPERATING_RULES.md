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
`hermes-snapshot-<topic>-<date>.md` (use
`tempfile.mkstemp(prefix="hermes-snapshot-",
dir=os.environ.get("TEMP", "/tmp"))` per OS-safe
tempfile path convention)
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
**See `M_SKILL_SYNCHRONIZE.md` (L2 companion per
P11 + R6) for decision tree + 4 sub-steps + 4 anti-
patterns + cross-project sync protocol.**

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
- `docs/SKILL_GENERATION.md` (deprecated 2026-07-15,
  per c87) — historical location of skill-generation-
  knowledge; canonical is now
  `../skill-incubator/SKILL_DESIGN.md`
- `docs/M_SKILL_SYNCHRONIZE.md` — full text with
  case studies, 4 sub-steps detail, worked examples
  (3 of them), and relationship to other M-rules
- `../skill-incubator/SKILL_DESIGN.md` — canonical
  design knowledge (per c88)
- `../skill-incubator/docs/process/when-to-incubate.md`
  — 4-condition checklist
- `../skill-incubator/docs/framework/case-studies.md`
  — first worked case
- `../agent-reflection-skill/HANDOFF_DETAIL.md` 04a2935
  — skill side mirror
- `../agent-reflection-skill/docs/framework/analogy-and-induction.md`
  — the 4 (now 6) reasoning primitives that skill teaches

### M-experiment-in-subproject (added 2026-07-15, per user meta-rule)

**Trigger**: when current project lacks experience to
handle a task, or when a sub-task becomes too complex
to handle in the main project.
**See `M_EXPERIMENT_IN_SUBPROJECT.md` + `_DETAIL`
(L2 companion per P11 + R6) for 4 sub-steps +
4 anti-patterns + prior art (Li 2022, Tsagkari 2020,
Sparrius 1980 via sciverse).**

**Action** (4 sub-steps):

1. **Decide**: evaluate whether the sub-task warrants
   a sub-project (per the 4 conditions in
   `docs/HANDOFF_DETAIL.md` "Sub-project-for-
   experimentation pattern" 段).
2. **Spawn**: create the sub-project as a sibling per
   P21 (separate git repo in `hermes-root/`, not a
   subdir of the main project).  Initialize with
   minimal skeleton (README + HANDOFF + 1 core doc).
3. **Set goal + return criterion**: explicitly write
   "I will return to the main project when [specific
   condition]" — this is the anti-trap.  Without a
   return criterion, the sub-project can become a
   permanent drift.
4. **Accumulate + return**: in the sub-project, follow
   the normal commit conventions (per P-n / M-n of
   the sub-project, OR a minimal version of SUA's P-n
   if sub-project is small).  When the return
   criterion is met, write a parent verification
   commit and resume the main project's queue.

**Anti-patterns**:

- **Don't** spawn a sub-project without a clear goal
  (per user meta-rule "可能陷进子任务，需要设定好
  目标").
- **Don't** spawn a sub-project as a subdir of the
  main project (per P21 cross-project independence,
  same as for sibling projects).
- **Don't** lose the connection to the main project
  (write a "Sub-project created" commit in the main
  project that references the sub-project's location
  and goal, per P14 docs stay current).
- **Don't** forget to return (the return criterion is
  the safety net; if no criterion, treat the sub-
  project as a permanent sibling per P21).

**Why this M-rule exists**: per user meta-rule
2026-07-15: "如果当前经验不足以支撑项目，可以考虑
新建一个子项目用来做实验积累失败经验" + "经验积累
完成，知道怎么处理后再切回主项目".  This M-rule
operationalizes that meta-rule into a 4-sub-step
process.

**Relationship to other M-rules**:

- M-self-audit: applies after sub-project cycle ends
  (verify the main project wasn't broken)
- M-task-summary: when returning, write a parent
  task summary that records the sub-project's findings
- M-add-then-reduce: sub-project findings should be
  *added* to the main project's docs, then *reduced*
  (per the skill-incubator's 信息拓扑 方案 C
  principle)
- P21 (cross-project): the sub-project is a sibling;
  P21 applies
- P22 (stuck→plan): this M-rule is one possible
  outcome of stuck→plan (when "plan" reveals
  insufficient experience, route to sub-project)
- P27 (project self-org): sub-project is a form of
  self-organization when the project recognizes its
  own experience limits

**Cross-references**:
- `docs/HANDOFF_DETAIL.md` "Sub-project-for-
  experimentation pattern" 段 — recording of the
  pattern (per c89-small)
- `docs/M_EXPERIMENT_IN_SUBPROJECT.md` (planned, c90)
  — L2 detail companion per P11
- `../skill-incubator/SKILL_DESIGN.md` — analogous
  pattern (skill-incubator itself is a sub-project
  for skill design, with 5-phase process)
- `../skill-incubator/docs/framework/case-studies.md`
  — first worked case (skill-incubator's first
  decision)

### M-terminology-clarity (added 2026-07-15, per user meta-rule)

**Trigger**: when a phrase / term / metaphor is used
in agent responses or user turns **without clear
operational definition**, AND the ambiguity may
cause confusion in later turns.
**See `M_TERMINOLOGY_CLARITY.md` + `_DETAIL` (L2
companion per P11 + R6) for 4 sub-steps + 3 anti-
patterns + worked examples ("撞到一起" → "replan";
"等下次 next trigger" → "我 [active plan]").**

**Action** (4 sub-steps):

1. **Detect**: notice when a phrase is repeated 3+
   times without a clear definition (P11 摘要+引用
   check: ≤ 120 chars, no jargon).
2. **Acknowledge**: explicitly say "this term is
   unclear; let me clarify" — not silently assume
   the user knows.
3. **Clarify or codify**: choose 1 of 3 paths:
   - (a) **Refine name**: pick a clearer term (e.g.,
     "撞到一起" → "plan-iterate on conflict" per
     P11)
   - (b) **Add definition段**: write 1 段 in
     PRINCIPLES.md or relevant doc
   - (c) **Update memory**: replace ambiguous term in
     memory entries
4. **Verify**: re-read after the change; ensure the
   new term is consistently used in future turns.

**Anti-patterns**:

- **Don't** silently use ambiguous terms (P17 honest:
  say "I'm using X to mean Y, but X is unclear; let
  me clarify").
- **Don't** over-codify: 1 occurrence doesn't warrant
  a M-n (M_RULE_AUTHORING 3-condition gate).
- **Don't** invent new terms without checking existing
  ones first (P7 奥卡姆: prefer existing terms).

**Why this M-rule exists**: per user meta-rule
2026-07-15: "如果'撞到一起'是你提的摘要/标题, 我认为
它没说清楚是什么意思, 你后续可能要处理一下这类问题".
The user is explicit: agent should self-detect
ambiguous terms and clarify them.  This M-rule
operationalizes that meta-rule.

**Example application**: the phrase "撞到一起" was
used 5+ times in 2026-07-15 turns without clear
definition.  Per this M-rule:
- Detect: 5+ occurrences
- Acknowledge: "撞到一起" 是 metaphor, not precise
  term
- Refine: replace with "plan-iterate on conflict" or
  simply "replan" (per P11 摘要+引用, ≤ 120 chars
  + clear English)
- Verify: future turns use "plan-iterate" consistently

**Relationship to other M-rules**:

- M-self-application: this M-rule is a self-application
  of M-self-application's 4-level check (L4 = agent's
  own operating behavior)
- P11 摘要+引用: P11 says "summary ≤ 120 chars, no
  jargon" — this M-rule operationalizes P11's
  terminology check
- P22 case-3: this is a meta-rule (about how the
  agent should behave in ambiguous situations)
- M_RULE_AUTHORING 3-condition gate: even meta-rules
  need 3+ observations OR bootstrap exception (this
  M-rule has bootstrap exception per user-explicit
  ask)

**Cross-references**:
- `docs/HANDOFF_DETAIL.md` — recording of related
  patterns
- `docs/OPERATING_RULES_DETAIL.md` (or new
  `M_TERMINOLOGY_CLARITY.md` companion per P11) —
  L2 detail
- User meta-rule 2026-07-15 — origin

### Autonomy boundary + phrasing revision (added 2026-07-15, per user meta-rules)

**Trigger**: when an agent is about to perform a
task, decide the risk level and corresponding
process.

**Action** (per risk level):

| Risk | Definition | Action |
|---|---|---|
| (a) **Low-risk** | 1-line change / doc typo / cross-ref update only | Autonomous, skip 7-check.  Still cite P-n/M-n in commit message (hook requires). |
| (b) **Mid-risk** | 1-2 files, 7-check needed | Run 7-check + P25 6-step.  No need to ask unless 真歧义. |
| (c) **High-risk** | 3+ files, vision-affecting, multi-commit batch | Always ask user first. |

**Anti-patterns**:

- **Don't** apply autonomy when 真歧义 exists
  (e.g., "撞到一起" 修订 — M-n 12 says clarify first).
- **Don't** skip 7-check for mid-risk tasks (per
  L4 weakness found in c90, 5b4900c).
- **Don't** end turn with passive "等下次 next
  trigger" (implies passive wait, 反 你 vision
  "agent 主动").

**修订 L4 boundary** (per c127 re-analysis +
你 turn 2026-07-15 explicit codification):

The 3 risk levels (a/b/c) are now consolidated
here as an explicit decision tree.  Per M-n 17
Path 1 + M-n 23 + M-n 24:

| Level | Trigger | Action | 7-check? | Ask user? |
|---|---|---|---|---|
| (a) Low | 1 line / typo / cross-ref | Autonomous | Skip | No |
| (b) Mid | 1-2 files / 7-check needed | Autonomous + 7-check | Yes | Only if 真歧义 |
| (c) High | 3+ files / vision-affecting | Ask user first | Yes | Yes |

**你 vision override** (per 你 turn 2026-07-15):

> "如果你通过了原则确认没问题，就直接进行，不用找我确认"
> "有计划的情况下，一直推进到遇到问题再来找我"
> "最近几轮不用这样打断项目推进节奏"

This means **(a) and (b) are autonomous** by
default.  (c) requires user confirmation only
when 真问题 (P17 honest "I can't proceed
because..."), not for trivial confirmations.

**M-n 24 (pace-continuity)** (per 你 turn
2026-07-15) reinforces: agent should commit +
continue per PLAN, not interrupt for trivial
reasons.

**Why this M-rule exists**: per 你 turn 2026-07-15:
 1. "当特别简单而且没有巨量的任务时你可以自行
    决定，不用经过check" (low-risk autonomy)
2. "我怀疑是hermes的skill让你每次跟我说'等下次
   next trigger'，你看看是否需要调整" (phrasing
   revision)

**Phrasing revision** (per P17 老实说 + M-n 12):
- "撞到一起" → "**replan on conflict**" (or just
  "**replan**") — per P11 摘要+引用 (≤ 120 chars,
  clear English) + P7 奥卡姆 (shorter)
- "等下次 next trigger" → "**我接下来 [active
  plan]**" (per P27 project self-org + 你 vision
  "agent 不依赖 hermes")

**Why both revisions**: the first ("撞到一起" → 
"replan") improves term clarity (M-n 12).  The
second ("等下次 next trigger" → "我接下来...")
removes passive-wait phrasing that 反 agent 主动
principle (P27 + 你 vision).

**Self-application of M-n 12 (per user feedback)**:
when user says "X is unclear", agent should:
1. Acknowledge (per P17)
2. Refine (Path (a)) or codify (Path (b))
3. Update memory
4. Verify (per P26)

**Cross-references**:
- `docs/M_TERMINOLOGY_CLARITY.md` — M-n 12 (Path (a)
  refine name process)
- memory entry 7 — 修订 L4 boundary + phrasing
  revision consolidated
- 你 turn 2026-07-15 — origin

### M-layer-extension (added 2026-07-15, per user meta-rule)

**Trigger**: when a project needs to add a new
information layer (e.g. L0.5, L2.5, L3) beyond the
fixed L0/L1/L2 structure.  **See
`M_LAYER_EXTENSION.md` (L2 companion per P11 + R6)
for worked examples + decision tree + naming
convention.**

**Action** (4 sub-steps):

1. **Detect**: notice when fixed L0/L1/L2 is
   insufficient (e.g., too long summary, or need
   intermediate layer for worked examples).
2. **Name the new layer**: pick a clear name (per
   M-n 12 terminology-clarity), e.g., L0.5 (between
   L0 summary and L1 detail), L2.5 (between L2
   detail and full examples), L3 (full examples).
3. **Codify the new layer**: add a 段 or doc for
   the new layer; reference from parent layer (per
   R6).
4. **Verify**: re-read after adding; ensure the new
   layer doesn't violate P11 摘要+引用 (≤ 120 chars
   for L0, ≤ 7KB for L1).

**Anti-patterns**:

- **Don't** add layers ad-hoc without naming (P11 +
  M-n 12).
- **Don't** add layers to fix unclear L0/L1/L2
  (refine existing first, per P7 奥卡姆).
- **Don't** add layers for every project (per M-n
  12, only when 3+ observed needs).

**Why this M-rule exists**: per 你 turn 2026-07-15
"我说过层级不一定只有固定层数，你需要看看项目会
在特定情况下主动扩展层数吗，管理是合理的吗？".

This M-rule operationalizes 你 turn: project CAN
add new layers in specific cases, but should manage
them (name + codify + verify).

**Observed cases** (per M_RULE_AUTHORING 3-condition
gate):

1. **L0.5 = Last P20-verified stamp** (per P20 段 in
   multiple docs).
2. **L2.5 = _DETAIL companion** (per R6).
3. **L3 = full worked examples** (per
   M_TERMINOLOGY_CLARITY_DETAIL.md 3 examples).
4. **"## Detail (L2)"段** in summary docs (per c93
   pattern).

**Relationship to other M-rules + P-n**:

- **P11 摘要+引用**: P11 fixed L0/L1/L2; this M-rule
  allows controlled extension (not violation).
- **P20 progressive disclosure**: P20 mandates L0/L1
  structure; this M-rule allows intermediate layers
  (L0.5, L2.5) when needed.
- **M-n 12 (terminology-clarity)**: this M-rule
  applies M-n 12 to layer names.
- **M_RULE_AUTHORING 3-condition gate**: this M-rule
  requires 3+ observed needs before adding new
  layer.
- **P7 奥卡姆**: don't add layers ad-hoc; refine
  existing first.

**Cross-references**:

- `docs/M_TERMINOLOGY_CLARITY.md` — M-n 12 (used
  for layer naming).
- `docs/P11.md` (if exists) — P11 摘要+引用 fixed
  L0/L1/L2.
- `docs/P20.md` (if exists) — P20 progressive
  disclosure.
- User meta-rule 2026-07-15 — origin.

### M-two-track-reasoning (added 2026-07-15, per 你 turn "类比推理 + 逻辑推理")

**Trigger**: when agent (or project) needs to reason
about a problem, structure, or pattern.  **See
`M_TWO_TRACK_REASONING_DETAIL.md` (L2 companion per
P11 + R6) for decision tree + worked examples +
how both tracks compose.**

**Action** (2 tracks):

**Track 1 — 类比推理 (analogical reasoning)**:
- Find structural similarity across domains
- Apply pattern from domain A to domain B
- Useful for: 5-family 类比 (c44), 信息拓扑 类比
  (c81), cross-project patterns (skill-incubator
  mirror), 案例库 类比
- Self-application: project applies P-n to similar
  projects, similar situations

**Track 2 — 逻辑推理 (logical reasoning)**:
- Sequential deduction from established facts
- 7-check + P25 6-step + 5-family verify
- Useful for: principle verification, code logic,
  test pyramid, failure → regression, gate checks
- Self-application: project verifies P-n internal
  consistency, M-rule boundary check

**When to use which** (per P7 奥卡姆):
- Use **类比** when problem is novel or cross-domain
- Use **逻辑** when problem is well-defined or needs
  verification
- Use **both** when problem is high-stakes (P25 6-step
  requires both: read first = 类比 + analysis = 逻辑)

**Entropy dimension** (per 你 turn 2026-07-15
"逻辑推理负责熵增发散，类比推理负责熵减归纳"):

- **类比推理** = **熵减归纳** (compression):
  compress possibilities to essence, reduce
  complexity.  Related to skill b502577 5th primitive
  "compression" + 4th primitive "abduction" (best
  explanation).
- **逻辑推理** = **熵增发散** (diverge):
  expand premises to conclusions, generate
  possibilities.  Related to skill b502577 2nd
  primitive "induction" + 6th primitive "recursion".

Both tracks operate on different entropy directions,
which is why both are needed for full reasoning.

**Classify 类比推理 as 抽象 + 归纳** (per 你 turn
2026-07-15 deep analysis):

- **类比推理 = 抽象能力**: extract common
  essence across domains (cross-domain abstraction).
- **类比推理 = 归纳能力**: induct N instances
  to 1 general rule.

**Why 类比 is project 自主 缩减 core (per 你 turn)**:
- Project context grows (P14 docs stay current +
  L2 companions + 24 P-n + 13 M-n).
- Without 类比: agent must read all docs (爆炸).
- With 类比: agent finds "M-n 17 similar to
  M-n 11 (both are 行为 rules)" → reuse M-n 11
  framework, avoid re-reading.
- **类比 = automatic "find prior similar pattern"
  → avoid duplicate context loading → project 自主
  缩减**.

**Classify 逻辑推理 as 演绎 + 发散** (per 你 turn
deep analysis):

- **逻辑推理 = 演绎能力**: general → specific
  (deduction).
- **逻辑推理 = 发散能力**: 1 rule → N cases
  (diverge).

**6-stage chain distribution** (per M-n 16 stage
3 top-down 分治 + 你 turn deep analysis):

| Stage | 类比 占比 | 逻辑 占比 | 说明 |
|---|---|---|---|
| 1. 观察 | 80% | 20% | find similar observations (类比) + verify (逻辑) |
| 2. 思考-1 (归纳) | 70% | 30% | 归纳 = 类比 + 逻辑 混合, 偏 类比 |
| 3. 执行-1 (规划) | 20% | 80% | top-down 分治 = 逻辑 sequential |
| 4. 思考-2 (怎么行动) | 70% | 30% | find similar past actions (类比) |
| 5. 执行-2 (调用记忆) | 30% | 70% | 顺序 apply memory entries (逻辑) |
| 6. 思考-3 + 执行-3 | 40% | 60% | 类比 verify + 逻辑 execute + verify |

**Conclusion**: 类比 在 阶段 1/2/4 重要 (观察,
归纳, 怎么行动), 逻辑 在 阶段 3/5/6 重要 (规划,
调用记忆, 修改代码).

**Topology dimension** (per 你 turn 2026-07-15
"类比是并行、图中任意两点串联的能力；逻辑推理是
串行、只在一条线上的单线程能力"):

- **类比推理 = 并行 + 图 (parallel + graph)**:
  - 并行 (parallel): process N cases / N domains
    同时, not sequentially.
  - 图中任意两点串联: any 2 nodes can be
    connected (类比), regardless of distance.
  - Like 知识图谱 (knowledge graph): nodes =
    domains, edges = 类比 relationships.
- **逻辑推理 = 串行 + 线 (serial + line)**:
  - 串行 (serial): 1 step at a time, in order.
  - 单线程 (single-thread): 1 path only, no
    branching.
  - Like 程序执行 (program execution): step 1 → step
    2 → step 3, no jumps.

**Implication for project**: 类比 thinking
allows agent to jump between domains freely
(graph traversal), while 逻辑 thinking forces
sequential reasoning (line traversal).  Both
needed: 类比 for cross-domain insight (避免 context
爆炸), 逻辑 for verification + gate checks.

**Anti-patterns**:

- **Don't** use only one track (both required for
  principled reasoning, per P25 6-step).
- **Don't** use 类比 when 逻辑 is sufficient
  (over-engineering).
- **Don't** use 逻辑 when 类比 is the right tool
  (cross-domain insight missed).

**Why this M-rule exists**: per 你 turn 2026-07-15
"我需要说明思考包括两种，类比推理和逻辑推理，请
你学习下这个观点，然后决定要不要做一些原则和
任务规划之类的调整".

This M-rule makes the 2 tracks explicit and
operational.  Project already uses both (c44 类比
framework, P25 6-step 逻辑); this M-rule codifies
both as a single framework.

**Relationship to other M-rules + P-n**:

- **P22 step 3 "find commonalities"** = 类比
  (per memory 5)
- **P25 6-step** = 逻辑 (per established practice)
- **P28 (recursion)** = both (apply 类比 + 逻辑
  to self)
- **M-n 12 (terminology-clarity)** = both (detect
  via 类比, refine via 逻辑)
- **M-n 13 (layer-extension)** = 类比 (find layer
  pattern across projects)
- **5-family 类比 framework (c44)** = 类比
  foundational

**Cross-references**:

- `docs/P22.md` (if exists) — P22 step 3 类比
- `docs/P25.md` (if exists) — P25 6-step 逻辑
- `docs/PRINCIPLES_FULL.md` "Recursion"段 — P28
  applies both
- User meta-rule 2026-07-15 — origin

### M-principle-reordering (added 2026-07-15, per 你 turn "原则混乱/修改原则后" 6-step)

**Trigger**: when agent notices that principles
have become disordered, or after modifying any
principle (P-n or M-n), or when project vision
drifts.  **See `M_PRINCIPLE_REORDERING_DETAIL.md`
(L2 companion per P11 + R6) for worked examples per
sub-step + relationship to P25 + self-application.**

**Action** (6 sub-steps, per 你 turn explicit
sequence):

1. **重读 (re-read)**: re-read all current P-n +
   M-n + R-n + memory entries.  Goal: ensure
   current state is fully internalized before
   proceeding.
2. **类比思考 (analogical thinking)**: find
   structural similarity between current chaos
   and previous patterns (per M-n 14 Track 1).
   Useful for: 5-family 类比 (c44), cross-project
   类比 (skill-incubator), prior similar disarrays.
3. **归纳总结 (inductive summary)**: extract
   pattern from observations.  Per M-n 14 Track 2
   (逻辑) + induction primitive (skill
   b502577).
4. **确认顺序 (confirm order)**: verify ordering
   of P-n (numerical), M-n (numerical), R-n
   (numerical), and within-doc段 (per 7-check
   step 3).
5. **整理 (reorganize)**: apply reorderings +
   renumberings + cross-ref updates.  Per P11 +
   R6 + P14.
6. **读一遍原则确认无误 (re-read principles to
   verify)**: re-read all P-n/M-n/R-n + memory
   once more, verify no further chaos, confirm
   order, then proceed.  This is the
   **principle-modification discipline** (per
   P25 6-step).

**Anti-patterns**:

- **Don't** skip 重读 (start with 类比 or 归纳
  without internalizing current state).
- **Don't** skip 确认顺序 (may miss numerical
  ordering issues, per 7-check step 3).
- **Don't** skip the final 读一遍原则确认无误
  (P25 step 7 post-modify check is critical).

**Why this M-rule exists**: per 你 turn 2026-07-15
"当你意识到原则混乱/修改过原则后需要重读、类比思
考、归纳总结、确认顺序、整理、最后读一遍原则确认
无误".

This M-rule operationalizes 你 6-step sequence as
a single M-rule.  Project has been doing this
informally (per c95, c96, c97, c98); this M-rule
makes it explicit.

**Relationship to other M-rules + P-n**:

- **P25 6-step**: this M-rule is P25 extended with
  explicit 类比 + 归纳 sub-steps
- **M-n 14 (two-track reasoning)**: sub-steps 2 +
  3 are 类比 + 归纳 (Track 1 + Track 2)
- **M-n 12 (terminology-clarity)**: step 5
  (整理) may rename unclear terms
- **M-n 13 (layer-extension)**: step 5 (整理)
  may add L0.5/L2.5/L3 if needed
- **7-check**: step 4 (确认顺序) maps to 7-check
  step 3 (ordering check)

**When to invoke**:

- After any P-n modification (per P25)
- After M-n codification (per M_RULE_AUTHORING)
- After parent verification (per SUMMARY_LIFECYCLE)
- When vision drift detected (per P26)
- When chaos / disorder observed in docs

**Cross-references**:

- `docs/PRINCIPLES.md` — P-n ordering check
- `docs/OPERATING_RULES.md` — M-n ordering check
- `docs/P25.md` (if exists) — P25 6-step (related
  but different: P25 is principle-modification
  discipline, this M-rule is post-chaos
  restoration)
- User meta-rule 2026-07-15 — origin

### M-observe-think-execute (added 2026-07-15, per 你 turn "观察-思考-执行链")

**Trigger**: when agent (or project) needs to
perform a task, and wants to use principled
meta-level structure.  **See
`M_OBSERVE_THINK_EXECUTE_DETAIL.md` (L2 companion
per P11 + R6) for worked examples per stage +
relationship to M-n 14 + self-application.**

**Action** (6-stage chain, per 你 turn explicit
sequence):

1. **观察 (observe)**: gather raw data, observe
   current state, identify changes.  Per M-n 14
   Track 1 (类比) — find similar observations.
2. **思考 (think 1)**: 归纳总结 + 判断是否进入
   规划.  Per M-n 14 Track 2 (逻辑) + induction
   primitive.
3. **执行 (execute 1)**: 实际规划.  Decide what
   to do, what memory is needed.  **Per 你 turn
   2026-07-15 top-down 分治 method**: 想清楚
   目标 → 倒推 需要做的 节点 → 自顶向下、分治
   拆解 → 做下去.  This applies to all planning
   steps, not just execute 1 (but execute 1 is
   where planning starts).
4. **思考 (think 2)**: 怎么行动, 需要什么记忆.
   Per M-n 14 Track 1 (类比) — find similar past
   actions.
5. **执行 (execute 2)**: 调用记忆.  Apply past
   patterns + memory entries.
6. **思考 (think 3) + 执行 (execute 3)**: 如何
   修改、运行代码 → 实际修改、运行代码.  Per M-n
   14 Track 2 (逻辑) + P25 6-step.

**本质 (essence)** (per 你 turn): 这条 链 本质
上 就是 "思考 包括 两种, 类比 推理 + 逻辑 推理":

- 观察 + 思考-1 + 思考-2 = 类比 推理 (Track 1)
- 思考-3 + 执行-1 + 执行-2 + 执行-3 = 逻辑 推理
  (Track 2)

**Higher-level position** (per 你 turn): this M-
rule is **higher-level** than M-n 14 (two-track
reasoning).  M-n 14 = the 2 tracks; M-n 16 = the
6-stage chain that uses both tracks.

**Relationship to other M-rules + P-n**:

- **M-n 14 (two-track-reasoning)**: this M-rule
  uses both tracks; M-n 14 is the foundation.
- **M-n 11 (sub-project)**: this M-rule applies
  within sub-project lifecycle (Decide → Spawn →
  Set goal → Return → Accumulate).
- **M-n 12 (terminology-clarity)**: this M-rule
  sub-step 1 (观察) may detect unclear terms.
- **M-n 13 (layer-extension)**: this M-rule sub-
  step 6 (修改、运行代码) may add L0.5/L2.5/L3.
- **M-n 15 (principle-reordering)**: this M-rule
  sub-step 4 (思考-2) may invoke M-n 15 when
  principles are in flux.
- **P22 step 3 "find commonalities"**: this M-rule
  sub-step 2 (思考-1) applies P22.
- **P25 6-step**: this M-rule sub-step 6 (思考-3 +
  执行-3) applies P25.

**Anti-patterns**:

- **Don't** skip 观察 (start with 思考 or 执行
  without data).
- **Don't** skip 思考 between 执行 stages (each
  执行 should be preceded by 思考).
- **Don't** conflate 思考 and 执行 (they are
  distinct stages per 你 turn).

**Cross-references**:

- `OPERATING_RULES.md` § M-n 14 (two-track
  reasoning) — foundation
- `OPERATING_RULES.md` § M-n 11 (sub-project) —
  related workflow
- `OPERATING_RULES.md` § M-n 15 (principle-
  reordering) — related workflow
- User meta-rule 2026-07-15 — origin

### M-context-freshness-check (added 2026-07-15, per 你 turn "经常修改的文件需要确认 + 新的领域需要搜索")

**Trigger**: when agent (or project) is about to
modify a doc that has been modified 3+ times
recently, OR when entering a domain that's new to
the agent.  **See `M_CONTEXT_FRESHNESS_CHECK_DETAIL.md`
(L2 companion per P11 + R6) for decision tree +
worked examples + how both paths compose.**

**Action** (2 paths, per 你 turn 类比 thinking):

**Path 1 — Intra-agent context check (经常修改的
文件)**:
- Re-read the doc before modifying
- Confirm agent has current context (印象)
- If 印象 不 清晰: re-read thoroughly
- Reason: avoid drifting from current content;
  avoid modifying based on stale context

**Path 2 — Inter-domain search (新的领域)**:
- Use MCP search tools (sciverse / llm_wiki /
  zotero / mineru / chrome_devtools) to read
  current state of the domain
- Search for prior art (academic papers,
  documentation, established practices)
- Reason: avoid reinventing; avoid 闭门造车;
  avoid repeating work (the 类比 between code and
  papers)

**Why both paths**: per 你 turn 2026-07-15
"经常修改的文件需要确认最后一次修改是否自己有印
象，确保自己的上下文是最新的；同样的，比较新的领
域也需要通过搜索工具读到最新的现状，才能避免闭门
造车，避免浪费时间重复造轮子（这指的不仅是代码，
也是论文等。这里需要你类比思考）".

The 2 paths are the same pattern: **context
freshness check**, applied at 2 different scopes
(intra-agent vs inter-domain).

**Anti-patterns**:

- **Don't** skip Path 1 (modifying doc without re-
  read leads to drift).
- **Don't** skip Path 2 (entering new domain without
  search leads to reinvention).
- **Don't** over-rely on Path 1 (memory may be
  stale; always verify).
- **Don't** over-rely on Path 2 (search results may
  be outdated; verify with multiple sources).

**Observed cases** (per M_RULE_AUTHORING 3-condition
gate, 5+ observed):

1. **c96 P28 lift**: modified PRINCIPLES.md +
   PRINCIPLES_FULL.md + AGENTS.md + hook (4 files),
   re-read M-n 12/13/14/15 + memory 7 first.
2. **c94 M-n 11 prior art**: entered "sub-project
   for experimentation" domain, used sciverse to
   search 3 papers (Li 2022 / Tsagkari 2020 /
   Sparrius 1980).
3. **c100 M-n 16 codify**: 你 turn "观察-思考-执行
   链" is implicit existing pattern, re-read M-n
   14 + memory to internalize.
4. **skill-incubator c88-c101**: multiple SKILL_DESIGN.md
   modifications, re-read prior content each time.
5. **c102-c105 L2 companion batch**: modified
   OPERATING_RULES.md 4 times for M-n 12/13/14/15/16
   L2, re-read OPERATING_RULES.md before each edit.

**Relationship to other M-rules + P-n**:

- **P14 docs stay current**: Path 1 enforces this.
- **M-n 14 (two-track reasoning)**: Path 2 uses
  Track 1 (类比 to search results) + Track 2
  (verify with multiple sources).
- **M-n 11 (sub-project)**: when entering new
  domain, may spawn sub-project (Path 2 → M-n 11).
- **M-n 15 (principle-reordering)**: Path 1
  complements M-n 15 sub-step 1 (重读).
- **M-n 16 (observe-think-execute)**: Path 1
  applies to stage 1 (观察); Path 2 applies to
  stage 2 (思考-1) when entering new domain.
- **P28 (recursion)**: this M-rule is recursive
  (apply to itself: re-read this M-rule when
  modifying).

**When to invoke**:

- Before modifying any doc that has been modified
  3+ times in last 10 commits (Path 1)
- Before entering any domain that hasn't been
  searched in last 20 commits (Path 2)
- When memory 印象 is unclear (Path 1)
- When user mentions a new term/concept (Path 2)

### M-recursive-summary-protocol (added 2026-07-15, per 你 turn "分治 + 递归 总结 + pollution control")

**Trigger**: when a task or sub-task completes
within a top-down 分治 plan (per M-n 16 stage 3).
**See `M_RECURSIVE_SUMMARY_PROTOCOL_DETAIL.md`
(L2 companion per P11 + R6) for decision tree +
worked examples + 节点 生命周期管理.**

**Action** (5 sub-steps, per 你 turn explicit
sequence):

1. **写子任务总结**: when sub-task completes,
   write summary (what was done, key insights,
   any issues).
2. **父任务看子任务总结**: parent task receives
   all its own sub-task summaries (not others'
   sub-tasks).
3. **父任务写父总结**: parent synthesizes child
   summaries → 1 parent summary (compress via
   类比 reasoning, per M-n 14).
4. **交给爷爷节点**: parent summary handed to
   grandparent node (not all child summaries).
5. **爷爷只看父**: grandparent sees only parent
   summary, not the 2nd/3rd-level summaries.

**Why this M-rule exists**: per 你 turn 2026-07-15
"总任务你应该是有记录的，每个拆解的子任务也有记
录（递归都有记录），子任务完成的时候写总结，父任
务看到所有自己子任务的总结后写父任务总结，然后交
给爷爷节点（爷爷节点只看到父节点，不然一堆二级三
级节点的总结会污染上下文）".

This M-rule operationalizes 你 分治 protocol:
递归 总结 + pollution control.  Without this
M-rule, context fills up with 2nd/3rd-level
summaries, polluting agent's working memory.

**Anti-patterns**:

- **Don't** skip sub-task summary (loses child
  insights).
- **Don't** forward all child summaries to
  grandparent (causes context pollution).
- **Don't** skip parent synthesis (grandparent
  needs 1 parent summary, not N child summaries).
- **Don't** include unrelated sub-tasks' summaries
  in parent summary (only own children).

**Observed cases** (per M_RULE_AUTHORING 3-condition
gate, 4+ observed):

1. **c60-c62 SUMMARY_LIFECYCLE 递归 destruction 协
   议**: SUA 之前 codify recursive destruction +
   parent summary. Same pattern (pollution
   control).
2. **skill-incubator 5-phase process (c88)**:
   Sense → Think → Extract → Organize → Design,
   with each phase producing summary. Same
   pattern (sub-task summary → parent).
3. **c107-c110 (我 之前 turns)**: did NOT follow
   this protocol (no sub-task summary per commit).
   Anti-example.
4. **你 turn 2026-07-15**: explicit codification
   request.

**Relationship to other M-rules + P-n**:

- **M-n 16 (observe-think-execute)**: stage 6
  (思考-3 + 执行-3) applies this M-rule after
  sub-task completion.
- **M-n 14 (two-track reasoning)**: parent synthesis
  uses 类比 (compress N child summaries → 1
  parent summary).
- **M-n 15 (principle-reordering)**: parent summary
  may trigger M-n 15 6-step if principles are
  disordered.
- **P11 摘要+引用**: this M-rule enforces P11
  via recursive summary.
- **P14 docs stay current**: parent summary
  ensures docs reflect all sub-task changes.
- **P28 (recursion)**: this M-rule IS recursion
  applied to summary protocol.

**When to invoke**:

- After any sub-task completes (write sub-task
  summary)
- After all sub-tasks of a parent complete (write
  parent summary, hand to grandparent)
- When working context has 3+ 2nd-level summaries
  (pollution alert, apply this M-rule)

**Cross-references**:

- `docs/SUMMARY_LIFECYCLE.md` — c62 recursive
  destruction 协议 (related)
- `docs/SKILL_GENERATION.md` /
  `../skill-incubator/SKILL_DESIGN.md` — 5-phase
  process (related sub-task pattern)
- `OPERATING_RULES.md` § M-n 16 — top-down 分治
  (parent)
- 你 turn 2026-07-15 — origin

### M-n 18 clarification: 节点 生命周期管理 (added 2026-07-15, per 你 turn "二级节点隔离 + 生命周期 + 销毁")

Per 你 turn 2026-07-15 clarification of M-n 18, the
node lifecycle has 3 additional details:

**1. 二级节点 隔离 (Sibling isolation)**:
- 二级节点 should NOT see other 二级兄弟节点's
  子节点 总结.
- Each 父 only sees its OWN 子's summaries (not
  other 父's children).
- This is what makes "父看自己子任务 总结" (sub-
  step 2 of M-n 18) explicit.

**2. 节点 状态 生命周期 (Node state lifecycle)**:
- **未完成 state**: node has 任务 摘要 (task
  description) + 子任务 说明 (sub-task descriptions).
- **完成 state**: node has 只留下 总结 (only
  summary remains; 任务 摘要 + 子任务 说明 are
  replaced by 总结).
- Transition: when sub-task 完成, write 总结;
  replace 任务 摘要 + 子任务 说明 with 总结.

**3. 销毁 子节点 (Destroy children after parent
synthesizes)**:
- After 父 reads 子 总结 (sub-step 2) + 父 writes
  父 总结 (sub-step 3) + 父 hands 父 总结 to 爷爷
  (sub-step 4):
- **Destroy 子 总结** (sub-step 5: 销毁) to avoid
  pollution.
- 爷爷 只看 父 总结 (sub-step 5: 爷爷只看父).

**Updated M-n 18 6 sub-steps (incorporating 你 turn
clarification)**:

1. 写子任务总结 (write sub-task summary when
   sub-task 完成)
2. 父看自己子任务总结 (parent sees OWN children's
   summaries only; sibling isolation)
3. 父写父总结 (parent synthesizes → 1 parent
   summary via 类比 compress)
4. 交父总结给爷爷节点 (hand parent summary to
   grandparent)
5. **销毁子节点** (destroy child summaries to
   avoid pollution)
6. 爷爷只看父总结 (grandparent sees only parent
   summary, not 2nd/3rd-level summaries)

**Why clarification matters**: per 你 turn "每个节
点未完成的时候是任务摘要和子任务说明，完成的时候
就只留下总结。在父节点读取子节点总结、写完父节点
总结之后应该将子节点销毁，避免污染上下文（这是节
点生命周期管理，这是agent行为规范的一部分）".

This M-rule is now part of agent behavior规范
(per 你 turn).  Project should self-learn +
consistently apply.

### M-file-naming-convention (added 2026-07-15, per 你 turn "recursive rule + multi-agent 维护")

**Trigger**: when agent creates a new file in
project (PLAN file, M-n L2 companion, etc.).
**See `M_FILE_NAMING_CONVENTION_DETAIL.md` for
decision tree, worked examples, and how to apply
across 3-project arch.**

**Action**: follow the 4 codified conventions:

1. **PLAN directory**: always `.hermes/plans/`
   (plural), NOT `.hermes/plan/` (singular).
2. **PLAN file naming**: `YYYY-MM-DD_HHMMSS-
   topic.md` (e.g., `2026-07-15_160000-replan.md`).
3. **M-n L2 companion**: `M_<NAME>_DETAIL.md`
   (no `_DETAIL` suffix in summary, `_DETAIL`
   suffix in companion).
4. **M-n summary segment in OPERATING_RULES.md**:
   `### M-<name> (added YYYY-MM-DD, per 你 turn ...)`.

**Why this M-rule exists**: per 你 turn 2026-07-15
"这是一个递归的规则（分治、自顶向下拆解），写的文
件路径、名字需要规范，不然新agent进来和老agent可能
维护两个任务，你需要在多agent协作的角度思考会不会
有问题".

This M-rule ensures:
- 新 agent knows where to find existing PLANS.
- 新 agent knows how to name new PLANS.
- 多 agent don't create dual maintenance (e.g.,
  one agent writes to `.hermes/plan/`, another to
  `.hermes/plans/`).
- M-n L2 companions are consistently named.

**Relationship to other M-rules + P-n**:

- **M-n 18 (recursive-summary-protocol)**: M-n 18
  produces files (PLAN, L2 companions); M-n 19
  codifies how those files are named + placed.
- **P21 (cross-project independence)**: M-n 19
  respects P21 (e.g., no commit to
  `../knowledge-graph-seed/` from SUA).
- **P11 摘要+引用**: M-n 19 enforces P11 via
  consistent file naming.
- **P28 (recursion)**: M-n 19 is recursive (apply
  to itself: new M-n files must follow M-n 19
  conventions).

**Observed cases** (per M_RULE_AUTHORING 3-condition
gate, 4+ observed):

1. **c115 (整理)**: detected inconsistency
   between `.hermes/plan/` (mine) and `.hermes/plans/`
   (existing).  Same pattern (multi-agent dual
   maintenance risk).
2. **c112 + c114**: PLAN file created without
   codified naming convention.  Anti-example.
3. **M-n 13-17 L2 companions (c102-c105, c113)**:
   all use `M_<NAME>_DETAIL.md` convention.
   Implicit pattern.
4. **你 turn 2026-07-15**: explicit codification
   request.

**When to invoke**:

- Before creating any new file in project.
- When 新 agent enters project (P26 fresh-agent
  discoverability check).
- When reviewing existing files for consistency
  (e.g., c115 整理).

**Anti-patterns**:

- **Don't** create files in `.hermes/plan/` (use
  `.hermes/plans/`).
- **Don't** name PLAN files without HHMMSS
  (multiple plans same day would conflict).
- **Don't** name M-n L2 companions inconsistently
  (always `_DETAIL.md` suffix).
- **Don't** skip cross-references between summary
  and companion (per R6).

**Cross-references**:

- `.hermes/plans/` — all PLAN files (per M-n 19)
- `docs/M_*_DETAIL.md` — all M-n L2 companions
  (per M-n 19)
- `OPERATING_RULES.md` § M-n 18 — recursive
  summary protocol (uses M-n 19 conventions)
- 你 turn 2026-07-15 — origin

### M-agent-discoverability-check (added 2026-07-15, per 你 turn "新 agent 读 + framework-agnostic + 持久化")

**Trigger**: when agent modifies any of the
following:
- **agent 原则**: P-n or M-n in SUA
- **skill 原则**: skill-generation-knowledge
  (per M-n 18 + c83 SKILL_GENERATION.md /
  skill-incubator/SKILL_DESIGN.md)
- **skill 内容**: skill files (in agent-reflection-
  skill or future incubated skills)
**See `M_AGENT_DISCOVERABILITY_CHECK_DETAIL.md`
for decision tree, worked examples, and how to
apply across 3-project arch.**

**Action** (4 sub-steps, per 你 turn 2026-07-15):

1. **Cross-framework check**:
   - 改动 是 framework-agnostic?
   - 不 only Hermes-specific?
   - 未来 agent (Codex / Claude Code / others)
     能 用?
   - If 不是: 修订 to be framework-agnostic
     (or explicitly mark as Hermes-only).

2. **Naming check** (per M-n 19):
   - 改动 涉及 的 路径/名字 framework-agnostic?
   - Avoid Hermes-specific terms in names
     (e.g., not "hermes-onboarding" but
     "agent-onboarding").
   - Per M-n 19: `.hermes/` is OK (it's the
     directory, not the file name); but file
     names should be framework-agnostic.

3. **Discoverability check** (per P26 fresh-agent
   simulation):
   - Simulate 新 agent entering project
   - Check if 新 agent can read what it needs
   - 4 questions:
     a. 新 agent 知道 原则 改了 吗? (commit
        message + cross-refs)
     b. 新 agent 知道 哪里 改的 吗? (file path
        + commit hash)
     c. 新 agent 知道 为什么 改 吗? (rationale
        + 你 turn origin)
     d. 新 agent 知道 怎么 follow 吗? (action
        steps + anti-patterns)

4. **Memory persistence** (per 你 turn "这条需要记"):
   - Persist this M-rule to memory
   - Per M-n 19: memory entry should be
     framework-agnostic (avoid Hermes-specific
     terms)
   - Future agents should load this memory
     entry on entry (P26 fresh-agent check)

**Why this M-rule exists**: per 你 turn 2026-07-15
"这条需要记，不然改几轮以后可能会发现，以后新agent
进来不知道很多东西、行为非预期".

This M-rule prevents:
- 新 agent 不知道 原则 改动
- 新 agent 行为 非预期
- 改 几轮 后 知识 丢失 (vs. memory persistence)

**Relationship to other M-rules + P-n**:

- **M-n 19 (file-naming-convention)**: M-n 20 sub-
  step 2 (naming check) uses M-n 19 conventions.
- **M-n 18 (recursive-summary-protocol)**: M-n 20
  sub-step 4 (memory persistence) uses M-n 18
  protocol.
- **P11 摘要+引用**: M-n 20 sub-step 3
  (discoverability) enforces P11.
- **P14 docs stay current**: M-n 20 ensures
  changes are discoverable.
- **P26 fresh-agent discoverability check**: M-n 20
  sub-step 3 IS P26 applied to principle changes.
- **P28 (recursion)**: M-n 20 is recursive
  (apply to itself: changes to M-n 20 also require
  M-n 20 check).

**Observed cases** (per M_RULE_AUTHORING 3-condition
gate, 4+ observed):

1. **c53 + c82 + c83 (3-project arch)**: SUA +
   skill-incubator + agent-reflection-skill split.
   agent-reflection-skill is framework-agnostic
   (Hermes/Codex/Claude Code).  Same pattern
   (cross-framework + discoverability).
2. **c92 (M-n 12)**: terminology-clarity + framing
   revision.  No framework-specific check at
   time.  Anti-example.
3. **c115 (M-n 19)**: file naming convention.  M-n
   19 mentions 新 agent but doesn't fully address
   framework-agnostic.
4. **你 turn 2026-07-15**: explicit codification
   request.

**When to invoke**:

- After any P-n modification (per P25 6-step
  includes M-n 20 implicit; now explicit).
- After any M-n codification (per M_RULE_AUTHORING).
- After any skill principle change (per M-skill-
  synchronize).
- After any skill content change.
- Before declaring "all pass" (per P26 + M-self-
  audit + M-n 20).

**Anti-patterns**:

- **Don't** assume changes are framework-agnostic
  without checking.
- **Don't** use Hermes-specific names in new
  files (e.g., "hermes-skill", "hermes-onboarding"
  vs. "agent-skill", "agent-onboarding").
- **Don't** skip memory persistence (per 你 turn
  "这条需要记").
- **Don't** skip P26 fresh-agent simulation after
  principle changes.
- **Don't** assume 新 agent has same context as
  current agent (per P26).

**Cross-references**:

- `OPERATING_RULES.md` § M-n 19 — file naming
  convention
- `docs/PRINCIPLES.md` — P-n list (24 P-n)
- `docs/AGENTS.md` — agent entry point (per P26)
- `OPERATING_RULES_DETAIL.md` (or
  `M_AGENT_DISCOVERABILITY_CHECK_DETAIL.md` future
  L2 companion)
- 你 turn 2026-07-15 — origin

### M-ask-or-infer-mark-guess (added 2026-07-15, per 你 turn "不仅要做什么, 还 为什么 + 问/推理/标注猜测 + top-down 默认")

**Trigger**: when agent is about to commit,
modify, or make any decision, AND agent is
uncertain about:
- What to do (what action)
- Why to do it (rationale)
- Whether to proceed (decision)
**See `M_ASK_OR_INFER_MARK_GUESS_DETAIL.md` for
decision tree, worked examples, and how to apply
across 3-project arch.**

**Action** (3 sub-steps, per 你 turn explicit
sequence):

1. **问 (ask)**:
   - First, ask user via clarify tool or
     direct question.
   - Be specific: list 2-4 options + 你 turn
     origin context.
   - Don't ask trivially (only 真歧义).

2. **推理 (infer)**:
   - If user does not respond OR response
     insufficient:
     - Apply 类比 reasoning (per M-n 14
       Track 1): find prior similar pattern
     - Apply 逻辑 reasoning (per M-n 14
       Track 2): verify with P-n + M-n
     - Self-reason the best action

3. **标注 猜测 (mark guess)**:
   - Mark the action as "**猜测**" or
     "**inferred, unverified**"
   - Cite the inference path (which P-n /
     M-n / memory entry was used)
   - Per P17 老实说: never claim green when
     yellow
   - If user later corrects: update memory

**Why this M-rule exists**: per 你 turn 2026-07-15
"不仅要考虑我在做什么，还需要考虑为什么我要这么
做，如果不确定就问，问了不回答就推理下，然后标注
为猜测".

This M-rule prevents:
- Agent 盲跟随 (just doing what user says
  without understanding why)
- Agent over-asking (ask when infer is possible)
- Agent 隐瞒 猜测 (claiming certainty when
  uncertain)

**Top-down 默认 (per 你 turn "要自顶向下分析问题")**:

Apply M-n 16 stage 3 (top-down 分治) **always**,
not just for explicit plans:
- 任何 commit / 改动 前:
  - clarify 目标 (what + why)
  - 倒推 节点 (reverse-engineer nodes)
  - 分治 拆解 (decompose)
  - 做下去 (execute)
- Per M-n 18: 写 sub-task summary

**Relationship to other M-rules + P-n**:

- **M-n 14 (two-track reasoning)**: sub-step 2
  (infer) uses both 类比 + 逻辑 tracks.
- **M-n 16 (observe-think-execute)**: top-down
  默认 applies M-n 16 stage 3 always.
- **M-n 18 (recursive-summary-protocol)**: sub-
  task summary protocol.
- **M-n 20 (agent-discoverability-check)**: M-n
  21 段 is discoverable (新 agent can read it).
- **P17 老实说**: sub-step 3 (mark guess)
  enforces P17.
- **P22 case-3 boundary**: M-n 21 is case 2
  (behavioral), not P-n.
- **P26 fresh-agent discoverability**: M-n 21
  applied to P26 simulation (新 agent should
  see M-n 21段).
- **P28 (recursion)**: M-n 21 is recursive
  (apply to itself: when modifying M-n 21,
  apply M-n 21 3 sub-steps).

**Observed cases** (per M_RULE_AUTHORING 3-condition
gate, 4+ observed):

1. **c86-r87 (clarify tool)**: 2 uses.  Pattern
   was just ask; not follow-up infer + mark
   guess.  Anti-example (now codified as M-n
   21 3 sub-steps).
2. **c106-c117 (recent turns)**: I did not
   always apply top-down 分治.  Some commits
   focused on "what" without "why".  Anti-
   example.
3. **c110 (M-n 14 topology)**: 我 didn't pre-
   analyze "为什么 你 turn 这条 insight 重要".
   Anti-example.
4. **你 turn 2026-07-15**: explicit codification
   request.

**When to invoke**:

- Before any commit (clarify why, not just what).
- Before any modification (clarify goal +
  reverse-engineer nodes).
- Before any decision (ask, then infer if no
  answer, then mark guess).
- Always apply top-down 分治 (M-n 16 stage 3
  + M-n 18 summary).

**Anti-patterns**:

- **Don't** ask without follow-up reasoning
  (sub-step 2).
- **Don't** infer without marking guess
  (sub-step 3).
- **Don't** skip top-down 分治 (per 你 turn
  "要自顶向下分析问题").
- **Don't** focus only on "what" without "why".
- **Don't** claim certainty when uncertain
  (per P17).

**Cross-references**:

- `OPERATING_RULES.md` § M-n 14 — two-track
  reasoning (used in sub-step 2)
- `OPERATING_RULES.md` § M-n 16 — top-down 分治
  (used in top-down 默认)
- `OPERATING_RULES.md` § M-n 18 — sub-task
  summary
- `OPERATING_RULES.md` § M-n 20 — agent
  discoverability
- `docs/PRINCIPLES.md` — P17 (老实说)
- 你 turn 2026-07-15 — origin

### M-3w1h-think-first (added 2026-07-15, per 你 turn "自顶向下之前, 往上思考一步, 3W1H 分析法")

**Trigger**: before any major decision, commit
batch, or analysis task.
**See `M_3W1H_THINK_FIRST_DETAIL.md` for decision
tree, worked examples, and how to apply across
3-project arch.**

**Action**: apply **3W1H 分析法** BEFORE
top-down 分治 (per M-n 16 stage 3):

| 3W1H | Question | 中文 |
|---|---|---|
| **What** | What is the problem / task? | 什么 |
| **Why** | Why is this important / rationale? | 为什么 |
| **Who** | Who is involved / affected? | 谁 |
| **How** | How to approach / execute? | 怎么 |

**3W1H → top-down 分治 sequence**:

1. **3W1H 分析** (NEW, per 你 turn "往上思考一步"):
   - What: clarify the problem
   - Why: clarify rationale (per M-n 21 强调 "不仅
     做什么, 还 为什么")
   - Who: clarify stakeholders
   - How: high-level approach
2. **top-down 分治** (per M-n 16 stage 3):
   - 目标 (per 3W1H What)
   - 倒推 节点 (per 3W1H How)
   - 分治 拆解 (per 3W1H How)
   - 做下去 (per 3W1H How)
3. **execute + sub-task summary** (per M-n 18)

**Why this M-rule exists**: per 你 turn 2026-07-15
"自顶向下想问题之前，也需要往上思考一步，3W1H分析
法".

This M-rule prevents:
- 直接 top-down 没 抽象 思考 (per 你 turn
  criticism)
- 漏掉 关键 维度 (What / Why / Who)
- 思考 顺序 错 (先 抽象, 再 具体, 不 直接 具体)

**When to invoke**:

- Before any major commit batch
- Before any 修订 L4 boundary decision
- Before applying M-n 16 stage 3
- Before declaring "all pass" (per P26 + M-self-
  audit + M-n 22)
- When 你 turn 涉及 multi-step decision

**Anti-patterns**:

- **Don't** skip 3W1H (go directly to top-down).
- **Don't** answer 3W1H trivially (e.g., What =
  "stuff" without specifics).
- **Don't** confuse 3W1H (abstract) with
  top-down (concrete): 3W1H is "above" (per
  你 turn), top-down is "below".

**Observed cases** (per M_RULE_AUTHORING 3-condition
gate, 4+ observed):

1. **c118 (M-n 21)**: 我 did not apply 3W1H first;
   went directly to M-n 21 codify.  Anti-example.
2. **c110 (M-n 14 topology)**: 我 did not ask "Why
   is this insight important" (3W1H Why).
   Anti-example.
3. **c119 (PROJECT_STATE reframe)**: 我 went
   directly to 类比 c117; didn't apply 3W1H
   Who (new agents affected).  Anti-example.
4. **你 turn 2026-07-15**: explicit codification
   request.

**Cross-references**:

- `OPERATING_RULES.md` § M-n 16 — top-down 分治
  (used in step 2)
- `OPERATING_RULES.md` § M-n 21 — ask-or-infer-
  mark-guess (3W1H Why relates)
- `docs/PRINCIPLES.md` — P17 (老实说, for 3W1H
  answers)
- 你 turn 2026-07-15 — origin



### M-periodic-re-analysis (added 2026-07-15, per 你 turn "如果做了很久, 重新在最终目标的角度上做分析")

**Trigger**: when agent has been working a long
time (per M-n 17 Path 1: 10+ commits OR 1+ hour
of work), OR when user explicitly asks for re-
analysis.
**See `M_PERIODIC_RE_ANALYSIS_DETAIL.md` for
decision tree, worked examples, and how to apply
across 3-project arch.**

**Action** (3 sub-steps, per 你 turn "自顶向下看
看有没有需要变动"):

1. **Re-analyze at 最终目标 level** (per M-n 22
   3W1H first):
   - What: What is the 最终目标? (per
     PROJECT_STATE.md + 3-project arch)
   - Why: Why is this important? (per P22 case-3
     boundary)
   - Who: Who is affected? (per M-n 20 framework-
     agnostic)
   - How: How to achieve? (per top-down 分治)

2. **Compare to 当前 state** (per M-n 17 Path 1):
   - List 实际 完成 state
   - Compare to 最终目标
   - Identify gaps (R-n violations, missing L2
     companions, stale entry files, etc.)

3. **Plan for re-analysis-driven changes**:
   - Per P7 奥卡姆: 哪些 changes 真正 需要?
   - Per M-n 16 stage 3 top-down: 优先级
   - Apply M-n 18 节点 生命周期管理 to
     sub-task summary

**Why this M-rule exists**: per 你 turn 2026-07-15
"如果做了很久，你可以考虑重新在最终目标的角度上
做分析。自顶向下看看有没有需要变动".

This M-rule prevents:
- Long sessions drift away from 最终目标
- Continue mechanical queue mode without
  questioning
- Missing critical gaps (R-n violations, etc.)
- Over-修订 L4 boundary without end vision

**Observed cases** (per M_RULE_AUTHORING 3-condition
gate, 4+ observed):

1. **c110 (你 turn "现在陷进任务很久了")**: 你
   raise concern about 做了很久.  Pattern:
   re-analysis needed.
2. **c115 (整理)**: 你 raise concern about 乱.
   Pattern: 整理 process.
3. **c116 (M-n 20 framework-agnostic)**: 你 raise
   concern about 新 agent.  Pattern: re-分析 at
   multi-agent level.
4. **你 turn 2026-07-15**: explicit codification
   request.

**When to invoke**:

- After 10+ commits in single session
- After 1+ hour of work without re-analysis
- When user explicitly asks (e.g., "重新分析")
- Before declaring "all pass" (per P26)
- After major M-rule changes (c97-c100, c106, c111,
  c115-c122)

**Anti-patterns**:

- **Don't** continue mechanical queue mode without
  re-analysis (per memory 9 trap symptom).
- **Don't** skip 3W1H first (per M-n 22).
- **Don't** miss critical gaps (R-n violations,
  L2 companions, stale entry files).
- **Don't** 修订 L4 boundary without end vision
  check.

**Cross-references**:

- `OPERATING_RULES.md` § M-n 22 — 3W1H 分析法
  (used in sub-step 1)
- `OPERATING_RULES.md` § M-n 17 — context-
  freshness-check (used in sub-step 2)
- `OPERATING_RULES.md` § M-n 16 — top-down 分治
  (used in sub-step 3)
- `OPERATING_RULES.md` § M-n 18 — recursive
  summary (used in sub-step 3)
- `docs/PROJECT_STATE.md` — 最终目标 reference
- 你 turn 2026-07-15 — origin



### M-pace-continuity (added 2026-07-15, per 你 turn "有计划的情况下，一直推进到遇到问题再来找我 ... 最近几轮不用这样打断项目推进节奏")

**Trigger**: when agent has plan (per M-n 16 top-
down + M-n 18 节点 生命周期管理) AND no 真问题
(P17 honest blockers).
**See `M_PACE_CONTINUITY_DETAIL.md` (L2 companion
per P11 + R6) for decision tree + worked examples
+ 5 anti-patterns.**

**Action** (3 sub-steps, per 你 vision 2026-07-15):

1. **Commit + continue** (no verbose ending):
   - After commit, **directly continue next
     commit** (per M-n 16 stage 3 + M-n 18 sub-
     task summary).
   - Don't add verbose "end this turn"段 or
     "active next plan"段.
   - Response should be: commit acknowledgment
     + 简短 status, NOT 重复 commit content.

2. **Only interrupt for 真问题** (P17 honest):
   - 真问题 = "I can't proceed because..." (per
     P17 老实说)
   - Not interrupt for: confirmation requests,
     verification, or trivial questions.
   - Per M-n 21: only ask when 真歧义 (not
     trivially).

3. **Per 你 vision "主动 + 不打扰"**:
   - Default mode: 主动 continue per PLAN.
   - Exception: 真问题 (per P17).
   - Per M-n 12: phrasing revision ("等下次
     next trigger" → "我 [active plan]"; "撞到
     一起" → "replan").

**Why this M-rule exists**: per 你 turn 2026-07-15
"有计划的情况下，一直推进到遇到问题再来找我 ...
最近几轮不用这样打断项目推进节奏".

This M-rule prevents:
- Agent 打断 项目 推进 节奏 (verbose "end this
  turn"段)
- Agent over-asking (already covered by M-n 21,
  but reinforced here)
- Agent "等我 next 决定" (passive wait, already
  covered by M-n 12)

**Observed cases** (per M_RULE_AUTHORING 3-condition
gate, 4+ observed):

1. **c106-c133 (最近 28 commits)**: 我 每次
   都 verbose "end this turn" + "active next
   plan" 段.  你 turn 第 2 部分 是 对 这 28
   commits 的 feedback.  Anti-example.
2. **c95 (L4 boundary 你 override)**: 你 vision
   = "不用找我确认" — 主动 continue.  Pattern:
   not interrupt.
3. **c100 ("只要你处理好了，就继续推进")**:
   你 vision = continue, don't wait.  Pattern:
   not interrupt.
4. **你 turn 2026-07-15**: explicit codification
   request.

**When to invoke**:

- Default: 任何 commit 后 (always apply).
- Exception: 真问题 (per P17 + M-n 21 sub-step 1).
- After M-n 18 sub-task summary: don't add
  verbose ending段.

**Anti-patterns**:

- **Don't** add "end this turn"段 after commit.
- **Don't** add "active next plan"段 after
  commit (plan is in PLAN file + commit body).
- **Don't** ask user for trivial confirmation
  (per M-n 21: 真歧义 only).
- **Don't** say "等下次 next trigger" (per M-n
  12).
- **Don't** "撞到一起" without replanning (per
  M-n 12).

**Cross-references**:

- `OPERATING_RULES.md` § M-n 12 — terminology-
  clarity (phrasing revision)
- `OPERATING_RULES.md` § M-n 16 — top-down 分治
  (used in sub-step 1)
- `OPERATING_RULES.md` § M-n 18 — recursive
  summary (used in sub-step 1)
- `OPERATING_RULES.md` § M-n 21 — ask-or-infer-
  mark-guess (used in sub-step 2)
- `OPERATING_RULES.md` § M-n 23 — periodic re-
  analysis (used to verify plan still valid)
- 你 turn 2026-07-15 — origin


### M-turn-pattern-recognition (added 2026-07-15, per 你 turn "学习下我发言的思路 ... 也需要看看有没有学习过")

**Trigger**: when agent receives a user turn
that contains 2+ parts (directive + 真问题
+ 真意 + 隐含 codify request).

**See `M_TURN_PATTERN_RECOGNITION_DETAIL.md`
(L2 companion per P11 + R6) for worked
examples + 4 sub-steps + 5 anti-patterns +
per-turn-type decision tree.**

**Action** (4 sub-steps per M-self-application
4 levels + M-n 14 类比 vs 逻辑):

1. **Parse turn** (object level): identify
   all parts (directive / 真问题 / 真意 /
   隐含 codify / 隐含 verification).
2. **Apply pattern** (rule level): recognize
   你 turn patterns (常见 pattern 见
   decision tree in L2 companion).
3. **Update memory** (memory level): if
   new pattern observed, add to
   7+ observed cases list.
4. **Adjust behavior** (self level): for
   next turn, recognize pattern faster +
   apply correct M-rule (M-n 21/22/23/24).

**5 observed 你 turn patterns** (per M_RULE_
AUTHORING 3-condition gate):

- **Pattern A (2-3 parts + directive)**: per
  c92, c98, c106 prior turns.
- **Pattern B (3-4 parts + 真问题)**: per
  c118, c122 prior turns.
- **Pattern C (5 parts + 真问题 + 隐含
  codify)**: per 你 turn 2026-07-15 (你
  turn 真意 = 5 distinct parts: 规划
  角度 / 方法 / 任务管理 / 记录 / 学习
  思路).
- **Pattern D (directive + 真问题 verify)**:
  per c145, c155 prior turns.
- **Pattern E (implicit + 主动)**: per
  c163-c182 prior turns (你 turn "按
  计划继续推进" = 主动 mode).

**Why this M-rule exists**: per 你 turn
2026-07-15 explicit ask "学习我发言
思路这个也需要看看有没有学习过" +
M_RULE_AUTHORING 3-condition gate (3+
sites: c18 + c92 + c98 + c106 + c118 +
c122 = 6 sites; triggerable: 你 turn
parser; 5+ observed: 5 patterns above).

**Self-application of M-self-application
(per P28 recursion)**: this M-rule IS
M-self-application applied to 你 turn
recognition (level 4: own behavior).

**Cross-references**:

- `docs/OPERATING_RULES.md` § M-self-
  application — 4 levels (this M-rule IS
  level 4 application)
- `docs/OPERATING_RULES.md` § M-n 12
  terminology-clarity — refine 你 turn
  terms
- `docs/OPERATING_RULES.md` § M-n 14
  two-track-reasoning — 类比 (find
  similar 你 turn) vs 逻辑 (parse 1
  turn)
- `docs/OPERATING_RULES.md` § M-n 21
  ask-or-infer-mark-guess — for 真问题
- `docs/OPERATING_RULES.md` § M-n 22
  3W1H-think-first — for 你 turn 真意
- 你 turn 2026-07-15 — origin

### M-context-decay-management (added 2026-07-15, per 你 turn "项目上下文可能变长 + agent 记忆遗忘")

**Trigger**: when agent has many commits OR
long context OR forgets prior M-rule / P-n.

**See `M_CONTEXT_DECAY_MANAGEMENT_DETAIL.md`
(L2 companion per P11 + R6) for compression
strategy + working memory + episodic memory +
类比 retrieval + 4 sub-steps + 5 anti-patterns.**

**Action** (4 sub-steps per M-n 14 类比
+ M-n 18 节点 生命周期 + 你 turn prior 5
directives):

1. **Detection**: identify when context is
   long (commits threshold 10+ OR time 1+
   hour) OR agent forgets prior rule.
2. **Classification**: classify decay
   pattern (5-types: working memory short /
   working memory overflow / episodic
   retrieval fail / 类比 inaccessible /
   L0 rule dropped).
3. **Compression**: per P29 主动 reduce
   context — destroy redundant summaries
   (per M-n 18 destruction contract) +
   compress to essence (per M-n 14
   compression primitive).
4. **Refresh**: load from MEMORY.md (per
   M-self-application level 3) + 类比
   retrieval (per M-n 17 Path 2 inter-
   domain MCP search).

**Why this M-rule exists**: per 你 turn
2026-07-15 explicit True问题 "记忆遗忘
的问题" + M_RULE_AUTHORING 3-condition
gate (6+ sites: c107 熵减 + c127
periodic re-analysis + c134 pace-
continuity + c183 turn-pattern + c165-c167
P29 reduce context + 你 turn explicit).

**5 decay patterns** (per 你 turn 5-part
pattern):

- **Pattern 1 (working memory short)**:
  agent forgets prior turn within session.
  → Apply M-n 25 Pattern E + M-n 21.
- **Pattern 2 (working memory overflow)**:
  agent has too many in-context items.
  → Apply M-n 18 destruction + P29.
- **Pattern 3 (episodic retrieval fail)**:
  agent can't recall past session via
  session_search.
  → Apply M-n 17 Path 2 (inter-domain MCP
  search).
- **Pattern 4 (类比 inaccessible)**: agent
  doesn't find similar prior pattern.
  → Apply M-n 14 类比 compression.
- **Pattern 5 (L0 rule dropped)**: agent
  forgets a P-n / M-n rule.
  → Apply M-self-application level 3 +
  MEMORY.md reload.

**Cross-references**:

- `docs/OPERATING_RULES.md` § M-n 14
  two-track-reasoning (类比)
- `docs/OPERATING_RULES.md` § M-n 17
  context-freshness-check (Path 2)
- `docs/OPERATING_RULES.md` § M-n 18
  recursive-summary-protocol (destruction)
- `docs/PRINCIPLES_FULL.md` "P29"段 (主动
  reduce context)
- 你 turn 2026-07-15 — origin



.

### M-knowledge-layer-architecture (added 2026-07-15, per 你 turn "3层知识结构 + 3 source 关系 + 单 skill scenario")

**Trigger**: when designing skill structure
OR auditing skill against new-agent perspective
OR integrating 3 sources (hermes + SUA +
skill) in single-skill scenario.

**See `M_KNOWLEDGE_LAYER_ARCHITECTURE_DETAIL.md`
(L2 companion per P11 + R6) for 3-layer
definition + 3 sources mapping + lifecycle +
跨项目 memory + 10 联想 问题.**

**Action** (3-layer architecture + 3 sources):

1. **3-layer knowledge structure**:
   - **核心层 (core layer)**: agent 自指
     behavior rules (M-n 12, M-n 14, M-n 18,
     M-n 21, M-n 22, M-n 25, M-n 26, M-n 27,
     P7, P17, P20, P22, P27, P28).  Self-
     reference (自指) = case-3 meta-principle
     per P22 — needs careful boundary.
   - **知识层 (knowledge layer)**: general
     agent capabilities applicable across
     most projects (类比 reasoning + 归纳 +
     压缩 + recursion, 6 primitives, 5 case
     studies, when-to-reflect, M-n 14, M-n
     23, M-n 26, P29, P10, P11).
   - **项目层 (project layer)**: project-
     specific knowledge (which framework,
     which combos, which APIs, project
     history, CHANGELOG, conventions).
     Examples: skill-incubator's 5-phase
     process, SUA's P-n/M-n system, hermes
     memory system.

2. **3 sources relationship**:
   - **hermes 自进化 files**: ephemeral
     (per-session) + cross-project memory.
     Source for M-n 7 (M-task-summary) +
     M-n 8 (M-task-graph) + self-application.
   - **SUA 项目知识库**: persistent
     (project-internal) + project-agnostic.
     Source for 25 P-n + 26 M-n + R1-R12.
   - **skill (final 3rd source)**: portable +
     cross-framework.  Source for 6 primitives
     + 6 case studies + when-to-reflect.
     Per 你 turn Part 3: 用户 may only have
     skill, not SUA/hermes.

3. **Single-skill scenario**:
   - skill contains ALL knowledge from
     3 layers (subset for portability):
     - 核心层: P7 + P11 + P17 + P20 + P22 +
       P28, M-n 12 + M-n 14 + M-n 18 + M-n 21
       + M-n 22 + M-n 25 + M-n 26
     - 知识层: 6 primitives + 5 case studies
       + when-to-reflect, M-n 14 + M-n 23 +
       M-n 26
     - 项目层: framework compatibility matrix
       + 3-layer architecture doc + single-
       skill fallback protocol
   - When skill is the ONLY source, agent
     should not require hermes-specific or
     SUA-specific paths.

**Why this M-rule exists**: per 你 turn
2026-07-15 explicit 6 parts + 联想 + 推理
+ 类比 (per M_RULE_AUTHORING 3-condition
gate, 5+ observed sites).

**5 transition rules** (per 你 turn + M-n 26
context-decay):

- 核心层 ↔ 知识层 transition: P22 case-3
  meta-principles → M-n operator rules.
- 知识层 ↔ 项目层 transition: M-n 14
  类比 → specific framework conventions.
- 3 source synchronization: M-skill-
  synchronize (c83) + hermes sync via
  MEMORY.md.
- Single-skill fallback: P29 reduce
  context + R6 cross-ref + R11 boundary.
- New agent perspective: P26 fresh-agent
  simulation 5/5 PASS.

**Cross-references**:

- `docs/OPERATING_RULES.md` § M-n 26
  context-decay-management
- `docs/OPERATING_RULES.md` § M-self-
  application 4 levels
- `docs/OPERATING_RULES.md` § M-n 18
  recursive-summary-protocol
- `docs/PRINCIPLES_FULL.md` "P29"段
- 你 turn 2026-07-15 — origin

### M-plan-conditional (added 2026-07-15, per 你 turn "不确定 → 规划; 清晰 → 继续")

**Trigger**: before any major decision OR
when 4 conditions met (any of):
- (a) agent 不确定 plan
- (b) plan 混乱 OR 多 part conflict
- (c) 重大调整 (new M-n / P-n / 原则
  改动, OR 项目 pivot)
- (d) user explicit "应该 先 做规划"

If NONE of (a-d): agent has plan AND
plan is 清晰 / 合理 / 可行 / 符合预期 →
**continue per plan** (per M-n 24 pace-
continuity).

**See `M_PLAN_CONDITIONAL_DETAIL.md`
(L2 companion per P11 + R6) for self-
audit 4-condition check + worked examples
+ relationship to P22 case-3 + P29.**

**Action** (4 sub-steps per 你 turn):

1. **Self-audit 4 conditions** (per M-n 22
   3W1H first):
   - Q1: agent 不确定? (per M-n 21 ask/
     infer/guess)
   - Q2: plan 混乱 OR 多 part conflict?
   - Q3: 重大调整 (new M-n / P-n)?
   - Q4: user explicit "先 做规划"?
2. **If any YES → 先 做规划** (per P22 +
   M-n 23 periodic re-analysis):
   - 目标 (final goal per M-n 23 re-
     analysis)
   - 倒推 (sub-tasks per M-n 16 stage 3
     top-down 分治)
   - 分治 (sub-task breakdown per M-n 22
     3W1H)
   - 做下去 (execute per plan per M-n 24)
3. **If all NO → continue per plan** (per
   M-n 24 + M-n 18 sub-task continue):
   - commit + continue per M-n 24
   - 节点 生命周期 (per M-n 18 destruction
     contract)
   - pace-continuity 不 interrupt
4. **Plan conditional 自我 验证** (per
   P17 老实说 + M-n 22):
   - If agent 显式 claim "规划 清晰 合理"
     but 实际 conflict → trigger this M-rule
   - Per P29 主动 reduce context: explicit
     plan > implicit assumption

**Why this M-rule exists**: per 你 turn
2026-07-15 explicit directive + 你 vision
"主动 allowed":

- 你 turn 1st: 不确定/混乱/重大调整 → 先
  做规划
- 你 turn 2nd: 清晰/可行/符合预期 → 继续
- 你 turn explicit: "如果你不知道的话
  就学习下"

Per M_RULE_AUTHORING 3-condition gate (7+
observed sites: c118 + c122 + c127 + c134
+ P22 + M-n 12 + 你 turn explicit).

**Relationship to other M-n / P-n**:

- **M-n 21 (ask-or-infer-mark-guess)**: this
  M-rule extends M-n 21 with explicit 4-
  condition check.
- **M-n 22 (3W1H-think-first)**: this
  M-rule uses M-n 22 BEFORE planning
  decision.
- **M-n 23 (periodic-re-analysis)**: this
  M-rule applies M-n 23 to 4-condition
  context.
- **M-n 24 (pace-continuity)**: this M-rule
  applies M-n 24 when all NO.
- **P22 (case-3 meta)**: P22 IS "when stuck
  STOP + plan" (subset of this M-rule).
- **P29 (reduce context)**: P29 IS "主动
  reduce context" (ethos of this M-rule).

**Self-application** (per P28 recursion):

This M-rule IS M-self-application level 4
applied to planning decision.  Recursive:
this M-rule applies itself (i.e., apply 4-
condition check to M-n 28 codification).

**Cross-references**:

- `docs/OPERATING_RULES.md` § M-n 21 ask-
  or-infer-mark-guess
- `docs/OPERATING_RULES.md` § M-n 22 3W1H-
  think-first
- `docs/OPERATING_RULES.md` § M-n 23
  periodic-re-analysis
- `docs/OPERATING_RULES.md` § M-n 24 pace-
  continuity
- `docs/PRINCIPLES.md` P22 (case-3 meta)
- 你 turn 2026-07-15 — origin

### M-acceptance-protocol (added 2026-07-15, per 你 turn "做完任务后需要验收 + 设计验收 + 完整项目 over + 未通过循环修复 + 通过明确说明")

**Trigger**: when agent 认为 任务 完成
(per M-n 21 self-audit OR M-n 22 final
3W1H OR per 你 turn explicit "验收" OR
after every major commit batch).

**See `M_ACCEPTANCE_PROTOCOL_DETAIL.md`
(L2 companion per P11 + R6) for 5-step
protocol + 验收 report template + NASA
SWE-034 reference + cycle loop + 你
notification.**

**Action** (5 sub-steps per 你 turn):

1. **Design 验收 角度 + 要求** (per M-n
   22 3W1H first):
   - What: 哪些 角度 验收?
   - Why: 验收 标准 = ?
   - Who: 谁 acceptance?
   - How: 验收 process?
   - 角度 examples: functional / performance
        / 兼容性 / 安全 / 维护性 / user-
        facing / framework-agnostic / 跨项目
        sync / R1-R12 / P-n compliance / M-n
        compliance / P29 self-application /
        **项目 整洁度** / **新 agent 可读性**
        (per 你 turn 2026-07-15 reminder, c205)

2. **执行 验收** (per M-n 14 类比 + 归纳
   + M-n 25 5-pattern + 你 turn
   "分析/推理/联想/归纳/总结" logic):
   - Analyze: 任务 IS what? (per M-n 16
     observe-think-execute stage 1)
   - Reason: 为什么 这样? (per M-n 16
     stage 2 + M-n 22 3W1H)
   - 联想: 类似 prior pattern? (per M-n 14
     class比 reasoning + M-n 17 Path 2
     inter-domain search)
   - 归纳: general pattern from specific?
     (per M-n 14 induction + M-n 18
     recursive summary)
   - 总结: synthesize? (per M-n 26
     compression + M-n 18 destruction
     contract)

3. **Validate 验收 condition** (per 你 turn
   Part 4 "确认没问题"):
   - All acceptance criteria PASS
   - No open FAIL / PARTIAL items
   - All 角度 covered
   - 验证 evidence recorded (test output,
     commit hash, etc.)
   - Per P17 老实说: don't claim green
     when yellow.

4. **If FAIL** → 新 任务 cycle (per 你 turn
   Part 5):
   - 创建 新 task in PLAN_DETAIL
   - Re-execute fix
   - Re-verify (回到 step 2)
   - Loop until ALL PASS
   - Per 你 turn: "每次你认为做完任务都
     需要验收，没通过就修复，修复完再测，
     循环"

5. **If PASS** → 明确 通知 你 (per 你 turn
   Part 6):
   - 明确 indicate "任务 完成 + 验收 通过"
   - List acceptance criteria + evidence
   - Per P17 老实说: don't claim PASS
     without evidence
   - Per M-n 24: pace-continuity 中 明确
     通知 user is allowed (interrupt
     permitted)

**Why this M-rule exists**: per 你 turn
2026-07-15 explicit 6 parts:

- Part 1 (验收): 任务 完成 后 need to
  verify
- Part 2 (设计): agent should design
  acceptance 角度
- Part 3 (process): 分析/推理/联想/归纳/
  总结 (5 primitives, per 你 turn prior
  c100 M-n 16 + M-n 14 + M-n 25)
- Part 4 (通过 condition): 确认没问题
- Part 5 (失败 loop): 验收 失败 = 新任务
  修复 循环
- Part 6 (通过 反馈): 通知 你 明确

Per M_RULE_AUTHORING 3-condition gate (5+
observed sites):
- c193 VERIFICATION.md create (1-page
  verification summary)
- c172 ad-hoc hermes-verify scripts
- P17 老实说 ("never claim green when
  yellow")
- P22 case-3 meta ("when stuck STOP +
  write plan")
- M-n 26 context-decay-management
- 你 turn prior 2026-07-15 ("如果做完任务
  需要明确指出")
- 你 turn 2026-07-15 explicit (this turn)

**NASA SWE-034 reference** (per research):

- acceptance criteria = (1) criteria user
  must satisfy + (2) performance + essential
  conditions
- 验收 plan documented in SDP-SMP OR
  separate V&V Plan
- Acceptance testing = major portion of
  验收 plan
- 如果 deviations exist → negotiated with
  customer (or fix prior to 验收)

**Claude acceptance-criteria-verification
skill reference**:

- Per-criterion status: PASS / FAIL /
  PARTIAL / SKIP
- Evidence: test output, screenshot, log
- Verification report template
- Synced to project-status fields

**Relationship to other M-n / P-n**:

- **M-n 14 (two-track-reasoning)**: this
  M-rule uses 类比 + 归纳 (steps 2 + 4).
- **M-n 16 (observe-think-execute)**: this
  M-rule uses all 6 stages (analyze =
  stage 1 + reason = stage 2).
- **M-n 17 (context-freshness-check)**: this
  M-rule uses Path 2 (联想).
- **M-n 18 (recursive-summary-protocol)**: this
  M-rule uses 归纳 (step 4).
- **M-n 24 (pace-continuity)**: this M-rule
  explicitly interrupts pace-continuity
  (step 5).
- **M-n 26 (context-decay-management)**: this
  M-rule uses 总结 (step 2).
- **M-n 28 (plan-conditional)**: this M-rule
  applies AFTER M-n 28 confirms plan
  complete.
- **P17 (老实说)**: this M-rule enforces P17.
- **P22 (case-3 meta)**: this M-rule IS P22
  applied to task completion.

**Self-application** (per P28 recursion):

This M-rule IS M-self-application level 4
applied to task acceptance.  Recursive:
this M-rule applies itself (i.e., apply
5-step protocol to M-n 29 codification).

**Cross-references**:

- `docs/OPERATING_RULES.md` § M-n 14/16/17/
  18/24/26/28
- `docs/PRINCIPLES.md` P17 (老实说)
- `docs/PRINCIPLES.md` P22 (case-3 meta)
- `VERIFICATION.md` (per c193, 1-page
  verification summary)
- 你 turn 2026-07-15 — origin
- NASA SWE-034 — research reference

### M-knowledge-context-trade-off (added 2026-07-15, per 你 turn "知识 vs 上下文 trade-off + 分层 + 类比")

**Trigger**: when designing new skill /
project / M-rule, or when agent must
balance knowledge 充足 度 vs context 管理
trade-off.

**See `M_KNOWLEDGE_CONTEXT_TRADE_OFF_DETAIL.md`
(L2 companion per P11 + R6) for 4-priority
decision tree + worked examples.**

**Action** (4-priority table per 你 turn
Part 1+2+3+4):

| Priority | Criterion | Method |
|---|---|---|
| **HIGHEST** | **Knowledge 充足** | All audit points PASS + reasoning primitives + case studies.  Per M-n 29 acceptance-protocol. |
| **HIGH** | **Context 管理** | M-n 26 (context-decay-management) + M-n 23 (periodic re-analysis) + M-n 18 (节点 生命周期).  Lazy-load for smaller models. |
| **TIE** | **Trade-off** | M-n 27 (3-layer) + M-n 14 (class比 compression).  分层 for knowledge layer + 平铺式 for behavior spec (per 你 turn Part 5). |
| **Always** | **分层 自顶向下 分治** | M-n 16 stage 3 top-down + M-n 18 recursive-summary + M-n 22 3W1H-first.  Per 你 turn Part 4 隐含 ask "希望 你 没有忘记". |
| **Always** | **Update order rule** | SUA (知识库, source) → skill-incubator (孵化器, middle) → skill (final, downstream).  Per 你 turn 2026-07-15 explicit priority directive.  When 知识 changes in SUA, MUST propagate to skill-incubator + skill.  Reverse direction NOT allowed (per M-n 20 + P21). |

**Why this M-rule exists**: per 你 turn
2026-07-15 explicit 5 parts:

1. Knowledge 充足 = HIGHEST priority
2. Context 管理 = HIGH priority
3. Trade-off via 分层 + 类比
4. 分层 自顶向下 分治 still 实践
5. Skill 行为规范 = 平铺式 (per M-n 27
   3-layer, 核心层 平铺)

Per M_RULE_AUTHORING 3-condition gate (5+
observed sites):
- c97-c110 (M-n 13 + M-n 14 + M-n 16 + M-n
  18 + M-n 22 + M-n 23 + M-n 24 codify)
- c197 (M-n 27 knowledge-layer-architecture)
- c189 (M-n 26 context-decay-management)
- c211 (skill Flat structure codify)
- 你 turn 2026-07-15 explicit trade-off

**Trade-off method** (per 你 turn Part 3):

- **分层 (hierarchical)**: for knowledge
  layer (primitives + case studies).
  Per P11 摘要+引用.
- **平铺式 (flat)**: for behavior spec
  (agent 行为规范).  Per M-n 27 核心
  layer.
- **类比 (analogy)**: for compression
  (per M-n 14 entropy dimension + 6
  reasoning primitives).
- **自顶向下 分治**: for project /
  task decomposition (per M-n 16 stage 3
  + M-n 22 3W1H).

**3-layer application** (per M-n 27):

- 核心层 (behavior spec) = 平铺式
  (per 你 turn Part 5)
- 知识层 (primitives + case studies) =
  分层 (per P11)
- 项目层 (framework specific) = high
  churn + 分层 as needed

**Self-application** (per P28 recursion):

This M-rule IS M-n 27 (3-layer) + M-n 14
(class比) + M-n 18 (节点 生命周期)
applied to knowledge vs context trade-off.
Recursive: applies itself.

**Cross-references**:

- `docs/OPERATING_RULES.md` § M-n 26 / M-n
  27 / M-n 29
- `docs/OPERATING_RULES.md` § M-n 18
  recursive-summary-protocol
- SUA `agent-reflection-skill/SKILL.md` §
  Flat structure for behavior spec (per
  c211)
- 你 turn 2026-07-15 — origin

