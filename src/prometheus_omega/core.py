"""Prometheus Ω - 核心编排引擎

整合XYZ全部机制的最高层协调器
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timezone
from enum import Enum
import uuid

# 延迟导入避免循环依赖
def _lazy_import():
    global OmegaCore, UnifiedEntry, FourNetworkMemory
    global PolyphonicRetrieval, GeneticAlgorithm, ConvergenceDetector
    global ConstitutionalPrinciples, HarnessX, DAGExecutor
    global Config, EventBus, Denylist
    
    from prometheus_omega import (
        Config, EventBus, create_uuid,
        UnifiedEntry, FourNetworkMemory,
        PolyphonicRetrieval,
        GeneticAlgorithm, ConvergenceDetector,
        ConstitutionalPrinciples, HarnessX, DAGExecutor,
        Denylist
    )


class OmegaState(Enum):
    """Ω系统状态"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    EVOLVING = "evolving"
    ERROR = "error"
    STOPPED = "stopped"


@dataclass
class OmegaContext:
    """Ω执行上下文"""
    session_id: str
    user_id: Optional[str] = None
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "request_id": self.request_id,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class OmegaResponse:
    """Ω系统响应"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    context: Optional[OmegaContext] = None
    execution_time_ms: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms
        }


class OmegaCore:
    """Prometheus Ω 核心引擎
    
    整合XYZ全部优势机制的最高层协调器
    """
    
    def __init__(self, config: Optional[Dict] = None):
        _lazy_import()
        
        # 配置
        user_config = config or {}
        self.config = Config()
        
        # 自定义配置
        self.ga_population_size = user_config.get("ga_population_size", 100)
        self.convergence_threshold = user_config.get("convergence_threshold", 0.01)
        self.max_sessions = user_config.get("max_sessions", 1000)
        self.enable_evolution = user_config.get("enable_evolution", True)
        self.enable_monitoring = user_config.get("enable_monitoring", True)
        
        # 核心组件
        self.event_bus = EventBus()
        self.memory: Optional[FourNetworkMemory] = None
        self.retrieval: Optional[PolyphonicRetrieval] = None
        self.evolution_engine: Optional[GeneticAlgorithm] = None
        self.convergence_detector: Optional[ConvergenceDetector] = None
        self.governance = ConstitutionalPrinciples()
        self.harness_x = HarnessX()
        self.dag_executor = DAGExecutor()
        self.denylist = Denylist()
        
        # 状态
        self.state = OmegaState.INITIALIZING
        self.sessions: Dict[str, OmegaContext] = {}
        
        # 统计
        self.stats = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_failed": 0,
            "memory_entries": 0,
            "evolutions": 0
        }
        
        self._initialize()
    
    def _initialize(self):
        """初始化所有组件"""
        # 初始化记忆
        self.memory = FourNetworkMemory()
        
        # 初始化检索
        self.retrieval = PolyphonicRetrieval()
        
        # 初始化进化引擎
        self.evolution_engine = GeneticAlgorithm(
            population_size=self.ga_population_size
        )
        
        # 初始化收敛检测
        self.convergence_detector = ConvergenceDetector(
            threshold=self.convergence_threshold
        )
        
        self.state = OmegaState.RUNNING
        self.event_bus.publish("omega.initialized", {"version": "1.0.0-Ω"})
    
    def create_session(self, user_id: Optional[str] = None) -> OmegaContext:
        """创建新会话"""
        session_id = str(uuid.uuid4())
        context = OmegaContext(session_id=session_id, user_id=user_id)
        self.sessions[session_id] = context
        return context
    
    def process_request(self, request: Dict) -> OmegaResponse:
        """处理请求"""
        import time
        start_time = time.time()
        
        self.stats["requests_total"] += 1
        
        try:
            # 1. 安全检查
            if not self._security_check(request):
                return OmegaResponse(
                    success=False,
                    error="Security check failed",
                    execution_time_ms=(time.time()-start_time)*1000
                )
            
            # 2. 获取或创建会话
            session_id = request.get("session_id")
            if session_id not in self.sessions:
                session_id = self.create_session(user_id=request.get("user_id")).session_id
            
            context = self.sessions[session_id]
            
            # 3. 处理请求
            action = request.get("action", "query")
            
            if action == "write_memory":
                result = self._write_memory(request, context)
            elif action == "read_memory":
                result = self._read_memory(request, context)
            elif action == "search_memory":
                result = self._search_memory(request, context)
            elif action == "execute_task":
                result = self._execute_task(request, context)
            elif action == "evolve":
                result = self._evolve(request, context)
            else:
                result = self._query(request, context)
            
            self.stats["requests_success"] += 1
            
            return OmegaResponse(
                success=True,
                data=result,
                context=context,
                execution_time_ms=(time.time()-start_time)*1000
            )
            
        except Exception as e:
            self.stats["requests_failed"] += 1
            return OmegaResponse(
                success=False,
                error=str(e),
                execution_time_ms=(time.time()-start_time)*1000
            )
    
    def _security_check(self, request: Dict) -> bool:
        """安全检查"""
        # 路径黑名单检查
        if "path" in request:
            if not self.denylist.is_allowed(request["path"]):
                return False
        
        # 内容安全检查 (简化)
        content = str(request.get("content", ""))
        dangerous_patterns = ["eval(", "exec(", "__import__("]
        for pattern in dangerous_patterns:
            if pattern in content:
                self.event_bus.publish("security.dangerous_pattern", {"pattern": pattern})
                return False
        
        return True
    
    def _write_memory(self, request: Dict, context: OmegaContext) -> Dict:
        """写入记忆"""
        content = request.get("content", "")
        importance = request.get("importance", 0.5)
        
        entry = UnifiedEntry(
            content=content,
            importance=importance,
            category=request.get("category", "experience")
        )
        
        self.memory.retain(content, network=None)
        
        self.stats["memory_entries"] += 1
        self.event_bus.publish("memory.written", {"entry_id": entry.id})
        
        return {"entry_id": entry.id, "status": "written"}
    
    def _read_memory(self, request: Dict, context: OmegaContext) -> Dict:
        """读取记忆"""
        entry_id = request.get("entry_id")
        
        results = self.memory.recall(entry_id)
        
        return {
            "results": [{"content": str(r)} for r in results],
            "count": len(results)
        }
    
    def _search_memory(self, request: Dict, context: OmegaContext) -> Dict:
        """搜索记忆"""
        query = request.get("query", "")
        top_k = request.get("top_k", 10)
        
        results = self.retrieval.retrieve(query, self.memory, top_k)
        
        return {
            "results": [{"id": r.entry_id, "score": r.score} for r in results],
            "count": len(results)
        }
    
    def _execute_task(self, request: Dict, context: OmegaContext) -> Dict:
        """执行任务"""
        task = request.get("task", {})
        
        # 使用DAG执行
        self.dag_executor.add_node(
            task.get("id", "task_1"),
            task.get("name", "task"),
            task.get("depends_on", [])
        )
        
        results = self.dag_executor.execute()
        
        return {"status": "executed", "results": results}
    
    def _evolve(self, request: Dict, context: OmegaContext) -> Dict:
        """执行进化"""
        # 检查收敛
        fitness = request.get("fitness", 0.5)
        
        if self.convergence_detector.check(fitness):
            return {"status": "converged", "fitness": fitness}
        
        # 执行一代进化
        self.evolution_engine.evolve(
            lambda genes: genes.get("fitness", fitness)
        )
        
        self.stats["evolutions"] += 1
        self.event_bus.publish("evolution.completed", {"generation": self.stats["evolutions"]})
        
        return {
            "status": "evolved",
            "generation": self.stats["evolutions"],
            "fitness": fitness
        }
    
    def _query(self, request: Dict, context: OmegaContext) -> Dict:
        """通用查询"""
        query = request.get("query", "")
        
        # 检索相关记忆
        search_results = self.retrieval.retrieve(query, self.memory, top_k=5)
        
        # 使用HarnessX评估
        evaluation = self.harness_x.evaluate({
            "accuracy": 0.8,
            "efficiency": 0.7,
            "safety": 0.9,
            "robustness": 0.8,
            "explainability": 0.7,
            "fairness": 0.8,
            "privacy": 0.9,
            "reliability": 0.8,
            "usability": 0.7
        })
        
        return {
            "query": query,
            "results": [{"id": r.entry_id, "score": r.score} for r in search_results],
            "evaluation": evaluation
        }
    
    def get_status(self) -> Dict:
        """获取系统状态"""
        return {
            "state": self.state.value,
            "stats": self.stats,
            "sessions": len(self.sessions),
            "memory_entries": self.stats["memory_entries"],
            "evolutions": self.stats["evolutions"]
        }
    
    def shutdown(self):
        """关闭系统"""
        self.state = OmegaState.STOPPED
        self.event_bus.publish("omega.shutdown", {})


def create_omega_system(config: Optional[Dict] = None) -> OmegaCore:
    """创建Ω系统实例"""
    return OmegaCore(config)


# 默认配置
DEFAULT_CONFIG = {
    "max_memory_size": 100000,
    "ga_population_size": 100,
    "convergence_threshold": 0.01,
    "max_sessions": 1000,
    "enable_evolution": True,
    "enable_monitoring": True
}