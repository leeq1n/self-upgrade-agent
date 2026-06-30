"""Self-Upgrade Agent core modules.

These modules are the TARGETS for autonomous improvement.
The pipeline generates code patches that modify these files.

Usage: python -m core.agent "your task here"
"""
__version__ = "1.3.0"

# Lazy imports to avoid 'found in sys.modules' warning when using python -m core.agent
__all__ = ["run", "register_tool", "call_tool", "list_tools", "plan_task"]


def __getattr__(name):
    if name == "run":
        from core.agent import run as _run
        return _run
    if name == "register_tool":
        from core.agent import register_tool as _rt
        return _rt
    if name == "call_tool":
        from core.agent import call_tool as _ct
        return _ct
    if name == "list_tools":
        from core.agent import list_tools as _lt
        return _lt
    if name == "plan_task":
        from core.planner import plan_task as _pt
        return _pt
    raise AttributeError(f"module 'core' has no attribute '{name}'")
