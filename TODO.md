L0: Pending tasks — backlog of next-up features.  Done items live in DONE.md.
Last P20-verified: 2026-07-13

# TODO —

Each task is a checkbox.  To claim: change `[ ]` to `[x]` and move
the line into DONE.md.  Keep this list SHORT and CURRENT; older
completed work lives in DONE.md.

> Convention: `- [ ]` = not started, `- [x]` = done, `- [/]` = in progress.

## Task ID + sub-task pointer convention (per user 2026-07-14)

When adding a new task to this file, use a hierarchical
ID scheme (per user 顿悟: "任务不一定是代码任务，
也可能是问题拆解汇总，写材料之类的任务"):

- **Top-level task**: `T-NNN` (3-digit sequence)
- **Sub-task**: `T-NNN.M` (parent ID + dot + sub-sequence)
- **Sub-sub-task**: `T-NNN.M.K` (deeper levels as needed)

Examples:
- `T-042`: top-level task "improve memory tool"
- `T-042.1`: sub-task "add doc layer"
- `T-042.1.2`: sub-sub-task "update USER_INSIGHTS cross-ref"

Format in entries: `T-NNN **Task title** ...` placed
at the start of the line, before the `**bold**` title.

When done, replace `[ ]` with `[x]`.  When the parent
task is complete and parent summary written, prefix
the entry with `[x-archived]` to signal "sub-tasks
consumed; no longer active" (per SUMMARY_LIFECYCLE
destroy contract pattern).

**When to use IDs** (trigger condition):

- Tasks that span multiple commits → use sub-task IDs.
- Tasks that have explicit dependencies on other
  tasks → use IDs for cross-references.
- Single-commit trivial tasks → no ID needed (existing
  convention `- [ ] **title**` is sufficient).

**Anti-patterns** (per P7 奥卡姆 + P23 doc>script):

- **Don't add IDs to every existing entry** — scope
  creep.  This is a forward-looking convention, not
  a back-fill mandate.
- **Don't create parallel task tree files** (e.g.
  TASK_TREE.md) — TODO.md is the single source of
  truth.  Per P11 摘要+引用, no duplicate.
- **Don't use a separate file-based task system**
  until multi-layer recursion is actually needed
  (P23 0-violations rule + M-add-then-reduce
  signal-trigger).  Current commit history + this
  TODO.md are sufficient for current scope.

**Why this is needed** (per user 2026-07-14):

"每次做完一条整理一下优先级，需要分成子任务的写
一下指向，方便新 agent 确认任务进行到哪里了".
Cross-task referencing (e.g. "this is part of T-042")
was previously ad-hoc; ID convention makes it
explicit and machine-parseable.

**Scope** (per P7 奥卡姆 + M-self-audit 4-level):

This is **1 logical feature**: "TODO.md gains a
task-ID convention for forward-compatibility".  No
back-fill of existing entries, no new files, no
script.  Future tasks use IDs; existing entries
keep their current form (forward-only).

## Completed (history, see DONE.md for details)

- [x] **Failure → regression test pipeline** — v2.3 (commit `0dc68cb`)
- [x] **Automatic replay of failure log** — v2.3.1 (commit `216f7e0`)
- [x] **Unified CLI** — v2.4.0 (commit `2442d09`)
- [x] **Gitignore cleanup** — v2.4.1 (commit `a5d3029`)
- [x] **Multi-paper reading** — v3.0.0 (commit `da3ba26`)
- [x] **Multi-paper selection** — v3.0.1 (4 sub-steps, 4 stage gates)
- [x] **Hotfix timeout bump** — v3.0.1 (commit `be0072c`)
- [x] **Progress markers** — v3.0.1 (commit `eb70e90`)
- [x] **v3.0.2 think-execute harness OVERALL** — 4 sub-steps + joint
      + wire into v2_round.  Commits `3d74ba8` + `d5b4a84` +
      `8b85660` + `009a26c` + `38920ff` + `9c69648` + `5623591`.
- [x] **v3.0.2 follow-ups** — 6 commits (--count N on harness+multi,
      奥卡姆 cleanup x2, unified `improve` with flags).
      Commits `30bcb1b` + `4f475eb` + `ed239b4` + `bb69983` +
      `2b88a79` + `20e958d`.
- [x] **Workflow-rules batch (20 commits, 2026-07-13)** —
      established 9 M-* rules (M-task-summary, M-must-read,
      M-context-snapshot, M-subtask-summary, M-intent-parsing,
      M-learn, M-add-then-reduce, M-self-audit, M-self-application).
      Sub-batches:
      - 1-5: M-intent-parsing + M-learn + RECURSIVE_DECOMPOSITION
        step-5 update + COMMON_PITFALLS 3-way table + AGENTS
        trigger surface (commits 9f1e3aa → 51638b1)
      - 6-12: M-add-then-reduce + M-learn dual-track + L0
        reminder + TODO recording + AGENTS orphan resolve +
        M-task-summary destroy contract + M-learn follow-ups
        (commits 5eb4fd0 → d5e2e95)
      - 13-19: split 3 sub-docs (SUMMARY_LIFECYCLE /
        SWITCH_SIGNALS / ADD_THEN_REDUCE) + _DETAIL companions
        + Last-P20-verified sweep + promote M-self-audit +
        M-self-application to full M-rules + t7 KG proposal +
        t8 snapshot proposal (commits 00fd258 → c296cef)
      See `git log 78e6b78..c296cef` for full hash list.
      Drives OPERATING_RULES.md from 4 to 9 rules (canonical
      7 + meta 2).
- [x] **Orphan-reference cleanup batch (7 commits, 2026-07-13/14)**
      — 5 follow-up items identified by user audit "对比你
      最后一个版本的文档和现在的文档，看看现在是否在正确
      的路上".  Sub-batches:
      - 1-5 (commits 95097fb, c2266ee, 90cbecf, 79eb741,
        a343373, a66b789): unify cross-skill references to
        "agent-onboarding skill, references/..." format +
        fix misattributed M_SELF_AUDIT line 23 + update
        workflow-rules batch entry (8 → 20) + mark
        60-70% claim unverified + remove stale TODO +
        slim M-self-audit inline段 to pointer
      - 6-7 (commits c414821 + parent verification):
        M-task-summary per SUMMARY_LIFECYCLE contract
      See `git log c414821~1..c414821` for the batch.
      Fixed: 4 doc drift issues + 1 misattribution + 1
      stale TODO + 1 inline duplication.
- [x] **EXTENSIONS.md X2 consolidation (4 commits, 2026-07-14)**
      — register X2 = agent-onboarding skill in
      `docs/EXTENSIONS.md` (per P21 cross-project independence);
      consolidate 5 scattered cross-skill references to
      EXTENSIONS.md X2 pointer.  Sub-batches:
      - 1 (commit 31ea3ce): X2 entry + Status "active" +
        location uses text reference (per R8)
      - 2 (commit 3b711af): inline 1-sentence AGENTS.md cap
        rationale in M_SELF_AUDIT.md line 23 + remove
        1 weak ref
      - 3 (commit bfeb185): consolidate 4 weak refs in
        M_SELF_APPLICATION.md / TODO_KNOWLEDGE_LIFECYCLE.md /
        TODO_SESSION_PERSISTENCE.md / TODO_SESSION_PERSISTENCE_DETAIL.md
      - 4 (commit e7a0c1f + parent verification):
        M-task-summary per SUMMARY_LIFECYCLE contract
      After: 0 scattered "agent-onboarding skill" refs;
      all cross-project pointers go through EXTENSIONS.md X2.
- [x] **Switch action protocol batch (2 commits, 2026-07-14)**
      — codify what to do when a switch signal fires.
      Triggered by user audit: "有的时候我在你子任务之间
      插入一个新任务，你好像把这个新任务直接作为子任务
      了" (real failure: 2026-07-13 session merged switch
      task into existing batch, leaving workflow-rules
      batch without its own parent verification).
      Sub-batches:
      - 1 (commit 05312d2): SWITCH_SIGNALS.md append
        "Switch action protocol" 段 (3-case decision tree
        + 3 anti-patterns + real-failure-case citation) +
        AGENTS.md add 1-sentence per-message-load trigger
      - 2 (commit b6adb74 + parent verification):
        M-task-summary per SUMMARY_LIFECYCLE contract +
        explicit fresh-agent simulation audit (per user
        TODO "对整个文档问一下新agent是否会按照我们想的
        规范自己行为")
      See `git log b6adb74~1..b6adb74` for the batch.
      Drives: SWITCH_SIGNALS.md 86 → 138 lines; AGENTS.md
      "Read first" pattern extended for switch signals.

## In progress (current 1-2 sessions)

### Lessons learned (per commit 28, 2026-07-14)

Per user audit "犯错时明确 root cause + 多一个案例
更好判断".  Three real errors observed this session;
root causes identified below.  **Status: tracked but
not yet codified into rules** — per M_RULE_AUTHORING
3-condition gate ("3+ observed"), 1 occurrence each
is not yet rule-worthy.  Future session: if a 2nd
similar error is observed, promote each to a rule.

- **T-001 **Partial-verify bias****: only verified
  the named follow-ups (F1 + F11 in commit 21),
  missed sibling P14 drift entries (3 more found
  in commits 23/26 verify).  Root cause: focused on
  the listed, didn't sweep same-pattern.
  **Codify trigger**: 2nd occurrence observed →
  add M-self-audit step 7 "sweep for siblings".

- **T-002 **Follow-up category confusion****: in
  commit 27 parent verification, wrote 4 follow-ups
  to commit message body only, **didn't propagate
  to TODO.md** (FU1/FU2/FU3 undiscoverable to fresh
  agents).  Root cause: conflated follow-ups with
  child summaries (destroy-after-consumed) when
  they should be tracked-in-TODO (publish-and-track).
  **Codify trigger**: 2nd occurrence observed →
  add M-task-summary "follow-up propagation
  contract"段.

- **T-003 **Deferred-but-not-tracked****: in commit
  26, said "TASK_TREE.md trigger fires → deferred"
  in commit message, but didn't add a TODO entry
  with `[deferred]` status.  Root cause: "deferred"
  was mental state (commit body), not durable state
  (TODO entry).
  **Codify trigger**: 2nd occurrence observed →
  add `[deferred]` status to TODO.md convention段
  (so deferred is first-class state, not comment).

- **T-004 **Track TASK_TREE.md trigger condition** (FU1
  from commit 27)**: per M-add-then-reduce signal-
  trigger design, multi-layer recursion triggers
  creation of TASK_TREE.md.  Currently deferred but
  not tracked as a TODO entry.  **Fix**: this entry
  IS the tracking; when trigger fires (a session
  faces multi-layer recursion), open T-004.1 sub-task
  to create TASK_TREE.md.  Otherwise: leave dormant.

- **T-005 **Commit 23 withdrawal formal note** (FU2
  from commit 27)**: commit 23 (.gitattributes +
  CRLF normalization) was withdrawn mid-edit because
  autocrlf artifact can't be fixed by commit (per-repo
  config required).  Working tree verified clean.
  **Fix**: add a 1-line entry to DONE.md recording
  this withdrawn commit's reasoning, so future agents
  reading git history can trace why commit 23 was
  withdrawn.  Optional but recommended for P14.

### v3.0.3 — autonomous daily loop (LITERATURE: Self-Harness "iterative
re-plan", Lilian Weng "harness as important as model")

Per user 2026-07-10: '我希望这个项目之后可以自己独立运行'.

- [ ] **step 1** — `python -m self_upgrade improve --multi --count 5`
      data: 1/5 KEPT (20%, n=5, commit `20e958d`).  Need 10+ runs.
- [ ] **step 2** — Decide `core/planner.py` (LLM Round 5 KEPT added
      `generate_tests` option).  User decides keep or revert.
- [ ] **step 3** — `python -m self_upgrade daily-loop --interval 24h`
      (autonomous vision, not user-triggered).
- [ ] **step 4** — state.json persistence (P19) + failure recovery
      (P18) + self-test gate.
- [/] **step 5** — Doc organization: L0/L1/L2 structure (per
      user 2026-07-10 '按你认为正确的思路整理文档').
      Now: all 17 docs have L0 header.  TODO: split
      DONE.md if > 7KB, archive CONSTRAINTS_DETAIL > 7KB.
- [/] **step 6** — Knowledge graph integration (TODO那条).
      Per user 2026-07-11 '按计划继续推进': seed project
      `../knowledge-graph-seed` now has minimal `src/kg.py`
      stub (per SEED.md, commit 4c79bbb).  Spec exists.
      Next sub-tasks: SEED.md 3 acceptance questions (graph
      can answer Q1/Q2/Q3).  See TODO_KNOWLEDGE_GRAPH.md +
      SEED.md + SEED_DETAIL.md (in ../knowledge-graph-seed/).

## Backlog (NOT in current session, recorded per user principle)

Per user 2026-07-10: '你认为有必要, 例如我说的内容属于附加功能时,
可以作为 TODO 记录下来, 这时候要整理文档'.

### Cleanup (low risk, 1 commit each, optional)

- [x] **AGENTS.md Read-first promotion for SWITCH_SIGNALS.md**
      (per commit b6adb74 follow-up #4): the per-message
      load trigger added in commit 05312d2 is sufficient
      for now, but SWITCH_SIGNALS.md is becoming a
      "must-consult-before-each-response" doc.  Consider
      promoting to "Read first" with size justification,
      OR add a meta-trigger in the "always-load" pointer
      list.  Defer until signal triggered (e.g.
      SWITCH_SIGNALS.md > 300 lines, or fresh-agent
      simulation fails without promotion).
- [ ] 删 6 个 v1.8.x files still referenced by tests + docs
      (`run_1round.py`, `run_3rounds_manual.py`, `run_stable.py`,
      `collect_papers.py`, `PROJECT_BRIEF.md`, `ISSUES.md`).
      Done in v3.0.2 follow-up #4: 删了 3 个 truly unused
      (`IDEA.md`, `run.py`, `run_5rounds_day6.py`).
- [ ] Update LITERATURE.md with better notes on 11 papers
      (per user 2026-07-10 "灵活运用 agent 知识").
- [x] Delete `docs/USER_INSIGHTS_KNOWLEDGEGRAPH_20260710.md`
      (transient note, content now in PRINCIPLES / OBSERVATIONS).
      **Done in prior session (file no longer exists); TODO
      entry mark [x] per P14 docs-stay-current.**
- [ ] **P19 + M-task-summary destroy contract cross-ref**
      (per M-learn from 2026-07-13 batch): P19 says "persist
      intermediate"; destroy contract says "destroy intermediate
      after consume".  These are complementary (add-phase vs
      reduce-phase), not contradictory.  Add 1-line cross-ref
      in PRINCIPLES.md P19 实操 → OPERATING_RULES.md
      M-task-summary destroy contract.
- [ ] **OPERATING_RULES.md split candidate**: file is 310
      lines (exceeds 300-line soft cap).  "Child-summary destroy
      contract" sub-section is a candidate to move to dedicated
      docs/SUMMARY_LIFECYCLE.md if file grows past 350 lines.
      Defer until then.
- [x] **Resolve orphan M-self-audit + M-self-application**
      cross-ref (per AGENTS.md "orphan-note" + commit `51638b1`):
      AGENTS.md referenced these as if they were full M-* rules
      in OPERATING_RULES.md, but OPERATING_RULES.md didn't contain
      them.  **Resolved via inline-reminder pattern** (commit
      final batch): AGENTS.md now describes both as inline
      reminders (honest about not being full rules); 7-rule list
      in OPERATING_RULES.md pointer updated to match actual
      contents.  See git log for the commit.

### User-side (you run)

- [ ] 5+ consecutive multi-paper rounds stability test
      New CLI: `python -m self_upgrade improve --multi --max-retries 2 --count 5`
- [ ] Verify unified CLI works: `python -m self_upgrade improve --help`

### Future (v3.1+ or v4+)

- [ ] 真实 daily loop (cron job)
- [ ] A/B benchmark (新 patch vs 旧)
- [ ] bootloader 风格 atomic 切换 (你 vision 起点)
- [/] Skill registry (per LITERATURE: SkillOpt) — step 1/3 done (metadata, commit `e65ba25`)
- [/] Knowledge graph (per docs/TODO_KNOWLEDGE_GRAPH.md) — see in-progress step 6 above
- [ ] Session persistence (per docs/TODO_SESSION_PERSISTENCE.md) —
      proposal written 2026-07-13 (commit pending).  M-context-
      snapshot rule is mature (3 places); this doc captures
      design for snapshot format + restore protocol + lifecycle.
      Implementation deferred (proposal-only).
- [ ] Knowledge lifecycle (per docs/TODO_KNOWLEDGE_LIFECYCLE.md) —
      PROPOSAL WRITTEN 2026-07-13 (commit pending).  Design
      covers: priority scoring (4-component composite),
      3-tier pruning (active/stale/dead), search bypass
      (top-N by priority).  Implementation deferred (KG
      frozen; last activity 2026-07-13).

## Lesson (per P19 + LITERATURE)

- Signal-to-Fix Loop (Droid 2026): telemetry → signal → fix → deploy
  我们 = progress markers (signal) → commit (fix) → user run (deploy)
- SkillOpt (Microsoft 2026): skills as external state
  我们 = failures.jsonl / judge_*.jsonl 作为 truth
- P19 data flow observability: persist intermediate results
  step 1.3 (save_summaries + save_decision) 已实现
- Self-Harness (40→62%): harness > model.  v3.0.2 implements this
  via Thinker+Executor+Loop.  v3.0.2 follow-up #6 unifies CLI
  with `--multi --max-retries --count` flags.
