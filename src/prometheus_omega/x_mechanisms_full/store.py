"""Prometheus X — SQLite Store

13-table storage layer with FTS5 full-text index and vector BLOB serialization.
Source: MnemosyneV3 storage/sqlite_store.py + Prometheus V7 store.py.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from pathlib import Path
from typing import Any, Optional

import numpy as np

from enum import Enum, IntEnum

from prometheus_x.core.schema import (
    AutonomyLevel,
    Belief,
    ConfidenceAction,
    EdgeType,
    GraphEdge,
    MemoryCategory,
    MemoryEntry,
    MemoryTier,
    TrustLevel,
    VeracityLevel,
)


_CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    category TEXT NOT NULL,
    tags TEXT DEFAULT '[]',
    agent_id TEXT DEFAULT '',
    embedding BLOB,
    tier TEXT DEFAULT 'working',
    tier_score REAL DEFAULT 0.0,
    last_tier_migration REAL DEFAULT 0.0,
    weibull_lambda REAL DEFAULT 7.0,
    weibull_k REAL DEFAULT 1.5,
    consecutive_hits INTEGER DEFAULT 0,
    last_accessed REAL DEFAULT 0.0,
    created_at REAL DEFAULT 0.0,
    importance REAL DEFAULT 0.5,
    confidence REAL DEFAULT 0.5,
    feedback_score REAL DEFAULT 0.0,
    access_count INTEGER DEFAULT 0,
    veracity TEXT DEFAULT 'unverified',
    depth INTEGER DEFAULT 0,
    valence REAL DEFAULT 0.0,
    entity_a TEXT DEFAULT '',
    entity_b TEXT DEFAULT '',
    wing_id TEXT DEFAULT '',
    co_occurrence_count INTEGER DEFAULT 0,
    belief_cluster_id TEXT DEFAULT '',
    harmony_score REAL DEFAULT 0.0,
    is_shmr_candidate INTEGER DEFAULT 0,
    foresight TEXT DEFAULT '',
    unresolved INTEGER DEFAULT 0,
    trust_level TEXT DEFAULT 'pending',
    autonomy_level INTEGER DEFAULT 3,
    confidence_gate_action TEXT DEFAULT 'defer',
    source_memory_ids TEXT DEFAULT '[]',
    metadata TEXT DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS facts (
    id TEXT PRIMARY KEY,
    memory_id TEXT NOT NULL,
    subject TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object TEXT NOT NULL,
    confidence REAL DEFAULT 0.5,
    FOREIGN KEY (memory_id) REFERENCES memories(id)
);

CREATE TABLE IF NOT EXISTS gists (
    id TEXT PRIMARY KEY,
    memory_id TEXT NOT NULL,
    summary TEXT NOT NULL,
    emotion TEXT DEFAULT '',
    FOREIGN KEY (memory_id) REFERENCES memories(id)
);

CREATE TABLE IF NOT EXISTS graph_edges (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    edge_type TEXT NOT NULL,
    weight REAL DEFAULT 1.0,
    confidence REAL DEFAULT 0.5,
    created_at REAL DEFAULT 0.0,
    metadata TEXT DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS hallways (
    id TEXT PRIMARY KEY,
    entity_a TEXT NOT NULL,
    entity_b TEXT NOT NULL,
    wing_id TEXT NOT NULL,
    co_occurrence_count INTEGER DEFAULT 1,
    last_seen REAL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS tunnels (
    id TEXT PRIMARY KEY,
    entity_a TEXT NOT NULL,
    entity_b TEXT NOT NULL,
    wing_id_a TEXT NOT NULL,
    wing_id_b TEXT NOT NULL,
    bridge_strength REAL DEFAULT 0.5
);

CREATE TABLE IF NOT EXISTS beliefs (
    id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    statement TEXT NOT NULL,
    confidence REAL DEFAULT 0.5,
    harmony_score REAL DEFAULT 0.0,
    source_memory_ids TEXT DEFAULT '[]',
    veracity TEXT DEFAULT 'unverified',
    created_at REAL DEFAULT 0.0,
    last_validated REAL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS conflicts (
    id TEXT PRIMARY KEY,
    memory_id_a TEXT NOT NULL,
    memory_id_b TEXT NOT NULL,
    conflict_type TEXT NOT NULL,
    resolution TEXT DEFAULT '',
    resolved INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS consolidated_facts (
    id TEXT PRIMARY KEY,
    topic TEXT NOT NULL,
    statement TEXT NOT NULL,
    confidence REAL DEFAULT 0.5,
    source_ids TEXT DEFAULT '[]',
    veracity TEXT DEFAULT 'confirmed',
    created_at REAL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS cycle_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cycle_type TEXT NOT NULL,
    started_at REAL NOT NULL,
    completed_at REAL,
    entries_processed INTEGER DEFAULT 0,
    success INTEGER DEFAULT 1,
    metadata TEXT DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS feedback_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id TEXT NOT NULL,
    feedback_type TEXT NOT NULL,
    score REAL DEFAULT 0.0,
    timestamp REAL NOT NULL,
    FOREIGN KEY (memory_id) REFERENCES memories(id)
);

CREATE TABLE IF NOT EXISTS forget_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    tier_at_forget TEXT NOT NULL,
    retention_at_forget REAL DEFAULT 0.0,
    timestamp REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS knowledge_transfer_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_agent TEXT NOT NULL,
    target_agent TEXT NOT NULL,
    memory_id TEXT NOT NULL,
    transfer_type TEXT NOT NULL,
    timestamp REAL NOT NULL
);
"""

_FTS5_VIRTUAL_TABLE = """
CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
    memory_id, content, tags, category, agent_id, tier
);
"""

_BLOB_FIELDS = {"embedding"}
_JSON_FIELDS = {"tags", "source_memory_ids", "metadata"}


class SQLiteStore:
    """Thread-safe SQLite store with FTS5 and vector BLOB support."""

    def __init__(self, db_path: str | Path = ":memory:") -> None:
        self._db_path = str(db_path)
        self._local = threading.local()
        self._write_lock = threading.Lock()

    def _get_conn(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            conn = sqlite3.connect(self._db_path, timeout=30)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA foreign_keys=ON")
            conn.row_factory = sqlite3.Row
            self._local.conn = conn
            conn.executescript(_CREATE_TABLES)
            conn.execute(_FTS5_VIRTUAL_TABLE)
            conn.commit()
        return self._local.conn

    # ------------------------------------------------------------------
    # Memory CRUD
    # ------------------------------------------------------------------

    def put_memory(self, entry: MemoryEntry) -> None:
        """Insert or update a memory entry."""
        with self._write_lock:
            conn = self._get_conn()
            data = self._entry_to_row(entry)
            placeholders = ", ".join(["?"] * len(data))
            columns = ", ".join(data.keys())
            conn.execute(
                f"INSERT OR REPLACE INTO memories ({columns}) VALUES ({placeholders})",
                list(data.values()),
            )
            # Update FTS5 index
            conn.execute("DELETE FROM memories_fts WHERE memory_id=?", (entry.id,))
            conn.execute(
                "INSERT INTO memories_fts(memory_id, content, tags, category, agent_id, tier) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                [entry.id, entry.content, json.dumps(entry.tags),
                 entry.category.value, entry.agent_id, entry.tier.value],
            )
            conn.commit()

    def get_memory(self, memory_id: str) -> Optional[MemoryEntry]:
        """Retrieve a single memory entry by its ID."""
        conn = self._get_conn()
        row = conn.execute("SELECT * FROM memories WHERE id=?", (memory_id,)).fetchone()
        if row is None:
            return None
        return self._row_to_entry(row)

    def search_fts(self, query: str, limit: int = 20) -> list[MemoryEntry]:
        """Full-text search via FTS5."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT m.* FROM memories m "
            "JOIN memories_fts f ON m.id = f.memory_id "
            "WHERE memories_fts MATCH ? LIMIT ?",
            (query, limit),
        ).fetchall()
        return [self._row_to_entry(r) for r in rows]

    def get_by_tier(self, tier: MemoryTier, limit: int = 100) -> list[MemoryEntry]:
        """Retrieve memories belonging to a specific storage tier."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT * FROM memories WHERE tier=? ORDER BY importance DESC LIMIT ?",
            (tier.value, limit),
        ).fetchall()
        return [self._row_to_entry(r) for r in rows]

    def delete_memory(self, memory_id: str) -> None:
        """Delete a memory entry and its FTS5 index."""
        with self._write_lock:
            conn = self._get_conn()
            conn.execute("DELETE FROM memories_fts WHERE memory_id=?", (memory_id,))
            conn.execute("DELETE FROM memories WHERE id=?", (memory_id,))
            conn.commit()

    def count(self) -> int:
        """Return the total number of stored memories."""
        conn = self._get_conn()
        return conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]

    # ------------------------------------------------------------------
    # Graph edges
    # ------------------------------------------------------------------

    def put_edge(self, edge: GraphEdge) -> None:
        """Insert or update a graph edge."""
        conn = self._get_conn()
        conn.execute(
            "INSERT OR REPLACE INTO graph_edges "
            "(id, source_id, target_id, edge_type, weight, confidence, created_at, metadata) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (edge.id, edge.source_id, edge.target_id, edge.edge_type.value,
             edge.weight, edge.confidence, edge.created_at, json.dumps(edge.metadata)),
        )
        conn.commit()

    def get_edges_from(self, node_id: str) -> list[GraphEdge]:
        """Retrieve all outgoing edges from a given node."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT * FROM graph_edges WHERE source_id=?", (node_id,)
        ).fetchall()
        return [GraphEdge(
            id=r["id"], source_id=r["source_id"], target_id=r["target_id"],
            edge_type=EdgeType(r["edge_type"]), weight=r["weight"],
            confidence=r["confidence"], created_at=r["created_at"],
            metadata=json.loads(r["metadata"]),
        ) for r in rows]

    # ------------------------------------------------------------------
    # Beliefs
    # ------------------------------------------------------------------

    def put_belief(self, belief: Belief) -> None:
        """Insert or update a synthesized belief."""
        conn = self._get_conn()
        conn.execute(
            "INSERT OR REPLACE INTO beliefs "
            "(id, topic, statement, confidence, harmony_score, source_memory_ids, veracity, created_at, last_validated) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (belief.id, belief.topic, belief.statement, belief.confidence,
             belief.harmony_score, json.dumps(belief.source_memory_ids),
             belief.veracity.name.lower(), belief.created_at, belief.last_validated),
        )
        conn.commit()

    def get_beliefs(self, min_confidence: float = 0.5) -> list[Belief]:
        """Retrieve beliefs meeting a minimum confidence threshold."""
        conn = self._get_conn()
        rows = conn.execute(
            "SELECT * FROM beliefs WHERE confidence>=? ORDER BY confidence DESC",
            (min_confidence,),
        ).fetchall()
        return [Belief(
            id=r["id"], topic=r["topic"], statement=r["statement"],
            confidence=r["confidence"], harmony_score=r["harmony_score"],
            source_memory_ids=json.loads(r["source_memory_ids"]),
            veracity=VeracityLevel[r["veracity"].upper()],
            created_at=r["created_at"], last_validated=r["last_validated"],
        ) for r in rows]

    # ------------------------------------------------------------------
    # Feedback
    # ------------------------------------------------------------------

    def log_feedback(self, memory_id: str, feedback_type: str, score: float) -> None:
        """Log user feedback for a memory entry."""
        conn = self._get_conn()
        conn.execute(
            "INSERT INTO feedback_log (memory_id, feedback_type, score, timestamp) "
            "VALUES (?, ?, ?, ?)",
            (memory_id, feedback_type, score, time.time()),
        )
        conn.commit()

    def batch_update_memories(self, entries: list[MemoryEntry]) -> None:
        """Batch update multiple memories in a single transaction (including FTS5)."""
        with self._write_lock:
            conn = self._get_conn()
            for entry in entries:
                data = self._entry_to_row(entry)
                placeholders = ", ".join(["?"] * len(data))
                columns = ", ".join(data.keys())
                conn.execute(
                    f"INSERT OR REPLACE INTO memories ({columns}) VALUES ({placeholders})",
                    list(data.values()),
                )
                # Update FTS5 index
                conn.execute("DELETE FROM memories_fts WHERE memory_id=?", (entry.id,))
                conn.execute(
                    "INSERT INTO memories_fts(memory_id, content, tags, category, agent_id, tier) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    [entry.id, entry.content, json.dumps(entry.tags),
                     entry.category.value, entry.agent_id, entry.tier.value],
                )
            conn.commit()

    # ------------------------------------------------------------------
    # Serialization helpers
    # ------------------------------------------------------------------

    def _entry_to_row(self, entry: MemoryEntry) -> dict[str, Any]:
        data = {}
        for f in entry.__dataclass_fields__:
            val = getattr(entry, f)
            if f in _BLOB_FIELDS and val is not None:
                data[f] = np.array(val, dtype=np.float32).tobytes()
            elif f in _JSON_FIELDS:
                data[f] = json.dumps(val)
            elif isinstance(val, IntEnum):
                data[f] = val.value
            elif isinstance(val, Enum):
                data[f] = val.name.lower()
            else:
                data[f] = val
        return data

    def _row_to_entry(self, row: sqlite3.Row) -> MemoryEntry:
        data = dict(row)
        # Restore enums
        data["category"] = MemoryCategory(data["category"])
        data["tier"] = MemoryTier(data["tier"])
        data["veracity"] = VeracityLevel[data["veracity"].upper()]
        data["trust_level"] = TrustLevel(data["trust_level"])
        data["autonomy_level"] = AutonomyLevel(data["autonomy_level"])
        if "confidence_gate_action" in data and isinstance(data["confidence_gate_action"], str):
            data["confidence_gate_action"] = ConfidenceAction(data["confidence_gate_action"])
        # Restore blob → list[float]
        if data.get("embedding") is not None:
            data["embedding"] = np.frombuffer(data["embedding"], dtype=np.float32).tolist()
        # Restore JSON fields
        for f in _JSON_FIELDS:
            if f in data and isinstance(data[f], str):
                data[f] = json.loads(data[f])
        # Restore bool fields (SQLite stores as INTEGER)
        for f in ("is_shmr_candidate", "unresolved"):
            if f in data:
                data[f] = bool(data[f])
        # Remove any extra columns
        valid = {f for f in MemoryEntry.__dataclass_fields__}
        data = {k: v for k, v in data.items() if k in valid}
        return MemoryEntry(**data)
