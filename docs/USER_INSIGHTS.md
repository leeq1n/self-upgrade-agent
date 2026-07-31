L0: User intent summary — paraphrased rules from past sessions.
Last P20-verified: 2026-07-13

---
description: "User's vision and feedback (verbatim excerpts)"
status: "summary"
---

# USER_INSIGHTS — brief
> L0: User's preferences + working style.  Load when: calibrating responses to user.

User's original goal (paraphrased): a self-improving agent that
reads papers, modifies code, validates via harness, keeps
improvements.  Stability + bloat-control over time, not point
estimates.

**Most-cited constraints from user feedback (2026-07-08)**:

- 奥卡姆剃刀: fewer rules, not more; minimal agent first
- fail-OPEN: pre-filters must let LLM decide, not keyword-match
- 整理 → 思考 → 行动: organize first, then design, then code
- 搜资料, 不拍脑门: read literature before designing
- 1 commit per logical feature (multi-file OK), not per-file
- unit → joint → 端到端测: small to large
- 测通再 commit: run real path before commit
- user edits .env keys, agent doesn't
- pre-run 不要 gc, post-run 只归档 (don't delete logs)

**Most-cited workflow rules from user feedback (2026-07-08)**:

- 完整跑过一次再 "v3.x" features
- 失败 mode 进了 memory
- Multi-paper reading 优于单 paper guessing
- Think-execute harness 是未来 (deep thinker + light executor)
- 规划属于思考, 查询/更新记忆属于执行
- 环境查询 = 记忆查询 (同类)
- Skip-execute 是优化, 实验性, 后续做
- (parenthetical) future work goes in TODO.md; cross off as done;
  move to DONE.md

Full verbatim quotes (long form) are in
[`USER_INSIGHTS_DETAIL.md`](USER_INSIGHTS_DETAIL.md).

## References

- INDEX: [INDEX.md](INDEX.md)
- Project state: [PROJECT_STATE.md](PROJECT_STATE.md)
- Constraints (hard rules): [CONSTRAINTS.md](CONSTRAINTS.md)
- LLM choice: [MODEL_STRATEGY.md](MODEL_STRATEGY.md)
- Pending tasks: [../TODO.md](../TODO.md)
- Done tasks: [../DONE.md](../DONE.md)
- Full quotes: [USER_INSIGHTS_DETAIL.md](USER_INSIGHTS_DETAIL.md)
