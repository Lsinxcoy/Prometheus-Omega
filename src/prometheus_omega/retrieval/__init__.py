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