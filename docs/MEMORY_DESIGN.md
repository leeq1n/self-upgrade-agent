# Memory Design — Emergent, Not Hand-Coded

> v1.8.1 — 涌现 vs 固定 的 memory 设计哲学

## 核心决定

**记忆设计不由我(开发者)拍脑袋**。`gc_seen_papers(max_rows=500)`、`history_archive(older_than=100)` 这种 magic number **不应该是 hard-coded**。

我提供:
1. **空 hook**:`apply_memory_policy(conn, policy_fn=None)` 默认 noop
2. **唯一 safety ceiling**:`MAX_LEARNING_ROWS = 10000`(硬 fuse)
3. **可插拔接口**:`self_upgrade gc --memory-policy module:fn` 让 LLM/用户安装策略

LLM 通过 patchgen 改 `apply_memory_policy` 或传 `--memory-policy` 来**涌现**真策略。

## 为什么这样做

### 反对:我自己设计
```python
# BAD: hand-designed policy
def gc_seen_papers(conn, max_rows=500):
    # Why 500?  I just guessed.  No evidence.
    ...
```

**问题**:
- 我不知道 500 是对的还是 1000 是对的
- **这个子系统永不能被 patch 改进**(因为 patchgen 只改 `core/planner.py`, 不改 `src/learning.py`)
- 我设计的"经验阈值" 在你的数据上可能完全错

### 赞成:涌现
```python
# GOOD: emergent policy
def apply_memory_policy(conn, policy_fn=None):
    if policy_fn is None:
        return {"policy": "noop", ...}  # LLM will install one
    return policy_fn(conn)  # LLM-designed policy runs
```

**优点**:
- LLM 可以根据 `get_seen_db_stats` 真数据设计
- LLM 可以被 patch 改进(改 `apply_memory_policy` 或装新 policy)
- 0 magic number 在我代码里

## 涌现怎么发生(2 条路径)

### 路径 1:patchgen 改 `apply_memory_policy`

LLM 看到 `apply_memory_policy` 是 38 行函数, 直接 patch 它。Patch 会被:
1. harness 测 (`tests/test_apply_memory_policy_*`)
2. sandbox 测
3. atomic write 到 `src/learning.py`

### 路径 2:LLM 创建 `upgrades/memory_policies.py` + `gc --memory-policy`

LLM 写:
```python
# upgrades/memory_policies.py
def trim_old_unused(c):
    """Delete papers seen >3 times AND last_outcome != 'kept'."""
    c.execute("DELETE FROM seen_papers WHERE times_seen > 3 AND last_outcome != 'kept'")
    c.commit()
    return {"policy": "trim_old_unused", "deleted": ...}
```

然后:`self_upgrade gc --memory-policy upgrades.memory_policies:trim_old_unused`

## 唯一 hard safety: `MAX_LEARNING_ROWS=10000`

即使 LLM 设计的策略是 noop,10005 行时 fuse 自动 fire:

```
seen_papers: hard ceiling fired — deleted 5 rows 
(now at 10000, ceiling 10000). Install a smarter policy via patchgen.
```

**这是"宪法底线"**:LLM 不能让 DB 无限增长。**它只能决定"如何 trim",不能决定"是否 trim 超过 10000"**。

## 涌现风险评估

| 风险 | 概率 | 缓解 |
|---|---|---|
| LLM 设计烂策略,trim 太多 | 中 | Harness + 单元测试覆盖 |
| LLM 装 policy 但 bug 隐藏 | 中 | `--memory-policy` 是 opt-in,显式激活 |
| LLM 改 `apply_memory_policy` 破坏 schema | 低 | Harness 测 schema 不变 |
| MAX 太大,DB 仍然爆炸 | 低 | 10000 足够大,半年才到 |

## 未来观察

`apply_memory_policy` 的 `result` dict 应该被记到 `learning.db`:

```sql
CREATE TABLE policy_history (
    id INTEGER PRIMARY KEY,
    applied_at TEXT,
    policy_name TEXT,
    before_count INTEGER,
    after_count INTEGER,
    deleted INTEGER,
    hard_ceiling_fired INTEGER DEFAULT 0
);
```

(留给 LLM 涌现时加 — 我不写 schema)

## 给未来 agent 的提醒

**不要**:
- ❌ 不要加 `gc_seen_papers(max_rows=N)` 这种 magic number 函数
- ❌ 不要 hard-code "keep last 30 days" / "delete if times_seen > X"
- ❌ 不要把 trim 逻辑塞进 `node_research`/`node_filter`

**应该**:
- ✅ 让 LLM 设计 `apply_memory_policy` 或新 `*_policy_fn`
- ✅ 加 harness test 测"policy runs + doesn't crash"
- ✅ schema 演化让 LLM 自己来(涌现的 schema 比设计的 schema 更优)