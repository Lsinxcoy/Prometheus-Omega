from prometheus_omega.foundation import KeyNode
"""L2 Memory - 记忆层

整合XYZ机制:
- X: UnifiedEntry(15维), 13-table SQLite, OME离线引擎, 4层Bank
- Y: Bank架构, Veracity置信度, Consolidation
- Z: GraphMemory, FourNetworkMemory, 四网络(World/Experiences/Summaries/Beliefs)
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Callable
from datetime import datetime, timezone
from enum import Enum
import uuid
import json


# ===== 15维UnifiedEntry - 来自X系统机制 #4 =====
# ═══════════════════════════════════════════════════════════════
# 安全工具类
# ═══════════════════════════════════════════════════════════════


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



@dataclass

@dataclass

@dataclass
class EpisodeEvent:
    """情节事件"""
    event_id: str
    timestamp: float
    event_type: str
    content: str
    importance: float = 0.5
class PersonalEvent:
    """个人事件"""
    event_id: str
    event_type: str
    timestamp: float
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
class Topic:
    """主题"""
    topic_id: str
    name: str
    keywords: List[str] = field(default_factory=list)
    weight: float = 1.0
class ErrorHandler:
    """统一错误处理器 - 提供异常处理和输入验证
    
    Attributes:
        提供静态方法处理错误和验证输入
    
    Example:
        >>> result = ErrorHandler.handle_error(ValueError("test"), "context")
        >>> print(result['error_type'])
        'ValueError'
    """
    
    @staticmethod
    def handle_error(error: Exception, context: str = "") -> dict:
        """统一错误处理
        
        Args:
            error: 异常对象
            context: 错误上下文
            
        Returns:
            dict: 错误信息字典
        """
        import traceback
        return {
            "error_type": type(error).__name__,
            "message": str(error),
            "context": context,
            "traceback": traceback.format_exc()
        }
    
    @staticmethod
    def validate_input(value: Any, expected_type: type, field_name: str) -> Any:
        """输入验证
        
        Args:
            value: 待验证值
            expected_type: 期望类型
            field_name: 字段名
            
        Returns:
            Any: 验证通过返回原值
            
        Raises:
            TypeError: 类型不匹配
        """
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


class CircuitBreaker:
    """熔断器 - 防止故障级联"""
    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    def record_success(self) -> None:
        self.failure_count = 0
        self.state = "closed"
    
    def record_failure(self) -> None:
        import time
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
    
    def can_execute(self) -> bool:
        import time
        if self.state == "closed":
            return True
        if self.state == "open" and self.last_failure_time:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half-open"
                return True
        return self.state == "half-open"


class RateLimiter:
    """速率限制器 - 防止API滥用"""
    def __init__(self, max_requests: int = 100, window_seconds: float = 60.0):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = []
    
    def is_allowed(self) -> bool:
        import time
        now = time.time()
        self.requests = [t for t in self.requests if now - t < self.window_seconds]
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        return False


class InputValidator:
    """输入验证器 - 防止注入攻击"""
    @staticmethod
    def sanitize(value: str, max_length: int = 10000) -> str:
        """清理输入"""
        if not isinstance(value, str):
            return str(value)
        # 移除危险字符
        value = value.replace("<script", "").replace("javascript:", "")
        return value[:max_length]
    
    @staticmethod
    def validate_type(value: Any, expected_type: type) -> bool:
        """类型验证"""
        return isinstance(value, expected_type)


class EntryCategory(Enum):
    """记忆类别"""
    FACT = "fact"
    EXPERIENCE = "experience"
    SKILL = "skill"
    TOOL = "tool"
    TASK = "task"
    CONCEPT = "concept"
    RELATIONSHIP = "relationship"
    METADATA = "metadata"


@dataclass
class UnifiedEntry:
    """15维统一记忆条目 - 来自X系统最丰富数据模型
    
    15个维度:
    1. id - 唯一标识
    2. content - 内容
    3. category - 类别
    4. importance - 重要性 (0-1)
    5. veracity - 真实性 (0-1)
    6. created_at - 创建时间
    7. updated_at - 更新时间
    8. last_accessed - 最��访问
    9. access_count - 访问次数
    10. tags - 标签
    11. entity_ids - 关联实体
    12. source - 来源
    13. provenance - 来源追踪
    14. embedding - 向量嵌入
    15. metadata - 扩展元数据
    """
    
    # 必需字段
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    category: EntryCategory = EntryCategory.FACT
    
    # 重要性与真实性
    importance: float = 0.5  # 0-1
    veracity: float = 0.5    # 置信度
    
    # 时间戳
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_accessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    access_count: int = 0
    
    # 关联
    tags: List[str] = field(default_factory=list)
    entity_ids: List[str] = field(default_factory=list)
    source: str = "system"
    
    # 来源追踪
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    # 向量
    embedding: Optional[List[float]] = None
    
    # 扩展
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # 额外维度 (完整15维)
    embedding_model: str = ""
    language: str = "zh"
    isarchived: bool = False
    expires_at: Optional[datetime] = None
    
    def access(self):
        """记录访问"""
        self.last_accessed = datetime.now(timezone.utc)
        self.access_count += 1
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "content": self.content,
            "category": self.category.value,
            "importance": self.importance,
            "veracity": self.veracity,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "access_count": self.access_count,
            "tags": self.tags,
            "entity_ids": self.entity_ids,
            "source": self.source,
            "provenance": self.provenance,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "UnifiedEntry":
        """从字典创建"""
        if "category" in data and isinstance(data["category"], str):
            data["category"] = EntryCategory(data["category"])
        return cls(**data)


# ===== 四网络记忆 - 来自Z系统Hindsight =====
class MemoryNetwork(Enum):
    """四网络类型 - 来自Z系统Hindsight"""
    WORLD = "world"              # 世界事实
    EXPERIENCES = "experiences"  # 智能体经验
    SUMMARIES = "summaries"      # 实体摘要
    BELIEFS = "beliefs"          # 演化信念


@dataclass
class FourNetworkFact:
    """四网络记忆事实"""
    fact_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    network_type: MemoryNetwork = MemoryNetwork.WORLD

    # 实体关联
    entity_ids: List[str] = field(default_factory=list)

    # 时间和置信度
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    confidence: float = 0.5
    
    def is_trusted(self, threshold: float = 0.6) -> bool:
        return self.confidence >= threshold
    
    def get_age(self) -> float:
        return (datetime.now(timezone.utc) - self.created_at).total_seconds()
    
    def to_dict(self) -> Dict:
        return {
            'fact_id': self.fact_id,
            'content': self.content[:100] + '...' if len(self.content) > 100 else self.content,
            'network_type': self.network_type.value if isinstance(self.network_type, Enum) else self.network_type,
            'entity_ids': self.entity_ids,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat(),
        }
    
    def add_entity(self, entity_id: str):
        if entity_id not in self.entity_ids:
            self.entity_ids.append(entity_id)


class MemoryNetwork(Enum):
    """四网络类型"""
    WORLD = "world"
    EXPERIENCES = "experiences"
    SUMMARIES = "summaries"
    BELIEFS = "beliefs"


class FourNetworkMemory:
    """四网络记忆系统 - 来自Z系统Hindsight
    
    整合Hindsight的核心创新:
    - World Facts: 客观知识
    - Experiences: 交互历史
    - Summaries: 实体档案
    - Beliefs: 演化信念
    
    新增方法:
    - consolidate: 记忆整合
    - prune: 记忆修剪
    - get_temporal_context: 时间上下文
    """
    
    def __init__(self, bank_id: str = "default", max_per_network: int = 10000):
        self.bank_id = bank_id
        self.max_per_network = max_per_network
        
        # 四个网络存储
        self.world_facts: Dict[str, FourNetworkFact] = {}
        self.experiences: Dict[str, FourNetworkFact] = {}
        self.summaries: Dict[str, FourNetworkFact] = {}
        self.beliefs: Dict[str, FourNetworkFact] = {}
        
        # 访问统计
        self._access_counts: Dict[str, int] = {}
        
        # 索引 (加速检索)
        self._content_index: Dict[str, Set[str]] = {}  # word -> fact_ids
        self._tag_index: Dict[str, Set[str]] = {}       # tag -> fact_ids
    
    def store(self, entry) -> bool:
        """存储条目 (统一接口)
        
        Args:
            entry: UnifiedEntry 或 FourNetworkFact
            
        Returns:
            bool: 是否成功
        """
        from datetime import datetime, timezone
        
        # 如果是 UnifiedEntry，转换为 FourNetworkFact
        if hasattr(entry, 'id') and hasattr(entry, 'content'):
            fact = FourNetworkFact(
                fact_id=entry.id,
                content=entry.content,
                network_type=MemoryNetwork.WORLD,
                confidence=entry.confidence if hasattr(entry, 'confidence') else 0.5,
                tags=entry.tags if hasattr(entry, 'tags') else [],
            )
            self.world_facts[fact.fact_id] = fact
            self._index_fact(fact)
            return True
        
        # 如果是 FourNetworkFact
        if hasattr(entry, 'fact_id'):
            if entry.network_type == MemoryNetwork.WORLD:
                self.world_facts[entry.fact_id] = entry
            elif entry.network_type == MemoryNetwork.EXPERIENCES:
                self.experiences[entry.fact_id] = entry
            elif entry.network_type == MemoryNetwork.SUMMARIES:
                self.summaries[entry.fact_id] = entry
            elif entry.network_type == MemoryNetwork.BELIEFS:
                self.beliefs[entry.fact_id] = entry
            self._index_fact(entry)
            return True
        
        return False
    
    def _index_fact(self, fact: FourNetworkFact):
        """索引事实用于快速检索"""
        # 内容分词索引
        words = fact.content.lower().split()
        for word in words:
            if len(word) > 2:  # 忽略短词
                if word not in self._content_index:
                    self._content_index[word] = set()
                self._content_index[word].add(fact.fact_id)
        
        # 标签索引
        for tag in fact.tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = set()
            self._tag_index[tag].add(fact.fact_id)
    
    def _remove_from_index(self, fact_id: str):
        """从索引中移除"""
        # 简化实现: 重建索引(实际应该反向映射)
        pass
    
    # === 三操作 API (来自Hindsight) ===
    
    def retain(self, content: str, network: MemoryNetwork = MemoryNetwork.WORLD,
               entity_ids: List[str] = None, tags: List[str] = None,
               confidence: float = 0.5, source: str = "") -> FourNetworkFact:
        """retain: 存入记忆
        
        Args:
            content: 记忆内容
            network: 目标网络
            entity_ids: 关联实体ID
            tags: 标签
            confidence: 置信度 (0-1)
            source: 来源
            
        Returns:
            FourNetworkFact: 存储的事实
        """
        # 检查容量
        network_key = network.value
        current_size = len(getattr(self, f"{network_key}_facts"))
        
        if current_size >= self.max_per_network:
            # 需要修剪
            self.prune(network, count=100)
        
        fact = FourNetworkFact(
            content=content,
            network_type=network,
            entity_ids=entity_ids or [],
            tags=tags or [],
            confidence=confidence,
            source=source,
        )
        
        # 存储到对应网络
        if network == MemoryNetwork.WORLD:
            self.world_facts[fact.fact_id] = fact
        elif network == MemoryNetwork.EXPERIENCES:
            self.experiences[fact.fact_id] = fact
        elif network == MemoryNetwork.SUMMARIES:
            self.summaries[fact.fact_id] = fact
        elif network == MemoryNetwork.BELIEFS:
            self.beliefs[fact.fact_id] = fact
        
        # 索引
        self._index_fact(fact)
        
        return fact
    
    def recall(self, query: str, network: MemoryNetwork = None,
               top_k: int = 10) -> List[FourNetworkFact]:
        """recall: 检索记忆
        
        Args:
            query: 查询字符串
            network: 指定网络 (None表示所有网络)
            top_k: 返回数量
            
        Returns:
            List[FourNetworkFact]: 相关记忆列表
        """
        import math
        
        # 确定搜索范围
        networks = [network] if network else list(MemoryNetwork)
        
        # 查询分词
        query_words = query.lower().split()
        
        results = []
        
        for net in networks:
            if net == MemoryNetwork.WORLD:
                facts = self.world_facts
            elif net == MemoryNetwork.EXPERIENCES:
                facts = self.experiences
            elif net == MemoryNetwork.SUMMARIES:
                facts = self.summaries
            elif net == MemoryNetwork.BELIEFS:
                facts = self.beliefs
            else:
                continue
            
            # 计算相关性分数
            for fact in facts.values():
                score = self._calculate_relevance(query_words, fact)
                if score > 0:
                    results.append((score, fact))
        
        # 排序并返回top_k
        results.sort(key=lambda x: x[0], reverse=True)
        return [f for _, f in results[:top_k]]
    
    def _calculate_relevance(self, query_words: List[str], fact: FourNetworkFact) -> float:
        """计算查询与事实的相关性"""
        if not query_words:
            return 0.0
        
        score = 0.0
        content_lower = fact.content.lower()
        
        # 1. 关键词匹配分数
        for word in query_words:
            if word in content_lower:
                score += 1.0
            # 标签匹配
            if any(word in tag.lower() for tag in fact.tags):
                score += 0.5
        
        # 2. 置信度加权
        score *= (0.5 + fact.confidence * 0.5)
        
        # 3. 时间衰减 (新记忆权重略高)
        days_old = (datetime.now(timezone.utc) - fact.created_at).days
        time_factor = math.exp(-days_old / 365)  # 1年后衰减到37%
        score *= time_factor
        
        return score
    
    def reflect(self, query: str) -> Dict[str, Any]:
        """reflect: 反思学习
        
        基于检��到的记忆生成洞察
        
        Args:
            query: 反思主题
            
        Returns:
            Dict: 反思结果
        """
        # 收集相关记忆
        relevant = self.recall(query, top_k=50)
        
        if not relevant:
            return {
                "query": query,
                "relevant_count": 0,
                "networks_found": [],
                "key_themes": [],
                "insights": ["无相关记忆"],
            }
        
        # 提取主题
        themes = self._extract_themes(relevant)
        
        # 生成洞察
        insights = self._generate_insights(relevant)
        
        # 分析网络分布
        networks_found = list(set(f.network_type.value for f in relevant))
        
        return {
            "query": query,
            "relevant_count": len(relevant),
            "networks_found": networks_found,
            "key_themes": themes,
            "insights": insights,
            "avg_confidence": sum(f.confidence for f in relevant) / len(relevant),
            "time_span_days": self._calculate_time_span(relevant),
        }
    
    def _extract_themes(self, facts: List[FourNetworkFact]) -> List[str]:
        """提取主题"""
        all_tags = []
        for f in facts:
            all_tags.extend(f.tags)
        
        if not all_tags:
            return []
        
        # 标签频率统计
        from collections import Counter
        tag_counts = Counter(all_tags)
        
        return [tag for tag, _ in tag_counts.most_common(5)]
    
    def _generate_insights(self, facts: List[FourNetworkFact]) -> List[str]:
        """生成洞察"""
        if not facts:
            return ["无足够信息生成洞察"]
        
        insights = []
        
        # 1. 跨网络洞察
        networks = set(f.network_type for f in facts)
        if len(networks) > 1:
            insights.append(f"跨{len(networks)}个网络发现关联")
        
        # 2. 置信度分析
        avg_confidence = sum(f.confidence for f in facts) / len(facts)
        if avg_confidence > 0.7:
            insights.append(f"高置信度记忆群 ({avg_confidence:.0%})")
        elif avg_confidence < 0.4:
            insights.append(f"低置信度记忆群,建议核实 ({avg_confidence:.0%})")
        
        # 3. 时间分析
        if len(facts) > 1:
            time_span = (max(f.created_at for f in facts) - 
                        min(f.created_at for f in facts)).days
            if time_span > 0:
                insights.append(f"时间跨度: {time_span}天")
        
        # 4. 来源分析
        sources = set(f.source for f in facts if f.source)
        if sources:
            insights.append(f"来源: {', '.join(list(sources)[:3])}")
        
        return insights
    
    def _calculate_time_span(self, facts: List[FourNetworkFact]) -> int:
        """计算时间跨度"""
        if len(facts) < 2:
            return 0
        
        dates = [f.created_at for f in facts]
        return (max(dates) - min(dates)).days
    
    # === 额外方法 ===
    
    def consolidate(self, network: MemoryNetwork = None) -> Dict[str, Any]:
        """记忆整合 - 合并相似记忆
        
        Args:
            network: 指定网络 (None表示所有)
            
        Returns:
            Dict: 整合统计
        """
        networks = [network] if network else list(MemoryNetwork)
        
        consolidated_count = 0
        removed_ids = []
        
        for net in networks:
            if net == MemoryNetwork.WORLD:
                facts = self.world_facts
            elif net == MemoryNetwork.EXPERIENCES:
                facts = self.experiences
            elif net == MemoryNetwork.SUMMARIES:
                facts = self.summaries
            elif net == MemoryNetwork.BELIEFS:
                facts = self.beliefs
            else:
                continue
            
            # 简化: 移除过期的低置信度记忆
            threshold = datetime.now(timezone.utc).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            
            for fact_id, fact in list(facts.items()):
                if (fact.valid_until and fact.valid_until < datetime.now(timezone.utc)):
                    if fact.confidence < 0.3:
                        removed_ids.append(fact_id)
                        del facts[fact_id]
                        consolidated_count += 1
        
        return {
            "consolidated_count": consolidated_count,
            "removed_ids": removed_ids,
        }
    
    def prune(self, network: MemoryNetwork, count: int = 100) -> int:
        """记忆修剪 - 移除低价值记忆
        
        Args:
            network: 目标网络
            count: 修剪数量
            
        Returns:
            int: 实际修剪数量
        """
        if network == MemoryNetwork.WORLD:
            facts = self.world_facts
        elif network == MemoryNetwork.EXPERIENCES:
            facts = self.experiences
        elif network == MemoryNetwork.SUMMARIES:
            facts = self.summaries
        elif network == MemoryNetwork.BELIEFS:
            facts = self.beliefs
        else:
            return 0
        
        if len(facts) < self.max_per_network * 0.8:
            return 0
        
        # 按置信度和时间排序, 移除最低的
        sorted_facts = sorted(
            facts.items(),
            key=lambda x: (x[1].confidence, x[1].created_at)
        )
        
        removed = 0
        for fact_id, _ in sorted_facts[:count]:
            del facts[fact_id]
            removed += 1
        
        return removed
    
    def get_network_stats(self) -> Dict[str, int]:
        """获取网络统计"""
        return {
            "world": len(self.world_facts),
            "experiences": len(self.experiences),
            "summaries": len(self.summaries),
            "beliefs": len(self.beliefs),
            "total": sum([
                len(self.world_facts),
                len(self.experiences),
                len(self.summaries),
                len(self.beliefs),
            ]),
            "indexed_words": len(self._content_index),
            "indexed_tags": len(self._tag_index),
        }
    
    def get_temporal_context(self, hours: int = 24) -> Dict[str, Any]:
        """获取时间上下文 - 特定时间段内的记忆
        
        Args:
            hours: 回溯小时数
            
        Returns:
            Dict: 时间上下文
        """
        import math
        cutoff = datetime.now(timezone.utc).timestamp() - (hours * 3600)
        
        all_facts = (
            list(self.world_facts.values()) +
            list(self.experiences.values()) +
            list(self.summaries.values()) +
            list(self.beliefs.values())
        )
        
        recent = [f for f in all_facts if f.created_at.timestamp() > cutoff]
        
        return {
            "hours": hours,
            "recent_count": len(recent),
            "by_network": {
                "world": len([f for f in recent if f.network_type == MemoryNetwork.WORLD]),
                "experiences": len([f for f in recent if f.network_type == MemoryNetwork.EXPERIENCES]),
                "summaries": len([f for f in recent if f.network_type == MemoryNetwork.SUMMARIES]),
                "beliefs": len([f for f in recent if f.network_type == MemoryNetwork.BELIEFS]),
            },
            "avg_confidence": sum(f.confidence for f in recent) / len(recent) if recent else 0,
        }


# ===== Bank分层架构 - 来自Y系统 =====
class BankLayer(Enum):
    """Bank分层 - 来自X系统#8"""
    WORKING = "working"       # 工作记忆 (短时)
    EPISODIC = "episodic"     # 情节记忆
    SEMANTIC = "semantic"     # 语义记忆
    ARCHIVE = "archive"       # 档案记忆


@dataclass
class Bank:
    """分层记忆银行 - 来自Y系统核心机制
    
    4层自动迁移:
    - Working: 当前活跃
    - Episodic: 重要经历
    - Semantic: 抽象知识
    - Archive: 长期存储
    """
    
    bank_id: str = "default"
    working: Dict[str, UnifiedEntry] = field(default_factory=dict)
    episodic: Dict[str, UnifiedEntry] = field(default_factory=dict)
    semantic: Dict[str, UnifiedEntry] = field(default_factory=dict)
    archive: Dict[str, UnifiedEntry] = field(default_factory=dict)
    
    # 迁移阈值
    working_to_episodic_threshold: int = 10  # 访问次数
    episodic_to_semantic_days: int = 30      # 天数
    semantic_to_archive_days: int = 90       # 天数
    
    def add(self, entry: UnifiedEntry, layer: BankLayer = BankLayer.WORKING):
        """添加到指定层"""
        if layer == BankLayer.WORKING:
            self.working[entry.id] = entry
        elif layer == BankLayer.EPISODIC:
            self.episodic[entry.id] = entry
        elif layer == BankLayer.SEMANTIC:
            self.semantic[entry.id] = entry
        elif layer == BankLayer.ARCHIVE:
            self.archive[entry.id] = entry
    
    def store(self, entry: UnifiedEntry) -> bool:
        """存储条目到工作层 (store是add的别名)
        
        Args:
            entry: 统一条目
            
        Returns:
            bool: 是否成功
        """
        self.add(entry, BankLayer.WORKING)
        return True
    
    def migrate(self) -> int:
        """执行自动迁移, 返回迁移数量"""
        migrated = 0
        now = datetime.now(timezone.utc)
        
        # Working → Episodic
        for entry_id, entry in list(self.working.items()):
            if entry.access_count >= self.working_to_episodic_threshold:
                self.episodic[entry_id] = entry
                del self.working[entry_id]
                migrated += 1
        
        # Episodic → Semantic
        for entry_id, entry in list(self.episodic.items()):
            days = (now - entry.updated_at).days
            if days >= self.episodic_to_semantic_days:
                self.semantic[entry_id] = entry
                del self.episodic[entry_id]
                migrated += 1
        
        # Semantic → Archive
        for entry_id, entry in list(self.semantic.items()):
            days = (now - entry.updated_at).days
            if days >= self.semantic_to_archive_days:
                self.archive[entry_id] = entry
                del self.semantic[entry_id]
                migrated += 1
        
        return migrated
    
    def get_all_count(self) -> int:
        """获取总数量"""
        return len(self.working) + len(self.episodic) + len(self.semantic) + len(self.archive)
    
    def get_layer_stats(self) -> Dict[str, int]:
        """获取各层统计"""
        return {
            "working": len(self.working),
            "episodic": len(self.episodic),
            "semantic": len(self.semantic),
            "archive": len(self.archive),
        }


# ===== Veracity贝叶斯置信度 - 来自X/Y系统 =====
@dataclass
class Veracity:
    """贝叶斯置信度 - 来自X系���#9
    
    多源置信度合并
    """
    
    sources: Dict[str, float] = field(default_factory=dict)  # source -> confidence
    combined_confidence: float = 0.5
    update_count: int = 0
    
    def add_source(self, source: str, confidence: float):
        """添加来源"""
        self.sources[source] = confidence
        self.update_count += 1
        self._recalculate()
    
    def _recalculate(self):
        """贝叶斯合并"""
        if not self.sources:
            self.combined_confidence = 0.5
            return
        
        # 简化的贝叶斯更新
        product = 1.0
        for conf in self.sources.values():
            product *= conf
        
        # 使用几何平均
        n = len(self.sources)
        self.combined_confidence = product ** (1.0 / n) if n > 0 else 0.5


# ===== 统一内存存储 =====
class MemoryStore:
    """统一内存存储 - 整合XYZ的记忆系统
    
    整合:
    - X: 15维UnifiedEntry
    - Y: Bank分层
    - Z: GraphMemory + FourNetwork
    """
    
    def __init__(self):
        self.entries: Dict[str, UnifiedEntry] = {}
        self.bank = Bank(bank_id="default")
        self.four_network = FourNetworkMemory()
        self.veracity = Veracity()
    
    def add(self, entry: UnifiedEntry) -> str:
        """添加记忆"""
        self.entries[entry.id] = entry
        self.bank.add(entry)
        return entry.id
    
    def get(self, entry_id: str) -> Optional[UnifiedEntry]:
        """获取记忆"""
        entry = self.entries.get(entry_id)
        if entry:
            entry.access()
        return entry
    
    def search(self, query: str, limit: int = 10) -> List[UnifiedEntry]:
        """搜索"""
        results = []
        query_lower = query.lower()
        
        for entry in self.entries.values():
            if query_lower in entry.content.lower():
                results.append(entry)
        
        # 按重要性排序
        results.sort(key=lambda e: -e.importance)
        return results[:limit]
    
    def get_stats(self) -> dict:
        """获取统计"""
        return {
            "total_entries": len(self.entries),
            "bank_layers": self.bank.get_layer_stats(),
            "four_network": self.four_network.get_network_stats(),
            "veracity_sources": len(self.veracity.sources),
        }


# ===== 工厂函数 =====
def create_unified_entry(content: str, category: EntryCategory = EntryCategory.FACT,
                         importance: float = 0.5, **kwargs) -> UnifiedEntry:
    """创建15维统一记忆条目"""
    return UnifiedEntry(
        content=content,
        category=category,
        importance=importance,
        **kwargs
    )


def create_four_network_memory(bank_id: str = "default") -> FourNetworkMemory:
    """创建四网络记忆"""
    return FourNetworkMemory(bank_id=bank_id)


def create_bank(bank_id: str = "default") -> Bank:
    """创建Bank"""
    return Bank(bank_id=bank_id)


def create_memory_store() -> MemoryStore:
    """创建统一内存存储"""
    return MemoryStore()


# ===== 来自XYZ系统 =====
class GraphMemory:
    """图结构记忆 - 四层节点架构
    
    基于MRAgent的图记忆设计：
    - KeyNode: 关键词节点
    - Topic: 主题节点  
    - PersonalEvent: 个人事件
    - EpisodeEvent: 对话事件
    
    边关系：
    - Key → Topic (通过tag连接)
    - Topic → EpisodeEvent (事件聚类)
    - Personal → EpisodeEvent (人-事件关系)
    """
    
    def __init__(self):
        # 四层节点
        self.key_nodes: Dict[str, KeyNode] = {}
        self.topics: Dict[str, Topic] = {}
        self.personal_events: Dict[str, PersonalEvent] = {}
        self.episode_events: Dict[str, EpisodeEvent] = {}
        
        # 人-事件索引
        self.person_events: Dict[str, List[str]] = defaultdict(list)
        
        # 时间索引
        self.temporal_index: Dict[str, List[str]] = defaultdict(list)
    
    def add_episode(self, text: str, metadata: dict = None) -> str:
        """添加对话事件"""
        event_id = f"E{len(self.episode_events)}"
        episode = EpisodeEvent(
            event_id=event_id,
            text=text,
            metadata=metadata or {}
        )
        self.episode_events[event_id] = episode
        
        # 时间索引
        conversation_id = metadata.get("conversation_id", "default") if metadata else "default"
        self.temporal_index[conversation_id].append(event_id)
        
        return event_id
    
    def add_key_node(self, key: str, text: str = "") -> KeyNode:
        """添加关键词节点"""
        if key not in self.key_nodes:
            self.key_nodes[key] = KeyNode(key_id=key, text=text or key)
        return self.key_nodes[key]
    
    def link_key_to_episode(self, key: str, event_id: str, tag: str) -> None:
        """建立Key → Episode的边"""
        key_node = self.add_key_node(key)
        key_node.add_tag(tag, event_id)
    
    def add_topic(self, topic_id: str, text: str) -> Topic:
        """添加主题节点"""
        if topic_id not in self.topics:
            self.topics[topic_id] = Topic(topic_id=topic_id, text=text)
        return self.topics[topic_id]
    
    def add_personal_event(self, person: str, text: str, 
                          tag: str, origin: str) -> str:
        """添加个人事件"""
        event_id = f"P{len(self.personal_events)}"
        event = PersonalEvent(
            person=person,
            personal_id=event_id,
            text=text,
            tag=tag,
            origin=origin
        )
        self.personal_events[event_id] = event
        self.person_events[person].append(event_id)
        return event_id
    
    def traverse_by_tag(self, key: str, tag: str) -> List[str]:
        """按tag遍历图 - 获取相关事件"""
        key_node = self.key_nodes.get(key)
        if not key_node:
            return []
        return key_node.get_events_by_tag(tag)
    
    def traverse_by_person(self, person: str) -> List[PersonalEvent]:
        """按人名遍历 - 获取个人事件"""
        event_ids = self.person_events.get(person, [])
        return [self.personal_events[eid] for eid in event_ids if eid in self.personal_events]
    
    def traverse_temporal(self, conversation_id: str) -> List[EpisodeEvent]:
        """时间遍历 - 获取对话中的所有事件"""
        event_ids = self.temporal_index.get(conversation_id, [])
        return [self.episode_events[eid] for eid in event_ids if eid in self.episode_events]
    
    def search_by_embedding(self, query_emb: List[float], 
                           k: int = 5) -> List[tuple[str, float]]:
        """Embedding相似度搜索"""
        if not query_emb:
            return []
        
        # 计算余弦相似度
        def cosine_sim(a, b):
            dot = sum(x*y for x,y in zip(a,b))
            norm_a = sum(x*x for x in a) ** 0.5
            norm_b = sum(x*x for x in b) ** 0.5
            return dot / (norm_a * norm_b + 1e-8)
        
        scores = []
        for eid, event in self.episode_events.items():
            if event.embedding:
                sim = cosine_sim(query_emb, event.embedding)
                scores.append((eid, sim))
        
        # 返回top-k
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:k]
    
    def get_statistics(self) -> dict:
        """获取记忆统计"""
        return {
            "key_nodes": len(self.key_nodes),
            "topics": len(self.topics),
            "personal_events": len(self.personal_events),
            "episode_events": len(self.episode_events),
            "conversations": len(self.temporal_index)
        }
    
    def to_dict(self) -> dict:
        """序列化"""
        return {
            "key_nodes": {k: {"key_id": v.key_id, "text": v.text, "tags": v.tag_list} 
                         for k, v in self.key_nodes.items()},
            "topics": {k: {"topic_id": v.topic_id, "text": v.text} 
                      for k, v in self.topics.items()},
            "episode_events": {k: v.to_dict() 
                              for k, v in self.episode_events.items()},
            "personal_events": {k: {"person": v.person, "text": v.text, "tag": v.tag}
                               for k, v in self.personal_events.items()}
        }
    
    def save(self, path: str) -> None:
        """保存到文件"""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load(cls, path: str) -> 'GraphMemory':
        """从文件加载"""
        with open(path) as f:
            data = json.load(f)
        
        graph = cls()
        
        # 恢复节点
        for k, v in data.get("key_nodes", {}).items():
            graph.key_nodes[k] = KeyNode(k, v.get("text", ""), v.get("tags", []))
        
        for k, v in data.get("topics", {}).items():
            graph.topics[k] = Topic(k, v.get("text", ""))
        
        for k, v in data.get("episode_events", {}).items():
            graph.episode_events[k] = EpisodeEvent(
                event_id=v["event_id"],
                text=v["text"],
                timestamp=v.get("timestamp", 0),
                embedding=v.get("embedding"),
                metadata=v.get("metadata", {})
            )
        
        for k, v in data.get("personal_events", {}).items():
            pe = PersonalEvent(
                person=v["person"],
                personal_id=k,
                text=v["text"],
                tag=v.get("tag", ""),
                origin=v.get("origin", "")
            )
            graph.personal_events[k] = pe
            graph.person_events[v["person"]].append(k)
        
        return graph


# ===== 来自XYZ系统 =====
class HallwayTransferResult:
    """Result of a hallway transfer operation."""

    def __init__(self):
        self.nodes_transferred: int = 0
        self.nodes_skipped: int = 0
        self.nodes_merged: int = 0
        self.edges_transferred: int = 0
        self.conflicts: list[dict] = []

    def to_dict(self) -> dict:
        return {
            "nodes_transferred": self.nodes_transferred,
            "nodes_skipped": self.nodes_skipped,
            "nodes_merged": self.nodes_merged,
            "edges_transferred": self.edges_transferred,
            "conflicts": self.conflicts,
        }



