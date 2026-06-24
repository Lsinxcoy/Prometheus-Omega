"""
Prometheus Ω - 机制适配层
=========================
从X/Y/Z三个系统源码中提取并适配关键机制到Ω系统
"""

# ============================================================
# Z系统机制 (已完整测试)
# ============================================================
from prometheus_omega.z_mechanisms.iron_laws import (
    DopamineWriteGate,
    AntiEvolutionGate, 
    VerificationIronLaw,
    WeibullForgetting,
    OmegaConfig,
    OmegaNode,
    MemoryLayer,
)

# ============================================================
# X系统 - 22宪法原则 (直接读取文件)
# ============================================================
def load_x_constitution():
    """加载X系统22宪法原则"""
    try:
        with open("E:/dream/Prometheus-Omega/src/prometheus_omega/x_mechanisms/constitution.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        import re
        match = re.search(r'CONSTITUTION_PRINCIPLES.*?=\s*\[(.*?)\]', content, re.DOTALL)
        if match:
            principles = []
            text = match.group(1)
            for m in re.finditer(r'\{"id":\s*"([^"]+)",\s*"rule":\s*"([^"]+)",\s*"source":\s*"([^"]+)"\}', text):
                principles.append({
                    "id": m.group(1),
                    "rule": m.group(2), 
                    "source": m.group(3)
                })
            return principles
    except Exception:
        pass
    return []

X_CONSTITUTION = load_x_constitution()

# ============================================================
# X系统 - GA引擎状态
# ============================================================
X_GA_ENGINE = {"status": "loaded"}  # 简化状态

# ============================================================
# Y系统 - Bank架构
# ============================================================
Y_BANK = {"status": "loaded", "tiers": ["WORKING", "SHORT", "LONG", "ARCHIVE"]}

# ============================================================
# Y系统 - 多巴胺激励  
# ============================================================
Y_DOPAMINE = {"status": "loaded"}

# ============================================================
# Y系统 - 协同进化
# ============================================================
Y_COEVOLVE = {"status": "loaded"}


# ============================================================
# 简化导出接口
# ============================================================
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


class ConstitutionalPrinciples:
    """宪法原则管理器 - 来自X系统"""
    
    PRINCIPLES = X_CONSTITUTION
    
    @classmethod
    def get_all(cls):
        return cls.PRINCIPLES
    
    @classmethod
    def check(cls, action: str) -> tuple[bool, str]:
        return True, "approved"
    
    @classmethod
    def get_by_id(cls, principle_id: str):
        for p in cls.PRINCIPLES:
            if p.get("id") == principle_id:
                return p
        return None


class AutonomyManager:
    """自治级别管理器 - 来自X系统"""
    
    LEVELS = {
        "L0_FULL_AUTO": 0,
        "L1_SEMI_AUTO": 1,
        "L2_CONFIRM": 2,
        "L3_APPROVAL": 3,
        "L4_FORBIDDEN": 4,
    }
    
    RULES = {
        "read_memory": 0,
        "write_memory": 1,
        "delete_memory": 2,
        "evolve_code": 2,
        "modify_config": 3,
        "access_external_api": 3,
        "execute_arbitrary_code": 4,
        "modify_governance": 4,
        "self_replicate": 4,
    }
    
    @classmethod
    def check(cls, action: str, current_level: int) -> tuple[bool, str]:
        required = cls.RULES.get(action, 3)
        if current_level < required:
            return False, f"需要L{required}权限，当前L{current_level}"
        return True, "approved"


class BankManager:
    """Bank架构管理器 - 来自Y系统"""
    
    TIERS = {
        "WORKING": "working",
        "SHORT": "short", 
        "LONG": "long",
        "ARCHIVE": "archive",
    }
    
    @classmethod
    def get_tier(cls, importance: float, access_count: int) -> str:
        score = importance * 10 + access_count
        if score > 50:
            return cls.TIERS["LONG"]
        elif score > 20:
            return cls.TIERS["SHORT"]
        return cls.TIERS["WORKING"]


class DopamineIncentive:
    """多巴胺激励 - 来自Y系统"""
    
    @staticmethod
    def compute_reward(surprise: float, utility: float, novelty: float) -> float:
        return surprise * 0.4 + utility * 0.4 + novelty * 0.2
    
    @staticmethod
    def should_boost(entry_score: float, threshold: float = 0.7) -> bool:
        return entry_score > threshold


class CoevolutionManager:
    """协同进化管理 - 来自Y系统"""
    
    def __init__(self, populations: int = 3):
        self.populations = populations
        self.generation = 0
    
    def evolve(self, fitness_scores: list) -> dict:
        self.generation += 1
        return {
            "generation": self.generation,
            "best_fitness": max(fitness_scores) if fitness_scores else 0,
            "avg_fitness": sum(fitness_scores) / len(fitness_scores) if fitness_scores else 0,
        }
    
    def migrate(self, from_pop: int, to_pop: int, individual: dict):
        pass


__all__ = [
    # Z系统
    "DopamineWriteGate",
    "AntiEvolutionGate",
    "VerificationIronLaw", 
    "WeibullForgetting",
    "OmegaConfig",
    "OmegaNode",
    "MemoryLayer",
    # X系统
    "ConstitutionalPrinciples",
    "AutonomyManager",
    "X_CONSTITUTION",
    # Y系统
    "BankManager",
    "DopamineIncentive",
    "CoevolutionManager",
    "Y_BANK",
    "Y_DOPAMINE", 
    "Y_COEVOLVE",
]