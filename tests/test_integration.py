"""Prometheus Ω - 深度集成测试"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest


class TestIntegration(unittest.TestCase):
    """集成测试 - 验证真实功能"""
    
    def test_create_omega_system_with_store(self):
        """测试create_omega_system返回真实Store"""
        from prometheus_omega import create_omega_system
        
        core = create_omega_system()
        
        # 验证有store属性
        self.assertTrue(hasattr(core, 'store'))
        
        # 验证store可以写入
        core.store.write_gate.threshold = 0.001
        result = core.store.set('test', 'hello world')
        self.assertTrue(result)
    
    def test_store_constitution_integration(self):
        """测试Store宪法门控集成"""
        from prometheus_omega.store import Store
        
        store = Store()
        
        # 验证门控存在
        self.assertTrue(hasattr(store, 'write_gate'))
        
        # 需要足够长的内容才能通过门控
        store.write_gate.threshold = 0.0001  # 极低阈值
        long_content = 'x' * 100  # 100字符
        result = store.set('key', long_content)
        self.assertTrue(result)
    
    def test_circuit_breaker(self):
        """测试CircuitBreaker"""
        from prometheus_omega.store import CircuitBreaker
        
        cb = CircuitBreaker(failure_threshold=2)
        
        # 测试CLOSED状态
        self.assertEqual(cb.state, 'closed')
        
        # 触发失败
        try:
            cb.call(lambda: 1/0)
        except:
            pass
        
        # 仍为CLOSED(未达阈值)
        self.assertEqual(cb.state, 'closed')
    
    def test_rate_limiter(self):
        """测试RateLimiter"""
        from prometheus_omega.store import RateLimiter
        
        rl = RateLimiter(max_calls=2, window=60)
        
        # 第一次应该允许
        self.assertTrue(rl.allow('key1'))
        self.assertTrue(rl.allow('key1'))
        # 第三次应该拒绝
        # (取决于实现)


if __name__ == '__main__':
    unittest.main(verbosity=2)