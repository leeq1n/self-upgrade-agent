L0: Done-stage-gates summary — last ~30% of stage gates. Older history in docs/archive/DONE_HISTORY.md (per P11 摘要+引用 + P20 R5; per c76 another round of archiving).
Last P20-verified: 2026-07-14 (per c76 + per existing archive mechanism)

# DONE — Completed Work (one line per item)

When you finish a TODO, move it here.  Each entry: one line + key commit.

> **Larger history (v1.8.x — v3.0.2 follow-up #5)** archived to
> `docs/archive/DONE_HISTORY.md` per P11 + P20 R5 (≤ 7KB per file).
> Recent stage gates (v3.0.2 follow-up #6 onwards) shown below.

---



---

## fix: plan_task persist parameter (per P18, pre-existing test bug fixed)

Per user 2026-07-11 '继续推进' (16th push).
Per 自上而下/分治 + 你 '排除bug' push (transparent disclosure = action):

Per P18: failure → regression test.
Per pre-existing test bug from 747d96e.

This commit:
- core/planner.py: plan_task accepts persist (default True)
- 179/179 combined tests PASS
- 2 previously-failing tests now PASS

Per 你 '排除bug': action over words.
Per LITERATURE: minimal, additive (backward compatible).




---

## fix: cron subcommand CLI wiring (per P18, user-reported bug)

Per user 2026-07-11 'python -m self_upgrade cron --install' failed with 'No such command cron'.
Per 你 '排除bug' push.

Per P18: failure → regression test.

This commit:
- self_upgrade/__main__.py: cron subcommand wired (--show, --install, --apply, --cron-expr)
- tests/test_cron_cli.py (5 tests)
- 184/184 combined tests PASS

Per LITERATURE: real bug, real fix.
Per P9: dry_run=True by default (safe).
Per 你 '排除bug': action over words.




---

## fix: install_cron actually executes (per P18, 你 2nd bug report)

Per user 2026-07-11 'python -m self_upgrade cron --install --apply' did not execute.
Per 你 '排除bug' push (2nd bug today).

Per P18: failure → regression test.

This commit:
- src/os_cron_installer.py: subprocess.run(install_cmd) when dry_run=False
- self_upgrade/__main__.py: shows register result (SUCCESS/FAILED)
- tests/test_cron_install_apply.py (3 tests)
- 187/187 combined tests PASS

Per P9: subprocess.run with timeout=30.
Per LITERATURE: real subprocess integration.
Per 你 '排除bug': action over words.




---

## chat subcommand (per 你 vision '其他agent产品')

Per user 2026-07-11 '好, 继续推进' + '像其他agent产品一样' push.

Per 你 vision 2026-07-08:
- 真 autonomous (cron) ✓
- Interactive chat (this commit) ✓
- 真 'real agent product'

This commit:
- src/chat_repl.py (~150 lines)
  - load_history / save_message
  - build_messages_prompt / format_chat_response
  - chat_repl (REPL with mocked or real LLM)
- self_upgrade/__main__.py: chat subcommand wired
- tests/test_chat_repl.py (11 tests)
- 198/198 combined tests PASS

Per P19: cross-session memory via JSONL file.
Per LITERATURE: minimal, 奥卡姆.




---

## chat streaming (sub-task 2/3)

Per user 2026-07-11 '好, 继续推进'.
Per 自上而下/分治 + 你 '不要给那么多选项' = push my recommendation.

Per 你 vision 'real agent product':
- Sub-task 1 done (chat REPL)
- Sub-task 2 done (streaming) — this
- Sub-task 3 pending (tool use)

This commit:
- src/chat_repl.py: stream_response + chat_repl_streaming
- self_upgrade/__main__.py: --stream flag
- tests/test_streaming.py (3 tests)
- 201/201 combined tests PASS

Per LITERATURE: minimal, additive, graceful fallback.
Per 你 vision: token-by-token display = 真 achieved.




---

## fix: _parse_patch markdown fence fallback (per P18, 你 0/10 KEPT bug)

Per user 2026-07-12 '修复' + 10 rounds 0/10 KEPT reproduction.
Per 你 '排除bug' push (action over words).

Per P18: failure -> regression test.

This commit:
- src/v2_agent.py: _parse_patch rewritten with 2 strategies
  1. JSON parse (backward compatible)
  2. Fallback: ```python fence extraction (the bug case)
- tests/test_parse_patch_regression.py (6 tests)
- 207/207 combined tests PASS

Per LITERATURE: real bug, real fix.
Per P9: real reproduction verified.




---

## fix: _parse_patch target_module fallback (per P18, 2nd '排除bug')

Per user 2026-07-12 '如果有已知bug, 那就修复' + 10 rounds 0/10 KEPT again.
Per 你 '排除bug' push (2nd round).

Per P18: failure -> regression test.

This commit:
- src/v2_agent.py: _parse_patch signature + target_module fallback
- tests/test_parse_patch_module_fallback.py (4 tests)
- Real LLM end-to-end verified: Patch EXTRACTED ✅

Per LITERATURE: real bug, real fix, real LLM verification.
Per P17 honest: first fix (004f47b) was INSUFFICIENT; this is the real fix.




---

## 2026-07-14 — Doc cleanup session (27 commits, summary)

Per user audit "对比你最后一个版本的文档和现在的文档" +
multiple session extensions (follow-ups, design filtering,
verify-before-edit, follow-up tracking).  27 commits across
7 batches (orphan-reference cleanup → EXTENSIONS.md X2 →
switch action protocol → follow-ups cleanup → verify-before-
edit → follow-ups + design filtering → follow-up tracking
fix).  Full batch summary in `git log c8efd26~1..HEAD~1` (parent
verification commits).

**Withdrawn commit (commit 23)**: planned as `.gitattributes` +
CRLF normalization (2 files: INDEX.md, EXTENSIONS.md), but
verify revealed autocrlf artifact can't be fixed by commit
(per-repo `core.autocrlf` config required).  Working tree
verified clean (4/4 PASS via hermes-verify-sua-c23-withdraw
script, since cleaned up).  Commit withdrawn mid-edit, no
git history residue.

**Key principles applied** (per M-self-application 4-level L4):
verify-before-edit (P-n vs M-* boundary), design filtering
(TASK_TREE.md rejected for 4+ principle violations), follow-up
tracking (3 root-causes tracked as TODO T-001/T-002/T-003).

Per P17: this summary is ad-hoc; future session should not
re-do this work.
