# Analysis: graph → flat skill export (per user critique 2026-07-14)

> L0: Honest re-analysis after user critique "你做了分析
> 吗? 这个方案是最好的吗?".  Commit 54 design was
> premature — chose "graph + converter in SUA" without
> presenting alternatives.  This doc does the proper
> analysis that should have preceded commit 54.
> Last P20-verified: 2026-07-14 (initial — this is a
> correction document, not a new design)

## Acknowledge premature decision (per P17 + M-self-application 4-level L4)

Per M-self-application 4-level (per c30):
- **Level 4 (own operating behavior)**: I jumped
  from "user says 'I need a tool'" to "design a
  tool" without first asking "is a tool the right
  solution?  Are there alternatives?"

Per P17 (honest reporting): **commit 54 design
was premature**.  I should have presented options
+ asked user before designing.  Per P7 奥卡姆:
less is more — option analysis prevents
over-engineering.

Per P25 step 1-3 (per c41):
- Step 1 (read first) ✅ — read user message
- Step 2 (root axiom) ✅ — Doc + Workflow
- Step 3 (no duplication) ❌ — **failed to check
  if existing tools cover the use case** (pandoc,
  llm-wiki, markdown libraries, etc.)

## The real question

User need: "随时导出一个 skill, 给到其他项目使用"

Translating: **on-demand, reliable export** of the
SUA knowledge graph as a **flat, portable skill**
for any target project.

Implicit constraints:
- **Reliable**: output should be consistent
- **On-demand**: not pre-generated; per export
- **Portable**: works across target projects
- **Self-sustaining**: project self-organizes
  (per c52 P27 candidate)

## Option analysis (5 options, ordered by my current best judgment)

### Option A: Pandoc + minimal Python wrapper ⭐ recommended

**What**: Use pandoc for MD → MD format conversion
(with custom template), Python for graph traversal
and skill assembly.

**Components**:
- `pandoc` (existing tool, battle-tested) for format
  conversion
- Python script for:
  - Reading SUA graph (markdown files + cross-refs)
  - Traversing graph (BFS or DFS)
  - Producing SKILL.md (L0) + references/*.md
    (L1/L2)

**Pros**:
- Pandoc is battle-tested (handles edge cases)
- Minimal Python (~100 lines)
- Self-contained in SUA (per P21 cross-project)
- Reliable (deterministic)

**Cons**:
- Pandoc must be installed (assumed)
- Skill format is project-specific (custom template)

**Score**: high

### Option B: Pure Python with markdown library

**What**: Use `markdown-it-py` or `mistune` for
parsing.  Build everything in Python.

**Pros**:
- No external deps beyond pip packages
- Self-contained

**Cons**:
- ~300 lines of Python (more maintenance)
- Less battle-tested than pandoc

**Score**: medium

### Option C: LLM-driven (no code, just agent + prompt)

**What**: LLM reads SUA docs, writes skill directly.
No conversion tool at all.

**Pros**:
- 0 lines of code
- Flexible (LLM can adapt to context)

**Cons**:
- Slow (LLM token cost per export)
- Non-deterministic (output varies)
- Not hermes-independent (depends on LLM)
- Per P11 摘要+引用: violates reliability
- Per P23 (doc > script with 3+ violations): once
  is fine, but 3+ triggers script

**Score**: low (when 3+ exports needed; OK for 1-2)

### Option D: Use llm-wiki MCP as graph backend

**What**: Don't make SUA docs the graph.  Use
llm-wiki MCP tools to query a real graph DB.
Build minimal script that queries llm-wiki +
produces skill.

**Pros**:
- Real graph infrastructure
- Multi-project knowledge sharing
- Reuses existing tool

**Cons**:
- Requires llm-wiki project setup (out of SUA scope)
- Cross-project dependency (per P21)
- llm-wiki not designed for this use case

**Score**: low (over-engineering for now)

### Option E: No tool — keep skill in SUA + cp

**What**: Don't build a tool.  Maintain ONE skill
in SUA (under `dist/` or similar).  When other
projects need it, `cp -r` from SUA.

**Pros**:
- 0 lines of code
- Simple
- Per P7 奥卡姆: minimum viable

**Cons**:
- Manual sync (drift)
- Per c54 analysis: 1 source of truth BUT manual
  copy means drift risk
- Doesn't address "stale skill" root cause

**Score**: low (the problem user is solving)



## Revised plan (per this analysis)

Per P22 stuck→plan + "如果发现问题，重新计划":

| # | Commit | Content | Status |
|---|---|---|---|
| 54 | Design doc | ✅ done (but premature) | needs revision |
| **55** | **Option A: pandoc + Python** | `graph_to_skill.py` (~100 lines) | TBD |
| **56** | **First export** | Test with agent-onboarding | TBD |
| **57** | **EXTENSIONS.md X2** | Update to "use converter" | TBD |
| 58 | Parent verification | SUMMARY_LIFECYCLE | TBD |

**Note**: c54 design doc still has value (codifies
the architecture question), but implementation
should follow Option A (not "new Python script
from scratch" as in original c54 design).

## Per P26 fresh-agent simulation (post-analysis)

| Discovery step | Pre-analysis | Post-analysis |
|---|---|---|
| Knows 5 options | ❌ (c54 only) | ✅ explicit |
| Knows trade-offs | ❌ (c54 only) | ✅ explicit |
| Knows best option | ❌ (premature) | ✅ Option A |
| Knows why A wins | ❌ | ✅ P7 + P11 + maintenance |
| Can decide | ❌ user must ask | ✅ user can pick from table |

Fresh-agent simulation **PASS** for this analysis
doc.

## Detail (L2)

For per-principle analysis, M-self-application, follow-ups, and other L2 detail, see [`GRAPH_TO_SKILL_ANALYSIS_DETAIL.md`](GRAPH_TO_SKILL_ANALYSIS_DETAIL.md).  Per R6, this companion is required for files > 7KB.
