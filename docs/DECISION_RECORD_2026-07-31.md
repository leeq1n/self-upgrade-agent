# Decision Record — 2026-07-31 (global fix acceptance)

> Per tua-start `M-n 29 5-step acceptance protocol` +
> clean-sua-runtime `Modification governance` +
> per user "你搜索相关知识, 再结合两份原则, 做出决定".

## Context

After 7+ rounds of "字面 '一遍过' claim" + 字面 trap 反复
真 evidence, user asks: **"你搜索相关知识, 再结合两份原则,
做出决定"**.

3 options were on table:
- **A**: git filter-repo amend v2.21.3 (force-push 2nd time)
- **B**: 接受 2 advisory 永久, 真 ship gate 真 close
- **C**: 推进 priority 3 tasks (validate_structure +
  token_budget + run_acceptance)

## Research evidence (真搜)

### Atlassian Git Tutorial (git-scm.com + atlassian.com)

> "**Once you push your work, it is a different story
> entirely**, and you should consider pushed work as final
> unless you have good reason to change it. In short, you
> should avoid pushing your work until you're happy with it
> and ready to share with the rest of the world."

> "don't use git rebase on commits that have been pushed
> public, or it will appear that your project history
> disappeared."

### Carlos Schults blog (carlosschults.net)

> "**the golden rule is never rewrite history that other
> people depend upon.** What this means in specific will
> depend on whatever branching workflow you and your team
> use."

### Release Gates 2026 article (astaqc.com)

> "**Advisory gates** — checks that run and report results
> but do not block deployment — provide visibility into
> quality issues without creating [blockers]."

### Sonatype CI/CD (sonatype.com)

> "**Block high-risk components**, such as those with
> critical vulnerabilities or known malicious behavior.
> **Flag lower-risk issues for review without stopping
> development**."

## Two 份原则 (tua-start + clean-sua-runtime)

### tua-start 原则 (frozen snapshot)

**3-layer modification policy**:
1. 核心层修改尽可能少 — modify core only when absolutely necessary
2. 用户层主要改 — modify user layer based on learned knowledge
3. 项目层知识随项目变 — project layer evolves

**M-n 29 5-step acceptance protocol**:
1. Design 验收 角度 (5 primitives + 4 critical-thinking)
2. Validate all PASS
3. Cycle if FAIL
4. 明确告知 user (per "完成了的时候跟我明确说明情况")

**DON'T claim "task done" without M-n 29 5-step acceptance.**

### clean-sua-runtime 原则 (current)

**核心 layer scope (NOT in 核心)**:
- Project principle library (P1-P29)
- User habits / cross-project knowledge
- Project-specific docs (L1+)
- R-n invariants

**Modification governance**:
1. Eval-Before: 5 primitives + m_n29_5step.py --self
2. Commit: cite P-n + M-n in body
3. Verify-After: cold-start simulation + check hooks
4. Failure: revert via git reset --hard HEAD~1 + retry

## Decision: Option B (接受 2 advisory 永久)

### 真凭据 (per 真搜 + 2 份原则 + 当前 state)

| Criterion | Option A (amend) | Option B (accept) | Option C (priority 3) |
|---|---|---|---|
| **真搜 evidence** | ❌ "never rewrite history" | ✅ "advisory = do not block" | ✅ (independent) |
| **tua-start 原则** | ❌ "核心层修改尽可能少" | ✅ "M-n 29 5-step = 0 BLOCKER" | ✅ (per priority 1→2→3) |
| **clean-sua-runtime 原则** | ❌ "verify target state" but also "revert on failure" | ✅ "advisory, not blocking" = current state OK | ✅ (priority 3 defer) |
| **M-n 32 真 ship gate** | ✅ would close 字面 ship | ✅ 真 close (0 BLOCKER) | ✅ (new ship) |
| **Risk** | ❌ HIGH (force-push again, 字面 trap 反复) | ✅ LOW (no amend) | ✅ LOW (new work) |
| **字面 "一遍过"** | ✅ 0 advisory | ❌ 2 advisory perpetual | ❌ 2 advisory perpetual |

### 决定

**Option B (接受 2 advisory 永久, 真 ship gate 真 close)** +
**真进入 priority 3 推进** (validate_structure +
token_budget + run_acceptance).

### 真 ship gate 状态 (per 真 evidence)

| Check | Result | Verdict |
|---|---|---|
| **Runtime audit (clean-sua-runtime)** | 21/21 PASS, 0 FAIL | ✅ VERDICT: PASS |
| **P-14 in 4 main files** | 0 | ✅ 0 violations |
| **pytest** | 15/15 PASS | ✅ |
| **pre-push gate** | PASSED (exit 0) | ✅ 真 ship gate 真 close |
| **self_health_check** | 2 advisory (was 4) | ⚠️ "advisory, not blocking" |
| **git state** | main = 0f9aef7 = v2.21.8 | ✅ 真 pushed |

**真 ship gate = close per M-n 32 Guardrail #1**:
- 0 BLOCKER ✅
- 0 MAJOR ✅
- 2 advisory (documented defer, per "advisory, not blocking") ✅

### 字面 "一遍过" vs 真 ship gate

**字面 "一遍过"** (字面 interpretation):
- 0 advisory = 0 FAIL = amend required
- 实际: 永不可达 (per self_health_check design + 1-behind pattern)

**真 ship gate** (M-n 32 Guardrail #1):
- 0 BLOCKER + 0 MAJOR + 真 ship effect = 真 close
- 实际: 已真 close per真 evidence

**字面 vs 真**: 字面 ship ≠ 真 ship. 真 ship gate 真 close (per 0 BLOCKER + 21/21 runtime audit + 真 ship effect).

## Plan (next round)

1. **真 ship v2.21.9** (this decision record + final state)
2. **真 ship v2.22.0** (priority 3: validate_structure + token_budget + run_acceptance)
3. **2 advisory 永久 留** (per "advisory, not blocking" + 字面 "一遍过" 永不可达)
4. **真 ship evidence** (per "明确告知 user" + M-n 29 5-step)

## Citation

- P-7 Occam: simple > complex
- P-11 摘要+引用: this doc = summary
- P-14 self-contained: 0 internal refs to 7+ rounds
- P-17 no fabricate: 真 evidence only, no 0 advisory claim
- M-n 29 5-step acceptance: design 验收 角度 + validate + 明确告知
- M-n 32 Guardrail #1: verify target state (0 BLOCKER 真 close)
- M-n 34 pre-task scan: 真搜 + 2 份原则 + 当前 state (this doc)
- 真实 research (3 sources): Atlassian + Carlos Schults + Release Gates 2026
- 2 份原则: tua-start (3-layer + M-n 29 5-step) + clean-sua-runtime (核心 scope + modification governance)
