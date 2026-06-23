"""Prometheus X — Polyphonic 5-Route Retrieval Engine

Fuses 5 retrieval routes + RRF + MMR for comprehensive memory recall.
Sources: MnemosyneV3 polyphonic.py + Prometheus V3 hybrid_search.py + V11 cascading_fetch.py.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Callable, Optional

import numpy as np

from prometheus_x.core.constants import (
    GRAPH_SEARCH_FTS_LIMIT,
    MMR_LAMBDA,
    RRF_K,
    VECTOR_SEARCH_TIER_LIMIT,
)
from prometheus_x.core.schema import (
    MemoryEntry,
    MemoryTier,
    compute_weibull_retention,
    mmr_score,
)
from prometheus_x.memory.store import SQLiteStore


class PolyphonicRetriever:
    """5-route parallel retrieval with RRF fusion and MMR diversity.

    Routes:
        1. FTS5 full-text search
        2. Vector semantic search (cosine similarity)
        3. Graph traversal (Hallway + Tunnel entity relations)
        4. Knowledge base (Beliefs + Consolidated facts)
        5. Cache (TTL-based hot memory)
    """

    # RRF constant (from Prometheus V3)
    RRF_K = RRF_K

    # Route weights for RRF fusion
    ROUTE_WEIGHTS = {
        "fts": 1.0,
        "vector": 1.2,
        "graph": 0.9,
        "knowledge": 1.1,
        "cache": 0.8,
    }

    # MMR lambda (from MnemosyneV3)
    MMR_LAMBDA = MMR_LAMBDA

    # Graph edge type weights (from Prometheus V3 graph search)
    EDGE_WEIGHTS = {
        "causal": 1.0,
        "hallway": 0.95,
        "semantic": 0.9,
        "temporal": 0.8,
        "hierarchical": 0.7,
        "tunnel": 0.85,
    }

    def __init__(self, store: SQLiteStore, embedding_fn: Callable[[str], list[float]] | None = None) -> None:
        self._store = store
        self._embed = embedding_fn  # Callable[[str], list[float]]
        self._cache: dict[str, tuple[float, list[MemoryEntry]]] = {}
        self._cache_ttl = 300.0  # 5 minutes

    def retrieve(
        self,
        query: str,
        limit: int = 20,
        tier_filter: Optional[MemoryTier] = None,
        entity_names: Optional[list[str]] = None,
    ) -> list[MemoryEntry]:
        """Execute 5-route retrieval and return MMR-ranked results."""
        import time

        # Check cache
        cache_key = f"{query}:{tier_filter}:{limit}"
        if cache_key in self._cache:
            ts, cached = self._cache[cache_key]
            if time.time() - ts < self._cache_ttl:
                return cached[:limit]

        # Route 1: FTS5
        fts_results = self._store.search_fts(query, limit=limit * 3)

        # Route 2: Vector semantic
        vector_results = self._vector_search(query, limit=limit * 3)

        # Route 3: Graph traversal
        graph_scores: dict[str, float] = {}
        graph_results = self._graph_search(query, entity_names or [], limit=limit * 2, scores=graph_scores)

        # Route 4: Knowledge base
        kb_results = self._knowledge_search(query, limit=limit * 2)

        # Route 5: Cache (recently accessed)
        cache_results = self._cache_search(query, limit=limit)

        # RRF Fusion (no side effects on entries)
        all_results, rrf_scores = self._rrf_fusion([
            ("fts", fts_results),
            ("vector", vector_results),
            ("graph", graph_results),
            ("knowledge", kb_results),
            ("cache", cache_results),
        ])

        # Apply Weibull retention filter (no side effects on entries)
        filtered, retention_scores = self._apply_retention_filter(all_results)

        # MMR diversity
        mmr_results = self._mmr_rerank(filtered, limit, rrf_scores)

        # Cache results
        self._cache[cache_key] = (time.time(), mmr_results)

        return mmr_results

    # ------------------------------------------------------------------
    # Route implementations
    # ------------------------------------------------------------------

    def _vector_search(self, query: str, limit: int) -> list[MemoryEntry]:
        """Cosine similarity search across all tiers."""
        if self._embed is None:
            return []
        query_vec = np.array(self._embed(query), dtype=np.float32)
        if np.linalg.norm(query_vec) == 0:
            return []

        results: list[tuple[float, MemoryEntry]] = []
        # Search across all tiers, not just WORKING
        for tier in MemoryTier:
            for entry in self._store.get_by_tier(tier, limit=VECTOR_SEARCH_TIER_LIMIT):
                if entry.embedding is None:
                    continue
                entry_vec = np.array(entry.embedding, dtype=np.float32)
                norm = np.linalg.norm(entry_vec)
                if norm == 0:
                    continue
                cosine = float(np.dot(query_vec, entry_vec) / (np.linalg.norm(query_vec) * norm))
                results.append((cosine, entry))

        results.sort(key=lambda x: x[0], reverse=True)
        return [e for _, e in results[:limit]]

    def _graph_search(
        self, query: str, entity_names: list[str], limit: int,
        scores: Optional[dict[str, float]] = None,
    ) -> list[MemoryEntry]:
        """Graph traversal via Hallway/Tunnel entity relations."""
        if not entity_names:
            return []

        seen_ids: set[str] = set()
        results: list[MemoryEntry] = []

        for entity in entity_names:
            fts_hits = self._store.search_fts(entity, limit=GRAPH_SEARCH_FTS_LIMIT)
            for mem in fts_hits:
                if mem.id not in seen_ids:
                    seen_ids.add(mem.id)
                    if scores is not None:
                        scores[mem.id] = self.EDGE_WEIGHTS.get("hallway", 0.95)
                    results.append(mem)

            edges = self._store.get_edges_from(entity)
            for edge in edges:
                target = self._store.get_memory(edge.target_id)
                if target and target.id not in seen_ids:
                    seen_ids.add(target.id)
                    weight = self.EDGE_WEIGHTS.get(edge.edge_type.value, 0.5)
                    if scores is not None:
                        scores[target.id] = weight
                    results.append(target)

        if scores:
            results.sort(key=lambda e: scores.get(e.id, 0), reverse=True)
        return results[:limit]

    def _knowledge_search(self, query: str, limit: int) -> list[MemoryEntry]:
        """Search beliefs and consolidated facts (from MnemosyneV3:130-145)."""
        beliefs = self._store.get_beliefs(min_confidence=0.5)
        results: list[MemoryEntry] = []
        for belief in beliefs[:limit]:
            # Convert belief to MemoryEntry for unified processing
            entry = MemoryEntry(
                id=belief.id,
                content=belief.statement,
                confidence=belief.confidence,
                importance=belief.confidence,
                metadata={"_kb_source": "belief", "_kb_boost": 1.2},
            )
            results.append(entry)
        return results

    def _cache_search(self, query: str, limit: int) -> list[MemoryEntry]:
        """Recently accessed memories (hot cache)."""
        # Simple heuristic: get most recently accessed from working tier
        all_working = self._store.get_by_tier(MemoryTier.WORKING, limit=limit * 2)
        all_working.sort(key=lambda e: e.last_accessed, reverse=True)
        return all_working[:limit]

    # ------------------------------------------------------------------
    # RRF Fusion (from Prometheus V3 hybrid_search.py)
    # ------------------------------------------------------------------

    def _rrf_fusion(
        self, route_results: list[tuple[str, list[MemoryEntry]]]
    ) -> tuple[list[MemoryEntry], dict[str, float]]:
        """Reciprocal Rank Fusion across all routes. Returns (entries, scores)."""
        score_map: dict[str, float] = defaultdict(float)
        entry_map: dict[str, MemoryEntry] = {}

        for route_name, results in route_results:
            weight = self.ROUTE_WEIGHTS.get(route_name, 1.0)
            for rank, entry in enumerate(results):
                rrf_score = weight / (self.RRF_K + rank + 1)
                score_map[entry.id] += rrf_score
                if entry.id not in entry_map:
                    entry_map[entry.id] = entry

        sorted_ids = sorted(score_map.keys(), key=lambda x: score_map[x], reverse=True)
        return [entry_map[eid] for eid in sorted_ids], dict(score_map)

    def _apply_retention_filter(self, entries: list[MemoryEntry]) -> tuple[list[MemoryEntry], dict[str, float]]:
        """Filter out memories with very low retention. Returns (entries, retention_scores)."""
        
        result = []
        retention_scores: dict[str, float] = {}
        for entry in entries:
            age_days = (time.time() - entry.created_at) / 86400.0
            retention = compute_weibull_retention(
                entry.tier, age_days, entry.importance, entry.consecutive_hits
            )
            if retention >= 0.05 or entry.tier == MemoryTier.PROCEDURAL:
                retention_scores[entry.id] = retention
                result.append(entry)
        return result, retention_scores

    # ------------------------------------------------------------------
    # MMR Diversity Reranking (from MnemosyneV3 models.py:426-429)
    # ------------------------------------------------------------------

    def _mmr_rerank(self, entries: list[MemoryEntry], limit: int,
                    rrf_scores: dict[str, float] | None = None) -> list[MemoryEntry]:
        """Maximal Marginal Relevance: balance relevance and diversity."""
        if not entries:
            return []

        rrf_scores = rrf_scores or {}
        selected: list[MemoryEntry] = []
        candidates = list(entries)

        # Precompute embeddings for similarity
        embeddings: dict[str, np.ndarray] = {}
        for e in candidates:
            if e.embedding:
                embeddings[e.id] = np.array(e.embedding, dtype=np.float32)

        while candidates and len(selected) < limit:
            best_idx = -1
            best_mmr = -float("inf")

            for i, candidate in enumerate(candidates):
                relevance = rrf_scores.get(candidate.id, 0.5)

                # Max similarity to already selected
                max_sim = 0.0
                if candidate.id in embeddings:
                    cand_vec = embeddings[candidate.id]
                    for sel in selected:
                        if sel.id in embeddings:
                            sel_vec = embeddings[sel.id]
                            sim = float(np.dot(cand_vec, sel_vec) / (
                                np.linalg.norm(cand_vec) * np.linalg.norm(sel_vec) + 1e-8
                            ))
                            max_sim = max(max_sim, sim)

                mmr = mmr_score(relevance, max_sim, self.MMR_LAMBDA)
                if mmr > best_mmr:
                    best_mmr = mmr
                    best_idx = i

            if best_idx >= 0:
                selected.append(candidates.pop(best_idx))

        return selected
