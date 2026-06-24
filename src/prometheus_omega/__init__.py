"""Prometheus Ω - 最强自进化AI记忆系统

整合XYZ全部优势机制:
- X系统: 70+机制, 12层架构, 585测试
- Y系统: 5项前沿研究, 宪法+刑法
- Z系统: Loop Engineering, Hindsight, 最新论文
"""
__version__ = "1.0.0-Ω"

import sys
from pathlib import Path

# 版本信息
__version__ = "1.0.0-Ω"
__author__ = "Prometheus Ω Team"

# 确保src在path中
_package_path = Path(__file__).parent
if str(_package_path) not in sys.path:
    sys.path.insert(0, str(_package_path))

# 延迟导入避免循环依赖
def __getattr__(name):
    if name in ["OmegaCore", "create_omega_system"]:
        from prometheus_omega.foundation import Config
        class OmegaCore:
            def __init__(self, config):
                self.config = config
        def create_omega_system(config=None):
            return OmegaCore(Config() if config is None else Config(**config))
        return OmegaCore if name == "OmegaCore" else create_omega_system
    
    # Foundation
    if name in ["create_uuid", "Config", "EventBus", "DeterministicRuleEngine"]:
        from prometheus_omega.foundation import create_uuid, Config, EventBus, DeterministicRuleEngine
        return locals()[name]
    
    # Memory
    if name in ["UnifiedEntry", "FourNetworkMemory", "Bank", "MemoryStore"]:
        from prometheus_omega.memory import UnifiedEntry, FourNetworkMemory, Bank, MemoryStore
        return locals()[name]
    
    # Evolution
    if name in ["GeneticAlgorithm", "ConvergenceDetector", "UCB1Bandit"]:
        from prometheus_omega.evolution import GeneticAlgorithm, ConvergenceDetector, UCB1Bandit
        return locals()[name]
    
    # Retrieval
    if name in ["PolyphonicRetrieval", "RRF"]:
        from prometheus_omega.retrieval import PolyphonicRetrieval, RRF
        return locals()[name]
    
    # Ecosystem
    if name in ["HarnessX", "LotkaVolterra", "FGGM"]:
        from prometheus_omega.ecosystem import HarnessX, LotkaVolterra, FGGM
        return locals()[name]
    
    # Execution
    if name in ["DAGExecutor"]:
        from prometheus_omega.execution import DAGExecutor
        return locals()[name]
    
    # Governance
    if name in ["ConstitutionalPrinciples"]:
        from prometheus_omega.governance import ConstitutionalPrinciples
        return locals()[name]
    
    # Evaluation
    if name in ["SEAGym", "MAA", "ThermodynamicIntelligence", "FiveViewEvaluator"]:
        from prometheus_omega.evaluation import SEAGym, MAA, ThermodynamicIntelligence, FiveViewEvaluator
        return locals()[name]
    
    # Safety
    if name in ["Denylist", "RateLimiter", "FourLayerDefense"]:
        from prometheus_omega.safety import Denylist, RateLimiter, FourLayerDefense
        return locals()[name]
    
    # Skills
    if name in ["SkillRegistry", "Curator"]:
        from prometheus_omega.skills import SkillRegistry, Curator
        return locals()[name]
    
    raise AttributeError(f"module has no attribute '{name}'")


__all__ = [
    "__version__",
    "OmegaCore", 
    "create_omega_system",
    "create_uuid",
    "Config", 
    "EventBus",
    "DeterministicRuleEngine",
    "UnifiedEntry",
    "FourNetworkMemory",
    "Bank",
    "MemoryStore",
    "GeneticAlgorithm",
    "ConvergenceDetector",
    "UCB1Bandit",
    "PolyphonicRetrieval",
    "RRF",
    "HarnessX",
    "LotkaVolterra",
    "FGGM",
    "DAGExecutor",
    "ConstitutionalPrinciples",
    "SEAGym",
    "MAA",
    "ThermodynamicIntelligence",
    "FiveViewEvaluator",
    "Denylist",
    "RateLimiter",
    "FourLayerDefense",
    "SkillRegistry",
    "Curator",
]