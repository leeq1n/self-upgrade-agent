L0: Per-P-n 实操 (L2 details) — how to actually follow each principle.  Main file is PRINCIPLES.md (L0+L1).
Last P20-verified: 2026-07-13

# PRINCIPLES_DETAIL — per-P-n 实操 (L2)
> L0: Full text of P1-P26 principles (P1-P21 + P22/P23 + P24-P26 cross-refs).  Companion to PRINCIPLES.md.  Load when: need rationale.

This file holds the L2 实操 details for each P-n principle.  The main
`docs/PRINCIPLES.md` holds L0 (4 root axioms) + L1 (the 23 principles).
Read main first; read this when you need to know "how to actually
follow" a specific principle.

Per P20 progressive disclosure: L1 in main, L2 in this detail file.
Per P11 摘要+引用: main = summary, detail = reference.

---

## L2: 实操 (per P-n, how to implement)

Each L1 principle (P-n) has a 1-line "实操" — how to actually
follow the principle.  The实操 references its root axiom (L0)
and any sibling L1 principles.  Per P7 奥卡姆: keep short.

### Root axioms (the 4 categories — 共性归纳)

Per P20 progressive disclosure, this section is the **L0
synthesis** of PRINCIPLES_DETAIL.md — applied to the
file itself, not just to other docs.  Per P22 step 3
("找 rule 之间的共性"), this section explicitly synthesizes
the 20 P-n principles below into 4 root axiom groups:

| # | Root axiom | P-n children | Common pattern (the 共性) |
|---|---|---|---|
| 奥卡姆 | P7, P9, P13, P23 | "Don't add what's not earned" — minimum API, hard rules over LLM-judged, no orphans, doc > script. |
| Workflow | P1, P2, P4, P5, P6, P15, P22, P23 | "Sequence matters" — organize, search, 1 commit = 1 feature, test pyramid, stage gate, plan-then-act, meta-rules. |
| Test | P3, P5, P6, P16, P18, P19 | "Verify, don't assume" — pyramid testing, real runs, ad-hoc verify, regression tests, intermediate-state observability. |
| Doc | P10, P11, P12, P14, P17, P20, P21 | "Capture in writing" — code over prompt, 摘要+引用, knowledge in files, docs stay current, honest reporting, progressive disclosure, cross-project boundaries. |

**Cross-cutting patterns (P-n that span multiple axioms)**:

- **P5, P6** span Workflow + Test (both about "verify
  before commit")
- **P22, P23** are **meta-rules** that span all 4
  axioms (they describe how to reason about the
  other P-n, not what to do directly)
- **P11, P14, P20** are **Doc-axis meta-tools** that
  operationalize progressive disclosure

**Inductive summary (for fresh agents)**:

When asked "is this principle aligned with the
project's 哲学?", check:
1. Does it descend from one of the 4 root axioms?
   (奥卡姆 / Workflow / Test / Doc)
2. Is the proposed P-n already covered by an
   existing P-n? (per P7 奥卡姆 — earn the place)
3. Does it cross-reference related P-n rather than
   redefine? (per P22 step 3 — find commonalities)

**Why this section exists** (per user audit 2026-07-14,
commit 43): "原则中有共性的是否汇总到一起？读了
这项目的 agent 有归纳总结的能力吗".  Without this
synthesis, fresh agents read 20 sequential P-n without
seeing the 4 root categories that bind them.  P22 step 3
already calls for "find commonalities" but PRINCIPLES_DETAIL.md
didn't actually do this synthesis.  This section fixes
that gap (per P25 step 7 post-modify re-apply check).

Per P20 progressive disclosure: this is the **L0 layer**
of PRINCIPLES_DETAIL.md — read this first, then jump to
specific P-n sections as needed.

**Cross-reference to PRINCIPLES.md 类比联想段** (per
commit 46, 2026-07-14):  PRINCIPLES.md has a **5
essence families** table (operational grouping, distinct
from the 4 categorical root axioms above).  The 5
essence families are:

| Family (operational) | P-n | Maps to root axiom(s) above |
|---|---|---|
| Plan-then-act | P1, P2, P4, P15, P22 | Workflow |
| Verify-don't-guess | P3, P5, P6, P16, P18, P19, P24 | Workflow + Test (P5/P6 dual) |
| Capture-in-writing | P10, P11, P12, P14, P17, P20, P21 | Doc |
| Minimum-viable | P7, P8, P9, P13 | 奥卡姆 |
| Meta-rules | P22, P23, P25, P26 | spans all 4 |

The 4 root axioms (this段) are **categorical** — they
answer "what abstract category does this P-n descend
from?".  The 5 essence families (PRINCIPLES.md) are
**operational** — they answer "what does the agent
actually do when following this P-n?".  Both views are
needed (per P20 progressive disclosure: categorical
L0 + operational L1).  See PRINCIPLES.md 类比联想段
for the operational details and per-family rationale.

**Difference vs P-n placement**: P24 (Sequential chain
test) is **in the 5 essence families** but **NOT in the
4 root axiom table above** — this is because P24 is
**operational** (when to write a chain test) more than
**categorical** (which axiom it descends from — could
be Test or Workflow).  Per c44 奥卡姆 implication段:
P24 may be a candidate for merge with P3 (test pyramid)
in commit 47+ evaluation.

## Detail (L2)

For per-P-n full text (P1-P18 + P22, P23), see [`PRINCIPLES_DETAIL_DETAIL.md`](PRINCIPLES_DETAIL_DETAIL.md).  Per R6, this companion is required for files > 7KB.
