# Self-Upgrade Agent — 达成目标完成计划

> **For Hermes:** 使用 plan skill 指导分步实施。

**目标:** 构建能自主搜索论文、生成代码补丁、测试、部署到自身核心模块的自进化 Agent。

**当前状态:** 85% 完成。核心管线已打通，缺沙箱稳定性、工具注册、真实 benchmark 和调度器。

---

## 任务 1: 修复 core/planner.py

**目标:** planner 是独立模块，不是 agent.py 副本。

**文件:** core/planner.py (重写), core/agent.py (import from planner)

**实施:**
1. core/planner.py 只保留 plan_task 函数
2. core/agent.py 添加 from core.planner import plan_task，删除本地定义

**验证:** python -c "from core.agent import run; from core.planner import plan_task"

---

## 任务 2: 注册真实工具

**目标:** Agent 能调用 shell/文件/计算工具。

**文件:** core/tools.py (新建), core/agent.py (启动时注册)

**实施:**
1. core/tools.py: tool_shell, tool_read_file, tool_calculate
2. agent.py run() 开头注册三个工具

**验证:** agent 运行 calculator 任务时 tools_used > 0

---

## 任务 3: 修复沙箱 unittest runner

**目标:** LLM 生成的 unittest.TestCase 代码能在沙箱通过。

**文件:** src/sandbox.py

**实施:**
1. 模板末尾添加 unittest.TestLoader 自动发现 TestCase
2. 确认 Node stub + typing imports 存在

**验证:** 生成 MCTS 代码后 sandbox PASS

---

## 任务 4: 连接真实 Benchmark A/B

**目标:** 评估不再用模拟数据，而是真正跑 agent benchmark。

**文件:** src/benchmark.py (新建), src/pipeline_lg.py (修改)

**实施:**
1. benchmark.py: 加载 tasks.json，运行 agent，返回 success_rate
2. pipeline node_evaluate: 调用 benchmark 对比 baseline vs patched

**验证:** benchmark 返回真实 success_rate (非随机数)

---

## 任务 5: 修复 LangGraph reflect 循环

**目标:** 沙箱失败 → reflect → 重试 (最多 3 次)

**文件:** src/pipeline_lg.py

**实施:** node_reflect 正确调用 reflect_and_improve() 并更新 state

---

## 任务 6: 内置调度器

**目标:** 不依赖外部 cron，自动每日运行。

**文件:** run.py

**实施:** --daemon 模式，每 24h 运行一次 pipeline

---

## 任务 7: 新模块测试

**文件:** tests/test_core_agent.py, tests/test_patchgen.py, tests/test_switcher.py

**实施:** import + 单元 + 集成测试（非 LLM 依赖）

---

## 任务 8: 端到端验证

清理 → 运行 pipeline → 检查 core/planner.py 是否被修改

---

## 实施顺序与时间

1. 修复 planner (5min)
2. 注册工具 (10min)
3. 修复沙箱 (15min)
4. 真实 benchmark (15min)
5. 修复 reflect (5min)
6. 调度器 (10min)
7. 测试 (15min)
8. 端到端 (10min)
总计: ~85min

## 风险
- LLM 生成代码不稳定 → reflect 循环最多 3 次
- arXiv 限流 → Selenium scraper 回退
- core 替换安全 → switcher 备份 + git

## 完成标准
- [x] 论文搜索+筛选
- [x] 代码生成 patchgen
- [x] 隔离沙箱
- [x] 候选/活跃/备份管理
- [x] LangGraph 管线
- [ ] 沙箱通过率 > 50%
- [ ] Agent 可调用真实工具
- [ ] Benchmark 真实对比
- [ ] Reflect 自动修复
- [ ] 每日自动调度
- [ ] 端到端跑通
