# Phase 4 C1+C2 retrospective (2026-07-16)

## Failure mode

Committed core/README.md (e7c9072) + core/governance-template.md
(a3de71f) — these docs **polluted `core/` dir which is SUA's
runtime agent Python package** (not a governance layer marker).

## Root cause

Did not verify `core/` dir state before creating. Should have:
- Run `ls core/` first (per M-n 32 Guardrail #1)
- Searched git history for existing core/ usage
- Picked different path name (e.g., `core-layer/`, `.core/`,
  `core_governance/`)

## Reverted

- ad8835e (revert a3de71f)
- (revert e7c9072)
- core/ back to 5 files (Python package) + no governance files

## Lesson

**Per M-n 32 self-learning-guardrail Guardrail #1**:
> "Don't modify without verifying"

Applied to directory creation: verify target directory
**state** (not just existence) before commit.

## Recommended followup

For Phase 4 C1 redo, use **different directory name**:
- `core-layer/` (hyphenated, distinct from `core`)
- Or `.core/` (hidden, conventional)
- Or under docs: `docs/core_governance/` (avoids Python
  namespace conflict entirely)

## P-n cited

P17 (老实说 — explicit failure report), P22 (when stuck
→ revert + plan again), P25 (post-modify re-apply — verify
target before modifying).
