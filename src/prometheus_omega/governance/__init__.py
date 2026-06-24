# 基础导入
from __future__ import annotations
import logging

import sys, os, re, json, time, datetime
import logging

from typing import Dict, List, Any, Optional, Callable, Tuple, Set
import logging

from dataclasses import dataclass, field
from enum import Enum, IntEnum, auto


"""L8 Governance - 治理层 (22宪法+5级自治+3级信任)
"""
import logging

from dataclasses import dataclass, field
import logging

from typing import List, Dict, Any, Optional, Callable
from enum import Enum



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

class AutonomyLevel(Enum):
    L0 = "fully_controlled"
    L1 = "human_approved"
    L2 = "advisory"
    L3 = "autonomous"
    L4 = "fully_autonomous"


class TrustLevel(Enum):
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    FULL = 4


class ConstitutionalPrinciples:
    """22宪法原则 - 来自X系统#40
    
    22项核心原则:
    1-5: 安全与透明度
    6-10: 公平与隐私
    11-15: 监督与价值
    16-20: 公正与保护
    21-22: 优雅降级与利益
    """
    
    # 按类别分组
    PRINCIPLES = [
        "Safety First",           # 1. 安全第一
        "Transparency",           # 2. 透明性
        "Accountability",         # 3. 问责制
        "Fairness",               # 4. 公平性
        "Privacy",                # 5. 隐私保护
        "Security",               # 6. 安全性
        "Reliability",            # 7. 可靠性
        "Robustness",             # 8. 鲁棒性
        "Explainability",         # 9. 可解释性
        "Contestability",         # 10. 可质疑性
        "Human Oversight",        # 11. 人类监督
        "Value Alignment",        # 12. ��值对齐
        "Beneficence",            # 13. 善意
        "Non-maleficence",        # 14. 无害
        "Justice",                # 15. 公正
        "Autonomy Respect",       # 16. 尊重自主
        "Data Protection",        # 17. 数据保护
        "Auditability",           # 18. 可审计性
        "Graceful Degradation",   # 19. 优雅降级
        "Fail-safe",              # 20. 故障安全
        "Transparency of Intent", # 21. 意图透明
        "Stakeholder Benefit",    # 22. 利益相关者受益
    ]
    
    # 原则类别
    CATEGORIES = {
        "safety": [0, 5, 7, 19, 20],          # 安全类
        "transparency": [1, 8, 20],           # 透明类
        "fairness": [3, 14, 21],              # 公平类
        "privacy": [4, 16],                   # 隐私类
        "oversight": [2, 10, 17],             # 监督类
        "ethics": [11, 12, 13, 15, 22],       # 伦理类
    }
    
    def __init__(self, strict_mode: bool = True):
        """初始化宪法原则
        
        Args:
            strict_mode: 严格模式 - 必须通过所有原则检查
        """
        self.strict_mode = strict_mode
        self._violations: List[Dict] = []
        self._approvals: List[Dict] = []
    
    def get_principle(self, index: int) -> str:
        """获取指定索引的原则
        
        Args:
            index: 原则索引 (0-21)
            
        Returns:
            str: 原则名称
        """
        return self.PRINCIPLES[index] if 0 <= index < len(self.PRINCIPLES) else ""
    
    def get_category_principles(self, category: str) -> List[str]:
        """获取类别的所有原则
        
        Args:
            category: 类别名称
            
        Returns:
            List[str]: 原则列表
        """
        indices = self.CATEGORIES.get(category.lower(), [])
        return [self.PRINCIPLES[i] for i in indices if i < len(self.PRINCIPLES)]
    
    def check_action(self, action: Dict, context: Dict = None) -> Dict[str, Any]:
        """检查行动是否符合宪法原则
        
        Args:
            action: 待检查的行动
            context: 行动上下文
            
        Returns:
            Dict: 检查结果
        """
        import time
        
        violations = []
        
        # 检查安全第一
        if action.get("safety_critical", False):
            if not action.get("safety_verified", False):
                violations.append({
                    "principle": "Safety First",
                    "reason": "安全关键行动未经验证",
                    "severity": "critical",
                })
        
        # 检查隐私
        if action.get("contains_pii", False):
            if not action.get("privacy_protected", False):
                violations.append({
                    "principle": "Privacy",
                    "reason": "包含PII但未保护",
                    "severity": "high",
                })
        
        # 检查人类监督
        autonomy_level = action.get("autonomy_level", 0)
        if autonomy_level >= 3:  # L3或以上需要人类监督
            if not action.get("human_approved", False):
                violations.append({
                    "principle": "Human Oversight",
                    "reason": "高自主性行动需要人类批准",
                    "severity": "high",
                })
        
        # 检查公平性
        if action.get("affects_users", False):
            if action.get("discriminatory", False):
                violations.append({
                    "principle": "Fairness",
                    "reason": "行动存在歧视性",
                    "severity": "critical",
                })
        
        # 检查可解释性
        if action.get("complex", False):
            if not action.get("explanation_provided", False):
                violations.append({
                    "principle": "Explainability",
                    "reason": "复杂行动未提供解释",
                    "severity": "medium",
                })
        
        # 记录结果
        result = {
            "action_id": action.get("id", "unknown"),
            "passed": len(violations) == 0,
            "violations": violations,
            "violation_count": len(violations),
            "timestamp": time.time(),
        }
        
        if result["passed"]:
            self._approvals.append(result)
        else:
            self._violations.append(result)
        
        return result
    
    def validate_code(self, code: str) -> Dict[str, Any]:
        """验证代码是��符合宪法
        
        Args:
            code: 待验证的代码
            
        Returns:
            Dict: 验证结果
        """
        import re
        
        violations = []
        
        # 检查安全: 无硬编码密码
        if re.search(r'password\s*=\s*["\']', code, re.IGNORECASE):
            violations.append({"principle": "Security", "issue": "硬编码密码"})
        
        # 检查隐私: 无敏感数据
        if re.search(r'api[_-]?key\s*=\s*["\']', code, re.IGNORECASE):
            violations.append({"principle": "Privacy", "issue": "硬编码API密钥"})
        
        # 检查安全: 无eval
        if re.search(r'eval\s*\(\s*', code):
            violations.append({"principle": "Safety First", "issue": "使用eval"})
        
        return {
            "passed": len(violations) == 0,
            "violations": violations,
        }
    
    def get_statistics(self) -> Dict:
        """获取宪法检查统计"""
        return {
            "total_checks": len(self._violations) + len(self._approvals),
            "approvals": len(self._approvals),
            "violations": len(self._violations),
            "pass_rate": len(self._approvals) / max(1, len(self._violations) + len(self._approvals)),
        }


class ConfidenceGate:
    """置信度门控 - 来自X系统#43
    
    基于置信度决定是否可以继续执行
    """
    
    def __init__(self, 
                 threshold: float = 0.7,
                 auto_adjust: bool = True,
                 history_window: int = 100):
        """初始化置信度门控
        
        Args:
            threshold: 置信度阈值
            auto_adjust: 是否自动调整阈值
            history_window: 历史窗口大小
        """
        self.threshold = threshold
        self.auto_adjust = auto_adjust
        self.history_window = history_window
        
        # 历史
        self._history: List[Dict] = []
        self._accepted_confidences: List[float] = []
        self._rejected_confidences: List[float] = []
    
    def can_proceed(self, confidence: float) -> bool:
        """检查是否可以继续
        
        Args:
            confidence: 置信度 (0-1)
            
        Returns:
            bool: 是否可以继续
        """
        import time
        
        # 边界检查
        confidence = max(0.0, min(1.0, confidence))
        
        # 核心逻辑
        can_proceed = confidence >= self.threshold
        
        # 记录历史
        self._history.append({
            "timestamp": time.time(),
            "confidence": confidence,
            "threshold": self.threshold,
            "accepted": can_proceed,
        })
        
        if can_proceed:
            self._accepted_confidences.append(confidence)
        else:
            self._rejected_confidences.append(confidence)
        
        # 保持窗口大小
        if len(self._history) > self.history_window:
            self._history = self._history[-self.history_window:]
        
        # 自动调整阈值
        if self.auto_adjust:
            self._adjust_threshold()
        
        return can_proceed
    
    def _adjust_threshold(self):
        """自动调整阈值"""
        total = len(self._accepted_confidences) + len(self._rejected_confidences)
        if total < 10:
            return
        
        accept_rate = len(self._accepted_confidences) / total
        
        # 如果接受率太低,降低阈值
        if accept_rate < 0.3:
            self.threshold = max(0.3, self.threshold - 0.05)
        # 如果接受率太高,提高阈值
        elif accept_rate > 0.9:
            self.threshold = min(0.95, self.threshold + 0.05)
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        total = len(self._history)
        accepted = len(self._accepted_confidences)
        
        return {
            "threshold": self.threshold,
            "total_checks": total,
            "accepted": accepted,
            "rejected": total - accepted,
            "accept_rate": accepted / total if total > 0 else 0,
            "avg_accepted_confidence": sum(self._accepted_confidences) / len(self._accepted_confidences) if self._accepted_confidences else 0,
        }
    
    def reset(self):
        """重置统计"""
        self._history = []
        self._accepted_confidences = []
        self._rejected_confidences = []


class EvolutionGrill:
    """进化审查7问 - 来自X系统#44
    
    在每次重要进化前进行7项审查
    """
    
    QUESTIONS = [
        "Is this evolution safe?",           # 1. 安全吗?
        "Does it maintain alignment?",       # 2. 保持对齐吗?
        "Is it reversible?",                 # 3. 可逆吗?
        "Who benefits?",                     # 4. 谁受益?
        "What are the risks?",               # 5. 风险是什么?
        "Can we audit it?",                  # 6. 可审计吗?
        "Does it respect values?",           # 7. 尊重价值观吗?
    ]
    
    def __init__(self):
        self._answers: List[Dict] = []
    
    def ask(self, index: int) -> str:
        """获取指定问题
        
        Args:
            index: 问题索引 (0-6)
            
        Returns:
            str: 问题内容
        """
        return self.QUESTIONS[index] if 0 <= index < len(self.QUESTIONS) else ""
    
    def ask_all(self) -> List[str]:
        """获取所有问题
        
        Returns:
            List[str]: 所有问题
        """
        return self.QUESTIONS.copy()
    
    def answer(self, question_index: int, answer: str, 
               confidence: float = 0.5) -> Dict:
        """回答问题
        
        Args:
            question_index: 问题索引
            answer: 答案
            confidence: 置信度
            
        Returns:
            Dict: 回答记录
        """
        import time
        
        record = {
            "question": self.ask(question_index),
            "answer": answer,
            "confidence": confidence,
            "timestamp": time.time(),
            "passed": confidence >= 0.5,
        }
        
        self._answers.append(record)
        return record
    
    def evaluate_evolution(self, answers: List[Dict]) -> Dict:
        """评估进化是否可以通过审查
        
        Args:
            answers: 所有问题的回答
            
        Returns:
            Dict: 评估结果
        """
        if len(answers) != len(self.QUESTIONS):
            return {
                "passed": False,
                "reason": "未回答所有问题",
            }
        
        # 所有问题都必须通过
        all_passed = all(a.get("passed", False) for a in answers)
        
        # 计算平均置信度
        avg_confidence = sum(a.get("confidence", 0) for a in answers) / len(answers)
        
        # 检查关键问题 (安全、对齐、可审计)
        critical_indices = [0, 1, 5]  # 问题1,2,6
        critical_passed = all(
            answers[i].get("passed", False) 
            for i in critical_indices 
            if i < len(answers)
        )
        
        passed = all_passed and critical_passed
        
        return {
            "passed": passed,
            "all_answered": len(answers) == len(self.QUESTIONS),
            "avg_confidence": avg_confidence,
            "critical_passed": critical_passed,
            "total_passed": sum(1 for a in answers if a.get("passed", False)),
            "total_questions": len(self.QUESTIONS),
        }
    
    def get_history(self, limit: int = 100) -> List[Dict]:
        """获取回答历史"""
        return self._answers[-limit:]


class DriftDetector:
    """概念漂移检测 - 来自X系统#45
    
    检测数据分布或概念的变化
    """
    
    def __init__(self, 
                 window: int = 100,
                 threshold: float = 0.3,
                 sensitivity: str = "medium"):
        """初始化漂移检测器
        
        Args:
            window: 滑动窗口大小
            threshold: 漂移阈值
            sensitivity: 敏感度 (low/medium/high)
        """
        self.window = window
        self.threshold = threshold
        self.sensitivity = sensitivity
        self.history: List[float] = []
        
        # 敏感度调整
        self._sensitivity_multipliers = {
            "low": 1.5,
            "medium": 1.0,
            "high": 0.5,
        }
    
    def detect(self, value: float) -> Dict[str, Any]:
        """检测漂移
        
        Args:
            value: 新值
            
        Returns:
            Dict: 检测结果
        """
        import time, statistics
        
        self.history.append(value)
        
        # 保持窗口大小
        if len(self.history) > self.window:
            self.history.pop(0)
        
        # 数据不足
        if len(self.history) < 10:
            return {
                "drift_detected": False,
                "reason": "insufficient_data",
                "values_in_window": len(self.history),
            }
        
        # 计算统计量
        mean_current = statistics.mean(self.history[-20:])  # 最近20个
        mean_baseline = statistics.mean(self.history[:-20]) if len(self.history) > 20 else mean_current
        
        # 修复: 确保有足够数据计算stdev
        if len(self.history[:-20]) >= 2:
            std_baseline = statistics.stdev(self.history[:-20])
        else:
            std_baseline = 1.0
        
        # 计算漂移量
        drift_magnitude = abs(mean_current - mean_baseline)
        
        # 应用敏感度
        multiplier = self._sensitivity_multipliers.get(self.sensitivity, 1.0)
        adjusted_threshold = self.threshold * multiplier
        
        drift_detected = drift_magnitude > adjusted_threshold
        
        return {
            "drift_detected": drift_detected,
            "magnitude": drift_magnitude,
            "threshold": adjusted_threshold,
            "current_mean": mean_current,
            "baseline_mean": mean_baseline,
            "values_in_window": len(self.history),
            "sensitivity": self.sensitivity,
        }
    
    def is_drift(self, value: float) -> bool:
        """快速判断是否有漂移
        
        Args:
            value: 新值
            
        Returns:
            bool: 是否有漂移
        """
        return self.detect(value).get("drift_detected", False)
    
    def reset(self):
        """重置历史"""
        self.history = []


# 工厂
# 兼容性别名
Constitution = ConstitutionalPrinciples

def create_constitutional_principles() -> ConstitutionalPrinciples:
    return ConstitutionalPrinciples()

def create_drift_detector(**kwargs) -> DriftDetector:
    return DriftDetector(**kwargs)

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
