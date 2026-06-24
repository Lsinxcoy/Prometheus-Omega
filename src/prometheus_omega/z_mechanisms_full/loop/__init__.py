"""Prometheus Z Loop Engine - 自进化循环执行框架

基于Loop Engineering的核心原则：
- Loop = Harness + Schedule + State + Verification Chain
- 五大原语：Scheduling, Worktrees, Skills, Plugins, Maker/Checker

本模块提供：
- LoopStateMachine: 循环执行状态管理
- ConvergenceDetector: 收敛检测，防止无限循环
- LoopStateStore: 状态持久化，防止State Rot
"""

from prometheus_z.loop.state_machine import (
    LoopState,
    LoopExecution,
    LoopStateMachine
)

from prometheus_z.loop.convergence import (
    ConvergenceDetector,
    AdaptiveConvergenceDetector
)

from prometheus_z.loop.state_store import (
    LoopStateStore,
    LoopStateManager
)

__all__ = [
    "LoopState",
    "LoopExecution", 
    "LoopStateMachine",
    "ConvergenceDetector",
    "AdaptiveConvergenceDetector",
    "LoopStateStore",
    "LoopStateManager",
]

__version__ = "1.0.0"