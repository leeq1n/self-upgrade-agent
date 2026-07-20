# M-two-track-reasoning (full text)
Last P20-verified: 2026-07-15

> L0: L2 detail for `OPERATING_RULES.md` § M-two-
> track-reasoning段.  Per P11 摘要+引用 + R6, this
> companion is required when the summary rule段
> references both tracks (类比 + 逻辑).  Load when:
> agent needs to reason about a problem and decides
> which track to use.

## Why both tracks (per user message 2026-07-15)

> "思考包括两种，类比推理和逻辑推理"
> "本质上就是'思考包括两种，类比推理和逻辑推理'
> 这一条"

This M-rule codifies both tracks as a unified
framework.  Project has been using both implicitly
(c44 5-family 类比 + P25 6-step 逻辑); this M-rule
makes them explicit.

## Track 1: 类比推理 (analogical reasoning)

**Definition**: find structural similarity across
domains and apply pattern from domain A to domain B.

**When to use**:
- Novel problem (no established procedure)
- Cross-domain insight needed
- Pattern recognition across cases

**Output format**:
- "X is to Y as A is to B"
- 1+ verifiable mapping between X and A

**Worked examples in SUA**:
- c44 5-family 类比 framework
- c50 (recursive 类比 on audit)
- c81 信息拓扑 类比 (3 schemes)
- c92 M-n 12 Path (a) "Refine name" = 类比 to existing
- c93 M_TERMINOLOGY_CLARITY_DETAIL examples (3 类比)

## Track 2: 逻辑推理 (logical reasoning)

**Definition**: sequential deduction from established
facts using structural verification.

**When to use**:
- Well-defined problem with established procedure
- Verification needed (gate checks, test pyramid)
- Sequential reasoning with verifiable steps

**Output format**:
- "Given [fact 1], [fact 2], ..., [conclusion]"
- Each step verifiable by structure (test, code, gate)

**Worked examples in SUA**:
- P25 6-step (principle modification discipline)
- 7-check (project self-org)
- P5 (verify before commit)
- P3 (test pyramid)
- P22 (stuck→plan)

## When to use which (decision tree)

```
Q1: Is the problem well-defined?
├── Yes → Q2
└── No → Track 1 (类比)

Q2: Is verification needed?
├── Yes → Track 2 (逻辑)
└── No → Track 1 (类比, faster)

Q3: Is high-stakes (P25 6-step requires)?
├── Yes → Both (Track 1 for read first, Track 2
│   for analysis)
└── No → Either (per Q1 + Q2)
```

## How both tracks compose

Per M-n 16 (observe-think-execute 6-stage chain):
- Track 1 (类比) applies to: 观察 + 思考-1 +
  思考-2 (stages 1, 2, 4)
- Track 2 (逻辑) applies to: 思考-3 + 执行-1 +
  执行-2 + 执行-3 (stages 3, 5, 6 + thinking in
  stage 6)

Combined: project observes (类比) → thinks 类比 →
executes 逻辑 → thinks 类比 → executes 逻辑 →
thinks 逻辑 + executes 逻辑.

## When NOT to use (anti-patterns)

### Anti-pattern 1: Only one track

Both tracks required for principled reasoning, per
P25 6-step (Read first = 类比, Analysis = 逻辑).

### Anti-pattern 2: 类比 when 逻辑 is sufficient

If the problem is well-defined and verification
suffices, use only 逻辑 (faster, more rigorous).

### Anti-pattern 3: 逻辑 when 类比 is right

If the problem is novel or cross-domain, 类比 is
the right tool.  逻辑 alone misses insight.

### Anti-pattern 4: Force both when neither fits

If the problem doesn't fit either track, the
problem may need re-framing (per M-n 15 principle-
reordering).

## Worked examples (2 cases)

### Case 1: c96 P28 lift

- **Track 1 (类比)**: project has skill b502577's
  6th primitive (recursion).  Mirror it to SUA as
  P28 (类比: skill recursion = project recursion)
- **Track 2 (逻辑)**: M_RULE_AUTHORING 3-condition
  gate (3+ observed needed).  Count recursion
  demos: c82, c92, c93, c94, c95 = 5+ ✅
- **Combined**: P28 lift succeeded

### Case 2: c100 M-n 16 (observe-think-execute)

- **Track 1 (类比)**: project has M-n 14 (2 tracks)
  + skill b502577 6 primitives.  Find 类比 to
  user message 6-stage chain.
- **Track 2 (逻辑)**: M_RULE_AUTHORING 3-condition
  gate.  Count uses of 6-stage chain: previous turns
  (c97-c99, c100 itself) + user message explicit = 3+
  ✅
- **Combined**: M-n 16 codify succeeded

## Relationship to other M-rules + P-n

- **P22 step 3 "find commonalities"** = Track 1 (类比)
- **P25 6-step** = Track 2 (逻辑)
- **P28 (recursion)** = both (apply 类比 + 逻辑
  to self)
- **M-n 12 (terminology-clarity)** = both (detect
  via 类比, refine via 逻辑)
- **M-n 13 (layer-extension)** = Track 1 (find
  layer pattern across projects)
- **M-n 15 (principle-reordering)** = both
  (6 sub-steps use 类比 + 逻辑)
- **M-n 16 (observe-think-execute)** = both
  (6-stage chain uses both tracks)

## Cross-references

- `OPERATING_RULES.md` § M-two-track-reasoning —
  the L0/L1 段 (in SUA)
- `docs/PRINCIPLES_FULL.md` — P22 + P25 full text
- `docs/PRINCIPLES_FULL.md` "Recursion"段 — P28
- `docs/OPERATING_RULES.md` § M-n 11/12/13/15/16
- `../agent-reflection-skill/docs/framework/analogy-and-induction.md`
  — skill 6 primitives
- user message 2026-07-15 — origin
