# M-experiment-in-subproject — Detail (L2)

> L0: L2 detail for `M_EXPERIMENT_IN_SUBPROJECT.md`.  Per
> P11 摘要+引用, the summary file is the L0/L1 layer
> (≤ 7KB); this file is the L2 layer (worked examples +
> M-rule relationships detail).  Per R6, this companion
> is referenced from the summary.

---

## Worked examples

### Example 1: skill-incubator (per c88 + f8404c5)

- **Decide**: 4 ✅ (experience was implicit in SUA
  SKILL_GENERATION.md, sub-task was skill design,
  expected 5+ commits, return criterion = "first
  skill is incubated")
- **Spawn**: `hermes-root/skill-incubator/` with
  README + HANDOFF + SKILL_DESIGN
- **Return criterion**: "first skill is incubated
  (per SKILL_DESIGN.md 5-phase process)"
- **Return**: skill-incubator is now permanent sibling
  (per P21); c86 + c87 + e19189b + dfaabe0 + 67ab0ab
  are the "Sub-project completed" commits in SUA +
  skill

Note: this is an interesting case where the "return"
became "promote to permanent sibling" — this is
permitted if the sub-project is genuinely independent
and useful as a sibling.  If unsure, treat as
sub-project (with return criterion) first, then
evaluate promotion after the criterion is met.

### Example 2: Not yet observed in SUA

A hypothetical case: SUA wants to investigate "should
we lift P28 to P28 (not candidate)?" but lacks
empirical evidence (need 2+ more recursion demos).

- **Decide**: 4 ✅ (lack of experience + independent
  + 5+ commits + return criterion "I have 2+ SUA
  recursion demos")
- **Spawn**: `hermes-root/recursion-investigation/`
- **Return criterion**: "I have 2+ SUA commits that
  demonstrate recursion in practice (each commit's
  message cites 'recursion' as a feature, not just
  a reference)"
- **Return**: parent verify in
  `recursion-investigation/`, then "Sub-project
  completed" commit in SUA codifying the evidence

This is a **template for future use**, not a real
case yet.


## Relationship to other M-rules + P-n

- **M-self-audit**: applies after sub-project cycle
  ends (verify the main project wasn't broken by
  the detour)
- **M-task-summary**: when returning, write a parent
  task summary that records the sub-project's
  findings
- **M-add-then-reduce**: sub-project findings should
  be *added* to the main project's docs, then
  *reduced* (per skill-incubator's 信息拓扑 方案 C
  principle)
- **M-skill-synchronize**: if sub-project is for
  skill design, M-skill-synchronize's 4 sub-steps
  apply
- **P21** (cross-project): the sub-project is a
  sibling; P21 applies
- **P22** (stuck→plan): this M-rule is one possible
  outcome of stuck→plan
- **P27** (project self-org): sub-project is a form
  of self-organization when the project recognizes
  its own experience limits
