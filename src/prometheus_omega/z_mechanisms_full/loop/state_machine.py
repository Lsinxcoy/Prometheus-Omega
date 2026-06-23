"""Loop状态机 - 核心执行状态管理"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import time
import json
from pathlib import Path


class LoopState(Enum):
    """Loop执行状态枚举"""
    IDLE = "idle"
    DISCOVERING = "discovering"
    ACTING = "acting"
    VERIFYING = "verifying"
    ESCALATING = "escalating"
    CONVERGED = "converged"
    FAILED = "failed"


@dataclass
class LoopExecution:
    """单次Loop执行记录"""
    run_id: str
    start_time: float
    state: LoopState
    attempt: int = 0
    max_attempts: int = 3
    convergence_threshold: float = 0.01
    history: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "start_time": self.start_time,
            "state": self.state.value,
            "attempt": self.attempt,
            "max_attempts": self.max_attempts,
            "convergence_threshold": self.convergence_threshold,
            "history": self.history,
            "errors": self.errors
        }


class LoopStateMachine:
    """Loop执行状态机 - 核心组件
    
    严格遵守宪法铁律：
    - DopamineWriteGate: 防止无限制自我强化
    - AntiEvolutionGate: 防止危险变异
    - VerificationIronLaw: 必须有独立验证
    """
    
    def __init__(self, loop_id: str, max_attempts: int = 3,
                 convergence_threshold: float = 0.01):
        self.loop_id = loop_id
        self.max_attempts = max_attempts
        self.convergence_threshold = convergence_threshold
        self.executions: dict[str, LoopExecution] = {}
        self._current: LoopExecution | None = None
        
    def start(self) -> LoopExecution:
        """开始新的Loop执行"""
        run_id = f"{self.loop_id}_{int(time.time())}"
        exec = LoopExecution(
            run_id=run_id,
            start_time=time.time(),
            state=LoopState.DISCOVERING,
            max_attempts=self.max_attempts,
            convergence_threshold=self.convergence_threshold
        )
        self.executions[run_id] = exec
        self._current = exec
        return exec
    
    def transition(self, new_state: LoopState, metadata: dict = None):
        """状态转换"""
        if not self._current:
            return
        
        # 支持字符串或枚举
        if isinstance(new_state, str):
            new_state = LoopState(new_state)
        
        self._current.state = new_state
        if metadata:
            self._current.history.append({
                "state": new_state.value,
                "timestamp": time.time(),
                "metadata": metadata or {}
            })
    
    def increment_attempt(self) -> int:
        """增加尝试次数"""
        if self._current:
            self._current.attempt += 1
            return self._current.attempt
        return 0
    
    def record_error(self, error: str) -> None:
        """记录错误"""
        if self._current:
            self._current.errors.append({
                "time": time.time(),
                "error": error
            })
    
    def should_continue(self) -> tuple[bool, str]:
        """判断是否继续循环 - 宪法铁律核心"""
        if not self._current:
            return False, "No active execution"
        
        # 宪法铁律1: 尝试次数限制 (DopamineWriteGate)
        if self._current.attempt >= self._current.max_attempts:
            return False, "max_attempts_reached"
        
        # 收敛检测
        if len(self._current.history) >= 2:
            recent = self._current.history[-1]
            previous = self._current.history[-2]
            
            recent_score = recent.get("metadata", {}).get("score", None)
            previous_score = previous.get("metadata", {}).get("score", None)
            
            if recent_score is not None and previous_score is not None:
                improvement = abs(recent_score - previous_score)
                if improvement < self._current.convergence_threshold:
                    self.transition(LoopState.CONVERGED)
                    return False, "converged"
        
        return True, "continue"
    
    def escalate_to_human(self) -> dict:
        """升级到人工审核 - VerificationIronLaw"""
        self.transition(LoopState.ESCALATING)
        return {
            "loop_id": self.loop_id,
            "run_id": self._current.run_id if self._current else None,
            "reason": "requires_human_review",
            "attempt": self._current.attempt if self._current else 0,
            "max_attempts": self.max_attempts,
            "history": self._current.history if self._current else [],
            "errors": self._current.errors if self._current else [],
            "requires_human": True
        }
    
    def get_status(self) -> dict:
        """获取当前状态"""
        if not self._current:
            return {"state": "idle", "loop_id": self.loop_id}
        
        return {
            "loop_id": self.loop_id,
            "run_id": self._current.run_id,
            "state": self._current.state.value,
            "attempt": self._current.attempt,
            "max_attempts": self._current.max_attempts,
            "can_continue": self.should_continue()[0]
        }