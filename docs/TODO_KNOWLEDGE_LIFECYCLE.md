# TODO: knowledge lifecycle (KG priority + pruning + search bypass)

> L0: Proposal for managing an ever-growing knowledge graph
> (KG).  Load when: KG size > 10K nodes, when search
> returns too many low-quality results, or when planning
> KG growth strategy.
Last P20-verified: 2026-07-13

**Status**: TODO (proposal only — not yet implemented).
**Priority**: LOW (KG is currently frozen; last activity was
2026-07-13 doc refresh.  Proposal is the design; implementation
deferred until seed work resumes).
**Triggered by**: user signal 2026-07-13 — "knowledge base
grows, need priority marking" (verbatim).  KG had 136KB
nodes.jsonl at that point; expected to grow.

## Current state (per audit)

- **KG location**: `knowledge-graph-seed/data/{nodes,edges,reasonings}.jsonl`
  - nodes.jsonl: 136KB
  - edges.jsonl: 352B
  - reasonings.jsonl: 20KB
- **KG code**: 7 modular modules in `src/` (kg.py is stub;
  others functional: kg_seed, kg_arbiter, kg_papers,
  kg_query_q1/2/3, kg_reason).  75 tests pass + 1 SKIP.
- **Activity**: frozen since 2026-07-13 (per `git log`).
  No active user work on KG.
- **Search**: per `docs/OPERATING_RULES.md` M-self-audit
  signal, "doc drift detected (> 2 files with Last
  P20-verified > 30 days)" — for KG, this would be
  "node drift detected" (> N nodes with no recent access).
  **Not yet implemented**.

## What's missing (the gap)

Per P22 (stuck→plan), KG lifecycle has **3 missing mechanisms**:

1. **Priority scoring**: how do we rank nodes by importance
   so search can return the top-N most relevant?
2. **Pruning**: when a node is stale (no recent access,
   no recent inbound edges), do we delete, archive, or
   mark deprecated?
3. **Search bypass**: how do we skip low-priority nodes
   when search returns too many results?

## Proposal (the design)

### 1. Priority scoring

Each node has a **priority score** = composite of:

- **Reference count** (40%): how many edges point to this
  node?  More refs = higher priority.
- **Recency** (30%): when was the node last accessed?
  Recent = higher priority.  Decay function: `exp(-age/30d)`.
- **Source quality** (20%): is the source a primary paper
  (DOI-verified) or secondary?  Primary = higher priority.
- **Manual override** (10%): user can boost/demote specific
  nodes.  Stored in a sidecar file.

Output: priority score in [0, 1].  Top 20% are "core",
next 30% are "active", bottom 50% are "long tail".

### 2. Pruning

3-tier policy based on age + access count:

- **Active** (last accessed < 30 days OR refs > 5):
  KEEP.  No action.
- **Stale** (last accessed 30-180 days, refs ≤ 5):
  MARK deprecated (add `deprecated: 2026-XX-XX` field).
  Still searchable but with demoted priority.
- **Dead** (last accessed > 180 days, refs = 0):
  ARCHIVE to `data/archive/dead-nodes-YYYY.jsonl`.
  Removed from active search.

Run pruning as a **batch job** (cron or manual trigger);
**not** automatic per-write (per P23 "doc > script with
nuance": batch is OK, real-time is not).

### 3. Search bypass

When search returns > N results (e.g. N=100):

- **Default**: return top N by priority score (already
  computed in step 1).
- **Escape hatch**: user can `search --no-bypass` to get
  raw results, or `search --priority-min X` to filter
  by minimum priority.
- **Cached bypass**: a precomputed `data/priority-index.jsonl`
  stores the top 1000 nodes by priority; loaded at search
  start to avoid re-scanning all nodes.

## Integration with existing patterns

- **M-add-then-reduce**: priority scoring is **always-on**
  (computed at write time); pruning is **reduce phase**
  (batch, signal-triggered).  Matches the cycle.
- **M-learn**: search-bypass results should feed into
  M-learn (if user finds the bypass useful, that's a
  reusable pattern; if bypass is wrong, fix in next batch).
- **M-self-audit**: trigger prune when "node drift
  detected" (analog of "doc drift detected").  M-self-audit
  also audits the bypass itself (does it return good
  results?  user feedback?).

## Open questions (per M-self-application 4 levels)

1. **Source quality metric**: how to score "primary vs
   secondary"?  DOI check is one signal; what about
   citation count, recency of the source itself?
2. **Prune frequency**: daily? weekly? on-write (real-time)?
   Per M-add-then-reduce, batch is preferred; but
   real-time might be needed if KG is critical-path.
3. **Archive format**: keep as JSONL?  Move to a separate
   DB (SQLite)?  Per "奥卡姆" (P7), JSONL is fine for
   now.
4. **Priority score calculation cost**: composite score
   is computed at every write?  At search?  Cached?
   Per P22 (stuck→plan), defer this to implementation.

## Implementation steps (when ready)

Per "1 commit = 1 logical feature":

1. **Commit 1 (this proposal + ref)**: write this doc +
   add reference from `docs/COMMON_PITFALLS.md` +
   `TODO.md` + `AGENTS.md` See-also.
2. **Commit 2 (later)**: implement priority scoring in
   `src/kg_priority.py` (new module).
3. **Commit 3 (later)**: implement prune batch job in
   `scripts/prune_kg.py` (new script).
4. **Commit 4 (later)**: implement search bypass in
   `src/kg_query_q*.py` (modify 3 query modules).
5. **Commit 5 (later)**: precompute priority-index.jsonl
   + verify search returns top-N by priority.

Per P23 (doc > script with nuance): doc commits first,
scripts when design is stable.  Per P5 (测通), all scripts
must pass tests before commit.

## See also

- `docs/COMMON_PITFALLS.md` §1 — Knowledge lifecycle is
  listed as an "open-work category" (was orphan before
  this doc was written).
- `docs/TODO_KNOWLEDGE_GRAPH.md` — pre-existing, different
  topic (KG architecture, not lifecycle).  See this doc
  for KG structural design.
- `docs/OPERATING_RULES.md` — M-add-then-reduce rule
  (where reduce phase = pruning fits).
- PRINCIPLES.md P7 (奥卡姆) — supports "JSONL is fine for
  archive" (don't over-engineer with DB).
- PRINCIPLES.md P14 (docs stay current) — the principle
  that "doc drift" extends to "node drift" in this domain.
- `~/AppData/Local/Temp/hermes-snapshot-sua-onboarding-20260713.md`
  — first snapshot (mentions KG frozen state).
- agent-onboarding skill, `references/M_RULE_AUTHORING.md`
  (skill) — the 7-section recipe for adding M-* rules
  (per M_RULE_AUTHORING cross-reference; 9 pitfalls
  including dual-trigger and child-summary-destroy).
  this proposal, it should follow the recipe.