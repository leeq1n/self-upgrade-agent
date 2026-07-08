"""src/memory_server.py — MCP server exposing memory operations.

Implements the "memory" MCP server (in-process).  Tools:
  - memory_add_paper(arxiv_id, summary, topics)
  - memory_add_outcome(paper_id, decision, patch_summary)
  - memory_search(query, top_k=3)
  - memory_get_related(memory_id, max_hops=2)
  - memory_compact(max_age_days=30)

Storage: SQLite (2 tables: memory_units + relations).  See design doc
§2.  Authority weighting: paper=0.5, outcome=1.0, patch=0.7, topic=0.9.

Honest about what it is: keyword-based similarity (not embeddings).
Upgrade path documented in design doc §2.
"""
import json
import logging
import os
import re
import sqlite3
import time
from typing import Any, Dict, List, Optional, Set, Tuple

from src.mcp_client import register_tool

logger = logging.getLogger(__name__)


# Authority weighting (from design doc §2)
_AUTHORITY = {"paper": 0.5, "outcome": 1.0, "patch": 0.7, "topic": 0.9}


# --------------------------------------------------------------------- #
# Storage
# --------------------------------------------------------------------- #

_SCHEMA = """
CREATE TABLE IF NOT EXISTS memory_units (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    kind        TEXT NOT NULL,     -- 'paper' | 'outcome' | 'patch' | 'topic'
    arxiv_id    TEXT,              -- nullable
    text        TEXT NOT NULL,
    topics      TEXT NOT NULL,     -- JSON list of strings
    bow         TEXT NOT NULL,     -- bag-of-words set (space-separated tokens)
    authority   REAL NOT NULL,
    created_at  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS relations (
    src_id      INTEGER NOT NULL,
    dst_id      INTEGER NOT NULL,
    rel_type    TEXT NOT NULL,     -- 'applies_to' | 'modified' | 'reverted' | 'extends'
    PRIMARY KEY (src_id, dst_id, rel_type)
);

CREATE INDEX IF NOT EXISTS idx_units_kind ON memory_units(kind);
CREATE INDEX IF NOT EXISTS idx_units_arxiv ON memory_units(arxiv_id);
CREATE INDEX IF NOT EXISTS idx_relations_src ON relations(src_id);
CREATE INDEX IF NOT EXISTS idx_relations_dst ON relations(dst_id);
"""


def _default_db_path() -> str:
    """Default DB path: upgrades/memory.db."""
    upgraded = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "upgrades",
    )
    os.makedirs(upgraded, exist_ok=True)
    return os.path.join(upgraded, "memory.db")


# --------------------------------------------------------------------- #
# Tokenization (intentionally simple; this is keyword match, not semantic)
# --------------------------------------------------------------------- #

_STOPWORDS = frozenset({
    "the", "a", "an", "and", "or", "but", "of", "in", "on", "for",
    "to", "with", "by", "is", "are", "was", "were", "be", "been",
    "this", "that", "these", "those", "it", "its", "as", "at",
    "from", "into", "than", "then", "so", "such", "also", "we",
    "our", "you", "your", "they", "their", "them", "i", "my",
})


def _tokenize(text: str) -> Set[str]:
    """Lowercase, split on non-alpha, drop stopwords, length>=3.

    Returns a set of tokens.  This is the 'bag of words' we use for
    similarity.  Not fancy, not semantic, but honest.
    """
    text = (text or "").lower()
    tokens = re.findall(r"[a-z][a-z0-9_-]{2,}", text)
    return {t for t in tokens if t not in _STOPWORDS}


# --------------------------------------------------------------------- #
# The Memory class — wraps DB
# --------------------------------------------------------------------- #

class Memory:
    """In-process memory store.  See design doc §2."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or _default_db_path()
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def close(self):
        self._conn.close()

    # ---- write ----

    def add_paper(self, arxiv_id: str, summary: str,
                  topics: List[str]) -> int:
        """Add a paper memory unit.  Returns the new memory id."""
        return self._insert(
            kind="paper",
            arxiv_id=arxiv_id,
            text=summary,
            topics=topics,
        )

    def add_outcome(self, paper_id: Optional[int], decision: str,
                    patch_summary: str,
                    topics: Optional[List[str]] = None) -> int:
        """Add a decision outcome memory unit.

        Args:
            paper_id: id of the related paper memory (or None)
            decision: 'kept' | 'reverted' | 'no_patch'
            patch_summary: short description of what the patch did
            topics: optional topic tags

        Returns: new memory id.
        """
        text = f"decision={decision}; {patch_summary}"
        new_id = self._insert(
            kind="outcome",
            arxiv_id=None,
            text=text,
            topics=topics or [decision],
        )
        if paper_id is not None:
            self._relate(new_id, paper_id, "applies_to")
        return new_id

    def add_patch(self, paper_id: Optional[int], function_name: str,
                  summary: str,
                  topics: Optional[List[str]] = None) -> int:
        """Add a patch memory unit (we wrote this code)."""
        text = f"patch fn={function_name}: {summary}"
        new_id = self._insert(
            kind="patch",
            arxiv_id=None,
            text=text,
            topics=topics or [function_name],
        )
        if paper_id is not None:
            self._relate(new_id, paper_id, "modified")
        return new_id

    def _insert(self, kind: str, arxiv_id: Optional[str],
                text: str, topics: List[str]) -> int:
        authority = _AUTHORITY.get(kind, 0.5)
        bow = " ".join(sorted(_tokenize(text + " " + " ".join(topics))))
        cur = self._conn.execute(
            """INSERT INTO memory_units
               (kind, arxiv_id, text, topics, bow, authority, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (kind, arxiv_id, text, json.dumps(topics), bow,
             authority, int(time.time())),
        )
        self._conn.commit()
        return cur.lastrowid

    def _relate(self, src_id: int, dst_id: int, rel_type: str) -> None:
        """Create an edge between two memory units."""
        self._conn.execute(
            """INSERT OR IGNORE INTO relations
               (src_id, dst_id, rel_type) VALUES (?, ?, ?)""",
            (src_id, dst_id, rel_type),
        )
        self._conn.commit()

    # ---- read ----

    def search(self, query: str, top_k: int = 3,
               kind_filter: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Keyword search ranked by Jaccard + authority.

        Returns a list of dicts: {id, kind, arxiv_id, text, topics,
        authority, score}.
        """
        query_tokens = _tokenize(query)
        if not query_tokens:
            return []
        rows = self._conn.execute(
            "SELECT id, kind, arxiv_id, text, topics, authority, bow "
            "FROM memory_units"
            + (" WHERE kind IN ({})".format(",".join("?" * len(kind_filter)))
               if kind_filter else ""),
            tuple(kind_filter) if kind_filter else (),
        ).fetchall()

        scored = []
        for row in rows:
            mid, kind, arxiv_id, text, topics, authority, bow = row
            unit_tokens = set(bow.split()) if bow else set()
            if not unit_tokens:
                continue
            jaccard = len(query_tokens & unit_tokens) / len(query_tokens | unit_tokens)
            # Weighted sum: keyword match (jaccard) + authority.
            # Multiplicative boost diluted when text is long; additive
            # keeps authority meaningful regardless of text length.
            # Authority is in [0.5, 1.0] for our kinds; we scale to
            # [0.0, 0.5] so jaccard still dominates when it should.
            score = jaccard + 0.5 * authority
            if score > 0:
                scored.append({
                    "id": mid,
                    "kind": kind,
                    "arxiv_id": arxiv_id,
                    "text": text,
                    "topics": json.loads(topics),
                    "authority": authority,
                    "score": score,
                })
        scored.sort(key=lambda u: -u["score"])
        return scored[:top_k]

    def get_related(self, memory_id: int, max_hops: int = 2) -> List[Dict[str, Any]]:
        """BFS over relations table, up to max_hops edges away.

        Returns the related units (excluding the starting one), grouped
        by hop distance.
        """
        visited: Set[int] = {memory_id}
        frontier: Set[int] = {memory_id}
        results = []
        for _hop in range(max_hops):
            if not frontier:
                break
            placeholders = ",".join("?" * len(frontier))
            rows = self._conn.execute(
                f"SELECT DISTINCT dst_id FROM relations WHERE src_id IN ({placeholders}) "
                f"UNION "
                f"SELECT DISTINCT src_id FROM relations WHERE dst_id IN ({placeholders})",
                tuple(frontier) + tuple(frontier),
            ).fetchall()
            next_frontier: Set[int] = set()
            for (mid,) in rows:
                if mid in visited:
                    continue
                visited.add(mid)
                next_frontier.add(mid)
            frontier = next_frontier
        # Read all visited units (excluding the start)
        visited.discard(memory_id)
        if not visited:
            return []
        placeholders = ",".join("?" * len(visited))
        rows = self._conn.execute(
            f"SELECT id, kind, arxiv_id, text, topics, authority "
            f"FROM memory_units WHERE id IN ({placeholders})",
            tuple(visited),
        ).fetchall()
        for row in rows:
            mid, kind, arxiv_id, text, topics, authority = row
            results.append({
                "id": mid,
                "kind": kind,
                "arxiv_id": arxiv_id,
                "text": text,
                "topics": json.loads(topics),
                "authority": authority,
            })
        return results

    def compact(self, max_age_days: int = 30) -> Tuple[int, int]:
        """Mark old units as 'archived' (v1.8.2: just count them).

        Returns: (n_before, n_after_active).

        v1.8.2 doesn't actually delete — we just report.  Real compaction
        (LLM summarization) is deferred until 100+ papers per design §6.
        """
        cutoff = int(time.time()) - max_age_days * 86400
        n_before = self._conn.execute(
            "SELECT COUNT(*) FROM memory_units"
        ).fetchone()[0]
        n_old = self._conn.execute(
            "SELECT COUNT(*) FROM memory_units WHERE created_at < ?",
            (cutoff,),
        ).fetchone()[0]
        n_after_active = n_before - n_old
        logger.info(
            f"memory.compact: {n_before} units total, {n_old} older than "
            f"{max_age_days}d, {n_after_active} still active."
        )
        return n_before, n_after_active


# --------------------------------------------------------------------- #
# MCP tool registration (after Memory class is defined)
# --------------------------------------------------------------------- #

# Module-level default memory instance.  The pipeline calls MCP tools,
# not this class directly — see design doc §2 (memory is MCP).
_default_memory: Optional[Memory] = None


def _mem() -> Memory:
    """Get or create the default memory instance."""
    global _default_memory
    if _default_memory is None:
        _default_memory = Memory()
    return _default_memory


def reset_default_memory() -> None:
    """For tests: drop the default memory instance."""
    global _default_memory
    if _default_memory is not None:
        _default_memory.close()
        _default_memory = None


@register_tool(
    name="memory_add_paper",
    description="Add a paper summary to memory.  Returns memory_id.",
    schema={"arxiv_id": "str", "summary": "str", "topics": "list[str]"},
)
def _add_paper(arxiv_id: str, summary: str,
               topics: Optional[List[str]] = None) -> Dict[str, Any]:
    topics = topics or []
    mid = _mem().add_paper(arxiv_id, summary, topics)
    return {"memory_id": mid}


@register_tool(
    name="memory_add_outcome",
    description="Record a decision outcome.  Returns memory_id.",
    schema={"paper_id": "int?", "decision": "str",
            "patch_summary": "str", "topics": "list[str]?"},
)
def _add_outcome(paper_id: Optional[int], decision: str,
                 patch_summary: str,
                 topics: Optional[List[str]] = None) -> Dict[str, Any]:
    mid = _mem().add_outcome(paper_id, decision, patch_summary, topics)
    return {"memory_id": mid}


@register_tool(
    name="memory_search",
    description="Search memory by keyword.  Returns top-k units.",
    schema={"query": "str", "top_k": "int?"},
)
def _search(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    return _mem().search(query, top_k=top_k)


@register_tool(
    name="memory_get_related",
    description="Get memory units related (via relations graph) to a given unit.",
    schema={"memory_id": "int", "max_hops": "int?"},
)
def _get_related(memory_id: int, max_hops: int = 2) -> List[Dict[str, Any]]:
    return _mem().get_related(memory_id, max_hops=max_hops)


@register_tool(
    name="memory_compact",
    description="Report old memory units (v1.8.2: report only; no deletion).",
    schema={"max_age_days": "int?"},
)
def _compact(max_age_days: int = 30) -> Dict[str, Any]:
    n_before, n_after_active = _mem().compact(max_age_days)
    return {"n_before": n_before, "n_after_active": n_after_active}