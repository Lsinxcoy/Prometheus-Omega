"""L4 Lifecycle - 生命周期层

整合XYZ机制:
- X: Weibull遗忘(5-tier), 4层Bank迁移, ZeroLLM, DopamineWriteGate
- Y: Consolidation, Bank
- Z: ConsolidationEngine
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta
from enum import Enum
import math
import random


class ForgettingStrategy(Enum):
    """遗忘策略"""
    WEIBULL = "weibull"      # 威布尔分布
    EXPONENTIAL = "exponential"
    LINEAR = "linear"


class WeibullForgetting:
    """Weibull遗忘 - 来自X系统#7
    
    5层参数:
    - shape (k): 曲线形状
    - scale (lambda): 尺度
    - threshold: 遗忘阈值
    - decay_rate: 衰减率
    - min_importance: 最低重要性
    """
    
    def __init__(self, 
                 shape: float = 1.5,      # k
                 scale: float = 30.0,     # lambda (天)
                 threshold: float = 0.1,
                 decay_rate: float = 0.05,
                 min_importance: float = 0.1):
        self.shape = shape
        self.scale = scale
        self.threshold = threshold
        self.decay_rate = decay_rate
        self.min_importance = min_importance
    
    def calculate(self, days_since_access: int, initial_importance: float) -> float:
        """计算当前重要性"""
        if days_since_access == 0:
            return initial_importance
        
        # Weibull分布: f(t) = (k/lambda) * (t/lambda)^(k-1) * e^(-(t/lambda)^k)
        t = days_since_access
        k = self.shape
        lmbda = self.scale
        
        # 记忆强度
        strength = math.exp(-((t / lmbda) ** k))
        current_importance = initial_importance * strength
        
        return max(current_importance, self.min_importance)
    
    def should_forget(self, entry) -> bool:
        """判断是否应该遗忘"""
        now = datetime.now(timezone.utc)
        days = (now - entry.last_accessed).days
        current = self.calculate(days, entry.importance)
        return current < self.threshold


class BankMigration:
    """Bank迁移 - 来自X系统#8"""
    
    def __init__(self, bank):
        self.bank = bank
    
    def auto_migrate(self) -> Dict[str, int]:
        """自动迁移"""
        return {"migrated": self.bank.migrate()}


class Consolidation:
    """记忆整合 - 来自X/Y/Z系统"""
    
    def __init__(self, interval_hours: int = 6):
        self.interval_hours = interval_hours
        self.last_consolidation = datetime.now(timezone.utc)
    
    def should_consolidate(self) -> bool:
        """是否应该整合"""
        now = datetime.now(timezone.utc)
        hours = (now - self.last_consolidation).total_seconds() / 3600
        return hours >= self.interval_hours
    
    def consolidate(self, memory_store) -> Dict[str, any]:
        """执行整合"""
        if not self.should_consolidate():
            return {"status": "skipped", "reason": "not_due"}
        
        # 简化整合
        entries = list(memory_store.entries.values())
        
        # 按主题聚类
        topics: Dict[str, List] = {}
        for entry in entries:
            for tag in entry.tags:
                if tag not in topics:
                    topics[tag] = []
                topics[tag].append(entry)
        
        self.last_consolidation = datetime.now(timezone.utc)
        
        return {
            "status": "completed",
            "entries_processed": len(entries),
            "topics_identified": len(topics),
        }


class ZeroLLM:
    """ZeroLLM生命周期 - 来自X系统#10
    
    防止外部LLM无限调用的保护机制
    """
    
    def __init__(self, max_calls_per_day: int = 1000):
        self.max_calls = max_calls_per_day
        self.today_calls = 0
        self.last_reset = datetime.now(timezone.utc).date()
    
    def can_call_llm(self) -> bool:
        """是否可以调用LLM"""
        self._check_reset()
        return self.today_calls < self.max_calls
    
    def record_call(self):
        """记录调用"""
        self._check_reset()
        self.today_calls += 1
    
    def _check_reset(self):
        """检查并重置"""
        today = datetime.now(timezone.utc).date()
        if today > self.last_reset:
            self.today_calls = 0
            self.last_reset = today
    
    def get_remaining(self) -> int:
        """剩余调用次数"""
        self._check_reset()
        return max(0, self.max_calls - self.today_calls)


class DopamineWriteGate:
    """多巴胺写入门控 - 来自X/Y系统#11
    
    3铁律之一: 根据内容质量(importance * utility * veracity)和多巴胺水平决定是否允许写入
    
    工作原理:
    1. 接收节点的importance/utility/veracity分数
    2. 计算质量分数 = importance * utility * veracity
    3. 与当前dopamine_level比较
    4. 通过后更新dopamine_level(奖励/惩罚机制)
    """
    
    def __init__(self, 
                 threshold: float = 0.3,
                 tau: float = 1.0,
                 decay_rate: float = 0.95,
                 boost_rate: float = 1.2,
                 min_dopamine: float = 0.1,
                 max_dopamine: float = 1.0):
        """初始化写入门控
        
        Args:
            threshold: 质量阈值, 低于此值拒绝写入
            tau: 温度参数, 控制随机性
            decay_rate: 多巴胺衰减率(每次拒绝后)
            boost_rate: 多巴胺boost率(每次通过后)
            min_dopamine: 最小多巴胺水平
            max_dopamine: 最大多巴胺水平
        """
        self.threshold = threshold
        self.tau = tau
        self.decay_rate = decay_rate
        self.boost_rate = boost_rate
        self.min_dopamine = min_dopamine
        self.max_dopamine = max_dopamine
        
        # 多巴胺水平: 0.1(低) -> 1.0(高)
        self.dopamine_level = 0.5
        
        # 统计
        self.total_attempts = 0
        self.total_approved = 0
        self.total_rejected = 0
        
        # 历史记录
        self._history: List[Dict] = []
    
    def can_write(self, quality_score: float) -> bool:
        """判断是否允许写入
        
        Args:
            quality_score: 质量分数 (0.0-1.0)
            
        Returns:
            bool: 是否允许写入
        """
        import time
        self.total_attempts += 1
        
        # === 输入验证 ===
        if not isinstance(quality_score, (int, float)):
            quality_score = 0.0
        
        # === 边界检查 ===
        quality_score = max(0.0, min(1.0, quality_score))
        
        # === 核心逻辑 ===
        # 有效质量 = 原始质量 * 多巴胺调节因子
        # 低多巴胺时提高阈值, 高多巴胺时降低阈值
        dopamine_factor = self.dopamine_level  # 0.1-1.0
        effective_threshold = self.threshold / dopamine_factor
        
        # 有效质量需要超过有效阈值
        can_write = quality_score >= effective_threshold
        
        # === 更新多巴胺 ===
        if can_write:
            self.dopamine_level = min(
                self.max_dopamine,
                self.dopamine_level * self.boost_rate
            )
            self.total_approved += 1
        else:
            self.dopamine_level = max(
                self.min_dopamine,
                self.dopamine_level * self.decay_rate
            )
            self.total_rejected += 1
        
        # === 记录历史 ===
        self._history.append({
            "timestamp": time.time(),
            "quality_score": quality_score,
            "threshold": effective_threshold,
            "dopamine_before": self.dopamine_level,
            "approved": can_write,
        })
        
        # 保持最近1000条
        if len(self._history) > 1000:
            self._history = self._history[-1000:]
        
        return can_write
    
    def compute_quality(self, importance: float, utility: float, veracity: float) -> float:
        """计算质量分数
        
        质量公式: Q = importance * (0.5 + utility/2) * veracity
        
        Args:
            importance: 重要性 (0.0-1.0)
            utility: 有用性 (0.0-1.0)
            veracity: 真实性 (0.0-1.0)
            
        Returns:
            float: 质量分数 (0.0-1.0)
        """
        # === 输入验证 ===
        importance = max(0.0, min(1.0, importance or 0))
        utility = max(0.0, min(1.0, utility or 0))
        veracity = max(0.0, min(1.0, veracity or 0.5))
        
        # === 质量公式 ===
        # importance: 基础重要性
        # utility: 0-1映射到0.5-1.0, 确保utility为0时也有基础分
        # veracity: 真实性加权
        quality = importance * (0.5 + utility * 0.5) * veracity
        
        return quality
    
    def get_dopamine_level(self) -> float:
        """获取当前多巴胺水平"""
        return self.dopamine_level
    
    def adjust_dopamine(self, delta: float):
        """手动调整多巴胺水平
        
        Args:
            delta: 调整量 (-1.0到1.0)
        """
        self.dopamine_level = max(
            self.min_dopamine,
            min(self.max_dopamine, self.dopamine_level + delta)
        )
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        total = self.total_attempts
        approval_rate = self.total_approved / total if total > 0 else 0
        
        return {
            "dopamine_level": self.dopamine_level,
            "threshold": self.threshold,
            "total_attempts": total,
            "approved": self.total_approved,
            "rejected": self.total_rejected,
            "approval_rate": approval_rate,
        }
    
    def reset_stats(self):
        """重置统计"""
        self.total_attempts = 0
        self.total_approved = 0
        self.total_rejected = 0
        self._history = []
    
    def get_history(self, limit: int = 100) -> List[Dict]:
        """获取历史记录"""
        return self._history[-limit:]
        # 向后兼容: 如果是浮点数，直接使用
        if isinstance(node, (int, float)):
            content_quality = node
        else:
            # 从OmegaNode提取质量指标
            importance = getattr(node, 'importance', 0.5)
            utility = getattr(node, 'utility', 0.0)
            veracity = getattr(node, 'veracity', 0.5)
            
            # 计算综合质量分数 (0-1范围)
            content_quality = importance * veracity * (0.5 + utility / 20.0)
        
        # 门控: 质量必须超过阈值
        return content_quality >= self.tau
    
    def should_write(self, node) -> bool:
        """别名方法，用于与Z系统兼容"""
        return self.can_write(node)
    
    def stimulate(self, amount: float = 0.1):
        """刺激多巴胺"""
        self.dopamine_level = min(1.0, self.dopamine_level + amount)
    
    def deplete(self, amount: float = 0.05):
        """消耗多巴胺"""
        self.dopamine_level = max(0.0, self.dopamine_level - amount)


class CasesToSkills:
    """案例到技能自动学习 - 来自X系统#12"""
    
    def __init__(self, min_cases: int = 5):
        self.min_cases = min_cases
        self.cases: Dict[str, List] = {}  # pattern -> cases
    
    def add_case(self, pattern: str, case: Dict):
        """添加案例"""
        if pattern not in self.cases:
            self.cases[pattern] = []
        self.cases[pattern].append(case)
    
    def extract_skill(self, pattern: str) -> Optional[Dict]:
        """提取技能"""
        cases = self.cases.get(pattern, [])
        if len(cases) < self.min_cases:
            return None
        
        return {
            "pattern": pattern,
            "examples": cases[:self.min_cases],
            "confidence": len(cases) / 10.0,
        }


# 工厂
def create_weibull_forgetting(**kwargs) -> WeibullForgetting:
    return WeibullForgetting(**kwargs)

def create_consolidation(interval_hours: int = 6) -> Consolidation:
    return Consolidation(interval_hours=interval_hours)

def create_zero_llm(max_calls: int = 1000) -> ZeroLLM:
    return ZeroLLM(max_calls_per_day=max_calls)

def create_dopamine_gate(threshold: float = 0.3) -> DopamineWriteGate:
    return DopamineWriteGate(threshold=threshold)


# ===== 来自XYZ系统 =====
class Metabolism:
    """K11: Memory metabolism — competitive energy allocation.

    Energy is allocated competitively: higher utility nodes get
    proportionally more energy. The exponent α controls how
    aggressively high-utility nodes are favored (α=1 = proportional,
    α=2 = quadratic advantage for high-utility nodes).
    """

    def __init__(self, store: MinervaStore, config: ZConfig | None = None,
                 alpha: float = 1.5):
        self._store = store
        self._config = config or ZConfig()
        self._alpha = alpha  # Utility exponent for competitive allocation
        self._total_energy = 100.0
        self._allocated: dict[str, float] = {}
        self._node_utilities: dict[str, float] = {}  # Track utility for rebalance
        self._stats = {"allocations": 0, "deallocations": 0,
                       "total_allocated": 0.0, "rebalances": 0}

    def allocate(self, node: Node) -> float:
        """Allocate energy to a memory node using competitive formula.

        Energy = budget × (utility^α) / Σ(all utilities^α)

        Recency and access frequency also factor in via effective_utility:
        effective = utility × recency × access_freq
        """
        self._stats["allocations"] += 1

        # Compute effective utility (utility × recency × access_freq)
        utility_norm = node.utility / self._config.max_utility
        now = time.time()
        age = (now - node.created_at) if node.created_at > 0 and now > node.created_at else 0
        recency = math.exp(-age / (86400 * 30))  # 30-day half-life
        access_freq = max(0.1, min(1.0, node.reinforce_count / 10.0))
        effective_utility = utility_norm * recency * access_freq

        self._node_utilities[node.id] = effective_utility

        # Competitive allocation: proportional to utility^α
        energy = self._competitive_allocate(node.id, effective_utility)

        self._allocated[node.id] = energy
        self._stats["total_allocated"] = sum(self._allocated.values())

        return energy

    def _competitive_allocate(self, node_id: str,
                               effective_utility: float) -> float:
        """Competitive energy allocation.

        If total allocation < budget: allocate proportionally.
        If total allocation >= budget: compete with existing nodes.

        Higher α means high-utility nodes dominate more.
        """
        # If we're within budget, just allocate proportionally
        current_total = sum(self._allocated.values())
        remaining_budget = self._total_energy - current_total

        if remaining_budget > 0:
            # Proportional share of remaining budget
            share = remaining_budget * 0.01 * effective_utility
            return min(share, remaining_budget)

        # Budget exceeded: compete — take from lowest-utility nodes
        # Find the node with lowest effective utility
        if self._node_utilities:
            min_id = min(self._node_utilities, key=self._node_utilities.get)
            min_utility = self._node_utilities[min_id]

            # Only take if this node is more deserving
            if effective_utility > min_utility and min_id in self._allocated:
                # Take a fraction of the low-utility node's energy
                stolen = self._allocated[min_id] * 0.5
                self._allocated[min_id] -= stolen
                return stolen

        # Fallback: small allocation
        return self._total_energy * 0.001

    def deallocate(self, node_id: str) -> float:
        """Deallocate energy from a memory node (e.g., after forgetting)."""
        energy = self._allocated.pop(node_id, 0.0)
        self._node_utilities.pop(node_id, None)
        self._stats["deallocations"] += 1
        return energy

    def rebalance(self) -> dict:
        """Rebalance energy allocation with priority re-sorting.

        Steps:
        1. Recompute effective utilities for all allocated nodes
        2. Sort by utility (highest first)
        3. Re-allocate budget proportionally using utility^α
        4. Ensure total doesn't exceed budget

        This ensures that after rebalancing, high-utility nodes
        get MORE energy than they had before, while low-utility
        nodes get LESS — not just proportional scaling.
        """
        self._stats["rebalances"] += 1

        if not self._allocated:
            return {"status": "empty", "total": 0.0,
                    "budget": self._total_energy}

        # Compute utility^α for all allocated nodes
        powered: dict[str, float] = {}
        total_powered = 0.0
        for nid in self._allocated:
            util = self._node_utilities.get(nid, 0.1)
            p = util ** self._alpha
            powered[nid] = p
            total_powered += p

        if total_powered == 0:
            return {"status": "balanced", "total": 0.0,
                    "budget": self._total_energy}

        # Re-allocate proportionally to utility^α
        for nid in self._allocated:
            self._allocated[nid] = self._total_energy * powered[nid] / total_powered

        total = sum(self._allocated.values())
        # Ensure we don't exceed budget (floating point safety)
        if total > self._total_energy:
            scale = self._total_energy / total
            for nid in self._allocated:
                self._allocated[nid] *= scale

        self._stats["total_allocated"] = sum(self._allocated.values())

        # Compute Gini coefficient for inequality measurement
        gini = self._compute_gini()

        return {
            "status": "rebalanced",
            "total": sum(self._allocated.values()),
            "budget": self._total_energy,
            "gini": gini,  # Higher = more unequal = high-utility nodes dominate
        }

    def _compute_gini(self) -> float:
        """Compute Gini coefficient of energy distribution.

        0 = perfectly equal, 1 = one node has all energy.
        Healthy system: 0.3-0.6 (some inequality, high-value nodes dominate).
        """
        values = sorted(self._allocated.values())
        n = len(values)
        if n == 0:
            return 0.0

        total = sum(values)
        if total == 0:
            return 0.0

        cumsum = 0.0
        gini_sum = 0.0
        for i, v in enumerate(values):
            cumsum += v
            gini_sum += (2 * (i + 1) - n - 1) * v

        return gini_sum / (n * total)

    def get_energy(self, node_id: str) -> float:
        """Get energy allocated to a node."""
        return self._allocated.get(node_id, 0.0)

    def get_low_energy_nodes(self, threshold: float = 0.1) -> list[str]:
        """Get nodes with energy below threshold (candidates for forgetting)."""
        return [nid for nid, e in self._allocated.items() if e < threshold]

    def reclaim_energy(self, node_ids: list[str]) -> float:
        """Reclaim energy from removed/forgotten nodes.

        Redistributes reclaimed energy proportionally to surviving nodes.
        """
        reclaimed = 0.0
        for nid in node_ids:
            if nid in self._allocated:
                reclaimed += self._allocated.pop(nid)
            self._node_utilities.pop(nid, None)

        if reclaimed > 0:
            # Redistribute reclaimed energy proportionally to utility^α
            total_powered = 0.0
            powered = {}
            for nid in self._allocated:
                util = self._node_utilities.get(nid, 0.1)
                p = util ** self._alpha
                powered[nid] = p
                total_powered += p

            if total_powered > 0:
                for nid in self._allocated:
                    self._allocated[nid] += reclaimed * powered[nid] / total_powered

            self._stats["reclaimed"] = self._stats.get("reclaimed", 0) + reclaimed

        return reclaimed

    @property
    def total_allocated(self) -> float:
        return sum(self._allocated.values())

    @property
    def budget_remaining(self) -> float:
        return max(0.0, self._total_energy - self.total_allocated)

    @property
    def stats(self) -> dict:
        return dict(self._stats)

    @property
    def gini(self) -> float:
        """Current Gini coefficient of energy distribution."""
        return self._compute_gini()


# ===== 来自XYZ系统 =====
class BeliefSystem:
    """E17: Three-layer belief state management."""

    def __init__(self, store: MinervaStore, config: ZConfig | None = None):
        self._store = store
        self._config = config or ZConfig()

    def record_event(self, content: str, branch: str = "main",
                     creator_agent: str = "") -> str:
        """Layer 1: Record a raw event in EventBuffer (WORKING memory)."""
        node = Node(
            content=content,
            type=NodeType.CONCEPT,
            utility=1.0,  # Low initial utility
            layer=MemoryLayer.WORKING,
            trust=TrustLevel.PENDING,
            creator_agent=creator_agent,
            branch=branch,
            custom_type="event",
        )
        return self._store._system_insert(node, reason="belief")

    def form_preference(self, event_id: str, branch: str = "main") -> Node | None:
        """Layer 2: Promote a repeated event to a PreferenceMemory (EPISODIC).

        Only if the event has been reinforced (reinforce_count >= 2).
        """
        event = self._store.get(event_id, branch)
        if event is None:
            return None

        # Only reinforce if seen multiple times
        event.reinforce_count += 1
        self._store._system_update(event, reason="belief")

        if event.reinforce_count < 2:
            return None

        # Create preference node
        pref = Node(
            content=f"Preference: {event.content}",
            type=NodeType.CONCEPT,
            utility=event.utility + 1.0,
            layer=MemoryLayer.EPISODIC,
            trust=TrustLevel.HIGH_SIGNAL,
            creator_agent=event.creator_agent,
            parent_id=event.id,
            branch=branch,
            custom_type="preference",
        )
        pref_id = self._store._system_insert(pref, reason="belief")

        # Create DERIVES_FROM edge
        edge = Edge(
            source=pref_id,
            target=event.id,
            type=EdgeType.DERIVED_FROM,
            weight=1.0,
            branch=branch,
        )
        self._store.insert_edge(edge)

        return pref

    def update_narrative(self, branch: str = "main") -> Node | None:
        """Layer 3: Update ProfileNarrative from confirmed preferences.

        Aggregates all HIGH_SIGNAL+ preferences into a narrative.
        """
        nodes = self._store.get_all_nodes(branch, limit=10000)
        preferences = [n for n in nodes
                       if n.custom_type == "preference"
                       and n.trust >= TrustLevel.HIGH_SIGNAL]

        if not preferences:
            return None

        # Find or create narrative node
        existing = [n for n in nodes if n.custom_type == "narrative"]
        if existing:
            narrative = existing[0]
        else:
            narrative = Node(
                content="",
                type=NodeType.CONCEPT,
                utility=5.0,
                layer=MemoryLayer.SEMANTIC,
                trust=TrustLevel.VERIFIED,
                branch=branch,
                custom_type="narrative",
            )

        # Build narrative from preferences
        lines = [f"- {p.content}" for p in preferences[:20]]
        narrative.content = "Profile Narrative:\n" + "\n".join(lines)
        self._store._system_insert(narrative, reason="belief")

        return narrative

    def get_belief_state(self, branch: str = "main") -> dict:
        """Get current belief state across all three layers."""
        nodes = self._store.get_all_nodes(branch, limit=10000)
        events = [n for n in nodes if n.custom_type == "event"]
        preferences = [n for n in nodes if n.custom_type == "preference"]
        narratives = [n for n in nodes if n.custom_type == "narrative"]

        return {
            "events": len(events),
            "preferences": len(preferences),
            "narratives": len(narratives),
            "event_layer": MemoryLayer.WORKING.name,
            "preference_layer": MemoryLayer.EPISODIC.name,
            "narrative_layer": MemoryLayer.SEMANTIC.name,
        }


# ===== 来自XYZ系统 =====
class CascadingFetch:
    """D9: 6-level waterfall retrieval with confidence thresholds.

    Confidence is computed via 3-dimensional fusion:
    1. FTS score normalized by historical max (adaptive)
    2. Semantic overlap between top results (Jaccard)
    3. Graph support from neighbor corroboration
    """

    def __init__(self, store: MinervaStore, config: ZConfig | None = None,
                 api_adapter: APIAdapter | None = None):
        self._store = store
        self._config = config or ZConfig()
        self._api_adapter = api_adapter
        self._cache: dict[str, list[Node]] = {}
        self._stats = {"cache_hits": 0, "vector_hits": 0, "graph_hits": 0,
                       "llm_hits": 0, "api_hits": 0, "human_hits": 0}
        # Adaptive normalization: track historical FTS max score
        self._fts_score_history: list[float] = []
        self._fts_score_max = 10.0  # Initial default

    def fetch(self, query: str, branch: str = "main",
              confidence_threshold: float = 0.7) -> FetchResult:
        """Cascade through retrieval levels until confidence >= threshold."""
        # Level 1: Cache
        if query in self._cache:
            nodes = self._cache[query]
            if nodes:
                self._stats["cache_hits"] += 1
                return FetchResult(
                    found=True, nodes=nodes,
                    level=0, level_name="cache", source="cache",
                    confidence=1.0, cost=0.0,
                )

        # Level 2: FTS + vector
        fts_results = self._store.search_fts(query, limit=10, branch=branch)
        if fts_results:
            # Update adaptive normalization
            best_raw = fts_results[0][1] if fts_results else 0.0
            self._fts_score_history.append(best_raw)
            if len(self._fts_score_history) > 100:
                self._fts_score_history = self._fts_score_history[-100:]
            self._fts_score_max = max(self._fts_score_max, best_raw)

            nodes = [n for n, _score in fts_results]
            # Adaptive confidence: normalize by historical max
            confidence = min(1.0, best_raw / self._fts_score_max)

            if confidence >= confidence_threshold:
                self._cache[query] = nodes
                self._stats["vector_hits"] += 1
                return FetchResult(
                    found=True, nodes=nodes,
                    level=1, level_name="vector", source="vector",
                    confidence=confidence, cost=0.01,
                )

        # Level 3: Graph neighborhood expansion
        if fts_results:
            seed_node = fts_results[0][0]
            neighbors = self._store.get_neighbors(seed_node.id, branch=branch)
            neighbor_nodes = [n for _e, n in neighbors]
            all_nodes = [n for n, _s in fts_results] + neighbor_nodes

            # Deduplicate by ID
            seen_ids: set[str] = set()
            unique_nodes = []
            for n in all_nodes:
                if n.id not in seen_ids:
                    seen_ids.add(n.id)
                    unique_nodes.append(n)

            if len(unique_nodes) > len(fts_results):
                self._cache[query] = unique_nodes
                self._stats["graph_hits"] += 1
                return FetchResult(
                    found=True, nodes=unique_nodes,
                    level=2, level_name="graph", source="graph",
                    confidence=min(0.8, confidence + 0.1), cost=0.02,
                )

        # Level 4: LLM — multi-source synthesis with 3D confidence
        llm_result = self._fetch_llm(query, fts_results, branch)
        if llm_result.found and llm_result.confidence >= confidence_threshold:
            self._cache[query] = llm_result.nodes
            self._stats["llm_hits"] += 1
            return llm_result

        # Level 5: API — pluggable external adapter
        api_result = self._fetch_api(query)
        if api_result.found and api_result.confidence >= confidence_threshold:
            self._cache[query] = api_result.nodes
            self._stats["api_hits"] += 1
            return api_result

        # Level 6: Human — escalate with fallback
        fallback_nodes = llm_result.nodes if llm_result.nodes else []
        return FetchResult(
            found=bool(fallback_nodes),
            nodes=fallback_nodes,
            level=5, level_name="human_escalation", source="human",
            confidence=llm_result.confidence if fallback_nodes else 0.0,
            cost=1.0,
            content=f"Requires human input: {query}" if not fallback_nodes else "",
        )

    def _fetch_llm(self, query: str,
                   fts_results: list[tuple[Node, float]],
                   branch: str) -> FetchResult:
        """Level 4: Multi-source synthesis with 3-dimensional confidence.

        Confidence = weighted average of:
        1. FTS score dimension (adaptive normalized)
        2. Semantic overlap dimension (Jaccard between top results)
        3. Graph support dimension (neighbor corroboration)

        Zero-LLM: no actual LLM call, uses deterministic fusion.
        """
        if not fts_results:
            return FetchResult(found=False, level=3, level_name="llm")

        nodes = [n for n, _s in fts_results]

        # ── Dimension 1: FTS score (adaptive normalized) ──
        best_raw = fts_results[0][1]
        fts_dim = min(1.0, best_raw / self._fts_score_max)

        # ── Dimension 2: Semantic overlap (Jaccard between top results) ──
        overlap_dim = 0.0
        if len(nodes) >= 2:
            word_sets = [set(n.content.lower().split()[:30]) for n in nodes[:3]]
            common = word_sets[0]
            for ws in word_sets[1:]:
                common = common & ws
            union = word_sets[0]
            for ws in word_sets[1:]:
                union = union | ws
            overlap_dim = len(common) / max(len(union), 1) if union else 0.0

        # ── Dimension 3: Graph support (neighbor corroboration) ──
        graph_dim = 0.0
        if nodes:
            seed = nodes[0]
            neighbors = self._store.get_neighbors(seed.id, branch=branch)
            neighbor_ids = {n.id for _e, n in neighbors}
            # How many FTS results have graph connections to the seed?
            corroborated = sum(1 for n in nodes[1:] if n.id in neighbor_ids)
            graph_dim = min(1.0, corroborated / max(len(nodes) - 1, 1))

        # ── Weighted fusion ──
        # FTS is primary signal, overlap validates, graph corroborates
        confidence = (
            0.5 * fts_dim +
            0.3 * overlap_dim +
            0.2 * graph_dim
        )
        # Boost if all 3 dimensions agree (multiplicative bonus)
        if fts_dim > 0.5 and overlap_dim > 0.3 and graph_dim > 0.2:
            confidence = min(1.0, confidence * 1.2)

        return FetchResult(
            found=True, nodes=nodes,
            level=3, level_name="llm", source="llm_synthesis",
            confidence=confidence, cost=0.1,
            content=nodes[0].content[:200] if nodes else "",
        )

    def _fetch_api(self, query: str) -> FetchResult:
        """Level 5: External API lookup via pluggable adapter.

        If no adapter is configured, returns not-found.
        """
        if self._api_adapter is None:
            return FetchResult(
                found=False, level=4, level_name="api",
                source="api", confidence=0.0, cost=0.5,
            )
        try:
            return self._api_adapter.fetch(query)
        except Exception:
            return FetchResult(
                found=False, level=4, level_name="api",
                source="api_error", confidence=0.0, cost=0.5,
            )

    @property
    def stats(self) -> dict:
        return dict(self._stats)

    def clear_cache(self) -> None:
        """Clear the in-memory cache."""
        self._cache.clear()


# ===== 来自XYZ系统 =====
class DreamCycle:
    """M6: Dream Cycle — graph reorganization during sleep."""

    def __init__(self, store: MinervaStore, events: EventBus | None = None,
                 config: ZConfig | None = None):
        self._store = store
        self._events = events or EventBus()
        self._config = config or ZConfig()
        self._lifecycle = ZeroLLMLifecycle(self._config)
        self._guard = ConsolidationGuard(store, self._config)

    def run(self, branch: str = "main") -> DreamResult:
        """Execute dream cycle: dedup → synthesize → pattern → foresight."""
        nodes = self._store.get_all_nodes(branch, limit=10000)
        if not nodes:
            return DreamResult()

        # Phase 1: Deduplication
        deduplicated = self._deduplicate(nodes, branch)

        # Phase 2: SHMR Belief Synthesis
        beliefs = self._synthesize_beliefs(branch)

        # Phase 3: Pattern Discovery
        patterns = self._discover_patterns(branch)

        # Phase 4: Foresight Generation
        foresights, edges = self._generate_foresight(branch)

        self._events.emit("dream_cycle.complete", {
            "deduplicated": deduplicated,
            "beliefs": beliefs,
            "patterns": patterns,
            "foresights": foresights,
            "edges": edges,
        })

        return DreamResult(
            deduplicated=deduplicated,
            patterns_found=patterns,
            beliefs_synthesized=beliefs,
            foresights_generated=foresights,
            edges_created=edges,
        )

    def _deduplicate(self, nodes: list[Node], branch: str) -> int:
        """Phase 1: Remove exact duplicates by fingerprint."""
        seen: dict[str, str] = {}
        count = 0
        for node in nodes:
            fp = node.fingerprint()
            if fp in seen:
                self._store.delete(node.id, branch)
                count += 1
            else:
                seen[fp] = node.id
        return count

    def _synthesize_beliefs(self, branch: str) -> int:
        """Phase 2: Merge highly similar episodic nodes into belief nodes.

        Two nodes are "similar" if they share >70% words.
        Uses ConsolidationGuard to protect originals.
        """
        nodes = self._store.get_all_nodes(branch, limit=10000)
        episodic = [n for n in nodes if n.layer == MemoryLayer.EPISODIC
                     and not n.is_consolidated]
        count = 0

        # Group by word overlap (O(n²) but limited to episodic)
        merged_ids: set[str] = set()
        for i, a in enumerate(episodic):
            if a.id in merged_ids:
                continue
            for j in range(i + 1, len(episodic)):
                b = episodic[j]
                if b.id in merged_ids:
                    continue
                if self._word_overlap(a.content, b.content) > 0.7:
                    # Consolidate b into a (ConsolidationGuard protects b)
                    self._guard.consolidate_safely(b, branch)
                    merged_ids.add(b.id)
                    count += 1

        return count

    def _discover_patterns(self, branch: str) -> int:
        """Phase 3: Find communities in the knowledge graph."""
        communities = detect_communities(self._store, branch, min_size=3)
        return len(communities)

    def _generate_foresight(self, branch: str) -> tuple[int, int]:
        """Phase 4: Create PREDICTS edges from pattern communities."""
        communities = detect_communities(self._store, branch, min_size=3)
        edges_created = 0
        foresights = 0

        # For each community, create PREDICTS edges between sequential nodes
        for community in communities:
            if len(community) < 2:
                continue
            # Link first → last as a prediction
            edge = Edge(
                source=community[0],
                target=community[-1],
                type=EdgeType.PREDICTS,
                weight=0.3,  # Low confidence prediction
                branch=branch,
            )
            try:
                self._store.insert_edge(edge)
                edges_created += 1
                foresights += 1
            except Exception:
                pass

        return foresights, edges_created

    @staticmethod
    def _word_overlap(a: str, b: str) -> float:
        """Jaccard similarity on word sets."""
        wa = set(a.lower().split())
        wb = set(b.lower().split())
        if not wa and not wb:
            return 1.0
        if not wa or not wb:
            return 0.0
        return len(wa & wb) / len(wa | wb)


# ===== 来自XYZ系统 =====
class TrajectoryStore:
    """D5: Record and recall execution trajectories."""

    def __init__(self, store: MinervaStore, config: ZConfig | None = None):
        self._store = store
        self._config = config or ZConfig()

    def record(self, steps: list[TrajectoryStep], branch: str = "main",
               creator_agent: str = "") -> str:
        """Record a complete execution trajectory.

        Creates a trajectory node + step nodes + PRECEDES edges.
        Returns trajectory node ID.
        """
        if not steps:
            return ""

        # Create trajectory head node
        avg_utility = sum(s.utility for s in steps) / len(steps)
        head_content = f"Trajectory: {steps[0].state} → {steps[-1].outcome}"

        head = Node(
            content=head_content,
            type=NodeType.PROCEDURE,
            utility=avg_utility,
            trust=TrustLevel.PENDING,
            creator_agent=creator_agent,
            branch=branch,
            custom_type="trajectory",
        )
        head_id = self._store._system_insert(head, reason="trajectory")

        # Create step nodes and chain them
        prev_id = head_id
        for i, step in enumerate(steps):
            step_content = json.dumps(step.to_dict())
            step_node = Node(
                content=step_content,
                type=NodeType.PROCEDURE,
                utility=step.utility,
                trust=TrustLevel.PENDING,
                creator_agent=creator_agent,
                parent_id=head_id,
                branch=branch,
                custom_type="trajectory_step",
            )
            step_id = self._store._system_insert(step_node, reason="trajectory")

            # PRECEDES edge: prev → step
            edge = Edge(
                source=prev_id,
                target=step_id,
                type=EdgeType.PRECEDES,
                weight=1.0,
                branch=branch,
            )
            self._store.insert_edge(edge)
            prev_id = step_id

        return head_id

    def recall_similar(self, query: str, branch: str = "main",
                       limit: int = 5,
                       prefer_recent: bool = True) -> list[tuple[Node, float]]:
        """Recall trajectories similar to the query.

        Uses FTS5 to find trajectory heads matching the query.
        When prefer_recent=True, boosts scores for more recent trajectories
        and for trajectories with higher step counts (causal richness).
        """
        results = self._store.search_fts(query, limit=limit * 2, branch=branch)
        trajectories = [(n, s) for n, s in results
                        if n.custom_type == "trajectory"]

        if prefer_recent and trajectories:
            boosted = []
            for node, score in trajectories:
                # Recency boost: newer trajectories get higher score
                age = time.time() - node.created_at
                recency = 1.0 / (1.0 + age / 86400)  # Half-life = 1 day

                # Causal richness: count PRECEDES edges from this trajectory
                neighbors = self._store.get_neighbors(
                    node.id, EdgeType.PRECEDES, branch
                )
                step_count = len(neighbors)
                richness = min(step_count / 5.0, 1.0)  # Cap at 5 steps

                # Combined score: base FTS × recency × (1 + richness)
                combined = score * recency * (1.0 + richness)
                boosted.append((node, combined))

            boosted.sort(key=lambda x: x[1], reverse=True)
            return boosted[:limit]

        return trajectories[:limit]

    def chain(self, trajectory_ids: list[str],
              branch: str = "main") -> list[Node]:
        """Chain multiple trajectories into a reasoning path.

        Follows PRECEDES edges to reconstruct the full step sequence.
        """
        all_steps: list[Node] = []

        for tid in trajectory_ids:
            head = self._store.get(tid, branch)
            if head is None:
                continue

            # Follow PRECEDES edges
            current_id = tid
            visited: set[str] = set()
            while current_id and current_id not in visited:
                visited.add(current_id)
                node = self._store.get(current_id, branch)
                if node is not None:
                    all_steps.append(node)

                # Find next step via PRECEDES edge
                neighbors = self._store.get_neighbors(
                    current_id, EdgeType.PRECEDES, branch
                )
                if neighbors:
                    current_id = neighbors[0][1].id  # Next node
                else:
                    break

        return all_steps


# ===== 来自XYZ系统 =====
class LoopBudget:
    """Loop预算守卫"""
    daily_token_limit: int = 100000  # 默认100k/day
    warn_threshold: float = 0.8
    critical_threshold: float = 1.0
    
    used_tokens: int = 0
    last_reset: float = 0
    
    def __post_init__(self):
        self.last_reset = time.time()
    
    def can_proceed(self) -> Tuple[bool, str]:
        """检查是否可以继续
        
        Returns:
            (can_proceed, reason)
        """
        # 每日重置
        if time.time() - self.last_reset > 86400:
            self.used_tokens = 0
            self.last_reset = time.time()
        
        ratio = self.used_tokens / self.daily_token_limit
        
        if ratio >= self.critical_threshold:
            return False, "budget_exceeded"
        elif ratio >= self.warn_threshold:
            return True, f"warning_{int(ratio*100)}%_used"
        
        return True, "ok"
    
    def record_usage(self, tokens: int) -> None:
        """记录Token使用"""
        self.used_tokens += tokens
    
    def get_remaining(self) -> int:
        """获取剩余Token"""
        return max(0, self.daily_token_limit - self.used_tokens)
    
    def get_usage_ratio(self) -> float:
        """获取使用率"""
        return self.used_tokens / self.daily_token_limit
    
    def reset(self) -> None:
        """重置预算"""
        self.used_tokens = 0
        self.last_reset = time.time()
    
    def to_dict(self) -> dict:
        return {
            "daily_token_limit": self.daily_token_limit,
            "used_tokens": self.used_tokens,
            "remaining": self.get_remaining(),
            "usage_ratio": self.get_usage_ratio(),
            "last_reset": self.last_reset
        }



class BudgetManager:
    """预算管理器 - 多Loop聚合预算
    
    基于Loop Engineering的多Loop协调：
    - 聚合所有Loop的Token预算
    - 防止单个Loop耗尽资源
    """
    
    def __init__(self, total_budget: int = 500000):
        self.total_budget = total_budget
        self._loop_budgets: dict[str, LoopBudget] = {}
        self._usage_log: list[dict] = []
        self._log_file = Path("loop_budget_log.json")
        self._load_log()
    
    def get_or_create_budget(self, loop_id: str) -> LoopBudget:
        """获取或创建Loop预算"""
        if loop_id not in self._loop_budgets:
            self._loop_budgets[loop_id] = LoopBudget()
        return self._loop_budgets[loop_id]
    
    def check_global_budget(self, requested: int = 0) -> Tuple[bool, str]:
        """检查全局预算"""
        total_used = sum(b.used_tokens for b in self._loop_budgets.values())
        total_used += requested
        
        ratio = total_used / self.total_budget
        
        if ratio >= 1.0:
            return False, "global_budget_exceeded"
        elif ratio >= 0.8:
            return True, f"global_warning_{int(ratio*100)}%"
        
        return True, "ok"
    
    def record(self, loop_id: str, tokens: int, context: str = "") -> None:
        """记录Token使用"""
        budget = self.get_or_create_budget(loop_id)
        budget.record_usage(tokens)
        
        # 记录日志
        self._usage_log.append({
            "time": time.time(),
            "loop_id": loop_id,
            "tokens": tokens,
            "context": context,
            "global_total": sum(b.used_tokens for b in self._loop_budgets.values())
        })
        
        # 限制日志大小
        if len(self._usage_log) > 1000:
            self._usage_log = self._usage_log[-500:]
        
        self._save_log()
    
    def get_loop_status(self, loop_id: str) -> dict:
        """获取Loop预算状态"""
        budget = self._loop_budgets.get(loop_id)
        if not budget:
            return {"status": "not_found"}
        
        can_proceed, reason = budget.can_proceed()
        
        return {
            "loop_id": loop_id,
            "used": budget.used_tokens,
            "remaining": budget.get_remaining(),
            "ratio": budget.get_usage_ratio(),
            "can_proceed": can_proceed,
            "reason": reason
        }
    
    def get_global_status(self) -> dict:
        """获取全局预算状态"""
        total_used = sum(b.used_tokens for b in self._loop_budgets.values())
        
        return {
            "total_budget": self.total_budget,
            "used": total_used,
            "remaining": self.total_budget - total_used,
            "ratio": total_used / self.total_budget,
            "active_loops": len(self._loop_budgets)
        }
    
    def pause_all_loops(self) -> list[str]:
        """暂停所有Loop - 预算耗尽"""
        paused = []
        for loop_id in self._loop_budgets:
            budget = self._loop_budgets[loop_id]
            if budget.can_proceed()[0]:
                paused.append(loop_id)
                # 强制设为超限
                budget.used_tokens = budget.daily_token_limit + 1
        return paused
    
    def _load_log(self) -> None:
        """加载历史日志"""
        if self._log_file.exists():
            try:
                with open(self._log_file) as f:
                    self._usage_log = json.load(f)
            except json.JSONDecodeError:
                self._usage_log = []
    
    def _save_log(self) -> None:
        """保存日志"""
        with open(self._log_file, 'w') as f:
            json.dump(self._usage_log, f)


# 导出单例
_budget_manager: Optional[BudgetManager] = None

def get_budget_manager() -> BudgetManager:
    """获取预算管理器单例"""
    global _budget_manager
    if _budget_manager is None:
        _budget_manager = BudgetManager()
    return _budget_manager


# ===== 来自XYZ系统 =====
class AdaptiveConvergenceDetector(ConvergenceDetector):
    """自适应收敛检测器 - 根据历史调整阈值"""
    
    def __init__(self, initial_threshold: float = 0.01, 
                 min_threshold: float = 0.001,
                 max_threshold: float = 0.1):
        super().__init__(threshold=initial_threshold)
        self.initial_threshold = initial_threshold
        self.min_threshold = min_threshold
        self.max_threshold = max_threshold
        self._convergence_count = 0
        self._oscillation_count = 0
    
    def check_and_adapt(self, score: float) -> bool:
        """检查收敛并自适应调整"""
        self.add_score(score)
        
        # 检测震荡
        if len(self._history) >= 3:
            recent = self._history[-3:]
            if (recent[0] > recent[1] < recent[2]) or (recent[0] < recent[1] > recent[2]):
                self._oscillation_count += 1
                # 震荡时放宽阈值
                self.threshold = min(self.threshold * 1.5, self.max_threshold)
        
        is_converged = self.is_converged()
        
        if is_converged:
            self._convergence_count += 1
            # 连续收敛时收紧阈值
            if self._convergence_count >= 2:
                self.threshold = max(self.threshold * 0.5, self.min_threshold)
        
        return is_converged
    
    def to_dict(self) -> dict:
        """扩展序列化"""
        base = super().to_dict()
        base.update({
            "convergence_count": self._convergence_count,
            "oscillation_count": self._oscillation_count,
            "adaptive_threshold": self.threshold
        })
        return base


# ===== 来自XYZ系统 =====
class LoopStateMachine:
    """Loop执行状态机 - 核心组件
    
    严格遵守宪法铁律：
    - DopamineWriteGate: 防止无限制自我强化
    - AntiEvolutionGate: 防止危险变异
    - VerificationIronLaw: 必须有独立验证
    """
    
    def __init__(self, loop_id: str, max_attempts: int = 3,
                 convergence_threshold: float = 0.01):
        self.loop_id = loop_id
        self.max_attempts = max_attempts
        self.convergence_threshold = convergence_threshold
        self.executions: dict[str, LoopExecution] = {}
        self._current: LoopExecution | None = None
        
    def start(self) -> LoopExecution:
        """开始新的Loop执行"""
        run_id = f"{self.loop_id}_{int(time.time())}"
        exec = LoopExecution(
            run_id=run_id,
            start_time=time.time(),
            state=LoopState.DISCOVERING,
            max_attempts=self.max_attempts,
            convergence_threshold=self.convergence_threshold
        )
        self.executions[run_id] = exec
        self._current = exec
        return exec
    
    def transition(self, new_state: LoopState, metadata: dict = None):
        """状态转换"""
        if not self._current:
            return
        
        # 支持字符串或枚举
        if isinstance(new_state, str):
            new_state = LoopState(new_state)
        
        self._current.state = new_state
        if metadata:
            self._current.history.append({
                "state": new_state.value,
                "timestamp": time.time(),
                "metadata": metadata or {}
            })
    
    def increment_attempt(self) -> int:
        """增加尝试次数"""
        if self._current:
            self._current.attempt += 1
            return self._current.attempt
        return 0
    
    def record_error(self, error: str) -> None:
        """记录错误"""
        if self._current:
            self._current.errors.append({
                "time": time.time(),
                "error": error
            })
    
    def should_continue(self) -> tuple[bool, str]:
        """判断是否继续循环 - 宪法铁律核心"""
        if not self._current:
            return False, "No active execution"
        
        # 宪法铁律1: 尝试次数限制 (DopamineWriteGate)
        if self._current.attempt >= self._current.max_attempts:
            return False, "max_attempts_reached"
        
        # 收敛检测
        if len(self._current.history) >= 2:
            recent = self._current.history[-1]
            previous = self._current.history[-2]
            
            recent_score = recent.get("metadata", {}).get("score", None)
            previous_score = previous.get("metadata", {}).get("score", None)
            
            if recent_score is not None and previous_score is not None:
                improvement = abs(recent_score - previous_score)
                if improvement < self._current.convergence_threshold:
                    self.transition(LoopState.CONVERGED)
                    return False, "converged"
        
        return True, "continue"
    
    def escalate_to_human(self) -> dict:
        """升级到人工审核 - VerificationIronLaw"""
        self.transition(LoopState.ESCALATING)
        return {
            "loop_id": self.loop_id,
            "run_id": self._current.run_id if self._current else None,
            "reason": "requires_human_review",
            "attempt": self._current.attempt if self._current else 0,
            "max_attempts": self.max_attempts,
            "history": self._current.history if self._current else [],
            "errors": self._current.errors if self._current else [],
            "requires_human": True
        }
    
    def get_status(self) -> dict:
        """获取当前状态"""
        if not self._current:
            return {"state": "idle", "loop_id": self.loop_id}
        
        return {
            "loop_id": self.loop_id,
            "run_id": self._current.run_id,
            "state": self._current.state.value,
            "attempt": self._current.attempt,
            "max_attempts": self._current.max_attempts,
            "can_continue": self.should_continue()[0]
        }


# ===== 来自XYZ系统 =====
class GagarinInjector:
    """K13: Inject structural novelty into stagnant code."""

    INJECTION_STRATEGIES = [
        "add_abstraction",    # Extract interface/base class
        "split_function",     # Break large function into smaller ones
        "add_dataclass",      # Replace dict with dataclass
        "add_logging",        # Add structured logging
        "add_metrics",        # Add performance metrics
        "add_error_handling", # Add comprehensive error handling
        "add_caching",        # Add caching decorator
        "add_validation",     # Add input validation
    ]

    def __init__(self, config: ZConfig | None = None):
        self._config = config or ZConfig()
        self._ast_mutator = ASTMutation(config)
        self._stagnation_count = 0
        self._injections: list[dict] = []
        self._stats = {"injections": 0, "structural_edits": 0,
                       "failed_injections": 0}

    def check_and_inject(self, code: str, fitness_history: list[float],
                          stagnation_threshold: int = 5) -> str | None:
        """Check if code is stagnant and inject novelty if so.

        Returns modified code if injection applied, None otherwise.
        """
        # Check stagnation
        if not self._is_stagnant(fitness_history, stagnation_threshold):
            return None

        self._stagnation_count += 1

        # Select injection strategy based on stagnation level
        strategy_idx = (self._stagnation_count - 1) % len(self.INJECTION_STRATEGIES)
        strategy = self.INJECTION_STRATEGIES[strategy_idx]

        # Apply injection
        result = self._inject(code, strategy)
        if result is not None:
            self._stats["injections"] += 1
            self._stats["structural_edits"] += self._count_structural_edits(code, result)
            self._injections.append({
                "strategy": strategy,
                "stagnation_count": self._stagnation_count,
            })
        else:
            self._stats["failed_injections"] += 1

        return result

    def _is_stagnant(self, fitness_history: list[float],
                      threshold: int) -> bool:
        """Check if fitness has been stagnant for > threshold rounds."""
        if len(fitness_history) < threshold:
            return False
        recent = fitness_history[-threshold:]
        return (max(recent) - min(recent)) < 0.01

    def _inject(self, code: str, strategy: str) -> str | None:
        """Apply a specific injection strategy."""
        try:
            if strategy == "add_logging":
                return self._ast_mutator.mutate(code, "log_add")
            elif strategy == "add_error_handling":
                return self._ast_mutator.mutate(code, "error_handle")
            elif strategy == "add_abstraction":
                return self._add_abstraction(code)
            elif strategy == "add_validation":
                return self._ast_mutator.mutate(code, "assert_add")
            elif strategy == "add_dataclass":
                return self._ast_mutator.mutate(code, "type_annotate")
            elif strategy == "add_caching":
                return self._add_caching_decorator(code)
            elif strategy == "add_metrics":
                return self._add_metrics(code)
            elif strategy == "split_function":
                return self._split_function(code)
            else:
                return None
        except Exception:
            return None

    def _add_caching_decorator(self, code: str) -> str | None:
        """Add @lru_cache decorator to pure functions."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return None

        tree = copy.deepcopy(tree)

        class CacheAdder(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                # Add @lru_cache to functions without decorators
                if not node.decorator_list:
                    lru_cache = ast.Name(id="lru_cache", ctx=ast.Load())
                    node.decorator_list = [lru_cache]
                return node

        try:
            tree = CacheAdder().visit(tree)
            result = ast.unparse(tree)
            ast.parse(result)  # Verify
            return result
        except Exception:
            return None

    def _add_abstraction(self, code: str) -> str | None:
        """Extract repeated code blocks into a helper function (true abstraction).

        Strategy: Find a function with >1 repeated expression,
        extract it into a _helper function and replace occurrences.
        """
        try:
            tree = ast.parse(code)
            transformer = _AbstractionTransformer()
            new_tree = transformer.visit(tree)
            if not transformer.abstracted:
                return None  # No abstraction opportunity found
            ast.fix_missing_locations(new_tree)
            result = ast.unparse(new_tree)
            ast.parse(result)  # Verify
            return result
        except Exception:
            return None

    def _add_metrics(self, code: str) -> str | None:
        """Add timing metrics to function calls (not just logging).

        Strategy: Wrap function body with time.time() before/after,
        store delta in a module-level _metrics dict.
        """
        try:
            tree = ast.parse(code)
            transformer = _MetricsTransformer()
            new_tree = transformer.visit(tree)
            if not transformer.instrumented:
                return None  # No functions to instrument
            ast.fix_missing_locations(new_tree)
            result = ast.unparse(new_tree)
            ast.parse(result)  # Verify
            return result
        except Exception:
            return None

    def _split_function(self, code: str) -> str | None:
        """Split large functions (>20 lines) into helper + main.

        Strategy: extract the first half of the body into a helper function.
        """
        import copy as cp
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return None

        tree = cp.deepcopy(tree)
        modified = False

        class Splitter(ast.NodeTransformer):
            def __init__(self_outer):
                self_outer._helpers = []

            def visit_FunctionDef(self_outer, node):
                # Only split functions with >20 lines of body
                body = node.body
                has_doc = (body and isinstance(body[0], ast.Expr) and
                          isinstance(body[0].value, ast.Constant) and
                          isinstance(body[0].value.value, str))
                code_body = body[1:] if has_doc else body

                if len(code_body) <= 20:
                    return node

                # Split: first half → helper, second half stays
                mid = len(code_body) // 2
                helper_name = f"_{node.name}_helper"
                helper_body = code_body[:mid]
                main_body = code_body[mid:]

                # Create helper function
                helper = ast.FunctionDef(
                    name=helper_name,
                    args=node.args,
                    body=helper_body + [ast.Return(value=ast.Constant(value=None))],
                    decorator_list=[],
                    returns=None,
                )

                # Replace main body with helper call + remaining
                helper_call = ast.Expr(
                    value=ast.Call(
                        func=ast.Name(id=helper_name, ctx=ast.Load()),
                        args=[],
                        keywords=[],
                    )
                )

                new_body = ([body[0]] if has_doc else []) + [helper_call] + main_body
                node.body = new_body
                self_outer._helpers.append(helper)
                modified = True
                return node

        splitter = Splitter()
        tree = splitter.visit(tree)

        if not modified:
            return None

        # Add helper functions to module
        for helper in splitter._helpers:
            tree.body.insert(0, helper)

        try:
            result = ast.unparse(tree)
            ast.parse(result)  # Verify
            return result
        except Exception:
            return None

    def _count_structural_edits(self, original: str,
                                 modified: str) -> int:
        """Count structural differences between original and modified code."""
        if original == modified:
            return 0
        # Simple: count lines that differ
        orig_lines = set(original.splitlines())
        mod_lines = set(modified.splitlines())
        return len(orig_lines.symmetric_difference(mod_lines))

    @property
    def stagnation_count(self) -> int:
        return self._stagnation_count

    @property
    def injection_count(self) -> int:
        return self._stats["injections"]

    @property
    def stats(self) -> dict:
        return dict(self._stats)


# ===== 来自XYZ系统 =====
class PreReflection:
    """K8: Pre-action reflection engine.

    Similarity: TF-IDF weighted cosine similarity between actions.
    Consequences: Pattern-based risk scoring with context rules.
    Confidence: Beta(α, β) posterior updated with each outcome.
    """

    def __init__(self, config: ZConfig | None = None):
        self._config = config or ZConfig()
        self._action_history: list[dict] = []
        self._stats = {"reflections": 0, "actions_approved": 0,
                       "actions_delayed": 0, "actions_blocked": 0}

        # TF-IDF corpus: accumulate document frequencies
        self._doc_freq: dict[str, int] = defaultdict(int)  # word → # docs containing it
        self._doc_count: int = 0

        # Bayesian confidence: Beta(α_success, β_failure) prior
        self._alpha = 1.0  # pseudo-count of successes
        self._beta = 1.0   # pseudo-count of failures

    def reflect(self, action: str, context: dict | None = None) -> dict:
        """Reflect on a proposed action before executing it.

        Returns:
            Dict with "proceed" (bool), "confidence" (float), "warnings" (list).
        """
        self._stats["reflections"] += 1
        context = context or {}

        # 1. Find similar past actions via TF-IDF cosine
        similar = self._find_similar_actions_tfidf(action)
        past_failure_rate = self._compute_failure_rate(similar)

        # 2. Assess consequences via pattern-based risk scoring
        risk_score, warnings = self._assess_consequences_v2(action, context)

        # 3. Calibrate confidence via Bayesian posterior
        confidence = self._calibrate_confidence_bayesian(
            action, similar, past_failure_rate, risk_score
        )

        # Decision: combine Bayesian confidence with risk score
        proceed = True
        # High failure rate + high risk = blocked
        if past_failure_rate > 0.8 or (past_failure_rate > 0.5 and risk_score > 0.7):
            proceed = False
            self._stats["actions_blocked"] += 1
        elif past_failure_rate > 0.5 or confidence < 0.3 or risk_score > 0.8:
            proceed = False
            self._stats["actions_delayed"] += 1
        else:
            self._stats["actions_approved"] += 1

        result = {
            "action": action,
            "proceed": proceed,
            "confidence": confidence,
            "warnings": warnings,
            "past_failure_rate": past_failure_rate,
            "risk_score": risk_score,
            "similar_actions_found": len(similar),
        }

        return result

    def record_outcome(self, action: str, success: bool,
                       context: dict | None = None) -> None:
        """Record the outcome of an action for future reflection.

        Updates TF-IDF corpus and Bayesian posterior.
        """
        self._action_history.append({
            "action": action,
            "success": success,
            "context": context or {},
        })

        # Update TF-IDF document frequencies
        words = set(action.lower().split())
        for w in words:
            self._doc_freq[w] += 1
        self._doc_count += 1

        # Update Bayesian posterior (Beta distribution)
        if success:
            self._alpha += 1.0
        else:
            self._beta += 1.0

    # ── Failure rate computation ──────────────────────────────

    def _compute_failure_rate(self, similar: list[dict]) -> float:
        """Compute failure rate from similar past actions."""
        if not similar:
            return 0.3  # Default uncertainty
        failures = sum(1 for a in similar if not a["success"])
        return failures / len(similar)

    # ── TF-IDF Cosine Similarity ──────────────────────────────

    def _find_similar_actions_tfidf(self, action: str,
                                     limit: int = 5) -> list[dict]:
        """Find similar past actions using TF-IDF cosine similarity.

        More accurate than word overlap: downweights common words,
        upweights distinctive terms.
        """
        if not self._action_history or self._doc_count == 0:
            return []

        query_vec = self._tfidf_vector(action)
        scored = []
        for past in self._action_history:
            past_vec = self._tfidf_vector(past["action"])
            sim = self._cosine_similarity(query_vec, past_vec)
            if sim > 0.01:  # Minimal relevance threshold
                scored.append((sim, past))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scored[:limit]]

    def _tfidf_vector(self, text: str) -> dict[str, float]:
        """Compute TF-IDF vector for a text string."""
        words = text.lower().split()
        if not words:
            return {}

        # Term frequency
        tf: dict[str, float] = {}
        for w in words:
            tf[w] = tf.get(w, 0) + 1
        total = len(words)
        for w in tf:
            tf[w] /= total

        # IDF: log(N / df(w)), with smoothing for unseen words
        idf: dict[str, float] = {}
        for w in tf:
            df = self._doc_freq.get(w, 0) + 1  # +1 smoothing
            idf[w] = math.log((self._doc_count + 1) / df) + 1  # +1 to avoid 0

        # TF-IDF = tf × idf
        return {w: tf[w] * idf[w] for w in tf}

    @staticmethod
    def _cosine_similarity(a: dict[str, float],
                           b: dict[str, float]) -> float:
        """Cosine similarity between two sparse vectors."""
        if not a or not b:
            return 0.0

        # Dot product over shared keys
        dot = sum(a[k] * b[k] for k in a if k in b)

        # Magnitudes
        mag_a = math.sqrt(sum(v * v for v in a.values()))
        mag_b = math.sqrt(sum(v * v for v in b.values()))

        if mag_a == 0 or mag_b == 0:
            return 0.0

        return dot / (mag_a * mag_b)

    # ── Pattern-based Risk Assessment ─────────────────────────

    def _assess_consequences_v2(self, action: str,
                                 context: dict) -> tuple[float, list[str]]:
        """Assess consequences via pattern-based risk scoring.

        Returns (risk_score: 0-1, warnings: list[str]).

        Risk patterns (compound = higher risk):
        - destructive action (delete/remove/drop/reset/clear/overwrite/truncate/format)
        - scope keywords (all/every/entire/whole/*)
        - production context
        - no backup
        - irreversible markers (permanent/final/force)
        """
        warnings = []
        risk = 0.0
        action_lower = action.lower()

        # Pattern 1: Destructive actions (+0.3 base)
        destructive = ["delete", "remove", "drop", "reset", "clear",
                       "overwrite", "truncate", "format", "erase", "purge"]
        is_destructive = any(kw in action_lower for kw in destructive)
        if is_destructive:
            risk += 0.3
            warnings.append("Destructive action detected")

        # Pattern 2: Wide scope (+0.2)
        wide_scope = ["all", "every", "entire", "whole", "*", "everything"]
        has_wide_scope = any(kw in action_lower for kw in wide_scope)
        if has_wide_scope:
            risk += 0.2
            warnings.append("Wide scope detected (affects many items)")

        # Pattern 3: Irreversible markers (+0.2)
        irreversible = ["permanent", "final", "force", "irreversible", "hard"]
        is_irreversible = any(kw in action_lower for kw in irreversible)
        if is_irreversible:
            risk += 0.2
            warnings.append("Irreversible action marker detected")

        # Pattern 4: Production context (+0.15)
        is_production = context.get("production", False)
        if is_production:
            risk += 0.15
            warnings.append("Action targets production environment")

        # Pattern 5: No backup (+0.1)
        no_backup = context.get("no_backup", False)
        if no_backup:
            risk += 0.1
            warnings.append("No backup available")

        # Compound risk: destructive + production = extra dangerous
        if is_destructive and is_production:
            risk += 0.2
            warnings.append("⚠ CRITICAL: Destructive action in production")

        # Compound risk: destructive + wide scope = mass destruction
        if is_destructive and has_wide_scope:
            risk += 0.15
            warnings.append("⚠ CRITICAL: Mass destructive action")

        # Compound risk: irreversible + no backup = unrecoverable
        if is_irreversible and no_backup:
            risk += 0.15
            warnings.append("⚠ CRITICAL: Irreversible with no backup")

        return min(1.0, risk), warnings

    # ── Bayesian Confidence Calibration ───────────────────────

    def _calibrate_confidence_bayesian(self, action: str,
                                        similar: list[dict],
                                        failure_rate: float,
                                        risk_score: float) -> float:
        """Calibrate confidence using Bayesian posterior.

        Beta(α, β) distribution:
        - α = pseudo-successes + actual successes
        - β = pseudo-failures + actual failures
        - Posterior mean = α / (α + β)

        Adjusted by:
        - Similarity: more similar actions → more informative
        - Risk: higher risk → lower confidence
        """
        # Base confidence from Beta posterior mean
        posterior_mean = self._alpha / (self._alpha + self._beta)

        # Sample size bonus: more similar actions → more calibrated
        sample_size = len(similar)
        # Weighted average: lean toward posterior_mean with more samples
        if sample_size > 0:
            # Blending weight: 0.3 base + 0.7 * sample_bonus
            sample_weight = min(0.8, 0.3 + sample_size * 0.05)
            # Direct observation confidence
            observation_confidence = 1.0 - failure_rate
            confidence = sample_weight * observation_confidence + (1 - sample_weight) * posterior_mean
        else:
            confidence = posterior_mean

        # Risk adjustment: high risk → reduce confidence
        risk_penalty = risk_score * 0.3
        confidence = max(0.0, min(1.0, confidence - risk_penalty))

        return confidence

    @property
    def stats(self) -> dict:
        return dict(self._stats)

    @property
    def posterior(self) -> dict:
        """Current Bayesian posterior parameters."""
        return {"alpha": self._alpha, "beta": self._beta,
                "mean": self._alpha / (self._alpha + self._beta)}


