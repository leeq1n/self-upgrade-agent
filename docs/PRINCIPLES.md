---
description: "Working principles distilled from this project — portable across projects"
status: "summary"
---

# PRINCIPLES — Working principles (portable)
> L0: The 24 working principles (P1-P27 minus P6 + P15 + P24, merged into P5 + P3 per c47a+c78+c79) of this project; P1-P21 in PRINCIPLES_DETAIL.md, P20+P21 + meta-rule pointers (P22, P23) here, P25 + P26 + P27 (also meta-rules) here.
> See `docs/PRINCIPLES_DETAIL.md` "Root axioms"段 (L0 categorical synthesis) + "Cross-reference to PRINCIPLES.md 类比联想段" (L1 operational mirror) for bidirectional context.
Last P20-verified: 2026-07-14

> Distilled from working on this project (2026-07-08 session).
> These are project-agnostic — copy them to any future project.
> Each rule has a 1-line WHY and a HOW.

## L0: Root principles (the 4 axioms)

Every P-n in L1 is a child of one of these 4 root axioms.  When
a new principle seems needed, it must (a) descend from a root
axiom, (b) not duplicate an existing L1 principle, (c) clear
P7 奥卡姆 — earn its place.

| # | Root axiom | L1 children | WHY |
|---|---|---|---|
| 奥卡姆 | P7, P9, P13, P23 | Minimum API, no rule until 3+ failures, no orphan nodes, doc > script (with nuance) |
| Workflow | P1, P2, P4, P5, P22, P23 | 整理→思考→行动, plan, test pyramid, 1 commit = 1 feature, verify (P5 merged with P6 + P15 per c77a+c79), meta-rules |
| Test | P3, P5, P16, P18, P19 | Unit → joint → integration, verify before commit (P5 merged with P6), ad-hoc verify, failure → regression test, data-flow observability |
| Doc | P10, P11, P12, P14, P17, P20, P21 | Entity > prompt, 摘要+引用, knowledge in project, docs stay current, honest reporting, progressive disclosure, cross-project boundaries |

**P27 (project self-organization)** spans **all 4 root axioms**
(meta-meta principle per c52 SELF_ORG.md case-3 boundary
test: "principle about principles").  It is the *operating*
form of these axioms — the axioms as observed from the
project's own behavior rather than the project's behavior
as observed from the axioms.

### 类比联想 (analogy map — the 4 root essences)

Per user audit 2026-07-14 ("原则中有共性的是否汇总到一起"
+ "本质相近/能够联想的内容放在一起，这就是分治
思想运用的方式"), the 4 root axioms above are
**abstract categories** — but the actual 26 P-n can
also be re-grouped by **essence (类比)** into 4-5
operational families.  This is **分治 applied to
P-n itself**: principles that share an operational
essence belong together.

**Essence families** (类比 grouping, NOT a renaming
of the 4 axioms — these are operational, the 4
axioms are categorical):

| Essence family | P-n | Operational commonalities (类比) |
|---|---|---|
| **Plan-then-act** (sequence + organization) | P1, P2, P4, P22 | All about "step before step".  Organize workspace (P1), search before designing (P2), 1 commit per feature (P4), plan when stuck (P22).  (P15 stage-gate demoted to P5 实操 per c79.)  Essence: **don't leapfrog steps**. |
| **Verify-don't-guess** (truth by structure) | P3, P5, P16, P18, P19 | All about "verify by structure, not by assumption".  Test pyramid (P3, merged with P24 per c78), verify before commit (P5, merged with P6 per c47a), ad-hoc verify when uncertain (P16), failure → regression (P18), intermediate state observable (P19).  Essence: **make the unseen testable**. |
| **Capture-in-writing** (docs as truth) | P10, P11, P12, P14, P17, P20, P21 | All about "if it isn't written, it isn't true".  Code over prompt (P10), 摘要+引用 (P11), knowledge in project not memory (P12), docs stay current (P14), honest reporting (P17), progressive disclosure (P20), cross-project boundaries (P21).  Essence: **commit to the record**. |
| **Minimum-viable** (奥卡姆 + structure) | P7, P8, P9, P13 | All about "don't over-build, but make structure clear".  奥卡姆 (P7), fail-open (P8), hard rules not LLM-judged (P9), no orphan nodes (P13).  Essence: **minimum + intentional structure**. |
| **Meta-rules** (how to reason about rules) | P22, P23, P25, P26, P27 | All about "how to think about the other P-n".  Stuck→plan (P22), doc>script (P23), principle modification discipline (P25), user-acceptance fresh-agent check (P26), project self-organization (P27).  Essence: **process for the process itself**. |

**Why 5 families not 4**: the 4 root axioms are
**categorical** (Test/Doc/Workflow/奥卡姆 as abstract
labels).  The 5 essence families are **operational**
(what does the agent actually do?).  Some P-n
(straddle multiple categories) — that's why we need
both views.  Per P20 progressive disclosure: **L0
axiom table is the categorical L0**, this段 is the
**operational L1**.

**类比 / analogy mechanism**: per user audit "本质
相近/能够联想的内容（这就是类比）放在一起，这
就是分治思想运用的方式" — grouping by essence IS
applying 分治思想 to P-n itself.  The families above
are the **top-level splits** (分); each family IS a
**sub-system** that can be reasoned about independently.

**Top-down reading order** (per user "原则和项目
都应该自顶向下"):

```
L0 axioms (4 categorical) — line 14
↓
L1 essence families (5 operational) — this段
↓
L1 specific P-n sections — line 82 onwards
↓
P-n vs M-* boundary — line 443
↓
L2 实操 — line 541
```

Fresh agents read **L0 → essence → specific P-n**,
not "20 random P-n in numerical order".  This is
P20 progressive disclosure applied to PRINCIPLES.md
itself.

**奥卡姆 implication**: per user "细节可能你还要
补全一部分" + "条数多而且混乱，不符合奥卡姆" —
some P-n were redundant.
Per c44 audit + c47 MERGE_EVAL: P5+P6 merged into
单一 P5 (per c47a, 2026-07-14).  Future batches
继续 evaluate per P7:
奥卡姆 whether to **merge** overlapping P-n.  This
commit establishes the **analogy framework** for
that evaluation.

---

When updating this doc, **check which root axiom** the change
descends from.  Per P22 步骤 3: 找 rule 之间的共性.

## References



- INDEX: [INDEX.md](INDEX.md)
- Project state: [PROJECT_STATE.md](PROJECT_STATE.md)
- User intent: [USER_INSIGHTS.md](USER_INSIGHTS.md)
- Constraints: [CONSTRAINTS.md](CONSTRAINTS.md)
- LLM choice: [MODEL_STRATEGY.md](MODEL_STRATEGY.md)
- Literature: [LITERATURE.md](LITERATURE.md)
- Pending tasks: [../../TODO.md](../../TODO.md)

## Detail (L2)

For per-P-n full text (P19, P20, P20细则, P21, P25, P26, P27), P-n vs M-* boundary段, and L2 实操段, see [`PRINCIPLES_FULL.md`](PRINCIPLES_FULL.md).  (P24 merged into P3 per c78; P24段 removed from PRINCIPLES_FULL.md.)  Per R6, this companion is required for files > 7KB.
