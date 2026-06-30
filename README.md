# Self-Upgrade Agent

自主升级的 AI Agent：搜索最新论文 → 筛选创新方法 → 生成技能 → 真实评估 → 决策留存。
支持 Skill 生命周期管理（注册、追踪、修剪、重评估）。

## 架构

```
src/
├── llm.py              ModelScope/Qwen LLM 调用层
├── config.py           配置加载 (YAML → dataclass)
├── research.py         arXiv 论文搜索 (真实 API)
├── filter.py           论文筛选 (keyword + LLM 双模式)
├── skillgen.py         技能生成 (模板 + LLM 双模式)
├── evaluate.py         A/B 评估 (模拟 + LLM 双模式)
├── decide.py           阈值决策 + 自动回滚
├── skill_lifecycle.py  生命周期管理 (注册/追踪/修剪/重评估)
├── db.py               SQLite 持久化 (3 张表)
└── pipeline.py         完整管线编排器

run.py                  命令行入口
config.yaml             所有配置
upgrades/               运行时产出 (skills/, snapshots/, history.db)
```

## 工作流程

```
1. RESEARCH  → arXiv API 搜索最新论文
2. FILTER    → 评分筛选 (keyword/LLM)
3. GENERATE  → 生成 Hermes Agent SKILL.md (template/LLM)
4. EVALUATE  → A/B 对比：baseline vs upgraded (simulated/LLM)
5. DECIDE    → 阈值判断 (成功率 + 成本), 自动回滚
                ↓
6. LIFECYCLE → 注册新 skill, 追踪使用, 定期修剪
```

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 LLM (ModelScope)
cp .env.example .env
# 编辑 .env 填入：
#   LLM_API_KEY=ms-***
#   LLM_MODEL=Qwen/Qwen3.5-35B-A3B

# 3. 运行管线
python run.py              # 模拟评估 (快速验证)
python run.py -v           # 详细日志
python run.py --stats      # 查看升级历史
python run.py --cull       # 修剪低效 skill
python run.py --evaluate-skills  # 重评估所有活跃 skill
```

### 启用真实 LLM 评估

编辑 `config.yaml`：
```yaml
evaluate:
  mode: llm           # simulated → llm
```

或者设置环境变量后直接运行 — 管线会自动检测 LLM 配置。

## 配置说明

| 配置段 | 关键字段 | 说明 |
|--------|---------|------|
| `research` | keywords, categories | arXiv 搜索范围 |
| `filter` | min_*_score | 论文打分阈值 |
| `evaluate` | mode, trials_per_test | lvm/simulated, 每次 N 轮 |
| `decide` | min_success_rate_delta, max_cost_increase_ratio | 决策阈值 |
| `lifecycle` | enabled, max_active_skills, inactivity_days | 生命周期参数 |
| `pipeline` | max_upgrades_per_cycle | 每轮最多升级几个 skill |

## 测试

```bash
# 纯逻辑测试 (无线) 
python -m pytest tests/ -m "not llm" -q

# LLM 集成测试 (需要 .env  置)
python -m pytest tests/ -m "llm" -q

# 全量
python -m pytest tests/ -q
```

## Skill 生命周期

```bash
# 修剪过期/低效 skill
python run.py --cull

# 重新评估所有活跃 skill
python run.py --evaluate-skills
```

修剪规则：
- 连续 30 天未使用 → 归档
- 改善度为负 (skill 帮倒忙) → 归档
- 超出 `max_active_skills` 限制 → 淘汰低效用者
