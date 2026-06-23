"""Prometheus Z Hindsight集成 - 四网络记忆架构

基于Hindsight (2512.12818) 的核心机制：
- 四网络记忆：World/Experiences/Summaries/Beliefs
- 三操作：retain/recall/reflect
- Disposition：用户偏好学习
- Consolidation：自动记忆整合
"""

from prometheus_z.hindsight.four_network import (
    FourNetworkMemory,
    MemoryNetwork,
    FactType,
    MemoryFact,
    EntitySummary,
    Belief,
    create_four_network_memory
)

from prometheus_z.hindsight.disposition import (
    DispositionLearner,
    DispositionTrait,
    TraitValue,
    TraitObservation,
    DispositionTraitProfile,
    create_disposition_learner
)

from prometheus_z.hindsight.consolidation import (
    ConsolidationEngine,
    ConsolidationStrategy,
    ConsolidationStatus,
    ConsolidationTask,
    MemoryFragment,
    create_consolidation_engine
)

__all__ = [
    # 四网络记忆
    "FourNetworkMemory",
    "MemoryNetwork", 
    "FactType",
    "MemoryFact",
    "EntitySummary",
    "Belief",
    "create_four_network_memory",
    
    # Disposition
    "DispositionLearner",
    "DispositionTrait",
    "TraitValue", 
    "TraitObservation",
    "DispositionTraitProfile",
    "create_disposition_learner",
    
    # Consolidation
    "ConsolidationEngine",
    "ConsolidationStrategy",
    "ConsolidationStatus", 
    "ConsolidationTask",
    "MemoryFragment",
    "create_consolidation_engine"
]

__version__ = "1.0.0"