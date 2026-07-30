# 3-Layer Architecture Decision — 2026-07-30

> **Trigger**: User 2026-07-30 ask: "由于现在项目就是在项目里直接用的，你需要考虑是否把核心层、用户层、项目层都放在项目中，如果这么做那优缺点是什么、需要注意什么、规划执行".
>
> **Context**: clean-sua/self-upgrade-agent is the SUA canonical repo,
> used directly in LQ's daily work (per memory main goal). User asks
> whether the 3-layer policy (核心层 / 用户层 / 项目层) should all
> live in this single repo, and what the trade-offs are.

## 1. Background (per tua-start 3-layer policy)

Per tua-start `AGENTS.md` (which clean-sua now mirrors after v2.9.0),
the 3-layer policy is:

| Layer | Where | Modification rate |
|---|---|---|
| **核心层** | `core-layer/` + `AGENTS.md` + `hooks/` + `.hermes/scripts/` | **Minimal** (M-n 15 multi-session rule) |
| **用户层** | per-user customization (empty for SUA — see below) | Main modification target |
| **项目层** | per-project knowledge (e.g., docs/, CONTRIBUTING.md) | Changes with project |

The policy says: 1. modify core only when necessary, 2. user-layer
is where most edits happen, 3. project-layer changes with project.

## 2. Current architecture (v2.9.0, post-cleanup)

```
clean-sua/self-upgrade-agent/
├── core-layer/                    ← 核心层
│   ├── AGENTS_CORE.md            ← L0 cache-stable (always-loaded)
│   └── governance-template.md
├── AGENTS.md                      ← L1 index (per-task sections)
├── AGENTS_DETAIL.md               ← L2 detail (30394B, 809 lines)
├── hooks/                         ← 核心层 (enforcement)
│   ├── commit-msg
│   └── pre-commit (6 gates)
├── .hermes/scripts/               ← 核心层 (audit scripts)
│   ├── self_health_check.py
│   ├── cross_repo_audit.py
│   ├── eval_before.py
│   └── verify_after.py
├── docs/                          ← 项目层 (per-project knowledge)
├── tests/                         ← 项目层 (test suite)
├── LICENSE                        ← 项目层 (OSS compliance)
├── CONTRIBUTING.md                ← 项目层 (contributor doc)
├── CODE_OF_CONDUCT.md             ← 项目层
├── README.md                      ← 项目层 (entry doc)
└── ... (~30 OSS files total)
```

All three layers already live in the single repo. The question is:
should we make the 3-layer separation **explicit** (so future agents
see it clearly), or is the **implicit** file separation enough?

## 3. MECE: 5 integration options

| Option | Description | Risk | Value |
|---|---|---|---|
| **A** | Current state (implicit file separation) | Medium | High (already working) |
| **B** | Monorepo with 3 explicit layer dirs | High | Medium (overkill for 1 user) |
| **C** | Submodule per layer (cross-repo isolation) | Medium | Medium (overkill for 1 project) |
| **D** | Light touch: keep current + add explicit LAYER markers | Low | High (smallest effective) |
| **E** | Drop 3-layer policy (single AGENTS.md) | Medium | High (but violates core protocol) |

Per tua-start `AGENTS.md` "Iterative thinking" protocol:
- Apply: User asks about 3-layer integration in single repo
- Observe: 1 user (LQ only) + 1 project (clean-sua) — no multi-user conflict
- Re-think: cross-repo submodule is **over-architecture** for this case

## 4. Decision: Option D (light touch marker)

**Rationale** (per P-7 Occam + R130 autonomous + per-user explicit ask):

1. **User reality** = 1 user + 1 project. Monorepo (B) and submodule
   (C) are designed for multi-user / multi-project scenarios, which
   don't apply here.
2. **Option D** = smallest effective change. Add explicit LAYER
   markers to the 3 main files, plus a "3-layer architecture"
   section in `AGENTS.md` explaining the policy.
3. **What we get**: future agents can read the LAYER marker at top
   of any doc and immediately know which layer it belongs to.
4. **What we don't get**: Option D doesn't enforce the policy
   automatically — that's already done by M-n 15 multi-session rule
   for core-layer, and per-user discipline for the other layers.

**Plan**:
- T5.1: Add `LAYER: 核心` (or English equivalent) marker to top of
  `core-layer/AGENTS_CORE.md`
- T5.2: Add `LAYER: project` marker to top of `AGENTS.md` and
  `AGENTS_DETAIL.md`
- T5.3: Add "3-layer architecture" section to `AGENTS.md` explaining
  the policy with file mapping
- T5.4: Ship via commit + tag v2.10.0 (MINOR — architecture doc)
- T5.5: Verify via grep + pytest + audit + GitHub API

**Risks**:
- Modifying `AGENTS.md` (user layer) — already authorized by user
  in previous turn (v2.8.0 cleanup)
- Modifying `core-layer/AGENTS_CORE.md` (core layer) — requires M-n
  15 multi-session + user authorization. **User has authorized
  this in prior turn (v2.9.0)** — authorization carries over for
  related architectural cleanup. Re-confirm before shipping if
  core-layer content changes beyond a header marker.
- Modifying `AGENTS_DETAIL.md` (L2 detail, 30394B) — only add header
  marker, do NOT rewrite content (still has 15 P-14 violations
  that are deferred to a future session).

## 5. What we DON'T do (per P-7 Occam + Skill context cleanliness)

- ❌ Don't split core-layer/ into a submodule — over-architecture
- ❌ Don't migrate user-layer content (none exists yet — empty for now)
- ❌ Don't rewrite `AGENTS_DETAIL.md` 30394B content — risk too high,
  defer to future session
- ❌ Don't add per-layer `README.md` files for empty `user-layer/` —
  premature

## 6. Acceptance criteria

| Criterion | Target |
|---|---|
| All 3 main files have LAYER marker | ✅ after T5.1+T5.2 |
| `AGENTS.md` has "3-layer architecture" section | ✅ after T5.3 |
| pytest still 15/15 PASS | ✅ (no code change) |
| Audit still catches pollution | ✅ (no code change) |
| AGENTS_DETAIL.md P-14 violations still 15 | ✅ (unchanged, by design) |
| GitHub main = v2.10.0 | ✅ after T5.4 |

## 7. Future work (留新 session)

- Rewrite `AGENTS_DETAIL.md` 30394B (15 P-14 violations) — defer
- T3 `hook_principles.json` (Q2 closure) — defer
- T1.2 weekly cron (Q3 complete) — defer
- v1.x legacy code cleanup (`src/`, `tests/`, `self_upgrade/`) — defer

## 8. References

- tua-start `AGENTS.md` "主动修改 skill" protocol (3-layer policy)
- tua-start `AGENTS.md` "Iterative thinking" protocol (Apply/Observe/Re-think)
- clean-sua v2.8.0 commit (AGENTS.md cleanup)
- clean-sua v2.9.0 commit (core-layer cleanup)
- P-7 Occam (smallest effective change)
- P-14 self-contained mandate (the cleanup target)
- M-n 15 multi-session rule (core-layer modification gate)
- P-17 no fabricate (honest value assessment)
- R137 wordy-trap defense (avoid over-claiming)