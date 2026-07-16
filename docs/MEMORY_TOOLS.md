# Memory tools decision matrix (per 2026-07-13 research)
Last P20-verified: 2026-07-13

> L0: Reference doc for which memory tool to use when.  Designed
> to be loaded on-demand, not always-in-context (per AGENTS.md
> 300-line cap; per Cognition "context engineering is the #1
> job").  Read this when you're unsure which tool to use; default
> is to use **no** extra tool.

## Why this doc exists

Per Karpathy ("context is RAM, not storage"), Mem0 ("context
window is RAM, not database"), and Reddit ("the agent should
just read from it on boot and write to it on tool execution.
It shouldn't be the database"):

- The LLM's context window is **working memory**, not
  long-term storage.
- Each tool use costs context tokens.
- Stuffing everything into context = context rot, context
  pollution, context confusion.
- Decision tree approach: pick the **cheapest** tool that
  answers the question.

## Tool inventory (with cost analysis)

| Tool | Scope | Cost (tokens) | When to use |
|------|-------|---------------|-------------|
| **AGENTS.md** | cross-project | low (1 read) | session start (always) |
| **search_files** (ripgrep) | repo | low per query | find content in repo |
| **read_file** | any file | high per file | full file content needed |
| **PRINCIPLES.md** (L0) | project | low (already in memory block) | rare; P-n pointers |
| **PRINCIPLES_DETAIL.md** (L2) | project | high (full P-n text) | only when P-n detail needed |
| **session_search** (Hermes DB) | cross-session | high per query | prior session content needed |
| **TodoWrite** | this session | medium | multi-leaf task (≥3 steps) |
| **memory block** (system prompt) | always | always-on | user/env persistent facts |
| **Temp snapshot** (`hermes-snapshot-*.md`) | session | low per read | resume after context overflow |
| **web_search** | web | medium | new pattern not in docs |
| **sciverse (MCP)** | academic | medium | citation-grade academic lookup |
| **arxiv (MCP)** | arxiv preprints | medium | preprint search |
| **zotero (MCP)** | user's library | medium | user's curated papers |
| **llm_wiki (MCP)** | knowledge graph | medium | cross-project entity lookup |
| **delegate_task** | subagent | high | subagent (independent context) |

## Decision tree (when you need X, use Y)

```
X = "I need to onboard"
  → read AGENTS.md (always at session start)

X = "I need to know which P-n applies"
  → AGENTS.md "Hard rules"段 (already loaded)
  → if detail needed: read PRINCIPLES.md (L0)
  → if L2 detail needed: read PRINCIPLES_DETAIL.md

X = "I need to find content in repo"
  → search_files (ripgrep) — cheap
  → only if exact match needed: read_file

X = "I need prior session context"
  → session_search (expensive — use only when truly needed)
  → otherwise: load Temp snapshot if exists

X = "I need to track multi-step task"
  → TodoWrite (≥3 steps; for 1-2 step tasks, skip)

X = "I need to resume after context overflow"
  → read Temp snapshot first
  → then load AGENTS.md

X = "I need to learn a new pattern (not in docs)"
  → web_search or sciverse (per P2 + search-then-update)
  → after search: update the relevant doc (search-then-update contract)

X = "I need a subagent for independent work"
  → delegate_task (per project autonomy rules)
```

## Anti-patterns (do NOT do)

- **Don't read PRINCIPLES_DETAIL.md end-to-end** at session
  start.  Read AGENTS.md → it tells you which section to
  read if needed.
- **Don't session_search** "just in case" prior session is
  relevant.  It almost never is.
- **Don't re-read** files you've already read in this
  conversation.  Working context should hold them.
- **Don't TodoWrite** for 1-2 step tasks.  The cost of
  writing the todo list exceeds the benefit.
- **Don't stuff** "important content" into chat replies
  "to remember it".  Use external tools (file write, TodoWrite,
  snapshot).
- **Don't** load the Temp snapshot "just to be safe".  Only
  when you actually need to resume.

## Per project cap rules (per AGENTS.md)

- AGENTS.md ≤ 300 lines (cap).  This doc (MEMORY_TOOLS.md)
  is the place to put decision matrices, not AGENTS.md.
- PRINCIPLES.md ≤ 10KB soft target.  PRINCIPLES_DETAIL.md
  for full text.
- INDEX.md L0/L1 only; L2 in topic-specific docs.

## See also

- AGENTS.md — onboarding contract (L0 line + read-order +
  hard rules + decision pointer to this doc).
- PRINCIPLES.md — P-n list (P1-P25).  P11 (摘要+引用)
  is the rule that keeps AGENTS.md short.