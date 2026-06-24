"""L9 Monitor - 监控层 (Z-score+CORAL+自愈)"""
from dataclasses import dataclass, field
from typing import List, Dict
from enum import Enum
import statistics, time


class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Alert:
    level: AlertLevel
    message: str
    timestamp: float = field(default_factory=time.time)


class ZScoreAnomaly:
    """Z-score异常检测 - 来自X系统#46"""
    
    def __init__(self, threshold: float = 3.0):
        self.threshold = threshold
        self.values: List[float] = []
    
    def add(self, value: float):
        self.values.append(value)
        if len(self.values) > 1000:
            self.values.pop(0)
    
    def is_anomaly(self, value: float) -> bool:
        if len(self.values) < 10:
            return False
        mean = statistics.mean(self.values)
        stdev = statistics.stdev(self.values) if len(self.values) > 1 else 1
        z = abs((value - mean) / stdev) if stdev > 0 else 0
        return z > self.threshold


class TrendPredictor:
    """趋势外推预测 - 来自X系统#47"""
    
    def __init__(self, window: int = 10):
        self.window = window
        self.history: List[float] = []
    
    def predict(self) -> float:
        if len(self.history) < 2:
            return 0
        # 简单线性趋势
        n = len(self.history)
        x_mean = (n - 1) / 2
        y_mean = sum(self.history) / n
        
        numerator = sum((i - x_mean) * (y - y_mean) for i, y in enumerate(self.history))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0
        return self.history[-1] + slope


class CORALHeartbeat:
    """CORAL心跳 - 来自X/Y系统#48
    
    Reflect → Consolidate → Redirect 循环
    """
    
    def __init__(self, interval: int = 60):
        self.interval = interval
        self.last_reflect = 0
        self.last_consolidate = 0
        self.last_redirect = 0
    
    def heartbeat(self) -> Dict[str, bool]:
        now = time.time()
        return {
            "reflect": now - self.last_reflect > self.interval,
            "consolidate": now - self.last_consolidate > self.interval * 6,
            "redirect": now - self.last_redirect > self.interval * 10,
        }


class SelfHealingEngine:
    """自愈引擎 - 来自X系统#49"""
    
    def __init__(self):
        self.healing_rules: Dict[str, callable] = {}
    
    def register_rule(self, condition: str, fix: callable):
        self.healing_rules[condition] = fix
    
    def heal(self, error: Dict) -> bool:
        for condition, fix in self.healing_rules.items():
            if condition in str(error):
                fix()
                return True
        return False


class Monitor:
    """统一监控系统 - 整合所有监控功能
    
    整合Z-score异常检测、趋势预测、CORAL心跳、自愈引擎、警报系统
    """
    
    def __init__(self, name: str = "omega_monitor"):
        self.name = name
        self.zscore = ZScoreAnomaly(threshold=3.0)
        self.trend = TrendPredictor(window=10)
        self.coral = CORALHeartbeat(interval=60)
        self.healer = SelfHealingEngine()
        self.alerts = AlertSystem()
        self._running = False
    
    def start(self) -> bool:
        """启动监控"""
        self._running = True
        self.alerts.alert(AlertLevel.INFO, f"{self.name} started")
        return True
    
    def stop(self):
        """停止监控"""
        self._running = False
        self.alerts.alert(AlertLevel.INFO, f"{self.name} stopped")
    
    def record_metric(self, name: str, value: float) -> bool:
        """记录指标并检测异常"""
        # 检测异常
        if self.zscore.is_anomaly(value):
            self.alerts.alert(
                AlertLevel.WARNING, 
                f"Anomaly detected: {name}={value}"
            )
            return False
        
        # 记录数据
        self.zscore.add(value)
        self.trend.history.append(value)
        if len(self.trend.history) > self.trend.window:
            self.trend.history.pop(0)
        
        return True
    
    def check_heartbeat(self) -> Dict[str, bool]:
        """检查CORAL心跳"""
        return self.coral.heartbeat()
    
    def heal_error(self, error: Dict) -> bool:
        """自愈错误"""
        result = self.healer.heal(error)
        if result:
            self.alerts.alert(AlertLevel.INFO, f"Healed error: {error}")
        return result
    
    def get_status(self) -> Dict[str, any]:
        """获取监控状态"""
        return {
            "name": self.name,
            "running": self._running,
            "metrics_count": len(self.zscore.values),
            "trend_history": len(self.trend.history),
            "alerts_count": len(self.alerts.alerts),
        }


class AlertSystem:
    """警报系统"""
    
    def __init__(self):
        self.alerts: List[Alert] = []
    
    def alert(self, level: AlertLevel, message: str):
        self.alerts.append(Alert(level=level, message=message))
        if len(self.alerts) > 100:
            self.alerts.pop(0)
    
    def get_recent(self, count: int = 10) -> List[Alert]:
        return self.alerts[-count:]


# 工厂
def create_zscore_anomaly(threshold: float = 3.0) -> ZScoreAnomaly:
    return ZScoreAnomaly(threshold=threshold)

def create_coral_heartbeat(interval: int = 60) -> CORALHeartbeat:
    return CORALHeartbeat(interval=interval)

def create_self_healing_engine() -> SelfHealingEngine:
    return SelfHealingEngine()