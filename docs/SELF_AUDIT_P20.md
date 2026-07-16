# Self-audit: do principle docs self-exemplify P20 progressive disclosure?

> L0: Self-audit per plan `docs/PLAN_TOPDOWN_REORG.md`
> commit 48.  Applies P20 progressive disclosure to
> PRINCIPLES.md + PRINCIPLES_DETAIL.md and checks if
> the docs themselves follow what they preach.
> Last P20-verified: 2026-07-14

## What is P20 progressive disclosure?

Per `docs/PRINCIPLES_DETAIL.md` P20段: "Documents
should expose content in layers, each layer
addressing a different consumer question."

Three layers per P20:
- **L0 — Pointer** (1-line header): "Where do I look?"
- **L1 — Summary** (1-3 paragraphs): "What is this in 30 seconds?"
- **L2 — Detail** (rest): "Give me the full story"





## Self-audit verdict

**Overall**: principle docs **mostly** self-exemplify
P20 (7 of 10 checks pass or are partial).  The
**1 critical gap** (reverse cross-ref) is fixed in
this commit.  **3 partial gaps** (L1 clarity)
deferred to follow-up.


## Per M-self-application 4-level

- **Level 1**: ✅ 1 file (this audit doc) + 1
  PRINCIPLES.md cross-ref addition.
- **Level 2 (rule itself)**: P20 self-application
  applied to the docs that define P20.
- **Level 3 (memory / project structure)**:
  PRINCIPLES.md ↔ PRINCIPLES_DETAIL.md now has
  bidirectional L0 cross-refs.
- **Level 4 (own operating behavior)**: future
  principle doc edits should preserve
  bidirectional cross-ref + L0/L1/L2 structure.

## Detail (L2)

For per-principle analysis, M-self-application, follow-ups, and other L2 detail, see [`SELF_AUDIT_P20_DETAIL.md`](SELF_AUDIT_P20_DETAIL.md).  Per R6, this companion is required for files > 7KB.
