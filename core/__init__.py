"""Self-Upgrade Agent core modules.

These modules are the TARGETS for autonomous improvement.
The pipeline generates code patches that modify these files.
"""
__version__ = "1.1.0"

from core.agent import run, register_tool, call_tool, list_tools
from core.planner import plan_task

__all__ = ["run", "register_tool", "call_tool", "list_tools", "plan_task"]
