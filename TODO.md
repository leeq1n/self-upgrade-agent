# TODO — Pending Tasks

Each task is a checkbox.  To claim: change `[ ]` to `[x]` and move
the line into DONE.md.  Keep this list SHORT and CURRENT; older
completed work lives in DONE.md.

> Convention: `- [ ]` = not started, `- [x]` = done, `- [/]` = in progress.

## High priority (block v2.x → v3.0)

- [ ] **Multi-paper reading** — read 5+ more papers on agent self-improvement,
  innovation extraction, multi-agent selectors.  Goal: inform v3.0 design
  for multi-paper selection.  See [TODO references](#todo-references).

- [ ] **Failure → regression test pipeline** — every NO_PATCH /
  APPLY_FAILED / REVERTED outcome must become a permanent regression
  test.  This is the highest-impact single change per production
  agent literature ("[every failure becomes a test][postsyntax]").
  Implementation: append to history.db or a separate `failures.jsonl`,
  and add a test that re-runs the same paper+target combo and asserts
  the failure mode no longer occurs (or records that it still does).

- [ ] **5 consecutive KEPT rounds** — run run_one_round 5 times in a row
  with the same paper (FIXED_PAPER=DyLAN).  Goal: prove the self-improving
  loop is stable, not just one-shot lucky.  User to run (requires real
  LLM time).

## Medium priority (v3.x features)

- [ ] **Think-execute harness** for LLM-as-deep-thinker (per user
  2026-07-08).  Uses strong model for planning, light model for
  execution.  See [TODO references](#todo-references).

- [ ] **Multi-paper selection** — extend FIXED_PAPER (single paper) to a
  paper pool + LLM-driven selection.  Per user: "规划属于思考, 查询和
  更新记忆属于执行".  See [TODO references](#todo-references).

- [ ] **Skip-execute-on-decision** optimization — think layer can
  short-circuit execute to save tokens.  Per user: "放在更后面做实验
  验证".  OPTIONAL / experimental.

- [ ] **Decision logging** — persist RoundResult to a database for
  audit + analysis.  Schema defined already (RoundResult dataclass).

## Cleanup (奥卡姆)

- [ ] **Delete deprecated `src/pipeline_lg.py` and 7 sibling files**
  once v2 is verified stable.  Listed in PROJECT_STATE §3.

- [ ] **Consolidate remaining 4 docs** into a single index.  Current
  state: `PROJECT_STATE.md` is the parent; the other 3 should each be
  §X with a 1-paragraph summary + link.  (See docs/INDEX.md once
  written.)

## TODO references

For the full paper notes, see [docs/LITERATURE.md](docs/LITERATURE.md)
and [docs/LITERATURE_DETAIL.md](docs/LITERATURE_DETAIL.md).

- [postsyntax]: production failures → regression test pattern.
  https://postsyntax.substack.com/p/the-agent-improvement-loop-turning
- [user-2026-07-08]: Multi-paper reading + think-execute + multi-paper
  selection are deferred until fixed-paper loop is verified end-to-end.
- [user-2026-07-08-docs]: docs should be "摘要+引用" pattern, not
  long-form essays.  See [docs/INDEX.md](docs/INDEX.md) for navigation.
- [user-2026-07-08-project-knowledge]: knowledge from papers belongs
  in the project (LITERATURE.md), not in agent memory.  Future agents
  should read LITERATURE_DETAIL.md to learn what we already know.
