"""Tests for src/mcp_client.py and src/memory_server.py.

Covers:
  - Tool registration / dispatch
  - Memory: add_paper, add_outcome, search, get_related, compact
  - Authority weighting
  - Persistence (separate DB instances see same data)
"""
import os
import sys
import tempfile

sys.path.insert(0, r"C:\Users\LQ\Documents\agent-workspace\hermes-root\self-upgrade-agent")

import pytest

from src.mcp_client import (
    call_tool, list_tools, register_tool, tool_count,
    unregister, clear_registry,
)
from src import memory_server
from src.memory_server import Memory, reset_default_memory


# --------------------------------------------------------------------- #
# mcp_client tests
# --------------------------------------------------------------------- #

class TestMcpClient:
    def setup_method(self):
        clear_registry()
        # Re-register memory tools (they auto-register on import)
        import importlib
        importlib.reload(memory_server)

    def test_register_and_call(self):
        @register_tool(name="test_echo", description="echo",
                       schema={"x": "int"})
        def echo(x):
            return x * 2
        assert tool_count() >= 1
        assert call_tool("test_echo", x=21) == 42

    def test_call_unknown_raises(self):
        with pytest.raises(KeyError):
            call_tool("does_not_exist")

    def test_list_tools_has_memory(self):
        tools = list_tools()
        names = {t["name"] for t in tools}
        assert "memory_search" in names
        assert "memory_add_paper" in names

    def test_unregister(self):
        @register_tool(name="to_remove", description="x", schema={})
        def fn():
            return 1
        assert "to_remove" in {t["name"] for t in list_tools()}
        unregister("to_remove")
        assert "to_remove" not in {t["name"] for t in list_tools()}


# --------------------------------------------------------------------- #
# memory_server tests (using a temp DB)
# --------------------------------------------------------------------- #

@pytest.fixture
def mem():
    """Fresh in-memory-ish Memory instance per test."""
    fd, path = tempfile.mkstemp(suffix=".db", prefix="test_mem_")
    os.close(fd)
    os.unlink(path)  # let SQLite create it
    m = Memory(db_path=path)
    yield m
    m.close()
    try:
        os.unlink(path)
    except OSError:
        pass


class TestMemoryAdd:
    def test_add_paper_returns_id(self, mem):
        mid = mem.add_paper("2310.02170", "DyLAN paper", ["agent", "graph"])
        assert isinstance(mid, int)
        assert mid > 0

    def test_add_outcome_with_paper_link(self, mem):
        pid = mem.add_paper("2310.02170", "DyLAN paper", ["agent"])
        oid = mem.add_outcome(pid, "kept", "improved plan_task by 12%")
        # Verify relation exists
        rows = mem._conn.execute(
            "SELECT rel_type FROM relations WHERE src_id=? AND dst_id=?",
            (oid, pid),
        ).fetchall()
        assert rows == [("applies_to",)]

    def test_add_outcome_without_paper(self, mem):
        oid = mem.add_outcome(None, "reverted", "broken patch")
        assert oid > 0


class TestMemorySearch:
    def test_search_finds_matching_paper(self, mem):
        mem.add_paper("2310.02170", "DyLAN dynamic agent network",
                      ["agent", "graph", "reasoning"])
        mem.add_paper("9999.99999", "unrelated topic about cats", ["animal"])
        results = mem.search("agent reasoning graph", top_k=2)
        assert len(results) >= 1
        # The agent paper should rank higher than cats
        assert results[0]["arxiv_id"] == "2310.02170"

    def test_search_returns_authority_in_result(self, mem):
        mem.add_paper("2310.02170", "DyLAN paper", ["agent"])
        results = mem.search("DyLAN paper", top_k=1)
        assert results[0]["authority"] == 0.5  # paper kind

    def test_search_empty_query_returns_empty(self, mem):
        mem.add_paper("2310.02170", "test", ["x"])
        assert mem.search("", top_k=3) == []
        assert mem.search("!!!@@@###", top_k=3) == []  # all stopwords

    def test_search_kind_filter(self, mem):
        mem.add_paper("2310.02170", "DyLAN", ["agent"])
        mem.add_outcome(None, "kept", "DyLAN worked", ["agent"])
        results = mem.search("DyLAN", top_k=5, kind_filter=["outcome"])
        assert all(r["kind"] == "outcome" for r in results)

    def test_search_authority_boost(self, mem):
        # Two units with SAME jaccard but different kinds.
        # Construct text carefully: paper has 3 tokens (all keywords),
        # outcome has same 3 keywords + a few non-keyword fillers so
        # union size grows but intersection stays equal.  Outcome
        # should still rank higher due to authority.
        # Use simple, short text where keyword match is unambiguous.
        mem.add_paper("1111.1111", "alpha beta", ["agent"])  # bow: agent alpha beta
        mem.add_outcome(None, "kept", "gamma delta", ["agent"])  # bow: agent delta gamma
        # Query: "agent" → both have token agent
        # paper bow {agent alpha beta} vs outcome bow {agent delta gamma}
        # query_tokens {agent}; jaccard_paper = 1/3, jaccard_outcome = 1/3 (equal)
        results = mem.search("agent", top_k=2)
        assert len(results) == 2
        kinds = [r["kind"] for r in results]
        scores = {r["kind"]: r["score"] for r in results}
        # When jaccard is equal, authority decides
        assert scores["outcome"] > scores["paper"], (
            f"outcome should rank higher; got {scores}"
        )


class TestMemoryGetRelated:
    def test_get_related_returns_neighbors(self, mem):
        pid = mem.add_paper("2310.02170", "DyLAN paper", ["agent"])
        oid = mem.add_outcome(pid, "kept", "improved plan_task")
        related = mem.get_related(pid, max_hops=1)
        ids = {r["id"] for r in related}
        assert oid in ids

    def test_get_related_two_hops(self, mem):
        pid = mem.add_paper("2310.02170", "DyLAN", ["agent"])
        oid = mem.add_outcome(pid, "kept", "x")
        oid2 = mem.add_outcome(oid, "kept", "y")  # chain
        related = mem.get_related(pid, max_hops=2)
        ids = {r["id"] for r in related}
        assert oid in ids
        assert oid2 in ids


class TestMemoryCompact:
    def test_compact_reports_counts(self, mem):
        mem.add_paper("2310.02170", "x", ["a"])
        mem.add_paper("9999.99999", "y", ["b"])
        n_before, n_after = mem.compact(max_age_days=30)
        assert n_before == 2
        assert n_after == 2  # both fresh

    def test_compact_old_count(self, mem):
        # Manually insert an old unit
        mem._conn.execute(
            """INSERT INTO memory_units
               (kind, arxiv_id, text, topics, bow, authority, created_at)
               VALUES ('paper', '0000.0000', 'old', '["x"]', 'old', 0.5, 1)"""
        )
        mem._conn.commit()
        n_before, n_after = mem.compact(max_age_days=30)
        assert n_before == 1
        assert n_after == 0


class TestMemoryPersistence:
    def test_two_instances_see_same_db(self):
        fd, path = tempfile.mkstemp(suffix=".db", prefix="persist_")
        os.close(fd)
        os.unlink(path)
        try:
            m1 = Memory(db_path=path)
            pid = m1.add_paper("2310.02170", "test", ["x"])
            m1.close()
            m2 = Memory(db_path=path)
            results = m2.search("test", top_k=1)
            assert len(results) == 1
            assert results[0]["id"] == pid
            m2.close()
        finally:
            try:
                os.unlink(path)
            except OSError:
                pass


class TestMcpViaMemoryTools:
    def test_memory_add_paper_via_mcp(self, mem, monkeypatch):
        """Call memory_add_paper via mcp_client.call_tool."""
        reset_default_memory()
        monkeypatch.setattr(memory_server, "_mem", lambda: mem)
        result = call_tool(
            "memory_add_paper",
            arxiv_id="2310.02170",
            summary="DyLAN paper",
            topics=["agent", "graph"],
        )
        assert "memory_id" in result
        assert isinstance(result["memory_id"], int)

    def test_memory_search_via_mcp(self, mem, monkeypatch):
        reset_default_memory()
        monkeypatch.setattr(memory_server, "_mem", lambda: mem)
        call_tool(
            "memory_add_paper",
            arxiv_id="2310.02170",
            summary="agent reasoning framework",
            topics=["agent"],
        )
        results = call_tool("memory_search", query="agent reasoning", top_k=3)
        assert isinstance(results, list)
        assert len(results) >= 1
        assert results[0]["arxiv_id"] == "2310.02170"