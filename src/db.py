"""SQLite database for tracking upgrade history across pipeline runs.

[FROZEN v1.1.0] — stable schema (3 tables), tested, do not modify.
"""
import sqlite3
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class UpgradeRecord:
    """A record of one upgrade attempt, persisted to SQLite."""
    paper_arxiv_id: str = ""
    paper_title: str = ""
    skill_name: str = ""
    skill_path: str = ""
    baseline_success_rate: float = 0.0
    upgraded_success_rate: float = 0.0
    baseline_cost_tokens: int = 0
    upgraded_cost_tokens: int = 0
    decision: str = "pending"   # kept | reverted | failed | pending
    notes: str = ""
    id: int = 0
    created_at: str = ""


class UpgradeHistory:
    """SQLite-backed history of all upgrade attempts."""

    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS skill_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_name TEXT UNIQUE,
                skill_path TEXT DEFAULT '',
                paper_arxiv_id TEXT DEFAULT '',
                paper_title TEXT DEFAULT '',
                status TEXT DEFAULT 'active',
                created_at TEXT DEFAULT (datetime('now')),
                last_used_at TEXT,
                use_count INTEGER DEFAULT 0,
                total_success INTEGER DEFAULT 0,
                total_failure INTEGER DEFAULT 0,
                avg_improvement REAL DEFAULT 0.0,
                last_evaluated_at TEXT,
                notes TEXT DEFAULT ''
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS skill_usage_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_name TEXT NOT NULL,
                task_id TEXT DEFAULT '',
                success BOOLEAN DEFAULT 0,
                tokens_used INTEGER DEFAULT 0,
                latency_seconds REAL DEFAULT 0.0,
                recorded_at TEXT DEFAULT (datetime('now'))
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS upgrades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paper_arxiv_id TEXT NOT NULL,
                paper_title TEXT NOT NULL,
                skill_name TEXT NOT NULL,
                skill_path TEXT DEFAULT '',
                baseline_success_rate REAL NOT NULL,
                upgraded_success_rate REAL NOT NULL,
                baseline_cost_tokens INTEGER NOT NULL,
                upgraded_cost_tokens INTEGER NOT NULL,
                decision TEXT NOT NULL DEFAULT 'pending',
                notes TEXT DEFAULT '',
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_decision ON upgrades(decision)
        """)
        self.conn.commit()

    def insert(self, record: UpgradeRecord) -> int:
        """Insert a new upgrade record. Returns the new row ID."""
        cursor = self.conn.execute("""
            INSERT INTO upgrades
                (paper_arxiv_id, paper_title, skill_name, skill_path,
                 baseline_success_rate, upgraded_success_rate,
                 baseline_cost_tokens, upgraded_cost_tokens,
                 decision, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.paper_arxiv_id, record.paper_title, record.skill_name,
            record.skill_path, record.baseline_success_rate,
            record.upgraded_success_rate, record.baseline_cost_tokens,
            record.upgraded_cost_tokens, record.decision, record.notes,
            datetime.now().isoformat()
        ))
        self.conn.commit()
        return cursor.lastrowid

    def get_all(self) -> List[UpgradeRecord]:
        """Retrieve all upgrade records, most recent first."""
        rows = self.conn.execute(
            "SELECT * FROM upgrades ORDER BY created_at DESC"
        ).fetchall()
        return [self._row_to_record(r) for r in rows]

    def get_by_decision(self, decision: str) -> List[UpgradeRecord]:
        """Filter records by decision status."""
        rows = self.conn.execute(
            "SELECT * FROM upgrades WHERE decision = ? ORDER BY created_at DESC",
            (decision,)
        ).fetchall()
        return [self._row_to_record(r) for r in rows]

    def get_stats(self) -> dict:
        """Return aggregate statistics over all records."""
        row = self.conn.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN decision = 'kept' THEN 1 ELSE 0 END) as kept,
                SUM(CASE WHEN decision = 'reverted' THEN 1 ELSE 0 END) as reverted,
                SUM(CASE WHEN decision = 'failed' THEN 1 ELSE 0 END) as failed,
                COALESCE(
                    AVG(CASE
                        WHEN decision IN ('kept', 'reverted')
                        THEN upgraded_success_rate - baseline_success_rate
                        ELSE NULL
                    END),
                    0.0
                ) as avg_delta
            FROM upgrades
        """).fetchone()
        return dict(row)

    def register_skill(self, skill_name, skill_path="", paper_arxiv_id="", paper_title=""):
        cursor = self.conn.execute("""
            INSERT OR REPLACE INTO skill_registry
                (skill_name, skill_path, paper_arxiv_id, paper_title, status, created_at)
            VALUES (?, ?, ?, ?, 'active', datetime('now'))
        """, (skill_name, skill_path, paper_arxiv_id, paper_title))
        self.conn.commit()
        return cursor.lastrowid
    
    def record_usage(self, skill_name, task_id="", success=True, tokens_used=0, latency=0.0):
        self.conn.execute("""
            INSERT INTO skill_usage_log (skill_name, task_id, success, tokens_used, latency_seconds)
            VALUES (?, ?, ?, ?, ?)
        """, (skill_name, task_id, success, tokens_used, latency))
        self.conn.execute("""
            UPDATE skill_registry SET 
                use_count = use_count + 1,
                total_success = total_success + ?,
                total_failure = total_failure + ?,
                last_used_at = datetime('now')
            WHERE skill_name = ?
        """, (1 if success else 0, 0 if success else 1, skill_name))
        self.conn.commit()
    
    def get_active_skills(self):
        rows = self.conn.execute("""
            SELECT * FROM skill_registry 
            WHERE status = 'active' 
            ORDER BY (use_count * ABS(avg_improvement)) DESC
        """).fetchall()
        return [dict(r) for r in rows]
    
    def archive_skill(self, skill_name):
        self.conn.execute(
            "UPDATE skill_registry SET status = 'archived' WHERE skill_name = ?",
            (skill_name,)
        )
        self.conn.commit()
    
    def update_improvement(self, skill_name, avg_imp):
        self.conn.execute(
            "UPDATE skill_registry SET avg_improvement = ?, last_evaluated_at = datetime('now') WHERE skill_name = ?",
            (avg_imp, skill_name)
        )
        self.conn.commit()
    
    def close(self):
        self.conn.close()
        import gc, time
        gc.collect()
        time.sleep(0.05)

    def _row_to_record(self, row) -> UpgradeRecord:
        return UpgradeRecord(
            id=row["id"],
            paper_arxiv_id=row["paper_arxiv_id"],
            paper_title=row["paper_title"],
            skill_name=row["skill_name"],
            skill_path=row["skill_path"],
            baseline_success_rate=row["baseline_success_rate"],
            upgraded_success_rate=row["upgraded_success_rate"],
            baseline_cost_tokens=row["baseline_cost_tokens"],
            upgraded_cost_tokens=row["upgraded_cost_tokens"],
            decision=row["decision"],
            notes=row["notes"],
            created_at=row["created_at"],
        )
