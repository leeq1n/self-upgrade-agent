# TODO —

Each task is a checkbox.  To claim: change `[ ]` to `[x]` and move
the line into DONE.md.  Keep this list SHORT and CURRENT; older
completed work lives in DONE.md.

> Convention: `- [ ]` = not started, `- [x]` = done, `- [/]` = in progress.

## Completed (history, see DONE.md for details)

- [x] **Failure → regression test pipeline** — v2.3 (commit `0dc68cb`)
- [x] **Automatic replay of failure log** — v2.3.1 (commit `216f7e0`)
- [x] **Unified CLI** — v2.4.0 (commit `2442d09`)
- [x] **Gitignore cleanup** — v2.4.1 (commit `a5d3029`)
- [x] **Multi-paper reading** — v3.0.0 (commit `da3ba26`)
- [x] **Multi-paper selection** — v3.0.1 (4 sub-steps, 4 stage gates)
- [x] **Hotfix timeout bump** — v3.0.1 (commit `be0072c`)
- [x] **Progress markers** — v3.0.1 (commit `eb70e90`)
- [x] **Replay default = inspect** — v3.0.2 step 1 (commit `3d74ba8`)

## In progress (current 1-2 sessions)

### v3.0.2 — think-execute harness (LITERATURE: Self-Harness, Lilian Weng)

Per user feedback 2026-07-10: '分治, 多次将功能分块, 直到足够小,
每个功能测通了再联合起来测, 继续你认为正确的方向, 中间记得
记录, 还有一开始那些关于 agent 的知识也要灵活运用'.

- [/] **step 1** — replay default = inspect (fast, no LLM)
      DONE in `3d74ba8` + `1b044ae`.  Verifier 16/16 PASS.
      `python -m self_upgrade replay` now < 1s (was 5+ min).
- [ ] **step 2.1** — `src/v4_thinker.py` (Thinker 抽象, plan API)
      5 tests.  ~80 LOC.  LLM-as-deep-thinker.
- [ ] **step 2.2** — `src/v4_executor.py` (Executor 抽象, tool dispatch)
      5 tests.  ~80 LOC.  Tool calls.
- [ ] **step 2.3** — `src/v4_loop.py` (Think → Execute → Observe)
      5 tests.  ~60 LOC.  Loop controller.
- [ ] **step 2.4** — joint test (LLM mock + thinker + executor)
      3 tests.  ~50 LOC.  End-to-end mock.

## Backlog (NOT in current session, recorded per user principle)

Per user 2026-07-10: '你认为有必要, 例如我说的内容属于附加功能时,
可以作为 TODO 记录下来, 这时候要整理文档'.

### Cleanup (低风险, 1 commit each)

- [ ] 删 v1.8.x deprecated modules (11 个)
      `src/pipeline_lg.py`, `src/react.py`, `src/mcp_client.py`,
      `src/memory_server.py`, `src/langchain_bridge.py`, etc.
- [ ] 删 `self_upgrade/__main__.v18_backup.py` (469 行, 没用)
- [ ] 更新 LITERATURE.md (新加 11 papers 待 better notes)

### User-side (你跑)

- [ ] 5 consecutive multi-paper rounds stability test
      CLI: `python -m self_upgrade test-scale 5`
- [ ] `python -m self_upgrade replay --live` (慢, 真 LLM, debug only)
- [ ] 真 `improve-multi` 跑 5+ 次,看 KEPT/NO_PATCH ratio

### Future (v3.1+ or v4+)

- [ ] 真实 daily loop (cron job)
- [ ] A/B benchmark (新 patch vs 旧)
- [ ] bootloader 风格 atomic 切换 (你 vision 起点)

## Lesson (per P19 + LITERATURE)

- Signal-to-Fix Loop (Droid 2026): telemetry → signal → fix → deploy
  我们 = progress markers (signal) → commit (fix) → user run (deploy)
- SkillOpt (Microsoft 2026): skills as external state
  我们 = failures.jsonl / judge_*.jsonl 作为 truth
- P19 data flow observability: persist intermediate results
  step 1.3 (save_summaries + save_decision) 已实现
