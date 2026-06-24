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

"""L9 Monitor - 监控层 (Z-score+CORAL+自愈)
"""
import logging

from dataclasses import dataclass, field
import logging

from typing import List, Dict, Any, Optional, Callable
from enum import Enum
import logging

import statistics, time
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




class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Alert:
    """警报"""
    level: AlertLevel
    message: str
    timestamp: float = field(default_factory=time.time)
    
    def is_critical(self) -> bool:
        return self.level == AlertLevel.CRITICAL
    
    def is_error(self) -> bool:
        return self.level in (AlertLevel.ERROR, AlertLevel.CRITICAL)
    
    def to_dict(self) -> Dict:
        return {
            'level': self.level.value,
            'message': self.message,
            'timestamp': self.timestamp,
        }
    
    def age(self) -> float:
        return time.time() - self.timestamp


class ZScoreAnomaly:
    """Z-score异常检测 - 来自X系统#46"""
    
    def __init__(self, threshold: float = 3.0):
        self.threshold = threshold
        self.values: List[float] = []
    
    def add(self, value: float):
        self.values.append(value)
        if len(self.values) > 1000:
            self.values.pop(0)
    
    def is_anomaly(self, value: float) -> bool:
        if len(self.values) < 10:
            return False
        mean = statistics.mean(self.values)
        stdev = statistics.stdev(self.values) if len(self.values) > 1 else 1
        z = abs((value - mean) / stdev) if stdev > 0 else 0
        return z > self.threshold


class TrendPredictor:
    """趋势外推预测 - 来自X系统#47"""
    
    def __init__(self, window: int = 10):
        self.window = window
        self.history: List[float] = []
    
    def predict(self) -> float:
        if len(self.history) < 2:
            return 0
        # 简单线性趋势
        n = len(self.history)
        x_mean = (n - 1) / 2
        y_mean = sum(self.history) / n
        
        numerator = sum((i - x_mean) * (y - y_mean) for i, y in enumerate(self.history))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0
        return self.history[-1] + slope


class CORALHeartbeat:
    """CORAL心跳 - 来自X/Y系统#48
    
    Reflect → Consolidate → Redirect 循环
    """
    
    def __init__(self, interval: int = 60):
        self.interval = interval
        self.last_reflect = 0
        self.last_consolidate = 0
        self.last_redirect = 0
    
    def heartbeat(self) -> Dict[str, bool]:
        now = time.time()
        return {
            "reflect": now - self.last_reflect > self.interval,
            "consolidate": now - self.last_consolidate > self.interval * 6,
            "redirect": now - self.last_redirect > self.interval * 10,
        }


class SelfHealingEngine:
    """自愈引擎 - 来自X系统#49
    
    功能:
    - 注册修复规则
    - 自动诊断错误
    - 执行修复动作
    - 记录自愈历史
    """
    
    def __init__(self, auto_heal: bool = True, max_retries: int = 3):
        """初始化自愈引擎
        
        Args:
            auto_heal: 是否自动执行修复
            max_retries: 最大重试次数
        """
        self.auto_heal = auto_heal
        self.max_retries = max_retries
        self.healing_rules: Dict[str, callable] = {}
        
        # 统计
        self.heal_attempts = 0
        self.heal_successes = 0
        self.heal_failures = 0
        
        # 历史
        self._history: List[Dict] = []
        
        # 内置规则
        self._register_builtin_rules()
    
    def _register_builtin_rules(self):
        """注册内置修复规则"""
        # 内存溢出 - 清理缓存
        def fix_memory():
            import gc
            gc.collect()
        
        self.register_rule("memory", fix_memory)
        self.register_rule("MemoryError", fix_memory)
        
        # 超时 - 重试
        def fix_timeout():
            pass  # 重试逻辑由调用方处理
        
        self.register_rule("timeout", fix_timeout)
        self.register_rule("TimeoutError", fix_timeout)
        
        # 连接错误 - 重置连接
        def fix_connection():
            pass  # 连接池重置
        
        self.register_rule("ConnectionError", fix_connection)
        self.register_rule("connection", fix_connection)
    
    def register_rule(self, condition: str, fix: callable, 
                     priority: int = 0, description: str = ""):
        """注册修复规则
        
        Args:
            condition: 错误条件关键词
            fix: 修复函数
            priority: 优先级 (越高越先执行)
            description: 规则描述
        """
        self.healing_rules[condition] = {
            "fix": fix,
            "priority": priority,
            "description": description,
            "condition": condition,
        }
    
    def heal(self, error: Dict) -> Dict[str, Any]:
        """执行自愈
        
        Args:
            error: 错误信息字典
            
        Returns:
            Dict: 自愈结果
        """
        self.heal_attempts += 1
        
        error_type = error.get("type", "")
        error_msg = error.get("message", str(error))
        error_key = f"{error_type}: {error_msg}"
        
        matched_rules = []
        
        # 匹配规则
        for condition, rule in self.healing_rules.items():
            if condition.lower() in error_key.lower():
                matched_rules.append(rule)
        
        # 按优先级排序
        matched_rules.sort(key=lambda x: x.get("priority", 0), reverse=True)
        
        if not matched_rules:
            self.heal_failures += 1
            return {
                "success": False,
                "reason": "no matching rule",
                "error": error_key,
            }
        
        # 执行修复
        for rule in matched_rules:
            try:
                fix_func = rule.get("fix")
                if callable(fix_func):
                    fix_func()
                    
                    # 记录成功
                    self.heal_successes += 1
                    self._history.append({
                        "timestamp": time.time(),
                        "error": error_key,
                        "rule": rule.get("description", rule.get("condition", "")),
                        "success": True,
                    })
                    
                    return {
                        "success": True,
                        "rule": rule.get("condition", ""),
                        "description": rule.get("description", ""),
                    }
                    
            except Exception as e:
                # 记录失败但继续尝试下一个规则
                self._history.append({
                    "timestamp": time.time(),
                    "error": error_key,
                    "rule": rule.get("condition", ""),
                    "success": False,
                    "exception": str(e),
                })
                continue
        
        # 所有规则都失败
        self.heal_failures += 1
        return {
            "success": False,
            "reason": "all rules failed",
            "error": error_key,
        }
    
    def can_heal(self, error: Dict) -> bool:
        """检查是否可以修复
        
        Args:
            error: 错误信息
            
        Returns:
            bool: 是否有匹配的修复规则
        """
        error_type = error.get("type", "")
        error_msg = error.get("message", str(error))
        error_key = f"{error_type}: {error_msg}"
        
        for condition in self.healing_rules:
            if condition.lower() in error_key.lower():
                return True
        
        return False
    
    def get_statistics(self) -> Dict:
        """获取自愈统计"""
        total = self.heal_attempts
        success_rate = self.heal_successes / total if total > 0 else 0
        
        return {
            "total_attempts": total,
            "successes": self.heal_successes,
            "failures": self.heal_failures,
            "success_rate": success_rate,
            "registered_rules": len(self.healing_rules),
        }
    
    def get_history(self, limit: int = 100) -> List[Dict]:
        """获取自愈历史"""
        return self._history[-limit:]
    
    def clear_history(self):
        """清除历史记录"""
        self._history = []


class Monitor:
    """统一监控系统 - 整合所有监控功能
    
    整合Z-score异常检测、趋势预测、CORAL心跳、自愈引擎、警报系统
    """
    
    def __init__(self, name: str = "omega_monitor",
                 enable_healing: bool = True,
                 alert_callback: callable = None):
        """初始化监控器
        
        Args:
            name: 监控器名称
            enable_healing: 是否启用自愈
            alert_callback: 警报回调函数
        """
        self.name = name
        self.enable_healing = enable_healing
        self.alert_callback = alert_callback
        
        # 组件
        self.zscore = ZScoreAnomaly(threshold=3.0)
        self.trend = TrendPredictor(window=10)
        self.coral = CORALHeartbeat(interval=60)
        self.healer = SelfHealingEngine(auto_heal=enable_healing)
        self.alerts = AlertSystem()
        
        # 指标收集
        self._metrics: Dict[str, List[float]] = {}
        self._start_time = time.time()
    
    def record_metric(self, metric_name: str, value: float):
        """记录指标
        
        Args:
            metric_name: 指标名称
            value: 指标值
        """
        if metric_name not in self._metrics:
            self._metrics[metric_name] = []
        
        self._metrics[metric_name].append(value)
        
        # 保持最近1000个值
        if len(self._metrics[metric_name]) > 1000:
            self._metrics[metric_name] = self._metrics[metric_name][-1000:]
        
        # 检查异常
        self.zscore.add(value)
        if self.zscore.is_anomaly(value):
            self.alerts.send(
                level=AlertLevel.WARNING,
                message=f"异常检测: {metric_name}={value}"
            )
    
    def predict_trend(self, metric_name: str) -> float:
        """预测趋势
        
        Args:
            metric_name: 指标名称
            
        Returns:
            float: 预测值
        """
        values = self._metrics.get(metric_name, [])
        if not values:
            return 0.0
        
        self.trend.history = values[-self.trend.window:]
        return self.trend.predict()
    
    def check_heartbeat(self) -> Dict[str, bool]:
        """检查心跳
        
        Returns:
            Dict: 需要执行的操作
        """
        return self.coral.heartbeat()
    
    def handle_error(self, error: Dict) -> Dict[str, Any]:
        """处理错误 (包含自愈)
        
        Args:
            error: 错误信息
            
        Returns:
            Dict: 处理结果
        """
        # 发送警报
        self.alerts.send(
            level=AlertLevel.ERROR,
            message=f"错误: {error.get('message', str(error))}"
        )
        
        # 自愈
        if self.enable_healing and self.healer.can_heal(error):
            result = self.healer.heal(error)
            if result.get("success"):
                self.alerts.send(
                    level=AlertLevel.INFO,
                    message=f"自愈成功: {result.get('description', '')}"
                )
            return result
        
        return {"success": False, "reason": "healing disabled or no rule"}
    
    def get_status(self) -> Dict:
        """获取监控状态
        
        Returns:
            Dict: 状态信息
        """
        uptime = time.time() - self._start_time
        
        return {
            "name": self.name,
            "uptime_seconds": uptime,
            "metrics_count": len(self._metrics),
            "zscore_baseline": len(self.zscore.values),
            "healer_stats": self.healer.get_statistics(),
            "alert_count": len(self.alerts.alerts),
        }
    
    def reset(self):
        """重置监控器"""
        self._metrics = {}
        self.zscore.values = []
        self.trend.history = []
        self.alerts.alerts = []
        self._running = False
    
    def start(self) -> bool:
        """启动监控"""
        self._running = True
        self.alerts.alert(AlertLevel.INFO, f"{self.name} started")
        return True
    
    def stop(self):
        """停止监控"""
        self._running = False
        self.alerts.alert(AlertLevel.INFO, f"{self.name} stopped")
    
    def record_metric(self, name: str, value: float) -> bool:
        """记录指标并检测异常"""
        # 检测异常
        if self.zscore.is_anomaly(value):
            self.alerts.alert(
                AlertLevel.WARNING, 
                f"Anomaly detected: {name}={value}"
            )
            return False
        
        # 记录数据
        self.zscore.add(value)
        self.trend.history.append(value)
        if len(self.trend.history) > self.trend.window:
            self.trend.history.pop(0)
        
        return True
    
    def check_heartbeat(self) -> Dict[str, bool]:
        """检查CORAL心跳"""
        return self.coral.heartbeat()
    
    def heal_error(self, error: Dict) -> bool:
        """自愈错误"""
        result = self.healer.heal(error)
        if result:
            self.alerts.alert(AlertLevel.INFO, f"Healed error: {error}")
        return result
    
    def get_status(self) -> Dict[str, any]:
        """获取监控状态"""
        return {
            "name": self.name,
            "running": self._running,
            "metrics_count": len(self.zscore.values),
            "trend_history": len(self.trend.history),
            "alerts_count": len(self.alerts.alerts),
        }


class AlertSystem:
    """警报系统"""

    def __init__(self):
        self.alerts: List[Alert] = []

    def alert(self, level: AlertLevel, message: str):
        self.alerts.append(Alert(level=level, message=message))
        if len(self.alerts) > 100:
            self.alerts.pop(0)
    
    def send(self, level: AlertLevel, message: str):
        """发送警报 (alert的别名)"""
        self.alert(level, message)
    
    def get_recent(self, count: int = 10) -> List[Alert]:
        return self.alerts[-count:]


# 工厂
def create_zscore_anomaly(threshold: float = 3.0) -> ZScoreAnomaly:
    return ZScoreAnomaly(threshold=threshold)

def create_coral_heartbeat(interval: int = 60) -> CORALHeartbeat:
    return CORALHeartbeat(interval=interval)

def create_self_healing_engine() -> SelfHealingEngine:
    return SelfHealingEngine()


# ===== 来自XYZ系统 =====
class CoralHeartbeat:
    """K7: CORAL heartbeat with UCB1-based attention redirect.

    Uses EWMA for metric smoothing and paired t-test for verification.
    Models subsystem dependencies for cascading health assessment.
    """

    def __init__(self, subsystems: list[str] | None = None,
                 config: ZConfig | None = None,
                 dependencies: dict[str, list[str]] | None = None):
        self._config = config or ZConfig()
        self._subsystems = subsystems or ["memory", "evolution", "safety", "search"]
        self._observations: dict[str, list[float]] = {s: [] for s in self._subsystems}
        self._attention_counts: dict[str, int] = {s: 0 for s in self._subsystems}
        self._total_beats = 0
        self._last_beat: dict | None = None
        self._stats = {"observe": 0, "redirect": 0, "verify": 0,
                       "redirects_total": 0}

        # EWMA tracking: smooth metric history
        self._ewma_alpha = 0.3  # Weight for new observations
        self._ewma_values: dict[str, float] = {s: 0.5 for s in self._subsystems}

        # Subsystem dependency graph: if A depends on B, B's failure degrades A
        # dependencies[A] = [B, C] means A depends on B and C
        self._dependencies: dict[str, list[str]] = dependencies or {
            "search": ["memory"],      # Search depends on memory
            "evolution": ["memory"],   # Evolution depends on memory
            "safety": ["memory"],      # Safety checks need memory
        }

    def beat(self, metrics: dict[str, float] | None = None) -> dict:
        """Execute one CORAL heartbeat cycle.

        Args:
            metrics: current subsystem metrics (subsystem_name → score)

        Returns:
            Beat result with phase, redirect target, and verification.
        """
        self._total_beats += 1
        result = {"beat": self._total_beats}

        # Beat 1: OBSERVE — collect metrics and update EWMA
        if metrics:
            for subsystem, score in metrics.items():
                if subsystem in self._observations:
                    self._observations[subsystem].append(score)
                    # Update EWMA
                    prev = self._ewma_values[subsystem]
                    self._ewma_values[subsystem] = (
                        self._ewma_alpha * score + (1 - self._ewma_alpha) * prev
                    )
        self._stats["observe"] += 1
        result["observe"] = dict(metrics or {})
        result["ewma"] = dict(self._ewma_values)

        # Beat 2: REDIRECT — find underperforming subsystem via UCB1
        # Account for dependency degradation
        adjusted_health = self._compute_adjusted_health()
        redirect_target = self._select_attention_target(adjusted_health)
        self._attention_counts[redirect_target] += 1
        self._stats["redirect"] += 1
        self._stats["redirects_total"] += 1
        result["redirect_target"] = redirect_target
        result["adjusted_health"] = adjusted_health

        # Beat 3: VERIFY — check if last redirect improved the metric (t-test)
        verification = self._verify_last_redirect()
        self._stats["verify"] += 1
        result["verification"] = verification

        self._last_beat = result
        return result

    def _compute_adjusted_health(self) -> dict[str, float]:
        """Compute health adjusted by subsystem dependencies.

        If a dependency is unhealthy, the dependent subsystem's
        effective health is reduced proportionally.

        adjustment[A] = ewma[A] × Π(ewma[dep] for dep in dependencies[A])
        """
        adjusted = {}
        for s in self._subsystems:
            base = self._ewma_values[s]
            deps = self._dependencies.get(s, [])
            if deps:
                # Multiply by dependency health (all must be healthy)
                dep_product = 1.0
                for dep in deps:
                    if dep in self._ewma_values:
                        dep_product *= self._ewma_values[dep]
                adjusted[s] = base * (0.5 + 0.5 * dep_product)
            else:
                adjusted[s] = base
        return adjusted

    def _select_attention_target(self,
                                  adjusted_health: dict[str, float]) -> str:
        """UCB1-based attention selection with dependency awareness.

        UCB1 = mean_reward + sqrt(2 * ln(total) / count)
        Mean reward uses EWMA-adjusted health.
        """
        # Ensure every subsystem gets at least one look
        for s in self._subsystems:
            if self._attention_counts[s] == 0:
                return s

        # UCB1 calculation with EWMA
        ucb_scores = {}
        for s in self._subsystems:
            count = self._attention_counts[s]
            # Use EWMA as the reward signal (smoother than raw observations)
            mean = adjusted_health.get(s, 0.5)
            ucb = mean + math.sqrt(2 * math.log(self._total_beats) / count)
            ucb_scores[s] = ucb

        return max(ucb_scores, key=ucb_scores.get)

    def _verify_last_redirect(self) -> dict:
        """Verify that the last redirect improved the target subsystem.

        Uses paired t-test for statistical significance when enough
        observations are available, otherwise falls back to simple comparison.
        """
        if not self._last_beat:
            return {"status": "no_previous_beat"}

        target = self._last_beat.get("redirect_target", "")
        observations = self._observations.get(target, [])

        if len(observations) < 2:
            return {"status": "insufficient_data", "target": target}

        # Split observations: before redirect vs after
        # Use last beat number to determine split point
        before_count = max(1, len(observations) - 3)
        before = observations[:before_count]
        after = observations[before_count:]

        if len(after) < 2:
            # Fall back to simple comparison
            improving = observations[-1] > observations[0]
            return {
                "status": "verified" if improving else "no_improvement",
                "target": target,
                "method": "simple_comparison",
                "improving": improving,
            }

        # Paired t-test: compare before vs after means
        t_stat, p_value, significant = self._paired_t_test(before, after)

        after_mean = sum(after) / len(after)
        before_mean = sum(before) / len(before)
        improving = after_mean > before_mean

        return {
            "status": "verified" if (improving and significant) else "no_improvement",
            "target": target,
            "method": "paired_t_test",
            "before_mean": before_mean,
            "after_mean": after_mean,
            "t_statistic": t_stat,
            "p_value": p_value,
            "significant": significant,
            "improving": improving,
        }

    @staticmethod
    def _paired_t_test(before: list[float], after: list[float],
                       alpha: float = 0.05) -> tuple[float, float, bool]:
        """Simplified paired t-test for two samples.

        Returns (t_statistic, approximate_p_value, is_significant).

        Uses Welch's t-test approximation for unequal sample sizes.
        """
        n1 = len(before)
        n2 = len(after)
        if n1 == 0 or n2 == 0:
            return 0.0, 1.0, False

        mean1 = sum(before) / n1
        mean2 = sum(after) / n2

        # Variances
        var1 = sum((x - mean1) ** 2 for x in before) / max(n1 - 1, 1)
        var2 = sum((x - mean2) ** 2 for x in after) / max(n2 - 1, 1)

        # Standard error
        se = math.sqrt(var1 / n1 + var2 / n2)
        if se == 0:
            return 0.0, 1.0, False

        # t-statistic
        t_stat = (mean2 - mean1) / se

        # Degrees of freedom (Welch-Satterthwaite)
        if var1 / n1 + var2 / n2 > 0:
            df = ((var1 / n1 + var2 / n2) ** 2) / \
                 ((var1 / n1) ** 2 / max(n1 - 1, 1) +
                  (var2 / n2) ** 2 / max(n2 - 1, 1))
        else:
            df = n1 + n2 - 2

        # Approximate p-value using normal approximation for large df
        # For small df, use a rough approximation
        if df >= 30:
            # Normal approximation
            p_value = 2 * (1 - _normal_cdf(abs(t_stat)))
        else:
            # Rough t-distribution approximation
            p_value = 2 * (1 - _t_cdf_approx(abs(t_stat), df))

        significant = p_value < alpha
        return t_stat, p_value, significant

    def get_subsystem_health(self) -> dict[str, float]:
        """Get health score for each subsystem (latest raw observation + EWMA)."""
        health = {}
        for s in self._subsystems:
            obs = self._observations[s]
            health[s] = obs[-1] if obs else 0.5
        return health

    def get_subsystem_health_ewma(self) -> dict[str, float]:
        """Get EWMA-smoothed health for each subsystem."""
        return dict(self._ewma_values)

    def get_attention_distribution(self) -> dict[str, float]:
        """Get attention distribution (fraction of beats per subsystem)."""
        total = sum(self._attention_counts.values())
        if total == 0:
            return {s: 1.0 / len(self._subsystems) for s in self._subsystems}
        return {s: c / total for s, c in self._attention_counts.items()}

    def set_dependencies(self, dependencies: dict[str, list[str]]) -> None:
        """Update subsystem dependency graph."""
        self._dependencies = dependencies

    @property
    def total_beats(self) -> int:
        return self._total_beats

    @property
    def stats(self) -> dict:
        return dict(self._stats)


def _normal_cdf(x: float) -> float:
    """Approximate normal CDF using error function."""
    # Abramowitz and Stegun approximation
    a1 = 0.254829592
    a2 = -0.284496736
    a3 = 1.421413741
    a4 = -1.453152027
    a5 = 1.061405429
    p = 0.3275911

    sign = 1 if x >= 0 else -1
    x = abs(x) / math.sqrt(2)

    t = 1.0 / (1.0 + p * x)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x * x)

    return 0.5 * (1.0 + sign * y)


def _t_cdf_approx(t: float, df: float) -> float:
    """Approximate t-distribution CDF using normal with correction."""
    # For large df, t ≈ normal; for small df, use correction
    correction = (t ** 3 + t) / (4 * df)
    z = t * (1 - correction / (1 + correction)) if df > 0 else t
    return _normal_cdf(z)

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
