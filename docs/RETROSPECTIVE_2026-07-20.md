# RETROSPECTIVE — 2026-07-20

> L0: 反思本次 session 中的失误与修复方法. 让 fresh agent 启动
> 时能 reference 此文件而非 always-loaded rules.
> 2026-07-20 同日内 12 commits + 多轮反思, 累积 over-process.
> 此 retro 旨在 close retrospective loop (M-n 33 必需) 而不 agent-rule 化.

## Session 上下文

用户初始问题: 项目中含中文「那个英文词 + turn」类角色简写 (你 / 我
+ 该英文词; user / assistant + 该英文词), 导致 decoder-loop 重复输出.
用户要求全面清理.

> 注: 该英文词 = banned 词 (本文件中用「那个英文词」/「banned 词」
> 替代指代, 因为 banned phrase 自身作为字面量会触发同项目 test 失败.
> structural necessity 例外仅限 `tests/test_prompt_hygiene.py` 的
> BANNED 元组.)

## 7 个失误 pattern (root classification)

### Pattern A — Narrow audit syndrome (4 misses)

- 早期 commit 添加 banned-phrase guard for narrow pattern (中文 role)
  但漏掉 English variants (英文 role + 该词). 同类 miss 第 2 次.
- b3bc888 catch 之前 commits 的 narrow audit. 之前「5 项目 0 hits」
  实际只审查 narrow pattern, 未声明 audit scope. 用户 catch 「之前是
  narrow audit」.

**Avoid**: 每次审计 declare in commit msg: 「本 commit per pattern X
hits = N」. 具体 pattern + 命中数.

### Pattern B — 加规则不是 simplify (OcCam 违反)

- 早期 commit chain — 3 commits narrow pattern expansion.
- 0db1250 — 加 28 行 self-referential guard 解决 5 行 exemption 问题.

**Avoid**: 修复前先应用 P7 + P25 step 3 — 「verify no duplication」,
看现有 rules 是否可简化而非新增.

### Pattern C — English indirection

- 98e5fb2 — 3 段英文绕路 (那个英文词的间接描述).

**Avoid**: 描述 banned word 时**语言切换到中文**自然 bypass 整个
系统. 如「那个会引发解码循环的英文单词」1 行替代 3 段英文.

### Pattern D — Late durable fix

- d17e4e1 — 加 rule 在 5 commits 失败后. 应该从 commit #1 即 codify.

**Avoid**: 任何 meta-rule 发现**立即** codify 到 always-loaded 或
per-task reference, 而非 wait for 5 failure cycles.

### Pattern E — P25 6-step skip

- 历史 commits 添加 M-n 36, 修改 AGENTS family 未守 P25 6-step gate.

**Avoid**: 触及 P-n / M-n / always-loaded 文件前**先问** (用户 explicit
+ multi-session + 3+ turn), 不是 commit 后 retro-fit.

### Pattern F — Cross-profile boundary 未声明

- hermes skills (cross-profile) + state.db (hermes internal) 从未
  clean 或 declare-boundary. 用户多次 catch 之后才意识.

**Avoid**: 每次审计 / cleanup commit 必须 explicit declare 「out of
scope: cross-profile X, narrative Y, reason Z」. 沉默处理 = 触发后续
miss.

### Pattern G — Verification after commit (vs before)

- 早期清理破坏 cross-project references, 但 verification 在 commit 后跑.

**Avoid**: per P5 + M-n 32 Guardrail #1: verification must run **before**
commit, not after.

## 5 self-audit questions (always apply, never add rules to enforce)

1. **Audit scope declaration**: 本次审计的 pattern 是什么? Explicit 写 in
   commit msg.
2. **P-n / M-n / AGENTS family touched?** Apply P25 6-step gate (用户
   explicit + multi-session).
3. **Cross-profile scope?** Declare in commit msg 「out of scope: X, Y,
   reason」.
4. **P7 ratio**: +N rules vs -M rules? If +N>1 且 -0, simplify first.
5. **Pre-commit verification** ran (M-n 32)? Required, not optional.

These 5 questions are **applied by agent reading this retro**, not
enforced by always-loaded rules. The retro IS the durable mechanism.
Per OcCam.

## Meta-lesson: 「OcCam ≠ Stop」

上轮反思我错误地把「OcCam」解读为「stop / no commit」, actual OcCam
is「least action that closes the loop」. Retrospective without action
项 = incomplete. This retro 本身 is the action; it's not 「done
nothing」.

下一轮如果发现 retrospective 提议「no action」— flag that as
rationalization, not principle. Stress test 30 days later: did not
acting avoid or prolong the issue?

注意: 本 retro 写完后, 项目 test guard 立刻 fail 了 (因 retro 自身含
banned phrase 字面量, 触发 self-violation). 这正是 Pattern E 与 Pattern
G 同时 trigger 的实例. Fix: 改用中文 / 片段拼写 / 占位符指代 banned
phrase, 不字面写入 retro. 这是**测试 enforcing 项目形态**的体现,
不是规则失败 — 这是 project-centric 而不是 agent-centric.

## Decision template (apply this when uncertain)

```
Principle claimed:   [P## / M-n ##]
Actual principle:    [correct reading of P## / M-n ##]
Confidence:          [low / med / high]
Stress test 30 days later: [will this decision avoid or prolong issue?]
Action:              [specific minimal action]
```

When 「Principle claimed」 doesn't match 「Actual principle」, **do NOT
use that principle as justification**. Re-derive from actual principle.

## Cross-references

- `docs/OPERATING_RULES.md` — full M-n 33 retrospective framework
- `core-layer/AGENTS_CORE.md` — M-n 34 pre-task scan (apply this retro
  at session start)
- AGENTS_DETAIL.md cross-ref added in same commit, links this file from
  per-task loading
