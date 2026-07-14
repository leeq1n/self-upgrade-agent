# Plan: Top-down reorganization + 类比 framework application (commits 45+)

> L0: Roadmap derived from user meta-critique 2026-07-14
> ("递进 + 类比 + 自顶向下 + 奥卡姆").  Per P22 stuck→plan
> + user "规划后续任务，规划顺序，然后推进".
> Last P20-verified: 2026-07-14

## Insights foundation (per user meta-critique, 2026-07-14)

1. **递进 relation**: "共性归纳" 是 "渐进式披露/分治" 的 子集
2. **类比 = 分治 mechanism**: 本质相近放一起 = 分治运用方式
3. **自顶向下**: 原则和项目 都应是 top-down
4. **整理 = 类比联想 + 归纳 + 排序**: 3-step sequence
5. **奥卡姆 罪魁祸首**: 26 P-n 太多 + 混乱 → 违反 P7

## Per-insight derived tasks

| Insight | Task | Commit | Priority |
|---|---|---|---|
| 自顶向下 | PRINCIPLES.md full section reorg | 45 | high |
| 类比 mechanism | PRINCIPLES_DETAIL.md cross-ref to family table | 46 | high |
| 奥卡姆 | P-n merge eval (P5+P6, P3+P24) | 47 | medium (needs user confirm) |
| 渐进式披露 self-app | Self-audit: do principle docs self-exemplify P20? | 48 | medium |
| 任务规划顺序 | Parent verification for batch 42-48 | 49 | required by SUMMARY_LIFECYCLE |
| Recursive 类比 to whole project | Apply 类比 + 自顶向下 to whole project | 50 | medium (big scope) |

## Task execution order (dependency graph)

```
45 (PRINCIPLES.md reorg) ← independent
  ↓
46 (PRINCIPLES_DETAIL cross-ref) ← depends on 45 (same family framework)
  ↓
47 (P-n merge eval) ← depends on 46 (need full picture)
  ↓
48 (self-audit) ← depends on 47 (post-merge state)
  ↓
49 (parent verification) ← depends on 48 (consume child summaries)
  ↓
50 (project-level audit) ← depends on 49 (post-batch state)
```

**Sequential dependency** — each commit consumes
previous.  Parallel only safe between 45 and 46 if
split scope (e.g. 45 = reorg sections, 46 = cross-ref).

## Per P25 step 7 self-application

Each future commit will re-apply:
- **类比**: principle P-n in commit must fit 1 of 5
  essence families
- **自顶向下**: commit should have clear L0 (what
  this commit does) → L1 (why) → L2 (how)
- **奥卡姆**: don't add new P-n in this batch (use
  existing); only re-organize existing
- **P22 step 3**: explicitly synthesize commonalities

## Per P7 奥卡姆 — task scope caution

Per user "条数多而且混乱，不符合奥卡姆 罪魁祸首":
- Don't add new P-n in this batch
- Don't expand doc structure beyond what's needed
- Re-organize + cross-ref = minimal scope
- Merge eval (commit 47) = user-confirmation
  required before changing P-n count

## Estimated batch size

- Commits 45-49 = batch 1 (5 commits, focused on
  principle doc reorganization + eval)
- Commit 50 = batch 2 (project-level audit, separate
  scope)
- Total: 6 commits planned
- Per "1 个 1 个来" — execute one at a time, no
  batch commitment

## Risk register

- **Risk 1**: P-n merge (commit 47) breaks references
  in OPERATING_RULES.md / AGENTS.md / hooks
  - **Mitigation**: per P25 step 5 impact analysis
    before any P-n number change
- **Risk 2**: PRINCIPLES.md full reorg (commit 45)
  causes massive diff, hard to review
  - **Mitigation**: split into 45a (P19 reorder) +
    45b (section ordering) — but per "1 个 1 个来"
    this is already 2 commits
- **Risk 3**: User disagrees with planned direction
  - **Mitigation**: pause after commit 45 (visible
    diff) for user review before commit 46+

## See also

- commit 44 (this insight is derived from)
- docs/PRINCIPLES.md 类比联想段 (the framework)
- docs/PRINCIPLES_DETAIL.md 共性归纳段 (the DETAIL side)