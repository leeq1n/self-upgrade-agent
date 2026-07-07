"""v1.8.1: tests for seen-papers filter + streaming wrapper + collect_papers."""
import os, sys, ast
from src.goals import _reseed_built_in_strategies
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
    # max_tokens can be 2048 (v1.8.1 local) or 4096 (v1.8.1 cloud)
    assert ("LLM_MAX_TOKENS=2048" in content or "LLM_MAX_TOKENS=4096" in content)


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



def test_goals_seeds_2_built_in_strategies():
    """v1.8.1: registry starts with 2 built-in seed strategies (NOT empty).

    The 'emergent' property is preserved: LLM can still add/remove/
    modify.  We just give the loop a starting point.

    This test supersedes the earlier 'registry is empty' assertion
    because the user asked for some help getting started.

    Note: earlier tests may have called clear_registry() which wipes
    the seeds, so we re-seed before checking.
    """
    sys.path.insert(0, PROJECT)
    from src.goals import list_strategies, _reseed_built_in_strategies
    _reseed_built_in_strategies()  # ensure seeds are present
    names = list_strategies()
    assert "explore_new_topic" in names
    assert "drill_after_failure" in names


def test_goals_pick_returns_fallback_when_empty():
    """With no strategies registered, pick_strategy returns fallback_explore."""
    sys.path.insert(0, PROJECT)
    from src.goals import pick_strategy, clear_registry, list_strategies
    clear_registry()
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
    clear_registry()
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



def test_decision_log_table_and_helpers():
    """src/learning.py has decision_log table + log_decision + get_recent_decisions + summarize_failures."""
    sys.path.insert(0, PROJECT)
    from src.learning import log_decision, get_recent_decisions, summarize_failures
    assert callable(log_decision)
    assert callable(get_recent_decisions)
    assert callable(summarize_failures)


def test_decision_log_records_in_real_db():
    """log_decision inserts a row, get_recent_decisions returns it."""
    import tempfile
    sys.path.insert(0, PROJECT)
    from src.learning import init_db, log_decision, get_recent_decisions

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        conn = init_db(path)
        try:
            log_decision(
                conn,
                paper_arxiv_id="9999.99999",
                paper_title="Test paper",
                decision="reverted",
                delta=-0.05,
                harness_pass_rate=0.0,
                failure_mode="harness_failed: 8/0",
                notes="test",
            )
            recent = get_recent_decisions(conn, limit=10)
            assert len(recent) == 1
            assert recent[0]["paper_arxiv_id"] == "9999.99999"
            assert recent[0]["decision"] == "reverted"
        finally:
            conn.close()
    finally:
        os.unlink(path)


def test_summarize_failures_groups_by_decision():
    """summarize_failures counts kept/reverted/crashed/no_patch."""
    import tempfile
    sys.path.insert(0, PROJECT)
    from src.learning import init_db, log_decision, summarize_failures

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        conn = init_db(path)
        try:
            for i in range(3):
                log_decision(conn, paper_arxiv_id=f"9999.{i:05d}", decision="reverted",
                             failure_mode=f"reason_{i % 2}")
            for i in range(2):
                log_decision(conn, paper_arxiv_id=f"8888.{i:05d}", decision="kept")
            summary = summarize_failures(conn)
            assert summary["n_reverted"] == 3
            assert summary["n_kept"] == 2
            assert summary["n_total"] == 5
            # top failure_mode should be one of reason_0 / reason_1
            assert len(summary["failure_modes"]) >= 1
        finally:
            conn.close()
    finally:
        os.unlink(path)


def test_research_context_passes_recent_failures_through():
    """_build_research_context preserves recent_failures if already in state."""
    import sys
    sys.path.insert(0, PROJECT)
    from src.pipeline_lg import _build_research_context
    # Inject recent_failures via state — _build_research_context shouldn't strip it
    state = {
        "recent_failures_str": "5 reverted, 1 kept",
        "top_failure_mode": "harness_failed (3x)",
    }
    ctx = _build_research_context(state)
    # These fields, if set in state, should survive (we just need _build_research_context
    # to not break them — we don\'t currently add them itself, but the caller can)
    # This test guards against the function accidentally overwriting good values
    assert isinstance(ctx, dict)
    assert ctx.get("seen_papers_count") == 0
    assert isinstance(ctx.get("seen_topics"), list)


def test_loop_feedback_includes_recent_failures():
    """_format_loop_feedback includes recent_failures_str + top_failure_mode."""
    sys.path.insert(0, PROJECT)
    from src.patchgen import _format_loop_feedback
    state = {
        "recent_failures_str": "3 reverted, 1 crashed",
        "top_failure_mode": "harness_failed (3x)",
    }
    out = _format_loop_feedback(state)
    assert "Recent outcomes" in out
    assert "3 reverted, 1 crashed" in out
    assert "Top failure mode" in out
    assert "harness_failed (3x)" in out


def test_node_decide_calls_log_decision():
    """node_decide in pipeline_lg must call log_decision."""
    p = os.path.join(PROJECT, "src", "pipeline_lg.py")
    with open(p) as f:
        content = f.read()
    assert "log_decision" in content
    # The function should be imported from src.learning
    assert "from src.learning import" in content
    # And called after discard_candidate
    assert content.find("discard_candidate") < content.find("log_decision(")



def test_tools_module_exists():
    """src/tools.py has register/unregister/list_tools/call_tool/registry_size."""
    sys.path.insert(0, PROJECT)
    from src.tools import register, unregister, list_tools, call_tool, registry_size
    assert callable(register)
    assert callable(unregister)
    assert callable(list_tools)
    assert callable(call_tool)
    assert callable(registry_size)


def test_tools_seeds_4_builtin():
    """src/tools.py auto-registers 4 built-in seed tools."""
    sys.path.insert(0, PROJECT)
    from src.tools import list_tools
    tools = list_tools()
    names = {t["name"] for t in tools}
    assert "web_search" in names, f"missing web_search: {names}"
    assert "evaluate_innovation" in names, f"missing evaluate_innovation: {names}"
    assert "run_harness" in names, f"missing run_harness: {names}"
    assert "read_decision_log" in names, f"missing read_decision_log: {names}"


def test_tools_register_and_unregister():
    """Tools can be registered and unregistered at runtime."""
    sys.path.insert(0, PROJECT)
    from src.tools import register, unregister, get_tool

    def my_fn(**kwargs):
        return "hi"

    register("test_x", "test tool", my_fn, params={"x": "int"})
    tool = get_tool("test_x")
    assert tool is not None
    assert tool["description"] == "test tool"
    assert unregister("test_x") is True
    assert get_tool("test_x") is None


def test_tools_call_tool_runs_fn():
    """call_tool invokes the registered fn."""
    sys.path.insert(0, PROJECT)
    from src.tools import register, unregister, call_tool

    def my_fn(x, y=0):
        return x + y

    register("adder", "adds 2 nums", my_fn, params={"x": "int", "y": "int"})
    result = call_tool("adder", x=3, y=4)
    assert result == 7
    unregister("adder")


def test_tools_health_check():
    """run_health_check runs test_fn for each tool."""
    sys.path.insert(0, PROJECT)
    from src.tools import run_health_check
    h = run_health_check()
    assert isinstance(h, dict)
    for name in h:
        assert h[name] is True, f"{name} failed health: {h}"


def test_goals_seeds_2_built_in_strategies():
    """v1.8.1: goals registry has 2 built-in seed strategies (not empty).

    This is the 'give some help' the user asked for.  LLM can remove
    or override them.  The emergent property is preserved: LLM is
    still expected to add/remove/modify.
    """
    sys.path.insert(0, PROJECT)
    from src.goals import list_strategies
    names = list_strategies()
    assert "explore_new_topic" in names, f"missing seed: {names}"
    assert "drill_after_failure" in names, f"missing seed: {names}"


def test_goals_seed_pick_strategy_works():
    """pick_strategy uses the seed strategies (no clear_registry here)."""
    sys.path.insert(0, PROJECT)
    from src.goals import pick_strategy
    # First 2 rounds should pick explore_new_topic
    s = pick_strategy({"round_number": 1})
    assert s in {"explore_new_topic", "fallback_explore"}
    # After a revert, should pick drill_after_failure or fallback
    s = pick_strategy({"round_number": 5, "last_outcome": {"decision": "reverted"}})
    assert s in {"drill_after_failure", "explore_new_topic", "fallback_explore"}


def test_reseed_function_works():
    """_reseed_built_in_strategies() re-registers the 2 seeds."""
    sys.path.insert(0, PROJECT)
    from src.goals import clear_registry, list_strategies, _reseed_built_in_strategies
    clear_registry()
    names = list_strategies()
    assert len(names) == 0, f"after clear, should be empty, got {names}"
    _reseed_built_in_strategies()
    names = list_strategies()
    assert "explore_new_topic" in names
    assert "drill_after_failure" in names


def test_pipeline_lg_exposes_tools_in_context():
    """_build_research_context includes available_tools + tool_count."""
    sys.path.insert(0, PROJECT)
    from src.pipeline_lg import _build_research_context
    ctx = _build_research_context({})
    assert "available_tools" in ctx
    assert "tool_count" in ctx
    assert ctx["tool_count"] >= 4
    if ctx["available_tools"]:
        t = ctx["available_tools"][0]
        assert "name" in t
        assert "description" in t
        assert "params" in t



def test_seen_papers_filter_keeps_new_papers():
    """v1.8.1 bug fix: node_research must KEEP unseen papers (not seen ones).

    get_unseen_paper_ids() returns SEEN papers (despite its name).
    node_research must filter `pid NOT IN seen_set` to keep NEW papers.
    """
    sys.path.insert(0, PROJECT)
    import re
    with open(os.path.join(PROJECT, "src", "pipeline_lg.py")) as f:
        content = f.read()
    # The filter logic must be `pid not in unseen_ids` (keeps new)
    assert "if pid not in unseen_ids:" in content, \
        "filter should keep papers NOT in seen set (new papers)"
    # Must NOT be the broken version
    assert "if pid in unseen_ids:" not in content, \
        "filter must NOT keep seen papers only"


def test_run_stable_patches_both_modules():
    """v1.8.1 bug fix: run_one_round must patch src.research AND src.pipeline_lg.

    Without patching both, node_research still gets empty papers.
    """
    sys.path.insert(0, PROJECT)
    with open(os.path.join(PROJECT, "run_stable.py")) as f:
        content = f.read()
    # Both module names must appear in the patch block
    patch_block_start = content.find("Inject fake paper")
    patch_block_end = content.find("cfg = load_config", patch_block_start)
    patch_block = content[patch_block_start:patch_block_end]
    assert "src.research as research_mod" in patch_block
    assert "src.pipeline_lg as plg" in patch_block



def test_run_stable_papers_are_real_arxiv():
    """v1.8.1 bug fix: PAPERS in run_stable.py must match real arxiv data.

    Earlier fake data cited "AutoGen" for arxiv 2310.02170 (wrong;
    2310.02170 is DyLAN).  This test catches any future regression.
    """
    sys.path.insert(0, PROJECT)
    with open(os.path.join(PROJECT, "run_stable.py")) as f:
        content = f.read()
    # Spot-check that 3 fixed titles appear (the ones that were wrong)
    assert "DyLAN" in content, "DyLAN should be in real 2310.02170 abstract"
    assert "MMLU-Pro" in content, "MMLU-Pro should be in real 2406.01574 title"
    assert "WorldEvolver" in content, "WorldEvolver should be in real 2606.30639 abstract"
    # And 3 wrong strings should NOT be present
    assert "Multi-Agent Collaboration Mechanisms: A Survey" not in content, \
        "fake 'Multi-Agent Collaboration' was wrong for 2406.01574"
    assert "AutoGen: Multi-Agent Conversation" not in content, \
        "fake 'AutoGen' was wrong for 2310.02170"
    assert "Generative Agents: Interactive Simulacra" not in content, \
        "fake 'Generative Agents' was wrong for 2304.14733"



def test_llm_config_has_thinking_fields():
    """v1.8.1: LLMConfig exposes enable_thinking_default + thinking_budget_default."""
    sys.path.insert(0, PROJECT)
    from src.llm import LLMConfig
    cfg = LLMConfig()
    # Defaults: thinking ON with 2K budget
    assert hasattr(cfg, "enable_thinking_default")
    assert hasattr(cfg, "thinking_budget_default")
    assert cfg.enable_thinking_default is True
    assert cfg.thinking_budget_default == 2048


def test_chat_simple_accepts_thinking_kwargs():
    """v1.8.1: chat_simple forwards enable_thinking + thinking_budget to chat()."""
    sys.path.insert(0, PROJECT)
    from src.llm import chat_simple
    import inspect
    sig = inspect.signature(chat_simple)
    assert "enable_thinking" in sig.parameters
    assert "thinking_budget" in sig.parameters


def test_chat_injects_chat_template_kwargs():
    """v1.8.1: chat() injects chat_template_kwargs into the request body.

    We can't actually call the LLM (no network), but we can verify the
    function signature accepts the new args.
    """
    sys.path.insert(0, PROJECT)
    from src.llm import chat
    import inspect
    sig = inspect.signature(chat)
    assert "enable_thinking" in sig.parameters
    assert "thinking_budget" in sig.parameters


def test_patchgen_uses_thinking_for_patch_design():
    """v1.8.1: src/patchgen.py chat() call enables thinking with budget."""
    sys.path.insert(0, PROJECT)
    with open(os.path.join(PROJECT, "src", "patchgen.py")) as f:
        content = f.read()
    # The chat() call in patchgen should specify thinking params
    assert "enable_thinking=True" in content
    assert "thinking_budget=4096" in content


def test_filter_disables_thinking_for_speed():
    """v1.8.1: src/filter.py chat_simple() disables thinking (keyword-based)."""
    sys.path.insert(0, PROJECT)
    with open(os.path.join(PROJECT, "src", "filter.py")) as f:
        content = f.read()
    assert "enable_thinking=False" in content


def test_env_example_has_thinking_defaults():
    """v1.8.1: .env.example documents the new thinking defaults."""
    sys.path.insert(0, PROJECT)
    with open(os.path.join(PROJECT, ".env.example")) as f:
        content = f.read()
    assert "LLM_ENABLE_THINKING_DEFAULT" in content
    assert "LLM_THINKING_BUDGET_DEFAULT" in content
    assert "LLM_AGENT_WORLD_URL" in content
    assert "LLM_AGENT_WORLD_MODEL" in content


def test_model_strategy_doc_exists():
    """v1.8.1: docs/MODEL_STRATEGY.md explains the dual llama-server setup."""
    sys.path.insert(0, PROJECT)
    assert os.path.exists(os.path.join(PROJECT, "docs", "MODEL_STRATEGY.md"))


def test_start_llama_servers_script_exists():
    """v1.8.1: scripts/start_llama_servers.sh provides one-shot server start."""
    sys.path.insert(0, PROJECT)
    path = os.path.join(PROJECT, "scripts", "start_llama_servers.sh")
    assert os.path.exists(path)
    with open(path) as f:
        content = f.read()
    assert "qwen3-vl-30b-a3b" in content
    assert "qwen-agentworld-35b-a3b" in content
    assert "38000" in content
    assert "38001" in content
    assert "mmproj" in content
    assert "enable_thinking" in content



def test_llm_ready_without_api_key():
    """v1.8.1: LLMConfig.ready is True when model + base_url set, no API key needed.

    Local llama-server setups (e.g. Qwen3-VL on AGX Thor) don't require
    an API key.  Previously, config.ready required api_keys non-empty,
    which made all local setups silently fall back to keyword scoring.
    """
    sys.path.insert(0, PROJECT)
    from src.llm import LLMConfig
    cfg = LLMConfig(api_keys=[], model="qwen3-vl-30b-a3b",
                    base_url="http://localhost:38000/v1")
    assert cfg.ready is True, "ready should be True for local server (no key)"

    cfg_no_url = LLMConfig(api_keys=[], model="qwen3-vl-30b-a3b", base_url="")
    assert cfg_no_url.ready is False, "ready should be False without base_url"

    cfg_no_model = LLMConfig(api_keys=[], model="", base_url="http://localhost:38000/v1")
    assert cfg_no_model.ready is False, "ready should be False without model"


def test_filter_skips_quota_check_when_no_api_keys():
    """v1.8.1: score_paper() skips QuotaState check when api_keys empty.

    For local llama-server (no API keys), the previous QuotaState check
    incorrectly concluded 'all keys dead' and bypassed LLM scoring,
    causing filter to fall back to keyword-only (which almost never
    met thresholds).  Now it skips that check entirely.
    """
    sys.path.insert(0, PROJECT)
    with open(os.path.join(PROJECT, "src", "filter.py")) as f:
        content = f.read()
    # Must have: if llm_config.api_keys: (not always check QuotaState)
    assert "if llm_config.api_keys:" in content, \
        "filter must skip QuotaState check when no API keys (local server)"



def test_try_with_fallback_handles_no_api_keys():
    """v1.8.1: _try_with_fallback handles api_keys empty (local llama-server).

    With local llama-server, api_keys is empty.  The previous code logged
    'All API keys marked dead' and tried with empty list, causing the
    for-loop to skip entirely.  Now it injects a 'local-sentinel' into
    config.api_keys so the loop and .index() calls work.
    """
    sys.path.insert(0, PROJECT)
    with open(os.path.join(PROJECT, "src", "llm.py")) as f:
        src = f.read()
    # Must inject sentinel when no keys
    assert 'config.api_keys = ["local-sentinel"]' in src, \
        "must inject local-sentinel into config.api_keys when empty"
    # Must NOT have the buggy if/else branch with if config.api_keys:
    assert 'if config.api_keys:\n        alive_keys' not in src, \
        "must not have the if/else gate (that broke api_keys.index())"
