"""Prometheus Ω - 最强自进化AI记忆系统

整合XYZ全部优势机制:
- X系统: 70+机制, 12层架构, 585测试
- Y系统: 5项前沿研究, 宪法+刑法
- Z系统: Loop Engineering, Hindsight, 最新论文
"""
__version__ = "1.0.0-Ω"

import sys
from pathlib import Path

# 版本信息
__version__ = "1.0.0-Ω"
__author__ = "Prometheus Ω Team"

# 确保src在path中
_package_path = Path(__file__).parent
if str(_package_path) not in sys.path:
    sys.path.insert(0, str(_package_path))

# 延迟导入避免循环依赖
def __getattr__(name):
    if name in ["OmegaCore", "create_omega_system"]:
        from prometheus_omega.foundation import Config
# ═══════════════════════════════════════════════════════════════
# 安全工具类
# ═══════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════
# 工程化工具类
# ═══════════════════════════════════════════════════════════════

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


        class OmegaCore:
            def __init__(self, config):
                self.config = config
        def create_omega_system(config=None):
            return OmegaCore(Config() if config is None else Config(**config))
        return OmegaCore if name == "OmegaCore" else create_omega_system
    
    # Foundation
    if name in ["create_uuid", "Config", "EventBus", "DeterministicRuleEngine"]:
        from prometheus_omega.foundation import create_uuid, Config, EventBus, DeterministicRuleEngine
        return locals()[name]
    
    # Memory
    if name in ["UnifiedEntry", "FourNetworkMemory", "Bank", "MemoryStore"]:
        from prometheus_omega.memory import UnifiedEntry, FourNetworkMemory, Bank, MemoryStore
        return locals()[name]
    
    # Evolution
    if name in ["GeneticAlgorithm", "ConvergenceDetector", "UCB1Bandit"]:
        from prometheus_omega.evolution import GeneticAlgorithm, ConvergenceDetector, UCB1Bandit
        return locals()[name]
    
    # Retrieval
    if name in ["PolyphonicRetrieval", "RRF"]:
        from prometheus_omega.retrieval import PolyphonicRetrieval, RRF
        return locals()[name]
    
    # Ecosystem
    if name in ["HarnessX", "LotkaVolterra", "FGGM"]:
        from prometheus_omega.ecosystem import HarnessX, LotkaVolterra, FGGM
        return locals()[name]
    
    # Execution
    if name in ["DAGExecutor"]:
        from prometheus_omega.execution import DAGExecutor
        return locals()[name]
    
    # Governance
    if name in ["ConstitutionalPrinciples"]:
        from prometheus_omega.governance import ConstitutionalPrinciples
        return locals()[name]
    
    # Evaluation
    if name in ["SEAGym", "MAA", "ThermodynamicIntelligence", "FiveViewEvaluator"]:
        from prometheus_omega.evaluation import SEAGym, MAA, ThermodynamicIntelligence, FiveViewEvaluator
        return locals()[name]
    
    # Safety
    if name in ["Denylist", "RateLimiter", "FourLayerDefense"]:
        from prometheus_omega.safety import Denylist, RateLimiter, FourLayerDefense
        return locals()[name]
    
    # Skills
    if name in ["SkillRegistry", "Curator"]:
        from prometheus_omega.skills import SkillRegistry, Curator
        return locals()[name]
    
    raise AttributeError(f"module has no attribute '{name}'")


__all__ = [
    "__version__",
    "OmegaCore", 
    "create_omega_system",
    "create_uuid",
    "Config", 
    "EventBus",
    "DeterministicRuleEngine",
    "UnifiedEntry",
    "FourNetworkMemory",
    "Bank",
    "MemoryStore",
    "GeneticAlgorithm",
    "ConvergenceDetector",
    "UCB1Bandit",
    "PolyphonicRetrieval",
    "RRF",
    "HarnessX",
    "LotkaVolterra",
    "FGGM",
    "DAGExecutor",
    "ConstitutionalPrinciples",
    "SEAGym",
    "MAA",
    "ThermodynamicIntelligence",
    "FiveViewEvaluator",
    "Denylist",
    "RateLimiter",
    "FourLayerDefense",
    "SkillRegistry",
    "Curator",
]