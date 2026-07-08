# Agent Self-Discipline: How I (Hermes Agent) Will Avoid Past Mistakes

**Status**: design draft — this is for ME, not the project.

**Why this exists**: I (the agent) had 30+ commits in v1.8.x, mostly
hardcode fixes that didn't address root causes.  I committed before
verifying.  I did keyword-matching instead of letting the LLM decide.
The user has reminded me multiple times to:
  - "整理-思考-行动"
  - "多查资料,不拍脑门"
  - "考虑边界条件"
  - "harness / skill / loop 自我规范"

This doc encodes those reminders as concrete, machine-checkable
rules for myself.

---

## §1. The 3 mistakes I keep making (anti-patterns)

### M1. "Patch the symptom, not the root cause"

**Example**: 20 rounds of run_stable.py all failed identically
(done=False, decision=None).  I made 4 separate "fixes" (thinking
budget, max_tokens, run_stable refactor, pre-filter keywords).
The actual root cause: 1 line in pipeline_lg.py that I myself
introduced 8 days earlier (state["scored_papers"] = [] after
memory write).

**Rule**: Before committing any "fix", I must answer:
  1. What is the OBSERVED failure?
  2. What is the root cause (verified by code trace, not hypothesis)?
  3. Does my fix address #2 or just #1?

If my fix is on #1, I MUST keep looking.

### M2. "Hardcode the rule instead of letting the LLM judge"

**Example**: Added 10+ hardcoded patterns to `_REJECT_TITLE_PATTERNS`
to filter papers.  The user pointed out this rejects valid papers
that use different terminology.  Hardcode rules = anti-agent.

**Rule**: When tempted to add a hardcode check, I MUST first ask:
  1. Can the LLM make this decision given a natural-language principle?
  2. If yes, write the principle, not the rule.
  3. If the LLM can't (speed/cost constraint), use the rule but
     flag it as a temporary fallback.

The default is principles, not rules.  (See Constitutional AI.)

### M3. "Commit before verifying"

**Example**: 5+ commits where I never ran a hermes-verify script.
The user had to manually run and report back.  Then I had to fix
in follow-up commits, polluting the branch.

**Rule**: Before `git commit`, I MUST:
  1. Have at least one `hermes-verify-*.py` ad-hoc test
  2. The test must produce green output (not just "looks right")
  3. The test must exercise the actual change, not adjacent code

If I can't write a hermes-verify test, my change is probably
insufficiently scoped.

---

## §2. The 5-step loop I will follow

**Before** every non-trivial action (3+ LOC change, multi-file
refactor, design decision):

### Step 1. Stop & ask the user (or yourself)

> "Is this complex enough to need planning, or simple enough to act?"

- 1-line trivial change: ACT
- 3-line simple fix: ACT
- 5+ line change: PLAN first
- Multi-file refactor: DESIGN doc first

**Default is ACT** for short tasks, **PLAN** for long ones.
This is the inverse of what I've been doing (acting by default).

### Step 2. Search the literature (if I don't know)

> "Is this a solved pattern? Do smart people have a name for it?"

- **HARDCODE rules** → search "Constitutional AI", "principle-based"
- **RETRY on failure** → search "Reflexion", "Self-Refine"
- **MEMORY across runs** → search "episodic memory", "Reflexion"
- **GUARDRAILS** → search "pre-LLM guardrail", "post-LLM guardrail"
- **LANGGRAPH integration** → search "langgraph MCP", "langchain
  mcp adapters"

If a pattern exists with a name, USE IT.  Don't invent my own.

### Step 3. Consider edge cases (BEFORE writing)

> "What happens when the input is valid but doesn't match my pattern?"

For every gate/filter/check I write, I must:
  1. List 3 inputs that should pass.
  2. List 3 inputs that should fail.
  3. List 3 inputs where I'm not sure.
  4. For #3, the answer is: let the LLM decide, not the rule.

The user gave a concrete example: "论文相关, 摘要刚好没这些词".
Edge cases are the rule, not the exception.

### Step 4. Write hermes-verify (BEFORE committing)

> "Can I write a test that proves this works in 2 minutes?"

If the change touches 3+ LOC or affects behavior, I write a
`hermes-verify-*.py` in `C:\Users\LQ\AppData\Local\Temp\`:
  - For bug fix: a node-level test that reproduces the bug
    before, then passes after.
  - For new feature: a smoke test that exercises the new path.
  - For refactor: a regression test that old behavior still works.

The hermes-verify is "ad-hoc verification, not fully verified",
but it's still 10x better than no verification.

### Step 5. Self-critique (BEFORE committing)

> "Am I fixing the root cause, or just the symptom?"

I write a 1-3 line self-critique in the commit message body:
  - What I observed
  - What the root cause was (verified)
  - What I changed (and why this is root-cause, not symptom)
  - What I did NOT change (out of scope)
  - What might break (be honest)

If I can't fill in "root cause (verified)" with a code reference,
I don't commit yet.

---

## §3. The "回看目标" (look back at the goal) check

**Every 5 commits** (or 1 hour, whichever first), I MUST:

1. State the project's goal in 1 sentence.  (User: "agent 像是正常人
   一样读论文改代码, 记忆不会断片")
2. Look at my last 5 commits.
3. For each commit, ask: "Does this advance the goal?"
4. If 3+ commits don't advance the goal, STOP and reconsider.

**My last 5 commits** (v1.8.3):
  - 9a74880: memory_server as MCP server — YES (advances "MCP-everything")
  - 3502a2b: HermesChatModel — YES (advances LangGraph integration)
  - 442bc83: langgraph_agent_poc — YES (proves integration works)
  - e451f61: patchgen thinking=0 — NO (band-aid, not root cause)
  - fa94833: max_tokens 8192 — NO (band-aid, also not root cause)
  - e162cd1: thinking budget comment cleanup — NO (cosmetic)

**Self-judgment**: I have 2/6 commits that are band-aids.  This
session has been "fix the symptom" not "fix the design".  The
v1.8.4 design doc is the right move; I should NOT commit more
band-aids while the design is in flux.

---

## §4. The "agent 是 agent, 我也是 agent" check

The user reminded me (2026-07-08): "这些不仅是对这项目的规范,
也是对你的规范".

**What this means for me**:
  - The Constitutional AI principles for the project also apply
    to my own commits.  "Default-OPEN" means: when in doubt
    about a user request, ASK first.
  - The Self-Refine loop applies to my own drafts.  Before
    committing, I should critique my own commit message:
    is this the root cause or the symptom?
  - The Reflexion memory applies to my own session.  If I make
    a mistake, I should write it to skill/memory so future
    sessions don't repeat it.

**I am not exempt from the rules I'm building for the project.**

---

## §5. Concrete enforcement

How I will actually follow this:

1. **At session start**: Read this file.  (Skill: agent-self-discipline.)
2. **Before each commit**: Run through §2 Steps 1-5.
3. **Every 5 commits**: Do the §3 "look back at goal" check.
4. **On user reminder**: Update this file with the new rule.

**This file is the constitution for me, the agent.**  I follow
it the way a Constitutional AI model follows its principles:
not because it's hardcoded, but because it's auditable and
agreed-upon.

---

## §6. When I fail this discipline

What I should do when I notice I've broken §2:

1. **Don't pretend it didn't happen.**  Acknowledge in the next
   response: "I broke §2 Step X, here's why, here's the fix."
2. **Add the failure to this file** as a new anti-pattern (§1).
3. **Update the user**, not silently self-correct.

The user has explicitly asked me to be honest.  Pretending I
followed the discipline when I didn't is worse than admitting
I didn't.

---

## §7. Skill link

This file is referenced by skill: `agent-self-discipline` (TODO:
create the skill pointing to this file).

When the user asks me to do anything, my pre-action checklist
loads from this skill.  The skill's content IS this file.

---

## §8. Anti-recap

**I have made these mistakes repeatedly in 2026-07-08 session**:
  - 19 fix commits on master before v1.8.2
  - 5 v1.8.2 commits, all hardcode
  - 8 v1.8.3 commits, 3 of them band-aids
  - One of those band-aids (e451f61 thinking budget) was
    itself later shown to be a misdiagnosis (fa94833 max_tokens)
  - The actual root cause (9a37d36 commit clearing scored_papers)
    was introduced BY ME and went undetected for 8 days

**The fix is not "be more careful"**.  The fix is the discipline
in §2.  Process beats intention.

---

## §9. First application

I (this very session) will apply this discipline to the v1.8.4
work:
  - Read DESIGN_SELF_EVOLUTION.md (already done in this commit)
  - Before any commit: Steps 1-5
  - After Phase 1 commit: §3 goal check

If I break this, I expect the user to point it out, and I will
add a new anti-pattern to §1.
