> L0: M-n 35 L2 detail — 4 个对抗性思维原语 (质疑/逆向/预演失败/对立论证).
# M-n 35: Critical-thinking primitives (4 adversarial primitives)

> L2 detail.  Companion to `M_ACCEPTANCE_PROTOCOL_DETAIL.md`
> (which defines **5 constructive primitives** = Analyze /
> Reason / 联想 / 归纳 / 总结).  Per user message 2026-07-16
> "思考除了正向思考，也需要批判性思考，你看看项目是不是
> 在这方面有欠缺？如果要加，应该加在哪几个步骤？" — this
> document codifies the 4 critical-thinking primitives that
> complement the existing 5.
>
> Per P22 + M-n 28: planning stage was `hermes-plan-critical-
> thinking-injection-2026-07-16.md` (Temp).  Lifted after
> Phase A commits.

## What is critical thinking (here)

In SUA context: **adversarial reasoning primitives** that
question / challenge / invert / construct-counters to a
proposal — pairing with **constructive reasoning primitives**
(Analyze / Reason / 联想 / 归纳 / 总结).  Per M-n 14
two-track-reasoning: a complete thinking system needs BOTH
constructive + adversarial tracks.

## Why needed

Per user message audit (2026-07-16): SUA has **5 constructive
primitives** but **0 adversarial primitives**.  This is a
**structural gap** in thinking methodology:
- Constructs plans + analyses
- Does NOT adversarially challenge them
- Confirmation bias + over-confidence risk

Per M-n 14: pair **constructive + adversarial** = full
thinking pair.  Per M-n 32 Guardrail #5 (auto-learning):
auto-learning claims must include **critical** perspective,
not just constructive.

## The 4 critical-thinking primitives

### Primitive 1: **质疑** (Challenge)

**What**: Ask "what is uncertain / under-justified / wrong
in this proposal?"

**When**: BEFORE claiming analysis is complete.  Usually
right after Analyze.

**How** (3 sub-steps):
1. List 3 specific weaknesses / uncertainties in current
   proposal
2. Identify which weakness would cause the **highest
   damage** if true (per M-n 22 3W1H "what's the worst case?")
3. State explicitly: "**weakness [X] is most likely true.  We
   proceed acknowledging X may invalidate this**"

**Anti-pattern**: skipping because "we've analyzed it
thoroughly already".  Per M-n 14 Track 1 类比: a thorough
constructive analysis can STILL miss adversarial concerns.

### Primitive 2: **逆向** (Invert)

**What**: Ask "what if the OPPOSITE were true?  What would
that imply?"

**When**: AFTER 质疑 identifies risk.  Especially when
proposal looks "too clean".

**How** (3 sub-steps):
1. State the OPPOSITE of current proposal explicitly
2. List 2-3 reasons the OPPOSITE could be true
3. **State what** would change about your reasoning if
   the OPPOSITE were true (not who wins)

**Per Munger inversion**: "It is remarkable how much long-
term advantage comes from not always trying to get the
things you want.  All I want to know is where I'm going to
die, so I can avoid going there."

**Anti-pattern**: dismissing inversion quickly.  Often
the **best** insights come from inversion that initially
felt silly.

### Primitive 3: **预演失败** (Pre-mortem)

**What**: "Imagine this plan / commit / claim has FAILED.
Why did it fail?"

**When**: BEFORE committing / shipping.  Especially for
high-stakes decisions.

**How** (3 sub-steps):
1. State explicitly: "**this commit FAILED in 30 days**"
2. Write 3-5 specific failure modes + their cause
3. Identify which 1-2 failure modes are **preventable**
   with current available info — fix before commit

**Per Gary Klein pre-mortem (Harvard Business Review 2007)**:
"Before a project is launched, the team imagines that the
project has been launched and has failed.  Then they write
a narrative describing how that failure came about."

**Anti-pattern**: skipping because "this commit is small".
Even small commits compound; pre-mortem is cheap insurance.

### Primitive 4: **对立论证** (Steelman-the-opposite)

**What**: Construct the **strongest** case AGAINST this
proposal.  Not straw man — actual steel-man: most charitable
reading of opposing view.

**When**: AFTER constructive analysis feels "complete" +
mostly positive.  Especially when others might disagree.

**How** (3 sub-steps):
1. State the OPPOSING case most charitably (without putting
   words in mouth)
2. Identify the **strongest 2-3 arguments** for opposing view
3. **Acknowledge which opposing arguments are valid** —
   ones you cannot refute without new evidence

**Per Steelman principle (Wiki/charity)**: assume the
strongest possible version of opposing argument.

**Anti-pattern**: only steel-manning **weak** opposing views
(confirmation bias).  The exercise is meaningless if you
don't steel-man **the strongest**.

## When to apply (4 primitives together)

**Default-on** for:
- High-stakes changes (architecture / cross-project / new
  P-n or M-n lifts)
- Claims that look "too clean"
- Pre-public-ship pre-mortem

**Optional but recommended** for:
- Single-file refactors
- New M-rules codifications

**Skip** for:
- Trivial fixes (typo / formatting)
- Emergency hotfixes (per R2 / 你 directive)

## Integration with 5 constructive primitives

| Constructive (existing) | Critical (new) | Stage |
|---|---|---|
| **Analyze** (M-n 16) | **质疑** (Challenge) | Apply AFTER Analyze |
| **Reason** (M-n 22) | **逆向** (Invert) | Apply AFTER Reason |
| **联想** (M-n 14 类比) | **预演失败** (Pre-mortem) | Apply AFTER 联想 |
| **归纳** (M-n 14 induction) | **对立论证** (Steelman) | Apply AFTER 归纳 |
| **总结** (M-n 26) | (none — summary is final) | Apply LAST (final L0) |

Total: **9 primitives** (5 constructive + 4 critical).
**Per M-n 14 two-track-reasoning**: 9 is enough; not so many
that LLM gets lost.

## Cross-references

- **M_ACCEPTANCE_PROTOCOL_DETAIL.md**: integration point
- **AGENTS.md** "Task-done-notify reminder"段: L0 surface
- **M_PRE_TASK_SCAN_DETAIL.md**: pre-task scan flows into
  these primitives
- **hooks/prepare-commit-msg**: optional trailer check
- **`.hermes/scripts/m_n29_5step.py`**: programmatic apply

## Anti-patterns to avoid

| Anti-pattern | Why bad | Better |
|---|---|---|
| Critical-thinking = "be skeptical" | Negative framing, | Apply 4 primitives formally |
| |  reduces engagement | (named, scripted) |
| Apply all 4 to every task | Adds 4-10 min overhead | Default-on for high-stakes only |
| Skip when analysis is "obvious" | Obvious = bias | Apply at least 质疑 + 预演失败 |
| Critical thinking as "lower bound" | Defensive posture | Critical as **companion** to constructive |
| Critical thinking = "disagree with self" | Cancels work | Critical = **strengthen** by surfacing risk |

## Sources cited (per P14 / P29)

- **Munger inversion principle** (billionaire investor
  Charlie Munger, popularized in Poor Charlie's Almanack)
- **Klein pre-mortem** (Gary Klein, HBR 2007)
- **Steelman principle** (rationalist / Wiki community
  consensus)
- **Confirmation bias** (Daniel Kahneman, Thinking Fast and
  Slow 2011)
- **Red team / blue team** (security industry standard)

## P-n / M-n citations

P5 (tests pass — script pre-commit verify), P11 (摘要+引用
this file), P14 (docs stay current — modify AGENTS.md in
same batch), P17 (老实说 — explicit framework gap report,
not aspirational), P22 (when stuck→plan), P25 (post-modify
re-apply), P29 (recursion — critical thinking = primitive
of self-application).

M-n 14 (two-track reasoning), M-n 16 (observe-think-execute),
M-n 22 (3W1H), M-n 26 (compression), M-n 28 (plan-conditional),
M-n 29 (acceptance-protocol — modify Step 2), M-n 32 (self-
learning-guardrail — Guardrail #5), M-n 34 (pre-task-scan
self-application).
