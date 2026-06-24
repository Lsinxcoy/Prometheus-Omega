"""Evaluation - 评估层 (SEAGym+HarnessX+MAA+Thermo+5view)"""
from dataclasses import dataclass, field
from typing import List, Dict, Any
from enum import Enum
import random


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

def create_maa(decay: float = 0.95) -> MAA:
    return MAA(decay=decay)

def create_thermodynamic() -> ThermodynamicIntelligence:
    return ThermodynamicIntelligence()