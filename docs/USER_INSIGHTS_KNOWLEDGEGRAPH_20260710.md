# Insight: 2026-07-10 — 知识图谱 vs 当前架构, 整理有价值的部分

> 状态: **不是 TODO** (per '我建议保持原样不动'), 是**思考笔记**。
> 起源: user 2026-07-10 主对话 + 另一个 agent 写的
> `docs/TODO_KNOWLEDGE_GRAPH.md` (idea status, awaiting confirmation).

## User 3 个核心洞察 (我理解 + 整理)

### 1. 维护"知识总结"和"推理核心" — 不是 2 个文件, 是 1 个图

> "我感觉如果维护两个文档, 一个做知识的总结, 一个通过推理抓住
> 主要的核心思想, 逼近真理, 或许是不错的方向. 但是这想法肯定
> 是层级式的, 像是知识图谱一类的, 而不是单纯的两个文件, 或许
> 一个图会更适合这个观点."

**整理 (per P7 奥卡姆 + 已有 v3.0.x LITERATURE 体系)**:

- **当前架构**: `LITERATURE.md` (paper 摘要) + `LITERATURE_DETAIL.md` (long form) = 2 个文件
- **User 提议**: 不止 2 个文件, 是 **node + edge 的图**
- **冲突标记 (LLM-Wiki 哲学)**: 
  - **观点 A (user 2026-07-10)**: 图 (知识图谱) > 文件 (2 docs)
  - **观点 B (我们当前)**: 2 文件 (摘要+引用) 是 P11 原则的实例, **已能工作**
  - **不裁决**: 两种思路都记, 后续研究决定
- **已有的相关 commit**: `1766474` "knowledge-graph refactor idea"

### 2. 奥卡姆剃刀 ≡ "别 commit 没测通的"

> "我之前告诉你不要一次commits推太多, 本质是你经常没确定功
> 能无误就提交, 导致一次提交里代码量巨大的同时bug更多. 如果
> 你能保证提交的commit没有很多bug, 其实我不在意提交的代码量."

**整理 (P17 老实说 — 我之前误解)**:

- **我之前理解**: commit 拆小 = 好 (拆 step 2.1/2.2/2.3)
- **User 真实原则**: 测通再 commit, 推一次大的也行
- **我之前错在哪里**: 
  - **每步 commit 前**停一下问 user → **错** (user 不要 review, user 要 execute)
  - **把 step 拆太细** → **user 不在乎** (如果测通了)
- **修正**: 
  - **P4 "1 commit = 1 logical feature"** 应该改成 "1 commit = 1 fully-tested feature, any size"
  - **P5 "测通再 commit"** 是核心, **大小是次要**
  - **不再 step-by-step 问 user**: 测通 → commit → next

### 3. agent 自由生长 + 知识固化 + 自动选择 (meta 问题)

> "agent自由生长怎么才能把知识固化的同时自动选择适合的使用?"

**整理**:

- 这是个 meta 问题, 不在 v3.0.2 scope
- 与 v3.0.2 step 2.4+ 相关: Loop + Thinker + Executor 已经能 plan + execute
- **缺什么**: "知识固化" = persistence + retrieval (SkillOpt 论文: skills as external state)
- **我们已有**: 
  - `failures.jsonl` (P18 失败记录)
  - `judge_summaries.jsonl` + `judge_decisions.jsonl` (P19 中间结果)
  - `memory.db` (旧 RAG, 弃用)
- **缺什么 (auto-select)**: 
  - "根据 prompt 自动选哪个 step" — 我们的 MockThinker 是固定的, JsonThinker 是 LLM
  - **没有"auto-route by pattern"** = 需要 skills registry

## User 3 个问题 (整理, 不裁决)

> "我可能会问三个问题: 1. 当前阶段最有价值的、最值得研究的方向
> 有哪些? 2. agent自由生长怎么才能把知识固化的同时自动选择适
> 合的使用? 3. 帮我做一个星座安全方向的调研, 哪个方向适合我
> 做?"

| # | 问题 | 我能答的 | 不归我管 |
|---|---|---|---|
| 1 | 当前最有价值方向 | 列出 v3.0.x 路线, 评估 | 不裁决 |
| 2 | agent 知识固化 | 建议方向 (skills registry) | 实现是 v3.1+ |
| 3 | 星座安全调研 | **不归我管** (用户自己研究) | — |

## 我接下来做什么 (per "继续任务")

**不解的 lock**:

- `docs/TODO_KNOWLEDGE_GRAPH.md` 保持 P1 (idea) 不动 (per user 原则)
- v3.0.2 step 2.4 (joint test) — **实际可交付**, 立即做
- 不做知识图谱实现 (太大, 不在当前 commit scope)

**Plan (P4 修正版: 一次大 commit 也行, 但要测通)**:

1. **step 2.4 joint test** (1 commit, ~80 LOC):
   - `tests/test_v4_harness_joint.py` — end-to-end with mock + 1 test with real LLM
   - 闭环: prompt → MockThinker → FunctionExecutor → Loop → LoopResult
   - **大 commit 是 OK 的, 因为全测通**
2. **v3.0.2 stage gate** (1 commit, docs)

**不**:

- 不再 step-by-step 问 user
- 不做知识图谱
- 不加 `TODO_KNOWLEDGE_GRAPH.md` 的状态
- 不裁决 user 自己的 3 个问题 (per LLM-Wiki 哲学)
