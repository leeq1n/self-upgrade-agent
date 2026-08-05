# TODO — Detail (L2)

> L0: L2 detail for `TODO.md`.  Per P11 摘要+引用 + R6, this companion holds Completed + In progress + Backlog + Lesson sections.

---

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
        M_SELF_APPLICATION.md / TODO_SESSION_PERSISTENCE.md /
        TODO_SESSION_PERSISTENCE_DETAIL.md
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


## Detail (per R6)

> L0: Per P11 摘要+引用 + R5, this L0/L1 summary (≤ 7KB).  Detail in `TODO_DETAIL.md`.

## See also

- `TODO_DETAIL.md` (L2 companion: In progress + Backlog + Lesson)
