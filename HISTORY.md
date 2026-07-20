# History

> L0: SUA 项目 版本历史 (per M-n 31 project
> lifecycle段 + user message 2026-07-15
> "联想分析类比" item 4).

This file records SUA project milestones
at version granularity (NOT per-commit).

Per user message prior: "项目生命周期，以及跨
项目记忆管理".

## Versions

### v2.0.0 (current, per c204 + 2026-07-16)

**Major milestones**:
- 25 P-n working (per c47a + c78 + c79 +
  c80 + c96 + c167; P6/P15/P16/P24
  demoted/merged)
- 31 M-n codified (M-n 12-31)
- 3-project architecture (SUA + skill-
  incubator + agent-reflection-skill +
  knowledge-graph-seed)
- VERIFICATION.md created (c193)
- ACCEPTANCE_REPORT.md created (c207)
- SKILL Standalone段 (c155) + acceptance
  spec (c209) + Flat structure (c211)
- Cross-project sync: skill-incubator +
  skill + KG all have Reading order + SUA
  cross-ref (c215-c225)
- M-n 30 Update order rule (Priority 5):
  SUA → skill-incubator → skill (c222 +
  propagation c224 + c225)
- M-n 31 task-lifecycle (4-phase, c228)
- TODO.md split to TODO_DETAIL (c230)

**Commits**: c1-c230 (442 total)

### v1.x (legacy, per c149 turn)

**Major milestones**:
- vision: self-improving agent that reads
  papers, modifies its own code in
  core/planner.py (per c36)
- 23 P-n initial codify
- Multiple M-n codify

**Refactored at c73 + c85 + c119 + c149 +
c193**: vision drift to "原则库项目".

### v0.x (initial, c1-c35)

**Major milestones**:
- AGENTS.md + PRINCIPLES.md + 5 essence
  families (c44 + c80)
- 4 root axioms (c43) + P27 cross-axiom
  (c74)
- Initial M-n 1-11 codified

## Lessons (per P19)

### Recurring patterns

- **Vision drift** (c73 + c85 + round 82 +
  c119 + c193): 多次 refine vision.  Per
  P14 docs stay current.
- **R5 violations** (c60-c194): 30+ docs
  fixed via _DETAIL companions.
- **Framework-agnostic** (c150 + c155 +
  c163): skill works in any framework.

### Heuristics

- TODO.md > 7KB → split (P11 摘要+引用)
- 30+ commits → 7-check + Plan re-analysis
  (M-n 23)
- 3+ P-n conflict → P22 case-3 (META) +
  P-n vs M-* boundary 3 cases

## See also

- `TODO.md` — current task list (L0/L1)
- `TODO_DETAIL.md` — task detail (L2)
- `docs/HANDOFF.md` — operational defaults
- `VERIFICATION.md` — 1-page verification
  summary (per c193)
- `ACCEPTANCE_REPORT.md` — 14 audit角度 +
  PASS/FAIL (per c207)