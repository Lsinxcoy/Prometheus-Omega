"""Loop Budget Guard - Token预算守卫

基于Loop Engineering的Budget Guard模式：
- 每次循环开头和结尾检查预算
- 超过80%切报告模式
- 超过100%立即退出
"""
import time
from dataclasses import dataclass
from typing import Tuple, Optional
import json
from pathlib import Path


@dataclass
class LoopBudget:
    """Loop预算守卫"""
    daily_token_limit: int = 100000  # 默认100k/day
    warn_threshold: float = 0.8
    critical_threshold: float = 1.0
    
    used_tokens: int = 0
    last_reset: float = 0
    
    def __post_init__(self):
        self.last_reset = time.time()
    
    def can_proceed(self) -> Tuple[bool, str]:
        """检查是否可以继续
        
        Returns:
            (can_proceed, reason)
        """
        # 每日重置
        if time.time() - self.last_reset > 86400:
            self.used_tokens = 0
            self.last_reset = time.time()
        
        ratio = self.used_tokens / self.daily_token_limit
        
        if ratio >= self.critical_threshold:
            return False, "budget_exceeded"
        elif ratio >= self.warn_threshold:
            return True, f"warning_{int(ratio*100)}%_used"
        
        return True, "ok"
    
    def record_usage(self, tokens: int) -> None:
        """记录Token使用"""
        self.used_tokens += tokens
    
    def get_remaining(self) -> int:
        """获取剩余Token"""
        return max(0, self.daily_token_limit - self.used_tokens)
    
    def get_usage_ratio(self) -> float:
        """获取使用率"""
        return self.used_tokens / self.daily_token_limit
    
    def reset(self) -> None:
        """重置预算"""
        self.used_tokens = 0
        self.last_reset = time.time()
    
    def to_dict(self) -> dict:
        return {
            "daily_token_limit": self.daily_token_limit,
            "used_tokens": self.used_tokens,
            "remaining": self.get_remaining(),
            "usage_ratio": self.get_usage_ratio(),
            "last_reset": self.last_reset
        }


class BudgetManager:
    """预算管理器 - 多Loop聚合预算
    
    基于Loop Engineering的多Loop协调：
    - 聚合所有Loop的Token预算
    - 防止单个Loop耗尽资源
    """
    
    def __init__(self, total_budget: int = 500000):
        self.total_budget = total_budget
        self._loop_budgets: dict[str, LoopBudget] = {}
        self._usage_log: list[dict] = []
        self._log_file = Path("loop_budget_log.json")
        self._load_log()
    
    def get_or_create_budget(self, loop_id: str) -> LoopBudget:
        """获取或创建Loop预算"""
        if loop_id not in self._loop_budgets:
            self._loop_budgets[loop_id] = LoopBudget()
        return self._loop_budgets[loop_id]
    
    def check_global_budget(self, requested: int = 0) -> Tuple[bool, str]:
        """检查全局预算"""
        total_used = sum(b.used_tokens for b in self._loop_budgets.values())
        total_used += requested
        
        ratio = total_used / self.total_budget
        
        if ratio >= 1.0:
            return False, "global_budget_exceeded"
        elif ratio >= 0.8:
            return True, f"global_warning_{int(ratio*100)}%"
        
        return True, "ok"
    
    def record(self, loop_id: str, tokens: int, context: str = "") -> None:
        """记录Token使用"""
        budget = self.get_or_create_budget(loop_id)
        budget.record_usage(tokens)
        
        # 记录日志
        self._usage_log.append({
            "time": time.time(),
            "loop_id": loop_id,
            "tokens": tokens,
            "context": context,
            "global_total": sum(b.used_tokens for b in self._loop_budgets.values())
        })
        
        # 限制日志大小
        if len(self._usage_log) > 1000:
            self._usage_log = self._usage_log[-500:]
        
        self._save_log()
    
    def get_loop_status(self, loop_id: str) -> dict:
        """获取Loop预算状态"""
        budget = self._loop_budgets.get(loop_id)
        if not budget:
            return {"status": "not_found"}
        
        can_proceed, reason = budget.can_proceed()
        
        return {
            "loop_id": loop_id,
            "used": budget.used_tokens,
            "remaining": budget.get_remaining(),
            "ratio": budget.get_usage_ratio(),
            "can_proceed": can_proceed,
            "reason": reason
        }
    
    def get_global_status(self) -> dict:
        """获取全局预算状态"""
        total_used = sum(b.used_tokens for b in self._loop_budgets.values())
        
        return {
            "total_budget": self.total_budget,
            "used": total_used,
            "remaining": self.total_budget - total_used,
            "ratio": total_used / self.total_budget,
            "active_loops": len(self._loop_budgets)
        }
    
    def pause_all_loops(self) -> list[str]:
        """暂停所有Loop - 预算耗尽"""
        paused = []
        for loop_id in self._loop_budgets:
            budget = self._loop_budgets[loop_id]
            if budget.can_proceed()[0]:
                paused.append(loop_id)
                # 强制设为超限
                budget.used_tokens = budget.daily_token_limit + 1
        return paused
    
    def _load_log(self) -> None:
        """加载历史日志"""
        if self._log_file.exists():
            try:
                with open(self._log_file) as f:
                    self._usage_log = json.load(f)
            except json.JSONDecodeError:
                self._usage_log = []
    
    def _save_log(self) -> None:
        """保存日志"""
        with open(self._log_file, 'w') as f:
            json.dump(self._usage_log, f)


# 导出单例
_budget_manager: Optional[BudgetManager] = None

def get_budget_manager() -> BudgetManager:
    """获取预算管理器单例"""
    global _budget_manager
    if _budget_manager is None:
        _budget_manager = BudgetManager()
    return _budget_manager