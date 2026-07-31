# README — Detail (L2)

> L0: L2 detail for `README.md`.  Per P11 摘要+引用,
> the README file is the L0/L1 layer (≤ 7KB); this
> file is the L2 layer (code legacy + project history).
> Per R6, this companion is referenced from the README.

---

## Self-improving agent — Code legacy (v1.x-v3.x)

Per c73 pivot note: this project was originally a
self-improving agent that modifies `core/planner.py`.
The code still exists and is functional, but is no
longer the project's focus (c73 + c81 + c83 explicitly
shifted focus to docs + skill generation).

### 工作流程 (per c50 audit archived)

```
1. RESEARCH  → 多源搜索 (arXiv + Semantic Scholar + PwC + GitHub, 可选)
2. FILTER    → 三维评分筛选 + citation 信号 (keyword + LLM 双模式)
3. PATCHGEN  → LLM 生成 Python 代码补丁 (目标: core/planner.py)
4. SANDBOX   → 隔离子进程验证代码正确性
5. REFLECT   → 失败后 LLM 自动修复 (最多 3 轮)
6. EVALUATE  → 真实 benchmark A/B 对比 (baseline vs patched) + bootstrap 显著性
7. DECIDE    → 阈值判断 + 统计 CI → keep 或 revert
8. DEPLOY    → bootloader 原子写入 core/ 模块, 备份旧版本
9. LIFECYCLE → 版本追踪、使用统计、定期修剪
```

### 架构 (per c50 audit archived)

```
self-upgrade-agent/
├── core/                    # agent 主循环 + LLM 适配
│   ├── agent.py             # 主 agent (LangGraph ReAct)
│   ├── planner.py           # 核心改造目标 (legacy)
│   ├── patchgen.py          # 补丁生成
│   ├── filter.py            # 论文筛选
│   ├── evaluate.py          # A/B benchmark
│   ├── reflector.py         # 失败反思
│   └── config.py            # 配置
├── benchmarks/tasks.json    # 21 个 benchmark 任务 (6 类别)
├── tests/                   # 78+ 测试
├── upgrades/                # 运行时产出 (candidates/backups/manifest)
└── config.yaml              # 配置
```

### 统一入口 (v1.8.0)

| Subcommand | 等价于旧 | 用途 |
|------------|---------|------|
| `run "task"` | `python -m core.agent "task"` | 使用 agent 解决任务 |
| `evolve [--live]` | `python run.py [--live]` | 自我进化 (7 阶段) |
| `status` | `python run.py --stats` | 查看历史/版本 |
| `unlock` | `python run.py --unlock-keys` | 恢复 quota_state |
| `cull` | `python run.py --cull` | 修剪低效 skill |

### CLI 详细参数

```
--live              真实评估模式 (运行完整 LLM benchmark)
--stats             显示升级历史统计
--cull              归档低效/过期 skill
```

(更多参数见 `python -m self_upgrade --help`)

### 配置说明

```bash
# 1. 安装 + 配置
pip install -r requirements.txt
cp .env.example .env  # 编辑填入 LLM_API_KEY 和 LLM_MODEL

# 2. 使用 agent (日常)
python -m self_upgrade run "Plan a 3-day trip to Tokyo"
python -m self_upgrade run "Write a palindrome check in Python"

# 3. 自我进化 (自主)
python -m self_upgrade evolve          # dry-run, 秒级
python -m self_upgrade evolve --live   # 真实 LLM benchmark

# 4. 维护
python -m self_upgrade status          # 看 history.db + manifest + planner 版本
python -m self_upgrade unlock          # 重置 quota_state (key 被 mark dead 时用)
python -m self_upgrade cull            # 修剪低效 skill
```

### 测试

```
pytest tests/  # 78+ tests (per c50 audit: 621+ tests pass + 6 skip + 0 fail)
```

### 项目历史 (per c50 audit, partial)

- v1.0-v1.5: initial self-improving agent
- v1.6.0: ISS-013/012 fixes (filter LLM wiring)
- v1.7.0-v1.8.x: scaling, MCP tools, LangGraph
- v2.0.0: minimal v2 with intent to focus on rules project
- v2.0.0-minimal (current branch): docs + P-n + M-n +
  sibling project + skill-generation-knowledge

### Last P20-verified

2026-07-15 (per c85 README vision sync).

---

## Why README is split into README.md + README_DETAIL.md

Per P11 摘要+引用 + R5 + P20 progressive disclosure: the
main README should be L0/L1 layer only (≤ 7KB, project
orientation, current state, links).  Code legacy detail
(workflow, architecture, CLI, config, testing, history)
goes to L2 detail companion.

This split is the **R5 fix for README** — same pattern
applied to PROJECT_TOPDOWN_AUDIT (c60), PRINCIPLES (c72),
KNOWLEDGE_ORG (c81), and other 11 docs (c60-c83 batch).

## Cross-references

- `AGENTS.md` — operating rules for new agents
- `docs/HOW_TO_READ_GRAPH.md` — 3-step read pattern
- `docs/HANDOFF.md` — project-specific onboarding
- `docs/PROJECT_STATE.md` — current state snapshot
- `docs/SKILL_DESIGN.md` — SUA 维护的 skill-generation-knowledge
- `../agent-reflection-skill/` — sibling project
