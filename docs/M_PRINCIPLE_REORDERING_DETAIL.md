# M-principle-reordering (full text)
Last P20-verified: 2026-07-15

> L0: L2 detail for `OPERATING_RULES.md` § M-principle-
> reordering段.  Per P11 摘要+引用 + R6, this
> companion is required when the summary rule段
> describes a multi-step procedure.  Load when:
> principles are disordered, after modifying any
> principle, or when project vision drifts.

## Why this L2 doc exists

The OPERATING_RULES.md § M-principle-reordering段
(c99, per user message "原则混乱后 6-step") provides the
6 sub-steps.  This L2 doc provides worked examples
per sub-step, decision tree, and how this M-rule
relates to P25 6-step.

## The 6 sub-steps (detailed)

### Sub-step 1: 重读 (re-read)

**Action**: re-read all current P-n + M-n + R-n +
memory entries.

**Goal**: ensure current state is fully
internalized before proceeding.

**Output**: refreshed understanding of current
principles + memory.

**Worked example**: c99 (M-n 15 codify) started
with re-read of c97 (M-n 13) + c98 (M-n 14) +
memory 7.  This ensured M-n 15 fit with existing
M-rules.

### Sub-step 2: 类比思考 (analogical thinking)

**Action**: find structural similarity between
current chaos and previous patterns.

**Tools**: M-n 14 Track 1 (类比), 5-family 类比
framework (c44), cross-project 类比.

**Output**: list of similar past patterns + their
resolutions.

**Worked example**: c99 类比思考 found: project has
P25 6-step for principle modification, M-n 15
extends P25 with explicit 类比 + 归纳 sub-steps.

### Sub-step 3: 归纳总结 (inductive summary)

**Action**: extract pattern from observations.

**Tools**: M-n 14 Track 2 (逻辑) + induction
primitive (skill b502577).

**Output**: pattern + general rule.

**Worked example**: c99 归纳总结: project has
informal 6-step process (c95, c96, c97, c98 all did
this informally).  Pattern: re-read → 类比 → 归纳
→ 顺序 → 整理 → 读 原则.

### Sub-step 4: 确认顺序 (confirm order)

**Action**: verify ordering of P-n (numerical),
M-n (numerical), R-n (numerical), and within-doc
段 (per 7-check step 3).

**Output**: verified ordering + identification of
disordered sections.

**Tools**: 7-check step 3 (ordering check).

**Worked example**: c99 confirmed M-n 14 (Track 1 +
Track 2) was correctly ordered before M-n 15
(post-chaos restoration).

### Sub-step 5: 整理 (reorganize)

**Action**: apply reorderings + renumberings +
cross-ref updates.

**Tools**: P11 摘要+引用, R6 _DETAIL inbound links,
P14 docs stay current.

**Output**: reorganized docs.

**Worked example**: c99 reorganized M-n 12 + M-n 13
+ M-n 14 in OPERATING_RULES.md to add M-n 15 + M-n
16段 in correct order.

### Sub-step 6: 读一遍原则确认无误 (re-read to verify)

**Action**: re-read all P-n/M-n/R-n + memory once
more, verify no further chaos, confirm order.

**Tools**: P25 6-step (post-modify check).

**Output**: verified state.

**Worked example**: c99 re-read M-n 12 + 13 + 14 + 15
+ 16 in OPERATING_RULES.md to verify no chaos, then
proceeded.

## How this M-rule relates to P25 6-step

Per P25 6-step:
1. Read first
2. Root axiom
3. No duplication
4. Draft 4 elements
5. Impact analysis
6. Commit with detailed trace
7. Post-modify re-apply new rules check

Per M-n 15 6 sub-steps:
1. 重读 (similar to P25 step 1)
2. 类比思考 (P25 doesn't have this)
3. 归纳总结 (P25 doesn't have this)
4. 确认顺序 (related to P25 step 3 + 7)
5. 整理 (P25 step 5)
6. 读一遍原则确认无误 (P25 step 7)

M-n 15 EXTENDS P25 with explicit 类比 (sub-step 2) +
归纳 (sub-step 3) + 确认顺序 (sub-step 4, more
explicit than P25).

## When to invoke (5 conditions, expanded)

1. **After any P-n modification**: per P25,
   principle modification requires this M-rule's
   6 sub-steps.
2. **After M-n codification**: per M_RULE_AUTHORING,
   new M-n may require reordering of existing
   M-rules.
3. **After parent verification**: per
   SUMMARY_LIFECYCLE, parent verify may surface
   principle disorders.
4. **When vision drift detected**: per P26, vision
   drift implies principle disorder.
5. **When chaos / disorder observed**: any visible
   disorder (numerical ordering, cross-refs broken,
   segment混乱).

## Worked example: c97 + c98 + c99 (recent M-n codifications)

These 3 commits demonstrate M-n 15 in action:

- c97 (M-n 13 codify): used M-n 15 sub-steps 1-6
  (re-read 类比 → 归纳 → 顺序 → 整理 → 读)
- c98 (M-n 14 codify): same
- c99 (M-n 15 codify itself): M-n 15 codify itself
  IS M-n 15 in action (recursion to self)

After c99, OPERATING_RULES.md has M-n 12 + 13 + 14 +
15 + 16 in numerical order, all cross-refs verified.

## When NOT to invoke (anti-patterns)

### Anti-pattern 1: Skip 重读 (start with 类比 or 归纳)

Without re-reading current state, the agent is
guessing.  Per P7 奥卡姆 + P5 verify, re-read is
mandatory.

### Anti-pattern 2: Skip 确认顺序

May miss numerical ordering issues, per 7-check step
3.

### Anti-pattern 3: Skip the final 读一遍原则确认无误

P25 step 7 post-modify check is critical.  Without
it, undiscovered chaos remains.

### Anti-pattern 4: Invoke for trivial tasks

For 1-line changes (low-risk per 修订 L4 boundary
(a)), M-n 15 6 sub-steps is over-engineering.  Use
when high-stakes (mid-risk or high-risk).

## Relationship to other M-rules + P-n

- **P25 6-step**: this M-rule extends P25 with
  explicit 类比 + 归纳 + 确认顺序.
- **M-n 11 (sub-project)**: this M-rule may apply
  within sub-project lifecycle.
- **M-n 12 (terminology-clarity)**: sub-step 5
  (整理) may rename unclear terms.
- **M-n 13 (layer-extension)**: sub-step 5 (整理)
  may add L0.5/L2.5/L3.
- **M-n 14 (two-track reasoning)**: sub-steps 2 +
  3 are 类比 + 归纳 (Track 1 + Track 2).
- **M-n 16 (observe-think-execute)**: M-n 15 is
  one application of M-n 16's 6-stage chain.
- **7-check**: sub-step 4 (确认顺序) maps to
  7-check step 3.

## Self-application (per P28 recursion)

This L2 doc IS M-n 15 applied to itself: M-n 15
sub-steps are used to write M-n 15's L2 detail.
Recursion depth = 2 (per M-n 12 boundary + memory 9).

## Cross-references

- `OPERATING_RULES.md` § M-principle-reordering —
  the L0/L1 段 (in SUA)
- `docs/PRINCIPLES.md` P25 — principle modification
  discipline
- `docs/OPERATING_RULES.md` § M-n 11/12/13/14/16
- user message 2026-07-15 — origin
