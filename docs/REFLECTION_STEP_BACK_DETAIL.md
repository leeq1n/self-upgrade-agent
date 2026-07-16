# REFLECTION_STEP_BACK — Detail (L2)
Last P20-verified: 2026-07-14 (split from summary per R5+R6)

> L0: L2 detail for REFLECTION_STEP_BACK.md summary.  Per
> P11 摘要+引用, the summary file is the L0/L1 layer
> (≤ 7KB); this file is the L2 layer (full detail).
> Per R6, this detail file is referenced from the summary.

This file holds the per-option detail (A-F), P26 fresh-agent
simulation, task-planning-order meta-rule application, P17
honest reporting, M-intent-parsing, M-self-application
4-level, and Known follow-ups.  See
`REFLECTION_STEP_BACK.md` for the summary.

---

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
