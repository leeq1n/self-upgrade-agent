"""
Self-Upgrade Agent 核心 —— 可被自主改进的推理引擎。

架构：
  agent.py   — 主推理循环 (run)
  tools.py   — 工具调用接口
  planner.py — 任务规划模块 (可被 patch 改进)

每个模块都是独立的 .py 文件，patchgen 可以单独修改任意模块。
"""
__version__ = "1.0.0"
import json, time
from core.planner import plan_task
from typing import List, Dict, Optional, Callable



# ── 配置 ──────────────────────────────────────────
MAX_TURNS = 10
MAX_TOOL_CALLS = 5

# ── 工具注册表 ─────────────────────────────────────
_TOOLS: dict = {}

def register_tool(name: str, fn, description: str = ""):
    _TOOLS[name] = fn
    fn.__tool_description__ = description

def list_tools():
    return [{"name": n, "description": getattr(f, "__tool_description__", "")} for n, f in _TOOLS.items()]

def call_tool(name: str, **kwargs):
    if name not in _TOOLS:
        return f"Tool '{name}' not registered. Available: {list(_TOOLS.keys())}"
    try:
        return str(_TOOLS[name](**kwargs))
    except Exception as e:
        return f"Tool error: {e}"


# ── 推理循环 ────────────────────────────────────────

def run(
    task: str,
    llm_call: Callable,
    max_turns: int = MAX_TURNS,
    verbose: bool = False,
) -> Dict:
    """
    主推理循环：规划 → 执行 → 反思。
    
    返回值包含执行结果、耗时、步数等指标。
    """
    # Auto-register built-in tools
    from core.tools import tool_shell, tool_read_file, tool_calculate
    register_tool("shell", tool_shell, "Run a shell command")
    register_tool("read", tool_read_file, "Read a file")
    register_tool("calc", tool_calculate, "Evaluate a math expression")
    
    t0 = time.time()
    results = []

    # 1. 规划
    plan = plan_task(task, llm_call)
    if verbose:
        print(f"  Plan: {len(plan)} steps")

    # 2. 执行
    success_count = 0
    for i, step in enumerate(plan[: max_turns]):
        if verbose:
            print(f"  Step {i+1}: {step[:60]}")

        # 尝试使用工具
        tool_result = None
        tool_names = list(_TOOLS.keys())
        if tool_names and i < MAX_TOOL_CALLS:
            tool_prompt = (
                f"Task step: {step}\n"
                f"Available tools: {', '.join(tool_names)}\n"
                f"Reply with tool_name: args (or 'none' if no tool needed)"
            )
            tool_result = llm_call(tool_prompt)
            if tool_result and tool_result.lower() != "none":
                try:
                    parts = tool_result.split(":", 1)
                    name = parts[0].strip()
                    body = parts[1].strip() if len(parts) > 1 else ""
                    result = call_tool(name, query=body)
                    if verbose:
                        print(f"    Tool {name}: {str(result)[:60]}")
                    if "error" not in str(result).lower():
                        success_count += 1
                except Exception as e:
                    if verbose:
                        print(f"    Tool error: {e}")

            results.append({"step": step, "tool_used": tool_result if "tool_result" in dir() else None})

    elapsed = time.time() - t0
    return {
        "success": success_count > 0,
        "task": task,
        "steps_planned": len(plan),
        "steps_executed": len(results),
        "tools_used": success_count,
        "elapsed": round(elapsed, 3),
        "logs": results,
    }


# ── 快捷入口 ────────────────────────────────────────

def quick_test(task: str) -> Dict:
    """使用默认 LLM 快速测试 agent。"""
    from src.llm import chat_simple, LLMConfig
    lc = LLMConfig.from_env()

    def _call(prompt):
        return chat_simple(prompt, config=lc) or ""

    return run(task, _call)
