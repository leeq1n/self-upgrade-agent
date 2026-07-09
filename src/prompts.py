"""Project prompts — the "static prompt" layer.

Per user feedback 2026-07-08:
  - '启动 prompt 越少越好, 实体承担重要作用'
  - '抽象层 = 虚函数 / 抽象函数范式'

This module is the ONE place where prompts live.  Per-role
prompts (one per use case) are defined here as module-level
constants.  No inline f-string templates scattered in code.

Why a separate file:
  - Single source of truth for prompt content
  - Easy to grep / version control / review
  - The "entity" (v2_agent, v2_apply, v2_round) consumes this
    as an abstract dependency — same as OOP's interface contract

Rule: each prompt must be < 500 tokens.  If you need more, the
task is too complex — split into multiple calls or move detail
to entity behavior (see v2_agent._PRELUDE for the harness-level
auto-injection pattern).

HARNESS BEHAVIOR (entity, not prompt):
  - typing imports auto-injected via v2_agent._PRELUDE
  - test extracted into subprocess with patch.function in same scope
  - target module not on sys.path (so don't reference it)
The LLM doesn't need to know this — the entity handles it.
"""

# --------------------------------------------------------------------- #
# v2_agent prompts (Paper -> Patch)
# --------------------------------------------------------------------- #

V2_GENERATE_PATCH = """You modify a Python module to add a new capability.

Target: {target_module}
Existing source:
```python
{current_source}
```

Paper: {title} (arxiv {arxiv_id})
Abstract: {abstract}

Similar past papers:
{similar}

Return a JSON object: {{"function": "<def plan_task(...)>", "test": "<pytest-style test>", "module": "{target_module}"}}

JSON only, no fences, no commentary."""


# --------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------- #

PROMPTS = {
    "v2_generate_patch": V2_GENERATE_PATCH,
}