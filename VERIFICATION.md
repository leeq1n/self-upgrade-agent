# VERIFICATION — Project-level verification summary

> L0: One-page verification summary — what's
been verified + cross-refs.  Per P11 摘要+
引用 + R6 + M-n 20 framework-agnostic.

Last P20-verified: 2026-07-15

## 1-axiomatic verification (per P5 measure
twice commit once)

- [x] SUA 621 tests PASS + 6 skip + 0 fail
- [x] `hooks/commit-msg` INSTALLED (P-n 1-29
  whitelist per c96 P28 LIFT + c167 P29 LIFT)
- [x] All commits reference at least 1 P-n

## R1-R12 invariant compliance (per c173)

| R-n | Status | Last verified |
|---|---|---|
| R1 | ✅ | c173 |
| R2 | ✅ | c173 |
| R3 | ✅ | c138 (trigger annotations) |
| R4 | ✅ | c173 |
| R5 | ✅ | c60-c192 (24+ docs fixed) |
| R6 | ✅ | c131-c136 (L2 companions) |
| R7 | ✅ | c173 |
| R8 | ✅ | c173 (3 OS-safe paths) |
| R9 | ✅ | c173 |
| R10 | ✅ | c173 |
| R11 | ✅ | c173 |
| R12 | ✅ | c139 + c169 (KG sync) |

**R1-R12 ALL PASS** (per c173 + c191).

## P-n / M-n completeness (per c167 + c183 + c189)

- **25 P-n working** (P1-P29 minus P6/P15/P16/P24)
- **27 M-n codified** (M-n 1-27, per c183 + c189 + c197)
- **24 M-n L2 companions** + 3 段 in OPERATING_RULES.md

## 3-project arch (per round 82 + c101)

| Project | Status | Arch role |
|---|---|---|
| SUA | ~95% | 原则库 (P-n + M-n + R-n) |
| skill-incubator | 100% | Skill 孵化器 (5 phases) |
| agent-reflection-skill | 100% | 已孵化 skill (6 primitives) |
| knowledge-graph-seed | synced | Cross-project KG (P1-P29) |

## Framework-agnostic compliance (per M-n 20 + c116)

- SUA: framework-agnostic (Hermes / Claude Code / Codex)
- skill-incubator: framework-agnostic
- agent-reflection-skill: framework-agnostic + AGENTS.md framework compatibility matrix
- knowledge-graph-seed: framework-agnostic

## Cross-references

- SUA `docs/PRINCIPLES.md` — 25 P-n working
- SUA `docs/OPERATING_RULES.md` — 26 M-n codified
- SUA `AGENTS.md` — operating rules for new agents
- SUA `docs/PROJECT_STATE.md` — current snapshot
- SUA `.hermes/plans/2026-07-15_160000-replan_DETAIL.md` — Changelog
- skill-incubator `SKILL_DESIGN.md` — 5-phase process
- agent-reflection-skill `SKILL.md` — invocation contract
- knowledge-graph-seed `docs/PHILOSOPHY.md` — P1-P29 sync

## Verification procedure for future agents

1. Read `VERIFICATION.md` (this file, L0).
2. Read `AGENTS.md` (operating rules).
3. Run `pytest` to confirm tests still PASS.
4. Spot-check `git log --grep='P[0-9]'` for
   P-n citation in recent commits.
5. Re-read 1 sample M-n 段 per M-n 26
   (context-decay-management) + 1 sample
   P-n 段 per P29.

## Mechanical enforcement layer (per retrospective 2026-07-16)

Per 你 turn "根据原则做决定" + retrospective 4-FAIL
diagnosis (M-n 32 Guardrail #4 violation across
multiple turns — claimed DONE without applying
5-step), this project adds mechanical external
trigger layer:

- **`.hermes/scripts/m_n29_5step.py`** (commit `05cd4d5`):
  deterministic baseline — 15 design criteria + 5
  primitives + validate cycle
- **`hooks/prepare-commit-msg`** (commit `f11b145`):
  commit-time reminder trailer when commit body
  mentions "task done" / "完成" / "PASS"
- **`AGENTS.md` "Task-done-notify reminder"段** (commit
  `e80fc73`): L0 surface with hard step 5 = external
  script invocation

## What's NOT yet enforced

Per 你 turn "怎么样才能保证自主阅读学习" + M-n 32
Guardrail #5 (auto-learning): LLM self-invocation
of M-n 29 5-step is NOT 100% guaranteed.  AGENTS.md
reminder + commit-time trailer + external script
all maximize external-trigger coverage.  Future
agents reading this project should:

1. Run `python .hermes/scripts/m_n29_5step.py --self`
   BEFORE claiming task done
2. Apply 5 primitives (Analyze / Reason / 联想 /
   归纳 / 总结) in plan / commit message
3. Cite P-n / M-n values that motivated changes

P-n cited: P17 (老实说 — explicit retrospective
diagnosis), P25 (post-modify re-apply per M-n 34
self-application), P29 (recursive enforcement).
M-n cited: M-acceptance-protocol (M-n 29 external
trigger), M-self-learning-guardrail (M-n 32
Guardrail #4 mechanical enforcement), M-knowledge-
context-trade-off (M-n 30 Priority 1).

## 3-layer governance (per 你 turn 2026-07-16)

Per 你 turn 3-layer architecture proposal +
M-n 30 Priority 1 (knowledge 充足) +
retrospective failure mode (e7c9072 → c681e0b
revert + a447b0b redo using `core-layer/`):

- **`core-layer/README.md`** (commit `a447b0b`):
  L0 marker for the 3-layer separation (核心/
  用户/项目).  Defines modification governance
  for core layer.
- **`core-layer/governance-template.md`** (commit
  `a447b0b`): L1 eval-before + verify-after
  template.  Agent-self-edit only, with
  M-n 29 5-step gate before AND after commit.

The **核心 layer scope** (per core-layer/README.md):

| In 核心 | NOT in 核心 |
|---|---|
| AGENTS.md, hooks/, .hermes/scripts/ | docs/PRINCIPLES.md |
| OPERATING_RULES.md M-n sections | docs/PROJECT_STATE.md |
| Mechanical enforcement trigger | docs/* (project-specific) |

Sibling repos (agent-reflection-skill,
skill-incubator, knowledge-graph-seed) each
adopted cross-ref to core-layer/ in their
VERIFICATION.md (commits `08ed89e`, `274ad5d`,
`7438fc4`).  See each repo's VERIFICATION.md
"3-layer governance cross-ref" 段.

## 4 critical-thinking primitives (per 你 turn 2026-07-16)

Per 你 turn 3-layer + critical-thinking injection:
SUA now codifies **9 primitives** for
self-correction (5 constructive + 4 adversarial):

- **5 constructive primitives** (existing):
  Analyze, Reason, 联想, 归纳, 总结
- **4 critical-thinking primitives** (new M-n 35):
  质疑 (Challenge), 逆向 (Invert), 预演失败
  (Pre-mortem), 对立论证 (Steelman-the-opposite)

Per M-n 14 two-track-reasoning: complete
thinking needs BOTH constructive + adversarial.

**L1 detail**: `docs/M_CRITICAL_THINKING_PRIMITIVES_DETAIL.md`
(commit `35a25d3`).

**Integration**:
- AGENTS.md "Task-done-notify reminder"段 updated
  (commit `d31e9de`)
- `M_ACCEPTANCE_PROTOCOL_DETAIL.md` Step 2 includes
  both constructive + adversarial (commit `f0ba8b7`)
- `.hermes/scripts/m_n29_5step.py` Step 2a runs
  critical-thinking BEFORE constructive (commit
  `b3b56a1`)
- `hooks/prepare-commit-msg` trailer checklist now
  includes Step 2a (commit `80cad53`)

**Default-on**: high-stakes commits (architecture
/ cross-project / new P-n or M-n lifts).
**Optional**: single-file refactors.
**Skip**: trivial fixes (typo / formatting).

## M-n 36 release-audit (per 你 turn 2026-07-16)

Per 你 turn retrospective + 自顶向下原则:
SUA codified **M-n 36 (release-audit)** for
release-time cleanliness.

**5 checks** (per `.hermes/scripts/release_audit.py`,
commits `c37c443` + `18e893e`):

1. **Commit count** — commits since last x.0.0
   tag ≤ 5 (configurable).
2. **P-n cited** — at least 1 P-n or M-n reference
   in commit messages since last tag.
3. **Q1+Q2 fixes embedded** — CHANGELOG.md
   references both Q1 (Anti-patterns) and Q2
   (Triggers) fix commits.
4. **Tag at HEAD** — HEAD == tag^{commit}
   (annotated tag dereferenced).
5. **Zip matches tag tree** — zipfile.namelist()
   == git ls-tree tag output.

**L2 detail**: `docs/M_PRE_RELEASE_AUDIT_DETAIL.md`
(commit `92b8732`).

**Integration**:
- AGENTS.md "Read first" item 10 = M_PRE_RELEASE_AUDIT_DETAIL.md
  (commit `ffacef7`)
- OPERATING_RULES.md M-n 36 section appended (commit
  `6683093`)
- `hooks/prepare-commit-msg` adds M-n 36 release-audit
  block (commit `5215126`)
- 3 sibling repos (skill-incubator, knowledge-graph-seed,
  [skill originally then reverted]) added M-n 36 cross-ref
  in their VERIFICATION.md (commits `deefd68`, `999fd13`)

**Default-on**: pre-release / pre-distribution.
**Optional**: per-commit dry-run.
**Skip**: WIP / draft commits.

**Self-application**: per 你 turn heuristic "细项目
直接改 + 大项目少提交" + M-n 18 destruction, this
project (SUA) = big project = minimize commits; but
codification M-n-n requires cross-ref here.

## How to update this verification

When a new P-n / M-n is added (codified +
LIFTED), update this file (per M-n 17 Path 1
re-audit).