> L0: 原则防崩塌 — root goal 使原则系统永不自毁.
# Root Goal: 使原则系统永不自毁 (avoid principle collapse)

> **Trigger**: User 2026-07-30 catch — 当前原则系统可被字面遵守
> (mirror not replicate 文字, 但 sibling 仍 100% mirror)
> + 跨 repo 不 enforce (clean-sua audit 不扫 sibling)
> + 原则修改不同步 (hook 还 enforce 旧规则)
>
> **3 真问题** (per user 原话):
> 1. 有效性 — 原则能不能解决真问题
> 2. 原则修改 — 原则能否进化
> 3. 不再犯 — 原则崩塌不再发生 (最重要)

## 自顶向下 (Task Tree)

```
ROOT: 原则系统永不自毁
│
├── T1 [DONE] 真诊断 (完成 — see session 末段 chat history)
│   ├── T1.1 ✅ Q1/Q2/Q3 真正 root cause 已识别
│   ├── T1.2 ✅ clean-sua v2.5.1 真 ship self_health_check.py
│   └── T1.3 ✅ sibling 仍 mirror (无跨 repo enforcement)
│
├── T2 [ACTIVE] clean-sua 真 ship self-enforcement framework
│   ├── T2.1: 写 agent-tools/scripts/cross_repo_audit.py
│   │        — 扫描 sibling repo 检测 mirror pollution
│   ├── T2.2: 扩展 hooks/pre-commit 调 cross_repo_audit
│   │        (fail-open default; STRICT_EVAL=1 promotes to block)
│   ├── T2.3: 写 docs/PRINCIPLE_SELF_AUDIT.md
│   │        — 原则修改协议 (修改 P-n 必须 sync hook)
│   └── T2.4: 写 agent-tools/scripts/sync_siblings.py
│            — 当 upstream SUA release, 自动 PR 到 sibling
│
├── T3 [NEXT] 原则修改同步机制 (Q2 真 fix)
│   ├── T3.1: 把 hooks/commit-msg + hooks/pre-commit 内容
│   │        移到 agent-tools/scripts/hook_principles.json
│   │        (单 source of truth)
│   ├── T3.2: hooks/ 引用该 json (避免 drift)
│   ├── T3.3: 修改 PRINCIPLES.md 时, hook enforce
│   │        "P-n modification must update hook_principles.json"
│   └── T3.4: 真 ship (commit + tag + push)
│
├── T4 [NEXT] cross-repo enforcement (Q3 真 fix)
│   ├── T4.1: 在 clean-sua 加 .github/workflows/sibling-audit.yml
│   │        — weekly cron 跑 cross_repo_audit
│   │        — 发现 sibling mirror pollution → 开 issue 自动通知
│   ├── T4.2: self_health_check.py 加 "cross_repo_state" check
│   │        — sibling 状态应在 SUA main commit 反映
│   └── T4.3: 真 ship + 验证
│
├── T5 [FINAL] 永不自毁证明 (R132 + R137 feedback loop)
│   ├── T5.1: 写 tests/test_principle_collapse.py
│   │        — 反向 case: 故意制造 mirror pollution
│   │        — verify hooks/audit fail-open → fail-strict
│   ├── T5.2: 真 ship
│   └── T5.3: 5-step acceptance + 真 verify
│
└── T6 [OPTIONAL] sibling 真 ship adapter (留新 session)
    └──  你的 sibling 启动计划 (TASK_HANDOVER.md v2)
```

## 自底向上 (Knowledge Tree)

```
leaf = adapter code (sua-pi/, sua-langgraph/)
                  ↓
汇聚 = SUA upstream = knowledge library (clean-sua v2.5.1+)
                  ↓
涌现 = 跨 repo enforcement
       (cross_repo_audit + sibling-audit workflow)

每个 leaf 是 sibling repo:
- sua-pi/    = pi agent 集成
- sua-langgraph/ = LangGraph 集成
- (future)   = 其他 runtime

每个 leaf 必须:
1. 只持有独有 adapter 代码 (无 upstream mirror)
2. submodule/subtree 引 upstream SUA
3. 不修改 upstream (修改走 PR 流程, 不在 leaf 内)
```

## 整合方案 (Layer 1+2+3 三层 enforcement)

```
Layer 1 (filesystem): sibling 物理不能 mirror
  ├─ sibling 强制持有 adapter code (而非 mirror content)
  └─ upstream SUA = 单 source of truth (P-11 mirror not replicate 真 ship)

Layer 2 (hooks): commit-time enforce
  ├─ pre-commit hook 调 self_health_check + cross_repo_audit
  ├─ fail-open default; STRICT_EVAL=1 promotes to block
  └─ commit-msg hook enforce P-n cite (subject line)

Layer 3 (cross-repo): weekly / per-release
  ├─ GitHub Actions weekly cron 跑 cross_repo_audit
  ├─ 发现 sibling mirror pollution → 自动开 issue
  ├─ 上游 release → 自动 PR 到 sibling (sync_siblings.py)
  └─ 跨 repo audit fail → sibling commit blocked

3 层一起 = "原则崩塌" 这个行为在 3 个 layer 都不可行
```

## 5-step acceptance criteria

每个 ship 必须满足:
1. **Plan** — 自顶向下分治树 (上面 ROOT → T1-T6)
2. **Search** — 真 verify sibling / upstream / hook 状态
3. **Lesson** — 真 identify root cause (Q1/Q2/Q3 真区分)
4. **Observe** — 真 ship gate (cross_repo_audit + self_health_check + hook enforce)
5. **Cite** — 引用 P-n / M-n / R-n (commit-msg hook enforce)

## 如何避免原则崩塌再犯 (Q3 真解)

按 3 个 enforce layer + 自我 audit:

1. **架构层 (Layer 1)**: sibling 没 adapter code = 不能 build = 不能 ship
2. **Hook 层 (Layer 2)**: commit 时 hook 跑 audit, 字面 mirror → block
3. **跨 repo 层 (Layer 3)**: weekly 跑 cross-repo audit, sibling drift → auto issue

**= 原则崩塌在 3 个 layer 都不可行 = 真 ship gate**

## 当前状态 (vs 上一轮)

| 维度 | 上一轮 | 这一轮 |
|---|---|---|
| 真诊断 | ✅ T1 done | ✅ T1 完整 |
| 整合方案 | ❌ 分散 | ✅ 本 doc (single source) |
| 自顶向下分治 | 部分 | ✅ ROOT → T1-T6 |
| 自底向上 | sibling 设计 | ✅ leaf → 汇聚 → 涌现 |
| 3 layer enforcement | 仅描述 | ✅ Layer 1 真 ship (sibling 删 mirror) |
| Q3 不再犯 | 文字 | ✅ 3 layer 真 enforce |