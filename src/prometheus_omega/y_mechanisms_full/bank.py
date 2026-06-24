"""Memory Bank — 4-tier migration + Weibull forgetting + memory gravity."""
from __future__ import annotations

import logging
import math
import time
from typing import Any

from ..schema import (
    Node, NodeType, MemoryTier, MemoryScope, EdgeType,
    WeibullParams, TIER_MIGRATION_THRESHOLDS, CommitState,
)
from ..store import Store, get_store
from ..config import get_config

logger = logging.getLogger(__name__)


class MemoryBank:
    """4-tier memory bank with Weibull forgetting and gravity-based routing."""

    TIER_RETENTION_PARAMS: dict[MemoryTier, WeibullParams] = {
        MemoryTier.WORKING: WeibullParams(shape=0.7, scale=300.0),
        MemoryTier.EPISODIC: WeibullParams(shape=0.8, scale=86400.0),
        MemoryTier.SEMANTIC: WeibullParams(shape=0.9, scale=2592000.0),
        MemoryTier.PROCEDURAL: WeibullParams(shape=1.0, scale=7776000.0),
    }

    def __init__(self, store: Store | None = None) -> None:
        self._store = store or get_store()

    def store(self, content: str, node_type: NodeType = NodeType.NOTE,
              tier: MemoryTier = MemoryTier.WORKING,
              importance: float = 0.5, tags: list[str] | None = None,
              source: str = "", summary: str = "") -> Node:
        """Write a node to memory."""
        node = Node(
            type=node_type,
            tier=tier,
            importance=importance,
            tags=tags or [],
            weibull=self.TIER_RETENTION_PARAMS[tier],
            commit_state=CommitState.DRAFT,
            created_at=time.time(),
            updated_at=time.time(),
        )
        node.payload.content = content
        node.payload.summary = summary
        node.payload.keywords = tags or []
        node.provenance.source = source
        self._store.put_node(node)
        logger.info(f"Stored {node_type.value} in {tier.value}: importance={importance:.2f}")
        return node

    def recall(self, node_id: str) -> Node | None:
        """Read a node, increment access count."""
        node = self._store.get_node(node_id)
        if node is None:
            return None
        node.access_count += 1
        node.updated_at = time.time()
        self._store.update_node(node)
        return node

    def compute_retention(self, node: Node) -> float:
        """Weibull retention: exp(-(t/λ)^k) * importance * hit_boost."""
        age = time.time() - node.created_at
        k = node.weibull.shape
        lam = node.weibull.scale
        if lam <= 0:
            return 0.0
        base = math.exp(-((age / lam) ** k))
        hit_boost = 1 + 0.1 * node.access_count
        return base * node.importance * min(hit_boost, 3.0)

    def compute_gravity(self, node: Node) -> float:
        """Memory gravity: importance * (1+log(1+access)) * retention * freshness."""
        age = time.time() - node.created_at
        retention = self.compute_retention(node)
        access_factor = 1 + math.log(1 + node.access_count)
        freshness = 1.0 / (1.0 + age / 86400.0)
        gravity = node.importance * access_factor * retention * freshness
        return gravity

    def should_migrate(self, node: Node) -> MemoryTier | None:
        """Check if node should migrate to next tier."""
        tier_order = [MemoryTier.WORKING, MemoryTier.EPISODIC, MemoryTier.SEMANTIC, MemoryTier.PROCEDURAL]
        current_idx = tier_order.index(node.tier)
        if current_idx >= len(tier_order) - 1:
            return None
        next_tier = tier_order[current_idx + 1]
        key = (node.tier, next_tier)
        thresholds = TIER_MIGRATION_THRESHOLDS.get(key)
        if thresholds is None:
            return None
        age = time.time() - node.created_at
        if (age >= thresholds["min_age_s"] and
                node.importance >= thresholds["min_importance"] and
                node.access_count >= thresholds["min_access"]):
            return next_tier
        return None

    def run_migration(self) -> dict[str, int]:
        """Migrate eligible nodes to higher tiers."""
        stats = {"migrated": 0, "forgotten": 0, "kept": 0}
        for tier in [MemoryTier.WORKING, MemoryTier.EPISODIC, MemoryTier.SEMANTIC]:
            nodes = self._store.query_nodes(tier=tier)
            for node in nodes:
                retention = self.compute_retention(node)
                node.retention = retention
                if retention < 0.05:
                    self._store.delete_node(node.id)
                    stats["forgotten"] += 1
                    continue
                next_tier = self.should_migrate(node)
                if next_tier is not None:
                    node.tier = next_tier
                    node.weibull = self.TIER_RETENTION_PARAMS[next_tier]
                    node.updated_at = time.time()
                    self._store.update_node(node)
                    stats["migrated"] += 1
                else:
                    self._store.update_node(node)
                    stats["kept"] += 1
        logger.info(f"Migration: {stats}")
        return stats

    def run_aging(self) -> dict[str, int]:
        """Apply Weibull aging to all nodes."""
        stats = {"aged": 0, "forgotten": 0}
        for tier in MemoryTier:
            nodes = self._store.query_nodes(tier=tier)
            for node in nodes:
                retention = self.compute_retention(node)
                node.retention = retention
                if retention < 0.05:
                    self._store.delete_node(node.id)
                    stats["forgotten"] += 1
                else:
                    self._store.update_node(node)
                    stats["aged"] += 1
        return stats

    def search(self, query: str, limit: int = 10, tier: MemoryTier | None = None) -> list[Node]:
        """FTS5 search with optional tier filter."""
        results = self._store.fts_search(query, limit=limit * 3)
        if tier is not None:
            results = [n for n in results if n.tier == tier]
        # Re-rank by gravity
        results.sort(key=lambda n: self.compute_gravity(n), reverse=True)
        return results[:limit]

    def get_gravity_distribution(self) -> dict[str, list[tuple[str, float]]]:
        """Get gravity scores across tiers for visualization."""
        dist: dict[str, list[tuple[str, float]]] = {}
        for tier in MemoryTier:
            nodes = self._store.query_nodes(tier=tier, limit=50)
            dist[tier.value] = [(n.id[:8], self.compute_gravity(n)) for n in nodes]
        return dist
