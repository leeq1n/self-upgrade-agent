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

### Option A: Fresh agent-onboarding skill v2 (replaces stale)

**What**: Build a fresh, complete
agent-onboarding skill.  Replace the stale one
in Hermes global.  Multi-commit (~5-8 commits
to do well).

**Value**: **HIGH** — kills the "stale skill"
problem you mentioned ("之前写的似乎已经过时很久
了").  Every new agent that uses the skill
benefits.

**Cost**: **HIGH** — needs:
- SKILL.md (entry point)
- references/ (8-12 sub-files)
- Examples + tests
- Compatibility check (L0/L1/L2 format)

**性价比**: **medium-high** (high value, high cost)

### Option B: AGENTS.md auto-gen from SUA graph

**What**: Script that reads SUA graph (docs +
cross-refs) and produces a clean AGENTS.md for
any project.  Single commit (~150 lines Python).

**Value**: **medium-high** — every project gets
a clean, well-structured AGENTS.md without
manual work.  Helps fresh agents enter.

**Cost**: **medium** — needs:
- Graph parser (existing markdown libs)
- AGENTS.md template
- Test with sample projects

**性价比**: **medium-high** (medium value, medium
cost)

### Option C: Pandoc + Python converter (per c55 Option A)

**What**: Script that converts SUA docs to skill
package using pandoc + Python wrapper.  Per c55
analysis.

**Value**: **medium** — on-demand skill export.
Useful but not daily-use.

**Cost**: **medium** — ~100 lines Python + pandoc
dependency.

**性价比**: **medium** (medium value, medium cost)

### Option D: LLM-driven skill export (no code, per c55 Option C)

**What**: LLM (in this conversation or any
agent) reads SUA graph, writes skill on demand.
Zero code.

**Value**: **low-medium** — works for 1-2 exports.
Per P11 (reliability) + P23 (3+ violations = script):
if 3+ exports needed, switch to A/B/C.

**Cost**: **zero** — no code.

**性价比**: **HIGH** (low value + zero cost = high
ROI for occasional use).  But scales badly.

### Option E: Graph traversal as a **read pattern** (NEW idea)

**What**: Codify "how to read SUA graph as a new
agent" as a **documented read pattern** (not a
tool).  This is the "transformation" your insight
refers to — but it's a **reading discipline**, not
a tool.

**Value**: **HIGH** — directly addresses "structure
vs reading" gap.  Zero new code.

**Cost**: **low** — write the read pattern doc.

**性价比**: **HIGH** (high value, low cost)

### Option F: Combined — read pattern + selective tools

**What**: E (read pattern) + A or B (selective
tools for high-value cases).  This is the
"differentiated" approach: do high-value things
in code, do medium-value things as read patterns.

**Value**: **HIGH** (full coverage)
**Cost**: **medium-high** (E is cheap; A or B
adds cost)
**性价比**: **medium-high** (best of both worlds)

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

A document like `docs/HOW_TO_READ_THIS_GRAPH.md`
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

## Per P26 fresh-agent simulation (post-reflection)

| Discovery step | Pre-reflection | Post-reflection |
|---|---|---|
| Sees 6 options clearly | ❌ (trapped in 1) | ✅ explicit |
| Knows 性价比 for each | ❌ | ✅ explicit |
| Sees "read pattern" as alternative to "tool" | ❌ (tool-only thinking) | ✅ explicit |
| Can pick highest-ROI option | ❌ | ✅ Option E recommended |
| Avoids over-engineering | ❌ | ✅ per P7 奥卡姆 |

Fresh-agent simulation **PASS** for this reflection
doc.

## Per task-planning-order meta-rule

Per user "如果发现任务对其他任务可能有影响，就重新
计划整理一下" (2026-07-14 follow-up): this is a
**plan re-revision**.  c54 design + c55 analysis
are both **trap thinking**; this reflection breaks
the trap.

| Sub-task | Depends on | Output informs |
|---|---|---|
| a. Acknowledge trap | c54 + c55 | (b) |
| b. List real capabilities | (a) | (c) |
| c. ROI analysis | (b) | (d) |
| d. Recommend highest-ROI | (c) | (e) |
| e. Defer code | (d) | (commit) |

(a) honesty informs (b) wider capability view.
(b) capability list informs (c) ROI.
(c) ROI informs (d) recommendation.
(d) Option E wins.
(e) defer code, focus on doc.

## Per P17 honest reporting

- **c54 + c55 were both over-engineered**: jumped
  to "build tool" before asking "is a tool the
  right solution?"
- **This reflection is a course correction**: step
  back, think clearly, find the highest-ROI
  option
- **Option E (read pattern doc)** is the best ROI
  by my analysis
- **But still user decision**: you may have
  different priorities

## What user should decide (per M-intent-parsing)

Per "哪个方向最有性价比" (per your question):

1. **Option E (read pattern doc)** — high value, low cost
2. **Option A (fresh skill v2)** — high value, high cost
3. **Option B (AGENTS.md auto-gen)** — medium-high, medium
4. **Option F (E + A or B)** — high value, medium-high cost
5. **Other direction** — you tell me

## Per M-self-application 4-level

- **Level 1**: ✅ 1 file (this reflection) + 1 commit.
- **Level 2 (rule itself)**: P7 奥卡姆 + P11 + P13
  + P17 + P22 + P25 + P26 all applied.  7 rules.
- **Level 3 (memory / project structure)**: SUA
  capabilities (A-J) explicit; ROI analysis
  explicit; Option E recommended.
- **Level 4 (own operating behavior)**: future
  "build a tool" thinking should be replaced
  with "is a tool the right solution?" first.

## Known follow-ups (deferred, awaiting user decision)

### From this reflection (per user choice)

1. **Next commit**: TBD per user choice (E, A,
   B, F, or other)
2. After E: AGENTS.md "Read first" link to
   HOW_TO_READ_GRAPH.md (low cost, high value)

### Pending user approval (from previous batches)

3. **commits 47a-d**: P-n merge (per c47)
4. **commits 50a-50e**: doc fixes (per c50)
5. **commit 47e**: AGENTS.md P-n count update
6. **P27 lift to PRINCIPLES.md** (per c52)

### Other

7. **Hook installed still P1-P26** (1 user action)
8. **knowledge-graph-seed PHILOSOPHY.md sync** (R12)
9. **TODO.md [x] drift entries** (3 stale)

## See also

- `docs/GRAPH_TO_SKILL_DESIGN.md` (c54, premature)
- `docs/GRAPH_TO_SKILL_ANALYSIS.md` (c55, honest
  but still over-engineered)
- `docs/KNOWLEDGE_ORG.md` (c53, 2-view model — correct)
- `docs/SELF_ORG.md` (c52, P27 candidate)
- `docs/PLAN_TOPDOWN_REORG.md` (revised plan)