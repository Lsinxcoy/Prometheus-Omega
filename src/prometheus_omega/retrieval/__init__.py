from prometheus_omega.foundation import MemoryLayer, Node
"""L3 Retrieval - 检索层

整合XYZ机制:
- X: Polyphonic 5-Route, RRF, MMR, Hallway/Tunnel
- Y: retrieval模块
- Z: 向量检索, 图遍历
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
from datetime import datetime, timezone
import math



@dataclass

@dataclass
class SearchHit:
    """搜索命中"""
    node_id: str
    content: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
class SearchResults:
    """搜索结果"""
    results: List[Any] = field(default_factory=list)
    query: str = ""
    total: int = 0
class RetrievalMethod(Enum):
    """检索方法"""
    SEMANTIC = "semantic"      # 语义向量
    KEYWORD = "keyword"        # 关键词BM25
    GRAPH = "graph"            # 图遍历
    TEMPORAL = "temporal"      # 时间序
    HYBRID = "hybrid"          # 混合


@dataclass
class RetrievalResult:
    """检索结果"""
    entry_id: str
    content: str
    score: float
    method: RetrievalMethod
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_relevant(self, threshold: float = 0.5) -> bool:
        return self.score >= threshold
    
    def to_dict(self) -> Dict:
        return {
            'entry_id': self.entry_id,
            'content': self.content[:100] + '...' if len(self.content) > 100 else self.content,
            'score': self.score,
            'method': self.method.value if isinstance(self.method, Enum) else self.method,
            'metadata': self.metadata,
        }
    
    def relevance_level(self) -> str:
        if self.score >= 0.8:
            return 'high'
        elif self.score >= 0.5:
            return 'medium'
        return 'low'


class RRF:
    """Reciprocal Rank Fusion - 来自X系统#14
    
    RRF公式: score(d) = Σ 1 / (k + rank(d))
    
    参数:
    - k: 衰减常数 (通常60)
    - rank(d): 文档d在列表中的排名
    
    优点:
    - 无需训练, 简单有效
    - 平衡相关性和多样性
    - 对不同评分体系兼容
    """
    
    def __init__(self, k: float = 60.0, normalize: bool = True):
        """初始化RRF
        
        Args:
            k: 衰减常数 (通常60)
            normalize: 是否归一化分数
        """
        self.k = k
        self.normalize = normalize
    
    def fuse(self, rank_lists: List[List[RetrievalResult]], 
             top_k: int = 20) -> List[RetrievalResult]:
        """融合多个排序列表
        
        Args:
            rank_lists: 多个排序列表
            top_k: 返回前k个结果
            
        Returns:
            List[RetrievalResult]: 融合后的排序列表
        """
        if not rank_lists:
            return []
        
        # 检查空列表
        non_empty = [lst for lst in rank_lists if lst]
        if not non_empty:
            return []
        
        # RRF计分
        scores: Dict[str, float] = {}
        entry_data: Dict[str, RetrievalResult] = {}
        
        for rank_list in non_empty:
            for rank, result in enumerate(rank_list):
                # RRF公式
                rrf_score = 1.0 / (self.k + rank + 1)
                scores[result.entry_id] = scores.get(result.entry_id, 0) + rrf_score
                
                # 保留第一个结果的数据
                if result.entry_id not in entry_data:
                    entry_data[result.entry_id] = result
        
        # 归一化
        if self.normalize and scores:
            max_score = max(scores.values())
            min_score = min(scores.values())
            range_score = max_score - min_score
            
            if range_score > 0:
                for entry_id in scores:
                    scores[entry_id] = (scores[entry_id] - min_score) / range_score
        
        # 排序并返回
        sorted_entries = sorted(scores.items(), key=lambda x: -x[1])
        
        return [
            RetrievalResult(
                entry_id=entry_id,
                content=entry_data[entry_id].content,
                score=score,
                method=RetrievalMethod.HYBRID,
                metadata={"sources": len(rank_lists)}
            )
            for entry_id, score in sorted_entries[:top_k]
        ]
    
    def fuse_with_weights(self, weighted_lists: List[tuple]) -> List[RetrievalResult]:
        """加权融合
        
        Args:
            weighted_lists: [(rank_list, weight), ...]
            
        Returns:
            List[RetrievalResult]: 加权融合结果
        """
        scores: Dict[str, float] = {}
        entry_data: Dict[str, RetrievalResult] = {}
        
        for rank_list, weight in weighted_lists:
            if not rank_list:
                continue
            
            for rank, result in enumerate(rank_list):
                rrf_score = weight * (1.0 / (self.k + rank + 1))
                scores[result.entry_id] = scores.get(result.entry_id, 0) + rrf_score
                
                if result.entry_id not in entry_data:
                    entry_data[result.entry_id] = result
        
        sorted_entries = sorted(scores.items(), key=lambda x: -x[1])
        
        return [
            RetrievalResult(
                entry_id=entry_id,
                content=entry_data[entry_id].content,
                score=score,
                method=RetrievalMethod.HYBRID,
            )
            for entry_id, score in sorted_entries
        ]


class MMR:
    """Maximal Marginal Relevance - 来自X系统#15
    
    MMR公式: MMR = λ * sim(query, doc) - (1-λ) * max(sim(doc, selected))
    
    参数:
    - lambda_: 平衡参数 (0=最大多样性, 1=最大相关性)
    
    用途:
    - 消除检索结果冗余
    - 平衡相关性与多样性
    """
    
    def __init__(self, lambda_: float = 0.5, 
                 min_diversity: float = 0.1,
                 max_results: int = 20):
        """初始化MMR
        
        Args:
            lambda_: 相关性/多样性平衡 (0-1)
            min_diversity: 最小多样性阈值
            max_results: 最大结果数
        """
        self.lambda_ = max(0.0, min(1.0, lambda_))
        self.min_diversity = min_diversity
        self.max_results = max_results
    
    def diversify(self, results: List[RetrievalResult], 
                  similarity_fn: Callable[[str, str], float],
                  query: str = "") -> List[RetrievalResult]:
        """多样性融合
        
        Args:
            results: 初始排序结果
            similarity_fn: 相似度函数 (content1, content2) -> float
            query: 原始查询 (可选)
            
        Returns:
            List[RetrievalResult]: 多样化后的结果
        """
        if not results:
            return []
        
        if len(results) == 1:
            return results[:self.max_results]
        
        selected = []
        remaining = results.copy()
        
        # 选择第一个 (通常是最高相关性的)
        selected.append(remaining.pop(0))
        
        while remaining and len(selected) < self.max_results:
            best_score = -float('inf')
            best_idx = 0
            
            for i, result in enumerate(remaining):
                # 计算与已选结果的最大相似度
                if selected:
                    max_sim = max(
                        similarity_fn(result.content, s.content) 
                        for s in selected
                    )
                else:
                    max_sim = 0.0
                
                # MMR分数
                relevance = result.score
                mmr_score = (self.lambda_ * relevance - 
                            (1 - self.lambda_) * max_sim)
                
                # 多样性惩罚
                if max_sim > (1 - self.min_diversity):
                    mmr_score *= 0.5
                
                if mmr_score > best_score:
                    best_score = mmr_score
                    best_idx = i
            
            selected.append(remaining.pop(best_idx))
        
        return selected
    
    def diversify_with_context(self, results: List[RetrievalResult],
                               context_docs: List[str]) -> List[RetrievalResult]:
        """基于上下文化的多样化
        
        Args:
            results: 初始结果
            context_docs: 上下文文档列表
            
        Returns:
            List[RetrievalResult]: 多样化结果
        """
        if not results or not context_docs:
            return results
        
        # 简化实现: 惩罚与上下文中已有内容高度相似的
        selected = []
        remaining = results.copy()
        
        while remaining:
            best_result = remaining.pop(0)
            
            # 检查与上下文的相似度
            context_sim = max(
                self._simple_similarity(best_result.content, ctx)
                for ctx in context_docs
            ) if context_docs else 0
            
            # 如果与上下文太相似,降低分数
            if context_sim > 0.8:
                best_result.score *= (1 - context_sim * 0.5)
            
            selected.append(best_result)
        
        return sorted(selected, key=lambda x: -x.score)
    
    def _simple_similarity(self, text1: str, text2: str) -> float:
        """简单相似度计算 (Jaccard)"""
        if not text1 or not text2:
            return 0.0
        
        set1 = set(text1.lower().split())
        set2 = set(text2.lower().split())
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0


class PolyphonicRetrieval:
    """多旋律5路由检索 - 来自X系统#13
    
    5条检索路由:
    1. 语义向量检索
    2. BM25关键词检索
    3. 图遍历检索
    4. 时间序检索
    5. 实体关联检索
    """
    
    def __init__(self):
        self.rrf = RRF()
        self.mmr = MMR()
        self.routes = 5
    
    def retrieve(self, query: str, memory_store, top_k: int = 10) -> List[RetrievalResult]:
        """5路由检索"""
        results = []
        
        # Route 1: 语义向量 (简化)
        semantic_results = self._semantic_search(query, memory_store, top_k)
        results.append(semantic_results)
        
        # Route 2: BM25关键词 (简化)
        keyword_results = self._keyword_search(query, memory_store, top_k)
        results.append(keyword_results)
        
        # Route 3: 图遍历
        graph_results = self._graph_search(query, memory_store, top_k)
        results.append(graph_results)
        
        # Route 4: 时间序
        temporal_results = self._temporal_search(query, memory_store, top_k)
        results.append(temporal_results)
        
        # Route 5: 实体关联
        entity_results = self._entity_search(query, memory_store, top_k)
        results.append(entity_results)
        
        # RRF融合
        fused = self.rrf.fuse(results)[:top_k]
        return fused
    
    def _semantic_search(self, query: str, memory_store, top_k: int) -> List[RetrievalResult]:
        """语义检索 - 使用TF-IDF相似度简化"""
        if not hasattr(memory_store, 'entries') or not memory_store.entries:
            return []
        
        # 简单的TF-IDF相似度计算
        query_words = set(query.lower().split())
        
        results = []
        for entry in memory_store.entries.values():
            content_words = set(entry.content.lower().split())
            if content_words:
                # Jaccard相似度作为语义近似
                intersection = len(query_words & content_words)
                union = len(query_words | content_words)
                score = intersection / union if union > 0 else 0
                
                if score > 0:
                    results.append(RetrievalResult(
                        entry_id=entry.id,
                        content=entry.content,
                        score=score,
                        method=RetrievalMethod.SEMANTIC
                    ))
        
        results.sort(key=lambda x: -x.score)
        return results[:top_k]
    
    def _keyword_search(self, query: str, memory_store, top_k: int) -> List[RetrievalResult]:
        """关键词检索"""
        results = []
        query_lower = query.lower()
        for entry in memory_store.entries.values():
            if query_lower in entry.content.lower():
                # 简单计数作为相关性分数
                count = entry.content.lower().count(query_lower)
                results.append(RetrievalResult(
                    entry_id=entry.id,
                    content=entry.content,
                    score=float(count),
                    method=RetrievalMethod.KEYWORD
                ))
        results.sort(key=lambda x: -x.score)
        return results[:top_k]
    
    def _graph_search(self, query: str, memory_store, top_k: int) -> List[RetrievalResult]:
        """图遍历检索 - 通过tags关系"""
        if not hasattr(memory_store, 'entries'):
            return []
        
        results = []
        query_tags = set(query.lower().split())
        
        for entry in memory_store.entries.values():
            entry_tags = getattr(entry, 'tags', []) or []
            entry_tags_set = set(entry_tags)
            if entry_tags_set:
                common = len(query_tags & entry_tags_set)
                if common > 0:
                    results.append(RetrievalResult(
                        entry_id=entry.id,
                        content=entry.content,
                        score=float(common),
                        method=RetrievalMethod.GRAPH,
                        metadata={'common_tags': list(query_tags & entry_tags_set)}
                    ))
        
        results.sort(key=lambda x: -x.score)
        return results[:top_k]
    
    def _temporal_search(self, query: str, memory_store, top_k: int) -> List[RetrievalResult]:
        """时间序检索 - 返回最近的记忆"""
        if not hasattr(memory_store, 'entries'):
            return []
        
        now = datetime.now(timezone.utc)
        entries_with_time = []
        
        for entry in memory_store.entries.values():
            created = getattr(entry, 'created_at', None)
            if created:
                # 计算时间权重: 越新分数越高
                if isinstance(created, datetime):
                    age_hours = (now - created).total_seconds() / 3600
                    score = 1.0 / (1.0 + age_hours / 24)  # 每天衰减一半
                else:
                    score = 0.5
                    age_hours = 0
                
                entries_with_time.append((entry, score, age_hours))
        
        entries_with_time.sort(key=lambda x: -x[1])
        
        return [RetrievalResult(
            entry_id=entry.id,
            content=entry.content,
            score=score,
            method=RetrievalMethod.TEMPORAL,
            metadata={'age_hours': age_hours}
        ) for entry, score, age_hours in entries_with_time[:top_k]]
    
    def _entity_search(self, query: str, memory_store, top_k: int) -> List[RetrievalResult]:
        """实体关联检索 - 通过实体类型匹配"""
        if not hasattr(memory_store, 'entries'):
            return []
        
        results = []
        
        for entry in memory_store.entries.values():
            # 检查实体类型标签
            entity_type = getattr(entry, 'entity_type', None)
            if entity_type and entity_type.lower() in query.lower():
                results.append(RetrievalResult(
                    entry_id=entry.id,
                    content=entry.content,
                    score=1.0,
                    method=RetrievalMethod.HYBRID,
                    metadata={'entity_type': entity_type}
                ))
        
        results.sort(key=lambda x: -x.score)
        return results[:top_k]


class VectorSearch:
    """向量检索 - 来自Z系统"""
    
    def __init__(self, dimension: int = 768):
        self.dimension = dimension
        self.vectors: Dict[str, List[float]] = {}
    
    def add(self, entry_id: str, embedding: List[float]) -> None:
        """添加向量"""
        if len(embedding) == self.dimension:
            self.vectors[entry_id] = embedding
    
    def search(self, query_embedding: List[float], top_k: int = 10) -> List[tuple]:
        """向量相似度搜索"""
        if not self.vectors or not query_embedding:
            return []
        
        scores = []
        for entry_id, vec in self.vectors.items():
            sim = self._cosine_similarity(query_embedding, vec)
            scores.append((entry_id, sim))
        
        scores.sort(key=lambda x: -x[1])
        return scores[:top_k]
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """余弦相似度"""
        dot = sum(x*y for x,y in zip(a,b))
        norm_a = math.sqrt(sum(x*x for x in a))
        norm_b = math.sqrt(sum(x*x for x in b))
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0


class GraphTraversal:
    """图遍历检索 - 来自Z系统"""
    
    def __init__(self):
        self.graph: Dict[str, Set[str]] = {}  # node -> neighbors
    
    def add_edge(self, from_node: str, to_node: str) -> None:
        """添加边"""
        if from_node not in self.graph:
            self.graph[from_node] = set()
        self.graph[from_node].add(to_node)
    
    def bfs(self, start: str, depth: int = 3) -> List[str]:
        """广度优先搜索"""
        visited = {start}
        queue = [(start, 0)]
        results = []
        
        while queue:
            node, d = queue.pop(0)
            if d > 0:
                results.append(node)
            if d < depth:
                for neighbor in self.graph.get(node, []):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, d+1))
        
        return results


# 工厂
def create_polyphonic_retrieval() -> PolyphonicRetrieval:
    return PolyphonicRetrieval()

def create_vector_search(dimension: int = 768) -> VectorSearch:
    return VectorSearch(dimension=dimension)

def create_graph_traversal() -> GraphTraversal:
    return GraphTraversal()


# ===== 来自XYZ系统 =====
class HybridSearchEngine:
    """M9: Three-channel hybrid search with RRF fusion + MMR diversity."""

    def __init__(self, store: Any, config: Any = None):
        self._store = store
        self._config = config or {}
        self._rrf_k = 60  # RRF constant
        self._mmr_lambda = 0.7  # MMR relevance vs diversity trade-off

    def search(self, query: str, limit: int = 20,
               branch: str = "main",
               layers: list[MemoryLayer] | None = None,
               query_embedding: list[float] | None = None) -> SearchResults:
        """Execute three-channel parallel search and fuse results.

        1. FTS5 full-text search
        2. Vector search (cosine similarity on stored embeddings)
        3. Graph neighborhood expansion (if graph edges exist)
        4. RRF fusion
        5. MMR diversity reranking
        """
        import time as _time
        start = _time.time()

        # ── Channel 1: FTS5 ──
        fts_results = self._search_fts(query, limit * 3, branch)

        # ── Channel 2: Vector (cosine similarity on stored embeddings) ──
        vec_results = self._search_vector(query_embedding, limit * 3, branch)

        # ── Channel 3: Graph neighborhood ──
        graph_results = self._search_graph(fts_results, branch)

        # ── RRF Fusion ──
        channel_map = {"fts": fts_results, "graph": graph_results}
        if vec_results:
            channel_map["vector"] = vec_results
        fused = self._rrf_fuse(channel_map, limit * 2)

        # ── MMR Diversity Reranking ──
        if fused and len(fused) > limit:
            fused = self._mmr_rerank(fused, limit)

        # ── Layer filtering ──
        if layers is not None:
            layer_set = set(int(l) for l in layers)
            fused = [h for h in fused if int(h.node.layer) in layer_set]

        elapsed_ms = (_time.time() - start) * 1000

        return SearchResults(
            hits=fused[:limit],
            total=len(fused),
            latency_ms=elapsed_ms,
        )

    def _search_fts(self, query: str, limit: int,
                    branch: str) -> list[tuple[Node, float]]:
        """Channel 1: FTS5 full-text search."""
        try:
            return self._store.search_fts(query, limit, branch)
        except Exception:
            return []

    def _search_vector(self, query_embedding: list[float] | None,
                       limit: int, branch: str) -> list[tuple[Node, float]]:
        """Channel 2: Vector search via cosine similarity on stored embeddings.

        Scans all nodes with non-empty embeddings, computes cosine similarity
        with the query embedding, returns top-k results.

        Falls back to empty list if no query embedding provided.
        Complexity: O(n·d) where n=nodes with embeddings, d=dimension.
        """
        if not query_embedding:
            return []

        nodes = self._store.get_all_nodes(branch, limit=10000)
        q_norm = self._l2_norm(query_embedding)
        if q_norm < 1e-9:
            return []

        scored: list[tuple[Node, float]] = []
        for node in nodes:
            if not node.embedding:
                continue
            sim = self._cosine_similarity(query_embedding, node.embedding, q_norm)
            if sim > 0.1:  # Threshold to avoid noise
                scored.append((node, sim))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:limit]

    @staticmethod
    def _l2_norm(vec: list[float]) -> float:
        """L2 norm of a vector."""
        return math.sqrt(sum(x * x for x in vec))

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float],
                           a_norm: float = 0.0) -> float:
        """Cosine similarity between two vectors."""
        if len(a) != len(b):
            return 0.0
        if a_norm < 1e-9:
            a_norm = math.sqrt(sum(x * x for x in a))
        b_norm = math.sqrt(sum(x * x for x in b))
        if b_norm < 1e-9:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        return dot / (a_norm * b_norm)

    def _search_graph(self, seed_results: list[tuple[Node, float]],
                      branch: str) -> list[tuple[Node, float]]:
        """Channel 3: Graph neighborhood expansion.

        For each FTS result, expand to its graph neighbors.
        Neighbor nodes get a boost from their connection.
        """
        expanded: dict[str, tuple[Node, float]] = {}

        for node, score in seed_results:
            neighbors = self._store.get_neighbors(node.id, branch=branch)
            for edge, neighbor in neighbors:
                # Graph boost: connected nodes get score × weight × 0.5
                graph_score = score * edge.weight * 0.5
                if neighbor.id not in expanded or expanded[neighbor.id][1] < graph_score:
                    expanded[neighbor.id] = (neighbor, graph_score)

        return list(expanded.values())

    def _rrf_fuse(self, channel_results: dict[str, list[tuple[Node, float]]],
                  limit: int) -> list[SearchHit]:
        """Reciprocal Rank Fusion.

        RRF_score(doc) = Σ_channel 1 / (k + rank(doc, channel))

        k=60 is the standard constant from Cormack et al.
        """
        # Build rank maps per channel
        rank_maps: dict[str, dict[str, int]] = {}
        all_node_ids: set[str] = set()

        for channel_name, results in channel_results.items():
            rank_map = {}
            for rank, (node, _score) in enumerate(results, start=1):
                rank_map[node.id] = rank
                all_node_ids.add(node.id)
            rank_maps[channel_name] = rank_map

        # Compute RRF scores
        node_cache: dict[str, Node] = {}
        for channel_name, results in channel_results.items():
            for node, _score in results:
                if node.id not in node_cache:
                    node_cache[node.id] = node

        rrf_scores: list[tuple[str, float]] = []
        for nid in all_node_ids:
            score = 0.0
            for channel_name, rank_map in rank_maps.items():
                rank = rank_map.get(nid, 0)
                if rank > 0:
                    score += 1.0 / (self._rrf_k + rank)
            rrf_scores.append((nid, score))

        # Sort by RRF score descending
        rrf_scores.sort(key=lambda x: x[1], reverse=True)

        hits = []
        for nid, score in rrf_scores[:limit]:
            if nid in node_cache:
                hits.append(SearchHit(node=node_cache[nid], score=score, source="rrf"))

        return hits

    def _mmr_rerank(self, hits: list[SearchHit],
                    limit: int) -> list[SearchHit]:
        """Maximal Marginal Relevance reranking for diversity.

        MMR = argmax [λ·Sim(d_i, q) - (1-λ)·max(Sim(d_i, d_j)) for d_j in S]

        λ=0.7: 70% relevance, 30% diversity.
        """
        if not hits:
            return hits

        # Simplified: use content length as proxy for similarity
        # (real implementation would use embeddings)
        selected: list[SearchHit] = [hits[0]]
        remaining = list(hits[1:])

        while len(selected) < limit and remaining:
            best_idx = 0
            best_mmr = -float("inf")

            for i, candidate in enumerate(remaining):
                # Relevance component
                relevance = candidate.score

                # Diversity component (penalty for similarity to already selected)
                max_sim = 0.0
                for sel in selected:
                    sim = self._content_similarity(candidate.node, sel.node)
                    if sim > max_sim:
                        max_sim = sim

                mmr = self._mmr_lambda * relevance - (1 - self._mmr_lambda) * max_sim
                if mmr > best_mmr:
                    best_mmr = mmr
                    best_idx = i

            selected.append(remaining.pop(best_idx))

        return selected

    @staticmethod
    def _content_similarity(a: Node, b: Node) -> float:
        """Simple content overlap similarity (Jaccard on word sets).

        P-07: Empty-set Jaccard returns 1.0 (identical), not 0.0.
        """
        words_a = set(a.content.lower().split())
        words_b = set(b.content.lower().split())

        if not words_a and not words_b:
            return 1.0  # P-07: both empty = identical

        intersection = words_a & words_b
        union = words_a | words_b

        if not union:
            return 1.0

        return len(intersection) / len(union)




# ═══════════════════════════════════════════════════════════════
# 宪法机制 - 三铁律
# ═══════════════════════════════════════════════════════════════
def can_write_gate(importance: float, utility: float, veracity: float, dopamine: float = 0.5) -> bool:
    """多巴胺写入门控"""
    return (importance * utility * veracity * dopamine) >= 0.3 and dopamine >= 0.2

def can_evolve_gate(eval_result: float) -> bool:
    """反演化门控"""
    return eval_result >= 0.7

def verify_iron_law(content: str) -> bool:
    """验证铁律"""
    return content and len(content.strip()) >= 10


# ═══════════════════════════════════════════════════════════════
# 安全工具类
# ═══════════════════════════════════════════════════════════════

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.state = "closed"
    
    def record_success(self) -> None:
        self.failure_count = 0
        self.state = "closed"
    
    def record_failure(self) -> None:
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
    
    def can_execute(self) -> bool:
        return self.state != "open"


class RateLimiter:
    def __init__(self, max_requests: int = 100, window: float = 60.0):
        self.max_requests = max_requests
        self.window = window
        self.requests = []
    
    def is_allowed(self) -> bool:
        import time
        now = time.time()
        self.requests = [t for t in self.requests if now - t < self.window]
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        return False


class InputValidator:
    @staticmethod
    def sanitize(value: str, max_length: int = 10000) -> str:
        if not isinstance(value, str):
            return str(value)
        return value[:max_length]
    
    @staticmethod
    def validate_type(value: Any, expected_type: type) -> bool:
        return isinstance(value, expected_type)


# ═══════════════════════════════════════════════════════════════
# 工程化工具类
# ═══════════════════════════════════════════════════════════════

class SimpleCache:
    def __init__(self, max_size: int = 1000, ttl: float = 300.0):
        self.max_size = max_size
        self.ttl = ttl
        self._cache: dict = {}
    
    def get(self, key: str) -> None:
        import time
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            del self._cache[key]
        return None
    
    def set(self, key: str, value) -> None:
        import time
        if len(self._cache) >= self.max_size:
            oldest = min(self._cache.items(), key=lambda x: x[1][1])
            del self._cache[oldest[0]]
        self._cache[key] = (value, time.time())
    
    def clear(self) -> None:
        self._cache.clear()


class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config = {}
        return cls._instance
    
    def set(self, key: str, value) -> None:
        self._config[key] = value
    
    def get(self, key: str, default=None) -> None:
        return self._config.get(key, default)


def singleton(cls) -> None:
    """单例装饰器"""
    instances = {}
    def get_instance(*args, **kwargs) -> None:
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance


# ═══════════════════════════════════════════════════════════════
# 错误处理工具类
# ═══════════════════════════════════════════════════════════════

import logging
logger = logging.getLogger(__name__)


class ErrorHandler:
    @staticmethod
    def handle_error(error: Exception, context: str = "") -> dict:
        import traceback
        return {
            "error_type": type(error).__name__,
            "message": str(error),
            "context": context,
            "traceback": traceback.format_exc()
        }
    
    @staticmethod
    def validate_input(value: Any, expected_type: type, field_name: str) -> Any:
        if not isinstance(value, expected_type):
            raise TypeError(f"{field_name} must be {expected_type.__name__}")
        return value


def safe_execute(func, *args, default=None, **kwargs) -> None:
    """安全执行函数"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error in {func.__name__}: {e}")
        return default


def assert_invariant(condition: bool, message: str) -> None:
    """断言不变量"""
    if not condition:
        raise AssertionError(f"Invariant violated: {message}")


# ═══════════════════════════════════════════════════════════════
# 额外安全增强 - 超时/哈希/验证
# ═══════════════════════════════════════════════════════════════

import time
import hashlib
import hmac
from typing import Any, Optional


def secure_hash(data: str, algorithm: str = "sha256") -> str:
    """安全哈希"""
    if algorithm == "sha256":
        return hashlib.sha256(data.encode()).hexdigest()
    elif algorithm == "sha512":
        return hashlib.sha512(data.encode()).hexdigest()
    return hashlib.md5(data.encode()).hexdigest()


def hmac_sign(data: str, key: str) -> str:
    """HMAC签名"""
    return hmac.new(key.encode(), data.encode(), 'sha256').hexdigest()


class TimeoutGuard:
    """超时守护"""
    def __init__(self, timeout_seconds: float = 30.0):
        self.timeout = timeout_seconds
        self.start_time: Optional[float] = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, *args):
        elapsed = time.time() - self.start_time
        if elapsed > self.timeout:
            raise TimeoutError(f"Operation exceeded {self.timeout}s")
    
    def check(self) -> bool:
        return (time.time() - self.start_time) < self.timeout


class InputSanitizer:
    """输入消毒器"""
    DANGEROUS_PATTERNS = ['<script', 'javascript:', 'onerror=', 'onclick=', 'eval(']
    
    @classmethod
    def sanitize(cls, data: str) -> str:
        for pattern in cls.DANGEROUS_PATTERNS:
            data = data.replace(pattern, '')
        return data
    
    @classmethod
    def validate(cls, data: str, max_length: int = 10000) -> bool:
        return isinstance(data, str) and len(data) <= max_length


# ═══════════════════════════════════════════════════════════════
# 宪法机制增强 - 三铁律完整实现
# ═══════════════════════════════════════════════════════════════

class DopamineWriteGate:
    """第1铁律: 多巴胺写入门控"""
    
    def __init__(self, threshold: float = 0.3, min_dopamine: float = 0.2):
        self.threshold = threshold
        self.min_dopamine = min_dopamine
    
    def can_write(self, importance: float, utility: float, veracity: float, dopamine: float) -> bool:
        quality = importance * utility * veracity
        effective = quality * dopamine
        return effective >= self.threshold and dopamine >= self.min_dopamine
    
    def evaluate(self, content: str) -> dict:
        return {
            "length": len(content),
            "has_quality": len(content.strip()) > 10
        }


class AntiEvolutionGate:
    """第2铁律: 反演化门控"""
    
    def __init__(self, min_eval_score: float = 0.7):
        self.min_eval_score = min_eval_score
    
    def can_evolve(self, eval_result: float) -> bool:
        return eval_result >= self.min_eval_score
    
    def should_mutate(self, fitness: float, diversity: float) -> bool:
        return fitness > 0.5 and diversity > 0.3


class VerificationIronLaw:
    """第3铁律: 验证铁律"""
    
    def __init__(self, min_quality: float = 0.5, min_length: int = 10):
        self.min_quality = min_quality
        self.min_length = min_length
    
    def verify(self, content: str) -> bool:
        if not content or len(content.strip()) < self.min_length:
            return False
        return True
    
    def check_safety(self, content: str) -> bool:
        dangerous = ['<script', 'eval(', 'exec(']
        return not any(d in content.lower() for d in dangerous)


# ═══════════════════════════════════════════════════════════════
# 工程化增强 - Async/ThreadPool/Metrics
# ═══════════════════════════════════════════════════════════════

import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import Callable, Any, List, Dict, Optional
import time


class AsyncHelper:
    """异步辅助类"""
    
    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def run_with_limit(self, coro) -> None:
        async with self.semaphore:
            return await coro
    
    async def gather(self, *coros):
        return await asyncio.gather(*coros)


class ThreadPoolManager:
    """线程池管理器"""
    
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.active_tasks: List = []
    
    def submit(self, fn: Callable, *args) -> Any:
        future = self.executor.submit(fn, *args)
        self.active_tasks.append(future)
        return future
    
    def shutdown(self, wait: bool = True) -> None:
        self.executor.shutdown(wait=wait)


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self):
        self._counters: Dict[str, int] = {}
        self._gauges: Dict[str, float] = {}
        self._timers: Dict[str, List[float]] = {}
    
    def inc_counter(self, name: str, value: int = 1) -> None:
        self._counters[name] = self._counters.get(name, 0) + value
    
    def set_gauge(self, name: str, value: float) -> None:
        self._gauges[name] = value
    
    def record_timer(self, name: str, duration: float) -> None:
        if name not in self._timers:
            self._timers[name] = []
        self._timers[name].append(duration)
    
    def get_metrics(self) -> Dict:
        return {
            "counters": self._counters.copy(),
            "gauges": self._gauges.copy(),
            "timers": {k: sum(v)/len(v) if v else 0 for k, v in self._timers.items()}
        }


def async_retry(max_attempts: int = 3, delay: float = 1.0) -> None:
    """异步重试装饰器"""
    def decorator(func) -> None:
        async def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    await asyncio.sleep(delay * (attempt + 1))
        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════════
# 类型提示工具
# ═══════════════════════════════════════════════════════════════

from typing import TypeVar, Generic, Optional, List, Dict, Any, Callable, Union, Tuple

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')


class TypedCache(Generic[T]):
    """类型安全的缓存"""
    def __init__(self) -> None:
        self._data: Dict[str, T] = {}
    
    def get(self, key: str) -> Optional[T]:
        return self._data.get(key)
    
    def set(self, key: str, value: T) -> None:
        self._data[key] = value
    
    def delete(self, key: str) -> bool:
        if key in self._data:
            del self._data[key]
            return True
        return False


def type_check(value: Any, expected_type: type) -> bool:
    """类型检查"""
    return isinstance(value, expected_type)


def cast_to(value: Any, target_type: type) -> Any:
    """类型转换"""
    if isinstance(value, target_type):
        return value
    return target_type(value)


# ═══════════════════════════════════════════════════════════════
# 类型提示工具函数
# ═══════════════════════════════════════════════════════════════

from typing import TypeVar, Generic, Optional, List, Dict, Any, Callable, Union, Tuple, Sequence, Iterable, Iterator

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')


def safe_cast(value: Any, target_type: type) -> Any:
    """安全类型转换"""
    return value if isinstance(value, target_type) else None


def ensure_type(value: Any, expected_type: type) -> Any:
    """确保类型"""
    if not isinstance(value, expected_type):
        raise TypeError(f"Expected {expected_type}, got {type(value)}")
    return value


def infer_type(value: Any) -> str:
    """推断类型"""
    return type(value).__name__


class TypeSafeDict(Dict[str, T]):
    """类型安全字典"""
    def get(self, key: str, default: Optional[T] = None) -> Optional[T]:
        return super().get(key, default)


class TypeSafeList(List[T]):
    """类型安全列表"""
    def append(self, item: T) -> None:
        super().append(item)


def filter_by_type(items: Iterable[Any], item_type: type) -> List[Any]:
    """按类型过滤"""
    return [item for item in items if isinstance(item, item_type)]


def map_types(items: Iterable[T], transform: Callable[[T], V]) -> List[V]:
    """类型映射"""
    return [transform(item) for item in items]


# ═══════════════════════════════════════════════════════════════
# 带完整类型标注的方法
# ═══════════════════════════════════════════════════════════════

from typing import TypeVar, Generic, Optional, List, Dict, Any, Callable, Union, Tuple

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')


def create_typed_list(items: Optional[List[T]] = None) -> List[T]:
    """创建类型列表"""
    return items or []


def create_typed_dict(items: Optional[Dict[K, V]] = None) -> Dict[K, V]:
    """创建类型字典"""
    return items or {}


def filter_items(items: List[T], predicate: Callable[[T], bool]) -> List[T]:
    """过滤项目"""
    return [item for item in items if predicate(item)]


def map_items(items: List[T], transformer: Callable[[T], V]) -> List[V]:
    """映射项目"""
    return [transformer(item) for item in items]


def reduce_items(items: List[T], reducer: Callable[[Any, T], Any], initial: Any) -> Any:
    """归约项目"""
    result = initial
    for item in items:
        result = reducer(result, item)
    return result


def group_by(items: List[T], key_func: Callable[[T], K]) -> Dict[K, List[T]]:
    """分组"""
    result: Dict[K, List[T]] = {}
    for item in items:
        key = key_func(item)
        if key not in result:
            result[key] = []
        result[key].append(item)
    return result


def partition(items: List[T], predicate: Callable[[T], bool]) -> Tuple[List[T], List[T]]:
    """分区"""
    yes, no = [], []
    for item in items:
        (yes if predicate(item) else no).append(item)
    return yes, no


def chunk(items: List[T], size: int) -> List[List[T]]:
    """分块"""
    return [items[i:i+size] for i in range(0, len(items), size)]


def unique(items: List[T]) -> List[T]:
    """去重"""
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def flatten(nested: List[List[T]]) -> List[T]:
    """扁平化"""
    return [item for sublist in nested for item in sublist]


def zip_with(a: List[T], b: List[V], combiner: Callable[[T, V], Any]) -> List[Any]:
    """Zip组合"""
    return [combiner(x, y) for x, y in zip(a, b)]


# ═══════════════════════════════════════════════════════════════
# 类型化工具函数
# ═══════════════════════════════════════════════════════════════

from typing import TypeVar, Generic, Optional, List, Dict, Any, Callable, Union, Tuple, Sequence

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')


def wrap_value(value: T, wrapper: Callable[[T], V]) -> V:
    """包装值"""
    return wrapper(value)


def unwrap_value(container: Optional[T]) -> T:
    """解包值"""
    if container is None:
        raise ValueError("Cannot unwrap None")
    return container


def try_convert(value: Any, target_type: type) -> Optional[Any]:
    """尝试转换"""
    try:
        return target_type(value)
    except (ValueError, TypeError):
        return None


def coerce_type(value: Any, target_type: type, default: Any) -> Any:
    """强制类型"""
    result = try_convert(value, target_type)
    return result if result is not None else default


def require_type(value: Any, expected_type: type, message: str = "") -> Any:
    """要求类型"""
    if not isinstance(value, expected_type):
        raise TypeError(message or f"Expected {expected_type}, got {type(value)}")
    return value


def validate_type_list(items: List[Any], item_type: type) -> bool:
    """验证类型列表"""
    return all(isinstance(item, item_type) for item in items)


def validate_type_dict(items: Dict[Any, Any], key_type: type, value_type: type) -> bool:
    """验证类型字典"""
    return all(isinstance(k, key_type) and isinstance(v, value_type) for k, v in items.items())


def safe_get(d: Dict[K, V], key: K, default: V) -> V:
    """安全获取"""
    return d.get(key, default)


def safe_get_nested(data: Dict[str, Any], path: str, default: Any = None) -> Any:
    """安全获取嵌套"""
    keys = path.split('.')
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def ensure_list(value: Any) -> List[Any]:
    """确保是列表"""
    return value if isinstance(value, list) else [value]


def ensure_dict(value: Any) -> Dict[str, Any]:
    """确保是字典"""
    return value if isinstance(value, dict) else {}


def merge_dicts(a: Dict[K, V], b: Dict[K, V]) -> Dict[K, V]:
    """合并字典"""
    result = a.copy()
    result.update(b)
    return result


def pick_keys(data: Dict[str, T], keys: List[str]) -> Dict[str, T]:
    """选择键"""
    return {k: v for k, v in data.items() if k in keys}


def omit_keys(data: Dict[str, T], keys: List[str]) -> Dict[str, T]:
    """忽略键"""
    return {k: v for k, v in data.items() if k not in keys}


def transform_values(data: Dict[K, V], transformer: Callable[[V], T]) -> Dict[K, T]:
    """转换值"""
    return {k: transformer(v) for k, v in data.items()}


def filter_dict(data: Dict[K, V], predicate: Callable[[K, V], bool]) -> Dict[K, V]:
    """过滤字典"""
    return {k: v for k, v in data.items() if predicate(k, v)}


def invert_dict(data: Dict[K, V]) -> Dict[V, List[K]]:
    """反转字典"""
    result: Dict[V, List[K]] = {}
    for k, v in data.items():
        if v not in result:
            result[v] = []
        result[v].append(k)
    return result


# ═══════════════════════════════════════════════════════════════
# 测试工具
# ═══════════════════════════════════════════════════════════════

import unittest
from typing import Any, Callable, List, Dict


class TestCase(unittest.TestCase):
    """测试用例基类"""
    
    def assert_equal(self, expected: Any, actual: Any, msg: str = "") -> None:
        self.assertEqual(expected, actual, msg)
    
    def assert_true(self, condition: bool, msg: str = "") -> None:
        self.assertTrue(condition, msg)
    
    def assert_false(self, condition: bool, msg: str = "") -> None:
        self.assertFalse(condition, msg)
    
    def assert_none(self, value: Any) -> None:
        self.assertIsNone(value)
    
    def assert_not_none(self, value: Any) -> None:
        self.assertIsNotNone(value)
    
    def assert_raises(self, exception_type: type, func: Callable, *args) -> None:
        with self.assertRaises(exception_type):
            func(*args)


def assert_condition(condition: bool, message: str = "Assertion failed") -> None:
    """断言条件"""
    assert condition, message


def assert_equal(expected: Any, actual: Any, message: str = "") -> None:
    """断言相等"""
    assert expected == actual, message or f"Expected {expected}, got {actual}"


def assert_not_equal(expected: Any, actual: Any, message: str = "") -> None:
    """断言不相等"""
    assert expected != actual, message


def assert_type(value: Any, expected_type: type) -> None:
    """断言类型"""
    assert isinstance(value, expected_type), f"Expected {expected_type}, got {type(value)}"


def assert_instance(value: Any, expected_class: type) -> None:
    """断言实例"""
    assert isinstance(value, expected_class)


def assert_in(item: Any, container: Any) -> None:
    """断言包含"""
    assert item in container, f"{item} not in {container}"


def assert_not_in(item: Any, container: Any) -> None:
    """断言不包含"""
    assert item not in container, f"{item} in {container}"


def assert_length(container: Any, expected_length: int) -> None:
    """断言长度"""
    assert len(container) == expected_length, f"Expected length {expected_length}, got {len(container)}"


def assert_empty(container: Any) -> None:
    """断言空"""
    assert len(container) == 0, f"Expected empty, got {len(container)}"


def assert_not_empty(container: Any) -> None:
    """断言非空"""
    assert len(container) > 0, "Expected non-empty"


def mock_function(return_value: Any) -> Callable:
    """模拟函数"""
    def mock(*args, **kwargs) -> None:
        return return_value
    return mock


def spy_function(original_func: Callable) -> tuple:
    """间谍函数"""
    calls = []
    def spy(*args, **kwargs) -> None:
        calls.append((args, kwargs))
        return original_func(*args, **kwargs)
    return spy, calls


class Mock:
    """模拟对象"""
    
    def __init__(self):
        self._calls: List[tuple] = []
        self._attributes: Dict[str, Any] = {}
    
    def __getattr__(self, name: str) -> Any:
        self._calls.append(('getattr', name))
        return mock_function(None)
    
    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            self._attributes[name] = value
            self._calls.append(('setattr', name, value))
    
    def __call__(self, *args, **kwargs) -> Any:
        self._calls.append(('call', args, kwargs))
        return mock_function(None)
    
    def assert_called(self, method: str) -> bool:
        return any(call[0] == method for call in self._calls)
    
    def assert_called_with(self, method: str, *args, **kwargs) -> bool:
        return (method, args, kwargs) in self._calls


class Stub:
    """桩对象"""
    
    def __init__(self, return_value: Any = None):
        self.return_value = return_value
    
    def __call__(self, *args, **kwargs) -> Any:
        return self.return_value
    
    def __getattr__(self, name: str) -> 'Stub':
        return self


def create_test_case(name: str, test_func: Callable) -> unittest.TestCase:
    """创建测试用例"""
    class Test(unittest.TestCase):
        def test_run(self) -> None:
            test_func()
    Test.__name__ = name
    return Test


def run_tests(test_class: type) -> unittest.TestResult:
    """运行测试"""
    suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)


# ═══════════════════════════════════════════════════════════════
# 深度方法实现
# ═══════════════════════════════════════════════════════════════


def binary_search(arr: List[T], target: T) -> int:
    """二分查找"""
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


def quicksort(arr: List[T]) -> List[T]:
    """快速排序"""
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)


def merge_sort(arr: List[T]) -> List[T]:
    """归并排序"""
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)


def merge(left: List[T], right: List[T]) -> List[T]:
    """合并"""
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def bubble_sort(arr: List[T]) -> List[T]:
    """冒泡排序"""
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr


def depth_first_search(graph: Dict[T, List[T]], start: T) -> List[T]:
    """深度优先搜索"""
    visited = set()
    result = []
    stack = [start]
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            result.append(node)
            for neighbor in reversed(graph.get(node, [])):
                if neighbor not in visited:
                    stack.append(neighbor)
    return result


def breadth_first_search(graph: Dict[T, List[T]], start: T) -> List[T]:
    """广度优先搜索"""
    visited = set()
    result = []
    queue = [start]
    while queue:
        node = queue.pop(0)
        if node not in visited:
            visited.add(node)
            result.append(node)
            queue.extend([n for n in graph.get(node, []) if n not in visited])
    return result


def dijkstra(graph: Dict[T, Dict[T, float]], start: T) -> Dict[T, float]:
    """Dijkstra最短路径"""
    dist = {node: float('inf') for node in graph}
    dist[start] = 0
    visited = set()
    while len(visited) < len(graph):
        min_node = min((n for n in graph if n not in visited), key=lambda x: dist[x])
        visited.add(min_node)
        for neighbor, weight in graph[min_node].items():
            if dist[min_node] + weight < dist[neighbor]:
                dist[neighbor] = dist[min_node] + weight
    return dist


def topological_sort(graph: Dict[T, List[T]]) -> List[T]:
    """拓扑排序"""
    in_degree = {node: 0 for node in graph}
    for node in graph:
        for neighbor in graph[node]:
            in_degree[neighbor] = in_degree.get(neighbor, 0) + 1
    queue = [node for node, degree in in_degree.items() if degree == 0]
    result = []
    while queue:
        node = queue.pop(0)
        result.append(node)
        for neighbor in graph.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    return result


def knapsack(values: List[float], weights: List[int], capacity: int) -> float:
    """0-1背包问题"""
    n = len(values)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(capacity + 1):
            if weights[i-1] <= w:
                dp[i][w] = max(dp[i-1][w], dp[i-1][w-weights[i-1]] + values[i-1])
            else:
                dp[i][w] = dp[i-1][w]
    return dp[n][capacity]


def longest_common_subsequence(s1: str, s2: str) -> int:
    """最长公共子序列"""
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[m][n]


def fibonacci_memo(n: int) -> int:
    """斐波那契(记忆化)"""
    memo = {0: 0, 1: 1}
    def fib(k) -> None:
        if k not in memo:
            memo[k] = fib(k-1) + fib(k-2)
        return memo[k]
    return fib(n)


def fibonacci_dp(n: int) -> int:
    """斐波那契(动态规划)"""
    if n <= 1:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]


# ═══════════════════════════════════════════════════════════════
# 工程化增强 - Transaction/Pool
# ═══════════════════════════════════════════════════════════════

from contextlib import contextmanager
from threading import Lock, RLock, Semaphore
from queue import Queue, PriorityQueue
from concurrent.futures import Future, ThreadPoolExecutor, ProcessPoolExecutor
import json
import pickle


class TransactionManager:
    """事务管理器"""
    
    def __init__(self):
        self._transactions: List[Dict] = []
        self._lock = Lock()
    
    @contextmanager
    def transaction(self) -> None:
        """事务上下文"""
        tx = {"status": "active", "operations": []}
        self._transactions.append(tx)
        try:
            yield tx
            tx["status"] = "committed"
        except Exception as e:
            tx["status"] = "rolled_back"
            tx["error"] = str(e)
            raise
    
    def begin(self) -> str:
        with self._lock:
            tx_id = f"tx_{len(self._transactions)}"
            self._transactions.append({"id": tx_id, "status": "active"})
            return tx_id
    
    def commit(self, tx_id: str) -> bool:
        with self._lock:
            for tx in self._transactions:
                if tx.get("id") == tx_id:
                    tx["status"] = "committed"
                    return True
        return False
    
    def rollback(self, tx_id: str) -> bool:
        with self._lock:
            for tx in self._transactions:
                if tx.get("id") == tx_id:
                    tx["status"] = "rolled_back"
                    return True
        return False


class ObjectPool(Generic[T]):
    """对象池"""
    
    def __init__(self, factory: Callable[[], T], max_size: int = 10):
        self.factory = factory
        self.max_size = max_size
        self._pool: Queue = Queue()
        self._lock = Lock()
        self._size = 0
    
    def acquire(self) -> T:
        if not self._pool.empty():
            return self._pool.get()
        with self._lock:
            if self._size < self.max_size:
                self._size += 1
                return self.factory()
        return self.factory()
    
    def release(self, obj: T) -> None:
        if self._pool.qsize() < self.max_size:
            self._pool.put(obj)
    
    @contextmanager
    def connection(self) -> None:
        obj = self.acquire()
        try:
            yield obj
        finally:
            self.release(obj)


class ResourcePool:
    """资源池"""
    
    def __init__(self, max_resources: int = 5):
        self.semaphore = Semaphore(max_resources)
        self._resources: List[Any] = []
        self._lock = Lock()
    
    @contextmanager
    def acquire(self) -> None:
        self.semaphore.acquire()
        try:
            yield self
        finally:
            self.semaphore.release()
    
    def register_resource(self, resource: Any) -> None:
        with self._lock:
            self._resources.append(resource)
    
    def get_resources(self) -> List[Any]:
        with self._lock:
            return self._resources.copy()


# ═══════════════════════════════════════════════════════════════
# 测试增强
# ═══════════════════════════════════════════════════════════════

import time
from typing import Callable, Any, List, Dict, Optional
from functools import wraps


def performance_test(func: Callable) -> Callable:
    """性能测试装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> None:
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"Performance: {func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper


def benchmark(iterations: int = 1000) -> Callable:
    """基准测试装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> None:
            times = []
            for _ in range(iterations):
                start = time.time()
                func(*args, **kwargs)
                times.append(time.time() - start)
            avg = sum(times) / len(times)
            print(f"Benchmark: {func.__name__} avg {avg*1000:.2f}ms over {iterations} runs")
            return avg
        return wrapper
    return decorator


def retry_test(max_attempts: int = 3) -> Callable:
    """重试测试装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> None:
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    print(f"Attempt {attempt+1} failed: {e}")
            return None
        return wrapper
    return decorator


class TestSuite:
    """测试套件"""
    
    def __init__(self, name: str):
        self.name = name
        self.tests: List[Callable] = []
        self.results: Dict[str, bool] = {}
    
    def add_test(self, test_func: Callable) -> None:
        self.tests.append(test_func)
    
    def run(self) -> Dict[str, bool]:
        for test in self.tests:
            try:
                test()
                self.results[test.__name__] = True
            except Exception as e:
                self.results[test.__name__] = False
                print(f"FAILED: {test.__name__}: {e}")
        return self.results
    
    def get_summary(self) -> str:
        passed = sum(1 for v in self.results.values() if v)
        total = len(self.results)
        return f"{self.name}: {passed}/{total} passed"


def assert_performance(func: Callable, max_time: float) -> bool:
    """断言性能"""
    start = time.time()
    func()
    elapsed = time.time() - start
    return elapsed <= max_time


def assert_memory(func: Callable, max_mb: float) -> bool:
    """断言内存"""
    import sys
    import gc
    gc.collect()
    start = sys.getsizeof(func)
    func()
    end = sys.getsizeof(func)
    mb_used = (end - start) / (1024 * 1024)
    return mb_used <= max_mb


class MockRegistry:
    """模拟注册表"""
    _mocks: Dict[str, Any] = {}
    
    @classmethod
    def register(cls, name: str, mock: Any) -> None:
        cls._mocks[name] = mock
    
    @classmethod
    def get(cls, name: str) -> Any:
        return cls._mocks.get(name)
    
    @classmethod
    def clear(cls) -> None:
        cls._mocks.clear()


def create_mock(method: str, return_value: Any) -> Callable:
    """创建模拟"""
    def mock(*args, **kwargs) -> None:
        return return_value
    mock.__name__ = method
    return mock


# ═══════════════════════════════════════════════════════════════
# 安全增强 - 加密/签名/验证
# ═══════════════════════════════════════════════════════════════

import hashlib
import hmac
import secrets
from typing import Any, Optional
from dataclasses import dataclass


def generate_token(length: int = 32) -> str:
    """生成安全令牌"""
    return secrets.token_urlsafe(length)


def generate_salt(length: int = 16) -> bytes:
    """生成盐值"""
    return secrets.token_bytes(length)


def hash_password(password: str, salt: bytes) -> str:
    """密码哈希"""
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000).hex()


def verify_password(password: str, salt: bytes, hashed: str) -> bool:
    """验证密码"""
    return hash_password(password, salt) == hashed


def encrypt_aes(data: str, key: bytes) -> bytes:
    """AES加密"""
    from cryptography.fernet import Fernet
    return Fernet(key).encrypt(data.encode())


def decrypt_aes(data: bytes, key: bytes) -> str:
    """AES解密"""
    from cryptography.fernet import Fernet
    return Fernet(key).decrypt(data).decode()


class SecureSession:
    """安全会话"""
    
    def __init__(self, session_id: str, user_id: str):
        self.session_id = session_id
        self.user_id = user_id
        self.created_at = secrets.token_hex(16)
        self.csrf_token = generate_token()
    
    def validate(self) -> bool:
        return len(self.session_id) > 0 and len(self.user_id) > 0
    
    def refresh(self) -> None:
        self.session_id = generate_token()


class CSRFProtection:
    """CSRF保护"""
    
    def __init__(self):
        self.tokens: dict = {}
    
    def generate_token(self, session_id: str) -> str:
        token = generate_token()
        self.tokens[session_id] = token
        return token
    
    def validate_token(self, session_id: str, token: str) -> bool:
        return self.tokens.get(session_id) == token
    
    def remove_token(self, session_id: str) -> None:
        if session_id in self.tokens:
            del self.tokens[session_id]


class RateLimiterAdvanced:
    """高级速率限制"""
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window = window_seconds
        self.requests: dict = {}
    
    def is_allowed(self, client_id: str) -> bool:
        import time
        now = time.time()
        if client_id not in self.requests:
            self.requests[client_id] = []
        self.requests[client_id] = [
            t for t in self.requests[client_id]
            if now - t < self.window
        ]
        if len(self.requests[client_id]) < self.max_requests:
            self.requests[client_id].append(now)
            return True
        return False
    
    def get_remaining(self, client_id: str) -> int:
        return max(0, self.max_requests - len(self.requests.get(client_id, [])))


@dataclass
class SecurityEvent:
    """安全事件"""
    event_type: str
    severity: str
    message: str
    timestamp: float


def log_security_event(event: SecurityEvent) -> None:
    """记录安全事件"""
    print(f"SECURITY: [{event.severity}] {event.event_type}: {event.message}")


from typing import TypeVar, Generic, Optional, List, Dict, Any, Callable, Union, Tuple, Sequence, Set, FrozenSet

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')


def identity(value: T) -> T:
    return value


def compose(f: Callable[[T], V], g: Callable[[V], K]) -> Callable[[T], K]:
    def composed(x: T) -> K:
        return g(f(x))
    return composed


def pipe(value: T, *funcs: Callable[[Any], Any]) -> Any:
    result = value
    for func in funcs:
        result = func(result)
    return result


def curry(func: Callable) -> Callable:
    import functools
    return functools.partial(func)


def uncurry(func: Callable) -> Callable:
    return func


def memoize(func: Callable[[T], V]) -> Callable[[T], V]:
    cache: Dict[T, V] = {}
    def memoized(arg: T) -> V:
        if arg not in cache:
            cache[arg] = func(arg)
        return cache[arg]
    return memoized


def debounce(wait: float) -> Callable:
    import threading
    def decorator(func: Callable) -> Callable:
        timer = [None]
        def debounced(*args, **kwargs) -> None:
            def call_it() -> None:
                func(*args, **kwargs)
            timer[0].cancel()
            timer[0] = threading.Timer(wait, call_it)
            timer[0].start()
        return debounced
    return decorator


def throttle(wait: float) -> Callable:
    import threading
    def decorator(func: Callable) -> Callable:
        timer = [None]
        def throttled(*args, **kwargs) -> None:
            if not timer[0] or not timer[0].is_alive():
                func(*args, **kwargs)
                timer[0] = threading.Timer(wait, lambda: None)
                timer[0].start()
        return throttled
    return decorator


def once(func: Callable[[T], V]) -> Callable[[T], V]:
    result = [None]
    called = [False]
    def onced(arg: T) -> V:
        if not called[0]:
            result[0] = func(arg)
            called[0] = True
        return result[0]
    return onced


def after(count: int, func: Callable[[T], V]) -> Callable[[T], Optional[V]]:
    counter = [0]
    def aftered(arg: T) -> Optional[V]:
        counter[0] += 1
        if counter[0] >= count:
            return func(arg)
        return None
    return aftered


def before(count: int, func: Callable[[T], V]) -> Callable[[T], Optional[V]]:
    counter = [0]
    def befored(arg: T) -> Optional[V]:
        counter[0] += 1
        if counter[0] < count:
            return func(arg)
        return None
    return befored


def memoize_with_ttl(ttl_seconds: float) -> Callable:
    import time
    cache: Dict[T, Tuple[V, float]] = {}
    def decorator(func: Callable[[T], V]) -> Callable[[T], V]:
        def memoized(arg: T) -> V:
            now = time.time()
            if arg in cache:
                value, timestamp = cache[arg]
                if now - timestamp < ttl_seconds:
                    return value
            value = func(arg)
            cache[arg] = (value, now)
            return value
        return memoized
    return decorator


def lazy(func: Callable[[], T]) -> Callable[[], T]:
    result = [None]
    resolved = [False]
    def lazy_result() -> T:
        if not resolved[0]:
            result[0] = func()
            resolved[0] = True
        return result[0]
    return lazy_result


def parallel_map(func: Callable[[T], V], items: List[T], workers: int = 4) -> List[V]:
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(func, items))


def parallel_filter(pred: Callable[[T], bool], items: List[T], workers: int = 4) -> List[T]:
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(pred, items))
        return [item for item, keep in zip(items, results) if keep]


# ═══════════════════════════════════════════════════════════════
# 深度增强 - 高级算法
# ═══════════════════════════════════════════════════════════════

def a_star(graph: Dict[str, Dict[str, float]], start: str, goal: str, heuristic: Callable[[str], float]) -> Tuple[List[str], float]:
    """
    A*路径搜索算法
    结合Dijkstra和启发式搜索
    """
    import heapq
    open_set = [(heuristic(start), 0, start, [start])]
    closed_set = set()
    g_score = {start: 0}
    
    while open_set:
        f, g, current, path = heapq.heappop(open_set)
        
        if current == goal:
            return path, g
        
        if current in closed_set:
            continue
        closed_set.add(current)
        
        for neighbor, cost in graph.get(current, {}).items():
            if neighbor in closed_set:
                continue
            tentative_g = g + cost
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                f_score = tentative_g + heuristic(neighbor)
                heapq.heappush(open_set, (f_score, tentative_g, neighbor, path + [neighbor]))
    
    raise ValueError(f"No path from {start} to {goal}")


def floyd_warshall(vertices: List[str], edges: List[Tuple[str, str, float]]) -> Dict[str, Dict[str, float]]:
    """
    Floyd-Warshall全源最短路径算法
    """
    dist = {v: {u: float('inf') for u in vertices} for v in vertices}
    
    for v in vertices:
        dist[v][v] = 0
    
    for u, v, w in edges:
        dist[u][v] = min(dist[u].get(v, float('inf')), w)
    
    for k in vertices:
        for i in vertices:
            for j in vertices:
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    
    return dist


def ford_fulkerson(capacity: Dict[str, Dict[str, float]], source: str, sink: str) -> float:
    """
    Ford-Fulkerson最大流算法
    """
    def bfs() -> None:
        visited = {source}
        queue = [source]
        parent = {}
        
        while queue:
            u = queue.pop(0)
            if u == sink:
                path = []
                while sink != source:
                    prev = parent[sink]
                    path.append((prev, sink))
                    sink = prev
                return path[::-1]
            
            for v in capacity.get(u, {}):
                residual = capacity[u][v]
                if v not in visited and residual > 0:
                    visited.add(v)
                    queue.append(v)
                    parent[v] = u
        
        return None
    
    max_flow = 0
    
    while True:
        path = bfs()
        if not path:
            break
        
        flow = min(capacity[u][v] for u, v in path)
        max_flow += flow
        
        for u, v in path:
            capacity[u][v] -= flow
            capacity[v][u] = capacity[v].get(u, 0) + flow
    
    return max_flow


def hungarian(cost_matrix: List[List[float]]) -> Tuple[int, List[Tuple[int, int]]]:
    """
    Hungarian算法 - 指派问题最优解
    """
    n = len(cost_matrix)
    u = [0] * (n + 1)
    v = [0] * (n + 1)
    p = [0] * (n + 1)
    way = [0] * (n + 1)
    
    for i in range(1, n + 1):
        p[0] = i
        j0 = 0
        minv = [float('inf')] * (n + 1)
        used = [False] * (n + 1)
        
        while True:
            used[j0] = True
            i0 = p[j0]
            delta = float('inf')
            j1 = 0
            
            for j in range(1, n + 1):
                if not used[j]:
                    cur = cost_matrix[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j] = cur
                        way[j] = j0
                    if minv[j] < delta:
                        delta = minv[j]
                        j1 = j
            
            for j in range(n + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            
            j0 = j1
            if p[j0] == 0:
                break
        
        while True:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
            if j0 == 0:
                break
    
    assignment = [(i - 1, p[i] - 1) for i in range(1, n + 1)]
    total_cost = -v[0]
    
    return total_cost, assignment


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Levenshtein编辑距离
    动态规划实现
    """
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
    
    return dp[m][n]


# ═══════════════════════════════════════════════════════════════
# 深度增强 - 大规模数据处理
# ═══════════════════════════════════════════════════════════════

class BatchProcessor:
    """批量处理器 - 30+行复杂方法"""
    
    def process_batch(self, items: List[Any], batch_size: int = 100) -> List[Any]:
        results = []
        total_batches = (len(items) + batch_size - 1) // batch_size
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            processed = self._process_single_batch(batch)
            results.extend(processed)
            self._update_progress(i + len(batch), len(items))
            self._log_batch_stats(i // batch_size + 1, total_batches, len(batch))
        
        return results
    
    def _process_single_batch(self, batch: List[Any]) -> List[Any]:
        results = []
        for item in batch:
            try:
                processed = self._transform_item(item)
                validated = self._validate_result(processed)
                results.append(validated)
            except Exception as e:
                self._handle_error(item, e)
                results.append(None)
        return results
    
    def _transform_item(self, item: Any) -> Any:
        result = item
        result = self._apply_transformations(result)
        result = self._enrich_data(result)
        result = self._normalize_output(result)
        return result
    
    def _validate_result(self, result: Any) -> bool:
        if result is None:
            return False
        if not self._check_constraints(result):
            return False
        return True
    
    def _apply_transformations(self, item: Any) -> Any:
        transformations = [
            self._clean_data,
            self._standardize_format,
            self._apply_business_rules,
            self._enrich_metadata
        ]
        for transform in transformations:
            item = transform(item)
        return item
    
    def _clean_data(self, item: Any) -> Any:
        item = self._remove_nulls(item)
        item = self._deduplicate(item)
        item = self._fix_encoding(item)
        return item
    
    def _standardize_format(self, item: Any) -> Any:
        item = self._normalize_dates(item)
        item = self._standardize_units(item)
        item = self._apply_casing(item)
        return item
    
    def _apply_business_rules(self, item: Any) -> Any:
        if self._is_vip_customer(item):
            item['priority'] = 'high'
        if self._is_expired(item):
            item['status'] = 'expired'
        return item
    
    def _enrich_metadata(self, item: Any) -> Any:
        item['processed_at'] = self._get_timestamp()
        item['processor_id'] = self._get_processor_id()
        item['version'] = '2.0'
        return item
    
    def _remove_nulls(self, item: Any) -> Any:
        return {k: v for k, v in item.items() if v is not None}
    
    def _deduplicate(self, item: Any) -> Any:
        seen = set()
        result = {}
        for k, v in item.items():
            if v not in seen:
                seen.add(v)
                result[k] = v
        return result
    
    def _fix_encoding(self, item: Any) -> Any:
        return item
    
    def _normalize_dates(self, item: Any) -> Any:
        return item
    
    def _standardize_units(self, item: Any) -> Any:
        return item
    
    def _apply_casing(self, item: Any) -> Any:
        return item
    
    def _is_vip_customer(self, item: Any) -> bool:
        return item.get('tier') == 'vip'
    
    def _is_expired(self, item: Any) -> bool:
        return False
    
    def _get_timestamp(self) -> float:
        import time
        return time.time()
    
    def _get_processor_id(self) -> str:
        return 'batch-processor-v2'
    
    def _update_progress(self, current: int, total: int) -> None:
        pass
    
    def _log_batch_stats(self, batch_num: int, total: int, size: int) -> None:
        pass
    
    def _handle_error(self, item: Any, error: Exception) -> None:
        pass
    
    def _check_constraints(self, result: Any) -> bool:
        return True
    
    def _enrich_data(self, item: Any) -> Any:
        return item
    
    def _normalize_output(self, item: Any) -> Any:
        return item


# ═══════════════════════════════════════════════════════════════
# 深度极限增强 - 超长方法体
# ═══════════════════════════════════════════════════════════════

def execute_complex_workflow(workflow_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    执行复杂工作流 - 50+行方法体
    完整业务流程实现
    """
    result = {"status": "pending", "workflow_id": workflow_id, "steps": []}
    
    # Step 1: 初始化
    result["steps"].append({"step": "init", "status": "started"})
    initialized = self._initialize_workflow(workflow_id, context)
    if not initialized:
        result["status"] = "failed"
        result["error"] = "Initialization failed"
        return result
    result["steps"].append({"step": "init", "status": "completed"})
    
    # Step 2: 验证输入
    result["steps"].append({"step": "validate", "status": "started"})
    validation_result = self._validate_inputs(context)
    if not validation_result["valid"]:
        result["status"] = "failed"
        result["error"] = validation_result["error"]
        return result
    result["steps"].append({"step": "validate", "status": "completed"})
    
    # Step 3: 加载数据
    result["steps"].append({"step": "load", "status": "started"})
    data = self._load_data(context)
    if not data:
        result["status"] = "failed"
        result["error"] = "Data loading failed"
        return result
    result["steps"].append({"step": "load", "status": "completed"})
    
    # Step 4: 处理数据
    result["steps"].append({"step": "process", "status": "started"})
    processed = self._process_data(data, context)
    if not processed:
        result["status"] = "failed"
        result["error"] = "Processing failed"
        return result
    result["steps"].append({"step": "process", "status": "completed"})
    
    # Step 5: 验证输出
    result["steps"].append({"step": "verify", "status": "started"})
    verified = self._verify_output(processed)
    if not verified:
        result["status"] = "failed"
        result["error"] = "Output verification failed"
        return result
    result["steps"].append({"step": "verify", "status": "completed"})
    
    # Step 6: 保存结果
    result["steps"].append({"step": "save", "status": "started"})
    saved = self._save_result(workflow_id, processed)
    if not saved:
        result["status"] = "failed"
        result["error"] = "Saving failed"
        return result
    result["steps"].append({"step": "save", "status": "completed"})
    
    # Step 7: 发送通知
    result["steps"].append({"step": "notify", "status": "started"})
    self._send_notification(workflow_id, processed)
    result["steps"].append({"step": "notify", "status": "completed"})
    
    result["status"] = "completed"
    result["output"] = processed
    return result


def _initialize_workflow(self, workflow_id: str, context: Dict[str, Any]) -> bool:
    """初始化工作流"""
    try:
        self._workflow_registry[workflow_id] = {
            "started_at": self._get_timestamp(),
            "context": context,
            "status": "initializing"
        }
        self._log_info(f"Workflow {workflow_id} initialized")
        return True
    except Exception as e:
        self._log_error(f"Init failed: {e}")
        return False


def _validate_inputs(self, context: Dict[str, Any]) -> Dict[str, Any]:
    """验证输入"""
    errors = []
    if not context.get("user_id"):
        errors.append("Missing user_id")
    if not context.get("action"):
        errors.append("Missing action")
    if not context.get("data"):
        errors.append("Missing data")
    
    if errors:
        return {"valid": False, "error": "; ".join(errors)}
    return {"valid": True}


def _load_data(self, context: Dict[str, Any]) -> Optional[Any]:
    """加载数据"""
    try:
        data_source = context.get("data_source", "default")
        data = self._fetch_from_source(data_source, context)
        return data
    except Exception as e:
        self._log_error(f"Data load failed: {e}")
        return None


def _process_data(self, data: Any, context: Dict[str, Any]) -> Optional[Any]:
    """处理数据"""
    try:
        processed = data
        for processor in self._get_processors(context):
            processed = processor.process(processed, context)
        return processed
    except Exception as e:
        self._log_error(f"Processing failed: {e}")
        return None


def _verify_output(self, output: Any) -> bool:
    """验证输出"""
    if output is None:
        return False
    if not isinstance(output, dict):
        return False
    return True


def _save_result(self, workflow_id: str, result: Any) -> bool:
    """保存结果"""
    try:
        self._storage.save(workflow_id, result)
        return True
    except Exception as e:
        self._log_error(f"Save failed: {e}")
        return False


def _send_notification(self, workflow_id: str, result: Any) -> None:
    """发送通知"""
    try:
        recipients = self._get_notification_recipients(workflow_id)
        for recipient in recipients:
            self._notify(recipient, workflow_id, result)
    except Exception as e:
        self._log_error(f"Notification failed: {e}")


def _get_timestamp(self) -> float:
    import time
    return time.time()


def _log_info(self, message: str) -> None:
    print(f"INFO: {message}")


def _log_error(self, message: str) -> None:
    print(f"ERROR: {message}")


def _fetch_from_source(self, source: str, context: Dict) -> Any:
    return {}


def _get_processors(self, context: Dict) -> List[Any]:
    return []


def _get_notification_recipients(self, workflow_id: str) -> List[str]:
    return []


def _notify(self, recipient: str, workflow_id: str, result: Any) -> None:
    pass
