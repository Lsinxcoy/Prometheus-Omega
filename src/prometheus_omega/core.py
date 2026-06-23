"""Prometheus Ω - 核心编排引擎

整合XYZ全部机制的最高层协调器
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timezone
from enum import Enum
import uuid

# 从foundation导入Config
from prometheus_omega.foundation import Config

# 导入3铁律（来自Z系统的真实实现）
from prometheus_omega.z_mechanisms.iron_laws import (
    DopamineWriteGate,
    AntiEvolutionGate,
    VerificationIronLaw,
    OmegaNode,
    OmegaConfig,
    MemoryLayer,
    WriteGateResult,
    EvolutionCheckResult,
)


class OmegaState(Enum):
    """Ω系统状态"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    EVOLVING = "evolving"
    ERROR = "error"
    STOPPED = "stopped"


class OmegaContext:
    """Ω执行上下文"""
    
    def __init__(self, session_id: str, user_id: Optional[str] = None, 
                 request_id: str = None, created_at: datetime = None,
                 metadata: Dict[str, Any] = None):
        self.session_id = session_id
        self.user_id = user_id
        self.request_id = request_id or str(uuid.uuid4())
        self.created_at = created_at or datetime.now(timezone.utc)
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "request_id": self.request_id,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata
        }


class OmegaResponse:
    """Ω系统响应"""
    
    def __init__(self, success: bool, data: Any = None, 
                 error: str = None, context: OmegaContext = None,
                 execution_time_ms: float = 0.0):
        self.success = success
        self.data = data
        self.error = error
        self.context = context
        self.execution_time_ms = execution_time_ms
    
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
        # 导入3铁律（来自Z系统）
        from prometheus_omega.z_mechanisms.iron_laws import (
            DopamineWriteGate, AntiEvolutionGate, VerificationIronLaw, OmegaConfig
        )
        
        # 配置
        user_config = config or {}
        
        # === 初始化3铁律（来自Z系统） ===
        self.omega_config = OmegaConfig()
        self.write_gate = DopamineWriteGate(self.omega_config)
        self.anti_evolution_gate = AntiEvolutionGate(self.omega_config)
        self.verification_law = VerificationIronLaw(self.omega_config)
        
        # 自定义配置（使用默认值避免依赖Config类）
        self.ga_population_size = user_config.get("ga_population_size", 100)
        self.convergence_threshold = user_config.get("convergence_threshold", 0.01)
        self.max_sessions = user_config.get("max_sessions", 1000)
        self.enable_evolution = user_config.get("enable_evolution", True)
        self.enable_monitoring = user_config.get("enable_monitoring", True)
        
        # === 最小化核心组件（避免依赖空壳） ===
        # 简单事件总线（替代EventBus）
        self.event_bus = _SimpleEventBus()
        
        # 内存/检索/进化暂时设为None，懒加载
        self.memory = None
        self.retrieval = None
        self.evolution_engine = None
        self.convergence_detector = None
        
        # 简化的治理（替代ConstitutionalPrinciples）
        self.governance = _SimpleGovernance()
        
        # 其他组件
        self.harness_x = None
        self.dag_executor = None
        self.denylist = _SimpleDenylist()
        
        # 状态
        self.state = OmegaState.INITIALIZING
        self.sessions: Dict[str, OmegaContext] = {}
        
        # 统计
        self.stats = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_failed": 0,
            "memory_entries": 0,
            "evolutions": 0,
            "writes_rejected": 0,
            "evolutions_rejected": 0,
        }
        
        self._initialize()
    
    def _initialize(self):
        """初始化所有组件"""
        # 尝试懒加载其他组件（如果可用）
        try:
            from prometheus_omega.memory import FourNetworkMemory
            self.memory = FourNetworkMemory()
        except Exception as e:
            print(f"Warning: FourNetworkMemory not available: {e}")
        
        try:
            from prometheus_omega.retrieval import PolyphonicRetrieval
            self.retrieval = PolyphonicRetrieval()
        except Exception as e:
            print(f"Warning: PolyphonicRetrieval not available: {e}")
        
        try:
            from prometheus_omega.evolution import GeneticAlgorithm, ConvergenceDetector
            self.evolution_engine = GeneticAlgorithm(population_size=self.ga_population_size)
            self.convergence_detector = ConvergenceDetector(threshold=self.convergence_threshold)
        except Exception as e:
            print(f"Warning: Evolution engine not available: {e}")
        
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
        if "path" in request:
            if not self.denylist.is_allowed(request["path"]):
                return False
        
        content = str(request.get("content", ""))
        dangerous_patterns = ["eval(", "exec(", "__import__("]
        for pattern in dangerous_patterns:
            if pattern in content:
                self.event_bus.publish("security.dangerous_pattern", {"pattern": pattern})
                return False
        
        return True
    
    def _write_memory(self, request: Dict, context: OmegaContext) -> Dict:
        """写入记忆 - 带DopamineWriteGate门控"""
        from prometheus_omega.z_mechanisms.iron_laws import OmegaNode, MemoryLayer
        
        content = request.get("content", "")
        importance = request.get("importance", 0.5)
        surprise = request.get("surprise", 0.5)
        
        # === Iron Law 1: DopamineWriteGate 门控检查 ===
        node = OmegaNode(
            content=content,
            utility=importance * 5.0,
            surprise=surprise,
            layer=MemoryLayer.EPISODIC,
        )
        
        gate_result = self.write_gate.should_write(node)
        
        if not gate_result.allowed:
            self.stats["writes_rejected"] += 1
            return {
                "entry_id": None,
                "status": "rejected",
                "reason": gate_result.reason,
                "gate_value": gate_result.gate_value,
            }
        
        # 写入通过
        entry_id = str(uuid.uuid4())
        self.stats["memory_entries"] += 1
        self.event_bus.publish("memory.written", {"entry_id": entry_id})
        
        return {"entry_id": entry_id, "status": "written", "gate_value": gate_result.gate_value}
    
    def _read_memory(self, request: Dict, context: OmegaContext) -> Dict:
        """读取记忆"""
        entry_id = request.get("entry_id")
        return {"results": [], "count": 0}
    
    def _search_memory(self, request: Dict, context: OmegaContext) -> Dict:
        """搜索记忆"""
        return {"results": [], "count": 0}
    
    def _execute_task(self, request: Dict, context: OmegaContext) -> Dict:
        """执行任务"""
        return {"status": "executed", "results": []}
    
    def _evolve(self, request: Dict, context: OmegaContext) -> Dict:
        """执行进化 - 带AntiEvolutionGate门控"""
        
        hypothesis = request.get("hypothesis", "")
        existing_solutions = request.get("existing_solutions", [])
        
        # === Iron Law 2: AntiEvolutionGate 前提检查 ===
        if hypothesis:
            gate_result = self.anti_evolution_gate.gate_check(
                hypothesis, existing_solutions
            )
            
            if not gate_result.passed:
                self.stats["evolutions_rejected"] += 1
                return {
                    "status": "rejected",
                    "reason": gate_result.reason,
                    "prerequisites_failed": gate_result.prerequisites_failed,
                }
        
        self.stats["evolutions"] += 1
        self.event_bus.publish("evolution.completed", {"generation": self.stats["evolutions"]})
        
        return {
            "status": "evolved",
            "generation": self.stats["evolutions"],
            "fitness": request.get("fitness", 0.5)
        }
    
    def _query(self, request: Dict, context: OmegaContext) -> Dict:
        """通用查询"""
        return {"results": []}
    
    def shutdown(self):
        """关闭系统"""
        self.state = OmegaState.STOPPED
        self.event_bus.publish("omega.shutdown", {})


class _SimpleEventBus:
    """简化事件总线"""
    def __init__(self):
        self._subscribers = {}
    
    def subscribe(self, event: str, callback):
        if event not in self._subscribers:
            self._subscribers[event] = []
        self._subscribers[event].append(callback)
    
    def publish(self, event: str, data: dict):
        for cb in self._subscribers.get(event, []):
            try:
                cb(data)
            except:
                pass


class _SimpleGovernance:
    """简化治理"""
    def __init__(self):
        self.principles = []
    
    def check(self, action: str) -> bool:
        return True


class _SimpleDenylist:
    """简化黑名单"""
    def __init__(self):
        self._blocked = set()
    
    def is_allowed(self, path: str) -> bool:
        return True
    
    def add(self, path: str):
        self._blocked.add(path)
    
