"""src/langchain_bridge.py — LangChain ChatModel wrapper for src/llm.chat().

Why this exists:
  LangGraph's create_react_agent requires a LangChain-compatible
  chat model (BaseChatModel).  Our src/llm.py uses httpx directly
  to call OpenAI-compatible endpoints, NOT LangChain.  This module
  bridges the two: LangGraph code can use our chat() underneath.

What it does:
  - HermesChatModel._generate(messages, ...) → ChatResult
  - Converts LangChain messages (SystemMessage, HumanMessage, AIMessage
    with tool_calls) into our chat() prompt format
  - Calls our chat() (which handles per-call thinking control, timeouts,
    retries, multi-key rotation)
  - Parses the response:
    - If JSON with tool_calls: return AIMessage with tool_calls
    - If plain text: return AIMessage(content=text)
  - bind_tools() inherited from BaseChatModel — LangGraph uses it
    to inject the tool list into the prompt

What it does NOT do:
  - No streaming (LangGraph astream_events not used; pipeline doesn't
    stream)
  - No multimodal / vision (out of scope)
  - No token counting (out of scope)
  - No caching (out of scope)
  - No async (_agenerate uses default sync _generate wrapper)

Tool-call format:
  The LLM is expected to reply with JSON of this shape:
    {"function": "<src>", "test": "<src>", "module": "<name>"}
  OR
    {"name": "tool_name", "arguments": {...}}

  We use the FIRST form (matches our existing patchgen JSON shape) and
  convert to LangChain's tool_calls format.

Why we don't break src/llm.py:
  src/llm.chat() remains the source of truth for LLM calls.  This
  bridge is a thin adapter that calls chat() and translates I/O.  No
  httpx, no retries, no quota logic duplicated.
"""
import json
import logging
from typing import Any, Dict, List, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage,
)
from langchain_core.outputs import ChatGeneration, ChatResult

logger = logging.getLogger(__name__)


class HermesChatModel(BaseChatModel):
    """LangChain-compatible chat model backed by src/llm.chat().

    Usage:
        from src.langchain_bridge import HermesChatModel
        from langgraph.prebuilt import create_react_agent

        model = HermesChatModel()
        agent = create_react_agent(model, tools)
        result = agent.invoke({"messages": [HumanMessage(content="...")]})
    """

    # LangChain contract
    @property
    def _llm_type(self) -> str:
        return "hermes"

    # Tools bound via bind_tools(); None if no tools bound
    bound_tools: Optional[List[Dict[str, Any]]] = None

    # Configuration injected at construction time
    config: Optional[Any] = None  # LLMConfig from src.llm
    enable_thinking: bool = True
    thinking_budget: Optional[int] = 2048

    model_config = {"arbitrary_types_allowed": True}

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Convert messages → prompt → call chat() → ChatResult."""
        # Lazy import to avoid hard LangChain dep at module-load time
        from src.llm import chat as _chat
        from src.llm import LLMConfig

        # 0. If tools bound, inject into the system message
        tool_block = self._format_tools_for_prompt()
        if tool_block:
            if messages and isinstance(messages[0], SystemMessage):
                messages = [
                    SystemMessage(content=messages[0].content + "\n\n" + tool_block),
                    *messages[1:],
                ]
            else:
                messages = [SystemMessage(content=tool_block), *messages]

        # 1. Translate messages to OpenAI-compatible dict format
        lc_messages: List[Dict[str, Any]] = []
        for m in messages:
            if isinstance(m, SystemMessage):
                lc_messages.append({"role": "system", "content": m.content})
            elif isinstance(m, HumanMessage):
                lc_messages.append({"role": "user", "content": m.content})
            elif isinstance(m, AIMessage):
                # If previous AI made tool calls, include them so the
                # next tool result can be matched.
                if m.tool_calls:
                    lc_messages.append({
                        "role": "assistant",
                        "content": m.content or "",
                        "tool_calls": [
                            {
                                "id": tc.get("id", f"call_{i}"),
                                "type": "function",
                                "function": {
                                    "name": tc["name"],
                                    "arguments": json.dumps(tc.get("args", {})),
                                },
                            }
                            for i, tc in enumerate(m.tool_calls)
                        ],
                    })
                else:
                    lc_messages.append({"role": "assistant", "content": m.content or ""})
            elif isinstance(m, ToolMessage):
                lc_messages.append({
                    "role": "tool",
                    "tool_call_id": m.tool_call_id,
                    "content": m.content if isinstance(m.content, str) else json.dumps(m.content),
                })
            else:
                # Fallback for unknown types
                lc_messages.append({"role": "user", "content": str(m.content)})

        # 2. Call our existing chat() (preserves thinking control, timeouts, retries)
        config = self.config if self.config is not None else LLMConfig.from_env()
        response = _chat(
            messages=lc_messages,
            config=config,
            enable_thinking=self.enable_thinking,
            thinking_budget=self.thinking_budget,
        )

        # 3. Build AIMessage, parsing tool_calls if present
        if response.error:
            # Surface error as a plain AIMessage; LangGraph will see
            # empty content and likely error on the tool call.  This
            # matches the existing pipeline_lg behavior (no-op on error).
            ai_msg = AIMessage(content=f"[LLM error: {response.error}]")
            return ChatResult(generations=[ChatGeneration(message=ai_msg)])

        content = response.content or ""
        tool_calls = self._parse_tool_calls(content)
        ai_msg = AIMessage(
            content="" if tool_calls else content,
            tool_calls=tool_calls if tool_calls else [],
        )
        return ChatResult(generations=[ChatGeneration(message=ai_msg)])

    def _parse_tool_calls(self, content: str) -> List[Dict[str, Any]]:
        """Parse tool calls from the LLM's response.

        Supports two formats:
          A. Patchgen-style: {"function": "<src>", "test": "<src>",
                              "module": "<name>"}
          B. ReAct-style: {"name": "<tool>", "arguments": {...}}
        Both return a list of tool_calls in LangChain format.
        """
        if not content or not content.strip():
            return []
        # Try to extract the first JSON object in the content
        # (some models wrap JSON in ```json ... ``` fences)
        text = content.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()
        # Find first { ... } block
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return []
        try:
            data = json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            return []

        # Patchgen-style: function + test + module → single "patch" tool call
        if isinstance(data, dict) and "function" in data and "test" in data:
            return [{
                "id": "call_0",
                "name": "submit_patch",
                "args": {
                    "function": data["function"],
                    "test": data.get("test", ""),
                    "module": data.get("module", ""),
                },
            }]
        # ReAct-style: name + arguments
        if isinstance(data, dict) and "name" in data and "arguments" in data:
            args = data["arguments"]
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    args = {"raw": args}
            return [{
                "id": "call_0",
                "name": data["name"],
                "args": args,
            }]
        return []

    def bind_tools(
        self,
        tools: List[Any],
        **kwargs: Any,
    ):
        """Bind tools to the model.

        Tools are passed to our existing prompt via the
        list_tools()-style registry.  LangGraph uses this to
        inject the tool list so the LLM knows what's available.

        v1.8.3 limitation: we don't change the wire format with
        the model.  Instead, we serialize the tool descriptions
        into the system message at _generate() time.  This keeps
        our existing chat() unchanged while still giving LangGraph
        the bound-tools semantics it needs.

        Returns a NEW HermesChatModel with bound_tools set;
        LangGraph treats this as a RunnableBinding-compatible object.
        """
        # Normalize tools to a list of dicts (name, description, schema)
        normalized: List[Dict[str, Any]] = []
        for t in tools:
            if isinstance(t, dict):
                normalized.append(t)
            elif hasattr(t, "name") and hasattr(t, "description"):
                # LangChain BaseTool
                normalized.append({
                    "name": t.name,
                    "description": t.description,
                })
            elif callable(t):
                # Python function: extract name + docstring
                normalized.append({
                    "name": getattr(t, "__name__", "tool"),
                    "description": (t.__doc__ or "").split("\n")[0],
                })
            else:
                normalized.append({"name": str(t), "description": ""})

        # Return a copy with bound_tools set; LangGraph accepts
        # any Runnable that has _generate + bound_tools.
        new = self.__class__(
            config=self.config,
            enable_thinking=self.enable_thinking,
            thinking_budget=self.thinking_budget,
            bound_tools=normalized,
        )
        return new

    def _format_tools_for_prompt(self) -> str:
        """Format bound tools for the system message."""
        if not self.bound_tools:
            return ""
        lines = ["Available tools (call via JSON {name, arguments}):"]
        for t in self.bound_tools:
            lines.append(f"- {t.get('name', '?')}: {t.get('description', '')}")
        return "\n".join(lines)