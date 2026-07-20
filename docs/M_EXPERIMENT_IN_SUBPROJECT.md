# M-experiment-in-subproject (full text)
Last P20-verified: 2026-07-15

> L0: L2 detail for `OPERATING_RULES.md` § M-experiment-
> in-subproject段.  Per P11 摘要+引用 + R6, this
> companion is required when the summary rule段 is
> detailed enough to warrant L2 expansion.  Load when:
> planning to spawn a sub-project, evaluating whether
> to return from a sub-project, or debugging "sub-
> project became a permanent drift".

## Why this M-rule exists

Per user meta-rule 2026-07-15: "如果当前经验不足以
支撑项目，可以考虑新建一个子项目用来做实验积累失败
经验" + "经验积累完成，知道怎么处理后再切回主项目".

This M-rule operationalizes that meta-rule into a
4-sub-step process.  This L2 doc provides worked
examples, return criteria, and decision support.

## The 4 sub-steps (detailed)

### Sub-step 1: Decide

Evaluate whether the sub-task warrants a sub-project.

**Decision criteria** (apply all 4):

- **Lack of experience**: does the main project
  have 3+ prior failed attempts to handle this kind
  of task?  (If yes, experience is sufficient; don't
  spawn.)  (If no, lack of experience confirmed;
  spawn.)
- **Sub-task complexity**: is the sub-task
  independent enough to be isolated?  (If tightly
  coupled to main project, don't spawn — handle in-
  place.)  (If independent, spawn.)
- **Expected duration**: is the sub-task expected to
  take 5+ commits?  (If < 5, handle in main project;
  too small to justify separate project.)  (If ≥ 5,
  spawn.)
- **Return criterion**: can you write a specific
  condition under which you'll return to the main
  project?  (If no, don't spawn — return criterion
  is the anti-drift mechanism.)

**Decision rule**: 3+ ✅ → spawn.  < 3 ✅ → handle in
main project.

### Sub-step 2: Spawn

Create the sub-project as a sibling per P21 (separate
git repo in `hermes-root/`, not a subdir of the main
project).

**Spawn checklist**:

- [ ] Create the directory: `hermes-root/<project>-
  <subproject>/`
- [ ] `git init` in the new directory (per P21
  cross-project independence)
- [ ] Initialize with minimal skeleton:
  - `README.md` (L0 + project intent + relationship
    to main project)
  - `HANDOFF.md` (onboarding for new agents; minimal
    is OK)
  - 1 core doc (the sub-project's purpose, similar
    to skill-incubator's `SKILL_DESIGN.md`)
- [ ] **CRITICAL**: in the main project, write a
  "Sub-project created" commit that references the
  sub-project's location, goal, and return criterion
  (per P14 docs stay current + P22 case-3 boundary
  for cross-project visibility)

### Sub-step 3: Set goal + return criterion

This is the **anti-trap** sub-step.  Without an
explicit return criterion, the sub-project can become
a permanent drift.

**Return criterion template**:

```
I will return to the main project when [specific
observable condition], e.g.:

- "I have committed 1 case study of a 3-condition
  decision matrix (per SKILL_DESIGN.md 4 sub-knowledge
  areas)"
- "I have a working `docs/framework/<topic>.md` that
  passes 7-check (per P20) and is R5-compliant"
- "I have validated the pattern across 3+ projects
  (per M_RULE_AUTHORING 3-condition gate)"
- "I have answered the question '<what was the gap
  in main project experience>' with a 1-paragraph
  explanation"
```

The criterion must be **observable** (you can check
it from a single command, e.g., `git log --grep
"case study"` returning N≥3 results).

### Sub-step 4: Accumulate + return

In the sub-project, follow the normal commit
conventions:

- **For P-n / M-n**: minimal version of SUA's P-n
  (e.g., P22 stuck→plan, P14 docs stay current) is
  enough.  Don't import the full 25 P-n + 11 M-n
  system.
- **For commits**: 1 logical feature per commit,
  hook enforces P-n cite (or, if sub-project has
  no P-n, plain messages).
- **For parent verification**: when return criterion
  is met, write a parent verification commit in
  the sub-project, then return to the main project.

**Return process**:

1. In the sub-project, write a parent verification
   commit (e.g., `docs: parent verify for [topic]`
   with a list of accumulated commits).
2. In the **main project**, write a "Sub-project
   completed" commit that:
   - References the sub-project's parent verify
     commit hash
   - Summarizes the sub-project's findings
   - Codifies the findings into the main project's
     docs (per M-add-then-reduce: add then reduce)
3. Resume the main project's queue.


## When NOT to invoke (anti-patterns)

- **Don't** spawn a sub-project without a clear goal
  (per user meta-rule "可能陷进子任务，需要设定好
  目标").
- **Don't** spawn a sub-project as a subdir of the
  main project (per P21 cross-project independence).
- **Don't** lose the connection to the main project
  (always write a "Sub-project created" commit in
  the main project).
- **Don't** forget to return (the return criterion
  is the safety net).
- **Don't** over-spawn (each sub-project adds
  cognitive overhead; 1-2 active sub-projects at a
  time is the practical max).


## Cross-references

- `OPERATING_RULES.md` § M-experiment-in-subproject —
  the L0/L1段 (in SUA)
- `docs/HANDOFF_DETAIL.md` "Sub-project-for-
  experimentation pattern" 段 (c89-small) —
  recording of the pattern
- `docs/SKILL_DESIGN.md` — analogous
  pattern (5-phase process)
  — first worked case

## Detail (L2)

For 'Worked examples' (2 examples) and 'Relationship to other M-rules + P-n' (detailed), see [`M_EXPERIMENT_IN_SUBPROJECT_DETAIL.md`](M_EXPERIMENT_IN_SUBPROJECT_DETAIL.md).  Per R6, this companion is required when the summary exceeds 7 KB.
