"""L5 Evolution - 进化层 (整合XYZ: 12层GA+CGP+Coevolve+Z Convergence)"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Callable, Optional
from datetime import datetime, timezone
from enum import Enum
import random, math


class EvolutionDirection(Enum):
    FORWARD = "forward"
    LATERAL = "lateral"
    REVERSE = "reverse"


@dataclass
class Individual:
    """进化个体"""
    id: str
    genes: Dict[str, Any]
    fitness: float = 0.0
    generation: int = 0
    parent_ids: List[str] = field(default_factory=list)


class GeneticAlgorithm:
    """12层遗传算法 - 来自X系统#17"""
    
    def __init__(self, population_size: int = 100,
                 mutation_rate: float = 0.1,
                 crossover_rate: float = 0.7):
        self.pop_size = population_size
        self.mut_rate = mutation_rate
        self.cross_rate = crossover_rate
        self.population: List[Individual] = []
        self.generation = 0
    
    def init_population(self, gene_generator: Callable):
        """初始化种群"""
        self.population = [
            Individual(id=f"ind_{i}", genes=gene_generator())
            for i in range(self.pop_size)
        ]
    
    def evolve(self, fitness_fn: Callable) -> List[Individual]:
        """执行一代进化"""
        # 评估适应度
        for ind in self.population:
            ind.fitness = fitness_fn(ind.genes)
        
        # 选择
        selected = self._select()
        
        # 交叉
        offspring = self._crossover(selected)
        
        # 变异
        offspring = self._mutate(offspring)
        
        self.population = offspring
        self.generation += 1
        return self.population
    
    def _select(self) -> List[Individual]:
        """选择 ( Tournament )"""
        selected = []
        for _ in range(self.pop_size):
            tournament = random.sample(self.population, 3)
            winner = max(tournament, key=lambda x: x.fitness)
            selected.append(winner)
        return selected
    
    def _crossover(self, parents: List[Individual]) -> List[Individual]:
        """交叉"""
        offspring = []
        for i in range(0, len(parents), 2):
            if i+1 < len(parents) and random.random() < self.cross_rate:
                child = self._single_point_crossover(parents[i], parents[i+1])
            else:
                child = parents[i]
            offspring.append(child)
        return offspring
    
    def _single_point_crossover(self, p1: Individual, p2: Individual) -> Individual:
        """单点交叉"""
        genes = {**p1.genes, **p2.genes}
        return Individual(id=f"gen{self.generation}_{random.randint(0,9999)}",
                         genes=genes, generation=self.generation)
    
    def _mutate(self, offspring: List[Individual]) -> List[Individual]:
        """变异"""
        for ind in offspring:
            if random.random() < self.mut_rate:
                key = random.choice(list(ind.genes.keys()))
                ind.genes[key] = random.random()
        return offspring


class UCB1Bandit:
    """UCB1 Bandit层选择 - 来自X系统#18"""
    
    def __init__(self, layers: List[str]):
        self.layers = layers
        self.counts = {l: 0 for l in layers}
        self.values = {l: 0.0 for l in layers}
        self.total = 0
    
    def select(self) -> str:
        """选择层"""
        for layer in self.layers:
            if self.counts[layer] == 0:
                self.counts[layer] += 1
                self.total += 1
                return layer
        
        # UCB1公式
        best_layer = None
        best_score = -float('inf')
        for layer in self.layers:
            avg = self.values[layer]
            ucb = math.sqrt(2 * math.log(self.total) / self.counts[layer])
            score = avg + ucb
            if score > best_score:
                best_score = score
                best_layer = layer
        
        self.counts[best_layer] += 1
        self.total += 1
        return best_layer
    
    def update(self, layer: str, reward: float):
        """更新"""
        n = self.counts[layer]
        self.values[layer] = (self.values[layer] * n + reward) / (n + 1)


class CGP:
    """笛卡尔遗传编程 - 来自X系统#23"""
    def __init__(self, rows: int = 5, cols: int = 5, levels: int = 10):
        self.rows, self.cols, self.levels = rows, cols, levels
        self.nodes = []
    
    def generate(self) -> List:
        return [random.randint(0, self.levels) for _ in range(self.rows * self.cols)]


class IslandGA:
    """Island并行GA - 来自X系统#20"""
    def __init__(self, num_islands: int = 4):
        self.islands = [[] for _ in range(num_islands)]
    
    def migrate(self):
        """环迁移"""
        for i in range(len(self.islands)):
            next_island = (i + 1) % len(self.islands)
            if self.islands[i] and self.islands[next_island]:
                migrant = self.islands[i].pop(0)
                self.islands[next_island].append(migrant)


class Coevolve:
    """协同进化 - 来自Y系统"""
    def __init__(self, populations: Dict[str, List[Individual]]):
        self.populations = populations
    
    def coevolve(self, fitness_fn: Callable) -> Dict[str, float]:
        results = {}
        for name, pop in self.populations.items():
            fit = sum(ind.fitness for ind in pop) / len(pop) if pop else 0
            results[name] = fit
        return results


class SpeculativeEvolution:
    """推测性进化 - 来自X/Y系统#25"""
    def __init__(self):
        self.branches: List[Individual] = []
    
    def fork(self, individual: Individual) -> Individual:
        branch = Individual(
            id=f"{individual.id}_branch",
            genes=dict(individual.genes),
            generation=individual.generation + 1,
            parent_ids=[individual.id]
        )
        self.branches.append(branch)
        return branch


class ConvergenceDetector:
    """收敛检测器 - 来自Z系统"""
    
    def __init__(self, threshold: float = 0.01, window: int = 10):
        self.threshold = threshold
        self.window = window
        self.history: List[float] = []
    
    def check(self, fitness: float) -> bool:
        self.history.append(fitness)
        if len(self.history) > self.window:
            self.history.pop(0)
        if len(self.history) < 2:
            return False
        diff = abs(self.history[-1] - self.history[0])
        return diff < self.threshold


# 工厂
def create_ga(pop_size: int = 100, **kwargs) -> GeneticAlgorithm:
    return GeneticAlgorithm(population_size=pop_size, **kwargs)

def create_ucb1(layers: List[str]) -> UCB1Bandit:
    return UCB1Bandit(layers)

def create_convergence_detector(**kwargs) -> ConvergenceDetector:
    return ConvergenceDetector(**kwargs)