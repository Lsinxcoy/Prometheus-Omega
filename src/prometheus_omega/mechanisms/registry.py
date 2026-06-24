"""
Prometheus Ω - 完整XYZ机制清单
=============================
92个机制完整列表 - 基于XYZ_MECHANISMS.md

已集成: 28个 (3铁律+22宪法+3 Y机制)
待集成: 64个
"""

# ═══════════════════════════════════════════════════════════════
# X系统 49个机制
# ═══════════════════════════════════════════════════════════════

# L0 Foundation (4个)
X_MECHANISMS_FOUNDATION = {
    "UUIDv7": {"desc": "时序ID", "layer": "L0", "status": "空壳"},
    "NodeType": {"desc": "42节点类型", "layer": "L0", "status": "空壳"},
    "EdgeType": {"desc": "40边类型", "layer": "L0", "status": "空壳"},
    "DeterministicRuleEngine": {"desc": "44规则引擎", "layer": "L0", "status": "空壳"},
}

# L2 Memory (3个)
X_MECHANISMS_MEMORY = {
    "MemoryEntryV3": {"desc": "15维记忆", "layer": "L2", "status": "空壳"},
    "SQLiteStore": {"desc": "13表存储+FTS5", "layer": "L2", "status": "空壳"},
    "OME": {"desc": "离线内存引擎", "layer": "L2", "status": "空壳"},
}

# L4 Lifecycle (4个)
X_MECHANISMS_LIFECYCLE = {
    "WeibullForgetting": {"desc": "Weibull遗忘", "layer": "L4", "status": "已集成-Z"},
    "BankMigration": {"desc": "4层Bank迁移", "layer": "L4", "status": "空壳"},
    "VeracityConfidence": {"desc": "贝叶斯置信度", "layer": "L4", "status": "空壳"},
    "DopamineWriteGate": {"desc": "乘法门控", "layer": "L4", "status": "已集成-Z"},
}

# L5 Evolution (6个)
X_MECHANISMS_EVOLUTION = {
    "GeneticAlgorithm": {"desc": "12层GA", "layer": "L5", "status": "空壳"},
    "CGP": {"desc": "笛卡尔遗传编程", "layer": "L5", "status": "空壳"},
    "IslandModel": {"desc": "Island并行+环迁移", "layer": "L5", "status": "空壳"},
    "ASTMutator": {"desc": "4操作变异", "layer": "L5", "status": "空壳"},
    "Speculative": {"desc": "推测进化", "layer": "L5", "status": "空壳"},
    "UCB1Bandit": {"desc": "UCB1 bandit选择", "layer": "L5", "status": "空壳"},
}

# L6 Organs (3个)
X_MECHANISMS_ORGANS = {
    "BaseOrgan": {"desc": "12-Factor器官基类", "layer": "L6", "status": "空壳"},
    "DNAMethod": {"desc": "DNA特征提取", "layer": "L6", "status": "空壳"},
    "PromotionGate": {"desc": "晋升门控", "layer": "L6", "status": "空壳"},
}

# L7 Safety (4个)
X_MECHANISMS_SAFETY = {
    "FourLayerDefense": {"desc": "4层防御", "layer": "L7", "status": "空壳"},
    "FiveGates": {"desc": "链式熔断", "layer": "L7", "status": "空壳"},
    "CodeSlopDetector": {"desc": "5维代码检测", "layer": "L7", "status": "空壳"},
    "ForbiddenOps": {"desc": "20禁止操作", "layer": "L7", "status": "空壳"},
}

# L8 Governance (6个) - 已集成
X_MECHANISMS_GOVERNANCE = {
    "Constitution": {"desc": "22宪法原则", "layer": "L8", "status": "已集成"},
    "AutonomyLevel": {"desc": "5级自治", "layer": "L8", "status": "已集成"},
    "TrustSystem": {"desc": "3级信任", "layer": "L8", "status": "空壳"},
    "ConfidenceGate": {"desc": "置信度门控", "layer": "L8", "status": "空壳"},
    "EvolutionGrill": {"desc": "7问审查", "layer": "L8", "status": "空壳"},
    "DriftDetector": {"desc": "4维漂移检测", "layer": "L8", "status": "空壳"},
}

# L9 Monitor (4个)
X_MECHANISMS_MONITOR = {
    "ZScoreAnomaly": {"desc": "Z-score异常", "layer": "L9", "status": "空壳"},
    "TrendExtrapolation": {"desc": "趋势外推", "layer": "L9", "status": "空壳"},
    "CORAL": {"desc": "心跳循环", "layer": "L9", "status": "空壳"},
    "SelfHealing": {"desc": "自愈引擎", "layer": "L9", "status": "空壳"},
}

# L10 Collaboration (4个)
X_MECHANISMS_COLLABORATION = {
    "VectorClock": {"desc": "向量时钟", "layer": "L10", "status": "空壳"},
    "CausalGraph": {"desc": "因果图", "layer": "L10", "status": "空壳"},
    "CollectiveAttention": {"desc": "群体注意力", "layer": "L10", "status": "空壳"},
    "KnowledgeBridge": {"desc": "跨代理转移", "layer": "L10", "status": "空壳"},
}

# L11 Ecosystem (11个) - 多个来自论文非X原创
X_MECHANISMS_ECOSYSTEM = {
    "LotkaVolterra": {"desc": "生态竞争", "layer": "L11", "source": "论文", "status": "空壳"},
    "EDRE": {"desc": "均衡机制", "layer": "L11", "source": "论文", "status": "空壳"},
    "HarnessX": {"desc": "9维+8钩子引擎", "layer": "L11", "source": "论文2606.14249", "status": "空壳"},
    "ToolPredictor": {"desc": "工具适应性预测", "layer": "L11", "status": "空壳"},
    "OperationalMirror": {"desc": "病理学检测", "layer": "L11", "status": "空壳"},
    "FGGM": {"desc": "版本控制", "layer": "L11", "source": "论文", "status": "空壳"},
    "EvolveMem": {"desc": "自进化检索", "layer": "L11", "status": "空壳"},
    "ExperienceRecall": {"desc": "轨迹记忆", "layer": "L11", "status": "空壳"},
    "MARS": {"desc": "信念状态追踪", "layer": "L11", "status": "空壳"},
    "LIFE": {"desc": "失败归因", "layer": "L11", "status": "空壳"},
    "RTKCache": {"desc": "3层缓存", "layer": "L11", "status": "空壳"},
    "SkillClaw": {"desc": "4级路由", "layer": "L11", "status": "空壳"},
}

# ═══════════════════════════════════════════════════════════════
# Y系统 19个机制
# ═══════════════════════════════════════════════════════════════

Y_MECHANISMS = {
    # Memory (4个)
    "BankArchitecture": {"desc": "分层记忆银行", "module": "memory", "status": "已集成"},
    "DopamineReward": {"desc": "多巴胺激励", "module": "memory", "status": "已集成"},
    "VeracityScore": {"desc": "真实性评估", "module": "memory", "status": "空壳"},
    "Consolidation": {"desc": "记忆整合", "module": "memory", "status": "空壳"},
    # Evolution (10个)
    "Coevolution": {"desc": "协同进化", "module": "evolution", "status": "已集成"},
    "CORALLoop": {"desc": "反射整合重定向", "module": "evolution", "status": "空壳"},
    "DAGScheduler": {"desc": "DAG调度", "module": "evolution", "status": "空壳"},
    "DirectionalEvo": {"desc": "方向进化", "module": "evolution", "status": "空壳"},
    "DynamicsModel": {"desc": "动力学模型", "module": "evolution", "status": "空壳"},
    "Mutator": {"desc": "变异器", "module": "evolution", "status": "空壳"},
    "PopulationMgr": {"desc": "种群管理", "module": "evolution", "status": "空壳"},
    "SpeculativeY": {"desc": "推测执行", "module": "evolution", "status": "空壳"},
    "StabilityCtrl": {"desc": "稳定性控制", "module": "evolution", "status": "空壳"},
    "ToolLifecycle": {"desc": "工具生命周期", "module": "evolution", "status": "空壳"},
    "TraceEngine": {"desc": "追踪引擎", "module": "evolution", "status": "空壳"},
    # Safety (3个)
    "AntiPattern": {"desc": "反模式检测", "module": "safety", "status": "空壳"},
    "Gates": {"desc": "多重门控", "module": "safety", "status": "空壳"},
    "SafeHarbor": {"desc": "安全港", "module": "safety", "status": "空壳"},
    # Evaluation (1个)
    "SEAGym": {"desc": "自进化评估", "module": "evaluation", "status": "空壳"},
}

# ═══════════════════════════════════════════════════════════════
# Z系统 24个机制
# ═══════════════════════════════════════════════════════════════

Z_MECHANISMS = {
    # Loop (4个)
    "LoopStateMachine": {"desc": "循环状态机", "module": "loop", "status": "空壳"},
    "ConvergenceDetector": {"desc": "收敛检测", "module": "loop", "status": "已集成-Z"},
    "LoopPersistence": {"desc": "状态持久化", "module": "loop", "status": "空壳"},
    "BudgetToken": {"desc": "Token预算", "module": "loop", "status": "空壳"},
    # Skills (2个)
    "SkillRegistry": {"desc": "技能注册表", "module": "skills", "status": "空壳"},
    "Curator": {"desc": "策展人", "module": "skills", "status": "空壳"},
    # Evaluation (4个)
    "Thermodynamic": {"desc": "热力学智能", "module": "evaluation", "source": "论文2606.20231", "status": "空壳"},
    "RareValidDetector": {"desc": "稀有有效检测", "module": "evaluation", "status": "空壳"},
    "FiveViewEvaluator": {"desc": "五视图评估", "module": "evaluation", "status": "空壳"},
    "MarginalAdvantage": {"desc": "边际优势累积", "module": "evaluation", "status": "空壳"},
    # Memory (4个)
    "GraphMemory": {"desc": "图结构记忆", "module": "memory", "source": "Graphiti(28k★)", "status": "空壳"},
    "KeyNodeTopic": {"desc": "分层记忆节点", "module": "memory", "status": "空壳"},
    "ToolReasoner": {"desc": "工具推理", "module": "memory", "status": "空壳"},
    "ToolLoop": {"desc": "5工具推理循环", "module": "memory", "status": "空壳"},
    # Execution (4个)
    "DAGExecutor": {"desc": "DAG执行器", "module": "execution", "status": "空壳"},
    "MonitoredDAG": {"desc": "可监控DAG", "module": "execution", "status": "空壳"},
    "ParallelDAG": {"desc": "并行DAG", "module": "execution", "status": "空壳"},
    "RetryableDAG": {"desc": "可重试DAG", "module": "execution", "status": "空壳"},
    # Hindsight (4个)
    "FourNetworkMemory": {"desc": "四网络记忆", "module": "hindsight", "source": "Hindsight(17k★)", "status": "空壳"},
    "RetainRecallReflect": {"desc": "三操作API", "module": "hindsight", "status": "空壳"},
    "DispositionLearner": {"desc": "用户偏好学习", "module": "hindsight", "status": "空壳"},
    "ConsolidationEngine": {"desc": "整合引擎", "module": "hindsight", "status": "空壳"},
    # Safety (2个)
    "PathDenylist": {"desc": "路径黑名单", "module": "safety", "status": "空壳"},
    "RateLimiter": {"desc": "速率限制", "module": "safety", "status": "空壳"},
}

# ═══════════════════════════════════════════════════════════════
# 统计
# ═══════════════════════════════════════════════════════════════

def get_statistics():
    """获取机制统计"""
    all_mechanisms = {
        **X_MECHANISMS_FOUNDATION,
        **X_MECHANISMS_MEMORY,
        **X_MECHANISMS_LIFECYCLE,
        **X_MECHANISMS_EVOLUTION,
        **X_MECHANISMS_ORGANS,
        **X_MECHANISMS_SAFETY,
        **X_MECHANISMS_GOVERNANCE,
        **X_MECHANISMS_MONITOR,
        **X_MECHANISMS_COLLABORATION,
        **X_MECHANISMS_ECOSYSTEM,
        **Y_MECHANISMS,
        **Z_MECHANISMS,
    }
    
    total = len(all_mechanisms)
    integrated = sum(1 for m in all_mechanisms.values() if m["status"] == "已集成")
    integrated_z = sum(1 for m in all_mechanisms.values() if m["status"] == "已集成-Z")
    empty = sum(1 for m in all_mechanisms.values() if m["status"] == "空壳")
    
    # 统计来源问题
    from_paper = sum(1 for m in all_mechanisms.values() if m.get("source") == "论文")
    
    return {
        "total": total,
        "integrated": integrated,
        "integrated_z": integrated_z,
        "empty": empty,
        "from_paper": from_paper,
    }

# ═══════════════════════════════════════════════════════════════
# 快速访问接口
# ═══════════════════════════════════════════════════════════════

class MechanismRegistry:
    """机制注册表"""
    
    def __init__(self):
        self.x = {
            "foundation": X_MECHANISMS_FOUNDATION,
            "memory": X_MECHANISMS_MEMORY,
            "lifecycle": X_MECHANISMS_LIFECYCLE,
            "evolution": X_MECHANISMS_EVOLUTION,
            "organs": X_MECHANISMS_ORGANS,
            "safety": X_MECHANISMS_SAFETY,
            "governance": X_MECHANISMS_GOVERNANCE,
            "monitor": X_MECHANISMS_MONITOR,
            "collaboration": X_MECHANISMS_COLLABORATION,
            "ecosystem": X_MECHANISMS_ECOSYSTEM,
        }
        self.y = Y_MECHANISMS
        self.z = Z_MECHANISMS
    
    def get_all(self):
        result = {}
        for category, mechanisms in self.x.items():
            result.update(mechanisms)
        result.update(self.y)
        result.update(self.z)
        return result
    
    def get_status(self, name: str) -> str:
        """获取机制状态"""
        all_mechs = self.get_all()
        return all_mechs.get(name, {}).get("status", "未知")

__all__ = [
    "X_MECHANISMS_FOUNDATION",
    "X_MECHANISMS_MEMORY", 
    "X_MECHANISMS_LIFECYCLE",
    "X_MECHANISMS_EVOLUTION",
    "X_MECHANISMS_ORGANS",
    "X_MECHANISMS_SAFETY",
    "X_MECHANISMS_GOVERNANCE",
    "X_MECHANISMS_MONITOR",
    "X_MECHANISMS_COLLABORATION",
    "X_MECHANISMS_ECOSYSTEM",
    "Y_MECHANISMS",
    "Z_MECHANISMS",
    "MechanismRegistry",
    "get_statistics",
]