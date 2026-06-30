# Self-Upgrade Agent

通过搜索最新论文 → 生成代码补丁 → 真实 benchmark 对比 → 自动部署来**自主改进自身源代码**的 AI Agent。

> ⚠️ 当前状态：原型级。核心骨架已就位，但主链路尚未完全打通。详见 [PROJECT_BRIEF.md](PROJECT_BRIEF.md)。

## 工作流程

```
1. RESEARCH  → 搜索 arXiv 最新论文（API + Selenium 回退）
2. FILTER    → 三维评分筛选（适用性/新颖性/质量，keyword + LLM 双模式）
3. PATCHGEN  → LLM 生成 Python 代码补丁（目标：core/planner.py）
4. SANDBOX   → 隔离子进程验证代码正确性
5. REFLECT   → 失败后 LLM 自动修复（最多 3 轮）
6. EVALUATE  → 真实 benchmark A/B 对比（baseline vs patched）
7. DECIDE    → 阈值判断 + 统计显著性 → keep 或 revert
8. DEPLOY    → bootloader 原子写入 core/ 模块，备份旧版本
9. LIFECYCLE → 版本追踪、使用统计、定期修剪
```

## 架构

```
self-upgrade-agent/
├── core/                    # Agent 核心（可被自我改进的目标）
│   ├── agent.py            # 主推理循环
│   ├── planner.py          # 任务规划（故意做薄供 patch 改进）
│   └── tools.py            # 内置工具
├── src/                     # 自改进引擎
│   ├── research.py         # arXiv API 搜索
│   ├── scraper.py          # Selenium 刮取回退
│   ├── filter.py           # 论文筛选
│   ├── patchgen.py         # 代码补丁生成
│   ├── sandbox.py          # 沙箱隔离执行
│   ├── reflect.py          # 失败自动修复
│   ├── evaluate.py         # A/B 评估
│   ├── decide.py           # 决策
│   ├── switcher.py         # bootloader 版本管理
│   ├── benchmark.py        # Agent benchmark 运行器
│   ├── pipeline_lg.py      # LangGraph 完整管线
│   ├── skill_lifecycle.py  # 生命周期管理
│   ├── db.py               # SQLite 持久化
│   ├── llm.py              # LLM 调用层
│   └── config.py           # 配置
├── benchmarks/tasks.json   # Benchmark 任务集
├── tests/                   # 66+ 测试
├── upgrades/                # 运行时产出（candidates/backups/history）
├── config.yaml              # 配置
└── run.py                   # CLI 入口
```

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 LLM
cp .env.example .env
# 编辑 .env 填入 LLM_API_KEY 和 LLM_MODEL

# 3. 运行（当前为 dry-run 模式，评估用模拟数据）
python run.py              # 模拟评估（快速验证链路）
python run.py -v           # 详细日志
python run.py --stats      # 查看升级历史
python run.py --cull       # 修剪低效 skill
python run.py --schedule   # 输出 crontab 调度配置
python run.py --daemon     # 后台每 24h 自动运行
```

## 命令行参数

```
--live              真实评估（当前未完全实现，回退到 dry-run）
--stats             显示升级历史统计
--cull              归档低效/过期 skill
--evaluate-skills   重新评估所有活跃 skill
--promote SKILL     手动将候选 skill 提升为活跃
--schedule          输出 crontab 配置
--daemon            后台守护模式，每 24h 自动运行
--config PATH       自定义配置文件路径
-v, --verbose       DEBUG 级别日志
```

## 配置说明

| 配置段 | 关键字段 | 说明 |
|--------|---------|------|
| `research` | keywords, categories | arXiv 搜索范围 |
| `filter` | min_*_score | 论文打分阈值 |
| `implement` | max_attempts, backup_existing_skill | 补丁生成和安全策略 |
| `evaluate` | mode, trials_per_test | 评估模式（llm/simulated）、每 task 试验次数 |
| `decide` | min_success_rate_delta, max_cost_increase_ratio | 决策阈值 |
| `lifecycle` | max_active_skills, inactivity_days | 生命周期参数 |
| `pipeline` | max_upgrades_per_cycle, auto_promote | 每轮最多升级数和部署策略 |

## 测试

```bash
# 纯逻辑测试（不依赖网络）
python -m pytest tests/ -m "not llm" -q

# LLM 集成测试（需要 .env 配置）
python -m pytest tests/ -m "llm" -q

# 全量
python -m pytest tests/ -q
```

## 当前限制与下一步

详细改进计划见：`.hermes/plans/2026-06-30_comp-plan.md`

| 限制 | 影响 | 计划 |
|------|------|------|
| 信息源只有 arXiv | 错过有价值的方法 | 接入 Semantic Scholar / Papers With Code / GitHub |
| 评估用随机数 | 决策无意义 | 替换为真实 benchmark 执行 |
| 主流程走 skillgen 而非 patchgen | 不修改自身代码 | run.py 切换到 pipeline_lg |
| bootloader 不写 core/ | 代码从未真正改变 | switcher 改造为原子写入 core 模块 |
