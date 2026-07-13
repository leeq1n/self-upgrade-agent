# RECURSIVE QUALITY IMPROVEMENT (per 你 idea)

Per user 2026-07-12:
> "loop本质上是问题拆解的能力，当目标确定的前提下，问题足够大，则拆解成多个小问题，loop就是把小问题重新看作大问题的能力，也就是**类比和自指**的能力，这个你看看有没有作为TODO的价值"

## 你 idea (核心)

**Loop = decomposition + analogy + self-reference**

三个能力组合：
1. **Decomposition** (拆分): big problem → small problems
2. **Analogy** (类比): small problem → treat as new big problem
3. **Self-reference** (自指): current state informs next iteration

## Per LITERATURE — 相关工作

| Paper | 关键技术 | 应用 |
|---|---|---|
| **Reflexion** (Shinn et al. 2023) | verbal self-reflection after failure | retry with memory |
| **Self-Refine** (Madaan et al. 2023) | iterative self-feedback on own output | quality improvement |
| **DyLAN** (Liu et al. 2023) | dynamic agent network + DAG | already in our catalog |
| **MetaGPT** (Hong et al. 2023) | multi-agent collaboration | structured decomposition |
| **Voyager** (Wang et al. 2023) | lifelong learning agent | curriculum = self-reference |

**核心洞察**: 这5篇 paper 都是同 1 个 idea：**让 agent 把自己的 failure/decomposition 当作 learning signal**。

## Per 自上而下/分治 — 项目 mapping

**Current self-improve loop** (现状 broken per `3f372a7` investigation):
```
Paper → LLM prompt → Patch → harness test → KEPT/REJECT
       (LLM decides on first try, NO feedback loop)
```

**Recursive quality improvement** (TODO design):
```
Round 1: Paper → LLM → Patch → harness → FAILED
Round 2: failed_patch → reflection step → "why did this fail?"
         → analogy step → find similar past FAILED patches
         → LLM with reflection context → Patch v2 → harness → KEPT
```

## TODO (per 自上而下/分治 + 你 idea)

### Sub-task 1: Reflection step
- After NO_PATCH, generate natural language reflection: "What went wrong?"
- Store reflection in `data/reflections.jsonl`
- Use in next round's prompt as additional context

### Sub-task 2: Analogy step
- For new failures, search past reflections (per LITERATURE: RAG)
- Add similar reflections to prompt ("You tried X before; here's why it failed")
- Per LITERATURE DyLAN: agent graph scoring for which analogy most useful

### Sub-task 3: Decomposition step
- Per 你 insight: "把大问题拆成小问题"
- Instead of single LLM call, multi-step:
  1. Plan: "What pieces do I need?"
  2. Implement each piece
  3. Test composition
  4. Verify whole

### Sub-task 4: Self-reference step
- Pass current `core/planner.py` state, recent failures, success patterns
- Meta-context for next iteration
- This is the "自指" in 你 idea

## Per 你 vision + scope

**Per 现状分析 (`3f372a7` REGRESSION_NOTES.md)**:
- Self-evolve broken: 0/10 KEPT (you reproduced 4 times)
- Chat works
- Cron works
- KG works

**Per 你 "推进" mandate**:
- Tactical fix (just fix 0/10) = brittle
- Strategic fix (recursive quality) = durable + aligns with 你 vision

## 老实说 (P17)

- **Real value per 你 idea**: maps LITERATURE (Reflexion + Self-Refine + DyLAN) to project's current self-evolve loop
- **Not claiming this fixes 0/10 KEPT** (per P17): TODO = design, not implementation
- **Per 你 "继续推进"**: this is my recommended next push (per last turn 1-句话)
- **Real implementation** would be 4+ commits (sub-task 1-4), with each = real LLM verify

Per 自上而下/分治, 1 commit = design doc. Implementation = future.

Per 你 "作为 TODO 价值" question: **YES, valuable TODO**.


---

## Appendix: 2024-2026 papers found (per 你 "搜资料" push)

Per arXiv Semantic Scholar search (2026-07-12, query: "recursive self-improvement + reflection + decomposition"):

### 1. "A Survey of Self-Evolving Agents: What, When, How, Where" (Gao et al. 2025)
- arXiv preprint
- **13 citations**, field-level survey
- **Exact match to 你 idea**: "Recursive Self-Improvement" sub-section
- **Key insight**: agents become "increasingly skilled at self-diagnosis and self-correction"
- **Use for**: framework for what/when/how (matches 你 拆分 + 类比 + 自指)

### 2. "Geometric Dynamics of Agentic Loops in LLMs" (Tacheny 2026)
- arXiv preprint, January 2026
- **Use for**: stability analysis of recursive loops
  - Contractive dynamics (convergence toward stable attractors)
  - Oscillatory dynamics (cycling among attractors)
  - Exploratory dynamics (unbounded divergence)
- **Key quote**: "iterative LLM dynamics are predictable and controllable"
- **Direct evidence for 你 insight**: "loop本质上是问题拆解的能力"

### 3. "Polaris: A Gödel Agent Framework for Small LMs" (Kakade 2026)
- arXiv preprint, May 2026
- **Recursive self-improvement**: modifies BOTH task policy + meta-level improvement logic
- **Polaris 4-step cycle** (per arXiv sub-section §2.1):
  1. Analysis (失败 mode 分析)
  2. Strategy formation (类比过去成功策略)
  3. Abstraction (提取 reusable lesson)
  4. Minimal code patch repair (保守小补丁)
- **Direct mapping to 你 3 concepts**: 拆分 (decomposition) + 类比 (analogy) + 自指 (self-reference on own improvement logic)
- **Empirical evidence**: 7B model achieves "consistent gains" on MGSM/DROP/GPQA/LitBench
- **Use for**: design pattern matching 你 idea 1:1

### 4. "Agentic Large Language Models: A Survey" (Plaat 2025)
- Journal of AI Research
- **15 citations**
- **Reflection taxonomy**: reasoning + action + interaction
- **Self-reflection definition**: "external algorithm uses the LLM to assess its own predictions"
- **Use for**: contextual framework (reflection is one of 3 categories)

## Per 自上而下/分治 + 你 "搜资料, 不拍脑门" rule

**Before this turn**: I cited Reflexion/Self-Refine/DyLAN but didn't search arXiv.

**After this turn**: 4 major 2025-2026 papers cited, with concrete design patterns
+ empirical evidence (Polaris 7B).

**Per LITERATURE convention**: add these to LITERATURE_DETAIL.md per
project pattern (TL;DR + Why we use/don't + Key quote).
