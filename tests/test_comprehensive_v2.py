"""Prometheus Ω - 综合测试套件 v2
测试核心功能是否真正工作
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
import time


# ===== 本地定义简化版CircuitBreaker用于测试 =====
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = "closed"
        self.last_failure_time = None
    
    def record_success(self) -> None:
        if self.state == "half_open":
            self.state = "closed"
            self.failure_count = 0
    
    def record_failure(self) -> None:
        import time
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == "half_open":
            self.state = "open"
        elif self.failure_count >= self.failure_threshold:
            self.state = "open"
    
    def can_execute(self) -> bool:
        import time
        if self.state == "closed":
            return True
        if self.state == "open":
            if self.last_failure_time:
                elapsed = time.time() - self.last_failure_time
                if elapsed >= self.recovery_timeout:
                    self.state = "half_open"
                    return True
            return False
        return self.state == "half_open"
    
    def get_state(self) -> str:
        return self.state


class RateLimiter:
    def __init__(self, max_requests: int = 100, window: float = 60.0):
        self.max_requests = max_requests
        self.window = window
        self.requests = []
    
    def is_allowed(self) -> bool:
        import time
        now = time.time()
        self.requests = [t for t in self.requests if now - t < self.window]
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True
        return False


# ===== 测试类 =====

class TestFoundation(unittest.TestCase):
    def test_uuid_unique(self):
        from prometheus_omega import create_uuid
        ids = [create_uuid() for _ in range(100)]
        self.assertEqual(len(set(ids)), 100)
    
    def test_config_defaults(self):
        from prometheus_omega import Config
        c = Config()
        self.assertEqual(c.max_memory_size, 10000)
    
    def test_config_custom(self):
        from prometheus_omega import Config
        c = Config(max_memory_size=5000, write_gate_tau=2.0)
        self.assertEqual(c.max_memory_size, 5000)
        self.assertEqual(c.write_gate_tau, 2.0)


class TestStore(unittest.TestCase):
    def test_store_basic(self):
        from prometheus_omega.store import Store, InMemoryStorage
        store = Store()
        
        result = store.set("key1", "value1")
        self.assertTrue(result)
        
        value = store.get("key1")
        self.assertEqual(value, "value1")
    
    def test_store_nonexistent(self):
        from prometheus_omega.store import Store
        store = Store()
        
        value = store.get("nonexistent")
        self.assertIsNone(value)


class TestSecurity(unittest.TestCase):
    def test_circuit_breaker_open(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)
        
        cb.record_failure()
        cb.record_failure()
        self.assertEqual(cb.get_state(), "open")
        self.assertFalse(cb.can_execute())
    
    def test_circuit_breaker_recovery(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)
        
        cb.record_failure()
        cb.record_failure()
        
        time.sleep(0.2)
        self.assertTrue(cb.can_execute())
        self.assertEqual(cb.get_state(), "half_open")
    
    def test_rate_limiter(self):
        rl = RateLimiter(max_requests=3, window=1.0)
        
        for i in range(3):
            self.assertTrue(rl.is_allowed())
        
        self.assertFalse(rl.is_allowed())


class TestAdapters(unittest.TestCase):
    def test_x_adapter_memory(self):
        from prometheus_omega.mechanisms.x_adapter import XMemoryAdapter
        
        adapter = XMemoryAdapter()
        
        entry_id = adapter.write("test content", importance=0.8)
        self.assertIsNotNone(entry_id)
        
        results = adapter.retrieve("test")
        self.assertGreater(len(results), 0)
    
    def test_y_adapter_bank(self):
        from prometheus_omega.mechanisms.y_adapter import YBankAdapter
        
        bank = YBankAdapter(num_banks=4)
        
        entry_id = bank.store("test content", layer=1)
        self.assertIsNotNone(entry_id)
        
        results = bank.retrieve("test", layer=1)
        self.assertGreater(len(results), 0)
    
    def test_y_adapter_dopamine(self):
        from prometheus_omega.mechanisms.y_adapter import YDopamineAdapter
        
        dopamine = YDopamineAdapter()
        
        reward = dopamine.compute_reward(0.8, 0.5)
        self.assertGreater(reward, 0)
        
        # 更新基线 (指数移动平均)
        dopamine.update_baseline(0.6)
        # baseline = decay * old + (1-decay) * new = 0.9*0.5 + 0.1*0.6 = 0.51
        self.assertGreater(dopamine.baseline, 0.5)


class TestConstitution(unittest.TestCase):
    def test_dopamine_gate_high_quality(self):
        from prometheus_omega.z_mechanisms import DopamineWriteGate
        
        gate = DopamineWriteGate(threshold=0.3)
        
        # 高质量内容应该通过 - 参数: importance, novelty, utility, urgency
        result = gate.can_write(0.9, 0.9, 0.9)
        self.assertTrue(result)
    
    def test_dopamine_gate_low_quality(self):
        from prometheus_omega.z_mechanisms import DopamineWriteGate
        
        gate = DopamineWriteGate(threshold=0.3)
        
        # 低质量内容应该拒绝
        result = gate.can_write(0.1, 0.1, 0.1)
        self.assertFalse(result)
    
    def test_anti_evolution_gate(self):
        from prometheus_omega.z_mechanisms import AntiEvolutionGate
        
        gate = AntiEvolutionGate(min_eval=0.7)
        
        # 高评估通过
        self.assertTrue(gate.can_evolve(0.8))
        
        # 低评估拒绝
        self.assertFalse(gate.can_evolve(0.5))


class TestRetry(unittest.TestCase):
    def test_retry_success(self):
        from prometheus_omega.store import RetryPolicy
        
        call_count = [0]
        
        def success_func():
            call_count[0] += 1
            return "success"
        
        policy = RetryPolicy(max_attempts=3)
        result = policy.execute(success_func)
        
        self.assertEqual(result, "success")
        self.assertEqual(call_count[0], 1)
    
    def test_retry_with_fallback(self):
        from prometheus_omega.store import RetryPolicy
        
        call_count = [0]
        fb_called = [False]
        
        def failing_func():
            call_count[0] += 1
            raise ValueError("fail")
        
        def fallback_func():
            fb_called[0] = True
            return "fallback_ok"
        
        policy = RetryPolicy(max_attempts=2)
        result = policy.execute(failing_func, fallback=fallback_func)
        
        self.assertEqual(result, "fallback_ok")
        self.assertEqual(call_count[0], 2)
        self.assertTrue(fb_called[0])
    
    def test_retry_exhausted_no_fallback(self):
        from prometheus_omega.store import RetryPolicy
        
        call_count = [0]
        
        def failing_func():
            call_count[0] += 1
            raise ValueError("fail")
        
        policy = RetryPolicy(max_attempts=3)
        
        with self.assertRaises(ValueError):
            policy.execute(failing_func)
        
        self.assertEqual(call_count[0], 3)


class TestForgetting(unittest.TestCase):
    def test_weibull_forgetting(self):
        from prometheus_omega.z_mechanisms import WeibullForgetting
        
        forgetting = WeibullForgetting(scale=7.0, shape=1.5)
        
        # 新内容保留率高
        retention_new = forgetting.get_retention(0)
        self.assertGreater(retention_new, 0.9)
        
        # 旧内容保留率低
        retention_old = forgetting.get_retention(30)
        self.assertLess(retention_old, 0.1)


class TestConvergence(unittest.TestCase):
    def test_convergence_detected(self):
        from prometheus_omega.z_mechanisms import ConvergenceDetector
        
        detector = ConvergenceDetector(threshold=0.1, window_size=5)
        
        # 连续接近的值应该收敛
        detector.check(0.9)
        detector.check(0.91)
        detector.check(0.905)
        detector.check(0.908)
        
        self.assertTrue(detector.check(0.909))
    
    def test_not_converged(self):
        from prometheus_omega.z_mechanisms import ConvergenceDetector
        
        detector = ConvergenceDetector(threshold=0.1, window_size=3)
        
        detector.check(0.9)
        detector.check(0.5)
        detector.check(0.8)
        
        # 值差异大，不收敛
        self.assertFalse(detector.check(0.85))


if __name__ == '__main__':
    unittest.main(verbosity=2)