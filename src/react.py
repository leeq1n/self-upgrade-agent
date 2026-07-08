"""src/react.py — ReAct action loop (small, focused, ~150 LOC).

ReAct = Reasoning + Acting (Yao et al., 2022).  The agent iterates:
  Thought: <reasoning>
  Action: <tool_name>
  Action Input: <kwargs>
  Observation: <tool result>
  ... loop ...
  Final Answer: <result>

This module implements the loop.  It does NOT define tools; tools
are registered via src/mcp_client.  It does NOT know about papers
or memory — those are tools.

Why a separate module instead of inlining in pipeline_lg:
  - Reusable from multiple call sites (patchgen, filter, future agents)
  - Easier to test in isolation
  - Single place to add ReAct-specific features (loop bounds, scratchpad)

Why not LangChain/LangGraph:
  - We already have chat() + mcp_client; ReAct is just a prompt format
    and a parsing loop.  ~150 LOC is honest; LangChain is ~5000 LOC.
  - User's "奥卡姆" principle: prefer explicit code over framework.

v1.8.2 limitations:
  - No streaming output (LLM response is full message)
  - No parallel tool calls (sequential)
  - No memory between sessions (use src/memory_server for that)
"""
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from src.llm import chat
from src.mcp_client import call_tool, list_tools

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------- #

@dataclass
class ReActConfig:
    """ReAct loop configuration.

    Attributes:
        max_iterations: hard cap on Thought/Action cycles.  Default 8.
        tools_desc_chars: max chars of tool descriptions in prompt.
        scratchpad_max_chars: truncate scratchpad if it grows beyond this.
        on_step: optional callback(iteration, thought, action, observation)
                 for observability (logging, memory writes, etc.)
    """
    max_iterations: int = 8
    tools_desc_chars: int = 4000
    scratchpad_max_chars: int = 8000
    on_step: Optional[Callable[[int, str, Optional[str], Optional[str]], None]] = None


# --------------------------------------------------------------------- #
# Parsing helpers
# --------------------------------------------------------------------- #

# Match "Action: tool_name" or "Action: [tool_name]" — optional brackets
_ACTION_RE = re.compile(r"^Action:\s*\[?(\w+)\]?\s*$", re.MULTILINE)
_ACTION_INPUT_RE = re.compile(
    r"Action\s+Input:\s*(.+?)(?=\n(?:Observation:|Thought:|Final Answer:|$))",
    re.DOTALL,
)
_THOUGHT_RE = re.compile(
    r"Thought:\s*(.+?)(?=\n(?:Action:|Final Answer:|$))", re.DOTALL
)
_FINAL_ANSWER_RE = re.compile(
    r"Final Answer:\s*(.+?)$", re.DOTALL
)


@dataclass
class ReactStep:
    """One iteration of the loop."""
    iteration: int
    thought: str
    action: Optional[str]
    action_input: Optional[Dict[str, Any]]
    observation: Optional[str]
    is_final: bool = False
    final_answer: Optional[str] = None


def parse_llm_step(text: str) -> ReactStep:
    """Parse one Thought/Action/Action Input/Final Answer from LLM output.

    Returns a ReactStep.  If 'Final Answer:' is present, is_final=True
    and final_answer is set.
    """
    final = _FINAL_ANSWER_RE.search(text)
    if final:
        return ReactStep(
            iteration=0,
            thought="",
            action=None,
            action_input=None,
            observation=None,
            is_final=True,
            final_answer=final.group(1).strip(),
        )

    thought_match = _THOUGHT_RE.search(text)
    thought = thought_match.group(1).strip() if thought_match else ""

    action_match = _ACTION_RE.search(text)
    action = action_match.group(1) if action_match else None

    action_input: Optional[Dict[str, Any]] = None
    if action:
        input_match = _ACTION_INPUT_RE.search(text)
        if input_match:
            raw = input_match.group(1).strip()
            action_input = _parse_action_input(raw)

    return ReactStep(
        iteration=0,
        thought=thought,
        action=action,
        action_input=action_input,
        observation=None,
    )


def _parse_action_input(raw: str) -> Dict[str, Any]:
    """Best-effort parse of Action Input.

    Tries JSON first; falls back to a simple key=value parser.
    """
    import json
    raw = raw.strip()
    # Try JSON
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    # Try key=value lines
    out: Dict[str, str] = {}
    for line in raw.splitlines():
        if "=" in line:
            k, _, v = line.partition("=")
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k:
                out[k] = v
    return out


# --------------------------------------------------------------------- #
# Prompt template
# --------------------------------------------------------------------- #

_REACT_SYSTEM_TEMPLATE = """\
You are a self-upgrade agent.  Solve tasks using available tools.

Format (mandatory):
Thought: <your reasoning>
Action: <tool_name>
Action Input: <key=value or JSON>
Observation: <result of action — filled by the system, NOT by you>
... (repeat Thought/Action/Observation as needed) ...
Final Answer: <your answer to the original task>

Rules:
  - Always start with Thought.
  - Use one of the available tools via Action.
  - Stop after Action Input; do NOT write Observation yourself.
  - When done, write 'Final Answer: <text>'.
  - If a tool returns an error, think about whether to retry with
    different args or use a different tool.

Available tools:
{tools}
"""


def _format_tools_for_prompt(tools_desc_chars: int = 4000) -> str:
    """Format registered tools for the system prompt."""
    tools = list_tools()
    lines = []
    total = 0
    for t in tools:
        line = f"- {t['name']}: {t['description']}"
        if total + len(line) > tools_desc_chars:
            break
        lines.append(line)
        total += len(line)
    return "\n".join(lines) if lines else "(no tools registered)"


# --------------------------------------------------------------------- #
# Main loop
# --------------------------------------------------------------------- #

def run_react(
    task: str,
    config: Optional[ReActConfig] = None,
    enable_thinking: Optional[bool] = None,
    thinking_budget: Optional[int] = None,
) -> Dict[str, Any]:
    """Run a ReAct loop on a task.  Returns dict with:
        - final_answer: str or None
        - transcript: list of ReactStep
        - iterations: int
        - error: str or None
    """
    cfg = config or ReActConfig()
    system_prompt = _REACT_SYSTEM_TEMPLATE.format(
        tools=_format_tools_for_prompt(cfg.tools_desc_chars)
    )
    scratchpad = f"Question: {task}\n\n"
    transcript: List[ReactStep] = []

    for i in range(1, cfg.max_iterations + 1):
        prompt = scratchpad + "Thought:"
        response = chat(
            messages=[{"role": "user", "content": prompt}],
            system=system_prompt,
            enable_thinking=enable_thinking,
            thinking_budget=thinking_budget,
        )
        if response.error:
            return {
                "final_answer": None,
                "transcript": transcript,
                "iterations": i - 1,
                "error": f"LLM error: {response.error}",
            }
        llm_text = response.content
        step = parse_llm_step(llm_text)
        step.iteration = i

        if step.is_final:
            transcript.append(step)
            if cfg.on_step:
                cfg.on_step(i, "", None, None)
            return {
                "final_answer": step.final_answer,
                "transcript": transcript,
                "iterations": i,
                "error": None,
            }

        # Execute action
        observation_text = ""
        if step.action:
            try:
                obs = call_tool(step.action, **(step.action_input or {}))
                observation_text = _format_observation(obs)
            except KeyError as e:
                observation_text = f"Error: tool not found: {e}"
            except Exception as e:
                observation_text = f"Error: {type(e).__name__}: {e}"
        else:
            observation_text = (
                "Error: no Action in your output.  You must include "
                "'Action: <tool_name>' followed by 'Action Input: ...'"
            )

        step.observation = observation_text
        transcript.append(step)

        # Append to scratchpad (with truncation if too long)
        scratchpad += (
            f" {step.thought}\n"
            f"Action: {step.action or '(none)'}\n"
            f"Action Input: {_format_action_input(step.action_input)}\n"
            f"Observation: {observation_text}\n\n"
        )
        if len(scratchpad) > cfg.scratchpad_max_chars:
            # Keep the question + tail
            tail = scratchpad[-cfg.scratchpad_max_chars:]
            scratchpad = (
                f"Question: {task}\n\n"
                f"... (scratchpad truncated) ...\n\n"
                f"{tail}"
            )

        if cfg.on_step:
            cfg.on_step(i, step.thought, step.action, observation_text)

    # Hit max_iterations without Final Answer
    return {
        "final_answer": None,
        "transcript": transcript,
        "iterations": cfg.max_iterations,
        "error": "max_iterations reached without Final Answer",
    }


def _format_observation(obs: Any) -> str:
    """Format a tool observation for the scratchpad."""
    if isinstance(obs, str):
        return obs
    if isinstance(obs, (dict, list)):
        import json
        try:
            return json.dumps(obs, ensure_ascii=False, indent=2)
        except (TypeError, ValueError):
            return str(obs)
    return str(obs)


def _format_action_input(action_input: Optional[Dict[str, Any]]) -> str:
    if not action_input:
        return "(none)"
    import json
    try:
        return json.dumps(action_input, ensure_ascii=False)
    except (TypeError, ValueError):
        return str(action_input)