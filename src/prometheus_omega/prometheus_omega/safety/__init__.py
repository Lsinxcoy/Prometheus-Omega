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
    """FiveGates链式熔断 - 来自X/Y系统#34
    
    五门安全检查: 读门、写门、 Consolidation门、执行门、退出门
    """
    
    def __init__(self):
        self.gates = {
            "read": True,      # 读门: 验证访问权限
            "write": True,     # 写门: 验证写入质量
            "consolidate": True,  # Consolidation门: 验证记忆巩固
            "execute": True,   # 执行门: 验证执行安全
            "exit": True,      # 退出门: 验证输出安全
        }
    
    def read_gate_check(self, node) -> bool:
        """读门检查 - 验证节点是否可以读取
        
        Args:
            node: OmegaNode对象
            
        Returns:
            bool: 是否允许读取
        """
        if not self.gates.get("read", True):
            return False
        
        # 检查节点的trust级别
        trust = getattr(node, 'trust', 0)
        return trust >= 1  # 至少LOW信任级别
    
    def write_gate_check(self, node) -> bool:
        """写门检查 - 验证节点是否可以写入
        
        Args:
            node: OmegaNode对象
            
        Returns:
            bool: 是否允许写入
        """
        if not self.gates.get("write", True):
            return False
        
        # 检查内容质量
        importance = getattr(node, 'importance', 0)
        utility = getattr(node, 'utility', 0)
        
        return importance > 0.1 and utility >= 0
    
    def consolidate_gate_check(self, nodes: list) -> bool:
        """Consolidation门检查 - 验证是否可以 Consolidation
        
        Args:
            nodes: OmegaNode列表
            
        Returns:
            bool: 是否允许 Consolidation
        """
        if not self.gates.get("consolidate", True):
            return False
        
        # 需要至少3个节点才能 Consolidation
        return len(nodes) >= 3
    
    def execute_gate_check(self, tool_name: str, params: dict) -> bool:
        """执行门检查 - 验证工具是否可以执行
        
        Args:
            tool_name: 工具名称
            params: 工具参数
            
        Returns:
            bool: 是否允许执行
        """
        if not self.gates.get("execute", True):
            return False
        
        # 危险工具黑名单
        dangerous = ['eval', 'exec', '__import__', 'os.system', 'subprocess']
        return not any(d in tool_name for d in dangerous)
    
    def exit_gate_check(self, output: str) -> bool:
        """退出门检查 - 验证输出是否安全
        
        Args:
            output: 输出内容
            
        Returns:
            bool: 是否允许输出
        """
        if not self.gates.get("exit", True):
            return False
        
        # 检查敏感信息泄露
        sensitive_patterns = ['password', 'token', 'secret', 'api_key']
        output_lower = output.lower()
        
        return not any(p in output_lower for p in sensitive_patterns)
    
    def pass_gate(self, gate_name: str) -> bool:
        """检查指定门是否通过"""
        return self.gates.get(gate_name, False)
    
    def trip(self, gate_name: str):
        """触发(熔断)指定门"""
        if gate_name in self.gates:
            self.gates[gate_name] = False
    
    def reset(self):
        """重置所有门"""
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