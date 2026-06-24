"""Prometheus Z Evaluation System - 自进化评估框架

基于三篇论文的核心机制：
- 2606.20231: 热力学智能度量 (ThermodynamicIntelligence)
- 2606.17546: SEAGym五视图评估 (FiveViewEvaluator)
- 2606.20475: 边际优势累积 (MarginalAdvantageAccumulator)
"""

from prometheus_z.evaluation.thermodynamic import (
    ThermodynamicIntelligence,
    RareValidDetector
)

from prometheus_z.evaluation.five_view import (
    FiveViewEvaluator,
    Snapshot
)

from prometheus_z.evaluation.maa import (
    MarginalAdvantageAccumulator,
    OperationRecord
)

__all__ = [
    "ThermodynamicIntelligence",
    "RareValidDetector",
    "FiveViewEvaluator",
    "Snapshot",
    "MarginalAdvantageAccumulator",
    "OperationRecord"
]

__version__ = "1.0.0"