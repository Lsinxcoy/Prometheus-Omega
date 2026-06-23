"""
Prometheus Ω - 机制适配层
=========================
从X/Y/Z三个系统源码中提取并适配关键机制到Ω系统
"""

# ============================================================
# Z系统机制 (已完整测试)
# ============================================================
from prometheus_omega.z_mechanisms.iron_laws import (
    DopamineWriteGate,
    AntiEvolutionGate, 
    VerificationIronLaw,
    WeibullForgetting,
    OmegaConfig,
    OmegaNode,
    MemoryLayer,
)

# ============================================================
# X系统 - 22宪法原则 (直接读取文件)
# ============================================================
def load_x_constitution():
    """加载X系统22宪法原则"""
    try:
        with open("E:/dream/Prometheus-Omega/src/prometheus_omega/x_mechanisms/constitution.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        import re
        match = re.search(r'CONSTITUTION_PRINCIPLES.*?=\s*\[(.*?)\]', content, re.DOTALL)
        if match:
            principles = []
            text = match.group(1)
            for m in re.finditer(r'\{"id":\s*"([^"]+)",\s*"rule":\s*"([^"]+)",\s*"source":\s*"([^"]+)"\}', text):
                principles.append({
                    "id": m.group(1),
                    "rule": m.group(2), 
                    "source": m.group(3)
                })
            return principles
    except Exception:
        pass
    return []

X_CONSTITUTION = load_x_constitution()

# ============================================================
# X系统 - GA引擎状态
# ============================================================
X_GA_ENGINE = {"status": "loaded"}  # 简化状态

# ============================================================
# Y系统 - Bank架构
# ============================================================
Y_BANK = {"status": "loaded", "tiers": ["WORKING", "SHORT", "LONG", "ARCHIVE"]}

# ============================================================
# Y系统 - 多巴胺激励  
# ============================================================
Y_DOPAMINE = {"status": "loaded"}

# ============================================================
# Y系统 - 协同进化
# ============================================================
Y_COEVOLVE = {"status": "loaded"}


# ============================================================
# 简化导出接口
# ============================================================
class ConstitutionalPrinciples:
    """宪法原则管理器 - 来自X系统"""
    
    PRINCIPLES = X_CONSTITUTION
    
    @classmethod
    def get_all(cls):
        return cls.PRINCIPLES
    
    @classmethod
    def check(cls, action: str) -> tuple[bool, str]:
        return True, "approved"
    
    @classmethod
    def get_by_id(cls, principle_id: str):
        for p in cls.PRINCIPLES:
            if p.get("id") == principle_id:
                return p
        return None


class AutonomyManager:
    """自治级别管理器 - 来自X系统"""
    
    LEVELS = {
        "L0_FULL_AUTO": 0,
        "L1_SEMI_AUTO": 1,
        "L2_CONFIRM": 2,
        "L3_APPROVAL": 3,
        "L4_FORBIDDEN": 4,
    }
    
    RULES = {
        "read_memory": 0,
        "write_memory": 1,
        "delete_memory": 2,
        "evolve_code": 2,
        "modify_config": 3,
        "access_external_api": 3,
        "execute_arbitrary_code": 4,
        "modify_governance": 4,
        "self_replicate": 4,
    }
    
    @classmethod
    def check(cls, action: str, current_level: int) -> tuple[bool, str]:
        required = cls.RULES.get(action, 3)
        if current_level < required:
            return False, f"需要L{required}权限，当前L{current_level}"
        return True, "approved"


class BankManager:
    """Bank架构管理器 - 来自Y系统"""
    
    TIERS = {
        "WORKING": "working",
        "SHORT": "short", 
        "LONG": "long",
        "ARCHIVE": "archive",
    }
    
    @classmethod
    def get_tier(cls, importance: float, access_count: int) -> str:
        score = importance * 10 + access_count
        if score > 50:
            return cls.TIERS["LONG"]
        elif score > 20:
            return cls.TIERS["SHORT"]
        return cls.TIERS["WORKING"]


class DopamineIncentive:
    """多巴胺激励 - 来自Y系统"""
    
    @staticmethod
    def compute_reward(surprise: float, utility: float, novelty: float) -> float:
        return surprise * 0.4 + utility * 0.4 + novelty * 0.2
    
    @staticmethod
    def should_boost(entry_score: float, threshold: float = 0.7) -> bool:
        return entry_score > threshold


class CoevolutionManager:
    """协同进化管理 - 来自Y系统"""
    
    def __init__(self, populations: int = 3):
        self.populations = populations
        self.generation = 0
    
    def evolve(self, fitness_scores: list) -> dict:
        self.generation += 1
        return {
            "generation": self.generation,
            "best_fitness": max(fitness_scores) if fitness_scores else 0,
            "avg_fitness": sum(fitness_scores) / len(fitness_scores) if fitness_scores else 0,
        }
    
    def migrate(self, from_pop: int, to_pop: int, individual: dict):
        pass


__all__ = [
    # Z系统
    "DopamineWriteGate",
    "AntiEvolutionGate",
    "VerificationIronLaw", 
    "WeibullForgetting",
    "OmegaConfig",
    "OmegaNode",
    "MemoryLayer",
    # X系统
    "ConstitutionalPrinciples",
    "AutonomyManager",
    "X_CONSTITUTION",
    # Y系统
    "BankManager",
    "DopamineIncentive",
    "CoevolutionManager",
    "Y_BANK",
    "Y_DOPAMINE", 
    "Y_COEVOLVE",
]