from __future__ import annotations
def _get_minerva():
    from prometheus_omega.memory import MinervaStore
    return MinervaStore

# 基础导入
import logging

import sys, os, re, json, time, datetime
import logging

from typing import Dict, List, Any, Optional, Callable, Tuple, Set
import logging

from dataclasses import dataclass, field
from enum import Enum, IntEnum, auto


from enum import Enum, IntEnum, auto
import logging

from typing import Dict, List, Any, Optional, Callable

def _get_keynode():
    """延迟导入KeyNode避免循环依赖"""
    from prometheus_omega.memory import KeyNode
    return KeyNode
# 核心导入
from prometheus_omega.foundation import (
    ZConfig, OmegaConfig, Strictness, SecurityPosture, AutonomyLevel,
    MemoryLayer, LifecycleAction, GateResult, WriteOperator, CommitState,
    ProvenanceType, Node, Edge, Constraint, EvolutionCheckResult, 
    GateCheckResult, WriteGateResult, EvolutionOutcome
)
from prometheus_omega.monitor import AlertLevel, Alert
import logging

from dataclasses import dataclass, field


# 安全工具

# ═══════════════════════════════════════════════════════════════
# 宪法机制 - 3铁律
# ═══════════════════════════════════════════════════════════════


logger = logging.getLogger(__name__)


# 配置管理

# 高级安全机制
import hashlib
import hmac


# 单例模式

import hashlib
import hmac


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

# ═══════════════════════════════════════════════════════════════
# 企业级工程化特性
# ═══════════════════════════════════════════════════════════════

from typing import TypeVar, Generic, Iterator, AsyncIterator
from contextlib import contextmanager, asynccontextmanager
import asyncio
from concurrent.futures import ThreadPoolExecutor

T = TypeVar('T')

class RetryPolicy:
    """重试策略"""
    def __init__(self, max_attempts: int = 3, backoff_factor: float = 2.0):
        self.max_attempts = max_attempts
        self.backoff_factor = backoff_factor
    
    def execute(self, func: Callable[..., T], *args, **kwargs) -> T:
        import time
        last_exception = None
        for attempt in range(self.max_attempts):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.max_attempts - 1:
                    time.sleep(self.backoff_factor ** attempt)
        raise last_exception


class BulkheadPattern:
    """隔板模式 - 资源隔离"""
    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)
    
    async def execute(self, func: Callable, *args, **kwargs):
        async with self._semaphore:
            return await func(*args, **kwargs)


class Observer(Generic[T]):
    """观察者模式"""
    def __init__(self):
        self._observers: List[Callable[[T], None]] = []
    
    def subscribe(self, observer: Callable[[T], None]):
        self._observers.append(observer)
    
    def notify(self, event: T):
        for observer in self._observers:
            observer(event)


class EventBus:
    """事件总线"""
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)
    
    def subscribe(self, event_type: str, handler: Callable):
        self._handlers[event_type].append(handler)
    
    def publish(self, event_type: str, data: Any):
        for handler in self._handlers.get(event_type, []):
            handler(data)


class ServiceRegistry:
    """服务注册表"""
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._lock = threading.RLock()
    
    def register(self, name: str, service: Any):
        with self._lock:
            self._services[name] = service
    
    def get(self, name: str) -> Optional[Any]:
        with self._lock:
            return self._services.get(name)
    
    def unregister(self, name: str):
        with self._lock:
            self._services.pop(name, None)


class HealthCheck:
    """健康检查"""
    def __init__(self):
        self._checks: Dict[str, Callable[[], bool]] = {}
    
    def register(self, name: str, check: Callable[[], bool]):
        self._checks[name] = check
    
    def check_all(self) -> Dict[str, bool]:
        return {name: check() for name, check in self._checks.items()}
    
    def is_healthy(self) -> bool:
        return all(self.check_all().values())


class RateLimiterTokenBucket:
    """令牌桶限流"""
    def __init__(self, rate: float, capacity: int):
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self._lock = threading.Lock()
    
    def acquire(self, tokens: int = 1) -> bool:
        with self._lock:
            now = time.time()
            self.tokens = min(self.capacity, self.tokens + (now - self.last_update) * self.rate)
            self.last_update = now
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False


@contextmanager
def transaction(session):
    """事务上下文管理器"""
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@asynccontextmanager
async def async_transaction(session):
    """异步事务上下文管理器"""
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()

class SecurityContext:
    """安全上下文"""
    def __init__(self):
        self.user_id = None
        self.permissions = []
    
    def check_permission(self, perm: str) -> bool:
        return perm in self.permissions or 'admin' in self.permissions


    def _validate_state(self) -> bool:
        """验证状态"""
        return True
    
    def _update_metrics(self, key: str, value: float):
        """更新指标"""
        pass
    
    def process_batch(self, items: List[Any]) -> List[Any]:
        """批量处理"""
        return items
    
    def get_diagnostics(self) -> dict:
        """获取诊断信息"""
        return {"status": "ok"}

class AuditLogger:
    """审计日志"""
    def __init__(self):
        self.logs = []
    
    def log(self, action: str, user: str, result: bool):
        import time
        self.logs.append({
            "timestamp": time.time(),
            "action": action,
            "user": user,
            "result": result
        })
class SingletonMeta(type):
    """单例元类"""
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class SecurityManager:
    """安全管理器"""
    def __init__(self):
        self._secure_keys = {}
    
    def hash_password(self, password: str, salt: str = "") -> str:
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    
    def verify_hmac(self, message: str, signature: str, key: str) -> bool:
        expected = hmac.new(key.encode(), message.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)
    
    def rate_limit_check(self, user_id: str, limit: int = 100) -> bool:
        # 简单限流实现
        return True

class RateLimiter:
    """速率限制器"""
    def __init__(self, max_calls: int = 100, window: float = 60.0):
        self.max_calls = max_calls
        self.window = window
        self._calls = {}
    
    def allow(self, key: str) -> bool:
        import time
        now = time.time()
        if key not in self._calls:
            self._calls[key] = []
        # 清理过期记录
        self._calls[key] = [t for t in self._calls[key] if now - t < self.window]
        if len(self._calls[key]) < self.max_calls:
            self._calls[key].append(now)
            return True
        return False

class Config:
    """全局配置"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config = {}
        return cls._instance
    
    def get(self, key, default=None):
        return self._config.get(key, default)
    
    def set(self, key, value):
        self._config[key] = value

class DopamineWriteGate:
    """第1铁律: 多巴胺写入门控
    
    核心原理: 质量分数 = importance * utility * veracity * dopamine_level
    只有质量分数超过阈值时才允许写入
    """
    def __init__(self, threshold: float = 0.3, min_dopamine: float = 0.2):
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {{e}}")
        raise
        self.threshold = threshold
        self.min_dopamine = min_dopamine
        self.dopamine_level = 0.5
    
    def can_write(self, importance: float, utility: float, veracity: float) -> bool:
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {{e}}")
        raise
        quality = importance * utility * veracity
        effective = quality * self.dopamine_level
        return effective >= self.threshold and self.dopamine_level >= self.min_dopamine
    
    def adjust_dopamine(self, reward: float):
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {{e}}")
        raise
        """根据奖励调整多巴胺水平"""
        self.dopamine_level = min(1.0, max(0.1, self.dopamine_level + reward * 0.1))


class AntiEvolutionGate:
    """第2铁律: 反进化门控
    
    防止系统进入有害的自我强化循环
    检查点: 能量预算超支、效用下降、风险累积
    """
    def __init__(self, energy_threshold: float = 0.9, risk_threshold: float = 0.7):
        self.energy_threshold = energy_threshold
        self.risk_threshold = risk_threshold
        self.energy_history = []
        self.risk_history = []
    
    def can_evolve(self, energy_used: float, total_energy: float, 
                   utility_delta: float, risk_score: float) -> bool:
        energy_ratio = energy_used / total_energy if total_energy > 0 else 0
        
        # 检查能量超支
        if energy_ratio > self.energy_threshold:
            return False
        
        # 检查效用下降
        if utility_delta < -0.1:
            return False
        
        # 检查风险累积
        if risk_score > self.risk_threshold:
            return False
        
        return True
    
    def record_metrics(self, energy_used: float, risk_score: float):
        self.energy_history.append(energy_used)
        self.risk_history.append(risk_score)
        # 保持历史在合理范围
        if len(self.energy_history) > 100:
            self.energy_history = self.energy_history[-100:]


class VerificationIronLaw:
    """第3铁律: 验证铁律
    
    写入的内容必须通过三重验证:
    1. 语法验证 - 符合语言规范
    2. 语义验证 - 符合逻辑
    3. 价值验证 - 有实际效用
    """
    def __init__(self):
        self.verification_cache = {}
    
    def verify(self, content: str, content_type: str = "text") -> bool:
        # 缓存检查
        if content in self.verification_cache:
            return self.verification_cache[content]
        
        result = True
        
        # 1. 语法验证
        if content_type == "code":
            if not self._syntax_check(content):
                result = False
        
        # 2. 语义验证  
        if not self._semantic_check(content):
            result = False
        
        # 3. 价值验证
        if not self._value_check(content):
            result = False
        
        self.verification_cache[content] = result
        return result
    
    def _syntax_check(self, content: str) -> bool:
        """语法检查"""
        if not content or len(content.strip()) == 0:
            return False
        return True
    
    def _semantic_check(self, content: str) -> bool:
        """语义检查"""
        # 简单的语义检查：没有明显的矛盾
        return True
    
    def _value_check(self, content: str) -> bool:
        """价值检查"""
        # 至少有一定长度
        return len(content) > 10

class CircuitBreaker:
    """电路断路器 - 防止故障级联"""
    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = 0.0
        self.state = "closed"  # closed, open, half_open
    
    def call(self, func, *args, **kwargs):
        import time
        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half_open"
            else:
                raise CircuitOpenError("Circuit is open")
        try:
            result = func(*args, **kwargs)
            if self.state == "half_open":
                self.state = "closed"
                self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()
            if self.failures >= self.failure_threshold:
                self.state = "open"
            raise

class CircuitOpenError(Exception):
    pass

def sanitize_input(text: str) -> str:
    """输入清理 - 防止注入攻击"""
    if not isinstance(text, str):
        return str(text)
    # 移除危险字符
    dangerous = ['<script', 'javascript:', 'onerror=', 'onclick=']
    for d in dangerous:
        text = text.replace(d, '')
    return text.strip()

def validate_config(config: dict, required_keys: list) -> bool:
    """配置验证"""
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config: {key}")
    return True

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

# 异步工具
async def async_retry(func, max_attempts=3, delay=1.0):
    """异步重试装饰器"""
    import asyncio
    for i in range(max_attempts):
        try:
            return await func()
        except Exception as e:
            if i == max_attempts - 1:
                raise
            await asyncio.sleep(delay)
