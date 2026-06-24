"""Prometheus Ω - 综合测试套件 v3
覆盖更多功能
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
import time


class TestFoundation(unittest.TestCase):
    def test_uuid_unique(self):
        from prometheus_omega import create_uuid
        ids = [create_uuid() for _ in range(100)]
        self.assertEqual(len(set(ids)), 100)
    
    def test_config(self):
        from prometheus_omega import Config
        c = Config()
        self.assertIsNotNone(c.max_memory_size)
    
    def test_omega_core_init(self):
        from prometheus_omega import OmegaCore
        core = OmegaCore({'test': True})
        self.assertIsNotNone(core)


class TestAdapter(unittest.TestCase):
    def test_x_adapter(self):
        from prometheus_omega.mechanisms.x_adapter import XMemoryAdapter
        
        adapter = XMemoryAdapter()
        
        # 写入
        entry_id = adapter.write("test content", importance=0.8)
        self.assertIsNotNone(entry_id)
        
        # 检索
        results = adapter.retrieve("test")
        self.assertIsInstance(results, list)
        
        # 统计
        stats = adapter.get_stats()
        self.assertIn('total_entries', stats)
    
    def test_y_bank(self):
        from prometheus_omega.mechanisms.y_adapter import YBankAdapter
        
        bank = YBankAdapter(num_banks=4)
        
        # 存储
        entry_id = bank.store("test content", layer=1)
        self.assertIsNotNone(entry_id)
        
        # 多层检索
        results = bank.retrieve("test")
        self.assertIsInstance(results, list)
        
        # 迁移
        result = bank.migrate("node_0_1", 1, 2)
        self.assertIsInstance(result, bool)
    
    def test_y_dopamine(self):
        from prometheus_omega.mechanisms.y_adapter import YDopamineAdapter
        
        dopamine = YDopamineAdapter()
        
        # 计算奖励
        reward = dopamine.compute_reward(0.8, 0.5)
        self.assertIsInstance(reward, float)
        
        # 更新基线
        old_baseline = dopamine.baseline
        dopamine.update_baseline(0.6)
        self.assertNotEqual(dopamine.baseline, old_baseline)


class TestConstitution(unittest.TestCase):
    def test_dopamine_gate(self):
        from prometheus_omega.z_mechanisms import DopamineWriteGate
        
        gate = DopamineWriteGate(threshold=0.1)
        
        # 各种质量组合
        result1 = gate.can_write(0.9, 0.9, 0.9, 0.9)
        self.assertIsInstance(result1, bool)
        
        result2 = gate.can_write(0.1, 0.1, 0.1, 0.1)
        self.assertIsInstance(result2, bool)
    
    def test_dopamine_stats(self):
        from prometheus_omega.z_mechanisms import DopamineWriteGate
        
        gate = DopamineWriteGate(threshold=0.3)
        
        # 统计
        stats = gate.get_stats()
        self.assertIn('total_attempts', stats)
        self.assertIn('total_allowed', stats)
    
    def test_anti_evolution(self):
        from prometheus_omega.z_mechanisms import AntiEvolutionGate
        
        gate = AntiEvolutionGate()
        
        # 基本测试
        result = gate.can_evolve(0.8)
        self.assertIsInstance(result, bool)


class TestMemory(unittest.TestCase):
    def test_weibull(self):
        from prometheus_omega.z_mechanisms import WeibullForgetting
        
        f = WeibullForgetting(scale=7.0, shape=1.5)
        
        # 不同时间的保留率
        r1 = f.get_retention(0)    # 刚写入
        r2 = f.get_retention(7)    # 1周后
        r3 = f.get_retention(30)   # 1月后
        
        self.assertGreater(r1, r2)
        self.assertGreater(r2, r3)
    
    def test_weibull_params(self):
        from prometheus_omega.z_mechanisms import WeibullForgetting
        
        # 不同参数
        f1 = WeibullForgetting(scale=7.0)
        f2 = WeibullForgetting(scale=30.0)
        
        r1 = f1.get_retention(7)
        r2 = f2.get_retention(7)
        
        self.assertNotEqual(r1, r2)


class TestConvergence(unittest.TestCase):
    def test_convergence_detector(self):
        from prometheus_omega.z_mechanisms import ConvergenceDetector
        
        detector = ConvergenceDetector(threshold=0.1, window_size=3)
        
        # 连续接近的值应该收敛
        detector.check(0.9)
        detector.check(0.91)
        result = detector.check(0.905)
        
        self.assertIsInstance(result, bool)
    
    def test_convergence_noisy(self):
        from prometheus_omega.z_mechanisms import ConvergenceDetector
        
        detector = ConvergenceDetector(threshold=0.1, window_size=3)
        
        # 噪声数据不应该收敛
        detector.check(0.9)
        detector.check(0.5)
        detector.check(0.8)
        
        result = detector.check(0.85)
        self.assertFalse(result)


class TestRetry(unittest.TestCase):
    def test_retry_success(self):
        from prometheus_omega.store import RetryPolicy
        
        policy = RetryPolicy(max_attempts=3)
        
        call_count = [0]
        
        def success():
            call_count[0] += 1
            return "ok"
        
        result = policy.execute(success)
        self.assertEqual(result, "ok")
        self.assertEqual(call_count[0], 1)
    
    def test_retry_fallback(self):
        from prometheus_omega.store import RetryPolicy
        
        policy = RetryPolicy(max_attempts=2)
        
        call_count = [0]
        fb_called = [False]
        
        def fail():
            call_count[0] += 1
            raise ValueError("fail")
        
        def fallback():
            fb_called[0] = True
            return "fallback"
        
        result = policy.execute(fail, fallback=fallback)
        
        self.assertEqual(result, "fallback")
        self.assertEqual(call_count[0], 2)
        self.assertTrue(fb_called[0])
    
    def test_retry_exhausted(self):
        from prometheus_omega.store import RetryPolicy
        
        policy = RetryPolicy(max_attempts=3)
        
        def fail():
            raise ValueError("fail")
        
        with self.assertRaises(ValueError):
            policy.execute(fail)


class TestCache(unittest.TestCase):
    def test_cache_basic(self):
        from prometheus_omega.store import SimpleCache
        
        cache = SimpleCache(max_size=10, ttl=1.0)
        
        # 设置和获取
        cache.set("key1", "value1")
        value = cache.get("key1")
        
        self.assertEqual(value, "value1")
    
    def test_cache_expiry(self):
        from prometheus_omega.store import SimpleCache
        
        cache = SimpleCache(max_size=10, ttl=0.1)
        
        cache.set("key1", "value1")
        
        time.sleep(0.2)
        
        value = cache.get("key1")
        self.assertIsNone(value)
    
    def test_cache_delete(self):
        from prometheus_omega.store import SimpleCache
        
        cache = SimpleCache()
        
        cache.set("key1", "value1")
        cache.delete("key1")
        
        value = cache.get("key1")
        self.assertIsNone(value)


class TestSecurity(unittest.TestCase):
    def test_circuit_breaker_closed(self):
        from prometheus_omega.evaluation import CircuitBreaker
        
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=0.1)
        
        self.assertEqual(cb.get_state(), "closed")
        self.assertTrue(cb.can_execute())
    
    def test_circuit_breaker_open(self):
        from prometheus_omega.evaluation import CircuitBreaker
        
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)
        
        # 触发断路
        cb.record_failure()
        cb.record_failure()
        
        self.assertEqual(cb.get_state(), "open")
        self.assertFalse(cb.can_execute())
    
    def test_circuit_breaker_recovery(self):
        from prometheus_omega.evaluation import CircuitBreaker
        
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)
        
        cb.record_failure()
        cb.record_failure()
        
        # 等待恢复
        time.sleep(0.2)
        
        result = cb.can_execute()
        self.assertTrue(result)
        self.assertEqual(cb.get_state(), "half_open")
    
    def test_rate_limiter(self):
        from prometheus_omega.evaluation import RateLimiter
        
        rl = RateLimiter(max_requests=3, window=1.0)
        
        # 前3次通过
        for i in range(3):
            self.assertTrue(rl.is_allowed())
        
        # 第4次被限制
        self.assertFalse(rl.is_allowed())


if __name__ == '__main__':
    unittest.main(verbosity=2)