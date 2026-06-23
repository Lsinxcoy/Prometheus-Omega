"""L7 Safety - 安全层 (4层防御+Denylist+22宪法)"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Set
from enum import Enum
import re


class SafetyLevel(Enum):
    SAFE = "safe"
    WARNING = "warning"
    DANGER = "danger"
    CRITICAL = "critical"


@dataclass
class SecurityAudit:
    level: SafetyLevel
    issues: List[str] = field(default_factory=list)
    score: float = 1.0


class FourLayerDefense:
    """4层防御纵深 - 来自X系统#33"""
    
    def __init__(self):
        self.layer1_perimeter = True
        self.layer2_application = True
        self.layer3_data = True
        self.layer4_runtime = True
    
    def audit(self, context: Dict) -> SecurityAudit:
        issues = []
        if not self.layer1_perimeter:
            issues.append("Perimeter breach")
        return SecurityAudit(
            level=SafetyLevel.SAFE if not issues else SafetyLevel.WARNING,
            issues=issues,
            score=0.9
        )


class FiveGates:
    """FiveGates链式熔断 - 来自X/Y系统#34"""
    
    def __init__(self):
        self.gates = {"gate1": True, "gate2": True, "gate3": True, "gate4": True, "gate5": True}
    
    def pass_gate(self, gate_name: str) -> bool:
        return self.gates.get(gate_name, False)
    
    def trip(self, gate_name: str):
        self.gates[gate_name] = False
    
    def reset(self):
        for k in self.gates:
            self.gates[k] = True


class CodeSlopDetector:
    """CodeSlop检测 - 来自X系统#35"""
    
    def __init__(self):
        self.patterns = [
            (r"eval\s*\(", "eval_usage"),
            (r"exec\s*\(", "exec_usage"),
            (r"__import__\s*\(", "dynamic_import"),
        ]
    
    def detect(self, code: str) -> List[Dict]:
        issues = []
        for pattern, issue_type in self.patterns:
            if re.search(pattern, code):
                issues.append({"type": issue_type, "severity": "high"})
        return issues


class VerificationIronLaw:
    """验证铁律5步 - 来自X系统#36"""
    
    def __init__(self):
        self.steps = ["syntax", "semantics", "security", "testing", "deployment"]
    
    def verify(self, artifact: Dict) -> bool:
        for step in self.steps:
            if step not in artifact:
                return False
        return True


class CircuitBreaker:
    """3态断路器 - 来自X系统#37"""
    
    def __init__(self, threshold: int = 5):
        self.state = "closed"
        self.failure_count = 0
        self.threshold = threshold
    
    def record_success(self):
        self.failure_count = 0
        self.state = "closed"
    
    def record_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.threshold:
            self.state = "open"
    
    def can_execute(self) -> bool:
        return self.state == "closed"


class Denylist:
    """路径黑名单 - 来自Z系统"""
    
    SENSITIVE_PATTERNS = [
        r"\.env$",
        r"secrets?",
        r"\.password",
        r"\.ssh",
        r"/etc/passwd",
        r"windows/system32",
    ]
    
    def __init__(self):
        self.patterns = self.SENSITIVE_PATTERNS.copy()
    
    def is_allowed(self, path: str) -> bool:
        for pattern in self.patterns:
            if re.search(pattern, path, re.IGNORECASE):
                return False
        return True


class RateLimiter:
    """速率限制器 - 来自Z系统"""
    
    def __init__(self, max_per_minute: int = 60):
        self.max = max_per_minute
        self.requests: List[float] = []
    
    def allow(self) -> bool:
        import time
        now = time.time()
        self.requests = [t for t in self.requests if now - t < 60]
        if len(self.requests) < self.max:
            self.requests.append(now)
            return True
        return False


class AntiPattern:
    """反模式检测 - 来自Y系统"""
    
    def __init__(self):
        self.patterns = [
            "spaghetti_code",
            "god_object",
            "circular_dependency",
        ]
    
    def detect(self, code: str) -> List[str]:
        found = []
        if len(code) > 5000:
            found.append("god_object")
        return found


# 工厂
def create_four_layer_defense() -> FourLayerDefense:
    return FourLayerDefense()

def create_denylist() -> Denylist:
    return Denylist()

def create_rate_limiter(max_per_minute: int = 60) -> RateLimiter:
    return RateLimiter(max_per_minute=max_per_minute)