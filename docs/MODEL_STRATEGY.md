---
description: "Current LLM, fallback chain, and deployment notes"
status: "summary"
---

# MODEL_STRATEGY — brief

**Current**: minimax M2 (cloud API, no quota issues).
`LLM_BASE_URL=https://api.minimaxi.com/anthropic`, model `MiniMax-M2`.

**Fallback chain** (configured in `src/llm.py`):
- minimax M2 (active)
- minimax M3 (when available)
- (legacy) local Qwen3-VL-30B + Qwen-AgentWorld on AGX Thor (port 38000/38001) — historical

**Config (env vars)**:

- `LLM_BASE_URL` — endpoint
- `LLM_MODEL` — primary model name
- `LLM_API_KEY_0` — primary key (never in git; user-edited)
- `LLM_TIMEOUT=300` (cloud APIs need longer than local)
- `LLM_TOTAL_TIMEOUT=1800`
- `LLM_MAX_TOKENS=8192` (default; v1 default was 2048, too small)

**Note**: `LLMConfig.from_env()` auto-loads `.env` (added 2026-07-08
to fix REPL 401).  Without this, REPL/jupyter runs would fall back to
hardcoded ModelScope defaults and 401.

Full local-deployment detail (Qwen3-VL settings, llama-server args,
port mappings, MXFP4 vs Q8 tradeoffs) is in
[`MODEL_STRATEGY_DETAIL.md`](MODEL_STRATEGY_DETAIL.md).

## References

- INDEX: [INDEX.md](INDEX.md)
- Project state: [PROJECT_STATE.md](PROJECT_STATE.md)
- User intent: [USER_INSIGHTS.md](USER_INSIGHTS.md)
- Constraints: [CONSTRAINTS.md](CONSTRAINTS.md)
- Pending tasks: [../../TODO.md](../../TODO.md)
- Done tasks: [../../DONE.md](../../DONE.md)
- Full deployment notes: [MODEL_STRATEGY_DETAIL.md](MODEL_STRATEGY_DETAIL.md)
