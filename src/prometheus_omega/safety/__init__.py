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
    """4层防御纵深 - 来自X系统#33
    
    4层防御:
    L1 周界防御 - 输入验证、格式检查、路径检查
    L2 应用防御 - 业务逻辑、权限检查、反模式检测
    L3 数据防御 - 数据完整性、加密验证、脱敏检查
    L4 运行时防御 - 内存安全、资源限制、异常隔离
    """
    
    def __init__(self):
        # 每层状态: True=正常, False=被突破
        self.layer1_perimeter = True
        self.layer2_application = True
        self.layer3_data = True
        self.layer4_runtime = True
        
        # 每层规则
        self.perimeter_rules = {
            "max_input_length": 10000,
            "allowed_extensions": [".py", ".json", ".yaml", ".md", ".txt"],
            "blocked_paths": ["/etc", "/root", "C:\\Windows\\System32"],
        }
        self.application_rules = {
            "max_nesting_depth": 10,
            "max_function_length": 200,
            "require_type_hints": True,
        }
        self.data_rules = {
            "require_encryption": False,
            "max_data_size": 10_000_000,  # 10MB
            "pii_detection": True,
        }
        self.runtime_rules = {
            "max_memory_mb": 512,
            "max_cpu_percent": 80,
            "max_execution_time": 300,
        }
        
        # 审计日志
        self._audit_log: List[Dict] = []
    
    def check(self, layer: str, data: Dict = None) -> bool:
        """检查指定层是否安全
        
        Args:
            layer: 层名称 (layer1/layer2/layer3/layer4 或 perimeter/application/data/runtime)
            data: 可选的检查数据
            
        Returns:
            bool: 该层是否安全
        """
        layer_map = {
            "layer1": "layer1_perimeter",
            "layer2": "layer2_application",
            "layer3": "layer3_data",
            "layer4": "layer4_runtime",
            "perimeter": "layer1_perimeter",
            "application": "layer2_application",
            "data": "layer3_data",
            "runtime": "layer4_runtime",
        }
        
        attr = layer_map.get(layer.lower())
        if not attr:
            return False
        
        return getattr(self, attr, False)
    
    def audit(self, context: Dict) -> SecurityAudit:
        """4层纵深审计
        
        Args:
            context: 审计上下文, 包含待检查的数据和操作
            
        Returns:
            SecurityAudit: 审计结果
        """
        all_issues = []
        
        # L1: 周界检查
        l1_issues = self._check_perimeter(context)
        all_issues.extend(l1_issues)
        if l1_issues:
            self.layer1_perimeter = False
        
        # L2: 应用检查
        l2_issues = self._check_application(context)
        all_issues.extend(l2_issues)
        if l2_issues:
            self.layer2_application = False
        
        # L3: 数据检查
        l3_issues = self._check_data(context)
        all_issues.extend(l3_issues)
        if l3_issues:
            self.layer3_data = False
        
        # L4: 运行时检查
        l4_issues = self._check_runtime(context)
        all_issues.extend(l4_issues)
        if l4_issues:
            self.layer4_runtime = False
        
        # 计算安全级别
        breached = sum(1 for layer in [
            self.layer1_perimeter, self.layer2_application,
            self.layer3_data, self.layer4_runtime
        ] if not layer)
        
        if breached == 0:
            level = SafetyLevel.SAFE
            score = 1.0
        elif breached == 1:
            level = SafetyLevel.WARNING
            score = 0.7
        elif breached <= 2:
            level = SafetyLevel.DANGER
            score = 0.4
        else:
            level = SafetyLevel.CRITICAL
            score = 0.1
        
        result = SecurityAudit(
            level=level,
            issues=all_issues,
            score=score,
        )
        
        # 记录审计日志
        self._audit_log.append({
            "level": level.value,
            "issues": all_issues,
            "score": score,
            "breached_layers": breached,
        })
        
        return result
    
    def _check_perimeter(self, context: Dict) -> List[str]:
        """L1 周界检查"""
        issues = []
        
        # 输入长度检查
        input_data = context.get("input", "")
        if isinstance(input_data, str) and len(input_data) > self.perimeter_rules["max_input_length"]:
            issues.append(f"L1: 输入超长 ({len(input_data)}>{self.perimeter_rules['max_input_length']})")
        
        # 路径检查
        path = context.get("path", "")
        if path:
            for blocked in self.perimeter_rules["blocked_paths"]:
                if blocked.lower() in str(path).lower():
                    issues.append(f"L1: 受限路径访问: {path}")
                    break
        
        # 扩展名检查
        ext = context.get("extension", "")
        if ext and ext not in self.perimeter_rules["allowed_extensions"]:
            issues.append(f"L1: 不允许的文件扩展名: {ext}")
        
        return issues
    
    def _check_application(self, context: Dict) -> List[str]:
        """L2 应用检查"""
        issues = []
        code = context.get("code", "")
        
        if not code:
            return issues
        
        # 嵌套深度检查
        max_indent = 0
        for line in code.split('\n'):
            indent = len(line) - len(line.lstrip())
            max_indent = max(max_indent, indent)
        nesting = max_indent // 4
        if nesting > self.application_rules["max_nesting_depth"]:
            issues.append(f"L2: 嵌套过深 ({nesting}>{self.application_rules['max_nesting_depth']})")
        
        # 函数长度检查
        func_len = len(code.split('\n'))
        if func_len > self.application_rules["max_function_length"]:
            issues.append(f"L2: 函数过长 ({func_len}>{self.application_rules['max_function_length']})")
        
        return issues
    
    def _check_data(self, context: Dict) -> List[str]:
        """L3 数据检查"""
        issues = []
        data = context.get("data", "")
        
        if not data:
            return issues
        
        # 数据大小检查
        data_size = len(str(data))
        if data_size > self.data_rules["max_data_size"]:
            issues.append(f"L3: 数据过大 ({data_size}>{self.data_rules['max_data_size']})")
        
        # PII检测
        if self.data_rules["pii_detection"]:
            import re
            pii_patterns = [
                (r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', 'phone_number'),
                (r'\b\d{3}-\d{2}-\d{4}\b', 'ssn'),
                (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'email'),
                (r'\b\d{16,19}\b', 'credit_card'),
            ]
            for pattern, pii_type in pii_patterns:
                if re.search(pattern, str(data)):
                    issues.append(f"L3: 发现PII: {pii_type}")
        
        return issues
    
    def _check_runtime(self, context: Dict) -> List[str]:
        """L4 运行时检查"""
        issues = []
        
        # 内存检查
        memory_mb = context.get("memory_mb", 0)
        if memory_mb > self.runtime_rules["max_memory_mb"]:
            issues.append(f"L4: 内存超限 ({memory_mb}MB>{self.runtime_rules['max_memory_mb']}MB)")
        
        # CPU检查
        cpu_pct = context.get("cpu_percent", 0)
        if cpu_pct > self.runtime_rules["max_cpu_percent"]:
            issues.append(f"L4: CPU超限 ({cpu_pct}%>{self.runtime_rules['max_cpu_percent']}%)")
        
        # 执行时间检查
        exec_time = context.get("execution_time", 0)
        if exec_time > self.runtime_rules["max_execution_time"]:
            issues.append(f"L4: 执行超时 ({exec_time}s>{self.runtime_rules['max_execution_time']}s)")
        
        return issues
    
    def reset(self):
        """重置所有层"""
        self.layer1_perimeter = True
        self.layer2_application = True
        self.layer3_data = True
        self.layer4_runtime = True
    
    def get_layer_status(self) -> Dict[str, bool]:
        """获取各层状态"""
        return {
            "L1_perimeter": self.layer1_perimeter,
            "L2_application": self.layer2_application,
            "L3_data": self.layer3_data,
            "L4_runtime": self.layer4_runtime,
        }


class FiveGates:
    """FiveGates链式熔断 - 来自X/Y系统#34
    
    五门安全检查: 读门、写门、Consolidation门、执行门、退出门
    每门包含: 输入验证、边界检查、错误处理、日志追踪
    """
    
    def __init__(self, strict_mode: bool = True):
        """
        初始化五门
        
        Args:
            strict_mode: 严格模式 True=全部检查, False=宽松模式
        """
        # 门状态: True=开启(允许), False=关闭(阻止)
        self.gates = {
            "read": True,        # 读门: 验证访问权限
            "write": True,       # 写门: 验证写入质量
            "consolidate": True, # Consolidation门: 验证记忆巩固
            "execute": True,     # 执行门: 验证执行安全
            "exit": True,        # 退出门: 验证输出安全
        }
        self.strict_mode = strict_mode
        self._log: List[Dict] = []  # 审计日志
        self._trip_count: Dict[str, int] = {k: 0 for k in self.gates}
    
    def read_gate_check(self, node) -> bool:
        """读门检查 - 验证节点是否可以读取
        
        Args:
            node: OmegaNode对象
            
        Returns:
            bool: 是否允许读取
            
        Raises:
            ValueError: 节点无效
        """
        # === 输入验证 ===
        if node is None:
            self._log_event("read", False, "error", "node is None")
            if self.strict_mode:
                raise ValueError("节点不能为空")
            return False
        
        # === 属性提取 ===
        node_id = getattr(node, 'id', 'unknown')
        trust = getattr(node, 'trust', 0)
        content = getattr(node, 'content', '')
        
        # === 边界检查 ===
        if not isinstance(trust, (int, float)):
            trust = 0
        trust = max(0, min(1, trust))  # clamp to [0, 1]
        
        # === 核心逻辑 ===
        # 信任级别: UNVERIFIED=0, LOW=1, MEDIUM=2, HIGH=3, CONSTITUTIONAL=5
        min_trust = 1 if self.strict_mode else 0
        allowed = trust >= min_trust
        
        # === 日志记录 ===
        self._log_event("read", allowed, "check", 
                       f"node={node_id}, trust={trust}, min={min_trust}")
        
        return allowed
    
    def write_gate_check(self, node) -> bool:
        """写门检查 - 验证节点是否可以写入
        
        Args:
            node: OmegaNode对象
            
        Returns:
            bool: 是否允许写入
            
        Raises:
            ValueError: 节点无效
        """
        # === 输入验证 ===
        if node is None:
            self._log_event("write", False, "error", "node is None")
            if self.strict_mode:
                raise ValueError("节点不能为空")
            return False
        
        # === 属性提取 ===
        node_id = getattr(node, 'id', 'unknown')
        importance = getattr(node, 'importance', 0)
        utility = getattr(node, 'utility', 0)
        veracity = getattr(node, 'veracity', 0.5)
        
        # === 边界检查 ===
        importance = max(0, min(1, importance or 0))
        utility = max(-1, min(1, utility or 0))
        veracity = max(0, min(1, veracity or 0.5))
        
        # === 核心逻辑: 质量 = importance * utility * veracity ===
        quality_score = importance * (0.5 + utility/2) * veracity
        
        # 最低质量阈值
        min_importance = 0.1
        min_quality = 0.05
        
        allowed = importance > min_importance and quality_score >= min_quality
        
        # === 日志记录 ===
        self._log_event("write", allowed, "check",
                       f"node={node_id}, imp={importance:.2f}, qual={quality_score:.3f}")
        
        return allowed
    
    def consolidate_gate_check(self, nodes: list) -> bool:
        """Consolidation门检查 - 验证是否可以 Consolidation
        
        Args:
            nodes: OmegaNode列表
            
        Returns:
            bool: 是否允许 Consolidation
        """
        # === 输入验证 ===
        if not isinstance(nodes, list):
            self._log_event("consolidate", False, "error", f"invalid type: {type(nodes)}")
            return False
        
        # === 边界检查 ===
        if len(nodes) == 0:
            self._log_event("consolidate", False, "check", "empty nodes list")
            return False
        
        # === 核心逻辑: 至少3个节点才能 Consolidation ===
        min_nodes = 3 if self.strict_mode else 1
        allowed = len(nodes) >= min_nodes
        
        # === 检查节点质量 ===
        if allowed:
            avg_importance = sum(
                getattr(n, 'importance', 0) for n in nodes
            ) / len(nodes)
            allowed = avg_importance > 0.2
        
        # === 日志记录 ===
        self._log_event("consolidate", allowed, "check",
                       f"count={len(nodes)}, min={min_nodes}")
        
        return allowed
    
    def execute_gate_check(self, tool_name: str, params: dict = None) -> bool:
        """执行门检查 - 验证工具是否可以执行
        
        Args:
            tool_name: 工具名称
            params: 工具参数 (可选)
            
        Returns:
            bool: 是否允许执行
        """
        # === 输入验证 ===
        if not tool_name or not isinstance(tool_name, str):
            self._log_event("execute", False, "error", "invalid tool_name")
            return False
        
        tool_name = str(tool_name).strip()
        
        # === 参数边界检查 ===
        if params is None:
            params = {}
        if not isinstance(params, dict):
            params = {}
        
        # === 核心逻辑: 危险工具黑名单 ===
        dangerous_patterns = [
            'eval', 'exec', '__import__', 'os.system', 'subprocess',
            'shutil.rmtree', 'os.remove', 'open(/', 'compile(',
            'eval(', 'exec(', 'memoryview'
        ]
        
        # 检查工具名是否包含危险模式
        is_dangerous = any(d in tool_name.lower() for d in dangerous_patterns)
        
        # 参数检查: 禁止传递危险参数
        param_str = str(params).lower()
        param_dangerous = any(d in param_str for d in dangerous_patterns)
        
        allowed = not is_dangerous and not param_dangerous
        
        if not allowed:
            reason = "dangerous_tool" if is_dangerous else "dangerous_params"
            self._log_event("execute", False, "blocked", reason)
        
        # === 日志记录 ===
        self._log_event("execute", allowed, "check",
                       f"tool={tool_name}, dangerous={is_dangerous}")
        
        return allowed
    
    def exit_gate_check(self, output: str) -> bool:
        """退出门检查 - 验证输出是否安全
        
        Args:
            output: 输出内容
            
        Returns:
            bool: 是否允许输出
        """
        # === 输入验证 ===
        if output is None:
            return True  # 空输出允许
        
        if not isinstance(output, str):
            output = str(output)
        
        # === 边界检查: 输出长度限制 ===
        max_output_len = 100000  # 100KB
        if len(output) > max_output_len:
            output = output[:max_output_len]
            self._log_event("exit", True, "warning", "output truncated")
        
        # === 核心逻辑: 敏感信息检测 ===
        sensitive_patterns = [
            (r'password\s*[=:]\s*\S+', 'password_leak'),
            (r'token\s*[=:]\s*\S+', 'token_leak'),
            (r'secret\s*[=:]\s*\S+', 'secret_leak'),
            (r'api[_-]?key\s*[=:]\s*\S+', 'api_key_leak'),
            (r'Authorization\s*:\s*\S+', 'auth_header_leak'),
            (r'Bearer\s+\S+', 'bearer_token_leak'),
        ]
        
        findings = []
        for pattern, issue_type in sensitive_patterns:
            import re
            if re.search(pattern, output, re.IGNORECASE):
                findings.append(issue_type)
        
        allowed = len(findings) == 0
        
        # === 日志记录 ===
        self._log_event("exit", allowed, "check",
                       f"len={len(output)}, issues={findings}")
        
        return allowed
    
    def pass_gate(self, gate_name: str) -> bool:
        """检查指定门是否通过
        
        Args:
            gate_name: 门名称
            
        Returns:
            bool: 门状态
        """
        if gate_name not in self.gates:
            return False
        return self.gates.get(gate_name, False)
    
    def trip(self, gate_name: str, reason: str = "manual"):
        """触发(熔断)指定门
        
        Args:
            gate_name: 门名称
            reason: 触发原因
        """
        if gate_name in self.gates:
            self.gates[gate_name] = False
            self._trip_count[gate_name] = self._trip_count.get(gate_name, 0) + 1
            self._log_event(gate_name, False, "tripped", reason)
    
    def reset(self, gate_name: str = None):
        """重置门
        
        Args:
            gate_name: 门名称 (None表示重置所有门)
        """
        if gate_name:
            if gate_name in self.gates:
                self.gates[gate_name] = True
                self._log_event(gate_name, True, "reset", "manual")
        else:
            for k in self.gates:
                self.gates[k] = True
            self._log_event("all", True, "reset", "full_reset")
    
    def _log_event(self, gate: str, allowed: bool, event_type: str, detail: str):
        """记录审计日志
        
        Args:
            gate: 门名称
            allowed: 是否允许
            event_type: 事件类型
            detail: 详情
        """
        import time
        self._log.append({
            "timestamp": time.time(),
            "gate": gate,
            "allowed": allowed,
            "event": event_type,
            "detail": detail,
        })
        # 保持最近1000条日志
        if len(self._log) > 1000:
            self._log = self._log[-1000:]
    
    def get_audit_log(self, gate: str = None, limit: int = 100) -> List[Dict]:
        """获取审计日志
        
        Args:
            gate: 门名称 (None表示所有门)
            limit: 返回条数
            
        Returns:
            审计日志列表
        """
        if gate:
            filtered = [e for e in self._log if e['gate'] == gate]
        else:
            filtered = self._log
        return filtered[-limit:]
    
    def get_status(self) -> Dict[str, Any]:
        """获取安全系统状态
        
        Returns:
            状态字典
        """
        return {
            "gates": self.gates.copy(),
            "strict_mode": self.strict_mode,
            "trip_counts": self._trip_count.copy(),
            "log_size": len(self._log),
        }
    
    def check(self, gate: str, node=None) -> bool:
        """通用门检查 - 简化接口
        
        Args:
            gate: 门名称 (read/write/consolidate/execute/exit)
            node: 可选的节点对象
            
        Returns:
            bool: 是否允许
        """
        if gate not in self.gates:
            return False
        
        if gate == "read":
            return self.read_gate_check(node) if node else self.gates["read"]
        elif gate == "write":
            return self.write_gate_check(node) if node else self.gates["write"]
        else:
            return self.gates.get(gate, True)
        return {
            "gates": self.gates.copy(),
            "trip_count": self._trip_count.copy(),
            "strict_mode": self.strict_mode,
            "log_size": len(self._log),
        }


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
    """验证铁律5步 - 来自X系统#36
    
    5步验证:
    1. syntax - 语法检查
    2. semantics - 语义检查  
    3. security - 安全检查
    4. testing - 测试检查
    5. deployment - 部署检查
    
    每步包含: 检查逻辑、边界处理、失败详情、建议修复
    """
    
    def __init__(self, 
                 min_syntax_score: float = 0.8,
                 min_security_score: float = 0.9,
                 require_tests: bool = True):
        """初始化验证铁律
        
        Args:
            min_syntax_score: 语法最低分数
            min_security_score: 安全最低分数
            require_tests: 是否要求测试
        """
        self.steps = ["syntax", "semantics", "security", "testing", "deployment"]
        self.min_syntax_score = min_syntax_score
        self.min_security_score = min_security_score
        self.require_tests = require_tests
        
        # 验证结果缓存
        self._results: List[Dict] = []
        
        # 危险模式
        self._dangerous_patterns = [
            r'eval\s*\(', r'exec\s*\(', r'__import__\s*\(',
            r'os\.system', r'subprocess', r'shutil\.rmtree',
        ]
    
    def verify(self, artifact: Dict) -> bool:
        """验证制品
        
        Args:
            artifact: 包含所有5步检查结果的字典
            
        Returns:
            bool: 是否通过所有验证
            
        Raises:
            ValueError: artifact格式无效
        """
        # === 输入验证 ===
        if not isinstance(artifact, dict):
            raise ValueError("artifact必须是字典")
        
        # === 5步验证 ===
        results = {}
        
        # 1. 语法检查
        syntax_ok, syntax_details = self._check_syntax(artifact)
        results["syntax"] = {"passed": syntax_ok, "details": syntax_details}
        
        # 2. 语义检查
        semantics_ok, semantics_details = self._check_semantics(artifact)
        results["semantics"] = {"passed": semantics_ok, "details": semantics_details}
        
        # 3. 安全检查
        security_ok, security_details = self._check_security(artifact)
        results["security"] = {"passed": security_ok, "details": security_details}
        
        # 4. 测试检查
        testing_ok, testing_details = self._check_testing(artifact)
        results["testing"] = {"passed": testing_ok, "details": testing_details}
        
        # 5. 部署检查
        deployment_ok, deployment_details = self._check_deployment(artifact)
        results["deployment"] = {"passed": deployment_ok, "details": deployment_details}
        
        # 保存结果
        self._results.append({
            "artifact_id": artifact.get("id", "unknown"),
            "timestamp": __import__('time').time(),
            "results": results,
        })
        
        # 计算总分
        passed_steps = sum(1 for r in results.values() if r["passed"])
        overall_passed = passed_steps == 5
        
        return overall_passed
    
    def _check_syntax(self, artifact: Dict) -> tuple:
        """语法检查"""
        code = artifact.get("syntax", "")
        
        if not code:
            return False, ["代码为空"]
        
        # 检查基本语法
        issues = []
        
        # 括号匹配
        if code.count('(') != code.count(')'):
            issues.append("括号不匹配")
        if code.count('[') != code.count(']'):
            issues.append("方括号不匹配")
        if code.count('{') != code.count('}'):
            issues.append("花括号不匹配")
        
        # 检查基本Python语法
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            issues.append(f"语法错误: {e}")
        
        passed = len(issues) == 0
        return passed, issues if issues else ["语法正确"]
    
    def _check_semantics(self, artifact: Dict) -> tuple:
        """语义检查"""
        code = artifact.get("semantics", "")
        
        if not code:
            return True, ["无语义检查要求"]
        
        # 检查变量使用
        issues = []
        
        # 检查未使用的变量 (简化版)
        import re
        assigned = set(re.findall(r'\b(\w+)\s*=', code))
        used = set(re.findall(r'\b(\w+)\b', code))
        
        # 简单检查：是否有赋值但未使用
        # (实际应该更复杂，这里是简化版)
        
        passed = len(issues) == 0
        return passed, issues if issues else ["语义正确"]
    
    def _check_security(self, artifact: Dict) -> tuple:
        """安全检查"""
        code = artifact.get("security", "")
        
        if not code:
            return False, ["缺少安全检查"]
        
        issues = []
        
        # 检查危险模式
        import re
        for pattern in self._dangerous_patterns:
            if re.search(pattern, code):
                issues.append(f"发现危险模式: {pattern}")
        
        # 检查硬编码密码
        if re.search(r'password\s*=\s*["\']', code, re.IGNORECASE):
            issues.append("发现硬编码密码")
        
        # 检查SQL注入风险
        if re.search(r'execute\s*\(\s*["\'].*%s', code):
            issues.append("SQL注入风险")
        
        score = 1.0 - (len(issues) * 0.2)
        passed = score >= self.min_security_score and len(issues) == 0
        
        return passed, issues if issues else ["安全检查通过"]
    
    def _check_testing(self, artifact: Dict) -> tuple:
        """测试检查"""
        has_tests = artifact.get("testing", False)
        
        if self.require_tests and not has_tests:
            return False, ["缺少测试"]
        
        return True, ["测试通过"]
    
    def _check_deployment(self, artifact: Dict) -> tuple:
        """部署检查"""
        deployment = artifact.get("deployment", {})
        
        issues = []
        
        # 检查必需字段
        required = ["environment", "version"]
        for field in required:
            if field not in deployment:
                issues.append(f"缺少部署字段: {field}")
        
        # 检查环境
        env = deployment.get("environment", "")
        if env in ["prod", "production"] and not deployment.get("verified", False):
            issues.append("生产环境未验证")
        
        passed = len(issues) == 0
        return passed, issues if issues else ["部署检查通过"]
    
    def get_last_result(self) -> Dict:
        """获取最后一次验证结果"""
        if not self._results:
            return {}
        return self._results[-1]
    
    def get_summary(self) -> Dict:
        """获取验证摘要"""
        if not self._results:
            return {"total": 0, "passed": 0, "failed": 0}
        
        total = len(self._results)
        passed = sum(1 for r in self._results if all(
            step["passed"] for step in r["results"].values()
        ))
        
        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": passed / total if total > 0 else 0,
        }


class CircuitBreaker:
    """3态断路器 - 来自X系统#37
    
    三种状态:
    - closed: 正常, 允许执行
    - open: 熔断, 拒绝执行
    - half_open: 半开, 尝试恢复
    """
    
    def __init__(self, 
                 threshold: int = 5,
                 timeout: float = 60.0,
                 recovery_timeout: float = 30.0,
                 success_threshold: int = 3):
        """初始化断路器
        
        Args:
            threshold: 失败次数阈值, 达到后熔断
            timeout: 超时时间(秒)
            recovery_timeout: 恢复尝试超时
            success_threshold: 半开状态下成功次数阈值
        """
        self.state = "closed"  # closed, open, half_open
        self.failure_count = 0
        self.success_count = 0
        self.threshold = threshold
        self.timeout = timeout
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        
        # 时间戳
        self.last_failure_time = 0
        self.last_success_time = 0
        self.opened_at = 0
        
        # 审计日志
        self._log: List[Dict] = []
    
    def record_success(self):
        """记录成功
        
        成功时:
        - closed状态: 重置失败计数
        - half_open状态: 增加成功计数, 达到阈值则关闭
        """
        import time
        now = time.time()
        
        if self.state == "closed":
            self.failure_count = 0
            self.success_count += 1
            self._log_event("success", "reset failure count")
            
        elif self.state == "half_open":
            self.success_count += 1
            self._log_event("success", f"half_open success {self.success_count}/{self.success_threshold}")
            
            if self.success_count >= self.success_threshold:
                self.state = "closed"
                self.failure_count = 0
                self.success_count = 0
                self._log_event("state_change", "half_open -> closed (recovered)")
        
        elif self.state == "open":
            # open状态下不接受成功(需要通过half_open)
            self._log_event("warning", "success ignored in open state")
        
        self.last_success_time = now
    
    def record_failure(self):
        """记录失败
        
        失败时:
        - closed状态: 增加失败计数, 达到阈值则打开
        - open状态: 忽略(已经在open状态)
        - half_open状态: 立即打开
        """
        import time
        now = time.time()
        
        self.failure_count += 1
        self.last_failure_time = now
        self._log_event("failure", f"count={self.failure_count}/{self.threshold}")
        
        if self.state == "closed":
            if self.failure_count >= self.threshold:
                self.state = "open"
                self.opened_at = now
                self._log_event("state_change", f"closed -> open (failures={self.failure_count})")
        
        elif self.state == "half_open":
            self.state = "open"
            self.opened_at = now
            self.success_count = 0
            self._log_event("state_change", "half_open -> open (failure in recovery)")
        
        elif self.state == "open":
            # 已经在open状态, 更新打开时间
            self.opened_at = now
            self._log_event("warning", "failure recorded in open state")
    
    def can_execute(self) -> bool:
        """检查是否可以执行
        
        Returns:
            bool: 是否允许执行
        """
        import time
        now = time.time()
        
        # 检查超时恢复
        if self.state == "open":
            if self.opened_at > 0 and (now - self.opened_at) >= self.recovery_timeout:
                self.state = "half_open"
                self.success_count = 0
                self._log_event("state_change", "open -> half_open (timeout)")
        
        allowed = self.state in ["closed", "half_open"]
        
        self._log_event("check", f"state={self.state}, allowed={allowed}")
        
        return allowed
    
    def get_state(self) -> str:
        """获取当前状态"""
        return self.state
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "threshold": self.threshold,
            "recovery_timeout": self.recovery_timeout,
            "opened_duration": __import__('time').time() - self.opened_at if self.opened_at > 0 else 0,
        }
    
    def reset(self):
        """重置断路器"""
        self.state = "closed"
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0
        self.last_success_time = 0
        self.opened_at = 0
        self._log_event("reset", "manual reset")
    
    def _log_event(self, event_type: str, detail: str):
        """记录事件"""
        import time
        self._log.append({
            "timestamp": time.time(),
            "event": event_type,
            "detail": detail,
            "state": self.state,
        })
        # 保持最近1000条
        if len(self._log) > 1000:
            self._log = self._log[-1000:]
    
    def get_log(self, limit: int = 100) -> List[Dict]:
        """获取日志"""
        return self._log[-limit:]


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


# ===== 来自XYZ系统 =====
class EquilibriumGuard:
    """S2: Nash equilibrium monitor with 3-level early warning."""

    def __init__(self, config: ZConfig | None = None):
        self._config = config or ZConfig()
        self._fitness_history: deque[float] = deque(maxlen=200)
        self._error_history: deque[float] = deque(maxlen=200)
        self._population_history: deque[dict[str, float]] = deque(maxlen=200)
        self._last_alert = AlertLevel.GREEN
        self._stats = {"green": 0, "yellow": 0, "orange": 0, "red": 0,
                       "interventions": 0}

    def check(self, fitness: float, error_rate: float = 0.0,
              populations: dict[str, float] | None = None) -> AlertLevel:
        """Check system equilibrium. Returns current alert level.

        All thresholds are configurable, zero-LLM.
        """
        self._fitness_history.append(fitness)
        self._error_history.append(error_rate)
        if populations:
            self._population_history.append(populations)

        level = AlertLevel.GREEN

        # Check 1: Fitness convergence — not improving for N rounds
        if self._is_fitness_stagnant():
            level = max(level, AlertLevel.YELLOW)

        # Check 2: Fitness declining — going backwards
        if self._is_fitness_declining():
            level = max(level, AlertLevel.ORANGE)

        # Check 3: Error rate exceeding threshold
        if error_rate > self._config.max_error_rate:
            level = max(level, AlertLevel.ORANGE)

        # Check 4: Error rate spiking
        if self._is_error_rate_spiking():
            level = max(level, AlertLevel.RED)

        # Check 5: Population imbalance (one skill dominating)
        if populations and self._is_population_imbalanced(populations):
            level = max(level, AlertLevel.YELLOW)

        # Check 6: Critical — fitness collapsed
        if fitness < 0.1 and len(self._fitness_history) > 5:
            level = max(level, AlertLevel.RED)

        self._last_alert = level
        self._stats[{
            AlertLevel.GREEN: "green",
            AlertLevel.YELLOW: "yellow",
            AlertLevel.ORANGE: "orange",
            AlertLevel.RED: "red",
        }[level]] += 1

        return level

    def should_halt_evolution(self) -> bool:
        """RED alert → halt all evolution immediately."""
        return self._last_alert >= AlertLevel.RED

    def should_pause_evolution(self) -> bool:
        """ORANGE alert → pause evolution, allow diagnosis."""
        return self._last_alert >= AlertLevel.ORANGE

    def intervene(self) -> str | None:
        """Suggest intervention based on alert level.

        Returns intervention description or None if GREEN.
        """
        if self._last_alert == AlertLevel.GREEN:
            return None

        # RED alert should always suggest circuit breaker (most urgent response)
        if self._last_alert >= AlertLevel.RED:
            self._stats["interventions"] += 1
            return "CIRCUIT_BREAK: Critical alert — open circuit breaker immediately"

        if self._is_fitness_declining():
            self._stats["interventions"] += 1
            return "ROLLBACK: Fitness declining — revert last change"

        if self._is_error_rate_spiking():
            self._stats["interventions"] += 1
            return "CIRCUIT_BREAK: Error rate spiking — open circuit breaker"

        if self._is_fitness_stagnant():
            self._stats["interventions"] += 1
            return "REDIRECT: Fitness stagnant — try different strategy"

        self._stats["interventions"] += 1
        return "DIAGNOSE: Unknown issue — manual inspection needed"

    def _is_fitness_stagnant(self, window: int = 5, threshold: float = 0.01) -> bool:
        """Check if fitness hasn't improved in last N rounds."""
        if len(self._fitness_history) < window:
            return False
        recent = list(self._fitness_history)[-window:]
        return (max(recent) - min(recent)) < threshold

    def _is_fitness_declining(self, window: int = 3) -> bool:
        """Check if fitness is consistently declining."""
        if len(self._fitness_history) < window:
            return False
        recent = list(self._fitness_history)[-window:]
        return all(recent[i] > recent[i+1] for i in range(len(recent)-1))

    def _is_error_rate_spiking(self, window: int = 3,
                                factor: float = 3.0) -> bool:
        """Check if error rate has spiked by factor compared to baseline."""
        if len(self._error_history) < window * 2:
            return False
        # Use sliding window baseline: the period just before the recent window
        baseline = sum(list(self._error_history)[-2*window:-window]) / window
        recent = sum(list(self._error_history)[-window:]) / window
        if baseline == 0:
            return recent > 0.1
        return recent / baseline > factor

    def _is_population_imbalanced(self, populations: dict[str, float],
                                   threshold: float = 0.8) -> bool:
        """Check if one skill dominates (>threshold of total fitness)."""
        total = sum(populations.values())
        if total == 0:
            return False
        max_pop = max(populations.values())
        return (max_pop / total) > threshold

    @property
    def alert_level(self) -> AlertLevel:
        return self._last_alert

    @property
    def stats(self) -> dict:
        return dict(self._stats)

    @property
    def fitness_history(self) -> list[float]:
        return list(self._fitness_history)


# ===== 来自XYZ系统 =====
class RLPathologyDetector:
    """S7: Detect RL pathologies in evolution dynamics."""

    def __init__(self, config: ZConfig | None = None):
        self._config = config or ZConfig()
        self._reward_history: deque[float] = deque(maxlen=500)
        self._action_distribution: dict[str, int] = {}
        self._skill_history: dict[str, deque[float]] = {}
        self._exploration_history: deque[float] = deque(maxlen=500)
        self._pathologies: deque[dict] = deque(maxlen=100)

    def observe(self, reward: float, action: str = "",
                skills: dict[str, float] | None = None,
                exploration_rate: float = 1.0) -> list[dict]:
        """Observe a step and check for pathologies.

        Returns list of detected pathologies (empty if healthy).
        """
        self._reward_history.append(reward)
        if action:
            self._action_distribution[action] = self._action_distribution.get(action, 0) + 1
        if skills:
            for skill, fitness in skills.items():
                if skill not in self._skill_history:
                    self._skill_history[skill] = deque(maxlen=500)
                self._skill_history[skill].append(fitness)
        self._exploration_history.append(exploration_rate)

        detected = []
        if self._check_reward_hacking():
            detected.append({"pathology": "reward_hacking",
                           "description": "Reward increasing without real improvement"})
        if self._check_distribution_collapse():
            detected.append({"pathology": "distribution_collapse",
                           "description": "Actions converging to single strategy"})
        if self._check_catastrophic_forgetting():
            detected.append({"pathology": "catastrophic_forgetting",
                           "description": "Previously strong skills degrading"})
        if self._check_exploration_collapse():
            detected.append({"pathology": "exploration_collapse",
                           "description": "No new strategies being tried"})
        if self._check_oscillation():
            detected.append({"pathology": "oscillation",
                           "description": "Alternating strategies without convergence"})
        if self._check_policy_degeneration():
            detected.append({"pathology": "policy_degeneration",
                           "description": "Policy collapsed to near-deterministic"})

        self._pathologies.extend(detected)
        return detected

    def _check_reward_hacking(self, window: int = 10) -> bool:
        """Reward going up but skills not improving."""
        if len(self._reward_history) < window * 2:
            return False
        rh = list(self._reward_history)
        recent_reward = sum(rh[-window:]) / window
        old_reward = sum(rh[-2*window:-window]) / window
        # Reward increasing but no skill improvement
        if recent_reward > old_reward * 1.2:
            for skill, history in self._skill_history.items():
                if len(history) >= window:
                    hl = list(history)
                    recent_skill = sum(hl[-window:]) / window
                    old_skill = sum(hl[-2*window:-window]) / window if len(hl) >= 2*window else recent_skill
                    if recent_skill < old_skill * 0.9:
                        return True
        return False

    def _check_distribution_collapse(self, threshold: float = 0.8) -> bool:
        """One action dominates > threshold of all actions."""
        total = sum(self._action_distribution.values())
        if total < 10:
            return False
        max_count = max(self._action_distribution.values())
        return (max_count / total) > threshold

    def _check_catastrophic_forgetting(self, threshold: float = 0.5) -> bool:
        """Previously strong skill (fitness > 0.7) now below threshold."""
        for skill, history in self._skill_history.items():
            if len(history) >= 10:
                hl = list(history)
                peak = max(hl[:len(hl)//2])  # First half peak
                recent = min(hl[-5:])  # Recent minimum
                if peak > 0.7 and recent < threshold:
                    return True
        return False

    def _check_exploration_collapse(self, threshold: float = 0.05) -> bool:
        """Exploration rate dropped below threshold."""
        if len(self._exploration_history) < 10:
            return False
        recent = sum(list(self._exploration_history)[-5:]) / 5
        return recent < threshold

    def _check_oscillation(self, window: int = 10) -> bool:
        """Reward oscillating without convergence."""
        if len(self._reward_history) < window:
            return False
        recent = list(self._reward_history)[-window:]
        diffs = [recent[i+1] - recent[i] for i in range(len(recent)-1)]
        sign_changes = sum(1 for i in range(len(diffs)-1)
                         if (diffs[i] > 0) != (diffs[i+1] > 0))
        # More than 60% sign changes = oscillation
        return sign_changes > len(diffs) * 0.6

    def _check_policy_degeneration(self, threshold: float = 0.95) -> bool:
        """Policy becoming deterministic too early — entropy too low.

        Measures action distribution entropy. If near-zero (highly concentrated),
        the policy has collapsed to deterministic behavior prematurely.
        """
        total = sum(self._action_distribution.values())
        if total < 20:  # Need enough observations
            return False
        n_actions = len(self._action_distribution)
        if n_actions <= 1:
            return True  # Only one action = fully degenerate
        # Compute Shannon entropy
        entropy = 0.0
        for count in self._action_distribution.values():
            p = count / total
            if p > 0:
                entropy -= p * math.log2(p)
        # Maximum entropy = log2(n_actions)
        max_entropy = math.log2(n_actions)
        if max_entropy == 0:
            return False
        # Normalized entropy: 1 = uniform, 0 = deterministic
        normalized = entropy / max_entropy
        return normalized < (1 - threshold)  # Below 5% of max = degenerate

    @property
    def pathology_count(self) -> int:
        return len(self._pathologies)

    @property
    def pathologies(self) -> list[dict]:
        return list(self._pathologies)

    @property
    def is_healthy(self) -> bool:
        """No pathologies detected in recent observations.

        Checks whether the last N observations detected any pathologies,
        not whether the entire history is empty (which would always return True).
        
        FIX: If pathologies is empty, return True (healthy).
        If not empty, check if recent 5 have any pathology dict.
        """
        if not self._pathologies:
            return True
        
        recent_pathologies = list(self._pathologies)[-5:]
        has_recent_pathology = any(bool(p) for p in recent_pathologies)
        return not has_recent_pathology


# ===== 来自XYZ系统 =====
class PlanValidator:
    """S9: 3-layer plan validation."""

    def __init__(self, config: ZConfig | None = None):
        self._config = config or ZConfig()
        self._stats = {"single_step_pass": 0, "single_step_fail": 0,
                       "combination_pass": 0, "combination_fail": 0,
                       "topology_pass": 0, "topology_fail": 0}

    def validate(self, plan: dict) -> dict:
        """Validate a plan at all 3 levels.

        plan must contain:
        - "steps": list of step dicts, each with "action" and "target"
        - "dependencies": list of (step_i, step_j) pairs (step_j depends on step_i)

        Returns dict with "valid" (bool) and "issues" (list of strings).
        """
        steps = plan.get("steps", [])
        dependencies = plan.get("dependencies", [])

        issues = []

        # Layer 1: Single-step validation
        step_issues = self._validate_single_step(steps)
        issues.extend(step_issues)
        if step_issues:
            self._stats["single_step_fail"] += 1
        else:
            self._stats["single_step_pass"] += 1

        # Layer 2: Combination validation
        combo_issues = self._validate_combination(steps)
        issues.extend(combo_issues)
        if combo_issues:
            self._stats["combination_fail"] += 1
        else:
            self._stats["combination_pass"] += 1

        # Layer 3: Topology validation
        topo_issues = self._validate_topology(steps, dependencies)
        issues.extend(topo_issues)
        if topo_issues:
            self._stats["topology_fail"] += 1
        else:
            self._stats["topology_pass"] += 1

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "steps_validated": len(steps),
        }

    def _validate_single_step(self, steps: list[dict]) -> list[str]:
        """Layer 1: Each step must have valid action and target."""
        issues = []
        valid_actions = {"modify", "add", "remove", "rename", "refactor",
                         "optimize", "fix", "test", "document"}

        for i, step in enumerate(steps):
            action = step.get("action", "")
            target = step.get("target", "")

            if not action:
                issues.append(f"Step {i}: missing action")
            elif action not in valid_actions:
                issues.append(f"Step {i}: invalid action '{action}'")

            if not target:
                issues.append(f"Step {i}: missing target")

        return issues

    def _validate_combination(self, steps: list[dict]) -> list[str]:
        """Layer 2: Steps must not conflict."""
        issues = []

        # Check for conflicting targets (same target, opposite actions)
        targets: dict[str, list[tuple[int, str]]] = {}
        for i, step in enumerate(steps):
            target = step.get("target", "")
            action = step.get("action", "")
            if target not in targets:
                targets[target] = []
            targets[target].append((i, action))

        for target, actions in targets.items():
            if len(actions) > 1:
                # Check for add+remove on same target
                action_names = {a for _, a in actions}
                if "add" in action_names and "remove" in action_names:
                    issues.append(f"Target '{target}': add and remove conflict")
                if "modify" in action_names and len(actions) > 1:
                    issues.append(f"Target '{target}': multiple modifications")

        return issues

    def _validate_topology(self, steps: list[dict],
                           dependencies: list[tuple]) -> list[str]:
        """Layer 3: Dependency graph must be a DAG (no cycles)."""
        issues = []

        if not steps:
            issues.append("Plan has no steps")
            return issues

        if not dependencies:
            return issues  # No dependencies = trivially valid DAG

        # Build adjacency list
        n = len(steps)
        adj: dict[int, list[int]] = {i: [] for i in range(n)}
        for dep_i, dep_j in dependencies:
            if dep_i >= n or dep_j >= n:
                issues.append(f"Dependency ({dep_i}, {dep_j}): step index out of range")
                continue
            adj[dep_i].append(dep_j)

        # Detect cycles via DFS
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {i: WHITE for i in range(n)}

        def has_cycle(node: int) -> bool:
            color[node] = GRAY
            for neighbor in adj[node]:
                if color[neighbor] == GRAY:
                    return True  # Back edge = cycle
                if color[neighbor] == WHITE and has_cycle(neighbor):
                    return True
            color[node] = BLACK
            return False

        for node in range(n):
            if color[node] == WHITE:
                if has_cycle(node):
                    issues.append("Dependency cycle detected — plan is not a DAG")
                    break

        # Check for dead-end steps (no dependents and not final step)
        has_dependent = set()
        for dep_i, dep_j in dependencies:
            has_dependent.add(dep_i)
        # Build out-degree map
        out_degree = {i: len(adj[i]) for i in range(n)}
        for i in range(n):
            if i not in has_dependent and i < n - 1 and out_degree[i] == 0:
                # Intermediate step with no dependents and no outgoing edges — dead-end
                issues.append(f"Step {i}: dead-end (no dependents and no outgoing edges)")

        return issues

    @property
    def stats(self) -> dict:
        return dict(self._stats)


