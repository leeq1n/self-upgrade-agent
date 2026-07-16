# PROJECT_TOPDOWN_AUDIT — Detail (L2)
Last P20-verified: 2026-07-14 (split from summary per R5+R6)

> L0: L2 detail for PROJECT_TOPDOWN_AUDIT.md summary.  Per
> P11 摘要+引用, the summary file is the L0/L1 layer
> (≤ 7KB); this file is the L2 layer (full detail).
> Per R6, this detail file is referenced from the summary.

This file holds the per-tier inventory tables, per-severity
findings (low/medium), 5-family framework, P26 simulation,
P25 6-step self-application, M-self-application 4-level,
50a-50e plan, and Risk register.  See
`PROJECT_TOPDOWN_AUDIT.md` for the summary.

---

## Doc inventory + audit

### Tier 1: Principle docs (just reorganized)

| Doc | L0 | L1 | R10 | Cap | Cross-ref | Class |
|---|---|---|---|---|---|---|
| PRINCIPLES.md | ✅ | ⚠️ partial | ✅ (2026-07-13) | ❌ 621 lines (300+ cap) | ✅ (bidirectional c46+c48) | L1: Doc axiom |
| PRINCIPLES_DETAIL.md | ✅ | ✅ | ✅ | ✅ 394 lines (slightly over 300) | ✅ (bidirectional) | L2: Doc axiom |
| PLAN_TOPDOWN_REORG.md | ✅ | ✅ | ✅ | ✅ 99 lines | ✅ (cites 4 docs) | L1: Workflow |
| MERGE_EVAL.md | ✅ | ✅ | ✅ | ❌ 293 lines (close to cap) | ✅ (cites family table) | L2: 奥卡姆 |
| SELF_AUDIT_P20.md | ✅ | ✅ | ✅ | ❌ 203 lines (close to cap) | ✅ (cites 4 docs) | L2: Doc |

### Tier 2: Workflow docs (M-rules + tasks)

| Doc | L0 | L1 | R10 | Cap | Cross-ref | Class |
|---|---|---|---|---|---|---|
| OPERATING_RULES.md | ✅ | ✅ | ✅ (2026-07-13) | ❌ 318 lines | ✅ | L1: Workflow |
| OPERATING_RULES_DETAIL.md | ✅ | ✅ | ✅ | ✅ 123 lines | ✅ (cited) | L2: Workflow |
| RECURSIVE_DECOMPOSITION.md | ✅ | ✅ | ✅ | ✅ 133 lines | ✅ | L1: Workflow |
| RECURSIVE_QUALITY.md | ✅ | ✅ | ✅ | ✅ 145 lines | ✅ | L1: Workflow |
| SWITCH_SIGNALS.md | ✅ | ✅ | ✅ (2026-07-14) | ✅ 138 lines | ✅ | L1: Workflow |
| COMMON_PITFALLS.md | ✅ | ✅ | ✅ | ✅ 122 lines | ✅ | L1: Doc |
| M_SELF_AUDIT.md | ✅ | ✅ | ✅ | ✅ 137 lines | ✅ | L1: Workflow |
| M_SELF_APPLICATION.md | ✅ | ✅ | ✅ | ✅ 101 lines | ✅ | L1: Workflow |
| MEMORY_TOOLS.md | ✅ | ✅ | ✅ | ✅ 108 lines | ✅ | L1: Doc |
| ADD_THEN_REDUCE.md | ✅ | ✅ | ✅ | ✅ 81 lines | ✅ | L1: Workflow |
| SUMMARY_LIFECYCLE.md | ✅ | ✅ | ✅ | ✅ 77 lines | ✅ | L1: Workflow |
| CONSTRAINTS.md | ✅ | ✅ | ✅ | ✅ ~100 lines | ✅ | L1: Doc |
| CONSTRAINTS_DETAIL.md | ✅ | ✅ | ✅ | ❌ 317 lines | ⚠️ partial | L2: Doc |
| EXTENSIONS.md | ✅ | ✅ | ✅ (2026-07-13) | ❌ 1727 bytes (R4 fail) | ✅ | L1: Doc |
| INDEX.md | ✅ | ✅ | ✅ | ✅ ~70 lines | ✅ | L0: Doc |
| TODO_SESSION_PERSISTENCE.md | ✅ | ✅ | ✅ | ❌ 174 lines (close) | ✅ | L1: Workflow |
| TODO_SESSION_PERSISTENCE_DETAIL.md | ✅ | ✅ | ✅ | ✅ 67 lines | ✅ | L2: Workflow |
| TODO_KNOWLEDGE_LIFECYCLE.md | ✅ | ✅ | ✅ | ❌ 160 lines (close) | ✅ | L1: Doc |
| TODO_KNOWLEDGEGRAPH.md | ✅ | ✅ | ✅ | ✅ 97 lines | ✅ | L1: Doc |

### Tier 3: Project state

| Doc | L0 | L1 | R10 | Cap | Cross-ref | Class |
|---|---|---|---|---|---|---|
| PROJECT_STATE.md | ✅ | ✅ | ✅ (2026-07-14) | ✅ 134 lines | ✅ | L1: Doc |
| PROJECT_STATE_DETAIL.md | ✅ | ✅ | ✅ | ✅ | ✅ | L2: Doc |
| LITERATURE.md | ✅ | ✅ | ✅ | ✅ | ✅ | L1: Doc |
| LITERATURE_DETAIL.md | ✅ | ✅ | ✅ | ❌ 349 lines | ✅ | L2: Doc |
| MODEL_STRATEGY.md | ✅ | ✅ | ✅ | ✅ | ✅ | L1: Doc |
| MODEL_STRATEGY_DETAIL.md | ✅ | ✅ | ✅ | ✅ | ✅ | L2: Doc |
| USER_INSIGHTS.md | ✅ | ✅ | ✅ | ✅ | ✅ | L1: Doc |
| USER_INSIGHTS_DETAIL.md | ✅ | ✅ | ✅ | ✅ | ✅ | L2: Doc |
| OBSERVATIONS.md | ✅ | ✅ | ✅ | ❌ 71 KB / 1882 lines (severe!) | ✅ | L2: Doc |
| OBSERVATIONS_DETAIL.md | ✅ | ✅ | ✅ | ❌ 1882 lines | ✅ (cited in OBSERVATIONS) | L2: Doc |
| DONE.md | ❌ missing L0 | ❌ | ✅ | ❌ 57 KB / 1515 lines (severe!) | ✅ | L2: Doc |
| TODO.md | ✅ | ✅ | ✅ | ❌ 335 lines | ✅ | L1: Doc |
| AGENTS.md | ✅ | ✅ | ✅ | ✅ 202 lines | ✅ | L0: Doc |


## Per 类比 framework (5 essence families for docs)

Per c44 family framework, docs can be grouped by
**operational essence**:

| Doc family | Examples | Essence |
|---|---|---|
| **Plan-then-act** (workflow) | OPERATING_RULES, RECURSIVE_DECOMPOSITION, SWITCH_SIGNALS, ADD_THEN_REDUCE, M_SELF_AUDIT, M_SELF_APPLICATION, SUMMARY_LIFECYCLE | "how to sequence work" |
| **Verify-don't-guess** (verification) | TODO_KNOWLEDGEGRAPH, OBSERVATIONS, TODO_SESSION_PERSISTENCE | "track what was done" |
| **Capture-in-writing** (documentation) | PRINCIPLES, PRINCIPLES_DETAIL, LITERATURE, MODEL_STRATEGY, USER_INSIGHTS, PROJECT_STATE, EXTENSIONS, CONSTRAINTS, INDEX, COMMON_PITFALLS | "what to write" |
| **Minimum-viable** (cleanup) | MERGE_EVAL, SELF_AUDIT, PLAN_TOPDOWN_REORG | "evaluate and reduce" |
| **Meta-rules** (about rules) | TODO_KNOWLEDGE_LIFECYCLE, TODO_SESSION_PERSISTENCE_DETAIL | "proposals + future plans" |

This 5-family grouping IS the 类比 framework
applied to **docs**, not just P-n.  Per P22
recursion: applying 类比 to docs IS applying P22
to docs.


## P26 fresh-agent simulation (post-audit)

| Discovery step | Pre-audit | Post-audit |
|---|---|---|
| Sees all docs in 1 place | ⚠️ must `ls` manually | ✅ inventory + audit table |
| Identifies severity of issues | ⚠️ invisible | ✅ 3 critical + 3 high + 5 medium |
| Knows which doc needs L0 | ⚠️ must check each | ✅ DONE.md critical |
| Knows which doc needs split | ⚠️ must check each | ✅ OBSERVATIONS, DONE, PRINCIPLES |
| Knows which doc has R4 conflict | ⚠️ hidden | ✅ EXTENSIONS (R4+R6) |

Fresh-agent simulation **PASS**.


## Per P25 6-step self-application

✅ Step 1 (Read first): all 30+ docs read via
   inventory + audit.
✅ Step 2 (Root axiom): Doc root axiom.
✅ Step 3 (No duplication): audit checks 7
   properties, no new content.
✅ Step 4 (Draft with 4 elements): trigger +
   action + anti-patterns + rationale all
   present.
✅ Step 5 (Impact analysis): 3 critical + 3 high
   + 5 medium findings.
✅ Step 6 (Commit with detailed trace): this
   audit file.
✅ Step 7 (Post-modify re-apply new rules check):
   simulation (above).


## Per M-self-application 4-level (post-batch reflection)

- **Level 1**: ✅ 1 file (this audit) + 1 commit.
- **Level 2 (rule itself)**: P20 + P22 + P25 step 7
  + P26 + P11 + P13 all applied to whole project.
- **Level 3 (memory / project structure)**: 30+ docs
  audited, 14 findings identified, 5 planned fixes
  (50a-50e).
- **Level 4 (own operating behavior)**: future doc
  audits should use this 7-check framework + 5-
  family grouping.


## Proposed 50a-50e plan

### 50a: DONE.md L0 line add + 50b: DONE_DETAIL split

DONE.md is 57 KB / 1515 lines, missing L0 line (R9
violation).  Action: add L0 + split to DONE_DETAIL
companion (per R5/R6 pattern, like OBSERVATIONS).

### 50c: PRINCIPLES.md L1 rewrite

Replace current L1 (intro) with explicit "when to
load this"段 + operational vs categorical framing
(cites c44 family table).

### 50d: PRINCIPLES.md + OPERATING_RULES.md split

PRINCIPLES.md 621 lines → split to PRINCIPLES_DETAIL
companion (likely just移 "P-n vs M-* boundary"段
+ "L2: 实操"段).

OPERATING_RULES.md 318 lines → evaluate split
(may not need; M-rule summaries are meant to be
terse).

### 50e: EXTENSIONS.md R4/R6 conflict resolution

Per P25 6-step procedure: extend boundary段 of
R4 (or document R4 exception in EXTENSIONS.md).
**Caution**: this is a R-n modification, requires
P25 6-step + P26 + user confirmation.


## Risk register

- **Risk 1**: 50a DONE_DETAIL split = ~1500 lines
  of historical commit data.  May be lossy if
  not careful.  **Mitigation**: preserve all
  data, just move it.
- **Risk 2**: 50c PRINCIPLES.md L1 rewrite could
  break P20 self-application claim.  **Mitigation**:
  ensure L1 is genuinely L0-summary level.
- **Risk 3**: 50e R-n modification = high impact
  (R4 affects EXTENSIONS.md contract).  **Mitigation**:
  per plan risk register, pause for user review
  before 50e.
