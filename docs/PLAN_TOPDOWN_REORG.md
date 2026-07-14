# Plan: Top-down reorganization + 类比 framework application (commits 45+)

> L0: Roadmap derived from user meta-critique 2026-07-14
> ("递进 + 类比 + 自顶向下 + 奥卡姆").  Per P22 stuck→plan
> + user "规划后续任务，规划顺序，然后推进".
> Last P20-verified: 2026-07-14 (extended with commit 51-53
> per user meta-rule "新agent 不依赖hermes也能学到知识")

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
| **(NEW) 知识组织 architecture** | **图/树 + 平铺式 model** | **53** | **⏳ next** |
| **(NEW) skill-v2 项目 skeleton** | **Create `hermes-root/agent-onboarding-v2/`** | **54** | ⏳ after 53 |
| **(NEW) skill-v2 initial content** | **SKILL.md + references/** | 55 | ⏳ after 54 |
| **(NEW) EXTENSIONS.md X2 update** | **X2 = skill-v2 (in hermes-root, not Hermes global)** | 56 | ⏳ after 55 |
| **(NEW) SUA → skill cross-ref** | **SUA docs link to skill references** | 57 | ⏳ after 56 |
| 50a-50e (DONE/PRINCIPLES cap fixes) | Doc fixes (per c50 audit) | 50a-50e | ⏳ pending user |
| 47a-d (P-n merge) | Apply 4 merge candidates | 47a-d | ⏳ pending user |

## 2-project architecture (per user clarification 2026-07-14)

**SUA (this project)** = knowledge graph view
- P1-P27 principles
- M-* rules
- R1-R12 invariants
- MCP tools
- Plan files
- Audit results
- Cross-references

**agent-onboarding-v2 (NEW, in hermes-root)** = flat context view
- SKILL.md entry point
- references/ (sequential, L0/L1/L2)
- Self-contained reading
- Reusable across projects

Per P21 cross-project: SUA + skill-v2 linked via
EXTENSIONS.md (X1 = KG, X2 = skill-v2).

## New task sequence (commits 51-53) per user meta-rule

```
51 (MCP tools L0 doc) ← independent
  ↓
52 (Workflow patterns L0 doc) ← depends on 51 (same L0 doc pattern)
  ↓
53 (AGENTS.md update) ← depends on 51 + 52 (cross-ref integration)
  ↓
54 (parent verification for batch 51-53) ← SUMMARY_LIFECYCLE
```

**Why this matters** (per user "新agent 不依赖hermes
也能学到知识"): currently MCP tools + workflow patterns
are **hermes-runtime-only knowledge** — they live in
the agent's runtime context, not in the project.  A
fresh agent that joins the project without hermes
context (rare but possible) cannot discover these.
After commits 51-53, these are in `docs/` and
discoverable via `AGENTS.md` "Read first".

## Why not execute 50a-50e first?

Per user meta-rule "新agent 不依赖hermes": MCP tools
gap is **highest leverage** because:
- 50a-50e: fix internal doc structure (DONE, PRINCIPLES
  cap violations) — affects existing readers
- 51-53: add hermes-independent knowledge — affects
  future readers (including new agents)

Per P7 奥卡姆 + "选哪个最优": 51-53 enables future
work to be hermes-independent.  50a-50e is maintenance
of existing structure.  51-53 has higher forward
value.

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