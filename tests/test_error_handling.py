"""Prometheus Ω - 错误处理测试"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import unittest


class TestErrorHandling(unittest.TestCase):
    """错误处理测试"""
    
    def test_error_handler_basic(self):
        """测试ErrorHandler基本功能"""
        from prometheus_omega.store import ErrorHandler
        
        try:
            raise ValueError("test error")
        except ValueError as e:
            result = ErrorHandler.handle_error(e, "test_context")
        
        self.assertIn('error_type', result)
        self.assertIn('message', result)
        self.assertIn('context', result)
        self.assertIn('traceback', result)
        self.assertEqual(result['context'], "test_context")
        self.assertEqual(result['error_type'], "ValueError")
    
    def test_error_handler_keyerror(self):
        """测试ErrorHandler处理KeyError"""
        from prometheus_omega.store import ErrorHandler
        
        try:
            d = {}
            _ = d["missing"]
        except KeyError as e:
            result = ErrorHandler.handle_error(e, "lookup")
        
        self.assertIn('error_type', result)
        self.assertEqual(result['error_type'], "KeyError")
    
    def test_error_handler_timeout(self):
        """测试ErrorHandler处理TimeoutError"""
        from prometheus_omega.store import ErrorHandler
        
        try:
            raise TimeoutError("timeout")
        except TimeoutError as e:
            result = ErrorHandler.handle_error(e, "operation")
        
        self.assertIn('error_type', result)
        self.assertEqual(result['error_type'], "TimeoutError")
    
    def test_retry_with_fallback(self):
        """测试RetryPolicy fallback"""
        from prometheus_omega.store import RetryPolicy
        
        rp = RetryPolicy(max_attempts=1)
        
        call_count = 0
        def failing_func():
            nonlocal call_count
            call_count += 1
            raise ValueError("fail")
        
        def fallback_func():
            return "fallback_result"
        
        result = rp.execute(failing_func, fallback=fallback_func)
        
        self.assertEqual(result, "fallback_result")
        self.assertEqual(call_count, 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)