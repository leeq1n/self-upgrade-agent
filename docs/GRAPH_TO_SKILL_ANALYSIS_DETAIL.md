# GRAPH_TO_SKILL_ANALYSIS — Detail (L2)
Last P20-verified: 2026-07-14 (split from summary per R5+R6)

> L0: L2 detail for GRAPH_TO_SKILL_ANALYSIS.md.  Per P11 摘要+引用, the
> summary file is the L0/L1 layer (≤ 7KB); this file is
> the L2 layer (full detail).  Per R6, this detail file
> is referenced from the summary.

This file holds the L2 detail (per-principle analysis,
M-self-application, follow-ups, etc.).  See
`GRAPH_TO_SKILL_ANALYSIS.md` for the summary.

---

## Comparison table

| Option | Lines of code | Reliability | Maintenance | P7 奥卡姆 | P11 摘要+引用 |
|---|---|---|---|---|---|
| A: pandoc + Python | ~100 | high | low | satisfies | satisfies |
| B: pure Python | ~300 | medium | medium | partial | satisfies |
| C: LLM-driven | 0 | low | n/a | satisfies | violates |
| D: llm-wiki | ~150 | medium | high | violates | satisfies |
| E: no tool (cp) | 0 | high (manual) | n/a | satisfies | violates |


## Recommendation: Option A

Per P7 + P11 + P13 + P22 (read principles to
decide):

- **A wins on**: reliability + maintenance + P7 + P11
- **A trades**: requires pandoc installed
- **A is best** for the current need


## Per task-planning-order meta-rule

Per user "如果发现任务对其他任务可能有影响，就重新
计划整理一下" (2026-07-14): this commit IS a plan
revision.  c54 design choice is now exposed as one
of 5 options.

| Sub-task | Depends on | Output informs |
|---|---|---|
| a. Acknowledge premature decision | c54 | (b) |
| b. Identify real options | (a) + existing tools survey | (c) |
| c. Trade-off analysis | (b) | (d) |
| d. Recommend option | (c) + P7 + P11 | (e) |
| e. Defer implementation | (d) | (commit) |

(a) honesty informs (b) wider option search.
(b) survey found pandoc / llm-wiki / LLM-driven / cp.
(c) trade-offs explicit.
(d) Option A wins.
(e) defer commit 55 until user confirms.


## What user should decide (per M-intent-parsing)

Per "你看看是不是要修改" + "选哪个最优" (per
your meta-rule + my pre-commit-54 design choice):

1. **Accept Option A** → commit 55 = pandoc + Python
2. **Choose different option** → commit 55 = per choice
3. **Defer** → no commit 55, focus on other things
4. **Revise constraints** → tell me what's missing



## Per P17 honest reporting

- **c54 design was premature** — chose 1 option
  without presenting alternatives.
- **This commit does the analysis that should have
  preceded c54**.
- **c54 is not reverted** (per P7 奥卡姆 + P14)
  but is **superseded by this analysis**.
- **5 options presented** with trade-offs.
- **Recommendation: Option A** (pandoc + Python).
- **User should confirm** before commit 55.



## See also

- `docs/GRAPH_TO_SKILL_DESIGN.md` (c54, premature
  design — still valid as question, not as answer)
- `docs/KNOWLEDGE_ORG.md` (c53, 2-view architecture
  — correct)
- `docs/SELF_ORG.md` (c52, P27 candidate)
- `docs/MCP_TOOLS.md` (c51, graph view)
- `docs/PLAN_TOPDOWN_REORG.md` (revised plan)