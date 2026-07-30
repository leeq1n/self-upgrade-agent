# Implementation Plan — Principle Collapse Prevention (post-evaluation)

> **Decision**: Pick A4 + D2 + B3 + C3 (per deep evaluation).
> **Skip**: A1/A5/B1/C1/D1 (no value); A2/A3/B2/C2/C4/D3/D4 (risks outweigh).
>
> **Reference**: docs/PRINCIPLE_COLLAPSE_PREVENTION.md v2.5.3

## Tasks (top-down)

```
ROOT: 真 ship enforcement + 清理冗余
│
├── T1 [NEXT] clean-sua 真 ship A4 (weekly cron)
│   ├── T1.1: 写 .hermes/scripts/cross_repo_audit.py (per A2 sub-task,
│   │        必为 A4 准备)
│   ├── T1.2: 写 .github/workflows/sibling-audit.yml
│   │        (weekly cron, Monday 03:00 UTC)
│   ├── T1.3: 写 tests/test_cross_repo_audit.py
│   ├── T1.4: 本地真跑 verify (不 push, 让你 approve)
│   ├── T1.5: commit + tag v2.6.0 (MINOR: 新 enforcement layer)
│   │        + push
│   └── T1.6: 5-step acceptance report
│
├── T2 [AFTER T1] clean-sua 真 ship D2 — extend doc
│   ├── T2.1: docs/PRINCIPLE_COLLAPSE_PREVENTION.md 加 section
│   │        "Implementation status: 2026-07-30" — 记录
│   │        A4 真 ship + A2 真 ship + A5 留 future session
│   ├── T2.2: commit + push (docs-only PATCH = v2.6.1)
│   └── T2.3: 5-step acceptance
│
├── T3 [PARALLEL] 删 sua-start (per B3)
│   ├── T3.1: 你手动 (per 你原话"那三个不动,我一会儿手动删了更新版本")
│   │        — 但现在 5 Q 已决策, 我给 guide
│   └── T3.2: 释放 72 MB 空间
│
└── T4 [OPTIONAL] 删 sibling (per C3, 你手动)
    └── T4.1: 你手动 (per 你"sibling 不重要")

## Time estimate (per 真凭据)

| Task | Effort | Risk | Status |
|---|---|---|---|
| T1.1 cross_repo_audit.py | 1-2 hours | low (new file) | this session |
| T1.2 .github/workflows | 30 min | low (yml config) | this session |
| T1.3 tests | 30 min | low | this session |
| T1.4 local verify | 15 min | none | this session |
| T1.5 commit + push | 5 min | low (already pushed v2.5.3 ok) | this session |
| T1.6 acceptance | 10 min | none | this session |
| T2 doc extension | 15 min | low | this session |
| T3/T4 delete | 1 min | low (manual) | your manual |

Total: ~4-5 hours, but I propose splitting:

**Now (this session)**:
- T1.1 cross_repo_audit.py 真 ship (Q3 真 enforce)
- T1.3 tests 真 ship
- T1.4 local verify (per M-n 32 Guardrail #1)
- T2.1 doc extension
- T1.5 commit + tag v2.6.0 + push
- 5-step acceptance

**Next session (your judgment)**:
- T3/T4 manual delete
- T1.2 weekly cron activation
```

## What I will 真 ship now (per plan above)

Per R80 真 ship effect (commit + push + verify):

1. **T1.1** — `.hermes/scripts/cross_repo_audit.py` (新文件, ~150 行)
2. **T1.3** — `tests/test_cross_repo_audit.py` (新文件, ~80 行)
3. **T2.1** — `docs/PRINCIPLE_COLLAPSE_PREVENTION.md` append "Implementation status"
4. **T1.5** — commit + tag v2.6.0 + push

**Total**: 4 files, ~280 lines, 1 tag, 1 push.

## Why I pick A4 over A5 (真 trade-off reasoning)

A5 = 3 Q 全解 (A2+A3+A4):
- A3 改 hooks/commit-msg 高 risk (会 break existing commits)
- A5 = 跨 session (commit-msg 改需 multi-session per M-n 15)

A4 = 2 Q 解 (Q1 + Q3):
- A4 自动 detect drift
- A4 不改已有 hook
- A4 本 session 真 ship

按 P-7 Occam + R78 真 cause: A4 真解决 Q3 不再犯 (auto-detect drift = sibling 重新 mirror pollution 自动 open issue), 这是**最重要**问题 (你原话), 留 A3 给未来 session 风险可控.

## What I'll NOT do (per decision)

- ❌ A1/B1/C1/D1 (不动 = 0 价值, 字面 trap)
- ❌ A2 单独 ship (会被 A4 包含, 重复 work)
- ❌ A3 hook_principles (改 hook 高 risk, 留新 session)
- ❌ A5 全做 (跨 session 风险)
- ❌ B2 提取 sua-start 知识 (污染 risk, 你原话"旧版不用了")
- ❌ B4 归档 (git 操作 risk)
- ❌ C2/C4 sibling adapter (需你 spec, 你说不重要)
- ❌ D3 memory apply (bloat risk)
- ❌ D4 user profile (cross-profile risk)

## 5-step acceptance criteria (per task)

每个 ship 必须 verify:
1. **Plan** — 自顶向下分治 (上面 ROOT → T1-T4)
2. **Search** — 真 verify sibling / upstream 状态 (git + filesystem)
3. **Lesson** — 真 ship gate (cross_repo_audit + tests + self_health_check)
4. **Observe** — 真 verify before claim (per M-n 32 Guardrail #1)
5. **Cite** — P-n / M-n / R-n cite in commit-msg (hook enforce)