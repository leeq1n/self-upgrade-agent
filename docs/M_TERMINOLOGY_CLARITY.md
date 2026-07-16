# M-terminology-clarity (full text)
Last P20-verified: 2026-07-15

> L0: L2 detail for `OPERATING_RULES.md` § M-terminology-
> clarity段.  Per P11 摘要+引用 + R6, this companion
> is required when the summary rule段 is detailed
> enough to warrant L2 expansion.  Load when: agent
> notices ambiguous term, when user pushes back on
  unclear phrase, or when bootstrapping new term
  selection.

## Why this M-rule exists

Per user meta-rule 2026-07-15: "如果'撞到一起'是你
提的摘要/标题, 我认为它没说清楚是什么意思, 你后续
可能要处理一下这类问题".

This M-rule operationalizes that meta-rule into a
4-sub-step process.  This L2 doc provides worked
examples, term selection criteria, and decision
support.

## The 4 sub-steps (detailed)

### Sub-step 1: Detect (operational form)

A term is unclear when **any** of these are true:

- **Repeated 3+ times** without operational
  definition (P11 摘要+引用 implicit check: ≤ 120
  chars, no jargon).
- **Metaphor without source domain**: e.g., "撞到
  一起" (collision metaphor) — what's the source
  domain (physics? scheduling? traffic?)?
- **Multiple plausible meanings**: 2+ distinct
  interpretations are reasonable in the same context.
- **External audience (new agent) can't infer**: a
  fresh agent reading previous turns can't deduce
  the term's meaning from context alone.
- **User pushback**: user explicitly says "X is
  unclear" or "what does X mean?" (per M-self-
  application L4 + P26 fresh-agent simulation).

### Sub-step 2: Acknowledge

Per P17 honest reporting: explicitly say "I'm using
X to mean Y, but X is unclear; let me clarify".  This
avoids the silent-use anti-pattern.

**Acknowledge template**:

```
"I used [X] [N] times in previous turns, but X is
unclear (e.g., metaphor without source domain, or
multiple plausible meanings).  Let me clarify:
[X] means [Y, with operational definition].  Future
turns should use [refined term] instead."
```

### Sub-step 3: Clarify or codify (3 paths)

#### Path (a): Refine name

**When**: the term is replaceable with a clearer
one, and the cost of changing all references is
low.

**Refinement criteria** (per P7 奥卡姆 + P11
摘要+引用):

1. **Shorter** is better (per P7 奥卡姆).
2. **No jargon / no metaphor** (per P11 摘要+引用:
   ≤ 120 chars, clear English).
3. **Self-describing**: the new term itself hints
   at the meaning.
4. **Consistent with existing terminology**: if
   similar terms exist, prefer extension over
   invention.

**Refinement process**:

1. Brainstorm 3-5 candidate refined terms.
2. Apply refinement criteria (above).
3. Pick the best one (per P7 奥卡姆).
4. Update all references (in this turn + future
   turns).
5. Verify by re-reading (per P26 fresh-agent
   simulation).

**Example**: "撞到一起" → "**replan on conflict**"
(or simpler: "**replan**").  This applies the
refinement criteria:
- Shorter: yes (10 chars vs 4 Chinese chars; English
  is shorter for ASCII)
- No jargon: "replan" is clear; "on conflict"
  specifies when
- Self-describing: "replan" hints at "plan again"
- Consistent: matches existing P22 "stuck→plan"
  terminology

#### Path (b): Add definition段

**When**: the term is hard to replace (e.g., a
specific term-of-art), but lacks a clear definition
in the project.

**Process**:

1. Write 1 段 in PRINCIPLES.md or relevant doc
   (e.g., a glossary, or the term's own doc).
2. Per P11 摘要+引用: ≤ 120 chars for the L0
   definition; full L2 detail in companion.
3. Cross-reference from the term's first use site.

**Example**: "撞到一起" could be defined as "多个
context / task / rule 同时需要处理, 需要 replan"
in a glossary.  But since "replan" is shorter and
clearer, Path (a) is preferred.

#### Path (c): Update memory

**When**: the term is used in memory entries but
should be refined.

**Process**:

1. Use `memory` tool to replace old text with
   refined text in relevant entries.
2. Re-read to verify consistency.

**Example**: memory entry 7 contains "撞到一起"
5+ times; replace with "replan" (or "replan on
conflict" for first use, then "replan" thereafter).

### Sub-step 4: Verify

Per P26 fresh-agent simulation: a new agent reading
the project after the change should be able to
understand all terms without ambiguity.  If not,
re-iterate Sub-step 3.



## When NOT to invoke (anti-patterns)

- **Don't** silently use ambiguous terms (P17
  honest).
- **Don't** over-codify: 1 occurrence doesn't
  warrant M-n (M_RULE_AUTHORING 3-condition gate).
- **Don't** invent new terms without checking
  existing ones first (P7 奥卡姆: prefer existing
  terms).
- **Don't** over-refine: 3 refinements per term is
  enough; if still unclear, the term may be
  intrinsically ambiguous (consider Path (b)
  definition instead).
- **Don't** violate user explicit terminology: if
  user says "use X", use X (even if X is unclear
  to you).  Ask for clarification instead of
  silently substituting.

## Relationship to other M-rules + P-n

- **M-self-application** L4: this M-rule is a
  self-application of M-self-application's 4-level
  check (L4 = agent's own operating behavior).
- **M-self-audit** 6-step + step 7: apply M-self-audit
  after refining a term (verify no inconsistency).
- **P11 摘要+引用**: P11 says "summary ≤ 120 chars,
  no jargon" — this M-rule operationalizes P11's
  terminology check.
- **P22 case-3**: this is a meta-rule (about how
  the agent should behave in ambiguous situations).
- **P26 fresh-agent simulation**: Sub-step 4
  (verify) uses P26.
- **M_RULE_AUTHORING 3-condition gate**: even
  meta-rules need 3+ observations OR bootstrap
  exception (this M-rule has bootstrap exception
  per user-explicit ask).

## Cross-references

- `OPERATING_RULES.md` § M-terminology-clarity —
  the L0/L1段 (in SUA)
- `docs/HANDOFF_DETAIL.md` "Sub-project-for-
  experimentation pattern" 段 (c89-small) — related
  pattern
- `docs/HANDOFF.md` — onboarding for new agents
- User meta-rule 2026-07-15 — origin
- `docs/P11.md` (if exists) — P11 摘要+引用
  canonical
- `docs/P22.md` (if exists) — P22 case-3 boundary

## Detail (L2)

For 'Worked examples' (3 examples) and 'Term selection criteria' (7-row table), see [`M_TERMINOLOGY_CLARITY_DETAIL.md`](M_TERMINOLOGY_CLARITY_DETAIL.md).  Per R6, this companion is required when the summary exceeds 7 KB.
