# Self-Upgrade Agent 项目简报

**最后更新**：2026-06-30

---

## 一、核心目标

构建一个 **独立的、能自我进化的 AI Agent 系统**，不依赖任何外部框架（如 Hermes Agent）。

### 五大能力

| 能力 | 说明 |
|------|------|
| 🔍 自主搜索 | 每天自动搜索 arXiv 最新论文，筛选 AI agent 相关创新方法 |
| ✏️ 自我进化 | 将论文方法转化为代码补丁，**直接修改自己的核心模块** |
| 📊 自主评估 | 在自有 benchmark 上对比改进效果（成功率、效率、成本） |
| 🎯 自主决策 | 根据评估结果决定保留/回滚，支持自动回滚 |
| 🔄 生命周期 | 定期统计模块使用效果，淘汰低效代码 |

---

## 二、关键澄清

| ❌ 不是 | ✅ 是 |
|--------|------|
| 为 Hermes Agent 生成 SKILL.md | 独立系统，直接进化自己的源代码 |
| 模拟评估/硬编码数据 | 真实运行 benchmark，基于实际数据决策 |
| 线性流程执行完就结束 | 持续循环、断点续跑、长期运行 |

---

## 三、架构设计

```
self-upgrade-agent/
├── core/                    # Agent 核心（可被改进的对象）
│   ├── agent.py            # 主推理循环
│   ├── planner.py          # 任务规划
│   ├── reasoner.py         # 逻辑推理
│   └── tool_use.py         # 工具调用
├── self_improve/            # 自我进化引擎（使用 LangGraph）
│   ├── research.py         # 搜索论文
│   ├── filter.py           # 筛选方法
│   ├── patch_gen.py        # 生成代码补丁
│   ├── evaluate.py         # A/B 测试
│   └── decide.py           # 决策合并
├── benchmarks/              # 自有测试集
│   ├── planning_tasks.json
│   ├── reasoning_tasks.json
│   └── tool_use_tasks.json
├── langgraph_workflow.py   # LangGraph 编排
└── run.py                  # 入口
```

---

## 四、技术选型

| 组件 | 选型 | 理由 |
|------|------|------|
| 工作流编排 | **LangGraph** | 支持循环、条件路由、状态持久化、断点续跑 |
| 评估 | 自有 benchmark + 真实执行 | 产出真实数据 |
| 持久化 | SQLite | 代码版本、评估历史、决策记录 |
| 调度 | 内置调度器 | 不依赖外部 cron |

---

## 五、LangGraph 工作流

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Research   │ →   │   Filter    │ →   │  PatchGen   │
│  (arXiv)    │     │  (评分筛选)  │     │ (生成补丁)  │
└─────────────┘     └─────────────┘     └─────────────┘
       ↑                                       ↓
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Lifecycle  │ ←   │   Decide    │ ←   │  Evaluate   │
│ (修剪模块)   │     │ (merge/rollback)│  │  (A/B 测试)  │
└─────────────┘     └─────────────┘     └─────────────┘
       ↓
    ───────
   ↻ 循环继续
```

---

## 六、当前状态

| 模块 | 状态 | 说明 |
|------|------|------|
| 论文搜索 | ✅ 已完成 | `src/research.py` |
| 论文筛选 | ✅ 已完成 | `src/filter.py` |
| 代码生成 | ⚠️ 需改造 | 从生成 SKILL.md 改为生成核心代码补丁 |
| 沙箱测试 | ✅ 已完成 | `src/sandbox.py` |
| 评估框架 | ⚠️ 需改造 | 从模拟数据改为真实 benchmark |
| 决策机制 | ✅ 已完成 | `src/decide.py` |
| 版本管理 | ✅ 已完成 | `src/switcher.py` |
| 生命周期 | ✅ 已完成 | `src/skill_lifecycle.py` |
| LangGraph | ❌ 未引入 | 需要重构工作流 |
| 核心模块 | ❌ 未创建 | 需要创建 `core/*.py` |
| Benchmark | ❌ 未创建 | 需要创建 `benchmarks/` |

---

## 七、下一步行动

1. **P0**：创建核心模块框架（`core/agent.py` 等）
2. **P0**：创建 benchmark 任务集（`benchmarks/`）
3. **P0**：打通真实评估闭环
4. **P1**：引入 LangGraph 重构工作流
5. **P1**：改造代码生成为补丁生成
6. **P2**：添加内置调度器

---

## 八、验收标准

- [ ] 系统能独立运行，不依赖 Hermes
- [ ] 能从论文学习并生成核心代码补丁
- [ ] 能在 benchmark 上真实测试改进效果
- [ ] 能基于真实数据决策 merge/rollback
- [ ] 支持断点续跑和长期循环
- [ ] 有完整的版本历史和回滚能力

---

**备注**：如在新对话中接手此项目，请先阅读本文件，确保理解"独立 self-improving agent"的定位，不要与 Hermes Agent 集成混淆。
