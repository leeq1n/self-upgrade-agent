# Knowledge organization: graph/tree + flat context (per user 2026-07-14) + Information topology (方案 C, 2026-07-15)

> L0: Codification of "知识是图/树, 上下文是平铺式"
> insight.  This is the **architecture** for the
> self-organization sub-plan: SUA maintains the
> knowledge graph (project-agnostic), agent-onboarding
> skill maintains the flat context reader (per-project).
> Per user clarification 2026-07-14.
> **Update 2026-07-15**: this doc now also codifies the
> **information topology** (方案 C) — the rule that determines
> which knowledge is in which view.
> Last P20-verified: 2026-07-15 (信息拓扑 段 added)

## Why two views?

Knowledge has two consumers:

- **Other agents** (entering the project fresh): need a
  **flat, sequential** reading experience.  They can't
  follow graph edges without context for what each edge
  means.
- **The project itself** (when looking up a specific
  principle or pattern): needs a **graph** to find
  cross-references efficiently.

A single doc can't serve both consumers.  Two views is the
**minimum complete solution** (per P7 奥卡姆 — 3+ views is
over-engineering).

## Information topology (方案 C, per user meta-rule 2026-07-15)

Per user audit 2026-07-15, the **information topology** of
agent documentation has two layers:

| Knowledge type | Maintenance | Why |
|---|---|---|
| **agent behavior rules** (P-n, M-*, R-n) | **flat** + rarely modified | These are the contract — changes break agents that already read them |
| **domain knowledge** (concepts, audit findings, plans) | **classified hierarchy** (top-down by topic) | These evolve with the project; need clear taxonomy |

This is **方案 C** in action.  Specifically:

- `self-upgrade-agent/docs/PRINCIPLES.md` (L0 + L1) is
  **flat**: any agent reading it top-to-bottom gets the
  contract.
- `self-upgrade-agent/docs/PRINCIPLES_DETAIL.md` +
  `_DETAIL.md` are **classified**: per-P-n detail, organized
  by principle number.
- `agent-reflection-skill/` is **flat**: the skill is
  portable; new agents should read it without graph
  traversal.

### Where does the graph live?

Graphs (cross-references, edges, follow-up chains) live in
**`docs/`** as Markdown links and references.  The graph
exists in the form of `→ see also` 段 in each doc.  No
external graph database required.

This is **方案 C** in action: graph metadata (which doc
references which) is implicit in Markdown links; graph
content (the rules themselves) is in flat docs.

## When to update which view

- **P-n / M-* / R-n change** (rare): update PRINCIPLES.md
  + PRINCIPLES_DETAIL.md + AGENTS.md (flat).
- **Domain knowledge update** (frequent): update the topic's
  classified doc (e.g., PROJECT_TOPDOWN_AUDIT for audit
  findings).
- **Cross-reference addition** (frequent): add 1-line
  `→ see also` 段 to relevant docs (lightweight).

## Trade-offs (方案 C)

| Pro | Con |
|---|---|
| New agents onboard via flat context (no graph literacy required) | Maintaining two views = 2x doc-update work (mitigated by P14: "update all cross-refs in same commit") |
| Graph metadata is free (markdown links) | No automated graph-query tool (e.g., "which docs reference P7?") |
| Agent behavior contract is stable (flat) | New emergent rules take longer to surface (must codify in PRINCIPLES.md explicitly) |
| Domain knowledge is organized (classified) | Taxonomy may need to be re-organized as the project grows (per c45 reorg precedent) |

## Revised plan (commits 53+)

| # | Commit | Content |
|---|---|---|
| **53** | (done) | Codify 图/树 + 平铺式 model (this doc) |
| **54** | (done) | `agent-reflection-skill/` created (hermes-root, not in SUA) |
| **55** | (done) | SKILL.md + 4 reasoning primitives (this turn: also compression) |
| **61aab30** | (done) | SUA HANDOFF_DETAIL 加 Sibling project awareness 段 |
| **04a2935** | (done) | skill HANDOFF_DETAIL 加 Upstream sync 段 (mirror) |

## Per P26 fresh-agent simulation (post-this-doc, 2026-07-15)

| Discovery step | Pre-doc | Post-doc |
|---|---|---|
| New agent enters SUA project | sees graph, no flat reading path | ✅ sees both (graph + flat) |
| New agent enters other project | must import SUA docs (not portable) | ✅ imports skill (portable) |
| Understands graph vs flat distinction | ❌ implicit | ✅ explicit doc + 信息拓扑 段 |
| Knows where to put new knowledge | ⚠️ unclear | ✅ graph in SUA, flat in skill (方案 C) |
| Knows agent rules stay flat | ❌ no rule | ✅ 信息拓扑 段 (方案 C codified) |
| Cross-project link mechanism | ✅ EXTENSIONS.md | ✅ (unchanged) |

Fresh-agent simulation **PASS**.

## Detail (L2)

For per-principle analysis, M-self-application, follow-ups, and other L2 detail, see [`KNOWLEDGE_ORG_DETAIL.md`](KNOWLEDGE_ORG_DETAIL.md).  Per R6, this companion is required for files > 7KB.
