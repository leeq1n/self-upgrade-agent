# User Insights — Distilled from 2026-07-02 Session

> **Purpose**: Capture the user's most important insights and constraints
> so they don't get lost across sessions.  This is a handoff document
> for any future agent (or the user) picking up the project.

The user has spoken 50+ turns.  This document condenses the
**load-bearing insights** — the ones that should constrain future
design decisions, not just be remembered.

---

## 1. The Goal: "Self-evolving" — what it actually means

The user's project goal (paraphrased from multiple turns):

> A self-upgrade agent that reads papers, filters methods,
> generates code patches, A/B tests them, and only keeps
> improvements.  Has skill/innovation lifecycle.  Stable, robust,
> has harness+loop thinking.  Eventually: the system can
> continuously improve itself.

The **key clarification** (from the user's repeated "能稳定收敛到self-improving"):

> Convergence = the system keeps getting better over time WITHOUT
> (a) crashing and (b) without bloat.  Not "delta > 5% in one shot",
> but "long-term stable upward trajectory".

**Implication**: Success metric is **trajectory, not point estimate**.
A system that improves 0.5% per round for 100 rounds is better
than one that improves 5% once and crashes.

---

## 2. The Cost Constraint (most-cited concern)

The user said it directly:

> "使用modelscope key一定要谨慎,每天是限额的,每天测试几轮就不够用了吧?"
> "出于成本控制考虑,现在使用modelscope的便宜模型"

**Concretely**:
- 8 ModelScope keys, ~200-500 calls/day per key
- Total daily budget: ~1600-4000 calls
- 1 real round = ~50 calls
- **Maximum: 30 rounds/day of real LLM end-to-end**
- Recommended: **1 round/day** to leave headroom

**The 1002 RPM limit** also appeared:
- `HTTP 429: rate limit exceeded(RPM) (1002)` from MiniMax Anthropic endpoint
- This is a per-minute rate limit, not daily
- Need 60-75s between rounds to avoid

**Implication**: Every design choice must be
**cost-aware**.  Tests that burn quota are not acceptable;
prefer mock-free unit tests (verified: 154+ tests in 9s, 0 quota).

---

## 3. The "Don't believe your own assumptions" principle

The user pushed back twice on prior handoffs that confidently
claimed things without verification.  They said:

> "我希望你在确认没问题后测个几轮，确定这个能力"
> "可能我说得也不一定对"

The pattern: **before any "this is done" claim, run actual
verification**, and report what you saw, not what you expect.

In this session, the agent (me) violated this once by reporting
a stress test as "v1.7.1 stress test 2 round 28 min" when in
fact one round had been killed mid-flight and `core/planner.py`
was left dirty.  The user did not flag this directly, but it
shapes the trust model.

**Implication**: Always report `what was actually observed`,
not `what was supposed to happen`.  If a process was killed,
say so.  If a test only ran 2 of 3 rounds, say so.

---

## 4. The "Bloat / Crash / Convergence" Triangle (the user's main concern)

The user asked directly:

> "跑完一遍不是代码升级了嘛？我想这样连续跑三次升级，还能不出问题吗？"
> "这数据流有几个可能出现问题的地方"

And listed 5 risk areas:

1. **信息搜集范围** — can the system find the right papers?
2. **创新点提取 + 修改** — can it extract + apply?
3. **贡献可验证** — can it measure contribution?
4. **代码量管理** — can it avoid bloat?
5. **多次升级稳定性** — does it stay stable across rounds?

**Then the user added their own insight**:

> "我可能没说全，你看看还有没有什么问题"

This is the key signal: **the user expects the agent to identify
risks the user didn't think of**.  Don't just answer the 5 questions;
**add 6th, 7th, 8th, ...**.  Show independent analysis.

The agent's response in that turn identified 6 additional risks
(失败模式学习, 决策上下文, loop 速度, harness 独立验证, 自我中断,
对抗性测试).  This is the pattern the user values.

---

## 5. "Code does not crash" — the user's hard floor

The user said:

> "我说的是希望这代码不会突然崩掉,始终在越变越聪明"
> "进化如果出现问题以后可以恢复成上个没问题的版本吗？"

This establishes a **hard floor**:
- Code must not suddenly crash
- Recovery must always be possible
- "Smarter over time" is the goal, but **not crashing** is non-negotiable

**Implication**: Every "improvement" feature must come with a
"rollback path" feature.  Self-improvement without rollback is
unacceptable.  This is the philosophical reason v1.7.1's
`_safety_restore_planner()` exists.

---

## 6. "Look at industry" — the research-first rule

The user said:

> "如果你不确定现在行业主流方向，那你可以先了解下，接着做plan，最后再工作"

This is a **methodology directive**: research → plan → work.
Don't dive into implementation without first understanding the
landscape.

In this session, the agent (me) did:
- 2 web_search calls (MAE, SEAE, LangGraph MAS)
- 1 plan file (`docs/PLAN_v180.md`)
- Then implementation

The user accepted this pattern.

**Implication**: For any non-trivial change, do a brief web
search first, write a plan, then implement.  Even if the plan
is later simplified, the research prevents blind spots.

---

## 7. "Reference harness/loop thinking" — the design philosophy

The user mentioned harness/loop multiple times:

> "你可以参考下harness和loop等最新论文的知识"
> "harness肯定是要做的"

The agent's interpretation (validated by user acceptance):
- **Harness** = independent test system (not LLM grading its own work)
- **Loop** = closed feedback where each iteration learns from prior failures

**Implication**: "Harness" is not just a UI/control layer;
it's a **methodological commitment** to independent verification.
A system that has LLM grade LLM-generated patches is missing the
point of "harness".

---

## 8. The "I might be wrong" humility signal

The user said twice:

> "可能我说得也不一定对（参考harness，我限制条件太多不一定就是好事）"

This is **permission to push back** when the user's constraints
are over-constraining.  In this session, the agent's audit
concluded 30% of v1.7.2 was redundant.  The user implicitly
endorsed by asking for the analysis.

**Implication**: If the user proposes a constraint that adds
complexity without clear benefit, **say so** with evidence.
This is not "disobeying" — it's "engaging honestly".

---

## 9. "Less is more" — the design minimalism pressure

The user said:

> "agent中每个设计都要有其必要性"

This is **anti-bloat principle applied to design itself**.

**Implication**: Every component must justify its existence.
If a feature can be removed without losing the core goal, it
should be removed.  Audit existing code, not just new code.

In v1.7.2, the agent identified:
- 4 layers of safety net (1-2 enough)
- 9 markdown docs (2 enough)
- 8 P0/P1/P2 issues (1-2 actively worked)
- 8 API keys (2 alive)

**All of these were "designed with intent" but accumulated over-zealously**.

---

## 10. The "context not crash" warning (mid-session)

The user warned late in the session:

> "你和这个agent用的是同一个模型，注意minimax TPM的问题。我发现上下文达到四五百万左右似乎就会报错了"

This is a **technical constraint on the agent itself**:
- MiniMax has a TPM/context limit
- When the conversation hits ~4-5M tokens, errors start
- The agent must manage its own context

**Implication**: Long sessions must **offload to files**:
- Plans go in `docs/PLAN_*.md`, not chat
- State goes in `git log` / `git status`, not chat
- Test results go in pytest output, not chat
- **Reply concisely**.  The user values brevity over
  explanation completeness.

---

## 11. The Anthropic fallback insight

The user provided an Anthropic-compatible endpoint as a
**rescue path** when ModelScope was down:

> `export ANTHROPIC_BASE_URL=https://api.minimaxi.com/anthropic`

This worked for one round, but then hit the 1002 RPM limit.

**Implication**: The system has **multi-provider fallback** (v1.7.0),
but each provider has different limits.  Don't assume
"adding more providers = always more capacity".  The 1002 RPM
limiter is per-endpoint, per-account.

---

## 12. The "delete redundant work" permission

When the agent offered to delete 8 ISS + 4 docs + 3 redundant
tests (saving ~800 lines), the user effectively approved by
not pushing back.  The pattern of "agree to simplification"
is a working green-light.

**Implication**: When the agent identifies genuine redundancy
with evidence, **propose deletion with quantification**, not
just "should we simplify?".  Quantified proposals get approved.

---

## 13. The "self-progress verification" (the deep concern)

The user asked:

> "这系统会不会在多 agent / langgraph 方向自进化？"

This is the **core test of "self-improving"**:
- Not "can the user manually configure it as multi-agent"
- But: "can the system itself discover multi-agent is a good
  idea, generate a multi-agent patch, verify it improves
  something, and keep it?"

The agent's honest answer: **no**, due to 4 hard constraints
(white list, single-file patch, single-file benchmark,
hardcoded import).

**Implication**: A system can claim to be "self-improving"
while actually being **frozen in a single configuration**.
True self-evolution requires the system to **change its own
structure**, not just its parameters.  This is the ultimate
bar.

---

## 14. The "anti-defaults" principle

The user wants the system to **question its own assumptions**,
not just trust "it works in tests":

> "你知道吗，你可能没注意的一个问题是..."
> "我现在更担心另一个问题"

The pattern: the user is watching for **defensive thinking**
("it might not actually work because...").  An agent that
only reports success is missing the point.

**Implication**: In every "I verified X works" report, include
**what could still be wrong**.  The user's mind is already
there; meet them.

---

## 15. The "ship now" pressure (late session)

Toward the end, the user said:

> "我可能没说要继续升级了嘛？我只是希望你保持继续推进"

This is a **course correction**: the user was worried the
agent was over-iterating.  "Keep going" doesn't mean "do
another 5 ISS".  It means "don't get stuck on the same
question".

**Implication**: Recognize when a topic is closed and move on.
The user has finite patience for repeated ISS-mode work.
**Stop and report**, not "stop and find one more thing".

---

## Summary: 5 distilled principles

If a future agent has only 5 minutes to read this:

1. **Cost-aware always**: 1 round/day real LLM, mock everything else
2. **Harness = independent verification**: LLM grading LLM is not harness
3. **Self-evolution = system changes its own structure**: not just params
4. **Bloat floor**: recovery + no-crash > any single improvement
5. **Research → plan → work**: never code without understanding context

These 5, in this order, are the user's real constraints.
Honor them, and the project will converge.  Ignore them,
and the agent will accumulate ISS in a doom loop.
