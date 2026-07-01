# Self-Upgrade Agent — Known Issues & Roadmap

> **状态**：活跃 (v1.6.0)
> **更新**：2026-07-01

这份文件跟踪"项目本身没做好的事"和"v1.7.0 计划"。每条 issue 都有：
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

### ISS-012: `BenchmarkTask` 与 `benchmark.run_single` 类型不匹配
- **级别**：P1
- **影响**：`src/evaluate.py:41` 定义了 `@dataclass class BenchmarkTask`（属性 `id/description/query/...`），但 `src/benchmark.py:32` 用 `task["task"]` 当字典取。`tests/test_evaluate.py::TestLLMIntegration` 的 4 个测试因此失败：`TypeError: 'BenchmarkTask' object is not subscriptable`
- **当前 workaround**：生产 `node_evaluate` 调 `benchmark.run_all(tasks)` 时传的是 `benchmarks/tasks.json` 出来的 dict，所以 production 不撞这个 bug。**只影响 evaluate.py 单元测试**
- **修复状态**：✅ v1.6.0 修（commit `535fc85`）— `benchmark.run_single` 现在分支 `hasattr(task, "query")`，接受 dict 或 dataclass；`evaluate.run_benchmark_trial` 包 dict → BenchmarkResult
- **真实验证（2026-07-01）**：单次 LLM 调用测试通过；21-task benchmark 测试间歇性 fail（依赖 ModelScope 状态）

### ISS-013: `node_filter` 不传 `llm_config`，filter 永远走 keyword fallback
- **级别**：P2
- **影响**：`src/pipeline_lg.py:182` 调用 `filter_papers(papers, cfg.filter, use_llm=True)` 时**没传 `llm_config`**。`src/filter.py:205` 检查 `if use_llm and llm_config is not None and llm_config.ready:` —— `llm_config is None` → 直接走 keyword fallback。这意味着生产环境里 filter **永远不会用 LLM 评分**，永远用 keyword。**ISS-001（filter LLM 评分不稳定）的 deterministic 修复虽然进了 v1.5.0，但根本就没生效**
- **当前 workaround**：已修复
- **修复状态**：✅ v1.6.0 修（commit `535fc85`）— `node_filter` 现在调 `LLMConfig.from_env()` 并传给 `filter_papers(..., use_llm=llm_config.ready, llm_config=llm_config)`

### ISS-014: ModelScope 网关状态不稳定（间歇性 empty choices / timeout）
- **级别**：P1
- **影响**：在 2026-07-01 多次探测中发现，`DeepSeek-V4-Pro` / `Qwen/Qwen3-235B-A22B` / `ZhipuAI/GLM-5.1` 这 3 个声称可用的模型在 ModelScope 网关对**大 prompt + 大 max_tokens** 调用时会返回 `finish_reason=length` 但 `content=""` 或直接 30s timeout。状态在几秒到几分钟内剧烈波动（同样的请求第一次成功 27s 返回 JSON，第二次 empty choices，第三次 timeout）
- **当前 workaround**：
  - 测试用 `LLM_MAX_TOKENS=500` 降低单次响应大小
  - `tests/test_evaluate.py::TestLLMIntegration` 的 21-task benchmark 测试间歇性 fail —— 这是已知的，不算 regression
- **建议修复**：
  1. 在 `src/llm.py` 加 empty-choices 重试逻辑（不要 mark dead，直接换下一个 key/model）
  2. 或换 provider（OpenAI / Anthropic / DeepSeek 官方 API），绕过 ModelScope 网关
- **未修原因**：超出 mock 测试修复范围；建议 ISS-014 进入 v1.7.0 backlog

---

## v1.7.0 候选（按优先级）

1. **ISS-014** ModelScope 网关稳定性（empty choices 重试或换 provider）
2. **ISS-001** filter 稳定性（ISS-013 修后 ISS-001 修复真正生效，需回归验证）
3. **ISS-002** 真实 end-to-end 评估（让 promote 真正经过 evaluate）
4. **ISS-003** 多 daemon 文件锁
5. **ISS-005** cost tracking with real tokens
## v1.8.0 候选

6. **ISS-006/007** 拆分 llm.py / pipeline_lg.py
7. **ISS-008/010** 通知 + cost 预算

---

## 已修复 (v1.0 → v1.6.0)

| 版本 | 修复 |
|------|------|
| v1.1.0 | multi-key LLM 轮换；atomic write bootloader |
| v1.2.0 | surgical merge；multi-source 搜索 |
| v1.3.0 | node_research 读 trending 缓存（loop 闭环） |
| v1.4.0 | global timeout + diagnostic + 401/403 永久 mark dead |
| v1.5.0 | 8 key 全对上号；real promote 成功；BOM/utf-8-sig；filter/patchgen 对齐 self-upgrade 痛点 |
| v1.5.1 | ISS-004 evaluate.py / node_evaluate 单 A/B 路径合并；`tests/test_e2e.py` mock 端到端 3/3 通过 |
| v1.6.0 | ISS-013 `node_filter` 传 `llm_config`；ISS-012 benchmark dataclass 兼容；chromedriver-win64/ 物理清理；websocket-client 安装；Selenium 路径可跑 |
| v1.6.0+ (2026-07-01) | `.env` 改用 Qwen3-235B-A22B + GLM-5.1 (V4-Pro quota dead)。Filter 真调 LLM 11.7s (vs 之前 33s 因试 V4-Pro dead models)。PatchGen 仍受 ModelScope minute-level 限流影响——3 个活 key 在 60s 内被 rate-limit 一次后全 timeout。**真实端到端 promote 今日不可达**。ISS-014 实质修复(智能 cooldown + key 健康检查)留待 v1.7.0 |
