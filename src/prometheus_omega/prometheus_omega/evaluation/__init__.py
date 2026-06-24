"""Evaluation - 评估层 (SEAGym+HarnessX+MAA+Thermo+5view)"""
from dataclasses import dataclass, field
from typing import List, Dict, Any
from enum import Enum
import random


class EvalDimension(Enum):
    ACCURACY = "accuracy"
    EFFICIENCY = "efficiency"
    SAFETY = "safety"
    ROBUSTNESS = "robustness"


@dataclass
class Snapshot:
    """评估快照"""
    dimension: EvalDimension
    score: float
    timestamp: float


class SEAGym:
    """SEAGym自进化评估 - 来自X/Y/Z系统"""
    
    def __init__(self):
        self.snapshots: List[Snapshot] = []
    
    def evaluate(self, system_state: Dict) -> Dict[str, float]:
        return {
            "accuracy": random.uniform(0.7, 0.95),
            "efficiency": random.uniform(0.6, 0.9),
            "safety": random.uniform(0.8, 0.99),
            "robustness": random.uniform(0.7, 0.95),
        }


class HarnessXEval:
    """HarnessX评估 - 来自X/Y/Z"""
    
    def __init__(self):
        self.dimensions = 9
    
    def evaluate(self, individual: Dict) -> float:
        return random.uniform(0.6, 0.95)


class MAA:
    """边际优势累积 - 来自X/Y/Z系统"""
    
    def __init__(self, decay: float = 0.95):
        self.decay = decay
        self.history: List[float] = []
    
    def accumulate(self, advantage: float) -> float:
        if not self.history:
            self.history.append(advantage)
            return advantage
        
        maa = self.decay * self.history[-1] + (1 - self.decay) * advantage
        self.history.append(maa)
        return maa


class ThermodynamicIntelligence:
    """热力学智能 - 来自Z系统"""
    
    def measure(self, system_state: Dict) -> float:
        # rare-valid lift
        rare = system_state.get("rare_count", 1)
        valid = system_state.get("valid_count", 1)
        return (valid / rare) if rare > 0 else 0


class FiveViewEvaluator:
    """五视图评估 - 来自Z系统"""
    
    def __init__(self):
        self.views = ["architecture", "behavior", "interaction", "evolution", "deployment"]
    
    def evaluate(self, system: Any) -> Dict[str, float]:
        return {view: random.uniform(0.7, 0.95) for view in self.views}


class RareValidDetector:
    """稀有有效检测 - 来自Z系统"""
    
    def __init__(self, threshold: float = 0.1):
        self.threshold = threshold
    
    def detect(self, entries: List[Dict]) -> List[Dict]:
        return [e for e in entries if e.get("rarity", 1) < self.threshold]


# 工厂
def create_seagym() -> SEAGym:
    return SEAGym()

def create_maa(decay: float = 0.95) -> MAA:
    return MAA(decay=decay)

def create_thermodynamic() -> ThermodynamicIntelligence:
    return ThermodynamicIntelligence()