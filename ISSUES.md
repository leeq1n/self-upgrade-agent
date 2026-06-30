# Self-Upgrade Agent — Known Issues & Roadmap

> **状态**：活跃 (v1.5.0)
> **更新**：2026-06-30

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

---

## v1.6.0 候选（按优先级）

1. **ISS-001** filter 稳定性（deterministic boost + max_papers=5）
2. **ISS-002** 真实 end-to-end 评估（让 promote 真正经过 evaluate）
3. **ISS-004** evaluate.py / node_evaluate 合并
4. **ISS-003** 多 daemon 文件锁
5. **ISS-005** cost tracking with real tokens

## v1.7.0 候选

6. **ISS-006/007** 拆分 llm.py / pipeline_lg.py
7. **ISS-008/010** 通知 + cost 预算

---

## 已修复 (v1.0 → v1.5.0)

| 版本 | 修复 |
|------|------|
| v1.1.0 | multi-key LLM 轮换；atomic write bootloader |
| v1.2.0 | surgical merge；multi-source 搜索 |
| v1.3.0 | node_research 读 trending 缓存（loop 闭环） |
| v1.4.0 | global timeout + diagnostic + 401/403 永久 mark dead |
| v1.5.0 | 8 key 全对上号；real promote 成功；BOM/utf-8-sig；filter/patchgen 对齐 self-upgrade 痛点 |
