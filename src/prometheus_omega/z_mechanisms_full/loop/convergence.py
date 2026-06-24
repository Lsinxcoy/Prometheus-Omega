"""收敛检测器 - 决定何时停止进化"""
from typing import Callable, Optional


class ConvergenceDetector:
    """收敛检测器 - 防止无限进化
    
    基于2606.20231的热力学智能度量思想：
    当改进率低于阈值时，系统已达到稳定状态
    """
    
    def __init__(self, threshold: float = 0.01, window_size: int = 3):
        self.threshold = threshold
        self.window_size = window_size
        self._history: list[float] = []
        
    def add_score(self, score: float) -> None:
        """添加分数记录"""
        self._history.append(score)
        if len(self._history) > self.window_size:
            self._history.pop(0)
    
    def is_converged(self) -> bool:
        """检查是否收敛"""
        if len(self._history) < 2:
            return False
        
        # 计算变化率
        changes = []
        for i in range(1, len(self._history)):
            if self._history[i-1] != 0:
                change = abs(self._history[i] - self._history[i-1]) / abs(self._history[i-1])
                changes.append(change)
            else:
                changes.append(abs(self._history[i] - self._history[i-1]))
        
        if not changes:
            return False
            
        avg_change = sum(changes) / len(changes)
        return avg_change < self.threshold
    
    def get_improvement_rate(self) -> float:
        """获取改进率"""
        if len(self._history) < 2:
            return 0.0
        return (self._history[-1] - self._history[0]) / max(abs(self._history[0]), 0.001)
    
    def get_trend(self) -> str:
        """获取趋势"""
        if len(self._history) < 2:
            return "insufficient_data"
        if self._history[-1] > self._history[0]:
            return "improving"
        elif self._history[-1] < self._history[0]:
            return "degrading"
        return "stable"
    
    def reset(self) -> None:
        """重置历史"""
        self._history.clear()
    
    def to_dict(self) -> dict:
        """序列化为dict"""
        return {
            "threshold": self.threshold,
            "window_size": self.window_size,
            "history": self._history,
            "is_converged": self.is_converged(),
            "improvement_rate": self.get_improvement_rate(),
            "trend": self.get_trend()
        }


class AdaptiveConvergenceDetector(ConvergenceDetector):
    """自适应收敛检测器 - 根据历史调整阈值"""
    
    def __init__(self, initial_threshold: float = 0.01, 
                 min_threshold: float = 0.001,
                 max_threshold: float = 0.1):
        super().__init__(threshold=initial_threshold)
        self.initial_threshold = initial_threshold
        self.min_threshold = min_threshold
        self.max_threshold = max_threshold
        self._convergence_count = 0
        self._oscillation_count = 0
    
    def check_and_adapt(self, score: float) -> bool:
        """检查收敛并自适应调整"""
        self.add_score(score)
        
        # 检测震荡
        if len(self._history) >= 3:
            recent = self._history[-3:]
            if (recent[0] > recent[1] < recent[2]) or (recent[0] < recent[1] > recent[2]):
                self._oscillation_count += 1
                # 震荡时放宽阈值
                self.threshold = min(self.threshold * 1.5, self.max_threshold)
        
        is_converged = self.is_converged()
        
        if is_converged:
            self._convergence_count += 1
            # 连续收敛时收紧阈值
            if self._convergence_count >= 2:
                self.threshold = max(self.threshold * 0.5, self.min_threshold)
        
        return is_converged
    
    def to_dict(self) -> dict:
        """扩展序列化"""
        base = super().to_dict()
        base.update({
            "convergence_count": self._convergence_count,
            "oscillation_count": self._oscillation_count,
            "adaptive_threshold": self.threshold
        })
        return base