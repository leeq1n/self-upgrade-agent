# Self-Upgrade Agent

通过搜索最新论文 → 生成代码补丁 → 真实 benchmark 对比 → 自动部署来**自主改进自身源代码**的 AI Agent。

> **v1.6.0** — ISS-013/012 修复完成（filter 真正用 LLM；benchmark dataclass 兼容）；`--unlock-keys` 命令；ModelScope 网关稳定性 ISS-014 文档化。v1.5.0 commit 97aa0a1 留下真实端到端 promote 历史证据。

## 工作流程

```
1. RESEARCH  → 多源搜索（arXiv + Semantic Scholar + PwC + GitHub，可选）
2. FILTER    → 三维评分筛选 + citation 信号（keyword + LLM 双模式）
3. PATCHGEN  → LLM 生成 Python 代码补丁（目标：core/planner.py）
4. SANDBOX   → 隔离子进程验证代码正确性
5. REFLECT   → 失败后 LLM 自动修复（最多 3 轮）
6. EVALUATE  → 真实 benchmark A/B 对比（baseline vs patched）+ bootstrap 显著性
7. DECIDE    → 阈值判断 + 统计 CI → keep 或 revert
8. DEPLOY    → bootloader 原子写入 core/ 模块，备份旧版本
9. LIFECYCLE → 版本追踪、使用统计、定期修剪
```

## 架构

```
                        ┌──────────────────────────────────────┐
                        │         Self-Upgrade Pipeline         │
                        │         (src/pipeline_lg.py)         │
                        └──────────────────────────────────────┘
                                          │
         ┌────────────┬──────────┬────────┼────────┬──────────┬───────────┐
         ▼            ▼          ▼        ▼        ▼          ▼           ▼
    ┌─────────┐ ┌─────────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌────────┐ ┌────────┐
    │RESEARCH │→│ FILTER  │→│PATCH  │→│SANDBOX│→│EVALUATE│→│DECIDE  │→│DEPLOY  │
    │arxiv+s2 │ │score 3D │ │generate│ │test   │ │A/B     │ │keep/   │ │write   │
    │+pwc+gh  │ │+citation│ │code   │ │isolate│ │bench   │ │revert  │ │core/   │
    └─────────┘ └─────────┘ └───────┘ └───┬───┘ └───────┘ └────────┘ └────────┘
                                          │fail
                                          ▼
                                     ┌────────┐
                                     │REFLECT │──→ retry sandbox (max 3x)
                                     │fix code│
                                     └────────┘

    Sources:                    Target:                   Decision:
    ┌──────────────────┐       ┌──────────────┐         ┌────────────────┐
    │ arXiv API (主)    │       │ core/planner  │         │ keep → promote │
    │ Semantic Scholar  │──→   │ core/agent    │──→     │      写入 core/ │
    │ Papers With Code  │       │ core/tools    │         │ revert→discard │
    │ GitHub Trending   │       └──────────────┘         └────────────────┘
    │ Selenium (回退)   │
    └──────────────────┘
```

### 文件布局
├── core/                    # Agent 核心（可被自我改进的目标）
│   ├── agent.py            # 主推理循环
│   ├── planner.py          # 任务规划（主要补丁目标）
│   └── tools.py            # 内置工具
├── src/                     # 自改进引擎
│   ├── research.py         # arXiv API 搜索 + 多源聚合
│   ├── research_s2.py      # Semantic Scholar citation 数据
│   ├── research_pwc.py     # Papers With Code trending
│   ├── research_github.py  # GitHub trending 仓库
│   ├── scraper.py          # Selenium 浏览器回退
│   ├── filter.py           # 论文筛选 + 评分
│   ├── keyword_expander.py # 动态关键词提取
│   ├── patchgen.py         # 代码补丁生成
│   ├── sandbox.py          # 沙箱隔离执行
│   ├── reflect.py          # 失败自动修复
│   ├── benchmark.py        # Agent benchmark 运行器
│   ├── evaluate.py         # A/B 评估
│   ├── stats.py            # Bootstrap 统计显著性
│   ├── decide.py           # 决策逻辑
│   ├── switcher.py         # bootloader 版本管理
│   ├── pipeline_lg.py      # LangGraph 完整管线
│   ├── skill_lifecycle.py  # 生命周期管理
│   ├── db.py               # SQLite 持久化
│   ├── llm.py              # LLM 调用层
│   └── config.py           # 配置
├── benchmarks/tasks.json   # 21 个 benchmark 任务（6 类别）
├── tests/                   # 78+ 测试
├── upgrades/                # 运行时产出（candidates/backups/manifest）
├── config.yaml              # 配置
└── run.py                   # CLI 入口
```

## 统一入口 (v1.8.0)

> 之前 `python -m core.agent` 跟 `python run.py` 是两套独立入口,
> 看起来像两个产品。v1.8.0 统一为 `python -m self_upgrade <subcommand>`。
> 旧入口仍可工作(向后兼容)。

| Subcommand | 等价于旧 | 用途 |
|------------|---------|------|
| `run "task"` | `python -m core.agent "task"` | 使用 agent 解决任务 |
| `evolve [--live]` | `python run.py [--live]` | 自我进化(7 阶段) |
| `status` | `python run.py --stats` | 查看历史/版本 |
| `unlock` | `python run.py --unlock-keys` | 恢复 quota_state |
| `cull` | `python run.py --cull` | 修剪低效 skill |

```bash
# 1. 安装 + 配置
pip install -r requirements.txt
cp .env.example .env  # 编辑填入 LLM_API_KEY 和 LLM_MODEL

# 2. 使用 agent（日常）
python -m self_upgrade run "Plan a 3-day trip to Tokyo"
python -m self_upgrade run "Write a palindrome check in Python"

# 3. 自我进化（自主）
python -m self_upgrade evolve          # dry-run, 秒级
python -m self_upgrade evolve --live   # 真实 LLM benchmark

# 4. 维护
python -m self_upgrade status          # 看 history.db + manifest + planner 版本
python -m self_upgrade unlock          # 重置 quota_state (key 被 mark dead 时用)
python -m self_upgrade cull            # 修剪低效 skill
```

## 命令行参数

```
--live              真实评估模式（运行完整 LLM benchmark）
--stats             显示升级历史统计
--cull              归档低效/过期 skill
--evaluate-skills   重新评估所有活跃 skill
--promote PATCH     手动将候选补丁提升为活跃版本（写入 core/ 模块）
--schedule          输出 crontab 配置
--daemon            后台守护模式，每 24h 自动运行
--config PATH       自定义配置文件路径
--legacy            使用旧版 skillgen pipeline（仅供兼容）
-v, --verbose       DEBUG 级别日志
--version           显示版本信息
```

## 配置说明

| 配置段 | 关键字段 | 说明 |
|--------|---------|------|
| `research` | keywords, categories, multi_source | 搜索范围 + 多源开关 |
| `filter` | min_*_score | 论文打分阈值 |
| `implement` | max_attempts, backup_existing_skill | 补丁生成和安全策略 |
| `evaluate` | mode, trials_per_test (10) | 评估模式（llm/simulated）、每 task 试验次数 |
| `decide` | min_success_rate_delta, max_cost_increase_ratio | 决策阈值 |
| `lifecycle` | max_active_skills, inactivity_days | 生命周期参数 |
| `pipeline` | max_upgrades_per_cycle, auto_promote | 每轮最多升级数和部署策略 |

启用多源搜索：在 `config.yaml` 中设置 `research.multi_source: true`，将同时搜索 arXiv、Semantic Scholar、Papers With Code、GitHub。

## 测试

```bash
# 默认：自动跳过 @pytest.mark.llm 和 @pytest.mark.network 测试
# （除非环境变量里配了 LLM_API_KEY_*，才会真正跑 LLM 测试）
python -m pytest tests/ -q

# 显式只跑纯逻辑测试
python -m pytest tests/ -m "not llm and not network" -q

# 强制跑 LLM 测试（即使没配 key）
HERMES_FORCE_LLM=1 python -m pytest tests/ -m "llm" -q

# 跳过网络相关测试（CI 默认推荐）
HERMES_SKIP_NETWORK=1 python -m pytest tests/ -q

# 极快模式（也跳 slow 测试）
HERMES_FAST=1 python -m pytest tests/ -q
```

`conftest.py` 会在以下情况自动 skip：
- `@pytest.mark.llm` 测试 + 环境里没有 `LLM_API_KEY_*`（或 `LLM_API_KEY`）
- `@pytest.mark.network` 测试 + `HERMES_SKIP_NETWORK=1`
- `@pytest.mark.slow` 测试 + `HERMES_FAST=1`

## 文档

- [API Reference](docs/API_REFERENCE.md) — 所有模块和函数的完整签名
- [LLM Calls & Key Rotation](docs/LLM_CALLS.md) — 多 key 轮换、quota 持久化、模型路由
- [System Constraints](docs/CONSTRAINTS.md) — 7 个不变性（代码不崩 / 可恢复 / 不臃肿 / quota 受控 / 不静默 promote / 失败可观测 / 干净克隆可重现）+ 验证方法
- [CLI Guide](docs/CLI_GUIDE.md) — `python -m self_upgrade <sub>` 完整使用手册（run / evolve / status / unlock / cull + 3 round stress test 复现脚本）
- [Project Brief](PROJECT_BRIEF.md) — 项目状态和能力评估
- [Delivery](docs/DELIVERY.md) — v1.5.0 端到端 promote 案例 + 交付水平评估
- [Design Philosophy](docs/DESIGN_PHILOSOPHY.md) — 10 条设计原则（来自项目迭代）
- [Issues](ISSUES.md) — 已知问题 + v1.6.0 路线图
- [Plans](.hermes/plans/) — 历史改进计划和验收报告

## 版本历史

- **v1.5.1** (2026-06-30): atomic A/B bootloader write + sys.modules 缓存清理；ISS-004 评估路径统一
- **v1.5.0**: ISS-001 filter 关键词 boost + ISS-002 诊断 + ISS-004 status；真实端到端 promote `planner.py` 成功
- **v1.4.0**: surgical-merge bootloader + LLM JSON 围栏清洗
- **v1.3.0**: LLM 默认 model = Qwen3.5-2B + total_timeout + diagnostic
- **v1.2.0**: 修复 benchmark 补丁应用（surgical merge）、--live 标志生效、多源搜索（S2/PwC/GitHub）、benchmark 任务 8→21
- **v1.1.0**: bootloader 原子写入 core/、pipeline_lg 重构、stats.py bootstrap、research_s2.py、keyword_expander.py
- **v1.0.0**: 完整闭环原型（LangGraph pipeline、patchgen、switcher、评估）
