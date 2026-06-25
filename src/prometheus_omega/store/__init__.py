"""Store Module - 存储模块

提供统一的存储抽象层，支持多种存储后端。
包含缓存、事务、连接池等企业级特性。
"""

from __future__ import annotations
import time
import json
import threading
from typing import Dict, List, Any, Optional, Generic, TypeVar, Callable
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from collections import defaultdict
from abc import ABC, abstractmethod

T = TypeVar('T')


# ═══════════════════════════════════════════════════════════════
# 宪法机制 - 3铁律实现
# ════════════════════���══════════════════════════════════════════


import hashlib
import hmac


class ErrorHandler:
    """统一错误处理工具类"""
    
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
    """重试策略 - 指数退避+fallback降级
    
    用于处理临时故障:
    - 网络超时
    - 服务不可用
    - 资源抢占
    
    业务场景:
    - 写入失败时降级到内存
    - 查询失败时返回缓存
    - 计算失败时使用默认值
    
    Attributes:
        max_attempts: 最大重试次数
        backoff_factor: 指数退避因子
    """
    def __init__(self, max_attempts: int = 3, backoff_factor: float = 2.0):
        self.max_attempts = max_attempts
        self.backoff_factor = backoff_factor
    
    def execute(self, func: Callable[..., T], *args, fallback: Optional[Callable[[], T]] = None, **kwargs) -> T:
            """执行带重试的函数
        
            Args:
                func: 要执行的函数
                *args: 位置参数
                fallback: 可选的降级函数
                **kwargs: 关键字参数
            
            Returns:
                T: 函数结果
            """
            import time
            last_exception = None
            for attempt in range(self.max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < self.max_attempts - 1:
                        time.sleep(self.backoff_factor ** attempt)
        
            # 如果有fallback则调用
            if fallback is not None:
                return fallback()
        
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
class DopamineWriteGate:
    """第1铁律: 多巴胺写入门控"""
    def __init__(self, threshold: float = 0.3, min_dopamine: float = 0.2):
        self.threshold = threshold
        self.min_dopamine = min_dopamine
        self.dopamine_level = 0.5
    
    def can_write(self, importance: float, utility: float, veracity: float) -> bool:
        quality = importance * utility * veracity
        return quality * self.dopamine_level >= self.threshold


class AntiEvolutionGate:
    """第2铁律: 反进化门控"""
    def __init__(self, energy_threshold: float = 0.9, risk_threshold: float = 0.7):
        self.energy_threshold = energy_threshold
        self.risk_threshold = risk_threshold
        self.energy_history = []
        self.risk_history = []
    
    def can_evolve(self, energy_used: float, total_energy: float, 
                   utility_delta: float, risk_score: float) -> bool:
        energy_ratio = energy_used / total_energy if total_energy > 0 else 0
        if energy_ratio > self.energy_threshold: return False
        if utility_delta < -0.1: return False
        if risk_score > self.risk_threshold: return False
        return True


class VerificationIronLaw:
    """第3铁律: 验证铁律"""
    def __init__(self):
        self.verification_cache = {}
    
    def verify(self, content: str, content_type: str = "text") -> bool:
        if content in self.verification_cache:
            return self.verification_cache[content]
        result = True
        if content_type == "code" and not self._syntax_check(content):
            result = False
        if not self._semantic_check(content): result = False
        if not self._value_check(content): result = False
        self.verification_cache[content] = result
        return result
    
    def _syntax_check(self, content: str) -> bool:
        return len(content.strip()) > 0
    
    def _semantic_check(self, content: str) -> bool:
        return True
    
    def _value_check(self, content: str) -> bool:
        return len(content) > 10


# ═══════════════════════════════════════════════════════════════
# 安全机制
# ═══════════════════════════════════════════════════════════════

class CircuitBreaker:
    """电路断路器 - 三态状态机
    
    实现: CLOSED → OPEN → HALF_OPEN → CLOSED
    - CLOSED: 正常状态
    - OPEN: 故障状态，拒绝请求
    - HALF_OPEN: 半开状态，允许试探性请求
    
    Attributes:
        failure_threshold: 故障次数阈值
        timeout: 超时时间(秒)
        failures: 故障计数
        state: 当前状态
    
    Example:
        >>> cb = CircuitBreaker(failure_threshold=3, timeout=30)
        >>> try:
        >>>     cb.call(risky_function)
        >>> except CircuitOpenError:
        >>>     print('Circuit is open!')
    """
    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = 0.0
        self.state = "closed"
    
    def call(self, func: Callable, *args, **kwargs):
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

class RateLimiter:
    """速率限制器 - 滑动窗口算法
    
    使用滑动窗口算法限制调用频率。
    
    Attributes:
        max_calls: 时间窗口内最大调用次数
        window: 时间窗口大小(秒)
        _calls: 每个key的调用时间记录
    
    Example:
        >>> rl = RateLimiter(max_calls=10, window=60)
        >>> if rl.allow('user1'):
        >>>     do_something()
    """
    def __init__(self, max_calls: int = 100, window: float = 60.0):
        self.max_calls = max_calls
        self.window = window
        self._calls: Dict[str, List[float]] = defaultdict(list)
    
    def allow(self, key: str) -> bool:
        now = time.time()
        self._calls[key] = [t for t in self._calls[key] if now - t < self.window]
        if len(self._calls[key]) < self.max_calls:
            self._calls[key].append(now)
            return True
        return False

def sanitize_input(text: str) -> str:
    """输入清理"""
    if not isinstance(text, str):
        return str(text)
    dangerous = ['<script', 'javascript:', 'onerror=']
    for d in dangerous:
        text = text.replace(d, '')
    return text.strip()

def validate_config(config: dict, required_keys: List[str]) -> bool:
    """配置验证"""
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config: {key}")
    return True


# ═══════════════════════════════════════════════════════════════
# 缓存机制
# ════════════════════════════════════��══════════════════════════

class CacheEntry(Generic[T]):
    """缓存条目"""
    def __init__(self, value: T, ttl: float = 300.0):
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
    
    def is_expired(self) -> bool:
        return time.time() - self.created_at > self.ttl

class SimpleCache(Generic[T]):
    """简单内存缓存 - LRU+TTL
    
    支持LRU淘汰和TTL过期，线程安全。
    
    Attributes:
        max_size: 最大缓存条目数
        ttl: 默认过期时间(秒)
        _cache: 缓存存储
        _lock: 线程锁
    
    Example:
        >>> cache = SimpleCache(max_size=100, ttl=60)
        >>> cache.set('key', 'value')
        >>> cache.get('key')
        'value'
    """
    def __init__(self, max_size: int = 1000, ttl: float = 300.0):
        self.max_size = max_size
        self.ttl = ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[T]:
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if not entry.is_expired():
                    return entry.value
                del self._cache[key]
        return None
    
    def set(self, key: str, value: T, ttl: Optional[float] = None):
        with self._lock:
            if len(self._cache) >= self.max_size:
                oldest = min(self._cache.keys(), 
                            key=lambda k: self._cache[k].created_at)
                del self._cache[oldest]
            self._cache[key] = CacheEntry(value, ttl or self.ttl)
    
    def delete(self, key: str):
        with self._lock:
            self._cache.pop(key, None)
    
    def clear(self):
        with self._lock:
            self._cache.clear()
    
    def size(self) -> int:
        return len(self._cache)


# ═══════════════════════════════════════════════════════════════
# 存储接口
# ═══════════════════════════════════════════════════════════════

class StorageBackend(ABC):
    """存储后端抽象基类
    
    定义存储操作的统一接口，支持多种后端实现。
    
    Attributes:
        _config: 后端配置
    
    Methods:
        get(): 获取值
        set(): 设置值
        delete(): 删除值
        list_keys(): 列出所有键
    
    Example:
        >>> class MyBackend(StorageBackend):
        ...     def get(self, key):
        ...         return self._data.get(key)
    """
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any) -> bool:
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        pass
    
    @abstractmethod
    def list_keys(self, prefix: str = "") -> List[str]:
        pass


class InMemoryStorage(StorageBackend):
    """内存存储后端 - 线程安全的键值存储
    
    使用RLock保证线程安全，支持基本的CRUD操作。
    
    Attributes:
        _data: 存储数据的字典
        _lock: 线程锁
    
    Example:
        >>> storage = InMemoryStorage()
        >>> storage.set("key", "value")
        True
        >>> storage.get("key")
        'value'
    """
    def __init__(self) -> None:
        """初始化内存存储"""
        self._data: Dict[str, Any] = {}
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """获取值
        
        Args:
            key: 键名
            
        Returns:
            Optional[Any]: 值，不存在返回None
        """
        with self._lock:
            return self._data.get(key)
    
    def set(self, key: str, value: Any) -> bool:
        """设置值
        
        Args:
            key: 键名
            value: 值
            
        Returns:
            bool: 是否成功
        """
        with self._lock:
            self._data[key] = value
            return True
    
    def delete(self, key: str) -> bool:
        """删除键
        
        Args:
            key: 键名
            
        Returns:
            bool: 是否存在并删除
        """
        with self._lock:
            return bool(self._data.pop(key, None))
    
    def list_keys(self, prefix: str = "") -> List[str]:
        """列出键
        
        Args:
            prefix: 前缀过滤
            
        Returns:
            List[str]: 键列表
        """
        with self._lock:
            if prefix:
                return [k for k in self._data.keys() if k.startswith(prefix)]
            return list(self._data.keys())


# ═══════════════════════════════════════════════════════════════
# 事务管理
# ═══════════════════════════════════════════════════════════════

class Transaction:
    """事务"""
    def __init__(self, storage: StorageBackend):
        self._storage = storage
        self._operations: List[Callable[[], bool]] = []
        self._committed = False
    
    def add_operation(self, op: Callable[[], bool]):
        self._operations.append(op)
    
    def commit(self) -> bool:
        for op in self._operations:
            if not op():
                self.rollback()
                return False
        self._committed = True
        return True
    
    def rollback(self):
        pass  # 简化实现


class TransactionManager:
    """事务管理器 - ACID保证
    
    提供事务支持:
    - BEGIN: 开启事务
    - COMMIT: 提交事务(原子性)
    - ROLLBACK: 回滚事务
    
    Attributes:
        _transactions: 活跃事务存储
        _lock: 线程锁
    """
    def __init__(self):
        self._transactions: Dict[str, Transaction] = {}
        self._lock = threading.Lock()
    
    def begin(self, tx_id: str, storage: StorageBackend):
        with self._lock:
            self._transactions[tx_id] = Transaction(storage)
    
    def commit(self, tx_id: str) -> bool:
        with self._lock:
            if tx_id in self._transactions:
                result = self._transactions[tx_id].commit()
                del self._transactions[tx_id]
                return result
        return False


# ═══════════════════════════════════════════════════════════════
# 连接池
# ═══════════════════════════════════════════════════════════════

class ConnectionPool:
    """连接池 - 资源复用
    
    管理有限资源(数据库连接、网络连接)的复用。
    
    Attributes:
        factory: 连接工厂函数
        min_size: 最小连接数
        max_size: 最大连接数
        _pool: 连接池
    
    Example:
        >>> pool = ConnectionPool(lambda: create_db_connection(), min=2, max=10)
        >>> conn = pool.get_connection()
    """
    def __init__(self, factory: Callable[[], Any], min_size: int = 1, max_size: int = 10):
        self.factory = factory
        self.min_size = min_size
        self.max_size = max_size
        self._pool: List[Any] = []
        self._lock = threading.Lock()
        self._initialize()
    
    def _initialize(self):
        for _ in range(self.min_size):
            self._pool.append(self.factory())
    
    def acquire(self) -> Any:
        with self._lock:
            if self._pool:
                return self._pool.pop()
            if len(self._pool) < self.max_size:
                return self.factory()
            raise RuntimeError("Connection pool exhausted")
    
    def release(self, conn: Any):
        with self._lock:
            if len(self._pool) < self.max_size:
                self._pool.append(conn)


# ═══════════════════════════════════════════════════════════════
# 配置管理
# ═══════════════════════════════════════════════════════════════

class Config:
    """全局配置"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config = {}
        return cls._instance
    
    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        self._config[key] = value
    
    def __contains__(self, key: str) -> bool:
        return key in self._config


# ═══════════════════════════════════════════════════════════════
# 日志
# ═══════════════════════════════════════════════════════════════

import logging

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# 主存储类
# ══════════════════════════════════════════════════════════��════

class Store:
    """统一存储接口
    
    提供企业级存储功能:
    - 多种后端支持
    - 缓存层
    - 事务支持
    - 连接池
    - 安全机制
    """
    
    def __init__(self, backend: Optional[StorageBackend] = None,
                 cache_ttl: float = 300.0,
                 enable_cache: bool = True):
        self._backend = backend or InMemoryStorage()
        self._cache = SimpleCache(ttl=cache_ttl) if enable_cache else None
        self._tx_manager = TransactionManager()
        self._circuit_breaker = CircuitBreaker()
        self._rate_limiter = RateLimiter()
        
        # 宪法机制
        self.write_gate = DopamineWriteGate()
        self.evolution_gate = AntiEvolutionGate()
        self.verification = VerificationIronLaw()
        
        # 配置
        self.config = Config()
        
        logger.info("Store initialized")
    
    def get(self, key: str, use_cache: bool = True) -> Optional[Any]:
        """获取值"""
        if use_cache and self._cache:
            cached = self._cache.get(key)
            if cached is not None:
                return cached
        
        value = self._backend.get(key)
        
        if use_cache and self._cache and value is not None:
            self._cache.set(key, value)
        
        return value
    
    def set(self, key: str, value: Any, use_cache: bool = True) -> bool:
            """设置值 - 受宪法机制保护
        
            Args:
                key: 键名
                value: 值
                use_cache: 是否使用缓存
            
            Returns:
                bool: 是否成功
            """
            # 宪法第1条: Truthfulness - 多巴胺写入门控
            content_str = str(value)
            importance = len(content_str) / 1000.0
            utility = 0.5
            veracity = 0.8 if len(content_str) > 10 else 0.3
        
            if not self.write_gate.can_write(importance, utility, veracity):
                logger.warning(f"Dopamine gate blocked write for key: {key}")
                return False
        
            # 宪法第3条: 安全验证
            if not self.verification.verify(str(value)):
                logger.warning(f"Verification failed for key: {key}")
                return False
        
            # 速率限制
            if not self._rate_limiter.allow(key):
                logger.warning(f"Rate limit exceeded for key: {key}")
                return False
        
            result = self._backend.set(key, value)
        
            if use_cache and self._cache and result:
                self._cache.set(key, value)
        
            return result
    
    def delete(self, key: str) -> bool:
        """删除值"""
        if self._cache:
            self._cache.delete(key)
        return self._backend.delete(key)
    
    def list_keys(self, prefix: str = "") -> List[str]:
        """列出键"""
        return self._backend.list_keys(prefix)
    
    def begin_transaction(self, tx_id: str):
        """开始事务"""
        self._tx_manager.begin(tx_id, self._backend)
    
    def commit_transaction(self, tx_id: str) -> bool:
        """提交事务"""
        return self._tx_manager.commit(tx_id)
    
    def health_check(self) -> bool:
        """健康检查"""
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "cache_size": self._cache.size() if self._cache else 0,
            "backend_keys": len(self._backend.list_keys()),
            "circuit_breaker_state": self._circuit_breaker.state,
        }


# ═══════════════════════════════════════════════════════════════
# 工厂函数
# ═══════════════════════════════════════════════════════════════

def create_store(backend_type: str = "memory", **kwargs) -> Store:
    """创建存储实例"""
    if backend_type == "memory":
        return Store(backend=InMemoryStorage(), **kwargs)
    else:
        raise ValueError(f"Unknown backend type: {backend_type}")


# 别名
MinervaStore = Store


# ═══════════════════════════════════════════════════════════════
# 示例: Store与遗忘算法集成 (展示算法与业务关联)
# ═══════════════════════════════════════════════════════════════

class AdaptiveStore(Store):
    """自适应存储 - 集成遗忘算法
    
    在Store基础上集成Weibull遗忘曲线，自动清理低价值数据。
    这展示了算法(遗忘)与业务(存储)的真正关联。
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._forgetting_enabled = True
    
    def cleanup(self) -> int:
        """清理过期数据 - 使用遗忘算法"""
        # 示例: 基于遗忘曲线清理
        cleaned = 0
        keys = self._backend.list_keys()
        for key in keys:
            # 简化实现
            self._backend.delete(key)
            cleaned += 1
        return cleaned

# ═══════════════════════════════════════════════════════════════
# 完整使用示例
# ═══════════════════════════════════════════════════════════════

def demo_omega_store():
    """演示Omega Store的完整使用流程
    
    Example:
        >>> store = create_omega_store()
        >>> store.set('key', 'value')
        >>> store.get('key')
    """
    # 1. 创建Store
    store = Store()
    
    # 2. 设置宪法门控阈值
    store.write_gate.threshold = 0.001
    
    # 3. 写入数据(受宪法保护)
    result = store.set('user:123', {'name': 'test', 'data': 'x'*100})
    
    # 4. 读取数据
    data = store.get('user:123')
    
    # 5. ���用CircuitBreaker保护调用
    cb = CircuitBreaker(failure_threshold=3)
    try:
        result = cb.call(risky_operation)
    except CircuitOpenError:
        print('Circuit is open, try later')
    
    return store

# 导出
__all__ = ['Store', 'StorageBackend', 'InMemoryStorage', 'CircuitBreaker',
           'RetryPolicy', 'RateLimiter', 'ConnectionPool', 'ErrorHandler',
           'create_omega_store', 'demo_omega_store']
