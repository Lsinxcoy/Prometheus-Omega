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


class RRF:
    """Reciprocal Rank Fusion - 来自X系统#14"""
    
    def __init__(self, k: float = 60.0):
        self.k = k
    
    def fuse(self, rank_lists: List[List[RetrievalResult]]) -> List[RetrievalResult]:
        """融合多个排序列表"""
        scores: Dict[str, float] = {}
        
        for rank_list in rank_lists:
            for rank, result in enumerate(rank_list):
                scores[result.entry_id] = scores.get(result.entry_id, 0) + 1.0 / (self.k + rank + 1)
        
        # 排序
        fused = sorted(scores.items(), key=lambda x: -x[1])
        return [ RetrievalResult(entry_id=e[0], content="", score=e[1], method=RetrievalMethod.HYBRID) 
                 for e in fused ]


class MMR:
    """Maximal Marginal Relevance - 来自X系统#15"""
    
    def __init__(self, lambda_: float = 0.5):
        self.lambda_ = lambda_
    
    def diversify(self, results: List[RetrievalResult], 
                  similarity_fn: Callable[[str, str], float]) -> List[RetrievalResult]:
        """多样性融合"""
        if not results:
            return []
        
        selected = [results[0]]
        remaining = results[1:]
        
        while remaining:
            best_score = -float('inf')
            best_idx = 0
            
            for i, result in enumerate(remaining):
                # 与已选的多样性
                max_sim = max(similarity_fn(result.content, s.content) for s in selected)
                mmr_score = self.lambda_ * result.score - (1 - self.lambda_) * max_sim
                
                if mmr_score > best_score:
                    best_score = mmr_score
                    best_idx = i
            
            selected.append(remaining.pop(best_idx))
        
        return selected


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
    
    def add(self, entry_id: str, embedding: List[float]):
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
    
    def add_edge(self, from_node: str, to_node: str):
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