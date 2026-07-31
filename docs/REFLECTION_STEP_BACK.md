# Reflection: stepping back from "build a tool" trap (per user 2026-07-14)

> L0: Per user "不要陷进任务里, 先想清楚我们能做
> 出来什么, 哪个方向最有性价比".  This doc is a
> **reflection + option reframing**, NOT a new
> design.  Goal: clarify real options before
> committing more code.
> Last P20-verified: 2026-07-14 (initial)

## Acknowledge the trap (per P17 + M-self-application 4-level L4)

Per M-self-application 4-level L4 (own operating
behavior): **I've been trapped in "build a tool"
thinking** for commits 51-55.  Each commit
proposed a new tool/script/doc, but I didn't ask
**"is a tool the right solution at all?"**.

User's 2026-07-14 reframing: "结构是自顶向下的, 分治
的, 而上下文阅读需要顺序的, 所以这之间可能需要
转换".  This is **2 views of the same thing**:
- Graph view (structure) = tree
- Sequential view (reading) = tree traversal
  linearized

The "converter" is not necessarily a separate tool
— it could be a **read pattern** that new agents
apply (e.g., "read this file first, then this").

## Per P22 stuck→plan: stepping back

User says: "先想清楚我们能做出来什么, 哪个方向最有
性价比".  This is **P22 applied at meta level**: stop
and think before continuing.

## Capability + ROI analysis (per user "性价比")

What we can build (capability), with value/cost
trade-offs:







## Comparison table

| Option | Value | Cost | 性价比 | Status |
|---|---|---|---|---|
| A: Fresh skill v2 | high | high | medium-high | multi-commit |
| B: AGENTS.md auto-gen | medium-high | medium | medium-high | possible |
| C: pandoc + Python | medium | medium | medium | c55 design |
| D: LLM-driven export | low-medium | zero | high (for 1-2) | already works |
| **E: Read pattern doc** | **high** | **low** | **HIGH** ⭐ | **recommended** |
| F: E + A or B | high | medium-high | medium-high | combined |

## Per "先想清楚" + "性价比" recommendation

**Recommendation: Option E (read pattern doc)** as
the highest-ROI first step.

Why:
- **Low cost** (one new doc, ~100 lines)
- **High value** (directly addresses the
  "structure vs reading" gap)
- **Per P7 奥卡姆**: minimum viable
- **Per P11 摘要+引用**: doc is the L0 layer
- **Per P13 no orphan**: read pattern doc is
  discoverable from AGENTS.md "Read first"

After E, decide on A or B based on observed need:
- If fresh agents ask "where's the skill?", do A
- If fresh agents ask "how do I write AGENTS.md?",
  do B

## What "Option E" looks like in practice

A document like `docs/HOW_TO_READ_GRAPH.md`
(or similar) that:
1. Lists the 5 essence families of docs (per c44)
2. Shows the recommended reading order (per P20)
3. Identifies which doc to read first for which
   task
4. Notes which cross-refs to follow (and which
   to skip)
5. Notes the 7-check self-organization pattern
   (per c50 audit)

This is **read pattern**, not a converter.  The
"transformation" is in the **reader's head**, not
in a tool.







## See also

- `docs/GRAPH_TO_SKILL_DESIGN.md` (c54, premature)
- `docs/GRAPH_TO_SKILL_ANALYSIS.md` (c55, honest
  but still over-engineered)
- `docs/KNOWLEDGE_ORG.md` (c53, 2-view model — correct)
- `docs/SELF_ORG.md` (c52, P27 candidate)
- `docs/PLAN_TOPDOWN_REORG.md` (revised plan)

## Detail (L2)

For per-option detail (A-F), P26 fresh-agent simulation, task-planning-order meta-rule application, P17 honest reporting, M-intent-parsing, M-self-application 4-level, and Known follow-ups, see [`REFLECTION_STEP_BACK_DETAIL.md`](REFLECTION_STEP_BACK_DETAIL.md).  Per R6, this companion is required for files > 7KB.
