# README — Detail (L2)

> L0: L2 detail for `README.md`.  Per P11 摘要+引用,
> the README file is the L0/L1 layer (≤ 7KB); this
> file is the L2 layer (code legacy + CLI + history).
> Per R6, this companion is referenced from the README.

---

## Code legacy (v1.x-v3.x)

This project was originally a self-improving agent that modifies
`core/planner.py`.  The code still exists and is functional, but is
no longer the project's focus.  It is kept because 74 tests and 5
CLI scripts exercise `src/` (removing it would break CI).

### 工作流程

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

### 架构

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
├── benchmarks/tasks.json    # 22 个 benchmark 任务
├── tests/                   # ~875 测试
├── upgrades/                # 运行时产出 (candidates/backups/manifest)
└── config.yaml              # 配置
```

## 当前 CLI (python -m self_upgrade)

```
python -m self_upgrade improve [--single --paper <id>] [--count N] [--auto-commit]
python -m self_upgrade replay [--live]        # inspect (fast) or replay failures
python -m self_upgrade test-scale N           # N consecutive single-paper rounds
python -m self_upgrade daily-loop [--interval N] [--max-rounds N]
python -m self_upgrade chat                   # interactive chat
python -m self_upgrade cron [--install|--apply|--show]
```

- `improve`: 跑一轮自我改进（默认 multi-paper + harness 2 retries）。
- `replay`: 查看/重放 `upgrades/failures.jsonl` 中的失败（P18）。
- `test-scale`: 连续 N 轮（调试/负载/稳定性）。
- `daily-loop`: 自主循环，每 `--interval` 秒一轮，Ctrl-C 停止。
- `chat`: 交互式对话。
- `cron`: v4.0.0 定时部署（dry-run 默认，P9）。

完整参数见 `python -m self_upgrade <subcommand> --help`。

## 配置说明

```bash
# 1. 安装 + 配置
pip install -r requirements.txt
cp .env.example .env  # 编辑填入 LLM_API_KEY 和 LLM_MODEL

# 2. 使用 agent (日常)
python -m core.agent "Plan a 3-day trip to Tokyo"

# 3. 自我进化 (自主)
python -m self_upgrade improve --count 5     # 5 rounds
python -m self_upgrade daily-loop            # 自主循环

# 4. 维护
python -m self_upgrade replay                # 查看失败记录
```

## 测试

```
pytest tests/  # ~875 tests
```

## 项目历史

- v1.0-v1.5: initial self-improving agent
- v1.6.0: quota/key management fixes
- v1.7.0-v1.8.x: scaling, MCP tools, LangGraph
- v2.x: docs + P-n + M-n + skill-generation-knowledge
  (agent discipline knowledge library focus)

完整发布日志见 `CHANGELOG.md`。

---

## Why README is split into README.md + README_DETAIL.md

Per P11 摘要+引用 + R5 + P20 progressive disclosure: the
main README should be L0/L1 layer only (≤ 7KB, project
orientation, current state, links).  Code legacy detail
(workflow, architecture, CLI, config, testing, history)
goes to L2 detail companion.

## Cross-references

- `AGENTS.md` — operating rules for new agents
- `docs/HOW_TO_READ_GRAPH.md` — 3-step read pattern
- `docs/HANDOFF.md` — project-specific onboarding
- `docs/PROJECT_STATE.md` — current state snapshot
- `docs/SKILL_DESIGN.md` — skill-generation knowledge
