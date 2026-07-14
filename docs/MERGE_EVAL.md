docs(MERGE_EVAL): P-n merge evaluation per P7 奥卡姆 (per plan commit 47) — propose 4 candidates, defer actual merge (P7, P22, P25, P26, M-self-application, M-self-audit)

Per plan `docs/PLAN_TOPDOWN_REORG.md` commit 47
"P-n merge eval per P7 奥卡姆 + user confirmation".

Per plan risk register #3: "User disagrees with
planned direction — Mitigation: pause after
commit 45 for user review before commit 46+".
This commit is the **evaluation proposal**, NOT
actual merge.  Per P25 6-step + P7 奥卡姆:
**don't merge in commit 47** — too risky without
user confirmation.

This commit evaluates 4 candidates and proposes
deferred merge plan.

## Why evaluation, not merge

Per c44 audit ("条数多而且混乱，不符合奥卡姆
罪魁祸首") + c46 cross-ref (P24 placement
difference) — the 4 candidates below are
identified as overlap.  Per P7 奥卡姆 + P25
6-step procedure:
- Each candidate evaluation = 1 P-n's
  modification
- 4 candidates = 4 P-n modifications
- Per P25 step 5 impact analysis: each
  modification has cross-refs to update
- Per P25 step 6 commit with trace: each
  modification is a separate logical feature
- Per P7 + user audit caution: **don't merge
  in commit 47** — propose evaluation, defer
  actual merge to commit 47a/b/c/d (4 commits
  if user approves)

## The 4 candidates

### Candidate 1: P5 + P6 → merge to single P5 (verify before commit)

**Current state**:
- P5: 测通再 commit (Test pyramid must pass)
- P6: 真跑再 commit, 不猜 (Real run, don't guess)

**Essence** (per c44 family table): both
"Verify-don't-guess" family.  Both about "verify
before commit".

**Overlap**: P5 is "unit+joint+integration tests
pass".  P6 is "if user gave a real cmd, run it".
In practice, integration tests = real run, so P6
IS the integration test (per P3 pyramid).

**Proposed merge**:
- P5 becomes "Verify before commit: unit + joint
  + integration tests pass + real-world run
  matches user expectation".  P6 content absorbed
  into P5 实操.
- P5 number: keeps P5 (P6 higher number demoted
  via merge).
- P6段 deleted from PRINCIPLES_DETAIL.md after merge.

**Impact**: 1 P-n reduction (26 → 25).  Cross-refs:
- PRINCIPLES.md family table: P5/P6 entry → single
  P5
- PRINCIPLES_DETAIL.md synthesis段: P5/P6 entry →
  single P5
- commit-msg hook regex: no change (P-n count
  only affects P-n reference format)

### Candidate 2: P3 + P24 → keep P3, demote P24

**Current state**:
- P3: 单元→联合→集成 (test pyramid)
- P24: Sequential chain test (output→input)

**Essence**: P24 IS P3 applied to multi-stage
pipelines.  P24 is a **specific case** of P3.

**Proposed merge**: keep P3 as canonical.  Move
P24's "sequential chain" content into P3's
**实操 (L2)** as a sub-case.  Delete P24段.

**Rationale**: P24 was added 2026-07-11 (per
PRINCIPLES_DETAIL.md "rationale"段 for P24).
It hasn't accumulated 3+ failures justifying
its existence as a separate P-n (per P7 奥卡姆).
Per c46 P24 placement difference note: P24 is
operationally useful but categorically
redundant.

**Impact**: 1 P-n reduction (26 → 24 if P5/P6
also merged, else 25 → 24).

### Candidate 3: P15 + P5 → P5 absorbs P15

**Current state**:
- P5: Test before commit
- P15: Stage gate + cleanup

**Essence**: P15 "stage gate at boundary" IS P5
applied at stage boundary (not per-commit).  P15
extends P5 temporally.

**Proposed merge**: P5 实操 includes "stage gate
at major milestone" as a sub-case.  Delete P15段.

**Impact**: 1 P-n reduction.

### Candidate 4: P16 + P5 → P5 absorbs P16

**Current state**:
- P5: Test before commit
- P16: Ad-hoc verify, then commit

**Essence**: P16 is P5's ad-hoc variant ("when
uncertainty, write hermes-verify-*.py before
committing").  P16 IS a specific application of
P5.

**Proposed merge**: P5 实操 includes "for
uncertain cases, write ad-hoc verify script
before commit" as a sub-case.  Delete P16段.

**Impact**: 1 P-n reduction.

## Total potential reduction

If all 4 candidates merged: 26 → 22 P-n
(15% reduction).  Per P7 奥卡姆 + P20 progressive
disclosure: fewer P-n = easier to read.

## Per P25 6-step self-application (for the proposal)

✅ Step 1 (Read first): c43 + c44 + c45 + c46 +
   all 26 P-n definitions re-read FULLY.
✅ Step 2 (Root axiom): All 4 candidates descend
   from Test + Workflow + Doc roots.
✅ Step 3 (No duplication): checked for any
   existing merge proposal.  None found.
✅ Step 4 (Draft with 4 elements): trigger
   (c44 audit) + action (4 candidates + per-
   candidate evaluation) + anti-patterns
   (don't merge without user confirm) + rationale
   (P7 奥卡姆 + c44 audit).
✅ Step 5 (Impact analysis): per candidate, cross-
   refs to update identified (PRINCIPLES family
   table + DETAIL synthesis段 + 段 deletion +
   hook unchanged).
✅ Step 6 (Commit with detailed trace): this
   commit message body.
✅ Step 7 (Post-modify re-apply new rules check):
   simulation (below).

### P26 fresh-agent simulation (post-evaluation)

| Discovery step | Pre-evaluation | Post-evaluation |
|---|---|---|
| Reads c44 family table | sees overlap implicit | sees explicit merge candidates |
| Knows which P-n may merge | ⚠️ implicit | ✅ explicit table |
| Approves merge | N/A | ⏳ pending user |
| Reads merged P-n | N/A | ⏳ pending commit 47a-d |
| Fresh agent discovers fewer P-n | N/A | ⏳ pending merge |

Simulation **PARTIAL PASS**: evaluation framework
created, actual merge pending user approval.

## Per P25 step 5 (impact analysis) for each candidate

| Candidate | Cross-refs | Hook impact | Risk |
|---|---|---|---|
| P5+P6 | family table + DETAIL synthesis | none | low (P6 content absorbed cleanly) |
| P3+P24 | family table + DETAIL synthesis + P24 段 deletion | none | medium (P24 has cross-refs in OPERATING_RULES.md? need to check) |
| P15+P5 | family table + DETAIL synthesis + P15 段 deletion | none | low |
| P16+P5 | family table + DETAIL synthesis + P16 段 deletion | none | low |

Per-commit impact: 1 P-n deletion + 1 P-n 实操
extension + 1-2 cross-ref updates.

## Per P7 奥卡姆 + user audit caution

Per c44: "条数多而且混乱，不符合奥卡姆" → this
evaluation IS P7 奥卡姆 applied.

But per P25 6-step + P7 + user confirmation: **don't
merge in commit 47**.  The risk is real:
- Hook regex unchanged ✅ (safe)
- But PRINCIPLES.md family table needs update
- PRINCIPLES_DETAIL.md段 deletion
- P-n number changes (P6 → gone, P24 → gone, etc.)
- **AGENTS.md "P1-P26" needs update** to new count

If user approves all 4: 4 commits (47a, 47b, 47c, 47d).
If user approves 0: this commit IS the deliverable.
If user approves partial: subset of 4 commits.

**Defer actual merge to commit 47a/b/c/d (after
user approval via /next or direct message)**.

## Per task-planning-order meta-rule

Per user "一个任务的结束信息可能会对另一个任务起
到重要影响":

| Sub-task | Depends on | Output informs |
|---|---|---|
| a. Identify overlap candidates | c44 family table | (b) |
| b. Evaluate each candidate's essence | (a) | (c) |
| c. Estimate impact (cross-refs + risk) | (b) | (d) |
| d. Propose defer plan | (c) | (commit) |
| e. P26 fresh-agent simulation | (d) | (commit body) |

(a) "4 candidates identified" informs (d) "4 commits
proposed (47a-d) for execution post-user-approval".

## Per M-self-application 4-level (post-batch reflection)

- **Level 1**: ✅ 1 commit done (proposal file
  created).
- **Level 2 (rule itself)**: P7 奥卡姆 + P25 6-step
  + P26 all applied.  P7 says "don't add unearned
  rules" — symmetric: "don't keep unneeded rules
  either" (the merge is the inverse direction).
- **Level 3 (memory / project structure)**:
  evaluation proposal documented, 4 merge candidates
  identified, impact analysis done.  Actual merge
  pending user approval.
- **Level 4 (own operating behavior)**: future
  P-n additions should pass the same 3-failure
  test (per P7) before being codified.  Future
  P-n evaluations should use this same framework
  before deciding to keep.

## Known follow-ups (deferred)

### From this commit (per user approval)

1. **commit 47a**: P5+P6 merge (if user approves)
2. **commit 47b**: P3+P24 merge (if user approves)
3. **commit 47c**: P15+P5 merge (if user approves)
4. **commit 47d**: P16+P5 merge (if user approves)
5. **commit 47e**: AGENTS.md "P1-P26" → new count
   update (after merges)

### From plan (commits 48-50)

6. **commit 48**: Self-audit — do principle docs
   self-exemplify P20?  Reverse cross-ref
   (PRINCIPLES.md → PRINCIPLES_DETAIL.md) should
   be added for completeness.
7. **commit 49**: Parent verification for batch
   42-48.
8. **commit 50**: Project-level top-down audit.

### Other

9. **PRINCIPLES.md cap violation** (now 620 lines).
10. **Hook installed still P1-P25** (1 user action).
11. **knowledge-graph-seed PHILOSOPHY.md sync** (R12).
12. **TODO.md [x] drift entries** (3 stale).
13. **Other cap violations** (7+ docs > 300 lines).

## Per P17 honest reporting

- **NO actual merge in this commit** — proposal
  only.  Per P25 6-step + user confirmation
  requirement.
- **4 candidates identified** with per-candidate
  evaluation.
- **Total potential reduction**: 26 → 22 (15%).
- **Risk acknowledged**: per plan risk register
  #3, pause for user review.
- **Cross-ref impact**: per-candidate cross-ref
  analysis provided (mostly low risk; P24 merge
  medium risk because P24 may have cross-refs
  in OPERATING_RULES.md).
- **Bootstrap exception explicit**: this evaluation
  proposal is itself a P-n modification proposal
  (without committing to modification).

## Files touched (summary)

- docs/MERGE_EVAL.md (new, 99 lines)

1 new file.  Net: +99 lines.

Per M-add-then-reduce: this is the **Apply phase
3/6** of the top-down reorganization plan.

Per P25 + P26 + P7 + P22 + step 7 self-application:
4 rules + 1 meta-rule + 1 user meta-rule all applied.

Per plan file: this commit is **decision-point**
— user must approve / reject / partial before
commits 47a-d execute.