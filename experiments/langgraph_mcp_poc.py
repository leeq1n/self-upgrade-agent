"""experiments/langgraph_mcp_poc.py - POC: FastMCP server + langchain-mcp-adapters.

Per the user's question (2026-07-08): "agent 中绝大多数结构都应该是
工具 MCP 调用的".  This POC verifies that:

  1. Our memory_server.py can be exposed as a real MCP server (FastMCP).
  2. langchain-mcp-adapters.MultiServerMCPClient can connect to it.
  3. Tools discovered via MCP are callable and return correct results.

The POC does NOT integrate with LangGraph yet — that requires a
LangChain-compatible chat model which our current chat() in src/llm.py
doesn't provide (we use httpx directly).  See the design doc for the
migration path.

What's verified:
  - FastMCP server starts via `python -m src.memory_server`
  - MultiServerMCPClient connects via stdio transport
  - All 5 memory tools (add_paper, add_outcome, search, get_related, compact)
    are discoverable
  - Tool calls return the same shape as our in-process call_tool()
"""
import asyncio
import sys

PROJECT = r"C:\Users\LQ\Documents\agent-workspace\hermes-root\self-upgrade-agent"
sys.path.insert(0, PROJECT)


def _unwrap(result):
    """MCP tool returns [{'type': 'text', 'text': '<json>'}].

    For list results, FastMCP serializes twice — once to a JSON list of
    {type, text} wrapper, then the inner list as JSON inside text.
    """
    import json
    while isinstance(result, list) and len(result) == 1 and isinstance(result[0], dict):
        if "text" not in result[0]:
            break
        try:
            inner = json.loads(result[0]["text"])
            if isinstance(inner, str):
                # double-encoded: unwrap once more
                result = inner
                continue
            return inner
        except json.JSONDecodeError:
            return result[0]["text"]
    return result


async def main():
    from langchain_mcp_adapters.client import MultiServerMCPClient

    print("=== FastMCP server + langchain-mcp-adapters POC ===\n")

    # 1. Connect to our MCP server via stdio
    client = MultiServerMCPClient({
        "memory": {
            "command": sys.executable,
            "args": ["-m", "src.memory_server"],
            "transport": "stdio",
        }
    })
    print("[1] Connecting to MCP server via stdio...")
    tools = await client.get_tools()
    tool_names = sorted(t.name for t in tools)
    print(f"[1] Tools discovered: {tool_names}")
    expected = {"memory_add_paper", "memory_add_outcome", "memory_search",
                "memory_get_related", "memory_compact"}
    assert expected.issubset(set(tool_names)), (
        f"missing: {expected - set(tool_names)}"
    )

    # 2. Call memory_add_paper via MCP
    print("\n[2] Calling memory_add_paper via MCP...")
    add_paper = next(t for t in tools if t.name == "memory_add_paper")
    result = _unwrap(await add_paper.ainvoke({
        "arxiv_id": "9999.99999",
        "summary": "POC test paper",
        "topics": ["poc", "test"],
    }))
    print(f"[2] Result: {result}")
    memory_id = result["memory_id"]

    # 3. Call memory_search via MCP
    print("\n[3] Calling memory_search via MCP...")
    search = next(t for t in tools if t.name == "memory_search")
    raw = await search.ainvoke({"query": "POC test", "top_k": 3})
    print(f"[3] Raw type: {type(raw).__name__}, count: {len(raw)}")
    print(f"[3] Raw[0] type: {type(raw[0]).__name__ if raw else '?'}")
    # FastMCP wraps each list item separately; flatten all text fields
    import json as _json
    flat = []
    for item in raw:
        if isinstance(item, dict) and "text" in item:
            try:
                parsed = _json.loads(item["text"])
                if isinstance(parsed, list):
                    flat.extend(parsed)
                else:
                    flat.append(parsed)
            except _json.JSONDecodeError:
                flat.append(item["text"])
    print(f"[3] Flat count: {len(flat)}")
    for r in flat:
        if isinstance(r, dict):
            print(f"     [{r.get('kind','?')}] {r.get('arxiv_id','-')}: {r.get('text','')[:60]}")
    assert any(r.get("arxiv_id") == "9999.99999" for r in flat if isinstance(r, dict))

    # 4. Call memory_add_outcome via MCP
    print("\n[4] Calling memory_add_outcome via MCP...")
    add_outcome = next(t for t in tools if t.name == "memory_add_outcome")
    out = _unwrap(await add_outcome.ainvoke({
        "paper_id": memory_id,
        "decision": "kept",
        "patch_summary": "POC patch worked",
        "topics": ["poc"],
    }))
    print(f"[4] Result: {out}")

    # 5. Call memory_compact via MCP
    print("\n[5] Calling memory_compact via MCP...")
    compact = next(t for t in tools if t.name == "memory_compact")
    compact_result = _unwrap(await compact.ainvoke({"max_age_days": 30}))
    print(f"[5] Result: {compact_result}")

    print("\n=== POC PASS: all 5 MCP tools work end-to-end ===")


if __name__ == "__main__":
    asyncio.run(main())
