# PROJECT STATE — Where We Are (2026-07-07)

> Read this first if you are a new agent (or human) joining this project.
> Goal: orient you in 5 minutes.

## TL;DR

- **What**: A self-upgrading agent.  Daily loop: search arxiv → filter → patch → A/B + harness → decide → mark seen.
- **Status**: v1.8.1.  7+ commits this session.  270 unit tests + 5 skip + 0 fail.
- **Working tree**: clean, on `master`.
- **One thing to know**: v1.8.1 has **emergent subsystems** (memory policy, goals registry) — they start empty.  LLM is expected to populate them via patchgen over time.

## Project goals (your 2026-07-07 statement)

> "做一个能自主升级的 agent, 它可以通过 selenium 等工具每天通过搜索最新的论文,
> 筛选具体方法和趋势, 尝试将适合的创新点加在这个 agent 上, 对比这个功能的效果提升和代价,
> 最终决定是否留下, 使用类似 bootloader 的方法切换代码, 也就是说这个模型需要调用大模型改进自己的代码.
> 它应该有 skill 和新增创新点的生命周期管理, 每隔一段时间, 需要进行一次 skill/创新点
> 的使用频率统计、质量评估与优化/销毁.  项目应当有干净的接口、实现代码与文档.
> 项目应该有稳定性、可靠性、可用性和健壮性.  有 harness 和 loop 的思想."

## Architecture (3 layers)

```
Layer 1 — INVARIANT (these don't change):
  harness-first decision (src/decide.py)
  switcher atomic write (src/switcher.py)
  skill lifecycle (src/skill_lifecycle.py)
  preflight safety (src/pipeline_lg.py:_safety_restore_planner)

Layer 2 — EMERGENT (LLM is expected to evolve these):
  src/goals.py: registry of goal strategies.  Starts empty.
  src/learning.py:apply_memory_policy: memory trim.  Starts noop.

Layer 3 — USER INTERFACE:
  python -m core.agent "task"     # use the agent
  python run.py [--live]          # run self-evolve
  python -m self_upgrade <subcmd> # unified CLI
  python run_stable.py [target] [gap]  # convergence test
  python collect_papers.py 50 "topic" # bulk paper collection
```

## Current state

### Done in v1.8.0 / v1.8.1 (this session, 7+ commits)

| Commit | Feature |
|---|---|
| f37e48c | Real Python harness — 8 unit tests for core/planner.py |
| a7d91d5 | Harness wired into pipeline_lg + decide |
| 3247adc | node_evaluate e2e + skill_lifecycle_static + 1 round live |
| 39eb9f2 | node_skill_audit (8th node, 0 LLM) |
| 55bc8a8 | audit_history table |
| 5372b93 | `self_upgrade audit` CLI subcommand |
| 5401f0b | ISSUES + PROJECT_BRIEF updates with 5-round results |
| f41f21a | run_1round.py wrapper + provider config docs |
| e436412 | RELEASE_v180.md |
| 970d76c | Day 7 — local qwen3.6-27B + run_stable.py |
| 330801f | (other agent) P0 fixes — atomic manifest write + surgical merge |
| e0ce870 | (other agent) ISS-003 upgrade to P0 |
| 2b32628 | seen-papers filter + streaming LLM + collect_papers |
| 5e0adac | Streaming for core/agent + design philosophy docs |
| 0b76e55 | run_stable patches both namespaces + seen_papers gc |
| d3ab5fa | Emergent memory policy (let LLM design it) |
| f7bc951 | Emergent goals (extensible + anti-lock-in + 奥卡姆) |

### Open issues (per ISSUES.md)

- **ISS-014**: ModelScope instability (still open, lower priority now we have local qwen3.6)
- All P0/P1 from older issues are resolved.

## What works (verified)

- ✅ `pytest tests/ --deselect bloat --deselect slow` → 270 PASS, 5 skip, 0 fail
- ✅ `python -m self_upgrade gc` → runs, shows seen_papers status
- ✅ `python -m self_upgrade audit` → shows audit history
- ✅ `python -m self_upgrade status` → shows planner version + history.db
- ✅ `python -m src.llm_stream` → streaming works (local qwen3.6)
- ✅ `python collect_papers.py --help` → CLI works

## What is BROKEN or NOT verified

- ❌ `python run_stable.py N` — pipeline ran but every round `decision=None`.  Root cause:
  - arxiv search returns 0 papers (maybe network?) OR
  - patchgen returns 0 candidates OR
  - LLM timeout under 30 min budget
  - **Need a real LLM network test to debug**
- ❌ `python run.py` — same issue (depends on real LLM)
- ❌ `python -m core.agent "task"` — works in streaming mode but only smoke-tested

## What's expected but NOT implemented (future agent's job)

| Priority | Feature | Notes |
|---|---|---|
| HIGH | **Context-aware LLM prompts** (Step 3-5 of plan) | node_research / node_implement / sandbox |
| HIGH | **Real LLM end-to-end run** | After Step 1-5 are in place |
| MED | Auto-promote option (when cfg.pipeline.auto_promote=True) | Currently decision=KEPT is manual |
| MED | `node_evaluate` fail-fast: check harness BEFORE arm 2 | Saves LLM tokens |
| LOW | Split src/pipeline_lg.py (currently 1024 lines) | Decided NOT to do (奥卡姆) |
| LOW | `core/agent.py` agent loop optimization | Works, just slow on local model |

## Emergent subsystems state

### src/goals.py (commit f7bc951)
- Registry: **empty** (intentional, emergent)
- Fallback: `fallback_explore` always available
- LLM can `register(name, description, decide_fn)` via patchgen

### src/learning.py:apply_memory_policy (commit d3ab5fa)
- Default: **noop** (intentional, emergent)
- Hard ceiling: `MAX_LEARNING_ROWS = 10000` (fuse, not policy)
- LLM can edit `apply_memory_policy` or pass `--memory-policy module:fn`

### src/llm_stream.py (commit 2b32628)
- chat_stream(messages, ...) yields tokens
- Used by `core/agent.py` (default `stream=True`)
- NOT used by `pipeline_lg.py` (sequential node, streaming doesn't help)

## Constraints (奥卡姆 — don't violate)

1. **Don't hard-code strategies** in src/goals.py — they should emerge
2. **Don't hard-code memory policies** — they should emerge
3. **Don't hard-code "what makes a good patch"** — let harness decide
4. **Don't split src/pipeline_lg.py** unless absolutely needed (1024 lines, but cohesive)
5. **Don't add features "for completeness"** — every feature must solve a real pain

## Open risks

1. **LLM context window**: long prompts may exceed model limits.  Currently we don't summarize.
2. **arxiv search scope**: only 90 days lookback.  Older landmark papers missed.
3. **No compatibility check**: patches may target old Python / old LangGraph.
4. **No "what worked before" feedback**: filter doesn't see last_outcome.

## Recommended next actions (Step 1-6 of plan)

1. Write CONTEXT_FOR_LLM.md (LLM calling guide)
2. Add seen_papers summary to node_research prompt
3. Add last_outcome to node_implement prompt
4. Add sandbox compat check (Python version, etc.)
5. Run end-to-end with real LLM
6. Commit + report

## One-page "if you only read one thing"

→ Read `docs/DESIGN_PHILOSOPHY_v181.md` + `docs/MEMORY_DESIGN.md` + `docs/GOALS_DESIGN.md`.
   These three docs explain what is fixed, what is emergent, and why.