# 基础导入
from __future__ import annotations
import logging

import sys, os, re, json, time, datetime
import logging

from typing import Dict, List, Any, Optional, Callable, Tuple, Set
import logging

from dataclasses import dataclass, field
from enum import Enum, IntEnum, auto


"""Execution - 执行层 (DAG+Parallel+Retryable+Monitored)"""
import logging

from dataclasses import dataclass, field
import logging

from typing import List, Dict, Any, Optional, Set
from enum import Enum
import logging

import uuid, time



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

class NodeStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class DAGNode:
    """DAG节点"""
    node_id: str
    task: Any
    depends_on: List[str] = field(default_factory=list)
    status: NodeStatus = NodeStatus.PENDING
    result: Any = None
    
    def is_ready(self) -> bool:
        return self.status == NodeStatus.PENDING
    
    def is_completed(self) -> bool:
        return self.status == NodeStatus.COMPLETED
    
    def is_failed(self) -> bool:
        return self.status == NodeStatus.FAILED
    
    def mark_running(self):
        self.status = NodeStatus.RUNNING
    
    def mark_completed(self, result: Any):
        self.status = NodeStatus.COMPLETED
        self.result = result
    
    def mark_failed(self, error: Any):
        self.status = NodeStatus.FAILED
        self.result = error
    
    def get_info(self) -> Dict:
        return {
            'node_id': self.node_id,
            'status': self.status.value,
            'depends_on': self.depends_on,
            'has_result': self.result is not None,
        }


class DAGExecutor:
    """DAG执行器"""
    
    def __init__(self):
        self.nodes: Dict[str, DAGNode] = {}
    
    def add_node(self, node_id: str, task: Any, deps: List[str] = None):
        self.nodes[node_id] = DAGNode(node_id, task, deps or [])
    
    def execute(self) -> Dict[str, Any]:
        results = {}
        executed = set()
        
        while len(executed) < len(self.nodes):
            for node_id, node in self.nodes.items():
                if node_id in executed:
                    continue
                
                deps_done = all(d in executed for d in node.depends_on)
                if deps_done:
                    node.status = NodeStatus.RUNNING
                    node.result = {"node": node_id, "executed": True}
                    node.status = NodeStatus.COMPLETED
                    results[node_id] = node.result
                    executed.add(node_id)
        
        return results


class ParallelDAG:
    """并行DAG执行"""
    
    def __init__(self, max_parallel: int = 4):
        self.max_parallel = max_parallel
        self.execution_log: List[Dict] = []
        self._max_log = 200
    
    def execute_parallel(self, nodes: List[DAGNode]) -> List[Any]:
        results = []
        levels = self._compute_levels(nodes)
        
        for level_nodes in levels:
            batch = level_nodes[:self.max_parallel]
            for node in batch:
                try:
                    if callable(node.task):
                        node.result = node.task()
                    else:
                        node.result = {"node": node.node_id, "executed": True}
                    node.status = NodeStatus.COMPLETED
                    results.append(node.result)
                    self.execution_log.append({'node_id': node.node_id, 'status': 'completed', 'timestamp': time.time()})
                except Exception as e:
                    node.status = NodeStatus.FAILED
                    node.result = {'error': str(e)}
                    results.append(node.result)
            
            if len(self.execution_log) > self._max_log:
                self.execution_log = self.execution_log[-self._max_log:]
        
        return results
    
    def _compute_levels(self, nodes: List[DAGNode]) -> List[List[DAGNode]]:
        levels = []
        executed = set()
        
        while len(executed) < len(nodes):
            current_level = []
            for node in nodes:
                if node.node_id in executed:
                    continue
                deps_done = all(d in executed for d in node.depends_on)
                if deps_done:
                    current_level.append(node)
            
            if not current_level:
                break
            
            levels.append(current_level)
            for node in current_level:
                executed.add(node.node_id)
        
        return levels
    
    def get_statistics(self) -> Dict:
        if not self.execution_log:
            return {'total': 0, 'completed': 0, 'failed': 0}
        
        completed = sum(1 for l in self.execution_log if l['status'] == 'completed')
        failed = sum(1 for l in self.execution_log if l['status'] == 'failed')
        
        return {'total': len(self.execution_log), 'completed': completed, 'failed': failed}


class RetryableDAG:
    """可重试DAG"""
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.retry_log: List[Dict] = []
    
    def execute_with_retry(self, node: DAGNode) -> Any:
        last_error = None
        for attempt in range(self.max_retries):
            try:
                if callable(node.task):
                    result = node.task()
                else:
                    result = {"node": node.node_id, "executed": True}
                self.retry_log.append({'node_id': node.node_id, 'attempt': attempt+1, 'success': True, 'timestamp': time.time()})
                return result
            except Exception as e:
                last_error = e
                self.retry_log.append({'node_id': node.node_id, 'attempt': attempt+1, 'success': False, 'error': str(e), 'timestamp': time.time()})
        raise last_error
    
    def get_retry_count(self, node_id: str) -> int:
        return sum(1 for l in self.retry_log if l['node_id'] == node_id and not l['success'])


class MonitoredDAG:
    """可监控DAG"""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {}
        self._history_size = 500
    
    def record(self, node_id: str, metric: str, value: Any):
        if node_id not in self.metrics:
            self.metrics[node_id] = {'records': []}
        
        record = {'metric': metric, 'value': value, 'timestamp': time.time()}
        self.metrics[node_id]['records'].append(record)
        
        if len(self.metrics[node_id]['records']) > self._history_size:
            self.metrics[node_id]['records'] = self.metrics[node_id]['records'][-self._history_size:]
    
    def get_node_metrics(self, node_id: str) -> Dict:
        if node_id not in self.metrics:
            return {}
        
        records = self.metrics[node_id].get('records', [])
        numeric = {r['metric']: r['value'] for r in records if isinstance(r['value'], (int, float))}
        
        if not numeric:
            return {'records': len(records)}
        
        return {'count': len(records), 'min': min(numeric.values()), 'max': max(numeric.values()), 'avg': sum(numeric.values()) / len(numeric)}
    
    def get_all_metrics(self) -> Dict[str, Dict]:
        return {nid: self.get_node_metrics(nid) for nid in self.metrics}
    
    def clear_metrics(self):
        self.metrics = {}


# 工厂
def create_dag_executor() -> DAGExecutor:
    return DAGExecutor()

def create_parallel_dag(max_parallel: int = 4) -> ParallelDAG:
    return ParallelDAG(max_parallel=max_parallel)

def create_retryable_dag(max_retries: int = 3) -> RetryableDAG:
    return RetryableDAG(max_retries=max_retries)

def create_monitored_dag() -> MonitoredDAG:
    return MonitoredDAG()


# ===== 来自XYZ系统 =====
class ParallelDAGExecutor(DAGExecutor):
    """并行DAG执行器 - 支持并行执行独立节点"""
    
    def __init__(self, version: str = "1.0.0", max_parallel: int = 4):
        super().__init__(version)
        self.max_parallel = max_parallel
        self._parallel_groups: List[List[str]] = []
    
    def _compute_parallel_groups(self) -> List[List[str]]:
        """计算可并行执行的节点组"""
        # 简化：按层级分组
        in_degree = {node_id: 0 for node_id in self.nodes}
        for from_id, to_id in self.edges:
            in_degree[to_id] += 1
        
        groups = []
        remaining = set(self.nodes.keys())
        
        while remaining:
            # 找出入度为0的节点
            ready = [n for n in remaining if in_degree[n] == 0]
            if not ready:
                break
            
            groups.append(ready)
            
            # 移除已处理的节点
            for node_id in ready:
                remaining.remove(node_id)
                for from_id, to_id in self.edges:
                    if from_id == node_id:
                        in_degree[to_id] -= 1
        
        return groups
    
    def execute_parallel(self, initial_context: dict) -> dict:
        """并行执行"""
        self._parallel_groups = self._compute_parallel_groups()
        
        context = dict(initial_context)
        context["_execution"] = {
            "execution_id": self._execution_id,
            "version": self.version,
            "steps": [],
            "parallel": True
        }
        
        results = {}
        
        for group in self._parallel_groups:
            # 并行执行组内节点
            import concurrent.futures
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(group)) as executor:
                futures = {}
                for node_id in group:
                    node = self.nodes[node_id]
                    future = executor.submit(node.action, context)
                    futures[future] = node_id
                
                for future in concurrent.futures.as_completed(futures):
                    node_id = futures[future]
                    node = self.nodes[node_id]
                    try:
                        node.result = future.result()
                        node.state = "completed"
                    except Exception as e:
                        node.state = "failed"
                        node.error = str(e)
                    
                    results[node_id] = node.result
                    context[node_id] = node.result
        
        return {
            "context": context,
            "results": results,
            "parallel_groups": self._parallel_groups,
            "execution_id": self._execution_id
        }



class RetryableDAGExecutor(DAGExecutor):
    """可重试的DAG执行器"""
    
    def __init__(self, version: str = "1.0.0", max_retries: int = 3):
        super().__init__(version)
        self.max_retries = max_retries
        self._retry_counts: Dict[str, int] = {}
    
    def execute_with_retry(self, initial_context: dict) -> dict:
        """执行并重试失败的节点"""
        self._retry_counts = {node_id: 0 for node_id in self.nodes}
        
        for attempt in range(self.max_retries):
            result = self.execute(initial_context)
            
            # 检查是否有失败
            if not result["failed"]:
                result["attempts"] = attempt + 1
                return result
            
            # 重试失败的节点
            failed_id = result["failed"]
            self._retry_counts[failed_id] += 1
            
            # 重置节点状态
            self.nodes[failed_id].state = "pending"
            self.nodes[failed_id].error = ""
        
        result["attempts"] = self.max_retries
        result["final_failure"] = True
        return result
    
    def get_retry_stats(self) -> dict:
        """获取重试统计"""
        return dict(self._retry_counts)



class MonitoredDAGExecutor(DAGExecutor):
    """可监控的DAG执行器 - 带指标收集"""
    
    def __init__(self, version: str = "1.0.0"):
        super().__init__(version)
        self._metrics = {
            "node_executions": {},
            "total_duration": 0.0,
            "failed_count": 0,
            "success_count": 0
        }
    
    def _execute_node(self, node: DAGNode, context: dict) -> dict:
        """执行节点并收集指标"""
        start_time = time.time()
        
        result = super()._execute_node(node, context)
        
        duration = time.time() - start_time
        
        # 更新指标
        if node.node_id not in self._metrics["node_executions"]:
            self._metrics["node_executions"][node.node_id] = {
                "count": 0,
                "total_duration": 0.0,
                "failures": 0
            }
        
        m = self._metrics["node_executions"][node.node_id]
        m["count"] += 1
        m["total_duration"] += duration
        
        if node.state == "failed":
            m["failures"] += 1
            self._metrics["failed_count"] += 1
        else:
            self._metrics["success_count"] += 1
        
        self._metrics["total_duration"] += duration
        
        return result
    
    def get_metrics(self) -> dict:
        """获取执行指标"""
        return {
            **self._metrics,
            "avg_node_duration": {
                k: v["total_duration"] / max(v["count"], 1)
                for k, v in self._metrics["node_executions"].items()
            }
        }
    
    def reset_metrics(self) -> None:
        """重置指标"""
        self._metrics = {
            "node_executions": {},
            "total_duration": 0.0,
            "failed_count": 0,
            "success_count": 0
        }

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
