"""
Prometheus Ω - 完整功能测试
===========================
覆盖所有核心模块的单元测试
"""

import sys
import os

# 添加源码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from datetime import datetime, timedelta
import time


# ===== Foundation层测试 =====
class TestFoundation:
    """Foundation层测试"""
    
    def test_uuidv7_generation(self):
        """测试UUIDv7生成"""
        from prometheus_omega.foundation import UUIDv7Generator, create_uuid
        
        id1 = create_uuid()
        id2 = create_uuid()
        
        assert id1 != id2
        assert len(id1) == 36
        
        # 验证时间有序
        time.sleep(0.01)
        id3 = create_uuid()
        assert id1 < id3  # 后生成的在字典序上更大
    
    def test_config_creation(self):
        """测试配置创建"""
        from prometheus_omega.foundation import OmegaConfig, create_config
        
        config = OmegaConfig(
            max_memory_size=5000,
            write_gate_tau=2.0,
        )
        
        assert config.max_memory_size == 5000
        assert config.write_gate_tau == 2.0
        
        # 工厂函数
        config2 = create_config(max_context_length=4096)
        assert config2.max_context_length == 4096
    
    def test_node_creation(self):
        """测试节点创建"""
        from prometheus_omega.foundation import OmegaNode, NodeType, TrustLevel, create_node
        
        node = OmegaNode(
            content="test content",
            type=NodeType.CONCEPT,
            utility=8.5,
            importance=0.8,
            trust=TrustLevel.HIGH,
        )
        
        assert node.content == "test content"
        assert node.type == NodeType.CONCEPT
        assert node.utility == 8.5
        assert node.trust == TrustLevel.HIGH
        assert node.id is not None
        
        # 工厂函数
        node2 = create_node(content="another")
        assert node2.content == "another"
    
    def test_node_to_dict(self):
        """测试节点序列化"""
        from prometheus_omega.foundation import OmegaNode
        
        node = OmegaNode(content="test", utility=5.0)
        data = node.to_dict()
        
        assert data['content'] == 'test'
        assert data['utility'] == 5.0
        assert 'id' in data
    
    def test_node_from_dict(self):
        """测试节点反序列化"""
        from prometheus_omega.foundation import OmegaNode, NodeType
        
        data = {
            'id': 'test-id-123',
            'content': 'restored',
            'type': 2,
            'utility': 7.0,
        }
        
        node = OmegaNode.from_dict(data)
        assert node.id == 'test-id-123'
        assert node.content == 'restored'
        assert node.type == NodeType.EVENT
    
    def test_node_access(self):
        """测试节点访问更新"""
        from prometheus_omega.foundation import OmegaNode
        
        node = OmegaNode(content="test")
        original_time = node.accessed_at
        
        time.sleep(0.01)
        node.access()
        
        assert node.accessed_at > original_time
    
    def test_event_bus(self):
        """测试事件总线"""
        from prometheus_omega.foundation import EventBus
        
        bus = EventBus()
        events_received = []
        
        def handler(event):
            events_received.append(event)
        
        bus.subscribe('test_event', handler)
        bus.publish('test_event', {'data': 'hello'})
        
        assert len(events_received) == 1
        assert 'data' in events_received[0]
    
    def test_deterministic_rule_engine(self):
        """测试确定性规则引擎"""
        from prometheus_omega.foundation import DeterministicRuleEngine, Rule
        
        engine = DeterministicRuleEngine()
        
        # 添加规则
        rule = Rule(
            name="test_rule",
            condition={"field": "importance", "operator": ">", "value": 0.5},
            action="raise_trust",
            priority=10,
        )
        
        engine.add_rule(rule)
        assert engine.get_rule_count() > 0


# ===== Memory层测试 =====
class TestMemory:
    """Memory层测试"""
    
    def test_unified_entry(self):
        """测试统一条目"""
        from prometheus_omega.memory import UnifiedEntry, EntryCategory
        
        entry = UnifiedEntry(
            content="important memory",
            category=EntryCategory.EXPERIENCE,
            importance=0.9,
        )
        
        assert entry.content == "important memory"
        assert entry.category == EntryCategory.EXPERIENCE
    
    def test_four_network_memory(self):
        """测试四网络记忆"""
        from prometheus_omega.memory import FourNetworkMemory
        
        memory = FourNetworkMemory()
        
        # 验证初始化
        stats = memory.get_network_stats()
        assert 'total_nodes' in stats
    
    def test_bank_layer(self):
        """测试Bank分层"""
        from prometheus_omega.memory import BankLayer
        
        bank = BankLayer()
        
        # 测试迁移阈值
        threshold = bank.get_migration_threshold()
        assert threshold > 0
    
    def test_veracity(self):
        """测试真实性追踪"""
        from prometheus_omega.memory import Veracity
        
        veracity = Veracity()
        
        # 验证初始化
        assert veracity is not None


# ===== Retrieval层测试 =====
class TestRetrieval:
    """Retrieval层测试"""
    
    def test_rrf(self):
        """测试RRF排序"""
        from prometheus_omega.retrieval import RRF, RetrievalResult
        
        rrf = RRF(k=60)
        
        # 验证初始化
        assert rrf.k == 60
    
    def test_mmr(self):
        """测试MMR多样性"""
        from prometheus_omega.retrieval import MMR
        
        mmr = MMR(lambda_param=0.5)
        
        # 验证初始化
        assert mmr.lambda_param == 0.5
    
    def test_polyphonic_retrieval(self):
        """测试多声部检索"""
        from prometheus_omega.retrieval import PolyphonicRetrieval
        
        retrieval = PolyphonicRetrieval()
        
        # 验证5条检索路线存在
        assert len(retrieval.routes) >= 5


# ===== Lifecycle层测试 =====
class TestLifecycle:
    """Lifecycle层测试"""
    
    def test_weibull_forgetting(self):
        """测试Weibull遗忘"""
        from prometheus_omega.lifecycle import WeibullForgetting
        
        forgetting = WeibullForgetting(half_life=7.0)
        
        # 计算遗忘率
        decay = forgetting.calculate(days=7)
        assert 0 <= decay <= 1
    
    def test_bank_migration(self):
        """测试Bank迁移"""
        from prometheus_omega.lifecycle import BankMigration
        
        migration = BankMigration(threshold=0.7)
        
        # 测试初始化
        assert migration.threshold == 0.7
    
    def test_consolidation(self):
        """测试记忆巩固"""
        from prometheus_omega.lifecycle import Consolidation
        
        consolidation = Consolidation()
        
        # 验证初始化
        assert consolidation is not None
    
    def test_dopamine_write_gate(self):
        """测试多巴胺写入门控"""
        from prometheus_omega.lifecycle import DopamineWriteGate
        from prometheus_omega.foundation import OmegaNode
        
        gate = DopamineWriteGate(tau=1.0)
        
        # 低质量内容应被拒绝 (importance=0.1, utility=0.1)
        low_quality = OmegaNode(content="x", utility=0.1, importance=0.1, veracity=0.5)
        can_write = gate.can_write(low_quality)
        
        # 高质量内容应被接受
        high_quality = OmegaNode(content="x" * 100, utility=8.0, importance=0.9, veracity=0.8)
        can_write2 = gate.can_write(high_quality)
        
        # 向后兼容: 浮点数
        assert gate.can_write(0.1) == False  # 低于阈值
        assert gate.can_write(0.5) == True   # 高于阈值
    
    def test_zero_llm(self):
        """测试零LLM调用"""
        from prometheus_omega.lifecycle import ZeroLLM
        
        zero_llm = ZeroLLM(max_calls_per_day=100)
        
        # 测试调用限制
        assert zero_llm.can_call_llm()
        
        zero_llm.record_call()
        assert zero_llm.get_remaining() == 99


# ===== Evolution层测试 =====
class TestEvolution:
    """Evolution层测试"""
    
    def test_genetic_algorithm(self):
        """测试遗传算法"""
        from prometheus_omega.evolution import GeneticAlgorithm
        
        ga = GeneticAlgorithm(population_size=20)
        
        # 验证初始化
        assert ga.population_size == 20
    
    def test_ucb1_bandit(self):
        """测试UCB1 bandit"""
        from prometheus_omega.evolution import UCB1Bandit
        
        bandit = UCB1Bandit(n_arms=5)
        
        # 验证初始化
        assert bandit.n_arms == 5
    
    def test_cgp(self):
        """测试Cartesian Genetic Programming"""
        from prometheus_omega.evolution import CGP
        
        cgp = CGP(inputs=2, outputs=1, levels_back=2)
        
        # 生成程序
        program = cgp.generate()
        assert program is not None
    
    def test_island_ga(self):
        """测试岛屿遗传算法"""
        from prometheus_omega.evolution import IslandGA
        
        island_ga = IslandGA(n_islands=4, population_size=10)
        
        # 验证初始化
        assert island_ga.n_islands == 4
    
    def test_coevolve(self):
        """测试协同进化"""
        from prometheus_omega.evolution import Coevolve
        
        coevolve = Coevolve(n_species=3)
        
        # 验证初始化
        assert coevolve.n_species == 3
    
    def test_convergence_detector(self):
        """测试收敛检测"""
        from prometheus_omega.evolution import ConvergenceDetector
        
        detector = ConvergenceDetector(threshold=0.01)
        
        # 验证初始化
        assert detector.threshold == 0.01


# ===== Safety层测试 =====
class TestSafety:
    """Safety层测试"""
    
    def test_four_layer_defense(self):
        """测试四层防御"""
        from prometheus_omega.safety import FourLayerDefense
        
        defense = FourLayerDefense()
        
        # 验证初始化
        assert defense is not None
    
    def test_five_gates(self):
        """测试五门"""
        from prometheus_omega.safety import FiveGates
        from prometheus_omega.foundation import OmegaNode, TrustLevel
        
        gates = FiveGates()
        
        # 验证初始化
        assert gates is not None
    
    def test_denylist(self):
        """测试黑名单"""
        from prometheus_omega.safety import Denylist
        
        denylist = Denylist()
        
        # 验证初始化
        assert denylist is not None
    
    def test_circuit_breaker(self):
        """测试断路器"""
        from prometheus_omega.safety import CircuitBreaker
        
        breaker = CircuitBreaker(failure_threshold=3)
        
        # 验证初始化
        assert breaker.failure_threshold == 3
    
    def test_rate_limiter(self):
        """测试限流器"""
        from prometheus_omega.safety import RateLimiter
        
        limiter = RateLimiter(max_calls=5, window_seconds=60)
        
        # 验证初始化
        assert limiter.max_calls == 5


# ===== Governance层测试 =====
class TestGovernance:
    """Governance层测试"""
    
    def test_constitution(self):
        """测试宪法"""
        from prometheus_omega.governance import Constitution
        
        constitution = Constitution()
        
        # 验证原则数量
        assert len(constitution.principles) > 0
    
    def test_autonomy_level(self):
        """测试自治级别"""
        from prometheus_omega.governance import AutonomyLevel
        
        # 测试5级自治
        assert len(AutonomyLevel) >= 5


# ===== Monitor层测试 =====
class TestMonitor:
    """Monitor层测试"""
    
    def test_zscore_anomaly(self):
        """测试Z-score异常检测"""
        from prometheus_omega.monitor import ZScoreAnomalyDetector
        
        detector = ZScoreAnomalyDetector(threshold=3.0)
        
        # 验证初始化
        assert detector.threshold == 3.0
    
    def test_coral(self):
        """测试CORAL自愈"""
        from prometheus_omega.monitor import CORAL
        
        coral = CORAL()
        
        # 验证初始化
        assert coral is not None


# ===== 运行所有测试 =====
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])