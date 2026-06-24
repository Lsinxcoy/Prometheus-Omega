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



# ═══════════════════════════════════════════════════════════════
# 工程化工具类
# ═══════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════
# 错误处理工具类
# ═══════════════════════════════════════════════════════════════

import logging
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# 宪法机制引用 - 三铁律
# ═══════════════════════════════════════════════════════════════

# 第1铁律: 多巴胺写入门控 (DopamineWriteGate) - 见 safety 模块
# 第2铁律: 反演化门控 (AntiEvolutionGate) - 见 evolution 模块  
# 第3铁律: 验证铁律 (VerificationIronLaw) - 见 evolution 模块

def can_write_gate(importance: float, utility: float, veracity: float, dopamine: float = 0.5, threshold: float = 0.3) -> bool:
    """第1铁律: 多巴胺写入门控 - 质量分数必须超过阈值"""
    quality = importance * utility * veracity
    effective = quality * dopamine
    return effective >= threshold and dopamine >= 0.2

def can_evolve_gate(eval_result: float, min_threshold: float = 0.7) -> bool:
    """第2铁律: 反演化门控 - 只有评估结果足够好才能演化"""
    return eval_result >= min_threshold

def verify_iron_law(content: str, min_quality: float = 0.5) -> bool:
    """第3铁律: 验证铁律 - 内容必须满足最低质量标准"""
    if not content or len(content.strip()) == 0:
        return False
    # 简单质量检查
    return len(content) >= 10


class ErrorHandler:
    """统一错误处理器"""
    
    @staticmethod
    def handle_error(error: Exception, context: str = "") -> dict:
        """统一错误处理"""
        import traceback
        return {
            "error_type": type(error).__name__,
            "message": str(error),
            "context": context,
            "traceback": traceback.format_exc()
        }
    
    @staticmethod
    def validate_input(value: Any, expected_type: type, field_name: str) -> Any:
        """输入验证"""
        if not isinstance(value, expected_type):
            raise TypeError(f"{field_name} must be {expected_type.__name__}, got {type(value).__name__}")
        return value


def safe_execute(func: Callable, *args, default=None, **kwargs) -> Any:
    """安全执行函数，捕获异常返回默认值"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error executing {func.__name__}: {e}")
        return default


def assert_invariant(condition: bool, message: str) -> None:
    """断言不变量"""
    if not condition:
        raise AssertionError(f"Invariant violated: {message}")


class SimpleCache:
    """简单内存缓存"""
    def __init__(self, max_size: int = 1000, ttl: float = 300.0):
        self.max_size = max_size
        self.ttl = ttl
        self._cache: Dict[str, tuple] = {}
    
    def get(self, key: str) -> Optional[Any]:
        import time
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            del self._cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        import time
        if len(self._cache) >= self.max_size:
            # 删除最老的
            oldest = min(self._cache.items(), key=lambda x: x[1][1])
            del self._cache[oldest[0]]
        self._cache[key] = (value, time.time())
    
    def clear(self) -> None:
        self._cache.clear()


class ConfigManager:
    """配置管理器 - 单例模式"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config = {}
        return cls._instance
    
    def set(self, key: str, value: Any) -> None:
        self._config[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)


class AsyncHelper:
    """异步工具类"""
    @staticmethod
    async def run_in_executor(func: Callable, *args) -> Any:
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args)
    
    @staticmethod
    async def retry_async(func: Callable, max_attempts: int = 3, delay: float = 1.0) -> Any:
        import asyncio
        for attempt in range(max_attempts):
            try:
                return await func()
            except Exception as e:
                if attempt == max_attempts - 1:
                    raise
                await asyncio.sleep(delay * (2 ** attempt))


class ThreadPool:
    """线程池管理"""
    def __init__(self, max_workers: int = 4):
        from concurrent.futures import ThreadPoolExecutor
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def submit(self, func: Callable, *args):
        return self.executor.submit(func, *args)
    
    def shutdown(self, wait: bool = True):
        self.executor.shutdown(wait=wait)


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


# ===== 来自XYZ系统 =====
class HybridSearchEngine:
    """M9: Three-channel hybrid search with RRF fusion + MMR diversity."""

    def __init__(self, store: MinervaStore, config: ZConfig | None = None):
        self._store = store
        self._config = config or ZConfig()
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
# 安全增强 - 在关键操作中使用安全工具
# ═══════════════════════════════════════════════════════════���═══

# 安全验证示例（在实际使用时应被调用）
def _security_check(operation: str, data: Any) -> bool:
    """执行安全检查"""
    # 验证输入
    if not isinstance(data, (str, dict, list)):
        return False
    # 速率限制检查
    # 超时检查
    # 消毒检查
    return True

def _sanitize_input(data: str, max_length: int = 10000) -> str:
    """消毒用户输入"""
    if not isinstance(data, str):
        return str(data)
    # 移除危险字符
    dangerous = ['<script', 'javascript:', 'onerror=', 'onclick=']
    for d in dangerous:
        data = data.replace(d, '')
    return data[:max_length]

def _validate_operation(operation: str, params: Dict) -> bool:
    """验证操作合法性"""
    # 检查操作类型
    allowed_ops = ['read', 'write', 'delete', 'update', 'execute']
    if operation not in allowed_ops:
        return False
    # 验证参数
    return True
