# SKILL_DESIGN — How to design and incubate skills

> L0: The core knowledge for designing and incubating skills
> from SUA's accumulated reasoning patterns.  Restored to
> SUA on 2026-07-20 from `../skill-incubator/SKILL_DESIGN.md`
> (per project consolidation: skill-incubator is now archived).
> This is the canonical version (per 2026-07-15 split from
> SUA's `docs/SKILL_GENERATION.md`, then consolidated back).

## Why this doc exists

Without this doc, decisions about "should we create a new
skill project" are ad hoc.  This doc codifies the **decision
criteria** + **design principles** + **self-preservation
contract** so the decision is principled rather than random.

## 4 sub-knowledge areas (decision framework)

### 1. When to incubate a skill (触发)

Incubate a new skill (i.e., create a new `skill-*/` repo)
when **all 4 conditions** are met:

- SUA commit demonstrates a **meta-cognitive pattern**
  (about how to reason, not what to do in a specific
  project).
- Pattern has **3+ observed occurrences** (per
  M_RULE_AUTHORING 3-condition gate; not just 1 case).
- Pattern is **framework-agnostic** (would work in
  Hermes / Claude Code / Codex, not just SUA).
- User has explicitly endorsed the extraction (per their
  meta-rule "提炼到 skill 项目的时候提供给对方这类
  知识").

Don't incubate when:

- Pattern is **SUA-specific** (e.g., specific to SUA's
  test suite, P-n, or workflow).
- Pattern is **one-shot** (single observed case).
- Pattern is **framework-specific** (e.g., uses Hermes-
  only API).
- Pattern is **already codified** in an existing skill.

### 2. What to extract (提取内容)

A good skill design has:

- **Portable**: works in any agent framework that can
  read files.
- **Minimal**: 1 primitive per commit (per P4 1 logical
  feature per commit, applied to skill too).
- **Evidence-based**: each analogy cites 1+ verifiable
  mappings; each induction cites 3+ cases.
- **Self-contained**: doesn't import SUA-specific code
  (per P21 cross-project independence).
- **Cross-referenced**: cross-refs to SUA's source
  pattern (so the lineage is traceable).

### 3. How to format (格式)

Skill docs use the L0/L1/L2 + _DETAIL pattern (per P11
摘要+引用 + P20 progressive disclosure).  Specifically:

- L0: 1-line status (what this doc is, when to use it).
- L1: 5-10 minute read (the main content).
- L2: deeper detail in `_DETAIL.md` companion.
- Doc size: ≤ 7KB summary; if exceeded, split to
  `_DETAIL.md` (per R5 + R6).
- 4-line output structure (per P11 摘要+引用): pattern /
  why / limits / next action.

### 4. What NOT to do (避免破坏)

- **Don't break portability**: don't import SUA-only
  tools, hooks, or file paths.
- **Don't break existing primitives**: new content
  should extend, not replace.
- **Don't add primitives without user meta-rule**: per
  P7 奥卡姆, wait for explicit user request.
- **Don't auto-sync**: per `HANDOFF_DETAIL.md` sibling
  awareness 段, sync is "review at parent-verify",
  not "every commit".
- **Don't lose context**: when extracting a pattern,
  include the **why** (per M-self-application 4-level L2).

## Skill self-preservation contract

When an incubated skill updates itself (e.g., new
primitive, new case study, new doc), it must check
**5 preservation rules**:

1. **Preserve core primitives**: don't remove or
   contradict the existing primitives.
2. **Preserve cross-ref to SUA**: every skill commit
   should have at least 1 cross-ref to SUA (parent
   project), so the lineage is traceable.
3. **Preserve framework-agnostic claim**: no new
   framework-specific code (Hermes-only, etc.).
4. **Preserve R5 + R6 + R8 compliance**: skill docs
   follow the same caps as SUA (≤ 7KB summary, with
   `_DETAIL.md` companion if exceeded).
5. **Preserve 4-line output structure**: each primitive's
   output is `pattern / why / limits / next action` (per
   L2 detail).

This is the **self-preservation contract** that the
incubator explicitly teaches the skill (per user meta-rule
"skill 避免破坏自己, 做好维护").

## The 5-phase incubation process

When the 4 conditions (above) are met, follow this
process:

1. **Observe**: identify the pattern in SUA commits
   (typically 3+ recent commits show the pattern).
2. **Decide**: apply the 4 conditions as a checklist;
   if all 4 ✅, proceed.
3. **Spawn**: create a new `skill-<name>/` repo in
   `<workspace>/` with skeleton (README + SKILL.md +
   AGENTS.md + HANDOFF.md).
4. **Codify**: extract the pattern into 1 primitive per
   commit (per P4 1 logical feature per commit), with
   cross-refs to SUA's source.
5. **Maintain**: monitor the skill's self-application
   (per `Recursion` primitive); if the skill breaks the
   preservation contract, intervene.

## Cross-references

- `docs/SKILLS.md` — skill lifecycle overview
- `docs/PRINCIPLES.md` — principles applied here
- `docs/OPERATING_RULES.md` — M-skill-synchronize段 —
  the operational M-rule that this knowledge
  operationalizes
- `docs/HOW_TO_READ_GRAPH.md` — fresh-agent read
  pattern
- `docs/KNOWLEDGE_ORG.md` — information topology
  (where this knowledge lives, classified)
- `agent-reflection-skill/docs/framework/analogy-and-induction.md`
  — first incubated skill's primitives
- `agent-reflection-skill/docs/framework/skill-generation.md`
  — first incubated skill's mirror of this knowledge

## 核心 内容 (core content, per user message 2026-07-15)

Per user message 2026-07-15: "孵化器这项目或许需要将知
识库中agent行为规范和skill规范相关的内容标记核
心，方便后续skill项目的阅读".

This段 marks the **核心 (core)** content in this
project for skill projects to read first.  4 核心
areas + 1 核心 constraint.

## Note on 2026-07-20 consolidation

This doc was originally split to `../skill-incubator/`
on 2026-07-15, then consolidated back to SUA on
2026-07-20 (per project re-architecture: SUA = knowledge
library, skill-incubator = archived, agent-reflection-
skill = standalone since v1.0.0).

The archived `../skill-incubator/` directory retains
git history (per P14 docs current: history is the
narrative, don't rewrite).

## Detail (L2)

For 4 核心 areas + 1 核心 constraint + "How to use this
核心 marker", see [`SKILL_DESIGN_DETAIL.md`](SKILL_DESIGN_DETAIL.md).
Per R6, this companion is required when the summary
exceeds 7 KB.