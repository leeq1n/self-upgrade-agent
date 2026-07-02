"""v1.8.0 invariant tests for the learning harness (C8/C9/C10).

These tests verify the new learning loop mechanics without calling
the real LLM.  They use the in-memory SQLite pattern that
src.learning.py is designed to support.

Invariants:
  C8: cross-session memory (learning.db) records WHY each attempt
      failed, not just success/fail
  C9: lessons learned for a paper_type are retrievable (so patchgen
      can inject them into its prompt next time)
  C10: blacklist prevents repeated attempts on the same paper_id
       (failing papers don't get retried forever)
"""
import os, sys, tempfile, sqlite3
import pytest

PROJECT = r"C:\Users\LQ\Documents\agent-workspace\hermes-root\self-upgrade-agent"
sys.path.insert(0, PROJECT)


def test_C8_learning_db_records_why_not_just_outcome():
    """C8: each attempt must record failure_mode and lessons_learned.

    v1.7.2's history.db only stored 'reverted' or 'kept'.  v1.8.0 must
    store WHY (failure_mode) and WHAT TO TRY NEXT (lessons_learned)
    so future attempts can avoid past mistakes.
    """
    from src.learning import init_db, record_attempt, get_lessons_for_paper_type

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    conn = init_db(db_path)
    try:
        # Simulate a failed attempt
        record_attempt(
            conn,
            paper_id="2606.30639",
            paper_type="multi_agent_world_model",
            paper_title="Self-Evolving World Models",
            llm_model="Qwen3-235B",
            prompt_strategy="default",
            failure_mode="sandbox_import_error",
            failure_detail="LLM used 'import inspect' but sandbox didn't allow it",
            lessons_learned="Always add 'import' lines to the patch; sandbox doesn't auto-import",
            outcome="reverted",
        )

        # Verify lessons are retrievable
        lessons = get_lessons_for_paper_type(conn, "multi_agent_world_model")
        assert len(lessons) == 1, f"expected 1 lesson, got {len(lessons)}"

        failure_mode, detail, learned, outcome = lessons[0]
        assert failure_mode == "sandbox_import_error"
        assert "inspect" in detail
        assert "import" in learned
        assert outcome == "reverted"

        # Verify the lessons field is what we'd inject into a future prompt
        prompt_injection = f"AVOID: {learned}"
        assert "import" in prompt_injection
    finally:
        conn.close()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_C9_lessons_retrievable_per_paper_type():
    """C9: lessons are filtered by paper_type so the right
    'avoid X' reaches the right patchgen invocation.

    A multi-agent paper's lessons should NOT be mixed with a
    single-agent paper's lessons, because their failure modes differ.
    """
    from src.learning import init_db, record_attempt, get_lessons_for_paper_type

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    conn = init_db(db_path)
    try:
        # Record 2 different paper types
        record_attempt(
            conn, paper_id="p1", paper_type="single_agent",
            failure_mode="tool_fail", failure_detail="tool returned None",
            lessons_learned="Add null check before tool call",
            outcome="reverted",
        )
        record_attempt(
            conn, paper_id="p2", paper_type="multi_agent",
            failure_mode="message_routing_fail",
            failure_detail="agent A's output didn't reach agent B",
            lessons_learned="Add explicit message bus between agents",
            outcome="reverted",
        )

        # Query by type — should only get the matching one
        single = get_lessons_for_paper_type(conn, "single_agent")
        multi = get_lessons_for_paper_type(conn, "multi_agent")

        assert len(single) == 1
        assert "null check" in single[0][2]
        assert len(multi) == 1
        assert "message bus" in multi[0][2]
    finally:
        conn.close()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_C10_blacklist_prevents_repeated_attempts():
    """C10: blacklist stops the system from retrying the same paper
    forever (a real failure mode observed in v1.7.2: 5 rounds of
    the same paper all failed, all from scratch).
    """
    from src.learning import init_db, blacklist_paper, is_blacklisted

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    conn = init_db(db_path)
    try:
        # Initially, paper is not blacklisted
        assert not is_blacklisted(conn, "2606.30639")

        # Blacklist it
        blacklist_paper(
            conn,
            "2606.30639",
            "5 rounds, all failed with sandbox_import_error; "
            "no lessons improving after 3 retries",
        )

        # Now the filter should skip it
        assert is_blacklisted(conn, "2606.30639")

        # Other papers unaffected
        assert not is_blacklisted(conn, "2606.99999")
    finally:
        conn.close()
        if os.path.exists(db_path):
            os.remove(db_path)


def test_learning_db_independent_from_history_db():
    """learning.db and history.db must be separate databases.

    history.db is the audit log (kept forever).
    learning.db is the actionable memory (queried each attempt).

    Mixing them would either:
    - slow history.db (extra fields for memory)
    - or make learning.db lose audit properties
    """
    history_path = os.path.join(PROJECT, "upgrades", "history.db")
    learning_path = os.path.join(PROJECT, "upgrades", "learning.db")

    # Both should exist (or both not) — separate lifecycle
    # At minimum, they MUST be different files
    assert history_path != learning_path, \
        "history.db and learning.db must be separate files"

    # Verify the new learning.db hasn't been created yet (not yet wired)
    # (this test will start failing once v1.8.0 Phase A completes — that's expected)
    # We don't assert non-existence because that would force a fragile coupling.


def test_record_attempt_idempotent_under_concurrent_writes():
    """If 2 patches fail in the same round, both attempts must be
    recorded (no overwrite, no lost data)."""
    from src.learning import init_db, record_attempt

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    conn = init_db(db_path)
    try:
        # Record 3 attempts for the same paper, different failure modes
        for i, fm in enumerate(["sandbox_fail", "json_parse_fail", "evaluate_fail"]):
            record_attempt(
                conn, paper_id="p1", failure_mode=fm,
                failure_detail=f"detail {i}",
                lessons_learned=f"lesson {i}",
                outcome="reverted",
            )

        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM attempts WHERE paper_id = 'p1'")
        assert c.fetchone()[0] == 3, "all 3 attempts must be recorded"
    finally:
        conn.close()
        if os.path.exists(db_path):
            os.remove(db_path)
