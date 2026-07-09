---
description: "Full verbatim user quotes (long form reference)"
status: "reference"
---

# USER_INSIGHTS_DETAIL — verbatim quotes

> Read [USER_INSIGHTS.md](USER_INSIGHTS.md) first for the summary.
> This file preserves the verbatim quotes that drove each insight
> in the summary, for audit purposes.

## Goal (paraphrased, see [USER_INSIGHTS §1](USER_INSIGHTS.md))

> A self-upgrade agent that reads papers, filters methods,
> generates code patches, A/B tests them, and only keeps
> improvements.  Has skill/innovation lifecycle.  Stable, robust,
> has harness+loop thinking.  Eventually: the system can
> continuously improve itself.

## Key constraint quote (2026-07-06)

> "做一个能自主升级的 agent, 它可以通过 selenium 等工具每天通过搜索
> 最新的论文, 筛选具体方法和趋势, 尝试将适合的创新点加在这个 agent
> 上, 对比这个功能的效果提升和代价, 最终决定是否留下, 使用类似
> bootloader 的方法切换代码, 也就是说这个模型需要调用大模型改进自己
> 的代码. 它应该有 skill 和新增创新点的生命周期管理, 每隔一段时间,
> 需要进行一次 skill/创新点 的使用频率统计、质量评估与优化/销毁.
> 项目应当有干净的接口、实现代码与文档. 项目应该有稳定性、可靠性、
> 可用性和健壮性. 有 harness 和 loop 的思想."

## Convergence (2026-07-07)

> Convergence = the system keeps getting better over time WITHOUT
> (a) crashing and (b) without bloat.  Not "delta > 5% in one shot",
> but "long-term stable upward trajectory".

## Workflow rules (2026-07-08, chronological)

- "整理-思考-行动 不然混乱的项目导致上下文混乱"
- "简单的单步行动直接动, 上下文长再思考行动"
- "多查资料, 不要一拍脑门"
- "agent 最重要的就是 react 行动链 (输入-思考-输出循环)"
- "来吧, 还是一样的, 遇到问题查查资料, 让我们把项目整理好, 搭建起来"
- "之前的问题是 semanticscholar 的 api 撞墙了, 你为什么没有用 mcp 访问 arxiv 呢?"
- "我希望跑通逻辑, 但是中间不允许跳过任何流程"
- "如果你可以自动调 gc 清日志? 不...我希望日志集中在一起"
- "thor 只有 llm 模型功能...其他所有内容都在本地"
- "PDF 无法被 llm 直接读取, 一般需要 MCP 转换为 markdown"
- "我现在还有用 langgraph? 我感觉 langgraph 在未来会成为更多创新的基础"
- "现在没有 thor, 本地 agent 框架 + 远程 minimax LLM"
- "文档整理 + 切模型也能继续 + 别假阳性 + 别提前截断 + round 20 固定 1 paper"
- "未来工作写下来, 做一条划一条"
- "复杂的应该写成二级、三级 (摘要+引用)"
- "多读几篇论文, 才能知道哪篇值得实现"
- "环境查询 = 记忆查询, 作为 execute 的一个功能"
- "规划属于思考, 查询和更新记忆属于执行"

## Architecture decisions (this session)

- Local agent framework + remote minimax LLM (no more thor/local llama)
- No LangGraph, no multi-agent, no self-refine (paper-supported)
- MCP-everything philosophy (modules as MCP tools)
- Atomic apply (file-level snapshot + os.replace)
- Hard decision (test pass/fail), not LLM-judged

## Failure modes observed (this session)

- LLM timeout misdiagnosed (real issue: env not loaded)
- Key bypass missing (QuotaState blocked with no keys)
- Pre-filter keyword gating (relevant paper → hard-rejected)
- Memory write mutating pipeline state (silent regression)
- Hardcode patterns (vs LLM-as-judge)
- README sprawl (15 → 4 docs this session)
