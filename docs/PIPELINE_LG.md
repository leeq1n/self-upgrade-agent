# pipeline_lg.py — LangGraph 编排

> 单一文件包含完整的 self-evolution state machine (8 个 node + conditional edges)
> 这是 v1.8.0 设计的核心,**有意保持单一文件** — 拆成多文件会让人跨文件追 state,
> 比单一文件更难理解。

## 文件大小

`src/pipeline_lg.py` 当前 ~1024 行。这是合理边界:
- < 200 行: 太小,通常缺功能
- 200-800 行: 单文件理想范围
- 800-1500 行: 大文件,但适合 self-contained state machine
- > 1500 行: 应该拆

## 节点(8 个)

按执行顺序:

```
START
  ↓
research    (search arxiv, filter seen)
  ↓ (conditional: papers_qualified)
filter      (LLM 评分论文)
  ↓ (conditional: papers_qualified)
implement   (patchgen 生成 patch)
  ↓
reflect     (3 次 sandbox 修复机会)
  ↓
evaluate    (A/B benchmark + harness)
  ↓
decide      (4 步 decision logic)
  ↓
skill_audit (统计 + cull)
  ↓
END
```

## 主要函数(按行号)

| 行号 | 函数 | 作用 |
|---|---|---|
| 70 | `_extract_target_function` | 从 patch 提取单 function(v1.8.1 P0-2 fix) |
| ~250 | `node_research` | 搜论文 + 过滤 seen |
| ~280 | `node_filter` | LLM 评分 |
| ~310 | `node_implement` | patchgen |
| ~340 | `node_evaluate` | A/B + harness |
| ~390 | `node_reflect` | 3 次 sandbox retry |
| ~600 | `node_decide` | 4 步 decision |
| ~700 | `node_skill_audit` | skill lifecycle (0 LLM) |
| 880 | `run` | 入口,组装 graph |

## 关键 invariant (v1.8.1)

1. **`_extract_target_function`** (line 70): 只接受 1 个 function def,
   拒绝 mixed-patch 输入(防止 planner.py 膨胀)
2. **`mark_paper_seen`** 在 `node_decide` 末尾调用: 任何 round 完成后
   paper 都标记为 seen,下次 `node_research` 自动跳过
3. **`node_skill_audit`** 在 `node_decide` 之后: 0 LLM, 纯 db 统计,
   自动 cull quality_score < 0 的 skill
4. **`node_evaluate`** arm 2 调 `run_harness()` (subprocess pytest):
   harness < 100% → state["decision"] = "reverted" (覆盖 LLM delta)

## 修改该文件的"危险信号"

如果改了下面这些,要重新跑全套测试:

- **`_extract_target_function`**: 改了会破坏 patchgen 的 sanity check
- **`node_evaluate`**: 改了会破坏 harness-first decision logic
- **`node_decide`**: 改了会破坏 4 步决策
- **`mark_paper_seen` 调用点**: 改了会导致 seen-papers 失效

## 读这文件的入口

1. 先看 `run()` 函数 (line 880): 知道整个 graph 怎么组装
2. 再看 8 个 node_xxx 函数: 每个 ~50-100 行
3. 最后看 `_papers_qualified` (line 868): 知道 conditional edges 怎么分支

## 测这文件怎么测

- `tests/test_pipeline.py`: pipeline 基础
- `tests/test_node_evaluate_e2e.py`: evaluate 隔离
- `tests/test_node_skill_audit.py`: skill_audit 隔离
- `tests/test_seen_papers.py`: seen-papers 真接
- `tests/test_pipeline_harness_integration.py`: harness 集成