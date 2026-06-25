"""Store Module - 存储层"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional, List, Dict, Callable
import threading
import logging
import time

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """缓存条目"""
    value: Any
    expires_at: float

class SimpleCache:
    """简单缓存"""
    def __init__(self, ttl: int = 300):
        self.ttl = ttl
        self._data: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._data.get(key)
            if entry and entry.expires_at > time.time():
                return entry.value
            self._data.pop(key, None)
            return None
    
    def set(self, key: str, value: Any):
        with self._lock:
            self._data[key] = CacheEntry(value, time.time() + self.ttl)
    
    def delete(self, key: str):
        with self._lock:
            self._data.pop(key, None)
    
    def clear(self):
        with self._lock:
            self._data.clear()

class RateLimiter:
    """速率限制器"""
    def __init__(self, max_per_second: int = 100):
        self.max_per_second = max_per_second
        self._timestamps: Dict[str, List[float]] = {}
        self._lock = threading.Lock()
    
    def allow(self, key: str) -> bool:
        with self._lock:
            now = time.time()
            if key not in self._timestamps:
                self._timestamps[key] = []
            self._timestamps[key] = [t for t in self._timestamps[key] if now - t < 1]
            if len(self._timestamps[key]) < self.max_per_second:
                self._timestamps[key].append(now)
                return True
            return False

class CircuitBreaker:
    """断路器"""
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = 0
        self.state = "closed"
        self._lock = threading.Lock()
    
    def call(self, func: Callable, *args, **kwargs):
        with self._lock:
            if self.state == "open":
                if time.time() - self.last_failure_time > self.timeout:
                    self.state = "half-open"
                else:
                    raise Exception("Circuit breaker is open")
        
        try:
            result = func(*args, **kwargs)
            with self._lock:
                self.failures = 0
                self.state = "closed"
            return result
        except Exception as e:
            with self._lock:
                self.failures += 1
                self.last_failure_time = time.time()
                if self.failures >= self.failure_threshold:
                    self.state = "open"
            raise e

class InMemoryStorage:
    """内存存储"""
    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            return self._data.get(key)
    
    def set(self, key: str, value: Any) -> bool:
        with self._lock:
            self._data[key] = value
            return True
    
    def delete(self, key: str) -> bool:
        with self._lock:
            return bool(self._data.pop(key, None))
    
    def list_keys(self, prefix: str = "") -> List[str]:
        with self._lock:
            if prefix:
                return [k for k in self._data.keys() if k.startswith(prefix)]
            return list(self._data.keys())

class Store:
    """统一存储接口"""
    def __init__(self, backend=None, cache_ttl: int = 300, enable_cache: bool = True,
                 threshold: float = 0.05):
        self._backend = backend or InMemoryStorage()
        self._cache = SimpleCache(ttl=cache_ttl) if enable_cache else None
        self._circuit_breaker = CircuitBreaker()
        self._rate_limiter = RateLimiter()
        
        # 宪法门控
        from prometheus_omega.safety import DopamineWriteGate, AntiEvolutionGate
        self._dopamine = DopamineWriteGate(threshold=threshold)
        self._evolution = AntiEvolutionGate()
        self.write_gate = self._dopamine
        self.evolution_gate = self._evolution
    
    def get(self, key: str, use_cache: bool = True) -> Optional[Any]:
        """获取值"""
        try:
            if use_cache and self._cache:
                cached = self._cache.get(key)
                if cached is not None:
                    return cached
            value = self._backend.get(key)
            if use_cache and self._cache and value is not None:
                self._cache.set(key, value)
            return value
        except Exception as e:
            logger.error(f"Get failed: {e}")
            return None
    
    def set(self, key: str, value: Any, use_cache: bool = True,
            importance: float = 0.9, utility: float = 0.9, veracity: float = 0.9) -> bool:
        """设置值"""
        try:
            # 宪法门控检查
            if not self._dopamine.can_write(importance, utility, veracity):
                logger.warning(f"Write gate rejected: q={importance*utility*veracity}")
                return False
            # 速率限制
            if not self._rate_limiter.allow(key):
                logger.warning(f"Rate limit exceeded for key: {key}")
                return False
            # 写入
            result = self._backend.set(key, value)
            if use_cache and self._cache and result:
                self._cache.set(key, value)
            return result
        except Exception as e:
            logger.error(f"Set failed: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """删除"""
        try:
            if self._cache:
                self._cache.delete(key)
            return self._backend.delete(key)
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return False
    
    def list_keys(self, prefix: str = "") -> List[str]:
        """列出键"""
        return self._backend.list_keys(prefix)
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return key in self._backend._data
    
    def clear(self) -> bool:
        """清空"""
        try:
            if self._cache:
                self._cache.clear()
            self._backend._data.clear()
            return True
        except Exception as e:
            logger.error(f"Clear failed: {e}")
            return False
    
    def size(self) -> int:
        """返回存储数量"""
        return len(self._backend._data)
    
    def batch_set(self, items: dict) -> int:
        """批量设置"""
        count = 0
        for k, v in items.items():
            if self.set(k, v):
                count += 1
        return count
    
    def batch_get(self, keys: list) -> dict:
        """批量获取"""
        return {k: self.get(k) for k in keys}
    
    def health_check(self) -> bool:
        """健康检查"""
        return True
