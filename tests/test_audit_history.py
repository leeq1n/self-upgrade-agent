"""v1.8.0 Day 5: tests for audit_history tracking + get_audit_history()."""
import os, sys, tempfile
import pytest

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT)


def _temp_db():
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    from src.db import UpgradeHistory
    return UpgradeHistory(tmp.name), tmp.name


def test_record_audit_inserts_row():
    """record_audit() must insert a row in audit_history."""
    h, path = _temp_db()
    try:
        audit_id = h.record_audit(
            n_skills=5, n_culled=2, n_kept=3,
            details={"a": "kept", "b": "culled"},
        )
        assert audit_id > 0
        rows = h.get_audit_history()
        assert len(rows) == 1
        assert rows[0]["n_skills"] == 5
        assert rows[0]["n_culled"] == 2
        assert rows[0]["n_kept"] == 3
    finally:
        h.close()
        os.unlink(path)


def test_get_audit_history_limit():
    """get_audit_history(limit=N) returns at most N rows, most recent first."""
    h, path = _temp_db()
    try:
        for i in range(5):
            h.record_audit(n_skills=i, n_culled=0, n_kept=i, details={})
        rows = h.get_audit_history(limit=3)
        assert len(rows) == 3
        # Most recent first
        assert rows[0]["n_skills"] == 4
        assert rows[1]["n_skills"] == 3
        assert rows[2]["n_skills"] == 2
    finally:
        h.close()
        os.unlink(path)


def test_node_skill_audit_writes_audit_history():
    """Running node_skill_audit must persist to audit_history."""
    from src.config import Config, PipelineConfig, DatabaseConfig
    import src.pipeline_lg as plg
    h, path = _temp_db()
    try:
        # Register a bad skill
        h.register_skill("bad", skill_path="/tmp/x.py",
                         paper_arxiv_id="x", paper_title="x")
        h.conn.execute(
            "UPDATE skill_registry SET use_count=10, avg_improvement=-0.05 "
            "WHERE skill_name='bad'")
        h.conn.commit()
        h.close()
        h = None

        # Run audit
        cfg = Config()
        cfg.database = DatabaseConfig(path=path)
        cfg.pipeline = PipelineConfig()
        cfg.pipeline.skill_audit_every = 1
        state = {"config": cfg, "errors": []}
        result = plg.node_skill_audit(state)

        # Verify audit_history has 1 row
        h2 = type(None)  # avoid lint
        from src.db import UpgradeHistory as UH
        h2 = UH(path)
        try:
            history = h2.get_audit_history()
        finally:
            h2.close()
        assert len(history) == 1
        assert history[0]["n_skills"] == 1
        assert history[0]["n_culled"] == 1
        # Details is JSON
        import json
        details = json.loads(history[0]["details_json"])
        assert "bad" in details
        assert details["bad"]["action"] == "culled"
    finally:
        if h is not None:
            h.close()
        os.unlink(path)


def test_audit_history_persists_across_db_close():
    """audit_history rows persist after db is closed and reopened."""
    h, path = _temp_db()
    try:
        h.record_audit(n_skills=1, n_culled=0, n_kept=1, details={"a": "ok"})
        h.close()

        # Reopen
        from src.db import UpgradeHistory
        h2 = UpgradeHistory(path)
        try:
            rows = h2.get_audit_history()
        finally:
            h2.close()
        assert len(rows) == 1
        assert rows[0]["n_kept"] == 1
    finally:
        os.unlink(path)


def test_audit_history_table_exists():
    """audit_history table is created on UpgradeHistory init."""
    h, path = _temp_db()
    try:
        cursor = h.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='audit_history'"
        )
        tables = [r[0] for r in cursor.fetchall()]
        assert "audit_history" in tables
    finally:
        h.close()
        os.unlink(path)
