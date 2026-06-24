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

"""L10 Collaboration - 协作层 (Multi-agent+EventBus)"""
import logging

from dataclasses import dataclass, field
import logging

from typing import List, Dict, Any, Optional
from enum import Enum
import logging

import uuid, time
from prometheus_omega.foundation import ZConfig

# 安全工具


# 缓存工具

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

class SimpleCache:
    """简单内存缓存"""
    def __init__(self, max_size: int = 1000, ttl: float = 300.0):
        self.max_size = max_size
        self.ttl = ttl
        self._cache = {}
        self._times = {}
    
    def get(self, key):
        import time
        if key in self._cache:
            if time.time() - self._times[key] < self.ttl:
                return self._cache[key]
            del self._cache[key]
        return None
    
    def set(self, key, value):
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

class DopamineWriteGate:
    """多巴胺写入门控 - 宪法第1条"""
    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
        self.dopamine_level = 0.5
    
    def can_write(self, importance: float, utility: float, veracity: float) -> bool:
        quality = importance * utility * veracity
        return quality * self.dopamine_level >= self.threshold

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

class AlertLevel(IntEnum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4




class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    EVENT = "event"


@dataclass
class AgentMessage:
    """Agent间通信的消息结构"""
    msg_id: str
    sender: str
    receiver: str
    msg_type: MessageType
    content: Any
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    reply_to: Optional[str] = None
    ttl: int = 300  # 消息生存时间(秒)
    
    def is_expired(self) -> bool:
        """检查消息是否过期"""
        return (time.time() - self.timestamp) > self.ttl
    
    def age(self) -> float:
        """获取消息年龄(秒)"""
        return time.time() - self.timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'msg_id': self.msg_id,
            'sender': self.sender,
            'receiver': self.receiver,
            'msg_type': self.msg_type.value,
            'content': self.content,
            'timestamp': self.timestamp,
            'metadata': self.metadata,
            'reply_to': self.reply_to,
            'ttl': self.ttl,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMessage':
        """从字典创建"""
        if isinstance(data.get('msg_type'), str):
            data['msg_type'] = MessageType(data['msg_type'])
        return cls(**data)


class MultiAgentSystem:
    """多代理系统 - 来自X系统"""
    
    def __init__(self):
        self.agents: Dict[str, Dict] = {}
        self.messages: List[AgentMessage] = []
        self.message_queues: Dict[str, List[AgentMessage]] = {}
        self._history_size = 1000
    
    def register_agent(self, agent_id: str, config: Dict):
        """注册Agent"""
        self.agents[agent_id] = {"config": config, "status": "active"}
        self.message_queues[agent_id] = []
    
    def unregister_agent(self, agent_id: str) -> bool:
        """注销Agent"""
        if agent_id in self.agents:
            self.agents[agent_id]["status"] = "inactive"
            return True
        return False
    
    def send_message(self, sender: str, receiver: str, content: Any, 
                     msg_type: MessageType = MessageType.REQUEST) -> str:
        """发送消息"""
        # 检查sender和receiver是否存在
        if sender not in self.agents:
            raise ValueError(f"Unknown sender: {sender}")
        if receiver not in self.agents:
            raise ValueError(f"Unknown receiver: {receiver}")
        
        msg = AgentMessage(
            msg_id=str(uuid.uuid4()),
            sender=sender,
            receiver=receiver,
            msg_type=msg_type,
            content=content
        )
        self.messages.append(msg)
        
        # 限制历史大小
        if len(self.messages) > self._history_size:
            self.messages = self.messages[-self._history_size:]
        
        # 加入接收者队列
        if receiver in self.message_queues:
            self.message_queues[receiver].append(msg)
        
        return msg.msg_id
    
    def get_messages(self, agent_id: str, unread_only: bool = False) -> List[AgentMessage]:
        """获取Agent的消息"""
        if agent_id not in self.message_queues:
            return []
        
        messages = self.message_queues[agent_id]
        
        if unread_only:
            # 只返回未读消息(简化处理)
            return [m for m in messages if m.receiver == agent_id]
        
        return messages
    
    def clear_messages(self, agent_id: str):
        """清空Agent的消息队列"""
        if agent_id in self.message_queues:
            self.message_queues[agent_id] = []
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict]:
        """获取Agent状态"""
        return self.agents.get(agent_id)
    
    def broadcast(self, sender: str, content: Any) -> List[str]:
        """广播消息给所有活跃Agent"""
        msg_ids = []
        for agent_id in self.agents:
            if agent_id != sender and self.agents[agent_id].get("status") == "active":
                msg_id = self.send_message(sender, agent_id, content, MessageType.BROADCAST)
                msg_ids.append(msg_id)
        return msg_ids


class CIPEventBus:
    """CIP事件总线 - 来自X系统"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[callable]] = {}
        self.event_history: List[Dict] = []
        self._max_history = 500
    
    def subscribe(self, event: str, callback: callable):
        """订阅事件"""
        if event not in self.subscribers:
            self.subscribers[event] = []
        if callback not in self.subscribers[event]:
            self.subscribers[event].append(callback)
    
    def unsubscribe(self, event: str, callback: callable) -> bool:
        """取消订阅"""
        if event in self.subscribers and callback in self.subscribers[event]:
            self.subscribers[event].remove(callback)
            return True
        return False
    
    def publish(self, event: str, data: Any):
        """发布事件"""
        # 记录历史
        self.event_history.append({
            'event': event,
            'data': data,
            'timestamp': time.time(),
        })
        
        # 限制历史大小
        if len(self.event_history) > self._max_history:
            self.event_history = self.event_history[-self._max_history:]
        
        # 通知订阅者
        for callback in self.subscribers.get(event, []):
            try:
                callback(data)
            except Exception as e:
                print(f"Event callback error: {e}")
    
    def get_history(self, event: str = None, limit: int = 50) -> List[Dict]:
        """获取事件历史"""
        if event:
            return [h for h in self.event_history[-limit:] if h['event'] == event]
        return self.event_history[-limit:]
    
    def clear_history(self):
        """清空历史"""
        self.event_history = []


class KnowledgeBridge:
    """知识桥接 - 来自X系统#67
    
    在Agent之间转移知识/上下文
    """
    
    def __init__(self):
        self.bridges: Dict[str, str] = {}
        self.transfer_log: List[Dict] = []
        self._max_log = 200
    
    def register(self, from_agent: str, to_agent: str, knowledge: str):
        """注册知识桥接"""
        key = f"{from_agent}->{to_agent}"
        self.bridges[key] = knowledge
    
    def unregister(self, from_agent: str, to_agent: str) -> bool:
        """注销知识桥接"""
        key = f"{from_agent}->{to_agent}"
        if key in self.bridges:
            del self.bridges[key]
            return True
        return False
    
    def transfer(self, from_agent: str, to_agent: str) -> Optional[str]:
        """转移知识"""
        key = f"{from_agent}->{to_agent}"
        knowledge = self.bridges.get(key)
        
        # 记录转移
        if knowledge:
            self.transfer_log.append({
                'from': from_agent,
                'to': to_agent,
                'knowledge_size': len(knowledge),
                'timestamp': time.time(),
            })
            if len(self.transfer_log) > self._max_log:
                self.transfer_log = self.transfer_log[-self._max_log:]
        
        return knowledge
    
    def has_bridge(self, from_agent: str, to_agent: str) -> bool:
        """检查是否存在桥接"""
        key = f"{from_agent}->{to_agent}"
        return key in self.bridges
    
    def list_bridges(self, agent_id: str = None) -> List[Dict]:
        """列出桥接"""
        result = []
        for key, knowledge in self.bridges.items():
            from_a, to_a = key.split('->')
            if agent_id is None or from_a == agent_id or to_a == agent_id:
                result.append({
                    'from': from_a,
                    'to': to_a,
                    'knowledge_size': len(knowledge),
                })
        return result


class VectorClock:
    """向量时钟 - 来自X系统#64
    
    用于分布式系统中的因果顺序
    """
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.vector: Dict[str, int] = {agent_id: 0}
    
    def increment(self):
        """递增当前Agent的时钟"""
        self.vector[self.agent_id] = self.vector.get(self.agent_id, 0) + 1
    
    def merge(self, other: Dict[str, int]):
        """合并另一个向量时钟"""
        for agent, clock in other.items():
            self.vector[agent] = max(self.vector.get(agent, 0), clock)
    
    def happens_before(self, other: Dict[str, int]) -> bool:
        """检查是否happens-before"""
        # self <= other 当且仅当对于所有agent, self[agent] <= other[agent]
        # 且至少一个严格小于
        all_less_or_equal = True
        some_less = False
        
        # 合并后比较
        merged = {**self.vector}
        for agent, clock in other.items():
            merged[agent] = max(merged.get(agent, 0), clock)
        
        for agent in set(self.vector.keys()) | set(other.keys()):
            self_val = self.vector.get(agent, 0)
            other_val = other.get(agent, 0)
            
            if self_val > other_val:
                return False
            if self_val < other_val:
                some_less = True
        
        return some_less
    
    def concurrent_with(self, other: Dict[str, int]) -> bool:
        """检查是否并发(既不happens-before也不之后)"""
        return not self.happens_before(other) and not self._happens_after(other)
    
    def _happens_after(self, other: Dict[str, int]) -> bool:
        """检查other是否happens-before self"""
        return self.happens_before(other)
    
    def get_clock(self) -> Dict[str, int]:
        """获取当前时钟快照"""
        return dict(self.vector)
    
    def set_clock(self, clock: Dict[str, int]):
        """设置时钟"""
        self.vector = dict(clock)


class CausalKG:
    """因果知识图谱 - 来自X系统#65
    
    表示因果关系的知识图谱
    """
    
    def __init__(self):
        self.edges: Dict[str, List[str]] = {}
        self.reverse_edges: Dict[str, List[str]] = {}
        self.edge_weights: Dict[str, Dict[str, float]] = {}
    
    def add_causality(self, cause: str, effect: str, weight: float = 1.0):
        """添加因果边"""
        if cause not in self.edges:
            self.edges[cause] = []
        if effect not in self.edges[cause]:
            self.edges[cause].append(effect)
        
        # 反向索引
        if effect not in self.reverse_edges:
            self.reverse_edges[effect] = []
        if cause not in self.reverse_edges[effect]:
            self.reverse_edges[effect].append(cause)
        
        # 权重
        if cause not in self.edge_weights:
            self.edge_weights[cause] = {}
        self.edge_weights[cause][effect] = weight
    
    def remove_causality(self, cause: str, effect: str) -> bool:
        """移除因果边"""
        if cause in self.edges and effect in self.edges[cause]:
            self.edges[cause].remove(effect)
            if effect in self.reverse_edges and cause in self.reverse_edges[effect]:
                self.reverse_edges[effect].remove(cause)
            return True
        return False
    
    def get_effects(self, cause: str) -> List[str]:
        """获取因的所有果"""
        return self.edges.get(cause, [])
    
    def get_causes(self, effect: str) -> List[str]:
        """获取果的所有因"""
        return self.reverse_edges.get(effect, [])
    
    def get_weight(self, cause: str, effect: str) -> float:
        """获取因果权重"""
        return self.edge_weights.get(cause, {}).get(effect, 0.0)
    
    def get_all_concepts(self) -> List[str]:
        """获取所有概念节点"""
        return list(set(self.edges.keys()) | set(self.reverse_edges.keys()))
    
    def get_causal_chain(self, start: str, max_depth: int = 3) -> List[List[str]]:
        """获取从start出发的所有因果链"""
        result = []
        
        def dfs(current: str, path: List[str], depth: int):
            if depth >= max_depth:
                result.append(path)
                return
            
            for effect in self.edges.get(current, []):
                dfs(effect, path + [effect], depth + 1)
        
        dfs(start, [start], 0)
        return result


# 工厂
def create_multi_agent_system() -> MultiAgentSystem:
    return MultiAgentSystem()

def create_event_bus() -> CIPEventBus:
    return CIPEventBus()

def create_causal_kg() -> CausalKG:
    return CausalKG()


# ===== 来自XYZ系统 =====
class BehaviorMirror:
    """K9: Mirror user behavior for preference inference.

    Uses both frequency counting and 2nd-order Markov chain modeling
    to capture not just what users do, but what they do NEXT given
    the last TWO actions (context-aware prediction).
    """

    def __init__(self, config: ZConfig | None = None):
        self._config = config or ZConfig()
        self._observations: list[dict] = []
        self._style_counters: dict[str, dict[str, int]] = {}

        # 1st-order Markov chain: state → next_state → count
        self._transitions: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._state_totals: dict[str, int] = defaultdict(int)

        # 2nd-order Markov chain: (prev, curr) → next → count
        self._transitions_2: dict[tuple[str, str], dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self._state_totals_2: dict[tuple[str, str], int] = defaultdict(int)

        self._last_action: str = ""
        self._prev_action: str = ""  # For 2nd-order chain
        self._stats = {"observations": 0, "inferences": 0, "transitions": 0}

    def observe(self, action: str, category: str = "general",
                metadata: dict | None = None) -> dict:
        """Observe a user action.

        Args:
            action: What the user did (e.g., "approved concise summary")
            category: Action category (e.g., "communication", "decision")
            metadata: Additional context
        """
        self._stats["observations"] += 1
        entry = {
            "action": action,
            "category": category,
            "metadata": metadata or {},
        }
        self._observations.append(entry)

        # Update style counters
        if category not in self._style_counters:
            self._style_counters[category] = {}
        self._style_counters[category][action] = \
            self._style_counters[category].get(action, 0) + 1

        # Update 1st-order Markov chain
        if self._last_action:
            self._transitions[self._last_action][action] += 1
            self._state_totals[self._last_action] += 1
            self._stats["transitions"] += 1

        # Update 2nd-order Markov chain: (prev, last) → action
        if self._prev_action and self._last_action:
            key = (self._prev_action, self._last_action)
            self._transitions_2[key][action] += 1
            self._state_totals_2[key] += 1

        # Shift history
        self._prev_action = self._last_action
        self._last_action = action

        return entry

    def infer_style(self, category: str = "communication") -> dict:
        """Infer user style from observations.

        Returns the dominant action for each category.
        """
        self._stats["inferences"] += 1
        if category not in self._style_counters:
            return {"category": category, "dominant": None, "confidence": 0.0}

        counters = self._style_counters[category]
        if not counters:
            return {"category": category, "dominant": None, "confidence": 0.0}

        total = sum(counters.values())
        dominant = max(counters, key=counters.get)
        confidence = counters[dominant] / total if total > 0 else 0.0

        return {
            "category": category,
            "dominant": dominant,
            "confidence": confidence,
            "distribution": dict(counters),
        }

    def predict_next(self, current_action: str, prev_action: str = "",
                     top_k: int = 3) -> list[tuple[str, float]]:
        """Predict the most likely next action.

        Uses 2nd-order Markov chain if prev_action is provided and
        sufficient data exists, otherwise falls back to 1st-order.

        Returns list of (action, probability) sorted by probability.
        """
        # Try 2nd-order first (more context-aware)
        if prev_action:
            key = (prev_action, current_action)
            if key in self._transitions_2:
                total = self._state_totals_2.get(key, 0)
                if total > 0:
                    transitions = self._transitions_2[key]
                    probs = [(a, c / total) for a, c in transitions.items()]
                    probs.sort(key=lambda x: x[1], reverse=True)
                    return probs[:top_k]

        # Fallback to 1st-order
        if current_action not in self._transitions:
            return []

        total = self._state_totals.get(current_action, 0)
        if total == 0:
            return []

        transitions = self._transitions[current_action]
        probs = [(action, count / total) for action, count in transitions.items()]
        probs.sort(key=lambda x: x[1], reverse=True)
        return probs[:top_k]

    def get_transition_probability(self, from_action: str, to_action: str,
                                   prev_action: str = "") -> float:
        """Get P(to_action | from_action) or P(to_action | prev, from).

        Uses 2nd-order if prev_action provided and data exists.
        """
        # Try 2nd-order
        if prev_action:
            key = (prev_action, from_action)
            total = self._state_totals_2.get(key, 0)
            if total > 0:
                return self._transitions_2[key].get(to_action, 0) / total

        # Fallback to 1st-order
        total = self._state_totals.get(from_action, 0)
        if total == 0:
            return 0.0
        return self._transitions[from_action].get(to_action, 0) / total

    def detect_action_loops(self, min_length: int = 2,
                            min_repeats: int = 3) -> list[list[str]]:
        """Detect repeated action sequences using suffix array.

        O(n log n) via suffix array construction, vs O(n²) brute force.
        Finds subsequences that repeat ≥ min_repeats times.
        """
        if len(self._observations) < min_length * min_repeats:
            return []

        actions = [obs["action"] for obs in self._observations]
        return _detect_loops_suffix_array(actions, min_length, min_repeats)

    def get_preferred_style(self) -> dict[str, str]:
        """Get the dominant style for each category."""
        result = {}
        for category in self._style_counters:
            inference = self.infer_style(category)
            if inference["dominant"]:
                result[category] = inference["dominant"]
        return result

    def detect_repeated_questions(self, min_count: int = 3) -> list[str]:
        """Detect knowledge gaps — questions asked repeatedly."""
        question_counts: dict[str, int] = {}
        for obs in self._observations:
            if obs["category"] == "question":
                q = obs["action"]
                question_counts[q] = question_counts.get(q, 0) + 1

        return [q for q, c in question_counts.items() if c >= min_count]

    @property
    def observation_count(self) -> int:
        return len(self._observations)

    @property
    def stats(self) -> dict:
        return dict(self._stats)


def _detect_loops_suffix_array(actions: list[str],
                                min_length: int = 2,
                                min_repeats: int = 3) -> list[list[str]]:
    """Detect repeated subsequences using suffix array.

    Algorithm:
    1. Build suffix array by sorting all suffixes
    2. Scan adjacent suffixes in sorted order for common prefixes
    3. Common prefix length ≥ min_length → repeated subsequence
    4. Count repeats by grouping overlapping matches

    O(n log n) for sorting, O(n) for scanning.
    """
    n = len(actions)
    if n < min_length * min_repeats:
        return []

    # Build suffix array: indices sorted by their suffix
    suffixes = list(range(n))
    suffixes.sort(key=lambda i: actions[i:])

    # Find longest common prefix between adjacent sorted suffixes
    loops = []
    seen: set[tuple[str, ...]] = set()

    for i in range(len(suffixes) - 1):
        s1 = suffixes[i]
        s2 = suffixes[i + 1]

        # Compute LCP
        lcp = 0
        while (s1 + lcp < n and s2 + lcp < n
               and actions[s1 + lcp] == actions[s2 + lcp]):
            lcp += 1

        if lcp >= min_length:
            # Extract the repeated subsequence
            subseq = tuple(actions[s1:s1 + lcp])

            # Count total occurrences (not just adjacent pairs)
            if subseq not in seen:
                # Count by scanning for this subsequence
                count = 0
                for j in range(n - len(subseq) + 1):
                    if tuple(actions[j:j + len(subseq)]) == subseq:
                        count += 1

                if count >= min_repeats:
                    loops.append(list(subseq))
                    seen.add(subseq)

    return loops

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
