# M-layer-extension (full text)
Last P20-verified: 2026-07-15

> L0: L2 detail for `OPERATING_RULES.md` § M-layer-
> extension段.  Per P11 摘要+引用 + R6, this
> companion is required when the summary rule段 is
> detailed enough to warrant L2 expansion.  Load
> when: agent considers adding a new layer beyond
> fixed L0/L1/L2.

## Why this L2 doc exists

The OPERATING_RULES.md § M-layer-extension 段
(codified per c97, 2026-07-15) provides the 4-step
action.  This L2 doc provides worked examples,
decision tree, and naming conventions.

## When to add a layer (decision tree)

```
Q1: Is the L0/L1/L2 fixed structure insufficient?
├── Yes → Q2
└── No → Don't add layer; refine existing (P7 奥卡姆)

Q2: Is the need recurring (3+ times)?
├── Yes → Q3
└── No → Maybe document ad-hoc (record, don't codify)

Q3: Is the new layer needed in 1+ project?
├── Yes → Q4 (which layer?)
└── No → Don't codify

Q4: Which layer to add?
├── L0.5 (between L0 and L1): meta-info stamps
│   (e.g., Last P20-verified)
├── L2.5 (between L2 and full): worked examples
│   (e.g., _DETAIL companion content)
└── L3 (beyond L2): full reference (e.g., glossary)
```

## Naming convention (per M-n 12)

When adding a new layer:

1. **Pick decimal notation**: L0.5, L2.5 (not "L0.5
   - Meta-info" — too verbose)
2. **Self-describing**: the name should hint at its
   role (e.g., L2.5 = between L2 and L3)
3. **Consistent**: if multiple layers, use L<n>.<m>
   notation
4. **Document the layer**: add 1 段 explaining the
   layer's purpose

## Worked examples (4 cases, per OPERATING_RULES 段)

### Case 1: L0.5 = Last P20-verified stamp

**When needed**: when L0 summary alone is not enough
to communicate doc freshness.

**Implementation**: append "Last P20-verified: YYYY-
MM-DD" after the L0 line.

**Self-application**: this is applied to every doc
header in SUA (PRINCIPLES.md, PRINCIPLES_FULL.md,
PRINCIPLES_DETAIL.md, OPERATING_RULES.md, HANDOFF.md,
HANDOFF_DETAIL.md, SKILL_DESIGN.md, etc.).

**Trade-offs**:
- Pro: lightweight stamp, useful for fresh-agent
  simulation (P26)
- Con: requires discipline (must update on every
  change)

### Case 2: L2.5 = _DETAIL companion

**When needed**: when L2 detail in summary doc
exceeds 7KB R5 cap.

**Implementation**: split content into summary (L1
≤ 7KB) + _DETAIL companion (L2.5, no R5 cap).  Per
R6, summary must reference _DETAIL.

**Self-application**: applied to M_SELF_AUDIT.md (c18
→ _DETAIL), M_SELF_APPLICATION.md, M_TERMINOLOGY_CLARITY.md
(c93 → _DETAIL), M_TERMINOLOGY_CLARITY_DETAIL.md,
M_EXPERIMENT_IN_SUBPROJECT_DETAIL.md (c90), etc.

**Trade-offs**:
- Pro: keeps summary readable while preserving
  detail
- Con: cross-ref complexity (must link summary → _DETAIL)

### Case 3: L3 = full worked examples

**When needed**: when L2 detail doesn't have enough
space for full examples.

**Implementation**: full examples doc (per primitive)
or per topic.

**Self-application**: M_TERMINOLOGY_CLARITY_DETAIL.md
(3 worked examples: "撞到一起", "vision",
"agent behavior rules").

**Trade-offs**:
- Pro: enables P26 fresh-agent simulation
- Con: more docs to maintain

### Case 4: "## Detail (L2)"段 in summary

**When needed**: when the summary doc itself has a
"## Detail (L2)"段 that explains what content is
in the _DETAIL companion.

**Implementation**: brief 段 (3-5 lines) at the end
of summary doc, with link to _DETAIL companion.

**Self-application**: M_TERMINOLOGY_CLARITY.md c93
段 ("## Detail (L2)" with reference to _DETAIL).

**Trade-offs**:
- Pro: helps reader navigate
- Con: 1 more 段 per doc

## When NOT to add a layer (anti-patterns, expanded)

### Anti-pattern 1: Add layer to fix unclear L0/L1/L2

If the existing L0/L1/L2 is unclear, **refine** it
(per P7 奥卡姆 + M-n 12 terminology-clarity).  Don't
add a layer to work around unclear content.

### Anti-pattern 2: Add layer ad-hoc without naming

If you must add a layer, **name it first** (per M-n
12).  Unnamed layers cause confusion.

### Anti-pattern 3: Add layer for every project

Not every project needs additional layers.  Per M_RULE_AUTHORING
3-condition gate: requires 3+ observed needs.

### Anti-pattern 4: Add layer without verify

Per sub-step 4 (Verify): re-read after adding.  If
violation of P11 (e.g., L0 > 120 chars), fix before
proceeding.

## Relationship to other M-rules + P-n

- **P11 摘要+引用**: fixed L0/L1/L2 structure
- **P20 progressive disclosure**: progressive layers
  enabled
- **M-n 12 (terminology-clarity)**: applies to layer
  naming
- **M-n 13 (layer-extension)** [parent 段]: this L2
  companion
- **M-n 14 (two-track reasoning)**: deciding layer
  extension uses both tracks
- **M-n 15 (principle-reordering)**: may involve
  layer addition in step 5 (整理)
- **M-n 16 (observe-think-execute)**: layer
  extension is in step 6 (修改、运行代码)
- **7-check step 5 (cap check)**: R5 + R8 check
  applies to all layers
- **R6 (_DETAIL inbound links)**: mandatory for L2.5

## Cross-references

- `OPERATING_RULES.md` § M-layer-extension — the
  L0/L1 段 (in SUA)
- `docs/P11.md` (if exists) — P11 摘要+引用
- `docs/P20.md` (if exists) — P20 progressive
  disclosure
- `docs/OPERATING_RULES.md` § M-n 12 — terminology
  (applies to layer naming)
- `docs/OPERATING_RULES.md` § M-n 14 — two-track
  reasoning
- user message 2026-07-15 — origin
