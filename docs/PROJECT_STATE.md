# PROJECT STATE — Single Source of Truth (2026-07-08)

> This is THE doc.  Read this first.
> Goal: orient a new agent (or model) in 5 minutes.
> Replaces 15 other docs that were deleted (2026-07-08 cleanup).

## 1. Goal (1 sentence)

A self-improving agent that reads papers, modifies its own code
in a target module, verifies via harness, and either keeps or
reverts.  Local framework + remote minimax LLM API.

## 2. Current state (v2.0.0)

| | |
|---|---|
| **Branch** | `v2.0.0-minimal` |
| **Active code** | `src/v2_agent.py` (~250 LOC) + `tests/test_v2_agent.py` (16 tests) |
| **Test count** | 386 PASS + 5 skip + 0 fail |
| **Tag** | (none yet) |
| **Last commit** | `d853ed2 feat(v2.0.0): minimal self-improving agent` |

## 3. Deprecated (do not use, do not extend)

| | |
|---|---|
| `src/pipeline_lg.py` (1024 LOC) | 8-node LangGraph, replaced by `v2_agent.improve()` |
| `src/react.py` (280 LOC) | ReAct driver, not used by v2 |
| `src/langchain_bridge.py` (170 LOC) | HermesChatModel wrapper, not used by v2 |
| `src/mcp_client.py` (300+ LOC) | MCP registry, not used by v2 |
| `src/memory_server.py` (376 LOC) | 4-tier memory, replaced by `v2_agent` SQLite table |
| `src/filter.py` | pre-filter 13 patterns, **rejected** (fail-OPEN principle) |
| `src/goals.py` (306 LOC) | goals registry, not used |
| `src/tools.py` (301 LOC) | tool registry, not used |
| `experiments/langgraph_*.py` | POC, not used |

## 4. v2_agent minimal API (THE thing to use)

```python
from src.v2_agent import improve, Paper

result = improve(
    paper=Paper(arxiv_id="...", title="...", abstract="..."),
    target_module="core/planner.py",  # or any module
)
# Returns Patch(function, test, module) or None
```

Pipeline (1 LLM call, 1 harness test):
  1. RAG: `memory_find_similar(paper)` — keyword overlap
  2. Build prompt (paper + similar + target module)
  3. `_chat()` — single LLM call (thinking OFF, max_tokens=8192)
  4. `_parse_patch()` — lenient JSON
  5. `_run_harness()` — subprocess + test function extraction

## 5. Constraints (from user + literature)

### From user (verbatim or paraphrased)
- **奥卡姆** — fewer rules, not more.  30+ fix commits already failed.
- **Fail-OPEN** — pre-filters must let LLM decide, not keyword.
- **整理 → 思考 → 行动** — organize first.
- **搜资料, 不拍脑门** — read literature before designing.
- **ReAct 行动链** — input → thought → output loop.
- **MCP-everything** — tools/memory/agent as MCP calls (but minimal).
- **用户掌控 LLM** — agent does not change API keys.
- **日志保留** — pre-run no GC, post-run archive.

### From literature (read 9 papers)
- **Self-Refine regresses on code gen** (paper: "One Step Forward, Two
  Steps Back").  Don't add self-refine loops.
- **Multi-agent 41-86% fail rate** (UC Berkeley).  Don't multi-agent.
- **Constitutional AI** is training-time, not inference.  Don't add.
- **RAG (memory-augmented) works** for code gen tasks.
- **Minimal harness** (Self-Harness paper) is the right starting point.
- **Verifiable + looped** is the recipe that works (Nate Berkopec 2026).

## 6. Mistakes already made (do not repeat)

| # | Mistake | Consequence | Lesson |
|---|---|---|---|
| 1 | 19 fix commits on master before branching | Branch hygiene violated | Always branch first, tag at the end |
| 2 | 4 hypothesis-based fixes without tracing root cause | Each fix was wrong | Trace code, don't guess |
| 3 | Hardcoded `_REJECT_TITLE_PATTERNS` + `_paper_is_obviously_unrelated` | Rejected valid papers | Use LLM judge, not keyword |
| 4 | `state["scored_papers"] = []` after memory write (commit 9a37d36) | Pipeline silently broke | Memory writes must not mutate pipeline state |
| 5 | 3 amend + revert cycles in one session | Polluted git history | 1 commit = 1 decision; no partial commits |
| 6 | Wrote 2 design docs (DESIGN_SELF_EVOLUTION + AGENT_SELF_DISCIPLINE) | Did not change behavior | Process beats intention; enforce via mechanism |
| 7 | Read 3-4 papers and committed based on them | Designs based on unconfirmed applicability | Read paper limitations + multiple sources |
| 8 | Truncated LLM output + retry instead of letting it run | Wasted time + bad results | Let the model finish; one full run > three aborted runs |

## 7. minimax API configuration

```
LLM_BASE_URL=https://api.minimaxi.com/anthropic
LLM_MODEL=MiniMax-M2  (or M2.5 / M3)
LLM_API_KEY_0=<user-managed, never in git>
LLM_TIMEOUT=300
LLM_TOTAL_TIMEOUT=1800
LLM_MAX_TOKENS=8192  (default; 2048 was for ModelScope era)
```

Key facts:
- M2 has 204.8K context, M3 has 1M.  2048 default was way too small.
- Thinking OFF in patchgen — reasoning lives in the prompt.
- `LLM_CONFIG.ready` allows `api_keys=[]` for local server.

## 8. Next step (1 thing)

**User runs `run_stable.py 1 0` with a FIXED paper (2310.02170 DyLAN)**
to verify v2_agent.improve() makes 1 round KEPT.

If KEPT: add paper selection (back to variable papers).
If NOT KEPT: debug (likely test extraction or patch format).
