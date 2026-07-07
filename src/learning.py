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

-- v1.8.0 A4: persistent record of papers we've already seen.
-- This is the foundation for "don't waste quota on re-fetched papers".
-- A paper is added to seen_papers the first time it appears in
-- search_arxiv results.  Filter logic should exclude them from
-- subsequent search invocations.
CREATE TABLE IF NOT EXISTS seen_papers (
    paper_id TEXT PRIMARY KEY,
    first_seen_at TEXT NOT NULL,
    times_seen INTEGER DEFAULT 1,
    last_outcome TEXT
);
CREATE INDEX IF NOT EXISTS idx_seen_first_seen ON seen_papers(first_seen_at);

-- v1.8.0 A4: auto-blacklist after N failures.
-- A paper that fails N+ times gets auto-blacklisted so the system
-- stops wasting quota on it.  This is a soft blacklist separate
-- from the hard blacklist_paper() manual call.
CREATE TABLE IF NOT EXISTS auto_blacklist (
    paper_id TEXT PRIMARY KEY,
    reason TEXT NOT NULL,
    failure_count INTEGER NOT NULL,
    blacklisted_at TEXT NOT NULL
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


# === v1.8.0 A4: seen_papers tracking ===

def mark_paper_seen(
    conn: sqlite3.Connection,
    paper_id: str,
    outcome: str = None,
) -> None:
    """Record that we have seen a paper (called from node_research).

    Idempotent: increments times_seen if already present.
    This is the foundation for "don't waste quota re-fetching".
    """
    import datetime
    c = conn.cursor()
    c.execute("SELECT times_seen FROM seen_papers WHERE paper_id = ?", (paper_id,))
    row = c.fetchone()
    if row is None:
        c.execute(
            """
            INSERT INTO seen_papers (paper_id, first_seen_at, times_seen, last_outcome)
            VALUES (?, ?, 1, ?)
            """,
            (paper_id, datetime.datetime.utcnow().isoformat(), outcome),
        )
    else:
        c.execute(
            """
            UPDATE seen_papers
            SET times_seen = times_seen + 1, last_outcome = ?
            WHERE paper_id = ?
            """,
            (outcome, paper_id),
        )
    conn.commit()


def get_unseen_paper_ids(conn: sqlite3.Connection) -> set:
    """Return the set of paper_ids we have already seen.

    Used by node_research to filter search_arxiv results:
    only papers NOT in this set should be returned.

    Empty set on a fresh install (nothing seen yet, all are new).
    """
    c = conn.cursor()
    c.execute("SELECT paper_id FROM seen_papers")
    return {row[0] for row in c.fetchall()}


def get_seen_count(conn: sqlite3.Connection) -> int:
    """How many unique papers have we seen so far?"""
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM seen_papers")
    return c.fetchone()[0]


def auto_blacklist_paper(
    conn: sqlite3.Connection,
    paper_id: str,
    reason: str,
    failure_count: int,
) -> None:
    """Auto-blacklist a paper that has failed N+ times.

    Distinct from manual blacklist_paper() — this is system-driven
    based on the failure count observed in attempts.
    """
    import datetime
    c = conn.cursor()
    c.execute(
        """
        INSERT OR REPLACE INTO auto_blacklist
        (paper_id, reason, failure_count, blacklisted_at)
        VALUES (?, ?, ?, ?)
        """,
        (paper_id, reason, failure_count, datetime.datetime.utcnow().isoformat()),
    )
    conn.commit()


def is_auto_blacklisted(conn: sqlite3.Connection, paper_id: str) -> bool:
    """Check if a paper has been auto-blacklisted due to repeated failures."""
    c = conn.cursor()
    c.execute("SELECT 1 FROM auto_blacklist WHERE paper_id = ?", (paper_id,))
    return c.fetchone() is not None


def get_failure_count(conn: sqlite3.Connection, paper_id: str) -> int:
    """How many times has this paper failed in attempts table?"""
    c = conn.cursor()
    c.execute(
        "SELECT COUNT(*) FROM attempts WHERE paper_id = ? AND outcome != 'kept'",
        (paper_id,),
    )
    return c.fetchone()[0]



# ═══════════════════════════════════════════════════════════
# v1.8.1 (奥卡姆-涌现): Memory compression policy
# ═══════════════════════════════════════════════════════════
#
# v1.8.1 DESIGN PRINCIPLE:
#   We do NOT hard-code "trim to 500 rows" or "keep last 30 days".
#   Instead we expose:
#     1. Raw table data (so the policy can be observed)
#     2. ONE hard ceiling (MAX_LEARNING_ROWS) — last-resort safety
#     3. `apply_memory_policy(conn, policy_fn)` — policy_fn is a callable
#        that gets the conn and decides what to delete.
#
# The DEFAULT `apply_memory_policy` is "do nothing" — let LLM evolve it.
# `self_upgrade gc` accepts a `--policy` flag for the LLM to install
# its own policy (via a one-shot script or via patchgen).
#
# The hard ceiling only fires when total rows exceed MAX_LEARNING_ROWS,
# and even then it uses a simple "delete oldest" — this is just a fuse,
# not a real policy.  Real policy must come from evolution.

MAX_LEARNING_ROWS = 10000  # hard ceiling.  LLM policy should keep us below this.


def apply_memory_policy(conn: sqlite3.Connection, policy_fn=None) -> dict:
    """Apply a memory-compression policy.  Returns a report dict.

    Args:
        conn: sqlite3 connection to learning.db
        policy_fn: optional callable(conn) -> dict.  If None, uses the
            DEFAULT no-op policy (which is what runs today).  The LLM
            can install a smarter policy by passing a function here,
            or by editing this function via patchgen.

    Returns:
        dict with at least: {"policy": "<name>", "before": int,
                             "after": int, "deleted": int}
    """
    before = conn.execute("SELECT COUNT(*) FROM seen_papers").fetchone()[0]

    if policy_fn is None:
        # Default policy: nothing.  Trust LLM to install one later.
        result = {"policy": "noop", "before": before, "after": before, "deleted": 0}
    else:
        # Run the LLM-installed (or test-installed) policy
        result = policy_fn(conn)
        if not isinstance(result, dict):
            result = {"policy": "user_fn", "before": before, "after": before, "deleted": 0}

    # Hard safety ceiling — fuse only, no policy.  Runs AFTER both paths.
    after = conn.execute("SELECT COUNT(*) FROM seen_papers").fetchone()[0]
    if after > MAX_LEARNING_ROWS:
        n_to_delete = after - MAX_LEARNING_ROWS
        conn.execute(
            "DELETE FROM seen_papers WHERE rowid IN ("
            "  SELECT rowid FROM seen_papers ORDER BY first_seen_at ASC LIMIT ?"
            ")",
            (n_to_delete,),
        )
        conn.commit()
        result["hard_ceiling_fired"] = True
        result["deleted"] = result.get("deleted", 0) + n_to_delete
        result["after"] = MAX_LEARNING_ROWS
    return result
