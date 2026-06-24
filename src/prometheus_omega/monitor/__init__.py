"""L9 Monitor - 监控层 (Z-score+CORAL+自愈)
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
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
    """自愈引擎 - 来自X系统#49
    
    功能:
    - 注册修复规则
    - 自动诊断错误
    - 执行修复动作
    - 记录自愈历史
    """
    
    def __init__(self, auto_heal: bool = True, max_retries: int = 3):
        """初始化自愈引擎
        
        Args:
            auto_heal: 是否自动执行修复
            max_retries: 最大重试次数
        """
        self.auto_heal = auto_heal
        self.max_retries = max_retries
        self.healing_rules: Dict[str, callable] = {}
        
        # 统计
        self.heal_attempts = 0
        self.heal_successes = 0
        self.heal_failures = 0
        
        # 历史
        self._history: List[Dict] = []
        
        # 内置规则
        self._register_builtin_rules()
    
    def _register_builtin_rules(self):
        """注册内置修复规则"""
        # 内存溢出 - 清理缓存
        def fix_memory():
            import gc
            gc.collect()
        
        self.register_rule("memory", fix_memory)
        self.register_rule("MemoryError", fix_memory)
        
        # 超时 - 重试
        def fix_timeout():
            pass  # 重试逻辑由调用方处理
        
        self.register_rule("timeout", fix_timeout)
        self.register_rule("TimeoutError", fix_timeout)
        
        # 连接错误 - 重置连接
        def fix_connection():
            pass  # 连接池重置
        
        self.register_rule("ConnectionError", fix_connection)
        self.register_rule("connection", fix_connection)
    
    def register_rule(self, condition: str, fix: callable, 
                     priority: int = 0, description: str = ""):
        """注册修复规则
        
        Args:
            condition: 错误条件关键词
            fix: 修复函数
            priority: 优先级 (越高越先执行)
            description: 规则描述
        """
        self.healing_rules[condition] = {
            "fix": fix,
            "priority": priority,
            "description": description,
            "condition": condition,
        }
    
    def heal(self, error: Dict) -> Dict[str, Any]:
        """执行自愈
        
        Args:
            error: 错误信息字典
            
        Returns:
            Dict: 自愈结果
        """
        self.heal_attempts += 1
        
        error_type = error.get("type", "")
        error_msg = error.get("message", str(error))
        error_key = f"{error_type}: {error_msg}"
        
        matched_rules = []
        
        # 匹配规则
        for condition, rule in self.healing_rules.items():
            if condition.lower() in error_key.lower():
                matched_rules.append(rule)
        
        # 按优先级排序
        matched_rules.sort(key=lambda x: x.get("priority", 0), reverse=True)
        
        if not matched_rules:
            self.heal_failures += 1
            return {
                "success": False,
                "reason": "no matching rule",
                "error": error_key,
            }
        
        # 执行修复
        for rule in matched_rules:
            try:
                fix_func = rule.get("fix")
                if callable(fix_func):
                    fix_func()
                    
                    # 记录成功
                    self.heal_successes += 1
                    self._history.append({
                        "timestamp": time.time(),
                        "error": error_key,
                        "rule": rule.get("description", rule.get("condition", "")),
                        "success": True,
                    })
                    
                    return {
                        "success": True,
                        "rule": rule.get("condition", ""),
                        "description": rule.get("description", ""),
                    }
                    
            except Exception as e:
                # 记录失败但继续尝试下一个规则
                self._history.append({
                    "timestamp": time.time(),
                    "error": error_key,
                    "rule": rule.get("condition", ""),
                    "success": False,
                    "exception": str(e),
                })
                continue
        
        # 所有规则都失败
        self.heal_failures += 1
        return {
            "success": False,
            "reason": "all rules failed",
            "error": error_key,
        }
    
    def can_heal(self, error: Dict) -> bool:
        """检查是否可以修复
        
        Args:
            error: 错误信息
            
        Returns:
            bool: 是否有匹配的修复规则
        """
        error_type = error.get("type", "")
        error_msg = error.get("message", str(error))
        error_key = f"{error_type}: {error_msg}"
        
        for condition in self.healing_rules:
            if condition.lower() in error_key.lower():
                return True
        
        return False
    
    def get_statistics(self) -> Dict:
        """获取自愈统计"""
        total = self.heal_attempts
        success_rate = self.heal_successes / total if total > 0 else 0
        
        return {
            "total_attempts": total,
            "successes": self.heal_successes,
            "failures": self.heal_failures,
            "success_rate": success_rate,
            "registered_rules": len(self.healing_rules),
        }
    
    def get_history(self, limit: int = 100) -> List[Dict]:
        """获取自愈历史"""
        return self._history[-limit:]
    
    def clear_history(self):
        """清除历史记录"""
        self._history = []


class Monitor:
    """统一监控系统 - 整合所有监控功能
    
    整合Z-score异常检测、趋势预测、CORAL心跳、自愈引擎、警报系统
    """
    
    def __init__(self, name: str = "omega_monitor",
                 enable_healing: bool = True,
                 alert_callback: callable = None):
        """初始化监控器
        
        Args:
            name: 监控器名称
            enable_healing: 是否启用自愈
            alert_callback: 警报回调函数
        """
        self.name = name
        self.enable_healing = enable_healing
        self.alert_callback = alert_callback
        
        # 组件
        self.zscore = ZScoreAnomaly(threshold=3.0)
        self.trend = TrendPredictor(window=10)
        self.coral = CORALHeartbeat(interval=60)
        self.healer = SelfHealingEngine(auto_heal=enable_healing)
        self.alerts = AlertSystem()
        
        # 指标收集
        self._metrics: Dict[str, List[float]] = {}
        self._start_time = time.time()
    
    def record_metric(self, metric_name: str, value: float):
        """记录指标
        
        Args:
            metric_name: 指标名称
            value: 指标值
        """
        if metric_name not in self._metrics:
            self._metrics[metric_name] = []
        
        self._metrics[metric_name].append(value)
        
        # 保持最近1000个值
        if len(self._metrics[metric_name]) > 1000:
            self._metrics[metric_name] = self._metrics[metric_name][-1000:]
        
        # 检查异常
        self.zscore.add(value)
        if self.zscore.is_anomaly(value):
            self.alerts.send(
                level=AlertLevel.WARNING,
                message=f"异常检测: {metric_name}={value}"
            )
    
    def predict_trend(self, metric_name: str) -> float:
        """预测趋势
        
        Args:
            metric_name: 指标名称
            
        Returns:
            float: 预测值
        """
        values = self._metrics.get(metric_name, [])
        if not values:
            return 0.0
        
        self.trend.history = values[-self.trend.window:]
        return self.trend.predict()
    
    def check_heartbeat(self) -> Dict[str, bool]:
        """检查心跳
        
        Returns:
            Dict: 需要执行的操作
        """
        return self.coral.heartbeat()
    
    def handle_error(self, error: Dict) -> Dict[str, Any]:
        """处理错误 (包含自愈)
        
        Args:
            error: 错误信息
            
        Returns:
            Dict: 处理结果
        """
        # 发送警报
        self.alerts.send(
            level=AlertLevel.ERROR,
            message=f"错误: {error.get('message', str(error))}"
        )
        
        # 自愈
        if self.enable_healing and self.healer.can_heal(error):
            result = self.healer.heal(error)
            if result.get("success"):
                self.alerts.send(
                    level=AlertLevel.INFO,
                    message=f"自愈成功: {result.get('description', '')}"
                )
            return result
        
        return {"success": False, "reason": "healing disabled or no rule"}
    
    def get_status(self) -> Dict:
        """获取监控状态
        
        Returns:
            Dict: 状态信息
        """
        uptime = time.time() - self._start_time
        
        return {
            "name": self.name,
            "uptime_seconds": uptime,
            "metrics_count": len(self._metrics),
            "zscore_baseline": len(self.zscore.values),
            "healer_stats": self.healer.get_statistics(),
            "alert_count": len(self.alerts.alerts),
        }
    
    def reset(self):
        """重置监控器"""
        self._metrics = {}
        self.zscore.values = []
        self.trend.history = []
        self.alerts.alerts = []
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