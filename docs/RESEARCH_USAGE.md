# Research Usage Guide — 用 SUA 辅助科研

> Per user 2026-07-31 评估 request (项目使用方式 + 卫星安全
> 科研场景). This guide shows how a research project (e.g.,
> satellite security / CCSDS protocol security) uses SUA's
> discipline + tooling to assist deep-thinking research.

## 1. 本地用法（推荐，全局安装已弃用）

```bash
# 1. 把 SUA 下载到科研项目文件夹
git clone <sua-repo-url> .sua/          # 或放在项目子目录

# 2. 对 agent 说："用本地的 .sua/ 约束你的行为"
#    agent 自动读 .sua/AGENTS.md + core-layer/AGENTS_CORE.md
```

**机制**（per README "What the agent gets"）:
- `AGENTS.md` — operating rules (always-loaded contract)
- `core-layer/AGENTS_CORE.md` — cache-stable subset (~10 KB)
- `.hermes/scripts/` — 自审计 + 验证工具

**跨 agent 通用**: Codex / Claude Code / Hermes / Cursor /
GitHub Copilot（per docs/CROSS_RUNTIME_SKILL_BRIDGE.md）.

**冷启动 agent**: 先让 agent 读 README "Quick start" 6-step
（~30 min onboarding）.

## 2. 科研场景适配（adapter 模式）

SUA 的 AGENTS.md 是"SUA 自己的规则"，科研项目需要
一个 adapter（bridge 模式，per
docs/CROSS_RUNTIME_SKILL_BRIDGE.md）:

```
你的科研项目/
├── AGENTS.md          # 科研项目自己的规则（调用 .sua/ 原则）
├── .sua/              # SUA 本地副本（git submodule / clone）
│   ├── AGENTS.md
│   ├── core-layer/AGENTS_CORE.md
│   └── .hermes/scripts/
└── papers/            # 论文管理（LLM Wiki 三项目）
```

科研 AGENTS.md 示例：
```markdown
> 本项目的 agent 行为受 .sua/ 约束（per P-28 self-application）。
> 核心规则：
> 1. 预任务扫描（M-n 34）：任何任务前真检查状态
> 2. 验收协议（M-n 29 5-step）：完成后真验收 + 明确说明
> 3. P-14 self-contained：论文内容不引用内部编号
> 4. ATDD 4-phase：验收标准先于实验
```

## 3. 科研工作流（卫星安全项目示例）

### 3.1 文献综述（multi-source survey）

- 用 SUA 的"知识自底向上自组织"模式整理文献
- 选题阶段：多源调研（multi-source-academic-survey skill）
- 每篇论文：摘要 + 关键贡献 + 与我的方向的关系
- 收敛标准：≥3 独立来源支撑一个判断

### 3.2 论文实验（figure-driven）

- 先用 ATDD 4-phase 定义验收标准（figures 先行）
- 实验 = 代码变更 → 用 SUA 验收协议（Phase 1 verify →
  Phase 2 fix → Phase 3 re-verify）
- 结果诚实（P-17）：不能验证就明确说，不假装

### 3.3 论文写作（self-contained）

- 每章 = 自包含（P-14）：不引用内部 round 编号
- 审稿人视角验收（7 视角，per M-n 16）
- 提交前：完整验收（run_acceptance.sh）

### 3.4 深度思考辅助

SUA 的 5 primitives（Analyze / Reason / 联想 / 归纳 / 总结）
+ 4 critical-thinking（质疑 / 逆向 / 预演失败 / 对立论证）
= 科研推理的思考对（per M-n 14 two-track）:

| 科研阶段 | SUA 工具 |
|---|---|
| 选题 | multi-source-academic-survey + academic-direction-selection |
| 文献 | Zotero + LLM Wiki + academic-search |
| 实验 | ATDD 4-phase + run_acceptance.sh |
| 写作 | P-14 self-contained + figure-driven-paper-experiment |
| 验收 | M-n 29 5-step + ACCEPTANCE_PROTOCOL |

## 4. 版本策略

- 每个科研项目 pin 一个 SUA 版本（git submodule / commit hash）
- 科研项目独立演进，SUA 更新后按需升级
- 与 SUA 主线解耦（科研项目 = 用户层，SUA = 核心层）

## 5. 已破产方向（不追）

- 全局安装到用户电脑（install-global.sh / ~/.codex/AGENTS.md）
  — agent-self-discipline 仓库方向已放弃，部署会丢失
- 本地用法（本指南）是当前最优：0 配置 + 跨 agent + 版本独立

## 6. 快速上手（5 分钟）

```bash
# 在你的科研项目里
git clone <sua-url> .sua/
cp .sua/docs/RESEARCH_USAGE.md .sua-usage.md  # 这份指南
# 然后对 agent 说："用 .sua/ 约束你的行为，我要做 <研究任务>"
```
