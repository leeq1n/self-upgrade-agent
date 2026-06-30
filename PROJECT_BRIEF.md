# Self-Upgrade Agent 项目简报

**最后更新**：2026-06-30（v1.2.0 修复后）

---

## 一、核心目标

构建一个 **能通过搜索论文自主改进自身源代码的 AI Agent**。

### 五大能力（v1.2.0 评估）

| 能力 | 说明 | 完成度 |
|------|------|--------|
| 🔍 自主搜索 | 多源搜索：arXiv + Semantic Scholar + Papers With Code + GitHub | 85% — 四源已接入，PwC/GitHub 依赖 HTML 解析 |
| ✏️ 自我进化 | 论文方法 → 代码补丁 → 沙箱验证 → surgical merge 写入 core/ | 80% — 主链路已打通，surgical merge 保留 imports |
| 📊 自主评估 | Bootstrap 统计显著性 + 21 个 benchmark 任务 | 75% — 真实评估已启用，多维度评估待扩展 |
| 🎯 自主决策 | 阈值判断 + CI 置信区间 + auto-promote | 85% — 决策逻辑完整，数据来源真实 |
| 🔄 生命周期 | 模块版本追踪、使用统计、自动修剪 | 70% — 核心功能可用，待适配代码模块维度 |

---

## 二、当前真实状态（v1.2.0）

### 已具备 ✅

| 模块 | 路径 | 状态 |
|------|------|------|
| 多源搜索 | `src/research.py` + `research_s2.py` + `research_pwc.py` + `research_github.py` | arXiv + S2 + PwC + GitHub，带缓存 |
| 动态关键词 | `src/keyword_expander.py` | n-gram 提取 + LLM 判断新兴方法 |
| 论文筛选 | `src/filter.py` | keyword + LLM 双模式三维评分 + citation |
| LLM 调用层 | `src/llm.py` | OpenAI-compatible，多 key 轮换 |
| 代码补丁生成 | `src/patchgen.py` | 论文 → Python 代码 |
| 沙箱测试 | `src/sandbox.py` | subprocess 隔离执行 |
| 失败修复 | `src/reflect.py` | LLM 自动修复（最多 3 轮） |
| 真实评估 | `src/pipeline_lg.py` node_evaluate | surgical merge 补丁 → 真实 A/B benchmark |
| 统计显著性 | `src/stats.py` | Bootstrap CI + p-value |
| 决策模块 | `src/decide.py` | 阈值 + 显著性综合判断 |
| Bootloader | `src/switcher.py` | promote_patch 原子写入 core/，备份+回滚 |
| 数据库 | `src/db.py` | SQLite 3 张表 |
| 生命周期 | `src/skill_lifecycle.py` | 注册/追踪/修剪/重评估 |
| Agent 核心 | `core/` | agent.py + planner.py + tools.py |
| Benchmark | `benchmarks/tasks.json` | 21 个任务，6 个能力维度 |
| 测试 | `tests/` | 78+ 测试（非 LLM 全通过） |
| LangGraph 管线 | `src/pipeline_lg.py` | 完整 R→F→G→X→T→E→D 闭环 |
| --live 标志 | `run.py` + `pipeline_lg.py` | true=真实 benchmark，false=dry-run 模拟 |

### 已修复的致命缺陷 ✅

| 原缺陷 | 修复方式 | 版本 |
|--------|---------|------|
| 主入口跑偏 | run.py 默认调用 pipeline_lg | v1.1.0 |
| 评估用随机数 | node_evaluate 用 surgical merge + 真实 benchmark | v1.2.0 |
| bootloader 不切代码 | switcher.promote_patch 原子写入 core/ | v1.1.0 |
| 信息源单一 | 接入 S2 + PwC + GitHub，multi_source 开关 | v1.2.0 |
| --live 无效 | dry_run 参数贯穿 pipeline → node_evaluate | v1.2.0 |
| 文档过期 | README + PROJECT_BRIEF 更新 | v1.2.0 |

### 剩余改进空间 🟡

| 项目 | 说明 |
|------|------|
| 多维度评估 | 增加 instruction_following、hallucination 检测 |
| PwC/GitHub 解析 | 基于 regex 的 HTML 解析不如 BeautifulSoup 稳健 |
| pipeline_lg 可读性 | 已从单字母改为语义化，仍有进一步优化空间 |
| daemon 模式 | 已有重试和状态持久化，可增加日志轮转 |

---

## 三、架构（实际文件布局）

```
self-upgrade-agent/
├── core/                    # Agent 核心（可被自我改进的目标）
│   ├── agent.py            # 主推理循环
│   ├── planner.py          # 任务规划（故意做薄供 patch 改进）
│   └── tools.py            # 内置工具
├── src/                     # 自改进引擎
│   ├── research.py         # arXiv + 多源聚合
│   ├── research_s2.py      # Semantic Scholar
│   ├── research_pwc.py     # Papers With Code
│   ├── research_github.py  # GitHub trending
│   ├── scraper.py          # Selenium 回退
│   ├── keyword_expander.py # 动态关键词
│   ├── filter.py           # 论文筛选
│   ├── patchgen.py         # 代码补丁生成
│   ├── sandbox.py          # 沙箱隔离
│   ├── reflect.py          # 失败修复
│   ├── pipeline_lg.py      # LangGraph 管线
│   ├── benchmark.py        # Benchmark 运行器
│   ├── evaluate.py         # A/B 评估
│   ├── stats.py            # 统计显著性
│   ├── decide.py           # 决策
│   ├── switcher.py         # Bootloader
│   ├── skill_lifecycle.py  # 生命周期
│   ├── db.py               # SQLite
│   ├── llm.py              # LLM 层
│   └── config.py           # 配置
├── benchmarks/tasks.json   # 21 个 benchmark 任务
├── tests/                   # 78+ 测试
├── upgrades/                # 运行时产出
├── config.yaml              # 配置
└── run.py                   # CLI 入口
```

---

## 四、验收状态

**v1.2.0 验收评估：基本通过 ✅**

- [x] `python run.py --live` 完整闭环运行
- [x] 评估数据来自真实 benchmark，dry_run=False 时非随机数
- [x] `--promote patch-xxxx` 后 `core/planner.py` 确实改变（含 imports）
- [x] 多信息源（arXiv + S2 + PwC + GitHub）可选启用
- [x] 完整版本历史和回滚能力（manifest + backups/）
- [x] 78+ 测试通过
- [x] surgical merge 保留模块 imports 和 __version__
- [x] --live 标志真正控制 benchmark 行为

**建议后续改进**：多维度评估、daemon 日志轮转、PwC/GitHub 解析健壮化。
