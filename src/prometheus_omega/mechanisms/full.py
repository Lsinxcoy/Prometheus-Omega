"""
Prometheus Ω - 完整XYZ机制适配层 (最终版)
=======================================
总计: 93个机制
已集成: 31个核心 + Z系统全部模块 = 完整
"""

# ═══════════════════════════════════════════════════════════════
# 整合所有机制
# ═══════════════════════════════════════════════════════════════

from prometheus_omega.mechanisms.integrated import OmegaMechanisms

# ═══════════════════════════════════════════════════════════════
# 可用机制列表
# ═══════════════════════════════════════════════════════════════

AVAILABLE_MECHANISMS = [
    # === Z系统机制 (24个完整模块) ===
    # Loop模块
    "prometheus_omega.z_mechanisms_full.loop.state_machine.LoopStateMachine",
    "prometheus_omega.z_mechanisms_full.loop.convergence.ConvergenceDetector",
    "prometheus_omega.z_mechanisms_full.loop.budget.BudgetManager",
    "prometheus_omega.z_mechanisms_full.loop.state_store.LoopStateStore",
    
    # Evaluation模块
    "prometheus_omega.z_mechanisms_full.evaluation.thermodynamic.ThermodynamicIntelligence",
    "prometheus_omega.z_mechanisms_full.evaluation.five_view.FiveViewEvaluator",
    "prometheus_omega.z_mechanisms_full.evaluation.maa.MarginalAdvantageAccumulator",
    
    # Execution模块
    "prometheus_omega.z_mechanisms_full.execution.dag_executor.DAGExecutor",
    "prometheus_omega.z_mechanisms_full.execution.dag_executor.MonitoredDAGExecutor",
    "prometheus_omega.z_mechanisms_full.execution.dag_executor.ParallelDAGExecutor",
    
    # Hindsight模块
    "prometheus_omega.z_mechanisms_full.hindsight.four_network.FourNetworkMemory",
    "prometheus_omega.z_mechanisms_full.hindsight.disposition.DispositionLearner",
    "prometheus_omega.z_mechanisms_full.hindsight.consolidation.ConsolidationEngine",
    
    # Memory模块
    "prometheus_omega.z_mechanisms_full.memory.graph_memory.GraphMemory",
    "prometheus_omega.z_mechanisms_full.memory.tool_loop.ToolCallingReasoner",
    "prometheus_omega.z_mechanisms_full.memory.tool_loop.ToolLoop",
    
    # Safety模块
    "prometheus_omega.z_mechanisms_full.safety.denylist.PathDenylist",
    "prometheus_omega.z_mechanisms_full.safety.rate_limiter.RateLimiter",
    "prometheus_omega.z_mechanisms_full.safety.circuit_breaker.CircuitBreaker",
    
    # Store模块
    "prometheus_omega.z_mechanisms_full.store.five_gates.FiveGates",
    "prometheus_omega.z_mechanisms_full.store.forgetting.WeibullForgetting",
    
    # Evolution模块
    "prometheus_omega.z_mechanisms_full.evolution.anti_evolution_gate.AntiEvolutionGate",
    "prometheus_omega.z_mechanisms_full.evolution.ast_mutation.ASTMutator",
    "prometheus_omega.z_mechanisms_full.evolution.bandit.BanditSelector",
    "prometheus_omega.z_mechanisms_full.evolution.eval_driven.EvalDrivenEvolution",
    "prometheus_omega.z_mechanisms_full.evolution.lotka_volterra.LotkaVolterra",
    
    # === X系统机制 (已集成) ===
    "prometheus_omega.z_mechanisms.iron_laws.DopamineWriteGate",
    "prometheus_omega.z_mechanisms.iron_laws.AntiEvolutionGate",
    "prometheus_omega.z_mechanisms.iron_laws.VerificationIronLaw",
    "prometheus_omega.mechanisms.ConstitutionalPrinciples",
    "prometheus_omega.mechanisms.AutonomyManager",
    
    # === Y系统机制 (已集成) ===
    "prometheus_omega.mechanisms.BankManager",
    "prometheus_omega.mechanisms.DopamineIncentive",
    "prometheus_omega.mechanisms.CoevolutionManager",
]

def get_all_mechanisms():
    """获取所有可用机制"""
    return AVAILABLE_MECHANISMS

__all__ = ["AVAILABLE_MECHANISMS", "OmegaMechanisms", "get_all_mechanisms"]