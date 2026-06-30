# API Reference — Self-Upgrade Agent v1.3.0

> Auto-generated from module docstrings. Last updated: 2026-06-30.

---

## Core Modules (`core/`)

### `core.agent`

| Function | Signature | Description |
|----------|-----------|-------------|
| `run` | `(task: str, llm_call: Callable, verbose: bool = False) -> dict` | Main agent loop: plan → execute tools → respond. Returns dict with `steps_planned`, `tools_used`, `success`, `final_response`. |
| `register_tool` | `(name: str, fn: Callable)` | Register a callable tool accessible by the agent. |
| `call_tool` | `(name: str, args: dict) -> str` | Invoke a registered tool by name. |
| `list_tools` | `() -> List[str]` | List all registered tool names. |

### `core.planner`

| Function | Signature | Description |
|----------|-----------|-------------|
| `plan_task` | `(task: str, llm_call: Callable) -> List[str]` | Decompose a task goal into 3-5 ordered steps. PRIMARY target for self-improvement patches. |

---

## Self-Improvement Engine (`src/`)

### `src.research` — Multi-Source Paper Search

| Function | Signature | Description |
|----------|-----------|-------------|
| `search_arxiv` | `(config: ResearchConfig) -> List[Paper]` | Search arXiv API with keywords + categories. 1h cache, exponential backoff. Falls back to `src.scraper.search_arxiv_scrape`. |
| `search_all_sources` | `(config: ResearchConfig) -> List[Paper]` | Aggregate results from arXiv + S2 + PwC + GitHub with deduplication. All sources fail gracefully. |
| `build_query_string` | `(config) -> str` | Build arXiv API query from ResearchConfig keywords/categories. |
| **Paper** | `dataclass(arxiv_id, title, authors, published, abstract, categories, citation_count)` | Standardized paper object used across all modules. |

### `src.research_s2` — Semantic Scholar

| Function | Signature | Description |
|----------|-----------|-------------|
| `search_s2` | `(keywords: List[str], max_results: int = 10) -> List[Dict]` | Search Semantic Scholar API for papers. |
| `enrich_paper` | `(arxiv_id: str) -> dict` | Fetch citation count + influential citation count for a paper. |
| `enrich_papers` | `(papers: List[Paper]) -> None` | Enrich all papers in-place with citation data. |
| `get_citing_papers` | `(paper_id: str, limit: int = 5) -> List[dict]` | Get papers that cite this paper (citation chain). |

### `src.research_pwc` — Papers With Code

| Function | Signature | Description |
|----------|-----------|-------------|
| `fetch_trending_papers` | `(max_results: int = 10) -> List[Dict]` | Get trending papers. Selenium-first, regex fallback. |
| `search_pwc` | `(query: str, max_results: int = 10) -> List[Dict]` | Search PwC by query string. |

### `src.research_github` — GitHub

| Function | Signature | Description |
|----------|-----------|-------------|
| `search_github_repos` | `(query: str, max_results: int = 10) -> List[Dict]` | Search GitHub repositories API (optional GITHUB_TOKEN). |
| `search_trending_weekly` | `(language: str = "python") -> List[Dict]` | Get weekly trending repos. Selenium-first, regex fallback. |

### `src.scraper` — Selenium Browser Automation

| Function | Signature | Description |
|----------|-----------|-------------|
| `search_arxiv_scrape` | `(keywords, categories, max_results) -> List[Paper]` | Scrape arXiv search results via headless browser. |
| `scrape_pwc_trending` | `(max_results: int = 10) -> List[Dict]` | Scrape Papers With Code trending via Selenium. |
| `scrape_github_trending` | `(language: str = "python") -> List[Dict]` | Scrape GitHub trending via Selenium. |
| `check_selenium_available` | `() -> bool` | Health check: can we start a headless browser? |

### `src.keyword_expander` — Dynamic Keywords

| Function | Signature | Description |
|----------|-----------|-------------|
| `extract_ngrams` | `(text: str, n: int = 2, top_k: int = 20) -> List[str]` | Extract top n-grams from text, filtering noise terms. |
| `extract_trending_keywords` | `(papers: List[Paper], top_n: int = 5) -> List[str]` | Use LLM to identify emerging method names from paper titles/abstracts. |
| `merge_keywords` | `(existing: List[str], new: List[str], max_total: int = 15) -> List[str]` | Merge new keywords into existing list, dedup, cap at max. |
| `update_trending_keywords` | `(papers, existing_keywords) -> None` | Full cycle: extract → merge → persist to upgrades/trending_keywords.json. |

### `src.filter` — Paper Scoring

| Function | Signature | Description |
|----------|-----------|-------------|
| `filter_papers` | `(papers: List[Paper], config, use_llm: bool = True) -> List[ScoredPaper]` | Score and rank papers by 3D (applicability/novelty/abstract) + citation. Returns sorted list. |
| **ScoredPaper** | `dataclass(paper, applicability_score, novelty_score, abstract_score, citation_score, total_score, reasons)` | Paper with computed scores. |

### `src.patchgen` — Code Generation

| Function | Signature | Description |
|----------|-----------|-------------|
| `generate_patch` | `(paper: Paper, target_module: str) -> Dict` | Generate a Python code patch from paper content targeting a core module. Returns `{function, test, module}`. |

### `src.sandbox` — Isolated Testing

| Function | Signature | Description |
|----------|-----------|-------------|
| `run_in_sandbox` | `(code: str, test_code: str, timeout: int = 10) -> Dict` | Execute code in isolated subprocess. Returns `{passed, output, error, elapsed}`. |

### `src.reflect` — Auto-Repair

| Function | Signature | Description |
|----------|-----------|-------------|
| `reflect_and_improve` | `(code: str, test_code: str, error: str, max_attempts: int = 3) -> Dict` | LLM analyzes failure and rewrites code. Returns `{fixed, code, attempts}`. |

### `src.benchmark` — Agent Evaluation

| Function | Signature | Description |
|----------|-----------|-------------|
| `load_tasks` | `(path: str) -> List[Dict]` | Load benchmark tasks from JSON. |
| `run_single` | `(task: Dict, llm_config, verbose, skill_context) -> Dict` | Run agent on one benchmark task. |
| `run_all` | `(tasks, llm_config, verbose, skill_context) -> Dict` | Run agent on all tasks, return aggregate `{success_rate, results, categories}`. |
| `compare` | `(baseline: Dict, upgraded: Dict) -> Dict` | Compare two benchmark runs, return delta and improvement flag. |

### `src.stats` — Statistical Significance

| Function | Signature | Description |
|----------|-----------|-------------|
| `bootstrap_test` | `(baseline: List[bool], upgraded: List[bool], n_bootstrap=1000) -> Dict` | Bootstrap confidence intervals for success rate difference. Returns `{mean_delta, ci_lower, ci_upper, p_value, significant}`. |
| `is_real_improvement` | `(baseline_rate, upgraded_rate, baseline_results, upgraded_results, min_delta=0.05) -> Dict` | Combined check: delta >= threshold AND statistically significant. Returns `{decision, reasons, metrics}`. |

### `src.switcher` — Bootloader

| Function | Signature | Description |
|----------|-----------|-------------|
| `init` | `() -> None` | Initialize upgrades/ directory structure. |
| `deploy_candidate` | `(skill_name, skill_md, code_dict, target_module) -> str` | Save new patch as candidate. |
| `promote_patch` | `(skill_name: str) -> Dict` | Atomically write candidate to core/{module}, backup old version. |
| `promote_candidate` | `(skill_name: str) -> Dict` | Backward-compat wrapper: promote + legacy active/ copy. |
| `rollback_patch` | `(target_module, backup_path) -> Dict` | Restore core module from backup. |
| `discard_candidate` | `(skill_name: str) -> Dict` | Delete failed candidate. |
| `get_module_versions` | `() -> Dict` | Return version info for all tracked core modules. |

### `src.pipeline_lg` — LangGraph Pipeline

| Function | Signature | Description |
|----------|-----------|-------------|
| `run` | `(cfg: Config = None, dry_run: bool = False) -> dict` | Run full R→F→G→X→T→E→D self-upgrade loop. `dry_run=True` skips real benchmark. |
| `build_graph` | `() -> CompiledGraph` | Build and compile the LangGraph state machine. |
| `_apply_patch_to_module` | `(module_path: str, patch_code: str) -> str` | Surgically merge function patch into existing module, preserving imports. |

### `src.decide` — Decision Logic

| Function | Signature | Description |
|----------|-----------|-------------|
| `make_decision` | `(eval_data: Dict, config) -> Dict` | Decide keep/revert based on delta + cost thresholds. Returns `{decision, reasons}`. |

### `src.skill_lifecycle` — Lifecycle Management

| Function | Signature | Description |
|----------|-----------|-------------|
| `cull_obsolete` | `(db, max_active=10, inactivity_days=30) -> List[Tuple]` | Archive underperforming/inactive skills. 3 rules: negative improvement, unused>30d, over limit. |
| `evaluate_all_skills` | `(db, config) -> Dict` | Re-evaluate all active skills via LLM benchmark. |

### `src.db` — SQLite Persistence

| Class/Function | Signature | Description |
|----------------|-----------|-------------|
| **UpgradeHistory** | `(db_path: str)` | Manage upgrade records. Methods: `insert`, `get_all`, `get_stats`. |
| **UpgradeRecord** | `dataclass(...)` | Single upgrade attempt record (paper, scores, decision). |

### `src.llm` — LLM Interface

| Class/Function | Signature | Description |
|----------------|-----------|-------------|
| `chat_simple` | `(prompt: str, system: str = "", config = None) -> str` | Single-turn LLM completion. |
| **LLMConfig** | `dataclass(api_key, model, base_url, ...)` | LLM configuration. `from_env()` reads .env. |

---

## Configuration (`config.yaml`)

| Section | Key | Default | Description |
|---------|-----|---------|-------------|
| `research` | `keywords` | `["agent", ...]` | arXiv search keywords |
| | `categories` | `["cs.AI", ...]` | arXiv categories |
| | `multi_source` | `false` | Enable arXiv+S2+PwC+GitHub |
| `filter` | `min_abstract_score` | `3.0` | Minimum abstract relevance |
| `evaluate` | `trials_per_test` | `10` | Trials per benchmark task |
| `decide` | `min_success_rate_delta` | `0.05` | Minimum improvement to keep |
| | `max_cost_increase_ratio` | `1.2` | Max acceptable cost multiplier |
| `pipeline` | `auto_promote` | `false` | Auto-deploy on keep decision |
| `lifecycle` | `max_active_skills` | `10` | Maximum active skills |
| | `inactivity_days` | `30` | Days before archive |
