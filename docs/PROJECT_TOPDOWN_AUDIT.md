# Project-level top-down audit (per plan commit 50)

> L0: Top-down audit of the entire project, not just
> principle docs.  Applies 类比 + 自顶向下 + P20
> progressive disclosure framework (from c44 + c46)
> to all 30+ docs in `docs/`.
> Last P20-verified: 2026-07-14

## What this audit checks

Per plan `docs/PLAN_TOPDOWN_REORG.md` commit 50:
"Apply 类比 + 自顶向下 to whole project, not just
principle docs".

Concretely, for **every doc** in `docs/` (and
AGENTS.md / TODO.md / DONE.md at project root):

1. **L0 line at top** (per P20 + R9): single-line
   summary, ≤ 120 chars
2. **L1 summary段** (per P20): 1-3 paragraphs,
   "what is this in 30 seconds"
3. **L2 detail段** (per P20): full content
4. **Last P20-verified** (per R10): at end of doc
5. **Cap compliance** (per R5/R8): ≤ 7KB summary,
   > 7KB has _DETAIL companion (≤ 300 lines summary)
6. **Cross-refs** (per P11 摘要+引用 + P13 no orphan):
   parent doc + sibling docs reachable
7. **Class** (类比 framework): is this doc an
   L0/L1/L2 layer in the project's 4 axiom families?


## Findings (sorted by severity)

### Critical (severity 3 — structural issues)

1. **DONE.md missing L0 line** — the largest doc
   in the project (57 KB) but no L0 header.  R9
   violation.  **Action**: add L0 line in
   commit 50a.

2. **OBSERVATIONS.md / OBSERVATIONS_DETAIL.md**:
   OBSERVATIONS.md is 71 KB.  Per R5: > 7KB
   needs _DETAIL companion.  Already split (c38).
   But OBSERVATIONS_DETAIL.md is itself 73 KB
   (1882 lines).  Per R5: would need
   OBSERVATIONS_DETAIL_DETAIL.md?  **Action**:
   evaluate if nested _DETAIL is needed (likely
   yes, given size).

3. **DONE.md size (57 KB)** — too large for
   R5 ≤ 7KB summary.  Per R5, needs _DETAIL
   companion.  **Action**: create DONE_DETAIL.md
   in commit 50b.

### High (severity 2 — L0/L1 quality)

4. **PRINCIPLES.md L1段 partial** (already noted
   in c48 self-audit, finding 7): L1 doesn't say
   "when to load this vs PRINCIPLES_DETAIL.md".
   **Action**: rewrite L1段 in commit 50c.

5. **PRINCIPLES.md 621 lines** (300+ cap violation,
   accelerated by c44 + c48).  **Action**: split
   to PRINCIPLES_DETAIL companion in commit 50d.

6. **OPERATING_RULES.md 318 lines** (300+ cap).
   Has _DETAIL companion already.  **Action**:
   evaluate if split needed in commit 50d.

### Medium (severity 1 — minor)

7. **EXTENSIONS.md 1727 bytes (R4 fail)** —
   previously identified in c38 audit, deferred
   due to R4/R6 conflict.  **Action**: resolve
   R4/R6 conflict in commit 50e (per P25 6-step).

8. **PRINCIPLES_DETAIL.md 394 lines** (slightly
   over 300 cap).  Has P1-P26 sections.  **Action**:
   evaluate split.

9. **CONSTRAINTS_DETAIL.md 317 lines** (slightly
   over 300 cap).  **Action**: evaluate split.

10. **LITERATURE_DETAIL.md 349 lines** (slightly
    over 300 cap).  **Action**: evaluate split.

11. **MERGE_EVAL.md 293 lines** (close to cap,
    new in c47).  **Action**: monitor after
    merges (47a-d).

12. **SELF_AUDIT_P20.md 203 lines** (new in c48).
    **Action**: monitor.

13. **TODO_SESSION_PERSISTENCE.md 174 lines**
    (close to cap).  **Action**: monitor.

14. **TODO_KNOWLEDGE_LIFECYCLE.md 160 lines**
    (close to cap).  **Action**: monitor.

### Low (severity 0 — not addressed now)

15. **Several docs without L1 clarity** — minor
    can be improved but not blocking.

## Per task-planning-order meta-rule

Per user "一个任务的结束信息可能会对另一个任务起
到重要影响":

| Sub-task | Depends on | Output informs |
|---|---|---|
| a. List all docs | (none) | (b) |
| b. Audit each doc for 7 checks | (a) | (c) |
| c. Group by severity | (b) | (d) |
| d. Propose 50a-50e plan | (c) | (commit body) |
| e. P26 fresh-agent simulation | (d) | (commit body) |

(d) per-severity findings inform 50a-50e plan.







## Known follow-ups (per this audit)

### Critical (50a-50b)

1. **DONE.md L0 add** (R9 violation)
2. **DONE.md → DONE_DETAIL split** (R5 violation)

### High (50c-50d)

3. **PRINCIPLES.md L1 rewrite**
4. **PRINCIPLES.md + OPERATING_RULES.md cap splits**

### Medium (50e)

5. **EXTENSIONS.md R4/R6 conflict resolution**
   (R-n modification, user-confirmation required)

### Pending user approval

6. **commits 47a-d**: P-n merge
7. **commit 47e**: AGENTS.md P-n count update

### Self-audit deferred (c48)

8. **PRINCIPLES_DETAIL.md L0 enrichment**

## Per P17 honest reporting

- **14 findings identified** across 30+ docs.
- **3 critical** structural issues (DONE.md L0 +
  DONE split + OBSERVATIONS nested _DETAIL).
- **3 high** L0/L1 quality issues.
- **5 medium** minor issues.
- **3 low** not addressed.
- **5 fixes proposed** (50a-50e) but **NOT
  executed** in this commit (audit only).
- **Per "1 个 1 个来" + P7 奥卡姆**: 1 commit =
  1 logical feature.  Audit + fixes = 5+ commits.
- **Per plan file + plan risk register #3**: pause
  for user review before any 50a-50e execution.



## Detail (L2)

For the per-tier inventory tables, per-severity findings, 5-family framework, P26 simulation, P25 6-step, M-self-application 4-level, 50a-50e plan, and Risk register, see [`PROJECT_TOPDOWN_AUDIT_DETAIL.md`](PROJECT_TOPDOWN_AUDIT_DETAIL.md).  Per R6, this companion is required for files > 7KB.

## See also

- `docs/PLAN_TOPDOWN_REORG.md` (overall plan)
- `docs/SELF_AUDIT_P20.md` (c48 self-audit, principle
  docs only)
- `docs/MERGE_EVAL.md` (c47, P-n merge candidates)
- `docs/PRINCIPLES.md` 类比联想段 (5-family framework)