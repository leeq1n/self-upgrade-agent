# AGENTS — Operating Rules for AI Agents in This Project

> **LAYER**: project (L1 index — see "3-layer architecture" below)
>
> L0: AI agents entering this repo MUST read
> `core-layer/AGENTS_CORE.md` FIRST (always-loaded
> subset, ~6K chars, cache-stable), then this
> file (per-task 段s, load on demand).
>
> Per cache optimization (per docs/PRINCIPLES.md):
> - `core-layer/AGENTS_CORE.md` = always-loaded
>   (100% cache hit when stable)
> - This file = per-task (loaded when needed)
> - Per P11 摘要+引用 + P14 docs current.
>
> Split design: ~30K → ~6K always-loaded + ~3K
> per-task-index (summary + references).

## Cross-references to always-loaded 段s

> All "always-loaded" 段s are in
> `core-layer/AGENTS_CORE.md` (per P11 摘要+引用):

| 段 | Reference |
|---|---|
| Pre-task scan (M-n 34) | AGENTS_CORE.md § same |
| Read first (in order) | AGENTS_CORE.md § same |
| Hard rules (top 6 P-n) | AGENTS_CORE.md § same |
| What NOT TO DO | AGENTS_CORE.md § same |
| Commit message contract | AGENTS_CORE.md § same |
| When in doubt | AGENTS_CORE.md § same |

## Per-task 段s (this file = summary + reference)


### "继续" protocol

When user says "继续", agent MUST interpret as **推进任务**
(考虑之前说的那些思考方法, 考虑是否 重新做规划等, 考虑自顶向下等原则),
NOT as a generic continuation. **Two cases**:
- **任务未完成**: 承接上文, 推进 + 自顶向下分治
- **任务已完成**: 提议验收 + 新方向

**Live detail**: see AGENTS_DETAIL.md § "继续" protocol.


### "学习一下" protocol

When user says "学习一下", interpret as **cross-project learning**, NOT
single-repo learning. **Three layers of learning**:
- **核心层**: `core-layer/` + `AGENTS.md` + `hooks/` (rarely modified)
- **用户层**: per-user customization
- **项目层**: per-project knowledge

**Live detail**: see AGENTS_DETAIL.md § "学习一下" protocol.


### "主动修改 skill" protocol (3-layer modification policy)

When working on skills (or user-facing artifact), apply 3-layer policy:
1. **核心层修改尽可能少** — modify core only when absolutely necessary
   (e.g., new M-n, consistent failure pattern)
2. **用户层主要改** — modify user layer based on learned knowledge
3. **项目层知识随项目变** — project layer changes with project

**Live detail**: see AGENTS_DETAIL.md § "主动修改 skill" protocol.


### Iterative thinking protocol

Thinking is iterative, not single-pass. When first round produces output:
1. **Apply** (execute / commit / reply)
2. **Observe** (what worked, what didn't, what's missing)
3. **Re-think** (does my reasoning have blind spots?)

**Live detail**: see AGENTS_DETAIL.md § Iterative thinking protocol.


### Recursive test-verify protocol

Per TDD + recursive testing + 测试金字塔:
- Write test first, code until pass
- Sub-task 完成时 必须 一直测试-验收直到通过才能结束, 交给父任务
- 主动验收 (mod M-n 14 Track 1)

**Live detail**: see AGENTS_DETAIL.md § Recursive test-verify.


### Skill context cleanliness (P-14 self-contained mandate)

When working on skills (or user-facing artifact):
- **NO dev-session references** in skill content
  (e.g., dev history retrospective = not user-facing)
- **NO internal ref** patterns (round numbers, sibling paths, hermes refs)
- **NO SUA-specific examples** in skill content

**Live detail**: see AGENTS_DETAIL.md § Skill context cleanliness.


### Multi-perspective audit angles (per M-n 16)

When working on skills (or user-facing artifact), apply audit angles:
- **A1: User-skill angle** — when user installs skill, can they USE all
  primitives + 段s effectively?
- **A2: Fresh agent angle** — does a fresh agent find what they need?
- **A3: Daily user angle** — does daily workflow work end-to-end?
- **A4: Uninstaller angle** — does uninstall clean remove everything?
- **A5: Contributor angle** — can a contributor add a rule easily?
- **A6: Multi-platform angle** — works on Windows/Mac/Linux?
- **A7: Audit angle** — does commit history reveal real story?

**Live detail**: see AGENTS_DETAIL.md § Multi-perspective audit angles.


### Task-done-notify reminder (per M-n 16 stage 1-2)

**Before any commit / before sending "task done" message**, agent MUST
apply **5 primitives**:
1. **Plan** — 自顶向下分治 (per P-22)
2. **Search** — 真 verify state (per M-n 32 Guardrail #1)
3. **Lesson** — 真 identify root cause (per importance vs cause principle in docs/OPERATING_RULES.md)
4. **Observe** — 真 ship gate (per M-n 32)
5. **Cite** — 引用 P-n / M-n / R-n (per commit-msg hook)

**Live detail**: see AGENTS_DETAIL.md § Task-done-notify reminder.


### Post-completion verification suggestion

When agent reports task completion to user, the report MUST include:
1. **明确说明** (clear statement): "task done" / "complete" / "ACCEPTED"
2. **建议下一步做验收** (suggest next verification)

**Live detail**: see AGENTS_DETAIL.md § Post-completion verification.


### Operating rules (M-n 1-34)

**34 M-n** in `docs/OPERATING_RULES.md`. Per Phase 3 audit:
- 28 M-n codified with L1 段
- 22 M-n with L2 _DETAIL.md companion
- M-n 1, 5, 6, 9, 10 not in L1 (P-layer principles, not operational)

**Live detail**: see AGENTS_DETAIL.md § Operating rules.


### Cross-project sync

**SUA is a self-contained knowledge library.**  It does not depend on
any sibling repository; sibling projects are maintained independently
(standalone or frozen) and are not downstream of SUA.

**L4 boundary revision**:
- (a) 1 line / typo / cross-ref = low-risk autonomous, skip 7-check

**Live detail**: see AGENTS_DETAIL.md § Cross-project sync.


### 3-layer architecture

This project uses a **3-layer policy** to govern documentation
and modification rules:

| Layer | Marker | Files | Modification rule |
|---|---|---|---|
| **核心层** (core) | `LAYER: 核心` | `core-layer/AGENTS_CORE.md`, `hooks/*`, `.hermes/scripts/*` | M-n 15 multi-session + user explicit authorization |
| **项目层** (project) | `LAYER: project` | `AGENTS.md`, `AGENTS_DETAIL.md`, `docs/*`, `README.md`, `CONTRIBUTING.md`, `LICENSE`, `tests/*` | Update as project evolves |
| **用户层** (user) | `LAYER: user` | local-only (e.g., `~/.config/sua/USER_LAYER.md` or repo-local gitignored file) | Per-user customization, never committed to upstream |

**Why**: per the "主动修改 skill" protocol,
核心层修改需要尽可能少 (modify core only when absolutely necessary),
用户层主要改 (most edits happen in user layer), 项目层随项目变
(project layer changes with project).

**For fresh agents**: always read the LAYER marker at the top of
any doc to know which layer it belongs to and what modification
rules apply.

**Live detail**: see AGENTS_DETAIL.md § 3-layer architecture.


### Detail (L2)

For "## See also" section (long, conditional load docs), see
AGENTS_DETAIL.md. Per R6, this companion is required when the
summary exceeds 7 KB.

**Live detail**: see AGENTS_DETAIL.md § Detail (L2).


## Self-application (P29 recursion)

This split itself applies the principles:
- **P5** (test before commit) = release_audit 5/5
- **P11** (摘要+引用) = AGENTS.md = reference index
- **P14** (docs current) = AGENTS_CORE.md and
  AGENTS.md updated in same commit
- **P18** (auto-update) = future agents read
  AGENTS_CORE.md first
- **P22** (when stuck → plan) = split structure
  documented here
- **M-n 18** (destruction) = minimal viable split

If a 段 is missing from AGENTS_CORE.md, agent
should fall back to AGENTS.md (per P22).

## Recent retrospective

For session-specific learnings (5-question audit pattern, banned-
word language habit shift, "OcCam ≠ Stop" meta-insight, project
layer > agent layer, audit scope declaration), see
AGENTS_DETAIL.md § Retrospective notes.

Apply at every commit / audit / cross-project decision; not
encoded as always-loaded rule (per OcCam).
