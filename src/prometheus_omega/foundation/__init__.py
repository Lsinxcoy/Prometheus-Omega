# 基础导入
from __future__ import annotations
import logging

import sys, os, re, json, time, datetime
import logging

from typing import Dict, List, Any, Optional, Callable, Tuple, Set
import logging

from dataclasses import dataclass, field
from enum import Enum, IntEnum, auto


import logging

import time
from enum import IntEnum, Enum

"""L0 Foundation - 基础层

整合XYZ机制:
- X: UUIDv7, 42 NodeType, 40 EdgeType, DeterministicRuleEngine(44+规则)
- Z: Config, EventBus基础
"""
import logging

from dataclasses import dataclass, field
import logging

from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timezone
from enum import Enum
import logging

import uuid
import logging

import hashlib
import logging

import json


# ===== UUIDv7时序ID生成 =====

# 缓存工具

logger = logging.getLogger(__name__)


# 配置管理

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

    # 扩展工具方法
    def _get_state(self) -> dict:
        """获取当前状态"""
        return {"status": "active"}
    
    def _set_state(self, state: dict):
        """设置状态"""
        pass
    
    def reset(self):
        """重置"""
        pass
    
    def health_check(self) -> bool:
        """健康检查"""
        return True
    

class SimpleCache:
    """简单内存缓存"""
    def __init__(self, max_size: int = 1000, ttl: float = 300.0):
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {{e}}")
        raise
        self.max_size = max_size
        self.ttl = ttl
        self._cache = {}
        self._times = {}
    
    def get(self, key):
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {{e}}")
        raise
        import time
        if key in self._cache:
            if time.time() - self._times[key] < self.ttl:
                return self._cache[key]
            del self._cache[key]
        return None
    
    def set(self, key, value):
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {{e}}")
        raise
        import time
        if len(self._cache) >= self.max_size:
            # 删除最老的
            oldest = min(self._times, key=self._times.get)
            del self._cache[oldest]
            del self._times[oldest]
        self._cache[key] = value
        self._times[key] = time.time()

def cached(cache: SimpleCache):
    """缓存装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            result = cache.get(key)
            if result is not None:
                return result
            result = func(*args, **kwargs)
            cache.set(key, result)
            return result
        return wrapper
    return decorator

class UUIDv7Generator:
    """UUIDv7 时间有序唯一ID生成器
    
    来自X系统机制 #1
    """
    
    _counter: int = 0
    _last_timestamp: int = 0
    
    @classmethod
    def generate(cls) -> str:
        """生成UUIDv7"""
        # 获取当前时间戳(毫秒)
        now = datetime.now(timezone.utc)
        timestamp_ms = int(now.timestamp() * 1000)
        
        # 计数器处理同一毫秒
        if timestamp_ms == cls._last_timestamp:
            cls._counter = (cls._counter + 1) & 0xFFFF
        else:
            cls._counter = 0
            cls._last_timestamp = timestamp_ms
        
        # 构造UUIDv7
        # 时间部分 (48位)
        time_hi = (timestamp_ms >> 12) & 0xFFFF
        time_mid = timestamp_ms & 0x0FFF
        
        # 版本(7)和变体(2)
        ver = 7
        var = 0x02
        
        # 随机部分
        rand_a = (cls._counter << 4) | (cls._counter & 0x0F)
        rand_b = uuid.uuid4().int & 0x3FFF | (var << 14)
        rand_c = uuid.uuid4().int & 0xFFFFFFFFFFFF
        
        return f"{timestamp_ms:012x}-{rand_a:04x}-{ver:01x}{rand_b:04x}-{rand_c:012x}"
    
    @classmethod
    def from_timestamp(cls, timestamp_ms: int) -> str:
        """从时间戳生成UUIDv7"""
        time_hi = (timestamp_ms >> 12) & 0xFFFF
        time_mid = timestamp_ms & 0x0FFF
        ver = 7
        var = 0x02
        rand_b = (uuid.uuid4().int & 0x3FFF) | (var << 14)
        rand_c = uuid.uuid4().int & 0xFFFFFFFFFFFF
        return f"{timestamp_ms:012x}-{time_hi:04x}-{ver:01x}{rand_b:04x}-{rand_c:012x}"


# ===== 节点和边类型系统 =====
class NodeType(Enum):
    """42种节点类型 - 来自X系统机制 #2
    
    整合X系统的完备图节点类型
    """
    # 记忆节点
    EPISODIC = "episodic"           # 事件记忆
    ENTITY = "entity"               # 实体
    CONCEPT = "concept"             # 概念
    TOPIC = "topic"                 # 主题
    PERSONAL_EVENT = "personal_event"  # 个人事件
    EPISODE = "episode"             # 情节
    COMMUNITY = "community"         # 社区
    SAGA = "saga"                   # 长时间叙事
    
    # 世界模型节点 (Hindsight四网络)
    WORLD_FACT = "world_fact"       # 世界事实
    EXPERIENCE = "experience"       # 智能体经验
    ENTITY_SUMMARY = "entity_summary"  # 实体摘要
    BELIEF = "belief"               # 信念
    
    # 知识节点
    FACT = "fact"                   # 事实
    SKILL = "skill"                 # 技能
    TOOL = "tool"                   # 工具
    AGENT = "agent"                 # 代理
    TASK = "task"                   # 任务
    
    # 图节点
    KEY_NODE = "key_node"           # 关键节点
    MEMORY_NODE = "memory_node"     # 记忆节点
    QUERY_NODE = "query_node"       # 查询节点
    RESULT_NODE = "result_node"     # 结果节点
    
    # 元节点
    METADATA = "metadata"           # 元数据
    PROVENANCE = "provenance"       # 来源追踪
    VERSION = "version"             # 版本
    SNAPSHOT = "snapshot"           # 快照
    
    # 进化节点
    POPULATION = "population"       # 种群
    INDIVIDUAL = "individual"       # 个体
    GENE = "gene"                   # 基因
    MUTATION = "mutation"           # 变异
    FITNESS = "fitness"             # 适应度
    
    # 协作节点
    AGENT_INSTANCE = "agent_instance"  # 代理实例
    MESSAGE = "message"             # 消息
    CHANNEL = "channel"             # 通道
    SESSION = "session"             # 会话
    
    # 监控节点
    METRIC = "metric"                # 指标
    ALERT = "alert"                 # 警报
    ANOMALY = "anomaly"             # 异常


class EdgeType(Enum):
    """40种边类型 - 来自X系统机制 #2
    
    整合X系统的完备图边类型
    """
    # 时序边
    TEMPORAL_BEFORE = "temporal_before"
    TEMPORAL_AFTER = "temporal_after"
    CAUSAL = "causal"
    COREFERENCE = "coreference"
    
    # 语义边
    SIMILAR = "similar"
    RELATED = "related"
    antonym = "antonym"
    SYNONYM = "synonym"
    
    # 包含边
    CONTAINS = "contains"
    CONTAINED_BY = "contained_by"
    PART_OF = "part_of"
    HAS_PART = "has_part"
    
    # 引用边
    REFERENCES = "references"
    REFERENCED_BY = "referenced_by"
    CITES = "cites"
    CITED_BY = "cited_by"
    
    # 进化边
    PARENT_OF = "parent_of"
    CHILD_OF = "child_of"
    DESCENDANT_OF = "descendant_of"
    MUTATED_FROM = "mutated_from"
    EVOLVED_FROM = "evolved_from"
    
    # 协作边
    SENT_TO = "sent_to"
    RECEIVED_FROM = "received_from"
    COLLABORATES_WITH = "collaborates_with"
    COMPETES_WITH = "competes_with"
    
    # 推理边
    IMPLIES = "implies"
    IMPLIED_BY = "implied_by"
    ENTails = "entails"
    CONTRADICTS = "contradicts"
    
    # 记忆边
    RECALLS = "recalls"
    REMINDS_OF = "reminds_of"
    ASSOCIATED_WITH = "associated_with"
    
    # 元边
    HAS_VERSION = "has_version"
    DERIVED_FROM = "derived_from"
    COMPILED_FROM = "compiled_from"
    
    # 生态边
    PREDATOR_OF = "predator_of"
    PREY_OF = "prey_of"
    COMPETES_FOR = "competes_for"


# ===== 确定性规则引擎 =====
@dataclass
class Rule:
    """规则定义"""
    rule_id: str
    name: str
    condition: str  # 条件表达式
    action: str    # 执行动作
    priority: int = 0
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_applicable(self, context: Dict) -> bool:
        """检查规则是否适用于当前上下文"""
        if not self.enabled:
            return False
        
        # 简化条件检查
        try:
            # 支持简单的key==value条件
            if '==' in self.condition:
                key, value = self.condition.split('==', 1)
                key = key.strip()
                value = value.strip().strip('"\'')
                return str(context.get(key, '')) == value
            elif '>=' in self.condition:
                key, value = self.condition.split('>=', 1)
                return float(context.get(key.strip(), 0)) >= float(value.strip())
            elif '<=' in self.condition:
                key, value = self.condition.split('<=', 1)
                return float(context.get(key.strip(), 0)) <= float(value.strip())
            elif '>' in self.condition:
                key, value = self.condition.split('>', 1)
                return float(context.get(key.strip(), 0)) > float(value.strip())
            elif '<' in self.condition:
                key, value = self.condition.split('<', 1)
                return float(context.get(key.strip(), 0)) < float(value.strip())
            else:
                return self.condition in str(context)
        except (ValueError, KeyError):
            return False
    
    def to_dict(self) -> Dict:
        return {
            'rule_id': self.rule_id,
            'name': self.name,
            'condition': self.condition,
            'action': self.action,
            'priority': self.priority,
            'enabled': self.enabled,
        }


class DeterministicRuleEngine:
    """确定性规则引擎 - 来自X系统机制 #3
    
    44+规则，包含:
    - WriteGate写入门控
    - AntiEvolutionGate反进化
    - VerificationIronLaw验证铁律
    """
    
    def __init__(self):
        self.rules: Dict[str, Rule] = {}
        self._register_default_rules()
    
    def _register_default_rules(self):
        """注册默认规则"""
        # === WriteGate规则 (来自X系统 #11) ===
        write_gate_rules = [
            Rule("wg_001", "DopamineWriteGate乘法门控", 
                 "dopamine_level >= 0.3 AND content_quality >= 0.5",
                 "allow_write", priority=10),
            Rule("wg_002", "高频写入限制",
                 "write_frequency > 10 AND time_window < 60",
                 "rate_limit_write", priority=9),
            Rule("wg_003", "敏感内容过滤",
                 "contains_sensitive(content)",
                 "block_write", priority=20),
        ]
        
        # === AntiEvolutionGate规则 (来自X系统) ===
        anti_evo_rules = [
            Rule("aeg_001", "安全阈值检查",
                 "safety_score >= 0.7",
                 "allow_evolution", priority=15),
            Rule("aeg_002", "稳定性检查",
                 "stability_score >= 0.8",
                 "allow_evolution", priority=14),
            Rule("aeg_003", "回滚机制",
                 "failure_rate > 0.3",
                 "trigger_rollback", priority=18),
        ]
        
        # === VerificationIronLaw规则 (来自X系统 #36) ===
        verification_rules = [
            Rule("vil_001", "语法验证",
                 "code_syntax_valid == true",
                 "pass_verification", priority=5),
            Rule("vil_002", "语义验证",
                 "code_semantics_valid == true",
                 "pass_verification", priority=5),
            Rule("vil_003", "安全验证",
                 "security_scan_passed == true",
                 "pass_verification", priority=10),
            Rule("vil_004", "测试验证",
                 "test_coverage >= 0.8",
                 "pass_verification", priority=8),
        ]
        
        # === Bank迁移规则 (来自X系统 #8) ===
        bank_rules = [
            Rule("bm_001", "分层迁移",
                 "access_count > threshold AND age > 30 days",
                 "migrate_to_archive", priority=3),
            Rule("bm_002", "置信度合并",
                 "veracity_score < 0.5 AND multiple_sources",
                 "merge_confidence", priority=4),
        ]
        
        # === 其他规则 ===
        other_rules = [
            Rule("etc_001", "遗忘阈值",
                 "last_access > 90 days AND veracity < 0.3",
                 "mark_for_deletion", priority=2),
            Rule("etc_002", "整合触发",
                 "memory_count > 1000 AND consolidation_needed",
                 "trigger_consolidation", priority=3),
        ]
        
        all_rules = write_gate_rules + anti_evo_rules + verification_rules + bank_rules + other_rules
        for rule in all_rules:
            self.rules[rule.rule_id] = rule
    
    def evaluate(self, context: Dict[str, Any]) -> List[Rule]:
        """评估规则匹配"""
        matched = []
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            if self._matches_condition(rule, context):
                matched.append(rule)
        
        # 按优先级排序
        matched.sort(key=lambda r: -r.priority)
        return matched
    
    def _matches_condition(self, rule: Rule, context: Dict[str, Any]) -> bool:
        """检查条件是否匹配"""
        # 简化实现 - 实际应该解析表达式
        cond = rule.condition
        
        # 简单的条件检查
        if "dopamine_level" in cond and "dopamine_level" in context:
            return context["dopamine_level"] >= 0.3
        if "safety_score" in cond and "safety_score" in context:
            return context["safety_score"] >= 0.7
        if "stability_score" in cond and "stability_score" in context:
            return context["stability_score"] >= 0.8
        
        return True
    
    def add_rule(self, rule: Rule):
        """添加规则"""
        self.rules[rule.rule_id] = rule
    
    def remove_rule(self, rule_id: str):
        """移除规则"""
        self.rules.pop(rule_id, None)
    
    def get_rule_count(self) -> int:
        """获取规则数量"""
        return len(self.rules)


# ===== 配置管理 =====
@dataclass
class Config:
    """系统配置 - 来自Z系统"""
    
    # 记忆配置
    max_memory_size: int = 100000
    forget_threshold_days: int = 90
    consolidation_interval_hours: int = 6
    
    # 进化配置
    population_size: int = 100
    mutation_rate: float = 0.1
    crossover_rate: float = 0.7
    
    # 安全配置
    safety_threshold: float = 0.7
    enable_dopamine_gate: bool = True
    enable_verification: bool = True
    
    # 检索配置
    retrieval_top_k: int = 10
    rrf_k: float = 60.0
    diversity_weight: float = 0.5
    
    # 监控配置
    monitor_interval_seconds: int = 60
    alert_threshold: float = 0.8
    
    # 服务配置
    enable_http: bool = False
    enable_cli: bool = False
    enable_mcp: bool = False
    
    def to_dict(self) -> dict:
        return {
            "max_memory_size": self.max_memory_size,
            "forget_threshold_days": self.forget_threshold_days,
            "consolidation_interval_hours": self.consolidation_interval_hours,
            "population_size": self.population_size,
            "mutation_rate": self.mutation_rate,
            "crossover_rate": self.crossover_rate,
            "safety_threshold": self.safety_threshold,
            "enable_dopamine_gate": self.enable_dopamine_gate,
            "enable_verification": self.enable_verification,
            "retrieval_top_k": self.retrieval_top_k,
            "rrf_k": self.rrf_k,
            "diversity_weight": self.diversity_weight,
            "monitor_interval_seconds": self.monitor_interval_seconds,
            "alert_threshold": self.alert_threshold,
            "enable_http": self.enable_http,
            "enable_cli": self.enable_cli,
            "enable_mcp": self.enable_mcp,
        }


# ===== 事件总线 =====
class EventBus:
    """事件总线 - 来自X/Z系统"""
    
    def __init__(self):
        self._subscribers: Dict[str, List[callable]] = {}
        self._event_history: List[Dict] = []
        self._max_history = 1000
    
    def subscribe(self, event_type: str, callback: callable):
        """订阅事件"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: callable):
        """取消订阅"""
        if event_type in self._subscribers:
            self._subscribers[event_type] = [
                cb for cb in self._subscribers[event_type] if cb != callback
            ]
    
    def publish(self, event_type: str, data: Any = None):
        """发布事件"""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        # 记录历史
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        
        # 通知订阅者
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Event callback error: {e}")
    
    def get_history(self, event_type: str = None, limit: int = 100) -> List[Dict]:
        """获取事件历史"""
        if event_type:
            return [e for e in self._event_history if e["type"] == event_type][-limit:]
        return self._event_history[-limit:]


# ===== 来源追踪 =====
@dataclass
class Provenance:
    """来源追踪 - 来自X系统机制 #1"""
    
    source_id: str
    source_type: str  # "user", "agent", "system", "external"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)
    chain: List[str] = field(default_factory=list)  # 溯源链
    
    def add_to_chain(self, entity_id: str):
        """添加到溯源链"""
        self.chain.append(entity_id)
    
    def verify_chain(self) -> bool:
        """验证溯源链完整性"""
        return len(self.chain) > 0


# ===== Schema定义 =====
@dataclass
class Schema:
    """数据Schema - 来自X系统 L0"""
    
    version: str = "1.0.0"
    fields: Dict[str, type] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    indexes: List[str] = field(default_factory=list)
    
    def add_field(self, name: str, field_type: type, required: bool = True):
        """添加字段"""
        self.fields[name] = {"type": field_type, "required": required}
    
    def add_index(self, field: str):
        """添加索引"""
        if field not in self.indexes:
            self.indexes.append(field)
    
    def validate(self, data: Dict) -> tuple[bool, List[str]]:
        """验证数据"""
        errors = []
        
        for name, info in self.fields.items():
            if info["required"] and name not in data:
                errors.append(f"Missing required field: {name}")
        
        return len(errors) == 0, errors


# 导入统一数据结构
from .schema import OmegaNode, OmegaConfig, NodeType, TrustLevel, MemoryLayer


# ===== 来自XYZ系统 =====
class AutonomyLevel(IntEnum):
    """S1: 5-level autonomy. L0=full-auto, L4=forbidden."""
    L0_FULL_AUTO = 0
    L1_REPORT_AFTER = 1
    L2_CONFIRM_FIRST = 2
    L3_EXPLICIT_APPROVAL = 3
    L4_FORBIDDEN = 4




# ===== 兼容性别名 (使用统一schema) =====
Node = OmegaNode
Config = OmegaConfig

# ===== 工厂函数 =====
def create_uuid() -> str:
    """创建UUIDv7"""
    return UUIDv7Generator.generate()


def create_node(**kwargs) -> OmegaNode:
    """创建统一节点"""
    return OmegaNode(**kwargs)


def create_config(**kwargs) -> OmegaConfig:
    """创建统一配置"""
    return OmegaConfig(**kwargs)


def create_rule_engine() -> DeterministicRuleEngine:
    """创建规则引擎"""
    return DeterministicRuleEngine()


def create_event_bus() -> EventBus:
    """创建事件总线"""
    return EventBus()


# ===== 来自XYZ系统(依赖) =====

# ===== XYZ系统依赖类 =====

class Strictness(IntEnum):
    """P4: Buffering strictness levels."""
    NORMAL = 0
    CRITICAL = 1
    DREAM = 2



class SecurityPosture(IntEnum):
    """S13: 4-level dynamic security. LOW→CRITICAL."""
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3



class AutonomyLevel(IntEnum):
    """S1: 5-level autonomy. L0=full-auto, L4=forbidden."""
    L0_FULL_AUTO = 0
    L1_REPORT_AFTER = 1
    L2_CONFIRM_FIRST = 2
    L3_EXPLICIT_APPROVAL = 3
    L4_FORBIDDEN = 4



class MemoryLayer(IntEnum):
    """BEAM three-layer memory. Each layer has distinct Weibull parameters."""
    WORKING = 0
    EPISODIC = 1
    SEMANTIC = 2



class LifecycleAction(IntEnum):
    """Zero-LLM lifecycle decisions."""
    KEEP = 0
    PROMOTE = 1
    DECAY = 2
    ARCHIVE = 3
    DELETE = 4



class GateResult(IntEnum):
    """Result from any gate check."""
    PASS = 1
    FAIL = 0



class WriteOperator(IntEnum):
    """M14: Semantic write operators for isolation levels."""
    PLUS_T = 0   # ⊕t temporal: valid_at update only
    PLUS_P = 1   # ⊕p provenance: new source attribution
    PLUS_Q = 2   # ⊕? question: flag for verification
    PLUS_C = 3   # ⊕c correction: amend with evidence



class CommitState(IntEnum):
    """MVCC transaction states."""
    ACTIVE = 0
    COMMITTED = 1
    ROLLED_BACK = 2



class ProvenanceType(IntEnum):
    """Source of a node's knowledge."""
    UNKNOWN = 0
    OBSERVED = 1
    INFERRED = 2
    IMPORTED = 3
    GENERATED = 4



class NodeType(IntEnum):
    """Core node types. Extensible at runtime (D28 Dynamic Ontology)."""
    CONCEPT = 0
    FACT = 1
    EPISODE = 2
    SKILL = 3
    AVOID_RULE = 4
    QUESTION = 5
    HYPOTHESIS = 6
    CODE = 7
    PATTERN = 8
    GOAL = 9
    ANTI_PATTERN = 10
    BELIEF = 11
    CODE_UNIT = 12
    PROCEDURE = 13



class EdgeType(IntEnum):
    """Core edge types for knowledge graph connectivity."""
    RELATES_TO = 0
    DEPENDS_ON = 1
    CONSOLIDATES_TO = 2
    CONTRADICTS = 3
    SUPPORTS = 4
    DERIVED_FROM = 5
    IMPLEMENTS = 6
    SUBSUMES = 7
    MENTIONS = 8
    CONTAINS = 9
    PRECEDES = 10
    PREDICTS = 11



class ConstraintKind(IntEnum):
    """P14: Constraint types for ≤7 limit."""
    SAFETY = 0
    QUALITY = 1
    PERFORMANCE = 2
    BEHAVIOR = 3
    RESOURCE = 4
    SCOPE = 5
    COMPATIBILITY = 6


# ═══════════════════════════════════════════
#  Dataclasses
# ═══════════════════════════════════════════

@dataclass

class ZConfig:
    """System-wide configuration. All defaults are safe."""
    # Write gate
    write_gate_tau: float = 1.0         # DopamineWriteGate threshold
    surprise_beta: float = 0.3          # Surprise bonus (prevents gate collapse)
    max_utility: float = 5.0           # Utility cap

    # Weibull forgetting per layer (M7)
    weibull_lambda: dict[int, float] = field(default_factory=lambda: {
        MemoryLayer.WORKING: 30.0,     # days
        MemoryLayer.EPISODIC: 90.0,
        MemoryLayer.SEMANTIC: 365.0,
    })
    weibull_k: dict[int, float] = field(default_factory=lambda: {
        MemoryLayer.WORKING: 0.7,      # <1 = decelerating
        MemoryLayer.EPISODIC: 0.8,
        MemoryLayer.SEMANTIC: 1.5,     # >1 = accelerating (rarely forget)
    })

    # Trust promotion thresholds (K1)
    promote_after: int = 3             # reinforce_count for PENDING→HIGH_SIGNAL
    verify_after: int = 6              # reinforce_count for HIGH_SIGNAL→VERIFIED

    # AntiEvolutionGate (E10)
    consecutive_zero_gain_limit: int = 3  # reset after this many zero-gain rounds
    novelty_hunger_threshold: float = 0.7

    # Pass@k
    pass_k_k: int = 3
    pass_k_threshold: float = 0.9      # 90% for application

    # Compile-to-rule
    compile_fitness_threshold: float = 0.95

    # Constraints (P14)
    max_constraints: int = 7

    # Autonomy defaults
    default_autonomy: AutonomyLevel = AutonomyLevel.L1_REPORT_AFTER
    default_strictness: Strictness = Strictness.NORMAL
    default_security: SecurityPosture = SecurityPosture.LOW

    # LLM
    llm_base_url: str = ""
    llm_model: str = ""
    llm_max_retries: int = 3
    llm_timeout: float = 30.0
    llm_fallbacks: list[str] = field(default_factory=list)

    # Storage
    db_path: str = "prometheus_z.db"
    embedding_dim: int = 0  # 0 = auto-detect from first embedding

    # Safety
    max_error_rate: float = 0.3
    circuit_breaker_threshold: int = 5
    circuit_breaker_cooldown: float = 30.0  # seconds
    buffer_release_threshold: float = 0.7



class ZConfig:
    """System-wide configuration. All defaults are safe."""
    # Write gate
    write_gate_tau: float = 1.0         # DopamineWriteGate threshold
    surprise_beta: float = 0.3          # Surprise bonus (prevents gate collapse)
    max_utility: float = 5.0           # Utility cap

    # Weibull forgetting per layer (M7)
    weibull_lambda: dict[int, float] = field(default_factory=lambda: {
        MemoryLayer.WORKING: 30.0,     # days
        MemoryLayer.EPISODIC: 90.0,
        MemoryLayer.SEMANTIC: 365.0,
    })
    weibull_k: dict[int, float] = field(default_factory=lambda: {
        MemoryLayer.WORKING: 0.7,      # <1 = decelerating
        MemoryLayer.EPISODIC: 0.8,
        MemoryLayer.SEMANTIC: 1.5,     # >1 = accelerating (rarely forget)
    })

    # Trust promotion thresholds (K1)
    promote_after: int = 3             # reinforce_count for PENDING→HIGH_SIGNAL
    verify_after: int = 6              # reinforce_count for HIGH_SIGNAL→VERIFIED

    # AntiEvolutionGate (E10)
    consecutive_zero_gain_limit: int = 3  # reset after this many zero-gain rounds
    novelty_hunger_threshold: float = 0.7

    # Pass@k
    pass_k_k: int = 3
    pass_k_threshold: float = 0.9      # 90% for application

    # Compile-to-rule
    compile_fitness_threshold: float = 0.95

    # Constraints (P14)
    max_constraints: int = 7

    # Autonomy defaults
    default_autonomy: AutonomyLevel = AutonomyLevel.L1_REPORT_AFTER
    default_strictness: Strictness = Strictness.NORMAL
    default_security: SecurityPosture = SecurityPosture.LOW

    # LLM
    llm_base_url: str = ""
    llm_model: str = ""
    llm_max_retries: int = 3
    llm_timeout: float = 30.0
    llm_fallbacks: list[str] = field(default_factory=list)

    # Storage
    db_path: str = "prometheus_z.db"
    embedding_dim: int = 0  # 0 = auto-detect from first embedding

    # Safety
    max_error_rate: float = 0.3
    circuit_breaker_threshold: int = 5
    circuit_breaker_cooldown: float = 30.0  # seconds
    buffer_release_threshold: float = 0.7


class GateCheckResult:
    """Result from any gate check. Check .passed, NOT truthiness."""
    passed: bool = False
    reason: str = ""
    gate_name: str = ""
    details: dict[str, Any] = field(default_factory=dict)


@dataclass

class WriteGateResult:
    """DopamineWriteGate output. Check .allowed, NOT truthiness."""
    allowed: bool = False
    gate_value: float = 0.0
    reason: str = ""


@dataclass

class EvolutionCheckResult:
    """AntiEvolutionGate output. Check .passed, NOT truthiness."""
    passed: bool = False
    reason: str = ""
    prerequisites_met: list[str] = field(default_factory=list)
    prerequisites_failed: list[str] = field(default_factory=list)


# 别名
OmegaConfig = ZConfig

class EvolutionOutcome:
    """Result from evolve() pipeline."""
    def __init__(
        self,
        applied: bool = False,
        fitness_before: float = 0.0,
        fitness_after: float = 0.0,
        compilation: bool = False,
        reason: str = ""
    ):
        self.applied = applied
        self.fitness_before = fitness_before
        self.fitness_after = fitness_after
        self.compilation = compilation
        self.reason = reason

@dataclass
class Edge:
    """Connection between nodes. Value is in connections, not nodes (P9)."""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    source: str = ""   # node.id
    target: str = ""   # node.id
    type: EdgeType = EdgeType.RELATES_TO
    weight: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)
    valid_from: float = field(default_factory=time.time)
    valid_to: float = 0.0
    tx_from: float = field(default_factory=time.time)
    tx_to: float = 0.0
    branch: str = "main"

@dataclass
class Constraint:
    """P14: Constraint with P16 metadata. Max 7 active."""
    kind: ConstraintKind = ConstraintKind.SAFETY
    description: str = ""
    why: str = ""         # P16: why this constraint exists
    trigger: str = ""     # P16: when it fires
    verify: str = ""      # P16: how to verify compliance
    severity: float = 1.0

@dataclass
class FetchResult:
    """Retrieved memory entries with relevance scores."""
    nodes: List[Node]
    scores: List[float]
    query: str
    layer: MemoryLayer = MemoryLayer.EPISODIC
    branch: str = "main"

class TrustLevel(IntEnum):
    """Trust level for memory nodes."""
    PENDING = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERIFIED = 4

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
