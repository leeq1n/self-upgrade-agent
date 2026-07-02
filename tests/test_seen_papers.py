"""v1.8.0 A4: tests for seen_papers + auto_blacklist (C11/C12).

C11: search_arxiv must filter out papers we've already seen
     (don't waste quota re-fetching)
C12: papers that fail 3+ times get auto-blacklisted
     (don't waste quota on a paper that keeps failing the same way)
"""
import os, sys, tempfile
import pytest

PROJECT = r"C:\Users\LQ\Documents\agent-workspace\hermes-root\self-upgrade-agent"
sys.path.insert(0, PROJECT)


def test_C11_mark_paper_seen_then_get_unseen_excludes_it():
    """C11: after marking a paper as seen, it should be in
    the seen-set so the next search can filter it out."""
    from src.learning import (
        init_db, mark_paper_seen, get_unseen_paper_ids, get_seen_count
    )
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    try:
        conn = init_db(path)
        try:
            # Fresh install: nothing seen
            assert get_seen_count(conn) == 0
            assert get_unseen_paper_ids(conn) == set()

            # Mark a paper
            mark_paper_seen(conn, "2606.30639", outcome="reverted")
            assert get_seen_count(conn) == 1
            assert "2606.30639" in get_unseen_paper_ids(conn)

            # Marking again is idempotent (not double-counted as 2 unique papers)
            mark_paper_seen(conn, "2606.30639", outcome="reverted")
            assert get_seen_count(conn) == 1

            # Mark a different paper
            mark_paper_seen(conn, "2607.12345")
            assert get_seen_count(conn) == 2
            seen = get_unseen_paper_ids(conn)
            assert "2606.30639" in seen
            assert "2607.12345" in seen
        finally:
            conn.close()
    finally:
        if os.path.exists(path):
            os.remove(path)


def test_C11_filter_search_results_against_seen_set():
    """C11: the actual filter step.  search_arxiv returns N papers,
    but we filter to only those NOT in the seen set.
    This test simulates the filter without actually calling arxiv."""
    from src.learning import init_db, mark_paper_seen, get_unseen_paper_ids

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    try:
        conn = init_db(path)
        try:
            # Mark one paper as already seen
            mark_paper_seen(conn, "2606.30639")

            # Simulate search_arxiv returning 3 papers (one we've seen)
            fake_search_results = ["2606.30639", "2607.00001", "2607.00002"]
            seen = get_unseen_paper_ids(conn)
            new_papers = [p for p in fake_search_results if p not in seen]

            # Only 2 new papers should come through
            assert len(new_papers) == 2
            assert "2606.30639" not in new_papers
            assert "2607.00001" in new_papers
            assert "2607.00002" in new_papers
        finally:
            conn.close()
    finally:
        if os.path.exists(path):
            os.remove(path)


def test_C12_auto_blacklist_after_3_failures():
    """C12: after a paper has failed 3 times in attempts, it should
    be auto-blacklisted so the system doesn't keep wasting quota."""
    from src.learning import (
        init_db, record_attempt, auto_blacklist_paper, is_auto_blacklisted
    )
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    try:
        conn = init_db(path)
        try:
            # Record 3 failures for the same paper
            for i in range(3):
                record_attempt(
                    conn, paper_id="2606.30639",
                    failure_mode="sandbox_fail",
                    failure_detail=f"attempt {i+1}",
                    lessons_learned="imports not in sandbox",
                    outcome="reverted",
                )

            # After 3 failures, simulate the auto-blacklist check
            from src.learning import get_failure_count
            assert get_failure_count(conn, "2606.30639") == 3

            # System should now auto-blacklist it
            assert not is_auto_blacklisted(conn, "2606.30639")
            auto_blacklist_paper(
                conn, "2606.30639",
                "3 sandbox failures with same error",
                failure_count=3,
            )
            assert is_auto_blacklisted(conn, "2606.30639")

            # Other papers unaffected
            assert not is_auto_blacklisted(conn, "2607.99999")
        finally:
            conn.close()
    finally:
        if os.path.exists(path):
            os.remove(path)


def test_C12_failure_count_uses_attempts_table():
    """C12: get_failure_count should query attempts table,
    not seen_papers (which tracks exposure, not failure)."""
    from src.learning import (
        init_db, record_attempt, mark_paper_seen, get_failure_count
    )
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    try:
        conn = init_db(path)
        try:
            # Mark as seen 5 times (exposure)
            for _ in range(5):
                mark_paper_seen(conn, "2606.30639")

            # But only record 2 actual failures
            for i in range(2):
                record_attempt(
                    conn, paper_id="2606.30639",
                    failure_mode="sandbox_fail",
                    failure_detail=f"d{i}",
                    lessons_learned="l",
                    outcome="reverted",
                )

            # get_failure_count should return 2 (from attempts), not 5 (from seen)
            assert get_failure_count(conn, "2606.30639") == 2
        finally:
            conn.close()
    finally:
        if os.path.exists(path):
            os.remove(path)


def test_C11_seen_set_persists_across_db_reopen():
    """C11: marking seen must persist (otherwise we re-fetch)."""
    from src.learning import init_db, mark_paper_seen, get_seen_count

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    try:
        # First connection: mark
        conn1 = init_db(path)
        try:
            mark_paper_seen(conn1, "2606.30639")
            mark_paper_seen(conn1, "2607.11111")
        finally:
            conn1.close()

        # Second connection: read
        conn2 = init_db(path)
        try:
            assert get_seen_count(conn2) == 2, "seen count must persist"
        finally:
            conn2.close()
    finally:
        if os.path.exists(path):
            os.remove(path)
