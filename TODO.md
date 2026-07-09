# TODO — Pending Tasks

Each task is a checkbox.  To claim: change `[ ]` to `[x]` and move
the line into DONE.md.  Keep this list SHORT and CURRENT; older
completed work lives in DONE.md.

> Convention: `- [ ]` = not started, `- [x]` = done, `- [/]` = in progress.

## High priority (next 1-2 sessions)

- [x] **Failure → regression test pipeline** — DONE in v2.3
  (commit `0dc68cb`).  Every NO_PATCH / APPLY_FAILED / REVERTED
  outcome is logged to `upgrades/failures.jsonl`.  See
  [src/failures.py](src/failures.py) and
  [tests/test_v2_failures.py](tests/test_v2_failures.py).
  The replay mechanism is implemented (`replay_one`) but no
  automatic replay loop yet — that's a future v2.3.x addition.

- [x] **Automatic replay of failure log** — DONE in v2.3.1
  (commit `216f7e0`).  See `replay_all()` in [src/failures.py](src/failures.py)
  and `replay_all_failures()` driver in [src/v2_round.py](src/v2_round.py).
  The P18 loop is now closed: log on failure + replay the log.

- [ ] **5 consecutive KEPT rounds** — run run_one_round 5 times in a row
  with the same paper (FIXED_PAPER=DyLAN).  Goal: prove the self-improving
  loop is stable, not just one-shot lucky.  User to run (requires real
  LLM time).

- [ ] **Run replay_all_failures() on the real `upgrades/failures.jsonl`**
  — see which historical failures still recur vs which now pass.
  User to invoke after the LLM is available.  This is the
  first time the P18 loop runs on real data.

## Medium priority (v3.x features)

- [ ] **Multi-paper reading** — read 5+ more papers on agent self-improvement,
  innovation extraction, multi-agent selectors.  Goal: inform v3.0 design
  for multi-paper selection.  Update [docs/LITERATURE.md](docs/LITERATURE.md).

- [ ] **Think-execute harness** for LLM-as-deep-thinker (per user
  2026-07-08).  Uses strong model for planning, light model for
  execution.

- [ ] **Multi-paper selection** — extend FIXED_PAPER (single paper) to a
  paper pool + LLM-driven selection.  Per user: "规划属于思考, 查询和
  更新记忆属于执行".

- [ ] **Skip-execute-on-decision** optimization — think layer can
  short-circuit execute to save tokens.  Per user: "放在更后面做实验
  验证".  OPTIONAL / experimental.

- [ ] **Decision logging** — persist RoundResult to a database for
  audit + analysis.  Schema defined already (RoundResult dataclass).

## Cleanup (奥卡姆)

- [ ] **Delete deprecated `src/pipeline_lg.py` and 7 sibling files**
  once v2 is verified stable.  Listed in [PROJECT_STATE_DETAIL.md §Deprecated](docs/PROJECT_STATE_DETAIL.md#deprecated-modules).

- [ ] **Run real end-to-end with new shorter prompt** — verify the
  prompt-as-interface refactor (commit `19ebf8b`) didn't break real
  LLM output.  User to run.

## TODO references

For the full paper notes, see [docs/LITERATURE.md](docs/LITERATURE.md)
and [docs/LITERATURE_DETAIL.md](docs/LITERATURE_DETAIL.md).

For the project's working principles (not task-specific), see
[docs/PRINCIPLES.md](docs/PRINCIPLES.md).

- [postsyntax]: production failures → regression test pattern.
  https://postsyntax.substack.com/p/the-agent-improvement-loop-turning
- [user-2026-07-08]: Multi-paper reading + think-execute + multi-paper
  selection are deferred until fixed-paper loop is verified end-to-end.
- [user-2026-07-08-docs]: docs should be "摘要+引用" pattern, not
  long-form essays.  See [docs/INDEX.md](docs/INDEX.md) for navigation.
- [user-2026-07-08-project-knowledge]: knowledge from papers belongs
  in the project (LITERATURE.md), not in agent memory.  Future agents
  should read LITERATURE_DETAIL.md to learn what we already know.
- [user-2026-07-08-principles]: working principles (整理→思考→行动,
  单元→联合→集成, 摘要+引用, etc.) are extracted into PRINCIPLES.md
  so they survive across projects.