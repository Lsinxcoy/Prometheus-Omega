"""L4 Lifecycle - 生命周期层

整合XYZ机制:
- X: Weibull遗忘(5-tier), 4层Bank迁移, ZeroLLM, DopamineWriteGate
- Y: Consolidation, Bank
- Z: ConsolidationEngine
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta
from enum import Enum
import math
import random


class ForgettingStrategy(Enum):
    """遗忘策略"""
    WEIBULL = "weibull"      # 威布尔分布
    EXPONENTIAL = "exponential"
    LINEAR = "linear"


class WeibullForgetting:
    """Weibull遗忘 - 来自X系统#7
    
    5层参数:
    - shape (k): 曲线形状
    - scale (lambda): 尺度
    - threshold: 遗忘阈值
    - decay_rate: 衰减率
    - min_importance: 最低重要性
    """
    
    def __init__(self, 
                 shape: float = 1.5,      # k
                 scale: float = 30.0,     # lambda (天)
                 threshold: float = 0.1,
                 decay_rate: float = 0.05,
                 min_importance: float = 0.1):
        self.shape = shape
        self.scale = scale
        self.threshold = threshold
        self.decay_rate = decay_rate
        self.min_importance = min_importance
    
    def calculate(self, days_since_access: int, initial_importance: float) -> float:
        """计算当前重要性"""
        if days_since_access == 0:
            return initial_importance
        
        # Weibull分布: f(t) = (k/lambda) * (t/lambda)^(k-1) * e^(-(t/lambda)^k)
        t = days_since_access
        k = self.shape
        lmbda = self.scale
        
        # 记忆强度
        strength = math.exp(-((t / lmbda) ** k))
        current_importance = initial_importance * strength
        
        return max(current_importance, self.min_importance)
    
    def should_forget(self, entry) -> bool:
        """判断是否应该遗忘"""
        now = datetime.now(timezone.utc)
        days = (now - entry.last_accessed).days
        current = self.calculate(days, entry.importance)
        return current < self.threshold


class BankMigration:
    """Bank迁移 - 来自X系统#8"""
    
    def __init__(self, bank):
        self.bank = bank
    
    def auto_migrate(self) -> Dict[str, int]:
        """自动迁移"""
        return {"migrated": self.bank.migrate()}


class Consolidation:
    """记忆整合 - 来自X/Y/Z系统"""
    
    def __init__(self, interval_hours: int = 6):
        self.interval_hours = interval_hours
        self.last_consolidation = datetime.now(timezone.utc)
    
    def should_consolidate(self) -> bool:
        """是否应该整合"""
        now = datetime.now(timezone.utc)
        hours = (now - self.last_consolidation).total_seconds() / 3600
        return hours >= self.interval_hours
    
    def consolidate(self, memory_store) -> Dict[str, any]:
        """执行整合"""
        if not self.should_consolidate():
            return {"status": "skipped", "reason": "not_due"}
        
        # 简化整合
        entries = list(memory_store.entries.values())
        
        # 按主题聚类
        topics: Dict[str, List] = {}
        for entry in entries:
            for tag in entry.tags:
                if tag not in topics:
                    topics[tag] = []
                topics[tag].append(entry)
        
        self.last_consolidation = datetime.now(timezone.utc)
        
        return {
            "status": "completed",
            "entries_processed": len(entries),
            "topics_identified": len(topics),
        }


class ZeroLLM:
    """ZeroLLM生命周期 - 来自X系统#10
    
    防止外部LLM无限调用的保护机制
    """
    
    def __init__(self, max_calls_per_day: int = 1000):
        self.max_calls = max_calls_per_day
        self.today_calls = 0
        self.last_reset = datetime.now(timezone.utc).date()
    
    def can_call_llm(self) -> bool:
        """是否可以调用LLM"""
        self._check_reset()
        return self.today_calls < self.max_calls
    
    def record_call(self):
        """记录调用"""
        self._check_reset()
        self.today_calls += 1
    
    def _check_reset(self):
        """检查并重置"""
        today = datetime.now(timezone.utc).date()
        if today > self.last_reset:
            self.today_calls = 0
            self.last_reset = today
    
    def get_remaining(self) -> int:
        """剩余调用次数"""
        self._check_reset()
        return max(0, self.max_calls - self.today_calls)


class DopamineWriteGate:
    """多巴胺写入门控 - 来自X/Y系统#11
    
    根据内容质量(importance * utility * veracity)和多巴胺水平决定是否允许写入
    """
    
    def __init__(self, threshold: float = 0.3, tau: float = 1.0):
        self.threshold = threshold
        self.tau = tau  # 质量阈值
        self.dopamine_level = 0.5
    
    def can_write(self, node) -> bool:
        """是否可以写入
        
        Args:
            node: OmegaNode对象或content_quality浮点数(向后兼容)
        """
        # 向后兼容: 如果是浮点数，直接使用
        if isinstance(node, (int, float)):
            content_quality = node
        else:
            # 从OmegaNode提取质量指标
            importance = getattr(node, 'importance', 0.5)
            utility = getattr(node, 'utility', 0.0)
            veracity = getattr(node, 'veracity', 0.5)
            
            # 计算综合质量分数 (0-1范围)
            content_quality = importance * veracity * (0.5 + utility / 20.0)
        
        # 门控: 质量必须超过阈值
        return content_quality >= self.tau
    
    def should_write(self, node) -> bool:
        """别名方法，用于与Z系统兼容"""
        return self.can_write(node)
    
    def stimulate(self, amount: float = 0.1):
        """刺激多巴胺"""
        self.dopamine_level = min(1.0, self.dopamine_level + amount)
    
    def deplete(self, amount: float = 0.05):
        """消耗多巴胺"""
        self.dopamine_level = max(0.0, self.dopamine_level - amount)


class CasesToSkills:
    """案例到技能自动学习 - 来自X系统#12"""
    
    def __init__(self, min_cases: int = 5):
        self.min_cases = min_cases
        self.cases: Dict[str, List] = {}  # pattern -> cases
    
    def add_case(self, pattern: str, case: Dict):
        """添加案例"""
        if pattern not in self.cases:
            self.cases[pattern] = []
        self.cases[pattern].append(case)
    
    def extract_skill(self, pattern: str) -> Optional[Dict]:
        """提取技能"""
        cases = self.cases.get(pattern, [])
        if len(cases) < self.min_cases:
            return None
        
        return {
            "pattern": pattern,
            "examples": cases[:self.min_cases],
            "confidence": len(cases) / 10.0,
        }


# 工厂
def create_weibull_forgetting(**kwargs) -> WeibullForgetting:
    return WeibullForgetting(**kwargs)

def create_consolidation(interval_hours: int = 6) -> Consolidation:
    return Consolidation(interval_hours=interval_hours)

def create_zero_llm(max_calls: int = 1000) -> ZeroLLM:
    return ZeroLLM(max_calls_per_day=max_calls)

def create_dopamine_gate(threshold: float = 0.3) -> DopamineWriteGate:
    return DopamineWriteGate(threshold=threshold)