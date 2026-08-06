> L0: 验收协议 — Verify/Fix/Re-Verify 分离 (M-n 29 实操).  Load when: 验收任务.
# Acceptance Protocol — Verify / Fix / Re-Verify Separation

> **Trigger**: User 2026-07-30 final ask: "验收和修改是不是应该分开？验收只找问题，找完了再集体返修，这样有很多好处".
>
> **Pattern fixed**: Prior turns exhibited "ship → verify → fix → re-verify" within one
> turn, which caused acceptance result drift (M-n 32 Guardrail #1 violation).
> 55% of recent commits were "fix-after-verify" (per audit).
>
> **Decision**: 验收/修改分离 as standard practice. This document
> codifies the protocol for future turns.

## 1. Why separate (per 软件测试 standard practice)

Software testing has well-established phase separation:

| Phase | Purpose | Modifies state? |
|---|---|---|
| **Unit tests** | Test individual components | ❌ no |
| **Integration tests** | Test component interaction | ❌ no |
| **System tests** | Test full system | ❌ no |
| **Acceptance tests** | Verify against requirements | ❌ no |
| **Fix** | Apply patches based on findings | ✅ yes |

**Key principle**: Tests (incl. acceptance) should NOT modify the system under test.
Otherwise test results drift = can't compare across runs.

Per tua-start `AGENTS.md` "Task-done-notify reminder" (M-n 16 stage 1-2):
- 5 primitives must apply BEFORE any commit
- This includes Plan / Search / Lesson / Observe / Cite
- **None of these are "fix and ship"** — they're pre-commit gates

## 2. The 3-phase protocol

```
┌─────────────────────────────────────────────────┐
│ Phase 1: ACCEPTANCE (verify only, NO fix)        │
│   - Run sua-verify-*.py scripts              │
│   - Produce ACCEPTANCE_<DATE>.md with findings  │
│   - DO NOT modify any file in this phase        │
│   - Exit with status: PASS / FAIL / DEFERRED    │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ Phase 2: FIX (apply fixes based on acceptance)   │
│   - Read ACCEPTANCE_<DATE>.md                    │
│   - Plan fixes (pre-judgment per user ask)      │
│   - Apply fixes                                  │
│   - DO NOT re-run acceptance yet                 │
│   - Commit fixes (one or more commits)           │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ Phase 3: RE-VERIFY (acceptance on fixed state)   │
│   - Run sua-verify-*.py AGAIN                 │
│   - Compare results vs Phase 1                   │
│   - If new findings → back to Phase 2            │
│   - If all clean → ACCEPTED, ship tag            │
└─────────────────────────────────────────────────┘
```

## 3. Acceptance location (per user ask: project vs user layer)

| Layer | Purpose | Where |
|---|---|---|
| **核心层** (core) | SUA's permanent contract | agent-tools/scripts/, core-layer/, hooks/ |
| **项目层** (project) | SUA's design + protocol | docs/, AGENTS.md, AGENTS_DETAIL.md |
| **用户层** (user) | Per-user daily work | local file (gitignored) |

**Decision**: Acceptance results live in **用户层** (per-user, ephemeral),
project layer has the **protocol** (this doc).

Rationale:
- Project layer = SUA's design (what SUA is supposed to be)
- User layer = your daily work verification (what state is SUA in *now*)
- Separation per 3-layer policy: project documents don't mix with
  user artifacts.

Practical file naming:
- `docs/ACCEPTANCE_PROTOCOL.md` — this protocol (project layer)
- `~/.config/sua/acceptance/ACCEPTANCE_<DATE>.md` — your state (user layer)

## 4. Acceptance report structure

Each acceptance run produces a report with:

```markdown
# Acceptance Report — <DATE>

## State at acceptance
- HEAD: <git SHA>
- Tag: <vX.Y.Z if tagged>
- Working tree: clean / dirty
- Python version: <ver>
- Platform: <Windows/Mac/Linux>

## Run command
- bash sua-verify-<name>.py
- python -m pytest tests/

## Results
| Check | Result | Detail |
|---|---|---|
| pytest | PASS / FAIL | passed=X/Y |
| cross_repo_audit | PASS / FAIL | total_failures=N |
| self_health_check | PASS / FAIL | failures=[...] |
| ... | ... | ... |

## Findings
1. <finding 1>
2. <finding 2>
...

## Severity
- BLOCKER: must fix before ship
- MAJOR: should fix this turn
- MINOR: can defer to next session
- INFO: documentation only

## Verdict
PASS / FAIL / DEFERRED

## Next action
If FAIL → run Phase 2 (fix), then Phase 3 (re-verify)
If DEFERRED → capture in TODO, continue
```

## 5. Acceptance tools (sua-verify- prefix scripts)

Currently 3 scripts in `agent-tools/scripts/`:
- `self_health_check.py` — string pattern checks
- `cross_repo_audit.py` — sibling pollution check
- `hook_principles_loader.py` — Q2 closure registry

Recommended new tools (per gap analysis):
- `validate_links.py` — markdown cross-reference integrity (22 broken refs found)
- `validate_structure.py` — file structure matches expected layout
- `token_budget.py` — large file detection (> 100KB)

These should be invoked from a single entrypoint:

```bash
bash agent-tools/scripts/run_acceptance.sh
```

This produces the ACCEPTANCE_<DATE>.md report.

## 6. Acceptance as gate (notifier + rejector)

Two modes:

### 6a. Advisory mode (default)

- Run acceptance → produce report
- Decision is human's
- No automatic reject

### 6b. Gate mode (STRICT_EVAL=1)

- Run acceptance → if FAIL, reject commit
- Pre-commit hook: `bash agent-tools/scripts/run_acceptance.sh --gate`
- Set in `.git/hooks/pre-commit`

## 7. Implementation plan

This is **project-layer** change (new doc + protocol), not core-layer
(M-n 15 doesn't apply because adding new doc doesn't change core).

### Files to create
- `docs/ACCEPTANCE_PROTOCOL.md` (this file) — already done
- `agent-tools/scripts/run_acceptance.sh` — single entrypoint
- `agent-tools/scripts/validate_links.py` — link integrity check

### Files to modify
- `hooks/pre-commit` — add acceptance run (gated by STRICT_EVAL)
- `docs/PROJECT_STATE.md` — add acceptance protocol reference
- `AGENTS.md` — add acceptance phase to task-done-notify

### Files NOT to modify (留新 session)
- `core-layer/AGENTS_CORE.md` — core layer change requires M-n 15
- `docs/OPERATING_RULES.md` — 109KB file, split first (separate task)

## 8. Net assessment

Per 预判 (good vs bad):

| Aspect | Good | Bad |
|---|---|---|
| Acceptance / Fix separation | ✅ Stable results | ⚠️ More turns |
| User-layer acceptance | ✅ Project layer clean | ⚠️ Need new dir |
| New validate_links.py | ✅ Prevent link drift | ⚠️ Maintenance burden |
| 3-phase protocol | ✅ Software test standard | ⚠️ Adoption cost |

**Net verdict**: Adoption is worth it. Reduces verify-then-fix churn,
makes acceptance results comparable across versions.

## 9. References

- tua-start `AGENTS.md` "Task-done-notify reminder" (5 primitives)
- tua-start `AGENTS.md` "Iterative thinking" (Apply / Observe / Re-think)
- tua-start `AGENTS.md` "Recursive test-verify" (TDD pattern)
- M-n 32 Guardrail #1 (real verify before claim)
- M-n 36 pre-release audit (no github commit confusion)
- R137 wordy-trap defense (avoid "全部好了" claim)
- P-7 Occam (smallest effective change)
- P-14 self-contained mandate (no internal refs in user-facing docs)
- P-17 no fabricate (honest value assessment)
- Industry: 软件测试 V-model (Verification & Validation phases)
- Industry: Test-driven development (test first, code until pass)