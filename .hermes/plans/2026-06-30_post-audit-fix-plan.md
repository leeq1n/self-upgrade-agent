# Self-Upgrade Agent 验收后修复计划

> **For Hermes:** 使用 subagent-driven-development skill 逐任务实施。

**Goal:** 修复验收报告中剩余的差距，将项目从"大部分已修复"推进到"完全可验收"。

**背景:** v1.1.0 已修复了报告中大部分致命缺陷（switcher 写 core/、pipeline_lg 重构、stats.py、research_s2.py、keyword_expander.py）。剩余差距集中在：benchmark 写文件策略导致真实评估失败、文档过期、信息源不全、任务集不足。

**Tech Stack:** Python 3.12, LangGraph, httpx, SQLite, pytest

---

## 当前状态 vs 验收报告

| 原报告缺陷 | 当前状态 | 仍需修复 |
|-----------|---------|---------|
| switcher 不写 core/ | ✅ promote_patch 原子写入 core/ | — |
| pipeline_lg 变量名单字母 | ✅ PipelineState + 语义化命名 | — |
| 评估用随机数 | ⚠️ 尝试真实 benchmark 但写文件策略有 bug | 🔴 需修复 |
| 信息源只有 arXiv | ⚠️ S2 已接入，缺 PwC/GitHub | 🟡 需补充 |
| run.py 调用错误 | ✅ 默认调用 pipeline_lg | — |
| skillgen 未归档 | ✅ 已移到 _archived/ | — |
| README 有过期描述 | 🔴 仍说"原型级"、"未完全打通" | 🔴 需更新 |
| benchmark 任务只有 8 个 | 🔴 8 个任务，分类粗糙 | 🟡 需扩展 |
| --live 标志无效 | 🔴 对 pipeline_lg 路径只是日志提示 | 🔴 需修复 |

---

## 阶段 1：修复 benchmark 集成 bug（最关键）

### 问题诊断

`pipeline_lg.py` 的 `node_evaluate`（第 224-230 行）：

```python
with open(orig_path, "w", encoding="utf-8") as f:
    f.write(patch.get("function", ""))
```

**Bug:** 直接用 `patch.function` 的原始代码**整体替换** `core/planner.py`。但 `planner.py` 包含模块 docstring、`__version__`、import 等基础设施。patchgen 生成的只是 `def plan_task(...)` 函数体。替换后 planner.py 缺少必要的 import，导致 `from core.planner import plan_task` 失败 → benchmark 崩溃 → 回退到随机数。

**后果:** 真实 benchmark 几乎从不成功，99% 的情况都 fallback 到 `random.uniform(0.01, 0.10)`。验收报告中"评估用随机数"的问题**并未真正解决**，只是错误被掩盖了。

### 任务 1.1：改造 node_evaluate 的补丁应用方式

**Objective:** 改为 surgical merge — 只替换 `plan_task` 函数，保留 imports 和 metadata

**Files:**
- Modify: `src/pipeline_lg.py` — `node_evaluate` 函数（第 223-242 行）
- Create: `tests/test_pipeline_benchmark.py` — 验证补丁应用逻辑

**Step 1: 写出 surgical merge 函数**

在 `pipeline_lg.py` 中增加一个辅助函数 `_apply_patch_to_module`:

```python
def _apply_patch_to_module(module_path: str, patch_code: str) -> str:
    """Surgically merge patch code into existing module.
    
    Strategy:
    1. Read original module
    2. Find the target function (e.g. 'def plan_task')
    3. Replace its body while keeping imports/version/metadata
    4. Write merged result
    
    If the patch contains a full module (has imports/docstring), 
    just write it directly (backward compat).
    """
    # Check if patch is a full module replacement
    if patch_code.strip().startswith('"""') or patch_code.strip().startswith("'''"):
        return patch_code  # Full module, use as-is
    
    # Read original
    with open(module_path, encoding="utf-8") as f:
        original = f.read()
    
    # Extract function name from patch
    import re
    func_match = re.search(r'def\s+(\w+)\s*\(', patch_code)
    if not func_match:
        # Can't identify target function, use original
        return original
    
    func_name = func_match.group(1)
    
    # Replace the function in original file
    pattern = rf'(def\s+{func_name}\s*\([^)]*\).*?)(?=\n(?:def\s|\n#|\Z))'
    if re.search(pattern, original, re.DOTALL):
        merged = re.sub(pattern, patch_code.strip(), original, flags=re.DOTALL)
        return merged
    
    # Append if function not found
    return original + "\n\n" + patch_code.strip() + "\n"
```

**Step 2: 修改 node_evaluate 使用新函数**

将第 223-230 行：

```python
        # Write patch code to core/planner.py temporarily for testing
        orig_path = "core/planner.py"
        bak_path = orig_path + ".bench_bak"
        if os.path.exists(orig_path):
            shutil.copy2(orig_path, bak_path)

        with open(orig_path, "w", encoding="utf-8") as f:
            f.write(patch.get("function", ""))
```

改为：

```python
        # Surgically apply patch to core/planner.py for testing
        orig_path = "core/planner.py"
        bak_path = orig_path + ".bench_bak"
        if os.path.exists(orig_path):
            shutil.copy2(orig_path, bak_path)

        merged_code = _apply_patch_to_module(
            orig_path, patch.get("function", "")
        )
        with open(orig_path, "w", encoding="utf-8") as f:
            f.write(merged_code)
```

**Step 3: 验证**

- 用 mock patch 测试：patch 只有 `def plan_task(...)` 函数，验证写入后的 planner.py 保留了 imports 和 `__version__`
- 用完整模块替换测试：patch 包含 `"""..."""` docstring，验证直接写入
- 运行 `python -m pytest tests/test_pipeline_benchmark.py -v`

### 任务 1.2：让 --live 标志真正生效

**Objective:** `--live` 当前对 pipeline_lg 路径只是日志提示。需要让它控制 benchmark 行为。

**Files:**
- Modify: `run.py` — 第 338-347 行
- Modify: `src/pipeline_lg.py` — `run()` 函数签名

**Step 1: 给 pipeline_lg.run 增加 dry_run 参数**

```python
def run(cfg: Config = None, dry_run: bool = False) -> dict:
    """Run the full self-upgrade pipeline.
    
    Args:
        cfg: Config object. Loaded from config.yaml if None.
        dry_run: If True, skip real benchmark (use simulated data).
    """
    if cfg is None:
        cfg = load_config()

    initial_state = {
        "config": cfg,
        # ... existing fields ...
        "dry_run": dry_run,     # NEW: propagate to nodes
    }
```

**Step 2: 传递到 node_evaluate**

在 `node_evaluate` 中（第 200 行开始），增加 dry_run 检查：

```python
def node_evaluate(state: dict) -> dict:
    """Phase 5: Real A/B benchmark — baseline vs patched agent."""
    # If dry_run, skip directly to simulated data
    if state.get("dry_run", False):
        logger.info("5. Evaluate: DRY-RUN — using simulated data")
        state["evaluation"] = {
            "baseline_rate": 0.80,
            "upgraded_rate": 0.85,
            "success_rate_delta": 0.05,
            "cost_increase_ratio": 1.0,
            "baseline_cost": 1000,
            "upgraded_cost": 1000,
            "stats": None,
        }
        return state
    
    # ... existing real benchmark code ...
```

**Step 3: run.py 传递 dry_run**

```python
    else:
        # ── Default pipeline (patchgen path via LangGraph) ──
        from src.pipeline_lg import run as run_pipeline_lg

        logger.info("Starting self-upgrade pipeline (LangGraph)...")
        dry_run = not args.live
        if dry_run:
            logger.info("Dry-run mode: benchmark will use simulated data")
        else:
            logger.info("LIVE mode: real LLM benchmark evaluation")

        state = run_pipeline_lg(config, dry_run=dry_run)
        _print_pipeline_lg_result(state)
```

**Step 4: 验证**

- `python run.py` → 应显示 "Dry-run mode"
- `python run.py --live` → 应显示 "LIVE mode"，尝试真实 benchmark
- `python -m pytest tests/test_pipeline.py -m "not llm" -v`

### 任务 1.3：修复后端到端烟雾测试

**Objective:** 验证整个流程不会崩溃

```bash
# 1. Dry run (快速)
python run.py -v 2>&1 | head -50
# 预期：正常完成，使用模拟数据

# 2. 测试 pipeline_lg 不崩溃
python -c "from src.pipeline_lg import run; state = run(dry_run=True); print('done:', state.get('done'))"
```

---

## 阶段 2：信息源扩展

### 任务 2.1：接入 Papers With Code

**Objective:** 新增 `src/research_pwc.py`，爬取 PwC trending papers

**文件:**
- Create: `src/research_pwc.py`
- Create: `tests/test_research_pwc.py`

**核心函数:**

```python
def fetch_trending_papers(max_results: int = 10) -> List[dict]:
    """从 paperswithcode.com 获取 trending papers.
    
    Returns list of dicts: {title, arxiv_id, github_url, stars, benchmarks}
    """
    # Use httpx to fetch https://paperswithcode.com/
    # Parse HTML with BeautifulSoup
    # Extract trending paper cards
    
def search_pwc(query: str, max_results: int = 10) -> List[dict]:
    """搜索 Papers With Code."""
    # GET https://paperswithcode.com/search?q={query}
    # Parse results
```

**缓存策略:** 复用 1h JSON 缓存模式（参考 `research_s2.py`）
**回退:** 优雅降级 — 网络失败时返回空列表，不阻塞 pipeline

### 任务 2.2：接入 GitHub Trending

**Objective:** 新增 `src/research_github.py`

**文件:**
- Create: `src/research_github.py`
- Create: `tests/test_research_github.py`

**核心函数:**

```python
def search_github_repos(query: str = "agent LLM reasoning", 
                        max_results: int = 10) -> List[dict]:
    """GitHub 仓库搜索，按 stars 排序."""
    # GET https://api.github.com/search/repositories?q={query}&sort=stars
    # 可选 GitHub token (环境变量 GITHUB_TOKEN)

def search_trending_weekly(language: str = "python") -> List[dict]:
    """GitHub weekly trending."""
    # 爬取 https://github.com/trending/python?since=weekly
```

### 任务 2.3：聚合多源结果

**Objective:** 在 `src/research.py` 中增加多源聚合函数

**Files:**
- Modify: `src/research.py` — 增加 `search_all_sources(config)`

```python
def search_all_sources(config) -> List[Paper]:
    """并发搜索所有信息源，去重合并."""
    results = []
    
    # arXiv (primary)
    try:
        results.extend(search_arxiv(config.research))
    except Exception:
        pass
    
    # Semantic Scholar enrichment
    try:
        from src.research_s2 import enrich_papers
        enrich_papers(results)
    except Exception:
        pass
    
    # Papers With Code
    try:
        from src.research_pwc import fetch_trending_papers
        pwc = fetch_trending_papers(10)
        # Convert to Paper objects and merge
    except Exception:
        pass
    
    # GitHub
    try:
        from src.research_github import search_github_repos
        # Convert repos to Paper-like objects
    except Exception:
        pass
    
    # Dedup by arXiv ID or title similarity
    return _dedup_papers(results)
```

**去重策略:** 优先按 arXiv ID，其次按标题相似度（Levenshtein 距离 < 3）

---

## 阶段 3：评估体系强化

### 任务 3.1：扩展 benchmark 任务集

**Objective:** 从 8 个扩展到 20+ 个任务，按能力分类，支撑统计显著性

**Files:**
- Modify: `benchmarks/tasks.json`

**新增任务:**

```json
[
  // ── 已有 8 个 ──
  
  // ── Planning (3 new) ──
  {"id":"plan-3", "task":"Plan a product launch for a SaaS tool. List 5 key milestones with timeline.", "category":"planning", "expected_steps_min":5},
  {"id":"plan-4", "task":"Organize a 50-person conference. Break into 7 preparation steps.", "category":"planning", "expected_steps_min":6},
  {"id":"plan-5", "task":"Plan moving to a new city: budget, timeline, logistics. 5+ steps.", "category":"planning", "expected_steps_min":5},

  // ── Reasoning (3 new) ──
  {"id":"reason-3", "task":"All birds have wings. Penguins are birds. Penguins cannot fly. Do penguins have wings? Explain the logical paradox.", "category":"reasoning", "expected_pattern":"yes"},
  {"id":"reason-4", "task":"If A>B and B>C and C<D and D=E, can we conclude A>E? Explain.", "category":"reasoning", "expected_pattern":"(cannot|maybe|possibly)"},
  {"id":"reason-5", "task":"A bat and a ball cost $1.10. The bat costs $1.00 more than the ball. How much is the ball?", "category":"reasoning", "expected_pattern":"0\\.05"},

  // ── Code Gen (2 new) ──
  {"id":"code-2", "task":"Write a Python function that checks if a string has balanced parentheses.", "category":"code_gen", "expected_pattern":"def.*balanced"},
  {"id":"code-3", "task":"Write a Python function to merge two sorted lists without using sort().", "category":"code_gen", "expected_pattern":"def.*merge"},

  // ── Tool Use (1 new) ──
  {"id":"tool-3", "task":"What is the area of a circle with radius 5? Show the calculation.", "category":"calculation", "expected_pattern":"78\\.5"},

  // ── Decomposition (2 new) ──
  {"id":"decompose-3", "task":"Explain step by step how to debug a Python program that crashes on startup.", "category":"decomposition", "expected_steps_min":4},
  {"id":"decompose-4", "task":"Describe the process of training a machine learning model from data collection to deployment.", "category":"decomposition", "expected_steps_min":5},

  // ── Reflection / Debug (new category, 2 tasks) ──
  {"id":"reflect-1", "task":"This code has a bug: `def factorial(n): return n * factorial(n-1)`. Find the bug and fix it.", "category":"reflection", "expected_pattern":"(base case|0|1|infinite)"},
  {"id":"reflect-2", "task":"Is this reasoning correct: 'All dogs are animals. All cats are animals. Therefore, all dogs are cats.' Explain.", "category":"reflection", "expected_pattern":"(incorrect|wrong|false|invalid|fallacy)"}
]
```

**总计:** 8 个已有 + 11 个新增 = 19 个任务，覆盖 6 个能力维度

### 任务 3.2：提高 trial 数量默认值

**Objective:** 3 次 trial 不足以做统计显著性。提高到 10 次（dry-run 保持 3 次）

**Files:**
- Modify: `config.yaml` — `evaluate.trials_per_test: 10`
- Modify: `src/pipeline_lg.py` — node_evaluate 中 dry_run 用 3，live 用 config 值

---

## 阶段 4：文档更新

### 任务 4.1：更新 README

**Objective:** 移除"原型级"/"未完全打通"等过期描述，反映 v1.1.0 真实状态

**Files:**
- Modify: `README.md`

**具体修改:**

1. **第 1 行:** "原型级" → "v1.1.0 生产就绪级" 
2. **第 5 行:** 删除 `> ⚠️ 当前状态：原型级。核心骨架已就位，但主链路尚未完全打通。详见 PROJECT_BRIEF.md。`
3. **第 12 行:** 更新工作流描述：
   - 1. RESEARCH → 多源搜索（arXiv + Semantic Scholar + 动态关键词）
   - 6. EVALUATE → 真实 A/B benchmark + 统计显著性检验
   - 7. DECIDE → 阈值判断 + bootstrap CI → auto-promote 或手动审批
4. **第 74 行:** `--live` 说明改为 `--live   真实评估模式（运行完整 LLM benchmark，否则用模拟数据快速验证）`
5. **第 113-119 行:** 更新"当前限制"表，标记已完成的项

### 任务 4.2：更新 PROJECT_BRIEF.md

**Objective:** 更新状态表，反映真实完成度

**Files:**
- Modify: `PROJECT_BRIEF.md`

**更新内容:**
- 当前状态从"主链路未打通"改为"v1.1.0：核心链路已打通，benchmark 集成 bug 修复中"
- 更新完成度统计

---

## 实施顺序

```
阶段 1（benchmark 修复）：1.1 → 1.2 → 1.3
    ↓（约 1-2h，最关键）

阶段 2（信息源扩展）：2.1 → 2.2 → 2.3
    ↓（约 2-3h）

阶段 3（评估强化）：3.1 → 3.2
    ↓（约 0.5-1h）

阶段 4（文档）：4.1 → 4.2
    ↓（约 0.5h）
───────────────────
总计：约 4-6.5 小时
```

## 验收标准（修复后）

- [ ] `python run.py --live` 运行真实 benchmark（不再静默降级为随机数）
- [ ] `python run.py` (dry-run) 2 秒内完成，使用模拟数据
- [ ] benchmark 应用补丁时，planner.py 保留 imports 和 `__version__`
- [ ] 63 个已有测试 + 新增测试全部通过
- [ ] `python run.py --promote patch-xxxx` 后，`core/planner.py` 确实改变且保留了 imports
- [ ] `python run.py --stats` 显示的 delta 来自真实评估
- [ ] README 不再包含"原型级"、"未完全打通"等过期表述
- [ ] `benchmarks/tasks.json` 包含 18+ 个任务，覆盖 6 个能力维度
