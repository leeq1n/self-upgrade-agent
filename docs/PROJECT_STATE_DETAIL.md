L0: Long-form project state — version history, test counts, vision.
Last P20-verified: 2026-07-10

---
description: "Detailed technical history of the project (long form)"
status: "reference"
---

# PROJECT_STATE_DETAIL — long form

> Detail file.  Read [PROJECT_STATE.md](PROJECT_STATE.md) first
> (it's the 1-paragraph summary).  This file expands each section.

## Deprecated modules

These 11 modules in `src/` are historical artifacts of v1.8.x and
should NOT be extended, imported, or relied on by new code:

| Module | Why deprecated |
| --- | --- |
| `pipeline_lg.py` | 8-node LangGraph state machine replaced by 3-module v2 |
| `react.py` | ReAct driver driver — v2 uses harness test directly |
| `langchain_bridge.py` | HermesChatModel wrapper — not used by v2 |
| `mcp_client.py` | MCP registry abstraction — v2 keeps things direct |
| `memory_server.py` | 4-tier memory complexity — v2 has 1 SQLite table |
| `filter.py` | Pre-filter 13 patterns — violates fail-OPEN principle |
| `goals.py` | Goals registry — not exercised |
| `tools.py` | Tool registry — not exercised |
| `_archived/` | Earlier iterations of pipeline_lg |
| `benchmark.py` | (not yet evaluated) |
| `decide.py` | (not yet evaluated) |

When in doubt, grep first to confirm a deprecated module is not
re-imported by new code.

## Mistakes made (do not repeat)

| # | What | Why it's wrong |
| --- | --- | --- |
| 1 | 19 fix commits on master before branching | Branch hygiene violated; user wants tag-then-branch |
| 2 | 4 hypothesis-based fixes without tracing | Each fix was wrong; trace first |
| 3 | Hardcoded `_REJECT_TITLE_PATTERNS` | Violates fail-OPEN; LLM should judge |
| 4 | `state["scored_papers"] = []` after memory write (commit `9a37d36`) | Pipeline silently broke; memory writes must not mutate pipeline state |
| 5 | 3 amend + revert cycles in one session | Polluted git history; 1 commit = 1 decision |
| 6 | 2 design docs that didn't change behavior (DESIGN_SELF_EVOLUTION, AGENT_SELF_DISCIPLINE) | Process beats intention; enforce via mechanism |
| 7 | Read 3-4 papers and committed based on them | Designs based on unconfirmed applicability; read more |
| 8 | Truncated LLM output + retry | Wasted time + bad results; let the model finish |
| 9 | Commit before tracing the user's actual run | Surfaces bugs only when you run, not when you test |

## How it works (data flow)

```
        Paper
          |
          v
   v2_agent.improve()
       |   (1 LLM call + harness PRELUDE auto-imports typing)
       v
      Patch (function + test + module)
       |
       v
   v2_apply.apply_patch()
       |   (snapshot -> AST replace -> atomic write)
       v
   file modified + snapshot kept
       |
       v
   run_project_tests()
       |   (pytest test_path with HERMES_SKIP_NETWORK=1)
       v
      rc=0  -> KEPT     + keep snapshot
      rc!=0 -> REVERTED  + restore from snapshot
       |
       v
   RoundResult returned
```

DECISION IS HARD RULE (test pass/fail), not LLM-judged.  This avoids
the coherence trap where the model judges its own output.

## File map

```
src/
  v2_agent.py    <- generation: paper -> Patch
  v2_apply.py    <- deployment: atomic file rewrite
  v2_round.py    <- decision: KEPT/REVERTED based on tests
  llm.py         <- chat() (existing, used by all three)
  config.py      <- AppConfig / LLMConfig (existing)
  (deprecated modules — see table above)

tests/
  test_v2_agent.py         <- 26 unit tests
  test_v2_apply.py         <- 24 unit + joint tests
  test_v2_round.py         <- 7 fast + 1 slow test
  test_v2_integration.py   <- 10 joint tests (wire v2 modules together)
  test_llm.py              <- 31 tests for the chat() layer
  (everything else:        <- 350+ tests for legacy v1.8.x code, still kept
                             for regression purposes)
```
