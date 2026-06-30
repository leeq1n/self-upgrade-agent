"""Task planner — decomposes goals into executable steps.

This module is the PRIMARY target for self-improvement.
Papers about new planning algorithms generate patches for this file.
"""
__version__ = "1.0.0"
from typing import List, Callable


def plan_task(task: str, llm_call: Callable) -> List[str]:
    """Decompose a task into ordered steps."""
    prompt = (
        f"Break this task into 3-5 numbered steps. Reply only with the steps:\n{task}"
    )
    result = llm_call(prompt)
    steps = []
    for line in result.split("\n"):
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith("- ")):
            steps.append(line)
    if not steps:
        steps = [f"Do: {task}"]
    return steps
