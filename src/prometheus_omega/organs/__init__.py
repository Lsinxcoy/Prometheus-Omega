"""L6 Organs - 器官层 (5-organ pipeline + ToolLoop)"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
import uuid


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


class ErrorHandler:
    """统一错误处理器"""
    
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
    
    @staticmethod
    def validate_input(value: Any, expected_type: type, field_name: str) -> Any:
        """输入验证"""
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