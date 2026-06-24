# 基础导入
from __future__ import annotations
import sys, os, re, json, time, datetime
from typing import Dict, List, Any, Optional, Callable, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum, IntEnum, auto


from enum import Enum, IntEnum, auto
from typing import Dict, List, Any, Optional

def _get_keynode():
    """延迟导入KeyNode避免循环依赖"""
    from prometheus_omega.memory import KeyNode
    return KeyNode
# 核心导入
from prometheus_omega.foundation import (
    ZConfig, OmegaConfig, Strictness, SecurityPosture, AutonomyLevel,
    MemoryLayer, LifecycleAction, GateResult, WriteOperator, CommitState,
    ProvenanceType, Node, Edge, Constraint, EvolutionCheckResult, 
    GateCheckResult, WriteGateResult, EvolutionOutcome
)
from prometheus_omega.monitor import AlertLevel, Alert
from dataclasses import dataclass, field

class EntryCategory(Enum):
    """记忆类别"""
    FACT = "fact"
    EXPERIENCE = "experience"
    SKILL = "skill"
    TOOL = "tool"
    TASK = "task"
    CONCEPT = "concept"
    RELATIONSHIP = "relationship"
    METADATA = "metadata"


@dataclass
class UnifiedEntry:
    """15维统一记忆条目 - 来自X系统最丰富数据模型
    
    15个维度:
    1. id - 唯一标识
    2. content - 内容
    3. category - 类别
    4. importance - 重要性 (0-1)
    5. veracity - 真实性 (0-1)
    6. created_at - 创建时间
    7. updated_at - 更新时间
    8. last_accessed - 最��访问
    9. access_count - 访问次数
    10. tags - 标签
    11. entity_ids - 关联实体
    12. source - 来源
    13. provenance - 来源追踪
    14. embedding - 向量嵌入
    15. metadata - 扩展元数据
    """
    
    # 必需字段
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    category: EntryCategory = EntryCategory.FACT
    
    # 重要性与真实性
    importance: float = 0.5  # 0-1
    veracity: float = 0.5    # 置信度
    
    # 时间戳
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_accessed: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    access_count: int = 0
    
    # 关联
    tags: List[str] = field(default_factory=list)
    entity_ids: List[str] = field(default_factory=list)
    source: str = "system"
    
    # 来源追踪
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    # 向量
    embedding: Optional[List[float]] = None
    
    # 扩展
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # 额外维度 (完整15维)
    embedding_model: str = ""
    language: str = "zh"
    isarchived: bool = False
    expires_at: Optional[datetime] = None
    
    def access(self):
        """记录访问"""
        self.last_accessed = datetime.now(timezone.utc)
        self.access_count += 1
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "content": self.content,
            "category": self.category.value,
            "importance": self.importance,
            "veracity": self.veracity,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "access_count": self.access_count,
            "tags": self.tags,
            "entity_ids": self.entity_ids,
            "source": self.source,
            "provenance": self.provenance,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "UnifiedEntry":
        """从字典创建"""
        if "category" in data and isinstance(data["category"], str):
            data["category"] = EntryCategory(data["category"])
        return cls(**data)


# ===== 四网络记忆 - 来自Z系统Hindsight =====
class MemoryNetwork(Enum):
    """四网络类型 - 来自Z系统Hindsight"""
    WORLD = "world"              # 世界事实
    EXPERIENCES = "experiences"  # 智能体经验
    SUMMARIES = "summaries"      # 实体摘要
    BELIEFS = "beliefs"          # 演化信念


@dataclass
class FourNetworkFact:
    """四网络记忆事实"""
    fact_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    network_type: MemoryNetwork = MemoryNetwork.WORLD

    # 实体关联
    entity_ids: List[str] = field(default_factory=list)

    # 时间和置信度
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    confidence: float = 0.5
    
    def is_trusted(self, threshold: float = 0.6) -> bool:
        return self.confidence >= threshold
    
    def get_age(self) -> float:
        return (datetime.now(timezone.utc) - self.created_at).total_seconds()
    
    def to_dict(self) -> Dict:
        return {
            'fact_id': self.fact_id,
            'content': self.content[:100] + '...' if len(self.content) > 100 else self.content,
            'network_type': self.network_type.value if isinstance(self.network_type, Enum) else self.network_type,
            'entity_ids': self.entity_ids,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat(),
        }
    
    def add_entity(self, entity_id: str):
        if entity_id not in self.entity_ids:
            self.entity_ids.append(entity_id)


class MemoryNetwork(Enum):
    """四网络类型"""
    WORLD = "world"
    EXPERIENCES = "experiences"
    SUMMARIES = "summaries"
    BELIEFS = "beliefs"


class FourNetworkMemory:
    """四网络记忆系统 - 来自Z系统Hindsight
    
    整合Hindsight的核心创新:
    - World Facts: 客观知识
    - Experiences: 交互历史
    - Summaries: 实体档案
    - Beliefs: 演化信念
    
    新增方法:
    - consolidate: 记忆整合
    - prune: 记忆修剪
    - get_temporal_context: 时间上下文
    """
    
    def __init__(self, bank_id: str = "default", max_per_network: int = 10000):
        self.bank_id = bank_id
        self.max_per_network = max_per_network
        
        # 四个网络存储
        self.world_facts: Dict[str, FourNetworkFact] = {}
        self.experiences: Dict[str, FourNetworkFact] = {}
        self.summaries: Dict[str, FourNetworkFact] = {}
        self.beliefs: Dict[str, FourNetworkFact] = {}
        
        # 访问统计
        self._access_counts: Dict[str, int] = {}
        
        # 索引 (加速检索)
        self._content_index: Dict[str, Set[str]] = {}  # word -> fact_ids
        self._tag_index: Dict[str, Set[str]] = {}       # tag -> fact_ids
    
    def store(self, entry) -> bool:
        """存储条目 (统一接口)
        
        Args:
            entry: UnifiedEntry 或 FourNetworkFact
            
        Returns:
            bool: 是否成功
        """
        from datetime import datetime, timezone
        
        # 如果是 UnifiedEntry，转换为 FourNetworkFact
        if hasattr(entry, 'id') and hasattr(entry, 'content'):
            fact = FourNetworkFact(
                fact_id=entry.id,
                content=entry.content,
                network_type=MemoryNetwork.WORLD,
                confidence=entry.confidence if hasattr(entry, 'confidence') else 0.5,
                tags=entry.tags if hasattr(entry, 'tags') else [],
            )
            self.world_facts[fact.fact_id] = fact
            self._index_fact(fact)
            return True
        
        # 如果是 FourNetworkFact
        if hasattr(entry, 'fact_id'):
            if entry.network_type == MemoryNetwork.WORLD:
                self.world_facts[entry.fact_id] = entry
            elif entry.network_type == MemoryNetwork.EXPERIENCES:
                self.experiences[entry.fact_id] = entry
            elif entry.network_type == MemoryNetwork.SUMMARIES:
                self.summaries[entry.fact_id] = entry
            elif entry.network_type == MemoryNetwork.BELIEFS:
                self.beliefs[entry.fact_id] = entry
            self._index_fact(entry)
            return True
        
        return False
    
    def _index_fact(self, fact: FourNetworkFact):
        """索引事实用于快速检索"""
        # 内容分词索引
        words = fact.content.lower().split()
        for word in words:
            if len(word) > 2:  # 忽略短词
                if word not in self._content_index:
                    self._content_index[word] = set()
                self._content_index[word].add(fact.fact_id)
        
        # 标签索引
        for tag in fact.tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = set()
            self._tag_index[tag].add(fact.fact_id)
    
    def _remove_from_index(self, fact_id: str):
        """从索引中移除"""
        # 简化实现: 重建索引(实际应该反向映射)
        pass
    
    # === 三操作 API (来自Hindsight) ===
    
    def retain(self, content: str, network: MemoryNetwork = MemoryNetwork.WORLD,
               entity_ids: List[str] = None, tags: List[str] = None,
               confidence: float = 0.5, source: str = "") -> FourNetworkFact:
        """retain: 存入记忆
        
        Args:
            content: 记忆内容
            network: 目标网络
            entity_ids: 关联实体ID
            tags: 标签
            confidence: 置信度 (0-1)
            source: 来源
            
        Returns:
            FourNetworkFact: 存储的事实
        """
        # 检查容量
        network_key = network.value
        current_size = len(getattr(self, f"{network_key}_facts"))
        
        if current_size >= self.max_per_network:
            # 需要修剪
            self.prune(network, count=100)
        
        fact = FourNetworkFact(
            content=content,
            network_type=network,
            entity_ids=entity_ids or [],
            tags=tags or [],
            confidence=confidence,
            source=source,
        )
        
        # 存储到对应网络
        if network == MemoryNetwork.WORLD:
            self.world_facts[fact.fact_id] = fact
        elif network == MemoryNetwork.EXPERIENCES:
            self.experiences[fact.fact_id] = fact
        elif network == MemoryNetwork.SUMMARIES:
            self.summaries[fact.fact_id] = fact
        elif network == MemoryNetwork.BELIEFS:
            self.beliefs[fact.fact_id] = fact
        
        # 索引
        self._index_fact(fact)
        
        return fact
    
    def recall(self, query: str, network: MemoryNetwork = None,
               top_k: int = 10) -> List[FourNetworkFact]:
        """recall: 检索记忆
        
        Args:
            query: 查询字符串
            network: 指定网络 (None表示所有网络)
            top_k: 返回数量
            
        Returns:
            List[FourNetworkFact]: 相关记忆列表
        """
        import math
        
        # 确定搜索范围
        networks = [network] if network else list(MemoryNetwork)
        
        # 查询分词
        query_words = query.lower().split()
        
        results = []
        
        for net in networks:
            if net == MemoryNetwork.WORLD:
                facts = self.world_facts
            elif net == MemoryNetwork.EXPERIENCES:
                facts = self.experiences
            elif net == MemoryNetwork.SUMMARIES:
                facts = self.summaries
            elif net == MemoryNetwork.BELIEFS:
                facts = self.beliefs
            else:
                continue
            
            # 计算相关性分数
            for fact in facts.values():
                score = self._calculate_relevance(query_words, fact)
                if score > 0:
                    results.append((score, fact))
        
        # 排序并返回top_k
        results.sort(key=lambda x: x[0], reverse=True)
        return [f for _, f in results[:top_k]]
    
    def _calculate_relevance(self, query_words: List[str], fact: FourNetworkFact) -> float:
        """计算查询与事实的相关性"""
        if not query_words:
            return 0.0
        
        score = 0.0
        content_lower = fact.content.lower()
        
        # 1. 关键词匹配分数
        for word in query_words:
            if word in content_lower:
                score += 1.0
            # 标签匹配
            if any(word in tag.lower() for tag in fact.tags):
                score += 0.5
        
        # 2. 置信度加权
        score *= (0.5 + fact.confidence * 0.5)
        
        # 3. 时间衰减 (新记忆权重略高)
        days_old = (datetime.now(timezone.utc) - fact.created_at).days
        time_factor = math.exp(-days_old / 365)  # 1年后衰减到37%
        score *= time_factor
        
        return score
    
    def reflect(self, query: str) -> Dict[str, Any]:
        """reflect: 反思学习
        
        基于检��到的记忆生成洞察
        
        Args:
            query: 反思主题
            
        Returns:
            Dict: 反思结果
        """
        # 收集相关记忆
        relevant = self.recall(query, top_k=50)
        
        if not relevant:
            return {
                "query": query,
                "relevant_count": 0,
                "networks_found": [],
                "key_themes": [],
                "insights": ["无相关记忆"],
            }
        
        # 提取主题
        themes = self._extract_themes(relevant)
        
        # 生成洞察
        insights = self._generate_insights(relevant)
        
        # 分析网络分布
        networks_found = list(set(f.network_type.value for f in relevant))
        
        return {
            "query": query,
            "relevant_count": len(relevant),
            "networks_found": networks_found,
            "key_themes": themes,
            "insights": insights,
            "avg_confidence": sum(f.confidence for f in relevant) / len(relevant),
            "time_span_days": self._calculate_time_span(relevant),
        }
    
    def _extract_themes(self, facts: List[FourNetworkFact]) -> List[str]:
        """提取主题"""
        all_tags = []
        for f in facts:
            all_tags.extend(f.tags)
        
        if not all_tags:
            return []
        
        # 标签频率统计
        from collections import Counter
        tag_counts = Counter(all_tags)
        
        return [tag for tag, _ in tag_counts.most_common(5)]
    
    def _generate_insights(self, facts: List[FourNetworkFact]) -> List[str]:
        """生成洞察"""
        if not facts:
            return ["无足够信息生成洞察"]
        
        insights = []
        
        # 1. 跨网络洞察
        networks = set(f.network_type for f in facts)
        if len(networks) > 1:
            insights.append(f"跨{len(networks)}个网络发现关联")
        
        # 2. 置信度分析
        avg_confidence = sum(f.confidence for f in facts) / len(facts)
        if avg_confidence > 0.7:
            insights.append(f"高置信度记忆群 ({avg_confidence:.0%})")
        elif avg_confidence < 0.4:
            insights.append(f"低置信度记忆群,建议核实 ({avg_confidence:.0%})")
        
        # 3. 时间分析
        if len(facts) > 1:
            time_span = (max(f.created_at for f in facts) - 
                        min(f.created_at for f in facts)).days
            if time_span > 0:
                insights.append(f"时间跨度: {time_span}天")
        
        # 4. 来源分析
        sources = set(f.source for f in facts if f.source)
        if sources:
            insights.append(f"来源: {', '.join(list(sources)[:3])}")
        
        return insights
    
    def _calculate_time_span(self, facts: List[FourNetworkFact]) -> int:
        """计算时间跨度"""
        if len(facts) < 2:
            return 0
        
        dates = [f.created_at for f in facts]
        return (max(dates) - min(dates)).days
    
    # === 额外方法 ===
    
    def consolidate(self, network: MemoryNetwork = None) -> Dict[str, Any]:
        """记忆整合 - 合并相似记忆
        
        Args:
            network: 指定网络 (None表示所有)
            
        Returns:
            Dict: 整合统计
        """
        networks = [network] if network else list(MemoryNetwork)
        
        consolidated_count = 0
        removed_ids = []
        
        for net in networks:
            if net == MemoryNetwork.WORLD:
                facts = self.world_facts
            elif net == MemoryNetwork.EXPERIENCES:
                facts = self.experiences
            elif net == MemoryNetwork.SUMMARIES:
                facts = self.summaries
            elif net == MemoryNetwork.BELIEFS:
                facts = self.beliefs
            else:
                continue
            
            # 简化: 移除过期的低置信度记忆
            threshold = datetime.now(timezone.utc).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            
            for fact_id, fact in list(facts.items()):
                if (fact.valid_until and fact.valid_until < datetime.now(timezone.utc)):
                    if fact.confidence < 0.3:
                        removed_ids.append(fact_id)
                        del facts[fact_id]
                        consolidated_count += 1
        
        return {
            "consolidated_count": consolidated_count,
            "removed_ids": removed_ids,
        }
    
    def prune(self, network: MemoryNetwork, count: int = 100) -> int:
        """记忆修剪 - 移除低价值记忆
        
        Args:
            network: 目标网络
            count: 修剪数量
            
        Returns:
            int: 实际修剪数量
        """
        if network == MemoryNetwork.WORLD:
            facts = self.world_facts
        elif network == MemoryNetwork.EXPERIENCES:
            facts = self.experiences
        elif network == MemoryNetwork.SUMMARIES:
            facts = self.summaries
        elif network == MemoryNetwork.BELIEFS:
            facts = self.beliefs
        else:
            return 0
        
        if len(facts) < self.max_per_network * 0.8:
            return 0
        
        # 按置信度和时间排序, 移除最低的
        sorted_facts = sorted(
            facts.items(),
            key=lambda x: (x[1].confidence, x[1].created_at)
        )
        
        removed = 0
        for fact_id, _ in sorted_facts[:count]:
            del facts[fact_id]
            removed += 1
        
        return removed
    
    def get_network_stats(self) -> Dict[str, int]:
        """获取网络统计"""
        return {
            "world": len(self.world_facts),
            "experiences": len(self.experiences),
            "summaries": len(self.summaries),
            "beliefs": len(self.beliefs),
            "total": sum([
                len(self.world_facts),
                len(self.experiences),
                len(self.summaries),
                len(self.beliefs),
            ]),
            "indexed_words": len(self._content_index),
            "indexed_tags": len(self._tag_index),
        }
    
    def get_temporal_context(self, hours: int = 24) -> Dict[str, Any]:
        """获取时间上下文 - 特定时间段内的记忆
        
        Args:
            hours: 回溯小时数
            
        Returns:
            Dict: 时间上下文
        """
        import math
        cutoff = datetime.now(timezone.utc).timestamp() - (hours * 3600)
        
        all_facts = (
            list(self.world_facts.values()) +
            list(self.experiences.values()) +
            list(self.summaries.values()) +
            list(self.beliefs.values())
        )
        
        recent = [f for f in all_facts if f.created_at.timestamp() > cutoff]
        
        return {
            "hours": hours,
            "recent_count": len(recent),
            "by_network": {
                "world": len([f for f in recent if f.network_type == MemoryNetwork.WORLD]),
                "experiences": len([f for f in recent if f.network_type == MemoryNetwork.EXPERIENCES]),
                "summaries": len([f for f in recent if f.network_type == MemoryNetwork.SUMMARIES]),
                "beliefs": len([f for f in recent if f.network_type == MemoryNetwork.BELIEFS]),
            },
            "avg_confidence": sum(f.confidence for f in recent) / len(recent) if recent else 0,
        }


# ===== Bank分层架构 - 来自Y系统 =====
class BankLayer(Enum):
    """Bank分层 - 来自X系统#8"""
    WORKING = "working"       # 工作记忆 (短时)
    EPISODIC = "episodic"     # 情节记忆
    SEMANTIC = "semantic"     # 语义记忆
    ARCHIVE = "archive"       # 档案记忆


@dataclass
class Bank:
    """分层记忆银行 - 来自Y系统核心机制
    
    4层自动迁移:
    - Working: 当前活跃
    - Episodic: 重要经历
    - Semantic: 抽象知识
    - Archive: 长期存储
    """
    
    bank_id: str = "default"
    working: Dict[str, UnifiedEntry] = field(default_factory=dict)
    episodic: Dict[str, UnifiedEntry] = field(default_factory=dict)
    semantic: Dict[str, UnifiedEntry] = field(default_factory=dict)
    archive: Dict[str, UnifiedEntry] = field(default_factory=dict)
    
    # 迁移阈值
    working_to_episodic_threshold: int = 10  # 访问次数
    episodic_to_semantic_days: int = 30      # 天数
    semantic_to_archive_days: int = 90       # 天数
    
    def add(self, entry: UnifiedEntry, layer: BankLayer = BankLayer.WORKING):
        """添加到指定层"""
        if layer == BankLayer.WORKING:
            self.working[entry.id] = entry
        elif layer == BankLayer.EPISODIC:
            self.episodic[entry.id] = entry
        elif layer == BankLayer.SEMANTIC:
            self.semantic[entry.id] = entry
        elif layer == BankLayer.ARCHIVE:
            self.archive[entry.id] = entry
    
    def store(self, entry: UnifiedEntry) -> bool:
        """存储条目到工作层 (store是add的别名)
        
        Args:
            entry: 统一条目
            
        Returns:
            bool: 是否成功
        """
        self.add(entry, BankLayer.WORKING)
        return True
    
    def migrate(self) -> int:
        """执行自动迁移, 返回迁移数量"""
        migrated = 0
        now = datetime.now(timezone.utc)
        
        # Working → Episodic
        for entry_id, entry in list(self.working.items()):
            if entry.access_count >= self.working_to_episodic_threshold:
                self.episodic[entry_id] = entry
                del self.working[entry_id]
                migrated += 1
        
        # Episodic → Semantic
        for entry_id, entry in list(self.episodic.items()):
            days = (now - entry.updated_at).days
            if days >= self.episodic_to_semantic_days:
                self.semantic[entry_id] = entry
                del self.episodic[entry_id]
                migrated += 1
        
        # Semantic → Archive
        for entry_id, entry in list(self.semantic.items()):
            days = (now - entry.updated_at).days
            if days >= self.semantic_to_archive_days:
                self.archive[entry_id] = entry
                del self.semantic[entry_id]
                migrated += 1
        
        return migrated
    
    def get_all_count(self) -> int:
        """获取总数量"""
        return len(self.working) + len(self.episodic) + len(self.semantic) + len(self.archive)
    
    def get_layer_stats(self) -> Dict[str, int]:
        """获取各层统计"""
        return {
            "working": len(self.working),
            "episodic": len(self.episodic),
            "semantic": len(self.semantic),
            "archive": len(self.archive),
        }


# ===== Veracity贝叶斯置信度 - 来自X/Y系统 =====
@dataclass
class Veracity:
    """贝叶斯置信度 - 来自X系���#9
    
    多源置信度合并
    """
    
    sources: Dict[str, float] = field(default_factory=dict)  # source -> confidence
    combined_confidence: float = 0.5
    update_count: int = 0
    
    def add_source(self, source: str, confidence: float):
        """添加来源"""
        self.sources[source] = confidence
        self.update_count += 1
        self._recalculate()
    
    def _recalculate(self):
        """贝叶斯合并"""
        if not self.sources:
            self.combined_confidence = 0.5
            return
        
        # 简化的贝叶斯更新
        product = 1.0
        for conf in self.sources.values():
            product *= conf
        
        # 使用几何平均
        n = len(self.sources)
        self.combined_confidence = product ** (1.0 / n) if n > 0 else 0.5


# ===== 统一内存存储 =====
class MemoryStore:
    """统一内存存储 - 整合XYZ的记忆系统
    
    整合:
    - X: 15维UnifiedEntry
    - Y: Bank分层
    - Z: GraphMemory + FourNetwork
    """
    
    def __init__(self):
        self.entries: Dict[str, UnifiedEntry] = {}
        self.bank = Bank(bank_id="default")
        self.four_network = FourNetworkMemory()
        self.veracity = Veracity()
    
    def add(self, entry: UnifiedEntry) -> str:
        """添加记忆"""
        self.entries[entry.id] = entry
        self.bank.add(entry)
        return entry.id
    
    def get(self, entry_id: str) -> Optional[UnifiedEntry]:
        """获取记忆"""
        entry = self.entries.get(entry_id)
        if entry:
            entry.access()
        return entry
    
    def search(self, query: str, limit: int = 10) -> List[UnifiedEntry]:
        """搜索"""
        results = []
        query_lower = query.lower()
        
        for entry in self.entries.values():
            if query_lower in entry.content.lower():
                results.append(entry)
        
        # 按重要性排序
        results.sort(key=lambda e: -e.importance)
        return results[:limit]
    
    def get_stats(self) -> dict:
        """获取统计"""
        return {
            "total_entries": len(self.entries),
            "bank_layers": self.bank.get_layer_stats(),
            "four_network": self.four_network.get_network_stats(),
            "veracity_sources": len(self.veracity.sources),
        }


# ===== 工厂函数 =====
def create_unified_entry(content: str, category: EntryCategory = EntryCategory.FACT,
                         importance: float = 0.5, **kwargs) -> UnifiedEntry:
    """创建15维统一记忆条目"""
    return UnifiedEntry(
        content=content,
        category=category,
        importance=importance,
        **kwargs
    )


def create_four_network_memory(bank_id: str = "default") -> FourNetworkMemory:
    """创建四网络记忆"""
    return FourNetworkMemory(bank_id=bank_id)


def create_bank(bank_id: str = "default") -> Bank:
    """创建Bank"""
    return Bank(bank_id=bank_id)


def create_memory_store() -> MemoryStore:
    """创建统一内存存储"""
    return MemoryStore()


# ===== 来自XYZ系统 =====
class GraphMemory:
    """图结构记忆 - 四层节点架构
    
    基于MRAgent的图记忆设计：
    - KeyNode: 关键词节点
    - Topic: 主题节点  
    - PersonalEvent: 个人事件
    - EpisodeEvent: 对话事件
    
    边关系：
    - Key → Topic (通过tag连接)
    - Topic → EpisodeEvent (事件聚类)
    - Personal → EpisodeEvent (人-事件关系)
    """
    
    def __init__(self):
        # 四层节点
        self.key_nodes: Dict[str, KeyNode] = {}
        self.topics: Dict[str, Topic] = {}
        self.personal_events: Dict[str, PersonalEvent] = {}
        self.episode_events: Dict[str, EpisodeEvent] = {}
        
        # 人-事件索引
        self.person_events: Dict[str, List[str]] = defaultdict(list)
        
        # 时间索引
        self.temporal_index: Dict[str, List[str]] = defaultdict(list)
    
    def add_episode(self, text: str, metadata: dict = None) -> str:
        """添加对话事件"""
        event_id = f"E{len(self.episode_events)}"
        episode = EpisodeEvent(
            event_id=event_id,
            text=text,
            metadata=metadata or {}
        )
        self.episode_events[event_id] = episode
        
        # 时间索引
        conversation_id = metadata.get("conversation_id", "default") if metadata else "default"
        self.temporal_index[conversation_id].append(event_id)
        
        return event_id
    
    def add_key_node(self, key: str, text: str = "") -> KeyNode:
        """添加关键词节点"""
        if key not in self.key_nodes:
            self.key_nodes[key] = KeyNode(key_id=key, text=text or key)
        return self.key_nodes[key]
    
    def link_key_to_episode(self, key: str, event_id: str, tag: str) -> None:
        """建立Key → Episode的边"""
        key_node = self.add_key_node(key)
        key_node.add_tag(tag, event_id)
    
    def add_topic(self, topic_id: str, text: str) -> Topic:
        """添加主题节点"""
        if topic_id not in self.topics:
            self.topics[topic_id] = Topic(topic_id=topic_id, text=text)
        return self.topics[topic_id]
    
    def add_personal_event(self, person: str, text: str, 
                          tag: str, origin: str) -> str:
        """添加个人事件"""
        event_id = f"P{len(self.personal_events)}"
        event = PersonalEvent(
            person=person,
            personal_id=event_id,
            text=text,
            tag=tag,
            origin=origin
        )
        self.personal_events[event_id] = event
        self.person_events[person].append(event_id)
        return event_id
    
    def traverse_by_tag(self, key: str, tag: str) -> List[str]:
        """按tag遍历图 - 获取相关事件"""
        key_node = self.key_nodes.get(key)
        if not key_node:
            return []
        return key_node.get_events_by_tag(tag)
    
    def traverse_by_person(self, person: str) -> List[PersonalEvent]:
        """按人名遍历 - 获取个人事件"""
        event_ids = self.person_events.get(person, [])
        return [self.personal_events[eid] for eid in event_ids if eid in self.personal_events]
    
    def traverse_temporal(self, conversation_id: str) -> List[EpisodeEvent]:
        """时间遍历 - 获取对话中的所有事件"""
        event_ids = self.temporal_index.get(conversation_id, [])
        return [self.episode_events[eid] for eid in event_ids if eid in self.episode_events]
    
    def search_by_embedding(self, query_emb: List[float], 
                           k: int = 5) -> List[tuple[str, float]]:
        """Embedding相似度搜索"""
        if not query_emb:
            return []
        
        # 计算余弦相似度
        def cosine_sim(a, b):
            dot = sum(x*y for x,y in zip(a,b))
            norm_a = sum(x*x for x in a) ** 0.5
            norm_b = sum(x*x for x in b) ** 0.5
            return dot / (norm_a * norm_b + 1e-8)
        
        scores = []
        for eid, event in self.episode_events.items():
            if event.embedding:
                sim = cosine_sim(query_emb, event.embedding)
                scores.append((eid, sim))
        
        # 返回top-k
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:k]
    
    def get_statistics(self) -> dict:
        """获取记忆统计"""
        return {
            "key_nodes": len(self.key_nodes),
            "topics": len(self.topics),
            "personal_events": len(self.personal_events),
            "episode_events": len(self.episode_events),
            "conversations": len(self.temporal_index)
        }
    
    def to_dict(self) -> dict:
        """序列化"""
        return {
            "key_nodes": {k: {"key_id": v.key_id, "text": v.text, "tags": v.tag_list} 
                         for k, v in self.key_nodes.items()},
            "topics": {k: {"topic_id": v.topic_id, "text": v.text} 
                      for k, v in self.topics.items()},
            "episode_events": {k: v.to_dict() 
                              for k, v in self.episode_events.items()},
            "personal_events": {k: {"person": v.person, "text": v.text, "tag": v.tag}
                               for k, v in self.personal_events.items()}
        }
    
    def save(self, path: str) -> None:
        """保存到文件"""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load(cls, path: str) -> 'GraphMemory':
        """从文件加载"""
        with open(path) as f:
            data = json.load(f)
        
        graph = cls()
        
        # 恢复节点
        for k, v in data.get("key_nodes", {}).items():
            graph.key_nodes[k] = KeyNode(k, v.get("text", ""), v.get("tags", []))
        
        for k, v in data.get("topics", {}).items():
            graph.topics[k] = Topic(k, v.get("text", ""))
        
        for k, v in data.get("episode_events", {}).items():
            graph.episode_events[k] = EpisodeEvent(
                event_id=v["event_id"],
                text=v["text"],
                timestamp=v.get("timestamp", 0),
                embedding=v.get("embedding"),
                metadata=v.get("metadata", {})
            )
        
        for k, v in data.get("personal_events", {}).items():
            pe = PersonalEvent(
                person=v["person"],
                personal_id=k,
                text=v["text"],
                tag=v.get("tag", ""),
                origin=v.get("origin", "")
            )
            graph.personal_events[k] = pe
            graph.person_events[v["person"]].append(k)
        
        return graph


# ===== 来自XYZ系统 =====
class HallwayTransferResult:
    """Result of a hallway transfer operation."""

    def __init__(self):
        self.nodes_transferred: int = 0
        self.nodes_skipped: int = 0
        self.nodes_merged: int = 0
        self.edges_transferred: int = 0
        self.conflicts: list[dict] = []

    def to_dict(self) -> dict:
        return {
            "nodes_transferred": self.nodes_transferred,
            "nodes_skipped": self.nodes_skipped,
            "nodes_merged": self.nodes_merged,
            "edges_transferred": self.edges_transferred,
            "conflicts": self.conflicts,
        }


# ===== 来自XYZ系统(依赖) =====
class MinervaStore:
    """M1+M2: Three-engine storage with bi-temporal versioning.

    Engines:
    1. SQLite relational — structured queries, MVCC branches
    2. FTS5 full-text — content search (manually synced, no triggers)
    3. sqlite-vec — vector similarity search (deferred)

    Iron Law 1 enforcement: insert() requires a valid _gate_token.
    All writes MUST go through Z._gated_insert() or Z._system_insert().
    Direct store.insert() without a token raises IronLawViolation.
    """

    class IronLawViolation(Exception):
        """Raised when a write bypasses the required gate checks."""

    def __init__(self, config: ZConfig | None = None):
            self._config = config or ZConfig()
            self._db_path = self._config.db_path
            self._embedding_dim = self._config.embedding_dim
            self._conn = sqlite3.connect(self._db_path)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")
            self._gate_token: str | None = None
            self._audit_log: list[dict] = []
            # Query cache (FTS results)
            self._query_cache: dict[str, tuple[list, float]] = {}
            self._cache_max_size = 100
            # Node cache for get()
            self._node_cache: dict[str, tuple[Node, float]] = {}
            self._node_cache_max_size = 500
            self._init_schema()

    def _init_schema(self) -> None:
        """Create all tables, indexes, FTS. No triggers — manual FTS sync."""
        c = self._conn.cursor()

        # ── Nodes table ──
        # NOTE: id is NOT PRIMARY KEY (that makes it WITHOUT ROWID, breaking FTS5 triggers).
        # Instead, _rowid is the implicit INTEGER PRIMARY KEY (auto rowid).
        # UNIQUE constraint on (id, branch, tx_to) replaces the old PK.
        c.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                id TEXT NOT NULL DEFAULT '',
                type INTEGER NOT NULL DEFAULT 0,
                content TEXT NOT NULL DEFAULT '',
                embedding BLOB,
                valid_from REAL NOT NULL DEFAULT 0,
                valid_to REAL NOT NULL DEFAULT 0,
                tx_from REAL NOT NULL DEFAULT 0,
                tx_to REAL NOT NULL DEFAULT 0,
                layer INTEGER NOT NULL DEFAULT 0,
                trust INTEGER NOT NULL DEFAULT 0,
                reinforce_count INTEGER NOT NULL DEFAULT 0,
                utility REAL NOT NULL DEFAULT 0,
                surprise REAL NOT NULL DEFAULT 0,
                source INTEGER NOT NULL DEFAULT 0,
                creator_agent TEXT NOT NULL DEFAULT '',
                session_id TEXT NOT NULL DEFAULT '',
                parent_id TEXT NOT NULL DEFAULT '',
                confidence REAL NOT NULL DEFAULT 0,
                raw_proof TEXT NOT NULL DEFAULT '',
                branch TEXT NOT NULL DEFAULT 'main',
                created_at REAL NOT NULL DEFAULT 0,
                updated_at REAL NOT NULL DEFAULT 0,
                accessed_at REAL NOT NULL DEFAULT 0,
                access_count INTEGER NOT NULL DEFAULT 0,
                is_consolidated INTEGER NOT NULL DEFAULT 0,
                custom_type TEXT NOT NULL DEFAULT '',
                UNIQUE(id, branch, tx_to)
            )
        """)

        # ── Edges table ──
        c.execute("""
            CREATE TABLE IF NOT EXISTS edges (
                id TEXT NOT NULL DEFAULT '',
                source TEXT NOT NULL DEFAULT '',
                target TEXT NOT NULL DEFAULT '',
                type INTEGER NOT NULL DEFAULT 0,
                weight REAL NOT NULL DEFAULT 1.0,
                metadata TEXT NOT NULL DEFAULT '{}',
                valid_from REAL NOT NULL DEFAULT 0,
                valid_to REAL NOT NULL DEFAULT 0,
                tx_from REAL NOT NULL DEFAULT 0,
                tx_to REAL NOT NULL DEFAULT 0,
                branch TEXT NOT NULL DEFAULT 'main',
                UNIQUE(id, branch, tx_to)
            )
        """)

        # ── FTS5 full-text index — NO triggers, manual sync ──
        c.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS nodes_fts
            USING fts5(content)
        """)

        # ── Indexes ──
        c.execute("CREATE INDEX IF NOT EXISTS idx_nodes_id ON nodes(id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(type)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_nodes_layer ON nodes(layer)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_nodes_trust ON nodes(trust)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_nodes_branch ON nodes(branch)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_nodes_utility ON nodes(utility)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_nodes_active ON nodes(id, branch, tx_to)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_edges_type ON edges(type)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_edges_branch ON edges(branch)")

        # ── Branches table (D2: MVCC branch support) ──
        c.execute("""
            CREATE TABLE IF NOT EXISTS branches (
                name TEXT PRIMARY KEY,
                parent TEXT NOT NULL DEFAULT 'main',
                created_at REAL NOT NULL DEFAULT 0,
                is_active INTEGER NOT NULL DEFAULT 1
            )
        """)

        # ── Evolution experiments table (M16: EvolveMem) ──
        c.execute("""
            CREATE TABLE IF NOT EXISTS evolution_experiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL DEFAULT 0,
                hypothesis TEXT NOT NULL DEFAULT '',
                config_change TEXT NOT NULL DEFAULT '',
                result TEXT NOT NULL DEFAULT '',
                accepted INTEGER NOT NULL DEFAULT 0,
                fitness_before REAL NOT NULL DEFAULT 0,
                fitness_after REAL NOT NULL DEFAULT 0
            )
        """)

        # ── FTS-to-node mapping table (tracks which FTS rowid maps to which node) ──
        c.execute("""
            CREATE TABLE IF NOT EXISTS fts_map (
                fts_rowid INTEGER PRIMARY KEY,
                node_id TEXT NOT NULL,
                branch TEXT NOT NULL DEFAULT 'main'
            )
        """)
        c.execute("CREATE INDEX IF NOT EXISTS idx_fts_map_node ON fts_map(node_id, branch)")

        self._conn.commit()

        # ── sqlite-vec setup (deferred) ──
        self._vec_available = False

    # ═══════════════════════════════════════════
    #  Core CRUD
    # ═══════════════════════════════════════════

    def _set_gate_token(self, token: str) -> None:
        """Set the gate token for the next insert() call. Called by Z._gated_insert()."""
        self._gate_token = token

    def _system_insert(self, node: Node, reason: str = "") -> str:
        """System-level insert that bypasses WriteGate but logs an audit trail.

        Used by: consolidation, dream_cycle, hallway, branch operations.
        These are system-generated nodes derived from already-verified nodes.
        Every bypass is recorded in _audit_log for constitutional compliance review.
        """
        import uuid as _uuid
        token = f"sys_{_uuid.uuid4().hex[:12]}"
        self._audit_log.append({
            "token": token,
            "node_id": node.id,
            "reason": reason,
            "timestamp": time.time(),
        })
        self._gate_token = token
        try:
            return self.insert(node)
        finally:
            self._gate_token = None

    def insert(self, node: Node) -> str:
        """Insert a node. Returns node.id. P-26: all columns synced.

        Iron Law 1: insert() requires a valid _gate_token set by
        _set_gate_token() or _system_insert(). Direct calls without
        a token raise IronLawViolation.
        """
        if self._gate_token is None:
            raise MinervaStore.IronLawViolation(
                "Direct store.insert() without gate token. "
                "Use Z._gated_insert() or store._system_insert(). "
                "Iron Law 1: All writes must pass through the gate."
            )
        token = self._gate_token
        self._gate_token = None  # One-time use
        now = time.time()
        node.created_at = now
        node.updated_at = now
        node.accessed_at = now
        if node.tx_from == 0:
            node.tx_from = now
        if node.valid_from == 0:
            node.valid_from = now

        emb_blob = json.dumps(node.embedding) if node.embedding else None

        # Check if node already exists (by id + branch + tx_to=0)
        existing = self._conn.execute(
            "SELECT rowid FROM nodes WHERE id=? AND branch=? AND tx_to=0",
            (node.id, node.branch),
        ).fetchone()

        if existing:
            # Update existing active node + sync FTS
            old_rowid = existing["rowid"]
            self._conn.execute("""
                UPDATE nodes SET
                    type=?, content=?, embedding=?,
                    valid_from=?, valid_to=?, tx_from=?, tx_to=?,
                    layer=?, trust=?, reinforce_count=?, utility=?, surprise=?,
                    source=?, creator_agent=?, session_id=?, parent_id=?,
                    confidence=?, raw_proof=?,
                    created_at=?, updated_at=?, accessed_at=?, access_count=?,
                    is_consolidated=?, custom_type=?
                WHERE rowid=?
            """, (
                node.type, node.content, emb_blob,
                node.valid_from, node.valid_to, node.tx_from, node.tx_to,
                node.layer, node.trust, node.reinforce_count, node.utility, node.surprise,
                node.source, node.creator_agent, node.session_id, node.parent_id,
                node.confidence, node.raw_proof,
                node.created_at, node.updated_at, node.accessed_at, node.access_count,
                int(node.is_consolidated), node.custom_type,
                old_rowid,
            ))
            # Sync FTS: delete old, insert new
            self._conn.execute("DELETE FROM nodes_fts WHERE rowid=?", (old_rowid,))
            self._conn.execute("INSERT INTO nodes_fts(rowid, content) VALUES (?, ?)",
                               (old_rowid, node.content))
        else:
            # Insert new node
            cursor = self._conn.execute("""
                INSERT INTO nodes (
                    id, type, content, embedding,
                    valid_from, valid_to, tx_from, tx_to,
                    layer, trust, reinforce_count, utility, surprise,
                    source, creator_agent, session_id, parent_id,
                    confidence, raw_proof, branch,
                    created_at, updated_at, accessed_at, access_count,
                    is_consolidated, custom_type
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                node.id, node.type, node.content, emb_blob,
                node.valid_from, node.valid_to, node.tx_from, node.tx_to,
                node.layer, node.trust, node.reinforce_count, node.utility, node.surprise,
                node.source, node.creator_agent, node.session_id, node.parent_id,
                node.confidence, node.raw_proof, node.branch,
                node.created_at, node.updated_at, node.accessed_at, node.access_count,
                int(node.is_consolidated), node.custom_type,
            ))
            new_rowid = cursor.lastrowid
            # Sync FTS
            self._conn.execute("INSERT INTO nodes_fts(rowid, content) VALUES (?, ?)",
                               (new_rowid, node.content))
            # Track mapping
            self._conn.execute(
                "INSERT OR REPLACE INTO fts_map(fts_rowid, node_id, branch) VALUES (?,?,?)",
                (new_rowid, node.id, node.branch),
            )

        self._conn.commit()
        return node.id

    def get(self, node_id: str, branch: str = "main") -> Node | None:
        """Retrieve a node by ID. Returns None if not found.
        
        Uses node cache for faster repeated access.
        """
        import time as _time
        cache_key = f"{node_id}:{branch}"
        
        # Check cache
        if cache_key in self._node_cache:
            node, cached_at = self._node_cache[cache_key]
            # Cache valid for 60 seconds
            if _time.time() - cached_at < 60:
                return node
        
        # Query from DB
        row = self._conn.execute(
            "SELECT * FROM nodes WHERE id=? AND branch=? AND tx_to=0",
            (node_id, branch),
        ).fetchone()
        if row is None:
            return None
        
        node = self._row_to_node(row)
        
        # Add to cache (with LRU eviction)
        if len(self._node_cache) >= self._node_cache_max_size:
            # Remove oldest entry
            oldest_key = next(iter(self._node_cache))
            del self._node_cache[oldest_key]
        
        self._node_cache[cache_key] = (node, _time.time())
        
        return node

    def _system_update(self, node: Node, reason: str = "") -> bool:
        """System-level update that bypasses ModifyGate but logs audit trail."""
        import uuid as _uuid
        token = f"sys_upd_{_uuid.uuid4().hex[:12]}"
        self._audit_log.append({
            "token": token,
            "node_id": node.id,
            "reason": reason,
            "operation": "update",
            "timestamp": time.time(),
        })
        self._gate_token = token
        try:
            return self.update(node)
        finally:
            self._gate_token = None

    def update(self, node: Node) -> bool:
        """Update an existing node. Returns True if updated.

        Iron Law 1: update() requires a valid _gate_token.
        """
        if self._gate_token is None:
            raise MinervaStore.IronLawViolation(
                "Direct store.update() without gate token. "
                "Use Z._gated_update() or store._system_update(). "
                "Iron Law 1: All modifications must pass through the gate."
            )
        self._gate_token = None  # One-time use
        node.updated_at = time.time()
        emb_blob = json.dumps(node.embedding) if node.embedding else None

        # Find the row to update
        existing = self._conn.execute(
            "SELECT rowid FROM nodes WHERE id=? AND branch=? AND tx_to=0",
            (node.id, node.branch),
        ).fetchone()
        if existing is None:
            return False

        rowid = existing["rowid"]

        cursor = self._conn.execute("""
            UPDATE nodes SET
                type=?, content=?, embedding=?,
                valid_from=?, valid_to=?, tx_from=?, tx_to=?,
                layer=?, trust=?, reinforce_count=?, utility=?, surprise=?,
                source=?, creator_agent=?, session_id=?, parent_id=?,
                confidence=?, raw_proof=?, branch=?,
                updated_at=?, accessed_at=?, access_count=?,
                is_consolidated=?, custom_type=?
            WHERE rowid=?
        """, (
            node.type, node.content, emb_blob,
            node.valid_from, node.valid_to, node.tx_from, node.tx_to,
            node.layer, node.trust, node.reinforce_count, node.utility, node.surprise,
            node.source, node.creator_agent, node.session_id, node.parent_id,
            node.confidence, node.raw_proof, node.branch,
            node.updated_at, node.accessed_at, node.access_count,
            int(node.is_consolidated), node.custom_type,
            rowid,
        ))

        # Sync FTS: delete old, insert new
        self._conn.execute("DELETE FROM nodes_fts WHERE rowid=?", (rowid,))
        self._conn.execute("INSERT INTO nodes_fts(rowid, content) VALUES (?, ?)",
                           (rowid, node.content))

        self._conn.commit()
        return cursor.rowcount > 0

    def delete(self, node_id: str, branch: str = "main") -> bool:
        """Soft-delete: set tx_to to now. Returns True if deleted.

        Also removes from FTS5 index.
        """
        now = time.time()

        # Find the row
        existing = self._conn.execute(
            "SELECT rowid FROM nodes WHERE id=? AND branch=? AND tx_to=0",
            (node_id, branch),
        ).fetchone()
        if existing is None:
            return False

        rowid = existing["rowid"]

        # Remove from FTS
        self._conn.execute("DELETE FROM nodes_fts WHERE rowid=?", (rowid,))

        # Remove from fts_map
        self._conn.execute("DELETE FROM fts_map WHERE fts_rowid=?", (rowid,))

        # Soft-delete the node
        cursor = self._conn.execute(
            "UPDATE nodes SET tx_to=? WHERE rowid=?",
            (now, rowid),
        )
        self._conn.commit()
        return cursor.rowcount > 0

    # ═══════════════════════════════════════════
    #  Edge operations
    # ═══════════════════════════════════════════

    def insert_edge(self, edge: Edge) -> str:
        """Insert an edge. Returns edge.id."""
        now = time.time()
        if edge.tx_from == 0:
            edge.tx_from = now
        if edge.valid_from == 0:
            edge.valid_from = now

        self._conn.execute("""
            INSERT OR REPLACE INTO edges (
                id, source, target, type, weight, metadata,
                valid_from, valid_to, tx_from, tx_to, branch
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            edge.id, edge.source, edge.target, edge.type, edge.weight,
            json.dumps(edge.metadata),
            edge.valid_from, edge.valid_to, edge.tx_from, edge.tx_to, edge.branch,
        ))
        self._conn.commit()
        return edge.id

    def get_neighbors(self, node_id: str, edge_type: EdgeType | None = None,
                      branch: str = "main") -> list[tuple[Edge, Node]]:
        """Get neighboring nodes via edges. Returns (edge, neighbor_node) pairs."""
        if edge_type is not None:
            edge_rows = self._conn.execute("""
                SELECT * FROM edges
                WHERE (source=? OR target=?) AND type=? AND branch=? AND tx_to=0
            """, (node_id, node_id, edge_type, branch)).fetchall()
        else:
            edge_rows = self._conn.execute("""
                SELECT * FROM edges
                WHERE (source=? OR target=?) AND branch=? AND tx_to=0
            """, (node_id, node_id, branch)).fetchall()

        results = []
        for erow in edge_rows:
            edge = Edge(
                id=erow["id"], source=erow["source"], target=erow["target"],
                type=EdgeType(erow["type"]), weight=erow["weight"],
                metadata=json.loads(erow["metadata"]),
                valid_from=erow["valid_from"], valid_to=erow["valid_to"],
                tx_from=erow["tx_from"], tx_to=erow["tx_to"],
                branch=erow["branch"],
            )
            # Determine neighbor ID
            neighbor_id = erow["target"] if erow["source"] == node_id else erow["source"]
            neighbor = self.get(neighbor_id, branch)
            if neighbor is not None:
                results.append((edge, neighbor))
        return results

    def get_all_edges(self, branch: str = "main",
                      limit: int = 10000) -> list[Edge]:
        """Get all edges in a branch (for hallway transfer etc)."""
        rows = self._conn.execute("""
            SELECT * FROM edges WHERE branch=? AND tx_to=0 LIMIT ?
        """, (branch, limit)).fetchall()

        edges = []
        for erow in rows:
            edges.append(Edge(
                id=erow["id"], source=erow["source"], target=erow["target"],
                type=EdgeType(erow["type"]), weight=erow["weight"],
                metadata=json.loads(erow["metadata"]),
                valid_from=erow["valid_from"], valid_to=erow["valid_to"],
                tx_from=erow["tx_from"], tx_to=erow["tx_to"],
                branch=erow["branch"],
            ))
        return edges

    # ═══════════════════════════════════════════
    #  FTS5 search
    # ═══════════════════════════════════════════

    def search_fts(self, query: str, limit: int = 20,
                   branch: str = "main") -> list[tuple[Node, float]]:
        """Full-text search via FTS5. Returns (node, rank) pairs.

        Search FTS5 → get rowids → look up node IDs via fts_map → get nodes.
        """
        # Search FTS5
        fts_rows = self._conn.execute("""
            SELECT rowid, rank FROM nodes_fts
            WHERE nodes_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (query, limit * 3)).fetchall()

        results = []
        for fts_row in fts_rows:
            # Look up node_id from fts_map
            map_row = self._conn.execute(
                "SELECT node_id, branch FROM fts_map WHERE fts_rowid=?",
                (fts_row["rowid"],),
            ).fetchone()

            if map_row is None:
                continue

            # Filter by branch
            if map_row["branch"] != branch:
                continue

            # Get the node
            node = self.get(map_row["node_id"], branch)
            if node is not None:
                # FTS5 rank is negative (lower = better), negate for score
                results.append((node, -fts_row["rank"]))

            if len(results) >= limit:
                break

        return results

    # ═══════════════════════════════════════════
    #  Branch operations (D2: MVCC)
    # ═══════════════════════════════════════════

    def branch_create(self, name: str, parent: str = "main") -> bool:
        """Create a memory branch for parallel exploration.

        Uses _system_insert for Iron Law 1 compliance (branch copy is
        a system operation — nodes are derived from already-verified originals).
        """
        now = time.time()
        # Copy all active nodes from parent to new branch with new IDs
        parent_nodes = self._conn.execute(
            "SELECT * FROM nodes WHERE branch=? AND tx_to=0",
            (parent,),
        ).fetchall()

        for row in parent_nodes:
            node = self._row_to_node(row)
            if node is None:
                continue
            # Create a new node for the branch with suffixed ID
            new_id = f"{node.id}_{name}"
            node.id = new_id
            node.branch = name
            node.tx_from = now
            node.valid_from = now
            # Use _system_insert for gate compliance
            self._system_insert(node, reason=f"branch_create:{name}")

        # Register branch
        self._conn.execute(
            "INSERT OR IGNORE INTO branches (name, parent, created_at) VALUES (?,?,?)",
            (name, parent, now),
        )
        self._conn.commit()
        return True

    def branch_merge(self, source: str, target: str = "main") -> int:
        """Merge a branch back. Returns count of nodes merged."""
        # Get all active nodes in source branch
        rows = self._conn.execute(
            "SELECT * FROM nodes WHERE branch=? AND tx_to=0",
            (source,),
        ).fetchall()

        merged = 0
        for row in rows:
            node = self._row_to_node(row)
            if node is None:
                continue

            # Remove the branch suffix from the ID to get the original ID
            original_id = node.id
            if original_id.endswith(f"_{source}"):
                original_id = original_id[: -len(f"_{source}")]

            # Check if this node already exists in target
            existing = self.get(original_id, target)
            if existing is not None:
                # Node exists in target — update if source is newer
                if node.updated_at > existing.updated_at:
                    existing.content = node.content
                    existing.utility = node.utility
                    existing.trust = node.trust
                    existing.layer = node.layer
                    existing.reinforce_count = node.reinforce_count
                    self._system_update(existing, reason="branch_merge")
                    merged += 1
            else:
                # New node — insert into target branch
                node.id = original_id
                node.branch = target
                self._system_insert(node, reason="branch_merge")
                merged += 1

        self._conn.commit()
        return merged

    # ═══════════════════════════════════════════
    #  Time travel (M3: Bi-temporal)
    # ═══════════════════════════════════════════

    def get_at_time(self, node_id: str, timestamp: float,
                    branch: str = "main") -> Node | None:
        """Time-travel query: get node state at a specific point in time."""
        row = self._conn.execute("""
            SELECT * FROM nodes
            WHERE id=? AND branch=?
            AND tx_from <= ? AND (tx_to = 0 OR tx_to > ?)
            AND valid_from <= ? AND (valid_to = 0 OR valid_to > ?)
            ORDER BY tx_from DESC LIMIT 1
        """, (node_id, branch, timestamp, timestamp, timestamp, timestamp)).fetchone()
        if row is None:
            return None
        return self._row_to_node(row)

    # ═══════════════════════════════════════════
    #  Bulk operations
    # ═══════════════════════════════════════════

    def get_all_nodes(self, branch: str = "main", layer: MemoryLayer | None = None,
                      limit: int = 1000) -> list[Node]:
        """Get all active nodes, optionally filtered by layer."""
        if layer is not None:
            rows = self._conn.execute(
                "SELECT * FROM nodes WHERE branch=? AND tx_to=0 AND layer=? LIMIT ?",
                (branch, layer, limit),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM nodes WHERE branch=? AND tx_to=0 LIMIT ?",
                (branch, limit),
            ).fetchall()
        return [self._row_to_node(r) for r in rows if self._row_to_node(r) is not None]

    def count_nodes(self, branch: str = "main") -> int:
        """Count active nodes."""
        row = self._conn.execute(
            "SELECT COUNT(*) as cnt FROM nodes WHERE branch=? AND tx_to=0",
            (branch,),
        ).fetchone()
        return row["cnt"] if row else 0

    def count_edges(self, branch: str = "main") -> int:
        """Count active edges."""
        row = self._conn.execute(
            "SELECT COUNT(*) as cnt FROM edges WHERE branch=? AND tx_to=0",
            (branch,),
        ).fetchone()
        return row["cnt"] if row else 0

    def close(self) -> None:
        """Close the database connection."""
        self._conn.close()

    # ═══════════════════════════════════════════
    #  Internal helpers
    # ═══════════════════════════════════════════

    def _row_to_node(self, row: sqlite3.Row) -> Node | None:
        """Convert a database row to a Node. P-26: reads ALL columns."""
        try:
            embedding = []
            if row["embedding"] is not None:
                embedding = json.loads(row["embedding"])

            return Node(
                id=row["id"],
                type=NodeType(row["type"]),
                content=row["content"],
                embedding=embedding,
                valid_from=row["valid_from"],
                valid_to=row["valid_to"],
                tx_from=row["tx_from"],
                tx_to=row["tx_to"],
                layer=MemoryLayer(row["layer"]),
                trust=TrustLevel(row["trust"]),
                reinforce_count=row["reinforce_count"],
                utility=row["utility"],
                surprise=row["surprise"],
                source=ProvenanceType(row["source"]),
                creator_agent=row["creator_agent"],
                session_id=row["session_id"],
                parent_id=row["parent_id"],
                confidence=row["confidence"],
                raw_proof=row["raw_proof"],
                branch=row["branch"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                accessed_at=row["accessed_at"],
                access_count=row["access_count"],
                is_consolidated=bool(row["is_consolidated"]),
                custom_type=row["custom_type"],
            )
        except (KeyError, ValueError) as e:
            # P-26 guard: if column missing, log and return None
            return None

# ===== 来自XYZ系统 =====
    """关键词节点 - 连接事件"""
    key_id: str
    text: str = ""
    tag_list: List[str] = field(default_factory=list)
    tag_dict: Dict[str, List[str]] = field(default_factory=dict)
    
    def add_tag(self, tag: str, event_id: str) -> None:
        """添加tag连接"""
        if tag not in self.tag_list:
            self.tag_list.append(tag)
        if tag not in self.tag_dict:
            self.tag_dict[tag] = []
        if event_id not in self.tag_dict[tag]:
            self.tag_dict[tag].append(event_id)
    
    def get_events_by_tag(self, tag: str) -> List[str]:
        """按tag获取事件ID列表"""
        return self.tag_dict.get(tag, [])

# ===== 来自XYZ系统 =====
class KeyNode:
    """关键词节点 - 连接事件"""
    key_id: str
    text: str = ""
    tag_list: List[str] = field(default_factory=list)
    tag_dict: Dict[str, List[str]] = field(default_factory=dict)
    
    def add_tag(self, tag: str, event_id: str) -> None:
        """添加tag连接"""
        if tag not in self.tag_list:
            self.tag_list.append(tag)
        if tag not in self.tag_dict:
            self.tag_dict[tag] = []
        if event_id not in self.tag_dict[tag]:
            self.tag_dict[tag].append(event_id)
    
    def get_events_by_tag(self, tag: str) -> List[str]:
        """按tag获取事件ID列表"""
        return self.tag_dict.get(tag, [])


