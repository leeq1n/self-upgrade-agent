"""v1.8.0 learning.db schema for cross-session memory (SEAE HC7).

Goals:
  - Persist failure_reason (WHY each attempt failed) — not just success/fail
  - Persist paper_type, llm_model, prompt_strategy for each attempt
  - Persist lessons_learned (what to avoid next time)
  - Blacklist table: skip papers that already failed N times

This is the foundation for the "self-evolving harness":
  - v1.7.2 only records "reverted" or "kept" in history.db
  - v1.8.0 records WHY and WHAT NEXT
  - This feeds patchgen's prompt so it can avoid past mistakes

Design decisions:
  - SEPARATE database from history.db (single-responsibility)
  - Schema versioned (schema_version field) for future migrations
  - Indexes on (paper_id, attempt_id) for fast lookup
"""
import sqlite3
import os

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "upgrades",
    "learning.db",
)

SCHEMA_VERSION = 1

SCHEMA = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id TEXT NOT NULL,
    paper_type TEXT,
    paper_title TEXT,
    llm_model TEXT,
    prompt_strategy TEXT,
    failure_mode TEXT,
    failure_detail TEXT,
    lessons_learned TEXT,
    outcome TEXT,  -- "kept" | "reverted" | "skipped" | "crashed"
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_attempts_paper ON attempts(paper_id);
CREATE INDEX IF NOT EXISTS idx_attempts_type ON attempts(paper_type);
CREATE INDEX IF NOT EXISTS idx_attempts_failure ON attempts(failure_mode);

CREATE TABLE IF NOT EXISTS blacklist (
    paper_id TEXT PRIMARY KEY,
    reason TEXT NOT NULL,
    failure_count INTEGER DEFAULT 0,
    blacklisted_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS convergence_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""


def init_db(path: str = DB_PATH) -> sqlite3.Connection:
    """Initialize learning.db with schema. Idempotent."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    # Record schema version
    c = conn.cursor()
    c.execute("SELECT version FROM schema_version LIMIT 1")
    row = c.fetchone()
    if row is None:
        import datetime
        c.execute(
            "INSERT INTO schema_version (version, created_at) VALUES (?, ?)",
            (SCHEMA_VERSION, datetime.datetime.utcnow().isoformat()),
        )
    conn.commit()
    return conn


def record_attempt(
    conn: sqlite3.Connection,
    paper_id: str,
    failure_mode: str,
    failure_detail: str,
    lessons_learned: str,
    outcome: str,
    paper_type: str = None,
    paper_title: str = None,
    llm_model: str = None,
    prompt_strategy: str = None,
) -> int:
    """Record a single attempt with WHY-it-failed detail.

    This is the entry point the pipeline should call from
    node_reflect / node_evaluate when an attempt fails.
    """
    import datetime
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO attempts
        (paper_id, paper_type, paper_title, llm_model, prompt_strategy,
         failure_mode, failure_detail, lessons_learned, outcome, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            paper_id, paper_type, paper_title, llm_model, prompt_strategy,
            failure_mode, failure_detail, lessons_learned, outcome,
            datetime.datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()
    return c.lastrowid


def get_lessons_for_paper_type(
    conn: sqlite3.Connection,
    paper_type: str,
    limit: int = 5,
) -> list:
    """Retrieve the most recent lessons for a paper type.

    Used by patchgen to inject 'avoid X' into its prompt:
      "Previous attempts with paper_type=multi_agent failed because X.
       Avoid this by doing Y."
    """
    c = conn.cursor()
    c.execute(
        """
        SELECT failure_mode, failure_detail, lessons_learned, outcome
        FROM attempts
        WHERE paper_type = ? AND lessons_learned IS NOT NULL
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (paper_type, limit),
    )
    return c.fetchall()


def is_blacklisted(conn: sqlite3.Connection, paper_id: str) -> bool:
    """Check if a paper has been blacklisted (failed too many times)."""
    c = conn.cursor()
    c.execute("SELECT 1 FROM blacklist WHERE paper_id = ?", (paper_id,))
    return c.fetchone() is not None


def blacklist_paper(
    conn: sqlite3.Connection,
    paper_id: str,
    reason: str,
) -> None:
    """Add a paper to the blacklist. Idempotent."""
    import datetime
    c = conn.cursor()
    c.execute(
        """
        INSERT OR IGNORE INTO blacklist
        (paper_id, reason, failure_count, blacklisted_at)
        VALUES (?, ?, 0, ?)
        """,
        (paper_id, reason, datetime.datetime.utcnow().isoformat()),
    )
    conn.commit()


def get_convergence_state(conn: sqlite3.Connection, key: str) -> str:
    """Read a convergence control value (e.g. last_round_no_progress)."""
    c = conn.cursor()
    c.execute("SELECT value FROM convergence_state WHERE key = ?", (key,))
    row = c.fetchone()
    return row[0] if row else None


def set_convergence_state(conn: sqlite3.Connection, key: str, value: str) -> None:
    """Write a convergence control value."""
    import datetime
    c = conn.cursor()
    c.execute(
        """
        INSERT OR REPLACE INTO convergence_state
        (key, value, updated_at) VALUES (?, ?, ?)
        """,
        (key, value, datetime.datetime.utcnow().isoformat()),
    )
    conn.commit()
