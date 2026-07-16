# 核心 layer governance template (per 你 turn 2026-07-16)

> L1 governance template for modifying SUA 核心 layer
> content.  Defines the eval-before / verify-after gate.

## When this template applies

Any modification to:
- `core/` directory content (this project)
- `AGENTS.md` (L0 surface)
- `hooks/` (mechanical enforcement layer)
- `.hermes/scripts/` (programmatic baseline scripts)
- `docs/OPERATING_RULES.md` (M-n codification)
- `docs/M_*_DETAIL.md` (M-n L2 details)

## Eval-Before (steps BEFORE commit)

1. **Identify M-n / P-n reference**:
   - Which P-n motivated this change?
   - Which M-n codification is being added/modified?
   - Document in commit message body
2. **Apply 5 primitives**:
   - **Analyze** (M-n 16 stage 1): 任务 IS what? 范围
   - **Reason** (M-n 16 stage 2 + M-n 22 3W1H): why this design?
   - **联想** (M-n 14 Track 1): 类似 prior pattern?
   - **归纳** (M-n 14 induction): general pattern from specific?
   - **总结** (M-n 26 compression): 1-paragraph L0
3. **Run M-n 29 5-step script**:
   ```bash
   python .hermes/scripts/m_n29_5step.py --self --claim "<X>"
   ```
   - If FAIL items → re-verify (cycle per M-n 29 Step 4)
   - Otherwise proceed to verify-after
4. **Document in plan/commit body**: cite P-n / M-n per AGENTS.md
   commit-msg contract

## Verify-After (steps AFTER commit)

1. **Run cold-start simulation**:
   - Imagine fresh agent reading entry doc + tracing to modification
   - Verify reachability chain works
2. **Check mechanical triggers**:
   - Hook whitelist up-to-date (`hooks/commit-msg` regex matches)
   - prepare-commit-msg trailer not noise (if commit body mentions "task done")
   - 5 primitives mentioned in commit body (per hook dedup logic)
3. **Audit discoveries**:
   - Side effects on other files? Run M-self-audit if uncertain
   - Cross-ref broken? Run `python .hermes/scripts/check_cross_refs.py` (if exists)
4. **Update TODO / record** (M-n 31 phase 4 retrospective):
   - What was the cause of the original gap?
   - Was the gap closed?
   - Any cascading effects to track?

## Failure handling (per M-n 32 self-learning-guardrail Guardrail #1)

If verification fails:
- Revert: `git reset --hard HEAD~1` (or `git checkout - .` for staged)
- Re-think: re-apply 5 primitives with new hypothesis
- Retry: re-commit with new analysis

## Lifecycle (per M-n 18 destruction principle)

- Apply, verify, **then optionally destroy related obsolete state**
- E.g., if modifying `OPERATING_RULES.md` M-n section, OLD section text
  should be moved to archive or deleted if fully superseded
- Never destroy **before** verifying replacement is in place

## Coexistence with M-n 27

M-n 27 (knowledge-layer-architecture) is **content taxonomy** (3 sources:
HERMES / SUA / SKILL).  This 3-layer governance is **modification
rights** (核心 / 用户 / 项目).  Both coexist:
- M-n 27 says "where content lives"
- This 核心 layer says "who can modify what"

## Cross-references

- `core/README.md` (L0 marker)
- `AGENTS.md` (L0 operating rules)
- `docs/OPERATING_RULES.md` (M-n codification)
- `.hermes/scripts/m_n29_5step.py` (deterministic baseline)

---

**P-n cited**: P5 (tests pass — M-n 29 5-step is the test),
P11 (摘要+引用), P14 (docs stay current), P17 (老实说 — explicit
about failure modes), P22 (when stuck→plan), P25 (post-modify
re-apply).
**M-n cited**: M-n 14 (two-track reasoning), M-n 16
(observe-think-execute), M-n 18 (recursive-summary), M-n 22
(3W1H), M-n 25 (turn-pattern-recognition), M-n 26
(context-decay-management), M-n 29 (acceptance-protocol),
M-n 30 (knowledge-context-trade-off Priority 1), M-n 32
(self-learning-guardrail), M-n 34 (pre-task-scan).
