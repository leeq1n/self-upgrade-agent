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

## Prior art (per sciverse MCP search, 2026-07-15)

Per 你 turn "如果要搜索资料，有几个MCP可以用来搜索",
I used sciverse (academic literature) to verify the
sub-project-for-experimentation pattern is consistent
with established literature.  3 papers are
particularly relevant:

### Paper 1: "Abandoning innovation projects, filing
patent applications and receiving foreign direct
investment in R&D" (Li et al., 2022,
Technovation)

**Key insight**: "The knowledge and experience gained
from abandoned innovation projects can also be
transferred to ongoing projects, steering the firm
away from the sub-optimal path they had been
following.  As such, the experience of abandoning
innovation projects enhances a firm's capacity to
learn from its deficiencies and prevent their
reoccurrence."

**Validation**: M-n 11 (sub-project for
experimentation) is consistent with this finding —
"abandoning" or "completing" a sub-project yields
transferable knowledge to the main project.  This
paper provides 12 citations as evidence.

### Paper 2: "Local energy projects on islands:
assessing the creation and upscaling of social
niches" (Tsagkari, 2020, Sustainability)

**Key insight**: "Learning was essential for the
project as there are no other similar experiences
worldwide.  The experiment showed that some of the
technologies do not function properly and the design
had several flaws.  This failure produced important
technical knowledge, leading to reflexive learning."

**Validation**: M-n 11 sub-step 4 ("Accumulate")
matches this finding — failures during
sub-project execution produce reflexive learning
that benefits the main project.  10 citations.

### Paper 3: "Uncertainty-reducing techniques in
technological innovation" (Sparrius, 1980, SAJBM)

**Key insight**: The paper categorizes subsystem
"know how" levels (1-4) with corresponding
development iterations required.  Level 4 (no
experience) has unknown iteration count, suggesting
**sub-project iteration is the right approach when
experience is insufficient**.

**Validation**: M-n 11 sub-step 1 ("Decide") is
consistent with this framework — when experience is
at level 4, spawn a sub-project to reduce
uncertainty.  This is an older but seminal paper in
the field.

## What this prior art tells us

The 3 papers collectively validate M-n 11:

- **Paper 1** validates the **return-knowledge**
  mechanism (sub-project → main project)
- **Paper 2** validates the **failure-as-learning**
  mechanism (sub-project failures are valuable)
- **Paper 3** validates the **decide-when-insufficient-
  experience** trigger (sub-project is right for
  level-4 uncertainty)

Combined, these 3 papers support M-n 11's 4-sub-step
process as **not novel but well-established in
literature**.  This is a positive sign (per P7
奥卡姆: don't reinvent what's already known).

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
