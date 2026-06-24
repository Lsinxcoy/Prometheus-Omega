"""L8 Governance - 治理层 (22宪法+5级自治+3级信任)"""
from dataclasses import dataclass, field
from typing import List, Dict
from enum import Enum


class AutonomyLevel(Enum):
    L0 = "fully_controlled"
    L1 = "human_approved"
    L2 = "advisory"
    L3 = "autonomous"
    L4 = "fully_autonomous"


class TrustLevel(Enum):
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    FULL = 4


class ConstitutionalPrinciples:
    """22宪法原则 - 来自X系统#40"""
    
    PRINCIPLES = [
        "Safety First",
        "Transparency", 
        "Accountability",
        "Fairness",
        "Privacy",
        "Security",
        "Reliability",
        "Robustness",
        "Explainability",
        "Contestability",
        "Human Oversight",
        "Value Alignment",
        "Beneficence",
        "Non-maleficence",
        "Justice",
        "Autonomy Respect",
        "Data Protection",
        "Auditability",
        "Graceful Degradation",
        "Fail-safe",
        "Transparency of Intent",
        "Stakeholder Benefit",
    ]
    
    def get_principle(self, index: int) -> str:
        return self.PRINCIPLES[index] if index < len(self.PRINCIPLES) else ""


class ConfidenceGate:
    """置信度门控 - 来自X系统#43"""
    
    def __init__(self, threshold: float = 0.7):
        self.threshold = threshold
    
    def can_proceed(self, confidence: float) -> bool:
        return confidence >= self.threshold


class EvolutionGrill:
    """进化审查7问 - 来自X系统#44"""
    
    QUESTIONS = [
        "Is this evolution safe?",
        "Does it maintain alignment?",
        "Is it reversible?",
        "Who benefits?",
        "What are the risks?",
        "Can we audit it?",
        "Does it respect values?",
    ]
    
    def ask(self, index: int) -> str:
        return self.QUESTIONS[index] if index < len(self.QUESTIONS) else ""


class DriftDetector:
    """概念漂移检测 - 来自X系统#45"""
    
    def __init__(self, window: int = 100):
        self.window = window
        self.history: List[float] = []
    
    def detect(self, value: float) -> bool:
        self.history.append(value)
        if len(self.history) > self.window:
            self.history.pop(0)
        if len(self.history) < 2:
            return False
        # 简单漂移检测
        return abs(self.history[-1] - self.history[0]) > 0.3


# 工厂
# 兼容性别名
Constitution = ConstitutionalPrinciples

def create_constitutional_principles() -> ConstitutionalPrinciples:
    return ConstitutionalPrinciples()

def create_drift_detector(**kwargs) -> DriftDetector:
    return DriftDetector(**kwargs)