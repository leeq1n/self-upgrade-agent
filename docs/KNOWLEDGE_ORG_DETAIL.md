# KNOWLEDGE_ORG — Detail (L2)
Last P20-verified: 2026-07-14 (split from summary per R5+R6)

> L0: L2 detail for KNOWLEDGE_ORG.md.  Per P11 摘要+引用, the
> summary file is the L0/L1 layer (≤ 7KB); this file is
> the L2 layer (full detail).  Per R6, this detail file
> is referenced from the summary.

This file holds the L2 detail (per-principle analysis,
M-self-application, follow-ups, etc.).  See
`KNOWLEDGE_ORG.md` for the summary.

---

## The insight (per user)

> "知识是图/树，但是上下文是平铺式的"

Two complementary views of the same knowledge:

1. **Graph/tree view** (machine-readable, project-
   internal):
   - **Nodes**: docs, principles, M-rules, decisions
   - **Edges**: cross-refs, dependencies, references
   - **Tree structure**: parent/child relationships
     (per R12 hub-and-spoke pattern)
   - **Use case**: machine reasoning, search, audit

2. **Flat context view** (human-readable, agent-
   entry-point):
   - **Sequence**: L0 → L1 → L2 per P20 progressive
     disclosure
   - **Linear reading**: top to bottom, no jumps
   - **Use case**: new agent reads sequentially,
     builds context

These are **NOT in conflict** — they're two views of
the same knowledge:

- The **graph** is the **authoring structure**
  (how docs link to each other)
- The **flat context** is the **reading structure**
  (how new agents encounter the docs)


## The 2-project architecture (per user)

Per user 2026-07-14 clarification:

```
hermes-root/                          # parent workspace
├── self-upgrade-agent/               # this project (SUA)
│   ├── docs/PRINCIPLES.md            # knowledge graph
│   ├── docs/OPERATING_RULES.md       # knowledge graph
│   ├── docs/MCP_TOOLS.md             # knowledge graph
│   └── docs/KNOWLEDGE_ORG.md         # this doc
│
└── agent-onboarding-v2/              # NEW project (separate)
    ├── SKILL.md                      # entry point
    ├── README.md                     # entry point
    ├── references/                   # flat reading
    │   ├── 00-orientation.md
    │   ├── 10-principles.md
    │   ├── 20-rules.md
    │   └── 30-workflows.md
    └── ...
```

### SUA role: maintain the knowledge graph

SUA (this project) maintains:
- **P1-P27 principles** (P27 proposed per c52)
- **M-* rules** (M-self-audit, M-self-application,
  M-task-summary, etc.)
- **R1-R12 rules** (doc structure invariants)
- **MCP tools documentation** (per c51)
- **Plan files** (per c45)
- **Audit results** (per c50)
- **Cross-references** between these

These form the **graph view**: every doc has parent
+ sibling cross-refs.  The graph is **project-
internal** (machine-readable, search-friendly).

### agent-onboarding-v2 role: provide the flat context

The agent-onboarding skill (in hermes-root, separate
project from SUA) provides:
- **Flat, sequential reading order** for new agents
- **L0 → L1 → L2 structure** (P20 applied)
- **Self-contained references** (no need to follow
  cross-refs to understand a concept)
- **Reusable across projects** (any project can
  install this skill)

The flat context is **portable** (any project can
use it) and **readable** (new agents read top-to-
bottom).


## Per P11 摘要+引用 + P20 progressive disclosure

- **SUA docs are L0/L1 summaries with full cross-refs**
  (graph view)
- **Skill references are L2 details with self-contained
  text** (flat view)

Both views coexist:
- A new agent reads skill references sequentially
  (flat view) to learn the basics
- Then reads SUA docs (or sub-summaries) when they
  need depth (graph view)


## Per P13 no orphan nodes + P21 cross-project

- SUA docs are NOT orphans of the skill (they have
  their own cross-ref graph)
- Skill references are NOT orphans of SUA (they
  are self-contained)
- Cross-project links use EXTENSIONS.md (per P21)


## Per P25 6-step + P-n vs M-* boundary 3-case test

- "Knowledge should be in graph + flat views" =
  about what should be true (state invariant) =
  **P-n (case 1)**
- "Agent should write flat context + maintain
  graph" = about agent behavior = **M-***
- This doc codifies the **P-n** (state invariant)


## P27 candidate (per c52) — relationship to this doc

P27 (project self-organization) is the **principle**
that "project should self-organize".  This doc is
the **operational model** of how P27 is implemented:
the graph view (SUA) + flat view (skill).

P27 + this doc = 2 docs implementing 1 principle.


## Per task-planning-order meta-rule

Per user "如果发现任务对其他任务可能有影响，就重新
计划整理一下" (2026-07-14): the **commit 51 + 52
plan iterations** are **partial** — they added docs
to SUA that should be in the **agent-onboarding skill**
instead.  Per user clarification:

| Commit | Original intent | Corrected intent |
|---|---|---|
| 51 (MCP_TOOLS.md) | L0 doc in SUA | KEEP in SUA (graph view) + skill should reference it |
| 52 (SELF_ORG.md, P27 candidate) | P-n codification in SUA | KEEP in SUA (P27 lives in PRINCIPLES.md) |

Both commits are still **valid** (graph view in SUA
is correct), but **additionally need a skill project**
to provide the flat view.


## Per M-self-application 4-level

- **Level 1**: ✅ 1 file (this doc) + 1 commit.
- **Level 2 (rule itself)**: P11 + P13 + P20 + P21
  + P22 + P25 + P26 all applied.
- **Level 3 (memory / project structure)**: SUA
  graph view preserved (c51, c52 still valid);
  flat view to be created in skill-v2 (commits
  54-57).
- **Level 4 (own operating behavior)**: future
  knowledge additions should be classified: graph
  (SUA) vs flat (skill).


## Per P17 honest reporting

- **Commit 51 + 52 partial misinterpretation**:
  per user clarification, the "不依赖hermes也能学
  到知识" meta-rule was about the **skill's
 规划**, not SUA docs.  Commits 51 + 52 are still
  valid (graph view in SUA is correct), but the
  flat view belongs in a separate skill project.
- **No revert of c51 + c52** needed (per P7 奥卡姆
  + P14 — content is correct, just incomplete).
- **Plan file needs revision** (per this doc) to
  add commits 54-57 for skill-v2 creation.
- **hermes-root structure** = SUA (graph) + skill-v2
  (flat) + KG (cross-ref).


## See also

- `docs/MCP_TOOLS.md` (c51, graph view in SUA)
- `docs/SELF_ORG.md` (c52, P27 candidate)
- `docs/EXTENSIONS.md` (X1 = KG, X2 = skill — will
  be updated by commit 56)