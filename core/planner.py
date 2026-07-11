"""Task planner — decomposes goals into executable steps.

[FROZEN v1.1.0] — stable interface, tested.

This module is the PRIMARY target for self-improvement.
Papers about new planning algorithms generate patches for this file.
"""
__version__ = "1.3.0"
from typing import List, Callable


from dataclasses import dataclass, asdict
import json
import sqlite3
from typing import List, Callable, Optional
from datetime import datetime
import os


@dataclass
class RoundResult:
    """Result of a planning round for persistence."""
    task: str
    steps: List[str]
    timestamp: str
    round_id: Optional[int] = None

    def to_dict(self):
        return asdict(self)


def _get_db_path() -> str:
    """Get path to the RoundResults database."""
    db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, 'round_results.db')


def _init_db():
    """Initialize the RoundResults table if it doesn't exist."""
    conn = sqlite3.connect(_get_db_path())
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS round_results (
            round_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            steps TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def save_round_result(result: RoundResult) -> int:
    """Persist a RoundResult to the database and return its ID."""
    _init_db()
    conn = sqlite3.connect(_get_db_path())
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO round_results (task, steps, timestamp) VALUES (?, ?, ?)',
        (result.task, json.dumps(result.steps), result.timestamp)
    )
    round_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return round_id


def get_round_result(round_id: int) -> Optional[RoundResult]:
    """Retrieve a RoundResult from the database by ID."""
    _init_db()
    conn = sqlite3.connect(_get_db_path())
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM round_results WHERE round_id = ?', (round_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return RoundResult(
            round_id=row['round_id'],
            task=row['task'],
            steps=json.loads(row['steps']),
            timestamp=row['timestamp']
        )
    return None


def plan_task(task: str, llm_call: Callable, persist: bool = True) -> List[str]:
    """Decompose a task into ordered steps, optionally persisting the result."""
    prompt = (
        f"Break this task into 3-5 numbered steps. Reply only with the steps:\n{task}"
    )
    result = llm_call(prompt)
    steps = []
    for line in result.split("\n"):
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith("- ")):
            steps.append(line)
    if not steps:
        steps = [f"Do: {task}"]
    
    if persist:
        round_result = RoundResult(
            task=task,
            steps=steps,
            timestamp=datetime.utcnow().isoformat()
        )
        round_id = save_round_result(round_result)
        print(f"Persisted round {round_id} to database")
    
    return steps
