"""src/mcp_client.py — minimal in-process MCP client.

Aligns with user's "MCP-everything" idea: memory ops are tool calls.

Why an in-process client (not stdio/network MCP):
  - We're a single-process agent; spawning a separate MCP server
    subprocess adds complexity we don't need yet.
  - The interface is identical to a real MCP call (call_tool), so
    swapping in a real server later is one import change.
  - Production can later route to a real MCP server over stdio/HTTP
    by changing `_dispatch()`.

The contract: every tool is `(name, **kwargs) -> Any`.  Tools register
themselves via `register_tool()`.  The agent calls `call_tool(name, ...)`.

Usage:
    from src.mcp_client import call_tool, list_tools
    tools = list_tools()
    result = call_tool("memory_search", query="agent reasoning", top_k=3)
"""
import logging
from typing import Any, Callable, Dict, List, Tuple

logger = logging.getLogger(__name__)


# Tool registry: name -> (callable, description, schema_dict)
_TOOLS: Dict[str, Tuple[Callable, str, Dict[str, Any]]] = {}


def register_tool(name: str, description: str, schema: Dict[str, Any]):
    """Decorator to register a function as an MCP tool.

    Args:
        name: tool name (e.g. "memory_search")
        description: human-readable description for LLM prompts
        schema: JSON-Schema-like dict describing kwargs (informational
            for v1.8.2; not enforced yet — see design doc §6).
    """
    def deco(fn: Callable) -> Callable:
        if name in _TOOLS:
            raise ValueError(f"tool {name!r} already registered")
        _TOOLS[name] = (fn, description, schema)
        return fn
    return deco


def call_tool(name: str, timeout_s: float = 10.0, **kwargs) -> Any:
    """Call a registered tool by name.

    Args:
        name: tool name (must be registered)
        timeout_s: accepted for API parity with real MCP (stdio/HTTP)
            clients.  In-process tools do NOT enforce it — they run as
            fast as Python allows.  When we swap in a real MCP server,
            this arg becomes meaningful.
        **kwargs: tool arguments

    Returns:
        Whatever the tool returns.

    Raises:
        KeyError: tool name not registered
        TypeError: wrong kwargs (raised by the function itself)
    """
    if name not in _TOOLS:
        raise KeyError(
            f"tool {name!r} not registered. "
            f"Available: {sorted(_TOOLS)}"
        )
    fn, desc, schema = _TOOLS[name]
    logger.debug(f"mcp_client.call_tool({name}, {list(kwargs)})")
    return fn(**kwargs)


def list_tools() -> List[Dict[str, Any]]:
    """List all registered tools.  Used to populate LLM prompts."""
    return [
        {"name": name, "description": desc, "schema": schema}
        for name, (_, desc, schema) in _TOOLS.items()
    ]


def tool_count() -> int:
    """Number of registered tools."""
    return len(_TOOLS)


def unregister(name: str) -> None:
    """Remove a tool.  Mainly for tests."""
    _TOOLS.pop(name, None)


def clear_registry() -> None:
    """Remove all tools.  Mainly for tests."""
    _TOOLS.clear()