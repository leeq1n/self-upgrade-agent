# SKILL_GENERATION — How SUA generates skills (knowledge base)

> L0: SUA's knowledge base for **how to generate skills
> correctly**.  This is the **meta-knowledge** that SUA
> maintains about its sibling project
> (`../agent-reflection-skill/`).  Per user meta-rule
> 2026-07-15: "SUA 除了维护 agent 行为规范, 还有维护
> skill 生成规范. SUA 需要知道自己生成 skill 的时候需要
> 注意些什么".  This file is SUA's **self-knowledge** about
> skill generation, NOT a P-n (it's a M-n / knowledge
> type, not a principle).

## Why this file exists

SUA has two kinds of knowledge to maintain:

1. **agent behavior rules** (P-n, M-*, R-n) — codified in
   `docs/PRINCIPLES.md` (flat, per 信息拓扑 方案 C c81).
2. **skill generation knowledge** (this file) — SUA's
   self-knowledge about how to design / extract / maintain
   skills correctly.

Without (2), SUA can produce a skill that breaks the
sibling project.  With (2), SUA can ensure skill is
**portable**, **framework-agnostic**, and **self-preserving**.

## What "skill generation" means here

Per current setup:

- SUA = upstream (origin of patterns)
- skill = downstream (portable consumer of patterns)

SUA "generates" skill content via:

1. **Pattern extraction** (SUA commit demonstrates a
   pattern → skill commit codifies it as reasoning
   primitive, see skill `analogy-and-induction.md`).
2. **Process mirror** (SUA M-rule → skill process trigger,
   see `M-skill-synchronize` 段 in OPERATING_RULES.md).
3. **Topology decision** (per c81, SUA 决定 哪类知识
   flat vs classified vs skill-portable).

## 4 sub-knowledge areas (per M-skill-synchronize 4 sub-steps)

### 1. When to generate a skill commit (触发)

Generate a skill commit when:

- SUA commit demonstrates a **meta-cognitive pattern**
  (about how to reason, not what to do).
- Pattern has **3+ observed occurrences** (per
  M_RULE_AUTHORING 3-condition gate).
- Pattern is **framework-agnostic** (would work in
  Hermes / Claude Code / Codex, not just SUA).
- User has explicitly endorsed the extraction (per
  their meta-rule about "提炼到 skill 项目的时候").

Don't generate a skill commit when:

- Pattern is **SUA-specific** (e.g., specific to SUA's
  test suite, P-n, or workflow).
- Pattern is **one-shot** (single observed case).
- Pattern is **framework-specific** (e.g., uses Hermes-
  only API).
- Pattern is **already codified** in skill.

### 2. What to extract (提取内容)

A good skill extraction is:

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

### 4. What NOT to do (避免破坏)

- **Don't break portability**: don't import SUA-only
  tools, hooks, or file paths.
- **Don't break the 4 (now 6) primitives**: new content
  should extend, not replace.
- **Don't add primitives without user meta-rule**: per
  P7 奥卡姆, wait for explicit user request.
- **Don't auto-sync**: per HANDOFF_DETAIL.md 04a2935,
  sync is "review at parent-verify", not "every commit".
- **Don't lose context**: when extracting a pattern,
  include the **why** (per M-self-application 4-level
  L2 — code is incomplete without its motivation).

## Skill self-preservation (principle B)

When the skill project updates itself (e.g., new
primitive, new case study, new doc), it must check:

1. **Preserve core primitives**: don't remove or
   contradict the 6 primitives (analogy / induction /
   reflection / abduction / compression / recursion).
2. **Preserve cross-ref to SUA**: every skill commit
   should have at least 1 cross-ref to SUA (parent
   project), so the lineage is traceable.
3. **Preserve framework-agnostic claim**: no new
   framework-specific code (Hermes-only, etc.).
4. **Preserve R5 + R6 + R8 compliance**: skill docs
   follow the same caps as SUA (≤ 7KB summary, with
   `_DETAIL.md` companion if exceeded).
5. **Preserve 4-line output structure**: each
   primitive's output is `pattern / why / limits / next
   action` (per L2 detail).

This is the **self-preservation contract** that SUA
explicitly teaches the skill (per user meta-rule "skill
也需要注意不破坏自己").

## Cross-references

- `docs/M_SKILL_SYNCHRONIZE.md` (M-n operational form,
  in OPERATING_RULES.md) — the process rule.
- `docs/HANDOFF_DETAIL.md` 61aab30 (sibling awareness
  protocol) — the protocol part.
- `docs/KNOWLEDGE_ORG.md` c81 (information topology
  方案 C) — the placement part.
- `docs/PRINCIPLES_FULL.md` c82 (recursion primitive,
  P28 candidate) — the meta-cognitive part.
- `../agent-reflection-skill/HANDOFF_DETAIL.md` 04a2935
  (skill side mirror) — the receiving end.
- `../agent-reflection-skill/docs/framework/analogy-and-induction.md`
  (the 6 primitives) — what the skill currently teaches.
