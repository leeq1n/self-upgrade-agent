# 设计哲学:涌现 vs 固定

> v1.8.1 — 这是项目的核心 invariant。改了下面这些分类,会破坏整个系统。

## 1. LLM 应该涌现的功能(不靠代码)

这些**必须**靠 LLM,**代码只提供框架**:

| 功能 | LLM 涌现什么 | 代码提供什么 |
|---|---|---|
| `plan_task` (in core/planner.py) | 任务分解为步骤 | 输入输出 schema + 类型 hint |
| `node_filter` (论文评分) | 论文相关性判断 | 关键词 boost safety net |
| `node_implement` (patchgen) | 生成 patch 代码 | patch schema + 格式约束 |
| `node_reflect` | 修复 sandbox failure | retry 上限 (3 次) |
| `node_evaluate` (LLM 评分部分) | 21 task 评分 | task 列表 + A/B 框架 |
| `core/agent.run` | 工具选择 + reasoning | tool registry + loop |

**为什么不让代码固定**:这些是 LLM 应该擅长的。如果代码固定了 plan,
就退化成 rule-based system,失去 "调大模型改自己" 的意义。

## 2. 代码必须固定的功能(不靠 LLM)

这些**绝不**让 LLM 决定 — 必须代码固定,因为:

| 功能 | 为什么必须固定 | 失败代价 |
|---|---|---|
| **harness (run_harness)** | 真测试 = 客观真理 | LLM 自评 → LLM 骗 LLM |
| **decision (4 步)** | safety net | 错一次 = 烂代码入生产 |
| **switcher atomic write** | 并发安全 | 损坏 manifest.json |
| **node_skill_audit** | 0 LLM(省钱) | 多余调用浪费 quota |
| **mark_paper_seen** | 防止重复 | 浪费 LLM calls |
| **streaming output** | 底层 API | 用户看不到进度 |
| **preflight restore** | safety net | 烂 patch 卡住 planner.py |

**为什么不让 LLM 涌现**:LLM 不能"自我审查"。**harness 是独立 Python 测试,
不依赖 LLM**。这是项目的"宪法",不可动摇。

## 3. 边界 case — 哪些是"涌现 vs 固定"模糊地带

| 模糊地带 | 当前选择 | 理由 |
|---|---|---|
| patch 接受/拒绝 | **固定**(harness + LLM delta) | 必须有 safety net |
| 论文筛选 | **LLM 主导**,关键词 safety net | LLM 强项,关键词救场 |
| skill 评分 | **固定**(use_count × avg_improvement) | 必须客观 |
| skill 销毁 | **固定**(score < 阈值) | 必须有规则 |
| node failure 修复 | **LLM**(reflect) | LLM 强项 |
| node failure 重试次数 | **固定**(3 次) | 必须有上限 |

## 4. 为什么这个分类重要

如果让 LLM 决定 "应该销毁 skill",**LLM 可能有 incentive 保留自己写的 skill**。

如果让代码固定,所有 skill 都用同一标准评价。**公平、可审计、可解释**。

如果让 LLM 决定 "patch 是否破坏代码",**LLM 可能自我宽容**。

如果让 harness 真跑测试,**真破坏 = 100% 检测**(v1.8.0 Day 3 已验证)。

## 5. 这个分类不会变(版本 invariant)

- **v1.8.0 之前**:决定权几乎全在 LLM,system "看起来" 工作但脆弱
- **v1.8.0+**:harness-first decision,4 步强制,harness < 100% 直接 reject
- **v1.8.1**:seen-papers 强制,streaming 强制,这个文档强制

**改这个分类 = 改项目的灵魂 = 不要做**。