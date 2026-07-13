L0: Pending tasks — backlog of next-up features.  Done items live in DONE.md.
Last P20-verified: 2026-07-13

# TODO —

Each task is a checkbox.  To claim: change `[ ]` to `[x]` and move
the line into DONE.md.  Keep this list SHORT and CURRENT; older
completed work lives in DONE.md.

> Convention: `- [ ]` = not started, `- [x]` = done, `- [/]` = in progress.

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
- [x] **Workflow-rules batch (8 commits, 2026-07-13)** — added
      M-intent-parsing + M-learn + M-add-then-reduce +
      RECURSIVE_DECOMPOSITION layer-N context flow + COMMON_PITFALLS
      3-way table + AGENTS trigger surface + L0 invariant reminder.
      See `git log 78e6b78..HEAD` for full hash list.  Drives
      OPERATING_RULES.md to 7 rules; RECURSIVE_DECOMPOSITION.md to
      6-step loop; COMMON_PITFALLS.md §4 to 3-way table.

## In progress (current 1-2 sessions)

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

- [ ] 删 6 个 v1.8.x files still referenced by tests + docs
      (`run_1round.py`, `run_3rounds_manual.py`, `run_stable.py`,
      `collect_papers.py`, `PROJECT_BRIEF.md`, `ISSUES.md`).
      Done in v3.0.2 follow-up #4: 删了 3 个 truly unused
      (`IDEA.md`, `run.py`, `run_5rounds_day6.py`).
- [ ] Update LITERATURE.md with better notes on 11 papers
      (per user 2026-07-10 "灵活运用 agent 知识").
- [ ] Delete `docs/USER_INSIGHTS_KNOWLEDGEGRAPH_20260710.md`
      (transient note, content now in PRINCIPLES / OBSERVATIONS).
      Will be done in docs cleanup commit.
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
