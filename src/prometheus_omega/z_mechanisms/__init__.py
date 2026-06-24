
# ═══════════════════════════════════════════════════════════════
# 安全工具类
# ═══════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════
# 工程化工具类
# ═══════════════════════════════════════════════════════════════

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


"""Z系统核心机制 - 从Prometheus Z直接复制

本模块包含经过303测试验证的真实实现：
- DopamineWriteGate (写入门控)
- AntiEvolutionGate (反进化门控)  
- WeibullForgetting (遗忘曲线)
- ConvergenceDetector (收敛检测)

所有机制均通过Z系统测试验证。
"""
from prometheus_z.store.write_gate import DopamineWriteGate
from prometheus_z.evolution.anti_evolution_gate import AntiEvolutionGate
from prometheus_z.store.forgetting import WeibullForgetting
from prometheus_z.loop.convergence import ConvergenceDetector

__all__ = [
    "DopamineWriteGate",
    "AntiEvolutionGate", 
    "WeibullForgetting",
    "ConvergenceDetector",
]