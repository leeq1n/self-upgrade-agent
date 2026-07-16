L0: Long-form model strategy — model comparisons, latency, cost.
Last P20-verified: 2026-07-13

# Model Strategy & Deployment — v1.8.1
> L0: Full text of model strategy.  Companion to MODEL_STRATEGY.md.

> Complete guide to local model deployment for self-upgrade-agent.
> Updated 2026-07-07 after Qwen-AgentWorld discovery + dual-server setup.

## TL;DR

Two llama-server instances on AGX Thor, accessed via HTTP:

| Port | Model | Size | Purpose |
|---|---|---|---|
| **38000** | Qwen3-VL-30B-A3B-Instruct (Q8_0) | ~31 GB | Main reasoning + VL |
| **38001** | Qwen-AgentWorld-35B-A3B (UD-Q4_K_M) | ~22 GB | Environment simulation |

Total VRAM: ~53 GB out of 128 GB available. ~75 GB headroom.

Both are **MoE** (3B active), so per-call latency is fast.
Both expose **OpenAI-compatible API** (chat completions, etc.).
Main model supports **vision** (mmproj F16).

## Why These Models

### Qwen3-VL-30B-A3B-Instruct (main)

- **Multimodal**: can read paper figures (architecture diagrams, results)
- **Fast**: 30B total / 3B active MoE = single-call latency similar to small models
- **Q8_0 quality**: nearly lossless, ~31 GB VRAM fits comfortably
- **Tuned for thinking mode**: enable for deep analysis (paper relevance, patch design)

### Qwen-AgentWorld-35B-A3B (helper)

- **2026-06-24 release** — newest Qwen model
- **Native world model**: trained with environment simulation as objective
- **7 domains**: MCP, Search, Terminal, SWE, Android, Web, OS
- **Beats Qwen3.6-Plus on AgentWorldBench** (56.39 vs 50.81)
- **Use for**: simulating patch effects before real harness runs

## llama-server Launch Commands

### Main: Qwen3-VL-30B (port 38000)

```bash
llama-server \
  --model /workspace/Documents/models/GGUF/Qwen3-VL-30B-A3B-Instruct-GGUF/Qwen3VL-30B-A3B-Instruct-Q8_0.gguf \
  --mmproj /workspace/Documents/models/GGUF/Qwen3-VL-30B-A3B-Instruct-GGUF/mmproj-Qwen3VL-30B-A3B-Instruct-F16.gguf \
  --alias qwen3-vl-30b-a3b \
  --host 0.0.0.0 \
  --port 38000 \
  -ngl 99 \
  --ctx-size 8192 \
  --cache-ram 0 \
  --chat-template-kwargs '{"enable_thinking":true}'
```

| Flag | Why |
|---|---|
| `--mmproj` | vision projector (required for image input) |
| `--alias` | friendly name for API clients |
| `-ngl 99` | all layers to GPU (128 GB enough) |
| `--ctx-size 8192` | 8K context (more than enough for our prompts) |
| `--cache-ram 0` | disable RAM cache, fixes Qwen3-VL KV cache bug |
| `--chat-template-kwargs '{"enable_thinking":true}'` | default thinking mode ON |

### Helper: Qwen-AgentWorld (port 38001)

```bash
llama-server \
  --model /workspace/Documents/models/GGUF/Qwen-AgentWorld-35B-A3B-UD-Q4_K_M.gguf \
  --alias qwen-agentworld-35b-a3b \
  --host 0.0.0.0 \
  --port 38001 \
  -ngl 99 \
  --ctx-size 16384 \
  --cache-ram 0 \
  --chat-template-kwargs '{"enable_thinking":false}'
```

AgentWorld doesn't need thinking (it's a simulator, not a creative reasoner).

## .env Template

```bash
# Main model (Qwen3-VL-30B-A3B)
LLM_BASE_URL=http://172.16.121.200:38000/v1
LLM_MODEL=qwen3-vl-30b-a3b
LLM_MODELS=qwen3-vl-30b-a3b
LLM_TIMEOUT=300
LLM_TOTAL_TIMEOUT=1800
LLM_MAX_TOKENS=2048

# Helper: Qwen-AgentWorld (environment simulation)
LLM_AGENT_WORLD_URL=http://172.16.121.200:38001/v1
LLM_AGENT_WORLD_MODEL=qwen-agentworld-35b-a3b
LLM_AGENT_WORLD_ENABLED=true
```

## Thinking Mode Strategy

| Node | thinking | budget | Why |
|---|---|---|---|
| `node_filter` | **off** | - | keyword scoring is enough, speed matters |
| `node_research` | off | - | data fetching, no reasoning |
| `node_implement` (patchgen) | **on** | 4096 | needs to design code, deep reasoning |
| `node_evaluate` | **on** | 1024 | decision is critical |
| `node_decide` | **on** | 1024 | final KEPT/REVERTED logic |
| `node_read_paper` (v1.8.2) | **on** | 4096 | analyze paper, extract innovation |
| `node_skill_audit` | off | - | pure DB stats |

**Per-call override via API** (llama-server respects request-level chat_template_kwargs):

```json
{
  "model": "qwen3-vl-30b-a3b",
  "messages": [...],
  "chat_template_kwargs": {"enable_thinking": false}
}
```

## Why NOT Router Mode

llama-server has Router Mode (`--models-preset`) that loads multiple models in one process, but:
- **Multimodal support is immature** (mmproj + router not well-tested)
- **VRAM swap overhead**: 5-15s on each model switch
- **Your setup already works** (128 GB holds both, no swap needed)
- **Keep it simple** — 2 ports, 2 endpoints, clear ownership

Use Router Mode only if: 5+ models, VRAM-constrained, want single endpoint.

## Why NOT vLLM

For your specific setup:
- llama.cpp **GGUF** is more flexible (Q4_K_M, MXFP4_MOE, IQ2_XXS all available)
- llama.cpp **offloads better** when running 235B on 128 GB
- vLLM doesn't have MXFP4_MOE / Unsloth dynamic quants
- You already verified Qwen3-VL-235B on llama.cpp (proven workflow)

Use vLLM only if: you need 10+ concurrent users, or want a tightly integrated stack.

## Future: Adding More Models

When v1.8.2+ needs a 3rd model (e.g., Qwen3-VL-235B for deep research):

```bash
llama-server -m Qwen3-VL-235B-A22B-Instruct-Q3_K_M.gguf \
  --alias qwen3-vl-235b-a3b --port 38002 -ngl 99
```

Update `.env`:
```bash
LLM_DEEP_RESEARCH_URL=http://172.16.121.200:38002/v1
LLM_DEEP_RESEARCH_MODEL=qwen3-vl-235b-a3b
```

Code path (`src/llm.py`) checks env, picks endpoint per call. No code changes needed.

## Chrome DevTools MCP (for v1.8.2+)

Your machine has Chrome + `mcp__chrome_devtools__*` tools. For **deep paper analysis**:

- **v1.8.1**: skip Chrome, use arxiv API (already works)
- **v1.8.2+**: add `web_browse_chrome(url, action)` in `src/tools.py`
  - When LLM needs full paper text, it calls this tool
  - Uses your Chrome via MCP (you have it)
  - Returns rendered HTML / text / figure descriptions

**Important**: self-evolve loop runs on **AGX Thor** (headless), not your machine.
- v1.8.1: arxiv API works on Thor (we have httpx + paper data)
- v1.8.2: Chrome MCP tools only work on **your machine**, not Thor
- For Thor-side browsing: need headless Chrome wrapper (later)

## Verifying Setup

After launching both servers:

```python
import httpx

# Should get 200 OK
r = httpx.get("http://172.16.121.200:38000/v1/models")
print("Port 38000:", r.status_code, r.json())

# Should work
r = httpx.post("http://172.16.121.200:38000/v1/chat/completions",
    json={"model": "qwen3-vl-30b-a3b",
          "messages": [{"role": "user", "content": "Hi"}],
          "max_tokens": 20},
    timeout=30)
print("Chat:", r.json()["choices"][0]["message"]["content"])
```

## After Setup: Run the Pipeline

```bash
# Edit .env with the URLs above
python run_stable.py 1 0
```

Expected:
- ~3-5 min per round (was 5-15 min with Qwen3.6-27B thinking-only)
- papers fetched with real arxiv data (already verified via Chrome)
- agent makes real KEPT/REVERTED decisions
- decision_log records WHY each round failed/succeeded
