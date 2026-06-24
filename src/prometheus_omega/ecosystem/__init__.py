"""L11 Ecosystem - 生态层 (Lotka-Volterra+EDRE+HarnessX)"""
from dataclasses import dataclass, field
from typing import List, Dict
import math, random


@dataclass
class Species:
    """物种 - 用于生态模拟"""
    name: str
    population: float
    growth_rate: float
    capacity: float
    
    def population_growth(self, dt: float = 1.0) -> float:
        """计算种群增长 (逻辑斯蒂)"""
        # dP/dt = r*P*(1 - P/K)
        r = self.growth_rate
        P = self.population
        K = self.capacity
        return r * P * (1 - P / K) * dt
    
    def update(self, dt: float = 1.0):
        """更新种群数量"""
        self.population += self.population_growth(dt)
        self.population = max(0, min(self.population, self.capacity))
    
    def is_extinct(self) -> bool:
        """检查是否灭绝"""
        return self.population < 1.0
    
    def density(self) -> float:
        """计算种群密度"""
        return self.population / self.capacity if self.capacity > 0 else 0


class LotkaVolterra:
    """Lotka-Volterra技能动态 - 来自X系统#50
    
    生态竞争模型
    """
    
    def __init__(self):
        self.species: Dict[str, Species] = {}
    
    def add_species(self, name: str, initial_pop: float, 
                   growth: float, capacity: float):
        self.species[name] = Species(name, initial_pop, growth, capacity)
    
    def simulate(self, dt: float = 0.1) -> Dict[str, float]:
        results = {}
        for name, sp in self.species.items():
            # dN/dt = r*N*(1 - N/K)
            dN = sp.growth_rate * sp.population * (1 - sp.population / sp.capacity)
            sp.population += dN * dt
            results[name] = max(0, sp.population)
        return results


class EDRE:
    """EDRE均衡 - 来自X系统#51
    
    Lyapunov + ε-Nash 均衡
    """
    
    def __init__(self, epsilon: float = 0.1):
        self.epsilon = epsilon
        self.equilibria: List[Dict] = []
    
    def find_equilibrium(self, agents: List[Dict]) -> bool:
        # 简化: 检查是否接近均衡
        if len(agents) < 2:
            return True
        
        strategies = [a.get("strategy", 0) for a in agents]
        avg = sum(strategies) / len(strategies)
        
        for s in strategies:
            if abs(s - avg) > self.epsilon:
                return False
        
        self.equilibria.append({"strategies": strategies, "stable": True})
        return True


class SpeculativeFork:
    """推测性分支 - 来自X/Y系统#52"""
    
    def __init__(self):
        self.forks: List[Dict] = []
    
    def fork(self, system_state: Dict) -> Dict:
        fork_state = {
            "id": f"fork_{len(self.forks)}",
            "parent_state": system_state.copy(),
            "branch_state": system_state.copy(),
            "status": "speculating"
        }
        self.forks.append(fork_state)
        return fork_state


class HarnessX:
    """HarnessX 9维+8钩子 - 来自X/Y/Z系统#53
    
    综合进化引擎
    """
    
    def __init__(self):
        self.dimensions = 9
        self.hooks = 8
        self.metrics: Dict[str, float] = {}
    
    def evaluate(self, individual: Dict) -> float:
        # 9维评估
        scores = [
            individual.get("accuracy", 0.5),
            individual.get("efficiency", 0.5),
            individual.get("safety", 0.5),
            individual.get("robustness", 0.5),
            individual.get("explainability", 0.5),
            individual.get("fairness", 0.5),
            individual.get("privacy", 0.5),
            individual.get("reliability", 0.5),
            individual.get("usability", 0.5),
        ]
        return sum(scores) / len(scores)
    
    def hook(self, hook_name: str, func: callable):
        setattr(self, f"hook_{hook_name}", func)


class ToolFitnessPredictor:
    """工具适应性预测 - 来自X系统#54
    
    基于历史表现和环境上下文预测工具适应性
    """
    
    def __init__(self):
        self.model = None
        self.history: List[Dict] = []
        self._max_history = 500
    
    def predict(self, tool: Dict, context: Dict) -> float:
        """预测工具适应性
        
        Args:
            tool: 工具信息
            context: 上下文信息
            
        Returns:
            float: 0-1的适应性分数
        """
        # 简化预测模型
        base_score = tool.get('success_rate', 0.5)
        
        # 上下文调整
        context_match = 0.0
        if 'required_skills' in tool and 'skills' in context:
            required = set(tool['required_skills'])
            available = set(context['skills'])
            if required:
                context_match = len(required & available) / len(required)
        
        # 时间衰减因子
        recency = 1.0
        if self.history:
            last_used = self.history[-1].get('timestamp', 0)
            import time
            age = time.time() - last_used
            recency = max(0.5, 1.0 - age / (86400 * 7))  # 一周衰减50%
        
        # 综合分数
        score = (base_score * 0.5 + context_match * 0.3 + recency * 0.2)
        
        # 记录预测
        self.history.append({
            'tool_id': tool.get('id', 'unknown'),
            'score': score,
            'timestamp': time.time(),
        })
        
        if len(self.history) > self._max_history:
            self.history = self.history[-self._max_history:]
        
        return score
    
    def get_tool_stats(self, tool_id: str) -> Dict:
        """获取工具统计"""
        tool_history = [h for h in self.history if h.get('tool_id') == tool_id]
        if not tool_history:
            return {'count': 0, 'avg_score': 0.0}
        
        scores = [h['score'] for h in tool_history]
        return {
            'count': len(scores),
            'avg_score': sum(scores) / len(scores),
            'latest_score': scores[-1],
        }


class FGGM:
    """FGGM版本控制 - 来自X系统#56
    
    基于FGGM的智能体状态版本控制
    """
    
    def __init__(self):
        self.versions: List[Dict] = []
        self.current_version = 0
        self.branches: Dict[str, int] = {'main': 0}
        self._max_versions = 100
    
    def commit(self, state: Dict, message: str = "") -> str:
        """提交新版本
        
        Args:
            state: 状态字典
            message: 提交信息
            
        Returns:
            str: 版本ID
        """
        import time
        ver_id = f"v{self.current_version}_{int(time.time())}"
        
        self.versions.append({
            "id": ver_id,
            "state": state.copy(),
            "message": message,
            "timestamp": time.time(),
            "branch": 'main',
        })
        
        self.current_version += 1
        self.branches['main'] = self.current_version - 1
        
        # 限制版本数量
        if len(self.versions) > self._max_versions:
            self.versions = self.versions[-self._max_versions:]
        
        return ver_id
    
    def checkout(self, version: int) -> Dict:
        """检出指定版本"""
        if 0 <= version < len(self.versions):
            self.current_version = version
            return self.versions[version]["state"]
        return {}
    
    def diff(self, v1: int, v2: int) -> Dict:
        """比较两个版本"""
        if v1 >= len(self.versions) or v2 >= len(self.versions):
            return {}
        
        state1 = self.versions[v1]["state"]
        state2 = self.versions[v2]["state"]
        
        all_keys = set(state1.keys()) | set(state2.keys())
        changes = {}
        
        for key in all_keys:
            if key not in state1:
                changes[key] = {'status': 'added', 'value': state2[key]}
            elif key not in state2:
                changes[key] = {'status': 'removed', 'value': state1[key]}
            elif state1[key] != state2[key]:
                changes[key] = {'status': 'modified', 'old': state1[key], 'new': state2[key]}
        
        return changes
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """获取版本历史"""
        return self.versions[-limit:]
    
    def branch(self, name: str) -> str:
        """创建分支"""
        if name in self.branches:
            return f"Branch {name} already exists"
        
        self.branches[name] = self.current_version
        return f"Created branch {name} at version {self.current_version}"
    
    def log(self, version: int) -> Optional[Dict]:
        """查看版本详情"""
        if 0 <= version < len(self.versions):
            return self.versions[version]
        return None


class ExperienceRecall:
    """经验轨迹记忆 - 来自X系统#58
    
    记录和回放智能体的经验轨迹
    """
    
    def __init__(self):
        self.trajectories: List[List[Dict]] = []
        self.max_trajectories = 100
        self.max_steps = 1000
    
    def create_trajectory(self) -> int:
        """创建新轨迹"""
        trajectory_id = len(self.trajectories)
        self.trajectories.append([])
        
        # 限制轨迹数量
        if len(self.trajectories) > self.max_trajectories:
            self.trajectories.pop(0)
        
        return trajectory_id
    
    def add_step(self, trajectory_id: int, step: Dict):
        """添加步骤到轨迹"""
        if trajectory_id < 0:
            trajectory_id = len(self.trajectories) - 1
        
        if trajectory_id >= len(self.trajectories):
            trajectory_id = self.create_trajectory()
        
        # 添加时间戳
        import time
        step['timestamp'] = step.get('timestamp', time.time())
        
        self.trajectories[trajectory_id].append(step)
        
        # 限制每条轨迹长度
        if len(self.trajectories[trajectory_id]) > self.max_steps:
            self.trajectories[trajectory_id].pop(0)
    
    def get_trajectory(self, trajectory_id: int) -> List[Dict]:
        """获取轨迹"""
        return self.trajectories[trajectory_id] if trajectory_id < len(self.trajectories) else []
    
    def get_latest(self, count: int = 1) -> List[Dict]:
        """获取最近轨迹"""
        return self.trajectories[-count:] if self.trajectories else []
    
    def summarize_trajectory(self, trajectory_id: int) -> Dict:
        """总结轨迹"""
        traj = self.get_trajectory(trajectory_id)
        if not traj:
            return {'steps': 0}
        
        return {
            'trajectory_id': trajectory_id,
            'steps': len(traj),
            'duration': traj[-1].get('timestamp', 0) - traj[0].get('timestamp', 0),
            'outcomes': [s.get('outcome') for s in traj if 'outcome' in s],
        }


class MARS:
    """MARS信念状态追踪 - 来自X系统#59
    
    多维自适应信念状态追踪
    """
    
    def __init__(self):
        self.beliefs: Dict[str, float] = {}
        self.evidence_counts: Dict[str, int] = {}
        self.last_update: Dict[str, float] = {}
        import time
        self._current_time = time.time()
    
    def update(self, belief: str, value: float, evidence_weight: float = 1.0):
        """更新信念
        
        Args:
            belief: 信念名称
            value: 新证据值 (0-1)
            evidence_weight: 证据权重
        """
        import time
        current = self.beliefs.get(belief, 0.5)
        
        # 时间衰减
        last_time = self.last_update.get(belief, self._current_time)
        time_decay = min(1.0, (time.time() - last_time) / 3600)  # 一小时完全衰减
        decay_factor = 0.9 ** time_decay
        
        # 贝叶斯更新
        posterior = current * decay_factor + value * evidence_weight * (1 - decay_factor)
        self.beliefs[belief] = max(0, min(1, posterior))
        
        # 更新计数
        self.evidence_counts[belief] = self.evidence_counts.get(belief, 0) + 1
        self.last_update[belief] = time.time()
    
    def get_belief(self, belief: str) -> float:
        """获取信念值"""
        return self.beliefs.get(belief, 0.5)
    
    def get_confidence(self, belief: str) -> float:
        """获取信念置信度"""
        count = self.evidence_counts.get(belief, 0)
        # 置信度随证据数量增加
        return min(1.0, count / 10)
    
    def get_all_beliefs(self) -> Dict[str, float]:
        """获取所有信念"""
        return dict(self.beliefs)
    
    def decay_all(self, factor: float = 0.95):
        """衰减所有信念"""
        import time
        now = time.time()
        
        for belief in self.beliefs:
            last_time = self.last_update.get(belief, now)
            time_factor = min(1.0, (now - last_time) / 3600)
            self.beliefs[belief] *= factor ** time_factor
            self.last_update[belief] = now


# 工厂
def create_lotka_volterra() -> LotkaVolterra:
    return LotkaVolterra()

def create_harness_x() -> HarnessX:
    return HarnessX()

def create_fggm() -> FGGM:
    return FGGM()