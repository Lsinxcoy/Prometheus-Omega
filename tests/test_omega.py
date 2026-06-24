"""Prometheus Ω - Tests"""
import sys
sys.path.insert(0, 'src')

import pytest
from prometheus_omega import (
    OmegaCore, create_uuid, Config, EventBus,
    UnifiedEntry, FourNetworkMemory, Bank,
    PolyphonicRetrieval, GeneticAlgorithm, ConvergenceDetector,
    ConstitutionalPrinciples, HarnessX, DAGExecutor
)


class TestFoundation:
    """L0 Foundation测试"""
    
    def test_uuidv7(self):
        ids = [create_uuid() for _ in range(10)]
        assert len(set(ids)) == 10
    
    def test_config(self):
        cfg = Config(max_memory_size=50000)
        assert cfg.max_memory_size == 50000
    
    def test_event_bus(self):
        bus = EventBus()
        called = []
        bus.subscribe("test", lambda e: called.append(e))
        bus.publish("test", {"data": 123})
        assert len(called) == 1


class TestMemory:
    """L2 Memory测试"""
    
    def test_unified_entry(self):
        entry = UnifiedEntry(content="Test memory", importance=0.8)
        assert entry.content == "Test memory"
        assert entry.importance == 0.8
    
    def test_four_network(self):
        fnm = FourNetworkMemory()
        fact = fnm.retain("Python is great", 
                         network=fnf.MemoryNetwork.WORLD if 'fnf' in dir() else None)
        assert fact.content == "Python is great"


class TestRetrieval:
    """L3 Retrieval测试"""
    
    def test_rrf(self):
        from prometheus_omega.retrieval import RRF, RetrievalResult, RetrievalMethod
        rrf = RRF(k=60)
        results = rrf.fuse([[], []])
        assert isinstance(results, list)


class TestEvolution:
    """L5 Evolution测试"""
    
    def test_ga(self):
        ga = GeneticAlgorithm(population_size=10)
        ga.init_population(lambda: {"gene1": 0.5})
        assert len(ga.population) == 10
    
    def test_convergence(self):
        cd = ConvergenceDetector(threshold=0.1)
        cd.check(0.9)
        cd.check(0.91)
        cd.check(0.905)
        assert cd.check(0.908) == True


class TestGovernance:
    """L8 Governance测试"""
    
    def test_constitution(self):
        cp = ConstitutionalPrinciples()
        assert cp.get_principle(0) == "Safety First"
        assert len(cp.PRINCIPLES) == 22


class TestEcosystem:
    """L11 Ecosystem测试"""
    
    def test_harness_x(self):
        hx = HarnessX()
        score = hx.evaluate({"accuracy": 0.9, "efficiency": 0.8})
        assert 0 <= score <= 1


class TestExecution:
    """Execution测试"""
    
    def test_dag(self):
        dag = DAGExecutor()
        dag.add_node("a", "task_a", [])
        dag.add_node("b", "task_b", ["a"])
        results = dag.execute()
        assert "a" in results


if __name__ == "__main__":
    pytest.main([__file__, "-v"])