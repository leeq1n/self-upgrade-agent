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

## Detail (L2)

For per-principle analysis, M-self-application, follow-ups, and other L2 detail, see [`MERGE_EVAL_DETAIL.md`](MERGE_EVAL_DETAIL.md).  Per R6, this companion is required for files > 7KB.
