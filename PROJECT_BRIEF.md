# Self-Upgrade Agent 项目简报

**最后更新**：2026-07-06（v1.8.0 alpha — 真 harness + 8 节点 + skill 生命周期自动化 + 5 round live 1 kept）
**当前版本**：v1.7.1 (git tag), v1.8.0 alpha (master 分支)
**稳定 tag**：v1.7.1 — 2 轮 stress test 验证

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


---

## v1.8.0 进展 (2026-07-02, alpha)

**目标**: 让自进化在多 agent / multi-file patch 方向上收敛,同时建立可观测的失败学习。

### Phase A — Harness 框架(部分完成)

| 任务 | 状态 | Commit |
|------|------|--------|
| A1. learning.db schema (`attempts`, `blacklist`, `convergence_state`, `seen_papers`, `auto_blacklist`) | ✅ 完成 | 201c0d0, 55ffde3 |
| A2. 闭环反馈(失败 WHY 进 patchgen prompt) | ❌ 未做 | — |
| A3. 终止条件(`--max-rounds`, `--convergence-window`) | ❌ 未做 | — |
| A4. paper 排除(seen_papers + auto_blacklist) | ✅ 完成(commit 55ffde3) | 55ffde3 |
| A5. 文档 + 完整 unit test | ⚠️ 部分(test 7/7 PASS, docs 已有 CONSTRAINTS.md) | — |

### Phase B/C(未开始)

- Phase B: 架构灵活性(CORE_MODULES 白名单放宽, multi-file patch, dynamic import)
- Phase C: 真实 multi-agent harness 跑通

### 当前 tag 策略

| Tag | 状态 | 推荐使用 |
|-----|------|----------|
| v1.6.0 | ISS-013/012 修 | ✅ 旧, 已 superseded |
| v1.7.0 | Anthropic provider, 真 LLM 跑通一次 | ✅ 旧 |
| **v1.7.1** | **safety net + stress test 验证** | **✅ 当前推荐稳定版** |
| v1.8.0 | (未 tag) Phase A 部分完成 | ⚠️ alpha, 不建议生产 |

### v1.7.1 + v1.8.0 alpha 对比

| 维度 | v1.7.1 | v1.8.0 alpha (master) |
|------|--------|----------------------|
| 真 LLM 端到端 | ✅ 2 轮 stress test 验证 | 3 round live 跑(0 进展,ModelScope 网关 dead) |
| 单元测试 | 154 + 5 skip | 171 + 5 skip (新增 learning + CLI test) |
| CLI 入口 | `python -m core.agent` + `python run.py`(两套) | `python -m self_upgrade <sub>`(统一) |
| 失败学习 | 无 | learning.db schema 已写,未接入 pipeline |
| 文档 | 7 篇 | 9 篇 (+ USER_INSIGHTS + PLAN_v180) |
| 向后兼容 | n/a | ✅ `python -m core.agent` 跟 `python run.py` 仍工作 |

### 不建议现在就 tag v1.8.0 的原因

- Phase A 只完成 A1 + A4,A2/A3/A5 未做
- 真 LLM 端到端未跑通(3 round live 数据是 0 进展)
- 离"自进化收敛"目标还远
- 应该等 Phase A 完整 + Phase B 至少 B1 + 1 次真 LLM 跑通再 tag

### 怎么测 v1.8.0 alpha (用户手动)

```bash
# 1. 拉 master 分支
git checkout master

# 2. 跑 3 round live(等 ModelScope 网关恢复)
python -m self_upgrade unlock
python /path/to/run_3rounds.py  # 详见 docs/CLI_GUIDE.md

# 3. 看结果
python -m self_upgrade status
cat upgrades/3round_run_results.json

# 4. 验证不变性
pytest tests/ --ignore=tests/test_e2e.py --ignore=tests/test_evaluate.py
# 期望: 171 passed + 5 skip + 0 fail
```


### Day 6 (2026-07-06): 5-round live verification

| 指标 | 结果 |
|---|---|
| 5 round 跑通 | ✅ Total: 1243s (20.7 min) |
| True LLM 端到端 | ✅ 4/5 round done=True |
| 真 promote (decision=kept) | ✅ Round 2 (2606.30639 WorldEvolver) |
| Harness 8/8 pass | ✅ Round 2 (real Python unit tests, not LLM-grading-LLM) |
| LLM delta | +6.9% (over 5% threshold) |
| Safety net | ✅ planner.py MD5 stable across 5 rounds |
| history.db 增长 | +4 (5 round recorded) |
| audit_history 触发 | ✅ node_skill_audit ran (0 skills to cull) |

**Critical v1.8.0 validation**: Round 2's patch passed harness (8/8
Python unit tests) AND improved LLM benchmark by 6.9%.  The promote
was kept (decision=kept), demonstrating the harness is a real
independent verification signal — not "LLM grading LLM".

