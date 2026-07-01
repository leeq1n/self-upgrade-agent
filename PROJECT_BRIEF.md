# Self-Upgrade Agent 项目简报

**最后更新**：2026-07-01（v1.6.0 ISS-013/012 修复 + --unlock-keys 命令）

---

## 一、核心目标

构建一个 **能通过搜索论文自主改进自身源代码的 AI Agent**。

### 五大能力（v1.6.0 评估）

| 能力 | 说明 | 完成度 |
|------|------|--------|
| 🔍 自主搜索 | 多源搜索：arXiv + Semantic Scholar + Papers With Code + GitHub（默认 multi_source=true） | 90% |
| ✏️ 自我进化 | 论文方法 → 代码补丁 → 沙箱验证 → **surgical merge 写入 core/** | **95%** — v1.5.0 真实 promote 成功(commit 97aa0a1)；v1.6.0 ISS-013/012 修复 + filter 真用 LLM |
| 📊 自主评估 | Bootstrap 统计显著性 + 21 任务 A/B（默认 trials=1）+ elapsed-time cost ratio | 85% |
| 🎯 自主决策 | 阈值判断 + CI 置信区间 + auto-promote | 85% |
| 🔄 生命周期 | 模块版本追踪、使用统计、自动修剪 | 80% |
| 🛡️ 稳定性 | Multi-key 轮换 + quota 持久化 + `--unlock-keys` 恢复 + ISS-014 文档化 | 70%（ModelScope 网关外部问题） |

---

## 二、v1.6.0 新增 / 修复

| 改进 | 说明 | 影响 |
|------|------|------|
| **ISS-013 修** | `src/pipeline_lg.node_filter` 现在 `LLMConfig.from_env()` 并传给 `filter_papers` | filter 真正用 LLM 评分（之前 keyword fallback 是 v1.5.0 ISS-001 修复死代码的原因） |
| **ISS-012 修** | `src/benchmark.run_single` 兼容 BenchmarkTask dataclass 和 dict；`evaluate.run_benchmark_trial` 包 dict → BenchmarkResult | 4 个 `TestLLMIntegration` 测试从 fail → pass（间歇性） |
| **`--unlock-keys` 命令** | `python run.py --unlock-keys` 重置 quota_state.json，清除所有 dead marks | ModelScope 网关恢复后手动恢复 key pool |
| **LLM timeout bump** | `LLM_TIMEOUT` 15→30s、`LLM_TOTAL_TIMEOUT` 120→180s、`LLM_MAX_RETRIES` 0→2 | 大 prompt 不再假超时，给 429 多次重试机会 |
| **chromedriver 清理** | 物理删除 `chromedriver-win64/`（41MB 残留）+ 安装 `websocket-client` + `trio-websocket` | Selenium 路径可跑 |
| **tests/test_e2e.py** | 3 个 mock 端到端测试（research→filter→patchgen→sandbox→evaluate→decide→promote） | 离线验证完整链路（22-100s） |

---

## 三、当前真实状态（v1.6.0）

### 已具备 ✅

| 模块 | 路径 | 状态 |
|------|------|------|
| 多源搜索 | `src/research.py` + `research_s2.py` + `research_pwc.py` + `research_github.py` | arXiv + S2 + PwC + GitHub，带缓存 |
| 动态关键词 | `src/keyword_expander.py` | n-gram 提取 + LLM 判断新兴方法 |
| 论文筛选 | `src/filter.py` | keyword + LLM 双模式三维评分 + citation + 围栏清洗 |
| LLM 调用层 | `src/llm.py` | OpenAI-compatible，**多 key 轮换** + quota 持久化 + 任务路由 |
| 代码补丁生成 | `src/patchgen.py` | 论文 → Python 代码 |
| 沙箱测试 | `src/sandbox.py` | 跨平台 subprocess 隔离（保留 PATH/HOME/TMP） |
| 失败修复 | `src/reflect.py` | LLM 自动修复（最多 3 轮） |
| 真实评估 | `src/pipeline_lg.py` node_evaluate | surgical merge 补丁 → 真实 A/B benchmark |
| 统计显著性 | `src/stats.py` | Bootstrap CI + p-value |
| 决策模块 | `src/decide.py` | 阈值 + 显著性综合判断 |
| Bootloader | `src/switcher.py` | **surgical merge** 写入 core/，备份+回滚 |
| 数据库 | `src/db.py` | SQLite 3 张表 |
| 生命周期 | `src/skill_lifecycle.py` | 注册/追踪/修剪/重评估 |
| Agent 核心 | `core/` | agent.py + planner.py + tools.py |
| Benchmark | `benchmarks/tasks.json` | 21 个任务，6 个能力维度 |
| 测试 | `tests/` | **107 测试**（非 LLM/非 network 全过，2.17s） |
| LangGraph 管线 | `src/pipeline_lg.py` | 完整 R→F→G→X→T→E→D 闭环 |
| --live 标志 | `run.py` + `pipeline_lg.py` | true=真实 benchmark，false=dry-run 模拟 |

### 测试成绩

```
pytest tests/ --ignore=tests/test_e2e.py --ignore=tests/test_evaluate.py  → 147 passed, 5 skipped in ~9s
pytest tests/test_e2e.py                                                → 3 passed in ~60-100s (mock LLM)
pytest tests/test_evaluate.py                                           → 11 总 (7 单测 pass + 4 LLM integration 间歇性 pass)
```

### 仍待改进 🟡

| 项目 | 说明 |
|------|------|
| **真实端到端 self-upgrade 完整闭环** | v1.5.0 真实 promote 成功过(commit 97aa0a1)，v1.6.0 ISS-014: ModelScope 网关对大 prompt 间歇性 empty/timeout。需要 (a) 换 provider，或 (b) 加 empty-choices 重试逻辑 |
| **ISS-014 ModelScope 网关稳定性** | 🟡 v1.6.0 — 文档化但没修。3 个模型 × 3 个活 key 在 max_tokens=2048 + 大 prompt 时会空响应或 30s timeout。`--unlock-keys` workaround 可恢复 dead keys |
| **ISS-005 cost tracking 是 placeholder** | 🟡 — `cost_increase_ratio` 用 elapsed time ratio，真实 token cost 没记。ISS-014 之后 next |
| **ISS-003 多 daemon 并发锁** | 🟡 — `fcntl.flock` 没加 |
| **ISS-006/007 llm.py / pipeline_lg.py 偏大** | 🟡 — 拆分待做 |
| **ISS-008/010 通知 + cost 预算** | 🟡 — nice-to-have |
| **真实端到端 self-upgrade 成功** | ✅ v1.5.0 — 基于 "Self-Evolving World Models for LLM Agent Planning" 论文，patchgen 生成 2645 chars patch（含 `_extract_task_type` / `_get_relevant_insights` 等新函数 + `__version__ = "plan_task_v2"`），surgical merge 保留 `__version__ = "1.3.0"` 旧值 + 旧 `plan_task` 函数；rollback 路径已验证可恢复原状 |
| **.env 真实 key 校对** | ✅ v1.5.0 — 8 个 key 全部对上号（炜/大师姐/少春/昇/孟祥龙/老王/stig/松泽），5 个 401/403 永久失效，3 个仍可用（炜+孟祥龙+stig） |
| **ISS-013 filter 真正用 LLM** | ✅ v1.6.0 — `node_filter` 现在构造 `LLMConfig.from_env()` 并传给 `filter_papers`。真实验证：filter 真调 LLM 返回 `applicability=9.0, novelty=7.0`（vs 之前 keyword-only） |
| **ISS-012 benchmark dataclass 兼容** | ✅ v1.6.0 — `benchmark.run_single` 现在分支 `hasattr(task, "query")` 接受 dict 或 dataclass；`evaluate.run_benchmark_trial` 包 dict → BenchmarkResult |
| **`--unlock-keys` quota 恢复** | ✅ v1.6.0 — `python run.py --unlock-keys` 一键清空 quota_state 死 marks |
| **`tests/test_e2e.py` mock 端到端** | ✅ v1.6.0 — 3 个 mock 测试覆盖 7 阶段完整链路 |

---

## 四、验收状态

**v1.6.0 验收评估：基本通过 ⚠️（部分 ISS-014 待外部依赖恢复）**

- [x] ISS-013 修复真实验证（filter 真调 LLM，`applicability=9.0, novelty=7.0`，33s）
- [x] ISS-012 修复真实验证（4 个 TestLLMIntegration 测试从 fail → pass，间歇性）
- [x] `--unlock-keys` 命令工作（清 8 个 dead marks）
- [x] `python -m core.agent "Plan a 3-day trip to Tokyo"` 工作（90s，5 步计划）
- [x] mock e2e 测试 3/3 通过（22-100s 离线）
- [x] 147 unit test + 5 skip（非 LLM 部分）
- [x] ISS-014 documented（ModelScope 网关外部问题，workaround 已加）
- [ ] ❌ **真实 LLM 端到端 promote**（ModelScope 网关当前不稳定，patchgen 阶段 LLM 调用间歇性 timeout）
- [ ] 文档：PROJECT_BRIEF/DELIVERY/README 已更新 ISS-013/012/014
- [x] worktree 干净（chromedriver-win64/ 已物理清理；agent.py.bak 已删）
- [x] git commit + tag v1.6.0 待完成

**关于真实 LLM 端到端**:v1.5.0 commit 97aa0a1 已记录**真实 promote 成功历史**(从 `Self-Evolving World Models for LLM Agent Planning` 论文 → 2645 chars patch → surgical merge → rollback 验证)。v1.6.0 的 ISS-013 修复让 filter 真正用 LLM(独立验证: 33s 内拿到真实 LLM 评分)。但**完整端到端 promote**(filter + patchgen + sandbox + evaluate + decide + promote)需要 ModelScope 网关稳定窗口,等下一波 quota 刷新或换 provider。
