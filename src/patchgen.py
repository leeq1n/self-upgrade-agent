"""
Code patch generation from research papers.

Replaces skillgen.py for the agent self-modification use case.
Outputs executable Python code that replaces/enhances core agent modules.
"""
import json, logging
from src.llm import chat, LLMConfig
from src.research import Paper

logger = logging.getLogger(__name__)


def generate_patch(paper: Paper, target_module: str = "planner.py", llm_config=None) -> dict:
    """
    Generate a code patch for a core agent module from a paper.
    
    Args:
        paper: Paper with method/algorithm to implement
        target_module: Which core/*.py file to patch (agent.py, planner.py, etc.)
    
    Returns:
        {"function": "...", "test": "...", "module": "planner.py"} or None
    """
    prompt = (
        f"You are an expert AI engineer. Based on this paper, write improved code "
        f"for the agent's {target_module} module.\n\n"
        f"Paper: {paper.title}\n"
        f"Abstract: {paper.abstract}\n\n"
        f"Write a COMPLETE replacement Python file for {target_module}.\n"
        f"Include at least 3 test cases that verify the improvements.\n\n"
        f"Output ONLY valid JSON:"
        f'{{"function": "def improved_plan(...)\n    ...", '
        f'"test": "def test_plan()\n    assert ...", '
        f'"module": "{target_module}"}}'
    )

    resp = chat(
        messages=[{"role": "user", "content": prompt}],
        config=llm_config,
        response_format={"type": "json_object"},
    )

    if not resp.content:
        return None

    try:
        data = json.loads(resp.content)
        fn = data.get("function", "")
        t = data.get("test", "")
        if fn and len(fn) > 50 and t and len(t) > 30:
            return {"function": fn, "test": t, "module": data.get("module", target_module)}
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.warning(f"Patch generation JSON parse failed: {e}")

    return None
