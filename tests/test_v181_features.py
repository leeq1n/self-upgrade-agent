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



def test_apply_memory_policy_default_is_noop():
    """v1.8.1 (涌现): default policy is noop.  LLM installs better one."""
    import tempfile
    sys.path.insert(0, PROJECT)
    from src.learning import init_db, mark_paper_seen, apply_memory_policy

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        conn = init_db(path)
        try:
            for i in range(5):
                mark_paper_seen(conn, f"9999.{i:05d}")
            result = apply_memory_policy(conn)  # default = noop
            assert result["policy"] == "noop"
            assert result["deleted"] == 0
            # All 5 rows still there (noop didn\'t touch anything)
            after = conn.execute("SELECT COUNT(*) FROM seen_papers").fetchone()[0]
            assert after == 5
        finally:
            conn.close()
    finally:
        os.unlink(path)


def test_apply_memory_policy_accepts_user_fn():
    """apply_memory_policy runs a user-provided policy function."""
    import tempfile
    sys.path.insert(0, PROJECT)
    from src.learning import init_db, mark_paper_seen, apply_memory_policy

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        conn = init_db(path)
        try:
            for i in range(10):
                mark_paper_seen(conn, f"9999.{i:05d}")

            # User policy: trim to 3 rows
            def my_policy(c):
                cur = c.execute("SELECT COUNT(*) FROM seen_papers").fetchone()[0]
                if cur > 3:
                    n = cur - 3
                    c.execute(
                        "DELETE FROM seen_papers WHERE rowid IN ("
                        "  SELECT rowid FROM seen_papers "
                        "  ORDER BY first_seen_at ASC LIMIT ?)",
                        (n,))
                    c.commit()
                return {"policy": "my_policy", "deleted": max(0, cur - 3)}

            result = apply_memory_policy(conn, my_policy)
            assert result["policy"] == "my_policy"
            after = conn.execute("SELECT COUNT(*) FROM seen_papers").fetchone()[0]
            assert after == 3
        finally:
            conn.close()
    finally:
        os.unlink(path)


def test_apply_memory_policy_hard_ceiling_fuse():
    """Hard ceiling MAX_LEARNING_ROWS fires if user policy is too lax."""
    import tempfile
    sys.path.insert(0, PROJECT)
    from src.learning import (
        init_db, mark_paper_seen, apply_memory_policy, MAX_LEARNING_ROWS
    )

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        conn = init_db(path)
        try:
            # Add MAX+5 rows
            n_to_add = MAX_LEARNING_ROWS + 5
            # Use a batch insert to speed up
            import time
            for i in range(n_to_add):
                mark_paper_seen(conn, f"9999.{i:06d}")

            # Apply noop policy (default) — but the hard ceiling must fire
            result = apply_memory_policy(conn)  # noop
            assert result.get("hard_ceiling_fired") is True
            assert result["after"] == MAX_LEARNING_ROWS
        finally:
            conn.close()
    finally:
        os.unlink(path)


def test_gc_command_supports_memory_policy_flag():
    """self_upgrade gc --memory-policy module:fn wires through."""
    p = os.path.join(PROJECT, "self_upgrade", "__main__.py")
    with open(p) as f:
        content = f.read()
    assert "--memory-policy" in content
    assert "apply_memory_policy" in content
    # The flag should default to None (noop default)
    assert "default=None" in content or "memory_policy=None" in content


def test_run_stable_patches_research_module():
    """run_stable.py must patch BOTH plg.search_arxiv AND src.research.search_arxiv
    (since pipeline_lg imports search_arxiv as a local name)."""
    p = os.path.join(PROJECT, "run_stable.py")
    with open(p) as f:
        content = f.read()
    assert "plg.search_arxiv" in content
    # The actual fix: also patch src.research.search_arxiv
    assert "research_mod.search_arxiv" in content or "research.search_arxiv" in content



def test_goals_registry_starts_empty():
    """v1.8.1 (涌现): the goal registry is empty by default.

    The whole point: do NOT hard-code strategies.  LLM must register them.
    """
    sys.path.insert(0, PROJECT)
    from src.goals import list_strategies
    assert list_strategies() == [], "registry must start empty (emergent)"


def test_goals_pick_returns_fallback_when_empty():
    """With no strategies registered, pick_strategy returns fallback_explore."""
    sys.path.insert(0, PROJECT)
    from src.goals import pick_strategy, clear_registry, list_strategies
    clear_registry()  # ensure empty
    s = pick_strategy({"round_number": 1})
    assert s == "fallback_explore", f"expected fallback_explore, got {s}"


def test_goals_register_and_pick():
    """LLM can register a strategy and pick_strategy uses it."""
    sys.path.insert(0, PROJECT)
    from src.goals import register, unregister, pick_strategy, list_strategies, clear_registry
    clear_registry()

    def my_decide(state):
        return "fallback_explore"

    register("test_strategy", "test description", my_decide)
    assert "test_strategy" in list_strategies()
    s = pick_strategy({})
    assert s == "fallback_explore"  # because my_decide returns this

    unregister("test_strategy")
    assert "test_strategy" not in list_strategies()


def test_goals_crashing_strategy_does_not_break_loop():
    """A strategy whose decide_fn raises should NOT crash the loop."""
    sys.path.insert(0, PROJECT)
    from src.goals import register, unregister, pick_strategy, clear_registry
    clear_registry()

    def crash(state):
        raise RuntimeError("boom")

    register("crash_strategy", "always crashes", crash)
    s = pick_strategy({})
    # First registered strategy is crash_strategy, but it raises.
    # Loop should fall through to fallback_explore.
    assert s == "fallback_explore", f"expected fallback after crash, got {s}"
    unregister("crash_strategy")


def test_goals_register_validates():
    """register() must reject empty names or non-callable decide_fn."""
    sys.path.insert(0, PROJECT)
    from src.goals import register

    try:
        register("", "no name", lambda s: "x")
        assert False, "should have raised ValueError"
    except ValueError:
        pass

    try:
        register("ok_name", "no fn", "not callable")
        assert False, "should have raised ValueError"
    except ValueError:
        pass


def test_goals_test_fn_harness():
    """Each strategy has a test_fn that the harness can invoke."""
    sys.path.insert(0, PROJECT)
    from src.goals import register, unregister, run_health_check, clear_registry
    clear_registry()

    def my_decide(state):
        return "fallback_explore"

    def my_test():
        return True

    register("healthy_strategy", "always healthy", my_decide, test_fn=my_test)

    def bad_test():
        return False

    register("broken_strategy", "broken", my_decide, test_fn=bad_test)

    health = run_health_check()
    assert health["fallback_explore"] is True
    assert health["healthy_strategy"] is True
    assert health["broken_strategy"] is False

    unregister("healthy_strategy")
    unregister("broken_strategy")


def test_goals_fallback_never_breaks():
    """The hardcoded fallback must NEVER be removed (奥卡姆 guarantee)."""
    sys.path.insert(0, PROJECT)
    from src.goals import clear_registry, pick_strategy, describe
    clear_registry()  # wipe everything
    s = pick_strategy({})
    assert s == "fallback_explore"
    d = describe("fallback_explore")
    assert "haven" in d.lower() or "safe" in d.lower()


def test_goals_unregister_returns_bool():
    """unregister returns True if existed, False if not (for atomic semantics)."""
    sys.path.insert(0, PROJECT)
    from src.goals import register, unregister, clear_registry
    clear_registry()

    def d(state):
        return "fallback_explore"
    register("x", "test", d)

    assert unregister("x") is True
    assert unregister("x") is False  # already removed


def test_goals_long_term_default_is_string():
    """DEFAULT_LONG_TERM_GOAL exists and is a non-empty string."""
    sys.path.insert(0, PROJECT)
    from src.goals import DEFAULT_LONG_TERM_GOAL
    assert isinstance(DEFAULT_LONG_TERM_GOAL, str)
    assert len(DEFAULT_LONG_TERM_GOAL) > 0


def test_goals_describe_handles_all_cases():
    """describe(name) handles: known, fallback, unknown, empty."""
    sys.path.insert(0, PROJECT)
    from src.goals import describe, register, clear_registry, unregister
    clear_registry()

    def d(state):
        return "fallback_explore"
    register("k", "known strategy", d)

    assert "safe" in describe("fallback_explore").lower()
    assert "test" in describe("k").lower() or "known" in describe("k").lower()
    assert "unknown" in describe("xyz_unknown").lower()

    unregister("k")



def test_build_research_context_returns_dict():
    """_build_research_context always returns a dict with consistent shape."""
    sys.path.insert(0, PROJECT)
    from src.pipeline_lg import _build_research_context
    ctx = _build_research_context({})
    assert isinstance(ctx, dict)
    assert "seen_papers_count" in ctx
    assert "seen_topics" in ctx
    assert "last_outcome" in ctx
    assert "long_term_goal" in ctx
    # All values should be safe defaults when DB is empty
    assert ctx["seen_papers_count"] == 0
    assert isinstance(ctx["seen_topics"], list)


def test_build_research_context_with_last_outcome():
    """_build_research_context propagates last_outcome."""
    sys.path.insert(0, PROJECT)
    from src.pipeline_lg import _build_research_context
    state = {
        "last_outcome": {"decision": "reverted", "delta": -0.05},
        "long_term_goal": "test goal",
    }
    ctx = _build_research_context(state)
    assert ctx["last_outcome"]["decision"] == "reverted"
    assert ctx["long_term_goal"] == "test goal"


def test_format_loop_feedback_empty():
    """Empty loop_state returns empty string."""
    sys.path.insert(0, PROJECT)
    from src.patchgen import _format_loop_feedback
    assert _format_loop_feedback(None) == ""
    assert _format_loop_feedback({}) == ""


def test_format_loop_feedback_full():
    """All fields are formatted into a readable string."""
    sys.path.insert(0, PROJECT)
    from src.patchgen import _format_loop_feedback
    state = {
        "last_outcome": {"decision": "reverted", "delta": -0.05, "harness_pass_rate": 0.0},
        "seen_papers_count": 42,
        "seen_topics": ["multi-agent", "reasoning", "tool-use"],
        "long_term_goal": "improve planner",
        "sandbox_info": {"python_version": "3.11.15", "sys_path_sample": "/path1, /path2"},
    }
    out = _format_loop_feedback(state)
    assert "Loop feedback" in out
    assert "reverted" in out
    assert "-5.0%" in out or "−5.0%" in out or "-5" in out  # delta formatted
    assert "42 papers" in out
    assert "multi-agent" in out or "tool-use" in out
    assert "Python 3.11.15" in out
    assert "improve planner" in out


def test_patchgen_signature_has_loop_state():
    """generate_patch must accept loop_state kwarg (v1.8.1)."""
    import inspect
    sys.path.insert(0, PROJECT)
    from src.patchgen import generate_patch
    sig = inspect.signature(generate_patch)
    assert "loop_state" in sig.parameters
    # loop_state should default to None (backward compatible)
    assert sig.parameters["loop_state"].default is None


def test_patchgen_prompt_has_loop_feedback_placeholder():
    """PROMPT_TEMPLATE has {loop_feedback} placeholder."""
    sys.path.insert(0, PROJECT)
    from src.patchgen import PROMPT_TEMPLATE
    assert "{loop_feedback}" in PROMPT_TEMPLATE


def test_pipeline_lg_has_research_context():
    """node_research must set state['research_context']."""
    p = os.path.join(PROJECT, "src", "pipeline_lg.py")
    with open(p) as f:
        content = f.read()
    assert "research_context" in content
    assert "_build_research_context" in content


def test_pipeline_lg_passes_loop_state_to_patchgen():
    """node_generate_patch must pass loop_state to generate_patch."""
    p = os.path.join(PROJECT, "src", "pipeline_lg.py")
    with open(p) as f:
        content = f.read()
    assert "loop_state=" in content or "loop_state =" in content
    assert "loop_state=loop_state" in content or "loop_state=state.get" in content
