# Plan: Top-down reorganization + 类比 framework application (commits 45+)

> L0: Roadmap derived from user meta-critique 2026-07-14
> ("递进 + 类比 + 自顶向下 + 奥卡姆").  Per P22 stuck→plan
> + user "规划后续任务，规划顺序，然后推进".
> Last P20-verified: 2026-07-14 (extended with commit 51-53
> per user meta-rule "新agent 不依赖hermes也能学到知识")



## Final architecture (per c56 decision)

**Per 6-principle analysis (c56)**: Option E (read
pattern doc) is the only 0-fail option.  All tool
options (A, B, C, D) violate P7 + P23 (need 3+
failures first).

### Components

1. **SUA (this project)** = single source of truth
   - `docs/` = knowledge graph
   - `docs/HOW_TO_READ_GRAPH.md` = read pattern
     (the "transformation" is in the reader)

2. **No tool** (per P7 + P23 — tool not earned)
   - Future: if 3+ failures observed, consider
     Option A (pandoc + Python) or B (AGENTS.md
     auto-gen)

3. **No separate skill-v2 project** (per c53
   superseded by c54)
   - Skill = generated output (when needed)
   - HOW_TO_READ_GRAPH.md IS the entry point
     for new agents reading SUA

### Obsolete (per c56)

- ❌ graph_to_skill.py converter (c55 Option A)
- ❌ Pure Python script (c55 Option B)
- ❌ llm-wiki MCP backend (c55 Option D)
- ❌ Skill-v2 separate project (c53 plan)

### New (per c56 decision)

- ✅ Read pattern doc (commit 57 = this commit)
- ✅ AGENTS.md link (commit 58)
- ✅ Parent verification (commit 59)

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

## Detail (L2)

For per-principle analysis, M-self-application, follow-ups, and other L2 detail, see [`PLAN_TOPDOWN_REORG_DETAIL.md`](PLAN_TOPDOWN_REORG_DETAIL.md).  Per R6, this companion is required for files > 7KB.
