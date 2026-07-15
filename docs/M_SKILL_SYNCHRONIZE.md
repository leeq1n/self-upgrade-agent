# M-skill-synchronize (full text)
Last P20-verified: 2026-07-15

> L0: Operational M-rule for cross-project skill sync.
> Load when: user mentions a skill concept, when SUA's
> commits involve pattern-extraction to skill, or when
> debugging "skill broke after a sync".  Per
> M_RULE_AUTHORING 3-condition gate: reusable across
> projects ✓, triggerable (skill-mention user turn) ✓,
> 3+ occurrences observed (c83 + d1dbb66 + f09d06e +
> b502577 + e19189b + skill-incubator skeleton) ✓ →
> promoted to full M-rule (per 2026-07-15 session).

## Why this M-rule exists

Per user meta-rule 2026-07-15: "当我提到跟 skill 有关
的内容时, 你需要看看 SUA 能不能学到对应知识, 并且
在提炼到 skill 项目的时候提供给对方这类知识, 避免
破坏自己, 做好维护".  This M-rule operationalizes
that meta-rule into a 4-sub-step process that any
agent can apply.

## The 4 sub-steps (per OPERATING_RULES.md § M-skill-synchronize)

### Sub-step 1: Check SUA's skill-generation-knowledge

Does SUA already have a 段 about this skill topic?

- Read `docs/SKILL_GENERATION.md` (deprecated 2026-07-15)
  or `../skill-incubator/SKILL_DESIGN.md` (canonical
  post-c87).
- If yes, apply existing knowledge.
- If no, consider whether the topic warrants new
  knowledge (per 4-condition checklist).

### Sub-step 2: Decide sync direction

| Direction | When |
|---|---|
| SUA → skill | SUA demonstrates a new pattern; skill should learn it |
| skill → SUA | skill discovers a new insight; SUA should record it |
| skill-incubator → skill | skill-incubator decides to spawn / update a skill |
| skill-incubator → SUA | skill-incubator codifies a design principle that SUA should mirror |

Per sibling awareness protocol
(`HANDOFF_DETAIL.md` 61aab30), the direction is one-way
(per "skill 项目是基于 SUA" — SUA is upstream).

### Sub-step 3: Mirror appropriately

- **SUA → skill**: write a skill commit that captures
  the framework-agnostic pattern (without SUA-specific
  code).  Per P21 cross-project independence.
- **skill → SUA**: document the lesson in SUA's
  HANDOFF_DETAIL.md "Sibling project awareness" 段.
- **skill-incubator → skill**: create / update skill
  per `../skill-incubator/SKILL_DESIGN.md` 5-phase
  process.
- **skill-incubator → SUA**: SUA 留 1 cross-ref 段
  to skill-incubator's canonical doc (per c87 pattern).

### Sub-step 4: Verify skill self-preservation

Does the new content preserve the skill's portability,
cross-ref to SUA, and not break existing 6 reasoning
primitives?  Per skill's 5 self-preservation rules
(`../agent-reflection-skill/docs/framework/skill-generation.md`):

1. Preserve core primitives (6 + recursion)
2. Preserve cross-ref to SUA
3. Preserve framework-agnostic claim
4. Preserve R5 + R6 + R8 compliance
5. Preserve 4-line output structure

## When to invoke

Invoke this M-rule when **any** of these triggers fire:

- User mentions a skill concept (the original trigger,
  per user meta-rule)
- SUA commit involves pattern-extraction to skill
- A sibling skill project (e.g.,
  `agent-reflection-skill/`) requests sync
- A periodic review (per sibling awareness 段) identifies
  drift
- The 3-project architecture is being modified

## When NOT to invoke (anti-patterns)

- **Don't** auto-sync on every commit.  Per
  `HANDOFF_DETAIL.md` 04a2935, sync is "review at
  parent-verify", not "every commit".
- **Don't** break portability.  If SUA-specific code
  would need to be imported, don't sync.
- **Don't** add new skill primitives without explicit
  user meta-rule.  Per P7 奥卡姆, wait for explicit
  request.
- **Don't** sync without applying all 4 sub-steps.
  Skipping a sub-step leads to drift (one observed case
  in c83 → d1dbb66 cycle).

## Worked examples

### Example 1: SUA c83 → skill d1dbb66

- Sub-step 1: SUA created `docs/SKILL_GENERATION.md`
  (c83)
- Sub-step 2: SUA → skill (skill should mirror)
- Sub-step 3: skill created
  `docs/framework/skill-generation.md` (d1dbb66)
- Sub-step 4: 5 preservation rules verified

### Example 2: User turn 2026-07-15 → 3-project split

- Sub-step 1: User mentions "原则库 + skill 孵化器"
- Sub-step 2: SUA → skill-incubator (split project)
- Sub-step 3: skill-incubator created (f8404c5), SUA
  deprecated SKILL_GENERATION (c87), skill updated
  cross-refs (e19189b)
- Sub-step 4: All 3 projects preserve their respective
  responsibilities

### Example 3: skill b502577 recursion → SUA c82

- Sub-step 1: skill added 6th primitive (recursion)
- Sub-step 2: skill → SUA (SUA should learn about
  recursion)
- Sub-step 3: SUA added P28 candidate段 (c82)
- Sub-step 4: P28 candidate, not yet lifted (per
  M_RULE_AUTHORING 3-condition gate)

## Relationship to other M-rules

- **M-self-application**: M-skill-synchronize applies
  M-self-application's 4-level check to skill sync
  specifically.
- **M-self-audit**: After applying M-skill-synchronize,
  apply M-self-audit to verify the sync didn't break
  either project.
- **M-add-then-reduce**: When syncing, prefer adding to
  SUA's HANDOFF_DETAIL.md "Sibling project awareness"
  段 (not new files) to avoid bloat.
- **M-task-summary**: After sync, write a parent task
  summary that records the sync direction and content.

## Cross-references

- `OPERATING_RULES.md` § M-skill-synchronize — the
  L0/L1段 (in SUA)
- `docs/SKILL_GENERATION.md` (deprecated per c87) —
  original location of SUA's skill-generation-knowledge
- `../skill-incubator/SKILL_DESIGN.md` (canonical post-
  c87) — skill-incubator's design knowledge
- `../skill-incubator/docs/process/when-to-incubate.md`
  — 4-condition checklist
- `../skill-incubator/docs/framework/case-studies.md`
  — first worked case
- `../agent-reflection-skill/docs/framework/skill-generation.md`
  — skill-side mirror
- `HANDOFF_DETAIL.md` 61aab30 — sibling awareness
  protocol