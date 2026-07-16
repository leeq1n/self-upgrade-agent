# Analysis: can parent verification actually skip 3rd-level sub-task details?

> L0: Honest analysis per user 2026-07-14 question
> "commit 的信息, 二级任务全部完成的时候, agent
> 真的能在一级任务汇总的时候, 避开三级任务的总结,
> 只读取二级任务的总结吗?".
> Per P17 老实说 + P25 6-step.
> Last P20-verified: 2026-07-14 (initial)

## Question parsing (per M-intent-parsing)

3 levels of granularity:
- **1st level** = parent task (one batch, e.g. c59)
- **2nd level** = child commits within a batch
  (c50-c58)
- **3rd level** = sub-task details within each
  child commit (e.g., "Sub-task (a) Read first...")

**You ask**: When 1st-level (parent) verification
fires, can the agent **read ONLY 2nd-level (child)
summaries** and **avoid reading 3rd-level
(sub-task) details**?

## Per P17 honest answer

**Short answer**: **NO, the contract is not
technically enforced**.  Parent verification
commits contain the **consolidated summary** (1st
level), but child commit bodies (2nd level + 3rd
level) are still in `git log` history.

**Specifically**:

1. **Parent verification (c59) IS a complete 1st-
   level summary** (8392 chars).  A fresh agent
   reading ONLY c59 gets the consolidated view.

2. **Child commit bodies (c50-c58) are STILL in
   `git log`**.  They contain:
   - 2nd level: short description of each child's
     contribution
   - 3rd level: detailed sub-task decomposition
     (e.g., "Sub-task (a) Read first... (b) Apply
     原则... (c) Write doc... (d) Verify...")

3. **A fresh agent reading `git log` would see ALL
   commits (c50-c59)**.  The parent verification
   (c59) **supersedes** the children conceptually
   (per SUMMARY_LIFECYCLE.md) but does NOT
   **destroy** them in git (per
   SUMMARY_LIFECYCLE.md: "destroy = consumed, no
   longer needed in working set" — the children
   stay in git history).

4. **The technical mechanism for the agent**:
   - `git log --oneline 884dc51..HEAD` = 1-line
     summaries only (L0 view)
   - `git log c50..c58` = full child bodies
     (2nd level + 3rd level)
   - `git log -1 c59` = parent summary only
     (1st level)

**So the agent CAN avoid 3rd level by**:
- Reading c59 alone (`git log -1 c59`)
- OR using `--oneline` for 1st-level view
- OR explicitly skipping child bodies

**But the contract doesn't ENFORCE this**.  A
fresh agent that runs `git log -10` would see all
10 commits with their full bodies.

## Per "新agent 角度" — does the current contract work?

**Test 1**: Fresh agent reads ONLY c59 (parent verify)
- ✅ Gets 1st-level view (consolidated)
- ✅ Time: ~2 minutes
- ❌ Doesn't know what c50-c58 each did in detail

**Test 2**: Fresh agent reads `git log --oneline c50..c58`
- ✅ Gets 2nd-level view (one-line per child)
- ❌ Doesn't know what each child did in detail

**Test 3**: Fresh agent reads `git log c50..c58` (full bodies)
- ✅ Gets 2nd + 3rd level (full child details)
- ❌ Time: ~10-20 minutes
- ⚠️ Defeats purpose of parent summary (1st level)

**Per "新agent 角度"**:
- If agent reads ONLY c59, parent summary works
- If agent reads `git log` (no flags), parent summary
  is **conceptually superseded but technically
  redundant** (agent reads 10× bodies)
- **No technical enforcement** to force agent to
  read parent-only

## Per P11 摘要+引用 + P20 progressive disclosure

**The contract SHOULD work**:
- L0 = commit header (one-line)
- L1 = parent verification body (consolidated 1st
  level)
- L2 = child commit bodies (2nd + 3rd level detail)

A fresh agent should:
- Read L0 first (commit headers, `--oneline`)
- Read L1 if L0 prompts (parent summary)
- Read L2 only if L1 prompts (child bodies)

**The contract says L1 is enough**.  But **the
mechanism is not enforced**.

## Per P22 stuck→plan + P7 奥卡姆 — fix proposal

**Per "1 logical feature per commit" + 你 "如果有
需要调整的内容吗"**:

**Option 1**: Add explicit HEADER marker to parent
verification commits.  E.g., c59's body should
start with:

```
[PARENT VERIFICATION — DO NOT READ CHILD BODIES]
[Children c50-c58 SUPERSEDED; see THIS commit for
1st-level summary]
```

**Pro**: Visible to humans + LLM.  Easy to add.

**Con**: Still not enforced (LLM might still read
children).

**Option 2**: Update SUMMARY_LIFECYCLE.md to specify
**L0/L1/L2 markers** in commit message bodies.  Then
update HOW_TO_READ_GRAPH.md to add the rule:
"When reading git log, use --oneline for 1st-level
view; only read full bodies for specific 2nd-level
detail".

**Pro**: Codifies the contract more explicitly.

**Con**: Doesn't help past commits (c49, c59 already
landed).

**Option 3**: Use **git rebase -i** to **squash
children into parent** (collapse 10 commits into 1).
Then children don't exist in history.

**Pro**: Technically enforces (no children to read).

**Con**: 
- Destructive (rewrites history)
- Per P17: "Stale docs are worse than no docs"
  (squashed commits lose individual attribution)
- Per c59 commit: "fresh agents reading git log
  c59..HEAD~1 see only this parent summary"
  — but if squashed, the 9 child bodies are
  GONE, not just consumed

**Per P7 奥卡姆 + P17 老实说 + R5**: Option 1 is
minimum viable.  Option 2 is documentation-only
(no real change).  Option 3 is destructive
(against P17 audit trail principle).

## Recommendation

**Per "1 logical feature per commit" + P7 + 你
"读原则"**:

**Recommended**: **Option 1 + Option 2 combined**.
- Update SUMMARY_LIFECYCLE.md to specify L0/L1/L2
  marker protocol (Option 2)
- Add a HEADER marker to next parent verification
  commit (Option 1, demonstrated)

**Not recommended**: Option 3 (squash) — too
destructive per P17.


## Per P17 honest reporting

- **c49 + c59 do NOT have explicit L0/L1/L2
  markers**.  The contract was applied
  conceptually, not technically.
- **A new agent without knowing the read pattern
  would see all 10 commit bodies and may NOT
  understand parent supersedes children**.
- **This is a real gap, not a hypothetical**.

## Detail (L2)

For P25 6-step self-application, P26 fresh-agent simulation, P17 honest reporting, fix proposals, and See also, see [`ANALYSIS_PARENT_VERIFY_DETAIL.md`](ANALYSIS_PARENT_VERIFY_DETAIL.md).  Per R6, this companion is required for files > 7KB.
