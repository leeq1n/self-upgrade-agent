# Self-Upgrade Agent 项目简报

**最后更新**：2026-06-30（验收后更新）

---

## 一、核心目标

构建一个 **能通过搜索论文自主改进自身源代码的 AI Agent**。

### 五大能力

| 能力 | 说明 | 完成度 |
|------|------|--------|
| 🔍 自主搜索 | 每天自动搜索 arXiv 最新论文，筛选 AI agent 相关创新方法 | 60% — 只有 arXiv，缺 S2/PwC/GitHub |
| ✏️ 自我进化 | 将论文方法转化为代码补丁，直接修改自己的核心模块 | 30% — patchgen 存在但未接入主流程 |
| 📊 自主评估 | 在自有 benchmark 上对比改进效果 | 10% — benchmark 模块存在，但主评估用随机数 |
| 🎯 自主决策 | 根据评估结果决定保留/回滚 | 30% — 决策逻辑正确，但数据不真实 |
| 🔄 生命周期 | 定期统计模块使用效果，淘汰低效代码 | 40% — skill 维度追踪存在，未适配代码模块 |

---

## 二、当前真实状态（验收后）

### 已具备 ✅

| 模块 | 路径 | 状态 |
|------|------|------|
| 论文搜索 | `src/research.py` + `src/scraper.py` | arXiv API + Selenium fallback，有缓存 |
| 论文筛选 | `src/filter.py` | keyword + LLM 双模式三维评分 |
| LLM 调用层 | `src/llm.py` | OpenAI-compatible，多 key 轮换，模型降级 |
| 代码补丁生成 | `src/patchgen.py` | 论文 → Python 代码 |
| 沙箱测试 | `src/sandbox.py` | subprocess 隔离执行 |
| 失败修复 | `src/reflect.py` | LLM 自动修复（最多 3 轮） |
| 决策模块 | `src/decide.py` | 阈值判断 + 自动回滚 |
| 版本管理 | `src/switcher.py` | candidate/active/backup + manifest |
| 数据库 | `src/db.py` | SQLite 3 张表 |
| 生命周期 | `src/skill_lifecycle.py` | 注册/追踪/修剪/重评估 |
| Agent 核心 | `core/agent.py` + `core/planner.py` + `core/tools.py` | 推理循环骨架 |
| Benchmark | `benchmarks/tasks.json` | 8 个基础任务 |
| 测试 | `tests/` | 66+ 测试 |
| LangGraph 管线 | `src/pipeline_lg.py` | 完整自改进链路（patchgen → sandbox → reflect → benchmark） |

### 主要缺口 ❌

| 缺口 | 严重度 | 说明 |
|------|--------|------|
| 主入口跑偏 | 🔴 致命 | `run.py` 调用 skillgen 路径 (`pipeline.py`)，而非 patchgen 路径 (`pipeline_lg.py`) |
| 评估是随机数 | 🔴 致命 | `pipeline.py._run_evaluation` 用 `random.uniform` 生成评估数据 |
| bootloader 不切代码 | 🔴 致命 | `switcher.py` 只搬 upgrades/ 目录文件，从不写 `core/` |
| 信息源单一 | 🟡 | 只有 arXiv，缺 Semantic Scholar / PwC / GitHub |
| 关键词静态 | 🟡 | config.yaml 手工维护，不会自动发现趋势 |
| 调度器简陋 | 🟡 | daemon 模式无状态持久化、无重试 |

---

## 三、修复路线图

详细计划见：`.hermes/plans/2026-06-30_comp-plan.md`

```
阶段 A：信息搜集扩展 → Semantic Scholar / PwC / GitHub / 动态关键词
阶段 B：真实评估管线 → 替换随机数 / 统计显著性 / 多维度 / 退化检测
阶段 C：打通主链路   → run.py 切到 patchgen / switcher 改为 bootloader
阶段 D：代码质量     → pipeline_lg 重构 / 文档更新
```

---

## 四、架构（实际文件布局）

```
self-upgrade-agent/
├── core/                    # Agent 核心（可被自我改进的目标）
│   ├── agent.py            # 主推理循环（122 行）
│   ├── planner.py          # 任务规划（22 行，故意做薄供 patch 改进）
│   └── tools.py            # 内置工具（shell/read/calc/write）
├── src/                     # 自改进引擎
│   ├── research.py         # arXiv API 搜索 + 缓存
│   ├── scraper.py          # Selenium HTML 刮取回退
│   ├── filter.py           # 论文评分筛选
│   ├── patchgen.py         # 论文 → 代码补丁
│   ├── sandbox.py          # 隔离子进程执行
│   ├── reflect.py          # 失败后 LLM 自动修复
│   ├── evaluate.py         # A/B 评估框架
│   ├── decide.py           # 阈值决策
│   ├── switcher.py         # 候选/活跃/备份版本管理
│   ├── benchmark.py        # Agent benchmark 运行器
│   ├── pipeline_lg.py      # LangGraph 完整自改进管线
│   ├── skill_lifecycle.py  # Skill 生命周期管理
│   ├── db.py               # SQLite 持久化
│   ├── llm.py              # LLM 统一调用层
│   └── config.py           # YAML → dataclass 配置
├── benchmarks/tasks.json   # Benchmark 任务集
├── tests/                   # 测试套件（66+ tests）
├── upgrades/                # 运行时产出（candidates/backups/history.db）
├── config.yaml              # 完整配置
├── run.py                   # CLI 入口（--live/--daemon/--stats/--cull）
├── README.md
└── PROJECT_BRIEF.md
```

---

## 五、验收标准

- [ ] `python run.py --live` 完整闭环：搜索 → 筛选 → 补丁 → 沙箱 → 真实 benchmark → 决策 → bootloader 部署
- [ ] 评估数据全部来自真实 agent 执行，非随机数
- [ ] `--promote paper-xxxx` 后 `core/planner.py` 确实改变
- [ ] 多信息源（arXiv + S2 + PwC）融合搜索
- [ ] 完整的版本历史和回滚能力
- [ ] 66+ 测试全部通过

**当前状态：原型级，不能通过验收。需要按照 `.hermes/plans/2026-06-30_comp-plan.md` 执行修复。**
