"""
Prometheus Ω - 统一数据结构定义
===============================
所有层使用统一的OmegaNode和OmegaConfig
"""

from enum import IntEnum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid


class NodeType(IntEnum):
    """节点类型枚举"""
    CONCEPT = 1      # 概念节点
    EVENT = 2        # 事件节点  
    SKILL = 3        # 技能节点
    PLAN = 4         # 计划节点
    RESULT = 5       # 结果节点
    REFLECTION = 6   # 反思节点
    OBSERVATION = 7  # 观察节点
    MEMORY = 8       # 记忆节点
    TOOL = 9         # 工具节点
    AGENT = 10       # 代理节点
    SYSTEM = 11      # 系统节点


class TrustLevel(IntEnum):
    """信任等级"""
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERIFIED = 4


class MemoryLayer(IntEnum):
    """记忆层"""
    SENSORY = 0      # 感官记忆 (秒级)
    WORKING = 1      # 工作记忆 (分钟级)
    EPISODIC = 2     # 情景记忆 (小时级)
    SEMANTIC = 3     # 语义记忆 (长期)


@dataclass
class OmegaNode:
    """
    统一节点定义 - 所有层使用此结构
    """
    # 核心字段
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    type: NodeType = NodeType.CONCEPT
    
    # 评估指标
    utility: float = 0.0          # 效用值 [0, 10]
    importance: float = 0.0       # 重要性 [0, 1]
    confidence: float = 0.5       # 置信度 [0, 1]
    veracity: float = 0.5        # 真实性 [0, 1]
    
    # 信任与安全
    trust: TrustLevel = TrustLevel.NONE
    
    # 时间戳
    created_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    
    # 记忆层
    layer: MemoryLayer = MemoryLayer.WORKING
    
    # 元数据
    source: str = ""              # 来源
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # 图关系
    parent_ids: List[str] = field(default_factory=list)
    child_ids: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'content': self.content,
            'type': int(self.type),
            'utility': self.utility,
            'importance': self.importance,
            'confidence': self.confidence,
            'veracity': self.veracity,
            'trust': int(self.trust),
            'layer': int(self.layer),
            'created_at': self.created_at.isoformat(),
            'accessed_at': self.accessed_at.isoformat(),
            'source': self.source,
            'tags': self.tags,
            'metadata': self.metadata,
            'parent_ids': self.parent_ids,
            'child_ids': self.child_ids,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OmegaNode':
        """从字典创建"""
        node = cls(
            id=data.get('id', str(uuid.uuid4())),
            content=data.get('content', ''),
            type=NodeType(data.get('type', 1)),
            utility=data.get('utility', 0.0),
            importance=data.get('importance', 0.0),
            confidence=data.get('confidence', 0.5),
            veracity=data.get('veracity', 0.5),
            trust=TrustLevel(data.get('trust', 0)),
            layer=MemoryLayer(data.get('layer', 1)),
            source=data.get('source', ''),
            tags=data.get('tags', []),
            metadata=data.get('metadata', {}),
            parent_ids=data.get('parent_ids', []),
            child_ids=data.get('child_ids', []),
        )
        # 处理时间戳
        if 'created_at' in data:
            node.created_at = datetime.fromisoformat(data['created_at'])
        if 'accessed_at' in data:
            node.accessed_at = datetime.fromisoformat(data['accessed_at'])
        return node
    
    def access(self):
        """更新访问时间"""
        self.accessed_at = datetime.now()
    
    def update_content(self, new_content: str):
        """更新内容"""
        self.content = new_content
        self.last_modified = datetime.now()


@dataclass  
class OmegaConfig:
    """
    统一配置定义 - 所有层使用此配置
    """
    # 基础配置
    max_memory_size: int = 10000
    max_context_length: int = 8192
    
    # 写入门控 (DopamineWriteGate)
    write_gate_tau: float = 1.0          # 质量阈值
    write_gate_importance_threshold: float = 0.3
    write_gate_veracity_threshold: float = 0.5
    
    # 进化门控 (AntiEvolutionGate)
    evolution_hypothesis_min_length: int = 50
    evolution_hypothesis_keywords: List[str] = None
    
    # 验证铁律 (VerificationIronLaw)
    iron_law_min_improvement: float = 0.05
    iron_law_significance_level: float = 0.05
    
    # 遗忘机制
    forgetting_enabled: bool = True
    forgetting_half_life: float = 7.0    # 天
    
    # Bank迁移
    bank_migration_threshold: float = 0.7
    
    # 遗传算法
    ga_population_size: int = 50
    ga_generations: int = 100
    ga_mutation_rate: float = 0.1
    ga_crossover_rate: float = 0.7
    
    # 检索
    retrieval_top_k: int = 10
    retrieval_rrf_k: int = 60
    
    # 并发
    max_workers: int = 4
    
    def __post_init__(self):
        if self.evolution_hypothesis_keywords is None:
            self.evolution_hypothesis_keywords = [
                'improve', 'optimize', 'reduce', 'enhance', 'fix', 'increase'
            ]
    
    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}


# 兼容性别名
Node = OmegaNode
Config = OmegaConfig