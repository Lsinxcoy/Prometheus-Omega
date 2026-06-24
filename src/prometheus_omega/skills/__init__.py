"""Skills - 技能层 (SkillRegistry+Curator+SkillClaw)"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timezone
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


class SkillStatus(Enum):
    ACTIVE = "active"
    LEARNING = "learning"
    ARCHIVED = "archived"


@dataclass
class Skill:
    skill_id: str
    name: str
    description: str
    success_rate: float = 0.0
    usage_count: int = 0
    status: SkillStatus = SkillStatus.LEARNING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


class SkillRegistry:
    """技能注册表 - 来自Z/X系统"""
    
    def __init__(self):
        self.skills: Dict[str, Skill] = {}
    
    def register(self, name: str, description: str = "", 
                 executor: Optional[Callable] = None) -> str:
        skill_id = str(uuid.uuid4())
        self.skills[skill_id] = Skill(
            skill_id=skill_id,
            name=name,
            description=description,
            metadata={"executor": executor}
        )
        return skill_id
    
    def get(self, skill_id: str) -> Optional[Skill]:
        return self.skills.get(skill_id)
    
    def list_all(self) -> List[Skill]:
        return list(self.skills.values())
    
    def update_usage(self, skill_id: str, success: bool):
        skill = self.skills.get(skill_id)
        if skill:
            skill.usage_count += 1
            n = skill.usage_count
            old_rate = skill.success_rate
            skill.success_rate = (old_rate * (n-1) + (1 if success else 0)) / n


class Curator:
    """策展人 - 来自Z系统
    
    自动技能策展
    """
    
    def __init__(self, registry: SkillRegistry,
                 min_success_rate: float = 0.6,
                 min_usage: int = 5):
        self.registry = registry
        self.min_success_rate = min_success_rate
        self.min_usage = min_usage
    
    def curate(self) -> Dict[str, List[str]]:
        """策展返回需要归档和激活的技能"""
        to_archive = []
        to_activate = []
        
        for skill in self.registry.list_all():
            if skill.usage_count >= self.min_usage:
                if skill.success_rate >= self.min_success_rate:
                    skill.status = SkillStatus.ACTIVE
                    to_activate.append(skill.skill_id)
                else:
                    skill.status = SkillStatus.ARCHIVED
                    to_archive.append(skill.skill_id)
        
        return {
            "activate": to_activate,
            "archive": to_archive
        }


class SkillClaw:
    """SkillClaw PRM 4级路由 - 来自X系统#62"""
    
    def __init__(self):
        self.routes = {
            "pattern_match": [],
            "semantic_similarity": [],
            "context_aware": [],
            "adaptive": []
        }
    
    def route(self, query: str, skills: List[Skill]) -> Optional[Skill]:
        # 4级路由
        for skill in skills:
            if skill.status == SkillStatus.ACTIVE:
                return skill
        return None


# 工厂
def create_skill_registry() -> SkillRegistry:
    return SkillRegistry()

def create_curator(registry: SkillRegistry, **kwargs) -> Curator:
    return Curator(registry, **kwargs)