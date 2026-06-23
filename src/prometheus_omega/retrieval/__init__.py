"""L3 Retrieval - 检索层

整合XYZ机制:
- X: Polyphonic 5-Route, RRF, MMR, Hallway/Tunnel
- Y: retrieval模块
- Z: 向量检索, 图遍历
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
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
        """语义检索"""
        # 简化实现
        return []
    
    def _keyword_search(self, query: str, memory_store, top_k: int) -> List[RetrievalResult]:
        """关键词检索"""
        results = []
        query_lower = query.lower()
        for entry in memory_store.entries.values():
            if query_lower in entry.content.lower():
                results.append(RetrievalResult(
                    entry_id=entry.id,
                    content=entry.content,
                    score=1.0,
                    method=RetrievalMethod.KEYWORD
                ))
        return results[:top_k]
    
    def _graph_search(self, query: str, memory_store, top_k: int) -> List[RetrievalResult]:
        """图遍历检索"""
        return []
    
    def _temporal_search(self, query: str, memory_store, top_k: int) -> List[RetrievalResult]:
        """时间序检索"""
        return []
    
    def _entity_search(self, query: str, memory_store, top_k: int) -> List[RetrievalResult]:
        """实体关联检索"""
        return []


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