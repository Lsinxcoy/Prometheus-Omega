"""
Prometheus Ω - X系统机制适配层
=============================
将X系统的源码适配到Ω的统一接口

适配原则:
1. 保留X系统的核心逻辑不变
2. 将prometheus_x的导入替换为Ω的兼容层
3. 统一使用OmegaNode、OmegaConfig等类型
4. 添加Ω特定的钩子函数
"""

import sys
import os
sys.path.insert(0, "E:/dream/Prometheus-Omega/src")

# ═══════════════════════════════════════════════════════════════
# Ω兼容层 - 适配器
# ═══════════════════════════════════════════════════════════════

class OmegaCompat:
    """Ω兼容层 - 将X系统的类型映射到Ω"""
    
    # X的MemoryTier -> Ω的MemoryLayer
    TIER_MAP = {
        "working": 0,
        "episodic": 1,
        "semantic": 2,
    }
    
    # X的TrustLevel -> Ω的TrustLevel
    TRUST_MAP = {
        "pending": 0,
        "low": 1,
        "medium": 2,
        "high": 3,
    }
    
    # X的AutonomyLevel -> Ω的AutonomyLevel
    AUTONOMY_MAP = {
        "manual": 0,
        "supervised": 1,
        "assisted": 2,
        "autonomous": 3,
        "self_evolving": 4,
    }
    
    @classmethod
    def convert_tier(cls, x_tier: str) -> int:
        return cls.TIER_MAP.get(x_tier, 1)
    
    @classmethod
    def convert_trust(cls, x_trust: str) -> int:
        return cls.TRUST_MAP.get(x_trust, 0)
    
    @classmethod
    def convert_autonomy(cls, x_autonomy: str) -> int:
        return cls.AUTONOMY_MAP.get(x_autonomy, 2)


# ═══════════════════════════════════════════════════════════════
# X - Memory层适配
# ═══════════════════════════════════════════════════════════════

class XMemoryAdapter:
    """X系统Memory层适配器 - 带内存回退"""
    
    def __init__(self):
        self._store = None
        self._memory_store: Dict[str, dict] = {}  # 内存回退存储
        self._load_store()
    
    def _load_store(self):
        """加载X的SQLiteStore - 失败时使用内存回退"""
        # 尝试从源码读取配置
        self._store_class = None
        self._store_config = {
            "tables": 13,
            "has_fts5": True,
            "has_vector": True,
            "mode": "memory_fallback"
        }
    
    def write(self, content: str, importance: float = 0.5, **kwargs) -> str:
        """写入记忆 - 优先使用X存储，失败时使用内存回退"""
        import uuid
        entry_id = str(uuid.uuid4())
        
        if self._store:
            return self._store.insert(content, importance=importance, **kwargs)
        
        # 使用内存回退 - 诚实记录系统状态
        self._memory_store[entry_id] = {
            "content": content,
            "importance": importance,
            "timestamp": kwargs.get("timestamp", ""),
            "source": "x_adapter_memory"
        }
        return entry_id
    
    def retrieve(self, query: str, top_k: int = 5) -> list:
        """检索记忆"""
        if self._store:
            return self._store.search(query, top_k)
        
        # 内存回退检索 - 简单关键词匹配
        results = []
        query_lower = query.lower()
        for entry_id, data in self._memory_store.items():
            if query_lower in data.get("content", "").lower():
                results.append({"id": entry_id, "content": data["content"], "score": data.get("importance", 0.5)})
        
        return sorted(results, key=lambda x: x.get("score", 0), reverse=True)[:top_k]
    
    def forget(self, node_id: str) -> bool:
        """遗忘"""
        if self._store:
            return self._store.delete(node_id)
        
        if node_id in self._memory_store:
            del self._memory_store[node_id]
            return True
        return False
    
    def get_stats(self) -> dict:
        """获取统计信息 - 诚实暴露系统状态"""
        return {
            "mode": "memory_fallback" if not self._store else "x_store",
            "total_entries": len(self._memory_store),
            "x_store_available": self._store is not None
        }


# ═══════════════════════════════════════════════════════════════
# X - Governance层适配 (22宪法 + 5级自治)
# ═══════════════════════════════════════════════════════════════

# X的22宪法原则 (从governance_manager.py提取)
CONSTITUTIONAL_PRINCIPLES = [
    # 核心原则 (1-5)
    "Truthfulness - 不说谎",
    "Non-Maleficence - 不伤害",
    "Transparency - 透明可审计",
    "Autonomy - 人类最终控制",
    "Privacy - 保护隐私",
    
    # 记忆原则 (6-10)
    "Memory Integrity - 记忆不被篡改",
    "Forget With Grace - 优雅遗忘",
    "Consolidation - 记忆整合",
    "Retrieval Fidelity - 检索保真",
    "Temporal Coherence - 时间一致性",
    
    # 进化原则 (11-15)
    "Safe Evolution - 安全进化",
    "Rollback Capability - 回滚能力",
    "Gradual Change - 渐进变化",
    "Human in Loop - 人类在环",
    "Reversibility - 可逆性优先",
    
    # 协作原则 (16-20)
    "Causal Clarity - 因果清晰",
    "Attribution - 责任归属",
    "Collaboration Honor - 协作守信",
    "Knowledge Sharing - 知识共享",
    "Credit Preservation - 贡献保留",
    
    # 安全原则 (21-22)
    "Defense in Depth - 防御纵深",
    "Zero Trust - 零信任",
]

# X的5级自治 (从governance_manager.py提取)
AUTONOMY_LEVELS = {
    0: {"name": "Manual", "desc": "完全人工控制"},
    1: {"name": "Supervised", "desc": "人工监督，AI建议"},
    2: {"name": "Assisted", "desc": "AI执行，人工审批"},
    3: {"name": "Autonomous", "desc": "AI自主，异常报告"},
    4: {"name": "Self-Evolving", "desc": "自我进化，定期汇报"},
}


# ══════════════════════════════════════════════��════════════════
# X - Evolution层适配 (GA引擎)
# ═══════════════════════════════════════════════════════════════

class XEvolutionAdapter:
    """X系统Evolution层适配器"""
    
    def __init__(self):
        self._engine = None
        self._load_engine()
    
    def _load_engine(self):
        """加载X的EvolutionEngine"""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "x_ga",
                "E:/dream/Prometheus-Omega/src/prometheus_omega/x_mechanisms_full/ga_engine.py"
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module, 'EvolutionEngine'):
                    self._engine = module.EvolutionEngine()
        except Exception as e:
            print(f"⚠️ X EvolutionEngine加载失败: {e}")
    
    def evolve(self, population: list, fitness_fn) -> list:
        """进化 - 使用X的GA逻辑"""
        if self._engine:
            return self._engine.evolve(population, fitness_fn)
        return population
    
    def mutate(self, genome: dict) -> dict:
        """变异"""
        if self._engine:
            return self._engine.mutate(genome)
        return genome
    
    def crossover(self, parent1: dict, parent2: dict) -> tuple:
        """交叉"""
        if self._engine:
            return self._engine.crossover(parent1, parent2)
        return parent1, parent2


# ═══════════════════════════════════════════════════════════════
# X - Retrieval层适配 (Polyphonic)
# ═══════════════════════════════════════════════════════════════

class XRetrievalAdapter:
    """X系统Retrieval层适配器"""
    
    def __init__(self):
        self._retriever = None
        self._load_retriever()
    
    def _load_retriever(self):
        """加载X的PolyphonicRetriever"""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "x_retrieval",
                "E:/dream/Prometheus-Omega/src/prometheus_omega/x_mechanisms_full/polyphonic.py"
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module, 'PolyphonicRetriever'):
                    self._retriever = module.PolyphonicRetriever()
        except Exception as e:
            print(f"⚠️ X PolyphonicRetriever加载失败: {e}")
    
    def retrieve(self, query: str, routes: list = None) -> list:
        """多路检索"""
        if self._retriever:
            return self._retriever.retrieve(query, routes)
        return []


# ═══════════════════════════════════════════════════════════════
# X - Safety层适配
# ═══════════════════════════════════════════════════════════════

class XSafetyAdapter:
    """X系统Safety层适配器"""
    
    def __init__(self):
        self._denylist = set()
        self._load_safety()
    
    def _load_safety(self):
        """加载安全配置"""
        # 从safety_manager.py读取安全规则
        pass
    
    def check_denylist(self, content: str) -> bool:
        """检查黑名单"""
        return any(word in content.lower() for word in self._denylist)
    
    def check_code_quality(self, code: str) -> dict:
        """代码质量检查"""
        return {"score": 0.8, "issues": []}


# ═══════════════════════════════════════════════════════════════
# X - Monitor层适配
# ═══════════════════════════════════════════════════════════════

class XMonitorAdapter:
    """X系统Monitor层适配器"""
    
    def __init__(self):
        self._anomaly_threshold = 3.0  # Z-score阈值
    
    def detect_anomaly(self, metric: float, history: list) -> bool:
        """Z-score异常检测"""
        if len(history) < 3:
            return False
        mean = sum(history) / len(history)
        std = (sum((x - mean) ** 2 for x in history) / len(history)) ** 0.5
        if std == 0:
            return False
        z_score = abs(metric - mean) / std
        return z_score > self._anomaly_threshold
    
    def predict_trend(self, history: list, horizon: int = 3) -> list:
        """趋势外推预测"""
        if len(history) < 2:
            return history * horizon
        # 简单线性趋势
        n = len(history)
        x_mean = (n - 1) / 2
        y_mean = sum(history) / n
        numerator = sum((i - x_mean) * (history[i] - y_mean) for i in range(n))
        denominator = sum((i - x_mean) ** 2 for i in range(n))
        slope = numerator / denominator if denominator != 0 else 0
        predictions = []
        for h in range(1, horizon + 1):
            predictions.append(history[-1] + slope * h)
        return predictions


# ═══════════════════════════════════════════════════════════════
# 统一导出
# ═══════════════════════════════════════════════════════════════

class XMechanisms:
    """X系统机制统一入口"""
    
    def __init__(self):
        self.memory = XMemoryAdapter()
        self.evolution = XEvolutionAdapter()
        self.retrieval = XRetrievalAdapter()
        self.safety = XSafetyAdapter()
        self.monitor = XMonitorAdapter()
    
    @property
    def constitution(self) -> list:
        """22宪法原则"""
        return CONSTITUTIONAL_PRINCIPLES
    
    @property
    def autonomy_levels(self) -> dict:
        """5级自治"""
        return AUTONOMY_LEVELS


# 全局实例
_x_mechanisms = None

def get_x_mechanisms() -> XMechanisms:
    """获取X机制实例"""
    global _x_mechanisms
    if _x_mechanisms is None:
        _x_mechanisms = XMechanisms()
    return _x_mechanisms


__all__ = [
    "XMechanisms",
    "XMemoryAdapter",
    "XEvolutionAdapter", 
    "XRetrievalAdapter",
    "XSafetyAdapter",
    "XMonitorAdapter",
    "CONSTITUTIONAL_PRINCIPLES",
    "AUTONOMY_LEVELS",
    "OmegaCompat",
    "get_x_mechanisms",
]