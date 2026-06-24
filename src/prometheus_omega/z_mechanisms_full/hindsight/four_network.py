"""四网络记忆架构 - 基于Hindsight的核心创新

论文: Hindsight is 20/20 (2512.12818)
核心概念: 将记忆组织为四个逻辑网络

1. World Facts (世界事实) - 关于外部世界的客观知识
2. Agent Experiences (智能体经验) - 交互历史和体验
3. Entity Summaries (实体摘要) - 动态更新的实体档案
4. Evolving Beliefs (演化信念) - 智能体自身的目标和信念

三核心操作:
- retain: 保留 - 将对话流转为结构化记忆
- recall: 召回 - 检索相关记忆  
- reflect: 反思 - 推理并更新记忆
"""
from dataclasses import dataclass, field
from typing import Any, Optional, List, Dict
from datetime import datetime
from enum import Enum
import uuid
import json


class MemoryNetwork(Enum):
    """四网络类型"""
    WORLD = "world"           # 世界事实
    EXPERIENCES = "experiences"  # 智能体经验
    SUMMARIES = "summaries"   # 实体摘要
    BELIEFS = "beliefs"       # 演化信念


class FactType(Enum):
    """事实类型"""
    WORLD = "world"           # 客观事实
    ASSISTANT = "assistant"   # 主观体验


@dataclass
class MemoryFact:
    """记忆事实 - 四网络的基本单元"""
    fact_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    network: MemoryNetwork = MemoryNetwork.WORLD
    fact_type: FactType = FactType.WORLD
    
    # 时序信息
    occurred_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # 关联信息
    entity_ids: List[str] = field(default_factory=list)
    related_fact_ids: List[str] = field(default_factory=list)
    source_episode_id: Optional[str] = None
    
    # 元数据
    confidence: float = 1.0
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "fact_id": self.fact_id,
            "content": self.content,
            "network": self.network.value,
            "fact_type": self.fact_type.value,
            "occurred_at": self.occurred_at.isoformat() if self.occurred_at else None,
            "created_at": self.created_at.isoformat(),
            "entity_ids": self.entity_ids,
            "confidence": self.confidence,
            "tags": self.tags
        }


@dataclass
class EntitySummary:
    """实体摘要 - 动态更新的实体档案
    
    与Hindsight的Entity Summaries对应：
    - 从多次交互中累积关于实体的信息
    - 定期整合为连贯的摘要
    - 支持时间衰减和置信度更新
    """
    entity_id: str
    name: str
    
    # 摘要内容
    current_summary: str = ""
    summary_version: int = 0
    
    # 时序信息
    first_seen: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    update_count: int = 0
    
    # 统计
    total_interactions: int = 0
    key_facts: List[str] = field(default_factory=list)
    attribute_distribution: Dict[str, float] = field(default_factory=dict)
    
    def update_summary(self, new_facts: List[str], importance: float = 0.5) -> None:
        """更新摘要 - 基于新事实融合"""
        self.key_facts.extend(new_facts)
        # 保留最近的20条关键事实
        self.key_facts = self.key_facts[-20:]
        
        # 更新摘要版本
        self.summary_version += 1
        self.update_count += 1
        self.last_updated = datetime.now()
        
        # 简单融合策略
        if new_facts:
            self.current_summary = f"更新于{self.last_updated.strftime('%Y-%m-%d')}: 共有{len(self.key_facts)}条关键信息"


@dataclass
class Belief:
    """演化信念 - 智能体自身的目标和信念
    
    与Hindsight的Evolving Beliefs对应：
    - 随着交互形成关于用户/世界的信念
    - 信念随新证据更新
    - 可追溯信念来源
    """
    belief_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    
    # 信念强度和置信度
    strength: float = 0.5  # 0-1, 信念的坚定程度
    confidence: float = 0.5  # 0-1, 对信念正确性的置信度
    
    # 来源追踪
    source_fact_ids: List[str] = field(default_factory=list)
    supporting_evidence: List[str] = field(default_factory=list)
    contradicting_evidence: List[str] = field(default_factory=list)
    
    # 时序
    formed_at: datetime = field(default_factory=datetime.now)
    last_strengthened: datetime = field(default_factory=datetime.now)
    last_weakened: Optional[datetime] = None
    
    # 演化历史
    history: List[Dict[str, Any]] = field(default_factory=list)
    
    def strengthen(self, evidence: str, strength_delta: float = 0.1) -> None:
        """强化信念"""
        self.strength = min(1.0, self.strength + strength_delta)
        self.confidence = min(1.0, self.confidence + strength_delta * 0.5)
        self.supporting_evidence.append(evidence)
        self.last_strengthened = datetime.now()
        
        # 记录历史
        self.history.append({
            "action": "strengthen",
            "evidence": evidence,
            "new_strength": self.strength,
            "timestamp": datetime.now().isoformat()
        })
    
    def weaken(self, evidence: str, strength_delta: float = 0.1) -> None:
        """弱化信念"""
        self.strength = max(0.0, self.strength - strength_delta)
        self.last_weakened = datetime.now()
        self.contradicting_evidence.append(evidence)
        
        # 如果矛盾证据太多，降低置信度
        if len(self.contradicting_evidence) > len(self.supporting_evidence) * 2:
            self.confidence = max(0.0, self.confidence - strength_delta)
        
        self.history.append({
            "action": "weaken",
            "evidence": evidence,
            "new_strength": self.strength,
            "timestamp": datetime.now().isoformat()
        })


class FourNetworkMemory:
    """四网络记忆 - 基于Hindsight的核心架构
    
    四个逻辑网络：
    1. World Facts: 客观世界知识
    2. Experiences: 交互经验
    3. Summaries: 实体摘要
    4. Beliefs: 演化信念
    """
    
    def __init__(self, bank_id: str = "default"):
        self.bank_id = bank_id
        
        # 四个网络的存储
        self.world_facts: Dict[str, MemoryFact] = {}      # 世界事实
        self.experiences: Dict[str, MemoryFact] = {}      # 智能体经验
        self.summaries: Dict[str, EntitySummary] = {}     # 实体摘要
        self.beliefs: Dict[str, Belief] = {}              # 演化信念
        
        # 索引加速
        self._by_entity: Dict[str, List[str]] = {}        # entity_id -> fact_ids
        self._by_tag: Dict[str, List[str]] = {}           # tag -> fact_ids
        self._by_time: Dict[str, List[str]] = {}          # date -> fact_ids
    
    def retain(self, content: str, fact_type: FactType = FactType.WORLD,
               entity_ids: List[str] = None, tags: List[str] = None,
               occurred_at: datetime = None) -> MemoryFact:
        """retain: 保留 - 将对话流转为结构化记忆
        
        Hindsight的核心操作之一：
        - 解析内容，提取事实
        - 根据类型存入对应网络
        - 建立索引便于检索
        """
        # 确定目标网络
        if fact_type == FactType.WORLD:
            network = MemoryNetwork.WORLD
            storage = self.world_facts
        else:
            network = MemoryNetwork.EXPERIENCES
            storage = self.experiences
        
        # 创建记忆事实
        fact = MemoryFact(
            content=content,
            network=network,
            fact_type=fact_type,
            occurred_at=occurred_at or datetime.now(),
            entity_ids=entity_ids or [],
            tags=tags or []
        )
        
        # 存入对应网络
        storage[fact.fact_id] = fact
        
        # 建立索引
        for eid in fact.entity_ids:
            if eid not in self._by_entity:
                self._by_entity[eid] = []
            self._by_entity[eid].append(fact.fact_id)
        
        for tag in fact.tags:
            if tag not in self._by_tag:
                self._by_tag[tag] = []
            self._by_tag[tag].append(fact.fact_id)
        
        # 时间索引
        date_key = fact.created_at.strftime("%Y-%m-%d")
        if date_key not in self._by_time:
            self._by_time[date_key] = []
        self._by_time[date_key].append(fact.fact_id)
        
        return fact
    
    def recall(self, query: str, network_filter: List[MemoryNetwork] = None,
               top_k: int = 10) -> List[MemoryFact]:
        """recall: 召回 - 检索相关记忆
        
        Hindsight的核心操作之一：
        - 多网络并行检索
        - 支持混合排序
        - 返回最相关的记忆
        """
        results = []
        
        # 确定搜索范围
        if network_filter is None:
            networks = [MemoryNetwork.WORLD, MemoryNetwork.EXPERIENCES]
        else:
            networks = network_filter
        
        # 简单关键词匹配（实际可集成向量搜索）
        query_lower = query.lower()
        
        for network in networks:
            if network == MemoryNetwork.WORLD:
                facts = self.world_facts
            elif network == MemoryNetwork.EXPERIENCES:
                facts = self.experiences
            else:
                continue
            
            for fact in facts.values():
                # 计算相关性分数
                score = self._calculate_relevance(query_lower, fact)
                if score > 0:
                    results.append((score, fact))
        
        # 排序并返回top_k
        results.sort(key=lambda x: x[0], reverse=True)
        return [f for _, f in results[:top_k]]
    
    def _calculate_relevance(self, query: str, fact: MemoryFact) -> float:
        """计算查询与事实的相关性"""
        score = 0.0
        
        # 关键词匹配
        content_lower = fact.content.lower()
        query_words = query.split()
        
        for word in query_words:
            if word in content_lower:
                score += 1.0
        
        # 标签匹配
        for tag in fact.tags:
            if tag in query:
                score += 0.5
        
        # 时间衰减
        if fact.occurred_at:
            days_old = (datetime.now() - fact.occurred_at).days
            time_factor = max(0.5, 1.0 - days_old / 365)  # 1年后衰减到0.5
            score *= time_factor
        
        return score
    
    def reflect(self, query: str) -> Dict[str, Any]:
        """reflect: 反思 - 推理并更新记忆
        
        Hindsight的核心操作之一：
        - 分析相关记忆
        - 生成洞察
        - 可能更新信念
        """
        # 1. 检索相关记忆
        relevant_facts = self.recall(query, top_k=5)
        
        # 2. 分析实体
        entity_analysis = self._analyze_entities(relevant_facts)
        
        # 3. 生成反思结果
        reflection = {
            "query": query,
            "relevant_count": len(relevant_facts),
            "key_facts": [f.content for f in relevant_facts[:3]],
            "entity_analysis": entity_analysis,
            "suggested_beliefs": self._generate_belief_suggestions(relevant_facts),
            "timestamp": datetime.now().isoformat()
        }
        
        return reflection
    
    def _analyze_entities(self, facts: List[MemoryFact]) -> Dict[str, Any]:
        """分析相关实体"""
        entity_counts: Dict[str, int] = {}
        
        for fact in facts:
            for eid in fact.entity_ids:
                entity_counts[eid] = entity_counts.get(eid, 0) + 1
        
        return {
            "entities_mentioned": list(entity_counts.keys()),
            "entity_frequency": entity_counts
        }
    
    def _generate_belief_suggestions(self, facts: List[MemoryFact]) -> List[str]:
        """基于事实生成信念建议"""
        suggestions = []
        
        # 简单规则：从频繁共现的实体生成信念
        all_entities = []
        for fact in facts:
            all_entities.extend(fact.entity_ids)
        
        # 统计频率
        from collections import Counter
        entity_counter = Counter(all_entities)
        
        # 生成建议
        for entity, count in entity_counter.most_common(3):
            if count >= 2:
                suggestions.append(f"经常与{entity}相关")
        
        return suggestions
    
    # === 实体摘要管理 ===
    
    def get_or_create_summary(self, entity_id: str, name: str) -> EntitySummary:
        """获取或创建实体摘要"""
        if entity_id not in self.summaries:
            self.summaries[entity_id] = EntitySummary(
                entity_id=entity_id,
                name=name
            )
        return self.summaries[entity_id]
    
    def update_entity_summary(self, entity_id: str, name: str, new_facts: List[str]) -> EntitySummary:
        """更新实体摘要"""
        summary = self.get_or_create_summary(entity_id, name)
        summary.total_interactions += 1
        summary.update_summary(new_facts)
        return summary
    
    # === 信念管理 ===
    
    def form_belief(self, content: str, source_fact_ids: List[str] = None) -> Belief:
        """形成新信念"""
        belief = Belief(
            content=content,
            source_fact_ids=source_fact_ids or []
        )
        self.beliefs[belief.belief_id] = belief
        return belief
    
    def update_belief(self, belief_id: str, strengthen: bool, evidence: str) -> None:
        """更新信念强度"""
        if belief_id not in self.beliefs:
            return
        
        belief = self.beliefs[belief_id]
        if strengthen:
            belief.strengthen(evidence)
        else:
            belief.weaken(evidence)
    
    def get_beliefs(self, min_strength: float = 0.3) -> List[Belief]:
        """获取符合条件的信念"""
        return [b for b in self.beliefs.values() if b.strength >= min_strength]
    
    # === 统计和导出 ===
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取四网络记忆统计"""
        return {
            "bank_id": self.bank_id,
            "world_facts_count": len(self.world_facts),
            "experiences_count": len(self.experiences),
            "entities_count": len(self.summaries),
            "beliefs_count": len(self.beliefs),
            "total_memories": len(self.world_facts) + len(self.experiences),
            "indexes": {
                "by_entity": len(self._by_entity),
                "by_tag": len(self._by_tag),
                "by_time": len(self._by_time)
            }
        }
    
    def export(self) -> dict:
        """导出所有记忆数据"""
        return {
            "bank_id": self.bank_id,
            "world_facts": {k: v.to_dict() for k, v in self.world_facts.items()},
            "experiences": {k: v.to_dict() for k, v in self.experiences.items()},
            "summaries": {
                k: {"entity_id": v.entity_id, "name": v.name, "summary": v.current_summary}
                for k, v in self.summaries.items()
            },
            "beliefs": [
                {"id": b.belief_id, "content": b.content, "strength": b.strength}
                for b in self.beliefs.values()
            ]
        }


def create_four_network_memory(bank_id: str = "default") -> FourNetworkMemory:
    """工厂函数：创建四网络记忆"""
    return FourNetworkMemory(bank_id=bank_id)