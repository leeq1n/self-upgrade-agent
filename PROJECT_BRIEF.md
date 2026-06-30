# Self-Upgrade Agent 项目简报

**最后更新**：2026-06-30（v1.4.0 multi-key 轮换 + surgical bootloader）

---

## 一、核心目标

构建一个 **能通过搜索论文自主改进自身源代码的 AI Agent**。

### 五大能力（v1.4.0 评估）

| 能力 | 说明 | 完成度 |
|------|------|--------|
| 🔍 自主搜索 | 多源搜索：arXiv + Semantic Scholar + Papers With Code + GitHub | 95% — 四源已接入，PwC/GitHub 依赖 HTML 解析 |
| ✏️ 自我进化 | 论文方法 → 代码补丁 → 沙箱验证 → surgical merge 写入 core/ | 90% — surgical merge 已统一到 switcher 和 pipeline |
| 📊 自主评估 | Bootstrap 统计显著性 + 21 个 benchmark 任务 + multi-key LLM 轮换 | 85% — 真实评估已启用，多 key 轮换解决 429 限流 |
| 🎯 自主决策 | 阈值判断 + CI 置信区间 + auto-promote | 85% — 决策逻辑完整 |
| 🔄 生命周期 | 模块版本追踪、使用统计、自动修剪 | 75% — 三条 cull 规则，evaluate_all_skills() |

---

## 二、v1.4.0 新增 / 修复

| 改进 | 说明 | 影响 |
|------|------|------|
| **LLM 多 key 轮换** | `LLM_API_KEY_0..N` 自动发现；daily-quota 429 立即换 key | 之前 7 个 key 在 .env 里**是死配置**，单 trial 43s；现在 ~2s（~20× 加速） |
| **Quota 持久化** | `upgrades/quota_state.json` 记录 `dead_until/failures_today` | daemon 不会每天重头轮 |
| **按任务路由模型** | `LLMConfig.for_task_type('code'/'reasoning'/'planning'/'general')` | code→Coder-30B，reasoning→DeepSeek-V3.2，etc. |
| **Surgical merge bootloader** | `switcher.promote_patch` 改用 `_apply_patch_to_module` | 真正保留 imports 和 `__version__`（之前会全文件覆盖） |
| **LLM JSON 围栏清洗** | `filter._parse_llm_json` 容忍 ```json ... ``` 围栏 | LLM 经常返回 markdown 围栏，之前 warn 后静默失败 |
| **conftest auto-skip** | 无 LLM key → skip `@pytest.mark.llm`；`HERMES_SKIP_NETWORK=1` | 解决"测试 hang 180s"问题 |
| **`.env` 自动加载** | `run.py` 启动时读 .env | 用户不再需要 `export $(cat .env)` |
| **sandbox 跨平台** | 修 `env=dict()` 在 Linux/macOS 失败；去 `chr()` obfuscation | 之前只在 Windows 偶然工作 |

---

## 三、当前真实状态（v1.4.0）

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
pytest -m "not llm and not network"  → 94 passed, 1 skipped, 13 deselected in 2.17s
pytest -m "not network"             → 102 passed, 1 skipped in ~16s
pytest (full)                        → 107 passed, 1 skipped in ~68s
```

### 仍待改进 🟡

| 项目 | 说明 |
|------|------|
| 真实端到端 self-upgrade 成功 | 之前 `manifest.json` 显示 promote 都是空 candidate（`has_code: false`），从没真正成功过完整闭环 |
| 任务类型自动检测 | 现在 `for_task_type` 需要调用方显式指定；可以加自动检测（看 prompt 关键词） |
| filter 评分多维度 | 当前 abstract/applicability/novelty 三维，可加 hallucination / bias 检测 |
| pipeline_lg 可读性 | 已从单字母改为语义化，仍有进一步优化空间 |

---

## 四、验收状态

**v1.4.0 验收评估：基本通过 ✅**

- [x] 107 测试通过，2.17s 跑完纯逻辑
- [x] LLM multi-key 轮换生效（单 trial ~2s vs 之前 43s）
- [x] Quota 状态持久化到 `upgrades/quota_state.json`
- [x] `switcher.promote_patch` 真正用 surgical merge（保留 `__version__` + imports）
- [x] `filter._parse_llm_json` 容忍 ```json 围栏
- [x] `conftest.py` auto-skip 缺 key 的 llm 测试
- [x] `run.py` 自动加载 `.env`
- [x] `sandbox.py` 跨平台工作
- [x] 多信息源（arXiv + S2 + PwC + GitHub）可选启用
- [x] 完整版本历史和回滚能力（manifest + backups/）
- [x] 文档齐全：README + PROJECT_BRIEF + API_REFERENCE + LLM_CALLS + 架构图
