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
   to do, what memory is needed.
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
the agent.

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