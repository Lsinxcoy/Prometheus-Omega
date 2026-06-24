# 基础导入
from __future__ import annotations
import sys, os, re, json, time, datetime
from typing import Dict, List, Any, Optional, Callable, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum, IntEnum, auto


"""L6 Organs - 器官层 (5-organ pipeline + ToolLoop)"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
import uuid


class OrganType(Enum):
    TAOTIE = "taotie"     # 欲望/需求
    NUWA = "nuwa"         # 创造/生成
    DARWIN = "darwin"     # 进化/选择
    POOL = "pool"         # 资源池
    GUARD = "guard"       # 守护/安全


@dataclass
class OrganResult:
    """器官执行结果"""
    organ: OrganType
    success: bool
    output: Any = None
    metadata: Dict = field(default_factory=dict)
    
    def is_successful(self) -> bool:
        return self.success
    
    def get_output_or_default(self, default: Any = None) -> Any:
        return self.output if self.output is not None else default
    
    def to_dict(self) -> Dict:
        return {
            'organ': self.organ_type.value if isinstance(self.organ_type, Enum) else self.organ_type,
            'success': self.success,
            'output': self.output,
            'metadata': self.metadata,
        }


class BaseOrgan:
    """12-Factor基础器官"""
    def __init__(self, organ_type: OrganType):
        self.organ_type = organ_type
        self.execution_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.last_execution_time: Optional[float] = None
    
    def execute(self, input_data: Any) -> OrganResult:
        self.execution_count += 1
        self.last_execution_time = __import__('time').time()
        return OrganResult(organ=self.organ_type, success=True)
    
    def get_statistics(self) -> Dict:
        return {
            'organ_type': self.organ_type.value if isinstance(self.organ_type, Enum) else self.organ_type,
            'total_executions': self.execution_count,
            'successes': self.success_count,
            'failures': self.failure_count,
            'success_rate': self.success_count / max(1, self.execution_count),
        }
    
    def reset_statistics(self):
        self.execution_count = 0
        self.success_count = 0
        self.failure_count = 0


class DNAExtractor:
    """DNA提取器"""
    def __init__(self):
        self.extraction_history: List[Dict] = []
    
    def extract(self, individual: Any) -> Dict[str, Any]:
        result = {
            "features": self._extract_features(individual),
            "genotype": self._encode_genotype(individual),
            "phenotype": self._extract_phenotype(individual),
        }
        
        self.extraction_history.append({
            'individual_id': getattr(individual, 'id', 'unknown'),
            'timestamp': __import__('time').time(),
        })
        
        return result
    
    def _extract_features(self, individual: Any) -> List[str]:
        if hasattr(individual, 'genes'):
            return list(individual.genes.keys())
        return ["feature1", "feature2"]
    
    def _encode_genotype(self, individual: Any) -> str:
        if hasattr(individual, 'genes'):
            genes = individual.genes
            return ''.join('1' if v > 0.5 else '0' for v in genes.values())
        return "10101"
    
    def _extract_phenotype(self, individual: Any) -> Dict:
        if hasattr(individual, 'genes'):
            return {k: float(v) for k, v in individual.genes.items()}
        return {"attr1": 0.8}
    
    def get_history_size(self) -> int:
        return len(self.extraction_history)


class PromotionManifest:
    """晋升清单
    
    控制个体从候选池晋升到正式池的决策
    """
    def __init__(self, safety_threshold: float = 0.7):
        self.safety_threshold = safety_threshold
        self.promotion_history: List[Dict] = []
        self.rejection_history: List[Dict] = []
    
    def can_promote(self, safety_score: float, fitness: float) -> bool:
        return safety_score >= self.safety_threshold and fitness > 0.5
    
    def evaluate(self, candidate: Dict) -> Dict:
        """评估候选个体是否可晋升"""
        safety_score = candidate.get('safety_score', 0.0)
        fitness = candidate.get('fitness', 0.0)
        
        can = self.can_promote(safety_score, fitness)
        
        result = {
            'candidate_id': candidate.get('id', 'unknown'),
            'safety_score': safety_score,
            'fitness': fitness,
            'can_promote': can,
            'reason': self._get_reason(safety_score, fitness, can),
        }
        
        if can:
            self.promotion_history.append(result)
        else:
            self.rejection_history.append(result)
        
        return result
    
    def _get_reason(self, safety: float, fitness: float, can: bool) -> str:
        if can:
            return "All checks passed"
        if safety < self.safety_threshold:
            return f"Safety score {safety:.2f} below threshold {self.safety_threshold}"
        if fitness <= 0.5:
            return f"Fitness {fitness:.2f} too low"
        return "Unknown"
    
    def get_promotion_rate(self) -> float:
        total = len(self.promotion_history) + len(self.rejection_history)
        return len(self.promotion_history) / max(1, total)
    
    def get_statistics(self) -> Dict:
        return {
            'promoted': len(self.promotion_history),
            'rejected': len(self.rejection_history),
            'promotion_rate': self.get_promotion_rate(),
            'safety_threshold': self.safety_threshold,
        }


class ToolLoop:
    """工具调用推理循环"""

    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.history: List[Dict] = []
        self.max_iterations = 10
    
    def register_tool(self, name: str, func: Callable):
        self.tools[name] = func
    
    def reason(self, query: str, memory=None) -> List[Dict]:
        """推理循环"""
        plan = []
        
        # 5工具推理
        for tool_name in ["read", "search", "execute", "compute", "remember"]:
            if tool_name in self.tools:
                plan.append({"tool": tool_name, "status": "planned"})
        
        self.history.append({'query': query, 'plan': plan})
        return plan
    
    def execute_loop(self, query: str, memory=None) -> List[Dict]:
        """执行完整工具循环"""
        results = []
        plan = self.reason(query, memory)
        
        for step in plan:
            tool_name = step['tool']
            if tool_name in self.tools:
                try:
                    output = self.tools[tool_name](query)
                    results.append({'tool': tool_name, 'status': 'success', 'output': output})
                except Exception as e:
                    results.append({'tool': tool_name, 'status': 'error', 'error': str(e)})
            else:
                results.append({'tool': tool_name, 'status': 'unavailable'})
        
        self.history.append({'query': query, 'results': results})
        return results
    
    def get_tool_names(self) -> List[str]:
        return list(self.tools.keys())
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        return self.history[-limit:]


class FiveOrganPipeline:
    """5器官流水线 - 来自X/CIP系统#29"""
    
    def __init__(self):
        self.taotie = BaseOrgan(OrganType.TAOTIE)
        self.nuwa = BaseOrgan(OrganType.NUWA)
        self.darwin = BaseOrgan(OrganType.DARWIN)
        self.pool = BaseOrgan(OrganType.POOL)
        self.guard = BaseOrgan(OrganType.GUARD)
    
    def process(self, input_data: Any) -> List[OrganResult]:
        results = []
        # Taotie: 需求识别
        results.append(self.taotie.execute(input_data))
        # Nuwa: 方案生成
        results.append(self.nuwa.execute(input_data))
        # Darwin: 评估选择
        results.append(self.darwin.execute(input_data))
        # Pool: 资源分配
        results.append(self.pool.execute(input_data))
        # Guard: 安全检查
        results.append(self.guard.execute(input_data))
        return results


# 工厂
def create_five_organ_pipeline() -> FiveOrganPipeline:
    return FiveOrganPipeline()

def create_tool_loop() -> ToolLoop:
    return ToolLoop()