"""v1.8.1: tests for seen-papers filter + streaming wrapper + collect_papers."""
import os, sys, ast
import pytest

PROJECT = r"C:\Users\LQ\Documents\agent-workspace\hermes-root\self-upgrade-agent"


def test_seen_papers_function_exists():
    """src/learning.py has mark_paper_seen, get_unseen_paper_ids, is_blacklisted."""
    sys.path.insert(0, PROJECT)
    from src.learning import (
        mark_paper_seen, get_unseen_paper_ids, is_blacklisted, get_seen_count
    )
    assert callable(mark_paper_seen)
    assert callable(get_unseen_paper_ids)
    assert callable(is_blacklisted)
    assert callable(get_seen_count)


def test_pipeline_lg_filters_seen_papers():
    """src/pipeline_lg.py node_research must call get_unseen_paper_ids."""
    p = os.path.join(PROJECT, "src", "pipeline_lg.py")
    with open(p) as f:
        content = f.read()
    # node_research body must include seen-papers filter
    assert "get_unseen_paper_ids" in content
    assert "is_blacklisted" in content


def test_pipeline_lg_marks_seen_after_round():
    """node_decide must call mark_paper_seen."""
    p = os.path.join(PROJECT, "src", "pipeline_lg.py")
    with open(p) as f:
        content = f.read()
    assert "mark_paper_seen" in content


def test_llm_stream_module_exists():
    """src/llm_stream.py must exist with chat_stream function."""
    p = os.path.join(PROJECT, "src", "llm_stream.py")
    assert os.path.exists(p)
    with open(p) as f:
        content = f.read()
    assert "def chat_stream" in content
    # Validates as Python
    ast.parse(content)


def test_llm_stream_handles_anthropic_and_openai():
    """chat_stream must have both code paths."""
    p = os.path.join(PROJECT, "src", "llm_stream.py")
    with open(p) as f:
        content = f.read()
    # Anthropic path: event-based
    assert "event_block_delta" in content or "content_block_delta" in content
    # OpenAI path: choices[0].delta
    assert '"choices"' in content or "'choices'" in content
    assert "_is_anthropic" in content


def test_collect_papers_script_exists():
    """collect_papers.py is the bulk-fetch script."""
    p = os.path.join(PROJECT, "collect_papers.py")
    assert os.path.exists(p)
    with open(p) as f:
        content = f.read()
    assert "search_arxiv" in content
    assert "argparse" in content
    # Validates
    ast.parse(content)


def test_env_bumped_to_v181_timeouts():
    """v1.8.1: LLM_TIMEOUT=300, LLM_TOTAL_TIMEOUT=1800, LLM_MAX_TOKENS=4096."""
    p = os.path.join(PROJECT, ".env")
    if not os.path.exists(p):
        pytest.skip("no .env (not in this session)")
    with open(p) as f:
        content = f.read()
    # Either 300 or whatever the v1.8.1 value is
    assert "LLM_TIMEOUT=300" in content
    assert "LLM_TOTAL_TIMEOUT=1800" in content
    assert "LLM_MAX_TOKENS=4096" in content


def test_seen_papers_in_db_actually_records():
    """mark_paper_seen should add the paper to seen_papers table.

    Note: the function is named "get_unseen_paper_ids" but actually
    returns SEEN paper IDs (the filter logic in pipeline_lg.py
    uses "if pid in seen_ids: skip").  This is a known naming
    inconsistency — the function works correctly, just confusing.
    """
    sys.path.insert(0, PROJECT)
    import tempfile
    from src.learning import init_db, mark_paper_seen, get_unseen_paper_ids, get_seen_count

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        conn = init_db(path)
        try:
            # Initially empty
            assert get_seen_count(conn) == 0
            assert "9999.99999" not in get_unseen_paper_ids(conn)

            # Mark a paper (signature is mark_paper_seen(conn, paper_id, outcome))
            mark_paper_seen(conn, "9999.99999", outcome="kept: harness 8/8")
            assert get_seen_count(conn) == 1
            assert "9999.99999" in get_unseen_paper_ids(conn)

            # Mark same paper again — should not double-count (idempotent)
            mark_paper_seen(conn, "9999.99999", outcome="kept: harness 8/8")
            assert get_seen_count(conn) == 1, "duplicate mark should not double-count"
        finally:
            conn.close()
    finally:
        os.unlink(path)
