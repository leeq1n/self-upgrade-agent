# PLAN_TOPDOWN_REORG — Detail (L2)
Last P20-verified: 2026-07-14 (split from summary per R5+R6)

> L0: L2 detail for PLAN_TOPDOWN_REORG.md.  Per P11 摘要+引用, the
> summary file is the L0/L1 layer (≤ 7KB); this file is
> the L2 layer (full detail).  Per R6, this detail file
> is referenced from the summary.

This file holds the L2 detail (per-principle analysis,
M-self-application, follow-ups, etc.).  See
`PLAN_TOPDOWN_REORG.md` for the summary.

---

## Insights foundation (per user meta-critique, 2026-07-14)

1. **递进 relation**: "共性归纳" 是 "渐进式披露/分治" 的 子集
2. **类比 = 分治 mechanism**: 本质相近放一起 = 分治运用方式
3. **自顶向下**: 原则和项目 都应是 top-down
4. **整理 = 类比联想 + 归纳 + 排序**: 3-step sequence
5. **奥卡姆 罪魁祸首**: 26 P-n 太多 + 混乱 → 违反 P7
6. **(NEW 2026-07-14) 新agent 不依赖 hermes 也能学**: MCP
   tools, workflow patterns, project conventions should
   be in project docs, not just hermes runtime


## Per-insight derived tasks (updated per commit 51+)

| Insight | Task | Commit | Status |
|---|---|---|---|
| 自顶向下 | PRINCIPLES.md reorg | 45 | ✅ done |
| 类比 mechanism | PRINCIPLES_DETAIL.md cross-ref | 46 | ✅ done |
| 奥卡姆 | P-n merge eval (P5+P6, P3+P24) | 47 | ✅ done (proposal, 47a-d pending user) |
| 渐进式披露 self-app | Self-audit | 48 | ✅ done |
| 任务规划顺序 | Parent verification | 49 | ✅ done |
| Recursive 类比 to whole project | Project-level audit | 50 | ✅ done |
| **(NEW) 新agent hermes-independent** | **MCP tools L0 doc** | **51** | **✅ done (graph view in SUA)** |
| **(NEW) 项目 self-organization 自动化** | **SELF_ORG principle (P27 candidate)** | **52** | **✅ done (P27 lives in PRINCIPLES.md)** |
| **(NEW) 知识组织 architecture** | **图/树 + 平铺式 model** | **53** | **✅ done** |
| **(NEW) Converter design (premature)** | **graph + converter (premature)** | **54** | **✅ done (superseded)** |
| **(NEW) Honest re-analysis** | **5 options + A recommended** | **55** | **✅ done (superseded)** |
| **(NEW) Reflection + decision (Option E)** | **6 options + 6 principles + Option E wins** | **56** | **✅ done** |
| **(NEW) Read pattern doc (Option E)** | **`docs/HOW_TO_READ_GRAPH.md`** | **57** | **⏳ next (this commit)** |
| **(NEW) AGENTS.md link** | **Add HOW_TO_READ_GRAPH.md to "Read first"** | 58 | ⏳ after 57 |
| **(NEW) Parent verification** | **SUMMARY_LIFECYCLE for batch 51-57** | 59 | ⏳ after 58 |
| 50a-50e (DONE/PRINCIPLES cap fixes) | Doc fixes (per c50 audit) | 50a-50e | ⏳ pending user |
| 47a-d (P-n merge) | Apply 4 merge candidates | 47a-d | ⏳ pending user |


## Per-insight derived tasks (commits 45-50, completed)

| Insight | Task | Commit | Status |
|---|---|---|---|
| 自顶向下 | PRINCIPLES.md reorg | 45 | ✅ done |
| 类比 mechanism | PRINCIPLES_DETAIL.md cross-ref | 46 | ✅ done |
| 奥卡姆 | P-n merge eval | 47 | ✅ done (proposal) |
| 渐进式披露 self-app | Self-audit | 48 | ✅ done |
| 任务规划顺序 | Parent verification | 49 | ✅ done |
| Recursive 类比 | Project-level audit | 50 | ✅ done |


## Per task-planning-order meta-rule

Per user "如果发现任务对其他任务可能有影响，就重新
计划整理一下" (2026-07-14 follow-up): the addition
of commits 51-53 is a **plan iteration** triggered
by the discovery that MCP tools knowledge is
**hermes-runtime-only**, affecting:
- All future agent behavior (can't discover tools)
- All future commits (agent uses tools)

This is a "task affects other tasks" trigger per
your meta-rule, hence plan iteration.


## Per P25 step 7 self-application

Each commit (51-53) will:
- Re-apply class framework (5-family)
- Apply P20 progressive disclosure to new docs
- Apply P26 fresh-agent simulation
- Apply P11 + P13 cross-ref + no orphan


## Per P7 奥卡姆 — task scope caution

- Don't add unnecessary structure
- 1 commit = 1 logical feature
- Don't merge 51-53 with 50a-50e (different scope)
- Don't create tools L0 doc that duplicates
  hermes-runtime knowledge


## Risk register

- **Risk 1**: MCP tools list may go stale as
  hermes evolves.  **Mitigation**: tools list
  documents "as of 2026-07-14" + Last P20-verified
  marker.
- **Risk 2**: Workflow patterns L0 doc may overlap
  with OPERATING_RULES.md.  **Mitigation**: per
  P11 摘要+引用, L0 doc points to OPERATING_RULES
  for full detail.
- **Risk 3**: AGENTS.md update (53) may break
  existing "Read first" list.  **Mitigation**:
  add new docs as "Read conditionally" not in
  default "Read first" (per R3 conditional loads).


## See also

- commit 44 (insight foundation)
- commit 50 (project-level audit, found MCP gap)
- docs/PRINCIPLES.md class framework (5 families)
- docs/PRINCIPLES_DETAIL.md synthesis (cross-ref)