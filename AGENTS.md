# AGENTS — Operating Rules for AI Agents in This Project

> L0: AI agents entering this repo MUST read
> `core-layer/AGENTS_CORE.md` FIRST (always-loaded
> subset, ~6K chars, cache-stable), then this
> file (per-task 段s, load on demand).
>
> Per user message 2026-07-16 cache optimization:
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
| What NOT to do | AGENTS_CORE.md § same |
| Commit message contract | AGENTS_CORE.md § same |
| When in doubt | AGENTS_CORE.md § same |

## Per-task 段s (this file = summary + reference)


### "继续" protocol (per user message 2026-07-16)

Per user message "我说继续的时候, 一般都和我之前说的 那段是一个意思":  When user message says "继续", agent MUST interpret it as: **推进任务 (考虑之前说的那些思考方法, 考虑是否 重新做规划等, 考虑自顶向下等原则)**, NOT as a generic continuation.  **Two cases**:  | Case | user message signal | Agent action | |---|---|---| | **任务未完成** | 该消息隐含承接上文 (e.g., previous tur...

**Live detail**: see the matching section in [`AGENTS_DETAIL.md`](AGENTS_DETAIL.md).


### "学习一下" protocol (per user message 2026-07-16)

Per user message "我说学习一下的时候, 指的是不仅仅 是hermes学习, 也是这几个项目里 agent 的核心层 / 用户层需要学习, 需要在迁移到其他用户之后还能 有充足的这类知识":  "学习" = **cross-project learning**, NOT single- hermes learning.  **Three layers of learning**:  | Layer | Where | What | Persistence | |---|---|---|---| | **核心** | `core-layer/` + `AGENTS.md` + `hooks/...

**Live detail**: see the matching section in [`AGENTS_DETAIL.md`](AGENTS_DETAIL.md).


### "主动修改 skill" (per user message 2026-07-16)

Per user message "我希望这skill在别人电脑上还会主动 修改skill, 但是核心层修改需要尽可能少, 主要 修改用户层 (根据学到的知识判断改哪一层), 而 项目层知识随着项目变化而变化":  **3-layer modification policy**:  1. **核心层修改尽可能少** — modify core only    when absolutely necessary (e.g., new M-n,    consistent failure pattern). 2. **用户层主要改** — modify user layer mainly,    based ...

**Live detail**: see the matching section in [`AGENTS_DETAIL.md`](AGENTS_DETAIL.md).


### Iterative thinking (per user message 2026-07-16)

Per user message "有的时候, 一层思考不够充分, 执行 阶段可以判断需要额外轮的思考, 下一轮继续":  **Thinking is iterative, not single-pass**.  When the first round of thinking produces an output, the agent should:  1. **Apply the output** (execute / commit / reply) 2. **Observe results** (what worked, what didn't,    what's missing) 3. **Re...

**Live detail**: see the matching section in [`AGENTS_DETAIL.md`](AGENTS_DETAIL.md).


### Recursive test-verify (per user message 2026-07-16)

Per user message "我希望你能在修改后主动验收" + "自顶 向下分治法做任务的时候, 子任务做完的时候也需要 一直测试-验收直到通过才能结束, 交给父任务":  **类比 (per M-n 14 Track 1)**: this rule is **TDD + recursive testing + 测试金字塔**:  | Analog | Mechanism | |---|---| | **TDD (Test-Driven Development)** | Write test first, code until pass | | **Recursive testing** | Bas...

**Live detail**: see the matching section in [`AGENTS_DETAIL.md`](AGENTS_DETAIL.md).


### Skill context cleanliness (per user message 2026-07-16)

Per user message "skill 库是最终面向用户的库, 需要 为新agent保持项目上下文干净":  When working on skills (or any user-facing artifact):  - **NO dev-session references** in skill content   (e.g., "per user message 2026-07-16 retrospective" =   dev history; not user-facing). - **NO SUA-specific examples** in skill content   (e.g., "in ...

**Live detail**: see the matching section in [`AGENTS_DETAIL.md`](AGENTS_DETAIL.md).


### Multi-perspective audit angles (per user message 2026-07-16)

Per user message "我教过的那几个角度" + "或许你需 要学习下这个" + "你说学习的时候要考虑本地的 这几个项目":  When working on skills (or any user-facing artifact), apply **2 audit angles**:  ### A1: User-skill angle (skill usability)  **Question**: when user installs skill, can they USE all the primitives + 段s effectively?  **Sub-checks**:  1....

**Live detail**: see the matching section in [`AGENTS_DETAIL.md`](AGENTS_DETAIL.md).


### Task-done-notify reminder (per user message 2026-07-16)

Per user message "我之前说过，skill 最后的时候要验收，你验收 了吗？你不知道要验收这件事" + user message 2026-07-16 "很多地方说的思考都需要用原则里的思考方法。在工作 的时候你经常想不到用这思考方法，你得问问自己为什么" + L0.1-L0.3 commits in `fix/m29-trigger-explicit` branch:  **Before any commit / before sending "task done" message**, agent MUST apply **5 primitives** (per M-n 16 stage 1-2 ...

**Live detail**: see the matching section in [`AGENTS_DETAIL.md`](AGENTS_DETAIL.md).


### Post-completion verification suggestion (per user message 2026-07-16)

Per user message "因为有了更改, 现在应该再次验收" + "做完任务后, 跟用户明确说明的同时, 也需要 跟用户说建议下一步做验收":  When agent reports **task completion** to user, the report MUST include:  1. **明确说明** (clear statement): "task done" /    "complete" / "ACCEPTED" — explicit. 2. **建议下一步做验收** (suggest next verification):    "建议你进行下一步验收" / "建议验证 X...

**Live detail**: see the matching section in [`AGENTS_DETAIL.md`](AGENTS_DETAIL.md).


### Operating rules (M-n 1-34, per c95-c237 + M-pre-task-scan)

**34 M-n** in `docs/OPERATING_RULES.md` (per Phase 3 audit 2026-07-16: 28 M-n codified with L1段, 22 with L2 _DETAIL.md companion.  M-n 1, 5, 6, 9, 10 not in L1 (P-layer principles, not operational).):  - **M-n 1**: (top-level: principle-layer, no L1) - **M-n 2**: (concept-layer, no L1 in OPERATING_R...

**Live detail**: see the matching section in [`AGENTS_DETAIL.md`](AGENTS_DETAIL.md).


### Recent cross-project sync (per user message 2026-07-15)

Per M-n 30 Priority 5: SUA → skill-incubator (c215) → skill (c219) → KG (c217). All 3 sibling projects have Reading order + SUA cross-ref + Update order rule + "NOT in chain"段 (KG, c232).   **修订 L4 boundary (per c95 + memory 7)**:  - (a) 1 line / typo / cross-ref = low-risk autonomous, skip 7-check ...

**Live detail**: see the matching section in [`AGENTS_DETAIL.md`](AGENTS_DETAIL.md).


### Detail (L2)

For "## See also" section (long, conditional load docs), see [`AGENTS_DETAIL.md`](AGENTS_DETAIL.md). Per R6, this companion is required when the summary exceeds 7 KB.

**Live detail**: see the matching section in [`AGENTS_DETAIL.md`](AGENTS_DETAIL.md).


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
