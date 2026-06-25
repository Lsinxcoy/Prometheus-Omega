"""Evolution模块测试"""
import sys
sys.path.insert(0, 'src')

from prometheus_omega.evolution import EvolutionEngine, EvolutionOutcome

def test_evolution_engine():
    """测试进化引擎"""
    engine = EvolutionEngine(population_size=50)
    assert engine.population_size == 50
    assert engine.generation == 0

def test_evolve():
    """测试进化"""
    engine = EvolutionEngine()
    population = [1, 2, 3]
    result = engine.evolve(population)
    assert engine.generation == 1

def test_evaluate_fitness():
    """测试适应性评估"""
    engine = EvolutionEngine()
    score = engine.evaluate_fitness({})
    assert 0 <= score <= 1

if __name__ == '__main__':
    test_evolution_engine()
    test_evolve()
    test_evaluate_fitness()
    print("✅ All Evolution tests passed!")
