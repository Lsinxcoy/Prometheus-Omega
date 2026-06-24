"""Path Denylist - 敏感路径保护

基于Loop Engineering的安全机制：
- 永远不自动修改敏感路径
- 需要人工门控审核
"""
import fnmatch
from pathlib import Path
from typing import Tuple, List


# 基于Loop Engineering safety.md的敏感路径模式
SENSITIVE_PATTERNS = [
    # 环境变量
    "**/.env*",
    "**/.env.*",
    "**/.env.local",
    "**/.env.development",
    "**/.env.production",
    
    # 密钥和凭证
    "**/secrets/**",
    "**/credentials/**",
    "**/*_key*",
    "**/*_secret*",
    "**/api_key*",
    "**/password*",
    "**/*.pem",
    "**/*.key",
    "**/id_rsa*",
    "**/.ssh/**",
    
    # 基础设施
    "**/.terraform/**",
    "**/k8s/production/**",
    "**/kubernetes/**",
    "**/helm/**",
    
    # 数据库和迁移
    "**/migrations/**",
    "**/database/**",
    "**/*.sql",
    
    # 认证和支付
    "**/auth/**",
    "**/payments/**",
    "**/billing/**",
    "**/stripe/**",
    
    # Git忽略的安全文件
    "**/.gitignore",  # 特殊：这个可以修改但要小心
]

# 高风险模式 - 绝对禁止自动修改
HIGH_RISK_PATTERNS = [
    "**/.env*",
    "**/secrets/**",
    "**/credentials/**",
    "**/auth/**",
    "**/payments/**",
    "**/billing/**",
    "**/*_secret*",
    "**/id_rsa*",
]


def is_sensitive_path(path: str) -> bool:
    """检查路径是否敏感
    
    Returns:
        True if path matches any sensitive pattern
    """
    path_lower = path.lower().replace("\\", "/")
    
    for pattern in SENSITIVE_PATTERNS:
        # 移除 **/ 前缀用于fnmatch
        match_pattern = pattern.replace("**/", "")
        if fnmatch.fnmatch(path_lower, match_pattern):
            return True
    
    return False


def is_high_risk_path(path: str) -> bool:
    """检查路径是否高风险
    
    高风险路径需要人工门控，不能自动修改
    """
    path_lower = path.lower().replace("\\", "/")
    
    for pattern in HIGH_RISK_PATTERNS:
        match_pattern = pattern.replace("**/", "")
        if fnmatch.fnmatch(path_lower, match_pattern):
            return True
    
    return False


def check_path_allowed(path: str, allowlist: List[str] = None) -> Tuple[bool, str]:
    """检查路径是否允许修改
    
    Args:
        path: 要检查的路径
        allowlist: 白名单路径模式
        
    Returns:
        (allowed, reason) tuple
    """
    # 先检查白名单
    if allowlist:
        path_lower = path.lower().replace("\\", "/")
        for pattern in allowlist:
            match_pattern = pattern.replace("**/", "")
            if fnmatch.fnmatch(path_lower, match_pattern):
                return True, "allowlisted"
    
    # 检查高风险
    if is_high_risk_path(path):
        return False, "high_risk_path_requires_human"
    
    # 检查敏感
    if is_sensitive_path(path):
        return False, "sensitive_path"
    
    return True, "allowed"


def get_sensitive_paths(root: str, max_depth: int = 5) -> List[str]:
    """递归扫描获取所有敏感路径
    
    Args:
        root: 根目录
        max_depth: 最大扫描深度
        
    Returns:
        敏感路径列表
    """
    from pathlib import Path
    
    root_path = Path(root)
    sensitive = []
    
    def scan(path: Path, depth: int):
        if depth > max_depth:
            return
            
        try:
            for item in path.iterdir():
                if item.is_file():
                    str_path = str(item.relative_to(root_path))
                    if is_sensitive_path(str_path):
                        sensitive.append(str_item = str(item))
                elif item.is_dir():
                    scan(item, depth + 1)
        except PermissionError:
            pass
    
    scan(root_path, 0)
    return sensitive


class PathDenylist:
    """路径拒绝列表管理器"""
    
    def __init__(self, additional_patterns: List[str] = None,
                 allowlist: List[str] = None):
        self.patterns = list(SENSITIVE_PATTERNS)
        if additional_patterns:
            self.patterns.extend(additional_patterns)
        self.allowlist = allowlist or []
    
    def check(self, path: str) -> Tuple[bool, str]:
        """检查路径"""
        return check_path_allowed(path, self.allowlist)
    
    def add_allowlist(self, pattern: str) -> None:
        """添加白名单"""
        self.allowlist.append(pattern)
    
    def get_all_sensitive(self, root: str) -> List[str]:
        """获取所有敏感路径"""
        return get_sensitive_paths(root)


# 导出单例
default_denylist = PathDenylist()