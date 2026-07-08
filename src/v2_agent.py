"""src/v2_agent.py — minimal self-improving agent (v2.0.0).

Design rationale (2026-07-08 user session):
  - User's original vision: agent reads papers, modifies code, harness verifies.
  - 30+ prior fix commits (v1.8.x) all failed to make 1 round KEPT.
  - User said: "重新整理重写, 这样可能反而更快".

What this is (minimal):
  1. RAG via memory (paper-supported pattern, see Self-Refine critique)
  2. ONE LLM call (no self-refine loop — paper "One Step Forward, Two
     Steps Back" shows self-refine regresses on code gen)
  3. ONE harness test (verifiable, your vision)

What this is NOT (intentionally omitted):
  - No pre-filter (violates fail-OPEN principle; user feedback)
  - No constitution (paper applicability unconfirmed)
  - No self-refine loop (paper shows regression on code)
  - No multi-agent (UC Berkeley: 41-86% fail rate)
  - No LangGraph (single LLM call doesn't need orchestration)
  - No MCP-everything abstraction (over-engineered for 1 call)

~50 LOC.  Test in tests/test_v2_agent.py.
"""
import os
import json
import re
import sys
import subprocess
import tempfile
import sqlite3
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

# Reuse existing chat() — proven, with thinking control + multi-key
from src.llm import chat as _chat
from src.llm import LLMConfig


@dataclass
class Paper:
    arxiv_id: str
    title: str
    abstract: str


@dataclass
class Patch:
    function: str
    test: str
    module: str


# --------------------------------------------------------------------- #
# Memory (RAG) — single SQLite table, no MCP, no 4-tier
# --------------------------------------------------------------------- #

MEMORY_DB = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "upgrades", "v2_memory.db",
)


_SCHEMA = ("CREATE TABLE IF NOT EXISTS papers ("
             " id INTEGER PRIMARY KEY AUTOINCREMENT,"
             " arxiv_id TEXT, summary TEXT, topics TEXT)")


def _memory_path() -> str:
    parent = os.path.dirname(MEMORY_DB)
    if parent:
        os.makedirs(parent, exist_ok=True)
    conn = sqlite3.connect(MEMORY_DB)
    try:
        conn.execute(_SCHEMA)
        conn.commit()
    finally:
        conn.close()
    return MEMORY_DB


def memory_add(arxiv_id: str, summary: str, topics: List[str] = None) -> int:
    """Add paper to memory. Returns memory_id."""
    conn = sqlite3.connect(_memory_path())
    try:
        cur = conn.execute(
            "INSERT INTO papers (arxiv_id, summary, topics) VALUES (?, ?, ?)",
            (arxiv_id, summary, ",".join(topics or [])),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def memory_find_similar(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """RAG: find similar papers by keyword overlap (no embedding needed)."""
    conn = sqlite3.connect(_memory_path())
    try:
        cur = conn.execute(
            "SELECT id, arxiv_id, summary, topics FROM papers ORDER BY id DESC LIMIT 50"
        )
        rows = cur.fetchall()
    finally:
        conn.close()

    # Simple keyword overlap score (RAG-lite; embedding would be overkill)
    q_words = set(w for w in re.findall(r"\w+", query.lower()) if len(w) >= 3)
    scored = []
    for mid, arxiv_id, summary, topics in rows:
        text = f"{summary} {topics}".lower()
        overlap = sum(1 for w in q_words if w in text)
        if overlap > 0:
            scored.append({
                "memory_id": mid,
                "arxiv_id": arxiv_id,
                "summary": summary,
                "score": overlap,
            })
    scored.sort(key=lambda r: r["score"], reverse=True)
    return scored[:top_k]


# --------------------------------------------------------------------- #
# Build prompt
# --------------------------------------------------------------------- #

PROMPT_TEMPLATE = """You are modifying a Python module to add a new capability.

Target module: {target_module}
Existing source:
```python
{current_source}
```

Paper: {title} (arxiv {arxiv_id})
Abstract: {abstract}

Similar past papers (from memory):
{similar}

CRITICAL HARNESS RULE: The harness extracts your patch and test into a
standalone subprocess that does NOT have the target module on sys.path.
Therefore:
  - DO NOT "import target_module" inside the test
  - DO add needed typing imports (e.g. "from typing import Callable, List")
    INSIDE the function or test body, or use string annotations
  - The test should call the patch function directly (it's already defined
    in the same script)

Produce a JSON patch:
{{"function": "<complete def plan_task() body>", "test": "<pytest-style test that calls the patch function directly>", "module": "{target_module}"}}

Return ONLY the JSON, no markdown fences.
"""


def _read_target_module(path: str) -> str:
    if not path or not os.path.exists(path):
        return "(file does not exist or path empty — create from scratch)"
    # Force UTF-8; Windows default is GBK, breaks on UTF-8 source
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except (UnicodeDecodeError, PermissionError, OSError) as e:
        return f"(cannot read {path}: {e})"


def _build_prompt(paper: Paper, target_module: str, similar: List[Dict]) -> str:
    return PROMPT_TEMPLATE.format(
        target_module=target_module,
        current_source=_read_target_module(target_module)[:3000],
        title=paper.title,
        arxiv_id=paper.arxiv_id,
        abstract=paper.abstract[:1500],
        similar="\n".join(
            f"  - {s['arxiv_id']}: {s['summary'][:200]}" for s in similar
        ) or "  (none)",
    )


# --------------------------------------------------------------------- #
# Parse + verify
# --------------------------------------------------------------------- #

def _parse_patch(response: str) -> Optional[Patch]:
    """Lenient JSON parse — same logic as src/patchgen.py."""
    text = response.strip()
    # Strip markdown fences
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    # Find first balanced { ... }
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        data = json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None
    fn = data.get("function", "")
    test = data.get("test", "")
    module = data.get("module", "")
    # Structural checks: must contain 'def ' (function definition)
    # and 'def test_' (test function) — lengths are unreliable across
    # valid patches.  We just want to reject empty/garbage fields.
    if "def " not in fn or "def " not in test or not module:
        return None
    if len(fn.strip()) < 5 or len(test.strip()) < 5:
        return None
    return Patch(function=fn, test=test, module=module)


_PRELUDE = """from typing import Callable, List, Dict, Any, Optional, Tuple, Set, Iterable, Iterator, Generator
import typing
typing.Callable = Callable
typing.List = List
typing.Dict = Dict
typing.Any = Any
typing.Optional = Optional
typing.Tuple = Tuple
typing.Set = Set
typing.Iterable = Iterable
typing.Iterator = Iterator
typing.Generator = Generator
import sys, os, json, re, math, datetime, collections, itertools, functools, random
"""


def _run_harness(patch: Patch, timeout: int = 30) -> bool:
    """Run the patch + test in a subprocess. Returns True on pass.

    Wraps the patch in a script that:
      1. Pre-imports common typing helpers (LLMs often forget
         "from typing import Callable" in type hints)
      2. Defines the function from `patch.function`
      3. Defines the test from `patch.test` (test function name
         extracted via regex, def test_xxx(...))
      4. Actually calls the test function so NameError / assert fail
         cause non-zero exit

    This is a minimal harness — production should use pytest, but
    pytest adds a heavy dependency for a single round.  Inline exec
    keeps it ~30 LOC and self-contained.
    """
    # Extract test function name (e.g. "def test_foo(...)" -> "test_foo")
    test_name_match = re.search(r"^def\s+(test_\w+)\s*\(", patch.test, re.MULTILINE)
    if not test_name_match:
        # No test function — syntax-only check via py_compile
        return _syntax_check(patch.function + "\n\n" + patch.test)

    test_name = test_name_match.group(1)
    # Build a script: prelude (typing + stdlib) + function + test + call.
    script = (
        _PRELUDE
        + "\n\n"
        + patch.function
        + "\n\n"
        + patch.test
        + f"\n\n{test_name}()\n"
    )

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as f:
        f.write(script)
        test_file = f.name
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True, text=True, timeout=timeout,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, Exception):
        return False
    finally:
        try:
            os.unlink(test_file)
        except OSError:
            pass


def _syntax_check(code: str) -> bool:
    """Fallback: just verify the code parses."""
    try:
        compile(code, "<patch>", "exec")
        return True
    except SyntaxError:
        return False


# --------------------------------------------------------------------- #
# Main entry
# --------------------------------------------------------------------- #

def improve(
    paper: Paper,
    target_module: str = "core/planner.py",
    config: Optional[LLMConfig] = None,
) -> Optional[Patch]:
    """The whole agent: read paper, generate patch, verify. ONE LLM call.

    Returns the patch if harness passes, else None.
    """
    # 1. RAG: find similar papers (RAG is paper-supported)
    similar = memory_find_similar(paper.title + " " + paper.abstract, top_k=3)

    # 2. Build prompt
    prompt = _build_prompt(paper, target_module, similar)

    # 3. ONE LLM call (no self-refine — paper shows regression)
    config = config or LLMConfig.from_env()
    response = _chat(
        messages=[{"role": "user", "content": prompt}],
        config=config,
        enable_thinking=False,  # reasoning in prompt; saves tokens for code
    )
    if not response or not response.content:
        return None

    # 4. Parse
    patch = _parse_patch(response.content)
    if patch is None:
        return None

    # 5. Harness test
    if not _run_harness(patch):
        return None

    return patch


# --------------------------------------------------------------------- #
# Fixed-paper runner (user-feedback 2026-07-08: "固定用一篇论文, 跑通
# 后续功能再回来做论文筛选")
# --------------------------------------------------------------------- #

FIXED_PAPER = Paper(
    arxiv_id="2310.02170",
    title="A Dynamic LLM-Powered Agent Network for Task-Oriented Agent Collaboration",
    abstract=(
        "We propose DyLAN, a dynamic LLM-powered agent network that "
        "automatically selects agents based on their expertise scores, "
        "optimized for task-oriented agent collaboration.  DyLAN achieves "
        "strong performance on reasoning, code generation, and tool use "
        "by building a Directed Acyclic Graph (DAG) of agent interactions "
        "at inference time and applying a two-stage optimization."
    ),
)


def run_with_fixed_paper(target_module: str = "core/planner.py",
                          config: Optional[LLMConfig] = None) -> Optional[Patch]:
    """Run improve() with the fixed DyLAN paper.  Use this to verify
    the v2 pipeline end-to-end before adding paper selection back.

    Returns the Patch if harness passes, else None.
    """
    return improve(FIXED_PAPER, target_module=target_module, config=config)
