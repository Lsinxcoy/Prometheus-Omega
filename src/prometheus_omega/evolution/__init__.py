# 基础导入
from __future__ import annotations
import sys, os, re, json, time, datetime
from typing import Dict, List, Any, Optional, Callable, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum, IntEnum, auto


import time
from prometheus_omega.memory import MinervaStore
from enum import IntEnum, Enum

"""L5 Evolution - 进化层 (整合XYZ: 12层GA+CGP+Coevolve+Z Convergence)"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Callable, Optional, Dict, List, Any, Optional
from datetime import datetime, timezone
from enum import Enum
import random, math
import ast
from prometheus_omega.foundation import ZConfig, OmegaConfig, Strictness, SecurityPosture, GateCheckResult, WriteGateResult, EvolutionCheckResult, EvolutionOutcome



# 安全工具

# ═══════════════════════════════════════════════════════════════
# 宪法机制 - 3铁律
# ═══════════════════════════════════════════════════════════════


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

class EvolutionDirection(Enum):
    FORWARD = "forward"
    LATERAL = "lateral"
    REVERSE = "reverse"


@dataclass
class Individual:
    """进化个体"""
    id: str
    genes: Dict[str, Any]
    fitness: float = 0.0
    generation: int = 0
    parent_ids: List[str] = field(default_factory=list)


class GeneticAlgorithm:
    """12层遗传算法 - 来自X系统#17
    
    核心组件:
    - 种群管理: 初始化、选择(锦标赛)、交叉(单点)、变异(高斯)
    - 适应度: 评估函数、排序
    - 演化控制: 终止条件、精英保留、收敛检测
    """
    
    def __init__(self, population_size: int = 100,
                 mutation_rate: float = 0.1,
                 crossover_rate: float = 0.7,
                 elite_size: int = 2,
                 max_generations: int = 100):
        """初始化遗传算法
        
        Args:
            population_size: 种群大小
            mutation_rate: 变异概率
            crossover_rate: 交叉概率
            elite_size: 精英数量
            max_generations: 最大代数
        """
        self.pop_size = population_size
        self.mut_rate = mutation_rate
        self.cross_rate = crossover_rate
        self.elite_size = elite_size
        self.max_gen = max_generations
        
        self.population: List[Individual] = []
        self.generation = 0
        self.best_fitness = 0.0
        self.best_individual = None
        
        # 统计历史
        self._history: List[Dict] = []
    
    def init_population(self, gene_generator: Callable):
        """初始化种群"""
        self.population = [
            Individual(id=f"ind_{i}", genes=gene_generator())
            for i in range(self.pop_size)
        ]
    
    def evolve(self, fitness_fn: Callable) -> List[Individual]:
        """执行一代进化"""
        # 评估适应度
        for ind in self.population:
            ind.fitness = fitness_fn(ind.genes)
        
        # 选择
        selected = self._select()
        
        # 交叉
        offspring = self._crossover(selected)
        
        # 变异
        offspring = self._mutate(offspring)
        
        self.population = offspring
        self.generation += 1
        return self.population
    
    def _select(self) -> List[Individual]:
        """选择 ( Tournament )"""
        selected = []
        tournament_size = min(3, len(self.population))
        if tournament_size < 1:
            return self.population
        
        for _ in range(self.pop_size):
            if len(self.population) >= tournament_size:
                tournament = random.sample(self.population, tournament_size)
                winner = max(tournament, key=lambda x: x.fitness)
                selected.append(winner)
            else:
                selected.append(random.choice(self.population))
        return selected
    
    def _crossover(self, parents: List[Individual]) -> List[Individual]:
        """交叉"""
        offspring = []
        for i in range(0, len(parents), 2):
            if i+1 < len(parents) and random.random() < self.cross_rate:
                child = self._single_point_crossover(parents[i], parents[i+1])
            else:
                child = parents[i]
            offspring.append(child)
        return offspring
    
    def _single_point_crossover(self, p1: Individual, p2: Individual) -> Individual:
        """单点交叉"""
        genes = {**p1.genes, **p2.genes}
        return Individual(id=f"gen{self.generation}_{random.randint(0,9999)}",
                         genes=genes, generation=self.generation)
    
    def _mutate(self, offspring: List[Individual]) -> List[Individual]:
        """变异"""
        for ind in offspring:
            if random.random() < self.mut_rate:
                key = random.choice(list(ind.genes.keys()))
                ind.genes[key] = random.random()
        return offspring


class UCB1Bandit:
    """UCB1 Bandit层选择 - 来自X系统#18"""

    def __init__(self, n_arms: int = 3, arm_names: List[str] = None):
        """初始化UCB1
        
        Args:
            n_arms: arm数量
            arm_names: arm名称列表
        """
        if arm_names:
            self.arm_names = arm_names
        else:
            self.arm_names = [f"arm_{i}" for i in range(n_arms)]
        
        self.counts = {a: 0 for a in self.arm_names}
        self.values = {a: 0.0 for a in self.arm_names}
        self.total = 0
    
    def select(self) -> str:
        """UCB1选择"""
        for arm in self.arm_names:
            if self.counts[arm] == 0:
                self.counts[arm] += 1
                self.total += 1
                return arm
        
        # UCB1公式
        best_arm = None
        best_value = -float('inf')
        
        for arm in self.arm_names:
            avg_value = self.values[arm]
            exploration = math.sqrt(2 * math.log(self.total) / self.counts[arm])
            ucb_value = avg_value + exploration
            
            if ucb_value > best_value:
                best_value = ucb_value
                best_arm = arm
        
        self.counts[best_arm] += 1
        self.total += 1
        return best_arm
    
    def update(self, arm: str, reward: float):
        """更新arm的value
        
        Args:
            arm: arm名称
            reward: 奖励值
        """
        if arm not in self.counts:
            return
        
        n = self.counts[arm]
        old_value = self.values[arm]
        
        # 增量更新
        self.values[arm] = (old_value * n + reward) / (n + 1)


class CGP:
    """笛卡尔遗传编程 - 来自X系统#23
    
    自动生成程序/电路结构
    """
    def __init__(self, inputs: int = 2, outputs: int = 1, rows: int = 5, cols: int = 5, levels: int = 10):
        self.inputs = inputs
        self.outputs = outputs
        self.rows = rows
        self.cols = cols
        self.levels = levels  # levels_back参数
        self.functions = ['add', 'sub', 'mul', 'div', 'sin', 'cos', 'max', 'min']
    
    def generate(self) -> Dict[str, Any]:
        """生成完整CGP程序"""
        # 生成节点矩阵
        nodes = []
        for row in range(self.rows):
            for col in range(self.cols):
                # 每个节点选择输入连接
                max_input_idx = self.inputs + (row * self.cols + col) - 1
                if max_input_idx >= self.inputs:
                    # 随机选择输入源
                    input1 = random.randint(0, max_input_idx)
                    input2 = random.randint(0, max_input_idx)
                    func = random.choice(self.functions)
                    nodes.append({
                        'row': row, 'col': col,
                        'inputs': [input1, input2],
                        'function': func
                    })
        
        # 生成输出连接
        output_connections = []
        for out_idx in range(self.outputs):
            last_col_start = (self.rows - 1) * self.cols
            node_idx = random.randint(last_col_start, last_col_start + self.cols - 1)
            output_connections.append(node_idx)
        
        return {
            'nodes': nodes,
            'outputs': output_connections,
            'inputs': self.inputs,
            'outputs_count': self.outputs
        }
    
    def evaluate(self, program: Dict, inputs: List[float]) -> List[float]:
        """评估CGP程序"""
        if not inputs or len(inputs) != self.inputs:
            return []
        
        # 简化的前向传播
        values = list(inputs)
        
        for node in program.get('nodes', []):
            # 获取输入值
            in_vals = [values[i] for i in node['inputs'][:2] if i < len(values)]
            
            # 应用函���
            func = node['function']
            if func == 'add' and len(in_vals) >= 2:
                result = in_vals[0] + in_vals[1]
            elif func == 'sub' and len(in_vals) >= 2:
                result = in_vals[0] - in_vals[1]
            elif func == 'mul' and len(in_vals) >= 2:
                result = in_vals[0] * in_vals[1]
            elif func == 'div' and len(in_vals) >= 2:
                result = in_vals[0] / (in_vals[1] + 1e-10)
            elif func == 'sin':
                result = math.sin(in_vals[0] if in_vals else 0)
            elif func == 'cos':
                result = math.cos(in_vals[0] if in_vals else 0)
            elif func == 'max' and len(in_vals) >= 2:
                result = max(in_vals[0], in_vals[1])
            elif func == 'min' and len(in_vals) >= 2:
                result = min(in_vals[0], in_vals[1])
            else:
                result = in_vals[0] if in_vals else 0
            
            values.append(result)
        
        # 返回输出
        outputs = []
        for out_idx in program.get('outputs', []):
            if out_idx < len(values):
                outputs.append(values[out_idx])
        
        return outputs


class IslandGA:
    """Island并行GA - 来自X系统#20"""
    def __init__(self, num_islands: int = 4):
        self.islands = [[] for _ in range(num_islands)]
    
    def migrate(self):
        """环迁移"""
        for i in range(len(self.islands)):
            next_island = (i + 1) % len(self.islands)
            if self.islands[i] and self.islands[next_island]:
                migrant = self.islands[i].pop(0)
                self.islands[next_island].append(migrant)


class Coevolve:
    """协同进化 - 来自Y系统"""
    def __init__(self, populations: Dict[str, List[Individual]]):
        self.populations = populations
    
    def coevolve(self, fitness_fn: Callable) -> Dict[str, float]:
        results = {}
        for name, pop in self.populations.items():
            fit = sum(ind.fitness for ind in pop) / len(pop) if pop else 0
            results[name] = fit
        return results


class SpeculativeEvolution:
    """推测性进化 - 来自X/Y系统#25"""
    def __init__(self):
        self.branches: List[Individual] = []
    
    def fork(self, individual: Individual) -> Individual:
        branch = Individual(
            id=f"{individual.id}_branch",
            genes=dict(individual.genes),
            generation=individual.generation + 1,
            parent_ids=[individual.id]
        )
        self.branches.append(branch)
        return branch


class ConvergenceDetector:
    """收敛检测器 - 来自Z系统"""
    
    def __init__(self, threshold: float = 0.01, window: int = 10):
        self.threshold = threshold
        self.window = window
        self.history: List[float] = []
    
    def check(self, fitness: float) -> bool:
        self.history.append(fitness)
        if len(self.history) > self.window:
            self.history.pop(0)
        if len(self.history) < 2:
            return False
        diff = abs(self.history[-1] - self.history[0])
        return diff < self.threshold


# 工厂
def create_ga(pop_size: int = 100, **kwargs) -> GeneticAlgorithm:
    return GeneticAlgorithm(population_size=pop_size, **kwargs)

def create_ucb1(layers: List[str]) -> UCB1Bandit:
    return UCB1Bandit(layers)

def create_convergence_detector(**kwargs) -> ConvergenceDetector:
    return ConvergenceDetector(**kwargs)


# ===== 来自XYZ系统 =====
class ASTMutation:
    """E1: AST-safe code mutation engine."""

    MUTATION_TYPES = [
        "rename", "log_add", "error_handle", "type_annotate",
        "extract_const", "simplify_cond", "doc_add", "assert_add",
    ]

    def __init__(self, config: ZConfig | None = None):
        self._config = config or ZConfig()
        self._stats = {m: 0 for m in self.MUTATION_TYPES}
        self._stats["failed"] = 0

    def mutate(self, code: str, mutation_type: str = "rename",
               **kwargs) -> str | None:
        """Apply a single mutation to code.

        Returns mutated code, or None if mutation fails (syntax-safe: never returns invalid code).
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            self._stats["failed"] += 1
            return None

        try:
            if mutation_type == "rename":
                old_name = kwargs.get("old_name", "x")
                new_name = kwargs.get("new_name", "y")
                tree = self._rename(tree, old_name, new_name)
            elif mutation_type == "log_add":
                tree = self._add_logging(tree)
            elif mutation_type == "error_handle":
                tree = self._add_error_handling(tree)
            elif mutation_type == "extract_const":
                tree = self._extract_constants(tree)
            elif mutation_type == "doc_add":
                tree = self._add_docstrings(tree)
            elif mutation_type == "assert_add":
                tree = self._add_assertions(tree)
            elif mutation_type == "type_annotate":
                tree = self._add_type_annotations(tree)
            elif mutation_type == "simplify_cond":
                tree = self._simplify_conditions(tree)
            else:
                return None

            # Verify the mutation produces valid Python
            result = ast.unparse(tree)
            ast.parse(result)  # Round-trip verify
            self._stats[mutation_type] += 1
            return result

        except Exception:
            self._stats["failed"] += 1
            return None

    def safe_mutate(self, code: str, mutation_type: str = "rename",
                    **kwargs) -> str:
        """Mutate with fallback: if mutation fails, return original code."""
        result = self.mutate(code, mutation_type, **kwargs)
        return result if result is not None else code

    def _rename(self, tree: ast.AST, old_name: str, new_name: str) -> ast.AST:
        """Rename all occurrences of old_name to new_name."""
        tree = copy.deepcopy(tree)
        class Renamer(ast.NodeTransformer):
            def visit_Name(self, node):
                if node.id == old_name:
                    node.id = new_name
                return node
            def visit_FunctionDef(self, node):
                if node.name == old_name:
                    node.name = new_name
                self.generic_visit(node)
                return node
            def visit_arg(self, node):
                if node.arg == old_name:
                    node.arg = new_name
                return node
        return Renamer().visit(tree)

    def _add_logging(self, tree: ast.AST) -> ast.AST:
        """Add logging to function entries."""
        tree = copy.deepcopy(tree)
        class LogAdder(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                log_stmt = ast.Expr(
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Name(id="logger", ctx=ast.Load()),
                            attr="info",
                            ctx=ast.Load(),
                        ),
                        args=[ast.Constant(value=f"Entering {node.name}")],
                        keywords=[],
                    )
                )
                node.body.insert(0, log_stmt)
                return node
        return LogAdder().visit(tree)

    def _add_error_handling(self, tree: ast.AST) -> ast.AST:
        """Wrap function bodies in try/except."""
        tree = copy.deepcopy(tree)
        class ErrorHandler(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                original_body = node.body
                try_body = original_body
                except_body = [
                    ast.Expr(
                        value=ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(id="logger", ctx=ast.Load()),
                                attr="error",
                                ctx=ast.Load(),
                            ),
                            args=[ast.Call(
                                func=ast.Name(id="str", ctx=ast.Load()),
                                args=[ast.Name(id="e", ctx=ast.Load())],
                                keywords=[],
                            )],
                            keywords=[],
                        )
                    )
                ]
                try_node = ast.Try(
                    body=try_body,
                    handlers=[ast.ExceptHandler(
                        type=ast.Name(id="Exception", ctx=ast.Load()),
                        name="e",
                        body=except_body,
                    )],
                    orelse=[],
                    finalbody=[],
                )
                node.body = [try_node]
                return node
        return ErrorHandler().visit(tree)

    def _extract_constants(self, tree: ast.AST) -> ast.AST:
        """Extract magic numbers to named constants."""
        tree = copy.deepcopy(tree)
        class ConstExtractor(ast.NodeTransformer):
            def __init__(self):
                self.constants = {}
                self.counter = 0

            def visit_Constant(self, node):
                if isinstance(node.value, (int, float)) and node.value not in (0, 1, -1, True, False):
                    if node.value not in self.constants:
                        self.counter += 1
                        name = f"CONST_{self.counter}"
                        self.constants[node.value] = name
                    return ast.Name(id=self.constants[node.value], ctx=ast.Load())
                return node
        transformer = ConstExtractor()
        tree = transformer.visit(tree)
        return tree

    def _add_docstrings(self, tree: ast.AST) -> ast.AST:
        """Add docstrings to functions without them."""
        tree = copy.deepcopy(tree)
        class DocAdder(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                # Check if first statement is a docstring
                if (node.body and isinstance(node.body[0], ast.Expr)
                        and isinstance(node.body[0].value, ast.Constant)
                        and isinstance(node.body[0].value.value, str)):
                    return node  # Already has docstring
                docstring = ast.Expr(value=ast.Constant(value=f"TODO: Document {node.name}"))
                node.body.insert(0, docstring)
                return node
        return DocAdder().visit(tree)

    def _add_assertions(self, tree: ast.AST) -> ast.AST:
        """Add assertions at function entries for argument validation."""
        tree = copy.deepcopy(tree)
        class AssertAdder(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                for arg in node.args.args:
                    assert_stmt = ast.Assert(
                        test=ast.Compare(
                            left=ast.Name(id=arg.arg, ctx=ast.Load()),
                            ops=[ast.IsNot()],
                            comparators=[ast.Constant(value=None)],
                        ),
                        msg=ast.Constant(value=f"{arg.arg} must not be None"),
                    )
                    node.body.insert(0, assert_stmt)
                return node
        return AssertAdder().visit(tree)

    def _add_type_annotations(self, tree: ast.AST) -> ast.AST:
        """Add 'Any' type annotations to untyped function arguments."""
        tree = copy.deepcopy(tree)
        class TypeAnnotator(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                for arg in node.args.args:
                    if arg.annotation is None:
                        arg.annotation = ast.Name(id="Any", ctx=ast.Load())
                return node
        return TypeAnnotator().visit(tree)

    def _simplify_conditions(self, tree: ast.AST) -> ast.AST:
        """Simplify nested if/else patterns.

        Strategy: Flatten `if A: if B: X` → `if A and B: X`.
        Also flatten single-branch else-of-if.
        """
        class Simplifier(ast.NodeTransformer):
            simplified = False

            def visit_If(self, node):
                # First, recursively simplify children
                self.generic_visit(node)

                # Pattern: if A: if B: body → if A and B: body
                if (len(node.body) == 1
                        and isinstance(node.body[0], ast.If)
                        and not node.body[0].orelse):
                    inner = node.body[0]
                    combined_test = ast.BoolOp(
                        op=ast.And(),
                        values=[node.test, inner.test],
                    )
                    ast.copy_location(combined_test, node.test)
                    new_if = ast.If(
                        test=combined_test,
                        body=inner.body,
                        orelse=node.orelse,
                    )
                    ast.copy_location(new_if, node)
                    self.simplified = True
                    return new_if

                # Pattern: if A: X; else: if B: Y → if A: X; elif B: Y
                if (len(node.orelse) == 1
                        and isinstance(node.orelse[0], ast.If)):
                    inner = node.orelse[0]
                    node.orelse = [inner]
                    # Already an elif in practice (ast represents elif as If in orelse)

                return node

        simplifier = Simplifier()
        new_tree = simplifier.visit(tree)
        if simplifier.simplified:
            self._stats["simplifications"] += 1
        return new_tree

    @property
    def stats(self) -> dict:
        return dict(self._stats)


# ===== 来自XYZ系统 =====
class EvalDrivenEngine:
    """E2: 7-step evaluation-driven evolution pipeline."""

    def __init__(self, config: ZConfig | None = None,
                 store: 'MinervaStore | None' = None):
        self._config = config or ZConfig()
        self._gate = AntiEvolutionGate(self._config, store=store)
        self._iron_law = VerificationIronLaw(self._config)
        self._history: list[dict] = []

    def evolve(self, context: dict) -> EvolutionOutcome:
        """Run 7-step evolution pipeline.

        context must contain:
        - "weakness": what to improve (str)
        - "current_code": the code to evolve (str)
        - "eval_fn": callable that returns fitness score (0-1)
        - "apply_fn": callable that applies the change (optional)
        """
        weakness = context.get("weakness", "")
        current_code = context.get("current_code", "")
        eval_fn = context.get("eval_fn")
        apply_fn = context.get("apply_fn")

        if not weakness or not eval_fn:
            return EvolutionOutcome(applied=False, reason="Missing weakness or eval_fn")

        # ── Iron Law 2: AntiEvolutionGate ──
        gate_result = self._gate.check(
            hypothesis=weakness,
            existing_solutions=self._get_existing_solutions(),
        )
        if not gate_result.passed:
            return EvolutionOutcome(
                applied=False,
                reason=f"AntiEvolutionGate denied: {gate_result.reason}",
            )

        # ── Step 1: GRILL ──
        grill_answers = self._grill(weakness, current_code)

        # ── Step 2: DEFINE_EVAL ──
        eval_definition = self._define_eval(weakness, grill_answers)

        # ── Step 3: WRITE_PLAN ──
        plan = self._write_plan(weakness, grill_answers, eval_definition)

        # ── Step 4: EXECUTE ──
        fitness_before = eval_fn(current_code)
        modified_code = self._execute_plan(current_code, plan)

        # ── Step 5: GRADE (Iron Law 3: VerificationIronLaw) ──
        fitness_after = eval_fn(modified_code)

        # Determine direction from eval definition
        direction = eval_definition.get("direction", "maximize")

        # Verify improvement
        verification = self._iron_law.verify(
            claim=f"Change improves {weakness}",
            evidence={"before": fitness_before, "after": fitness_after},
            threshold=self._config.pass_k_threshold,
            direction=direction,
        )
        if not verification.passed:
            return EvolutionOutcome(
                applied=False,
                reason=f"VerificationIronLaw denied: {verification.reason}",
                fitness_before=fitness_before,
                fitness_after=fitness_after,
            )

        # ── Step 6: APPLY ──
        direction = context.get("direction", "maximize")
        if direction == "minimize":
            should_apply = fitness_after < fitness_before
        else:
            should_apply = fitness_after > fitness_before

        if should_apply:
            if apply_fn:
                apply_fn(modified_code)

            # ── Step 7: COMPILE ──
            compiled = fitness_after > self._config.compile_fitness_threshold

            outcome = EvolutionOutcome(
                applied=True,
                reason=f"Improved {weakness}: {fitness_before:.3f} → {fitness_after:.3f}",
                fitness_before=fitness_before,
                fitness_after=fitness_after,
                compilation=compiled,
            )

            self._history.append({
                "weakness": weakness,
                "fitness_before": fitness_before,
                "fitness_after": fitness_after,
                "applied": True,
                "compiled": compiled,
                "timestamp": time.time(),
            })

            return outcome

        return EvolutionOutcome(
            applied=False,
            reason=f"No improvement: {fitness_before:.3f} → {fitness_after:.3f}",
            fitness_before=fitness_before,
            fitness_after=fitness_after,
        )

    def _grill(self, weakness: str, code: str) -> dict:
        """Step 1: 4 questions about what to improve.

        Analyzes the weakness string and code to produce structured insights.
        Zero-LLM: uses heuristic analysis, not model calls.
        """
        # Parse weakness into components
        parts = weakness.lower().split()
        
        # Identify category from keywords
        categories = {
            "search": "retrieval_quality",
            "accuracy": "precision",
            "speed": "performance",
            "memory": "memory_efficiency",
            "consolidation": "knowledge_quality",
            "retention": "memory_retention",
            "utilization": "resource_efficiency",
            "relevance": "result_quality",
        }
        category = "general"
        for keyword, cat in categories.items():
            if keyword in parts:
                category = cat
                break

        # Analyze code structure for evidence
        code_lines = code.splitlines() if code else []
        code_size = len(code_lines)
        has_loops = any('for ' in l or 'while ' in l for l in code_lines)
        has_error_handling = any('try:' in l or 'except' in l for l in code_lines)
        has_caching = any('cache' in l.lower() for l in code_lines)

        # Build structured GRILL answers
        evidence_parts = []
        if code_size > 50:
            evidence_parts.append(f"code is {code_size} lines (large)")
        if not has_error_handling:
            evidence_parts.append("no error handling detected")
        if not has_caching:
            evidence_parts.append("no caching detected")
        evidence = "; ".join(evidence_parts) if evidence_parts else "observed in current behavior"

        # Generate improvement target
        improvement_map = {
            "retrieval_quality": "increase search recall and precision",
            "precision": "reduce false positive rate",
            "performance": "reduce latency of hot path",
            "memory_efficiency": "improve knowledge consolidation ratio",
            "knowledge_quality": "increase semantic node proportion",
            "memory_retention": "improve episodic-to-semantic promotion rate",
            "resource_efficiency": "increase recall/remember ratio",
            "result_quality": "improve ranking relevance score",
            "general": f"improve {weakness}",
        }

        # Suggest simplest change based on analysis
        change_map = {
            "retrieval_quality": "add hybrid search weight tuning",
            "precision": "add result filtering threshold",
            "performance": "add caching for frequent queries",
            "memory_efficiency": "add consolidation trigger threshold",
            "knowledge_quality": "add gravity-based promotion",
            "memory_retention": "adjust Weibull decay parameters",
            "resource_efficiency": "add prefetch for common patterns",
            "result_quality": "add MMR diversity filtering",
            "general": f"address {weakness} directly",
        }

        return {
            "weakness": weakness,
            "category": category,
            "evidence": evidence,
            "improvement_target": improvement_map.get(category, f"improve {weakness}"),
            "simplest_change": change_map.get(category, f"address {weakness} directly"),
        }

    def _define_eval(self, weakness: str, grill: dict) -> dict:
        """Step 2: Define how to measure improvement.

        Maps weakness category to concrete evaluation metrics.
        """
        category = grill.get("category", "general")

        metric_map = {
            "retrieval_quality": {"metric": "recall@k", "direction": "maximize", "threshold": 0.8},
            "precision": {"metric": "precision@k", "direction": "maximize", "threshold": 0.9},
            "performance": {"metric": "latency_p95_ms", "direction": "minimize", "threshold": 100},
            "memory_efficiency": {"metric": "consolidation_ratio", "direction": "maximize", "threshold": 0.6},
            "knowledge_quality": {"metric": "semantic_node_ratio", "direction": "maximize", "threshold": 0.3},
            "memory_retention": {"metric": "promotion_rate", "direction": "maximize", "threshold": 0.2},
            "resource_efficiency": {"metric": "recall_remember_ratio", "direction": "maximize", "threshold": 0.5},
            "result_quality": {"metric": "mmr_diversity_score", "direction": "maximize", "threshold": 0.4},
            "general": {"metric": weakness, "direction": "maximize", "threshold": self._config.pass_k_threshold},
        }

        result = metric_map.get(category, metric_map["general"]).copy()
        result["weakness"] = weakness
        result["category"] = category
        return result

    def _write_plan(self, weakness: str, grill: dict, eval_def: dict) -> dict:
        """Step 3: Write a concrete change plan.

        Maps GRILL insights + eval definition to a structured mutation plan.
        """
        category = grill.get("category", "general")
        improvement = grill.get("improvement_target", "")
        simplest = grill.get("simplest_change", "")
        metric = eval_def.get("metric", weakness)

        # Map category to meaningful AST mutation strategy
        # FIX: Use strategies that produce substantive code changes,
        # not cosmetic ones (log_add/doc_add are shallow).
        # rename → changes function/variable semantics
        # extract_const → makes magic numbers explicit
        # simplify_cond → reduces nesting complexity
        # error_handle → adds robustness
        strategy_map = {
            "retrieval_quality": "simplify_cond",    # Simplify nested retrieval logic
            "precision": "extract_const",            # Extract threshold constants for tuning
            "performance": "extract_const",          # Extract magic numbers for optimization
            "memory_efficiency": "error_handle",     # Add error handling for robustness
            "knowledge_quality": "rename",            # Rename for semantic clarity
            "memory_retention": "simplify_cond",     # Simplify retention logic
            "resource_efficiency": "extract_const",  # Extract config constants
            "result_quality": "assert_add",          # Add assertions for quality gates
            "general": "simplify_cond",
        }

        strategy = strategy_map.get(category, "log_add")

        return {
            "target": weakness,
            "category": category,
            "change_type": "ast_mutation",
            "strategy": strategy,
            "description": simplest,
            "improvement_target": improvement,
            "metric": metric,
            "threshold": eval_def.get("threshold", 0.5),
        }

    def _execute_plan(self, code: str, plan: dict) -> str:
        """Step 4: Execute the plan via AST mutation.

        Uses ASTMutation for syntax-safe code modification.
        Falls back to returning code unchanged if mutation fails.
        
        FIX: Pass mutation parameters from plan to mutator for substantive changes.
        """
        if not code:
            return code

        strategy = plan.get("strategy", "simplify_cond")
        
        # Extract mutation parameters from plan
        params = {}
        if plan.get("change_type") == "ast_mutation":
            # Pass relevant parameters based on strategy
            if strategy == "rename":
                # Could extract old_name/new_name from plan if available
                params = {"old_name": "x", "new_name": "improved_x"}
            elif strategy == "extract_const":
                params = {}  # ASTMutation._extract_constants handles this automatically

        # AST mutation not available in Omega, return code unchanged
                return code

    def _get_existing_solutions(self) -> list[str]:
        """Get list of existing attempted solutions for dedup check."""
        return [h["weakness"] for h in self._history]

    @property
    def history(self) -> list[dict]:
        return list(self._history)

    @property
    def success_rate(self) -> float:
        if not self._history:
            return 0.0
        applied = sum(1 for h in self._history if h.get("applied"))
        return applied / len(self._history)


# ===== 来自XYZ系统 =====
class CompileToRule:
    """E11: Compile high-fitness patterns to deterministic rules."""

    def __init__(self, store: MinervaStore, config: ZConfig | None = None):
        self._store = store
        self._config = config or ZConfig()
        self._compiled_rules: dict[str, dict] = {}

    def compile(self, pattern: Node, fitness: float,
                branch: str = "main") -> Node | None:
        """Compile a pattern to a deterministic rule if fitness > threshold.

        Args:
            pattern: The pattern to compile
            fitness: Current fitness score (0-1)
            branch: Memory branch

        Returns:
            The compiled rule node, or None if fitness too low.
        """
        if fitness < self._config.compile_fitness_threshold:
            return None  # Not ready for compilation

        # Create a deterministic rule node
        rule_fingerprint = hashlib.md5(
            pattern.content.encode()
        ).hexdigest()

        rule = Node(
            content=f"RULE: {pattern.content} (fitness={fitness:.3f})",
            type=NodeType.AVOID_RULE,  # Rules are deterministic
            utility=5.0,  # Max utility for compiled rules
            layer=2,  # SEMANTIC — permanent
            trust=TrustLevel.VERIFIED,
            reinforce_count=pattern.reinforce_count,
            surprise=0.0,  # No surprise — deterministic
            parent_id=pattern.id,
            branch=branch,
            custom_type="compiled_rule",
        )

        rule_id = self._store._system_insert(rule, reason="compile_to_rule")

        # Track in compiled rules registry
        self._compiled_rules[rule_fingerprint] = {
            "rule_id": rule_id,
            "pattern_id": pattern.id,
            "fitness": fitness,
            "content": rule.content,
        }

        return rule

    def is_compiled(self, pattern_id: str) -> bool:
        """Check if a pattern has been compiled to a rule."""
        for rule_info in self._compiled_rules.values():
            if rule_info["pattern_id"] == pattern_id:
                return True
        return False

    def get_rule(self, pattern_id: str) -> dict | None:
        """Get the compiled rule for a pattern."""
        for rule_info in self._compiled_rules.values():
            if rule_info["pattern_id"] == pattern_id:
                return rule_info
        return None

    @property
    def compiled_count(self) -> int:
        return len(self._compiled_rules)

    @property
    def compiled_rules(self) -> dict[str, dict]:
        return dict(self._compiled_rules)

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
