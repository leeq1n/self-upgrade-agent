# Self-Upgrade Agent (SUA)

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-orange.svg)](CONTRIBUTING.md)
[![AAIF Compatible](https://img.shields.io/badge/AAIF-AGENTS.md%20compatible-blueviolet)](AGENTS.md)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-open%20standard%202025--12--18-success)](docs/CROSS_RUNTIME_SKILL_BRIDGE.md)

> L0: SUA project README — orientation, current state.
> SUA is an **agent discipline knowledge library** — agent
> behavior rules, reasoning primitives, and operating principles
> that you can carry into any agent runtime.

## What is SUA?

SUA packages three categories of agent knowledge:

1. **Agent behavior rules** — working principles and operational
   rules that any agent on this contract should follow.
2. **Reasoning primitives** — critical/constructive thinking
   primitives used to evaluate and build.
3. **Operating conventions** — how a new agent onboards, how
   commits are structured, how rules evolve.

The agent reads these on session start and uses them to constrain
its behavior.

## Quick start (new agent)

1. Read `AGENTS.md` (operating rules)
2. Read `docs/HOW_TO_READ_GRAPH.md` (3-step read pattern)
3. Read `docs/HANDOFF.md` (project-specific onboarding)
4. Read `docs/PROJECT_STATE.md` Goal section (current state)
5. Read `docs/PRINCIPLES.md` (L0 + L1 layer only)
6. Optional: `docs/SKILL_DESIGN.md` (if designing or
   incubating a new skill)

Total: ~30 min onboarding.

**For non-canonical runtimes** (Cursor / Codex / Antigravity
that prefer the Agent Skills `SKILL.md` format, or stateless
sessions that need a one-line entry point), see
[`docs/CROSS_RUNTIME_SKILL_BRIDGE.md`](docs/CROSS_RUNTIME_SKILL_BRIDGE.md).
The bridge is a convenience layer; the 6-step workflow above is
the canonical SUA onboarding.

### What the agent gets

- `AGENTS.md` — operating rules (always-loaded contract)
- `core-layer/AGENTS_CORE.md` — cache-stable subset (~10 KB)
- `agent-tools/scripts/` — self-audit + verification tooling
  (self_health_check, validate_links, validate_structure,
  token_budget, cross_repo_audit, run_acceptance)

The agent reads these on session start. You only need to point
it at the directory once.

## Working principles (P-n) + workflow (M-n)

See `docs/PRINCIPLES.md` (P1-P29 working principles, with
P1-P30 referenced across docs). The commit-message hook
enforces P-n cite in commit messages.

See `docs/OPERATING_RULES.md` (M-* operating workflow rules:
M-task-summary, M-must-read, M-context-snapshot,
M-subtask-summary, M-intent-parsing, M-learn,
M-add-then-reduce, M-self-audit, M-self-application).

## Contributing

Contributions should follow the operating rules in `AGENTS.md`.
The commit-message hook enforces that every commit message
follows the contract.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the contribution
workflow and acceptance protocol.

## Detailed content (L2)

For full project history, CLI documentation, code architecture,
version history, and other L2 detail, see
[`README_DETAIL.md`](README_DETAIL.md). Per the R6 split rule,
this companion is required when the README exceeds 7 KB.

## Code legacy

This project was originally a self-improving agent that modifies
`core/planner.py`. The code still exists and is functional, but
is no longer the project's focus. For code documentation and CLI
usage, see `README_DETAIL.md` § Code legacy.

## Changelog

For the full history of SUA development, see
[`CHANGELOG.md`](CHANGELOG.md).

## Code of conduct

Participation in this project is governed by the
[Contributor Covenant](CODE_OF_CONDUCT.md), version 2.1.

## License

This project is licensed under the [MIT License](LICENSE)
(c) 2026 LiQin.

## Status

This repo is the default direct-use path: clone it into your
project, point your agent at `AGENTS.md`, and the agent absorbs
the operating contract on session start.

## Install

**Clone 用法（推荐，任何 agent 通用）**: SUA 不需要"安装"，
直接放进项目目录即可：

```bash
# 在你的项目里 (如科研项目 satellite-security/)
git clone https://github.com/leeq1n/self-upgrade-agent.git .sua/

# 对 agent 说：用 .sua/ 约束你的行为
# agent 自动读 .sua/AGENTS.md + core-layer/AGENTS_CORE.md
```

**跨 agent 使用教程**：

| Agent | 用法 |
|---|---|
| **Hermes / Cursor** | 项目内 clone `.sua/`，agent 自动读 AGENTS.md（本 README Quick start 6-step） |
| **Codex / Claude Code / Antigravity** | 见 [`docs/CROSS_RUNTIME_SKILL_BRIDGE.md`](docs/CROSS_RUNTIME_SKILL_BRIDGE.md)（Agent Skills `SKILL.md` 格式桥接） |
| **任意 stateless 会话** | 用 bridge 的 system-prompt 注入方式 |
| **科研项目** | 见 [`docs/RESEARCH_USAGE.md`](docs/RESEARCH_USAGE.md)（适配器模式 + 工作流） |

**Hook 安装（可选）**: 想让 SUA 的 commit-msg / pre-commit
等 hooks 在你的项目生效。**一条命令**（hooks + 依赖自动
处理，目标项目零污染 — 不会出现 `agent-tools/` 目录）：

```bash
# macOS / Linux / Git Bash:
bash .sua/install-hooks.sh

# Windows (cmd / PowerShell，无需 bash):
.sua\install-hooks.bat
# 或双击 install-hooks.bat
```

覆盖已存在的 hooks 加 `--force`；预览加 `--dry-run`。

> 注：install-hooks.sh / .bat 会把 hook 内的脚本路径重写
> 到 SUA clone 内部（`.sua/agent-tools/scripts/`），你的项目只
> 增加 `.git/hooks/` 条目，不产生任何 `agent-tools/` 目录（对
> codex / claude 等 agent 友好）。Windows 下 .bat
> 自动定位 git 自带的 bash 并处理路径转换（cygpath）。

## Uninstall

**Clone 用法（推荐）**: SUA 通过 `git clone` 放进项目目录，
移除 = 删除 `.sua/` 目录即可（无残留，因为 clone 不改动
项目自身的 git hooks）。

**Hook 安装用法**: 仅当你用 install-hooks.sh 安装过 hooks，
才需要清理：

```bash
# 移除 hooks（目标项目没有 agent-tools/，无需清理其他）
rm .git/hooks/commit-msg .git/hooks/pre-commit .git/hooks/prepare-commit-msg .git/hooks/pre-push
```
