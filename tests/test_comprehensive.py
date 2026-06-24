"""Prometheus Ω - 综合测试套件
测试核心功能是否真正工作
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
from prometheus_omega import create_uuid, Config, OmegaCore


class TestFoundation(unittest.TestCase):
    """基础功能测试"""
    
    def test_uuid_unique(self):
        """UUID应该唯一"""
        ids = [create_uuid() for _ in range(100)]
        self.assertEqual(len(set(ids)), 100)
    
    def test_config_defaults(self):
        """配置应有默认值"""
        c = Config()
        self.assertEqual(c.max_memory_size, 10000)
        self.assertEqual(c.write_gate_tau, 1.0)


class TestStore(unittest.TestCase):
    """存储层测试"""
    
    def test_store_basic(self):
        """测试存储基本功能"""
        from prometheus_omega.store import MemoryStore
        store = MemoryStore()
        
        # 测试写入
        result = store.set("key1", "value1")
        self.assertTrue(result)
        
        # 测试读取
        value = store.get("key1")
        self.assertEqual(value, "value1")
    
    def test_store_constitution_gate(self):
        """测试宪法门控是否工作"""
        from prometheus_omega.store import MemoryStore
        store = MemoryStore()
        
        # 长内容应该通过门控
        long_content = "Hello " * 100
        result = store.set("long_key", long_content)
        self.assertTrue(result, "长内容应该通过宪法门控")


class TestSecurity(unittest.TestCase):
    """安全机制测试"""
    
    def test_circuit_breaker_half_open(self):
        """测试断路器半开状态"""
        from prometheus_omega.evaluation import CircuitBreaker
        
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)
        
        # 触发失败，打开断路器
        cb.record_failure()
        cb.record_failure()
        self.assertEqual(cb.get_state(), "open")
        
        # 等待超时，进入半开
        import time
        time.sleep(0.2)
        self.assertTrue(cb.can_execute())
        self.assertEqual(cb.get_state(), "half_open")
        
        # 成功，关闭断路器
        cb.record_success()
        self.assertEqual(cb.get_state(), "closed")
    
    def test_rate_limiter(self):
        """测试速率限制"""
        from prometheus_omega.evaluation import RateLimiter
        
        rl = RateLimiter(max_requests=3, window=1.0)
        
        # 前3次应该通过
        for i in range(3):
            self.assertTrue(rl.is_allowed())
        
        # 第4次应该被限制
        self.assertFalse(rl.is_allowed())


class TestAdapter(unittest.TestCase):
    """适配器测试"""
    
    def test_x_adapter_memory_fallback(self):
        """测试X适配器内存回退"""
        from prometheus_omega.mechanisms.x_adapter import XMemoryAdapter
        
        adapter = XMemoryAdapter()
        
        # 写入
        entry_id = adapter.write("test content", importance=0.8)
        self.assertIsNotNone(entry_id)
        
        # 检索
        results = adapter.retrieve("test")
        self.assertGreater(len(results), 0)
        
        # 统计
        stats = adapter.get_stats()
        self.assertEqual(stats['mode'], 'memory_fallback')


class TestConstitution(unittest.TestCase):
    """宪法机制测试"""
    
    def test_dopamine_write_gate(self):
        """测试多巴胺写入门控"""
        from prometheus_omega.z_mechanisms import DopamineWriteGate
        
        gate = DopamineWriteGate(threshold=0.3)
        
        # 质量高的应该通过
        allowed = gate.can_write(0.8, 0.8, 0.9, 0.5)
        self.assertTrue(allowed)
        
        # 质量低的应该拒绝
        allowed = gate.can_write(0.1, 0.1, 0.1, 0.1)
        self.assertFalse(allowed)


class TestRetryPolicy(unittest.TestCase):
    """重试策略测试"""
    
    def test_retry_with_fallback(self):
        """测试重试和fallback"""
        from prometheus_omega.store import RetryPolicy
        
        call_count = [0]
        fallback_count = [0]
        
        def failing_func():
            call_count[0] += 1
            if call_count[0] < 3:
                raise ValueError("Temporary failure")
            return "success"
        
        def fallback_func():
            fallback_count[0] += 1
            return "fallback_result"
        
        policy = RetryPolicy(max_attempts=2)
        
        # 前2次失败，使用fallback
        result = policy.execute(failing_func, fallback=fallback_func)
        
        self.assertEqual(result, "fallback_result")
        self.assertEqual(call_count[0], 2)  # 2次重试后失败
        self.assertEqual(fallback_count[0], 1)  # fallback被调用


class TestMemory(unittest.TestCase):
    """记忆系统测试"""
    
    def test_four_network_basic(self):
        """测试四网络记忆"""
        from prometheus_omega.memory import FourNetworkMemory
        
        fnm = FourNetworkMemory()
        
        # 存储
        fact = fnm.retain("Important fact", network=1)
        self.assertIsNotNone(fact)
        
        # 检索
        results = fnm.recall("Important", top_k=5)
        self.assertIsNotNone(results)


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)