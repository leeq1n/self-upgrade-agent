# v1.8.0 Multi-Agent Harness 重构计划

> **目标**: 让 self-upgrade agent 能持续在 multi-agent 方向进化,
> 在上下文不崩的前提下实现"自进化闭环"
>
> **基于行业研究** (2026-07-02 web search):
>   * MAE (Multi-Agent Evolve, arXiv 2510.23595) — Proposer-Solver-Judge
>   * SEAE (Self-Evolving Agent Engineering, 2026) — 3 核心机制
>   * LangGraph MAS — 角色分工 + 通信 + 协调
>   * Agent Harness Survey 2026 — 不对称 co-evolution

---

## 一、当前 v1.7.2 阻碍自进化的硬约束(真实问题)

| # | 约束 | 来源 | 影响 |
|---|------|------|------|
| HC1 | `CORE_MODULES` 白名单只有 3 个文件 (planner/agent/tools) | `src/switcher.py:37-41` | 新 agent 文件无法 promote |
| HC2 | `_apply_patch_to_module` 只支持单文件 surgical merge | `src/pipeline_lg.py:71` | multi-file patch 拒绝 |
| HC3 | `should_promote` 只看 `core/planner.py` benchmark delta | `src/evaluate.py` | 架构变更永远 0 delta → reverted |
| HC4 | benchmark 只测 single-agent task (planning/reasoning/math) | `benchmarks/tasks.json` | multi-agent 协作改进测不出 |
| HC5 | `core/agent.py` 顶部 `from core.planner import plan_task` 硬编码 | `core/agent.py:11` | 新 agent 不会被 import |
| HC6 | 7 节点 StateGraph 是 sequential single-role | `src/pipeline_lg.py:653` | 不是多 agent 通信图 |
| HC7 | 缺跨 session persistent memory (SEAE 核心) | 没有 | 失败不累积 |
| HC8 | 缺 closed-loop RL pipeline (SEAE 核心) | 没有 | 无法"训练下一代" |
| HC9 | 缺 harness 反思(失败 WHY) | 没有 | 重试同样 prompt |
| HC10 | 缺终止条件(目标达就停) | 没有 | 浪费 quota |

---

## 二、v1.8.0 排程(按 ROI + 依赖排序)

### Phase A: Harness 框架(让自进化"路径通")- 1 周

#### A1. 加跨 session memory (HC7) - 1 天
- 失败原因累积表
- 表 schema: `(attempt_id, paper_id, paper_type, failure_mode, llm_model, prompt_strategy, lessons)`
- 写到 `upgrades/learning.db` (新 SQLite,跟 history.db 分离)
- 关键: **不要试图把 history.db 改造成 learning.db** — 关注点分离
- 验证: 单元测试断言失败 reason 持久化

#### A2. 加 closed-loop 反馈 (HC8 部分) - 1 天
- patchgen 失败时,记录 `(paper_type, error, suggested_retry_strategy)`
- 下次 filter 看到同 paper_type,自动 apply 之前 lessons
- **关键**: 不是"自动重试" — 是"避免同样失败"

#### A3. 加终止条件 (HC10) - 1 天
- `--max-rounds N` (硬上限)
- `--target-delta 0.05` (达到就停)
- `--convergence-window 5` (连续 5 round 无进步就停)
- 关键: **不是"加更多" — 是"明确什么时候停"**

#### A4. 加 paper 排除 (HC9) - 1 天
- 黑名单: `(paper_id, reason)`
- 避免反复试同一 paper
- 关键: **失败是数据,不是噪声**

#### A5. 单元测试 + 文档 (HC7-HC10) - 1 天
- 5 个新 invariant test
- `docs/CONSTRAINTS.md` 加 C8-C10 (新增 3 个不变性)
- **关键**: 不写单元测试的功能 = 不存在

### Phase B: 架构灵活性(让多 agent 创新能落地) - 1.5 周

#### B1. `CORE_MODULES` 白名单放宽 (HC1) - 半天
- 从固定 3 个文件 → 允许 `core/*_agent.py` 模式
- 加新文件时,必须满足命名约定 + 1 个测试文件
- 关键: **不是"无限制" — 是"约定驱动"**

#### B2. multi-file patch 支持 (HC2) - 2 天
- patch JSON 加 `files: [{path, function}, ...]`
- 多个文件 surgical merge 一起应用
- atomic rollback (整个 multi-file 一起)
- 关键: **multi-file 必须 atomic — 不允许半应用**

#### B3. `core/agent.py` import 改成 dynamic (HC5) - 1 天
- 改 hardcoded `from core.planner import plan_task` →
  `importlib.import_module(f"core.{name}")` 风格
- 加 agent registry 表: `(name, module_path, role, prompt_strategy)`
- 关键: **dynamic 但显式 — agent 注册,不是 magic**

#### B4. benchmark 加 multi-agent 协作 task (HC4) - 2 天
- 5 个新 task (e.g. "两个 agent 一个 plan 一个 verify ...")
- 必须能跑通(测试用 mock LLM 验证 task schema 正确)
- 关键: **不真调 LLM 测 — 那是 benchmark 的事**

#### B5. 单元测试 (HC1, HC2, HC4, HC5) - 1 天
- multi-file patch 的 atomic rollback 测试
- dynamic import 不破 planner 的测试
- multi-agent task schema 测试

### Phase C: 真实 multi-agent harness 跑通(让系统真自进化一次) - 1 周

#### C1. 跑通 v1.7.2 已有 7 节点 + 1 个 multi-agent node - 3 天
- 8 节点 StateGraph: 7 旧 + 1 个 new "verifier_agent" 节点
- 这个新 node 调 LLM 验证 patch
- 验证: 8 节点流程跑完 1 round,history.db 记录新 node
- 关键: **先加 1 个新 node,不要 5 个**

#### C2. 跑通 multi-agent reflection loop - 2 天
- 如果 verifier_agent 说"不通过",patchgen 收到 verifier 的反馈
- patchgen 调 LLM 用 verifier 反馈重新生成
- 关键: **反思要基于真实反馈,不是空 prompt**

#### C3. 端到端 stress test - 2 天
- 3 round stress test (用 C1 8 节点流程)
- 监控 C8-C10 (新增 3 个不变性)
- 关键: **不跑更多,先验证 C1-C2**

---

## 三、上下文管理(你的"上下文不崩"约束)

### 原则
- **不**在回复里展开大段 plan (上文已写 plan file)
- **不**重复设计 (引用 `docs/CONSTRAINTS.md`)
- **不**复述 commit (引用 `git log`)
- **不**重复实验数据 (引用 `history.db`)

### Token budget (估算)
- Phase A: ~50K tokens (10 个小 commit)
- Phase B: ~80K tokens (5 个大 commit)
- Phase C: ~60K tokens (3 个 medium commit)
- **总计: ~200K tokens**

### 上下文保护策略
1. 每次 commit 后,**刷新 working tree 状态** (不累积)
2. 跑完一段,**压缩回 handoff note** (不保留完整 log)
3. 关键设计决策写到文件,**不写在 chat**
4. **遇到 TPM 限流立即停** — 不要再硬试

---

## 四、成功标准

**v1.8.0 算交付,如果**:
1. ✅ 154+ unit test + 5 skip = 0 fail
2. ✅ 7 个旧不变性 + 3 个新不变性 (C8 跨 session memory, C9 reflection feedback, C10 终止条件)
3. ✅ multi-file patch 真能 atomic apply/rollback
4. ✅ 1 个 multi-agent node 真接进 StateGraph 并跑通 1 round
5. ✅ core/planner.py MD5 跨所有 round 稳定

**不算交付,如果**:
- ❌ 跑通但只靠 mock (不是真 LLM)
- ❌ 新增 multi-agent 但没真改进 (delta=0)
- ❌ 测试通过但 context 崩了 (QuotaState 损坏 etc.)
- ❌ 单元测试用 mock 凑数 (不真测 invariant)

---

## 五、不做(明确边界)

为了避免你提的"限制条件过多"问题,**v1.8.0 不做**:
- ❌ 完全 5 agent 重设计 — 只加 1 个 verifier
- ❌ 重写 `core/agent.py` — 只改 import 方式
- ❌ 替换 benchmark — 只加 5 个 multi-agent task
- ❌ 真实 RL fine-tune — 只到"训练下一轮"层面
- ❌ 完全动态 agent 拓扑 — 保持 StateGraph 静态

**理由**: 每个"不做"都是 1 周工作,加起来 5 周。**v1.8.0 只要 3 周**,必须砍。

---

## 六、排程时间线

```
Week 1:  Phase A (A1-A5) — Harness 框架
         Day 1-4: A1-A4 实现
         Day 5: A5 测试+文档
         Commit: 5 个小 commit

Week 2-3 (前 1.5 周):  Phase B (B1-B5) — 架构灵活性
         Day 6: B1 (白名单)
         Day 7-8: B2 (multi-file)
         Day 9: B3 (dynamic import)
         Day 10-11: B4 (benchmark)
         Day 12: B5 测试
         Commit: 5 个 medium commit

Week 3 (后 1 周):  Phase C (C1-C3) — multi-agent harness
         Day 13-15: C1 (8 节点流程)
         Day 16-17: C2 (reflection loop)
         Day 18-19: C3 (stress test)
         Commit: 3 个 medium commit

Total: 19 工作日 (3 周 + 1 天)
```

---

## 七、风险与缓解

| 风险 | 概率 | 缓解 |
|------|------|------|
| Phase A 学习表 schema 错 | 中 | 写 test 前先 review schema |
| Phase B multi-file atomic 写漏 | 高 | 复用 `_apply_patch_to_module` 逻辑 |
| Phase C verifier 跟 patchgen 通信 bug | 高 | 显式 state 字段,不隐式 shared memory |
| LLM quota 烧光 (v1.7.2 教训) | 高 | 每天最多 1 round 真实 LLM 测 |
| TPM 4-5M context 限制 (你警告) | 高 | commit 后立即压缩 + 写到文件 |
| ISS-014 ModelScope 网关不稳 | 高 | 已 commit `--unlock-keys` 恢复路径 |

---

## 八、立即可做的(今天)

如果你同意这 plan,**今天可以**:
1. ✅ 创建 `docs/PLAN_v180.md` (本文)
2. ✅ 加 `learning.db` schema (A1) - 0 quota
3. ✅ 写 C8/C9/C10 不变性测试 (A5 部分) - 0 quota
4. ❌ **不**跑 LLM (quota 保护)
5. ❌ **不**改 src/ (Phase A 完整 plan 后再动)

**今天的 commit**: 1-2 个 (docs + tests)
