# GRAPH_TO_SKILL_DESIGN — Detail (L2)
Last P20-verified: 2026-07-14 (split from summary per R5+R6)

> L0: L2 detail for GRAPH_TO_SKILL_DESIGN.md.  Per P11 摘要+引用, the
> summary file is the L0/L1 layer (≤ 7KB); this file is
> the L2 layer (full detail).  Per R6, this detail file
> is referenced from the summary.

This file holds the L2 detail (per-principle analysis,
M-self-application, follow-ups, etc.).  See
`GRAPH_TO_SKILL_DESIGN.md` for the summary.

---

## Per P25 6-step self-application

### Step 1 (Read first) ✅

User 2026-07-14 message re-read.  c53 plan + c51
+ c52 commits re-read.  KG project SEED.md
re-read (different role, not converter).

### Step 2 (Root axiom) ✅

Doc + Workflow root axioms.  Converter is
Workflow (sequencing) + Doc (output format).

### Step 3 (No duplication) ✅

- **No new P-n** (per P7 奥卡姆)
- **c51 (MCP_TOOLS.md)** stays in SUA (graph view)
- **c52 (SELF_ORG.md + P27 candidate)** stays in SUA
  (P27 lives in PRINCIPLES.md)
- **c53 (KNOWLEDGE_ORG.md)** stays — it codifies the
  2-view model (graph + flat) which is correct
  architecturally; this commit refines the
  **implementation** (converter, not separate
  project)

### Step 4 (Draft with 4 elements) ✅

- **Trigger**: user insight "我需要一个转换工具"
- **Action**: design doc + revised plan
- **Anti-patterns**: 4 (manual sync / 2 sources of
  truth / drift / per-project rewrite)
- **Rationale**: explicit user insight + P7 + P11
  + P13 + 8-rule table

### Step 5 (Impact analysis) ✅

Cross-refs to update:
- GRAPH_TO_SKILL_DESIGN.md: new file ✅
- PLAN_TOPDOWN_REORG.md: revised task table +
  removed obsolete commits 54-57 (c53 plan),
  added new commits 55-58 (revised plan)
- KNOWLEDGE_ORG.md (c53): no change (architecture
  correct, implementation refined)
- MCP_TOOLS.md (c51): no change (graph view)
- SELF_ORG.md (c52): no change (P27 candidate)
- EXTENSIONS.md: NOT yet (commit 57 in revised plan)

Minimal impact: 1 new file + 1 file updated.

### Step 6 (Commit with detailed trace) ✅

This commit message body.

### Step 7 (Post-modify re-apply new rules check) ✅

P26 simulation below.


## Per P26 fresh-agent simulation (post-design doc)

| Discovery step | Pre-design | Post-design |
|---|---|---|
| Knows architecture (graph + flat) | ✅ (c53) | ✅ (c53) |
| Knows implementation (converter, not 2 project) | ❌ (c53 manual) | ✅ (this commit) |
| Knows converter input/output | ❌ | ✅ explicit |
| Knows CLI invocation | ❌ | ✅ example command |
| Knows obsolete commits | ❌ (still in plan) | ✅ (revised plan) |
| Can export skill on-demand | ❌ (manual) | ✅ (one command) |

Fresh-agent simulation **PASS**.


## Per task-planning-order meta-rule

Per user "如果发现任务对其他任务可能有影响，就重新
计划整理一下" (2026-07-14 follow-up): this commit
IS a plan revision.  c53 plan had manual 2-project
architecture; revised plan has graph + converter.

| Sub-task | Depends on | Output informs |
|---|---|---|
| a. Parse user insight | user message | (b) |
| b. Apply 原则 to evaluate options | (a) + P7/P11/P13 | (c) |
| c. Choose graph + converter over 2-project | (b) | (d) |
| d. Write design doc | (c) | (e) |
| e. Revise plan file (c53 obsolete) | (d) | (commit) |
| f. P26 simulation | (e) | (commit body) |

(a) insight informs (b) option analysis.  (b) P7 +
P11 + P13 evaluate (c) decision.


## Per P17 honest reporting

- **c53 plan superseded**: manual 2-project
  architecture is replaced by graph + converter.
  Per P14 docs current + P17 honest: acknowledge
  the previous plan is now obsolete.
- **c51 + c52 + c53 are still valid** (graph view
  in SUA is correct; only implementation is
  refined).
- **KG project** (sibling) has different role
  (knowledge graph for answering 3 acceptance
  questions, per SEED.md).  NOT the converter
  (this is a separate tool, in SUA).
- **Converter is in SUA**, not in KG project (per
  P21 cross-project + P11 摘要+引用).


## See also

- `docs/KNOWLEDGE_ORG.md` (c53, 2-view model —
  architecture correct, implementation refined)
- `docs/MCP_TOOLS.md` (c51, graph view in SUA)
- `docs/SELF_ORG.md` (c52, P27 candidate)
- `docs/PLAN_TOPDOWN_REORG.md` (revised plan)
- `../knowledge-graph-seed/SEED.md` (sibling KG
  project, different role)