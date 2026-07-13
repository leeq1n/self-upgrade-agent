L0: Knowledge-as-graph refactor idea (per user 2026-07-10).  Now in separate project per P21.
Last P20-verified: 2026-07-13

# TODO: Knowledge-as-Graph Refactor

> **Status**: in progress — seed project (../knowledge-graph-seed) has
> minimal MVP stub (commit 4c79bbb, 2026-07-11).  Per user 2026-07-11
> '按计划继续推进' (TODO那条).  Spec + skeleton done; full graph
> impl per SEED.md acceptance questions is next sub-tasks.
> **Origin**: 2026-07-02 conversation, after P0-1/P0-2 audit + commit.

## Why this exists

User observation: we have ~6 markdown files (ISSUES.md, PROJECT_BRIEF.md,
README.md, DELIVERY.md, DESIGN_PHILOSOPHY.md, docs/CLI_GUIDE.md) and they
all overlap / drift / get stale.  Each is a *projection* of the same
underlying knowledge; the underlying knowledge is the *graph*, not the
files.

User framing: two layers, not two files.

- **Layer 1 — Facts** (append-only, verified):
  - "commit 330801f: `_write_manifest` changed to `.tmp + fsync + os.replace`"
  - "5-round apply+revert test: planner.py grew 340B (was 1250B before fix)"
  - "ISS-003 on Windows: `WinError 32` from concurrent `open(mf, 'w')`"
  - "P0-1: fix scope = atomicity per-write, NOT lock-step semantics"
- **Layer 2 — Reasoning** (extracted from facts, reusable):
  - "verification-as-precondition > commit-granularity" (user 2026-07-02)
    — instance of: don't optimize the proxy, optimize the thing
  - "奥卡姆剃刀 vs 整理文档" (user 2026-07-02)
    — instance of: don't add a new artifact when an existing one subsumes
  - "atomic write needs lock-step semantics for cross-process safety"
    — instance of: per-event guarantees ≠ per-system guarantees

## What's in scope (when this TODO is picked up)

1. **Edge-type schema** — at minimum:
   - `causal`: A caused B (commit → fix verified)
   - `inductive`: A and B and C together imply P (the reasoning layer)
   - `counter_example`: A is similar to B but B failed where A succeeded
   - `dual`: A is the inverse / complement of B (e.g. Linux vs Windows
     behavior on concurrent file open)
2. **Node-collection flow** — where nodes come from:
   - git commit message → parse for fact nodes
   - ad-hoc verify result → parse for fact nodes
   - ISSUES.md table rows → parse for fact nodes
3. **View renderer** — two traversals on the same graph:
   - **Facts view** = current ISSUES.md / PROJECT_BREEF.md (chronological,
     "what happened")
   - **Reasoning view** = current DESIGN_PHILOSOPHY.md (synthesized,
     "what did we learn")
4. **Migration** — once renderer works, the 6 existing markdown files
   become *output* of the renderer, not *source* of truth.

## What's NOT in scope

- Building a graph DB (overkill for ~hundreds of nodes; a flat JSON
  or even a directory of typed files is enough to start)
- Replacing all 6 markdown files at once (high risk; do renderer
  first, migrate one file at a time)
- Auto-extracting reasoning from facts (LLM task, low signal-to-noise
  at small scale; start with manual extraction, automate later)

## Success criterion

When the user asks "why did we do X?", the answer should come from the
reasoning layer (a typed chain through the graph) — NOT from a grep
through commit messages or markdown files.  When the user asks
"what's the current state of X?", the answer should come from the facts
layer — NOT from a half-updated markdown file.

## Trigger to start work

User says "go" / "做这个" / equivalent, AND the P0-1/P0-2 follow-ups
(ISS-003 file lock, ISS-014 ModelScope recovery) are settled.  Reason:
the graph refactor is meta-work, not blocking; the locking work is
blocking for real self-upgrade loops.

## Reference commit

`330801f` is a good first node to test the schema on — has all four
edge types implicit in the commit message + the ad-hoc verify report.

> **Status (2026-07-10)**: this idea is now implemented in a separate project (per user).  Kept here as historical record + pointer.  Per P21: cross-project = link, not duplicate.
