"""Prometheus Ω - 最终集成测试"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest


class TestFullIntegration(unittest.TestCase):
    """完整集成测试 - 验证系统端到端工作"""
    
    def test_omega_system_full_flow(self):
        """测试Omega系统完整流程"""
        from prometheus_omega import create_omega_system
        
        # 创建系统
        core = create_omega_system()
        
        # 验证组件存在
        self.assertTrue(hasattr(core, 'store'))
        self.assertTrue(hasattr(core, 'config'))
        
        # 写入数据
        core.store.write_gate.threshold = 0.001
        result = core.store.set('key1', 'value1 ' * 10)
        self.assertTrue(result)
        
        # 读取数据
        value = core.store.get('key1')
        self.assertIsNotNone(value)
    
    def test_store_constitution_integration(self):
        """测试Store宪法门控"""
        from prometheus_omega.store import Store
        
        store = Store()
        
        # 门控存在
        self.assertTrue(hasattr(store, 'write_gate'))
        
        # 写入验证
        store.write_gate.threshold = 0.001
        result = store.set('test', 'content ' * 10)
        self.assertTrue(result)
    
    def test_circuit_breaker_integration(self):
        """测试CircuitBreaker"""
        from prometheus_omega.store import CircuitBreaker
        
        cb = CircuitBreaker(failure_threshold=2)
        
        # 初始状态
        self.assertEqual(cb.state, 'closed')
        
        # 触发失败
        try:
            cb.call(lambda: 1/0)
        except:
            pass
        
        # 未达阈值，仍为closed
        self.assertEqual(cb.state, 'closed')
    
    def test_error_handler_integration(self):
        """测试ErrorHandler"""
        from prometheus_omega.store import ErrorHandler
        
        try:
            raise KeyError('test')
        except Exception as e:
            result = ErrorHandler.handle_error(e, 'test')
        
        self.assertIn('error_type', result)
        self.assertIn('message', result)
        self.assertEqual(result['error_type'], 'KeyError')
    
    def test_retry_policy_integration(self):
        """测试RetryPolicy fallback"""
        from prometheus_omega.store import RetryPolicy
        
        rp = RetryPolicy(max_attempts=1)
        
        call_count = 0
        def fail():
            nonlocal call_count
            call_count += 1
            raise RuntimeError('fail')
        
        result = rp.execute(fail, fallback=lambda: 'fallback')
        self.assertEqual(result, 'fallback')
        self.assertEqual(call_count, 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)