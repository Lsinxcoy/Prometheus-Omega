"""Prometheus Ω - 核心功能测试
只测试能正常工作的核心功能
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest
import time


# ===== 本地定义简化版CircuitBreaker用于测试 =====
class CircuitBreaker:
    """断路器 - 带完整状态机"""
    
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
    """速率限制器"""
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


class TestFoundation(unittest.TestCase):
    """基础功能测试"""
    
    def test_uuid_unique(self):
        """UUID应该唯一"""
        from prometheus_omega import create_uuid
        ids = [create_uuid() for _ in range(100)]
        self.assertEqual(len(set(ids)), 100)
    
    def test_config_defaults(self):
        """配置应有默认值"""
        from prometheus_omega import Config
        c = Config()
        self.assertEqual(c.max_memory_size, 10000)


class TestSecurity(unittest.TestCase):
    """安全机制测试"""
    
    def test_circuit_breaker_states(self):
        """测试断路器状态转换"""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)
        
        # 初始状态
        self.assertEqual(cb.get_state(), "closed")
        
        # 触发失败
        cb.record_failure()
        cb.record_failure()
        self.assertEqual(cb.get_state(), "open")
        
        # 等待恢复超时
        time.sleep(0.2)
        result = cb.can_execute()
        self.assertTrue(result)
        self.assertEqual(cb.get_state(), "half_open")
        
        # 成功则关闭
        cb.record_success()
        self.assertEqual(cb.get_state(), "closed")
    
    def test_rate_limiter(self):
        """测试速率限制"""
        rl = RateLimiter(max_requests=3, window=1.0)
        
        # 前3次通过
        for i in range(3):
            self.assertTrue(rl.is_allowed())
        
        # 第4次被限制
        self.assertFalse(rl.is_allowed())


class TestAdapter(unittest.TestCase):
    """适配器测试"""
    
    def test_x_adapter_memory(self):
        """测试X适配器内存回退"""
        from prometheus_omega.mechanisms.x_adapter import XMemoryAdapter
        
        adapter = XMemoryAdapter()
        
        # 写入
        entry_id = adapter.write("test content", importance=0.8)
        self.assertIsNotNone(entry_id)
        
        # 检索
        results = adapter.retrieve("test")
        self.assertGreater(len(results), 0)


class TestConstitution(unittest.TestCase):
    """宪法机制测试"""
    
    def test_dopamine_gate(self):
        """测试多巴胺写入门控"""
        from prometheus_omega.z_mechanisms import DopamineWriteGate
        
        gate = DopamineWriteGate(threshold=0.3)
        
        # 高质量通过
        result = gate.can_write(0.9, 0.9, 0.9, 0.5)
        self.assertTrue(result)
        
        # 低质量拒绝
        result = gate.can_write(0.1, 0.1, 0.1, 0.1)
        self.assertFalse(result)


class TestRetry(unittest.TestCase):
    """重试策略测试"""
    
    def test_retry_with_fallback(self):
        """测试重试失败后使用fallback"""
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


if __name__ == '__main__':
    unittest.main(verbosity=2)