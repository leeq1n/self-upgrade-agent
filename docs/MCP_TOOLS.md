# MCP tools available for this project

> L0: Project-portable reference of MCP tools that an
> agent (any agent, including hermes-independent) can
> use to interact with this project.  Per user meta-rule
> 2026-07-14 "新agent 不依赖hermes也能学到知识".
> Last P20-verified: 2026-07-14 (initial; update as
> tools evolve)

## What this doc is for

Per project audit (commit 50): MCP tool knowledge was
**hermes-runtime-only** — a fresh agent without hermes
context couldn't discover what tools were available
or how to use them.

This doc is the **L0 reference** for MCP tools in this
project.  Per P20 progressive disclosure:
- **L0** (this header + section headers): 30-second
  orientation
- **L1** (per-tool description): 1-paragraph per tool
- **L2** (per-tool "When to use" + examples): full
  detail

A new agent reading this doc should be able to decide
**which tool to reach for** without needing hermes
runtime context.

## Tools available (5 MCP servers)

| Server | Purpose | When to use |
|---|---|---|
| `chrome_devtools` | Browser automation (navigate, click, fill, screenshot) | Web testing, scraping, UI interaction |
| `llm_wiki` | Knowledge graph across projects | Cross-project context, related-project state |
| `zotero` | User's literature library (search, add, annotate) | Reading papers, citing in research |
| `sciverse` | Citation-grade academic search | Academic lit review, full-text snippets |
| `mineru` | PDF/document parsing (OCR + layout) | Extract text from PDFs, images |

## L1 — Per-tool description

### `chrome_devtools`

Browser automation tool.  Open pages, click elements,
fill forms, take screenshots, evaluate JavaScript,
list console messages + network requests.  Use for
**web testing, scraping, or any task that requires
interacting with a browser**.

### `llm_wiki`

Knowledge graph that links multiple projects.  Can
search across projects, list files, read content.
Use for **cross-project context discovery** (e.g.
"is there a related project for X?").

### `zotero`

User's curated literature library.  Search by
keyword/author/title, get metadata, get full text
(PDFs), create annotations, export bibliography.
Use for **reading papers and citing in research**
(per P2 搜资料 + LITERATURE workflow).

### `sciverse`

Citation-grade academic search.  Semantic search
(natural language query) + structured search (filters
for year/journal/author).  Returns snippets with
metadata.  Use for **academic literature review**
when `zotero` doesn't have what you need.

### `mineru`

PDF/document parser.  Handles scanned PDFs via OCR.
Returns structured markdown.  Use for **extracting
text from PDFs or images** that aren't text-searchable.

## L2 — When to use (decision tree)

```
Need to interact with a web page?
  → chrome_devtools
Need to read/store literature?
  → zotero (preferred; user's curated)
Need to find academic papers?
  → sciverse (semantic + structured search)
Need to extract text from PDF/image?
  → mineru
Need to find related project state?
  → llm_wiki
```

## L2 — Anti-patterns

- **Don't use chrome_devtools for non-browser tasks**
  (file I/O, terminal commands, etc.)
- **Don't use sciverse when zotero has the paper**
  (zotero is user's curated; sciverse is general
  academic search)
- **Don't use llm_wiki for current project state**
  (use `search_files` + `read_file` for current
  project; llm_wiki is for cross-project)
- **Don't use mineru for text-extractable PDFs**
  (modern PDFs have text layer; use `zotero` or
  `web_extract` for those)

## L2 — Tools NOT in this project

The following tools are **NOT** part of this project
even if available in the runtime:

- `todo` (internal session tool, not for project)
- `memory` (agent-only, project-agnostic)
- `terminal` (always available, not MCP-specific)
- File tools (read_file, write_file, patch, etc.)
  — always available, not MCP-specific

## L2 — Cross-references

- `docs/OPERATING_RULES.md` — M-rules for using
  these tools (per M-intent-parsing, M-task-summary,
  etc.)
- `docs/LITERATURE.md` + `LITERATURE_DETAIL.md` —
  workflow patterns for `zotero` + `sciverse`
- `docs/PRINCIPLES.md` P2 (搜资料, 不拍脑门) —
  the principle that drives `zotero`/`sciverse` use
- `~/.hermes/skills/agent-onboarding/references/M_RULE_AUTHORING.md` —
  M-rule authoring pattern (this doc follows it)

## Per P20 progressive disclosure self-application

This doc IS P20 applied to MCP tools:
- L0: 1-line header + table (above)
- L1: 1 paragraph per tool (above)
- L2: decision tree + anti-patterns (above)

A fresh agent reading L0 alone can decide which tool
to use.  Reading L1 adds 1-paragraph detail.  Reading
L2 adds full decision tree + cross-refs.

## Per P11 摘要+引用 + P13 no orphan

- This doc is the **summary** (L0 + L1 + L2 above)
- Per-tool "When to use" examples are at L2 inline
  (not split to _DETAIL companion, per P7 奥卡姆)
- AGENTS.md "Read first" should add this doc (per
  commit 53)

## Per P7 奥卡姆

- 5 tools (not 50)
- L0 table + L1 paragraphs + L2 decision tree
  (not exhaustive per-tool docs)
- Anti-patterns段 for common misuses (saves
  future error)

## Per P22 stuck→plan

When you don't know which tool to use:
1. Check this doc's L0 table.
2. If still unclear, read L1.
3. If decision tree needed, read L2.
4. If still unclear, ask user (per M-intent-parsing).

## See also

- `docs/PRINCIPLES.md` P2 (搜资料 principle)
- `docs/OPERATING_RULES.md` M-intent-parsing (when
  to ask vs guess)