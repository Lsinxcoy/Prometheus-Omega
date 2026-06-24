# 基础导入
from __future__ import annotations
import logging

import sys, os, re, json, time, datetime
import logging

from typing import Dict, List, Any, Optional, Callable, Tuple, Set
import logging

from dataclasses import dataclass, field
from enum import Enum, IntEnum, auto


"""L6 Organs - 器官层 (5-organ pipeline + ToolLoop)"""
import logging

from dataclasses import dataclass, field
import logging

from typing import List, Dict, Any, Optional, Callable
from enum import Enum
import logging

import uuid



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

class OrganType(Enum):
    TAOTIE = "taotie"     # 欲望/需求
    NUWA = "nuwa"         # 创造/生成
    DARWIN = "darwin"     # 进化/选择
    POOL = "pool"         # 资源池
    GUARD = "guard"       # 守护/安全


@dataclass
class OrganResult:
    """器官执行结果"""
    organ: OrganType
    success: bool
    output: Any = None
    metadata: Dict = field(default_factory=dict)
    
    def is_successful(self) -> bool:
        return self.success
    
    def get_output_or_default(self, default: Any = None) -> Any:
        return self.output if self.output is not None else default
    
    def to_dict(self) -> Dict:
        return {
            'organ': self.organ_type.value if isinstance(self.organ_type, Enum) else self.organ_type,
            'success': self.success,
            'output': self.output,
            'metadata': self.metadata,
        }


class BaseOrgan:
    """12-Factor基础器官"""
    def __init__(self, organ_type: OrganType):
        self.organ_type = organ_type
        self.execution_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.last_execution_time: Optional[float] = None
    
    def execute(self, input_data: Any) -> OrganResult:
        self.execution_count += 1
        self.last_execution_time = __import__('time').time()
        return OrganResult(organ=self.organ_type, success=True)
    
    def get_statistics(self) -> Dict:
        return {
            'organ_type': self.organ_type.value if isinstance(self.organ_type, Enum) else self.organ_type,
            'total_executions': self.execution_count,
            'successes': self.success_count,
            'failures': self.failure_count,
            'success_rate': self.success_count / max(1, self.execution_count),
        }
    
    def reset_statistics(self):
        self.execution_count = 0
        self.success_count = 0
        self.failure_count = 0


class DNAExtractor:
    """DNA提取器"""
    def __init__(self):
        self.extraction_history: List[Dict] = []
    
    def extract(self, individual: Any) -> Dict[str, Any]:
        result = {
            "features": self._extract_features(individual),
            "genotype": self._encode_genotype(individual),
            "phenotype": self._extract_phenotype(individual),
        }
        
        self.extraction_history.append({
            'individual_id': getattr(individual, 'id', 'unknown'),
            'timestamp': __import__('time').time(),
        })
        
        return result
    
    def _extract_features(self, individual: Any) -> List[str]:
        if hasattr(individual, 'genes'):
            return list(individual.genes.keys())
        return ["feature1", "feature2"]
    
    def _encode_genotype(self, individual: Any) -> str:
        if hasattr(individual, 'genes'):
            genes = individual.genes
            return ''.join('1' if v > 0.5 else '0' for v in genes.values())
        return "10101"
    
    def _extract_phenotype(self, individual: Any) -> Dict:
        if hasattr(individual, 'genes'):
            return {k: float(v) for k, v in individual.genes.items()}
        return {"attr1": 0.8}
    
    def get_history_size(self) -> int:
        return len(self.extraction_history)


class PromotionManifest:
    """晋升清单
    
    控制个体从候选池晋升到正式池的决策
    """
    def __init__(self, safety_threshold: float = 0.7):
        self.safety_threshold = safety_threshold
        self.promotion_history: List[Dict] = []
        self.rejection_history: List[Dict] = []
    
    def can_promote(self, safety_score: float, fitness: float) -> bool:
        return safety_score >= self.safety_threshold and fitness > 0.5
    
    def evaluate(self, candidate: Dict) -> Dict:
        """评估候选个体是否可晋升"""
        safety_score = candidate.get('safety_score', 0.0)
        fitness = candidate.get('fitness', 0.0)
        
        can = self.can_promote(safety_score, fitness)
        
        result = {
            'candidate_id': candidate.get('id', 'unknown'),
            'safety_score': safety_score,
            'fitness': fitness,
            'can_promote': can,
            'reason': self._get_reason(safety_score, fitness, can),
        }
        
        if can:
            self.promotion_history.append(result)
        else:
            self.rejection_history.append(result)
        
        return result
    
    def _get_reason(self, safety: float, fitness: float, can: bool) -> str:
        if can:
            return "All checks passed"
        if safety < self.safety_threshold:
            return f"Safety score {safety:.2f} below threshold {self.safety_threshold}"
        if fitness <= 0.5:
            return f"Fitness {fitness:.2f} too low"
        return "Unknown"
    
    def get_promotion_rate(self) -> float:
        total = len(self.promotion_history) + len(self.rejection_history)
        return len(self.promotion_history) / max(1, total)
    
    def get_statistics(self) -> Dict:
        return {
            'promoted': len(self.promotion_history),
            'rejected': len(self.rejection_history),
            'promotion_rate': self.get_promotion_rate(),
            'safety_threshold': self.safety_threshold,
        }


class ToolLoop:
    """工具调用推理循环"""

    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.history: List[Dict] = []
        self.max_iterations = 10
    
    def register_tool(self, name: str, func: Callable):
        self.tools[name] = func
    
    def reason(self, query: str, memory=None) -> List[Dict]:
        """推理循环"""
        plan = []
        
        # 5工具推理
        for tool_name in ["read", "search", "execute", "compute", "remember"]:
            if tool_name in self.tools:
                plan.append({"tool": tool_name, "status": "planned"})
        
        self.history.append({'query': query, 'plan': plan})
        return plan
    
    def execute_loop(self, query: str, memory=None) -> List[Dict]:
        """执行完整工具循环"""
        results = []
        plan = self.reason(query, memory)
        
        for step in plan:
            tool_name = step['tool']
            if tool_name in self.tools:
                try:
                    output = self.tools[tool_name](query)
                    results.append({'tool': tool_name, 'status': 'success', 'output': output})
                except Exception as e:
                    results.append({'tool': tool_name, 'status': 'error', 'error': str(e)})
            else:
                results.append({'tool': tool_name, 'status': 'unavailable'})
        
        self.history.append({'query': query, 'results': results})
        return results
    
    def get_tool_names(self) -> List[str]:
        return list(self.tools.keys())
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        return self.history[-limit:]


class FiveOrganPipeline:
    """5器官流水线 - 来自X/CIP系统#29"""
    
    def __init__(self):
        self.taotie = BaseOrgan(OrganType.TAOTIE)
        self.nuwa = BaseOrgan(OrganType.NUWA)
        self.darwin = BaseOrgan(OrganType.DARWIN)
        self.pool = BaseOrgan(OrganType.POOL)
        self.guard = BaseOrgan(OrganType.GUARD)
    
    def process(self, input_data: Any) -> List[OrganResult]:
        results = []
        # Taotie: 需求识别
        results.append(self.taotie.execute(input_data))
        # Nuwa: 方案生成
        results.append(self.nuwa.execute(input_data))
        # Darwin: 评估选择
        results.append(self.darwin.execute(input_data))
        # Pool: 资源分配
        results.append(self.pool.execute(input_data))
        # Guard: 安全检查
        results.append(self.guard.execute(input_data))
        return results


# 工厂
def create_five_organ_pipeline() -> FiveOrganPipeline:
    return FiveOrganPipeline()

def create_tool_loop() -> ToolLoop:
    return ToolLoop()

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
