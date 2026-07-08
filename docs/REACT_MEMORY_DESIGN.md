# v1.8.2 Design: ReAct Prompts + MCP Memory

**Status**: draft (v1.8.2-pdf-memory branch)

**Why this rewrite**: I had 19 fix-commit pile-up on master.
This design is the result of `整理 → 思考 → 清理 → 思考 → 行动`.
The previous draft was over-engineered (8 issues self-found); this
rewrite cuts them.

**Core principle**: align with user's "MCP-everything" idea — memory
operations should be tool calls, not direct Python imports.

---

## 0. Research notes

Sources I read (no other knowledge):

- **ReAct (Yao et al., 2022)** — arxiv 2210.03629.
  Format: `Question → Thought → Action → Action Input → Observation → ...`
  Source: https://www.promptingguide.ai/techniques/react

- **PyMuPDF4LLM** — best PDF→markdown for LLM (preserves tables).
  `pip install pymupdf4llm`.  3-line API.

- **arXiv PDF URL**: `https://arxiv.org/pdf/{arxiv_id}` (e.g.
  `https://arxiv.org/pdf/2310.02170`).  Direct download, no API.

- **4-tier agent memory** (2026 guide): in-context / short-term /
  vector / graph.  The tiers describe *where memory lives*, not
  *separate modules*.  Most agents combine them.

- **MCP memory servers** (mcp-memory-graph, Rag Memory, memorizedMCP).
  Reference implementations; we adapt the ideas, don't depend on them.

- **mcp-memory-graph** — has authority weighting (high/medium/low),
  typed edges, conflict detection.  We borrow the authority idea.

---

## 1. ReAct in the existing pipeline

We already have `src/llm.py:chat()` + `src/tools.py:call_tool()`.  We
do NOT need a separate "ReAct driver."  ReAct is a **prompt format**,
not a separate runtime.

### Where it goes

- `src/patchgen.py` — modify `PROMPT_TEMPLATE` to add
  `Thought:`, `Action:`, `Action Input:`, `Observation:` slots.
- `src/filter.py` — same template change for filter scoring.
- `src/llm.py:chat()` — add a `react_mode=True` flag that uses stop
  sequence `\nObservation:` to force LLM to halt before tool call.

### How it works in practice

```
[patchgen call]
1. Format prompt with Thought/Action/Action Input slots
2. LLM generates:
     Thought: I need to look at how plan_task handles failures
     Action: read_decision_log
     Action Input: {"limit": 5}
3. chat() returns up to first "Observation:" (stop sequence)
4. Our code calls read_decision_log("limit=5")
5. Append "Observation: <result>" to scratchpad
6. Re-prompt LLM with updated scratchpad
7. Repeat up to N=4 times
8. On "Final Answer:" or "Action: patch_propose", exit loop
```

This is ~80 LOC added to `src/llm.py`, no new module.

---

## 2. Memory (as MCP, not Python imports)

### Architecture

```
┌──────────────────────────────────────────────────────┐
│  Agent loop (src/pipeline_lg.py)                     │
│      │                                                │
│      │ tool call: memory_search, memory_add, ...     │
│      ▼                                                │
│  src/mcp_client.py (NEW, ~60 LOC)                    │
│      │  - call_tool(server, name, **kwargs)          │
│      │  - in-process registry of MCP server stubs    │
│      │                                                │
│      ▼                                                │
│  src/memory_server.py (NEW, ~120 LOC)                │
│      │  - implements the "memory" MCP server         │
│      │  - tools: memory_search, memory_add_paper,     │
│      │          memory_add_outcome, memory_compact    │
│      │                                                │
│      ▼                                                │
│  SQLite: upgrades/memory.db                          │
│      - memory_units (id, kind, text, vector, ts)     │
│      - relations (src_id, dst_id, rel_type)          │
└──────────────────────────────────────────────────────┘
```

### Tools (memory is a tool, like any other)

| Tool | Input | Output |
|---|---|---|
| `memory_add_paper` | `arxiv_id, summary, topics` | `memory_id` |
| `memory_add_outcome` | `paper_id, decision, patch_summary` | `memory_id` |
| `memory_search` | `query, top_k=3` | `[memory_units]` |
| `memory_get_related` | `memory_id, max_hops=2` | `[memory_units]` |
| `memory_compact` | `max_age_days=30` | `n_units_before, n_units_after` |

### Storage (1 schema, not 4)

```sql
CREATE TABLE memory_units (
    id          INTEGER PRIMARY KEY,
    kind        TEXT,    -- 'paper' | 'outcome' | 'patch' | 'topic'
    arxiv_id    TEXT,    -- nullable
    text        TEXT,
    topics      TEXT,    -- JSON list
    -- bag-of-words hash for similarity (see §3)
    bow_hash    BLOB,
    created_at  INTEGER
);

CREATE TABLE relations (
    src_id      INTEGER,
    dst_id      INTEGER,
    rel_type    TEXT,    -- 'applies_to' | 'modified' | 'reverted' | 'extends'
    PRIMARY KEY (src_id, dst_id, rel_type)
);
```

**Two tables, not four.**  Graph queries become SQL JOINs.  This is
the user's 奥卡姆 principle applied.

### Embedding (kept honest)

Three options considered:

1. **Bag-of-words hash** (my previous draft) — too weak, "vector" is a
   lie.  Reject.
2. **Real embedding model** (e.g. sentence-transformers) — adds a heavy
   dep (~600MB) we don't need yet.  Reject for v1.8.2.
3. **Keyword match + relation traversal** — uses existing TF-IDF-like
   scoring on `topics` and `text`, plus graph JOINs.  Honest about
   what it is (keyword, not semantic).

**Decision**: option 3 for v1.8.2.  When we have 100+ papers and the
keyword gap hurts, we upgrade to embedding (option 2).  Path is open.

### Authority weighting

Inspired by mcp-memory-graph:

- `kind='paper'`  → authority 0.5  (external, may not apply)
- `kind='outcome'` → authority 1.0  (our decision, real signal)
- `kind='patch'` → authority 0.7  (we wrote it)
- `kind='topic'` → authority 0.9  (synthesis, recent)

Used when ranking search results.

---

## 3. PDF reading

`src/web.py` adds `arxiv_pdf_markdown(arxiv_id) -> str`:

1. URL = `https://arxiv.org/pdf/{arxiv_id}`
2. `urllib.request.urlretrieve()` → `upgrades/cache/papers/{arxiv_id}.pdf`
3. `pymupdf4llm.to_markdown(local_path)` → markdown text
4. Cache in `upgrades/cache/papers/{arxiv_id}.md`
5. Return text

**Fallback**: if `pymupdf4llm` not installed → return `arxiv_paper()`
abstract only.  Pipeline continues, less precision.

**Dependency added**: `pymupdf4llm` (pure-Python).

---

## 4. Files

| File | Status | Est LOC |
|---|---|---|
| `src/mcp_client.py` | NEW | 60 |
| `src/memory_server.py` | NEW | 120 |
| `src/web.py` | add `arxiv_pdf_markdown` | +50 |
| `src/llm.py` | add `react_mode` flag + stop sequence | +80 |
| `src/patchgen.py` | modify `PROMPT_TEMPLATE` for ReAct | +30 |
| `src/filter.py` | same template change | +20 |
| `src/pipeline_lg.py` | call `memory_add_*` on writes | +15 |
| `tests/test_memory.py` | NEW | 80 |
| `tests/test_react.py` | NEW | 60 |
| `tests/test_web.py` | add `arxiv_pdf_markdown` | +30 |

Total: ~545 LOC.  Half of previous draft (was 770).

---

## 5. Commit plan (5 commits, not 6)

| # | Branch | Commit |
|---|---|---|
| 1 | `feature/v1.8.2-pdf-memory` | `docs(v1.8.2): REACT_MEMORY_DESIGN` (this file, amended) |
| 2 | same | `feat(v1.8.2): src/memory_server.py + mcp_client.py + tests` |
| 3 | same | `feat(v1.8.2): src/web.py arxiv_pdf_markdown + tests` |
| 4 | same | `feat(v1.8.2): src/llm.py react_mode + patchgen/filter ReAct prompt` |
| 5 | same | `feat(v1.8.2): wire memory ops into pipeline_lg nodes` |

Each ≤ 200 LOC.  Each reviewed before next.

---

## 6. What we explicitly do NOT do (奥卡姆)

- ❌ No LangChain / LangGraph dependency
- ❌ No chromadb / faiss
- ❌ No real embedding model (use keyword match + relations)
- ❌ No compact() in v1.8.2 (wait until 100+ papers)
- ❌ No separate ReAct driver (it's a prompt format, not a runtime)
- ❌ No 4-table schema (use 2 tables + JOIN)
- ❌ No JSON Schema enforcement (chat_simple + lenient parser is enough)
- ❌ No master commits (everything in feature branch)

---

## 7. Production vs research

The user said "actual production, not research."  This design is
deliberately production-leaning:

- All memory operations are idempotent and survive crashes (SQLite +
  WAL mode).
- All tool calls have timeouts (10s default, configurable).
- All external IO has fallback paths (PDF fails → abstract only).
- 309 existing tests still pass — this is the regression bar.
- No new heavy deps (PyMuPDF4LLM is ~5MB wheel).

What this design is NOT:
- Not optimized for 10k papers (would need real embeddings + HNSW).
- Not optimized for <1s response (vector search is keyword-based, ~10ms).
- Not multi-agent (single ReAct loop, no orchestration yet).

---

## 8. Open questions

1. **PyMuPDF4LLM** acceptable?  Or MarkItDown (covers 15+ formats)?
2. **Should we deprecate `src/tools.py`?**  We now use MCP-style tools
   via `mcp_client.py`.  Keeping `src/tools.py` as a thin shim avoids
   ripping it out, but is it worth it?
3. **Memory compaction**: skip for v1.8.2, but when should we revisit?
   My proposal: when `memory_units` count > 200.

---

## 9. Self-critique log

(Things I almost added, then removed.  Keeping as a guard against
re-introducing them.)

- ~~"ReAct driver" new module~~ → already have chat() + tools.py.
- ~~"bag-of-words embedding"~~ → dishonest, just keyword match instead.
- ~~"compact with LLM summarization"~~ → premature.
- ~~"JSON Schema enforced outputs"~~ → chat_simple is enough.
- ~~"Tier 2 as separate concept"~~ → state['...'] dict already covers it.
- ~~"4-table schema"~~ → 2 tables + JOIN.
- ~~"separate files for vector vs graph"~~ → one Memory class, one DB.

Half the original design, same goals.