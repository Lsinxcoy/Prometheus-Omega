"""热力学智能度量 - 基于2606.20231论文

论文核心概念：智能 = 合法放大罕见但有效的未来 (lawful amplification of rare-valid futures)
- rare-valid lift = P(rv|system) / P(rv|baseline)
- 递归自我模拟是必要条件
"""
from dataclasses import dataclass, field
from typing import Optional
import time


@dataclass
class ThermodynamicIntelligence:
    """基于热力学的智能度量"""
    
    baseline_rate: float = 0.01  # 被动系统约1% rare-valid
    
    _rare_valid_count: int = 0
    _total_outcomes: int = 0
    _history: list[dict] = field(default_factory=list)
    
    def record_outcome(self, is_rare_valid: bool, metadata: dict = None) -> None:
        """记录结果"""
        self._total_outcomes += 1
        if is_rare_valid:
            self._rare_valid_count += 1
        
        self._history.append({
            "timestamp": time.time(),
            "is_rare_valid": is_rare_valid,
            "metadata": metadata or {}
        })
        
        # 限制历史大小
        if len(self._history) > 1000:
            self._history = self._history[-500:]
    
    def compute_lift(self) -> float:
        """计算lift = P(rv|system) / P(rv|baseline)"""
        if self._total_outcomes == 0:
            return 0.0
        
        p_system = self._rare_valid_count / self._total_outcomes
        lift = p_system / self.baseline_rate
        return lift
    
    def is_intelligent(self, threshold: float = 2.0) -> bool:
        """lift > threshold表示系统具有智能"""
        return self.compute_lift() > threshold
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        return {
            "total_outcomes": self._total_outcomes,
            "rare_valid_count": self._rare_valid_count,
            "p_system": self._rare_valid_count / max(self._total_outcomes, 1),
            "baseline_rate": self.baseline_rate,
            "lift": self.compute_lift(),
            "is_intelligent": self.is_intelligent()
        }
    
    def reset(self) -> None:
        """重置"""
        self._rare_valid_count = 0
        self._total_outcomes = 0
        self._history.clear()


class RareValidDetector:
    """检测是否为"稀有有效"结果
    
    基于2606.20231的定义：
    - 稀有：在被动动力学下概率低
    - 有效：在领域约束下是可行的
    """
    
    def __init__(self, baseline_threshold: float = 0.1):
        self.baseline_threshold = baseline_threshold
        self._baseline_distribution: dict = {}
    
    def is_rare_valid(self, outcome: dict, baseline_distribution: dict = None) -> bool:
        """判断结果是否为稀有有效
        
        Args:
            outcome: 产出结果
            baseline_distribution: 基线分布（可选）
            
        Returns:
            True if rare and valid
        """
        # 检查稀有性
        if baseline_distribution:
            prob = baseline_distribution.get(outcome.get("type", "unknown"), 0.01)
            if prob > self.baseline_threshold:
                return False  # 不够稀有
        
        # 检查有效性 - 根据领域约束
        return self._validate(outcome)
    
    def _validate(self, outcome: dict) -> bool:
        """验证有效性"""
        # 基本验证：结果不为空
        if not outcome:
            return False
        
        # 可以扩展领域特定验证
        return True
    
    def update_baseline(self, distribution: dict) -> None:
        """更新基线分布"""
        self._baseline_distribution = distribution