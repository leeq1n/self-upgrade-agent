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

- [x] **Run replay_all_failures() on the real `upgrades/failures.jsonl`**
  — DONE in v2.3.2 (commit `9ea2b5e`).  See
  `python -m self_upgrade replay` (unified CLI).  Reported
  now_passes=4, still_fails=18 from the existing log.

- [ ] **Run 5 consecutive KEPT rounds** (still pending real LLM
  data).  The first 3 rounds in v2.3.2 showed: 1 KEPT, 2 NO_PATCH.
  Pattern: LLM temperature is non-zero; sometimes valid patch,
  sometimes bad parse.  Loop is working; need either more rounds
  or a prompt fix.  Use: `python -m self_upgrade test-scale 5`.

## v2.4.0 — CLI consolidation (current commit)

- [x] **Unified CLI** — `python -m self_upgrade` is the single
  entry point.  Replaces:
    - `python -m self_upgrade` (v1.8.x unified CLI, backed up
      in __main__.v18_backup.py)
    - `scripts/run_5_rounds.py` (v2.3.2)
    - `scripts/run_replay.py` (v2.3.2)
    - `scripts/_self_check_run_replay.py` (v2.3.2)
    - `scripts/start_llama_servers.sh` (v1.8.x, deleted)
  Subcommands: `improve`, `replay`, `test-scale N`.  Click-based.

- [x] **Deleted obsolete tests** — removed test_unified_cli.py
  (v1.8.x), test_gc.py (v1.8.x gc subcommand), test_audit_cli.py
  (v1.8.x audit subcommand).  Replaced test_start_llama_servers
  and test_gc_command with v2.x equivalents.

- [x] **Updated test_v181_features.py** — replaced
  test_gc_command_supports_memory_policy_flag and
  test_start_llama_servers_script_exists with
  test_cli_has_three_subcommands and test_no_legacy_scripts_directory.

- [x] **Added tests/test_v2_cli.py** (9 tests) — Click group
  structure, subcommand help, lazy import speed.

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

## v2.4.1 — Gitignore cleanup (current commit)

- [x] **Removed upgrades/* runtime artifacts from git** —
  20 files (JSONL, .db, .json) were accidentally committed
  via `git add -A` in v2.4.0.  This commit:
    - `git rm --cached -r upgrades/` (files still on disk)
    - Added `upgrades/*` catch-all to `.gitignore`
    - 1 commit, 21 files (1 modify + 20 delete)

Lesson (per P17 honest reporting): `git add -A` is too
permissive.  Future commits should use `git add <file>` or
`git add -u`.

Status: working tree fully clean.
