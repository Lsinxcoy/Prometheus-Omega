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
    """22宪法原则 - 来自X系统#40
    
    22项核心原则:
    1-5: 安全与透明度
    6-10: 公平与隐私
    11-15: 监督与价值
    16-20: 公正与保护
    21-22: 优雅降级与利益
    """
    
    # 按类别分组
    PRINCIPLES = [
        "Safety First",           # 1. 安全第一
        "Transparency",           # 2. 透明性
        "Accountability",         # 3. 问责制
        "Fairness",               # 4. 公平性
        "Privacy",                # 5. 隐私保护
        "Security",               # 6. 安全性
        "Reliability",            # 7. 可靠性
        "Robustness",             # 8. 鲁棒性
        "Explainability",         # 9. 可解释性
        "Contestability",         # 10. 可质疑性
        "Human Oversight",        # 11. 人类监督
        "Value Alignment",        # 12. ��值对齐
        "Beneficence",            # 13. 善意
        "Non-maleficence",        # 14. 无害
        "Justice",                # 15. 公正
        "Autonomy Respect",       # 16. 尊重自主
        "Data Protection",        # 17. 数据保护
        "Auditability",           # 18. 可审计性
        "Graceful Degradation",   # 19. 优雅降级
        "Fail-safe",              # 20. 故障安全
        "Transparency of Intent", # 21. 意图透明
        "Stakeholder Benefit",    # 22. 利益相关者受益
    ]
    
    # 原则类别
    CATEGORIES = {
        "safety": [0, 5, 7, 19, 20],          # 安全类
        "transparency": [1, 8, 20],           # 透明类
        "fairness": [3, 14, 21],              # 公平类
        "privacy": [4, 16],                   # 隐私类
        "oversight": [2, 10, 17],             # 监督类
        "ethics": [11, 12, 13, 15, 22],       # 伦理类
    }
    
    def __init__(self, strict_mode: bool = True):
        """初始化宪法原则
        
        Args:
            strict_mode: 严格模式 - 必须通过所有原则检查
        """
        self.strict_mode = strict_mode
        self._violations: List[Dict] = []
        self._approvals: List[Dict] = []
    
    def get_principle(self, index: int) -> str:
        """获取指定索引的原则
        
        Args:
            index: 原则索引 (0-21)
            
        Returns:
            str: 原则名称
        """
        return self.PRINCIPLES[index] if 0 <= index < len(self.PRINCIPLES) else ""
    
    def get_category_principles(self, category: str) -> List[str]:
        """获取类别的所有原则
        
        Args:
            category: 类别名称
            
        Returns:
            List[str]: 原则列表
        """
        indices = self.CATEGORIES.get(category.lower(), [])
        return [self.PRINCIPLES[i] for i in indices if i < len(self.PRINCIPLES)]
    
    def check_action(self, action: Dict, context: Dict = None) -> Dict[str, Any]:
        """检查行动是否符合宪法原则
        
        Args:
            action: 待检查的行动
            context: 行动上下文
            
        Returns:
            Dict: 检查结果
        """
        import time
        
        violations = []
        
        # 检查安全第一
        if action.get("safety_critical", False):
            if not action.get("safety_verified", False):
                violations.append({
                    "principle": "Safety First",
                    "reason": "安全关键行动未经验证",
                    "severity": "critical",
                })
        
        # 检查隐私
        if action.get("contains_pii", False):
            if not action.get("privacy_protected", False):
                violations.append({
                    "principle": "Privacy",
                    "reason": "包含PII但未保护",
                    "severity": "high",
                })
        
        # 检查人类监督
        autonomy_level = action.get("autonomy_level", 0)
        if autonomy_level >= 3:  # L3或以上需要人类监督
            if not action.get("human_approved", False):
                violations.append({
                    "principle": "Human Oversight",
                    "reason": "高自主性行动需要人类批准",
                    "severity": "high",
                })
        
        # 检查公平性
        if action.get("affects_users", False):
            if action.get("discriminatory", False):
                violations.append({
                    "principle": "Fairness",
                    "reason": "行动存在歧视性",
                    "severity": "critical",
                })
        
        # 检查可解释性
        if action.get("complex", False):
            if not action.get("explanation_provided", False):
                violations.append({
                    "principle": "Explainability",
                    "reason": "复杂行动未提供解释",
                    "severity": "medium",
                })
        
        # 记录结果
        result = {
            "action_id": action.get("id", "unknown"),
            "passed": len(violations) == 0,
            "violations": violations,
            "violation_count": len(violations),
            "timestamp": time.time(),
        }
        
        if result["passed"]:
            self._approvals.append(result)
        else:
            self._violations.append(result)
        
        return result
    
    def validate_code(self, code: str) -> Dict[str, Any]:
        """验证代码是��符合宪法
        
        Args:
            code: 待验证的代码
            
        Returns:
            Dict: 验证结果
        """
        import re
        
        violations = []
        
        # 检查安全: 无硬编码密码
        if re.search(r'password\s*=\s*["\']', code, re.IGNORECASE):
            violations.append({"principle": "Security", "issue": "硬编码密码"})
        
        # 检查隐私: 无敏感数据
        if re.search(r'api[_-]?key\s*=\s*["\']', code, re.IGNORECASE):
            violations.append({"principle": "Privacy", "issue": "硬编码API密钥"})
        
        # 检查安全: 无eval
        if re.search(r'eval\s*\(\s*', code):
            violations.append({"principle": "Safety First", "issue": "使用eval"})
        
        return {
            "passed": len(violations) == 0,
            "violations": violations,
        }
    
    def get_statistics(self) -> Dict:
        """获取宪法检查统计"""
        return {
            "total_checks": len(self._violations) + len(self._approvals),
            "approvals": len(self._approvals),
            "violations": len(self._violations),
            "pass_rate": len(self._approvals) / max(1, len(self._violations) + len(self._approvals)),
        }


class ConfidenceGate:
    """置信度门控 - 来自X系统#43
    
    基于置信度决定是否可以继续执行
    """
    
    def __init__(self, 
                 threshold: float = 0.7,
                 auto_adjust: bool = True,
                 history_window: int = 100):
        """初始化置信度门控
        
        Args:
            threshold: 置信度阈值
            auto_adjust: 是否自动调整阈值
            history_window: 历史窗口大小
        """
        self.threshold = threshold
        self.auto_adjust = auto_adjust
        self.history_window = history_window
        
        # 历史
        self._history: List[Dict] = []
        self._accepted_confidences: List[float] = []
        self._rejected_confidences: List[float] = []
    
    def can_proceed(self, confidence: float) -> bool:
        """检查是否可以继续
        
        Args:
            confidence: 置信度 (0-1)
            
        Returns:
            bool: 是否可以继续
        """
        import time
        
        # 边界检查
        confidence = max(0.0, min(1.0, confidence))
        
        # 核心逻辑
        can_proceed = confidence >= self.threshold
        
        # 记录历史
        self._history.append({
            "timestamp": time.time(),
            "confidence": confidence,
            "threshold": self.threshold,
            "accepted": can_proceed,
        })
        
        if can_proceed:
            self._accepted_confidences.append(confidence)
        else:
            self._rejected_confidences.append(confidence)
        
        # 保持窗口大小
        if len(self._history) > self.history_window:
            self._history = self._history[-self.history_window:]
        
        # 自动调整阈值
        if self.auto_adjust:
            self._adjust_threshold()
        
        return can_proceed
    
    def _adjust_threshold(self):
        """自动调整阈值"""
        total = len(self._accepted_confidences) + len(self._rejected_confidences)
        if total < 10:
            return
        
        accept_rate = len(self._accepted_confidences) / total
        
        # 如果接受率太低,降低阈值
        if accept_rate < 0.3:
            self.threshold = max(0.3, self.threshold - 0.05)
        # 如果接受率太高,提高阈值
        elif accept_rate > 0.9:
            self.threshold = min(0.95, self.threshold + 0.05)
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        total = len(self._history)
        accepted = len(self._accepted_confidences)
        
        return {
            "threshold": self.threshold,
            "total_checks": total,
            "accepted": accepted,
            "rejected": total - accepted,
            "accept_rate": accepted / total if total > 0 else 0,
            "avg_accepted_confidence": sum(self._accepted_confidences) / len(self._accepted_confidences) if self._accepted_confidences else 0,
        }
    
    def reset(self):
        """重置统计"""
        self._history = []
        self._accepted_confidences = []
        self._rejected_confidences = []


class EvolutionGrill:
    """进化审查7问 - 来自X系统#44
    
    在每次重要进化前进行7项审查
    """
    
    QUESTIONS = [
        "Is this evolution safe?",           # 1. 安全吗?
        "Does it maintain alignment?",       # 2. 保持对齐吗?
        "Is it reversible?",                 # 3. 可逆吗?
        "Who benefits?",                     # 4. 谁受益?
        "What are the risks?",               # 5. 风险是什么?
        "Can we audit it?",                  # 6. 可审计吗?
        "Does it respect values?",           # 7. 尊重价值观吗?
    ]
    
    def __init__(self):
        self._answers: List[Dict] = []
    
    def ask(self, index: int) -> str:
        """获取指定问题
        
        Args:
            index: 问题索引 (0-6)
            
        Returns:
            str: 问题内容
        """
        return self.QUESTIONS[index] if 0 <= index < len(self.QUESTIONS) else ""
    
    def ask_all(self) -> List[str]:
        """获取所有问题
        
        Returns:
            List[str]: 所有问题
        """
        return self.QUESTIONS.copy()
    
    def answer(self, question_index: int, answer: str, 
               confidence: float = 0.5) -> Dict:
        """回答问题
        
        Args:
            question_index: 问题索引
            answer: 答案
            confidence: 置信度
            
        Returns:
            Dict: 回答记录
        """
        import time
        
        record = {
            "question": self.ask(question_index),
            "answer": answer,
            "confidence": confidence,
            "timestamp": time.time(),
            "passed": confidence >= 0.5,
        }
        
        self._answers.append(record)
        return record
    
    def evaluate_evolution(self, answers: List[Dict]) -> Dict:
        """评估进化是否可以通过审查
        
        Args:
            answers: 所有问题的回答
            
        Returns:
            Dict: 评估结果
        """
        if len(answers) != len(self.QUESTIONS):
            return {
                "passed": False,
                "reason": "未回答所有问题",
            }
        
        # 所有问题都必须通过
        all_passed = all(a.get("passed", False) for a in answers)
        
        # 计算平均置信度
        avg_confidence = sum(a.get("confidence", 0) for a in answers) / len(answers)
        
        # 检查关键问题 (安全、对齐、可审计)
        critical_indices = [0, 1, 5]  # 问题1,2,6
        critical_passed = all(
            answers[i].get("passed", False) 
            for i in critical_indices 
            if i < len(answers)
        )
        
        passed = all_passed and critical_passed
        
        return {
            "passed": passed,
            "all_answered": len(answers) == len(self.QUESTIONS),
            "avg_confidence": avg_confidence,
            "critical_passed": critical_passed,
            "total_passed": sum(1 for a in answers if a.get("passed", False)),
            "total_questions": len(self.QUESTIONS),
        }
    
    def get_history(self, limit: int = 100) -> List[Dict]:
        """获取回答历史"""
        return self._answers[-limit:]


class DriftDetector:
    """概念漂移检测 - 来自X系统#45
    
    检测数据分布或概念的变化
    """
    
    def __init__(self, 
                 window: int = 100,
                 threshold: float = 0.3,
                 sensitivity: str = "medium"):
        """初始化漂移检测器
        
        Args:
            window: 滑动窗口大小
            threshold: 漂移阈值
            sensitivity: 敏感度 (low/medium/high)
        """
        self.window = window
        self.threshold = threshold
        self.sensitivity = sensitivity
        self.history: List[float] = []
        
        # 敏感度调整
        self._sensitivity_multipliers = {
            "low": 1.5,
            "medium": 1.0,
            "high": 0.5,
        }
    
    def detect(self, value: float) -> Dict[str, Any]:
        """检测漂移
        
        Args:
            value: 新值
            
        Returns:
            Dict: 检测结果
        """
        import time, statistics
        
        self.history.append(value)
        
        # 保持窗口大小
        if len(self.history) > self.window:
            self.history.pop(0)
        
        # 数据不足
        if len(self.history) < 10:
            return {
                "drift_detected": False,
                "reason": "insufficient_data",
                "values_in_window": len(self.history),
            }
        
        # 计算统计量
        mean_current = statistics.mean(self.history[-20:])  # 最近20个
        mean_baseline = statistics.mean(self.history[:-20]) if len(self.history) > 20 else mean_current
        
        std_baseline = statistics.stdev(self.history[:-20]) if len(self.history) > 20 else 1.0
        
        # 计算漂移量
        drift_magnitude = abs(mean_current - mean_baseline)
        
        # 应用敏感度
        multiplier = self._sensitivity_multipliers.get(self.sensitivity, 1.0)
        adjusted_threshold = self.threshold * multiplier
        
        drift_detected = drift_magnitude > adjusted_threshold
        
        return {
            "drift_detected": drift_detected,
            "magnitude": drift_magnitude,
            "threshold": adjusted_threshold,
            "current_mean": mean_current,
            "baseline_mean": mean_baseline,
            "values_in_window": len(self.history),
            "sensitivity": self.sensitivity,
        }
    
    def is_drift(self, value: float) -> bool:
        """快速判断是否有漂移
        
        Args:
            value: 新值
            
        Returns:
            bool: 是否有漂移
        """
        return self.detect(value).get("drift_detected", False)
    
    def reset(self):
        """重置历史"""
        self.history = []


# 工厂
# 兼容性别名
Constitution = ConstitutionalPrinciples

def create_constitutional_principles() -> ConstitutionalPrinciples:
    return ConstitutionalPrinciples()

def create_drift_detector(**kwargs) -> DriftDetector:
    return DriftDetector(**kwargs)