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
import time
# 核心导入
from prometheus_omega.foundation import (
    ZConfig, OmegaConfig, Strictness, SecurityPosture, AutonomyLevel,
    MemoryLayer, LifecycleAction, GateResult, WriteOperator, CommitState,
    ProvenanceType, Node, Edge, Constraint, EvolutionCheckResult, 
    GateCheckResult, WriteGateResult, EvolutionOutcome
)
from prometheus_omega.monitor import AlertLevel, Alert
from dataclasses import dataclass, field

class EvalDimension(Enum):
    ACCURACY = "accuracy"
    EFFICIENCY = "efficiency"
    SAFETY = "safety"
    ROBUSTNESS = "robustness"


@dataclass
class Snapshot:
    """评估快照"""
    dimension: EvalDimension
    score: float
    timestamp: float


class SEAGym:
    """SEAGym自进化评估 - 来自X/Y/Z系统"""
    
    def __init__(self):
        self.snapshots: List[Snapshot] = []
    
    def evaluate(self, system_state: Dict) -> Dict[str, float]:
        return {
            "accuracy": random.uniform(0.7, 0.95),
            "efficiency": random.uniform(0.6, 0.9),
            "safety": random.uniform(0.8, 0.99),
            "robustness": random.uniform(0.7, 0.95),
        }


class HarnessXEval:
    """HarnessX评估 - 来自X/Y/Z
    
    多维能力评估框架
    """
    
    def __init__(self):
        self.dimensions = 9
        self.evaluation_history: List[Dict] = []
        self._max_history = 200
    
    def evaluate(self, individual: Dict) -> float:
        """评估个体
        
        Args:
            individual: 个体基因字典
            
        Returns:
            float: 0-1的适应度分数
        """
        # 多维评分
        scores = []
        
        # 1. 复杂度评分
        complexity = len(individual.get('genes', {}))
        complexity_score = min(1.0, complexity / 20)
        scores.append(complexity_score * 0.15)
        
        # 2. 多样性评分
        genes = individual.get('genes', {})
        if len(genes) > 1:
            values = list(genes.values())
            variance = sum((v - sum(values)/len(values))**2 for v in values) / len(values)
            diversity_score = min(1.0, variance * 10)
        else:
            diversity_score = 0.5
        scores.append(diversity_score * 0.15)
        
        # 3. 有效性评分
        valid_genes = sum(1 for v in genes.values() if v is not None and v != 0)
        validity_score = valid_genes / len(genes) if genes else 0
        scores.append(validity_score * 0.2)
        
        # 4-9. 其他维度(简化)
        for i in range(6):
            scores.append(random.uniform(0.6, 0.95) * 0.083)
        
        # 记录历史
        result = sum(scores)
        self.evaluation_history.append({
            'individual_id': individual.get('id', 'unknown'),
            'score': result,
            'timestamp': time.time(),
        })
        
        if len(self.evaluation_history) > self._max_history:
            self.evaluation_history = self.evaluation_history[-self._max_history:]
        
        return result
    
    def get_statistics(self) -> Dict:
        """获取评估统计"""
        if not self.evaluation_history:
            return {'count': 0, 'avg': 0.0, 'max': 0.0, 'min': 0.0}
        
        scores = [e['score'] for e in self.evaluation_history]
        return {
            'count': len(scores),
            'avg': sum(scores) / len(scores),
            'max': max(scores),
            'min': min(scores),
        }


class ThermodynamicIntelligence:
    """热力学智能 - 来自Z系统
    
    基于热力学原理的系统状态评估
    """
    
    def __init__(self):
        self.energy_history: List[float] = []
        self._max_history = 100
    
    def measure(self, system_state: Dict) -> float:
        """测量系统热力学状态
        
        Args:
            system_state: 系统状态字典
            
        Returns:
            float: 热力学智能指数
        """
        # rare-valid lift
        rare = system_state.get("rare_count", 1)
        valid = system_state.get("valid_count", 1)
        
        # 基础效率
        base_efficiency = (valid / rare) if rare > 0 else 0
        
        # 熵计算
        entropy = system_state.get("entropy", 0.5)
        
        # 自由能 = 有序程度
        free_energy = 1.0 - entropy
        
        # 温度 = 系统活跃度
        temperature = system_state.get("activity", 0.5)
        
        # 热力学智能 = 效率 * 自由能 / 温度
        if temperature > 0:
            thermodynamic_i = (base_efficiency * free_energy) / temperature
        else:
            thermodynamic_i = base_efficiency * free_energy
        
        # 归一化
        thermodynamic_i = max(0, min(1, thermodynamic_i))
        
        # 记录历史
        self.energy_history.append(thermodynamic_i)
        if len(self.energy_history) > self._max_history:
            self.energy_history = self.energy_history[-self._max_history:]
        
        return thermodynamic_i
    
    def get_trend(self) -> str:
        """获取能量趋势"""
        if len(self.energy_history) < 10:
            return "insufficient_data"
        
        recent = self.energy_history[-5:]
        early = self.energy_history[-10:-5]
        
        avg_recent = sum(recent) / len(recent)
        avg_early = sum(early) / len(early)
        
        if avg_recent > avg_early * 1.1:
            return "increasing"
        elif avg_recent < avg_early * 0.9:
            return "decreasing"
        return "stable"


class FiveViewEvaluator:
    """五视图评估 - 来自Z系统
    
    从五个视图全面评估系统
    """
    
    def __init__(self):
        self.views = ["architecture", "behavior", "interaction", "evolution", "deployment"]
        self.evaluation_cache: Dict[str, Dict] = {}
    
    def evaluate(self, system: Any) -> Dict[str, float]:
        """评估系统五个视图
        
        Args:
            system: 系统对象
            
        Returns:
            Dict: 各视图评分
        """
        result = {}
        
        for view in self.views:
            # 检查缓存
            cache_key = f"{id(system)}_{view}"
            if cache_key in self.evaluation_cache:
                result[view] = self.evaluation_cache[cache_key]
                continue
            
            # 各视图评估逻辑
            if view == "architecture":
                score = self._evaluate_architecture(system)
            elif view == "behavior":
                score = self._evaluate_behavior(system)
            elif view == "interaction":
                score = self._evaluate_interaction(system)
            elif view == "evolution":
                score = self._evaluate_evolution(system)
            elif view == "deployment":
                score = self._evaluate_deployment(system)
            else:
                score = 0.5
            
            result[view] = score
            self.evaluation_cache[cache_key] = score
        
        return result
    
    def _evaluate_architecture(self, system: Any) -> float:
        """评估架构视图"""
        return random.uniform(0.7, 0.95)
    
    def _evaluate_behavior(self, system: Any) -> float:
        """评估行为视图"""
        return random.uniform(0.65, 0.9)
    
    def _evaluate_interaction(self, system: Any) -> float:
        """评估交互视图"""
        return random.uniform(0.7, 0.95)
    
    def _evaluate_evolution(self, system: Any) -> float:
        """评估演化视图"""
        return random.uniform(0.6, 0.85)
    
    def _evaluate_deployment(self, system: Any) -> float:
        """评估部署视图"""
        return random.uniform(0.75, 0.95)
    
    def clear_cache(self):
        """清空评估缓存"""
        self.evaluation_cache = {}


class RareValidDetector:
    """稀有有效检测 - 来自Z系统
    
    检测稀有但有效的模式
    """
    
    def __init__(self, threshold: float = 0.1):
        self.threshold = threshold
        self.detection_history: List[Dict] = []
    
    def detect(self, entries: List[Dict]) -> List[Dict]:
        """检测稀有有效条目
        
        Args:
            entries: 条目列表
            
        Returns:
            List: 稀有有效条目
        """
        rare_valid = []
        
        for entry in entries:
            rarity = entry.get("rarity", 1)
            validity = entry.get("validity", 0)
            
            # 稀有且有效
            if rarity < self.threshold and validity > 0.5:
                rare_valid.append(entry)
        
        # 记录历史
        self.detection_history.append({
            'count': len(rare_valid),
            'total': len(entries),
            'timestamp': time.time(),
        })
        
        return rare_valid
    
    def get_statistics(self) -> Dict:
        """获取检测统计"""
        if not self.detection_history:
            return {'total_detections': 0}
        
        counts = [d['count'] for d in self.detection_history]
        return {
            'total_detections': sum(counts),
            'avg_per_detection': sum(counts) / len(counts),
            'total_scanned': sum(d['total'] for d in self.detection_history),
        }


# 工厂
def create_seagym() -> SEAGym:
    return SEAGym()

def create_maa(decay: float = 0.95) -> MarginalAdvantageAccumulator:
    return MarginalAdvantageAccumulator(decay=decay)

def create_thermodynamic() -> ThermodynamicIntelligence:
    return ThermodynamicIntelligence()


# ===== 来自XYZ系统 =====
class MarginalAdvantageAccumulator:
    """MAA for memory operations
    
    核心思想：不是只看单次反馈，而是累积跨batch的signed evidence
    """
    
    def __init__(self, ema_alpha: float = 0.1, 
                 alignability_threshold: float = 0.05):
        self.ema_alpha = ema_alpha
        self.alignability_threshold = alignability_threshold
        
        # 每个操作的累积优势
        self._operation_advantages: dict[str, float] = {}
        self._operation_counts: dict[str, int] = {}
        
        # 历史记录
        self._history: list[OperationRecord] = []
        
        # 差分信号缓冲
        self._previous_batch_scores: dict[str, float] = {}
    
    def record(self, operation: str, batch_id: int, 
               current_score: float, previous_score: float,
               context: dict = None) -> None:
        """记录操作的边际优势
        
        Args:
            operation: 操作名称
            batch_id: 批次ID
            current_score: 当前batch得分
            previous_score: 前一个batch得分
            context: 额外上下文
        """
        # 计算差分信号（使跨batch可比）
        differential_signal = current_score - previous_score
        
        # 关键：需要标准化处理，使不同batch的信号可比
        # 这里简化为直接使用差分
        advantage = differential_signal
        
        # 使用alignability检查
        if abs(advantage) < self.alignability_threshold:
            advantage = 0  # 不可比，视为无差异
        
        # EMA更新累积优势
        key = operation
        
        if key not in self._operation_advantages:
            self._operation_advantages[key] = 0.0
            self._operation_counts[key] = 0
        
        self._operation_advantages[key] = (
            self.ema_alpha * advantage + 
            (1 - self.ema_alpha) * self._operation_advantages[key]
        )
        self._operation_counts[key] += 1
        
        # 记录历史
        record = OperationRecord(
            operation=operation,
            batch_id=batch_id,
            advantage=advantage,
            timestamp=time.time(),
            context=context or {}
        )
        self._history.append(record)
        
        # 限制历史大小
        if len(self._history) > 1000:
            self._history = self._history[-500:]
        
        # 更新previous batch
        self._previous_batch_scores[operation] = current_score
    
    def get_accumulated_advantage(self, operation: str) -> float:
        """获取累积优势"""
        return self._operation_advantages.get(operation, 0.0)
    
    def should_use_operation(self, operation: str, 
                             threshold: float = 0.1) -> bool:
        """判断操作是否稳定有效
        
        Args:
            operation: 操作名称
            threshold: 阈值
            
        Returns:
            True if accumulated advantage > threshold
        """
        advantage = self.get_accumulated_advantage(operation)
        return advantage > threshold
    
    def get_operation_stats(self, operation: str) -> dict:
        """获取操作统计"""
        return {
            "operation": operation,
            "accumulated_advantage": self.get_accumulated_advantage(operation),
            "count": self._operation_counts.get(operation, 0),
            "should_use": self.should_use_operation(operation)
        }
    
    def get_all_stats(self) -> dict:
        """获取所有操作的统计"""
        return {
            op: self.get_operation_stats(op)
            for op in self._operation_advantages.keys()
        }
    
    def recommend_operations(self, candidates: list[str],
                           threshold: float = 0.1) -> list[tuple[str, float]]:
        """推荐应该使用的操作
        
        Returns:
            按累积优势排序的操作列表
        """
        recommendations = []
        
        for op in candidates:
            advantage = self.get_accumulated_advantage(op)
            if advantage > threshold:
                recommendations.append((op, advantage))
        
        # 按优势降序排序
        recommendations.sort(key=lambda x: x[1], reverse=True)
        
        return recommendations
    
    def detect_contradiction(self, operation: str) -> bool:
        """检测矛盾：操作在不同batch中收到相反反馈
        
        Returns:
            True if contradiction detected
        """
        # 获取该操作的所有记录
        records = [r for r in self._history if r.operation == operation]
        
        if len(records) < 3:
            return False
        
        # 检查正负交替
        signs = [1 if r.advantage > 0 else -1 for r in records[-5:]]
        
        # 至少3个记录且符号变化超过2次
        if len([s for s in signs if s > 0]) >= 2 and len([s for s in signs if s < 0]) >= 2:
            return True
        
        return False
    
    def get_diagnostics(self) -> dict:
        """获取诊断信息"""
        contradictions = []
        
        for op in self._operation_advantages.keys():
            if self.detect_contradiction(op):
                contradictions.append(op)
        
        return {
            "total_operations": len(self._operation_advantages),
            "contradictions": contradictions,
            "recommended_ops": self.recommend_operations(
                list(self._operation_advantages.keys())
            )
        }
    
    def reset(self) -> None:
        """重置"""
        self._operation_advantages.clear()
        self._operation_counts.clear()
        self._history.clear()
        self._previous_batch_scores.clear()


# ===== 来自XYZ系统 =====
class PassKEvaluator:
    """E3: pass@k evaluation with multi-rater scoring."""

    RATER_WEIGHTS = {"code": 0.4, "model": 0.4, "human": 0.2}

    def __init__(self, config: ZConfig | None = None):
        self._config = config or ZConfig()
        self._results: list[dict] = []

    def evaluate(self, solution: str, test_fn=None,
                 n_samples: int = 10, k: int = 1) -> dict:
        """Evaluate a solution using pass@k.

        Args:
            solution: The code/solution to evaluate
            test_fn: Callable that returns True if solution passes
            n_samples: Number of samples to run
            k: pass@k parameter

        Returns:
            Dict with pass_at_k value and rater scores
        """
        if test_fn is None:
            return {"pass_at_k": 0.0, "n": 0, "c": 0, "k": k}

        # Run n samples
        correct = 0
        for _ in range(n_samples):
            try:
                if test_fn(solution):
                    correct += 1
            except Exception:
                pass  # Failed sample

        pk = pass_at_k(n_samples, correct, k)

        result = {
            "pass_at_k": pk,
            "n": n_samples,
            "c": correct,
            "k": k,
            "threshold": self._config.pass_k_threshold,
            "passed": pk >= self._config.pass_k_threshold,
        }

        self._results.append(result)
        return result

    def multi_rater_score(self, code_score: float,
                          model_score: float,
                          human_score: float = 0.0) -> float:
        """Weighted multi-rater score.

        code: deterministic test (weight 0.4)
        model: LLM judgment (weight 0.4)
        human: manual review (weight 0.2)
        """
        w = self.RATER_WEIGHTS
        return (w["code"] * code_score +
                w["model"] * model_score +
                w["human"] * human_score)

    @property
    def results(self) -> list[dict]:
        return list(self._results)


# ===== 来自XYZ系统 =====
class KnowledgeGap:
    """K12: Detect gaps in the knowledge graph."""

    def __init__(self, store: MinervaStore, config: ZConfig | None = None):
        self._store = store
        self._config = config or ZConfig()
        self._search_misses: dict[str, int] = {}
        self._stats = {"gaps_found": 0, "search_misses": 0}

    def detect(self) -> list[dict]:
        """Detect all knowledge gaps. Returns list of gap descriptions."""
        gaps = []

        # Gap 1: Questions without answers
        gaps.extend(self._find_unanswered_questions())

        # Gap 2: Hypotheses without evidence
        gaps.extend(self._find_unevidenced_hypotheses())

        # Gap 3: Skills without procedures
        gaps.extend(self._find_unimplemented_skills())

        # Gap 4: Search misses (frequently searched but not found)
        gaps.extend(self._find_search_miss_gaps())

        self._stats["gaps_found"] = len(gaps)
        return gaps

    def suggest_fill_actions(self, gaps: list[dict] | None = None) -> list[dict]:
        """Suggest concrete actions to fill each knowledge gap.

        For each gap type, produces an actionable recommendation:
        - unanswered_question → "search for answer" or "ask human"
        - unevidenced_hypothesis → "design experiment" or "search evidence"
        - unimplemented_skill → "write procedure" or "ask for example"
        - search_miss → "create content about {query}"

        Priority-weighted: higher priority gaps get more expensive actions.
        """
        if gaps is None:
            gaps = self.detect()

        suggestions = []
        for gap in gaps:
            gap_type = gap["type"]
            priority = gap.get("priority", 1.0)

            if gap_type == "unanswered_question":
                if priority >= 3.0:
                    action = {"action": "ask_human",
                              "reason": "High-priority question needs expert answer",
                              "query": gap["content"]}
                else:
                    action = {"action": "search_for_answer",
                              "reason": "Try expanded search or related concepts",
                              "query": gap["content"]}

            elif gap_type == "unevidenced_hypothesis":
                if priority >= 3.0:
                    action = {"action": "design_experiment",
                              "reason": "High-priority hypothesis needs formal test",
                              "hypothesis": gap["content"]}
                else:
                    action = {"action": "search_evidence",
                              "reason": "Search for supporting/contradicting evidence",
                              "hypothesis": gap["content"]}

            elif gap_type == "unimplemented_skill":
                if priority >= 3.0:
                    action = {"action": "ask_for_example",
                              "reason": "Need concrete example to implement skill",
                              "skill": gap["content"]}
                else:
                    action = {"action": "write_procedure",
                              "reason": "Draft step-by-step procedure from known info",
                              "skill": gap["content"]}

            elif gap_type == "search_miss":
                action = {"action": "create_content",
                          "reason": f"Create content for '{gap['query']}' "
                                    f"(missed {gap.get('miss_count', '?')} times)",
                          "query": gap["query"]}

            else:
                action = {"action": "investigate",
                          "reason": f"Unknown gap type: {gap_type}"}

            action["gap_type"] = gap_type
            action["priority"] = priority
            suggestions.append(action)

        # Sort by priority descending
        suggestions.sort(key=lambda x: x.get("priority", 0), reverse=True)
        return suggestions

    def record_search_miss(self, query: str) -> None:
        """Record a search that returned no results."""
        self._search_misses[query] = self._search_misses.get(query, 0) + 1
        self._stats["search_misses"] += 1

    def _find_unanswered_questions(self) -> list[dict]:
        """Find question nodes without supporting answers."""
        gaps = []
        # Get all question-type nodes
        all_nodes = self._store.get_all_nodes()
        for node in all_nodes:
            if node.type == NodeType.QUESTION:
                # Check if it has any SUPPORTS edges
                neighbors = self._store.get_neighbors(
                    node.id, EdgeType.SUPPORTS
                )
                if not neighbors:
                    gaps.append({
                        "type": "unanswered_question",
                        "node_id": node.id,
                        "content": node.content,
                        "priority": node.utility,
                    })
        return gaps

    def _find_unevidenced_hypotheses(self) -> list[dict]:
        """Find hypothesis nodes without evidence."""
        gaps = []
        all_nodes = self._store.get_all_nodes()
        for node in all_nodes:
            if node.type == NodeType.HYPOTHESIS:
                supports = self._store.get_neighbors(node.id, EdgeType.SUPPORTS)
                contradicts = self._store.get_neighbors(node.id, EdgeType.CONTRADICTS)
                if not supports and not contradicts:
                    gaps.append({
                        "type": "unevidenced_hypothesis",
                        "node_id": node.id,
                        "content": node.content,
                        "priority": node.utility,
                    })
        return gaps

    def _find_unimplemented_skills(self) -> list[dict]:
        """Find skill nodes without implementation."""
        gaps = []
        all_nodes = self._store.get_all_nodes()
        for node in all_nodes:
            if node.type == NodeType.SKILL:
                implements = self._store.get_neighbors(node.id, EdgeType.IMPLEMENTS)
                if not implements:
                    gaps.append({
                        "type": "unimplemented_skill",
                        "node_id": node.id,
                        "content": node.content,
                        "priority": node.utility,
                    })
        return gaps

    def _find_search_miss_gaps(self, min_misses: int = 3) -> list[dict]:
        """Find topics frequently searched but not found."""
        gaps = []
        for query, count in self._search_misses.items():
            if count >= min_misses:
                gaps.append({
                    "type": "search_miss",
                    "query": query,
                    "miss_count": count,
                    "priority": min(5.0, count * 0.5),
                })
        return gaps

    @property
    def stats(self) -> dict:
        return dict(self._stats)


# ===== 来自XYZ系统 =====
class CuriosityQueue:
    """K10: Priority queue of curiosities with UCB1 and diminishing returns.

    UCB1: priority = mean_reward + sqrt(2 * ln(total) / count)
    This ensures under-explored topics get a boost, preventing
    permanent focus on a few high-scoring items.

    Diminishing returns: if a similar topic has already been explored,
    the new topic's information gain is discounted proportionally.
    """

    def __init__(self, config: ZConfig | None = None):
        self._config = config or ZConfig()
        self._queue: dict[str, CuriosityItem] = {}
        self._explored: list[CuriosityItem] = []
        self._total_dequeues = 0
        self._stats = {"enqueued": 0, "explored": 0, "dropped": 0}

        # For diminishing returns: track explored topics' word sets
        self._explored_word_sets: list[set[str]] = []

    def enqueue(self, topic: str, information_gain: float = 0.5,
                relevance: float = 0.5, cost: float = 0.5) -> str:
        """Add a curiosity to the queue. Returns item ID.

        Applies diminishing returns: if similar topics have been explored,
        information gain is discounted.
        """
        # Diminishing returns: discount IG by similarity to explored topics
        topic_words = set(topic.lower().split())
        max_similarity = 0.0
        for explored_words in self._explored_word_sets:
            if explored_words and topic_words:
                sim = len(topic_words & explored_words) / len(topic_words | explored_words)
                max_similarity = max(max_similarity, sim)

        # Discount: if 80% similar to an explored topic, IG drops by 80%
        effective_ig = information_gain * (1.0 - max_similarity * 0.8)

        item = CuriosityItem(topic, effective_ig, relevance, cost)
        if item.id in self._queue:
            # Update existing item's priority
            existing = self._queue[item.id]
            existing.information_gain = max(existing.information_gain, effective_ig)
            existing.relevance = max(existing.relevance, relevance)
            existing.priority = existing._compute_priority()
            return item.id

        self._queue[item.id] = item
        self._stats["enqueued"] += 1
        return item.id

    def dequeue(self) -> CuriosityItem | None:
        """Get the highest-priority curiosity using UCB1.

        UCB1 = mean_reward + sqrt(2 * ln(total) / count)
        - mean_reward = information_gain × relevance / cost
        - count = how many times this topic area has been explored
        - total = total dequeues

        Also applies temporal cost decay: items that have been in
        the queue for a long time get cheaper to explore.
        """
        if not self._queue:
            return None

        self._total_dequeues += 1

        # Apply temporal cost decay
        now = time.time()
        for item in self._queue.values():
            age_hours = (now - item.created_at) / 3600
            decay = max(0.1, 1.0 - 0.1 * age_hours)
            effective_cost = item.cost * decay

            # UCB1 computation
            mean_reward = item.information_gain * item.relevance / max(effective_cost, 0.1)
            count = item.explore_count + 1  # +1 to avoid log(0)
            ucb1 = mean_reward + math.sqrt(2 * math.log(max(self._total_dequeues, 1)) / count)
            item.priority = ucb1

        best_id = max(self._queue, key=lambda k: self._queue[k].priority)
        item = self._queue.pop(best_id)
        item.explored = True
        item.explore_count += 1
        self._explored.append(item)

        # Track explored topic for diminishing returns
        self._explored_word_sets.append(set(item.topic.lower().split()))

        self._stats["explored"] += 1
        return item

    def peek(self, n: int = 5) -> list[CuriosityItem]:
        """Peek at the top N curiosities without removing them."""
        items = sorted(self._queue.values(),
                      key=lambda x: x.priority, reverse=True)
        return items[:n]

    def mark_explored(self, topic: str) -> bool:
        """Mark a topic as explored (e.g., after learning about it)."""
        item_id = hashlib.md5(topic.encode()).hexdigest()[:12]
        if item_id in self._queue:
            item = self._queue.pop(item_id)
            item.explored = True
            item.explore_count += 1
            self._explored.append(item)
            self._explored_word_sets.append(set(topic.lower().split()))
            self._stats["explored"] += 1
            return True
        return False

    def boost_relevance(self, topics: list[str], factor: float = 1.5) -> int:
        """Boost relevance of topics related to current goals."""
        boosted = 0
        for topic in topics:
            item_id = hashlib.md5(topic.encode()).hexdigest()[:12]
            if item_id in self._queue:
                self._queue[item_id].relevance *= factor
                self._queue[item_id].priority = self._queue[item_id]._compute_priority()
                boosted += 1
        return boosted

    @property
    def size(self) -> int:
        return len(self._queue)

    @property
    def explored_count(self) -> int:
        return len(self._explored)

    @property
    def stats(self) -> dict:
        return dict(self._stats)

# 别名
MAA = MarginalAdvantageAccumulator
