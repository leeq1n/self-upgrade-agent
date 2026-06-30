# Self-Upgrade Agent — Known Issues & Roadmap

> **状态**：活跃 (v1.5.1)
> **更新**：2026-07-01

这份文件跟踪"项目本身没做好的事"和"v1.6.0 计划"。每条 issue 都有：
- **级别**：P0 必修 / P1 应修 / P2 nice-to-have
- **影响**：为什么重要
- **当前 workaround**：怎么临时绕过

---

## P0 必修（影响真实使用，但当前有 workaround）

### ISS-001: filter LLM 评分不稳定
- **级别**：P0
- **影响**：同一篇 paper 不同次跑可能排第 1 或第 4。因为：
  - LLM 评分本身有随机性（即使 temperature=0.1）
  - S2 引用 enrichment 失败时返回 0，但成功时返回不同数字
  - `max_papers_to_consider=3` 太少，错过了 qualified 4-5
- **当前 workaround**：None — 真实 promote 时可能错过好 paper
- **建议修复**：
  1. 加 deterministic 关键词 boost（命中 "self-improve" / "agent planning" / "self-evolving" / "world model" 加 +2 分）
  2. `max_papers_to_consider` 改 5
  3. 跑 2-3 次 filter LLM 评分取平均

### ISS-002: 真实端到端没有经过 evaluate 流程
- **级别**：P0（流程问题）
- **影响**：v1.5.0 那次"真实成功 promote `core/planner.py`" 是**手动调用 `promote_patch()`** 触发的，**没经过 A/B benchmark 评估**。生产流程应该是：patchgen → sandbox → evaluate → decide → auto-promote
- **当前 workaround**：None
- **建议修复**：
  - `node_evaluate` 跑 trials=1（21 任务）但**真实能跑**（实测 ~2 min）
  - 在 `node_decide` 加 `min_success_rate_delta` 阈值，没达到就 rollback

---

## P1 应修（影响中长期使用，不阻塞当前）

### ISS-003: 多 daemon 并发锁
- **级别**：P1
- **影响**：如果用户不小心跑 2 个 daemon（`run.py --daemon` × 2），它们会同时写 `manifest.json` / `quota_state.json`，可能产生竞态
- **当前 workaround**：None（靠用户自觉）
- **建议修复**：`fcntl.flock` 文件锁包 `manifest.json` 写入

### ISS-004: evaluate.py 和 pipeline_lg.node_evaluate 两套并行
- **级别**：P1
- **影响**：DeepSeek 之前提过的"两套并行评估"。`src/evaluate.py` 是独立模块，`pipeline_lg.node_evaluate` 也跑评估，两份代码可能漂移
- **当前 workaround**：只用 pipeline_lg；evaluate.py 仍被 `run.py --legacy` 调用
- **建议修复**：让 `pipeline_lg.node_evaluate` 调 `src.evaluate.evaluate_skill()`，消除重复
- **状态**：✅ v1.5.1 修（`src/evaluate.py` 现在是 `src/benchmark.run_all` 的薄包装；`node_evaluate` 调 `src.evaluate.compare_results`；6 个新测试覆盖）

### ISS-005: cost tracking 是 placeholder
- **级别**：P1
- **影响**：`cost_increase_ratio` 现在用 elapsed time ratio 代替（v1.5.0 改的），但**真实 token cost** 没记
- **当前 workaround**：用 elapsed time ratio 近似
- **建议修复**：从 `LLMResponse.total_tokens` 拿真实 cost，存到 history.db

### ISS-006: pipeline_lg 646 行偏大
- **级别**：P1
- **影响**：可读性
- **当前 workaround**：None
- **建议修复**：把 `_apply_patch_to_module` 移到 `src/surgical_merge.py`，与 switcher 共用

### ISS-007: llm.py 789 行偏大
- **级别**：P1
- **影响**：同上
- **建议修复**：把 `QuotaState` 移到 `src/quota_state.py`

---

## P2 nice-to-have（改进体验，不是核心）

### ISS-008: daemon 跑完无邮件/通知
- **级别**：P2
- **影响**：daemon 跑一天 24h，如果 promote 成功用户不知道
- **建议修复**：加 webhook / 邮件通知（可选）

### ISS-009: trending 缓存手工维护
- **级别**：P2
- **影响**：`upgrades/trending_keywords.json` 是 daemon 跨日反馈的状态，但没有 UI/命令清空
- **建议修复**：`run.py --reset-trending`

### ISS-010: 无 cost 预算
- **级别**：P2
- **影响**：用户没法设"每天最多花 X token"
- **建议修复**：在 config.yaml 加 `daily_token_budget`，daemon 检查

### ISS-011: `pipeline_lg._print_pipeline_lg_result` 在 run.py 重复实现
- **级别**：P2
- **影响**：输出格式可能在两处漂移
- **建议修复**：移到 `src/pipeline_lg.py` 作为 public function

### ISS-012: `BenchmarkTask` 与 `benchmark.run_single` 类型不匹配（pre-existing，新发现）
- **级别**：P1
- **影响**：`src/evaluate.py:41` 定义了 `@dataclass class BenchmarkTask`（属性 `id/description/query/...`），但 `src/benchmark.py:32` 用 `task["task"]` 当字典取。`tests/test_evaluate.py::TestLLMIntegration` 的 4 个测试因此失败：`TypeError: 'BenchmarkTask' object is not subscriptable`
- **当前 workaround**：`run.py --legacy` 路径绕开 `benchmark.run_single`；新路径 `node_evaluate` 调 `benchmark.run_all(tasks)` 时传的是 `benchmarks/tasks.json` 出来的 dict，所以 production 不撞这个 bug。**只影响 evaluate.py 单元测试**
- **建议修复**：
  1. 让 `benchmark.run_single(task)` 兼容两种类型：`task["task"]` 走 dict，`task.query` 走 dataclass；或
  2. 把 `evaluate.BenchmarkTask` 改成 dict 派生（TypedDict）；或
  3. 删 `BenchmarkTask` dataclass，统一走 `benchmarks/tasks.json`
- **未修原因**：本次任务只修 `tests/test_e2e.py`，不在 v1.5.1 修复范围
- **真实验证（2026-07-01）**：`git stash` 掉我的 e2e 改动后，干净 `fcb73ef` 上跑 `tests/test_evaluate.py`，同样 4 个 fail，证明 pre-existing

### ISS-013: mock e2e 测试发现 `node_filter` 不传 `llm_config`，filter 永远走 keyword fallback
- **级别**：P2（已通过 mock e2e 测试绕过；production 影响待评估）
- **影响**：`src/pipeline_lg.py:182` 调用 `filter_papers(papers, cfg.filter, use_llm=True)` 时**没传 `llm_config`**。`src/filter.py:205` 检查 `if use_llm and llm_config is not None and llm_config.ready:` —— `llm_config is None` → 直接走 keyword fallback。这意味着生产环境里 filter **永远不会用 LLM 评分**，永远用 keyword。这意味着 ISS-001（filter LLM 评分不稳定）的 deterministic 修复虽然进了 v1.5.0，但根本就没生效
- **当前 workaround**：`tests/test_e2e.py` fixture 直接 patch `src.filter.score_paper`，绕过这个 wiring 问题
- **建议修复**：
  1. `node_filter` 调 `LLMConfig.from_env()` 并传给 `filter_papers(..., llm_config=cfg.llm)`；或
  2. `filter_papers` 内部 `from src.llm import LLMConfig; LLMConfig.from_env()`，自动拿到 config
  3. 跑真实 e2e 验证 filter LLM 评分确实在跑
- **未修原因**：production wiring 改动超出 mock 测试修复范围；建议 ISS-013 进入 v1.6.0 backlog

---

## v1.6.0 候选（按优先级）

1. **ISS-001** filter 稳定性（deterministic boost + max_papers=5）
2. **ISS-002** 真实 end-to-end 评估（让 promote 真正经过 evaluate）
3. **ISS-013** `node_filter` 传 `llm_config`（让 ISS-001 修复真正生效）
4. **ISS-003** 多 daemon 文件锁
5. **ISS-005** cost tracking with real tokens
6. **ISS-012** `BenchmarkTask` 类型不匹配（pre-existing 4 测试失败）
## v1.7.0 候选

7. **ISS-006/007** 拆分 llm.py / pipeline_lg.py
8. **ISS-008/010** 通知 + cost 预算

---

## 已修复 (v1.0 → v1.5.1)

| 版本 | 修复 |
|------|------|
| v1.1.0 | multi-key LLM 轮换；atomic write bootloader |
| v1.2.0 | surgical merge；multi-source 搜索 |
| v1.3.0 | node_research 读 trending 缓存（loop 闭环） |
| v1.4.0 | global timeout + diagnostic + 401/403 永久 mark dead |
| v1.5.0 | 8 key 全对上号；real promote 成功；BOM/utf-8-sig；filter/patchgen 对齐 self-upgrade 痛点 |
| v1.5.1 | ISS-004 evaluate.py / node_evaluate 单 A/B 路径合并；`tests/test_e2e.py` mock 端到端 3/3 通过（修复了 PATCH_JSON 自相矛盾断言 + node_filter 不传 llm_config 的 mock 绕过） |
