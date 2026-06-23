"""边际优势累积 - 基于2606.20475论文

论文核心概念：MAA (Marginal Advantage Accumulation)
- 问题：同一记忆操作在不同batch中收到矛盾反馈
- 解决方案：
  1. alignability + comparability 结构条件
  2. 构建差分信号使跨batch可比
  3. 通过EMA累积signed evidence
  4. 语义身份合并确保跨batch可追溯

结果：14/16设置最佳，减少75% token消耗
"""
from dataclasses import dataclass, field
from typing import Optional
import time


@dataclass
class OperationRecord:
    """操作记录"""
    operation: str
    batch_id: int
    advantage: float
    timestamp: float
    context: dict = field(default_factory=dict)


class MarginalAdvantageAccumulator:
    """MAA for memory operations
    
    核心思想：不是只看单次反馈，而是累积跨batch的signed evidence
    """
    
    def __init__(self, ema_alpha: float = 0.1, 
                 alignability_threshold: float = 0.05):
        self.ema_alpha = ema_alpha
        self.alignability_threshold = alignability_threshold
        
        # 每个操作的累积优势
        self._operation_advantages: dict[str, float] = {}
        self._operation_counts: dict[str, int] = {}
        
        # 历史记录
        self._history: list[OperationRecord] = []
        
        # 差分信号缓冲
        self._previous_batch_scores: dict[str, float] = {}
    
    def record(self, operation: str, batch_id: int, 
               current_score: float, previous_score: float,
               context: dict = None) -> None:
        """记录操作的边际优势
        
        Args:
            operation: 操作名称
            batch_id: 批次ID
            current_score: 当前batch得分
            previous_score: 前一个batch得分
            context: 额外上下文
        """
        # 计算差分信号（使跨batch可比）
        differential_signal = current_score - previous_score
        
        # 关键：需要标准化处理，使不同batch的信号可比
        # 这里简化为直接使用差分
        advantage = differential_signal
        
        # 使用alignability检查
        if abs(advantage) < self.alignability_threshold:
            advantage = 0  # 不可比，视为无差异
        
        # EMA更新累积优势
        key = operation
        
        if key not in self._operation_advantages:
            self._operation_advantages[key] = 0.0
            self._operation_counts[key] = 0
        
        self._operation_advantages[key] = (
            self.ema_alpha * advantage + 
            (1 - self.ema_alpha) * self._operation_advantages[key]
        )
        self._operation_counts[key] += 1
        
        # 记录历史
        record = OperationRecord(
            operation=operation,
            batch_id=batch_id,
            advantage=advantage,
            timestamp=time.time(),
            context=context or {}
        )
        self._history.append(record)
        
        # 限制历史大小
        if len(self._history) > 1000:
            self._history = self._history[-500:]
        
        # 更新previous batch
        self._previous_batch_scores[operation] = current_score
    
    def get_accumulated_advantage(self, operation: str) -> float:
        """获取累积优势"""
        return self._operation_advantages.get(operation, 0.0)
    
    def should_use_operation(self, operation: str, 
                             threshold: float = 0.1) -> bool:
        """判断操作是否稳定有效
        
        Args:
            operation: 操作名称
            threshold: 阈值
            
        Returns:
            True if accumulated advantage > threshold
        """
        advantage = self.get_accumulated_advantage(operation)
        return advantage > threshold
    
    def get_operation_stats(self, operation: str) -> dict:
        """获取操作统计"""
        return {
            "operation": operation,
            "accumulated_advantage": self.get_accumulated_advantage(operation),
            "count": self._operation_counts.get(operation, 0),
            "should_use": self.should_use_operation(operation)
        }
    
    def get_all_stats(self) -> dict:
        """获取所有操作的统计"""
        return {
            op: self.get_operation_stats(op)
            for op in self._operation_advantages.keys()
        }
    
    def recommend_operations(self, candidates: list[str],
                           threshold: float = 0.1) -> list[tuple[str, float]]:
        """推荐应该使用的操作
        
        Returns:
            按累积优势排序的操作列表
        """
        recommendations = []
        
        for op in candidates:
            advantage = self.get_accumulated_advantage(op)
            if advantage > threshold:
                recommendations.append((op, advantage))
        
        # 按优势降序排序
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return recommendations
    
    def detect_contradiction(self, operation: str) -> bool:
        """检测矛盾：操作在不同batch中收到相反反馈
        
        Returns:
            True if contradiction detected
        """
        # 获取该操作的所有记录
        records = [r for r in self._history if r.operation == operation]
        
        if len(records) < 3:
            return False
        
        # 检查正负交替
        signs = [1 if r.advantage > 0 else -1 for r in records[-5:]]
        
        # 至少3个记录且符号变化超过2次
        if len([s for s in signs if s > 0]) >= 2 and len([s for s in signs if s < 0]) >= 2:
            return True
        
        return False
    
    def get_diagnostics(self) -> dict:
        """获取诊断信息"""
        contradictions = []
        
        for op in self._operation_advantages.keys():
            if self.detect_contradiction(op):
                contradictions.append(op)
        
        return {
            "total_operations": len(self._operation_advantages),
            "contradictions": contradictions,
            "recommended_ops": self.recommend_operations(
                list(self._operation_advantages.keys())
            )
        }
    
    def reset(self) -> None:
        """重置"""
        self._operation_advantages.clear()
        self._operation_counts.clear()
        self._history.clear()
        self._previous_batch_scores.clear()