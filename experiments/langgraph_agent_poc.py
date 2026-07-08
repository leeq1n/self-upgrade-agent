"""experiments/langgraph_agent_poc.py - Real LangGraph agent + MCP + HermesChatModel.

v1.8.3 step: with the LangChain bridge (src/langchain_bridge.py)
and the FastMCP server (src/memory_server.py), we can now wire a
real LangGraph agent that:

  - Uses HermesChatModel (our httpx-based chat, exposed as BaseChatModel)
  - Connects to FastMCP memory server via MultiServerMCPClient
  - Calls create_react_agent(model, mcp_tools)
  - Asks the agent to "remember this paper about agent coordination"

This POC is INTENTIONALLY minimal.  It verifies the integration end
to end without touching production code (pipeline_lg, react.py).
If this works, the next step is refactoring those to use the
LangGraph path.

Mocking note: we use a Mock chat() that returns scripted responses
to drive the agent loop without a real LLM.  This isolates the
framework integration from LLM behavior.
"""
import asyncio
import sys
from unittest.mock import patch, MagicMock

PROJECT = r"C:\Users\LQ\Documents\agent-workspace\hermes-root\self-upgrade-agent"
sys.path.insert(0, PROJECT)


def _mock_chat_response(content):
    """Build an LLMResponse-like object."""
    r = MagicMock()
    r.content = content
    r.error = None
    return r


async def main():
    print("=== LangGraph agent + HermesChatModel + MCP memory POC ===\\n")

    # --- Set up mocked chat() to drive the agent deterministically ---
    call_count = [0]

    scripted_responses = [
        # Step 1: agent decides to call memory_search first
        _mock_chat_response(
            '{"name": "memory_search", '
            '"arguments": {"query": "agent coordination", "top_k": 3}}'
        ),
        # Step 2: agent decides to call memory_add_paper
        _mock_chat_response(
            '{"name": "memory_add_paper", '
            '"arguments": {"arxiv_id": "2310.02170", '
            '"summary": "DyLAN paper on dynamic agent networks", '
            '"topics": ["agent", "coordination"]}}'
        ),
        # Step 3: agent gives Final Answer
        _mock_chat_response(
            "I've recorded the paper about dynamic agent networks."
        ),
    ]

    def fake_chat(messages, **kwargs):
        idx = min(call_count[0], len(scripted_responses) - 1)
        call_count[0] += 1
        return scripted_responses[idx]

    # --- Build the agent ---
    from langgraph.prebuilt import create_react_agent
    from langchain_core.messages import HumanMessage
    from langchain_mcp_adapters.client import MultiServerMCPClient

    from src.langchain_bridge import HermesChatModel

    # 1. Connect to MCP memory server (real stdio transport)
    print("[1] Connecting to MCP server via stdio...")
    mcp_client = MultiServerMCPClient({
        "memory": {
            "command": sys.executable,
            "args": ["-m", "src.memory_server"],
            "transport": "stdio",
        }
    })
    mcp_tools = await mcp_client.get_tools()
    print(f"[1] MCP tools discovered: {[t.name for t in mcp_tools]}")

    # 2. Build the HermesChatModel with our chat() mocked
    print("\\n[2] Building HermesChatModel...")
    model = HermesChatModel(enable_thinking=False, thinking_budget=0)
    # Patch the underlying chat() so we drive it deterministically
    with patch("src.llm.chat", side_effect=fake_chat):
        # 3. Build the agent via create_react_agent
        print("[3] Building LangGraph ReAct agent...")
        agent = create_react_agent(model, mcp_tools)

        # 4. Run the agent
        print("[4] Invoking agent...\\n")
        result = await agent.ainvoke({
            "messages": [
                HumanMessage(content=(
                    "Please remember this paper for me: "
                    "arxiv 2310.02170 DyLAN, about dynamic agent networks."
                )),
            ],
        })

    # 5. Inspect results
    print("[5] Result messages:")
    for m in result["messages"]:
        kind = type(m).__name__
        content_preview = str(m.content)[:80] if m.content else ""
        tool_calls = getattr(m, "tool_calls", [])
        if tool_calls:
            print(f"  {kind}: tool_calls={[(tc['name'], tc['args']) for tc in tool_calls]}")
        else:
            print(f"  {kind}: {content_preview}")

    # 6. Verify memory was written via MCP (separate in-process check)
    print("\\n[6] Verifying memory was written...")
    from src import memory_server  # registers the MCP tools
    from src.mcp_client import call_tool as _call_tool
    results = _call_tool("memory_search", query="DyLAN coordination", top_k=3)
    print(f"[6] Memory search found {len(results)} results")
    for r in results:
        if isinstance(r, dict):
            print(f"     [{r.get('kind', '?')}] {r.get('arxiv_id', '-')}: {r.get('text', '')[:60]}")

    has_paper = any(
        r.get("arxiv_id") == "2310.02170" for r in results if isinstance(r, dict)
    )
    print(f"\\n[6] DyLAN paper found in memory: {has_paper}")
    assert has_paper, "DyLAN paper not in memory — agent didn't call memory_add_paper"

    # 7. Verify the agent loop iterated (at least 3 messages: Human, AI, AI)
    print(f"\\n[7] Total messages in conversation: {len(result['messages'])}")
    assert len(result["messages"]) >= 3, (
        f"expected >=3 messages (human + 2 AI), got {len(result['messages'])}"
    )

    print("\\n=== POC PASS: LangGraph + HermesChatModel + MCP works end-to-end ===")


if __name__ == "__main__":
    asyncio.run(main())